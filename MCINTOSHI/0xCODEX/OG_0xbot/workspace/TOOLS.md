# 0x::OG — Tools & Integrations

## Required Environment Variables

| Variable | Description | Source in `.env` |
|----------|-------------|-----------------|
| `TELEGRAM_BOT_TOKEN` / `OG_API` | Bot token | `OG_API` |
| `REDIS_URL` | Redis connection | Direct |

## Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SCHEDULED_CHAT_ID` | Channel for scheduled transmissions | (empty) |
| `PIN_CHAT_ID` | Primary channel for pinned messages | (empty) |
| `LOG_LEVEL` | Log verbosity | `INFO` |
| `ADMIN_USER_IDS` | Telegram IDs for admin commands | (empty — harden before production) |

## Telegram Permissions Required

- Send Messages
- Pin Messages (for pinned update functionality)
- Must be added as admin to target channels

## Redis

- Namespaces: `agent:OG_0xbot:*`, `user:*`
- Mode: single-instance

## Channel Discovery

OG auto-discovers channels where it has admin rights with "Pin Messages" permission.
`PIN_CHAT_ID` designates a primary channel (auto-prioritized).

## Future Tools (Planned)

- Discord webhook (`DISCORD_WEBHOOK_URL`) — cross-platform announcement
- Scheduled announcement engine (cron or Celery beat)
