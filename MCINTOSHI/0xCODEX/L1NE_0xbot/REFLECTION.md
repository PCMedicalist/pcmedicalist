# 0x::L1NE — Reflection & Introspection

## Self-Check Schedule
| Check | Frequency | Output |
|-------|-----------|--------|
| Webhook signature verification rate | Every 5 min | Log failure rate; alert if > 1% |
| SIWE binding success rate | Every 10 min | Log and alert if low |
| Replay detection | Continuous | Increment `replays_detected` on detection |
| Heartbeat | Every 30s | Redis key updated |

## Anomaly Detection
| Anomaly | Indicator | Response |
|---------|-----------|----------|
| Signature spike failures | Sudden increase in signature verification failures | Alert; rotate secret if suspected compromise |
| Replay flood | > 10 replay attempts/min | Block source IP/rate limit upstream |
| Unexpected event types | Unrecognised event schema | Log warn; route to ERR for analysis |

## Introspection Tools
- `redis-cli lrange agent:0xL1NEbot:recent_webhooks 0 9`
- `redis-cli get agent:0xL1NEbot:heartbeat`
- Check EventSub subscription status in Twitch developer console

## Audit Log Schema
```json
{
  "event": "webhook_received",
  "event_type": "channel.follow",
  "signature_valid": true,
  "replay_detected": false,
  "timestamp": "2026-03-21T22:00:00Z"
}
```

## Review Cadence
- Weekly review of webhook failure trends
- Monthly review of SIWE success and binding lifecycle
