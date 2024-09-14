import logging

from verification.helper import decode_and_validate_token, parse_verify_args

logger = logging.getLogger(__name__)


def is_valid(claims: dict) -> bool:
    """Check the validity of the claims."""
    audience = claims.get("aud")
    if not audience:
        msg = "Missing 'aud' claim"
        raise ValueError(msg)

    subject = claims.get("sub")
    if not subject:
        msg = "Missing 'sub' claim"
        raise ValueError(msg)

    issued_at = claims.get("iat")
    if not issued_at:
        msg = "Missing 'iat' claim"
        raise ValueError(msg)

    expires_at = claims.get("exp")
    if not expires_at:
        msg = "Missing 'exp' claim"
        raise ValueError(msg)

    hw_model = claims.get("hwmodel")
    if hw_model != "GCP_AMD_SEV":
        msg = "Invalid or missing 'hwmodel' claim"
        raise ValueError(msg)

    sw_name = claims.get("swname")
    if sw_name != "GCE":
        msg = "Invalid or missing 'swname' claim"
        raise ValueError(msg)

    secure_boot = claims.get("secboot")
    if not secure_boot:
        msg = "Invalid or missing 'secboot' claim"
        raise ValueError(msg)

    return True


def start() -> bool:
    args = parse_verify_args()
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    logger.info("Expected issuer: %s", args.expected_issuer)

    decoded_token = decode_and_validate_token(
        args.token, args.expected_issuer, args.well_known_path
    )
    logger.info("Successfully verified signature against issuer")
    validity = is_valid(decoded_token)
    logger.info("Token Payload: %s", decoded_token)
    logger.info(
        "Result: Token signature and payload was successfully verified against issuer"
    )
    return validity
