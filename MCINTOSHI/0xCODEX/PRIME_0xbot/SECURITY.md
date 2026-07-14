# 0x::PRIME — Security Policy

## Secrets Inventory
| Secret | Variable | Rotation | Who Can Rotate |
|--------|----------|----------|----------------|
| Feed API keys | `MARKET_FEED_KEYS` | Rotate on compromise | DevOps |
| Redis connection string | `REDIS_URL` | On infra change | DevOps |
| Model credentials | `MODEL_CREDENTIALS` | Per provider policy | DevOps |

## Secret Handling Rules
- Feed keys and model credentials stored in secret store; not in source
- Do not log keys, raw feed payloads, or model tokens
- Access to feeds must be audited and limited

## Data Integrity
- Validate checksums or signed data where feed provides integrity guarantees
- Reject feeds with inconsistent timestamps or signature mismatches

## Incident Response
| Severity | Example | Response |
|----------|---------|----------|
| P1 | Compromised feed producing adversarial signals | Pause PRIME; notify ERR and ROOT; investigate; switch to backup feeds |
| P2 | Model poisoning detected | Revert model; restore from validated checkpoint; audit ingestion pipeline |
| P3 | Unauthorized access to metrics | Audit access logs; rotate credentials

## Network Security
- Restrict feed endpoints and allowlist IPs where possible
- Keep internal services (Redis, model servers) on private network only

## Dependency Security
- Run `pip-audit` on requirements and update vulnerable packages promptly
