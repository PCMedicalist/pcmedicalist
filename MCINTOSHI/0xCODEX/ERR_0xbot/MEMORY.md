# 0x::ERR — Memory Policy

## What Is Stored
| Store | Key Pattern | Content | TTL |
|-------|------------|---------|-----|
| Redis hash | `agent:0xERRbot:fault_registry` | Active fault records (fault_id, severity, agent, timestamp) | None |
| Redis counter | `agent:0xERRbot:errors_reported` | Lifetime total faults reported | None |
| Redis counter | `agent:0xERRbot:alerts_sent` | Lifetime alerts dispatched | None |
| Redis counter | `agent:0xERRbot:circuit_breakers_fired` | Circuit breakers triggered | None |
| Redis counter | `agent:0xERRbot:suppression_attempts` | Suppression requests blocked | None |
| Redis list | `agent:0xERRbot:fault_log` | Recent fault entries (capped at 1000) | 7 days |
| Redis string | `agent:0xERRbot:heartbeat` | Last heartbeat ISO timestamp | None |
| Redis string | `network:circuit_breaker:{agent}` | Active circuit breaker state | 1h (auto-reset) |

## What Is NOT Stored
- Raw error stack traces with PII (user IDs stripped from traces before storage)
- Telegram message IDs from alerts (ephemeral)
- Resolved / acknowledged faults (purged from `fault_registry` on resolution)
- Sentry event IDs or full payload (Sentry holds canonical data)

## Data Privacy
- Fault records contain: fault_id, severity, source_agent, error_class, timestamp
- User IDs associated with a fault must be hash-anonymised before storage (`sha256(user_id)`)
- No usernames, messages, or raw content stored

## Purge Policy
| Data Class | Automatic TTL | Manual Purge |
|-----------|--------------|--------------|
| Fault log | 7 days | `redis-cli del agent:0xERRbot:fault_log` |
| Circuit breaker | 1h auto-expire | `redis-cli del network:circuit_breaker:{agent}` |
| Fault registry | No TTL — persistent | Admin purge after resolution |
| Lifetime counters | No TTL | Admin only |

## Retention Limits
- `fault_log` list capped to 1000 entries (LTRIM in application code)
- `fault_registry` should be reviewed and purged of resolved faults weekly

## Compliance Notes
- No sensitive personal data stored
- Fault records serve as audit evidence — do not purge without operational sign-off
