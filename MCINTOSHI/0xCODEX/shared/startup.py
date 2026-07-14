"""
Startup roll call announcements for 0xCODEX bot fleet.
Each agent announces itself on initialization to confirm it's online.
"""

import os
import html
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .inter_agent import InterAgentMessage, MessageType, RiskLevel

from typing import Dict, Any

if TYPE_CHECKING:
    from .inter_agent import InterAgentCommunicator
    from .persona import PersonaProfile


def announce_startup_rollcall(
    inter_agent: "InterAgentCommunicator",
    persona_profile: "PersonaProfile",
    agent_name: str
) -> None:
    """
    Broadcast an agent's startup announcement to confirm it's online.
    Includes: name, purpose, personality, and use case.
    
    Args:
        inter_agent: InterAgentCommunicator instance
        persona_profile: Agent's PersonaProfile with voice/goals/etc
        agent_name: Human-readable agent name (e.g., "0xCODEX")
    """
    
    # Compose structured payload honoring optional per-agent overrides
    now = datetime.now(timezone.utc)

    # Base fields
    agent_id = persona_profile.agent_name
    display_name = persona_profile.rollcall_overrides.get("display_name") if getattr(persona_profile, "rollcall_overrides", None) else agent_name
    role = persona_profile.rollcall_overrides.get("role") if getattr(persona_profile, "rollcall_overrides", None) else persona_profile.goals
    primary_commands = persona_profile.rollcall_overrides.get("primary_commands") if getattr(persona_profile, "rollcall_overrides", None) else []
    public_targets = persona_profile.rollcall_overrides.get("public_targets") if getattr(persona_profile, "rollcall_overrides", None) else [os.getenv("TELEGRAM_PUBLIC_GROUP_CHAT_ID", "@baseline0xcodex")]
    contact = persona_profile.rollcall_overrides.get("contact") if getattr(persona_profile, "rollcall_overrides", None) else os.getenv("ROLLCALL_CONTACT", "@maintainers")
    extra_notes = persona_profile.rollcall_overrides.get("extra_notes") if getattr(persona_profile, "rollcall_overrides", None) else None

    # Health checks (best-effort)
    health: Dict[str, Any] = {"redis": "unknown", "telegram": "unknown"}
    try:
        if hasattr(inter_agent, "redis") and inter_agent.redis:
            try:
                inter_agent.redis.ping()
                health["redis"] = "ok"
            except Exception:
                health["redis"] = "err"
    except Exception:
        health["redis"] = "unknown"

    # Version/commit info
    version = os.getenv("RELEASE_VERSION") or os.getenv("GIT_COMMIT") or "unknown"

    # Build human-friendly plain and HTML versions
    primary_commands_str = ", ".join(primary_commands) if primary_commands else "(none listed)"
    start_time_iso = now.isoformat()

    # Escape HTML for safe Telegram HTML parse mode
    def esc(s: str) -> str:
        return html.escape(str(s))

    html_lines = []
    html_lines.append(f"<b>🚀 {esc(display_name)} ROLLCALL — CONFIRMING LIFE</b>")
    html_lines.append(f"<b>Agent ID:</b> {esc(agent_id)}")
    html_lines.append(f"<b>Role:</b> {esc(role)}")
    html_lines.append(f"<b>Purpose:</b> {esc(persona_profile.goals)}")
    html_lines.append(f"<b>Personality:</b> {esc(persona_profile.voice_style)}")
    html_lines.append(f"<b>Primary Commands:</b> {esc(primary_commands_str)}")
    html_lines.append(f"<b>Public Targets:</b> {esc(', '.join(public_targets))}")
    html_lines.append(f"<b>Start Time:</b> {esc(start_time_iso)}")
    html_lines.append(f"<b>Version:</b> {esc(version)}")
    html_lines.append(f"<b>Health:</b> Redis={esc(health.get('redis'))} | Telegram={esc(health.get('telegram'))}")
    if contact:
        html_lines.append(f"<b>Contact:</b> {esc(contact)}")
    if extra_notes:
        html_lines.append(f"<i>{esc(extra_notes)}</i>")

    rollcall_html = "\n".join(html_lines)

    # Plain text fallback for console printing
    plain_lines = []
    for l in html_lines:
        stripped = (
            l.replace("<b>", "")
            .replace("</b>", "")
            .replace("<i>", "")
            .replace("</i>", "")
        )
        plain_lines.append(html.unescape(stripped))
    plain_text = "\n".join(plain_lines)

    structured_payload = {
        "agent_id": agent_id,
        "display_name": display_name,
        "role": role,
        "purpose": persona_profile.goals,
        "personality": persona_profile.voice_style,
        "primary_commands": primary_commands,
        "public_targets": public_targets,
        "start_time_iso": start_time_iso,
        "version": version,
        "health": health,
        "contact": contact,
        "extra_notes": extra_notes,
        "rollcall_type": "startup",
    }

    message = InterAgentMessage(
        source_agent=persona_profile.agent_name,
        target_agent="ALL",
        message_type=MessageType.STATUS_UPDATE,
        intent="startup_rollcall",
        payload={
            "rollcall_text": plain_text,
            "rollcall_html": rollcall_html,
            **structured_payload,
        },
        timestamp=now.isoformat(),
        trace_id=f"startup-{persona_profile.agent_name}-{now.timestamp()}",
        risk_level=RiskLevel.LOW,
        requires_approval=False,
        confidence=1.0,
    )

    inter_agent.send_message(message)
    print(f"\n{plain_text}")
