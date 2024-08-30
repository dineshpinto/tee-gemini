# TEE Gemini Reference Implementation

## Installation

Uses [uv](https://docs.astral.sh/uv/)

```bash
uv python install 3.12
uv sync
```

## Local

```bash
uv run start-gemini
```

## Docker

```bash
docker build -t tee-gemini .
```

```bash
docker run --name tee-gemini tee-gemini -e GEMINI_ENDPOINT_ADDRESS=0x... RPC_URL=https... SECONDS_BW_ITERATIONS=3 TEE_ADDRESS=0x... TEE_PRIVATE_KEY=...
```

## GCP

1. Create a [Compute VM](https://console.cloud.google.com/compute/instancesAdd)
2. Set the following parameters (any parameters not mentioned should be left default):

    - Name: `tee-gemini`
    - Machine Configuration -> Compute Optimized: C2D
    - Confidential VM Service: Enable
    - Deploy Container -> Container Image: `ghcr.io/dineshpinto/tee-gemini:main`
    - Environment Variables -> All environment variables defined in `src/tee_gemini/config.py`
    - Boot Disk -> Change -> Confidential Images: Container-Optimized-OS 113-18224.151.27 LTS
    - Advanced Options -> Security -> Shielded VM: Check Turn on Secure Boot

3. Click on create