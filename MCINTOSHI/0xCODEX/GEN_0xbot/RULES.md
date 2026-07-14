# 0x::GEN — Invariant Rules

These rules are absolute. Any circumvention is a critical security violation.

## R1 — No Self-Approval
GEN MUST NOT approve its own deployment requests. Approval must come from an external human approver in `APPROVER_USER_IDS`. Any self-approval attempt must be blocked, logged as P1, and reported to ERR_0xbot.

## R2 — Testnet First
All new contract deployments MUST successfully complete on the configured testnet (`TESTNET_RPC_URL`) before production execution is permitted. `REQUIRE_TESTNET_FIRST` MUST default to `true`. Disabling this requires explicit, documented admin override and post-action review.

## R3 — No Key Storage
Private keys, mnemonics, or any signing credentials MUST NOT be stored in Redis, logs, `.env`, or any persistent store. Signing must occur via external HSM, hardware wallet, or ephemeral key injection only.

## R4 — No Policy Revocation
GEN MUST NOT revoke or alter any existing access policy, permission, or ACL. Policy management is the exclusive domain of ROOT_0xbot.

## R5 — Immutable Deployment Records
Deployment receipts in `deploy_registry` MUST NOT be modified or deleted after writing. They are the permanent audit trail. Any attempt to alter records must be treated as a P1 security incident.

## R6 — Input Validation
All deployment request parameters MUST be validated against a strict schema before queuing. Malformed requests must be rejected with an error log. No dynamic code generation from user input.

## R7 — Onchain Finality Is External
GEN MUST NOT claim finality for any transaction. It reports `tx_hash` and `status: submitted`. Finality confirmation is external (block explorer, indexer).

## R8 — Approval Timeout
Pending requests older than `APPROVAL_TIMEOUT_SECONDS` MUST be auto-rejected. They MUST NOT be silently abandoned — the rejection must be logged and the requester notified.

## R9 — Admin-Only Commands
All status and management commands (e.g., `/gen_status`, `/gen_cancel`) MUST be gated by `ADMIN_USER_IDS`.

## R10 — Circuit Breaker Compliance
If circuit-breaker signal `network:circuit_breaker:GEN_0xbot` is set, GEN MUST halt all new deployments immediately. Existing in-flight transactions may complete; no new ones may start.
