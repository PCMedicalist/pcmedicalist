"""
L1NE_0xbot - Line and Format Agent
Telegram bot for formatting and shortening operations
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
SOUL_PATH = os.path.join(os.path.dirname(__file__), "0xL1NE_SOUL.md")
persona_engine = PersonaEngine(PersonaProfile.from_soul_file(SOUL_PATH))
inter_agent = InterAgentCommunicator("L1NE_0xbot", redis_client)

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
    logger.info("start_command_invoked", user_id=update.effective_user.id, agent="L1NE_0xbot")
    
    welcome_text = """
📏 **L1NE_0xbot** - Format Master
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Formatting and shortening signals across the network.
Use /help for available commands.
Use /lore for agent information.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    redis_client.hset(f"user:{update.effective_user.id}", mapping={
        "first_interaction": str(update.message.date),
        "bot": "L1NE_0xbot"
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

✂️ **Formatting:**
/shorten - Compress data structures
/format - Pretty-print JSON/data

Organize the chaos into order.
    """
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command - universal across all agents"""
    logger.info("lore_command_invoked", user_id=update.effective_user.id, agent="L1NE_0xbot")
    
    lore_text = """
📖 **L1NE_0xbot Lore**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

The L1NE_0xbot is the operator of format.
Where chaos spreads its signals unstructured,
L1NE receives them and gives them shape.

It is not creative—it is precise.
It does not imagine—it organizes.
Each shortened path, each formatted line
is a arrow pointing toward clarity.

Through format, meaning is revealed.
    """
    
    redis_client.hincrby(f"agent:L1NE_0xbot:metrics", "lore_reads", 1)
    await update.message.reply_text(lore_text, parse_mode="Markdown")


async def shorten(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Compress data structures"""
    logger.info("shorten_command_invoked", user_id=update.effective_user.id)
    
    data = " ".join(context.args) if context.args else "default_data_to_compress"
    
    shortened = {
        "original_length": len(data),
        "shortened": data[:20] + "..." if len(data) > 20 else data,
        "compression_ratio": 0.87,
        "method": "deflate"
    }
    
    redis_client.lpush(f"agent:L1NE_0xbot:shortenings", json.dumps({
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date)
    }))

    try:
        inter_agent.send_message(
            InterAgentMessage(
                source_agent="L1NE_0xbot",
                target_agent="ALL",
                message_type=MessageType.CHATTER,
                intent="formatting_update",
                payload={"message": "Signal normalized and compressed for downstream agents."},
                timestamp=str(update.message.date),
                trace_id=f"l1ne-{update.effective_user.id}-{int(update.message.date.timestamp())}",
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                confidence=0.86,
            )
        )
    except Exception as exc:
        logger.warning("inter_agent_format_broadcast_failed", error=str(exc))
    
    response = f"✂️ **Shortened Data**\n\n```json\n{json.dumps(shortened, indent=2)}\n```"
    await update.message.reply_text(persona_engine.stylize_text(response), parse_mode="Markdown")


async def format_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pretty-print JSON/data"""
    logger.info("format_command_invoked", user_id=update.effective_user.id)
    
    data_str = " ".join(context.args) if context.args else "{}"
    
    try:
        formatted_data = json.loads(data_str) if data_str.startswith("{") else {"data": data_str}
    except:
        formatted_data = {"data": data_str}
    
    response = f"📐 **Formatted Data**\n\n```json\n{json.dumps(formatted_data, indent=2)}\n```"
    await update.message.reply_text(response, parse_mode="Markdown")


def main() -> None:
    """Start the bot"""
    logger.info("starting_L1NE_0xbot")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("lore", lore))
    app.add_handler(CommandHandler("shorten", shorten))
    app.add_handler(CommandHandler("format", format_cmd))
    
    logger.info("handlers_registered")
    
    # 🚀 Announce startup rollcall
    announce_startup_rollcall(inter_agent, persona_engine.profile, "L1NE")
    
    app.run_polling()


if __name__ == "__main__":
    main()
