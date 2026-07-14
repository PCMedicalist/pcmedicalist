# 0x::CODEX — Autonomy Policy

## Autonomy Level
**Level 2 — Command Gateway**
Fully reactive; all operations triggered by explicit user commands. No unsolicited autonomous execution.

## Allowed Operations ✅
- Respond to all registered slash commands
- Read and write own Redis namespace (`agent:0xCODEXbot:*`, `user:*`)
- Emit structured signals to other agents via Redis pub/sub
- Log structured audit events to stdout
- Serve cached state from Redis to users

## Forbidden Operations ❌
- No blockchain transaction execution or value movement
- No storage or transmission of private keys, secrets, or credentials
- No modification of ACLs, roles, or permissions
- No unsolicited broadcasts to Telegram channels
- No execution of code received from user input
- No read/write of other agents' Redis namespaces without an explicit signal contract
- No network calls outside of: Telegram API, Redis, and tools listed in `TOOLS.md`

## Escalation Paths
| Trigger | Response |
|---------|---------|
| Unknown or unregistered command received | Reply with `/help`; log warn; no action |
| Per-user rate limit exceeded | Drop silently; increment `rate_limited` counter |
| Redis write failure | Log error; emit ERR signal; serve stateless responses |
| Telegram API 5xx error | Retry with backoff (max 3); alert after exhaustion |
| Bot token invalid at boot | Fatal exit with error log; notify ROOT_0xbot |

## Admin Gate (Hardening Required)
Commands with side effects (`/codex_scan`, `/signal`) must be restricted to admin Telegram user IDs via `ADMIN_USER_IDS` env var.
See `RULES.md` — Rule 4 for implementation guidance.

## Review Cadence
Autonomy policy reviewed: **monthly** by system admin.
