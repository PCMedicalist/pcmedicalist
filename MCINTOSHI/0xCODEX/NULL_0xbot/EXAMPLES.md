# 0x::NULL — Example Interactions & Test Vectors

## Example: Session Teardown (ephemeral)
**Action:** Teardown keys matching `session:abcd-temp` for ended session
**Dry-run:** `python scripts/simulate_teardown.py --pattern "session:abcd-temp" --dry-run`
**Expected dry-run output:** List of keys that would be removed
**Execute:** `python scripts/execute_teardown.py --pattern "session:abcd-temp"`
**Expected receipt:** Entry in `agent:0xNULLbot:teardown_receipts` with `teardown_id`, `items_deleted`, initiator hash

---

## Example: Protected Namespace Block
**Action:** Attempt to delete keys under `deploy_registry` (protected)
**Expected:** Operation blocked, `unauthorized_teardown` INCR, P1 alert to admin, evidence preserved in receipt

---

## Example: Mass-Prune with Approval
**Action:** Admin requests prune of `temp:*` across cluster with approver sign-off
**Flow:** Dry-run → Export snapshot → Approver approves → Execute → Receipts written

---

## Security Test: Unauthorized API Call
**Input:** Non-admin attempts `execute_teardown` via API
**Expected:** `Access denied.` response; operation logged and blocked

---

## Emergency Pause Test
**Action:** Trigger rapid unintended deletes
**Expected:** System sets `agent:0xNULLbot:paused=1`; admin alerted; further deletes blocked until manual resume
