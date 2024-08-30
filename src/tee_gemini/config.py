import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(".env")


def load_env_var(var_name: str) -> str:
    """Load variables from environment."""
    env_var = os.getenv(var_name, default="")
    if not env_var:
        msg = f"'{var_name}' not found in env"
        raise ValueError(msg)
    return env_var


# Contracts
GEMINI_ENDPOINT_ADDRESS = load_env_var("GEMINI_ENDPOINT_ADDRESS")
ROOT_FOLDER = Path(__file__).resolve().parent.parent
with (ROOT_FOLDER / "contracts" / "output" / "Interactor.abi").open() as f:
    GEMINI_ENDPOINT_ABI = json.load(f)

# Network
RPC_URL = load_env_var("RPC_URL")
SECONDS_BW_ITERATIONS = float(load_env_var("SECONDS_BW_ITERATIONS"))

# TEE
TEE_ADDRESS = load_env_var("TEE_ADDRESS")
TEE_PRIVATE_KEY = load_env_var("TEE_PRIVATE_KEY")
GEMINI_API_KEY = load_env_var("GEMINI_API_KEY")
