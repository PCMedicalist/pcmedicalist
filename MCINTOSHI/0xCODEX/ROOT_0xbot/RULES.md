# 0x::ROOT — Invariant Rules

These rules are enforced at all times. No exception without documented multi-party override.

## R1 — Multi-Party Approval
All credential anchors and role grants require approver signatures or admin approvals recorded and hashed. Single-party changes to critical roles are forbidden.

## R2 — No Private Key Storage
ROOT MUST NEVER store private keys or secret signing material. Signing must be delegated to external HSMs or verified onchain.

## R3 — Immutable Anchors
Anchored credentials must be recorded immutably; modifications require an explicit revocation and re-anchor flow.

## R4 — Auditability
All ACL and credential changes must emit an audit record to `agent:0xROOTbot:acl_change_log`.

## R5 — Protective Defaults
Default role assignments should be least-privilege. New roles require documented purpose and risk assessment.

## R6 — Emergency Revocation Procedure
In case of compromise, follow documented emergency revocation and rotation steps; log all actions and notify security.

## R7 — No Onchain Execution Claims
ROOT records anchors and references onchain proofs but does not claim finality or perform final settlement actions itself.

## R8 — Admin Gating
All management endpoints restricted to `ADMIN_USER_IDS` and require 2FA where available.

## R9 — Heartbeat Honesty
Heartbeats must reflect true registry integrity; do not report healthy when inconsistencies exist.

## R10 — Secret Hygiene
All secrets used by ROOT must be managed by secret stores and never logged.
