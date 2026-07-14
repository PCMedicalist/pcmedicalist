# 0x::L1NE — Tools & Integrations

## Required Environment Variables
| Variable | Description | Source |
|----------|-------------|--------|
| `TWITCH_CLIENT_ID` | Twitch app client id | `.env` |
| `TWITCH_CLIENT_SECRET` | Twitch app client secret | Secret store |
| `TWITCH_EVENTSUB_SECRET` | Secret used to sign EventSub callbacks | `.env` |
| `REDIS_URL` | Redis connection string | `.env` |
| `SIWE_DOMAIN` | Domain used in SIWE messages | `.env` |

## Optional Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `EVENT_RATE_LIMIT` | Max events per minute per source | `200` |
| `LOG_LEVEL` | Structlog level | `INFO` |
| `WEBHOOK_PUBLIC_URL` | Public callback URL for EventSub | (required for production) |

## Integrations
- Twitch EventSub / Webhooks — subscribe to channel events
- SIWE — wallet linking flows; nonces stored in Redis
- Redis — event queueing and dedup/replay caches
- Optional: Sentry for error reporting

## Webhook Handling
- Validate `Twitch-Eventsub-Message-Signature` header using HMAC-SHA256 with `TWITCH_EVENTSUB_SECRET`
- Maintain short-lived cache of recent signatures to prevent replay
- Respond to challenge verification during subscription handshake

## SIWE Integration
- Generate nonce: store `siwe:nonce:{nonce}` → session id, TTL 10min
- Verify SIWE message signature on callback and then store hashed wallet binding
- Do not log raw SIWE messages or signatures

## Developer Tools
- Local testing: `ngrok` or similar to expose local callback URL
- Replay tool: `scripts/replay_webhooks.py` to test new schema handlers

## Future Integrations
- Rate-limit controller service for global event throttling
- IP blocklist integration for suspicious sources
