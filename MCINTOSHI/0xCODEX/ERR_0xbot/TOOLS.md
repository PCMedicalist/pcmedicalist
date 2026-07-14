# 0x::ERR — Tools & Integrations

## Required Environment Variables
| Variable | Description | Source |
|----------|-------------|--------|
| `TELEGRAM_BOT_TOKEN` / `ERR_API` | Bot token from BotFather | `.env` |
| `REDIS_URL` | Redis connection string | `.env` (default: `redis://redis:6379`) |

## Optional Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `ADMIN_ALERT_CHAT_ID` | Telegram chat ID for admin alerts | Must be set for alerts to work |
| `SENTRY_DSN` | Sentry project DSN for crash reporting | (none — optional) |
| `PROMETHEUS_PUSH_URL` | Prometheus pushgateway URL | (none — optional) |
| `LOG_LEVEL` | Structlog output level | `INFO` |
| `ALERT_RATE_LIMIT_SECONDS` | Min seconds between alerts for same fault class | `300` |
| `ADMIN_USER_IDS` | Comma-separated Telegram IDs for admin commands | (required for command gate) |
| `HEARTBEAT_INTERVAL` | Seconds between heartbeat writes | `30` |

## Telegram Bot API
- Library: `python-telegram-bot==20.7` (polling mode)
- Permissions needed: Send Messages to admin channels
- Bot must be added to admin channel with send permission

## Redis Integration
- Subscribes to: all agent error channels (`agent:*:errors`, `network:faults`)
- Writes: `fault_registry`, `fault_log`, metrics counters, circuit-breaker keys
- Namespaces: `agent:0xERRbot:*`, `network:circuit_breaker:*`

## Observability Stack (Optional but Recommended)
| Tool | Purpose | Config |
|------|---------|--------|
| Sentry | Crash reporting and stack trace capture | `SENTRY_DSN` in `.env` |
| Prometheus | Metrics scraping / push | `PROMETHEUS_PUSH_URL` |
| Grafana | Dashboard for fault trends | Reads from Prometheus |

## Fault Classification Registry
- Fault classes defined in: `data/fault_classes.json` (create as needed)
- Each class defines: `class_id`, `severity`, `description`, `suggested_action`

## Future Tools (Planned)
- PagerDuty / OpsGenie integration for P1 on-call paging
- Slack webhook for secondary alerting channel
