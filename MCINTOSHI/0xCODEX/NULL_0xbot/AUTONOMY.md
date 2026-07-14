# 0x::NULL — Autonomy Policy

## Autonomy Level
**Level 1 — Controlled Teardown Agent (human-gated, non-destructive onchain)**
NULL performs ephemeral state teardowns, cache pruning, and revoke of temporary grants. It MUST NEVER remove immutable onchain history or act on onchain finality.

## Allowed Operations ✅
- Clear session-specific ephemeral state (Redis keys, caches)
- Revoke temporary grants, ephemeral tokens, or session-scoped permissions
- Emit teardown receipts and audit logs to Redis
- Respect `protected_namespaces` — do not touch keys outside allowed patterns

## Forbidden Operations ❌
- No deletion or modification of immutable onchain records
- No modification of permanent registries (deploy_registry, credential anchors)
- No access to private keys or signing operations
- No unilateral escalation of privileges or policy changes

## Human-in-the-Loop Requirements
- Any teardown that could affect cross-session shared state requires explicit admin approval (via `ADMIN_USER_IDS`) and is logged with approver ID hash.

## Escalation Paths
| Trigger | Response |
|---------|----------|
| Attempted delete of protected namespace | Block; P1 alert; increment `unauthorized_teardown` |
| Repeated teardown failures | Alert admin; emit ERR event |
| High-frequency teardowns | Throttle; log for review |

## Review Cadence
Autonomy policy reviewed quarterly and after any P1 incident.
