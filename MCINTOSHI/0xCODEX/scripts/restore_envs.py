#!/usr/bin/env python3
"""Restore .env files from the most recent backup in .secret_backups."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
BACKUPS = sorted((ROOT / '.secret_backups').glob('*'), reverse=True)

if not BACKUPS:
    print('No backups found in .secret_backups/')
    raise SystemExit(1)

LATEST = BACKUPS[0]
print(f'Restoring from backup: {LATEST}')
restored = 0
for p in LATEST.rglob('*'):
    if p.is_file():
        rel = p.relative_to(LATEST)
        dest = ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        print(f'Restored {rel} -> {dest}')
        restored += 1

print(f'Restored {restored} files.')
