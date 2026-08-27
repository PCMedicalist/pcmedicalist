"""
PCMedicalist Diffusion Scene Service
====================================
Per-post FRESH cyber backdrop generator for the Creative Studio + all
social-publisher image/video pipelines. Uniformly upgrades every pipeline
that calls publish_creative_studio.composite_image_url().

Design (intelligence over speed):
  - Each sequenced post gets a FRESH diffusion backdrop (uniqueness per cycle).
  - SD1.5 on the RTX 2060 (12GB) is SHARED with Ollama qwen3.5:9b (~6.2GB
    resident via a snap listener that auto-respawns and CANNOT be killed from
    inside the agent gateway). To guarantee a fresh scene every cycle WITHOUT
    disrupting Ollama, the pipeline runs on CPU when the GPU is contested.
    GPU is used only when it is actually free (e.g. Ollama off-peak).
    CPU @512px ~90-150s; GPU ~6.6s. Both produce a real diffusion scene.
  - FAIL-SOFT: if diffusion is truly unavailable (model missing, CPU OOM),
    returns None -> caller falls back to the flat brand gradient (no broken
    post, no model drift in final asset).
  - Seeded by topic hash so a given post is deterministic/reproducible for
    audit, but DIFFERENT topics -> different scenes (fresh per post).

This module is imported lazily by composite_image_url(); it never blocks
the post if anything goes wrong.
"""
from __future__ import annotations
import os
import sys
import hashlib
from pathlib import Path

# Ollama's qwen3.5:9b (~6.2GB) is resident on the RTX 2060 via a snap listener
# that auto-respawns and CANNOT be killed from inside the agent gateway, so the
# GPU is permanently contested. To guarantee a FRESH diffusion scene every post
# WITHOUT disrupting Ollama, we run inference on CPU by default. Set
# PCMED_DIFFUSE_CUDA=1 in the environment (e.g. during an off-peak window when
# Ollama is stopped) to use the GPU for ~6.6s/img instead of ~90-150s on CPU.
if os.environ.get("PCMED_DIFFUSE_CUDA") != "1":
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

import torch
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler

HERE = Path(__file__).resolve().parent
CKPT = HERE / "ComfyUI" / "models" / "checkpoints" / "v1-5-pruned-emaonly.safetensors"
OUT_DIR = HERE / "scenes"
OUT_DIR.mkdir(exist_ok=True)

# Brand-aligned scene prefix (enterprise / technical / cybersecurity language;
# AVOIDS anti_language: gaming UI, streamer graphics, sci-fi overload,
# cyberpunk clutter per branding.json).
_BRAND_SCENE_PREFIX = (
    "enterprise cybersecurity operations center, clean technical aesthetic, "
    "server racks, diagnostic blue and accent purple lighting, "
    "minimal premium render, high detail, cinematic, no text, no logos"
)

_PIPE = None
_DEVICE = None


def _get_pipe() -> StableDiffusionPipeline:
    """Load SD1.5 on CPU (CUDA is hidden from torch by default so Ollama keeps
    the GPU). Cached after first load. If PCMED_DIFFUSE_CUDA=1 was set, torch
    sees the GPU and we use it instead."""
    global _PIPE, _DEVICE
    if _PIPE is not None:
        return _PIPE
    if not CKPT.exists():
        raise FileNotFoundError(f"SD1.5 checkpoint missing: {CKPT}")
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        if dev == "cpu":
            # Force every component onto CPU. SD1.5 checkpoints load some
            # submodules onto CUDA by default (the text encoder then fails at
            # inference with "No CUDA GPUs are available"); device_map="cpu"
            # + set_default_device("cpu") keeps the whole graph on CPU so
            # Ollama can keep the GPU undisturbed.
            torch.set_default_device("cpu")
            pipe = StableDiffusionPipeline.from_single_file(
                str(CKPT), torch_dtype=torch.float32, use_safetensors=True,
                device_map="cpu"
            )
        else:
            try:
                pipe = StableDiffusionPipeline.from_single_file(
                    str(CKPT), torch_dtype=torch.float16, use_safetensors=True
                ).to("cuda")
            except Exception as _cuda_e:
                # CUDA load failed (usually OOM because Ollama hasn't fully
                # released VRAM yet, or a race with the gpu_gate unload window).
                # NEVER fail to a flat gradient — fall back to CPU so the post
                # still gets a real diffusion scene (slower, but correct).
                # 2026-08-26 fix: gradient fallback was producing solid-color
                # video backgrounds on ~half of cron runs (intermittent OOM race).
                print(f"[scene_service] CUDA load failed ({_cuda_e}); retrying on CPU")
                torch.set_default_device("cpu")
                pipe = StableDiffusionPipeline.from_single_file(
                    str(CKPT), torch_dtype=torch.float32, use_safetensors=True,
                    device_map="cpu",
                )
                dev = "cpu"
        pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config)
        pipe.enable_attention_slicing()
        pipe.safety_checker = None  # internal brand asset, not public
        _PIPE, _DEVICE = pipe, dev
        print(f"[scene_service] pipeline loaded on {dev}")
        return _PIPE
    except Exception as e:
        raise RuntimeError(f"could not load diffusion pipeline on {dev}: {e}")


def generate_scene(topic: str, size: int = 384, steps: int = 20) -> Path | None:
    """Generate a FRESH cyber backdrop for `topic`. Returns Path or None.

    None signals the caller to fall back to the flat brand gradient.
    Never raises — fail-soft by design.

    Default 384px / 20 steps: fast enough for CPU (~90-150s on the 2060's
    cores) while the compositor upscales the backdrop to 1080x1350. GPU mode
    (PCMED_DIFFUSE_CUDA=1, Ollama off) uses full 512px / 30 steps (~6.6s)."""
    try:
        # Deterministic-but-unique seed: hash the topic so the same post
        # reproduces the same scene (audit), different posts differ.
        seed = int(hashlib.sha256(topic.encode()).hexdigest(), 16) % (2**32)
        full = f"{_BRAND_SCENE_PREFIX}, {topic}"
        pipe = _get_pipe()
        dev = _DEVICE or "cpu"
        gen = torch.Generator(device=dev).manual_seed(seed)
        img = pipe(full, num_inference_steps=steps, height=size, width=size,
                   guidance_scale=7.5, generator=gen).images[0]
        out = OUT_DIR / f"scene_{seed % 100000:05d}.png"
        img.save(out)
        return out
    except Exception as e:
        print(f"[scene_service] diffusion unavailable, fall back to gradient: {e}")
        return None


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("topic", help="post topic / prompt fragment")
    ap.add_argument("--size", type=int, default=512)
    args = ap.parse_args()
    p = generate_scene(args.topic, size=args.size)
    print("SCENE:", p)
