# 0x::PRIME — Tools & Integrations

## Required Environment Variables
| Variable | Description | Source |
|----------|-------------|--------|
| `REDIS_URL` | Redis connection string | `.env` |
| `MARKET_FEEDS` | Comma-separated feed identifiers/endpoints | `.env` |
| `LOG_LEVEL` | Structlog level | `.env` |

## Optional Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `OBSERVATION_RATE_LIMIT` | Max observations per minute | `60` |
| `MODEL_PATH` | Local path or URL to model artifact | (optional) |
| `PROMETHEUS_PUSH_URL` | For metrics push | (optional) |

## Integrations
- Market data providers / oracles
- Redis for publish/subscribe and storage
- NEXUS for downstream coordination
- Optional: ML model serving (TorchServe / custom endpoint)

## Observation Pipeline
- Ingest → Sanitize → Feature extract → Score → Publish
- Include `sources` and `confidence` in every publish

## Developer Tools
- `scripts/replay_feeds.py` for deterministic testing
- `tests/fixtures/` with historical feeds for validation

## Safety Tools
- Input schema validation middleware
- Confidence threshold guard and publish throttler
- Circuit-breaker for anomalous feed behavior
