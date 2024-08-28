import asyncio
import logging

from web3 import AsyncHTTPProvider, AsyncWeb3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.types import BlockData

logger = logging.getLogger(__name__)


class RpcAPI:
    def __init__(self, rpc_url: str) -> None:
        """Initialize the asynchronous Web3 instance."""
        self.rpc_url = rpc_url

        self.w3 = AsyncWeb3(
            AsyncHTTPProvider(self.rpc_url), middleware=[ExtraDataToPOAMiddleware]
        )

    async def wait_for_new_block(self, last_block_number: int, delay: float = 0) -> int:
        """Wait for a new block to be mined."""
        while True:
            new_block_number = await self.w3.eth.block_number
            if new_block_number > last_block_number:
                return new_block_number
            await asyncio.sleep(delay)

    async def get_latest_block_number(self) -> int:
        """Get the current block number."""
        return await self.w3.eth.block_number

    async def get_latest_block(self) -> BlockData:
        """Get the current block."""
        return await self.w3.eth.get_block("latest")

    async def check_connection(self) -> None:
        """Check connection to the RPC."""
        if not await self.w3.is_connected():
            msg = f"Connection to {self.rpc_url} failed"
            raise ConnectionError(msg)
        logger.info("Successfully connected to `%s`", self.rpc_url)

    async def get_block(self, number: int) -> BlockData:
        """Get the current block."""
        return await self.w3.eth.get_block(number, full_transactions=True)
