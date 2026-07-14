# 0x::OG — Reflection & Introspection

## Self-Check Schedule
| Check | Frequency | Output |
|-------|-----------|--------|
| Engagement summary | Daily | Log: posts sent, interactions logged |
| Channel permission check | On startup | Warn if missing admin rights |
| Announcement queue review | Hourly | Alert if stalled items > 10 min old |

## Anomaly Detection
| Anomaly | Indicator | Response |
|---------|-----------|---------|
| Repeated failed channel writes | 3 consecutive | Alert admin; pause queue |
| Spike in engagement errors | > 10 / hour | Log + alert |
| Unexpected content in announcement drafts | Financial or PII terms detected | Reject; alert admin |

## Audit Log Schema
```json
{
  "event": "announcement_sent",
  "channel_id": -100123456789,
  "bot": "OG_0xbot",
  "timestamp": "2026-03-21T22:00:00Z",
  "content_hash": "sha256:...",
  "approved_by": "admin_user_id"
}
```

## Review Cadence
- **Weekly:** review post history for tone and accuracy
- **Monthly:** audit channel permissions and membership; review approval workflow
