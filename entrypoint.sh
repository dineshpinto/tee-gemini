#!bin/bash
mount -t securityfs securityfs /sys/kernel/security
uv run start-gemini