# 0x::L1NE — Operations Guide

## Start / Stop / Restart
```bash
# Build image
docker compose -f 0xCODEXbot/docker-compose.bots.yml build l1ne-bot

# Start (detached)
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d l1ne-bot

# Stop
docker compose -f 0xCODEXbot/docker-compose.bots.yml stop l1ne-bot

# Restart
docker compose -f 0xCODEXbot/docker-compose.bots.yml restart l1ne-bot

# View live logs
docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f l1ne-bot
```

## Diagnostics
```bash
# Check heartbeat
redis-cli get agent:0xL1NEbot:heartbeat

# Recent webhook signatures
redis-cli lrange agent:0xL1NEbot:recent_webhooks 0 9

# SIWE nonces
redis-cli keys "siwe:nonce:*"

# Check EventSub subscription status via Twitch dev console or API
```

## Webhook Secret Rotation
1. Generate new `TWITCH_EVENTSUB_SECRET` in secret store
2. Update `.env` and deploy
3. Re-subscribe EventSub callbacks (or rotate via API)
4. Monitor signature verification rates for anomalies

## Local Testing
- Use `ngrok http 8000` to expose `WEBHOOK_PUBLIC_URL`
- Run `scripts/replay_webhooks.py recorded_sample.json` to validate handlers

## Emergency Steps
- If replay attacks detected: set `agent:0xL1NEbot:blocked_sources` and block IPs at network edge
- If webhook flood: enable throttle and notify admin
