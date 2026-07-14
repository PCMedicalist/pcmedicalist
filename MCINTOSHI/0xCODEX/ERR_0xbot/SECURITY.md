# 0x::ERR — Security Policy

## Secrets Inventory
| Secret | Variable | Rotation | Who Can Rotate |
|--------|----------|----------|----------------|
| Telegram Bot Token | `TELEGRAM_BOT_TOKEN` / `ERR_API` | On suspicion of leak; quarterly | Admin via BotFather |
| Sentry DSN | `SENTRY_DSN` | On project change | DevOps |
| Redis connection string | `REDIS_URL` | On infra change | DevOps |

## Secret Handling Rules
- All secrets sourced from `.env` — never hardcoded
- `.env` MUST be in `.gitignore`
- Secrets MUST NOT appear in fault alerts, logs, Redis values, or Telegram messages
- Fault details sent to ADMIN-ONLY private channels — never public

## Token Rotation Procedure
1. Open BotFather; revoke current token with `/revoke`
2. Issue new token; update `.env`
3. `docker compose restart err-bot`
4. Verify no 401 errors in startup logs
5. Send test fault to confirm alerts routing correctly
6. Log rotation in incident record

## Alert Channel Security
- `ADMIN_ALERT_CHAT_ID` must point to a private admin channel only
- Rotate channel IDs if channel membership changes (departing team members)
- Error details (fault class, agent, stack hints) MUST NOT be posted to public channels

## Access Control
- All Telegram commands gated by `ADMIN_USER_IDS` (see `RULES.md` R9)
- Container runs as non-root user
- Redis accessible only on `send0x-network` bridge — never public

## Incident Response
| Severity | Example | Response |
|----------|---------|----------|
| P1 — Critical | ERR token leaked, false circuit breakers fired | Revoke; rotate; audit fault log |
| P2 — High | False-positive P1 alerts flooding admin | Review classification logic; throttle |
| P3 — Medium | Sentry project misconfigured | Reconfigure DSN; redeploy |
| P4 — Low | Dependency CVE in requirements | Patch within 7 days |

## Sentry Security
- Sentry receives stack traces — ensure no PII in exception messages
- Enable Sentry data scrubbing for any potentially sensitive fields
- Review Sentry project members quarterly

## Dependency Security
- `pip-audit requirements.txt` before each release
- Base image: `python:3.11-slim` — update to latest patch quarterly
