# 0x::VOID — Heartbeat

- Cadence: every 45 seconds, write `agent:0xVOIDbot:heartbeat` → {ts, status, load, version}.
- Alert: if 4 consecutive missed heartbeats (3 minutes), emit `ops:agent:stalled` and notify `NEXUS`.
- Health checks: memory pressure, Redis availability, and message queue length.
# 0x::VOID — Heartbeat

## Cadence
- **Interval:** `30s` (env: `HEARTBEAT_INTERVAL`, default `30`)
- **Mechanism:** Redis `PING` and silence-detection window checks
- **Persistent key:** `agent:0xVOIDbot:heartbeat` — ISO timestamp

## Metrics Emitted (Redis Keys)
| Key | Type | Description |
|-----|------|-------------|
| `agent:0xVOIDbot:heartbeat` | string | Last successful heartbeat (ISO) |
| `agent:0xVOIDbot:silence_events` | counter | Detected silence/unknown events |
| `agent:0xVOIDbot:watch_mode_activations` | counter | Times watch-mode entered |

## Startup Health Checks
- [ ] Redis reachable
- [ ] Monitoring endpoints accessible
- [ ] Silence-detection thresholds loaded

## Runtime Alert Thresholds
| Condition | Threshold | Response |
|-----------|-----------|----------|
| Missed heartbeats | ≥ 3 | Emit ERR alert; enter degraded mode |
| Prolonged silence detected | > configured window | Emit watch-mode advisory to NEXUS and ERR |
| Sensor feed gap | Any | Log and notify admin |

## Escalation Path
1. Logs: `docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f void-bot`
2. Inspect silence markers: `redis-cli get agent:0xVOIDbot:last_silence`
3. Restart: `docker compose restart void-bot`
