# 0x::OG — Security Policy

## Secrets Inventory
| Secret | Variable | Rotation Trigger | Who Rotates |
|--------|----------|-----------------|-------------|
| Telegram Bot Token | `OG_API` | Suspected leak; quarterly | Admin via BotFather |
| Redis URL | `REDIS_URL` | Infrastructure change | DevOps |

## Secret Handling
- `.env` must be in `.gitignore`
- Tokens must not appear in logs or broadcast messages
- Rotate immediately on any suspected exposure

## Token Rotation
1. BotFather → `/mybots` → OG bot → Revoke token
2. Update `.env` → `OG_API=<new_token>`
3. `docker compose restart og-bot`
4. Verify bot responds in Telegram
5. Log the event

## Network Security
- Redis bound to internal Docker network only
- No inbound ports required (polling mode)

## Channel Security
- OG bot should be the **only** automated poster in managed channels
- Audit channel admin list monthly — remove unnecessary admins
- If OG token is compromised, revoke immediately to prevent unauthorized broadcasts

## Incident Response
| Severity | Example | Action |
|----------|---------|--------|
| P1 | Token leaked; unauthorized broadcast | Revoke immediately; audit channel post history |
| P2 | Spam messages from bot | Revoke token; check for injection in command args |
| P3 | Incorrect announcement posted | Delete message; post correction; audit |
