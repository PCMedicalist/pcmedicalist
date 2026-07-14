# 0x::NULL — Memory Policy

## What Is Stored
| Store | Key Pattern | Content | TTL |
|-------|------------|---------|-----|
| Redis list | `agent:0xNULLbot:teardown_receipts` | JSON receipts for completed teardowns | 90 days |
| Redis counter | `agent:0xNULLbot:teardowns` | Lifetime teardowns executed | None |
| Redis counter | `agent:0xNULLbot:unauthorized_teardown` | Unauthorized attempts blocked | None |
| Redis string | `agent:0xNULLbot:heartbeat` | Last heartbeat | None |

## What Is NOT Stored
- Raw user data or PII removed during teardowns (only hashed receipts retained)
- Private keys, signing material, or permanent registry contents

## Purge Policy
- `teardown_receipts` retained for 90 days for audit; can be exported to offsite archive
- Counters retained indefinitely

## Data Privacy
- Receipts include: `teardown_id`, `namespace_pattern`, `initiator_id_hash`, `approver_id_hash` (if any), `timestamp` — no raw identifiers

## Compliance Notes
- Teardown receipts are audit evidence; do not purge without documented approval
- For any teardown affecting shared state, create an incident record linked to receipt
