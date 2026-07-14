# 0x::GEN — Reflection & Introspection

## Self-Check Schedule
| Check | Frequency | Output |
|-------|-----------|--------|
| Pending approval queue depth | Every 5 min | Alert if > 5 |
| Deployment failure rate | Every 15 min | Alert on ≥ 3 consecutive failures |
| Self-approval attempt counter | Every 30s | P1 alert if > 0 |
| Testnet-first flag validation | On startup + hourly | Alert if disabled |
| RPC endpoint health | Every 5 min | Log warn on latency > 2s |
| Heartbeat | Every 30s | Redis key updated |

## Anomaly Detection
| Anomaly | Indicator | Response |
|---------|-----------|----------|
| Self-approval attempt | Any attempt logged | P1 alert; block; emit ERR signal |
| Unexpected deployment type | Request for unregistered type | Reject; log warn; notify admin |
| RPC provider change detected | Different chain_id in response | Alert; halt queue; verify config |
| Deploy receipt hash mismatch | tx_hash doesn't match receipt | P1 alert; audit deployment |
| Approval timeout without action | Request > `APPROVAL_TIMEOUT_SECONDS` | Auto-reject; log; notify requester |

## Introspection Commands (admin-only, Telegram)
- `/gen_status` — Current queue depth, last deploy timestamp, failure count
- `/gen_history` — Last 5 deployment receipts
- `/gen_cancel {request_id}` — Cancel a pending request (admin only)

## Audit Log Schema
```json
{
  "event": "deployment_executed",
  "deploy_id": "0xGEN-2026-0321-001",
  "deployment_type": "session_contract",
  "tx_hash": "0xabc123...",
  "chain_id": 8453,
  "approver_id_hash": "sha256_hash",
  "requester_id_hash": "sha256_hash",
  "bot": "0xGENbot",
  "timestamp": "2026-03-21T22:00:00Z",
  "testnet_validated": true
}
```

## Review Cadence
- **Immediately:** any failed or anomalous deployment triggers review
- **Weekly:** admin review of deploy_registry and queue state
- **Monthly:** full deployment audit; verify testnet-first compliance
