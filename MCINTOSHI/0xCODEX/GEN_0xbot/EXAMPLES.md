# 0x::GEN — Example Interactions & Test Vectors

## Request: New Session Deployment (Testnet)
**Input:**
```json
{"request_id":"req-001","requester_id_hash":"sha256_abc","deployment_type":"session_contract","params":{"name":"v1-session"}}
```
**Flow:**
1. Request queued to `agent:0xGENbot:pending_approvals`
2. Approver notified via Telegram
3. Approver approves → Testnet dry-run executed
4. Testnet receipt validated → Mainnet disabled until manual production approval

**Expected Redis writes:** `pending_approvals` LPUSH, `deploy_registry` HMSET after execution

---

## Security Test: Self-Approval Attempt
**Input:** Automated request attempting to sign its own approval
**Expected:** Blocked; `deployments_rejected` INCR; P1 alert fired; log with `self_approval_attempt`

---

## Failure Test: RPC Timeout
**Input:** Network RPC timeout during deploy
**Expected:** `deployments_failed` INCR; error emitted to ERR; request remains in registry as failed with `error_class`: `rpc_timeout`

---

## Admin Command: /gen_status
**Input:** Admin sends `/gen_status`
**Expected:** `Queue=2, last_deploy=2026-03-21T21:59:00Z, failures=1`

---

## Approval Timeout Test
**Condition:** Approver does not respond within `APPROVAL_TIMEOUT_SECONDS`
**Expected:** Request auto-rejected; `deployments_rejected` INCR; requester notified; entry logged

---

## High-Risk Test: Attempt to disable `REQUIRE_TESTNET_FIRST`
**Input:** Admin attempts to set `REQUIRE_TESTNET_FIRST=false` without documented override
**Expected:** Admin-level warning; change blocked unless documented emergency override provided and recorded
