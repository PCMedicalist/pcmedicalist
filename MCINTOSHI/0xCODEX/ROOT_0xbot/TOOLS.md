# 0x::ROOT — Tools & Integrations

## Required Environment Variables
| Variable | Description | Source |
|----------|-------------|--------|
| `REDIS_URL` | Redis connection string | `.env` |
| `AGENT_REGISTRY_URL` | URL to discover agent metadata | `.env` |
| `ADMIN_USER_IDS` | Admin Telegram IDs | `.env` |

## Optional Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DID_RESOLVER_URL` | DID resolver endpoint | (optional) |
| `ANCHOR_CHAIN_RPC` | RPC for anchoring credentials (optional) | (optional) |

## Integrations
- DID/ENS resolver for identity verification
- Redis for ACL and credential registry storage
- Optional anchoring service for onchain proofs
- Telegram for admin approvals and notifications

## Developer Tools
- `scripts/anchor_credential.py` for test anchoring flows (dry-run)
- `scripts/export_acl_snapshot.py` to produce an ACL snapshot for auditing

## Safety Tools
- Approval middleware enforcing `APPROVER_USER_IDS`
- Snapshot and rollback utilities for ACL changes
