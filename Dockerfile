FROM python:3.12-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.3.5 /uv /bin/uv

# Copy the project into the image
ADD . /tee-gemini

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /tee-gemini
RUN uv sync --frozen

ENTRYPOINT ["uv", "run", "start-gemini"]
