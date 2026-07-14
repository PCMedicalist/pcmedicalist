# 0x::NULL — Heartbeat

## Cadence
- **Interval:** `30s` (env: `HEARTBEAT_INTERVAL`, default `30`)
- **Mechanism:** Redis `PING` + snapshot of ephemeral session counters
- **Persistent key:** `agent:0xNULLbot:heartbeat` — ISO timestamp

## Metrics Emitted (Redis Keys)
| Key | Type | Description |
|-----|------|-------------|
| `agent:0xNULLbot:heartbeat` | string | Last successful heartbeat (ISO) |
| `agent:0xNULLbot:teardowns` | counter | Total teardown operations executed |
| `agent:0xNULLbot:teardown_receipts` | list | Last N teardown receipts |
| `agent:0xNULLbot:prunes` | counter | Number of ephemeral cache prunes |

## Startup Health Checks
- [ ] Redis reachable
- [ ] Session manager accessible
- [ ] Teardown policies loaded and validated

## Runtime Alert Thresholds
| Condition | Threshold | Response |
|-----------|-----------|----------|
| Missed heartbeats | ≥ 3 | Alert ERR; pause teardown operations |
| Excessive teardowns | > 500/min | Throttle and alert admin |
| Unauthorized teardown attempt | Any | Block and alert P1 |

## Escalation Path
1. Check logs: `docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f null-bot`
2. Inspect receipt list: `redis-cli lrange agent:0xNULLbot:teardown_receipts 0 9`
3. Pause teardowns: `redis-cli set agent:0xNULLbot:paused 1`
