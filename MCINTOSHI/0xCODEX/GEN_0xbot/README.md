# 0x::GEN (Genesis)
**Role:** Contract deployment & initialization  
**Authority:** Limited execution (scoped wallet + gas budget)

## Responsibilities
- Deploy contracts to Base/Ethereum
- Initialize contract state
- Verify deployments

## Event Channels
- Subscribes to: `codex:deploy:request`
- Publishes to: `codex:deploy:result`

## Security
- Uses scoped executor wallet
- Enforces gas budget limits
- Requires deployment approval


🌱 0x::GEN — Generator / Creation Engine
Purpose

Spawn anything new.

Webhooks (Inbound)

New session start

Builder-triggered deploy

Channel reward activation

User opt-in creation

WebSockets (Outbound)

/ws/creation

/ws/deployments

Callers (Outbound)

Smart wallet factory

ENS subname factory

Session NFT mint

Capability registry

GEN always leaves artifacts.