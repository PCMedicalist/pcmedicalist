# 0x::EMO — Live Memory Model

## Persistent Local Memory

EMO now stores its lightweight conversational memory on disk inside `workspace/memory/`.

| Path | Purpose |
|------|---------|
| `workspace/memory/conversation_log.jsonl` | Per-turn chat log used to recover recent context for the current chat only |
| `workspace/memory/dreams.md` | User statements that match dream / wish language |
| `workspace/memory/thoughts.md` | User statements that match idea / thought / remember language |
| `workspace/memory/vision.md` | User statements that match goal / mission / future language |

## How Conversation Context Works

- Each recorded turn stores `timestamp`, `chat_id`, `sender_name`, `user_text`, `reply_text`, and optionally the touched workspace file path.
- When Em generates a new reply, it only reads the most recent turns for the current `chat_id`.
- Cross-chat bleed is intentionally blocked; one chat's rolling context is not injected into another chat's prompt.

## File Revision History

- Rewritten workspace files are backed up into `workspace/.revisions/` before Em writes the new version.
- Backups are timestamped `.bak` files and remain local to the workspace mount.

## What Is Not Persisted By This Layer

- Binary attachments or non-text file contents.
- Full Redis event payload archives.
- Hidden reasoning or system-prompt text.
- Any files outside `workspace/`.

## Retention And Purge

- Memory files persist until you delete them.
- To clear conversation context, remove `workspace/memory/conversation_log.jsonl`.
- To clear categorized memory, remove or edit `dreams.md`, `thoughts.md`, and `vision.md`.
- To clear revision history, remove `workspace/.revisions/`.

## Privacy Notes

- The conversation log contains raw user and Em text for the recent-turn memory feature, but it is stored locally in the mounted workspace rather than in Redis.
- Memory capture is keyword-triggered and intentionally lightweight; it is not a full long-term knowledge base.
