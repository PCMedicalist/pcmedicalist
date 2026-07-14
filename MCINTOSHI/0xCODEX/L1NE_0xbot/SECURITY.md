# 0x::L1NE — Security Policy

## Secrets Inventory
| Secret | Variable | Rotation | Who Can Rotate |
|--------|----------|----------|----------------|
| Twitch Client Secret | `TWITCH_CLIENT_SECRET` | Rotate on suspicion; quarterly | DevOps |
| EventSub Secret | `TWITCH_EVENTSUB_SECRET` | Rotate when rotated in Twitch Dev Console | Admins |
| Redis connection string | `REDIS_URL` | On infra change | DevOps |

## Secret Handling Rules
- All secrets kept in secret store; `.env` used for local development only and must be gitignored
- Webhook secret must not be logged or stored in Redis
- SIWE nonces stored transiently with TTL and not logged

## Webhook Signature Verification
- Use HMAC-SHA256 with `TWITCH_EVENTSUB_SECRET` to validate `Twitch-Eventsub-Message-Signature`
- Reject and log any events failing validation; increment `webhook_errors`
- Maintain replay cache to detect duplicates

## SIWE Security
- Nonce generation must be cryptographically secure
- Verify SIWE signatures server-side and store only hashed address (`sha256(address)`)
- Do not log SIWE payloads or signatures

## Network Security
- Webhook callback should be behind HTTPS with valid certs
- Restrict any admin endpoints to `send0x-network` or VPN
- Use IP allowlists for known Twitch webhook sources if possible

## Incident Response
| Severity | Example | Response |
|----------|---------|----------|
| P1 | EventSub secret leaked | Rotate secret immediately; reissue EventSub subscriptions; audit bindings |
| P2 | Repeated replay attack | Block source IPs; increase monitoring; notify admin |
| P3 | SIWE brute-force attempts | Increase nonce complexity; rate-limit SIWE endpoints |

## Dependency Security
- Keep webhook libraries and HTTP server patched
- Run `pip-audit` on `requirements.txt` before each release
