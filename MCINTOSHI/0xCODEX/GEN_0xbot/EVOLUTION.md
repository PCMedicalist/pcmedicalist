# 0x::GEN — Evolution Policy

## Versioning
- Semantic versioning: `MAJOR.MINOR.PATCH`
- Version tracked in `main.py` and `CHANGELOG.md`
- Deployment artifact templates versioned separately in `data/templates/`
- Contract ABIs and factory addresses pinned per release

## Upgrade Process
1. Branch; implement changes
2. Update `CHANGELOG.md` with artifact template changes (if any)
3. Run tests — include testnet deployment dry-run
4. Code review — mandatory for any changes to: approval gate, testnet-first flag, RPC config
5. Deploy to **staging/testnet** environment; execute test deployment
6. Multi-party sign-off (min 2 approvers) for production upgrade
7. Tag release; deploy to production

## Breaking Changes
- **Approval gate logic changes** — Any change weakening the approval requirements MUST be reviewed with a security audit before merging
- **New deployment types** — Document in `TOOLS.md` and `EXAMPLES.md` before deploying
- **RPC provider changes** — Update `TOOLS.md` and verify new endpoint before cutover
- **Testnet-first flag removal** — Explicitly forbidden without documented emergency override and post-incident review

## Artifact Template Versioning
- Contract templates in `data/templates/` follow `{name}_v{semver}.json`
- Old templates retained for one full year (deployment history may reference them)
- Template changes require ABI compatibility check

## Deployment Audit Preservation
- Deployment receipts MUST be retained indefinitely in Redis and backed up externally
- Deleting or altering historical deployment records is forbidden

## Rollback
- Pin Docker image per deploy
- Rollback of application: `docker compose up -d --no-deps gen-bot:<previous-tag>`
- Onchain deployments are immutable — application rollback does NOT undo deployed contracts. Document this in post-incident reports.

## Changelog
See `CHANGELOG.md` (create per release). Each entry must include: version, date, deployment type changes, approval gate changes, testnet validation status.
