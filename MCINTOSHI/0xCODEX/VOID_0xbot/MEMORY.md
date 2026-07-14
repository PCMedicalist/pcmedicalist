# 0x::VOID — Memory Policy

## What Is Stored
| Store | Key Pattern | Content | TTL |
|-------|------------|---------|-----|
| Redis string | `agent:0xVOIDbot:last_silence` | Timestamp and context of last silence event | 30 days |
| Redis counter | `agent:0xVOIDbot:silence_events` | Lifetime silence detections | None |
| Redis list | `agent:0xVOIDbot:watch_traces` | Diagnostic traces for watch-mode events | 30 days |
| Redis string | `agent:0xVOIDbot:heartbeat` | Last heartbeat | None |

## What Is NOT Stored
- No raw payloads from other agents
- No user-identifying information

## Purge Policy
- `watch_traces` trimmed after 30 days
- `last_silence` retained 30 days for correlation

## Data Privacy
- All stored context is anonymised and aggregate in nature
