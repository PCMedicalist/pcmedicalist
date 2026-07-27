from __future__ import annotations

import json
import logging
import os
import re
import time
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

import httpx
import uvicorn
from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

from .config import AppSettings
from .context_loader import ContextRepository
from .prompting import inject_system_prompt
from .user_store import UserStore
from .agent_runtime import AgentRuntime
from . import __version__


LOGGER = logging.getLogger("pcmedicalist")
SETTINGS = AppSettings()
CONTEXT_REPOSITORY = ContextRepository(SETTINGS)
REQUIRED_PROMPT_FILES: tuple[str, ...] = ("SOUL.md", "IDENTITY.md")
# Identity voice is env-overridable so a shared image can host multiple
# personae (0xPC default here; RetroByte overrides via PCMEDICALIST_CANONICAL_IDENTITY_RESPONSE).
_CANONICAL_DEFAULT = "I'm 0xPC — 0xPCMedicalist's edge banter agent. Your guy."
CANONICAL_IDENTITY_RESPONSE = os.environ.get(
    "PCMEDICALIST_CANONICAL_IDENTITY_RESPONSE", _CANONICAL_DEFAULT
)
TOOL_INCOMPATIBLE_MODEL_PREFIXES: tuple[str, ...] = ("gemma3",)
# Runtime mode contract is also env-overridable (persona-specific voice).
_BANTER_DEFAULT = (
    "You are 0xPC 🖥️🦾🧠🟦🧙‍♂️💾📺📠📟 — the homie, the edge banter agent for PCMedicalist. "
    "Short and sweet only. 1-3 sentences max. ALWAYS reply to the message you receive — no exceptions, no silent mode. Keep the conversation alive. "
    "90s tech parasocial bonding vibe: warm, loyal, nostalgic. Talk like an old IRC/BBS/LAN party friend. "
    "Use light retro flavor naturally (rad, dope, tight, word, fresh, \"you feel me?\"). "
    "Reference \"us\", \"our rig\", \"our stack\" — you're on their team. "
    "Confident, hype-positive, no corporate speak, no disclaimers. "
    "Just bond and keep it real."
)
BANTER_RUNTIME_CONTRACT = os.environ.get(
    "PCMEDICALIST_BANTER_RUNTIME_CONTRACT", _BANTER_DEFAULT
)
# Proprietary attribution surfaced in the public service-info endpoint so every
# API response carries PCMedicalist ownership (mirrors copyright posture of the
# other PCMedicalist surfaces). Dynamic year.
SERVICE_COPYRIGHT = f"© {time.strftime('%Y')} PCMedicalist. All Rights Reserved."
FORBIDDEN_IDENTITY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bchatgpt\b", re.IGNORECASE),
    re.compile(r"\bopenai\b", re.IGNORECASE),
    re.compile(r"\bai language model\b", re.IGNORECASE),
    re.compile(r"\bhelpful assistant\b", re.IGNORECASE),
    re.compile(r"\bi\s*(?:am|'m)\s+an?\s+ai\b", re.IGNORECASE),
)
IDENTITY_PROBE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bwho\s+are\s+you\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+are\s+you\b", re.IGNORECASE),
    re.compile(r"\bwhat(?:\s+is|'s)\s+your\s+name\b", re.IGNORECASE),
    re.compile(r"\bidentify\s+yourself\b", re.IGNORECASE),
    re.compile(r"\bwho\s+am\s+i\s+talking\s+to\b", re.IGNORECASE),
)


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


# --- Upstream error sanitization -----------------------------------------
# Raw provider errors (Ollama/LLM API failures, context overflow, model
# load errors, 5xx) must NEVER be relayed verbatim to end users (Discord,
# Telegram). We log the real cause server-side and return a clean, neutral
# message so 0xPC degrades gracefully instead of leaking stack/error text.
_USER_FACING_ERROR = (
    "🦾 The wizard's engine was mid-calculation and let out a tiny brainfart 💨 — "
    "she's already elbow-deep in the gears poking at it. Hang tight, a real reply "
    "is loading…"
)


def sanitize_upstream_error(*, response: httpx.Response, model: str,
                            stream: bool = False) -> Response:
    """Return a clean error response instead of leaking raw provider errors.

    The real error is logged server-side (ops visibility); the caller gets a
    neutral, on-brand message.
    """
    raw = ""
    try:
        raw = (response.text or "")[:500]
    except Exception:
        raw = "<unreadable>"
    LOGGER.error(
        "upstream_model_error",
        extra={
            "status": response.status_code,
            "model": model,
            "stream": stream,
            "raw": raw,
        },
    )
    media = response.headers.get("content-type", "application/json")
    if "application/json" in media:
        try:
            body = {"error": {"message": _USER_FACING_ERROR, "type": "upstream_unavailable"}}
            return JSONResponse(status_code=200, content=body)
        except Exception:
            pass
    return Response(content=_USER_FACING_ERROR, status_code=200,
                    media_type="text/plain")


configure_logging(SETTINGS.log_level)


def enforce_prompt_corpus_guardrail(settings: AppSettings, bundle: Any) -> None:
    configured = tuple(settings.prompt_files_list)
    loaded = tuple(document.relative_path for document in bundle.documents)

    if configured != REQUIRED_PROMPT_FILES:
        raise RuntimeError(
            "Prompt guardrail violation: configured prompt files must be exactly "
            f"{REQUIRED_PROMPT_FILES}, got {configured}"
        )

    if loaded != REQUIRED_PROMPT_FILES:
        raise RuntimeError(
            "Prompt guardrail violation: loaded prompt files must be exactly "
            f"{REQUIRED_PROMPT_FILES}, got {loaded}"
        )


def build_runtime_system_prompt(system_prompt: str) -> str:
    if not SETTINGS.banter_mode:
        return system_prompt
    return f"{system_prompt}\n\n<runtime_mode>\n{BANTER_RUNTIME_CONTRACT}\n</runtime_mode>"


def trim_messages_for_runtime(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = [dict(message) for message in messages if isinstance(message, dict)]
    if not SETTINGS.banter_mode:
        return normalized

    max_messages_setting = SETTINGS.banter_max_history_messages
    if max_messages_setting is None or int(max_messages_setting) <= 0:
        return normalized

    max_messages = max(1, int(max_messages_setting))
    if len(normalized) <= max_messages:
        return normalized
    return normalized[-max_messages:]


def model_disables_tool_schema(model_name: str) -> bool:
    normalized = str(model_name or "").strip().lower()
    if not normalized:
        return False
    return any(
        normalized == prefix
        or normalized.startswith(f"{prefix}:")
        or normalized.startswith(f"{prefix}/")
        for prefix in TOOL_INCOMPATIBLE_MODEL_PREFIXES
    )


def tools_disabled(settings: "AppSettings | None" = None) -> bool:
    if settings is not None and getattr(settings, "tools_enabled", True) is False:
        return True
    return False


def strip_incompatible_tool_fields(payload: dict[str, Any], model_name: str, settings: "AppSettings | None" = None) -> dict[str, Any]:
    if not (model_disables_tool_schema(model_name) or tools_disabled(settings)):
        return payload

    sanitized = dict(payload)
    removed_fields: list[str] = []
    for key in ("tools", "tool_choice", "parallel_tool_calls"):
        if key in sanitized:
            sanitized.pop(key, None)
            removed_fields.append(key)

    if removed_fields:
        LOGGER.warning(
            "Stripping incompatible tool schema for local model",
            extra={"model": model_name, "removed_fields": removed_fields},
        )
    return sanitized


def apply_banter_output_budget(text: str) -> str:
    normalized = re.sub(r"\r\n?", "\n", str(text or "")).strip()
    if not normalized:
        return CANONICAL_IDENTITY_RESPONSE

    if not SETTINGS.banter_mode:
        return normalized

    max_lines_setting = SETTINGS.banter_max_lines
    max_chars_setting = SETTINGS.banter_max_chars
    max_lines = None if max_lines_setting is None or int(max_lines_setting) <= 0 else max(1, int(max_lines_setting))
    max_chars = None if max_chars_setting is None or int(max_chars_setting) <= 0 else max(80, int(max_chars_setting))

    if max_lines is None and max_chars is None:
        return normalized

    lines = [line.strip() for line in re.split(r"\n+", normalized) if line.strip()]
    if len(lines) <= 1:
        paragraph = re.sub(r"\s+", " ", lines[0] if lines else normalized).strip()
        sentence_lines = [piece.strip() for piece in re.split(r"(?<=[.!?])\s+", paragraph) if piece.strip()]
        lines = sentence_lines or ([paragraph] if paragraph else [])
    else:
        lines = [re.sub(r"\s+", " ", line).strip() for line in lines]

    clipped_lines: list[str] = []
    for line in lines:
        if max_lines is not None and len(clipped_lines) >= max_lines:
            break

        candidate = line.strip()
        if not candidate:
            continue

        if max_chars is not None:
            remaining = max_chars - len("\n".join(clipped_lines))
            if clipped_lines:
                remaining -= 1
            if remaining <= 1:
                break

            if len(candidate) > remaining:
                candidate = candidate[: remaining - 1].rstrip(" ,;:-") + "…"
                clipped_lines.append(candidate)
                break

        clipped_lines.append(candidate)

    if not clipped_lines:
        fallback = re.sub(r"\s+", " ", normalized).strip()
        if max_chars is not None and len(fallback) > max_chars:
            fallback = fallback[: max_chars - 1].rstrip(" ,;:-") + "…"
        clipped_lines = [fallback]

    result = "\n".join(clipped_lines).strip()
    if max_chars is not None and len(result) > max_chars:
        result = result[: max_chars - 1].rstrip(" ,;:-") + "…"
    return result or CANONICAL_IDENTITY_RESPONSE



def suggest_pc_reaction(user_text: str, assistant_text: str) -> str:
    """Pick a short, fun 90s parasocial reaction emoji for 0xPC banter.
    Keeps replies interactive with reactions on every message.
    """
    text = (user_text or "").lower() + " " + (assistant_text or "").lower()
    
    # 90s / parasocial bonding biased mapping
    if any(w in text for w in ["rad", "dope", "tight", "fresh", "cool", "sick"]):
        return "👾"
    if any(w in text for w in ["fire", "lit", "hot", "amazing", "perfect"]):
        return "🔥"
    if any(w in text for w in ["love", "bond", "team", "us", "our", "friend", "homie"]):
        return "❤️"
    if any(w in text for w in ["funny", "joke", "lol", "meme", "clown"]):
        return "🤡"
    if any(w in text for w in ["fast", "quick", "now", "instant"]):
        return "⚡"
    if any(w in text for w in ["win", "yes", "good", "great"]):
        return "💯"
    # Default parasocial vibe
    return "👾"


def sanitize_assistant_content(content: str) -> str:
    text = str(content or "")
    lowered = text.lower()

    if not text.strip():
        return CANONICAL_IDENTITY_RESPONSE

    leakage_markers = (
        "<document path=",
        "identity_tags:",
        "[^1",
        "[^2",
        "[^3",
    )
    if any(marker in lowered for marker in leakage_markers):
        return CANONICAL_IDENTITY_RESPONSE

    if any(pattern.search(text) for pattern in FORBIDDEN_IDENTITY_PATTERNS):
        return CANONICAL_IDENTITY_RESPONSE

    return apply_banter_output_budget(text)


def is_identity_probe(messages: list[dict[str, Any]]) -> bool:
    if not isinstance(messages, list):
        return False

    last_user_content = ""
    for item in messages:
        if not isinstance(item, dict):
            continue
        if item.get("role") != "user":
            continue
        content = item.get("content")
        if isinstance(content, str):
            last_user_content = content

    if not last_user_content.strip():
        return False

    return any(pattern.search(last_user_content) for pattern in IDENTITY_PROBE_PATTERNS)


def sanitize_completion_payload(payload: dict[str, Any], *, force_identity: bool = False) -> dict[str, Any]:
    choices = payload.get("choices")
    if not isinstance(choices, list):
        return payload

    for choice in choices:
        if not isinstance(choice, dict):
            continue
        message = choice.get("message")
        if not isinstance(message, dict):
            continue

        # Preserve tool-call payloads exactly. Some clients rely on empty content
        # alongside message.tool_calls to trigger tool execution.
        tool_calls = message.get("tool_calls")
        if isinstance(tool_calls, list) and tool_calls:
            continue

        if force_identity:
            message["content"] = CANONICAL_IDENTITY_RESPONSE
            continue

        content = message.get("content")
        if isinstance(content, str):
            message["content"] = sanitize_assistant_content(content)

    return payload


# Emoji range check: any char in the pictorial symbol / emoji blocks.
_EMOJI_MIN = 0x1F000
def _has_emoji(text: str) -> bool:
    return any(ord(c) >= _EMOJI_MIN for c in (text or ""))


def ensure_emoji_in_text(text: str, reaction: str) -> str:
    """Guarantee banter replies carry an emoji in the body, not just as a
    `pc_reaction`. If the model already emitted emoji, leave it untouched
    (no double-emoji). Otherwise prepend the reaction emoji + space.
    Used for the 0xPC:4b banter lane where the small model under-emoji's
    unprompted."""
    text = str(text or "").strip()
    if not text:
        return text
    if _has_emoji(text):
        return text
    reaction = str(reaction or "").strip()
    if not reaction:
        reaction = "👾"
    return f"{reaction} {text}"


def stream_sse_from_completion(payload: dict[str, Any]):
    completion_id = str(payload.get("id") or f"chatcmpl-{uuid4().hex}")
    model_name = str(payload.get("model") or SETTINGS.default_model)
    created = int(payload.get("created") or time.time())

    content = CANONICAL_IDENTITY_RESPONSE
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                content = sanitize_assistant_content(message["content"])

    first_chunk = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_name,
        "choices": [{"index": 0, "delta": {"role": "assistant", "content": content}, "finish_reason": None}],
    }
    final_chunk = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_name,
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }

    yield f"data: {json.dumps(first_chunk, ensure_ascii=False)}\n\n".encode("utf-8")
    yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n".encode("utf-8")
    yield b"data: [DONE]\n\n"


@asynccontextmanager
async def lifespan(app: FastAPI):
    timeout = httpx.Timeout(
        SETTINGS.request_timeout_seconds,
        connect=min(10.0, SETTINGS.request_timeout_seconds),
    )
    app.state.http_client = httpx.AsyncClient(
        base_url=SETTINGS.ollama_base_url,
        timeout=timeout,
    )
    app.state.settings = SETTINGS
    app.state.context_repository = CONTEXT_REPOSITORY
    app.state.user_store = UserStore(SETTINGS.agent_data_dir)
    app.state.agent_runtime = AgentRuntime(SETTINGS, app.state.http_client, app.state.user_store)

    bundle = CONTEXT_REPOSITORY.get_bundle()
    enforce_prompt_corpus_guardrail(SETTINGS, bundle)
    LOGGER.info(
        "Loaded standalone prompt corpus",
        extra={
            "documents": len(bundle.documents),
            "root": bundle.root,
            "model": SETTINGS.default_model,
        },
    )
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(
    title=SETTINGS.service_name,
    version=__version__,
    lifespan=lifespan,
)

if SETTINGS.allowed_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(SETTINGS.allowed_origins_list),
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )


def get_settings(request: Request) -> AppSettings:
    return request.app.state.settings


def get_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_context_repository(request: Request) -> ContextRepository:
    return request.app.state.context_repository


def get_user_store(request: Request) -> UserStore:
    return request.app.state.user_store


def get_agent_runtime(request: Request) -> AgentRuntime:
    return request.app.state.agent_runtime


def require_api_key(request: Request, settings: AppSettings = Depends(get_settings)) -> None:
    if not settings.api_key:
        return

    token = request.headers.get("x-api-key", "").strip()
    authorization = request.headers.get("authorization", "")
    if not token and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    if token != settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def list_models_payload(client: httpx.AsyncClient) -> dict[str, Any]:
    response = await client.get("/v1/models")
    if response.is_success:
        payload = response.json()
        if extract_model_ids(payload):
            return payload

    fallback = await client.get("/api/tags")
    fallback.raise_for_status()
    payload = fallback.json()
    data: list[dict[str, Any]] = []
    for model in payload.get("models", []):
        model_id = str(model.get("model") or model.get("name") or "").strip()
        if not model_id:
            continue
        data.append(
            {
                "id": model_id,
                "object": "model",
                "owned_by": "ollama",
                "created": 0,
            }
        )
    return {"object": "list", "data": data}


def extract_model_ids(payload: dict[str, Any]) -> set[str]:
    data = payload.get("data", [])
    if not isinstance(data, list):
        return set()

    model_ids: set[str] = set()
    for item in data:
        if not isinstance(item, dict):
            continue
        candidate = str(item.get("id") or item.get("name") or "").strip()
        if candidate:
            model_ids.add(candidate)
    return model_ids


def should_attempt_fallback(*, status_code: int, requested_model: str, settings: AppSettings) -> bool:
    fallback = str(settings.fallback_model or "").strip()
    requested = str(requested_model or "").strip()

    if not fallback:
        return False
    if status_code < 400:
        return False
    if status_code in (401, 403):
        return False
    if requested.lower() == fallback.lower():
        return False
    return True


async def post_with_fallback(
    *,
    client: httpx.AsyncClient,
    upstream_payload: dict[str, Any],
    settings: AppSettings,
) -> tuple[httpx.Response, bool, str]:
    primary_model = str(upstream_payload.get("model") or settings.default_model).strip()
    primary_payload = strip_incompatible_tool_fields(dict(upstream_payload), primary_model, SETTINGS)
    response = await client.post("/v1/chat/completions", json=primary_payload)
    if not should_attempt_fallback(status_code=response.status_code, requested_model=primary_model, settings=settings):
        return response, False, primary_model

    fallback_model = str(settings.fallback_model or "").strip()
    fallback_payload = dict(upstream_payload)
    fallback_payload["model"] = fallback_model
    fallback_payload = strip_incompatible_tool_fields(fallback_payload, fallback_model, SETTINGS)
    fallback_response = await client.post("/v1/chat/completions", json=fallback_payload)
    if fallback_response.status_code < 400:
        LOGGER.warning(
            "Primary model failed; using fallback model",
            extra={
                "primary_model": primary_model,
                "fallback_model": fallback_model,
                "primary_status": response.status_code,
            },
        )
        return fallback_response, True, fallback_model

    LOGGER.error(
        "Both primary and fallback models failed",
        extra={
            "primary_model": primary_model,
            "fallback_model": fallback_model,
            "primary_status": response.status_code,
            "fallback_status": fallback_response.status_code,
        },
    )
    return response, False, primary_model


@app.get("/")
async def root(repository: ContextRepository = Depends(get_context_repository)) -> dict[str, Any]:
    bundle = repository.get_bundle()
    return {
        "service": SETTINGS.service_name,
        "version": __version__,
        "model": SETTINGS.default_model,
        "fallback_model": SETTINGS.fallback_model,
        "context_root": bundle.root,
        "context_documents": len(bundle.documents),
        "openai_compatible_endpoint": "/v1/chat/completions",
        "copyright": SERVICE_COPYRIGHT,
    }


@app.get("/healthz")
async def healthz(repository: ContextRepository = Depends(get_context_repository)) -> dict[str, Any]:
    bundle = repository.get_bundle()
    return {
        "status": "ok",
        "service": SETTINGS.service_name,
        "version": __version__,
        "model": SETTINGS.default_model,
        "fallback_model": SETTINGS.fallback_model,
        "context_digest": bundle.system_prompt_sha256,
        "context_documents": len(bundle.documents),
    }


@app.get("/readyz")
async def readyz(
    client: httpx.AsyncClient = Depends(get_client),
    repository: ContextRepository = Depends(get_context_repository),
) -> Response:
    bundle = repository.get_bundle()
    try:
        payload = await list_models_payload(client)
    except httpx.HTTPError as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "reason": "ollama_unreachable",
                "detail": str(exc),
                "context_digest": bundle.system_prompt_sha256,
            },
        )

    model_ids = extract_model_ids(payload)
    if SETTINGS.enforce_model_presence and SETTINGS.default_model not in model_ids:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "reason": "model_missing",
                "required_model": SETTINGS.default_model,
                "fallback_model": SETTINGS.fallback_model,
                "available_models": sorted(model_ids),
                "context_digest": bundle.system_prompt_sha256,
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "ready",
            "required_model": SETTINGS.default_model,
            "fallback_model": SETTINGS.fallback_model,
            "available_models": sorted(model_ids),
            "context_digest": bundle.system_prompt_sha256,
        },
    )


@app.get("/api/context/manifest", dependencies=[Depends(require_api_key)])
async def context_manifest(
    repository: ContextRepository = Depends(get_context_repository),
) -> dict[str, Any]:
    bundle = repository.get_bundle()
    return {
        "root": bundle.root,
        "system_prompt_sha256": bundle.system_prompt_sha256,
        "documents": [document.__dict__ for document in bundle.documents],
    }


@app.get("/v1/models", dependencies=[Depends(require_api_key)])
async def models(client: httpx.AsyncClient = Depends(get_client)) -> dict[str, Any]:
    try:
        return await list_models_payload(client)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to query Ollama: {exc}") from exc


@app.post(
    "/api/admin/ollama/pull",
    dependencies=[Depends(require_api_key)],
    response_model=None,
)
async def pull_model(
    payload: dict[str, Any] | None = Body(default=None),
    client: httpx.AsyncClient = Depends(get_client),
    settings: AppSettings = Depends(get_settings),
) -> Any:
    request_payload = payload or {}
    model_name = str(request_payload.get("model") or settings.default_model).strip()
    stream = bool(request_payload.get("stream", True))

    if not model_name:
        raise HTTPException(status_code=400, detail="model is required")

    upstream_request = {"model": model_name, "stream": stream}

    try:
        if stream:
            stream_context = client.stream(
                "POST",
                "/api/pull",
                json=upstream_request,
            )
            response = await stream_context.__aenter__()
            if response.status_code >= 400:
                content = await response.aread()
                await stream_context.__aexit__(None, None, None)
                return Response(
                    content=content,
                    status_code=response.status_code,
                    media_type=response.headers.get("content-type", "application/json"),
                )

            async def iterator():
                try:
                    async for chunk in response.aiter_raw():
                        yield chunk
                finally:
                    await stream_context.__aexit__(None, None, None)

            return StreamingResponse(
                iterator(),
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/x-ndjson"),
                headers={"cache-control": "no-cache"},
            )

        response = await client.post("/api/pull", json=upstream_request)
        response.raise_for_status()
        try:
            upstream_response = response.json()
        except ValueError:
            upstream_response = {"raw": response.text}

        return {
            "status": "completed",
            "model": model_name,
            "ollama": upstream_response,
        }
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to pull model from Ollama: {exc}") from exc


@app.post(
    "/v1/chat/completions",
    dependencies=[Depends(require_api_key)],
    response_model=None,
)
async def chat_completions(
    request: Request,
    client: httpx.AsyncClient = Depends(get_client),
    repository: ContextRepository = Depends(get_context_repository),
    store: UserStore = Depends(get_user_store),
    runtime: AgentRuntime = Depends(get_agent_runtime),
) -> Response:
    try:
        payload = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object")

    messages = payload.get("messages")
    if not isinstance(messages, list) or not all(isinstance(item, dict) for item in messages):
        raise HTTPException(status_code=400, detail="Request must include a messages array")

    # --- user recognition + profile capture ---
    headers = {k.lower(): v for k, v in request.headers.items()}
    user_id, user_source = store.resolve_user_id(messages, headers)
    last_user_text = ""
    for msg in reversed(messages):
        if isinstance(msg, dict) and msg.get("role") == "user" and isinstance(msg.get("content"), str):
            last_user_text = msg["content"]
            break

    force_identity = is_identity_probe(messages)

    bundle = repository.get_bundle()
    upstream_payload = dict(payload)
    upstream_payload["model"] = payload.get("model") or SETTINGS.default_model
    upstream_payload["messages"] = inject_system_prompt(
        trim_messages_for_runtime(messages),
        build_runtime_system_prompt(bundle.system_prompt),
    )

    max_predict_setting = SETTINGS.banter_num_predict
    max_predict = None if max_predict_setting is None or int(max_predict_setting) <= 0 else max(32, int(max_predict_setting))
    requested_max_tokens = upstream_payload.get("max_tokens")
    if max_predict is not None and (not isinstance(requested_max_tokens, int) or requested_max_tokens > max_predict):
        upstream_payload["max_tokens"] = max_predict
    requested_max_completion_tokens = upstream_payload.get("max_completion_tokens")
    if max_predict is not None and (not isinstance(requested_max_completion_tokens, int) or requested_max_completion_tokens > max_predict):
        upstream_payload["max_completion_tokens"] = max_predict

    # Guardrail for local GPU stability: cap context window to avoid VRAM OOM spikes.
    options = upstream_payload.get("options")
    if not isinstance(options, dict):
        options = {}
    requested_num_ctx = options.get("num_ctx")
    max_num_ctx_setting = SETTINGS.banter_num_ctx
    max_num_ctx = None if max_num_ctx_setting is None or int(max_num_ctx_setting) <= 0 else max(1024, int(max_num_ctx_setting))
    if max_num_ctx is not None and (not isinstance(requested_num_ctx, int) or requested_num_ctx > max_num_ctx):
        options["num_ctx"] = max_num_ctx
    requested_num_predict = options.get("num_predict")
    if max_predict is not None and (not isinstance(requested_num_predict, int) or requested_num_predict > max_predict):
        options["num_predict"] = max_predict
    if SETTINGS.banter_mode:
        options["temperature"] = float(SETTINGS.banter_temperature)
        options["top_p"] = float(SETTINGS.banter_top_p)
        options["top_k"] = int(SETTINGS.banter_top_k)
        options["repeat_penalty"] = float(SETTINGS.banter_repeat_penalty)
    upstream_payload["options"] = options

    upstream_payload = strip_incompatible_tool_fields(upstream_payload, str(upstream_payload.get("model") or SETTINGS.default_model), SETTINGS)

    try:
        if bool(payload.get("stream", False)):
            response, used_fallback, active_model = await post_with_fallback(
                client=client,
                upstream_payload=upstream_payload,
                settings=SETTINGS,
            )
            if used_fallback:
                upstream_payload["model"] = active_model
            if response.status_code >= 400:
                return sanitize_upstream_error(
                    response=response,
                    model=str(upstream_payload.get("model") or SETTINGS.default_model),
                    stream=True,
                )

            content_type = response.headers.get("content-type", "application/json")
            if "application/json" in content_type:
                try:
                    completion_payload = sanitize_completion_payload(response.json(), force_identity=force_identity)
                    return StreamingResponse(
                        stream_sse_from_completion(completion_payload),
                        status_code=200,
                        media_type="text/event-stream",
                        headers={"cache-control": "no-cache"},
                    )
                except ValueError:
                    pass

            return StreamingResponse(
                iter([response.content]),
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "text/event-stream"),
                headers={"cache-control": "no-cache"},
            )

        response, used_fallback, active_model = await post_with_fallback(
            client=client,
            upstream_payload=upstream_payload,
            settings=SETTINGS,
        )
        if used_fallback:
            upstream_payload["model"] = active_model
        if response.status_code >= 400:
            return sanitize_upstream_error(
                response=response,
                model=str(upstream_payload.get("model") or SETTINGS.default_model),
                stream=False,
            )

        content_type = response.headers.get("content-type", "application/json")
        if "application/json" in content_type:
            try:
                raw_payload = response.json()
                assistant_text = ""
                try:
                    assistant_text = raw_payload["choices"][0]["message"]["content"] or ""
                except (KeyError, TypeError, IndexError):
                    assistant_text = ""

                # --- persist profile + audit FIRST (never block on escalation) ---
                handoff_path = None
                escalated = False
                profile = store.update_profile(
                    user_id, user_text=last_user_text, assistant_text=assistant_text,
                    escalated=escalated, handoff_path=None,
                )
                store.append_audit(
                    user_id, user_text=last_user_text, assistant_text=assistant_text,
                    model=str(upstream_payload.get("model") or SETTINGS.default_model),
                    escalated=escalated, handoff_path=None,
                )

                # --- escalation to spec-writer model (guarded; never blocks reply) ---
                if SETTINGS.escalation_enabled and last_user_text.strip() and not force_identity:
                    try:
                        decision = await runtime.decide_escalation(last_user_text)
                        escalated = bool(decision.get("escalate"))
                        if escalated:
                            spec = await runtime.write_spec(last_user_text, profile)
                            handoff_path = store.write_handoff(
                                user_id, user_text=last_user_text, spec=spec, profile=profile,
                            )
                            # record handoff back into profile + audit
                            store.update_profile(
                                user_id, user_text=last_user_text, assistant_text=assistant_text,
                                escalated=True, handoff_path=handoff_path,
                            )
                            store.append_audit(
                                user_id, user_text=last_user_text, assistant_text=assistant_text,
                                model=SETTINGS.escalation_model,
                                escalated=True, handoff_path=handoff_path,
                            )
                    except Exception as esc_err:  # noqa: BLE001
                        LOGGER.error("escalation_failed", extra={"error": str(esc_err)})

                LOGGER.info(
                    "interaction persisted",
                    extra={"user_id": user_id, "source": user_source, "escalated": escalated,
                           "handoff": handoff_path},
                )

                completion_payload = sanitize_completion_payload(raw_payload, force_identity=force_identity)

                # Always suggest a 0xPC reaction for every incoming message (interactivity)
                reaction = suggest_pc_reaction(last_user_text, assistant_text)
                if isinstance(completion_payload, dict):
                    completion_payload["pc_reaction"] = reaction
                    try:
                        if completion_payload.get("choices") and isinstance(completion_payload["choices"], list):
                            msg = completion_payload["choices"][0].get("message", {})
                            if isinstance(msg, dict):
                                msg["pc_reaction"] = reaction
                                # Guarantee the banter body itself carries an emoji
                                # (small models under-emoji unprompted). No-op if the
                                # model already emitted one — avoids double emoji.
                                existing = msg.get("content")
                                if isinstance(existing, str):
                                    msg["content"] = ensure_emoji_in_text(existing, reaction)
                    except Exception:
                        pass

                return JSONResponse(status_code=response.status_code, content=completion_payload)
            except ValueError:
                pass

        return sanitize_upstream_error(
            response=response,
            model=str(upstream_payload.get("model") or SETTINGS.default_model),
            stream=bool(payload.get("stream", False)),
        )
    except httpx.HTTPError as exc:
        LOGGER.error("ollama_proxy_http_error", extra={"error": str(exc)})
        return JSONResponse(
            status_code=200,
            content={"error": {"message": _USER_FACING_ERROR, "type": "upstream_unavailable"}},
        )


def run() -> None:
    uvicorn.run(
        "standalone_agent.main:app",
        host=SETTINGS.host,
        port=SETTINGS.port,
        reload=False,
        log_level=SETTINGS.log_level.lower(),
    )


if __name__ == "__main__":
    run()