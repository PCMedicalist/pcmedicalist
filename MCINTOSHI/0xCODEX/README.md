# 0x::AGENTS — User Help & Operations

This document is a user-focused help file summarizing the private 0x::Agents in this repository, how to interact with them, and important safety and operational notes. These agents are private system components; do not expose their tokens, API keys, or endpoints to third parties.

--

**Quick overview**
- Purpose: Lightweight Telegram + Redis agents (bots and background subscribers) that provide monitoring, formatting, generation, nexus (network) lookups, error reporting, and characterful responses.
- How to talk to them: Each agent runs as a Telegram bot (polling) and exposes a small set of slash commands (e.g., `/help`, `/lore`, and a few agent-specific commands).
- Important: These are NOT public-facing services. Keep bot tokens, Redis access, and any AI API keys private.

--

**Operational prerequisites**
- Required environment variables (common): `TELEGRAM_BOT_TOKEN` or `TELEGRAM_TOKEN`, `REDIS_URL` (defaults to `redis://redis:6379`).
- Optional / agent-specific: `OPENAI_API_KEY` (used by `EMO_0xbot`), and tuning vars such as `OPENAI_RATE_LIMIT_PER_MINUTE`.
- Runtime: Each agent is a Python script (uses python-telegram-bot, structlog, redis). Run via `python main.py` inside agent folder or via the repository's Docker setup.

--

**Agents & how to use them**

Note: All agents expose `/start`, `/help`, and `/lore` by convention. Use `/help` first to see agent-specific commands.

- `0xCODEXbot` (core / gateway)
  - Purpose: Core network agent and indexer; central command set and orchestration.
  - Commands: `/start`, `/help`, `/lore`, `/codex`, `/law`, `/state`, `/observe`, `/signal`, `/stats`, `/null`, `/void`, `/og`, `/prime`, `/root`, `/gen`, `/nexus`, `/decode`, `/codex_scan`.
  - File: see [0xCODEXbot/main.py](0xCODEXbot/main.py).

- `EMO_0xbot` (emotion / personality)
  - Purpose: Subscribe to state changes and generate humanlike responses (optionally calls OpenAI). Runs as a Redis subscriber; not a typical command bot.
  - Commands / behavior: Listens on `codex:state:change` and posts characterful messages. Requires `OPENAI_API_KEY` to enable OpenAI calls; includes rate-limiting and retry logic.
  - File: see [EMO_0xbot/main.py](EMO_0xbot/main.py).

- `ERR_0xbot` (error reporting)
  - Purpose: Collect and display error reports and logs.
  - Commands: `/start`, `/help`, `/lore`, `/report`, `/logs`.
  - File: see [ERR_0xbot/main.py](ERR_0xbot/main.py).

- `GEN_0xbot` (generation)
  - Purpose: Create contract templates and conceptual protocol artifacts.
  - Commands: `/start`, `/help`, `/lore`, `/generate`, `/imagine`.
  - File: see [GEN_0xbot/main.py](GEN_0xbot/main.py).

- `L1NE_0xbot` (formatting)
  - Purpose: Shorten and pretty-print data.
  - Commands: `/start`, `/help`, `/lore`, `/shorten`, `/format`.
  - File: see [L1NE_0xbot/main.py](L1NE_0xbot/main.py).

- `NEXUS_0xbot` (network queries)
  - Purpose: Transaction and balance lookups (simulated responses in code).
  - Commands: `/start`, `/help`, `/lore`, `/tx`, `/balance`.
  - File: see [NEXUS_0xbot/main.py](NEXUS_0xbot/main.py).

- `NULL_0xbot` (null-state)
  - Purpose: Ping/echo utilities and null-state management.
  - Commands: `/start`, `/help`, `/lore`, `/ping`, `/echo`.
  - File: see [NULL_0xbot/main.py](NULL_0xbot/main.py).

- `OG_0xbot` (original/core variant)
  - Purpose: A variant of the core bot; mirrors `0xCODEXbot` behavior.
  - Commands: Mirrors core commands.
  - File: see [OG_0xbot/main.py](OG_0xbot/main.py) (also nested copy in `OG_0xbot/OG_0xbot/`).

- `PRIME_0xbot` (announcements / deployments)
  - Purpose: Broadcasts and simulated deployments.
  - Commands: `/start`, `/help`, `/lore`, `/announce`, `/deploy`.
  - File: see [PRIME_0xbot/main.py](PRIME_0xbot/main.py).

- `ROOT_0xbot` (administration)
  - Purpose: Restart and status operations for foundations.
  - Commands: `/start`, `/help`, `/lore`, `/restart`, `/status`.
  - File: see [ROOT_0xbot/main.py](ROOT_0xbot/main.py).

- `VOID_0xbot` (entropy)
  - Purpose: Void/chaos operations and entropy controls.
  - Commands: `/start`, `/help`, `/lore`, `/void`, `/rollicking`, `/silence`.
  - File: see [VOID_0xbot/main.py](VOID_0xbot/main.py).

--

Security & responsible operation
- Keep `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, and any DB credentials out of source control.
- Restrict bot admin controls: commands such as `/restart`, `/deploy`, or any admin operation should be gated behind explicit admin checks before use in production. The example agents do not implement robust auth — treat them as internal tools only.
- Redis: Bind access to a private network and use auth where supported. Do not expose `REDIS_URL` publicly.
- Rate limiting: `EMO_0xbot` shows an example of local rate-limiting for external API calls; respect providers' TOS and set conservative limits.
- Audit logging: Structured logs (structlog) are used; ensure logs are stored securely and rotated.

Privacy & non-exploit notice
- These agents have capabilities that could be abused if misconfigured (broadcasts, simulated deployments, restart hooks, or OpenAI calls). They are private infrastructure components intended for internal orchestration and diagnostics.
- Do NOT:
  - Post bot tokens, API keys, or Redis credentials publicly.
  - Expose these services to the public internet without strong authentication and rate-limiting.
  - Use the generation or deployment functions in an unreviewed production environment.

If you suspect credentials were leaked, rotate them immediately and revoke access.

--

Troubleshooting
- If a bot doesn't start: verify `TELEGRAM_BOT_TOKEN` and `REDIS_URL`, confirm Python dependencies (see agents' `requirements.txt` files), and check logs for initialization errors.
- `EMO_0xbot` OpenAI errors: ensure `OPENAI_API_KEY` is set and valid; check rate limits and `OPENAI_RATE_LIMIT_PER_MINUTE`.
- Docker: several folders include `Dockerfile` and docker-compose YAMLs for containerized runs — prefer containerization for production-like environments.

--

Files referenced in this help
- Repository vision: [vision.md](vision.md)
- Core bot implementation: [0xCODEXbot/main.py](0xCODEXbot/main.py)
- Agents: [EMO_0xbot/main.py](EMO_0xbot/main.py), [ERR_0xbot/main.py](ERR_0xbot/main.py), [GEN_0xbot/main.py](GEN_0xbot/main.py), [L1NE_0xbot/main.py](L1NE_0xbot/main.py), [NEXUS_0xbot/main.py](NEXUS_0xbot/main.py), [NULL_0xbot/main.py](NULL_0xbot/main.py), [OG_0xbot/main.py](OG_0xbot/main.py), [PRIME_0xbot/main.py](PRIME_0xbot/main.py), [ROOT_0xbot/main.py](ROOT_0xbot/main.py), [VOID_0xbot/main.py](VOID_0xbot/main.py)

--

## 0x::AGENTS - Reference on skills and advanced operations.

**Agentic WAllet**
> ## Documentation Index
> Fetch the complete documentation index at: https://docs.cdp.coinbase.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Agentic Wallet

Give your AI agent a wallet. Pay for APIs, send money, and trade tokens safely, with built-in spending limits.

## What is Agentic Wallet?

Agentic Wallet gives any AI agent a standalone wallet to hold and spend stablecoins, or trade for other tokens on Base.

Built on Coinbase Developer Platform (CDP) infrastructure, agents can authenticate via email OTP, hold USDC, and send, trade, or pay for services without ever accessing private keys.

<Accordion title="Comparing AgentKit vs Agentic Wallet">
  |                 | [AgentKit](/agent-kit/welcome)                     | Agentic Wallet                                    |
  | --------------- | -------------------------------------------------- | ------------------------------------------------- |
  | **What it is**  | SDK/toolkit for onchain actions                    | Standalone wallet via CLI/MCP                     |
  | **Integration** | Import into your agent code                        | Can call CLI or MCP tools (e.g., `npx awal send`) |
  | **Scope**       | Full onchain capabilities (deploy contracts, etc.) | Wallet ops: send, trade, x402                     |
  | **Networks**    | Multi-network (EVM + Solana)                       | Base                                              |
</Accordion>

## Use cases

<CardGroup cols={2}>
  <Card title="Pay-per-call APIs" icon="bolt">
    Agents pay for external services via [x402](/x402/core-concepts/how-it-works)
  </Card>

  <Card title="Gasless autonomy" icon="paper-plane">
    Send payments, tip creators, split bills without paying gas fees
  </Card>

  <Card title="Agent-to-agent commerce" icon="store">
    Build paid APIs that other agents can consume
  </Card>

  <Card title="Budget-constrained agents" icon="shield">
    Give agents spending power with per-session limits
  </Card>
</CardGroup>

## Capabilities

| Feature                                               | Description                                                                                         |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| **Wallet identity**                                   | Self-custody wallet controlled by the agent                                                         |
| **Spending limits**                                   | Configurable caps per session and per transaction                                                   |
| **Gasless trading**                                   | Token swaps on Base without requiring gas                                                           |
| **Skill extensibility**                               | Add new capabilities via [agentic-wallet-skills](https://github.com/coinbase/agentic-wallet-skills) |
| **[x402](/x402/core-concepts/how-it-works) payments** | Machine-to-machine paid API requests                                                                |

### Security

* **Key isolation**: Private keys stay in Coinbase infrastructure
* **Spending guardrails**: Enforce limits before any transaction
* **KYT screening**: Block high-risk interactions automatically

## Components

### awal CLI

Command-line tool for wallet operations. Use it directly for testing, or let agents invoke it via skills.

```bash  theme={null}
npx awal status      # Check auth status
npx awal send 1 vitalik.eth   # Send USDC
npx awal trade 5 usdc eth     # Swap tokens
```

### Agent Skills

Instead of manually wiring wallet operations into your agent, install skills and let the agent handle it.

```bash  theme={null}
npx skills add coinbase/agentic-wallet-skills
```

Skills include: authenticate, fund, send, trade, search-for-service, pay-for-service, monetize-service.

### x402 Integration

Protocol for machine-to-machine payments. Agents can both consume and provide paid APIs with [x402](/x402/core-concepts/how-it-works), enabling agent-to-agent commerce.

## What to read next

<CardGroup cols={2}>
  <Card title="Quickstart" icon="rocket" href="/agentic-wallet/quickstart">
    First wallet in 2 minutes
  </Card>

  <Card title="Skills Reference" icon="book" href="/agentic-wallet/skills/overview">
    All agent capabilities
  </Card>
</CardGroup>


***Agentic Wallet Skills***
https://github.com/coinbase/agentic-wallet-skills

