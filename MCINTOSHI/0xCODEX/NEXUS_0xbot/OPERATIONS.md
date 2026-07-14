# 0x::NEXUS — Operations Guide

## Start / Stop / Restart
```bash
# Build image
docker compose -f 0xCODEXbot/docker-compose.bots.yml build nexus-bot

# Start (detached)
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d nexus-bot

# Stop
docker compose -f 0xCODEXbot/docker-compose.bots.yml stop nexus-bot

# Restart
docker compose -f 0xCODEXbot/docker-compose.bots.yml restart nexus-bot

# View live logs
docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f nexus-bot
```

## Diagnostics
```bash
# Check heartbeat
redis-cli get agent:0xNEXUSbot:heartbeat

# Last snapshot
redis-cli get agent:0xNEXUSbot:last_snapshot

# Recent recommendations
redis-cli lrange agent:0xNEXUSbot:recommendation_log 0 9

# Coordination run count
redis-cli get agent:0xNEXUSbot:coordination_runs
```

## Safe Restart Sequence
1. Pause new coordination runs (`redis-cli set agent:0xNEXUSbot:paused 1`)
2. Restart container
3. Validate snapshot ingestion from key agents
4. Unpause when healthy

## Emergency Steps
- If cascade detected: set `network:pause` and notify ERR and ROOT
- Use replay tool to reprocess last-known good snapshot for debugging
