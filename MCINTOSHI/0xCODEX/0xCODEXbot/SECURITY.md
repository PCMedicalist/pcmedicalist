# 0x::CODEX — Security Policy

## Secrets Inventory
| Secret | Env Variable | Rotation Trigger | Who Rotates |
|--------|-------------|------------------|-------------|
| Telegram Bot Token | `TELEGRAM_BOT_TOKEN` / `CODEX_API` | Suspected leak; quarterly | Admin via BotFather |
| Redis connection string | `REDIS_URL` | Infrastructure change | DevOps |
| Admin user IDs | `ADMIN_USER_IDS` | Team change | Admin (update `.env`, restart) |

## Secret Handling Rules
- All secrets sourced from `.env` — **never hardcoded in source**
- `.env` MUST be in `.gitignore` — never committed to any repository
- Secrets MUST NOT appear in: logs, Telegram responses, Redis values, or Docker image layers
- Any accidental exposure triggers immediate rotation (see Token Rotation Procedure below)

## Token Rotation Procedure
1. Open Telegram BotFather → `/mybots` → Select bot → `API Token` → `Revoke current token`
2. Copy new token; update `.env`: `CODEX_API=<new_token>`
3. Rebuild and restart: `docker compose restart codex-bot`
4. Verify bot responds to `/start` from Telegram
5. Record the rotation date and reason in the incident log
6. Notify other admins

## Network Security
- Redis port `6379` MUST bind to internal Docker network (`send0x-network`) only
- Never expose Redis to `0.0.0.0` or the public internet
- Telegram polling uses outbound HTTPS only — no inbound ports required
- Docker network type: `bridge` — isolated from host network by default

## Access Control
- Container runs as non-root user `codex` (uid 1000)
- Admin command access enforced via `ADMIN_USER_IDS` env var (see `RULES.md` R4)
- Redis has no public auth in dev; **add `requirepass` in production Redis config**

## Incident Response Matrix
| Severity | Example | Response SLA | Action |
|----------|---------|-------------|--------|
| P1 — Critical | Bot token leaked publicly | Immediate | Revoke token; rotate; page all admins; audit logs |
| P2 — High | Unauthorized admin command usage | < 1 hour | Block user; audit logs; rotate if necessary |
| P3 — Medium | Unexpected data in Redis namespace | < 24 hours | Audit keys; purge unauthorized; document |
| P4 — Low | Dependency CVE in requirements.txt | < 7 days | Schedule patch; update image; redeploy |

## Dependency Security
- Audit dependencies on each release: `pip-audit -r requirements.txt`
- Base image: `python:3.11-slim` — update to latest patch quarterly
- Pin all dependency versions in `requirements.txt` (already done — maintain pins)
