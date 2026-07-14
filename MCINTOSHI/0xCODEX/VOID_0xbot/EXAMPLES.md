# 0x::VOID — Examples

Example 1 — Suspicious binary payload:
- Input: base64 blob received on `channel:uploads`.
- Action: mark as `quarantine`, create sealed trace key `agent:0xVOIDbot:trace:{id}`, notify `NEXUS` with metadata.

Example 2 — Noise reduction:
- Input: repeated low-value messages from source X.
- Action: apply rate-limit, increment `agent:0xVOIDbot:silence_events`, notify operator if threshold exceeded.
