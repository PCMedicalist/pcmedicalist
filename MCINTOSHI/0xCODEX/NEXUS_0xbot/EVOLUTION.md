# 0x::NEXUS — Evolution Policy

## Versioning
- Semantic versioning: `MAJOR.MINOR.PATCH`
- Coordination schemas versioned separately (`coord_schema_v{n}.json`) and stored in `data/`

## Upgrade Process
1. Propose schema changes; notify downstream consumers (GEN, PRIME, ROOT, EMO)
2. Deploy to staging and run integration replays
3. Monitor recommendation acceptance rates in staging
4. Promote to production once compatibility verified

## Breaking Changes Protocol
- Provide an adapter layer for backward-incompatible schema changes
- Maintain legacy schema support for at least one release cycle
- Coordinate with ops before removing old schema versions

## Rollback
- Application rollback: `docker compose up -d --no-deps nexus-bot:<previous-tag>`
- Recommendation history is append-only; no destructive schema migrations

## Changelog
Keep `CHANGELOG.md` updated with coordination model changes and schema updates.
