# 0x::L1NE — Invariant Rules

## R1 — Signature Verification
All incoming webhooks MUST be verified using `TWITCH_EVENTSUB_SECRET` or equivalent. Events failing verification MUST be rejected and logged.

## R2 — No Custody
L1NE MUST NOT accept, store, or manage user private keys, wallet mnemonics, or OAuth refresh tokens.

## R3 — Replay Protection
Replay attacks MUST be detected using signature + recent signature cache; any replay must be rejected and `replays_detected` incremented.

## R4 — Input Sanitization
All event fields consumed or forwarded MUST be validated against the event schema to prevent injection and malformed payloads.

## R5 — Explicit Consent for Wallet Binding
Wallet link via SIWE requires explicit user action and nonce verification. No binding without successful SIWE verification.

## R6 — Rate Limits
Per-source rate limits must be enforced to prevent EventSub flood. Default: 200 events/min per channel; configurable via `EVENT_RATE_LIMIT`.

## R7 — No Public Exposure of Secrets
Webhook secrets, SIWE nonces, and RPC keys MUST NOT be logged or persisted in plaintext.

## R8 — Error Routing
Malformed or suspicious events routed to ERR_0xbot for analysis. No silent drops except for repeated replay attempts after logging.

## R9 — Admin Gating
All management commands (e.g., rotate webhook secret, subscribe/unsubscribe) must be admin-only (`ADMIN_USER_IDS`).

## R10 — Respect Platform Policies
Do not attempt to circumvent Twitch platform rules or create unauthorized subscriptions.
