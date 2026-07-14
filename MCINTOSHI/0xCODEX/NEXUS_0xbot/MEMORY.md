# 0x::NEXUS — Memory Policy

## What Is Stored
| Store | Key Pattern | Content | TTL |
|-------|------------|---------|-----|
| Redis hash | `agent:0xNEXUSbot:last_snapshot` | Aggregated telemetry snapshot | None (rotating) |
| Redis list | `agent:0xNEXUSbot:recommendation_log` | Recent recommendations (capped) | 30 days |
| Redis counter | `agent:0xNEXUSbot:coordination_runs` | Lifetime coordination runs | None |
| Redis string | `agent:0xNEXUSbot:heartbeat` | Last heartbeat | None |

## What Is NOT Stored
- Raw PII from upstream agents
- Signatures, private keys, or credentials
- Detailed per-user activity beyond aggregated metrics

## Purge Policy
- `recommendation_log` retained for 30 days, then trimmed
- Snapshots rotated daily; store last 7 snapshots

## Data Privacy
- Store only aggregated telemetry and recommendations; no user-level detail
- All stored identifiers hashed where necessary for traceability

## Compliance Notes
- Aggregated telemetry used for coordination only; ensure consumer agents do not rely on NEXUS for per-user decisions
