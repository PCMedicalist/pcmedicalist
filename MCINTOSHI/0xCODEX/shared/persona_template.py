"""
Template for creating persona profiles from SOUL.md files.
This module provides a standardized way to parse SOUL.md files and create PersonaProfile objects.
"""

import os
import re
from typing import List, Dict, Any

try:
    from .persona import PersonaProfile, ResponseMode
except ImportError:
    from persona import PersonaProfile, ResponseMode

def parse_soul_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a SOUL.md file and extract the relevant sections.
    
    Args:
        file_path: Path to the SOUL.md file
        
    Returns:
        Dictionary with extracted sections
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract sections using regex
    sections = {}
    
    # Extract voice style
    voice_match = re.search(r'## Voice Style\s*\|(.*?)\|', content, re.DOTALL)
    if voice_match:
        sections['voice_style'] = voice_match.group(1).strip()
    
    # Extract language patterns
    lang_match = re.search(r'## Language Patterns\s*\|(.*?)\|', content, re.DOTALL)
    if lang_match:
        # Split by bullet points or new lines
        patterns = re.split(r'[\n\r]+[*\-]', lang_match.group(1))
        sections['language_patterns'] = [p.strip() for p in patterns if p.strip()]
    
    # Extract goals
    goals_match = re.search(r'## Goals\s*\|(.*?)\|', content, re.DOTALL)
    if goals_match:
        sections['goals'] = goals_match.group(1).strip()
    
    # Extract boundaries
    boundaries_match = re.search(r'## Boundaries\s*\|(.*?)\|', content, re.DOTALL)
    if boundaries_match:
        # Split by bullet points or new lines
        boundaries = re.split(r'[\n\r]+[*\-]', boundaries_match.group(1))
        sections['boundaries'] = [b.strip() for b in boundaries if b.strip()]
    
    # Extract key directives
    directives_match = re.search(r'## Key Directives\s*\|(.*?)\|', content, re.DOTALL)
    if directives_match:
        # Split by bullet points or new lines
        directives = re.split(r'[\n\r]+[*\-]', directives_match.group(1))
        sections['key_directives'] = [d.strip() for d in directives if d.strip()]
    
    # Extract interaction style
    interaction_match = re.search(r'## Interaction Style\s*\|(.*?)\|', content, re.DOTALL)
    if interaction_match:
        sections['interaction_style'] = interaction_match.group(1).strip()
    
    return sections

def create_persona_profile(agent_dir: str, base_path: str = "D:\\web3Dev\\Twitch\\0xCODEX") -> PersonaProfile:
    """
    Create a PersonaProfile from an agent's SOUL.md file.
    
    Args:
        agent_dir: Name of the agent directory (e.g., "0xCODEXbot")
        base_path: Base path to the project directory
        
    Returns:
        PersonaProfile object
    """
    soul_file = os.path.join(base_path, agent_dir, f"0x{agent_dir.split('_')[0]}_SOUL.md")
    
    if not os.path.exists(soul_file):
        # Return a default profile if SOUL file doesn't exist
        return PersonaProfile(
            agent_name=agent_dir,
            voice_style="Neutral",
            language_patterns=["Standard communication patterns"],
            goals="General assistance",
            boundaries=["Follow ethical guidelines"],
            key_directives=["Be helpful", "Be harmless", "Be honest"],
            interaction_style="Helpful and informative"
        )
    
    # Parse the SOUL file
    sections = parse_soul_file(soul_file)
    
    # Determine response mode based on agent type
    response_mode = ResponseMode.HYBRID
    if agent_dir == "EMO_0xbot":
        response_mode = ResponseMode.LLM_ONLY
    elif agent_dir == "OG_0xbot":
        response_mode = ResponseMode.TEMPLATE_FIRST
    
    return PersonaProfile(
        agent_name=agent_dir,
        voice_style=sections.get('voice_style', 'Neutral'),
        language_patterns=sections.get('language_patterns', []),
        goals=sections.get('goals', ''),
        boundaries=sections.get('boundaries', []),
        key_directives=sections.get('key_directives', []),
        interaction_style=sections.get('interaction_style', ''),
        response_mode=response_mode
    )

# Example usage:
# profile = create_persona_profile("0xCODEXbot")
# print(profile)