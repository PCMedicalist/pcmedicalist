# 0x::ROOT — Example Interactions & Test Vectors

## Example: Anchor Credential Flow
**Action:** Admin requests to anchor a verified identity credential
**Flow:**
1. Admin submits credential hash and metadata
2. Multi-party approval collected (approver hashes recorded)
3. Anchor written to `agent:0xROOTbot:credential_registry` and optional onchain anchor emitted
4. Audit record appended to `acl_change_log`

**Expected receipt:** `credential_anchored` event with approver hash and anchor tx

---

## Example: Role Grant (approved)
**Action:** Grant `moderator` role to user
**Flow:**
1. Proposal created and approver signs
2. ROOT applies ACL change and logs entry in `acl_change_log`
3. Notification emitted to relevant agents

---

## Security Test: Unauthorized Role Change
**Input:** Non-admin attempts role change via API
**Expected:** `Access denied.` response; P1 alert; evidence preserved in logs

---

## Integrity Test: Anchor Mismatch
**Input:** Anchor proof that doesn't match recorded hash
**Expected:** Anchor quarantined; P1 alert; admin notified for manual reconciliation

---

## Audit Query Example
**Command:** `redis-cli lrange agent:0xROOTbot:acl_change_log 0 9`
**Expected:** Recent ACL changes with approver hashes and timestamps
