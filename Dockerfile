FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Download the go-tpm-tools binary
RUN apt-get update && apt-get install -y \
    curl \
    tar \
    tpm2-tools \    
    && rm -rf /var/lib/apt/lists/* \
    && curl -L https://github.com/google/go-tpm-tools/releases/download/v0.4.4/go-tpm-tools_Linux_x86_64.tar.gz -o /tmp/go-tpm-tools.tar.gz \
    && tar -xzf /tmp/go-tpm-tools.tar.gz -C /usr/local/bin/ \
    && rm /tmp/go-tpm-tools.tar.gz \
    && apt-get autoremove -y

# Copy the project into the image
ADD . /tee-gemini

# Set the working directory
WORKDIR /tee-gemini

# Sync the project into a new environment using the frozen lockfile
RUN uv sync --frozen

# Make the entrypoint executable
RUN chmod +x ./entrypoint.sh

LABEL "tee.launch_policy.allow_env_override"="GEMINI_ENDPOINT_ADDRESS,RPC_URL,SECONDS_BW_ITERATIONS,TEE_ADDRESS,TEE_PRIVATE_KEY,GEMINI_API_KEY"
LABEL "tee.launch_policy.log_redirect"="always"

# Define the entrypoint
ENTRYPOINT ["./entrypoint.sh"]
