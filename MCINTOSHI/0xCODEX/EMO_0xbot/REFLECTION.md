# 0x::EMO — Reflection & Introspection

## Self-Check Schedule

| Check | Frequency | Output |

|-------|-----------|--------|

| Reaction emission rate | Every 5 min | Logged to stdout |
| OpenAI error rate | Every 10 min | Alert if > 10% |
| Rate limiter drop rate | Every 5 min | Log warn if > 50/min |
| Redis subscription health | On reconnect | Log status |
| Heartbeat | Every 30s | Redis key updated |

## Anomaly Detection

| Anomaly | Indicator | Response |

|---------|-----------|----------|

| Reaction flood | > 200 reactions/min | Log warn; check upstream event volume |
| Repeated OpenAI errors | > 5 consecutive 5xx | Degrade to emoji-only; alert |
| Subscription silent period | No events for > 10 min | Log warn — may indicate upstream issue |
| Sentiment always neutral | > 100 consecutive neutral reactions | Log warn; review prompt library |

## Introspection Output

EMO does not expose user-facing introspection commands (no Telegram polling).
Internal state can be observed via:

- Redis keys: `redis-cli keys agent:0xEMObot:*`
- Docker logs: `docker compose logs emo-bot`

## Audit Log Schema

Each reaction event emits a structured log entry:

```json
{
  "event": "reaction_emitted",
  "event_type": "milestone_hit",
  "reaction_category": "celebration",
  "bot": "0xEMObot",
  "timestamp": "2026-03-21T22:00:00Z",
  "openai_used": true
}
```

## Review Cadence

- **Daily:** automated log scan for OpenAI error spikes
- **Weekly:** admin review of reaction rate and drop rate trends
- **Monthly:** review emotional response categories against community feedback
