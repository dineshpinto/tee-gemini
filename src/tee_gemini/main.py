import asyncio
import logging
import subprocess

from web3.exceptions import ContractLogicError

from tee_gemini.config import (
    GEMINI_API_KEY,
    GEMINI_ENDPOINT_ABI,
    GEMINI_ENDPOINT_ADDRESS,
    IN_TEE,
    RPC_URL,
    SECONDS_BW_ITERATIONS,
    TEE_ADDRESS,
    TEE_PRIVATE_KEY,
)
from tee_gemini.gemini_api import GeminiAPI
from tee_gemini.gemini_endpoint import GeminiEndpoint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_and_process_events(
    gemini_api: GeminiAPI,
    gemini_endpoint: GeminiEndpoint,
    latest_block_num: int,
) -> int:
    """Poll event emitting contract and get latest feed values."""
    new_block_num = await gemini_endpoint.get_latest_block_number()

    if new_block_num > latest_block_num + 1:
        logger.info(
            "Polling Gemini Endpoint for `RequestSubmitted` from %i to %i",
            latest_block_num,
            new_block_num - 1,
        )
        logs = await gemini_endpoint.get_event_logs(
            from_block=latest_block_num,
            to_block=new_block_num - 1,
            event_name="RequestSubmitted",
        )
        if logs:
            logger.debug("Found logs, querying Gemini API")

            for log in logs:
                if not {"uid", "sender", "data"} <= log["args"].keys():
                    logger.warning("Event log does not contain valid args")
                    continue
                uid, data = log["args"]["uid"], log["args"]["data"]
                logger.info("New request uid=%d, data=%s", uid, data)
                response = gemini_api.make_query(uid=uid, data=data)
                logger.info(response)
                try:
                    await gemini_endpoint.respond_to_query(response)
                except ContractLogicError:
                    logger.exception("Error responding to query")
                    continue
        else:
            logger.debug("No `MessageRequested` logs found")

        return new_block_num

    return latest_block_num


async def query_gemini_api() -> None:
    pass


async def async_loop() -> None:
    # Connect to Gemini Endpoint contract
    gemini_endpoint = GeminiEndpoint(
        RPC_URL,
        GEMINI_ENDPOINT_ADDRESS,
        GEMINI_ENDPOINT_ABI,
        TEE_ADDRESS,
        TEE_PRIVATE_KEY,
    )
    await gemini_endpoint.check_connection()

    # Connect to Gemini API
    gemini_api = GeminiAPI(model="gemini-1.5-flash-001", api_key=GEMINI_API_KEY)

    logger.info("Waiting for requests...")
    latest_block_num = await gemini_endpoint.get_latest_block_number()
    while True:
        try:
            latest_block_num = await fetch_and_process_events(
                gemini_api, gemini_endpoint, latest_block_num
            )
        except Exception:
            logger.exception("Error during event processing")
            latest_block_num = await gemini_endpoint.get_latest_block_number()
            continue

        await asyncio.sleep(SECONDS_BW_ITERATIONS)


def start() -> None:
    # Verify TEE
    if IN_TEE:
        logger.info("In TEE, fetching TEE PubKey...")
        gotpm_help_output = subprocess.run(
            ["./gotpm", "--help"],
            capture_output=True,
            check=True,
            text=True,
        )
        logger.info("%s", gotpm_help_output.stdout)

        endorsement_pubkey_output = subprocess.run(
            ["sudo", "./gotpm", "pubkey", "endorsement"],
            capture_output=True,
            check=True,
            text=True,
        )
        endorsement_pubkey = endorsement_pubkey_output.stdout
        logger.info("TEE Endorsement PubKey %s", endorsement_pubkey)
    else:
        logger.info("Not in TEE")

    try:
        asyncio.run(async_loop())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")


if __name__ == "__main__":
    start()
