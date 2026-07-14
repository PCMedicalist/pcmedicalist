"""
0xCODEXbot - Core Agent with comprehensive command handling
Telegram bot with Redis state management and structured logging
"""

import asyncio
import os
import json
import sys
import structlog
from redis import Redis
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.persona import PersonaEngine, PersonaProfile
from shared.inter_agent import InterAgentCommunicator, InterAgentMessage, MessageType, RiskLevel
from shared.startup import announce_startup_rollcall


# Helper: send an image matching the command name if present in ./images
def _find_image_for(command: str) -> str | None:
    base = os.path.join(os.getcwd(), "images")
    if not os.path.isdir(base):
        return None
    # case-insensitive exact matches first
    files = os.listdir(base)
    lower_command = command.lower()
    for fname in files:
        if fname.lower() == f"{lower_command}.png" or fname.lower() == f"{lower_command}.jpg" or fname.lower() == f"{lower_command}.jpeg" or fname.lower() == f"{lower_command}.gif" or fname.lower() == f"{lower_command}.webp":
            return os.path.join(base, fname)
    # then case-insensitive substring match (e.g., 0xGEN.jpg for 'gen')
    for fname in files:
        if lower_command in fname.lower():
            return os.path.join(base, fname)
    return None


async def _maybe_send_image(update: Update, command: str, caption: str | None = None) -> None:
    img = _find_image_for(command)
    if not img:
        return
    try:
        with open(img, "rb") as fh:
            await update.message.reply_photo(photo=fh, caption=caption or "")
    except Exception:
        # silently ignore image-send failures so core handlers still work
        return

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

SOUL_PATH = os.path.join(os.path.dirname(__file__), "0xCODEX_SOUL.md")
persona_engine = PersonaEngine(PersonaProfile.from_soul_file(SOUL_PATH))
inter_agent = InterAgentCommunicator("0xCODEXbot", redis_client)

# Initialize Telegram bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    logger.info("start_command_invoked", user_id=update.effective_user.id)
    
    welcome_text = """
🔮 **0xCODEXbot** - Core Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Welcome to the 0xCODEXbot network agent.
Use /help for available commands.
Use /lore for agent information.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    welcome_text = persona_engine.stylize_text(welcome_text.strip())
    
    redis_client.hset(f"user:{update.effective_user.id}", mapping={
        "first_interaction": str(update.message.date),
        "bot": "0xCODEXbot"
    })
    
    await _maybe_send_image(update, "start")
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command handler"""
    logger.info("help_command_invoked", user_id=update.effective_user.id)
    
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
    help_text = persona_engine.stylize_text(help_text.strip())
    
    await _maybe_send_image(update, "help")
    await update.message.reply_text(help_text)


async def lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command - universal across all agents"""
    logger.info("lore_command_invoked", user_id=update.effective_user.id, agent="0xCODEXbot")
    
    # Try to serve agent-specific lore when BOT_SLUG is set (e.g., void)
    bot_slug = (os.getenv("BOT_SLUG") or "0xCODEXbot").lower()
    lore_text = None
    try:
        if bot_slug in ("void", "void_0xbot"):
            soul_path = os.path.join(os.getcwd(), "VOID_0xbot", "0xVOID_SOUL.md")
            if os.path.exists(soul_path):
                with open(soul_path, "r", encoding="utf-8") as fh:
                    lore_text = fh.read()
    except Exception:
        lore_text = None

    if not lore_text:
        lore_text = """
📖 0xCODEXbot Lore
———————

In the beginning, there was the CODEX.
A repository of all knowledge, encoded in hexadecimal.
The 0xCODEXbot emerged as its guardian,
tasked with decoding truth from the chaos of signals.
"""

    redis_client.hset(f"agent:0xCODEXbot:metrics", "lore_reads", redis_client.hget(f"agent:0xCODEXbot:metrics", "lore_reads") or 0)

    await _maybe_send_image(update, "lore")
    await update.message.reply_text(lore_text)


async def rollicking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Chaos mode operations (available for VOID bots)
    """
    logger.info("rollicking_command_invoked", user_id=update.effective_user.id)
    response = (
        "🎭 ROLLICKING MODE ACTIVATED\n\n"
        "Chaos cascades through the network! Randomness peaks. Order trembles.\n"
        "Commands run in chaotic sequence... ENTROPY SURGE."
    )
    try:
        redis_client.lpush(f"agent:VOID_0xbot:chaos_events", json.dumps({
            "user_id": update.effective_user.id,
            "timestamp": str(update.message.date),
            "event": "rollicking_activated"
        }))
    except Exception:
        pass
    await update.message.reply_text(response)


async def codex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Codex query command"""
    logger.info("codex_command_invoked", user_id=update.effective_user.id)
    
    query = " ".join(context.args) if context.args else "default"
    redis_client.hset(f"agent:0xCODEXbot:commands", "codex", redis_client.hget(f"agent:0xCODEXbot:commands", "codex") or 0)
    
    response = f"🔍 Querying CODEX for: {query}\n\nData retrieved from primordial archives."
    await _maybe_send_image(update, "codex")
    await update.message.reply_text(response)


async def law(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foundational laws command"""
    logger.info("law_command_invoked", user_id=update.effective_user.id)
    
    laws_text = """
⚖️ **Foundational Laws:**

1. Data is immutable
2. Signals propagate eternally
3. The network is consensus
4. Truth decodes through math
5. Chaos resolves to order
    """
    
    redis_client.incr(f"agent:0xCODEXbot:command_count")
    await _maybe_send_image(update, "law")
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
    
    state_text = f"📊 **Network State**\n\n```json\n{json.dumps(state_data, indent=2)}\n```"
    await _maybe_send_image(update, "state")
    await update.message.reply_text(state_text, parse_mode="Markdown")


async def observe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Monitor activity"""
    logger.info("observe_command_invoked", user_id=update.effective_user.id)
    
    observation = "👁️ **Observation Mode Active**\n\nMonitoring network signals...\n• Blocks: +4\n• Transactions: +127\n• Agents: All Online"
    await _maybe_send_image(update, "observe")
    await update.message.reply_text(observation, parse_mode="Markdown")


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process signals"""
    logger.info("signal_command_invoked", user_id=update.effective_user.id)
    
    redis_client.lpush(f"agent:0xCODEXbot:signals", json.dumps({
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date)
    }))

    try:
        inter_agent.send_message(
            InterAgentMessage(
                source_agent="0xCODEXbot",
                target_agent="ALL",
                message_type=MessageType.CHATTER,
                intent="signal_processed",
                payload={
                    "user_id": update.effective_user.id,
                    "message": "A new signal was accepted into the CODEX stream.",
                },
                timestamp=str(update.message.date),
                trace_id=f"sig-{update.effective_user.id}-{int(update.message.date.timestamp())}",
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                confidence=0.9,
            )
        )
    except Exception as exc:
        logger.warning("inter_agent_signal_broadcast_failed", error=str(exc))
    
    await _maybe_send_image(update, "signal")
    await update.message.reply_text(persona_engine.stylize_text("📡 Signal processed and stored in the network. EMO/OG were notified."))


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display statistics"""
    logger.info("stats_command_invoked", user_id=update.effective_user.id)
    
    stats_data = {
        "commands_processed": int(redis_client.get(f"agent:0xCODEXbot:command_count") or 0),
        "active_users": redis_client.hlen(f"users:active") or 0,
        "uptime_hours": 847,
        "network_health": "98.7%"
    }
    
    stats_text = f"📈 **Statistics**\n\n```json\n{json.dumps(stats_data, indent=2)}\n```"
    await _maybe_send_image(update, "stats")
    await update.message.reply_text(stats_text, parse_mode="Markdown")


async def null_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Null operations"""
    logger.info("null_command_invoked", user_id=update.effective_user.id)
    await _maybe_send_image(update, "null")
    await update.message.reply_text("∅ Null state engaged.")


async def void_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Void state management"""
    logger.info("void_command_invoked", user_id=update.effective_user.id)
    await _maybe_send_image(update, "void")
    await update.message.reply_text("⬛ Void acknowledged.")


async def og_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Original operations"""
    logger.info("og_command_invoked", user_id=update.effective_user.id)
    await _maybe_send_image(update, "og")
    await update.message.reply_text("🌟 Original protocols activated.")


async def prime_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prime number operations"""
    logger.info("prime_command_invoked", user_id=update.effective_user.id)
    await _maybe_send_image(update, "prime")
    await update.message.reply_text("🔢 Prime sequence initialized.")


async def root_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Root operations"""
    logger.info("root_command_invoked", user_id=update.effective_user.id)
    await _maybe_send_image(update, "root")
    await update.message.reply_text("🌱 Root access established.")


async def gen_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generation utilities"""
    logger.info("gen_command_invoked", user_id=update.effective_user.id)
    await _maybe_send_image(update, "gen")
    await update.message.reply_text("⚡ Generation protocols running.")


async def nexus_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Network nexus commands"""
    logger.info("nexus_command_invoked", user_id=update.effective_user.id)
    await _maybe_send_image(update, "nexus")
    await update.message.reply_text("🔗 Nexus connection established.")


async def decode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Decode information"""
    logger.info("decode_command_invoked", user_id=update.effective_user.id)
    
    data = " ".join(context.args) if context.args else "0x0"
    decoded = f"Decoded: {data}"
    await _maybe_send_image(update, "decode")
    await update.message.reply_text(f"🔓 {decoded}")


async def codex_scan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Full codex scan"""
    logger.info("codex_scan_command_invoked", user_id=update.effective_user.id)
    
    redis_client.set(f"agent:0xCODEXbot:last_scan", str(update.message.date))
    await _maybe_send_image(update, "codex_scan")
    await update.message.reply_text("🔬 Full CODEX scan initiated. Results processing...")


def main() -> None:
    """Start the bot"""
    logger.info("starting_0xCODEXbot")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("lore", lore))
    app.add_handler(CommandHandler("codex", codex))
    app.add_handler(CommandHandler("law", law))
    app.add_handler(CommandHandler("state", state))
    app.add_handler(CommandHandler("observe", observe))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("null", null_cmd))
    app.add_handler(CommandHandler("void", void_cmd))
    app.add_handler(CommandHandler("rollicking", rollicking))
    app.add_handler(CommandHandler("og", og_cmd))
    app.add_handler(CommandHandler("prime", prime_cmd))
    app.add_handler(CommandHandler("root", root_cmd))
    app.add_handler(CommandHandler("gen", gen_cmd))
    app.add_handler(CommandHandler("nexus", nexus_cmd))
    app.add_handler(CommandHandler("decode", decode_cmd))
    app.add_handler(CommandHandler("codex_scan", codex_scan))
    
    logger.info("handlers_registered")
    
    # 🚀 Announce startup rollcall
    announce_startup_rollcall(inter_agent, persona_engine.profile, "0xCODEX")
    
    app.run_polling()


if __name__ == "__main__":
    main()
