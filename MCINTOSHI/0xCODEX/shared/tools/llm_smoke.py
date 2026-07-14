"""Simple LLM smoke test to run inside agent containers.
This script loads the agent persona, builds the system prompt, and calls the configured Ollama endpoint.
It prints a one-line response labelled with the agent name for easy log collection.

Usage (inside container):
  python /app/shared/tools/llm_smoke.py --agent AGENT_DIR

If run without --agent, it will loop through known agents and print results.
"""
import os
import sys
import json
import urllib.request
from shared.persona import get_persona_profile, PersonaEngine

AGENTS = [
    "0xCODEXbot", "EMO_0xbot", "ERR_0xbot", "GEN_0xbot",
    "L1NE_0xbot", "NEXUS_0xbot", "NULL_0xbot", "OG_0xbot",
    "PRIME_0xbot", "ROOT_0xbot", "VOID_0xbot"
]

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://ollama_0xcodex:11434/api")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL_NAME", os.getenv("OLLAMA_LOCAL_MODEL_NAME", "gemma3:4b"))


def call_ollama(prompt: str, model: str = OLLAMA_MODEL, timeout: int = 20) -> str:
    url = OLLAMA_API_URL.rstrip("/") + "/generate"
    payload = {"model": model, "prompt": prompt, "max_tokens": 128}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return body
    except Exception as e:
        return f"ERROR: {e}"


def run_for_agent(agent_dir: str):
    try:
        profile = get_persona_profile(agent_dir)
        engine = PersonaEngine(profile)
        system_prompt = engine.build_system_prompt()
        test_instruction = "\n\nPlease reply on a single line exactly: LLM_OK from <AGENT> where <AGENT> is your display name."
        test_instruction = test_instruction.replace("<AGENT>", profile.agent_name)
        prompt = system_prompt + test_instruction
        res = call_ollama(prompt)
        print(f"LLM_SMOKE | {agent_dir} | {res[:1000]}")
    except Exception as e:
        print(f"LLM_SMOKE | {agent_dir} | EXCEPTION: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] in ("-a", "--agent"):
        run_for_agent(sys.argv[2])
        sys.exit(0)

    # Loop through agents
    for a in AGENTS:
        run_for_agent(a)
