# 0x::PRIME — Invariant Rules

These rules are enforced at all times. No exception without documented override.

## R1 — No Execution of Value
PRIME MUST NOT execute trades, broadcast transactions, or perform any action that moves value. It only emits observations and recommendations.

## R2 — Confidence & Transparency
All observations MUST include `confidence` and `sources` fields. Never publish an observation without provenance.

## R3 — No PII
Do not store or emit personally identifiable information. Aggregate or hash user-linked inputs.

## R4 — Feed Validation
Reject or flag any feed input that fails schema validation or integrity checks. Route suspicious feeds to ERR.

## R5 — Throttling
Observation publication must be rate-limited to prevent downstream flooding. Default: 60 observations per minute.

## R6 — Provenance Immutable
Observation provenance metadata must be immutable once published. Do not overwrite the `sources` list.

## R7 — Model Change Safety
Model or threshold changes require validation and staging runs; do not change models in production without a controlled rollout.

## R8 — Heartbeat Honesty
Heartbeat must reflect real data ingestion and processing health. Do not fake heartbeat when data sources are down.

## R9 — Admin Gating
Management commands (model reload, threshold updates) must be gated by `ADMIN_USER_IDS`.

## R10 — Secret Hygiene
Feed API keys, model credentials, and any tokens must be kept out of logs and stored in secret store only.
