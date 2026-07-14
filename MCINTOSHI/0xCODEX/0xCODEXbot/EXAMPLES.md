# 0x::CODEX — Example Interactions & Test Vectors

## /start
**Input:** User sends `/start`
**Expected response:**
```
🔮 0xCODEXbot - Core Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Welcome to the 0xCODEXbot network agent.
Use /help for available commands.
Use /lore for agent information.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
**Redis side-effect:** `user:{id}` hash written with `first_interaction` + `bot=0xCODEXbot`

---

## /codex blockchain
**Input:** `/codex blockchain`
**Expected response:** `🔍 Querying CODEX for: blockchain\n\nData retrieved from primordial archives.`

---

## /state
**Input:** `/state`
**Expected response:**
```json
{
  "network": "active",
  "consensus": "reached",
  "blocks": 15847392,
  "agents": 11,
  "status": "operational"
}
```

---

## /decode 0xdeadbeef
**Input:** `/decode 0xdeadbeef`
**Expected response:** `🔓 Decoded: 0xdeadbeef`

---

## /law
**Input:** `/law`
**Expected response (all 5 laws listed):**
```
1. Data is immutable
2. Signals propagate eternally
3. The network is consensus
4. Truth decodes through math
5. Chaos resolves to order
```

---

## /signal
**Input:** `/signal`
**Expected response:** `📡 Signal processed and stored in the network.`
**Redis side-effect:** Signal JSON pushed to `agent:0xCODEXbot:signals` list

---

## /codex_scan
**Input:** `/codex_scan`
**Expected response:** `🔬 Full CODEX scan initiated. Results processing...`
**Redis side-effect:** `agent:0xCODEXbot:last_scan` timestamp updated

---

## Security Test: Long argument
**Input:** `/codex ` + 1000-char string
**Expected:** Response should truncate or reject per `RULES.md` R2 (max 256 chars)
**Hardening note:** Input validation not yet in `main.py` — add before production.

## Security Test: Unknown command
**Input:** `/unknowncommand`
**Expected:** No response (no handler) — add catch-all handler to log and reply `/help`.
