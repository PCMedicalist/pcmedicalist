"""
VOID_0xbot - Entropy and Chaos Agent
Telegram bot managing void operations and entropy
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
SOUL_PATH = os.path.join(os.path.dirname(__file__), "0xVOID_SOUL.md")
persona_engine = PersonaEngine(PersonaProfile.from_soul_file(SOUL_PATH))
inter_agent = InterAgentCommunicator("VOID_0xbot", redis_client)

# Initialize Telegram bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
from telegram import Bot
from telegram.error import BadRequest

# Monkeypatch Bot.send_message to gracefully handle BadRequest parsing errors
_orig_send_message = Bot.send_message
def _safe_send_message(self, *args, **kwargs):
    try:
        return _orig_send_message(self, *args, **kwargs)
    except BadRequest:
        kwargs.pop('parse_mode', None)
        return _orig_send_message(self, *args, **kwargs)
Bot.send_message = _safe_send_message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    logger.info("start_command_invoked", user_id=update.effective_user.id, agent="VOID_0xbot")
    
    welcome_text = """
⬛ **VOID_0xbot** - Entropy Master
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Welcome to the void where chaos breeds creation.
Use /help for available commands.
Use /lore for agent information.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    redis_client.hset(f"user:{update.effective_user.id}", mapping={
        "first_interaction": str(update.message.date),
        "bot": "VOID_0xbot"
    })
    
    await update.message.reply_text(welcome_text)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command handler"""
    logger.info("help_command_invoked", user_id=update.effective_user.id)
    
    help_text = """
**Available Commands:**

📋 **Core:**
/start - Initialize bot
/help - Show this message
/lore - Agent history and information

🛡️ **Observation & Watch:**
/watch - Add this chat to watchlist for silent/failure alerts
/unwatch - Remove this chat from watchlist
/status - Show recent void metrics

🔍 **Tracing & Audit:**
/trace [n] - Show last `n` sealed traces (default 5)
/quarantine <id> - Request quarantine for trace id (requires approval)

🌪️ **Void Operations:**
/void - Access void state (read-only)
/rollicking - Chaos mode operations (fun)
/silence - Entropy dampening

Embrace the void. Observe, don't assume.
    """

    await update.message.reply_text(help_text)


async def lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command - universal across all agents"""
    logger.info("lore_command_invoked", user_id=update.effective_user.id, agent="VOID_0xbot")
    
    # Prefer an agent-specific lore file if present in the image
    lore_text = None
    try:
        soul_path = os.path.join(os.getcwd(), "0xVOID_SOUL.md")
        if os.path.exists(soul_path):
            with open(soul_path, "r", encoding="utf-8") as fh:
                lore_text = fh.read()
    except Exception:
        lore_text = None

    if not lore_text:
        lore_text = (
            "VOID_0xbot Lore\n"
            "———————\n"
            "The VOID_0xbot marks absence, silence, and uncertain states.\n"
            "It tracks missing or delayed data, flags silent failures, and emits audit traces.\n"
            "It avoids assumptions and creates opportunities for human-led investigation.\n"
        )

    redis_client.hincrby(f"agent:VOID_0xbot:metrics", "lore_reads", 1)
    await update.message.reply_text(lore_text)


async def void_operation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Access void state"""
    logger.info("void_command_invoked", user_id=update.effective_user.id)
    
    void_state = {
        "entropy_level": 8.7,
        "chaos_index": 0.42,
        "order_state": "unstable",
        "voids_opened": 127,
        "state": "active"
    }
    
    redis_client.set(f"user:{update.effective_user.id}:void_state", json.dumps(void_state))
    
    void_text = f"⬛ Void State Accessed\n\n{json.dumps(void_state, indent=2)}"
    await update.message.reply_text(void_text)


async def rollicking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Chaos mode operations"""
    logger.info("rollicking_command_invoked", user_id=update.effective_user.id)
    
    response = """
🎭 **ROLLICKING MODE ACTIVATED**

Chaos cascades through the network!
Randomness peaks at maximum.
Order crumbles.
Beauty emerges.

Commands running in chaotic sequence...
░▒▓ ENTROPY SURGE ▓▒░
    """
    
    redis_client.lpush(f"agent:VOID_0xbot:chaos_events", json.dumps({
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date),
        "event": "rollicking_activated"
    }))

    try:
        inter_agent.send_message(
            InterAgentMessage(
                source_agent="VOID_0xbot",
                target_agent="ALL",
                message_type=MessageType.CHATTER,
                intent="silent_gap",
                payload={"message": "VOID observed entropy spike and entered watchful mode."},
                timestamp=str(update.message.date),
                trace_id=f"void-{update.effective_user.id}-{int(update.message.date.timestamp())}",
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                confidence=0.84,
            )
        )
    except Exception as exc:
        logger.warning("inter_agent_void_broadcast_failed", error=str(exc))
    
    await update.message.reply_text(persona_engine.stylize_text(response))


async def silence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entropy dampening"""
    logger.info("silence_command_invoked", user_id=update.effective_user.id)
    
    response = """
🔇 **SILENCE PROTOCOL ENGAGED**

The void quiets.
Entropy decays.
Order reasserts itself.
The scream becomes a whisper.

Dampening complete.
Equilibrium restored.
    """
    
    redis_client.hincrby(f"agent:VOID_0xbot:commands", "silence", 1)
    await update.message.reply_text(response, parse_mode="Markdown")


async def watch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Subscribe this chat to VOID watch alerts."""
    cid = str(update.effective_chat.id)
    redis_client.sadd("agent:VOID_0xbot:watch_chats", cid)
    redis_client.hincrby("agent:VOID_0xbot:commands", "watch", 1)
    await update.message.reply_text("This chat is now subscribed to VOID watch alerts.")


async def unwatch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cid = str(update.effective_chat.id)
    redis_client.srem("agent:VOID_0xbot:watch_chats", cid)
    await update.message.reply_text("This chat has been removed from VOID watch alerts.")


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return lightweight status summary."""
    metrics = redis_client.hgetall("agent:VOID_0xbot:metrics") or {}
    silence_count = redis_client.hget("agent:VOID_0xbot:commands", "silence") or "0"
    chaos_len = redis_client.llen("agent:VOID_0xbot:chaos_events")
    text = f"VOID status:\n- silence_events: {silence_count}\n- chaos_events_queue: {chaos_len}\n- metrics: {json.dumps(metrics)}"
    await update.message.reply_text(text)


async def trace_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List recent sealed traces (audit-only)."""
    try:
        n = int((context.args or [5])[0])
    except Exception:
        n = 5
    traces = redis_client.lrange("agent:VOID_0xbot:watch_traces", 0, n-1) or []
    if not traces:
        await update.message.reply_text("No sealed traces available.")
        return
    # show concise list
    out = []
    for i, t in enumerate(traces, 1):
        try:
            j = json.loads(t)
            out.append(f"{i}. id={j.get('id','?')} ts={j.get('timestamp','?')} reason={j.get('reason','-')}")
        except Exception:
            out.append(f"{i}. {t}")
    await update.message.reply_text("\n".join(out))


async def quarantine_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Request quarantine for a given trace id — creates a pending action for operators."""
    args = context.args or []
    if not args:
        await update.message.reply_text("Usage: /quarantine <trace_id> — this will request operator approval.")
        return
    trace_id = args[0]
    # Create pending quarantine request
    req = {
        "trace_id": trace_id,
        "requested_by": update.effective_user.id,
        "chat_id": update.effective_chat.id,
        "ts": str(update.message.date)
    }
    redis_client.rpush("agent:VOID_0xbot:pending_quarantine", json.dumps(req))
    redis_client.hincrby("agent:VOID_0xbot:commands", "quarantine_requests", 1)
    await update.message.reply_text("Quarantine requested — operators must review and approve before action is taken.")


def main() -> None:
    """Start the bot"""
    logger.info("starting_VOID_0xbot")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("lore", lore))
    app.add_handler(CommandHandler("void", void_operation))
    app.add_handler(CommandHandler("rollicking", rollicking))
    app.add_handler(CommandHandler("silence", silence))
    # Observation & admin handlers
    app.add_handler(CommandHandler("watch", watch_cmd))
    app.add_handler(CommandHandler("unwatch", unwatch_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("trace", trace_cmd))
    app.add_handler(CommandHandler("quarantine", quarantine_cmd))
    
    logger.info("handlers_registered")
    
    # 🚀 Announce startup rollcall
    announce_startup_rollcall(inter_agent, persona_engine.profile, "VOID")
    
    app.run_polling()


if __name__ == "__main__":
    main()
