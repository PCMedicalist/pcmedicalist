# 0x::GEN — Memory Policy

## What Is Stored
| Store | Key Pattern | Content | TTL |
|-------|------------|---------|-----|
| Redis list | `agent:0xGENbot:pending_approvals` | Queued deployment requests (JSON) | `APPROVAL_TIMEOUT_SECONDS` |
| Redis hash | `agent:0xGENbot:deploy_registry` | Completed deployment receipts (tx_hash, timestamp, type, approver) | None — permanent |
| Redis string | `agent:0xGENbot:last_deploy` | Timestamp + tx_hash of last deploy | None |
| Redis counter | `agent:0xGENbot:deployments_executed` | Lifetime successful deployments | None |
| Redis counter | `agent:0xGENbot:deployments_failed` | Lifetime failures | None |
| Redis counter | `agent:0xGENbot:deployments_rejected` | Lifetime rejections | None |
| Redis string | `agent:0xGENbot:heartbeat` | Last heartbeat ISO timestamp | None |
| Redis hash | `session:{session_id}` | Deployed session NFT metadata (address, chain, block) | None |
| Redis hash | `namespace:{ns_id}` | Registered namespace metadata | None |

## What Is NOT Stored
- Private keys, mnemonics, or signing credentials — EVER
- Unapproved request payloads longer than 48h (auto-expire from pending list)
- RPC API keys or Alchemy/Infura tokens (env-only)
- Raw requester message content

## Data Privacy
- Deployment records reference: requester_user_id (hash-anonymised), approver_user_id (hash-anonymised), tx_hash, timestamp, deployment_type
- No raw command text stored — only structured metadata

## Purge Policy
| Data Class | Automatic TTL | Manual Purge |
|-----------|--------------|--------------|
| Pending approvals | `APPROVAL_TIMEOUT_SECONDS` (default 1h) | `redis-cli del agent:0xGENbot:pending_approvals` |
| Deploy registry | No TTL — permanent | Admin only; requires documented sign-off |
| Session metadata | No TTL — permanent | Coordinated with ROOT_0xbot |

## Critical Note
**Deployment receipts are the onchain audit trail.** They MUST NOT be purged without a documented decommissioning process. These records are used for incident investigations and compliance.

## Compliance Notes
- Deployment audit records may be required for legal/compliance purposes
- External backup of `deploy_registry` recommended (nightly Redis DUMP or BGSAVE)
