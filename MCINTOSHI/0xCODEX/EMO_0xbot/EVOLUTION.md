# 0x::EMO — Evolution Policy

## Versioning

- Semantic versioning: `MAJOR.MINOR.PATCH`
- Current version tracked in `main.py` module docstring
- Emotional response library (prompts, emoji mappings) versioned separately in `data/` or inline config

## Upgrade Process

1. Create feature branch; implement changes
2. Update `CHANGELOG.md`
3. Test locally with mocked Redis events (`pytest tests/` or manual Redis PUBLISH)
4. Code review — focus on: OpenAI prompt changes, rate limiter config, new event schemas
5. Deploy to staging; verify reactions fire correctly against test events
6. Tag release; deploy to production with zero-downtime restart

## Breaking Changes Protocol

- **New event schemas EMO subscribes to** — document new channel/key pattern in `TOOLS.md` before merging
- **OpenAI model upgrades** — test output against existing reaction library; prompts may need adjustment
- **Rate limiter changes** — model adjustments must not increase per-minute token spend without budget review

## Emotional Response Library Evolution

- New reaction categories require a deliberate design decision (not ad-hoc)
- Prompts MUST be reviewed for tone — EMO should always be empathetic and non-authoritative
- Remove stale reaction types with a deprecation window of one release cycle

## Rollback

- Each production deploy pins Docker image tag
- Rollback: `docker compose up -d --no-deps emo-bot:<previous-tag>`
- OpenAI API changes are external — maintain model version pin in config

## Forking Policy

- Forks inherit the emotional response library at fork point
- Personality divergence from `0xEMO_SOUL.md` must be explicitly documented in the forked SOUL file

## Changelog

See `CHANGELOG.md` (create per release).
