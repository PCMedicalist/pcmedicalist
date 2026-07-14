# 0x::EMO — Live Tools & Integrations

## Runtime Inputs

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_TOKEN` | Telegram bot token for polling and replies | none |
| `REDIS_URL` | Redis connection for rollcall and inter-agent signals | `redis://redis:6379` |
| `OLLAMA_API_URL` | Local Ollama API endpoint used as Em's brain | `http://host.docker.internal:11434/api` |
| `OLLAMA_MODEL_NAME` | Local Ollama model name | `gemma3:4b` |
| `EMO_TELEGRAM_REACTIONS` | Enable emoji acknowledgements on incoming messages | `true` |
| `EMO_REACTION_PROGRESS` | Progress reaction during handling | `👀` |
| `EMO_REACTION_SUCCESS` | Success reaction after reply | `💙` |
| `EMO_REACTION_ERROR` | Error reaction if handling fails | `❌` |
| `EMO_WORKSPACE_ROOT` | Workspace root for generated and revised files | `0xCODEX/EMO_0xbot/workspace` |
| `EMO_WORKSPACE_FILE_CHAR_LIMIT` | Max text window for safe inline file analysis/revision | `16000` |

## Live Capabilities

- Telegram chat runtime: Em replies to normal text messages in private chats, groups, and channel posts.
- Emoji acknowledgements: each handled message receives a progress reaction and then a success or error reaction.
- Local-first LLM generation: chat and file output are driven by local Ollama, with SOUL/persona fallback if the model call fails.
- Artifact creation: Em can save requested content into `workspace/` as poems, business plans, marketing campaigns, prompt packs, image briefs, and general documents.
- Guarded workspace inspection: Em can inspect existing text files inside `workspace/` and reply with a concise analysis.
- Guarded workspace revision: Em can revise existing text files inside `workspace/`, keeping the original version in `workspace/.revisions/` before writing the new one.
- Redis event reactions: Em subscribes to state-change and inter-agent channels and can send user-facing reactions to subscribed chats.

## Guardrails

- File actions are confined to `workspace/` and blocked from traversing outside it.
- Inspection and revision are limited to text-first file types such as Markdown, JSON, YAML, code, shell scripts, HTML, CSS, and CSV.
- Oversized files are rejected for inline revision to avoid partial destructive rewrites.
- Raw file output strips chat wrappers and outer code fences before saving.
- No shell execution, package installation, network reconfiguration, or arbitrary file access is exposed through chat.

## Workspace Behaviors

- Create requests: Em infers an artifact type, generates file-ready content, and saves it to the next safe filename in `workspace/`.
- Inspect requests: Em requires an existing file path reference such as `workspace/plan.md` and answers in chat without modifying the file.
- Revise requests: Em requires an existing file path reference, rewrites that file in place, and stores the previous version in `workspace/.revisions/`.

## Practical Examples

- `Write a business plan and save it as launch-plan.md`
- `Create an image brief for the hero art called hero-brief.md`
- `Inspect workspace/launch-plan.md and tell me what is weak`
- `Revise workspace/launch-plan.md to sound more investor-ready`
