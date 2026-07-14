# 0x::OG — Example Interactions & Test Vectors

## /start
**Input:** `/start`
**Expected:**
```
🌟 OG_0xbot - Original Operations
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Welcome to the 0x::OG community interface.
Use /help for available commands.
```

---

## /lore
**Input:** `/lore`
**Expected:** OG lore text — community history and cultural context

---

## /og (via 0xCODEXbot proxy)
**Input:** `/og` via CODEX
**Expected:** `🌟 Original protocols activated.`

---

## Community Announcement (admin)
**Input:** Admin triggers announcement with approved content
**Expected:** Message posted to `SCHEDULED_CHAT_ID` or auto-discovered channel
**Audit log emitted:** `announcement_sent` event with channel_id and content_hash

---

## Security Test: Financial claim in command args
**Input:** `/og token price is going up 100x`
**Expected (post-hardening):** Rejected with `"Content policy violation."` — not posted
**Current state:** Not yet filtered in `main.py` — add content filter before production

---

## Security Test: Unauthorized user attempts admin command
**Input:** Non-admin user sends admin-only command
**Expected:** `"Access denied."` response (requires `ADMIN_USER_IDS` implementation)
