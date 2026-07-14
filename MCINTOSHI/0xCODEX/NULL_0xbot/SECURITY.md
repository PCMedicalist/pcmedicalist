# 0x::NULL — Security Policy

## Secrets Inventory
| Secret | Variable | Rotation | Who Can Rotate |
|--------|----------|----------|----------------|
| Redis connection string | `REDIS_URL` | On infra change | DevOps |
| Admin tokens | `ADMIN_USER_IDS` | Rotate when team changes | Admins |

## Secret Handling Rules
- No secrets or private keys stored by NULL
- Admin tokens and approvals must be managed via secret store in production
- `.env` for local development only and must be gitignored

## Access Control
- Teardown commands requiring approver must validate `APPROVER_USER_IDS` via Telegram callbacks
- Admin-only endpoints limited to `ADMIN_USER_IDS`

## Incident Response
| Severity | Example | Response |
|----------|---------|----------|
| P1 | Unauthorized deletion attempt on protected namespace | Immediate halt; P1 alert; preserve evidence; notify ROOT and ERR |
| P2 | Mass unintended deletion | Halt; begin recovery using snapshots; multi-party post-incident review |
| P3 | Rate-limit bypass | Reinstate throttle; log offender; review middleware |

## Operational Safety
- Use Redis `UNLINK` for large deletes to avoid blocking
- Prefer dry-run and snapshot export before destructive operations
- Maintain offline backups of any shared-state data before mass teardowns

## Dependency Security
- Keep deletion utilities patched; audit scripts that perform deletes
