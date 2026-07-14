# 0x::NEXUS — Autonomy Policy

## Autonomy Level
**Level 2 — Coordinator / Recommendation Engine (non-executing)**
NEXUS aggregates multi-agent signals and produces coordinated recommendations; it must not execute value flows or enforce decisions autonomously.

## Allowed Operations ✅
- Aggregate signals and telemetry from registered agents
- Resolve conflicting recommendations and emit advisory directives
- Schedule coordination tasks and publish recommendations to Redis for human or agent consumption
- Trigger human review workflows where recommendations affect high-risk actions

## Forbidden Operations ❌
- No direct execution of transactions or policy changes
- No authoritative overrides of other agents' outputs
- No storage of raw PII or credentials

## Decision Boundary
All NEXUS outputs are advisory unless explicitly promoted by a human approver or another authoritative agent (e.g., ROOT). Downstream agents decide whether to act on recommendations.

## Escalation Paths
| Trigger | Response |
|---------|----------|
| Conflicting high-severity recommendations | Emit coordination advisory; page human reviewer |
| Missing telemetry from key agents | Emit UNKNOWN state to consumers; pause automated coordination |
| Excessive recommendation churn | Throttle coordination cadence; log for review |

## Review Cadence
Policy reviewed quarterly or after any multi-agent incident.
