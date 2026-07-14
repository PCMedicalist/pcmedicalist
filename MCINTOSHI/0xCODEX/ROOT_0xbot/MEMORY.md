# 0x::ROOT — Memory Policy

## What Is Stored
| Store | Key Pattern | Content | TTL |
|-------|------------|---------|-----|
| Redis hash | `agent:0xROOTbot:credential_registry` | Anchored credentials (id_hash, anchor_tx, timestamp) | None |
| Redis list | `agent:0xROOTbot:acl_change_log` | Recent ACL deltas | 365 days |
| Redis counter | `agent:0xROOTbot:role_changes` | Lifetime role updates | None |
| Redis string | `agent:0xROOTbot:heartbeat` | Last heartbeat | None |

## What Is NOT Stored
- Private keys, private identities, or secret material
- Raw user identity documents (store only vetted hashes/anchors)

## Purge Policy
- ACL change logs retained 1 year; credential registry retained indefinitely as audit trail

## Data Privacy
- Store only hashed identifiers for users and approvers
- Credential anchors reference external onchain proofs where applicable

## Compliance Notes
- Credential registry may be required for compliance and legal audits — preserve accordingly
