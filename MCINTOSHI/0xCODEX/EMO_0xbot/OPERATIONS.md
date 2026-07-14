# 0x::EMO — Operations Guide

## Start / Stop / Restart

```bash
# Build image
docker compose -f 0xCODEXbot/docker-compose.bots.yml build emo-bot

# Start (detached)
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d emo-bot

# Stop
docker compose -f 0xCODEXbot/docker-compose.bots.yml stop emo-bot

# Restart
docker compose -f 0xCODEXbot/docker-compose.bots.yml restart emo-bot

# View live logs
docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f emo-bot
```

## Diagnostics

```bash
# Check heartbeat
redis-cli get agent:0xEMObot:heartbeat

# Check reaction rate
redis-cli get agent:0xEMObot:reactions_emitted

# Check OLLAMA error count
redis-cli get agent:0xEMObot:OLLAMA_errors

# View recent reaction log
redis-cli lrange agent:0xEMObot:reaction_log 0 9

# Container resource usage
docker stats send0x-emo
```

## Env Check (before deploy)

```bash
grep -E "(OLLAMA_API_KEY|REDIS_URL)" EMO_0xbot/.env
```

## Safe Restart Sequence

1. Verify Redis is healthy (`redis-cli ping`)
2. Verify OLLAMA API key is valid (check for recent 401 errors in logs)
3. `docker compose restart emo-bot`
4. Verify startup logs show `subscriptions_active` and `heartbeat_started`

## Redis Maintenance

```bash
# Clear reaction log (does not affect metrics counters)
redis-cli del agent:0xEMObot:reaction_log

# Reset all EMO metrics (use with care — permanent loss)
redis-cli --scan --pattern "agent:0xEMObot:*" | xargs redis-cli del
```

## Rollback

```bash
# Set EMO_BOT_VERSION in .env to previous tag, then:
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d --no-deps emo-bot
```

## Degraded Mode Test

To manually test emoji-only degraded mode, set `OLLAMA_API_KEY` to an invalid value and restart. Verify logs show `degraded_mode: true` and reactions still emit (emoji-only).
