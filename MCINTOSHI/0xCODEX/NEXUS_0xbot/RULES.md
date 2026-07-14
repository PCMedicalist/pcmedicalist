# 0x::NEXUS — Invariant Rules

These rules are enforced at all times. No exception without documented override.

## R1 — Advisory Only
NEXUS outputs are advisory recommendations. It MUST NOT perform authoritative actions or directly modify other agents' state.

## R2 — No PII
NEXUS MUST NOT store or forward personally identifiable information. Aggregation only.

## R3 — Input Validation
All incoming telemetry must be schema-validated. Invalid or malicious inputs must be routed to ERR_0xbot.

## R4 — Conflict Escalation
When high-confidence conflicts occur between agents, NEXUS MUST escalate to human review rather than auto-resolving.

## R5 — Rate Limiting
Coordination runs must be rate-limited to avoid thrashing downstream systems. Default cadence: one run per 30s.

## R6 — Heartbeat Honesty
Heartbeat must reflect true snapshot success; do not report healthy when snapshot incomplete.

## R7 — Immutable Audit Log
Recommendation logs must be append-only and retained per `MEMORY.md` policy.

## R8 — Secret Hygiene
No secrets, API keys, or private data in snapshots or recommendations.

## R9 — Failure Isolation
If NEXUS detects cascading failures, it should emit advisory `network:pause` keys and notify ERR and ROOT.

## R10 — Admin Gating
Administrative control commands must be restricted to `ADMIN_USER_IDS`.
