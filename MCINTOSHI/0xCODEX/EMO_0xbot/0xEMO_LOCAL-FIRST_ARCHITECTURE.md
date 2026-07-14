# 🧠 0x::EMO — Local-First System Architecture

🎯 Objectives
Run on your desktop (GPU-accelerated when available)
Containerized microservices (clean isolation, reproducibility)
Low-latency reactions (sub-second for common paths)
Heavy generation offload (API/MCP fallback)
Strict persona enforcement (no drift, no “AI” leakage)
🧩 High-Level Topology
                ┌──────────────────────────────┐
                │   Social Connectors Layer    │
                │ Telegram | Discord | X       │
                └──────────────┬───────────────┘
                               │
                     ┌─────────▼─────────┐
                     │  Gateway API      │  (Node/TS)
                     │  (Auth + Routing) │
                     └─────────┬─────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼────────┐   ┌────────▼────────┐   ┌─────────▼────────┐
│ Signal Engine  │   │ Persona Kernel  │   │  Composer        │
│ (Python)       │   │ (TS + Rules)    │   │ (TS)             │
└───────┬────────┘   └────────┬────────┘   └─────────┬────────┘
        │                     │                      │
        └──────────────┬──────┴──────────────┬──────┘
                       │                     │
              ┌────────▼────────┐   ┌────────▼────────┐
              │ Asset Service   │   │ Generation Hub   │
              │ (Redis + FS)    │   │ (Python GPU)     │
              └────────┬────────┘   └────────┬────────┘
                       │                     │
                ┌──────▼──────┐       ┌──────▼─────────────┐
                │ Local Cache │       │ External APIs/MCP  │
                │ (Redis)     │       │ (Burst Compute)    │
                └─────────────┘       └────────────────────┘
🧱 Containerized Services (Docker Network)

1. Gateway API (Node.js / TypeScript)
Entry point for all events
Handles:
Webhooks (Telegram, Discord, X)
Auth + rate limiting
Routing to internal services

Stack:

Fastify (preferred over Express for perf)
Zod (schema validation)
pino (logging)
2. Signal Engine (Python)
Converts raw text → emotional signal vector

Models:

Lightweight sentiment model (local)
Optional: small transformer via Ollama

Output:

{
  "valence": 0.2,
  "arousal": 0.7,
  "intent": "celebrate"
}
3. Persona Kernel (TypeScript)
Deterministic rule engine (CRITICAL)

Responsibilities:

Apply IDENTITY/SOUL spec
Map signals → Em-state
Enforce canon rules

Why TS here?

Easier to maintain logic + constraints
Tight integration with frontend + gateway
4. Composer Service (TypeScript)
Builds final response:
selects asset
generates short text
decides format (sticker/GIF/audio)
5. Asset Service
Local registry of:
stickers
GIFs
clips
Indexed by tags

Storage:

File system + Redis index
6. Generation Hub (Python + GPU)

This is your power node.

Capabilities:
Image generation
Voice synthesis
Music generation
Suggested Stack:
🖼️ Images
Stable Diffusion (via:
AUTOMATIC1111 OR
ComfyUI (better for pipelines))
ControlNet (for consistency)
🔊 Voice
Coqui TTS (local)
Bark (expressive, experimental)
🎵 Music
Meta MusicGen (local)
Or API fallback for quality
7. External Burst Layer (API / MCP)

For heavy jobs:

High-res renders
long-form audio/music
batch jobs

Routing logic:

IF job_cost > threshold → send external
ELSE → local generation
⚙️ DevOps Stack
Container Orchestration
Docker Compose (start here)
Later: k3s (lightweight Kubernetes)
Observability
Prometheus (metrics)
Grafana (dashboards)
Loki (logs)

Track:

latency
generation time
error rates
engagement
Queue System (Important)
Redis Queue / BullMQ (Node)
Celery (Python alternative)

Used for:

async generation
retries
scheduling
Storage
Redis → hot cache
Postgres → metadata
Local FS / S3-compatible → assets
🎤 Voice + Music Pipeline
Voice Flow
Text → Persona Tone → TTS → Post-process → Deliver

Add:

slight reverb
stereo widening
subtle modulation (alien feel)
Music Flow
User Prompt → Style Map → MusicGen → Trim/Loop → Deliver
🧠 Model Strategy (Local First)
Use Ollama (fits your setup)

Run:

small LLMs for:
text generation (short responses)
fallback reasoning

Examples:

mistral / llama variants
qwen (you mentioned)
🔐 Persona Protection Layer

Add a middleware check before output:

if (response.includes("AI") || breaksCanon) {
  return fallbackEmResponse();
}

No exceptions.

🎛️ Frontend Control Panel (React + Vite)

Build a local dashboard:

Features:
Live event stream
Em state visualization
Trigger manual responses
Upload assets
Monitor system health
🚀 Deployment Modes
Mode 1 — Fully Local
Everything runs on desktop
No external dependencies
Mode 2 — Hybrid (Recommended)
Local for:
reactions
small generations
External for:
heavy media
Mode 3 — Scaled (Future)
Move services to cloud
Keep persona kernel identical
🔥 Key Engineering Insight

You are NOT building:

a chatbot

You are building:

a real-time emotional response system with media synthesis capabilities

That means:

latency matters
consistency matters
identity matters more than intelligence
⚡ Immediate Build Plan
Phase 1 (Foundation)
Docker Compose setup
Gateway + Telegram bot
Asset service (manual responses)
Phase 2
Signal engine (Python)
Persona kernel (TS rules)
Composer
Phase 3
Generation hub (images + voice)
Queue system
Phase 4
Dashboard + observability
External API fallback
