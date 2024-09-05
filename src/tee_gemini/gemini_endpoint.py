import logging
from dataclasses import dataclass

from web3 import AsyncWeb3
from web3.types import EventData, TxParams, TxReceipt

from tee_gemini.rpc_api import RpcAPI

logger = logging.getLogger(__name__)


@dataclass
class GeminiResponse:
    uid: int
    text: str
    prompt_token_count: int
    candidates_token_count: int
    total_token_count: int


@dataclass
class OIDCResponse:
    uid: int
    token: str


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
        self.contract = self.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(contract_address),
            abi=contract_abi,
        )

    async def get_event_logs(
        self, from_block: int, to_block: int, event_name: str
    ) -> list[EventData]:
        """Get contract event logs."""
        return await self.contract.events[event_name]().get_logs(  # pyright: ignore [reportAttributeAccessIssue]
            from_block=from_block, to_block=to_block
        )

    async def sign_and_send_transaction(self, tx: TxParams) -> TxReceipt:
        """Sign and send a transaction, then wait for receipt."""
        signed_tx = self.w3.eth.account.sign_transaction(
            tx, private_key=self.tee_private_key
        )
        tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.debug("Tx Receipt: %s", tx_receipt)
        return tx_receipt

    async def fulfill_gemini_request(self, response: GeminiResponse) -> None:
        """Fulfills a Gemini request by sending a transaction to the contract."""
        tx = await self.contract.functions.fulfillRequest(
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
        await self.sign_and_send_transaction(tx)

    async def fulfill_oidc_request(self, response: OIDCResponse) -> None:
        """Fulfills an OIDC request by sending a transaction to the contract."""
        tx = await self.contract.functions.fulfillOIDCToken(
            response.uid,
            response.token,
        ).build_transaction(
            {
                "from": self.tee_address,
                "nonce": await self.w3.eth.get_transaction_count(self.tee_address),
                "maxFeePerGas": await self.w3.eth.gas_price,
                "maxPriorityFeePerGas": await self.w3.eth.max_priority_fee,
            }
        )
        await self.sign_and_send_transaction(tx)

    async def set_ek_pubkey(self, pubkey: str) -> None:
        """Sets the EK public key on the contract."""
        tx = await self.contract.functions.setEkPublicKey(
            pubkey.encode(),
        ).build_transaction(
            {
                "from": self.tee_address,
                "nonce": await self.w3.eth.get_transaction_count(self.tee_address),
                "maxFeePerGas": await self.w3.eth.gas_price,
                "maxPriorityFeePerGas": await self.w3.eth.max_priority_fee,
            }
        )
        await self.sign_and_send_transaction(tx)
        logger.info("Set EK pubkey on %s", self.contract.address)
