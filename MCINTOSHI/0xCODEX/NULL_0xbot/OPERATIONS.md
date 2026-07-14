# 0x::NULL — Operations Guide

## Start / Stop / Restart
```bash
# Build image
docker compose -f 0xCODEXbot/docker-compose.bots.yml build null-bot

# Start (detached)
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d null-bot

# Stop
docker compose -f 0xCODEXbot/docker-compose.bots.yml stop null-bot

# Restart
docker compose -f 0xCODEXbot/docker-compose.bots.yml restart null-bot

# View live logs
docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f null-bot
```

## Diagnostics
```bash
# Check heartbeat
redis-cli get agent:0xNULLbot:heartbeat

# Recent teardown receipts
redis-cli lrange agent:0xNULLbot:teardown_receipts 0 9

# Check paused flag
redis-cli get agent:0xNULLbot:paused

# Count teardowns
redis-cli get agent:0xNULLbot:teardowns
```

## Safe Teardown Sequence (manual)
1. Run dry-run: `python scripts/simulate_teardown.py --pattern "session:*-temp" --dry-run`
2. Export snapshot (optional): `python scripts/export_keys.py --pattern "session:*-temp" --out snapshot.json`
3. Request approver sign-off (if shared-state): obtain approver hash and set `APPROVER_ID_HASH`
4. Execute batch delete with rate limiting: `python scripts/execute_teardown.py --pattern "session:*-temp"`
5. Verify receipts: `redis-cli lrange agent:0xNULLbot:teardown_receipts 0 9`

## Emergency Pause
```bash
# Pause teardowns
redis-cli set agent:0xNULLbot:paused 1

# Resume teardowns
redis-cli del agent:0xNULLbot:paused
```

## Rollback / Recovery
- Deleted ephemeral data may be irrecoverable; rely on pre-teardown snapshots for recovery
- For accidental deletion of important shared state, notify ROOT and ERR immediately
