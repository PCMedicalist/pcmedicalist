# 0x::GEN — Autonomy Policy

## Autonomy Level
**Level 3 — Supervised Deployer (multi-party approval required)**
GEN is the highest-risk deployer in the network. Every deployment request that creates onchain artifacts MUST be approved by at least one human approver from the `APPROVER_USER_IDS` list before execution. GEN CANNOT approve its own requests.

## Allowed Operations ✅
- Queue deployment requests and emit to pending_approvals list
- Execute approved deployments (contract deploy, session NFT mint, namespace register) after human sign-off
- Report deployment status and receipt to Telegram and Redis
- Cancel pending requests on admin command
- Query deployment history

## Forbidden Operations ❌
- **Self-approval** — GEN MUST NOT approve its own deployment requests under any circumstance
- No deployment to mainnet without explicit testnet validation (see `REQUIRE_TESTNET_FIRST`)
- No revocation of existing policies or permissions
- No confirmation of onchain finality (finality determination is external)
- No storage of private keys or signing credentials in Redis, logs, or `.env`
- No deletion of deployment audit records
- No deployment on behalf of an unauthenticated or unverified requester

## Approval Gate
```
Request queued → Notification to APPROVER_USER_IDS → Human reviews →
  ├── Approved → GEN executes → Deploy receipt written
  └── Rejected → Request discarded → Rejection logged
```

Approval timeout: `APPROVAL_TIMEOUT_SECONDS` (default: `3600`). Expired requests are auto-rejected.

## Testnet-First Policy
All new contract deployments MUST first succeed on a configured testnet (`TESTNET_RPC_URL`) before production deployment is permitted. Set `REQUIRE_TESTNET_FIRST=true` (default). This flag MUST NOT be disabled without documented admin override.

## Escalation Paths
| Trigger | Response |
|---------|----------|
| Self-approval attempt | Block; P1 alert; increment `deployments_rejected` |
| RPC failure during deploy | Emit ERR fault; cancel request; alert |
| Unapproved deploy request | Queue for review; never auto-execute |
| 3 consecutive deploy failures | Circuit-break; halt queue; alert ERR + ROOT |

## Review Cadence
Autonomy policy reviewed: **monthly** and after every production deployment.
