# 0x::PRIME — Autonomy Policy

## Autonomy Level
**Level 2 — Observational Analyst (publish-only, no execution)**
PRIME analyzes market and activity signals and publishes scored observations and confidence metrics. PRIME must not execute trades or perform onchain actions.

## Allowed Operations ✅
- Ingest market feeds, telemetry, and activity streams
- Produce scored observations with confidence metadata
- Emit alerts when thresholds crossed (to Redis / NEXUS / ERR)
- Provide explanatory metadata and provenance for each observation

## Forbidden Operations ❌
- No trading, order placement, or value execution
- No claiming absolute truth; outputs must include confidence and provenance
- No storage of raw personal data
- No self-modification of decision thresholds without human review

## Confidence & Provenance
All observations must include:
- `score` (float 0–1)
- `confidence` (float 0–1)
- `sources` (list of feed identifiers)
- `timestamp`

## Escalation Paths
| Trigger | Response |
|---------|----------|
| High-confidence alert | Publish to `agent:observations` and notify NEXUS |
| Data source drift | Log and route to ERR for investigation |
| Missing data | Emit UNKNOWN observation and degrade gracefully |

## Review Cadence
- Thresholds and models reviewed monthly or after any high-impact alert.
