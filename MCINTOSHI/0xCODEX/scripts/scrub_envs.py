#!/usr/bin/env python3
"""Backup and scrub committed .env files by replacing secret values with placeholders.

Backups are written to `.secret_backups/<timestamp>/...` and that folder is gitignored.
"""
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
BACKUP_ROOT = ROOT / '.secret_backups' / datetime.utcnow().strftime('%Y%m%d_%H%M%S')
PRESERVE_KEYS = {'SOUL_ID'}

def scrub_file(p: Path):
    rel = p.relative_to(ROOT)
    backup_path = BACKUP_ROOT / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    # copy original
    content = p.read_text(encoding='utf-8', errors='ignore')
    backup_path.write_text(content, encoding='utf-8')

    lines = content.splitlines()
    out_lines = []
    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#') or '=' not in line:
            out_lines.append(line)
            continue
        key, val = line.split('=', 1)
        key = key.strip()
        val = val.strip()
        if key in PRESERVE_KEYS:
            out_lines.append(f"{key}={val}")
            continue
        # heuristics: if value empty or placeholder, leave; else replace
        if not val or val.upper() in ('REPLACE_ME', 'XXXXX', '***'):
            out_lines.append(f"{key}={val}")
        else:
            out_lines.append(f"{key}=REPLACE_ME")

    p.write_text('\n'.join(out_lines) + ('\n' if content.endswith('\n') else ''), encoding='utf-8')
    print(f"Scrubbed {rel} -> backup at {backup_path}")

def find_env_files():
    for p in ROOT.rglob('.env'):
        # skip our backup folder
        if '.secret_backups' in p.parts:
            continue
        yield p

def main():
    envs = list(find_env_files())
    if not envs:
        print('No .env files found to scrub.')
        return 0
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    for p in envs:
        try:
            scrub_file(p)
        except Exception as e:
            print(f'Failed to scrub {p}: {e}')
    print(f'Backups written to {BACKUP_ROOT}. Remove backups securely when done.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
