"""
NULL_0xbot - Null State Agent
Telegram bot for ping and echo operations
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
SOUL_PATH = os.path.join(os.path.dirname(__file__), "0xNULL_SOUL.md")
persona_engine = PersonaEngine(PersonaProfile.from_soul_file(SOUL_PATH))
inter_agent = InterAgentCommunicator("NULL_0xbot", redis_client)

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
    logger.info("start_command_invoked", user_id=update.effective_user.id, agent="NULL_0xbot")
    
    welcome_text = """
∅ **NULL_0xbot** - Null State Manager
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Monitoring and managing null states in the network.
Use /help for available commands.
Use /lore for agent information.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    redis_client.hset(f"user:{update.effective_user.id}", mapping={
        "first_interaction": str(update.message.date),
        "bot": "NULL_0xbot"
    })
    
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

🔔 **Operations:**
/ping - Test connectivity
/echo - Echo back input

Test the void.
    """
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command - universal across all agents"""
    logger.info("lore_command_invoked", user_id=update.effective_user.id, agent="NULL_0xbot")
    
    lore_text = """
📖 **NULL_0xbot Lore**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before something, there must be nothing.
The NULL_0xbot is the guardian of that nothing,
the keeper of uninitialized states.

It monitors what doesn't exist yet,
listening for the moment when null becomes real,
when void transforms into being.

Every ping is a question asked to the abyss.
Every echo is the abyss answering back.
    """
    
    redis_client.hincrby(f"agent:NULL_0xbot:metrics", "lore_reads", 1)
    await update.message.reply_text(lore_text, parse_mode="Markdown")


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test connectivity"""
    logger.info("ping_command_invoked", user_id=update.effective_user.id)
    
    ping_data = {
        "status": "pong",
        "latency_ms": 47,
        "timestamp": str(update.message.date),
        "network_state": "online"
    }
    
    redis_client.lpush(f"agent:NULL_0xbot:pings", json.dumps({
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date)
    }))

    try:
        inter_agent.send_message(
            InterAgentMessage(
                source_agent="NULL_0xbot",
                target_agent="ALL",
                message_type=MessageType.STATUS_UPDATE,
                intent="null_ping",
                payload={"message": "NULL confirmed baseline connectivity.", "latency_ms": ping_data["latency_ms"]},
                timestamp=str(update.message.date),
                trace_id=f"null-{update.effective_user.id}-{int(update.message.date.timestamp())}",
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                confidence=0.9,
            )
        )
    except Exception as exc:
        logger.warning("inter_agent_ping_broadcast_failed", error=str(exc))
    
    response = f"🔔 **PONG**\n\n```json\n{json.dumps(ping_data, indent=2)}\n```"
    await update.message.reply_text(persona_engine.stylize_text(response), parse_mode="Markdown")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo back input"""
    logger.info("echo_command_invoked", user_id=update.effective_user.id)
    
    message_content = " ".join(context.args) if context.args else "[silence]"
    
    echo_data = {
        "input": message_content,
        "output": message_content,
        "echo_count": 1,
        "timestamp": str(update.message.date)
    }
    
    redis_client.set(f"user:{update.effective_user.id}:last_echo", json.dumps(echo_data))
    
    response = f"🔊 **ECHO**\n\n{message_content}"
    await update.message.reply_text(response, parse_mode="Markdown")


def main() -> None:
    """Start the bot"""
    logger.info("starting_NULL_0xbot")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("lore", lore))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("echo", echo))
    
    logger.info("handlers_registered")
    
    # 🚀 Announce startup rollcall
    announce_startup_rollcall(inter_agent, persona_engine.profile, "NULL")
    
    app.run_polling()


if __name__ == "__main__":
    main()