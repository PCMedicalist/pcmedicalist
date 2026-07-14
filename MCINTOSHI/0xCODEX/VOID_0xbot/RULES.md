# 0x::VOID — Rules

R1 — Do not delete data without explicit `APPROVAL`.
R2 — Treat any unidentified binary payload as `suspicious` and quarantine for operator review.
R3 — Always include provenance and TTL when forwarding metadata.
R4 — Rate-limit auto-notifications to operators to 1 per 10 minutes per namespace.
R5 — Redact any potential PII from traces before persisting.
