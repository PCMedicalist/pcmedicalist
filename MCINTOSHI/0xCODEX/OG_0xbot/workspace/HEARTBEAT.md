# 0x::OG — Heartbeat

## Cadence
- **Interval:** `30s` (env: `HEARTBEAT_INTERVAL`)
- **Persistent key:** `agent:OG_0xbot:heartbeat`

## Metrics Emitted
| Key | Type | Description |
|-----|------|-------------|
| `agent:OG_0xbot:heartbeat` | string | Last successful heartbeat (ISO) |
| `agent:OG_0xbot:post_count` | counter | Public messages sent |
| `agent:OG_0xbot:announcement_count` | counter | Announcements broadcast |
| `agent:OG_0xbot:last_announcement` | string | Timestamp of last broadcast |
| `agent:OG_0xbot:metrics` | hash | Engagement KPIs |

## Startup Health Checks
- [ ] Redis reachable
- [ ] Telegram token valid (`OG_API`)
- [ ] Target channel IDs configured (`PIN_CHAT_ID`, `SCHEDULED_CHAT_ID` if set)
- [ ] Bot has "Pin Messages" permission in target channel (if pinning enabled)

## Alert Thresholds
| Condition | Threshold | Response |
|-----------|-----------|---------|
| Consecutive missed heartbeats | ≥ 3 | Page on-call; emit ERR signal |
| Channel write failure | 2 consecutive | Alert admin; log incident |
| Announcement queue stall | > 10 min with items queued | Alert |

## Escalation Path
1. `docker compose logs -f og-bot`
2. `redis-cli hgetall agent:OG_0xbot:metrics`
3. Verify bot channel admin rights in Telegram
