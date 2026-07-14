# 0x::L1NE — Evolution Policy

## Versioning
- Semantic versioning: `MAJOR.MINOR.PATCH`
- Event schema versions must be bumped when breaking changes occur
- `event_schema_v{n}.json` maintained in `data/`

## Upgrade Process
1. Update schema and `CHANGELOG.md`
2. Notify downstream consumers (NEXUS, PRIME, EMO) of schema change
3. Deploy to staging and run replay tests with recorded webhook streams
4. Monitor for drop/failure rates before promoting to production

## Breaking Changes Protocol
- Backwards-incompatible event schema changes require a migration adaptor
- Maintain compatibility layer for at least one release cycle
- Coordinate with consumer agents and update `TOOLS.md` accordingly

## Rollback
- Event schema changes are code-level — revert via tag: `docker compose up -d --no-deps l1ne-bot:<previous-tag>`
- Maintain recorded webhook samples for replay testing

## Changelog
Record changes to EventSub handling, SIWE flow, and webhook security in `CHANGELOG.md`.
