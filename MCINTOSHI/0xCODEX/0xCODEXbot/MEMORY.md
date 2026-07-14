# 0x::CODEX — Memory Policy

## What Is Stored
| Store | Key Pattern | Content | TTL |
|-------|-------------|---------|-----|
| Redis hash | `user:{user_id}` | First interaction timestamp, bot name | None |
| Redis counter | `agent:0xCODEXbot:command_count` | Lifetime command total | None |
| Redis list | `agent:0xCODEXbot:signals` | Signal payloads (user_id + timestamp only) | 24h |
| Redis string | `agent:0xCODEXbot:last_scan` | Timestamp of last scan | 7 days |
| Redis hash | `agent:0xCODEXbot:metrics` | Aggregate KPIs | None |
| Redis string | `user:{user_id}:last_state_check` | Serialized state snapshot | 1h |

## What Is NOT Stored
- Raw message text or command argument content
- Usernames, first names, last names, or display identifiers
- Phone numbers, email addresses, or any sensitive PII
- Private keys, tokens, or secrets

## Data Privacy
- Telegram `user_id` is treated as a pseudonymous opaque integer
- No cross-referencing of `user_id` with external identity systems
- Users may request erasure of their stored data (see Purge Policy)

## Purge Policy
| Data Class | Automatic TTL | Manual Purge Command |
|------------|--------------|----------------------|
| User session state | 1h | `redis-cli del user:{id}:*` |
| Signal queue | 24h | `redis-cli del agent:0xCODEXbot:signals` |
| Scan timestamp | 7 days | Automatic |
| Command metrics | No TTL (permanent) | Admin only; document reason |
| User first-interaction record | No TTL | `redis-cli hdel user:{id}` on request |

## Retention Limits
- Signal log: cap list at 1000 entries maximum (implement `LTRIM` after each `LPUSH`)
- Metrics counters: indefinite (low-cardinality counters only; no PII)

## Compliance Notes
- No GDPR/CCPA sensitive data categories stored
- User right-to-erasure: run `redis-cli hdel user:{id}` plus scan and delete `user:{id}:*`
- Data minimization principle: only store what is needed for observability
