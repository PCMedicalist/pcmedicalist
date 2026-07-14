"""
Initialization file for the shared modules package.
"""

# Import the main classes and functions for easy access
from .persona import PersonaProfile, PersonaEngine, load_all_personas
from .inter_agent import InterAgentMessage, InterAgentCommunicator, MessageType, RiskLevel
from .config import config, get_response_mode, get_chatter_frequency
from .persona_template import create_persona_profile

__all__ = [
    "PersonaProfile",
    "PersonaEngine",
    "load_all_personas",
    "InterAgentMessage",
    "InterAgentCommunicator",
    "MessageType",
    "RiskLevel",
    "config",
    "get_response_mode",
    "get_chatter_frequency",
    "create_persona_profile"
]