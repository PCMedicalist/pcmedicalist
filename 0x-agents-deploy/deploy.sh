#!/usr/bin/env bash
# Deploy the 0x::CODEX fleet under the Compose project name "0x-agents".
# Run from this directory (which holds the override + .env).
# Base compose is sourced from /home/pcmedicalist/MCINTOSHI/0xCODEX (READ-ONLY).
set -euo pipefail

BASE_COMPOSE=/home/pcmedicalist/MCINTOSHI/0xCODEX/docker-compose.yml
OVERRIDE_COMPOSE="$(dirname "$0")/docker-compose.override.yml"

if [[ ! -f "$BASE_COMPOSE" ]]; then
  echo "ERROR: base compose not found at $BASE_COMPOSE" >&2
  exit 1
fi

echo ">> Building & starting 0x-agents fleet (project: 0x-agents)"
docker compose \
  --env-file "$(dirname "$0")/.env" \
  -f "$BASE_COMPOSE" \
  -f "$OVERRIDE_COMPOSE" \
  up -d --build

echo ">> Done. Showing status:"
docker compose \
  --env-file "$(dirname "$0")/.env" \
  -f "$BASE_COMPOSE" \
  -f "$OVERRIDE_COMPOSE" \
  ps
