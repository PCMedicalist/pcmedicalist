# 0x::OG — Operations Guide

## Build & Deploy
```bash
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d --build og-bot
```

## Logs & Diagnostics
```bash
docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f og-bot
redis-cli -u $REDIS_URL hgetall agent:OG_0xbot:metrics
redis-cli -u $REDIS_URL get agent:OG_0xbot:last_announcement
docker stats send0x-og --no-stream
```

## Restart
```bash
docker compose -f 0xCODEXbot/docker-compose.bots.yml restart og-bot
```
Verify: send `/start` from Telegram to the OG bot — expect welcome message.

## Channel Permission Check
1. Open Telegram; find target channel
2. Channel Info → Administrators → confirm OG bot has "Pin Messages" right
3. If missing: add bot as admin with pin permissions

## Rollback
```bash
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d --no-deps og-bot
```
