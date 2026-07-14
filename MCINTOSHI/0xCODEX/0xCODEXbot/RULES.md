# 0x::CODEX — Invariant Rules

These rules are enforced at all times. No exception without an explicit documented override approved by admin.

---

## R1 — No Value Execution
The agent MUST NOT execute, sign, or broadcast any blockchain transaction.
It MUST NOT hold, route, or reference wallet private keys.

## R2 — Input Validation
All user-supplied command arguments MUST be sanitized before processing:
- Strip leading/trailing whitespace
- Enforce max argument length: **256 characters** (default)
- No `eval`, `exec`, or dynamic code generation from user input
- Reject null bytes and control characters

## R3 — Rate Limiting
Per-user command rate limit: **60 commands / minute** (env: `RATE_LIMIT_PER_USER`).
Exceeding the limit results in a silent drop and counter increment.
User bans require human admin decision — not automated.

## R4 — Admin-Only Commands
Commands with write access or scan capabilities MUST validate the calling Telegram user ID against the `ADMIN_USER_IDS` env var (comma-separated list) before executing.
Unauthorized callers receive: `"Access denied."` — no other information.

## R5 — No Content Logging
Raw message text from users MUST NOT be written to logs or Redis.
Only structured metadata is permitted: `user_id`, `command`, `timestamp`, `success/fail`.
Arguments are logged as `[redacted]`.

## R6 — Help Always Available
`/help` and `/start` MUST always respond regardless of rate limit, Redis state, or error conditions.

## R7 — Graceful Degradation
If Redis is unreachable, the agent MUST continue serving stateless commands (`/help`, `/lore`, `/law`) and MUST emit a startup warning log.
It MUST NOT crash silently or expose connection error details to users.

## R8 — Namespace Ownership
The agent MUST only write to `agent:0xCODEXbot:*` and `user:*` Redis namespaces.
Writing to another agent's namespace requires an explicit inter-agent signal contract.

## R9 — Heartbeat Honesty
The agent MUST NOT spoof or fake heartbeat timestamps.
If the heartbeat mechanism fails, it MUST log the failure immediately.

## R10 — Secret Hygiene
Token and credential values MUST be sourced exclusively from environment variables.
They MUST NOT appear in logs, Telegram responses, Redis values, or Docker image layers.
