# 0x::ERR — Reflection & Introspection

## Self-Check Schedule
| Check | Frequency | Output |
|-------|-----------|--------|
| Error rate across all agents | Every 5 min | Logged; alert on cascade pattern |
| Circuit breaker state review | On each fault | Evaluate need to fire |
| `suppression_attempts` counter | Every 30s | Alert immediately if > 0 |
| Fault registry stale entries | Hourly | Log any unresolved faults > 24h old |
| Heartbeat | Every 30s | Redis key updated |

## Anomaly Detection
| Anomaly | Indicator | Response |
|---------|-----------|----------|
| Error cascade | > 50 faults from multiple agents in 5 min | Alert admin; consider circuit-breaking all |
| Suppression attempt | `suppression_attempts` > 0 | P1 alert immediately |
| ERR itself silent | No alerts in > 30 min during known incidents | Admin manual check |
| Unknown agent source | Fault from unregistered agent ID | Log warn; route as P3-Unknown |

## Introspection Commands (Telegram, admin-only after hardening)
- `/err_status` — Live fault registry snapshot
- `/err_clear {fault_id}` — Mark fault as resolved (admin only)
- `/err_history` — Last 10 fault entries from log

## Audit Log Schema
Each fault detection emits a structured log event:
```json
{
  "event": "fault_detected",
  "fault_id": "0xERR-2026-0321-001",
  "severity": "P2",
  "source_agent": "GEN_0xbot",
  "error_class": "deployment_timeout",
  "bot": "0xERRbot",
  "timestamp": "2026-03-21T22:00:00Z",
  "alert_sent": true
}
```

## Review Cadence
- **Immediately:** any P1 incident triggers a post-incident review within 24h
- **Weekly:** admin review of fault log for patterns
- **Monthly:** full audit of fault registry; purge resolved entries
