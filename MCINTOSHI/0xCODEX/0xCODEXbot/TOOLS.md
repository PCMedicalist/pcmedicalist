# 0x::CODEX — Tools & Integrations

## Required Environment Variables
| Variable | Description | Source in `.env` |
|----------|-------------|-----------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | `CODEX_API` |
| `TELEGRAM_TOKEN` | Alias (checked if above absent) | `CODEX_API` |
| `REDIS_URL` | Redis connection string | Direct (default: `redis://redis:6379`) |

## Optional Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | structlog output level | `INFO` |
| `RATE_LIMIT_PER_USER` | Max commands / minute per user | `60` |
| `ADMIN_USER_IDS` | Comma-separated Telegram IDs allowed to run admin commands | (empty = all public; **harden before production**) |
| `HEARTBEAT_INTERVAL` | Seconds between heartbeat writes | `30` |
| `OPENAI_API_KEY` | OpenAI key (future LLM-backed `/codex`) | (not used yet) |

## Telegram Bot API
- Library: `python-telegram-bot==20.7` (polling mode)
- Permissions needed: Send Messages, Reply to Messages, Send Photos
- Must be added to target groups/channels with admin rights for any broadcast functions

## Redis
- Client: `redis==5.0.1`
- Mode: single-instance (`Redis.from_url(REDIS_URL, decode_responses=True)`)
- Namespaces owned: `agent:0xCODEXbot:*`, `user:*`
- Minimum Redis version: 5.x

## Image Assets (Optional)
Place `{command}.png|jpg|gif|webp` in `./images/` to auto-attach a matching image to command responses.
The agent falls back gracefully if the image is not found — no error surfaced to user.

## Rate Limits & Quotas
| Service | Limit | Notes |
|---------|-------|-------|
| Telegram Bot API | 30 msg/s per bot | Enforced by upstream; library queues internally |
| Redis ops | ~100k/s (local) | Well within scope |
| OpenAI (future) | Per-key plan limits | See EMO_0xbot `TOOLS.md` for rate-limiter reference implementation |

## Future Tools (Planned)
- `OPENAI_API_KEY` — LLM-backed `/codex` knowledge queries
- `SENTRY_DSN` — crash and error reporting
- Prometheus push gateway (`PROMETHEUS_PUSHGATEWAY_URL`) — metrics export
