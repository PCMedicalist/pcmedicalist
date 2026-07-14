# EMO_0xbot Docker Deploy

This stack runs EMO as a Telegram-first local assistant:

- Local Ollama backend: `http://host.docker.internal:11434/api`
- Default model: `gemma3:4b`
- Telegram polling runtime
- Local Redis sidecar for inter-agent signals
- Mounted workspace for generated files, revisions, and memory

## Prerequisites

- Docker and the Docker Compose plugin
- Ollama reachable from the container host at `http://127.0.0.1:11434`
- A Telegram bot token in `.env`

## 1) Configure Environment

```bash
cd 0xCODEX/EMO_0xbot
cp .env.example .env
```

Set at minimum:

- `TELEGRAM_BOT_TOKEN`
- `EMO_OLLAMA_API_URL=http://host.docker.internal:11434/api`
- `EMO_OLLAMA_MODEL_NAME=gemma3:4b`

Linux Docker Engine already uses `extra_hosts: host.docker.internal:host-gateway` in compose.

## 2) Build And Start

Standard rebuild:

```bash
cd 0xCODEX/EMO_0xbot
docker compose up -d --build emo-agent
```

Full no-cache rebuild:

```bash
cd 0xCODEX/EMO_0xbot
docker compose build --no-cache emo-agent
docker compose up -d emo-agent
```

Important: only `workspace/` is bind-mounted. Code changes under `0xCODEX/EMO_0xbot` or `0xCODEX/shared` require a rebuild before the container sees them.

## 3) Verify Runtime

```bash
docker compose ps
docker compose logs --tail=200 emo-agent
```

Healthy startup should show:

- EMO startup with Ollama URL and model
- Telegram polling started
- Redis connection attempt

## 4) Test Ollama In Container

```bash
docker compose exec emo-agent python - <<'PY'
import os
from shared.llm_providers import generate_with_ollama

print(generate_with_ollama(
    "You are concise.",
    "Reply with: ollama-ok",
    os.getenv("OLLAMA_MODEL_NAME", "gemma3:4b"),
    0.1,
    os.getenv("OLLAMA_API_URL", "http://host.docker.internal:11434/api"),
))
PY
```

## 5) Telegram Behaviors Now Live

EMO no longer relies on slash-command workspace controls. The live interface is natural language.

Artifact examples:

- `Write a poem and save it as tide-song.md`
- `Create a business plan called launch-plan.md`
- `Generate a prompt pack for my sales assistant`
- `Create an image brief for the hero art`

Workspace tool examples:

- `Inspect workspace/launch-plan.md and tell me what is weak`
- `Revise workspace/launch-plan.md to sound more investor-ready`

Memory behaviors:

- `dreams.md`, `thoughts.md`, and `vision.md` are stored under `workspace/memory/`
- recent conversation context is recorded in `workspace/memory/conversation_log.jsonl`
- rewritten files are backed up in `workspace/.revisions/`

Reaction behavior:

- incoming messages receive a progress reaction first
- successful replies receive the success emoji
- failures receive the error emoji without crashing the chat flow

## Stop / Restart

```bash
docker compose stop emo-agent
docker compose restart emo-agent
docker compose down
```
