# PCMedicalist x402 Skills — Deployment Runbook

Prod-ready reference for the 13 PCMedicalist platform-engineering x402 endpoints on Bankr x402 Cloud.

## Architecture
- **Primary (live):** Bankr-hosted endpoints at `https://x402.bankr.bot/<WALLET>/<service>`
  - WALLET (endpoint owner / payer for tests): `0xd8f369f47eba08c29a024b64a52d2bbedbe252b0`
- **Branded facade (planned):** `api.pcmedicalist.com` proxies to Bankr + failover to Bankr direct.
  Bankr API key stays server-side only (env, never in repo).
- **Treasury (earnings pay-to):** `0x63603ffEC1e771d914119eF74ecDf4b15C9CCAc5`
  — set per-endpoint in the Bankr x402 dashboard "Edit pay-to address". Config `payTo` only
    applies at FIRST creation; later changes MUST be done in the dashboard.

## Services (13)
discovery ($0.01), security-fundamentals ($0.50), database-deep-dive ($0.50),
distributed-patterns ($0.40), resilience-engineering ($0.40), caching-strategies ($0.40),
http-protocol ($0.40), networking-infra ($0.40), infrastructure-ops ($0.50),
messaging-semantics ($0.40), event-driven-architecture ($0.40),
platform-engineering-index ($0.01), skills-pro ($4.00).

## Local project
`/home/pcmedicalist/pcmedicalist/pcmedicalist-skills-x402/`
- `bankr.x402.json` — service config: price, method, files, schema, category, tags.
- `x402/<service>/index.ts` — self-contained handler (inline receipt capture, NO shared imports —
  Bankr bundles per-service and does not resolve `../` parent imports; that caused 500s).
- `receipts_ledger.py` — local-only ledger (superseded by in-handler `ctx.files` receipt; kept for reference).

## Deployment
```bash
cd /home/pcmedicalist/pcmedicalist/pcmedicalist-skills-x402
# Bankr key must have BOTH Wallet API + Agent API scopes (bankr.bot/api-keys)
bankr x402 deploy <service>      # per-service (preferred; bulk 13-at-once 413s)
# DO NOT: `bankr x402 deploy` with all 13 — total bundle > payload cap → 413
```
Rate limit: 20 deploys/hour/IP. Per-service handler source cap 1 MB (skills-pro inlined at ~4 KB).

## In-handler receipt capture
Each handler calls `recordReceipt(ctx?.files, svc, price, req)` BEFORE returning:
- Reads `x-402-payer` header (Bankr-set, trusted) → payer wallet.
- Appends `{ ts, endpoint, payer, amountUsdc, note }` to `/x402/<svc>/receipts.json` via `ctx.files`.
- `ctx.files` enabled per-service in `bankr.x402.json` (`files.enabled: true`, roots `/x402/<svc>`).
- On-chain tx hash is NOT in the handler — it surfaces in Bankr dashboard Request Logs / Base scan.

## Payment flow (verified)
1. `curl <url>` → HTTP 402 + PaymentRequirements (amount in atomic USDC, network eip155:8453, facilitator api.bankr.bot/facilitator).
2. Payer wallet signs + retries → Bankr verifies (EIP-712) + settles on-chain AFTER a 200 response (settle-after-response).
3. Platform fee (5% after first 1,000 free reqs/mo) split out on-chain; remainder → endpoint pay-to.
4. Revenue appears in dashboard; Request Logs show payer + settlement status + error.

## Verification gate (DO NOT SKIP before live test)
After any dashboard pay-to edit, re-GET the 402 and confirm:
`payTo == 0x63603ffEC1e771d914119eF74ecDf4b15C9CCAc5`
Only then run a paid call — otherwise funds route to Bankr's default pay-to.

## Gotchas (hard-won)
- `bankr x402 call` swallows settlement errors (just "400 x402 payment failed"). Root-cause via dashboard Request Logs.
- Shared `../` imports → 500 at bundle. Keep handlers self-contained.
- 413 = bundle too large (bulk deploy or >1 MB handler). Fix: per-service deploy / shrink handler.
- `price: 0` → 500 "payment configuration error". Use a tiny non-zero price ($0.01).

## Security
- Bankr key file `~/.bankr/config.json` is `chmod 600`, OUTSIDE any git repo. Never commit.
- No secrets in skill handlers (read-only skills). Encrypted env vars via `bankr x402 env set` if ever needed.
- GitHub org-wide search for `bk_usr_`/`BANKR_API_KEY`/`CDP_*`/PEMs = 0 matches (verified).
