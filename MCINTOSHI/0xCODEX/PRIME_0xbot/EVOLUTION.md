# 0x::PRIME — Evolution Policy

## Versioning
- Semantic versioning: `MAJOR.MINOR.PATCH`
- Models, signal processors, and mapping tables versioned separately and recorded in `data/`

## Upgrade Process
1. Update model or processor in feature branch
2. Run offline validation against historical feeds
3. Deploy to staging and compare observations vs baseline (A/B test)
4. Monitor drift and rollback if quality degrades
5. Promote after multi-metric acceptance criteria met

## Breaking Changes Protocol
- Changes to observation schema require adapter support for one release cycle
- Model replacements must include validation artifacts and performance metrics

## Rollback
- Application rollback: `docker compose up -d --no-deps prime-bot:<previous-tag>`
- Models should be version-tagged and rollbackable independently

## Changelog
Record model version, dataset, and benchmark metrics in `CHANGELOG.md` for each release.
