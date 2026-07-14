# 0x::OG — Evolution Policy

## Versioning
- Semantic versioning aligned with 0xCODEXbot releases
- Community-facing changes (personality, voice, announcement format) carry additional review — these are visible to the public

## Upgrade Process
1. Draft change; update announcement templates
2. Review change against `RULES.md` (no financial claims, no PII)
3. Test in staging channel before production
4. Deploy with zero-downtime restart

## Breaking Changes
- **Voice or persona changes** require a 2-week community notice period
- **Announcement format changes** require template updates documented in `TOOLS.md`
- **New channel integrations** require admin sign-off and `.env` update

## Deprecation
- Deprecated commands include a notice for 30 days
- Deprecated announcement templates archived in `templates/deprecated/`

## Rollback
- Revert image tag
- Re-apply previous announcement templates from Git history
