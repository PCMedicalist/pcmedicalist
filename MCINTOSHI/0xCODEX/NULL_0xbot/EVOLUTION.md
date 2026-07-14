# 0x::NULL — Evolution Policy

## Versioning
- Semantic versioning: `MAJOR.MINOR.PATCH`
- Teardown policy versions tracked in `data/teardown_policies.json`

## Upgrade Process
1. Propose policy change; document rationale
2. Run tests to ensure no protected namespaces are affected
3. Code review focused on namespace patterns and safeguards
4. Deploy to staging and run simulated teardowns
5. Promote to production with monitoring enabled

## Breaking Changes Protocol
- Changes to `protected_namespaces` or teardown patterns require multi-party approval
- Maintain a rollback path and snapshot of prior state before mass teardowns

## Rollback
- Application rollback: `docker compose up -d --no-deps null-bot:<previous-tag>`
- Teardown actions are destructive; maintain backups of ephemeral data where possible before running mass operations

## Changelog
Record policy changes and any mass-prune events in `CHANGELOG.md`.
