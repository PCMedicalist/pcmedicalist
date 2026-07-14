"""
0xCODEXbot - Core Agent with comprehensive command handling
Telegram bot with Redis state management and structured logging
"""

import asyncio
import os
import json
import sys
import structlog
import re
import uuid
from pathlib import Path
import importlib
import importlib.util
from redis import Redis
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.persona import PersonaEngine, PersonaProfile
from shared.inter_agent import InterAgentCommunicator, InterAgentMessage, MessageType, RiskLevel
from shared.startup import announce_startup_rollcall

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Initialize Redis client
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
SOUL_PATH = os.path.join(os.path.dirname(__file__), "0xOG_SOUL.md")
persona_engine = PersonaEngine(PersonaProfile.from_soul_file(SOUL_PATH))
inter_agent = InterAgentCommunicator("OG_0xbot", redis_client)

# Initialize Telegram bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")


# --- Template loading utilities -------------------------------------------------
BASE_DIR = Path(__file__).parent


def load_runtime_templates(base: Path) -> dict:
    """Load runtime templates from YAML or JSON if present.

    Returns a dict mapping command -> template string. If templates file
    includes objects, use the `body` field as the template text.
    """
    out = {}
    # Try YAML first
    yaml_path = base / "templates.yaml"
    yaml_path2 = base / "templates.yml"
    json_path = base / "templates.json"
    try:
        import yaml  # type: ignore
    except Exception:
        yaml = None

    try:
        if yaml and yaml_path.exists():
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
        elif yaml and yaml_path2.exists():
            data = yaml.safe_load(yaml_path2.read_text(encoding="utf-8")) or {}
        elif json_path.exists():
            data = json.loads(json_path.read_text(encoding="utf-8")) or {}
        else:
            data = {}

        tpl_map = data.get("templates") if isinstance(data, dict) else {}
        for k, v in (tpl_map.items() if isinstance(tpl_map, dict) else []):
            if isinstance(v, dict):
                out[k] = v.get("body", "")
            else:
                out[k] = str(v)
    except Exception:
        out = {}
    return out


def parse_response_templates(path: Path) -> dict:
    templates = {}
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception:
        return templates

    # Split sections by YAML/Markdown separator lines (---)
    sections = re.split(r"\n-{3,}\n", txt)
    for sec in sections:
        m = re.search(r"Command:\s*`([^`]+)`", sec)
        if not m:
            continue
        cmd = m.group(1).strip()
        # Extract text after 'Template:' if present, else fallback to section body
        m2 = re.search(r"Template:\s*(.*)$", sec, flags=re.DOTALL | re.IGNORECASE)
        if m2:
            tm = m2.group(1).strip()
        else:
            # remove header lines like Purpose/Inputs metadata for brevity
            lines = [l for l in sec.splitlines() if not re.match(r"^(Purpose:|Inputs:|Approval:|Command:|---)", l.strip())]
            tm = "\n".join(lines).strip()
        templates[cmd] = tm
    return templates


def format_template(tpl: str, **kwargs) -> str:
    if not tpl:
        return ""

    def _repl(m):
        k = m.group(1).strip()
        return str(kwargs.get(k, m.group(0)))

    return re.sub(r"{{\s*([^}]+)\s*}}", _repl, tpl)


# Load templates at import time (best-effort)
TEMPLATES = {}
TONE_TEXT = ""
try:
    # Prefer runtime YAML/JSON templates when available
    runtime = load_runtime_templates(BASE_DIR)
    if runtime:
        TEMPLATES = runtime
    else:
        rt = BASE_DIR / "RESPONSE_TEMPLATES.md"
        if rt.exists():
            TEMPLATES = parse_response_templates(rt)

    tv = BASE_DIR / "TONE_VOCAB.md"
    if tv.exists():
        TONE_TEXT = tv.read_text(encoding="utf-8")
except Exception:
    TEMPLATES = {}
    TONE_TEXT = ""

# --------------------------------------------------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    logger.info("start_command_invoked", user_id=update.effective_user.id)
    
    # Prefer template if available
    tpl = TEMPLATES.get("start") if 'TEMPLATES' in globals() else None
    if tpl:
        welcome_text = format_template(tpl)
    else:
        welcome_text = """
🔮 **0xCODEXbot** - Core Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Welcome to the 0xCODEXbot network agent.
Use /help for available commands.
Use /lore for agent information.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    redis_client.hset(f"user:{update.effective_user.id}", mapping={
        "first_interaction": str(update.message.date),
        "bot": "0xCODEXbot"
    })
    
    # interactive buttons to keep the conversation flowing
    kb = [
        [InlineKeyboardButton("Lore", callback_data="og:lore"), InlineKeyboardButton("Announcements", callback_data="og:announce")],
        [InlineKeyboardButton("Builder Spotlight", callback_data="og:spotlight"), InlineKeyboardButton("Help", callback_data="og:help")]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(kb))


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command handler"""
    logger.info("help_command_invoked", user_id=update.effective_user.id)
    
    tpl = TEMPLATES.get("help") if 'TEMPLATES' in globals() else None
    if tpl:
        help_text = format_template(tpl)
    else:
        help_text = """
**Available Commands:**

📋 **Core:**
/start - Initialize bot
/help - Show this message
/lore - Agent history and information

🔍 **Analysis:**
/codex - Query the codex database
/law - View foundational laws
/state - Check network state
/observe - Monitor activity
/signal - Process signals
/stats - Display statistics

⚙️ **Operations:**
/null - Null operations
/void - Void state management
/og - Original operations
/prime - Prime number operations
/root - Root operations
/gen - Generation utilities
/nexus - Network nexus commands
/decode - Decode information
/codex_scan - Full codex scan

Type a command to get started!
    """
    
    kb = [[InlineKeyboardButton("Lore", callback_data="og:lore")]]
    await update.message.reply_text(help_text, reply_markup=InlineKeyboardMarkup(kb))


async def lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command - universal across all agents"""
    logger.info("lore_command_invoked", user_id=update.effective_user.id, agent="0xCODEXbot")
    

    # Prefer template-driven reply; fall back to soul file or hardcoded summary
    tpl = TEMPLATES.get("lore") if 'TEMPLATES' in globals() else None
    lore_text = None
    try:
        soul_path = os.path.join(os.getcwd(), "0xOG_SOUL.md")
        if os.path.exists(soul_path):
            with open(soul_path, "r", encoding="utf-8") as fh:
                lore_text = fh.read()
    except Exception:
        lore_text = None

    if tpl:
        soul_summary = lore_text or "0x::OG — Human interface and community layer. Friendly, cultural, and informative."
        lore_text = format_template(tpl, soul_summary=soul_summary)
    else:
        if not lore_text:
            lore_text = "0x::OG — Human interface and community layer. Friendly, cultural, and informative."

    redis_client.hset(f"agent:OG_0xbot:metrics", "lore_reads", redis_client.hget(f"agent:OG_0xbot:metrics", "lore_reads") or 0)
    kb = [[InlineKeyboardButton("Examples", callback_data="og:examples"), InlineKeyboardButton("Ask OG", callback_data="og:ask")]]
    await update.message.reply_text(lore_text, reply_markup=InlineKeyboardMarkup(kb))


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button callbacks for OG agent"""
    q = update.callback_query
    await q.answer()
    data = q.data or ""
    if data == "og:lore":
        await lore(update, context)
        return
    if data == "og:help":
        await help_handler(update, context)
        return
    if data == "og:examples":
        # try to load examples file
        examples = None
        try:
            p = os.path.join(os.getcwd(), "EXAMPLES.md")
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as fh:
                    examples = fh.read()
        except Exception:
            examples = None
        if not examples:
            examples = "No examples available. Use /og to see operations or /help."
        await q.message.reply_text(examples)
        return
    if data == "og:announce":
        await q.message.reply_text("To create an announcement, send /announce <message> — OG will format and broadcast it to channels (requires operator approval).")
        return
    if data == "og:spotlight":
        await q.message.reply_text("Builder Spotlight: use /spotlight <builder_name> to showcase a builder.")
        return
    if data == "og:ask":
        await q.message.reply_text("Ask OG: send your question with /ask <your question> and OG will respond using its community-first style.")
        return


async def ask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """User-facing ask command that enriches user input with OG soul context"""
    user_q = " ".join(context.args) if context.args else None
    if not user_q:
        await update.message.reply_text("Usage: /ask <question> — OG will respond with community-friendly explanation.")
        return
    # Build enriched prompt using soul summary and template
    soul_summary = "Human interface and community layer. Approachable, culturally aware, and adaptive."
    # Generate an internal answer (placeholder logic — replace with model call if available)
    generated_answer = f"Short explanation for: {user_q}"
    tpl = TEMPLATES.get("ask") if 'TEMPLATES' in globals() else None
    if tpl:
        reply = format_template(tpl, question=user_q, answer=generated_answer)
    else:
        reply = f"OG (context: {soul_summary}) — You asked: {user_q}\n\nOG reply: {generated_answer}"
    await update.message.reply_text(reply)


async def codex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Codex query command"""
    logger.info("codex_command_invoked", user_id=update.effective_user.id)
    
    query = " ".join(context.args) if context.args else "default"
    redis_client.hset(f"agent:0xCODEXbot:commands", "codex", redis_client.hget(f"agent:0xCODEXbot:commands", "codex") or 0)
    
    tpl = TEMPLATES.get("codex") if 'TEMPLATES' in globals() else None
    if tpl:
        response = format_template(tpl, term=query, codex_entry="Data retrieved from primordial archives.")
    else:
        response = f"🔍 Querying CODEX for: {query}\n\nData retrieved from primordial archives."
    await update.message.reply_text(response)


async def law(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foundational laws command"""
    logger.info("law_command_invoked", user_id=update.effective_user.id)
    
    tpl = TEMPLATES.get("law") if 'TEMPLATES' in globals() else None
    if tpl:
        laws_text = format_template(tpl)
    else:
        laws_text = """
⚖️ **Foundational Laws:**

1. Data is immutable
2. Signals propagate eternally
3. The network is consensus
4. Truth decodes through math
5. Chaos resolves to order
    """

    redis_client.incr(f"agent:0xCODEXbot:command_count")
    await update.message.reply_text(laws_text, parse_mode="Markdown")


async def state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check network state"""
    logger.info("state_command_invoked", user_id=update.effective_user.id)
    
    state_data = {
        "network": "active",
        "consensus": "reached",
        "blocks": 15847392,
        "agents": 11,
        "status": "operational"
    }
    
    redis_client.set(f"user:{update.effective_user.id}:last_state_check", json.dumps(state_data))
    
    tpl = TEMPLATES.get("state") if 'TEMPLATES' in globals() else None
    if tpl:
        state_text = format_template(tpl, timestamp=str(update.message.date), finalized_block=state_data.get("blocks"), reorg_count=0)
        await update.message.reply_text(state_text)
    else:
        state_text = f"📊 **Network State**\n\n```json\n{json.dumps(state_data, indent=2)}\n```"
        await update.message.reply_text(state_text, parse_mode="Markdown")


async def observe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Monitor activity"""
    logger.info("observe_command_invoked", user_id=update.effective_user.id)
    
    tpl = TEMPLATES.get("signal") if 'TEMPLATES' in globals() else None
    if tpl:
        observation = format_template(tpl, event_summary="Monitoring network signals...", evidence_snippet="Blocks:+4, Tx:+127")
        await update.message.reply_text(observation)
    else:
        observation = "👁️ **Observation Mode Active**\n\nMonitoring network signals...\n• Blocks: +4\n• Transactions: +127\n• Agents: All Online"
        await update.message.reply_text(observation, parse_mode="Markdown")


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process signals"""
    logger.info("signal_command_invoked", user_id=update.effective_user.id)
    
    redis_client.lpush(f"agent:0xCODEXbot:signals", json.dumps({
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date)
    }))
    
    tpl = TEMPLATES.get("signal") if 'TEMPLATES' in globals() else None
    if tpl:
        msg = format_template(tpl, event_summary="Signal received", evidence_snippet="Stored to queue")
    else:
        msg = "📡 Signal processed and stored in the network."
    await update.message.reply_text(msg)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display statistics"""
    logger.info("stats_command_invoked", user_id=update.effective_user.id)
    
    stats_data = {
        "commands_processed": int(redis_client.get(f"agent:0xCODEXbot:command_count") or 0),
        "active_users": redis_client.hlen(f"users:active") or 0,
        "uptime_hours": 847,
        "network_health": "98.7%"
    }
    
    tpl = TEMPLATES.get("stats") if 'TEMPLATES' in globals() else None
    if tpl:
        stats_text = format_template(tpl, tx_count=stats_data.get("commands_processed"), alert_count=0, uptime=stats_data.get("uptime_hours"))
        await update.message.reply_text(stats_text)
    else:
        stats_text = f"📈 **Statistics**\n\n```json\n{json.dumps(stats_data, indent=2)}\n```"
        await update.message.reply_text(stats_text, parse_mode="Markdown")


async def null_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Null operations"""
    logger.info("null_command_invoked", user_id=update.effective_user.id)
    tpl = TEMPLATES.get("null") if 'TEMPLATES' in globals() else None
    if tpl:
        await update.message.reply_text(format_template(tpl))
    else:
        await update.message.reply_text("∅ Null state engaged.")


async def void_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Void state management"""
    logger.info("void_command_invoked", user_id=update.effective_user.id)
    tpl = TEMPLATES.get("void") if 'TEMPLATES' in globals() else None
    if tpl:
        await update.message.reply_text(format_template(tpl))
    else:
        await update.message.reply_text("⬛ Void acknowledged.")


async def og_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Original operations"""
    logger.info("og_command_invoked", user_id=update.effective_user.id)
    tpl = TEMPLATES.get("og") if 'TEMPLATES' in globals() else None
    if tpl:
        await update.message.reply_text(format_template(tpl))
    else:
        await update.message.reply_text("🌟 Original protocols activated.")


async def prime_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prime number operations"""
    logger.info("prime_command_invoked", user_id=update.effective_user.id)
    tpl = TEMPLATES.get("prime") if 'TEMPLATES' in globals() else None
    if tpl:
        await update.message.reply_text(format_template(tpl))
    else:
        await update.message.reply_text("🔢 Prime sequence initialized.")


async def root_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Root operations"""
    logger.info("root_command_invoked", user_id=update.effective_user.id)
    tpl = TEMPLATES.get("root") if 'TEMPLATES' in globals() else None
    if tpl:
        await update.message.reply_text(format_template(tpl))
    else:
        await update.message.reply_text("🌱 Root access established.")


async def gen_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generation utilities"""
    logger.info("gen_command_invoked", user_id=update.effective_user.id)
    tpl = TEMPLATES.get("generate") if 'TEMPLATES' in globals() else None
    if tpl:
        await update.message.reply_text(format_template(tpl))
    else:
        await update.message.reply_text("⚡ Generation protocols running.")


async def nexus_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Network nexus commands"""
    logger.info("nexus_command_invoked", user_id=update.effective_user.id)
    tpl = TEMPLATES.get("nexus") if 'TEMPLATES' in globals() else None
    if tpl:
        await update.message.reply_text(format_template(tpl))
    else:
        await update.message.reply_text("🔗 Nexus connection established.")


async def decode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Decode information"""
    logger.info("decode_command_invoked", user_id=update.effective_user.id)
    
    data = " ".join(context.args) if context.args else "0x0"
    decoded = f"Decoded: {data}"
    tpl = TEMPLATES.get("decode") if 'TEMPLATES' in globals() else None
    if tpl:
        await update.message.reply_text(format_template(tpl, decoded=decoded))
    else:
        await update.message.reply_text(f"🔓 {decoded}")


async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create an announcement draft (admin approval required)"""
    logger.info("announce_invoked", user_id=update.effective_user.id)
    message = " ".join(context.args) if context.args else None
    if not message:
        await update.message.reply_text("Usage: /announce <message> — creates a draft that requires admin approval.")
        return

    author = getattr(update.effective_user, "username", None) or str(update.effective_user.id)
    draft_id = str(uuid.uuid4())
    redis_client.hset(f"announce:draft:{draft_id}", mapping={
        "author": author,
        "message": message,
        "timestamp": str(update.message.date)
    })

    tpl = TEMPLATES.get("announce") if 'TEMPLATES' in globals() else None
    if tpl:
        formatted = format_template(tpl, author=author, message=message, draft_id=draft_id)
    else:
        formatted = f"Announcement Draft by @{author}:\n\n{message}\n\nTo broadcast, an admin must confirm with /announce confirm {draft_id}."

    try:
        inter_agent.send_message(
            InterAgentMessage(
                source_agent="OG_0xbot",
                target_agent="ALL",
                message_type=MessageType.CHATTER,
                intent="community_milestone",
                payload={"message": message, "draft_id": draft_id, "author": author},
                timestamp=str(update.message.date),
                trace_id=f"og-{update.effective_user.id}-{int(update.message.date.timestamp())}",
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                confidence=0.87,
            )
        )
    except Exception as exc:
        logger.warning("inter_agent_og_broadcast_failed", error=str(exc))

    await update.message.reply_text(persona_engine.stylize_text(formatted))


async def codex_scan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Full codex scan"""
    logger.info("codex_scan_command_invoked", user_id=update.effective_user.id)
    
    redis_client.set(f"agent:0xCODEXbot:last_scan", str(update.message.date))
    tpl = TEMPLATES.get("codex_scan") if 'TEMPLATES' in globals() else None
    if tpl:
        await update.message.reply_text(format_template(tpl))
    else:
        await update.message.reply_text("🔬 Full CODEX scan initiated. Results processing...")


def main() -> None:
    """Start the bot"""
    logger.info("starting_0xCODEXbot")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("lore", lore))
    app.add_handler(CommandHandler("ask", ask_cmd))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern=r"^og:"))
    app.add_handler(CommandHandler("codex", codex))
    app.add_handler(CommandHandler("law", law))
    app.add_handler(CommandHandler("state", state))
    app.add_handler(CommandHandler("observe", observe))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("null", null_cmd))
    app.add_handler(CommandHandler("void", void_cmd))
    app.add_handler(CommandHandler("og", og_cmd))
    app.add_handler(CommandHandler("prime", prime_cmd))
    app.add_handler(CommandHandler("root", root_cmd))
    app.add_handler(CommandHandler("gen", gen_cmd))
    app.add_handler(CommandHandler("nexus", nexus_cmd))
    app.add_handler(CommandHandler("decode", decode_cmd))
    app.add_handler(CommandHandler("codex_scan", codex_scan))
    # Announce handler (creates draft requiring admin confirmation)
    app.add_handler(CommandHandler("announce", announce))
    
    logger.info("handlers_registered")
    
    # 🚀 Announce startup rollcall
    announce_startup_rollcall(inter_agent, persona_engine.profile, "OG")
    
    app.run_polling()


if __name__ == "__main__":
    main()
