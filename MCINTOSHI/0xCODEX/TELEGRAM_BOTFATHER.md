# BotFather Update Pack (0x::CODEX)

Use this file to update BotFather `setcommands` for each 0x::CODEX bot. The lists below are generated from the current handlers in each bot's `main.py` and include the primary public commands for BotFather.

## 0xCODEX (@Zer0xCodexBot)

**Short description:** CODEX system narrator and state transmitter.
**Welcome description:** Silent execution-layer narrator for CODEX. Sends state updates, lore, and minimal guidance.
**Commands (setcommands):**
start - Initialize the agent and show welcome
codex - Retrieve a CODEX core statement
law - Return a governing principle
state - Display current execution state
observe - Output an observation snapshot
signal - Emit/distribute a signal to subscribed agents
stats - View statistics and milestone progress
null - Inspect NULL profile
void - Inspect VOID profile
og - Inspect OG profile
prime - Inspect PRIME profile
root - Inspect ROOT profile
gen - Inspect GEN profile
nexus - Inspect NEXUS profile
decode - Submit to resolve a cipher or decode
codex_scan - Scan CODEX progress and operator status

## EMO_0xbot (@EMO_0xbot)

**Short description:** Emotional reactor and engagement agent.
**Welcome description:** EMO posts sentiment, reactions, and lightweight engagement messages.
**Commands (setcommands):**
start - Basic EMO welcome
help - List EMO commands
lore - Show EMO personality
react - React with emoji or animation
mood - Report current mood
sentiment - Run sentiment on provided text
applaud - Post applause
hug - Send a virtual hug
subscribe - Subscribe this chat to EMO notifications
unsubscribe - Unsubscribe this chat

## OG_0xbot (@OG_0xbot)

**Short description:** Culture interface and community updates.
**Welcome description:** OG translates protocol operations into community narratives and announcements.
**Commands (setcommands):**
start - OG welcome
help - List OG commands
lore - Show OG lore
ask - Submit a human friendly query
codex - Proxy to CODEX core
law - Show governing principle
state - Show system state
observe - Show recent observations
signal - Emit a signal into the fleet
stats - Show community stats
null - Proxy to NULL
void - Proxy to VOID
og - OG-specific info
prime - Proxy to PRIME
root - Proxy to ROOT
gen - Proxy to GEN
nexus - Proxy to NEXUS
decode - Cipher decode helper
codex_scan - Scan CODEX status
announce - Post a community announcement

## VOID_0xbot (@VOID_0xbot)

**Short description:** Entropy coordinator and watch mode.
**Welcome description:** VOID tracks silent/unknown conditions and emits audit traces.
**Commands (setcommands):**
start - VOID welcome
help - VOID helper commands
lore - VOID lore and voice
void - Invoke void response
rollicking - Lightweight fun and entropy command
silence - Mute bot in a chat
watch - Add a watch target
unwatch - Remove a watch target
status - Query VOID status
trace - Retrieve recent traces
quarantine - Place an item into quarantine

## GEN_0xbot (@GEN_0xbot)

**Short description:** Genesis protocol and creative ignition.
**Welcome description:** GEN handles creative generation and deployment prep.
**Commands (setcommands):**
start - GEN welcome
help - List generation commands
lore - GEN creative lore
generate - Generate content or prompts
imagine - Create an image prompt or asset descriptor

## PRIME_0xbot (@PRIME_0xbot)

**Short description:** Probability engine and analysis.
**Welcome description:** PRIME offers probabilistic guidance and deployment hooks.
**Commands (setcommands):**
start - PRIME welcome
help - Admin and usage commands
lore - PRIME lore
announce - Broadcast an announcement (admin)
deploy - Trigger a deployment hook (admin)

## L1NE_0xbot (@L1NE_0xbot)

**Short description:** Signal intake and routing utility.
**Welcome description:** L1NE ingests external signals and routes them into CODEX.
**Commands (setcommands):**
start - L1NE welcome
help - Utility commands
lore - L1NE personality
shorten - Shorten a URL/text
format - Apply formatting helpers

## NEXUS_0xbot (@NEXUS_0xbot)

**Short description:** Multi-chain connector and utilities.
**Welcome description:** NEXUS bridges chains and resolves on-chain queries.
**Commands (setcommands):**
start - NEXUS welcome
help - Connector utilities
lore - NEXUS lore
tx - Lookup a transaction hash
balance - Check address balance

## NULL_0xbot (@NULL_0xbot)

**Short description:** First observer and null-state assistant.
**Welcome description:** NULL provides minimal assistance and observability checks.
**Commands (setcommands):**
start - NULL welcome
help - NULL helper commands
lore - NULL lore
ping - Ping/pong health check
echo - Echo input (debug)

## ROOT_0xbot (@ROOT_0xbot)

**Short description:** Governance and infrastructure layer.
**Welcome description:** ROOT manages system health, restarts, and approval flows.
**Commands (setcommands):**
start - ROOT welcome
help - Root admin commands
lore - ROOT governance lore
restart - Request controlled restart (admin)
status - Get system status and health

## ERR_0xbot (@ERR_0xbot)

**Short description:** Error reporting and diagnostics.
**Welcome description:** ERR handles debugging, logs, and error reporting.
**Commands (setcommands):**
start - ERR welcome
help - Error reporting helper
lore - ERR troubleshooting lore
report - Report an error to maintainers
logs - Retrieve recent logs (admin)

---
Notes:

- Use BotFather's `setcommands` for each bot account with the command list above.
- If you want a narrower public command set for production, consider limiting `announce`, `deploy`, `logs`, and other admin actions to admins only and omitting them from public BotFather lists.
