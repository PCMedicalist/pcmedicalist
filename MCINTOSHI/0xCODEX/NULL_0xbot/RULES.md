# 0x::NULL — Invariant Rules

These rules are enforced at all times. No exception without documented override.

## R1 — No Deletion of Immutable Onchain Data
NULL MUST NEVER delete or modify any immutable onchain records, anchors, or deployment receipts. Any attempt to alter onchain audit records is a P1 security incident.

## R2 — Protected Namespaces
A configurable list `protected_namespaces` defines Redis key patterns that are off-limits to NULL. Attempts to operate on these patterns must be blocked and logged.

## R3 — Admin Approval for Shared State
Any teardown that affects shared or cross-session resources requires explicit `APPROVER_USER_IDS` approval. Single-session ephemeral teardowns may proceed without approver if within policy.

## R4 — No Secret Exposure
Deleted content MUST not be logged; teardown receipts store only hashed identifiers.

## R5 — Rate Limiting
Teardown operations must be rate-limited to avoid accidental mass data loss. Default throttle: 1000 keys per minute for automated runs; manual runs require higher approval.

## R6 — Auditability
Every teardown must produce an immutable receipt recorded in `agent:0xNULLbot:teardown_receipts` with initiator and approver hashes.

## R7 — Pause on Anomaly
If anomalies detected (unauthorized access, spike failures), set `agent:0xNULLbot:paused=1` and notify ERR and ROOT.

## R8 — No Key Material Handling
NULL MUST NOT handle private keys, mnemonics, or signing operations.

## R9 — Human-Only Promotions
Promotion of a teardown from dry-run to live requires explicit human approval recorded in the receipt.

## R10 — Secret Hygiene
Teardown tool auth tokens and any operational secrets must be stored outside of source and never logged.
