# 0x::VOID — Tools

- Redis (read/write) under `agent:0xVOIDbot:*` for ephemeral traces.
- Local diagnostic dump tool: `void-dump` (internal only) that exports sealed traces to `logs/void/` for operator download.
- Watcher: subscribe to `agent:*:alerts` for cross-agent signals.
