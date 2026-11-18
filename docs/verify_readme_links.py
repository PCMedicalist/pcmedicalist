#!/usr/bin/env python3
"""Verify every external URL in README.md. Usage: python3 docs/verify_readme_links.py [--strict]"""
import re, subprocess, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "README.md").read_text(encoding="utf-8")

URLS = set(re.findall(r'(?:src="|href=|\]\()([^"\s)]+?)(?:"|\))', TEXT))
SKIP_PREFIXES = ("#", "mailto:", "./", "../", "assets/")

def check(url: str) -> tuple[str, int, str]:
    if any(url.startswith(p) for p in SKIP_PREFIXES):
        return url, 0, "skip"
    if url.startswith(("http://", "https://")) is False:
        return url, 0, "not-url"
    proc = subprocess.run(
        ["curl", "-s", "-L", "-o", "/dev/null", "-m", "20", "-w", "%{http_code} %{content_type}", url],
        capture_output=True, text=True,
    )
    parts = proc.stdout.strip().split(" ", 1)
    return url, int(parts[0]) if parts and parts[0].isdigit() else 0, (parts[1] if len(parts) > 1 else "")

def main() -> int:
    strict = "--strict" in sys.argv
    bad = []
    for url in sorted(URLS):
        u, code, ctype = check(url)
        status = "OK " if code == 200 else ("SKIP" if code == 0 else "BAD ")
        print(f"{status} {code} {ctype[:28]:28} {u[:110]}")
        if strict and code not in (0, 200):
            bad.append((u, code))
    if bad:
        print(f"\nFAIL: {len(bad)} non-200 URL(s) in strict mode")
        return 1
    print(f"\nPASS: {len(URLS)} URL(s) checked")
    return 0

if __name__ == "__main__":
    sys.exit(main())
