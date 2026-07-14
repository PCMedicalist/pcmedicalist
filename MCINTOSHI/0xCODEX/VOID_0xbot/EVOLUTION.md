# 0x::VOID — Evolution

Versioning:
- Record major/minor versions in `agent:0xVOIDbot:meta`.

Upgrade policy:
- Non-blocking updates may be staged behind feature flags.
- Critical fixes should follow CODEX approval workflow and maintainers must schedule a maintenance window.

Telemetry:
- Keep anonymized telemetry for 90 days to guide tuning of detection heuristics.
# 0x::VOID — Evolution Policy

## Versioning
- Semantic versioning: `MAJOR.MINOR.PATCH`
- Silence-detection rules/versioned configs stored in `data/`

## Upgrade Process
1. Update detection thresholds or window config
2. Run replay tests with recorded gaps
3. Deploy to staging and verify no false positives
4. Promote after monitoring period

## Breaking Changes Protocol
- Changes that broaden what is considered "UNKNOWN" must be coordinated with NEXUS and ERR to avoid alert storms

## Rollback
- Application rollback: `docker compose up -d --no-deps void-bot:<previous-tag>`

## Changelog
Document any detection rule changes in `CHANGELOG.md`.
