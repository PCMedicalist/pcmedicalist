# 0x::EMO — Autonomy Policy

## Autonomy Level

**Level 2 — Chat-First Assistant With Guarded Workspace Tools**

EMO is no longer publish-only. It responds directly in Telegram, acknowledges handled messages with emoji reactions, generates workspace artifacts, and can inspect or revise existing workspace files under a constrained path and file-type policy.

## Allowed Operations

- Poll Telegram and reply to ordinary user messages.
- Add Telegram emoji reactions during message handling.
- Use local Ollama as the primary generation engine, with SOUL/persona fallback if Ollama fails.
- Subscribe to Redis state-change and inter-agent channels and send user-facing reactions to subscribed chats.
- Create new files inside `workspace/` from natural-language requests.
- Inspect existing text files inside `workspace/` and summarize them back to the user.
- Revise existing text files inside `workspace/`, storing a backup in `workspace/.revisions/` first.
- Persist lightweight local memory in `workspace/memory/`.

## Forbidden Operations

- No file access outside `workspace/`.
- No destructive path traversal, arbitrary absolute-path reads, or parent-directory escapes.
- No binary-file rewriting through chat.
- No shell execution, package installation, container control, or arbitrary host commands from Telegram chat.
- No onchain actions, approvals, transfers, or other authority claims beyond Em's role.

## Operational Boundaries

- Workspace inspection and revision require an explicit file reference such as `workspace/plan.md`.
- Inline revision is limited to text-first files and a bounded prompt window.
- If a requested rewrite produces empty or unchanged output, Em refuses to overwrite the file.
- Revision history remains local in `workspace/.revisions/` so prior content is recoverable.

## Degradation Behavior

| Trigger | Response |
|---------|----------|
| Ollama request fails | Fall back to SOUL/persona generation without crashing the runtime |
| Telegram reaction call fails | Keep chat flow alive; log debug and continue |
| Workspace file outside policy | Refuse the action and explain the guardrail |
| Workspace file too large for safe inline revision | Refuse in-place rewrite and ask for a narrower slice |
| Redis event error | Log the error and keep the Telegram runtime alive |

## Review Cadence

Autonomy policy should be reviewed whenever EMO gains a new file operation, external integration, or broader execution surface.
