# 0x::L1NE — Memory Policy

## What Is Stored
| Store | Key Pattern | Content | TTL |
|-------|------------|---------|-----|
| Redis hash | `session:{session_id}:wallet_binding` | `address_hash`, `timestamp`, `method` | None (short-lived for session) |
| Redis string | `agent:0xL1NEbot:heartbeat` | Last heartbeat ISO timestamp | None |
| Redis counter | `agent:0xL1NEbot:webhook_events` | Total events processed | None |
| Redis counter | `agent:0xL1NEbot:replays_detected` | Replay attempts | None |
| Redis string | `siwe:nonce:{nonce}` | SIWE nonce mapping to session | TTL 10min |
| Redis list | `agent:0xL1NEbot:recent_webhooks` | Last N webhook signatures (for replay detection) | 1h capped

## What Is NOT Stored
- Raw chat content or full webhook payloads containing user messages
- Private keys or OAuth tokens
- Full SIWE messages beyond nonce mapping

## Purge Policy
- `siwe:nonce:{nonce}` auto-expires (10min)
- `recent_webhooks` trimmed to last 1000 entries
- Wallet bindings for ephemeral sessions removed on logout

## Data Privacy
- Wallet addresses stored only as hash (`sha256(address)`) and associated metadata, never raw address unless explicitly required and stored in secure vault
- No PII stored

## Compliance Notes
- SIWE flows must not be logged with raw nonce or signature fields
- Maintain minimal storage required for binding verification
