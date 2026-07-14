"""
Example of parsing SOUL.md files and creating persona profiles automatically.
This script demonstrates how to use the persona_template module to create persona profiles.
"""

import os
import sys

# Add the shared directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from persona_template import create_persona_profile, parse_soul_file

def parse_all_souls(base_path: str = ".."):
    """Parse all SOUL.md files and create persona profiles"""
    print("Parsing all SOUL.md files...")
    
    # List of agent directories
    agent_dirs = [
        "0xCODEXbot", "EMO_0xbot", "ERR_0xbot", "GEN_0xbot", 
        "L1NE_0xbot", "NEXUS_0xbot", "NULL_0xbot", "OG_0xbot",
        "PRIME_0xbot", "ROOT_0xbot", "VOID_0xbot"
    ]
    
    profiles = {}
    
    for agent_dir in agent_dirs:
        print(f"\nParsing {agent_dir}...")
        try:
            # Create a persona profile from the SOUL.md file
            profile = create_persona_profile(agent_dir, base_path)
            profiles[agent_dir] = profile
            
            print(f"  Agent Name: {profile.agent_name}")
            print(f"  Voice Style: {profile.voice_style}")
            print(f"  Goals: {profile.goals}")
            print(f"  Response Mode: {profile.response_mode.value}")
            
            # Show a few boundaries and directives
            if profile.boundaries:
                print(f"  Boundaries: {profile.boundaries[:2]}...")
            if profile.key_directives:
                print(f"  Key Directives: {profile.key_directives[:2]}...")
                
        except Exception as e:
            print(f"  Error parsing {agent_dir}: {e}")
    
    return profiles

def parse_single_soul(agent_dir: str, base_path: str = ".."):
    """Parse a single SOUL.md file and create a persona profile"""
    print(f"Parsing {agent_dir}...")
    
    try:
        # Parse the SOUL file directly
        soul_file = os.path.join(base_path, agent_dir, f"0x{agent_dir.split('_')[0]}_SOUL.md")
        if os.path.exists(soul_file):
            print(f"  Parsing {soul_file}")
            sections = parse_soul_file(soul_file)
            
            print("  Parsed sections:")
            for key, value in sections.items():
                if isinstance(value, list):
                    print(f"    {key}: {value[:3]}...")  # Show first 3 items
                else:
                    print(f"    {key}: {value[:100]}...")  # Show first 100 characters
        else:
            print(f"  SOUL file not found: {soul_file}")
            
        # Create a persona profile
        profile = create_persona_profile(agent_dir, base_path)
        
        print(f"  Created profile: {profile.agent_name}")
        print(f"  Voice Style: {profile.voice_style}")
        print(f"  Goals: {profile.goals}")
        print(f"  Response Mode: {profile.response_mode.value}")
        
        return profile
        
    except Exception as e:
        print(f"  Error parsing {agent_dir}: {e}")
        return None

def main():
    """Main function"""
    print("SOUL.md Parser Example")
    print("======================")
    
    # Parse all SOUL files
    profiles = parse_all_souls()
    
    print(f"\nParsed {len(profiles)} SOUL files")
    
    # Parse a single SOUL file as an example
    print("\n\nParsing single SOUL file...")
    parse_single_soul("0xCODEXbot")

if __name__ == "__main__":
    main()