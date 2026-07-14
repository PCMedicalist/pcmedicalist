# 0x::ERR — Evolution Policy

## Versioning
- Semantic versioning: `MAJOR.MINOR.PATCH`
- Version tracked in `main.py` module docstring and `CHANGELOG.md`
- Error taxonomy (fault classes, severity levels) versioned as a sub-component

## Upgrade Process
1. Create feature branch; implement changes
2. Update `CHANGELOG.md` with fault taxonomy changes (if any)
3. Run tests — verify no existing error classifications are silently removed
4. Code review — focus on: new fault classes, alert routing changes, suppression safeguards
5. Deploy to staging; trigger test fault events and verify alerts fire
6. Tag release; deploy to production

## Breaking Changes Protocol
- **Error taxonomy changes** (adding/removing fault classes) — document in `CHANGELOG.md` and notify downstream consumers (Grafana dashboards, alert rules)
- **Alert routing changes** (new Telegram channel, new Sentry project) — document in `TOOLS.md` before merging
- **Circuit-breaker signal schema changes** — coordinate with NEXUS_0xbot and consuming agents

## Deprecation
- Deprecated fault classes must remain active for one full release cycle before removal
- Removed classes must be logged in `CHANGELOG.md` with the final affected version

## Rollback
- Pin Docker image tag per deploy
- Rollback: `docker compose up -d --no-deps err-bot:<previous-tag>`
- Fault log data in Redis is additive — rollback does not affect historical records

## Observability Stack Evolution
- Changes to Prometheus metrics labels or Grafana dashboard IDs must be versioned and communicated to the ops team
- Sentry project DSN changes require `.env` update and redeploy

## Changelog
See `CHANGELOG.md` (create per release).
