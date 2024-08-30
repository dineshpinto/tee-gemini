import logging
from dataclasses import dataclass

from web3 import AsyncWeb3
from web3.types import EventData

from tee_gemini.rpc_api import RpcAPI

logger = logging.getLogger(__name__)


@dataclass
class RequestResponse:
    uid: int
    text: str
    prompt_token_count: int
    candidates_token_count: int
    total_token_count: int


class GeminiEndpoint(RpcAPI):
    """Asynchronous methods to interact with the event emitting contract."""

    def __init__(
        self,
        rpc_url: str,
        contract_address: str,
        contract_abi: dict,
        tee_address: str,
        tee_private_key: str,
    ) -> None:
        super().__init__(rpc_url)
        self.tee_address = self.w3.to_checksum_address(tee_address)
        self.tee_private_key = tee_private_key
        self.gemini_endpoint = self.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(contract_address),
            abi=contract_abi,
        )

    async def get_event_logs(
        self, from_block: int, to_block: int, event_name: str
    ) -> list[EventData]:
        """Get contract event logs."""
        return await self.gemini_endpoint.events[event_name]().get_logs(  # pyright: ignore [reportAttributeAccessIssue]
            from_block=from_block, to_block=to_block
        )

    async def respond_to_query(self, response: RequestResponse) -> None:
        tx = await self.gemini_endpoint.functions.fulfillRequest(
            response.uid,
            (
                response.uid,
                response.text,
                response.prompt_token_count,
                response.candidates_token_count,
                response.total_token_count,
            ),
        ).build_transaction(
            {
                "from": self.tee_address,
                "nonce": await self.w3.eth.get_transaction_count(self.tee_address),
                "maxFeePerGas": await self.w3.eth.gas_price,
                "maxPriorityFeePerGas": await self.w3.eth.max_priority_fee,
            }
        )
        signed_tx = self.w3.eth.account.sign_transaction(
            tx, private_key=self.tee_private_key
        )
        tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.debug("Tx Receipt: %s", tx_receipt)
