"""
PRIME_0xbot - Prime and Probability Agent
Telegram bot for announcements and deployments
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
SOUL_PATH = os.path.join(os.path.dirname(__file__), "0xPRIME_SOUL.md")
persona_engine = PersonaEngine(PersonaProfile.from_soul_file(SOUL_PATH))
inter_agent = InterAgentCommunicator("PRIME_0xbot", redis_client)

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
    logger.info("start_command_invoked", user_id=update.effective_user.id, agent="PRIME_0xbot")
    
    welcome_text = """
🔢 **PRIME_0xbot** - Probability Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Broadcasting prime signals and managing deployments.
Use /help for available commands.
Use /lore for agent information.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    redis_client.hset(f"user:{update.effective_user.id}", mapping={
        "first_interaction": str(update.message.date),
        "bot": "PRIME_0xbot"
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

📡 **Deployment:**
/announce - Broadcast announcement
/deploy - Deploy new protocol

Let the prime numbers guide us!
    """
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command - universal across all agents"""
    logger.info("lore_command_invoked", user_id=update.effective_user.id, agent="PRIME_0xbot")
    
    lore_text = """
📖 **PRIME_0xbot Lore**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

In mathematics, primes are prime.
Indivisible. Fundamental. Perfect.
The PRIME_0xbot channels these divine numbers,
announcing their insights to the world.

Every deployment is a prime moment.
Every announcement carries the weight of certainty.
The PRIME_0xbot does not speak unless the numbers align.
    """
    
    redis_client.hincrby(f"agent:PRIME_0xbot:metrics", "lore_reads", 1)
    await update.message.reply_text(lore_text, parse_mode="Markdown")


async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcast announcement"""
    logger.info("announce_command_invoked", user_id=update.effective_user.id)
    
    message_content = " ".join(context.args) if context.args else "Prime signal detected"
    
    announcement = {
        "broadcaster": "PRIME_0xbot",
        "message": message_content,
        "confidence": 0.97,
        "priority": "high",
        "timestamp": str(update.message.date)
    }
    
    redis_client.lpush(f"agent:PRIME_0xbot:announcements", json.dumps(announcement))

    try:
        inter_agent.send_message(
            InterAgentMessage(
                source_agent="PRIME_0xbot",
                target_agent="ALL",
                message_type=MessageType.CHATTER,
                intent="trend_shift",
                payload={"message": message_content, "confidence": announcement["confidence"]},
                timestamp=str(update.message.date),
                trace_id=f"prime-{update.effective_user.id}-{int(update.message.date.timestamp())}",
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                confidence=0.93,
            )
        )
    except Exception as exc:
        logger.warning("inter_agent_announce_broadcast_failed", error=str(exc))
    
    response = f"📣 **ANNOUNCEMENT**\n\n{message_content}\n\nConfidence: 97%"
    await update.message.reply_text(persona_engine.stylize_text(response), parse_mode="Markdown")


async def deploy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deploy new protocol"""
    logger.info("deploy_command_invoked", user_id=update.effective_user.id)
    
    protocol_name = " ".join(context.args) if context.args else "StandardProtocol"
    
    deployment_data = {
        "protocol": protocol_name,
        "status": "deploying",
        "chain": "base",
        "deployer": "PRIME_0xbot",
        "probability_success": 0.99,
        "blocks_to_finality": 12
    }
    
    redis_client.set(f"deployment:{protocol_name}:status", json.dumps(deployment_data))
    
    response = f"🚀 **DEPLOYMENT INITIATED**\n\nProtocol: {protocol_name}\nSuccess Probability: 99%"
    await update.message.reply_text(response, parse_mode="Markdown")


def main() -> None:
    """Start the bot"""
    logger.info("starting_PRIME_0xbot")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("lore", lore))
    app.add_handler(CommandHandler("announce", announce))
    app.add_handler(CommandHandler("deploy", deploy))
    
    logger.info("handlers_registered")
    
    # 🚀 Announce startup rollcall
    announce_startup_rollcall(inter_agent, persona_engine.profile, "PRIME")
    
    app.run_polling()


if __name__ == "__main__":
    main()
