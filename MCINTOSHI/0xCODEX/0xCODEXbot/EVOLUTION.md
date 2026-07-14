# 0x::CODEX — Evolution Policy

## Versioning
- Semantic versioning: `MAJOR.MINOR.PATCH`
- Current version tracked in `main.py` module docstring and `CHANGELOG.md`
- Docker image tagged per release (e.g., `0xcodexbot-codex-bot:1.2.0`)

## Upgrade Process
1. Create feature branch; implement and document changes
2. Update `CHANGELOG.md` with detailed release notes
3. Pass all tests (`pytest tests/` if present)
4. Code review by at least one peer
5. Deploy to staging: `docker compose build codex-bot` + manual smoke test via Telegram
6. Tag release in Git: `git tag -a v1.2.0 -m "Release notes"`
7. Deploy to production with zero-downtime restart (see `OPERATIONS.md`)

## Breaking Changes Protocol
- **Command signature changes** require a 30-day deprecation notice added to `/help` text
- **New required env vars** must be documented in `TOOLS.md` *before* deployment
- **Redis key schema changes** require a migration script and a backward-compatible window of ≥ 1 week

## Deprecation Policy
- Deprecated commands display a `[DEPRECATED — removing YYYY-MM-DD]` notice for 30 days
- Removed commands are logged in `CHANGELOG.md` with final removal date

## Rollback
- Every production deploy pins a specific Docker image tag
- Rollback: `docker compose up -d --no-deps codex-bot:<previous-tag>`
- Redis state is additive; metric counters survive rollback without cleanup

## Forking Policy
- Forks create independent agent instances with new Telegram bot tokens
- Fork origin, purpose, and token must be documented in `CHANGELOG.md`
- Forked agents inherit all policies at fork time; divergence must be tracked

## Changelog
Maintain `CHANGELOG.md` in this folder using [Keep a Changelog](https://keepachangelog.com/) format.
