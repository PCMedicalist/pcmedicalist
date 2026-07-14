# 0x::CODEX — Heartbeat

## Cadence
- **Interval:** `30s` (override: env `HEARTBEAT_INTERVAL`)
- **On startup:** Redis `PING` + Telegram `getMe()` to confirm live credentials
- **Persistent key:** `agent:0xCODEXbot:heartbeat` — ISO timestamp updated each cycle

## Metrics Emitted (Redis Keys)
| Key | Type | Description |
|-----|------|-------------|
| `agent:0xCODEXbot:heartbeat` | string | Last successful heartbeat (ISO) |
| `agent:0xCODEXbot:command_count` | counter | Lifetime commands processed |
| `agent:0xCODEXbot:signals` | list | Outbound signal queue |
| `agent:0xCODEXbot:last_scan` | string | Timestamp of last `/codex_scan` |
| `agent:0xCODEXbot:metrics` | hash | Aggregate KPIs (lore_reads, etc.) |

## Startup Health Checks
- [ ] Redis reachable: `redis_client.ping()`
- [ ] Telegram token valid: `application.bot.get_me()`
- [ ] Required env vars present: `TELEGRAM_BOT_TOKEN`, `REDIS_URL`
- [ ] Signal queue depth < 500 on start

## Runtime Alert Thresholds
| Condition | Threshold | Response |
|-----------|-----------|----------|
| Consecutive missed heartbeats | ≥ 3 | Page on-call; publish to ERR channel |
| Command error rate | > 5% over 5 min | Alert + log spike |
| Signal queue depth | > 500 (warn) / > 1000 (alert) | Alert |
| Container memory | > 80% limit | Alert |
| Telegram API errors | 3 consecutive | Pause polling; alert |

## Escalation Path
1. Live logs: `docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f codex-bot`
2. Redis inspect: `redis-cli hgetall agent:0xCODEXbot:metrics`
3. Container restart: `docker compose restart codex-bot`
4. If token suspected compromised → see `SECURITY.md`
