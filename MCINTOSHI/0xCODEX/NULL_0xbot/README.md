# 0x::NULL
**Role:** Void state monitoring  
**Authority:** Read-only

Tracks uninitialized state and null pointers in the system.


🚫 0x::NULL — Reset / Teardown
Purpose

Safe deletion and cleanup.

Webhooks (Inbound)

Session end

Logout

Feature disable

Explicit reset request

WebSockets (Outbound)

/ws/reset

/ws/cleared

Callers (Outbound)

Subscription cleanup

Cache purge

Permission revoke

Memory pruning

NULL erases without opinion.