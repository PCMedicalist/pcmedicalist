# 0x::VOID — Operations

Routine checks:
- Verify Redis connectivity and `watch_traces` retention.
- Run signature tuning job weekly in staging.

Incident response:
- Quarantine flow: mark trace sealed, increment `agent:0xVOIDbot:silence_events`, notify `NEXUS`, and await approval.
