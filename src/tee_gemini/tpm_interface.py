import asyncio
import logging

from tee_gemini.gemini_endpoint import OIDCResponse

logger = logging.getLogger(__name__)


class TPMCommunicationError(Exception):
    """Custom exception for TPM communication errors."""


class TPMInterface:
    """Interface for communicating with TPM (Trusted Platform Module)."""

    def __init__(self) -> None:
        pass

    async def _communicate(self, command: str) -> str:
        """Execute a TPM-related command via the subprocess shell."""
        full_command = f"gotpm {command}"
        logger.debug("Executing command: %s", full_command)

        process = await asyncio.create_subprocess_shell(
            full_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode()
            msg = f"Command `{full_command}` failed with error: `{error_msg}`"
            raise TPMCommunicationError(msg)
        return stdout.decode()

    async def check_connection(self) -> str:
        """Check TPM connection by running a simple command."""
        return await self._communicate("--help")

    async def query_ek_pubkey(self) -> str:
        """Query the endorsement key public key (EK pubkey) from the TPM."""
        pubkey = await self._communicate("pubkey endorsement")
        pubkey_cleaned = pubkey.replace("-----BEGIN PUBLIC KEY-----", "").replace(
            "-----END PUBLIC KEY-----", ""
        )

        if not pubkey_cleaned:
            msg = "Received an empty EK public key from TPM"
            raise TPMCommunicationError(msg)

        logger.info("Successfully retrieved EK pubkey: %s", pubkey_cleaned)
        return pubkey_cleaned

    async def query_oidc_token(self, uid: int) -> OIDCResponse:
        """Query the OIDC token from the TPM and return the response."""
        res = await self._communicate("token")

        if not res:
            msg = "Failed to retrieve OIDC token from TPM"
            raise TPMCommunicationError(msg)

        logger.info("Successfully retrieved OIDC token for UID: %s", uid)
        return OIDCResponse(uid, res)
