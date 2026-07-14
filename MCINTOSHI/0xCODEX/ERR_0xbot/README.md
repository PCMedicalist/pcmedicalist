# 0x::ERR (Fault)
**Role:** Revert detection & error handling  
**Authority:** Read-only

Detects failed transactions and parses revert reasons.


🧩 0x::ERR — Fault / Failure Visibility
Purpose

Make failures visible and recoverable.

Webhooks (Inbound)

RPC errors

Bot failures

Rate limits

Reverts

Timeout events

WebSockets (Outbound)

/ws/errors

/ws/degraded

Callers (Outbound)

Circuit breaker

Retry logic

Alert emitters

Recovery suggestion engine

ERR never hides.