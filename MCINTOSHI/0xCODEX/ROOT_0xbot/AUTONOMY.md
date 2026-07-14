# 0x::ROOT — Autonomy Policy

## Autonomy Level
**Level 1 — Authority Anchor (human-gated, minimal writes)**
ROOT anchors identities, roles, and ACLs. All sensitive writes (credential anchors, role grants) require multi-party approval or admin gating.

## Allowed Operations ✅
- Verify identities (DID/ENS) and anchor credential records
- Update ACL entries and role assignments after approval
- Emit audit records for any changes to trust fabric

## Forbidden Operations ❌
- No unilateral credential issuance without approver approval
- No signing of onchain transactions on behalf of users
- No storage of private keys or secret material

## Approval Requirements
- Role or credential changes require admin approvals (`APPROVER_USER_IDS` / multi-sig) and are recorded with approver hash

## Escalation Paths
| Trigger | Response |
|---------|----------|
| Unauthorized role change | Block; P1 alert; notify security team |
| Credential compromise detected | Revoke anchor; rotate policy; notify affected parties |

## Review Cadence
- Weekly review of ACL deltas
- Immediate post-incident review for any P1 events
