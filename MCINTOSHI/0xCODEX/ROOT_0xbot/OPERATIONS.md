# 0x::ROOT — Operations Guide

## Start / Stop / Restart
```bash
# Build image
docker compose -f 0xCODEXbot/docker-compose.bots.yml build root-bot

# Start (detached)
docker compose -f 0xCODEXbot/docker-compose.bots.yml up -d root-bot

# Stop
docker compose -f 0xCODEXbot/docker-compose.bots.yml stop root-bot

# Restart
docker compose -f 0xCODEXbot/docker-compose.bots.yml restart root-bot

# View live logs
docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f root-bot
```

## Diagnostics
```bash
# Check heartbeat
redis-cli get agent:0xROOTbot:heartbeat

# ACL snapshot
redis-cli get agent:0xROOTbot:last_acl_snapshot

# Recent ACL changes
redis-cli lrange agent:0xROOTbot:acl_change_log 0 9
```

## Safe Role Change Sequence
1. Propose role change and generate change package
2. Obtain approver signatures (record approver_id_hash)
3. Apply change in staged environment and validate
4. Apply to production and emit audit record

## Emergency Revocation
- Follow documented emergency plan: isolate affected credentials, rotate related secrets, and notify stakeholders
