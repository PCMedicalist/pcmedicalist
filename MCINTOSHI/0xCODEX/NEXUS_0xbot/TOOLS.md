# 0x::NEXUS — Tools & Integrations

## Required Environment Variables
| Variable | Description | Source |
|----------|-------------|--------|
| `REDIS_URL` | Redis connection string | `.env` |
| `SCHEDULER_URL` | Scheduler endpoint (if separate) | `.env` |
| `AGENT_REGISTRY_URL` | Service to lookup agent metadata | `.env` |

## Optional Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Structlog output level | `INFO` |
| `COORDINATION_WINDOW` | Time window to aggregate signals | `60s` |
| `RECOMMENDATION_TTL` | How long recommendations are valid | `5m` |

## Integrations
- Agent Registry: to discover agent capabilities and trust levels
- Redis: primary transport for telemetry and recommendations
- Scheduler / Job Queue: for periodic coordination runs
- Optional: Observability (Prometheus, Grafana) for metrics

## Coordination Algorithms
- Weighted voting based on agent confidence scores (PRIME provides confidence)
- Conflict detection heuristics and tie-breaker policies
- Human-in-the-loop promotion for high-risk directives

## Developer Tools
- `scripts/replay_snapshots.py` to run historical snapshots through coordination logic
- Local testing via mocked agent telemetry in `tests/fixtures/`

## Future Tools
- Integrate with ROOT for policy-driven decision promotion workflows
- Add a trust-scoring service for agents to adjust weighting dynamically
