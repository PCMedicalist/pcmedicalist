"""
Test script for persona integration.
Verifies that the persona engine can generate responses for different agents.
"""

import sys
import os

# Add the shared directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from persona import PersonaProfile, PersonaEngine, load_all_personas
from config import get_response_mode, get_chatter_frequency

def test_codex_persona():
    """Test creating a persona profile for 0xCODEXbot"""
    print("Testing 0xCODEXbot persona profile creation...")
    
    # Create a persona profile for 0xCODEXbot
    profile = PersonaProfile(
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
    
    print(f"Created profile: {profile.agent_name}")
    print(f"Voice style: {profile.voice_style}")
    print(f"Goals: {profile.goals}")
    
    # Create a persona engine
    engine = PersonaEngine(profile)
    
    # Test response generation
    response = engine.generate_response("test_intent", {"test": "data"})
    print(f"Generated response: {response}")
    
    return profile, engine

def test_emo_persona():
    """Test creating a persona profile for EMO_0xbot"""
    print("\nTesting EMO_0xbot persona profile creation...")
    
    # Create a persona profile for EMO_0xbot
    profile = PersonaProfile(
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
        response_mode="llm_only"
    )
    
    print(f"Created profile: {profile.agent_name}")
    print(f"Voice style: {profile.voice_style}")
    print(f"Goals: {profile.goals}")
    
    # Create a persona engine
    engine = PersonaEngine(profile)
    
    # Test response generation
    response = engine.generate_response("test_intent", {"test": "data"})
    print(f"Generated response: {response}")
    
    return profile, engine

def test_config():
    """Test configuration management"""
    print("\nTesting configuration...")
    
    # Test getting config values
    response_mode = get_response_mode()
    chatter_frequency = get_chatter_frequency()
    
    print(f"Response mode: {response_mode}")
    print(f"Chatter frequency: {chatter_frequency}")

def main():
    """Run all tests"""
    print("Running persona integration tests...\n")
    
    test_codex_persona()
    test_emo_persona()
    test_config()
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    main()