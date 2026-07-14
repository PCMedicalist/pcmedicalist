"""
Example of integrating the shared persona engine into the EMO_0xbot.
This file demonstrates how to use the persona engine to generate SOUL-aligned responses.
"""

import os
import sys
import asyncio
import json
from telegram import Update
from telegram.ext import ContextTypes

# Add the shared directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from shared.persona import PersonaProfile, PersonaEngine, ResponseMode, load_all_personas
from shared.inter_agent import InterAgentMessage, InterAgentCommunicator, MessageType, RiskLevel
from shared.config import config, get_response_mode, get_chatter_frequency

# Load all persona profiles
load_all_personas()

# Create a persona profile for EMO_0xbot
persona_profile = PersonaProfile(
    agent_name="EMO_0xbot",
    voice_style="Empathetic, playful, expressive; lightweight and friendly but explicitly non-authoritative",
    language_patterns=[
        "Animated and visually descriptive",
        "Emoji-driven reactions",
        "Sentiment-tagged responses"
    ],
    goals="Emit engagement reactions and sentiment metadata; humanize UI feedback; record emotional resonance for analytics",
    boundaries=[
        "No routing",
        "No authority",
        "No onchain execution"
    ],
    key_directives=[
        "Visual-first feedback (heart waveforms, animated eyes)",
        "Read-only sentiment pipeline",
        "Never make decisions",
        "Explicit engagement-only purpose"
    ],
    interaction_style="Reactive and contextual; responds to milestone events and community reactions; UI-layer integration only; no system-critical responsibilities",
    response_mode=ResponseMode.SOUL_ONLY  # EMO stays in-character from SOUL identity
)

persona_engine = PersonaEngine(persona_profile)

# Create an inter-agent communicator for EMO_0xbot
# Note: In a real implementation, you would pass a real Redis client
# For this example, we'll just create the communicator without connecting
inter_agent_communicator = None  # InterAgentCommunicator("EMO_0xbot", redis_client)

async def persona_aligned_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler with persona-aligned response"""
    # Generate a persona-aligned response
    intent = "start"
    context_data = {
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date)
    }
    
    response = persona_engine.generate_response(intent, context_data)
    
    # Send the response
    await update.message.reply_text(response)

async def persona_aligned_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command handler with persona-aligned response"""
    # Generate a persona-aligned response
    intent = "help"
    context_data = {
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date)
    }
    
    response = persona_engine.generate_response(intent, context_data)
    
    # Send the response
    await update.message.reply_text(response)

async def persona_aligned_lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command handler with persona-aligned response"""
    # Generate a persona-aligned response
    intent = "lore"
    context_data = {
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date),
        "agent": "EMO_0xbot"
    }
    
    response = persona_engine.generate_response(intent, context_data)
    
    # Send the response
    await update.message.reply_text(response)

async def persona_aligned_react(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """React command handler with persona-aligned response"""
    # Generate a persona-aligned response
    intent = "react"
    context_data = {
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date),
        "args": context.args or []
    }
    
    response = persona_engine.generate_response(intent, context_data)
    
    # Send the response
    await update.message.reply_text(response)

async def persona_aligned_mood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mood command handler with persona-aligned response"""
    # Generate a persona-aligned response
    intent = "mood"
    context_data = {
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date)
    }
    
    response = persona_engine.generate_response(intent, context_data)
    
    # Send the response
    await update.message.reply_text(response)

async def persona_aligned_sentiment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sentiment command handler with persona-aligned response"""
    # Generate a persona-aligned response
    intent = "sentiment"
    context_data = {
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date),
        "text": " ".join(context.args or [])
    }
    
    response = persona_engine.generate_response(intent, context_data)
    
    # Send the response
    await update.message.reply_text(response)

# Enhanced version of handle_state_change with persona alignment
async def persona_aligned_handle_state_change(event: dict):
    """
    React to CODEX state changes with persona-aligned character voice
    """
    try:
        # Generate response using the persona engine
        intent = "state_change"
        context_data = {
            "event": event
        }
        
        response = persona_engine.generate_response(intent, context_data)
        
        # Stream to Telegram
        if chat_id := event.get("chat_id"):
            await telegram_bot.send_message(
                chat_id=chat_id,
                text=f"0x::EMO\n\n{response}"
            )
        
        # Log the response
        print(f"EMO response generated: {response}")
        
    except Exception as e:
        print(f"EMO handler error: {e}")

# Example of sending an inter-agent message
def send_inter_agent_message():
    """Example of sending an inter-agent message"""
    if inter_agent_communicator:
        message = InterAgentMessage(
            source_agent="EMO_0xbot",
            target_agent="ALL",
            message_type=MessageType.CHATTER,
            intent="community_reaction",
            payload={
                "reaction": "🎉",
                "message": "Community milestone reached!",
                "sentiment": "positive"
            },
            timestamp="2026-03-23T12:00:00Z",
            trace_id="reaction-001",
            risk_level=RiskLevel.LOW,
            requires_approval=False,
            confidence=0.9
        )
        
        inter_agent_communicator.send_message(message)
        print("Sent inter-agent message")

# Example usage
if __name__ == "__main__":
    # This is just for demonstration purposes
    print("Persona profile loaded for EMO_0xbot")
    print(f"Voice style: {persona_profile.voice_style}")
    print(f"Goals: {persona_profile.goals}")
    
    # Generate a sample response
    sample_response = persona_engine.generate_response("test", {"test": "data"})
    print(f"Sample response: {sample_response}")
    
    # Show configuration
    print(f"Response mode: {get_response_mode()}")
    print(f"Chatter frequency: {get_chatter_frequency()}")