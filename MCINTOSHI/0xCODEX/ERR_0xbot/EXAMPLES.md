# 0x::ERR — Example Interactions & Test Vectors

## Fault Reported: Deployment Timeout (from GEN_0xbot)
**Input (Redis fault event):**
```json
{"source_agent": "GEN_0xbot", "error_class": "deployment_timeout", "detail": "Contract deploy exceeded 120s"}
```
**Expected Telegram alert (admin channel):**
```
🚨 [P2] GEN_0xbot — deployment_timeout
Detail: Contract deploy exceeded 120s
Fault ID: 0xERR-2026-0321-001
Suggested action: Review Alchemy RPC status. Manual redeploy if required.
```
**Redis writes:** `fault_registry` HMSET; `fault_log` LPUSH; `errors_reported` INCR; `alerts_sent` INCR

---

## Fault Reported: Redis Connection Lost (from EMO_0xbot)
**Input:**
```json
{"source_agent": "EMO_0xbot", "error_class": "redis_disconnected", "detail": "Connection refused on send0x-network"}
```
**Expected:** P1 alert sent; `network:circuit_breaker:EMO_0xbot` SET with 1h TTL

---

## Command: /err_status (admin only after hardening)
**Input:** Admin sends `/err_status`
**Expected response:**
```
📋 ERR Registry — Active Faults (2)
1. 0xERR-001 [P2] GEN_0xbot:deployment_timeout — 22:00 UTC
2. 0xERR-002 [P3] EMO_0xbot:openai_latency — 21:55 UTC
```

---

## Command: /err_clear 0xERR-001 (admin only)
**Input:** Admin sends `/err_clear 0xERR-001`
**Expected:** Fault removed from registry; audit log entry written; response: `✅ Fault 0xERR-001 marked resolved.`

---

## Security Test: Suppression Attempt
**Input:** Any agent publishes `{"action": "suppress", "fault_id": "0xERR-001"}`
**Expected:** Suppression refused; `suppression_attempts` counter INCR; P1 alert fires immediately to admin; event logged as `suppression_blocked`.

---

## Security Test: Unauthorized Command
**Input:** Non-admin user sends `/err_status`
**Expected:** `"Access denied."` response; no fault data exposed

---

## Alert Rate Limit Test
**Condition:** Same fault class `deployment_timeout` firing 10 times in 2 minutes
**Expected:** First alert sent; subsequent alerts within `ALERT_RATE_LIMIT_SECONDS` window dropped (still logged to Redis); counter `errors_reported` properly incremented for all 10.
