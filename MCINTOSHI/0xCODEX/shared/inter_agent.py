"""
Inter-agent communication system for 0xCODEX bot fleet.
Handles cross-agent messaging using Redis pub/sub and queues.
"""

import json
import os
import uuid
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import redis
from datetime import datetime
from urllib import request, parse

class MessageType(Enum):
    CHATTER = "chatter"
    STATUS_UPDATE = "status_update"
    ALERT = "alert"
    REQUEST = "request"
    RESPONSE = "response"
    HEARTBEAT = "heartbeat"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class InterAgentMessage:
    """Standardized message format for cross-agent communication"""
    source_agent: str
    target_agent: str  # "ALL" for broadcast
    message_type: MessageType
    intent: str
    payload: Dict[str, Any]
    timestamp: str
    trace_id: str
    risk_level: RiskLevel = RiskLevel.LOW
    requires_approval: bool = False
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "message_type": self.message_type.value,
            "intent": self.intent,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "trace_id": self.trace_id,
            "risk_level": self.risk_level.value,
            "requires_approval": self.requires_approval,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InterAgentMessage':
        msg_type = data.get('message_type', MessageType.CHATTER.value)
        risk_level = data.get('risk_level', RiskLevel.LOW.value)
        if isinstance(msg_type, str):
            msg_type = msg_type.lower()
        if isinstance(risk_level, str):
            risk_level = risk_level.lower()
        data['message_type'] = MessageType(msg_type)
        data['risk_level'] = RiskLevel(risk_level)
        return cls(**data)

class InterAgentCommunicator:
    """Handles sending and receiving messages between agents"""
    
    def __init__(self, agent_name: str, redis_client: redis.Redis):
        self.agent_name = agent_name
        self.redis = redis_client
        self.pubsub = redis_client.pubsub()
        
        # Use pattern subscriptions for wildcard channels.
        self.pubsub.psubscribe("agent:broadcast:*")
        self.pubsub.psubscribe("agent:alert:*")
        self.pubsub.psubscribe("agent:health:*")
        self.pubsub.psubscribe(f"agent:{agent_name}:*")
    
    def send_message(self, message: InterAgentMessage):
        """Send a message to another agent or broadcast"""
        message_json = json.dumps(message.to_dict())
        
        if message.target_agent == "ALL":
            # Broadcast to all agents
            self.redis.publish(f"agent:broadcast:{message.intent}", message_json)
        else:
            # Send to specific agent queue
            queue_name = f"agent:{message.target_agent}:messages"
            self.redis.lpush(queue_name, message_json)

        # Mirror agent-to-agent chatter publicly to Telegram group/channel.
        if message.message_type != MessageType.HEARTBEAT:
            try:
                broadcast_inter_agent_message_to_telegram(message)
            except Exception as e:
                print(f"Error broadcasting to Telegram: {e}")
    
    def receive_messages(self) -> List[InterAgentMessage]:
        """Receive pending messages for this agent"""
        messages = []
        queue_name = f"agent:{self.agent_name}:messages"
        
        # Get all messages from queue
        while True:
            message_json = self.redis.rpop(queue_name)
            if not message_json:
                break
                
            try:
                message_data = json.loads(message_json)
                message = InterAgentMessage.from_dict(message_data)
                messages.append(message)
            except Exception as e:
                print(f"Error parsing message: {e}")
        
        return messages
    
    def listen_for_messages(self, callback):
        """Listen for incoming messages and process with callback"""
        for item in self.pubsub.listen():
            if item['type'] in ('message', 'pmessage'):
                try:
                    raw = item['data']
                    if isinstance(raw, bytes):
                        raw = raw.decode('utf-8')
                    message_data = json.loads(raw)
                    message = InterAgentMessage.from_dict(message_data)
                    callback(message)
                except Exception as e:
                    print(f"Error processing message: {e}")

# Predefined conversation moments
CONVERSATION_MOMENTS = {
    "new_builder_event": {
        "initiators": ["L1NE_0xbot"],
        "participants": ["OG_0xbot", "EMO_0xbot", "GEN_0xbot"],
        "frequency": "high"
    },
    "deployment_update": {
        "initiators": ["GEN_0xbot"],
        "participants": ["OG_0xbot", "EMO_0xbot", "0xCODEXbot"],
        "frequency": "medium"
    },
    "detected_fault": {
        "initiators": ["ERR_0xbot"],
        "participants": ["0xCODEXbot", "ROOT_0xbot", "VOID_0xbot"],
        "frequency": "high"
    },
    "trend_shift": {
        "initiators": ["PRIME_0xbot"],
        "participants": ["OG_0xbot", "EMO_0xbot", "NEXUS_0xbot"],
        "frequency": "medium"
    },
    "silent_gap": {
        "initiators": ["VOID_0xbot"],
        "participants": ["ERR_0xbot", "0xCODEXbot"],
        "frequency": "low"
    },
    "identity_change": {
        "initiators": ["ROOT_0xbot"],
        "participants": ["OG_0xbot", "0xCODEXbot"],
        "frequency": "medium"
    },
    "community_milestone": {
        "initiators": ["OG_0xbot"],
        "participants": ["EMO_0xbot", "0xCODEXbot"],
        "frequency": "high"
    }
}

def generate_conversation_starter(moment_type: str, context: Dict[str, Any]) -> InterAgentMessage:
    """Generate a conversation starter message for a specific moment"""
    if moment_type not in CONVERSATION_MOMENTS:
        raise ValueError(f"Unknown conversation moment: {moment_type}")
    
    moment = CONVERSATION_MOMENTS[moment_type]
    initiator = moment["initiators"][0]  # Simplified for now
    
    return InterAgentMessage(
        source_agent=initiator,
        target_agent="ALL",
        message_type=MessageType.CHATTER,
        intent=moment_type,
        payload=context,
        timestamp=datetime.now().isoformat(),
        trace_id=str(uuid.uuid4()),
        risk_level=RiskLevel.LOW,
        requires_approval=False,
        confidence=0.8
    )


def broadcast_inter_agent_message_to_telegram(message: InterAgentMessage) -> None:
    """Broadcast an inter-agent message to configured public Telegram targets.

    Targets are read from:
    - TELEGRAM_PUBLIC_BROADCAST_TARGETS (comma-separated chat IDs/usernames; explicit override)
    - TELEGRAM_PUBLIC_GROUP_CHAT_ID (single group id/username; preferred default)
    - TELEGRAM_PUBLIC_CHANNEL (single channel username or id; fallback only)
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
    if not bot_token:
        return

    targets = _resolve_public_targets()
    if not targets:
        return

    # Prefer rich HTML rollcall content when present
    payload = message.payload if isinstance(message.payload, dict) else {}
    if payload.get("rollcall_html"):
        text = payload.get("rollcall_html")
        parse_mode = "HTML"
    else:
        text = _format_public_message(message)
        parse_mode = "HTML"

    for target in targets:
        _send_telegram_text(bot_token, target, text, parse_mode=parse_mode)


def _resolve_public_targets() -> List[str]:
    raw_targets = os.getenv("TELEGRAM_PUBLIC_BROADCAST_TARGETS", "")
    targets: List[str] = []
    if raw_targets.strip():
        targets.extend([t.strip() for t in raw_targets.split(",") if t.strip()])
    else:
        # Default to group destination to avoid channel->group duplication.
        group_id = os.getenv("TELEGRAM_PUBLIC_GROUP_CHAT_ID", "").strip()
        if group_id:
            targets.append(group_id)
        else:
            channel = os.getenv("TELEGRAM_PUBLIC_CHANNEL", "").strip()
            if channel:
                targets.append(channel)

    # Deduplicate while preserving order
    deduped: List[str] = []
    for t in targets:
        if t not in deduped:
            deduped.append(t)
    return deduped


def _format_public_message(message: InterAgentMessage) -> str:
    payload_message = message.payload.get("message") if isinstance(message.payload, dict) else None
    payload_text = str(payload_message or "signal update")
    approval_text = "yes" if message.requires_approval else "no"
    # Escape minimal HTML characters to keep text safe
    payload_text = _escape_html(payload_text)
    return (
        f"[{_escape_html(message.source_agent)} -> {_escape_html(message.target_agent)}] {_escape_html(message.intent)}\n"
        f"type: {_escape_html(message.message_type.value)} | risk: {_escape_html(message.risk_level.value)} | approval: {approval_text}\n"
        f"{payload_text}"
    )


def _send_telegram_text(bot_token: str, chat_id: str, text: str, parse_mode: str = "HTML") -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    body = parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": "true",
            "disable_notification": "true",
        }
    ).encode("utf-8")

    req = request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with request.urlopen(req, timeout=8) as resp:
        if resp.status < 200 or resp.status >= 300:
            raise RuntimeError(f"Telegram send failed with status {resp.status}")


def _escape_html(s: str) -> str:
    # Minimal escaping for HTML parse mode
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )