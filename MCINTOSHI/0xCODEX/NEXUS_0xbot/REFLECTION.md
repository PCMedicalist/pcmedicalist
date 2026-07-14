# 0x::NEXUS — Reflection & Introspection

## Self-Check Schedule
| Check | Frequency | Output |
|-------|-----------|--------|
| Coordination success rate | Every 5 min | Log and alert if below threshold |
| Snapshot freshness | Every 5 min | Alert if no new snapshots from key agents |
| Recommendation acceptance rate | Every 30 min | Track downstream acceptance metrics |
| Heartbeat | Every 30s | Redis key updated |

## Anomaly Detection
| Anomaly | Indicator | Response |
|---------|-----------|----------|
| Conflicting high-confidence signals | Multiple agents produce incompatible high-confidence recommendations | Emit advisory and page human reviewer |
| Snapshot staleness | Missing agent telemetry | Mark UNKNOWN and limit recommendations |
| Recommendation spike | Sudden surge in recommendations | Throttle coordination; log for investigation |

## Introspection Tools
- `redis-cli get agent:0xNEXUSbot:last_snapshot`
- `redis-cli lrange agent:0xNEXUSbot:recommendation_log 0 9`
- Check downstream acceptance via `agent:metrics:acceptance:{agent}` if available

## Audit Log Schema
```json
{
  "event": "coordination_recommendation",
  "recommendation_id": "nexus-2026-0321-001",
  "inputs": ["PRIME","GEN","ROOT"],
  "directive": "recommend_pause",
  "confidence": 0.82,
  "timestamp": "2026-03-21T22:00:00Z"
}
```

## Review Cadence
- Weekly: recommendation trends and false-positive review
- Monthly: cross-agent coordination audits
