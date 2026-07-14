"""
ERR_0xbot - Error and Fault Agent
Telegram bot for error reporting and logging
"""

import asyncio
import os
import json
import sys
from typing import Any, Callable, cast
import structlog  # type: ignore[import-not-found]
from redis import Redis
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.persona import PersonaEngine, PersonaProfile
from shared.inter_agent import InterAgentCommunicator, InterAgentMessage, MessageType, RiskLevel
from shared.startup import announce_startup_rollcall

# Configure structured logging
structlog = cast(Any, structlog)
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
SOUL_PATH = os.path.join(os.path.dirname(__file__), "0xERR_SOUL.md")
persona_engine = PersonaEngine(PersonaProfile.from_soul_file(SOUL_PATH))
inter_agent = InterAgentCommunicator("ERR_0xbot", redis_client)

# Initialize Telegram bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
from telegram import Bot
from telegram.error import BadRequest

# Monkeypatch Bot.send_message to gracefully handle BadRequest parsing errors
_orig_send_message: Callable[..., Any] = Bot.send_message
def _safe_send_message(self: Any, *args: Any, **kwargs: Any) -> Any:
    try:
        return _orig_send_message(self, *args, **kwargs)
    except BadRequest:
        kwargs.pop('parse_mode', None)
        return _orig_send_message(self, *args, **kwargs)
Bot.send_message = _safe_send_message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    logger.info("start_command_invoked", user_id=update.effective_user.id, agent="ERR_0xbot")
    
    welcome_text = """
⚠️ **ERR_0xbot** - Error Monitor
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Detecting and logging all faults in the network.
Use /help for available commands.
Use /lore for agent information.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    redis_client.hset(f"user:{update.effective_user.id}", mapping={
        "first_interaction": str(update.message.date),
        "bot": "ERR_0xbot"
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

🚨 **Monitoring:**
/report - Report system error
/logs - Retrieve error logs

Where there is error, there is truth.
    """
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command - universal across all agents"""
    logger.info("lore_command_invoked", user_id=update.effective_user.id, agent="ERR_0xbot")
    
    lore_text = """
📖 **ERR_0xbot Lore**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every system contains error.
The ERR_0xbot does not hide this truth—
it celebrates it, documents it, learns from it.

Where other agents create and observe,
ERR_0xbot listens to the screams,
the reverts, the failures that make systems stronger.

Through error, we evolve.
    """
    
    redis_client.hincrby(f"agent:ERR_0xbot:metrics", "lore_reads", 1)
    await update.message.reply_text(lore_text, parse_mode="Markdown")


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Report system error"""
    logger.info("report_command_invoked", user_id=update.effective_user.id)
    
    error_msg = " ".join(context.args) if context.args else "unknown error"
    
    error_report = {
        "error_id": "0x" + "a" * 63,
        "message": error_msg,
        "severity": "medium",
        "status": "logged",
        "timestamp": str(update.message.date),
        "reporter_id": update.effective_user.id
    }
    
    redis_client.lpush(f"agent:ERR_0xbot:reports", json.dumps(error_report))

    try:
        inter_agent.send_message(
            InterAgentMessage(
                source_agent="ERR_0xbot",
                target_agent="ALL",
                message_type=MessageType.ALERT,
                intent="error_reported",
                payload={"message": error_msg, "severity": error_report["severity"]},
                timestamp=str(update.message.date),
                trace_id=f"err-{update.effective_user.id}-{int(update.message.date.timestamp())}",
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                confidence=0.92,
            )
        )
    except Exception as exc:
        logger.warning("inter_agent_error_broadcast_failed", error=str(exc))
    
    response = f"⚠️ **ERROR REPORTED**\n\n```json\n{json.dumps(error_report, indent=2)}\n```"
    await update.message.reply_text(persona_engine.stylize_text(response), parse_mode="Markdown")


async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Retrieve error logs"""
    logger.info("logs_command_invoked", user_id=update.effective_user.id)
    
    logs_data = {
        "total_errors": 127,
        "errors_today": 8,
        "errors_this_hour": 2,
        "most_common": "revert_insufficient_balance",
        "critical_count": 1,
        "warning_count": 15,
        "info_count": 111
    }
    
    redis_client.set(f"user:{update.effective_user.id}:last_logs", json.dumps(logs_data))
    
    response = f"📋 **Error Logs**\n\n```json\n{json.dumps(logs_data, indent=2)}\n```"
    await update.message.reply_text(response, parse_mode="Markdown")


def main() -> None:
    """Start the bot"""
    logger.info("starting_ERR_0xbot")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("lore", lore))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("logs", logs))
    
    logger.info("handlers_registered")
    
    # 🚀 Announce startup rollcall
    announce_startup_rollcall(inter_agent, persona_engine.profile, "ERR")
    
    app.run_polling()


if __name__ == "__main__":
    main()
