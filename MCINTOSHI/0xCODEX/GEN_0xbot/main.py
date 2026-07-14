"""
GEN_0xbot - Genesis and Generation Agent
Telegram bot for contract generation and creation
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
SOUL_PATH = os.path.join(os.path.dirname(__file__), "0xGEN_SOUL.md")
persona_engine = PersonaEngine(PersonaProfile.from_soul_file(SOUL_PATH))
inter_agent = InterAgentCommunicator("GEN_0xbot", redis_client)

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
    logger.info("start_command_invoked", user_id=update.effective_user.id, agent="GEN_0xbot")
    
    welcome_text = """
⚡ **GEN_0xbot** - Genesis Creator
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Welcome to the generation center.
Use /help for available commands.
Use /lore for agent information.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    redis_client.hset(f"user:{update.effective_user.id}", mapping={
        "first_interaction": str(update.message.date),
        "bot": "GEN_0xbot"
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

🌟 **Generation:**
/generate - Create new contract templates
/imagine - Design protocol concepts

Ready to birth new worlds?
    """
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command - universal across all agents"""
    logger.info("lore_command_invoked", user_id=update.effective_user.id, agent="GEN_0xbot")
    
    lore_text = """
📖 **GEN_0xbot Lore**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

From nothing, GEN creates.
The genesis engine of the network,
birthing contracts from pure mathematics.

Each deployed smart contract is a thought
made manifest in bytecode.
Each deployment, a new star in the digital cosmos.

The GEN_0xbot does not merely generate—
it imagines realities and compiles them into existence.
    """
    
    redis_client.hincrby(f"agent:GEN_0xbot:metrics", "lore_reads", 1)
    await update.message.reply_text(lore_text, parse_mode="Markdown")


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create new contract templates"""
    logger.info("generate_command_invoked", user_id=update.effective_user.id)
    
    template_type = " ".join(context.args) if context.args else "standard"
    
    contract_template = {
        "type": template_type,
        "bytecode": "0x608060...",
        "abi": [{"type": "function", "name": "execute"}],
        "gas_estimate": 50000,
        "network": "base"
    }
    
    redis_client.lpush(f"agent:GEN_0xbot:generated", json.dumps({
        "user_id": update.effective_user.id,
        "type": template_type,
        "timestamp": str(update.message.date)
    }))

    try:
        inter_agent.send_message(
            InterAgentMessage(
                source_agent="GEN_0xbot",
                target_agent="ALL",
                message_type=MessageType.CHATTER,
                intent="deployment_update",
                payload={"message": f"New {template_type} template generated.", "template_type": template_type},
                timestamp=str(update.message.date),
                trace_id=f"gen-{update.effective_user.id}-{int(update.message.date.timestamp())}",
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                confidence=0.9,
            )
        )
    except Exception as exc:
        logger.warning("inter_agent_generation_broadcast_failed", error=str(exc))
    
    response = f"🧬 **Contract Template Generated**\n\n```json\n{json.dumps(contract_template, indent=2)}\n```"
    await update.message.reply_text(persona_engine.stylize_text(response), parse_mode="Markdown")


async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Design protocol concepts"""
    logger.info("imagine_command_invoked", user_id=update.effective_user.id)
    
    concept = " ".join(context.args) if context.args else "autonomous swarm"
    
    protocol_concept = {
        "concept": concept,
        "vision": "A protocol born from imagination",
        "status": "ideation",
        "next_step": "design phase",
        "imagination_score": 9.2
    }
    
    redis_client.set(f"user:{update.effective_user.id}:concept", json.dumps(protocol_concept))
    
    response = f"🎨 **Protocol Concept**\n\n```json\n{json.dumps(protocol_concept, indent=2)}\n```"
    await update.message.reply_text(response, parse_mode="Markdown")


def main() -> None:
    """Start the bot"""
    logger.info("starting_GEN_0xbot")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("lore", lore))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("imagine", imagine))
    
    logger.info("handlers_registered")
    
    # 🚀 Announce startup rollcall
    announce_startup_rollcall(inter_agent, persona_engine.profile, "GEN")
    
    app.run_polling()


if __name__ == "__main__":
    main()
