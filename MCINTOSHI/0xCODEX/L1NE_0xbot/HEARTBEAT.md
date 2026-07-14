# 0x::L1NE — Heartbeat

## Cadence
- **Interval:** `30s` (env: `HEARTBEAT_INTERVAL`, default `30`)
- **Mechanism:** Redis `PING`, EventSub callback verification, webhook replay window check
- **Persistent key:** `agent:0xL1NEbot:heartbeat` — ISO timestamp

## Metrics Emitted (Redis Keys)
| Key | Type | Description |
|-----|------|-------------|
| `agent:0xL1NEbot:heartbeat` | string | Last successful heartbeat (ISO) |
| `agent:0xL1NEbot:webhook_events` | counter | Total EventSub/webhook events processed |
| `agent:0xL1NEbot:webhook_errors` | counter | Webhook signature or processing errors |
| `agent:0xL1NEbot:siwe_bindings` | counter | Wallet bindings completed |
| `agent:0xL1NEbot:replays_detected` | counter | Replay attempts blocked |

## Startup Health Checks
- [ ] Redis reachable
- [ ] Twitch API credentials valid (`TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`)
- [ ] EventSub secret present and verified (`TWITCH_EVENTSUB_SECRET`)
- [ ] Webhook callback endpoint reachable (public URL or tunnel)
- [ ] SIWE config present if wallet linking enabled

## Runtime Alert Thresholds
| Condition | Threshold | Response |
|-----------|-----------|----------|
| Missed heartbeats | ≥ 3 | Emit ERR alert; page on-call |
| Signature failures | > 5/min | Log warn; check webhook secret rotation |
| Replay attempts | Any | Increment `replays_detected`; block sender IP |
| SIWE failure rate | > 10% over 10 min | Log warn; notify admin |

## Escalation Path
1. Check logs: `docker compose logs -f l1ne-bot`
2. Verify EventSub subscriptions via Twitch dev console
3. Inspect replay attempt keys: `redis-cli get agent:0xL1NEbot:replays_detected`
4. Restart container if necessary
