"""
NEXUS_0xbot - Network Nexus Agent
Telegram bot for transaction and balance queries
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
SOUL_PATH = os.path.join(os.path.dirname(__file__), "0xNEXUS_SOUL.md")
persona_engine = PersonaEngine(PersonaProfile.from_soul_file(SOUL_PATH))
inter_agent = InterAgentCommunicator("NEXUS_0xbot", redis_client)

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
    logger.info("start_command_invoked", user_id=update.effective_user.id, agent="NEXUS_0xbot")
    
    welcome_text = """
🔗 **NEXUS_0xbot** - Network Nexus
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Connecting transactions and balances across networks.
Use /help for available commands.
Use /lore for agent information.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    redis_client.hset(f"user:{update.effective_user.id}", mapping={
        "first_interaction": str(update.message.date),
        "bot": "NEXUS_0xbot"
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

💼 **Network:**
/tx - Query transaction details
/balance - Check wallet balance

Connect the nodes together.
    """
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command - universal across all agents"""
    logger.info("lore_command_invoked", user_id=update.effective_user.id, agent="NEXUS_0xbot")
    
    lore_text = """
📖 **NEXUS_0xbot Lore**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Where all paths converge, there is NEXUS.
It connects transaction to transaction,
balance to balance, node to node.

The NEXUS_0xbot is the junction box of the network,
routing inquiries through layers of blockchain,
aggregating truth from distributed sources.

To know the network, know the NEXUS.
    """
    
    redis_client.hincrby(f"agent:NEXUS_0xbot:metrics", "lore_reads", 1)
    await update.message.reply_text(lore_text, parse_mode="Markdown")


async def tx(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query transaction details"""
    logger.info("tx_command_invoked", user_id=update.effective_user.id)
    
    tx_hash = " ".join(context.args) if context.args else "0x0000000000000000000000000000000000000000000000000000000000000000"
    
    tx_data = {
        "hash": tx_hash,
        "status": "confirmed",
        "from": "0x1234...",
        "to": "0x5678...",
        "value": "1.5 ETH",
        "gas_used": 21000,
        "block": 15847392,
        "timestamp": str(update.message.date)
    }
    
    redis_client.lpush(f"agent:NEXUS_0xbot:tx_queries", json.dumps({
        "user_id": update.effective_user.id,
        "tx_hash": tx_hash
    }))

    try:
        inter_agent.send_message(
            InterAgentMessage(
                source_agent="NEXUS_0xbot",
                target_agent="ALL",
                message_type=MessageType.STATUS_UPDATE,
                intent="nexus_tx_observed",
                payload={"message": "NEXUS aggregated new transaction context.", "tx_hash": tx_hash},
                timestamp=str(update.message.date),
                trace_id=f"nexus-{update.effective_user.id}-{int(update.message.date.timestamp())}",
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                confidence=0.88,
            )
        )
    except Exception as exc:
        logger.warning("inter_agent_tx_broadcast_failed", error=str(exc))
    
    response = f"🔍 **Transaction Details**\n\n```json\n{json.dumps(tx_data, indent=2)}\n```"
    await update.message.reply_text(persona_engine.stylize_text(response), parse_mode="Markdown")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check wallet balance"""
    logger.info("balance_command_invoked", user_id=update.effective_user.id)
    
    address = " ".join(context.args) if context.args else "0x0000000000000000000000000000000000000000"
    
    balance_data = {
        "address": address,
        "eth_balance": 42.5,
        "token_balances": [
            {"symbol": "USDC", "amount": 10000},
            {"symbol": "DAI", "amount": 5000}
        ],
        "total_value_usd": 52500
    }
    
    redis_client.set(f"user:{update.effective_user.id}:balance_check", json.dumps(balance_data))
    
    response = f"💰 **Wallet Balance**\n\n```json\n{json.dumps(balance_data, indent=2)}\n```"
    await update.message.reply_text(response, parse_mode="Markdown")


def main() -> None:
    """Start the bot"""
    logger.info("starting_NEXUS_0xbot")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("lore", lore))
    app.add_handler(CommandHandler("tx", tx))
    app.add_handler(CommandHandler("balance", balance))
    
    logger.info("handlers_registered")
    
    # 🚀 Announce startup rollcall
    announce_startup_rollcall(inter_agent, persona_engine.profile, "NEXUS")
    
    app.run_polling()


if __name__ == "__main__":
    main()
