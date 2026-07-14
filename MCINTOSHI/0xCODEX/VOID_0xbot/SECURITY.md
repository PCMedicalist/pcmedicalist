# 0x::VOID — Security

Secrets:
- VOID does not store secrets. When a secret is required to escalate, route an approval stub to `ROOT` for secure injection.

ACLs:
- Strict operator-only commands for quarantine and purge.

Audit:
- Append-only audit trail to `agent:0xVOIDbot:audits` for any state changes.
