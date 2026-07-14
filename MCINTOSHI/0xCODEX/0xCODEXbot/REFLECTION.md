# 0x::CODEX — Reflection & Introspection

## Self-Check Schedule
| Check | Frequency | Output |
|-------|-----------|--------|
| Command count report | Hourly | Logged to stdout (structlog) |
| Error rate summary | Every 5 min | Logged; alert if threshold exceeded |
| Signal queue depth | Every 60s | Warn if > 500; alert if > 1000 |
| Agent identity verification | On startup | Fatal if Telegram token mismatch |
| Redis key TTL audit | Weekly (manual) | Admin reviews for expired or unexpected keys |

## Introspection Commands
- `/stats` — Exposes live Redis metric snapshot to calling user (admin-gate recommended)
- `/state` — Returns current network state object
- `/observe` — Activates observation mode report

## Anomaly Detection
| Anomaly | Indicator | Response |
|---------|-----------|---------|
| Command flood | > 100 cmds/min from single user | Rate-limit; log incident; increment counter |
| Unexpected command | Unregistered handler invoked | Log warn; reply `/help` |
| Redis latency spike | > 500ms per operation | Log warn; degrade gracefully |
| Repeated scan abuse | > 10 `/codex_scan` / hour | Log and alert admin |
| Token rotation event | New token accepted mid-session | Log and alert for verification |

## Audit Log Schema
Every command handler emits a structured log event:
```json
{
  "event": "command_invoked",
  "command": "/codex",
  "user_id": 123456789,
  "bot": "0xCODEXbot",
  "timestamp": "2026-03-21T22:00:00Z",
  "success": true,
  "args": "[redacted]"
}
```

## Review Cadence
- **Daily:** automated log scan for error spikes (script or Sentry alert)
- **Weekly:** admin reviews `/stats` output and signal queue trends
- **Monthly:** full audit of Redis keys against `MEMORY.md` policy; review `AUTONOMY.md` thresholds
