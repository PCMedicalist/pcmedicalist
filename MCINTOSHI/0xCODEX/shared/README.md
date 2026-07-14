# 0xCODEX Shared Modules

This directory contains shared modules used across all 0xCODEX bot agents to provide consistent personality-driven responses and inter-agent communication.

## Modules

### persona.py
Provides the personality engine for generating SOUL-aligned responses:
- Template-based response generation
- LLM-based response generation with persona constraints
- Hybrid approach combining both methods
- Persona profile management

### inter_agent.py
Handles communication between agents:
- Standardized message format for cross-agent communication
- Redis-based pub/sub and queue mechanisms
- Predefined conversation moments
- Risk assessment and approval workflows

### config.py
Centralized configuration management:
- Environment variable overrides
- Default configuration values
- Nested configuration access

### persona_template.py
Utilities for creating persona profiles from SOUL.md files:
- SOUL.md file parsing
- Standardized persona profile creation
- Agent-specific response mode determination

## Installation

To use these shared modules, ensure the following dependencies are installed:

```bash
pip install -r requirements.txt
```

## Usage

### Persona Engine

```python
from shared.persona import PersonaProfile, PersonaEngine

# Create a persona profile
profile = PersonaProfile(
    agent_name="TEST_0xbot",
    voice_style="Testy McTestface",
    # ... other attributes
)

# Create a persona engine
engine = PersonaEngine(profile)

# Generate a response
response = engine.generate_response("test_intent", {"test": "data"})
```

### Inter-Agent Communication

```python
from shared.inter_agent import InterAgentMessage, InterAgentCommunicator, MessageType, RiskLevel
import redis

# Create a Redis client
redis_client = redis.Redis.from_url("redis://localhost:6379")

# Create an inter-agent communicator
communicator = InterAgentCommunicator("TEST_0xbot", redis_client)

# Create a message
message = InterAgentMessage(
    source_agent="TEST_0xbot",
    target_agent="ALL",
    message_type=MessageType.CHATTER,
    intent="test_conversation",
    payload={"test": "data"},
    timestamp="2026-03-23T12:00:00Z",
    trace_id="test-trace-id"
)

# Send the message
communicator.send_message(message)
```

### Configuration

```python
from shared.config import config, get_response_mode

# Get configuration values
response_mode = get_response_mode()
llm_provider = config.get("RESPONSE_ENGINE.LLM_PROVIDER")
```

## Testing

To run the tests:

```bash
python test_shared.py
```

## Integration with Docker

The shared modules are mounted as a volume in the docker-compose.yml file, making them available to all bot agents:

```yaml
volumes:
  - ./shared:/app/shared
```

Each bot agent can then import and use the shared modules:

```python
import sys
sys.path.insert(0, '/app/shared')

from persona import PersonaEngine
from inter_agent import InterAgentCommunicator
```