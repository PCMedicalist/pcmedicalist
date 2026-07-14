# 0x::L1NE (Operator)

**Role:** Signal intake gateway  
**Authority:** None - emits events only

## Responsibilities
- Receive Twitch EventSub webhooks
- Receive Telegram bot updates
- Normalize all external signals
- Publish to Redis event bus
- NO execution authority

## Endpoints
- `POST /webhook/twitch` - Twitch EventSub
- `POST /webhook/telegram` - Telegram updates
- `GET /health` - Health check

## Event Channels
- `codex:signals:twitch` - Normalized Twitch events
- `codex:signals:telegram` - Normalized Telegram events

## Security
- Verifies Twitch HMAC signatures
- Verifies Telegram webhook secrets
- Rate-limited endpoints
- No private keys stored


🧠 0x::L1NE — Operator / Signal Router
Purpose

Translate everything → deterministic signals.

Webhooks (Inbound)

Twitch EventSub:

chat messages

commands

extensions

donations (non-custodial)

Telegram Bot:

messages

commands

Internal agent events

WebSockets (Outbound)

/ws/signals

/ws/alerts

/ws/ui-feed

Callers (Outbound)

Signal normalization engine

Queue publisher

Permission checks via ROOT

Optional AI summarizer (OpenAI)

This is the busiest agent.