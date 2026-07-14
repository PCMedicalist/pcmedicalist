# 0x::ROOT — Evolution Policy

## Versioning
- Semantic versioning: `MAJOR.MINOR.PATCH`
- ACL schema versions tracked in `data/acl_schema_v{n}.json`

## Upgrade Process
1. Propose ACL or credential flow changes with rationale
2. Run staging tests and impact analysis for dependent agents
3. Multi-party approval required for production changes
4. Deploy with audit logging enabled

## Breaking Changes Protocol
- Changes to ACL schemas or trust models require migration adaptors and backward compatibility for at least one release cycle

## Rollback
- Application rollback: `docker compose up -d --no-deps root-bot:<previous-tag>`
- ACL changes must be reversible; keep snapshots before changes

## Changelog
Document all trust-model and ACL changes in `CHANGELOG.md` with approver references.
