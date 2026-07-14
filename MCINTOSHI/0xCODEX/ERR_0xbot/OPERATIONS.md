# 0x::ERR — Operations Guide

## Start / Stop / Restart
```bash
# Build image
docker compose -f 0xCODEXbot/docker-compose.bots.yml build err-bot

# Start (detached)
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d err-bot

# Stop
docker compose -f 0xCODEXbot/docker-compose.bots.yml stop err-bot

# Restart
docker compose -f 0xCODEXbot/docker-compose.bots.yml restart err-bot

# View live logs
docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f err-bot
```

## Diagnostics
```bash
# Check heartbeat
redis-cli get agent:0xERRbot:heartbeat

# View active fault registry
redis-cli hgetall agent:0xERRbot:fault_registry

# Check suppression attempts (MUST be 0)
redis-cli get agent:0xERRbot:suppression_attempts

# View recent fault log
redis-cli lrange agent:0xERRbot:fault_log 0 19

# Check circuit breakers
redis-cli --scan --pattern "network:circuit_breaker:*" | xargs redis-cli get

# Container resource usage
docker stats send0x-err
```

## Env Check (before deploy)
```bash
grep -E "(TELEGRAM_BOT_TOKEN|ERR_API|REDIS_URL|ADMIN_ALERT_CHAT_ID)" ERR_0xbot/.env
```

## Safe Restart Sequence
1. Confirm Redis is healthy (`redis-cli ping`)
2. Confirm no active P1 incidents (check `fault_registry`)
3. `docker compose restart err-bot`
4. Verify startup logs show `subscriptions_active` and `fault_registry_loaded`
5. Send test fault event to confirm alerting is working

## Redis Maintenance
```bash
# Purge resolved faults from registry (admin approval required)
redis-cli del agent:0xERRbot:fault_registry

# Purge fault log (does not affect counters)
redis-cli del agent:0xERRbot:fault_log

# Clear stale circuit breaker
redis-cli del network:circuit_breaker:{agent_name}
```

## Rollback
```bash
# Set ERR_BOT_VERSION in .env to previous tag, then:
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d --no-deps err-bot
```

## Post-Incident Checklist
After resolving any P1 fault:
1. Mark fault as resolved in registry: `/err_clear {fault_id}` (admin command)
2. Update incident log with root cause and resolution
3. Review `RULES.md` to confirm no policy violations occurred
4. Review if new fault class needs adding to classification registry
