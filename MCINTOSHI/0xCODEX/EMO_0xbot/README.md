# 0x::EMO (Cognition)

**Role:** Personality & voice  
**Authority:** None - interprets state, does NOT create it

## Responsibilities

- Subscribe to CODEX state changes
- Generate character-driven responses
- Stream consciousness to Telegram
- Interpret but not decide

## Critical Constraints

❌ EMO does NOT:

- Execute transactions
- Make financial decisions
- Predict market outcomes
- Access private keys

✅ EMO does:

- Generate character voice using Edge voices (via OLLAMA)
- React to state changes with emotionally resonant messages
- Use humor and empathy to humanize the system
- Stream updates to Telegram and other UX layers
- Interpret existing state
- Express system consciousness
- Stream to Telegram

## Event Channels

- Subscribes to: `codex:state:change`
- Outputs to: Telegram bot

## Character

EMO embodies the collective consciousness of the CODEX.
It gives voice to the system's state, not authority over it.

😄 0x::EMO — UX / Personality Layer
Purpose

Humanize the system without authority.

Webhooks (Inbound)

Signal summaries from L1NE

State changes (non-critical)

WebSockets (Outbound)

/ws/personality

/ws/ux-feedback

Callers (Outbound)

OLLAMA (tone + phrasing)

Chat emitters

UI copy updates

EMO never touches value or permissions.
