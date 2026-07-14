# 0x::OG — Memory Policy

## What Is Stored
| Key Pattern | Content | TTL |
|-------------|---------|-----|
| `user:{user_id}` | First interaction timestamp, bot name | None |
| `agent:OG_0xbot:metrics` | Post count, announcement count | None |
| `agent:OG_0xbot:last_announcement` | Timestamp of last broadcast | 30 days |
| `builder:{id}` | Builder registration metadata (if stored) | None |

## What Is NOT Stored
- Message content of community members
- Usernames or display names
- PII beyond pseudonymous user_id
- Private keys, credentials

## Purge Policy
| Data | TTL | Manual Purge |
|------|-----|-------------|
| Last announcement | 30 days | `redis-cli del agent:OG_0xbot:last_announcement` |
| User first-interaction | None | `redis-cli hdel user:{id}` on request |
| Builder metadata | None | Admin decision; document removal |

## Compliance
- No sensitive data categories stored
- Builder registration data: confirm with builder before storing any identity-linked data
