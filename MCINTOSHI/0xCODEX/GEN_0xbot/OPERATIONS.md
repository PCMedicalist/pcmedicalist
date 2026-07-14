# 0x::GEN — Operations Guide

## Start / Stop / Restart
```bash
# Build image
docker compose -f 0xCODEXbot/docker-compose.bots.yml build gen-bot

# Start (detached)
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d gen-bot

# Stop
docker compose -f 0xCODEXbot/docker-compose.bots.yml stop gen-bot

# Restart
docker compose -f 0xCODEXbot/docker-compose.bots.yml restart gen-bot

# View live logs
docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f gen-bot
```

## Diagnostics
```bash
# Check heartbeat
redis-cli get agent:0xGENbot:heartbeat

# Pending approvals
redis-cli lrange agent:0xGENbot:pending_approvals 0 -1

# Deploy registry tail
redis-cli hgetall agent:0xGENbot:deploy_registry | tail -n 20

# Check recent failures
redis-cli get agent:0xGENbot:deployments_failed

# Container resource usage
docker stats send0x-gen
```

## Approval Flow
- New request: `POST /deploy` → push to `agent:0xGENbot:pending_approvals`
- Notifies approvers via Telegram
- Approver approves via inline callback (Approve/Reject)
- On approval: GEN validates, testnet dry-run, then executes mainnet deploy if validated

## Safe Restart Sequence
1. Ensure Redis healthy (`redis-cli ping`)
2. Ensure no active pending approvals (or pause new requests)
3. `docker compose restart gen-bot`
4. Run smoke test deployment on testnet to verify system integrity

## Emergency Halt
If compromise or unexpected behavior detected:
1. Set `network:circuit_breaker:GEN_0xbot` = 1 (via Redis)
2. Notify ROOT and ERR
3. Halt processing and require manual admin intervention

## Rollback
- Application rollback: `docker compose up -d --no-deps gen-bot:<previous-tag>`
- Onchain rollbacks are impossible; ensure testnet-first before mainnet

## Backup
- Nightly snapshot of `deploy_registry` via Redis BGSAVE or export
- Export list of pending approvals for audit before clearing queues
