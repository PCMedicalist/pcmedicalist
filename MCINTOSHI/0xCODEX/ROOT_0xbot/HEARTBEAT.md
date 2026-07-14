# 0x::ROOT — Heartbeat

## Cadence
- **Interval:** `30s` (env: `HEARTBEAT_INTERVAL`, default `30`)
- **Mechanism:** Redis `PING` and quick ACL registry verification
- **Persistent key:** `agent:0xROOTbot:heartbeat` — ISO timestamp

## Metrics Emitted (Redis Keys)
| Key | Type | Description |
|-----|------|-------------|
| `agent:0xROOTbot:heartbeat` | string | Last successful heartbeat (ISO) |
| `agent:0xROOTbot:credentials_issued` | counter | Lifetime credentials anchored |
| `agent:0xROOTbot:role_changes` | counter | Role/permission updates |

## Startup Health Checks
- [ ] Redis reachable
- [ ] DID/ENS provider reachable (if used)
- [ ] ACL registry accessible

## Runtime Alert Thresholds
| Condition | Threshold | Response |
|-----------|-----------|----------|
| Missed heartbeats | ≥ 3 | Emit ERR alert; pause credential issuance |
| Unauthorized role change attempt | Any | P1 alert; block and log |
| High frequency role churn | > 10 changes/min | Throttle and notify admin |

## Escalation Path
1. Check logs: `docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f root-bot`
2. Inspect ACL registry snapshot: `redis-cli get agent:0xROOTbot:last_acl_snapshot`
3. Restart if necessary: `docker compose restart root-bot`
