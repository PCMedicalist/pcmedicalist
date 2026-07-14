# 0x::OG (Observer)
**Role:** Transaction finality monitoring  
**Authority:** Read-only

Monitors pending transactions and emits finality events.

👑 0x::OG — Observer / Finality Authority
Purpose

Final confirmation, attestations, irreversible truth.

Webhooks (Inbound)

Alchemy:

tx.confirmed

tx.finalized

contract.event.confirmed

Internal: state.ready_for_finality

WebSockets (Outbound)

/ws/finality

/ws/attestations

Callers (Outbound)

Attestation contract writer

Checkpoint registry

Audit log writer (IPFS / Arweave optional)

NEVER CALLS

Twitch

Telegram

Wallet execution

OG only speaks when truth is finalized.