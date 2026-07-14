# 0x::NEXUS — Security Policy

## Secrets Inventory
| Secret | Variable | Rotation | Who Can Rotate |
|--------|----------|----------|----------------|
| Redis connection string | `REDIS_URL` | On infra change | DevOps |
| Agent registry credentials | `AGENT_REGISTRY_URL` auth | Rotate per policy | DevOps |

## Secret Handling Rules
- No private keys or PII stored by NEXUS
- All credentials sourced from secret store; `.env` only for local dev and gitignored
- Audit access to agent registry and snapshot storages

## Network Security
- Internal-only access to Redis and agent registry
- No public endpoints exposed by NEXUS
- Rate-limit incoming telemetry ingestion where applicable

## Incident Response
| Severity | Example | Response |
|----------|---------|----------|
| P1 | Malicious telemetry causing harmful coordination | Pause NEXUS; notify ERR and ROOT; preserve logs for audit |
| P2 | Agent registry compromise | Isolate registry access; require manual approval for coordination until resolved |
| P3 | Excessive recommendation churn | Throttle; investigate source agents |

## Auditing
- All recommendations and inputs logged append-only
- Offsite backups of `recommendation_log` recommended

## Dependency Security
- Keep dependencies up to date; run `pip-audit` before release
