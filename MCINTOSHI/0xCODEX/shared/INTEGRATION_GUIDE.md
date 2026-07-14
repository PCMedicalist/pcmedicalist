# 0xCODEX Shared Modules Integration Guide

This guide explains how to integrate the shared modules into the 0xCODEX bot agents to provide consistent personality-driven responses and inter-agent communication.

## Overview

The shared modules provide two main features:

1. **Persona Engine**: Generates SOUL-aligned responses for each agent based on their personality profile
2. **Inter-Agent Communication**: Enables agents to send and receive messages to/from other agents

## Integration Steps

### 1. Update Docker Compose Configuration

The shared modules are automatically mounted as a volume in the docker-compose.yml file:

```yaml
volumes:
  - ./shared:/app/shared
```

This makes the shared modules available to all bot agents.

### 2. Update Requirements

Add the following to each bot's requirements.txt file:

```txt
PyYAML==6.0
```

### 3. Import Shared Modules

In your bot's main.py file, add the following imports:

```python
import sys
import os

# Add the shared directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.persona import PersonaProfile, PersonaEngine
from shared.inter_agent import InterAgentMessage, InterAgentCommunicator, MessageType, RiskLevel
from shared.config import config, get_response_mode, get_chatter_frequency
```

### 4. Create Persona Profiles

Create a persona profile for your agent based on its SOUL.md file:

```python
# Create a persona profile for your agent
persona_profile = PersonaProfile(
    agent_name="YOUR_BOT_NAME",
    voice_style="Description of the agent's voice style",
    language_patterns=["Pattern 1", "Pattern 2"],
    goals="Agent's goals",
    boundaries=["Boundary 1", "Boundary 2"],
    key_directives=["Directive 1", "Directive 2"],
    interaction_style="Description of interaction style"
)

# Create a persona engine
persona_engine = PersonaEngine(persona_profile)
```

### 5. Generate Persona-Aligned Responses

Use the persona engine to generate responses:

```python
# Generate a persona-aligned response
intent = "command_name"
context_data = {
    "user_id": update.effective_user.id,
    "timestamp": str(update.message.date)
}

response = persona_engine.generate_response(intent, context_data)

# Send the response
await update.message.reply_text(response)
```

### 6. Set Up Inter-Agent Communication

Create an inter-agent communicator for your agent:

```python
# Create an inter-agent communicator (requires a Redis client)
inter_agent_communicator = InterAgentCommunicator("YOUR_BOT_NAME", redis_client)
```

### 7. Send Inter-Agent Messages

Send messages to other agents:

```python
# Create a message
message = InterAgentMessage(
    source_agent="YOUR_BOT_NAME",
    target_agent="TARGET_BOT_NAME",  # or "ALL" for broadcast
    message_type=MessageType.CHATTER,
    intent="message_intent",
    payload={"key": "value"},
    timestamp=datetime.now().isoformat(),
    trace_id="unique-trace-id"
)

# Send the message
inter_agent_communicator.send_message(message)
```

### 8. Receive Inter-Agent Messages

Receive messages from other agents:

```python
# Receive pending messages
messages = inter_agent_communicator.receive_messages()

# Process each message
for message in messages:
    print(f"Received message from {message.source_agent}: {message.payload}")
    # Process the message based on its type and intent
```

### 9. Listen for Inter-Agent Messages

Listen for incoming messages in real-time:

```python
# Define a callback function to process incoming messages
def message_callback(message):
    print(f"Received message: {message}")
    # Process the message

# Listen for messages
inter_agent_communicator.listen_for_messages(message_callback)
```

## Configuration

The shared modules can be configured using environment variables:

- `PERSONA_RESPONSE_MODE`: Response mode (template_first, llm_only, hybrid)
- `CHATTER_FREQUENCY`: Chatter frequency (rare, moderate, frequent)
- `INTER_AGENT_ENABLED`: Enable/disable inter-agent communication
- `GUARDRAILS_ENABLED`: Enable/disable persona guardrails
- `OBSERVABILITY_ENABLED`: Enable/disable observability features

### Public Telegram Broadcast For Agent Conversations

Inter-agent messages are mirrored publicly to Telegram when `InterAgentCommunicator.send_message(...)` is used.

- `TELEGRAM_PUBLIC_BROADCAST_TARGETS`: Comma-separated chat targets.
    Example: `@baseline0x,-1001234567890`
- `TELEGRAM_PUBLIC_GROUP_CHAT_ID`: Group chat ID (for the 0xCODEX group).
- `TELEGRAM_PUBLIC_CHANNEL`: Channel username or ID (defaults to `@baseline0x`).

Recommended setup:

```env
TELEGRAM_PUBLIC_CHANNEL=@baseline0x
TELEGRAM_PUBLIC_GROUP_CHAT_ID=-1001234567890
TELEGRAM_PUBLIC_BROADCAST_TARGETS=@baseline0x,-1001234567890
```

Notes:

- Private invite links like `https://t.me/+...` are not chat IDs. Use the numeric group chat ID.
- Since all agents are admins, each bot can post as itself with its own token.

## Example Integration

See the following files for complete examples:

- `0xCODEXbot/persona_integration.py`: Example of integrating the persona engine into 0xCODEXbot
- `EMO_0xbot/persona_integration.py`: Example of integrating the persona engine into EMO_0xbot
- `0xCODEXbot/inter_agent_example.py`: Example of inter-agent communication

## Testing

To test the integration:

1. Run the persona integration tests:
   ```bash
   cd shared && python test_persona_integration.py
   ```

2. Run the import tests:
   ```bash
   cd shared && python test_import.py
   ```

3. Run the inter-agent example:
   ```bash
   cd 0xCODEXbot && python inter_agent_example.py
   ```

## Best Practices

1. **Persona Consistency**: Ensure that the persona profile accurately reflects the agent's SOUL.md file
2. **Error Handling**: Always handle exceptions when calling the shared modules
3. **Configuration**: Use environment variables to configure the shared modules
4. **Logging**: Log important events and errors for debugging
5. **Security**: Validate all inputs and outputs to prevent injection attacks
6. **Performance**: Cache persona profiles and engines where possible to reduce overhead

## Troubleshooting

### ImportError: No module named 'shared'

Make sure you've added the shared directory to the Python path:

```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
```

### ValueError: 'LOW' is not a valid RiskLevel

Make sure you're using the lowercase string values for enums:

```python
"risk_level": "low"  # Correct
"risk_level": "LOW"  # Incorrect
```

### ModuleNotFoundError: No module named 'yaml'

Install the PyYAML package:

```bash
pip install PyYAML
```