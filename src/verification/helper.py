import argparse
import base64
from dataclasses import dataclass

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey


@dataclass
class VerifyArgs:
    token: str
    expected_issuer: str
    well_known_path: str


def parse_verify_args() -> VerifyArgs:
    """Parse command line arguments for verification."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--token",
        type=str,
        required=True,
        help="oidc token",
    )
    parser.add_argument(
        "--expected-issuer",
        type=str,
        default="https://confidentialcomputing.googleapis.com",
        help="expected issuer of token (default: https://confidentialcomputing.googleapis.com)",
    )
    parser.add_argument(
        "--well-known-path",
        type=str,
        default="/.well-known/openid-configuration",
        help="well known path (default: /.well-known/openid-configuration)",
    )
    return VerifyArgs(**vars(parser.parse_args()))


def get_well_known_file(expected_issuer: str, well_known_path: str) -> dict:
    """Fetch JWKS URL from well known file."""
    response = requests.get(expected_issuer + well_known_path, timeout=10)
    valid_status_code = 200
    if response.status_code == valid_status_code:
        return response.json()
    msg = f"Failed to fetch JWKS URI: {response.status_code}"
    raise requests.exceptions.HTTPError(msg)


def fetch_jwks(uri: str) -> dict:
    """Fetch the JWKS data from a remote endpoint."""
    response = requests.get(uri, timeout=10)
    valid_status_code = 200
    if response.status_code == valid_status_code:
        return response.json()
    msg = f"Failed to fetch JWKS: {response.status_code}"
    raise requests.exceptions.HTTPError(msg)


def jwk_to_rsa_key(jwk: dict) -> RSAPublicKey:
    """Convert a JWK key (from JWKS) into an RSA public key object."""
    n = int.from_bytes(base64.urlsafe_b64decode(jwk["n"] + "=="), "big")
    e = int.from_bytes(base64.urlsafe_b64decode(jwk["e"] + "=="), "big")
    return rsa.RSAPublicNumbers(e, n).public_key(backend=default_backend())


def decode_and_validate_token(
    token: str, expected_issuer: str, well_known_path: str
) -> dict:
    """Decode and validate the JWT token using the JWKS RSA public key."""
    wk = get_well_known_file(expected_issuer, well_known_path)
    jwks_uri = wk["jwks_uri"]

    jwks = fetch_jwks(jwks_uri)
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = None

    # Find the correct key based on the key ID (kid)
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = jwk_to_rsa_key(key)
            break

    if rsa_key is None:
        msg = "Unable to find appropriate key"
        raise ValueError(msg)

    # Verify and decode the token using the public RSA key
    try:
        return jwt.decode(
            token, rsa_key, algorithms=["RS256"], options={"verify_aud": False}
        )
    except jwt.ExpiredSignatureError as e:
        msg = "Token has expired"
        raise ValueError(msg) from e
    except jwt.InvalidTokenError as e:
        msg = f"Invalid token: {e!s}"
        raise ValueError(msg) from e
