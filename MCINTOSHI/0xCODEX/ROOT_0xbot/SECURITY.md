# 0x::ROOT — Security Policy

## Secrets Inventory
| Secret | Variable | Rotation | Who Can Rotate |
|--------|----------|----------|----------------|
| Redis connection string | `REDIS_URL` | On infra change | DevOps |
| DID resolver credentials | `DID_RESOLVER_URL` auth | Per provider policy | DevOps |
| Admin tokens | `ADMIN_USER_IDS` | Rotate when team changes | Admins |

## Secret Handling Rules
- No private keys stored by ROOT; signing delegated to HSM/external signer
- Secrets managed in secret store; `.env` only for local dev and gitignored
- Access to credential registry audited

## Incident Response
| Severity | Example | Response |
|----------|---------|----------|
| P1 | Unauthorized credential anchoring | Revoke anchors if possible; halt issuance; notify security and legal |
| P2 | ACL registry tampering | Isolate registry; restore from snapshot; audit access |
| P3 | DID resolver compromise | Switch resolver; revalidate anchors

## Access Controls
- Admin endpoints require multi-factor and approver checks
- Approver list maintained and audited regularly

## Auditing
- All anchor and ACL deltas logged append-only and exported for offline audit

## Dependency Security
- Keep DID/anchor libraries updated; run `pip-audit` regularly
