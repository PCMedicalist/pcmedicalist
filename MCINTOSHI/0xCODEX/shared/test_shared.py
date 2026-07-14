"""
Test script for shared modules.
Verifies that the persona engine and inter-agent communication work correctly.
"""

import sys
import os

# Add the shared directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from persona import PersonaProfile, PersonaEngine, load_all_personas
from inter_agent import InterAgentMessage, InterAgentCommunicator, MessageType, RiskLevel
from config import config, get_response_mode, get_chatter_frequency

def test_persona_profile():
    """Test creating a persona profile"""
    print("Testing persona profile creation...")
    
    # Create a test profile
    profile = PersonaProfile(
        agent_name="TEST_0xbot",
        voice_style="Testy McTestface",
        language_patterns=["testing", "verification"],
        goals="Test all the things",
        boundaries=["Don't break stuff", "Be nice"],
        key_directives=["Verify functionality", "Report issues"],
        interaction_style="Test-oriented"
    )
    
    print(f"Created profile: {profile.agent_name}")
    print(f"Voice style: {profile.voice_style}")
    print(f"Goals: {profile.goals}")
    
    return profile

def test_persona_engine():
    """Test the persona engine"""
    print("\nTesting persona engine...")
    
    profile = test_persona_profile()
    engine = PersonaEngine(profile)
    
    # Test response generation
    response = engine.generate_response("test_intent", {"test": "data"})
    print(f"Generated response: {response}")
    
    return engine

def test_inter_agent_message():
    """Test creating an inter-agent message"""
    print("\nTesting inter-agent message creation...")
    
    message = InterAgentMessage(
        source_agent="TEST_0xbot",
        target_agent="ALL",
        message_type=MessageType.CHATTER,
        intent="test_conversation",
        payload={"test": "data"},
        timestamp="2026-03-23T12:00:00Z",
        trace_id="test-trace-id",
        risk_level=RiskLevel.LOW,
        requires_approval=False,
        confidence=0.9
    )
    
    print(f"Created message from {message.source_agent} to {message.target_agent}")
    print(f"Intent: {message.intent}")
    print(f"Payload: {message.payload}")
    
    # Test serialization
    message_dict = message.to_dict()
    print(f"Serialized message: {message_dict}")
    
    # Test deserialization
    restored_message = InterAgentMessage.from_dict(message_dict)
    print(f"Restored message: {restored_message.source_agent}")
    
    return message

def test_config():
    """Test configuration management"""
    print("\nTesting configuration...")
    
    # Test getting config values
    response_mode = get_response_mode()
    chatter_frequency = get_chatter_frequency()
    
    print(f"Response mode: {response_mode}")
    print(f"Chatter frequency: {chatter_frequency}")
    
    # Test getting nested config values
    llm_provider = config.get("RESPONSE_ENGINE.LLM_PROVIDER")
    template_fallback = config.get("RESPONSE_ENGINE.TEMPLATE_FALLBACK")
    
    print(f"LLM provider: {llm_provider}")
    print(f"Template fallback: {template_fallback}")

def main():
    """Run all tests"""
    print("Running shared module tests...\n")
    
    test_persona_profile()
    test_persona_engine()
    test_inter_agent_message()
    test_config()
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    main()