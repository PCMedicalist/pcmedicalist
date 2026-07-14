# 0x::L1NE — Autonomy Policy

## Autonomy Level
**Level 2 — Translator / Event Router (non-authoritative)**
L1NE translates platform events into structured signals; it never executes value flows or makes policy decisions.

## Allowed Operations ✅
- Receive Twitch EventSub and webhook events
- Validate event signatures and sanitize payloads
- Emit structured signals to Redis for downstream agents
- Initiate SIWE flows for wallet linking (interactive; requires user action)
- Rate-limit and reject malformed or replayed webhooks

## Forbidden Operations ❌
- No custody of funds or signing of transactions
- No automatic forwarding of private user data
- No onchain execution or transaction broadcasting
- No policy enforcement beyond validation and routing (NEXUS/ROOT handle orchestration)

## Boundaries
- All identity bindings require explicit user consent (SIWE or signed assertion)
- Rejected events must be logged to ERR channel with reason

## Escalation Paths
| Trigger | Response |
|---------|----------|
| Signature verification failure | Reject event; increment `webhook_errors`; emit ERR alert if repeated |
| Suspicious replay attempt | Block and log; increment `replays_detected` |
| High event flood | Throttle input; notify admin |

## Review Cadence
Autonomy policy reviewed: **quarterly** or after major EventSub changes.
