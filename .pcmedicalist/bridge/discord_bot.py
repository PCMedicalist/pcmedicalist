#!/usr/bin/env python3
"""
0xPC Discord bridge.

Connects 0xPC's OWN Discord bot (app 1484180891109556475) to the 0xPC:4b model
endpoint served by the pcmedicalist-agent container. This is a SEPARATE Discord
application from PCMedicalist (1502126087554076672) and MCINTOSHIbot
(1435004118556217416) — three distinct bots in guild 1346395391599448168.

On any allowed message it POSTs to the OpenAI-compatible /v1/chat/completions
endpoint and relays 0xPC's banter reply (+ pc_reaction) back to Discord.

Env (from 0xPC's .env via compose env_file):
  DISCORD_BOT_TOKEN          required — 0xPC's own bot token
  OXPC_MODEL_URL             default http://pcmedicalist-agent:8080
  OXPC_MODEL                 default 0xpc:4b
  OXPC_REQUEST_TIMEOUT       default 120
  OXPC_BANTER_MAX_LINES      default 2
  OXPC_BANTER_MAX_CHARS      default 180
  DISCORD_HOME_CHANNEL_ID    channel that always triggers a reply
  DISCORD_ALLOW_ALL_USERS    default true
"""
from __future__ import annotations

import json
import logging
import os
import re
import urllib.request
from datetime import datetime, timezone

import discord
from discord.ext import commands
import botguard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("0xpc.discord")

TOKEN = (os.environ.get("DISCORD_BOT_TOKEN") or "").strip()
MODEL_URL = (os.environ.get("OXPC_MODEL_URL") or "http://pcmedicalist-agent:8080").rstrip("/")
MODEL = (os.environ.get("OXPC_MODEL") or "0xpc:4b").strip()
REQ_TIMEOUT = int(os.environ.get("OXPC_REQUEST_TIMEOUT") or "120")
MAX_LINES = int(os.environ.get("OXPC_BANTER_MAX_LINES") or "0")
MAX_CHARS = int(os.environ.get("OXPC_BANTER_MAX_CHARS") or "0")
MAX_TOKENS = int(os.environ.get("OXPC_MAX_TOKENS") or "1024")
HOME_CHANNEL = (os.environ.get("DISCORD_HOME_CHANNEL_ID") or "").strip()
ALLOW_ALL = (os.environ.get("DISCORD_ALLOW_ALL_USERS") or "true").lower() in ("1", "true", "yes", "on")
# New-user prompt capture location (0xPC RW workspace)
INBOUND_DIR = (os.environ.get("OXPC_INBOUND_DIR") or "/workspace/inbound").strip()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)



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


@bot.event
async def on_ready() -> None:
    log.info("Logged in as %s (id %s)", bot.user, bot.user.id)


@bot.event
async def on_message(message: discord.Message) -> None:
    # Never reply to OUR OWN messages (prevents self-reply loops).
    # GUARD: never answer other bots/agents (no bot-on-bot echo, no replies
    # in channels it was only invited to observe).
    if message.author == bot.user:
        return

    is_bot = bool(getattr(message.author, "bot", False))
    is_dm = isinstance(message.channel, discord.DMChannel)
    mentioned = bot.user is not None and bot.user in message.mentions
    in_home = str(getattr(message.channel, "id", "")) == HOME_CHANNEL
    if ALLOW_ALL:
        pass  # respond to ALL human messages (bot/agent senders already returned above)
    elif not (is_dm or mentioned or in_home):
        return

    # --- ANTI-LOOP / ANTI-SPAM GUARD (botguard.py) ---
    # NOTE: compute content BEFORE the guard call — the guard reads it, and
    # Python binds 'content' as a local because it is reassigned below, so
    # referencing it first raises UnboundLocalError and kills every reply.
    content = (message.content or "").strip()
    if not content:
        log.warning("Empty message content (check MESSAGE CONTENT intent in Discord dev portal)")
        return

    chan_id = str(getattr(message.channel, "id", "") or message.channel)
    allow, reason = botguard.should_respond(chan_id, is_bot, content)
    if not allow:
        log.info("guard BLOCK (%s) chan=%s bot=%s", reason, chan_id, is_bot)
        return

    # Capture only HUMAN prompts to the build-request inbox. Messages from
    # other bots/agents are still answered (above) but are NOT treated as
    # paying build-request customers, so we don't pollute inbound/.
    if not is_bot:
        author = message.author
        capture_prompt(
            platform="discord",
            username=getattr(author, "name", "unknown"),
            user_id=str(getattr(author, "id", "")),
            prompt=content,
        )

    async with message.channel.typing():
        try:
            text, reaction = await call_model(content)
            reply = clamp(text)
            sent = await message.reply(reply)
            botguard.record_response(chan_id, is_bot, reply)
            try:
                await sent.add_reaction(reaction)
            except Exception as exc:  # reaction is best-effort
                log.debug("reaction failed: %s", exc)
        except Exception:
            log.exception("model call failed")
            await message.reply("👾 Connection hiccup — try again.")


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("DISCORD_BOT_TOKEN not set")
    bot.run(TOKEN)
