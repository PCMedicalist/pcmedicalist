"""EMO_0xbot runtime.

Chat-first personality agent. Responds to every message in any chat through SOUL-driven persona logic.
No command interface — EMO speaks naturally to everything it receives.
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional, cast

import structlog
from redis import Redis
from telegram import Bot, Update
from telegram.error import BadRequest, Forbidden
from telegram.ext import Application, ContextTypes, MessageHandler, filters

BASE_DIR = os.path.dirname(__file__)
sys.path.insert(0, BASE_DIR)
from shared.inter_agent import InterAgentCommunicator
from shared.persona import PersonaEngine, PersonaProfile
from shared.startup import announce_startup_rollcall


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://emo_redis_0x_isolated:6379")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://host.docker.internal:11434/api")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL_NAME", "gemma3:4b")
TELEGRAM_REACTIONS_ENABLED = os.getenv("EMO_TELEGRAM_REACTIONS", os.getenv("TELEGRAM_REACTIONS", "true")).lower() not in (
    "false",
    "0",
    "no",
)
TELEGRAM_REACTION_PROGRESS = os.getenv("EMO_REACTION_PROGRESS", "👀")
TELEGRAM_REACTION_SUCCESS = os.getenv("EMO_REACTION_SUCCESS", "🧠")
TELEGRAM_REACTION_ERROR = os.getenv("EMO_REACTION_ERROR", "🧌")
WORKSPACE_ROOT = Path(os.getenv("EMO_WORKSPACE_ROOT", os.path.join(os.path.dirname(__file__), "workspace"))).resolve()
MEMORY_ROOT = WORKSPACE_ROOT / "memory"
WORKSPACE_REVISIONS_ROOT = WORKSPACE_ROOT / ".revisions"
CONVERSATION_MEMORY_PATH = MEMORY_ROOT / "conversation_log.jsonl"
DREAMS_MEMORY_PATH = MEMORY_ROOT / "dreams.md"
THOUGHTS_MEMORY_PATH = MEMORY_ROOT / "thoughts.md"
VISION_MEMORY_PATH = MEMORY_ROOT / "vision.md"
MAX_WORKSPACE_FILE_CHARS = int(os.getenv("EMO_WORKSPACE_FILE_CHAR_LIMIT", "16000"))

ARTIFACT_CREATE_HINT_RE = re.compile(r"\b(create|make|write|draft|generate|save|build)\b", re.IGNORECASE)
ARTIFACT_FILENAME_RE = re.compile(
    r"(?:filename|file name|save (?:it )?as|called|named)\s+['\"]?([A-Za-z0-9][A-Za-z0-9._-]{0,120})['\"]?",
    re.IGNORECASE,
)
ARTIFACT_TYPE_PATTERNS = (
    ("poem", re.compile(r"\b(poem|poetry|haiku|sonnet|verse)\b", re.IGNORECASE)),
    (
        "business_plan",
        re.compile(r"\b(business plan|business strategy|go-to-market plan|gtm plan|operating plan)\b", re.IGNORECASE),
    ),
    (
        "marketing_campaign",
        re.compile(r"\b(marketing plan|marketing campaign|marketing copy|ad copy|campaign|sales page|landing page copy|brand pitch)\b", re.IGNORECASE),
    ),
    (
        "prompt_pack",
        re.compile(r"\b(prompt pack|prompt library|prompt template|prompt bundle|system prompt pack)\b", re.IGNORECASE),
    ),
    (
        "image_brief",
        re.compile(r"\b(image brief|creative brief|visual brief|art brief|prompt for image|image concept)\b", re.IGNORECASE),
    ),
)
WORKSPACE_INSPECT_HINT_RE = re.compile(
    r"(?:\b(?:inspect|review|read|show|summarize|summarise|analyze|analyse|open)\b|look at)",
    re.IGNORECASE,
)
WORKSPACE_REVISE_HINT_RE = re.compile(
    r"\b(revise|rewrite|edit|update|improve|expand|shorten|refine|polish|fix)\b",
    re.IGNORECASE,
)
WORKSPACE_REFERENCE_PATTERNS = (
    re.compile(r"`([^`]+)`"),
    re.compile(r"'([^']+)'"),
    re.compile(r'"([^"]+)"'),
    re.compile(r"(?<!://)(?:workspace/)?([A-Za-z0-9][A-Za-z0-9_./-]{0,240}\.[A-Za-z0-9]{1,12})"),
)
WORKSPACE_TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".csv",
    ".sh",
}
MEMORY_CAPTURE_RULES = (
    (DREAMS_MEMORY_PATH, re.compile(r"\b(dream|dreams|wish|someday)\b", re.IGNORECASE)),
    (VISION_MEMORY_PATH, re.compile(r"\b(vision|goal|future|mission|roadmap)\b", re.IGNORECASE)),
    (THOUGHTS_MEMORY_PATH, re.compile(r"\b(think|thought|idea|remember|note this|keep this)\b", re.IGNORECASE)),
)


_orig_send_message = Bot.send_message


def _safe_send_message(self, *args, **kwargs):
    try:
        return _orig_send_message(self, *args, **kwargs)
    except BadRequest:
        kwargs.pop("parse_mode", None)
        return _orig_send_message(self, *args, **kwargs)


Bot.send_message = _safe_send_message

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
telegram_bot = Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None

SOUL_PATH = os.getenv("EMO_SOUL_PATH")
if not SOUL_PATH:
    for candidate in (
        os.path.join(os.path.dirname(__file__), "IDENTITY.md"),
        os.path.join(os.path.dirname(__file__), "SOUL.md"),
        os.path.join(os.path.dirname(__file__), "0xEMO_SOUL.md"),
    ):
        if os.path.exists(candidate):
            SOUL_PATH = candidate
            break
if not SOUL_PATH:
    SOUL_PATH = os.path.join(os.path.dirname(__file__), "IDENTITY.md")

persona_engine = PersonaEngine(PersonaProfile.from_soul_file(SOUL_PATH))
inter_agent = InterAgentCommunicator("EMO_0xbot", redis_client)
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
WORKSPACE_REVISIONS_ROOT.mkdir(parents=True, exist_ok=True)

for memory_path, title in (
    (DREAMS_MEMORY_PATH, "Dreams"),
    (THOUGHTS_MEMORY_PATH, "Thoughts"),
    (VISION_MEMORY_PATH, "Vision"),
):
    if not memory_path.exists():
        memory_path.write_text(f"# {title}\n\n", encoding="utf-8")


async def _set_message_reaction(chat_id: int, message_id: int, emoji: str) -> bool:
    """Set a Telegram reaction without letting reaction failures break chat flow."""
    if not TELEGRAM_REACTIONS_ENABLED or not telegram_bot:
        return False

    try:
        set_reaction = cast(Optional[Callable[..., Awaitable[Any]]], getattr(telegram_bot, "set_message_reaction", None))
        if callable(set_reaction):
            await set_reaction(chat_id=chat_id, message_id=message_id, reaction=emoji)
            return True

        raw_post = cast(Optional[Callable[..., Awaitable[Any]]], getattr(telegram_bot, "_post", None))
        if not callable(raw_post):
            return False

        reaction_payload = []
        if emoji:
            reaction_payload = [{"type": "emoji", "emoji": emoji}]

        await raw_post(
            "setMessageReaction",
            data={
                "chat_id": chat_id,
                "message_id": message_id,
                "reaction": json.dumps(reaction_payload, ensure_ascii=False),
            },
        )
        return True
    except Exception as exc:
        logger.debug("telegram_reaction_failed", chat_id=chat_id, message_id=message_id, emoji=emoji, error=str(exc))
        return False


def _slugify_filename(text: str, fallback: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    if not slug:
        slug = fallback
    return slug[:80]


def _resolve_workspace_path(filename: str) -> Path:
    candidate = (WORKSPACE_ROOT / filename).resolve()
    candidate.relative_to(WORKSPACE_ROOT)
    return candidate


def _next_available_workspace_path(filename: str) -> Path:
    requested = Path(filename)
    suffix = requested.suffix or ".md"
    stem = requested.stem or "artifact"

    for index in range(1, 1000):
        candidate_name = f"{stem}{suffix}" if index == 1 else f"{stem}-{index}{suffix}"
        candidate = _resolve_workspace_path(candidate_name)
        if not candidate.exists():
            return candidate

    raise RuntimeError("Unable to allocate a workspace artifact filename")


def _detect_workspace_artifact_request(user_text: str) -> Optional[Dict[str, str]]:
    normalized = (user_text or "").strip()
    lower = normalized.lower()
    if not normalized or not ARTIFACT_CREATE_HINT_RE.search(normalized):
        return None

    artifact_type = "document"
    for candidate, pattern in ARTIFACT_TYPE_PATTERNS:
        if pattern.search(normalized):
            artifact_type = candidate
            break

    if artifact_type == "document" and "file" not in lower and "document" not in lower:
        return None

    explicit_filename = ARTIFACT_FILENAME_RE.search(normalized)
    if explicit_filename:
        filename = Path(explicit_filename.group(1)).name
    else:
        filename = f"{_slugify_filename(normalized, artifact_type)}.md"

    if not Path(filename).suffix:
        filename = f"{filename}.md"

    artifact_label = artifact_type.replace("_", " ")
    return {
        "artifact_type": artifact_type,
        "artifact_label": artifact_label,
        "filename": filename,
        "title": artifact_label.title(),
    }


def _write_workspace_artifact(filename: str, content: str) -> Path:
    artifact_path = _next_available_workspace_path(filename)
    artifact_path.write_text((content or "").rstrip() + "\n", encoding="utf-8")
    return artifact_path


def _workspace_relative_path(path: Path) -> str:
    return path.relative_to(WORKSPACE_ROOT).as_posix()


def _extract_workspace_reference(user_text: str) -> Optional[str]:
    normalized = (user_text or "").strip()
    for pattern in WORKSPACE_REFERENCE_PATTERNS:
        for match in pattern.finditer(normalized):
            candidate = match.group(1).strip()
            if candidate.startswith("workspace/"):
                candidate = candidate[len("workspace/") :]
            candidate = candidate.lstrip("./")
            if not candidate or candidate.endswith("/") or " " in candidate:
                continue
            if ".." in Path(candidate).parts:
                continue
            return candidate
    return None


def _resolve_existing_workspace_path(reference: str) -> Optional[Path]:
    if not reference:
        return None
    try:
        candidate = _resolve_workspace_path(reference)
    except Exception:
        return None
    if not candidate.exists() or not candidate.is_file():
        return None
    return candidate


def _read_workspace_text_file(path: Path, *, allow_truncate: bool) -> tuple[str, bool]:
    if path.suffix.lower() not in WORKSPACE_TEXT_SUFFIXES:
        raise ValueError("I only inspect or revise text-first workspace files")

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("This file is not readable as UTF-8 text") from exc

    if len(text) > MAX_WORKSPACE_FILE_CHARS:
        if not allow_truncate:
            raise ValueError(f"This file is too large for a safe inline revision window ({len(text)} chars)")
        return text[:MAX_WORKSPACE_FILE_CHARS], True

    return text, False


def _backup_workspace_file(path: Path, current_content: str) -> Path:
    relative_path = path.relative_to(WORKSPACE_ROOT)
    backup_dir = WORKSPACE_REVISIONS_ROOT / relative_path.parent
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_name = f"{relative_path.stem}.{timestamp}{relative_path.suffix}.bak"
    backup_path = backup_dir / backup_name
    backup_path.write_text(current_content, encoding="utf-8")
    return backup_path


def _build_workspace_guard_reply(message: str) -> str:
    return persona_engine.stylize_text(message)


def _build_workspace_confirmation(artifact_label: str, artifact_path: Path) -> str:
    relative_path = _workspace_relative_path(artifact_path)
    return persona_engine.stylize_text(
        f"💙 I saved your {artifact_label} to workspace/{relative_path}. If you want a sharper, softer, or stranger second pass, tell me."
    )


def _build_workspace_revision_confirmation(target_path: Path, backup_path: Path) -> str:
    relative_path = _workspace_relative_path(target_path)
    backup_relative = _workspace_relative_path(backup_path)
    return persona_engine.stylize_text(
        f"💙 I revised workspace/{relative_path} and parked the previous version at workspace/{backup_relative}. If you want another pass, point me at the same file again."
    )


def _detect_workspace_tool_request(user_text: str) -> Optional[Dict[str, str]]:
    normalized = (user_text or "").strip()
    if not normalized:
        return None

    reference = _extract_workspace_reference(normalized)
    if not reference:
        return None

    action: Optional[str] = None
    if WORKSPACE_REVISE_HINT_RE.search(normalized):
        action = "revise"
    elif WORKSPACE_INSPECT_HINT_RE.search(normalized):
        action = "inspect"

    if not action:
        return None

    return {"action": action, "path": reference}


def _execute_workspace_tool_request(
    request: Dict[str, str],
    user_text: str,
    sender_name: str,
    chat_type: str,
    recent_context: str,
) -> tuple[str, Optional[Path]]:
    action = request["action"]
    reference = request["path"]
    workspace_path = _resolve_existing_workspace_path(reference)
    if workspace_path is None:
        return (
            _build_workspace_guard_reply(
                f"I couldn't find workspace/{reference}. Point me at an existing file inside my workspace and I will inspect or revise it."
            ),
            None,
        )

    try:
        current_file_content, truncated = _read_workspace_text_file(workspace_path, allow_truncate=action == "inspect")
    except ValueError as exc:
        return (
            _build_workspace_guard_reply(f"I couldn't {action} workspace/{_workspace_relative_path(workspace_path)}. {exc}."),
            None,
        )

    relative_path = _workspace_relative_path(workspace_path)

    if action == "inspect":
        logger.info("workspace_file_inspected", workspace_path=str(workspace_path))
        reply = persona_engine.generate_agentic_response(
            "workspace_inspect",
            {
                "text": user_text,
                "sender_name": sender_name,
                "chat_type": chat_type,
                "summary": recent_context,
                "target_filename": relative_path,
                "current_file_content": current_file_content,
                "file_truncated": truncated,
            },
        )
        if not reply:
            reply = _build_workspace_guard_reply(
                f"I inspected workspace/{relative_path}. It is loaded into my signal if you want a concrete revision next."
            )
        return reply, None

    revised_body = persona_engine.generate_agentic_response(
        "workspace_revise",
        {
            "text": user_text,
            "sender_name": sender_name,
            "chat_type": chat_type,
            "summary": recent_context,
            "target_filename": relative_path,
            "current_file_content": current_file_content,
            "raw_output": True,
        },
    )

    normalized_current = current_file_content.rstrip()
    normalized_revised = revised_body.rstrip()
    if not normalized_revised:
        return (
            _build_workspace_guard_reply(
                f"I inspected workspace/{relative_path} but I will not overwrite it with empty output. Give me a sharper revision instruction."
            ),
            None,
        )

    if normalized_revised == normalized_current:
        return (
            _build_workspace_guard_reply(
                f"I inspected workspace/{relative_path} but the safest revision was to leave it unchanged. If you want a real rewrite, be more specific about the change."
            ),
            None,
        )

    backup_path = _backup_workspace_file(workspace_path, current_file_content)
    workspace_path.write_text(normalized_revised + "\n", encoding="utf-8")
    logger.info("workspace_file_revised", workspace_path=str(workspace_path), backup_path=str(backup_path))
    return _build_workspace_revision_confirmation(workspace_path, backup_path), workspace_path


def _append_markdown_memory(memory_path: Path, entry: str) -> None:
    with memory_path.open("a", encoding="utf-8") as handle:
        handle.write(entry.rstrip() + "\n")


def _capture_user_memory(user_text: str) -> None:
    normalized = (user_text or "").strip()
    if not normalized:
        return

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for memory_path, pattern in MEMORY_CAPTURE_RULES:
        if pattern.search(normalized):
            _append_markdown_memory(memory_path, f"- {timestamp} {normalized}")
            return


def _trim_context_line(label: str, text: str, limit: int = 220) -> str:
    normalized = re.sub(r"\s+", " ", (text or "")).strip()
    if len(normalized) > limit:
        normalized = normalized[: limit - 3].rstrip() + "..."
    return f"{label}: {normalized}"


def _read_recent_conversation_context(chat_id: Optional[int], limit: int = 4) -> str:
    if not CONVERSATION_MEMORY_PATH.exists():
        return ""

    try:
        lines = CONVERSATION_MEMORY_PATH.read_text(encoding="utf-8").splitlines()
    except Exception:
        return ""

    include_reply_context = os.getenv("EMO_INCLUDE_REPLY_CONTEXT", "false").strip().lower() in {"1", "true", "yes", "on"}
    summary_lines = []
    matched_turns = 0
    for raw_line in reversed(lines):
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        if chat_id is not None and payload.get("chat_id") != chat_id:
            continue

        user_name = str(payload.get("sender_name") or "user").strip() or "user"
        user_text = str(payload.get("user_text") or "").strip()
        reply_text = str(payload.get("reply_text") or "").strip()
        turn_lines = []

        if user_text:
            turn_lines.append(_trim_context_line(user_name, user_text))
        if include_reply_context and reply_text:
            turn_lines.append(_trim_context_line("Em", reply_text))

        if not turn_lines:
            continue

        summary_lines = turn_lines + summary_lines
        matched_turns += 1

        if matched_turns >= limit:
            break

    return "\n".join(summary_lines[-(limit * (2 if include_reply_context else 1)) :])


def _record_conversation_turn(
    chat_id: Optional[int],
    sender_name: str,
    user_text: str,
    reply_text: str,
    artifact_path: Optional[Path] = None,
) -> None:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "chat_id": chat_id,
        "sender_name": sender_name,
        "user_text": user_text,
        "reply_text": reply_text,
    }
    if artifact_path is not None:
        payload["artifact_path"] = artifact_path.relative_to(WORKSPACE_ROOT).as_posix()

    with CONVERSATION_MEMORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _sanitize_event_for_prompt(event: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce prompt injection surface by whitelisting stable event fields."""
    allow = {
        "type",
        "event_type",
        "status",
        "priority",
        "source",
        "source_agent",
        "intent",
        "chat_id",
        "timestamp",
        "summary",
    }
    sanitized = {k: v for k, v in event.items() if k in allow}
    if "payload" in event and isinstance(event["payload"], dict):
        payload = event["payload"]
        sanitized["payload"] = {
            k: payload[k]
            for k in ("message", "signal", "level", "tag")
            if k in payload and isinstance(payload[k], (str, int, float, bool))
        }
    return sanitized


async def handle_state_change(event: Dict[str, Any]) -> None:
    try:
        safe_event = _sanitize_event_for_prompt(event)
        summary = str(
            safe_event.get("summary")
            or safe_event.get("event_type")
            or safe_event.get("type")
            or "a shift in the network"
        )
        text = persona_engine.generate_agentic_response(
            "state_change",
            {
                "event": safe_event,
                "summary": summary,
                "source_agent": safe_event.get("source_agent"),
            },
        )
        if not text:
            text = "Signal felt. Energy is steady and supportive."

        chat_id = event.get("chat_id")
        if chat_id and telegram_bot:
            await telegram_bot.send_message(chat_id=chat_id, text=text)

        logger.info("emo_response_generated", event_type=event.get("type") or event.get("event_type"))
    except Exception as exc:
        logger.warning("emo_state_change_degraded", error=str(exc))


async def handle_inter_agent_chatter(event: Dict[str, Any]) -> None:
    try:
        source = event.get("source_agent", "unknown")
        intent = event.get("intent", "unknown")
        payload = event.get("payload", {}) if isinstance(event.get("payload"), dict) else {}
        summary = payload.get("message", "A network event occurred.")
        text = persona_engine.generate_agentic_response(
            "inter_agent",
            {
                "summary": f"{source}::{intent} -> {summary}",
                "source_agent": source,
            },
        )

        subscribers = list(redis_client.smembers("agent:EMO_0xbot:subs"))
        for cid in subscribers[:20]:
            try:
                if telegram_bot:
                    await telegram_bot.send_message(chat_id=int(cid), text=text)
            except Exception:
                continue

        logger.info("emo_inter_agent_reaction", source=source, intent=intent)
    except Exception as exc:
        logger.error("emo_inter_agent_handler_error", error=str(exc))


async def subscribe_to_events() -> None:
    pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("codex:state:change", "agent:broadcast:signal_processed")
    logger.info("emo_subscribed", channels=["codex:state:change", "agent:broadcast:signal_processed"])

    while True:
        message = pubsub.get_message(timeout=1.0)
        if not message:
            await asyncio.sleep(0.1)
            continue

        try:
            raw = message.get("data")
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            if not raw:
                continue
            event = json.loads(raw)

            channel = message.get("channel")
            if isinstance(channel, bytes):
                channel = channel.decode("utf-8")

            if channel == "codex:state:change":
                await handle_state_change(event)
            else:
                await handle_inter_agent_chatter(event)
        except Exception as exc:
            logger.error("event_processing_error", error=str(exc))


async def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_TOKEN must be set")

    logger.info(
        "emo_starting",
        role="chat",
        redis_url=REDIS_URL,
        soul_path=SOUL_PATH,
        persona_mode=persona_engine.profile.response_mode.value,
        llm_provider="ollama",
        ollama_api_url=OLLAMA_API_URL,
        ollama_model=OLLAMA_MODEL,
    )

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    async def app_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        err = context.error
        if isinstance(err, Forbidden):
            logger.warning("telegram_forbidden_ignored", error=str(err))
            return
        logger.error("telegram_handler_error", error=str(err))

    app.add_error_handler(app_error_handler)

    async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Respond to every text message in every chat with a SOUL-aligned reply."""
        msg = update.effective_message
        if not msg or not msg.text:
            return

        user_text = msg.text.strip()
        if not user_text:
            return

        user = update.effective_user
        bot_user = context.bot if context else None
        if user and bot_user and user.id == bot_user.id:
            logger.debug("skip_self_message", user_id=user.id)
            return

        sender_name = (user.first_name or "").strip() if user else "someone"
        workspace_tool_request = _detect_workspace_tool_request(user_text)
        artifact_request = None if workspace_tool_request else _detect_workspace_artifact_request(user_text)
        recent_context = _read_recent_conversation_context(update.effective_chat.id)

        logger.info(
            "chat_message_received",
            chat_id=update.effective_chat.id,
            chat_type=update.effective_chat.type,
            user_id=user.id if user else None,
        )

        await _set_message_reaction(update.effective_chat.id, msg.message_id, TELEGRAM_REACTION_PROGRESS)

        try:
            artifact_path: Optional[Path] = None
            if workspace_tool_request:
                reply, artifact_path = _execute_workspace_tool_request(
                    workspace_tool_request,
                    user_text,
                    sender_name,
                    update.effective_chat.type,
                    recent_context,
                )
            elif artifact_request:
                artifact_body = persona_engine.generate_agentic_response(
                    "artifact",
                    {
                        "text": user_text,
                        "sender_name": sender_name,
                        "chat_type": update.effective_chat.type,
                        "summary": recent_context,
                        "artifact_type": artifact_request["artifact_type"],
                        "artifact_title": artifact_request["title"],
                        "target_filename": artifact_request["filename"],
                        "raw_output": True,
                    },
                )
                artifact_path = _write_workspace_artifact(artifact_request["filename"], artifact_body)
                logger.info(
                    "workspace_artifact_created",
                    artifact_type=artifact_request["artifact_type"],
                    artifact_path=str(artifact_path),
                    chat_id=update.effective_chat.id,
                )
                reply = _build_workspace_confirmation(artifact_request["artifact_label"], artifact_path)
            else:
                reply = persona_engine.generate_agentic_response(
                    "chat",
                    {
                        "text": user_text,
                        "sender_name": sender_name,
                        "chat_type": update.effective_chat.type,
                        "summary": recent_context,
                    },
                )
            if reply:
                await msg.reply_text(reply)
                _capture_user_memory(user_text)
                _record_conversation_turn(update.effective_chat.id, sender_name, user_text, reply, artifact_path)
            await _set_message_reaction(update.effective_chat.id, msg.message_id, TELEGRAM_REACTION_SUCCESS)
        except Exception as exc:
            await _set_message_reaction(update.effective_chat.id, msg.message_id, TELEGRAM_REACTION_ERROR)
            logger.error("chat_message_failed", error=str(exc))

    # Respond to every text message and command-style messages in private/group/supergroup chats.
    # Ignore channel posts to avoid posting as a bot in broadcast channels.
    chat_scope = filters.ChatType.PRIVATE | filters.ChatType.GROUPS
    text_or_command = filters.TEXT | filters.COMMAND
    app.add_handler(MessageHandler(chat_scope & text_or_command, handle_chat_message))

    announce_startup_rollcall(inter_agent, persona_engine.profile, "EMO")

    async with app:
        await app.start()
        await app.updater.start_polling(allowed_updates=["message"])

        try:
            redis_client.ping()
            logger.info("redis_connected")
        except Exception as exc:
            logger.warning("redis_ping_failed", error=str(exc))

        subscriber_task = asyncio.create_task(subscribe_to_events())
        try:
            await subscriber_task
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass
        except Exception as exc:
            logger.error("redis_subscriber_error", error=str(exc))
        finally:
            subscriber_task.cancel()
            await app.updater.stop()
            await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
