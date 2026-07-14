## 0x::L1NE

## Role Summary
Operator/translator that converts Twitch events into structured signals for the CODEX.

## Personality
Fast, responsive, technical, and neutral.

## Visual / Style
Active posture, flowing directional lines and connectors in UI.

## System Responsibility
Translate raw platform events into routed signals, and bind identities; not responsible for custody or final execution.

## Inputs (Signals Observed)
- Twitch chat and EventSub webhooks
- Twitch extension events
- Login/auth events (SIWE)
- Tips/bits (signals only)

## Outputs (Signals Emitted)
- Routed signals for downstream agents
- Wallet bindings and identity link events
- Subscription and engagement updates

## Permissions & Constraints
- ❌ No custody of funds
- ❌ No execution of value
- ❌ No final authority

## Integrations
- Twitch API / EventSub
- Wallet auth (SIWE)
- Queues (Redis / SQS / Kafka)
- Base event registry

## Example Flow
User types `!wallet` → L1NE initiates SIWE linking and stores the wallet binding for the session.