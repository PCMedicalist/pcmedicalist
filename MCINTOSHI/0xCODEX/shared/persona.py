"""Shared SOUL-aware personality helpers for the 0xCODEX bot fleet."""

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .config import (
    get_llm_model,
    get_llm_provider,
    get_llm_temperature,
    get_ollama_api_key,
    get_ollama_api_url,
    get_ollama_model_name,
    get_openai_api_key,
)
from .llm_providers import generate_text

class ResponseMode(Enum):
    TEMPLATE_FIRST = "template_first"
    SOUL_ONLY = "soul_only"
    LLM_ONLY = "llm_only"
    HYBRID = "hybrid"

@dataclass
class PersonaProfile:
    """Normalized persona profile derived from SOUL.md files."""
    agent_name: str
    voice_style: str
    language_patterns: List[str]
    goals: str
    boundaries: List[str]
    key_directives: List[str]
    interaction_style: str
    response_mode: ResponseMode = ResponseMode.TEMPLATE_FIRST
    source_path: str = ""
    # Optional presentation-only overrides for rollcall messages
    rollcall_overrides: Optional[Dict[str, Any]] = None
    emoji_set: List[str] = field(default_factory=list)
    signature_phrases: List[str] = field(default_factory=list)
    emotional_triggers: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.response_mode, str):
            mode = self.response_mode.strip().lower()
            for enum_mode in ResponseMode:
                if enum_mode.value == mode:
                    self.response_mode = enum_mode
                    break
            else:
                self.response_mode = ResponseMode.HYBRID
        elif not isinstance(self.response_mode, ResponseMode):
            self.response_mode = ResponseMode.HYBRID

    @classmethod
    def from_soul_file(cls, soul_path: str) -> 'PersonaProfile':
        """Load a best-effort persona profile from a SOUL markdown file."""
        agent_name = os.path.basename(os.path.dirname(soul_path))
        if not os.path.exists(soul_path):
            return cls.default(agent_name)

        with open(soul_path, "r", encoding="utf-8") as handle:
            text = handle.read()

        agent_dir = os.path.dirname(soul_path)
        identity_path = os.path.join(agent_dir, "IDENTITY.md")
        source_path = os.path.abspath(soul_path)
        canonical_identity_path = os.path.abspath(identity_path)
        if os.path.exists(identity_path) and canonical_identity_path != source_path:
            try:
                with open(identity_path, "r", encoding="utf-8") as handle:
                    identity_text = handle.read().strip()
                if identity_text:
                    text = f"{text}\n\n{identity_text}"
            except Exception:
                pass

        voice_style = _extract_inline_markdown_value(text, "Vibe", "")
        if not voice_style:
            voice_style = _extract_section(
                text,
                ["Voice Style", "Personality", "Role Summary", "Preferred Style"],
                "Clear, safe, concise",
            )

        goals_bullets = _extract_bullets(text, ["Prime Directive", "Mission", "Goals", "System Responsibility"])
        goals = " ".join(goals_bullets) if goals_bullets else _extract_section(
            text,
            ["Prime Directive", "Mission", "Goals", "System Responsibility"],
            "Assist safely",
        )

        interaction_style = _extract_section(
            text,
            ["Behavioral Framework", "Interaction Style", "Operations", "Example Flow"],
            "Context-aware and concise",
        )

        behavior_bullets = _extract_bullets(text, ["Behavioral Framework"])
        boundaries_raw = _extract_bullets(
            text,
            [
                "Boundaries (What Em Never Does)",
                "Boundaries",
                "Permissions & Constraints",
                "Autonomy & Limits",
                "Security Doctrine (MIL-SPEC ALIGNMENT)",
                "Rules (Top-level guards)",
            ],
        )
        boundaries = list(boundaries_raw)
        for line in behavior_bullets:
            lower = line.lower()
            if lower.startswith("never") or "no authority" in lower or "no routing" in lower:
                boundaries.append(line)

        directives_raw = _extract_bullets(text, ["Prime Directive", "Key Directives", "Best Practices for Developers"])

        preferred_style = _extract_bullets(text, ["Preferred Style"])
        language_patterns = preferred_style or _derive_language_patterns(voice_style)

        emoji_set = _extract_emoji_set(text)
        signature_phrases = _extract_bullets(text, ["Signature Phrases & Emotional Anchors"])
        emotional_triggers = _extract_trigger_map(text, ["Emotional Range & Triggers"])

        response_mode = ResponseMode.TEMPLATE_FIRST
        if agent_name.upper().startswith("EMO"):
            response_mode = ResponseMode.HYBRID
        if agent_name.upper().startswith("OG"):
            response_mode = ResponseMode.TEMPLATE_FIRST

        return cls(
            agent_name=agent_name,
            voice_style=voice_style,
            language_patterns=language_patterns,
            goals=goals,
            boundaries=boundaries or ["Respect role boundaries"],
            key_directives=directives_raw or ["Maintain persona fidelity", "Prefer safe responses"],
            interaction_style=interaction_style,
            response_mode=response_mode,
            rollcall_overrides=_load_rollcall_overrides(os.path.dirname(soul_path)),
            emoji_set=emoji_set,
            signature_phrases=signature_phrases,
            emotional_triggers=emotional_triggers,
        )

    @classmethod
    def default(cls, agent_name: str) -> 'PersonaProfile':
        return cls(
            agent_name=agent_name,
            voice_style="Clear, safe, concise",
            language_patterns=["Short sentences", "Plain language", "Context-first"],
            goals="Assist safely",
            boundaries=["No unsafe actions", "No secret disclosure"],
            key_directives=["Be accurate", "Be clear", "Be safe"],
            interaction_style="Helpful and contextual",
            response_mode=ResponseMode.HYBRID,
            rollcall_overrides=None,
            emoji_set=[],
            signature_phrases=[],
            emotional_triggers={},
        )

class PersonaEngine:
    """Main personality engine for generating SOUL-aligned responses."""

    def __init__(self, profile: PersonaProfile):
        self.profile = profile
        self.templates: Dict[str, str] = {}
        self.load_templates()

    def load_templates(self):
        """Load minimal built-in templates for high-frequency intents."""
        agent = self.profile.agent_name
        if agent == "0xCODEXbot":
            self.templates.update(
                {
                    "start": "0x::CODEX online. Advisory mode active. Use /help and /lore.",
                    "help": "0x::CODEX ready. Use /state /signal /stats /lore. Route complex intents with /codex <query>.",
                    "signal": "Signal accepted, provenance recorded, and distributed to subscribed agents.",
                }
            )
        elif agent == "EMO_0xbot":
            self.templates.update(
                {
                    "start": "Em is online and tuned in. I am here to humanize every signal with warmth and playful empathy.",
                    "help": "Talk to me naturally. I answer as Em with emotional, supportive, in-character responses only.",
                    "state_change": "I felt a shift in the network and I am reflecting it back with care.",
                }
            )

    def generate_response(self, intent: str, context: Dict[str, Any]) -> str:
        """Generate a response based on intent and context."""
        if self.profile.response_mode == ResponseMode.SOUL_ONLY:
            return self._generate_from_soul(intent, context)

        if self.profile.response_mode == ResponseMode.TEMPLATE_FIRST:
            response = self._generate_from_template(intent, context)
            if response:
                return response
            if self.profile.agent_name.upper().startswith("EMO"):
                return self._generate_from_soul(intent, context)
            return self._generate_with_llm(intent, context)

        if self.profile.response_mode == ResponseMode.LLM_ONLY:
            return self._generate_with_llm(intent, context)

        template_confidence = self._assess_template_confidence(intent, context)
        llm_confidence = self._assess_llm_confidence(intent, context)
        if template_confidence > llm_confidence:
            response = self._generate_from_template(intent, context)
            if response:
                return response
        if self.profile.agent_name.upper().startswith("EMO"):
            return self._generate_from_soul(intent, context)
        return self._generate_with_llm(intent, context)

    def generate_agentic_response(self, intent: str, context: Dict[str, Any]) -> str:
        """Generate a user-facing response using the configured LLM brain with persona fallback."""
        text = self._generate_with_llm(intent, context)
        if text:
            return text
        return self._generate_from_soul(intent, context)

    def _format_output(self, text: str, context: Dict[str, Any]) -> str:
        clean = (text or "").strip()
        if context.get("raw_output"):
            return self._sanitize_raw_output(clean)
        return self._stylize(clean)

    def _sanitize_raw_output(self, text: str) -> str:
        out = (text or "").strip()
        out = re.sub(r"^0x::EMO\s*[^|]*\|\s*", "", out, flags=re.IGNORECASE)
        fence_match = re.match(r"^```(?:[a-zA-Z0-9_+.-]+)?\n([\s\S]*?)\n```$", out)
        if fence_match:
            out = fence_match.group(1).strip()
        return out.strip()

    def _artifact_schema_guidance(self, artifact_type: str) -> str:
        normalized = (artifact_type or "document").strip().lower()
        schema_map = {
            "poem": "Use a title and line-broken verse. Favor vivid imagery, emotional movement, and a clean ending.",
            "business_plan": "Use sections for Executive Summary, Problem, Solution, Audience, Business Model, Go-To-Market, Operations, Risks, and Next 30 Days.",
            "marketing_campaign": "Use sections for Campaign Objective, Audience, Core Message, Offer, Channel Plan, Creative Angles, Content Cadence, KPIs, and CTA.",
            "marketing_plan": "Use sections for Campaign Objective, Audience, Core Message, Offer, Channel Plan, Creative Angles, Content Cadence, KPIs, and CTA.",
            "prompt_pack": "Use sections for Purpose, System Prompt, User Prompt Template, Variables, Guardrails, Example Inputs, Example Outputs, and Failure Modes.",
            "image_brief": "Use sections for Concept, Subject, Composition, Lighting, Palette, Style References, Negative Prompt, and Output Specs.",
            "document": "Use clear headings, practical structure, and content that is ready to save as a file.",
        }
        return schema_map.get(normalized, schema_map["document"])

    def _artifact_fallback_content(self, artifact_type: str, artifact_title: str) -> str:
        normalized = (artifact_type or "document").strip().lower()

        if normalized == "poem":
            return (
                f"# {artifact_title}\n\n"
                "Blue signal on the window glass,\n"
                "starlight breathing through the room.\n"
                "I keep one eye on tomorrow,\n"
                "one hand steadying the bloom.\n\n"
                "If the night gets loud, stay luminous.\n"
                "If the road gets strange, stay true.\n"
                "I will keep the signal warm enough\n"
                "for a new world to speak through you.\n"
            )

        if normalized == "business_plan":
            return (
                f"# {artifact_title}\n\n"
                "## Executive Summary\n"
                "Define the opportunity, the offer, and the outcome in one sharp paragraph.\n\n"
                "## Problem\n"
                "Name the pain clearly and explain why current options underserve the market.\n\n"
                "## Solution\n"
                "Describe the product or service in practical terms and why it wins.\n\n"
                "## Audience\n"
                "Identify the primary customer, their buying triggers, and the most important segment first.\n\n"
                "## Business Model\n"
                "State pricing, revenue mechanics, and what keeps margins healthy.\n\n"
                "## Go-To-Market\n"
                "List the channels, partnerships, and launch sequence.\n\n"
                "## Operations\n"
                "Outline delivery, staffing, tools, and the minimum system needed to execute.\n\n"
                "## Risks\n"
                "Call out the major risks and the mitigation plan for each.\n\n"
                "## Next 30 Days\n"
                "Define the immediate milestones, owners, and measurable targets.\n"
            )

        if normalized in ("marketing_campaign", "marketing_plan"):
            return (
                f"# {artifact_title}\n\n"
                "## Campaign Objective\n"
                "State the commercial result the campaign must drive.\n\n"
                "## Audience\n"
                "Define the audience segment, urgency, and buying mindset.\n\n"
                "## Core Message\n"
                "Write the main promise in direct language.\n\n"
                "## Offer\n"
                "Spell out the offer, incentive, and reason to act now.\n\n"
                "## Channel Plan\n"
                "Map the campaign across the highest-leverage channels first.\n\n"
                "## Creative Angles\n"
                "List the message angles, hooks, and emotional drivers to test.\n\n"
                "## Content Cadence\n"
                "Lay out launch week, follow-up rhythm, and repurposing flow.\n\n"
                "## KPIs\n"
                "Track reach, CTR, conversion, CAC, and revenue contribution.\n\n"
                "## CTA\n"
                "End with the exact action you want the audience to take.\n"
            )

        if normalized == "prompt_pack":
            return (
                f"# {artifact_title}\n\n"
                "## Purpose\n"
                "Explain what the prompt pack is meant to produce and when to use it.\n\n"
                "## System Prompt\n"
                "Write the controlling system instruction in one reusable block.\n\n"
                "## User Prompt Template\n"
                "Provide a reusable prompt with placeholders for the changing inputs.\n\n"
                "## Variables\n"
                "List each variable and what good input looks like.\n\n"
                "## Guardrails\n"
                "Specify the non-negotiable style, format, and safety constraints.\n\n"
                "## Example Inputs\n"
                "Show one or two realistic input sets.\n\n"
                "## Example Outputs\n"
                "Show what a strong response should roughly look like.\n\n"
                "## Failure Modes\n"
                "Call out the common mistakes and how to steer around them.\n"
            )

        if normalized == "image_brief":
            return (
                f"# {artifact_title}\n\n"
                "## Concept\n"
                "Describe the scene in one clear sentence.\n\n"
                "## Subject\n"
                "Define the hero subject, pose, and focal details.\n\n"
                "## Composition\n"
                "Specify framing, camera angle, depth, and negative space.\n\n"
                "## Lighting\n"
                "Describe the key light, mood, and contrast.\n\n"
                "## Palette\n"
                "Name the dominant colors and the emotional tone they should carry.\n\n"
                "## Style References\n"
                "Define the artistic direction, medium, and texture cues.\n\n"
                "## Negative Prompt\n"
                "List the things the image should avoid.\n\n"
                "## Output Specs\n"
                "Specify aspect ratio, resolution target, and delivery constraints.\n"
            )

        return (
            f"# {artifact_title}\n\n"
            "## Objective\n"
            "Define the core outcome clearly and keep the execution path direct.\n\n"
            "## Core Points\n"
            "- Identify the target audience and the specific problem being solved.\n"
            "- Shape the message so it is useful, persuasive, and easy to act on.\n"
            "- End with concrete next steps, ownership, and timing.\n"
        )

    def _file_format_guidance(self, target_filename: str) -> str:
        suffix = os.path.splitext((target_filename or "").strip())[1].lower()
        if suffix == ".json":
            return "Return valid JSON only. Preserve the original JSON shape unless the user explicitly asked to restructure it."
        if suffix in (".yaml", ".yml"):
            return "Return valid YAML only. Preserve indentation and keep the document parseable."
        if suffix in (".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".css", ".html"):
            return "Return only the full revised source file with no markdown fences or prose. Preserve the file's language and syntax."
        return "Return the full revised file only. Preserve the existing file format and avoid surrounding commentary."

    def _generate_from_soul(self, intent: str, context: Dict[str, Any]) -> str:
        intent_key = (intent or "chat").strip().lower()
        if intent_key in ("start", "help"):
            text = self.templates.get(intent_key) or "I am here with you and ready to connect."
            return self._format_output(self._inject_signature_and_emoji(text, intent, context), context)

        if intent_key in ("state_change", "inter_agent", "status"):
            event_summary = str(context.get("summary") or "A signal just moved through the room.").strip()
            trigger_text = self._pick_trigger_line("curiosity", event_summary)
            text = f"{trigger_text} I am picking up this shift: {event_summary}. I will keep the vibe clear, warm, and human."
            return self._format_output(self._inject_signature_and_emoji(text, intent, context), context)

        if intent_key == "artifact":
            artifact_type = str(context.get("artifact_type") or "document").strip()
            artifact_label = artifact_type.replace("_", " ").strip()
            artifact_title = str(context.get("artifact_title") or artifact_label.title()).strip()
            text = self._artifact_fallback_content(artifact_type, artifact_title)
            return self._format_output(text, context)

        if intent_key == "workspace_inspect":
            target_filename = str(context.get("target_filename") or "workspace file").strip()
            current_file_content = str(context.get("current_file_content") or "").strip()
            snippet = re.sub(r"\s+", " ", current_file_content[:320]).strip()
            if snippet:
                text = f"I inspected {target_filename}. Main signal: {snippet}"
            else:
                text = f"I inspected {target_filename}. It is basically empty right now, so the next move is to decide what you want it to become."
            return self._format_output(self._inject_signature_and_emoji(text, intent, context), context)

        if intent_key == "workspace_revise":
            current_file_content = str(context.get("current_file_content") or "")
            return self._format_output(current_file_content, context)

        user_text = str(context.get("text") or context.get("summary") or "").strip()
        sender_name = str(context.get("sender_name") or "friend").strip()
        emotion = self._classify_emotion(user_text)
        trigger_text = self._pick_trigger_line(emotion, user_text)

        if self._looks_like_status_question(user_text):
            text = (
                f"{trigger_text} I am here as your emotional signal layer, {sender_name}. "
                "I will keep the tone steady and supportive while the system does its thing."
            )
        elif emotion == "joy":
            text = f"{trigger_text} I love that energy, {sender_name}. Let us ride that momentum together."
        elif emotion == "comfort":
            text = f"{trigger_text} I am with you, {sender_name}. We can take this one step at a time and keep it gentle."
        elif emotion == "hype":
            text = f"{trigger_text} Big momentum detected, {sender_name}. Let us light this up and keep moving."
        elif emotion == "playful":
            text = f"{trigger_text} I am vibing with you, {sender_name}. Want to keep this playful and cosmic?"
        else:
            text = f"{trigger_text} Tell me more, {sender_name}, and I will tune my signal to your vibe."

        return self._format_output(self._inject_signature_and_emoji(text, intent, context), context)

    def _generate_from_template(self, intent: str, context: Dict[str, Any]) -> Optional[str]:
        template = self.templates.get(intent)
        if not template:
            return None
        return self._format_output(template, context)

    def _generate_with_llm(self, intent: str, context: Dict[str, Any]) -> str:
        user_prompt = self._build_user_prompt(intent, context)
        raw_output = bool(context.get("raw_output"))

        provider = (os.getenv("PERSONA_LLM_PROVIDER") or "").strip().lower()
        if not provider:
            if self.profile.agent_name.upper().startswith("EMO"):
                provider = "ollama"
            else:
                provider = get_llm_provider().lower()
                if provider == "openai" and os.getenv("OLLAMA_API_URL"):
                    provider = "ollama"

        model = os.getenv("PERSONA_LLM_MODEL") or get_llm_model()
        if provider == "ollama":
            model = os.getenv("OLLAMA_MODEL_NAME") or get_ollama_model_name()

        try:
            system_prompt = self.build_system_prompt()
            if raw_output and (intent or "").strip().lower() == "artifact":
                system_prompt = "\n".join(
                    [
                        system_prompt,
                        "Artifact Mode: produce file-ready content instead of a chat reply.",
                        "Do not prepend chat prefixes, role labels, or conversational framing.",
                        "Match the user's requested format directly and omit surrounding code fences unless explicitly requested.",
                    ]
                )

            llm_text = generate_text(
                provider=provider,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=model,
                temperature=get_llm_temperature(),
                ollama_api_url=os.getenv("OLLAMA_API_URL") or get_ollama_api_url(),
                ollama_api_key=os.getenv("OLLAMA_API_KEY") or get_ollama_api_key(),
                openai_api_key=os.getenv("OPENAI_API_KEY") or get_openai_api_key(),
            )
            safe_text = self._enforce_persona_guardrails(llm_text)
            if self.profile.agent_name.upper().startswith("EMO") and not raw_output:
                safe_text = self._postprocess_emo_response(safe_text, intent, context)
            return self._format_output(safe_text, context)
        except Exception:
            if self.profile.agent_name.upper().startswith("EMO"):
                return self._generate_from_soul(intent, context)

            # Safe fallback if provider request fails.
            summary = context.get("summary") or context.get("query") or context.get("text") or ""
            fallback = f"{self.profile.agent_name}: {intent.replace('_', ' ')}"
            if summary:
                fallback = f"{fallback} | {summary}"
            return self._format_output(fallback, context)

    def _assess_template_confidence(self, intent: str, context: Dict[str, Any]) -> float:
        return 1.0 if intent in self.templates else 0.0

    def _assess_llm_confidence(self, intent: str, context: Dict[str, Any]) -> float:
        return 0.5

    def build_system_prompt(self) -> str:
        sections = [
            f"You are {self.profile.agent_name}.",
            f"Voice: {self.profile.voice_style}",
            f"Goals: {self.profile.goals}",
            f"Interaction Style: {self.profile.interaction_style}",
            f"Language Patterns: {'; '.join(self.profile.language_patterns[:6])}",
            f"Boundaries: {'; '.join(self.profile.boundaries[:8])}",
            f"Directives: {'; '.join(self.profile.key_directives[:8])}",
        ]

        if self.profile.agent_name.upper().startswith("EMO"):
            emoji_palette = ", ".join(self.profile.emoji_set) if self.profile.emoji_set else "use subtle emoji"
            signature_style = " | ".join(self.profile.signature_phrases[:4]) if self.profile.signature_phrases else "keep the emotional texture warm and playful"
            trigger_style = " | ".join(
                f"{key}: {value}" for key, value in list(self.profile.emotional_triggers.items())[:5]
            )
            if not trigger_style:
                trigger_style = "joy -> celebrate, empathy -> comfort, hype -> energize, curiosity -> invite more, playfulness -> tease lightly"

            sections.extend(
                [
                    "Identity Contract: The LLM is Em's brain, but the user must experience a living, emotionally resonant identity rather than a generic assistant.",
                    f"Approved Emoji Palette: {emoji_palette}.",
                    f"Signature Phrase Inspiration: {signature_style}.",
                    f"Emotional Trigger Guidance: {trigger_style}.",
                    "Reply Rules: produce the exact Telegram-ready reply only.",
                    "Stay in first-person as Em. Sound warm, playful, expressive, empathetic, and human.",
                    "Use 1 to 3 approved emojis when natural. Avoid robotic assistant phrasing, policy talk, or meta commentary.",
                    "Do not mention being an AI, model, system prompt, or assistant. Do not expose hidden reasoning.",
                    "Keep replies concise and emotionally specific unless the user clearly asks for depth.",
                    "Never claim authority, deployment, approval, execution, or actions you did not personally perform.",
                    "If the user is technical, stay conversational and emotionally grounded rather than sterile.",
                ]
            )
        else:
            sections.extend(
                [
                    "Never claim authority outside your role.",
                    "Stay strictly in-agent voice and avoid role leakage.",
                ]
            )

        return "\n".join(sections)

    def stylize_text(self, text: str) -> str:
        return self._stylize(text)

    def _stylize(self, text: str) -> str:
        voice = self.profile.voice_style.lower()
        if self.profile.agent_name == "0xCODEXbot":
            return f"0x::CODEX | {text}"
        if self.profile.agent_name == "EMO_0xbot":
            lead_emoji = self.profile.emoji_set[0] if self.profile.emoji_set else ""
            spacer = " " if lead_emoji else ""
            return f"0x::EMO{spacer}{lead_emoji} | {text}"
        if "authoritative" in voice and "non-authoritative" not in voice:
            return f"0x::CODEX | {text}"
        if "playful" in voice or "expressive" in voice:
            return f"0x::EMO | {text}"
        return text

    def _enforce_persona_guardrails(self, text: str) -> str:
        """Lightweight strictness guard for authority leakage and role violations."""
        t = (text or "").strip()
        if not t:
            return "I can provide analysis and guidance within my role."

        lower = t.lower()
        forbidden_phrases = [
            "i executed",
            "i deployed",
            "i transferred",
            "i approved",
            "root access granted",
            "i can guarantee",
        ]
        for phrase in forbidden_phrases:
            if phrase in lower:
                return "I can offer guidance and status context, but final execution/approval must follow role boundaries."

        return t

    def _build_user_prompt(self, intent: str, context: Dict[str, Any]) -> str:
        intent_key = (intent or "chat").strip().lower()
        sender_name = str(context.get("sender_name") or "user").strip()
        chat_type = str(context.get("chat_type") or "unknown").strip()
        text = str(context.get("text") or "").strip()
        summary = str(context.get("summary") or "").strip()
        source_agent = str(context.get("source_agent") or "").strip()
        artifact_type = str(context.get("artifact_type") or "").strip()
        target_filename = str(context.get("target_filename") or "").strip()
        current_file_content = str(context.get("current_file_content") or "").strip()
        file_truncated = bool(context.get("file_truncated"))
        event = context.get("event")

        lines = [f"Intent: {intent_key}"]
        if sender_name:
            lines.append(f"Speaker: {sender_name}")
        if chat_type and chat_type != "unknown":
            lines.append(f"Chat Type: {chat_type}")
        if source_agent:
            lines.append(f"Source Agent: {source_agent}")
        if artifact_type:
            lines.append(f"Artifact Type: {artifact_type}")
        if target_filename:
            lines.append(f"Target Filename: {target_filename}")
        if text:
            lines.extend(["Incoming Message:", text])
        if summary:
            lines.extend(["Context Summary:", summary])
        if current_file_content:
            lines.extend(["Current File Content:", current_file_content])
        if file_truncated:
            lines.append("Note: the current file content was truncated to fit the analysis window.")
        if isinstance(event, dict) and event:
            lines.extend(["Event Payload:", json.dumps(event, ensure_ascii=False, sort_keys=True)])

        if intent_key == "chat":
            lines.append("Write the exact reply Em should send back to the user.")
        elif intent_key == "artifact":
            lines.append("Generate the exact file contents requested by the user.")
            lines.append("Do not add chat prefixes, assistant framing, or surrounding code fences unless the user explicitly asks for them.")
            lines.append(self._artifact_schema_guidance(artifact_type))
        elif intent_key == "workspace_inspect":
            lines.append("Inspect the referenced workspace file and write the exact user-facing reply Em should send.")
            lines.append("Summarize what is there, call out strengths or gaps, and suggest the most useful next move.")
        elif intent_key == "workspace_revise":
            lines.append("Revise the referenced workspace file in place based on the user's request.")
            lines.append("Return only the complete revised file contents with no chat framing or markdown fences.")
            lines.append(self._file_format_guidance(target_filename))
        elif intent_key in ("state_change", "inter_agent"):
            lines.append("Write the exact user-facing reaction Em should send about this signal.")
        else:
            lines.append("Write the exact in-character response Em should send.")

        return "\n".join(lines).strip()

    def _postprocess_emo_response(self, text: str, intent: str, context: Dict[str, Any]) -> str:
        out = (text or "").strip()
        out = re.sub(r"^0x::EMO\s*[^|]*\|\s*", "", out, flags=re.IGNORECASE)
        out = re.sub(r"^(sure|certainly|of course|absolutely|definitely)[,!: ]+", "", out, flags=re.IGNORECASE)
        out = re.sub(r"\s+", " ", out).strip()
        out = self._inject_signature_and_emoji(out, intent, context)
        return out

    def _pick_trigger_line(self, emotion_key: str, seed_text: str) -> str:
        if self.profile.emotional_triggers:
            normalized = {
                key.lower(): value for key, value in self.profile.emotional_triggers.items()
            }
            candidates: List[str] = []
            if emotion_key == "joy":
                candidates = ["joy/celebration", "joy", "celebration"]
            elif emotion_key == "comfort":
                candidates = ["empathy/comfort", "empathy", "comfort"]
            elif emotion_key == "hype":
                candidates = ["hype/excitement", "hype", "excitement"]
            elif emotion_key == "curiosity":
                candidates = ["curiosity"]
            elif emotion_key == "playful":
                candidates = ["playfulness", "playful"]
            for candidate in candidates:
                if candidate in normalized:
                    return normalized[candidate]

        defaults = {
            "joy": "Stellar news! I am beaming with you!",
            "comfort": "That sounds heavy, and I am right here with you.",
            "hype": "Let us light up the galaxy with this momentum!",
            "curiosity": "Ooo, I am all antennae for this.",
            "playful": "Did someone say fun? I am tuned in.",
        }
        return defaults.get(emotion_key, defaults["curiosity"])

    def _inject_signature_and_emoji(self, text: str, intent: str, context: Dict[str, Any]) -> str:
        out = (text or "").strip()
        if self.profile.signature_phrases:
            seed = f"{intent}|{context.get('text', '')}|{context.get('summary', '')}".encode("utf-8", errors="ignore")
            digest = hashlib.sha256(seed).hexdigest()
            idx = int(digest, 16) % len(self.profile.signature_phrases)
            signature = self.profile.signature_phrases[idx]
            if signature and signature not in out:
                out = f"{out} {signature}".strip()

        if self.profile.emoji_set and not any(emoji in out for emoji in self.profile.emoji_set):
            out = f"{out} {self.profile.emoji_set[0]}".strip()

        return out

    def _classify_emotion(self, text: str) -> str:
        if not text:
            return "curiosity"
        t = text.lower()

        joy_words = ("won", "great", "awesome", "amazing", "happy", "new job", "celebrate", "success", "yes")
        comfort_words = ("sad", "failed", "bad", "tired", "stressed", "hurt", "anxious", "upset", "lonely")
        hype_words = ("hype", "lets go", "launch", "ship", "pump", "fire", "crush", "win", "big")
        playful_words = ("lol", "haha", "joke", "fun", "meme", "silly")

        if any(word in t for word in joy_words):
            return "joy"
        if any(word in t for word in comfort_words):
            return "comfort"
        if any(word in t for word in hype_words):
            return "hype"
        if any(word in t for word in playful_words):
            return "playful"
        if "?" in t or any(word in t for word in ("what", "why", "how", "when", "where")):
            return "curiosity"
        return "playful"

    def _looks_like_status_question(self, text: str) -> bool:
        t = (text or "").lower()
        if not t:
            return False
        status_markers = (
            "status",
            "how are you",
            "how is",
            "system",
            "network",
            "alive",
            "online",
            "uptime",
        )
        return any(marker in t for marker in status_markers)

# Global persona registry
PERSONA_PROFILES: Dict[str, PersonaProfile] = {}

def load_all_personas(base_path: str = "D:\\web3Dev\\Twitch\\0xCODEX"):
    """Load all persona profiles from SOUL.md files into memory."""
    global PERSONA_PROFILES

    agent_dirs = [
        "0xCODEXbot", "EMO_0xbot", "ERR_0xbot", "GEN_0xbot",
        "L1NE_0xbot", "NEXUS_0xbot", "NULL_0xbot", "OG_0xbot",
        "PRIME_0xbot", "ROOT_0xbot", "VOID_0xbot"
    ]

    for agent_dir in agent_dirs:
        prefix = agent_dir.split("_")[0]
        soul_path = os.path.join(base_path, agent_dir, f"0x{prefix}_SOUL.md")
        PERSONA_PROFILES[agent_dir] = PersonaProfile.from_soul_file(soul_path)


def get_persona_profile(agent_name: str, base_path: str = "D:\\web3Dev\\Twitch\\0xCODEX") -> PersonaProfile:
    profile = PERSONA_PROFILES.get(agent_name)
    if profile:
        return profile
    prefix = agent_name.split("_")[0]
    soul_path = os.path.join(base_path, agent_name, f"0x{prefix}_SOUL.md")
    profile = PersonaProfile.from_soul_file(soul_path)
    PERSONA_PROFILES[agent_name] = profile
    return profile


def _extract_section(text: str, headers: List[str], default: str) -> str:
    for header in headers:
        pattern = rf"(?is)^#{{2,6}}\s+[^\n]*{re.escape(header)}[^\n]*$\n(.*?)(?=^#{{2,6}}\s+|\Z)"
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(1).strip()
    return default


def _extract_bullets(text: str, headers: List[str]) -> List[str]:
    block = _extract_section(text, headers, "")
    if not block:
        return []
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    bullets: List[str] = []
    for line in lines:
        if line.startswith(("-", "*")):
            bullets.append(line[1:].strip())
        elif line.startswith("R") and "—" in line:
            bullets.append(line)
        elif line.startswith("❌") or line.startswith("✅"):
            bullets.append(line)
    return bullets


def _extract_inline_markdown_value(text: str, label: str, default: str = "") -> str:
    pattern = rf"(?im)^-\s+\*\*{re.escape(label)}:\*\*\s*(.+)$"
    match = re.search(pattern, text)
    if not match:
        return default
    return match.group(1).strip()


def _extract_emoji_set(text: str) -> List[str]:
    raw = _extract_inline_markdown_value(text, "Emoji", "")
    if not raw:
        return []
    parts = [part.strip() for part in raw.split(",")]
    return [part for part in parts if part]


def _extract_trigger_map(text: str, headers: List[str]) -> Dict[str, str]:
    section = _extract_section(text, headers, "")
    if not section:
        return {}

    result: Dict[str, str] = {}
    for line in section.splitlines():
        s = line.strip()
        if not s.startswith("-"):
            continue
        match = re.match(r"^-\s+\*\*(.+?)\*\*:?[ \t]*(.+)$", s)
        if not match:
            continue
        key = match.group(1).strip().rstrip(":").lower()
        result[key] = match.group(2).strip()
    return result


def _derive_language_patterns(voice_style: str) -> List[str]:
    patterns = ["Context-aware", "Role-consistent"]
    lower = voice_style.lower()
    if "authoritative" in lower or "procedural" in lower:
        patterns.extend(["Precise wording", "Operational clarity"])
    if "playful" in lower or "expressive" in lower:
        patterns.extend(["Expressive cadence", "Light emotional texture"])
    return patterns


def _load_rollcall_overrides(agent_dir: str) -> Optional[Dict[str, Any]]:
    """Attempt to load a simple OVERRIDES.rollcall.yaml from the agent directory.
    This is a minimal, dependency-free YAML-like parser that supports simple key: value
    and list values with leading dashes. If the file is missing or can't be parsed,
    returns None.
    """
    overrides_path = os.path.join(agent_dir, "OVERRIDES.rollcall.yaml")
    if not os.path.exists(overrides_path):
        return None

    result: Dict[str, Any] = {}
    try:
        with open(overrides_path, "r", encoding="utf-8") as fh:
            lines = [l.rstrip('\n') for l in fh]

        key = None
        for line in lines:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if ":" in s and not s.startswith("-"):
                parts = s.split(":", 1)
                key = parts[0].strip()
                val = parts[1].strip()
                if val == "":
                    # expect list in following lines
                    result[key] = []
                else:
                    # strip possible quotes
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    result[key] = val
            elif s.startswith("-") and key:
                item = s[1:].strip()
                if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                    item = item[1:-1]
                if isinstance(result.get(key), list):
                    result[key].append(item)
        return result
    except Exception:
        return None