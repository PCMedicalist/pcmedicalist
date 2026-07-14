# 0x::CODEX — Operations Guide

## Build & Deploy
```bash
# Build image only
docker compose -f 0xCODEXbot/docker-compose.bots.yml build codex-bot

# Start detached
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d codex-bot

# Rebuild and start
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d --build codex-bot
```

## Start / Stop / Restart
```bash
# Stop
docker compose -f 0xCODEXbot/docker-compose.bots.yml stop codex-bot

# Restart (safe for single-instance Telegram polling)
docker compose -f 0xCODEXbot/docker-compose.bots.yml restart codex-bot

# View live logs (Ctrl+C to detach)
docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f codex-bot
```

## Safe Restart Sequence
1. Verify Redis is healthy: `redis-cli -u $REDIS_URL ping`
2. Check signal queue is low: `redis-cli -u $REDIS_URL llen agent:0xCODEXbot:signals`
3. Restart: `docker compose restart codex-bot`
4. Confirm startup in logs: look for `handlers_registered`
5. Smoke test: send `/start` from Telegram — expect welcome message

## Diagnostics
```bash
# Check all CODEX metrics
redis-cli -u $REDIS_URL hgetall agent:0xCODEXbot:metrics

# Signal queue depth
redis-cli -u $REDIS_URL llen agent:0xCODEXbot:signals

# Last heartbeat
redis-cli -u $REDIS_URL get agent:0xCODEXbot:heartbeat

# Last scan timestamp
redis-cli -u $REDIS_URL get agent:0xCODEXbot:last_scan

# Container resource usage
docker stats send0x-codex --no-stream
```

## Env Verification (before deploy)
```bash
grep -E "(TELEGRAM_BOT_TOKEN|CODEX_API|REDIS_URL)" 0xCODEXbot/.env
```

## Redis Maintenance
```bash
# Emergency drain signal queue
redis-cli -u $REDIS_URL del agent:0xCODEXbot:signals

# Purge all user session keys (destructive — use with care)
redis-cli -u $REDIS_URL --scan --pattern "user:*" | xargs redis-cli -u $REDIS_URL del
```

## Rollback
```bash
# Pin a previous image tag (set CODEX_IMAGE_TAG in environment first)
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d --no-deps codex-bot
```
Document the rollback in the incident log.

## Monitoring Dashboard Links
- Container logs: Docker Desktop → `send0x-codex` → Logs
- Redis metrics: `redis-cli -u $REDIS_URL hgetall agent:0xCODEXbot:metrics`
- Error reports: see ERR_0xbot Telegram channel
