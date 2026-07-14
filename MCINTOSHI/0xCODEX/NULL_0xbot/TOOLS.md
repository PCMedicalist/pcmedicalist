# 0x::NULL — Tools & Integrations

## Required Environment Variables
| Variable | Description | Source |
|----------|-------------|--------|
| `REDIS_URL` | Redis connection string | `.env` |
| `ADMIN_USER_IDS` | Admin Telegram IDs for approval workflows | `.env` |
| `PROTECTED_NAMESPACES` | Comma-separated key patterns not to touch | `.env` |

## Optional Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `TEARDOWN_RATE_LIMIT` | Keys per minute for automated teardowns | `1000` |
| `LOG_LEVEL` | Structlog level | `INFO` |

## Integrations
- Redis — primary store for tear-down operations and receipts
- Telegram — admin approval and notifications (admin-only)
- ERR_0xbot — route unauthorized or suspicious attempts

## Teardown Utilities
- `dry_run` mode to list keys that would be deleted without executing
- `snapshot_export` to export keys matching pattern before deletion (optional; store offsite)
- `batch_delete` helper using `UNLINK` for safe asynchronous deletion

## Developer Tools
- `scripts/simulate_teardown.py` for dry-run testing
- `scripts/export_receipts.sh` to archive receipts

## Safety Tools
- `PROTECTED_NAMESPACES` enforcement middleware
- Approval guard for shared-state teardowns
- Rate limiter middleware
