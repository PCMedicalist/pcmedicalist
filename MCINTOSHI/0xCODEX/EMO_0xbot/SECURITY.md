# 0x::EMO — Security Policy

## Secrets Inventory

| Secret | Variable | Rotation | Who Can Rotate |

|--------|----------|----------|----------------|

| OpenAI API Key | `OPENAI_API_KEY` | On suspicion of leak; quarterly | Admin via OpenAI dashboard |
| Redis connection string | `REDIS_URL` | On infra change | DevOps |

## Secret Handling Rules

- All secrets sourced from `.env` file — never hardcoded in source
- `.env` MUST be listed in `.gitignore` — never commit to version control
- Secrets MUST NOT appear in: logs, OpenAI prompts, Redis values, or Docker image layers
- `OPENAI_API_KEY` MUST NOT be included in any prompt or completion text (see `RULES.md` R10)

## OpenAI API Key Rotation Procedure

1. Log into OpenAI dashboard; revoke the existing key
2. Generate a new key; update `.env` with new value
3. Rebuild and redeploy: `docker compose restart emo-bot`
4. Verify no 401 errors in logs within 60s of restart
5. Log the rotation event in incident log

## Prompt Injection Prevention

- EMO prompts MUST only include structured, pre-defined event metadata (see `RULES.md` R6)
- User-generated content (chat messages, usernames) MUST NOT be passed to OpenAI prompts
- Prompt templates must be reviewed on each update to ensure they cannot be manipulated by crafted event types

## Network Security

- Redis must bind to internal Docker network only (`send0x-network`)
- OpenAI calls are outbound HTTPS only — no inbound ports required
- No public endpoints exposed by this container

## Access Control

- Container runs as non-root user (implement in Dockerfile: `USER emo`)
- Only admin can modify `.env` and trigger redeploy

## Incident Response

| Severity | Example | Response |

|----------|---------|----------|

| P1 — Critical | OpenAI key leaked publicly | Revoke key immediately; rotate; purge logs |
| P2 — High | Prompt injection attempt detected | Review prompt templates; add sanitisation |
| P3 — Medium | Unexpected data in Redis EMO namespace | Audit and purge; assess upstream signal source |
| P4 — Low | Dependency CVE in requirements.txt | Schedule patch within 7 days |

## Dependency Security

- Run `pip-audit` on `requirements.txt` before each release
- Base image: `python:3.11-slim` — update to latest patch quarterly
