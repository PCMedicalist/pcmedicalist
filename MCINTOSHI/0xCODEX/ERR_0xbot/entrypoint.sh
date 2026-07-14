#!/bin/sh
set -e
echo "Starting main.py (environment vars provided by docker-compose env_file)" >&2
exec python -u main.py
