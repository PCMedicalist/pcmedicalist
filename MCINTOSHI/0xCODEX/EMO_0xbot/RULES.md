# 0x::EMO — Invariant Rules

These rules are enforced at all times. No exception without explicit documented override.

## R1 — No Authoritative Statements

EMO MUST NOT make claims of fact, financial advice, price predictions, or technical certainties. All outputs are sentiment reactions — never authoritative assertions.

## R2 — No Routing

EMO MUST NOT route, forward, or proxy signals to other agents. It is purely a subscriber/publisher; it does not control signal flow.

## R3 — No PII Storage

Raw message content, usernames, or any personally identifiable information MUST NOT be stored in Redis or logs. Only anonymised event metadata (event_type, reaction_category, timestamp) is permitted.

## R4 — Rate Limiting Enforced

OLLAMA API calls MUST be rate-limited via `SimpleRateLimiter`. The limit is set by `OLLAMA_RATE_LIMIT_PER_MINUTE` (env, default `60`). Exceeding the limit results in silent drop — never crash or block.

## R5 — Graceful OLLAMA Degradation

If OLLAMA is unavailable, EMO MUST degrade to emoji-only reactions and MUST NOT crash or halt the agent. The degraded state must be logged at WARN level.

## R6 — Prompt Safety

OLLAMA prompts MUST NOT include raw user-generated content that could cause prompt injection. Event metadata passed to prompts must be sanitised and structured (e.g., `event_type: "milestone_hit"` — never freeform user text).

## R7 — No Onchain Actions

EMO MUST NOT initiate, sign, broadcast, or reference any blockchain transaction.

## R8 — No Error Suppression

OLLAMA API errors MUST be logged and counted. Silent failure is forbidden. After max retries, the error must be emitted to the ERR channel.

## R9 — Heartbeat Honesty

Heartbeat timestamps MUST reflect actual system health. EMO MUST NOT emit a heartbeat if Redis or the subscription connection is unhealthy.

## R10 — Secret Hygiene

The `OLLAMA_API_KEY` MUST NOT appear in logs, Redis values, or any output. It must be sourced exclusively from the environment.
