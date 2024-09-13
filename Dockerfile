FROM python:3.12-slim-bookworm

# Download the go-tpm-tools binary
RUN apt-get update && apt-get install -y \
    curl \
    tar \
    && rm -rf /var/lib/apt/lists/* \
    && curl -L https://github.com/google/go-tpm-tools/releases/download/v0.4.4/go-tpm-tools_Linux_x86_64.tar.gz -o /tmp/go-tpm-tools.tar.gz \
    && tar -xzf /tmp/go-tpm-tools.tar.gz -C /usr/local/bin/ \
    && rm /tmp/go-tpm-tools.tar.gz \
    && apt-get autoremove -y

# Set the working directory
WORKDIR /tee-gemini

# Copy the project into the image
COPY . /tee-gemini

# Sync the project into a new environment using the frozen lockfile
RUN uv sync --frozen

# Make the entrypoint executable
RUN chmod +x ./entrypoint.sh

# Define the entrypoint
ENTRYPOINT ["./entrypoint.sh"]
