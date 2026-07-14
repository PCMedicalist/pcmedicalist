# 0x::GEN — Heartbeat

## Cadence
- **Interval:** `30s` (env: `HEARTBEAT_INTERVAL`, default `30`)
- **Mechanism:** Redis `PING` + Telegram `getMe()` on startup
- **Persistent key:** `agent:0xGENbot:heartbeat` — ISO timestamp

## Metrics Emitted (Redis Keys)
| Key | Type | Description |
|-----|------|-------------|
| `agent:0xGENbot:heartbeat` | string | Last successful heartbeat (ISO) |
| `agent:0xGENbot:deployments_queued` | counter | Deployments awaiting approval |
| `agent:0xGENbot:deployments_executed` | counter | Lifetime deployments completed |
| `agent:0xGENbot:deployments_failed` | counter | Lifetime deployment failures |
| `agent:0xGENbot:deployments_rejected` | counter | Requests rejected by approval gate |
| `agent:0xGENbot:last_deploy` | string | Timestamp and hash of last deployment |
| `agent:0xGENbot:pending_approvals` | list | Outstanding deployment approvals |

## Startup Health Checks
- [ ] Redis reachable: `redis_client.ping()`
- [ ] Telegram token valid: `getMe()`
- [ ] Required env vars present: `TELEGRAM_BOT_TOKEN` / `GEN_API`, `REDIS_URL`
- [ ] Deployment RPC endpoint reachable (Alchemy / Infura)
- [ ] Approval gate configured: `APPROVER_USER_IDS` not empty
- [ ] Testnet-first flag validated: `REQUIRE_TESTNET_FIRST=true` (default)

## Runtime Alert Thresholds
| Condition | Threshold | Response |
|-----------|-----------|----------|
| Consecutive missed heartbeats | ≥ 3 | P1 alert; emit ERR signal |
| Pending approval queue | > 5 items | Alert admin |
| Deployment failure | Any | P2 alert; emit to ERR channel |
| Self-approval attempt | Any | P1 alert; block; log |
| Consecutive deployment failures | ≥ 3 | Circuit-break deployments; alert ERR |

## Escalation Path
1. Live logs: `docker compose logs -f gen-bot`
2. Redis: `redis-cli get agent:0xGENbot:last_deploy`
3. Pending approvals: `redis-cli lrange agent:0xGENbot:pending_approvals 0 -1`
4. RPC status: verify Alchemy/Infura endpoint health
5. If deployment suspected compromised → HALT all pending; notify ROOT_0xbot
