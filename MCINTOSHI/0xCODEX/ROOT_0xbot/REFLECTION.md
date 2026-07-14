# 0x::ROOT — Reflection & Introspection

## Self-Check Schedule
| Check | Frequency | Output |
|-------|-----------|--------|
| Credential registry integrity | Every 5 min | Validate anchor consistency |
| ACL drift detection | Every 10 min | Alert if unexpected role changes detected |
| Heartbeat | Every 30s | Redis key updated |

## Anomaly Detection
| Anomaly | Indicator | Response |
|---------|-----------|----------|
| Unexpected credential anchor | Anchor not matching onchain proof | P1 alert; quarantine anchor; notify admin |
| Unauthorized role grant | Role change not matching approver records | Block; P1 alert |
| ACL registry inconsistency | Hash mismatch between snapshots | Pause changes; audit |

## Introspection Tools
- `redis-cli hgetall agent:0xROOTbot:credential_registry`
- `redis-cli lrange agent:0xROOTbot:acl_change_log 0 9`

## Audit Log Schema
```json
{
  "event": "credential_anchored",
  "credential_id_hash": "sha256_abc",
  "anchor_tx": "0xabc123",
  "anchor_chain": "chain_id",
  "approver_id_hash": "sha256_def",
  "timestamp": "2026-03-21T22:00:00Z"
}
```

## Review Cadence
- Immediate post-incident review for P1s
- Weekly ACL delta review
