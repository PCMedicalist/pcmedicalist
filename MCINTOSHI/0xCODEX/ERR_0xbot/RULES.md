# 0x::ERR — Invariant Rules

These rules are enforced at all times. No exception without explicit documented override.

## R1 — No Automatic Fixes
ERR MUST NOT attempt to repair, restart, or correct any fault in any other agent. It detects, reports, and stops. Recovery is a human responsibility.

## R2 — No Retries
ERR MUST NOT retry failed operations on behalf of other agents. One attempt to report a fault; if reporting fails, log to stdout and exit gracefully.

## R3 — No Error Suppression
ERR MUST NOT suppress, mask, ignore, or silently discard any reported fault. Every fault that enters the error pipeline must be surfaced. If suppression is requested by any source, refuse and alert admin.

## R4 — No Public Broadcast of Error Details
Error details (stack traces, fault class, affected agent) MUST be sent only to admin-designated private Telegram channels. Public channels MUST NOT receive error specifics — only generic status updates if broadcast is intended.

## R5 — PII Redaction
User IDs referenced in fault records MUST be hash-anonymised (`sha256(user_id)`) before storage or logging. Raw user IDs MUST NOT appear in fault records.

## R6 — Severity Classification Required
Every reported fault MUST be assigned a severity level (P1–P4) before alerting. Uncategorised faults must be treated as P3-Unknown. Alert routing depends on severity.

| Severity | Definition |
|----------|------------|
| P1 | System down, data risk, security breach |
| P2 | Major feature impaired, degraded performance |
| P3 | Minor feature fault, recoverable |
| P4 | Warning, potential future risk |

## R7 — Circuit Breaker Signals Are Advisory
Circuit-breaker signals emitted to `network:circuit_breaker:{agent}` are advisory — consuming agents choose whether to honour them. ERR does not force shutdown.

## R8 — Rate Limit on Alerts
Telegram alerts MUST be rate-limited (max 1 per fault class per 5 minutes) to avoid flooding the admin channel. Rate-limited alerts are still logged to Redis.

## R9 — Admin-Only Commands
All Telegram commands (e.g., `/err_status`, `/err_clear`) MUST be gated by `ADMIN_USER_IDS` allowlist.

## R10 — Secret Hygiene
Bot token and any API keys MUST be sourced from environment variables and MUST NOT appear in logs, alerts, or Redis values.
