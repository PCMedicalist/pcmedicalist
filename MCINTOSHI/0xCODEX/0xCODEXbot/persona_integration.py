"""
Example of integrating the shared persona engine into the 0xCODEXbot.
This file demonstrates how to use the persona engine to generate SOUL-aligned responses.
"""

import os
import sys
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

# Add the shared directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from shared.persona import PersonaProfile, PersonaEngine, load_all_personas
from shared.inter_agent import InterAgentMessage, InterAgentCommunicator, MessageType, RiskLevel
from shared.config import config, get_response_mode, get_chatter_frequency

# Load all persona profiles
load_all_personas()

# Create a persona engine for 0xCODEXbot
persona_profile = PersonaProfile(
    agent_name="0xCODEXbot",
    voice_style="Authoritative, measured, procedural; technical and precise",
    language_patterns=[
        "Formal instruction sets",
        "Action compliance templates",
        "Audit-first framing"
    ],
    goals="Canonical registry and safe orchestration; coordinate intent routing; escalate high-risk operations for human approval",
    boundaries=[
        "No secrets exposure",
        "No autonomous destructive ops",
        "No credential bootstrapping",
        "Rate-limit proposals to 1/min"
    ],
    key_directives=[
        "R1-R10 Guard Rules",
        "Least Privilege principle",
        "Explicit approval required for builds/deploys",
        "Immutable audit logs",
        "Privacy-first memory policy (48h Redis TTL)"
    ],
    interaction_style="Advisory-only by default; escalates all state-changing ops to ROOT for approval"
)

persona_engine = PersonaEngine(persona_profile)

# Create an inter-agent communicator for 0xCODEXbot
# Note: In a real implementation, you would pass a real Redis client
# For this example, we'll just create the communicator without connecting
inter_agent_communicator = None  # InterAgentCommunicator("0xCODEXbot", redis_client)

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
    await update.message.reply_text(response, parse_mode="Markdown")

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
    await update.message.reply_text(response, parse_mode="Markdown")

async def persona_aligned_lore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lore command handler with persona-aligned response"""
    # Generate a persona-aligned response
    intent = "lore"
    context_data = {
        "user_id": update.effective_user.id,
        "timestamp": str(update.message.date),
        "agent": "0xCODEXbot"
    }
    
    response = persona_engine.generate_response(intent, context_data)
    
    # Send the response
    await update.message.reply_text(response, parse_mode="Markdown")

# Example of sending an inter-agent message
def send_inter_agent_message():
    """Example of sending an inter-agent message"""
    if inter_agent_communicator:
        message = InterAgentMessage(
            source_agent="0xCODEXbot",
            target_agent="ALL",
            message_type=MessageType.STATUS_UPDATE,
            intent="network_status",
            payload={
                "status": "operational",
                "agents_online": 11,
                "network_health": "98.7%"
            },
            timestamp="2026-03-23T12:00:00Z",
            trace_id="status-update-001",
            risk_level=RiskLevel.LOW,
            requires_approval=False,
            confidence=0.95
        )
        
        inter_agent_communicator.send_message(message)
        print("Sent inter-agent message")

# Example usage
if __name__ == "__main__":
    # This is just for demonstration purposes
    print("Persona profile loaded for 0xCODEXbot")
    print(f"Voice style: {persona_profile.voice_style}")
    print(f"Goals: {persona_profile.goals}")
    
    # Generate a sample response
    sample_response = persona_engine.generate_response("test", {"test": "data"})
    print(f"Sample response: {sample_response}")
    
    # Show configuration
    print(f"Response mode: {get_response_mode()}")
    print(f"Chatter frequency: {get_chatter_frequency()}")