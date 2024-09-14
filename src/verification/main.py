import logging

from verification.helper import decode_and_validate_token, parse_verify_args

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_valid(claims: dict) -> bool:
    """Check the validity of the claims."""
    subject = claims.get("sub")
    if not subject:
        msg = "Missing 'sub' claim"
        raise ValueError(msg)
    logger.info("Valid 'sub': %s", subject)

    issued_at = claims.get("iat")
    if not issued_at:
        msg = "Missing 'iat' claim"
        raise ValueError(msg)
    logger.info("Valid 'iat': %s", issued_at)

    hw_model = claims.get("hwmodel")
    if hw_model != "GCP_AMD_SEV":
        msg = "Invalid or missing 'hwmodel' claim"
        raise ValueError(msg)
    logger.info("Valid 'hwmodel': %s", hw_model)

    sw_name = claims.get("swname")
    if sw_name != "GCE":
        msg = "Invalid or missing 'swname' claim"
        raise ValueError(msg)
    logger.info("Valid 'swname': %s", sw_name)

    return True


def start() -> bool:
    args = parse_verify_args()
    decoded_token = decode_and_validate_token(
        args.token, args.expected_issuer, args.well_known_path
    )
    logger.info("Signature is valid")
    validity = is_valid(decoded_token)
    logger.info("Token is valid")
    return validity
