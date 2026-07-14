# 0x::ERR — Heartbeat

## Cadence
- **Interval:** `30s` (env: `HEARTBEAT_INTERVAL`, default `30`)
- **Mechanism:** Redis `PING` + Telegram `getMe()` on startup; heartbeat key updated each cycle
- **Persistent key:** `agent:0xERRbot:heartbeat` — ISO timestamp

## Metrics Emitted (Redis Keys)
| Key | Type | Description |
|-----|------|-------------|
| `agent:0xERRbot:heartbeat` | string | Last successful heartbeat (ISO) |
| `agent:0xERRbot:errors_reported` | counter | Lifetime errors surfaced |
| `agent:0xERRbot:alerts_sent` | counter | Lifetime alert messages sent |
| `agent:0xERRbot:circuit_breakers_fired` | counter | Circuit breaker signals emitted |
| `agent:0xERRbot:suppression_attempts` | counter | Suppression requests blocked (MUST stay 0) |

## Startup Health Checks
- [ ] Redis reachable: `redis_client.ping()`
- [ ] Telegram token valid: `getMe()`
- [ ] Required env vars present: `TELEGRAM_BOT_TOKEN` / `ERR_API`, `REDIS_URL`
- [ ] Observability stack endpoints reachable (Sentry DSN if configured)
- [ ] Error registry baseline written to Redis

## Runtime Alert Thresholds
| Condition | Threshold | Response |
|-----------|-----------|----------|
| Consecutive missed heartbeats | ≥ 3 | Self-page admin via Telegram; emit to Redis ERR channel |
| Error report flood | > 100 errors / 5 min | Alert admin of potential cascade failure |
| Suppression attempt | Any | Immediate alert; log P1; never suppress |
| Telegram API unavailable | 3 consecutive failures | Fallback to Redis-only alerting |

## Escalation Path
1. Live logs: `docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f err-bot`
2. Redis metrics: `redis-cli hgetall agent:0xERRbot:metrics`
3. Check `suppression_attempts` counter — **MUST be 0 at all times**
4. Container restart: `docker compose restart err-bot`
5. If ERR itself is down: contact admin directly — the alerting layer has failed
