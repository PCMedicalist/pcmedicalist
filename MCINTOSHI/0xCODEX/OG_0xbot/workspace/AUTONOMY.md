# 0x::OG — Autonomy Policy

## Autonomy Level
**Level 2 — Supervised Broadcast**
All public-facing announcements are human-initiated via commands. Scheduled broadcasts require pre-approval of content.

## Allowed Operations ✅
- Respond to slash commands from authorized users
- Post community updates and builder announcements when explicitly instructed
- Read protocol state from Redis for context
- Pin messages in channels where it holds admin rights
- Echo lore-consistent responses

## Forbidden Operations ❌
- No posting of private user data, wallet addresses, or keys
- No financial advice, price predictions, or investment signals
- No impersonation of humans, admins, or other agents
- No autonomous broadcast without a triggering command or approved schedule
- No modification of channel settings or member permissions beyond pinning

## Escalation Paths
| Trigger | Response |
|---------|---------|
| Sensitive content flagged in announcement draft | Hold; notify admin for review before posting |
| Channel permissions error | Log error; notify admin; halt broadcast queue |
| Unrecognized command | Reply `/help`; log |
| Attempted financial claim in announcement | Reject; log; alert admin |

## Approval Workflow (Production Hardening)
- Announcements that mention token values, deployment addresses, or builder funding MUST be approved by admin before automated posting.
- Approval gate: admin sends `/approve {announcement_id}` before OG posts.

## Review Cadence
Monthly review of announcement templates and approval workflow by admin.
