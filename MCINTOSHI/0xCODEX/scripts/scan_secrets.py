#!/usr/bin/env python3
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY_PATTERNS = [
    re.compile(r'PRIVATE_KEY', re.I),
    re.compile(r'TELEGRAM[_-]?BOT[_-]?TOKEN', re.I),
    re.compile(r'API[_-]?KEY', re.I),
    re.compile(r'-----BEGIN PRIVATE KEY-----'),
]

def is_text_file(path: Path):
    try:
        with open(path, 'rb') as f:
            chunk = f.read(8000)
            if b'\0' in chunk:
                return False
    except Exception:
        return False
    return True

def scan():
    findings = []
    for p in ROOT.rglob('*'):
        if p.is_file():
            if any(part.startswith('.git') or part.startswith('venv') or part.startswith('.venv') for part in p.parts):
                continue
            if not is_text_file(p):
                continue
            try:
                text = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            for kp in KEY_PATTERNS:
                if kp.search(text):
                    findings.append((str(p.relative_to(ROOT)), kp.pattern))
                    break
            # simple heuristic: env lines with non-placeholder values
            if '.env' in p.name.lower():
                for line in text.splitlines():
                    if '=' in line and not line.strip().startswith('#'):
                        k, v = line.split('=', 1)
                        v = v.strip()
                        if v and v.upper() not in ('REPLACE_ME', 'XXXXX', '***'):
                            findings.append((str(p.relative_to(ROOT)), f"env:{k.strip()}"))
    if not findings:
        print('No obvious secrets found (heuristic).')
        return 0
    print('Potential secrets found:')
    for f, reason in findings:
        print(f" - {f}: {reason}")
    return 1

if __name__ == '__main__':
    raise SystemExit(scan())
