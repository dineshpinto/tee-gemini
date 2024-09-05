import asyncio
import logging

from tee_gemini.gemini_endpoint import OIDCResponse

logger = logging.getLogger(__name__)


class TPMCommunicationError(Exception):
    pass


class TPMInterface:
    def __init__(self) -> None:
        pass

    async def _communicate(self, command: str) -> str:
        command = "./gotpm " + command
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            msg = f"Failed when executing `{command}`, stderr: `{stderr.decode()}`"
            raise TPMCommunicationError(msg)
        return stdout.decode()

    async def check_connection(self) -> str:
        return await self._communicate("--help")

    async def query_ek_pubkey(self) -> str:
        pubkey = await self._communicate("pubkey endorsement")
        return pubkey.replace("-----BEGIN PUBLIC KEY-----", "").replace(
            "-----END PUBLIC KEY-----", ""
        )

    async def query_oidc_token(self, uid: int) -> OIDCResponse:
        res = await self._communicate("token")
        return OIDCResponse(uid, res)
