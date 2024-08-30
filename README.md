# TEE Gemini Reference Implementation

# Installation

Uses [uv](https://docs.astral.sh/uv/)

```bash
uv python install 3.12
uv sync
```

## Start Gemini 

```bash
uv run start-gemini
```

# Docker

```bash
docker build -t tee-gemini .
```

```bash
docker run --name tee-gemini tee-gemini -e GEMINI_ENDPOINT_ADDRESS=0x... RPC_URL=https... SECONDS_BW_ITERATIONS=3 TEE_ADDRESS=0x... TEE_PRIVATE_KEY=...
```