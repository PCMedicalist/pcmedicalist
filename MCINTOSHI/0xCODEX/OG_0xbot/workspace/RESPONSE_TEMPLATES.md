# OG Agent — Response Templates

Purpose: canonical templates and variables for all user-facing commands. Templates use placeholders in `{{var}}` form. Follow tone rules in `TONE_VOCAB.md` and hard constraints in `RULES.md`.

Usage notes

- Each template includes: Purpose, Inputs, Approval (if admin), and Template Body.
- Handlers should prefer these templates verbatim; small runtime substitutions allowed.

---

Command: `start`

- Purpose: Welcome new users and show quick actions.
- Inputs: none
- Template:

Hello! 👋 I'm OG — the community steward for 0x.

Quick commands:

- `/help` — list commands
- `/lore` — OG's purpose and mission
- `/ask <question>` — ask OG a question

If you'd like an announcement posted, ask an admin to run `/announce <message>`.

---

Command: `help`

- Purpose: Show available commands and short usage.
- Inputs: optional `command_name`
- Template (general):

Available commands (short):

- `/ask <question>` — Ask OG anything.
- `/lore` — Read OG's persona and responsibilities.
- `/state` — Current observed network state.
- `/stats` — Recent metrics snapshot.
- `/announce <message>` — Admin-only: create an announcement (approval required).

Use `/help <command>` for details.

---

Command: `lore`

- Purpose: Return the agent's `0xOG_SOUL.md` summary or section.
- Inputs: optional `section`
- Template:

OG — Persona & Mission

{{soul_summary}}

---

Command: `ask`

- Purpose: General question to OG (assistant-style reply).
- Inputs: `question`, optional `context`
- Template:

You asked: "{{question}}"

Answer:
{{answer}}

Notes: If OG cannot verify facts from authoritative sources, append: "I don't have that data right now — try again later or contact an admin."

---

Command: `announce`

- Purpose: Admin request to prepare a public announcement; requires approval before broadcast.
- Inputs: `message`, `author_id`
- Approval: `requires_admin_approval: true`
- Template (draft):

Announcement Draft by @{{author}}:

{{message}}

This is an automated message from OG — it will be broadcast only after admin approval.

--
To broadcast, an admin must confirm with `/announce confirm {{draft_id}}`.

---

Command: `state`

- Purpose: Show recent network/finality state from Redis.
- Inputs: none / optional `topic`
- Template:

Current state snapshot (as of {{timestamp}}):

- Finalized block: {{finalized_block}}
- Observed reorgs (24h): {{reorg_count}}

Source: authoritative telemetry. If data missing: "Data not available from source."

---

Command: `stats`

- Purpose: Return metrics summary.
- Template:

Metrics (last 24h):

- Transactions processed: {{tx_count}}
- Alerts: {{alert_count}}
- Uptime: {{uptime}}

---

Command: `codex` / `codex_scan`

- Purpose: Lookup or scan codex entries.
- Inputs: `term`
- Template:

Codex lookup: `{{term}}`

Result:
{{codex_entry}}

---

Command: `signal` / `observe`

- Purpose: Report a detected event or observation.
- Inputs: `event_summary`, `evidence`
- Template:

Observation: {{event_summary}}

Evidence: {{evidence_snippet}}

If this is actionable and meets broadcast criteria, tag an admin for review.

---

Command: `decode`

- Purpose: Decode small payloads/hash into readable form (non-sensitive only).
- Inputs: `payload`
- Template:

Decoded result:
{{decoded}}

If the payload may contain PII or keys, refuse: "I can't decode that — it may contain private data."

---

Admin / Agent-group Commands (examples)

- `history`, `rank`, `spotlight`, `generate`, `imagine`, `deploy`, `tx`, `balance`, `ping`, `echo`, `restart`, `status`, `report`, `logs`

Common admin template pattern:

{{command_title}} — {{short_description}}

Usage: `{{usage}}`

Response:
{{response_body}}

If admin-only: include `requires_admin_approval: true` in metadata.

---

Template conventions

- Use `{{var}}` for substitution.
- Include `requires_admin_approval` flag for any broadcast or action that modifies state or posts publicly.
- Include `source` lines for any factual claims e.g., "Source: Redis `agent:OG_0xbot:state`."

Maintenance

- Keep templates short. Update this file when new commands are added in `CONFIG_BOT_COMMANDS.md`.
