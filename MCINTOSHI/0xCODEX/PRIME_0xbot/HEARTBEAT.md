# 0x::PRIME — Heartbeat

## Cadence
- **Interval:** `30s` (env: `HEARTBEAT_INTERVAL`, default `30`)
- **Mechanism:** Redis `PING` and sample ingest verification from market feeds
- **Persistent key:** `agent:0xPRIMEbot:heartbeat` — ISO timestamp

## Metrics Emitted (Redis Keys)
| Key | Type | Description |
|-----|------|-------------|
| `agent:0xPRIMEbot:heartbeat` | string | Last successful heartbeat (ISO) |
| `agent:0xPRIMEbot:observations` | counter | Total observations emitted |
| `agent:0xPRIMEbot:alerts` | counter | Alerts emitted when thresholds crossed |
| `agent:0xPRIMEbot:confidence_histogram` | histogram | Distribution of confidence scores |

## Startup Health Checks
- [ ] Redis reachable
- [ ] Market data feeds reachable (oracle / price feed)
- [ ] Model/provider credentials present (if using ML models)
- [ ] Observation pipeline consumers reachable (NEXUS, LOG)

## Runtime Alert Thresholds
| Condition | Threshold | Response |
|-----------|-----------|----------|
| Missed heartbeats | ≥ 3 | Emit ERR alert; pause observation publication |
| Confidence collapse | Median confidence < 0.2 over 10m | Log warn; investigate data sources |
| Feed disconnect | Any | Emit ERR event; fallback to cached feeds |

## Escalation Path
1. View logs: `docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f prime-bot`
2. Check recent observations: `redis-cli lrange agent:0xPRIMEbot:recent_observations 0 9`
3. Restart if necessary: `docker compose restart prime-bot`
