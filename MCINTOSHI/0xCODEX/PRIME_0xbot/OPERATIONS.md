# 0x::PRIME — Operations Guide

## Start / Stop / Restart
```bash
# Build image
docker compose -f 0xCODEXbot/docker-compose.bots.yml build prime-bot

# Start (detached)
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d prime-bot

# Stop
docker compose -f 0xCODEXbot/docker-compose.bots.yml stop prime-bot

# Restart
docker compose -f 0xCODEXbot/docker-compose.bots.yml restart prime-bot

# View live logs
docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f prime-bot
```

## Diagnostics
```bash
# Check heartbeat
redis-cli get agent:0xPRIMEbot:heartbeat

# Recent observations
redis-cli lrange agent:0xPRIMEbot:recent_observations 0 9

# Confidence histogram snapshot
redis-cli get agent:0xPRIMEbot:confidence_histogram

# Feed health checks (example)
curl -fsS ${FEED_URL}/health || echo "feed down"
```

## Safe Restart Sequence
1. Pause observation publication (`redis-cli set agent:0xPRIMEbot:paused 1`)
2. Restart container
3. Validate feed ingestion and baseline comparison
4. Unpause when stable

## Rollback
- Application rollback: `docker compose up -d --no-deps prime-bot:<previous-tag>`
- Model rollback: revert model pointer and restart service
