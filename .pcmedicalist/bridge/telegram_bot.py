#!/usr/bin/env python3
"""
0xPC Telegram bridge.

Connects 0xPC's OWN Telegram bot (@OxPClawbot) to the 0xPC:4b model endpoint
served by the pcmedicalist-agent container. Distinct from PCMedicalistBot and
@McIntoshibot — three separate bots.

Env (from 0xPC's .env via compose env_file):
  TELEGRAM_BOT_TOKEN         required — 0xPC's own Telegram bot token
  OXPC_MODEL_URL             default http://pcmedicalist-agent:8080
  OXPC_MODEL                 default 0xpc:4b
  OXPC_REQUEST_TIMEOUT       default 120
  OXPC_BANTER_MAX_LINES      default 2
  OXPC_BANTER_MAX_CHARS      default 180
  TELEGRAM_HOME_CHANNEL      chat id that always triggers a reply
  TELEGRAM_ALLOW_ALL_USERS   default true
"""
from __future__ import annotations

import json
import logging
import os
import re
import urllib.request
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import botguard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("0xpc.telegram")

TOKEN = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
MODEL_URL = (os.environ.get("OXPC_MODEL_URL") or "http://pcmedicalist-agent:8080").rstrip("/")
MODEL = (os.environ.get("OXPC_MODEL") or "0xpc:4b").strip()
REQ_TIMEOUT = int(os.environ.get("OXPC_REQUEST_TIMEOUT") or "120")
MAX_LINES = int(os.environ.get("OXPC_BANTER_MAX_LINES") or "0")
MAX_CHARS = int(os.environ.get("OXPC_BANTER_MAX_CHARS") or "0")
MAX_TOKENS = int(os.environ.get("OXPC_MAX_TOKENS") or "1024")
HOME_CHANNEL = (os.environ.get("TELEGRAM_HOME_CHANNEL") or "").strip()
ALLOW_ALL = (os.environ.get("TELEGRAM_ALLOW_ALL_USERS") or "true").lower() in ("1", "true", "yes", "on")
# New-user prompt capture location (0xPC RW workspace)
INBOUND_DIR = (os.environ.get("OXPC_INBOUND_DIR") or "/workspace/inbound").strip()



import asyncio
import concurrent.futures

def _blocking_call_model(user_text: str) -> tuple[str, str]:
    import json as _json
    import urllib.request as _urllib
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": user_text}],
        "stream": False,
        "max_tokens": MAX_TOKENS,
        "options": {"keep_alive": -1},
    }
    data = _json.dumps(payload).encode()
    last_err = None
    for attempt in range(2):
        try:
            req = _urllib.Request(
                MODEL_URL + "/v1/chat/completions",
                data=data,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with _urllib.urlopen(req, timeout=REQ_TIMEOUT) as resp:
                body = _json.loads(resp.read().decode())
            msg = (body.get("choices") or [{}])[0].get("message", {})
            text = (msg.get("content") or "").strip()
            reaction = (msg.get("pc_reaction") or "ð¾").strip() or "ð¾"
            return text, reaction
        except Exception as exc:
            last_err = exc
            log.warning("model call attempt %d failed: %s", attempt + 1, exc)
    raise RuntimeError(f"model call failed: {last_err}")

async def call_model(user_text: str) -> tuple[str, str]:
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return await loop.run_in_executor(ex, _blocking_call_model, user_text)


def clamp(text: str) -> str:
    if not text:
        return "👾 Here."
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if MAX_LINES > 0 and len(lines) > MAX_LINES:
        lines = lines[:MAX_LINES]
    text = "\n".join(lines)
    if MAX_CHARS > 0 and len(text) > MAX_CHARS:
        text = text[: MAX_CHARS - 1].rstrip(" ,;:-") + "…"
    return text


def capture_prompt(platform: str, username: str, user_id: str, prompt: str) -> None:
    """Persist a new-user prompt to the 0xPC workspace inbound/ for later build
    requests (watched by PCMedicalist after payment clears)."""
    try:
        os.makedirs(INBOUND_DIR, exist_ok=True)
        ts = datetime.now(timezone.utc).isoformat()
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", f"{ts}_{username}")[:120]
        path = os.path.join(INBOUND_DIR, f"{safe}.json")
        rec = {
            "platform": platform,
            "username": username,
            "user_id": user_id,
            "timestamp": ts,
            "prompt": prompt,
            "paid": False,
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=2)
        log.info("captured prompt -> %s", path)
    except Exception as exc:  # capture must never break the reply path
        log.warning("prompt capture failed: %s", exc)


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    user = update.effective_user
    # Per operator directive, 0xPC answers ALL messages including those from
    # other bots/agents — so we no longer skip user.is_bot here. (This restores
    # the prior setup.) We still record the source so capture can be gated below.
    is_bot = bool(user and getattr(user, "is_bot", False))
    chat_id = str(update.effective_chat.id) if update.effective_chat else ""
    if not ALLOW_ALL and chat_id != HOME_CHANNEL:
        return
    # Capture only HUMAN prompts to the build-request inbox. Bots/agents are
    # still answered but are NOT treated as paying build-request customers.
    is_bot = bool(user and getattr(user, "is_bot", False))
    if is_bot:
        return
    chat_id = str(update.effective_chat.id) if update.effective_chat else ""
    if not ALLOW_ALL and chat_id != HOME_CHANNEL:
        return

    # --- ANTI-LOOP / ANTI-SPAM GUARD (botguard.py) ---
    allow, reason = botguard.should_respond(chat_id, is_bot, update.message.text)
    if not allow:
        log.info("guard BLOCK (%s) chat=%s bot=%s", reason, chat_id, is_bot)
        return

    chat = update.effective_chat
    try:
        # show "typing…" while the model thinks (auto-refresh so it doesn't fade on cold loads)
        _stop = asyncio.Event()
        async def _typing():
            try:
                while not _stop.is_set() and chat is not None:
                    await context.bot.send_chat_action(chat_id=chat.id, action="typing")
                    await asyncio.sleep(3)
            except Exception:
                pass
        _t = asyncio.create_task(_typing())
        try:
            text, _reaction = await call_model(update.message.text)
            reply = clamp(text)
            await update.message.reply_text(reply)
            botguard.record_response(chat_id, is_bot, reply)
        finally:
            _stop.set()
            _t.cancel()
    except Exception:
        log.exception("model call failed")
        await update.message.reply_text("👾 Connection hiccup — try again.")


def main() -> None:
    if not TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN not set")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))
    log.info("0xPC Telegram bridge polling (model %s @ %s)", MODEL, MODEL_URL)
    app.run_polling()


if __name__ == "__main__":
    main()
