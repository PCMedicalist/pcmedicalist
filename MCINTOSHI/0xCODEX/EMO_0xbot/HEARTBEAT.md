# 0x::EMO — Heartbeat

## Cadence

- **Interval:** `30s` (env: `HEARTBEAT_INTERVAL`, default `30`)
- **Mechanism:** Redis `PING` + OpenAI API key validation on startup
- **Persistent key:** `agent:0xEMObot:heartbeat` — ISO timestamp, updated each cycle

## Metrics Emitted (Redis Keys)

| Key | Type | Description |

| `agent:0xEMObot:heartbeat` | string | Last successful heartbeat (ISO) |
| `agent:0xEMObot:reactions_emitted` | counter | Lifetime sentiment reactions fired |
| `agent:0xEMObot:openai_calls` | counter | Total OpenAI API invocations |
| `agent:0xEMObot:openai_errors` | counter | OpenAI API failures |
| `agent:0xEMObot:rate_limited` | counter | Requests dropped by rate limiter |
| `agent:0xEMObot:last_reaction` | string | Timestamp of last reaction emitted |

## Startup Health Checks

- [ ] Redis reachable: `redis_client.ping()`
- [ ] OpenAI API key present: env `OPENAI_API_KEY` — test with a minimal ping call
- [ ] Rate limiter initialized: `SimpleRateLimiter` configured with `OPENAI_RATE_LIMIT_PER_MINUTE`
- [ ] Redis subscription channel active

## Runtime Alert Thresholds

| Condition | Threshold | Response |

| Consecutive missed heartbeats | ≥ 3 | Publish to ERR channel; page on-call |
| OpenAI error rate | > 10% over 10 min | Alert + increase backoff; log |
| Rate limit drops | > 50 in 1 min | Log warn; check upstream signal volume |
| OpenAI latency | > 10s per call | Log warn; degrade to no-reaction mode |

## Escalation Path

1. Live logs: `docker compose -f 0xCODEXbot/docker-compose.bots.yml logs -f emo-bot`
2. Redis metrics: `redis-cli hgetall agent:0xEMObot:metrics`
3. Verify OpenAI key valid (no 401 errors in logs)
4. Container restart: `docker compose restart emo-bot`
