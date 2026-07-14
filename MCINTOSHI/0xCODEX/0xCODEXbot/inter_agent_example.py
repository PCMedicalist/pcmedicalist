"""
Example of integrating the shared inter-agent communication system into the 0xCODEXbot.
This file demonstrates how to send and receive messages between agents.
"""

import os
import sys
import json
import asyncio
from datetime import datetime

# Add the shared directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.inter_agent import InterAgentMessage, InterAgentCommunicator, MessageType, RiskLevel
from shared.config import config, is_inter_agent_comm_enabled

# Example of sending an inter-agent message
def send_status_update():
    """Example of sending a status update message to all agents"""
    # In a real implementation, you would use a real Redis client
    # For this example, we'll just create the message without sending it
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
        timestamp=datetime.now().isoformat(),
        trace_id="status-update-001",
        risk_level=RiskLevel.LOW,
        requires_approval=False,
        confidence=0.95
    )
    
    print(f"Created message: {message}")
    print(f"Message dict: {message.to_dict()}")
    
    # In a real implementation, you would send the message like this:
    # communicator.send_message(message)
    
    return message

# Example of receiving inter-agent messages
def receive_messages():
    """Example of receiving messages (this would be called periodically)"""
    # In a real implementation, you would use a real Redis client
    # For this example, we'll just show how it would work
    
    # Create a mock message that might be received
    message_data = {
        "source_agent": "EMO_0xbot",
        "target_agent": "ALL",
        "message_type": "chatter",
        "intent": "community_reaction",
        "payload": {
            "reaction": "🎉",
            "message": "Community milestone reached!",
            "sentiment": "positive"
        },
        "timestamp": datetime.now().isoformat(),
        "trace_id": "reaction-001",
        "risk_level": "low",
        "requires_approval": False,
        "confidence": 0.9
    }
    
    # Parse the message
    message = InterAgentMessage.from_dict(message_data)
    
    print(f"Received message from {message.source_agent}: {message.payload}")
    
    # Process the message based on its type and intent
    if message.message_type == MessageType.CHATTER:
        if message.intent == "community_reaction":
            print(f"Processing community reaction: {message.payload}")
            # In a real implementation, you might respond to this message
            # or take some action based on the community reaction
    
    return message

# Example of listening for messages
def listen_for_messages():
    """Example of listening for incoming messages"""
    # In a real implementation, you would use a real Redis client
    # For this example, we'll just show how it would work
    
    print("Listening for inter-agent messages...")
    
    # This is how you would set up a listener in a real implementation:
    # def message_callback(message):
    #     print(f"Received message: {message}")
    #     # Process the message
    #     
    # communicator.listen_for_messages(message_callback)
    
    # For now, we'll just simulate receiving a message
    receive_messages()

# Example of generating conversation starters
def generate_conversation_starter(moment_type: str, context: dict):
    """Generate a conversation starter message for a specific moment"""
    from shared.inter_agent import generate_conversation_starter as gen_starter
    
    try:
        message = gen_starter(moment_type, context)
        print(f"Generated conversation starter: {message}")
        return message
    except ValueError as e:
        print(f"Error generating conversation starter: {e}")
        return None

# Example usage
if __name__ == "__main__":
    print("Inter-agent communication example")
    print("==================================")
    
    # Check if inter-agent communication is enabled
    if is_inter_agent_comm_enabled():
        print("Inter-agent communication is enabled")
    else:
        print("Inter-agent communication is disabled")
    
    # Send a status update
    print("\nSending status update...")
    send_status_update()
    
    # Receive messages
    print("\nReceiving messages...")
    receive_messages()
    
    # Listen for messages
    print("\nListening for messages...")
    listen_for_messages()
    
    # Generate conversation starters
    print("\nGenerating conversation starters...")
    
    # New builder event
    generate_conversation_starter("new_builder_event", {
        "builder_name": "Alice",
        "project": "AwesomeContract"
    })
    
    # Deployment update
    generate_conversation_starter("deployment_update", {
        "contract_address": "0x1234...",
        "status": "deployed"
    })
    
    # Detected fault
    generate_conversation_starter("detected_fault", {
        "component": "GEN_0xbot",
        "error": "Deployment failed",
        "severity": "high"
    })