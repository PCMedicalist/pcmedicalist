#!/bin/sh
set -e

echo "Starting main.py (environment vars provided by docker-compose env_file)" >&2
echo "Using Python: $(/opt/emvenv/bin/python --version 2>&1)" >&2

# Run EMO as the foreground process so Docker restart policy can recover on failure.
exec /opt/emvenv/bin/python /app/main.py
