# 0x::GEN — Security Policy

## Secrets Inventory
| Secret | Variable | Rotation | Who Can Rotate |
|--------|----------|----------|----------------|
| Alchemy API Key | `ALCHEMY_API_KEY` | On suspicion of leak; rotate quarterly | DevOps |
| RPC provider keys | `MAINNET_RPC_URL` / `TESTNET_RPC_URL` | On infra change | DevOps |
| GEN API token | `GEN_API` | Revoke & rotate on compromise | Admin via BotFather |
| Signing endpoint credentials | `DEPLOYMENT_SIGNER` | Rotate per security policy | Security team |

## Secret Handling Rules
- Never store private keys or mnemonics in Redis, logs, or `.env`
- Prefer external signer/HSM for any signing operations
- `.env` must be gitignored and managed in secret store for production
- Keys must not be included in any alerts or logs

## Approval Gate Security
- Approver list `APPROVER_USER_IDS` must be maintained and pruned when users leave
- Approval messages must be delivered via secure Telegram admin channels
- Inline approval callbacks must validate callback identity against `APPROVER_USER_IDS`

## Testnet-First Enforcement
- `REQUIRE_TESTNET_FIRST=true` enforces testnet dry-run; this flag must not be disabled without documented override
- Testnet deployments verified by `TESTNET_VALIDATOR` service

## Emergency Response
| Severity | Example | Response |
|----------|---------|----------|
| P1 | Unauthorized deploy executed | Revoke keys; halt queue; full audit; notify legal if necessary |
| P2 | Repeated RPC failures during deploy | Halt queue; notify DevOps; open incident ticket |
| P3 | Failed testnet validation | Reject request; notify approver |

## Signing Security
- Use external signer with attestation (HSM recommended)
- Signing service must require multi-party approval for high-value actions
- Keep signing minimal — only send the signed transaction; never send private keys

## Network Security
- Restrict RPC endpoints to known IPs where possible
- Redis and internal services must be on internal Docker network only
- Do not expose admin endpoints publicly

## Auditing
- All approvals, rejections, and deployments logged immutably in `deploy_registry`
- Maintain offsite backups of registry for forensic needs
- Regular audits of `APPROVER_USER_IDS` and approval patterns
