"""Provider abstraction for LLM calls used by the persona engine.

Exports:
  generate_text(...) -> str

Supports providers: 'ollama', 'openai', and 'github-copilot'. Uses `httpx` for HTTP calls
and falls back to returning helpful error messages on failure.
"""
from typing import Optional
import json
import os

import httpx

try:
    import openai
except Exception:
    openai = None


def generate_text(
    provider: str,
    system_prompt: str,
    user_prompt: str,
    model: str,
    temperature: float = 0.3,
    ollama_api_url: Optional[str] = None,
    ollama_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    timeout: int = 120,
) -> str:
    provider = (provider or "").strip().lower()
    if provider == "ollama":
        return _call_ollama(system_prompt, user_prompt, model, temperature, ollama_api_url, ollama_api_key, timeout)
    if provider == "openai":
        return _call_openai(system_prompt, user_prompt, model, temperature, openai_api_key)
    raise ValueError(f"Unsupported LLM provider: {provider}")


def _call_ollama(system: str, user: str, model: str, temperature: float, api_url: Optional[str], api_key: Optional[str], timeout: int) -> str:
    if not api_url:
        raise ValueError("OLLAMA API URL is required for provider 'ollama'")
    url = api_url.rstrip("/") + "/generate"
    prompt = (system or "") + "\n\n" + (user or "")
    # Raise token cap (was 512 -> truncated persona replies). Keep a generous
    # upper bound so long SOUL-driven responses are not cut mid-sentence.
    # keep_alive holds the model in VRAM to avoid the ~30s cold-load penalty.
    payload = {
        "model": model or "",
        "prompt": prompt,
        "temperature": float(temperature or 0.0),
        "max_tokens": 2048,
        "keep_alive": "5m",
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        # Ollama may return plain text or JSON; prefer text body.
        text = resp.text
        # If it's JSON with a 'response' field, try to extract the textual response.
        try:
            j = resp.json()
            # Common fields could vary; try several heuristics.
            if isinstance(j, dict):
                for key in ("response", "text", "content", "result"):
                    if key in j and isinstance(j[key], str):
                        return j[key]
                # If 'choices' present (OpenAI-like), join them
                if "choices" in j and isinstance(j["choices"], list) and j["choices"]:
                    first = j["choices"][0]
                    if isinstance(first, dict):
                        return first.get("text") or first.get("message", {}).get("content", json.dumps(first))
        except Exception:
            pass
        return text
    except Exception as e:
        return f"ERROR (ollama): {e}"


def _call_openai(
    system: str, user: str, model: str, temperature: float, api_key: Optional[str]
) -> str:
    if openai is None:
        raise RuntimeError("openai package not available in environment")
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key required for provider 'openai'")
    openai.api_key = api_key
    messages = [
        {"role": "system", "content": system or ""},
        {"role": "user", "content": user or ""},
    ]
    try:
        resp = openai.ChatCompletion.create(model=model, messages=messages, temperature=float(temperature or 0.0), max_tokens=2048)
        if resp and getattr(resp, "choices", None):
            choice = resp.choices[0]
            # Newer responses may nest message.content
            if hasattr(choice, "message") and isinstance(choice.message, dict):
                return choice.message.get("content", "")
            return getattr(choice, "text", "") or ""
        return ""
    except Exception as e:
        return f"ERROR (openai): {e}"


import os
import time
from typing import Optional

import httpx


def _normalize_ollama_base(api_url: str) -> str:
    base = (api_url or "").strip()
    if not base:
        return "http://host.docker.internal:11435/api"
    if base.endswith("/"):
        base = base[:-1]
    if not base.endswith("/api"):
        base = f"{base}/api"
    return base


def generate_with_ollama(
    system_prompt: str,
    user_prompt: str,
    model: str,
    temperature: float,
    api_url: str,
    api_key: Optional[str] = None,
    timeout_seconds: float = 120.0,
    max_retries: int = 3,
) -> str:
    """Generate text from an Ollama endpoint with retries."""
    url = f"{_normalize_ollama_base(api_url)}/chat"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # keep_alive holds the model in VRAM to avoid the ~30s cold-load penalty
    # that caused truncated/template-fallback replies. options.num_predict is
    # the /chat equivalent of max_tokens; raised from the legacy 512 cap.
    payload = {
        "model": model,
        "stream": False,
        "keep_alive": "5m",
        "options": {"temperature": float(temperature), "num_predict": 2048},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    last_error: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                resp = client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                msg = data.get("message", {})
                content = msg.get("content") if isinstance(msg, dict) else None
                if not content:
                    content = data.get("response")
                return str(content or "").strip()
        except Exception as exc:
            last_error = exc
            if attempt >= max_retries:
                break
            sleep_s = min(0.8 * (2 ** (attempt - 1)), 5.0)
            time.sleep(sleep_s)

    raise RuntimeError(f"Ollama request failed: {last_error}")


def generate_with_openai(
    system_prompt: str,
    user_prompt: str,
    model: str,
    temperature: float,
    api_key: Optional[str] = None,
    max_retries: int = 3,
) -> str:
    """Generate text from OpenAI with retries (sync client)."""
    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError(f"OpenAI package unavailable: {exc}") from exc

    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=key)
    last_error: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=float(temperature),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return str(response.choices[0].message.content or "").strip()
        except Exception as exc:
            last_error = exc
            if attempt >= max_retries:
                break
            sleep_s = min(0.8 * (2 ** (attempt - 1)), 5.0)
            time.sleep(sleep_s)

    raise RuntimeError(f"OpenAI request failed: {last_error}")


def generate_text(
    provider: str,
    system_prompt: str,
    user_prompt: str,
    model: str,
    temperature: float,
    ollama_api_url: str,
    ollama_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
) -> str:
    """Provider router for LLM text generation."""
    p = (provider or "").strip().lower()
    if p == "ollama":
        return generate_with_ollama(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            temperature=temperature,
            api_url=ollama_api_url,
            api_key=ollama_api_key,
        )
    if p == "openai":
        return generate_with_openai(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            temperature=temperature,
            api_key=openai_api_key,
        )
    # Support GitHub Copilot as an OpenAI-compatible provider if a Copilot token is available.
    if p in ("github-copilot", "copilot", "github_copilot"):
        # Prefer an explicit Copilot env var, then fall back to provided openai_api_key
        copilot_key = os.getenv("COPILOT_GITHUB_TOKEN") or os.getenv("GITHUB_COPILOT_TOKEN") or openai_api_key or os.getenv("OPENAI_API_KEY")
        return generate_with_openai(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            temperature=temperature,
            api_key=copilot_key,
        )
    raise RuntimeError(f"Unsupported LLM provider: {provider}")
