# 0x::NULL — Reflection & Introspection

## Self-Check Schedule
| Check | Frequency | Output |
|-------|-----------|--------|
| Teardown success/failure rates | Every 5 min | Log and alert if failures spike |
| Protected namespace access attempts | Continuous | Immediate alert on any attempt |
| Heartbeat | Every 30s | Redis key updated |

## Anomaly Detection
| Anomaly | Indicator | Response |
|---------|-----------|----------|
| Unauthorized namespace access | Attempt to delete protected key pattern | Block; P1 alert; persist evidence in `teardown_receipts` |
| Repeated failures | Multiple failed teardown operations | Pause teardowns; alert admin |
| Unexpected mass-prune | High volume of teardowns in short window | Throttle; require approver; preserve pre-prune snapshot if possible |

## Introspection Tools
- `redis-cli lrange agent:0xNULLbot:teardown_receipts 0 9`
- `redis-cli get agent:0xNULLbot:heartbeat`
- Check paused flag: `redis-cli get agent:0xNULLbot:paused`

## Audit Log Schema
```json
{
  "event": "teardown_executed",
  "teardown_id": "null-2026-0321-001",
  "namespace_pattern": "session:*-temp",
  "initiator_id_hash": "sha256_abc",
  "approver_id_hash": "sha256_def",
  "timestamp": "2026-03-21T22:00:00Z",
  "items_deleted": 123
}
```

## Review Cadence
- Immediate review on any P1 event
- Weekly sampling of teardown receipts
- Monthly audit of `protected_namespaces` rules
