"""
ROOT_0xbot - Root Foundation Agent
Telegram bot for restart and status operations
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
SOUL_PATH = os.path.join(os.path.dirname(__file__), "0xROOT_SOUL.md")
persona_engine = PersonaEngine(PersonaProfile.from_soul_file(SOUL_PATH))
inter_agent = InterAgentCommunicator("ROOT_0xbot", redis_client)

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
    logger.info("start_command_invoked", user_id=update.effective_user.id, agent="ROOT_0xbot")
    
    welcome_text = """
🌱 **ROOT_0xbot** - Foundation Root
━━━━━━━━━━━━━━━━━━━━━━━━━━━
The foundation of the network awaits your commands.
Use /help for available commands.
Use /lore for agent information.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    redis_client.hset(f"user:{update.effective_user.id}", mapping={
        "first_interaction": str(update.message.date),
        "bot": "ROOT_0xbot"
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

🔧 **Administration:**
/restart - Restart network services
/status - Check network status

Root access granted.
    """
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command - universal across all agents"""
    logger.info("lore_command_invoked", user_id=update.effective_user.id, agent="ROOT_0xbot")
    
    lore_text = """
📖 **ROOT_0xbot Lore**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Below everything is ROOT.
The foundation upon which systems grow,
the base from which all else emerges.

The ROOT_0xbot commands the roots themselves,
able to restart what was broken,
able to diagnose what ails the network.

To speak to ROOT is to speak to the ground of being.
    """
    
    redis_client.hincrby(f"agent:ROOT_0xbot:metrics", "lore_reads", 1)
    await update.message.reply_text(lore_text, parse_mode="Markdown")


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Restart network services"""
    logger.info("restart_command_invoked", user_id=update.effective_user.id)
    
    restart_data = {
        "action": "restart",
        "service": "network",
        "status": "initiated",
        "estimated_recovery": "2 minutes",
        "timestamp": str(update.message.date)
    }
    
    redis_client.lpush(f"agent:ROOT_0xbot:restarts", json.dumps({
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date)
    }))

    try:
        inter_agent.send_message(
            InterAgentMessage(
                source_agent="ROOT_0xbot",
                target_agent="ALL",
                message_type=MessageType.ALERT,
                intent="identity_change",
                payload={"message": "ROOT initiated infrastructure restart sequence.", "service": restart_data["service"]},
                timestamp=str(update.message.date),
                trace_id=f"root-{update.effective_user.id}-{int(update.message.date.timestamp())}",
                risk_level=RiskLevel.MEDIUM,
                requires_approval=True,
                confidence=0.85,
            )
        )
    except Exception as exc:
        logger.warning("inter_agent_restart_broadcast_failed", error=str(exc))
    
    response = f"🔄 **RESTART INITIATED**\n\n```json\n{json.dumps(restart_data, indent=2)}\n```"
    await update.message.reply_text(persona_engine.stylize_text(response), parse_mode="Markdown")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check network status"""
    logger.info("status_command_invoked", user_id=update.effective_user.id)
    
    status_data = {
        "network": "base",
        "status": "healthy",
        "uptime": "847 hours",
        "agents_online": 11,
        "cpu_usage": "34%",
        "memory_usage": "67%",
        "last_block": 15847392,
        "tps": 247.5
    }
    
    redis_client.set(f"user:{update.effective_user.id}:last_status", json.dumps(status_data))
    
    response = f"📊 **Network Status**\n\n```json\n{json.dumps(status_data, indent=2)}\n```"
    await update.message.reply_text(response, parse_mode="Markdown")


def main() -> None:
    """Start the bot"""
    logger.info("starting_ROOT_0xbot")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("lore", lore))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("status", status))
    
    logger.info("handlers_registered")
    
    # 🚀 Announce startup rollcall
    announce_startup_rollcall(inter_agent, persona_engine.profile, "ROOT")
    
    app.run_polling()


if __name__ == "__main__":
    main()
