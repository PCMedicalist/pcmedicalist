# 0x::PRIME — Memory Policy

## What Is Stored
| Store | Key Pattern | Content | TTL |
|-------|------------|---------|-----|
| Redis list | `agent:0xPRIMEbot:recent_observations` | Recent observation JSON objects (capped) | 7 days |
| Redis counter | `agent:0xPRIMEbot:observations` | Lifetime observations emitted | None |
| Redis histogram | `agent:0xPRIMEbot:confidence_histogram` | Confidence distribution | 30 days |
| Redis string | `agent:0xPRIMEbot:heartbeat` | Last heartbeat | None |

## What Is NOT Stored
- Raw market orderbooks or proprietary feed contents beyond aggregated indicators
- Personal user data or identifiable activity records

## Purge Policy
- `recent_observations` retained 7 days, trimmed regularly
- Histograms rotated after 30 days; aggregated summaries persisted

## Data Privacy
- Observations include provenance and source identifiers but not raw PII
- Any user-linked metrics must be hashed and anonymised

## Compliance Notes
- Observation logs may be used for audits; preserve critical evidence separately when required
