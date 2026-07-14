# 0x::L1NE — Example Interactions & Test Vectors

## Example: User requests wallet link (`!wallet`)
**Flow:**
1. User types `!wallet` in chat → frontend sends event to L1NE
2. L1NE generates SIWE nonce `n123` and stores `siwe:nonce:n123` → session
3. L1NE replies with SIWE message template and instructions
4. User signs SIWE message and posts signature to callback endpoint
5. L1NE verifies signature, stores `sha256(address)` binding, and emits `wallet_bound` signal

**Redis writes:** `siwe:nonce:n123` (TTL 10min), `session:{id}:wallet_binding`

---

## Example: EventSub channel.follow
**Input webhook:** EventSub `channel.follow` payload with signature header
**Expected:** Signature valid → sanitized event emitted to Redis `event:channel.follow` with normalized fields

---

## Replay Attack Test
**Input:** Duplicate webhook with identical signature and recent timestamp
**Expected:** Rejected; `replays_detected` INCR; blocked source logged

---

## Malformed Webhook
**Input:** Missing signature header or invalid JSON
**Expected:** Rejected; `webhook_errors` INCR; routed to ERR_0xbot with `error_class: malformed_webhook`

---

## Webhook Subscription Challenge
**Input:** Twitch subscription verification challenge request
**Expected:** Respond with challenge token to confirm subscription

---

## Security Test: Secret Rotation
**Action:** Rotate `TWITCH_EVENTSUB_SECRET` and re-subscribe
**Expected:** Old webhooks fail verification; after re-subscription new webhooks verify successfully; monitor `webhook_errors` spike during rotation
