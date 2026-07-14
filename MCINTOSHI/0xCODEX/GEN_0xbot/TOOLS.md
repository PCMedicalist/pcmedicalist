# 0x::GEN — Tools & Integrations

## Required Environment Variables
| Variable | Description | Source |
|----------|-------------|--------|
| `GEN_API` | Internal API token for GEN bot (Telegram or internal RPC) | `.env` |
| `REDIS_URL` | Redis connection string | `.env` |
| `ALCHEMY_API_KEY` | Alchemy key for deployments | `.env` or secret store |
| `REQUIRE_TESTNET_FIRST` | Enforce testnet-first policy | `.env` (default `true`)
| `APPROVER_USER_IDS` | Comma-separated list of approver Telegram IDs | `.env` (required)

## Optional Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `TESTNET_RPC_URL` | RPC endpoint for testnet deployments | (required for testnet) |
| `MAINNET_RPC_URL` | RPC endpoint for mainnet deployments | (required for production) |
| `APPROVAL_TIMEOUT_SECONDS` | Timeout for approver response | `3600` |
| `LOG_LEVEL` | Structlog output level | `INFO` |
| `DEPLOYMENT_SIGNER` | HSM or external signer endpoint | (preferred over local keys) |

## Deployment Providers
- Primary: Alchemy/Infura — set `ALCHEMY_API_KEY` in `.env`
- Fallback: local RPC nodes (configured via `MAINNET_RPC_URL`/`TESTNET_RPC_URL`)
- Signing: use HSM/external signer; never store private keys locally

## Redis Integration
- Namespaces used: `agent:0xGENbot:*`, `agent:0xGENbot:pending_approvals`, `agent:0xGENbot:deploy_registry`
- Use Redis list for pending approvals, hash for deploy registry

## Telegram Integration
- Admin/approver notifications sent via Telegram using `GEN_API` token
- Approval flow implemented as interactive messages with inline buttons (Approve/Reject)

## Observability & Auditing
- Recommend Sentry for error capturing (`SENTRY_DSN`)
- Prometheus metrics: expose deployment counters
- Nightly backup of `deploy_registry` recommended

## Safety Tools
- `APPROVAL_GUARD` middleware to prevent self-approval
- `TESTNET_VALIDATOR` to verify testnet receipt before allowing mainnet
- `DEPLOYMENT_SANDBOX` for dry-run simulations

## Future Integrations
- Multi-signature wallet integration for high-value deployments
- Hardware signer orchestration via secure signing service
