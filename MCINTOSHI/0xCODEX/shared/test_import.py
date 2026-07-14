"""
Simple test script to verify that the shared modules can be imported correctly.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    # Test importing the shared modules
    from shared import (
        PersonaProfile, 
        PersonaEngine, 
        InterAgentMessage, 
        InterAgentCommunicator, 
        MessageType, 
        RiskLevel,
        config,
        get_response_mode,
        create_persona_profile
    )
    
    print("All shared modules imported successfully!")
    
    # Test creating a simple persona profile
    profile = PersonaProfile(
        agent_name="TEST_0xbot",
        voice_style="Testy McTestface",
        language_patterns=["testing", "verification"],
        goals="Test all the things",
        boundaries=["Don't break stuff", "Be nice"],
        key_directives=["Verify functionality", "Report issues"],
        interaction_style="Test-oriented"
    )
    
    print(f"Created test profile: {profile.agent_name}")
    
    # Test getting a config value
    response_mode = get_response_mode()
    print(f"Response mode: {response_mode}")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")