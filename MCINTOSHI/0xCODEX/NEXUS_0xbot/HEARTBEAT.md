# 0x::NEXUS — Heartbeat

## Cadence
- **Interval:** `30s` (env: `HEARTBEAT_INTERVAL`, default `30`)
- **Mechanism:** Redis `PING`, aggregation snapshot write to `agent:0xNEXUSbot:heartbeat`
- **Persistent key:** `agent:0xNEXUSbot:heartbeat` — ISO timestamp

## Metrics Emitted (Redis Keys)
| Key | Type | Description |
|-----|------|-------------|
| `agent:0xNEXUSbot:heartbeat` | string | Last successful heartbeat (ISO) |
| `agent:0xNEXUSbot:coordination_runs` | counter | Total coordination events executed |
| `agent:0xNEXUSbot:conflicts_resolved` | counter | Number of conflict resolution suggestions emitted |
| `agent:0xNEXUSbot:telemetry_snapshots` | counter | Aggregated telemetry snapshots taken |

## Startup Health Checks
- [ ] Redis reachable
- [ ] Agent registry accessible
- [ ] Scheduler / job queue healthy
- [ ] Dependent agents (PRIME, GEN, ROOT) responding to ping

## Runtime Alert Thresholds
| Condition | Threshold | Response |
|-----------|-----------|----------|
| Missed heartbeats | ≥ 3 | Emit ERR alert; pause coordination runs |
| Coordination failures | > 5 in 10 min | Log warn; notify admin |
| Telemetry staleness | No updates from key agents > 5 min | Alert and write UNKNOWN markers |

## Escalation Path
1. Check logs: `docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f nexus-bot`
2. Inspect recent snapshot: `redis-cli get agent:0xNEXUSbot:last_snapshot`
3. Restart if necessary: `docker compose restart nexus-bot`
