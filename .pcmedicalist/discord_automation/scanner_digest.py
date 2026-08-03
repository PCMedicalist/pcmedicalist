"""Scanner feed digest -> one clean post in PCMedicalist guild.
Reads LIVE scanner feeds from MCINTOSHI guild (read-only GET), dedups by token,
ranks by age, and posts to a target channel in the PCMedicalist guild.
No writes to MCINTOSHI. Default target: #📊-scanner-digest (PCM guild).

Usage:
  python3 scanner_digest.py --dry
  python3 scanner_digest.py --post            # post to #📊-scanner-digest
  python3 scanner_digest.py --post --target NAME
"""
import sys, re
from common import (PCM_GUILD_ID, MCINTOSHI_GUILD_ID, get_channels,
                    get_messages, send_message, channel_id_by_name, days_since)

DRY = '--dry' in sys.argv or '--post' not in sys.argv
TARGET = None
if '--target' in sys.argv:
    TARGET = sys.argv[sys.argv.index('--target') + 1]
TARGET = TARGET or '📊-scanner-digest'

def is_scanner(c):
    return c.get('type') in (0, 5) and 'scanner' in c['name'].lower()

def token_of(text):
    # STRICT: only real on-chain identifiers, never prose.
    # 1) $TICKER (3-10 uppercase, optionally with chain prefix like base/eth:)
    m = re.findall(r'\$[A-Z]{3,10}\b', text or '')
    if m:
        return m[0]
    # 2) 0x contract address (>=8 hex, real ERC-20 style)
    m = re.findall(r'\b0x[a-fA-F0-9]{8,}\b', text or '')
    if m:
        return m[0]
    return None

def looks_like_signal(text):
    # Reject MCINTOSHIbot forensic prose / instructions / tables.
    reject = ("Dedicated feed", "MCINTOSHI-SEED", "Verify Officially",
              "Do NOT trust", "WARNING", "Abnormal Gains", "Report Abuse",
              "market intelligence", "looks like", "Verdict", "Analysis is",
              "just a status", "Wait, one check", "passed", "Volume vs",
              "Note:", "Date Context", "It is likely", "Hey Agent")
    return not any(r in (text or '') for r in reject)

def main(source_guild):
    chs = get_channels(source_guild)
    if '_error' in chs:
        return None, 0, 0
    feeds = [c for c in chs if is_scanner(c)]
    seen, rows = {}, []
    for c in feeds:
        msgs = get_messages(c['id'], 50)
        if not isinstance(msgs, list):
            continue
        for m in msgs:
            txt = m.get('content', '')
            key = token_of(txt)
            if not key or key in seen:
                continue
            # skip pure seed/description noise AND forensic-prose false positives
            if not looks_like_signal(txt):
                continue
            seen[key] = True
            rows.append({'token': key, 'ch': c['name'], 'age': days_since(m.get('timestamp')),
                         'text': txt[:120]})
    rows.sort(key=lambda r: (r['age'], r['ch']))
    return rows, len(feeds), len(rows)

if __name__ == '__main__':
    rows, nf, nr = main(MCINTOSHI_GUILD_ID)  # live source
    if rows is None:
        print("SOURCE ERROR (MCINTOSHI feeds)")
        raise SystemExit(1)
    md = (f"**📊 Scanner Digest** — {nr} unique live hits "
          f"(deduped from {nf} MCINTOSHI feeds)\n"
          f"_Posted to PCMedicalist #📊-scanner-digest_\n\n")
    if not rows:
        md += "_No fresh scanner hits in window._"
    for r in rows[:25]:
        md += f"- `{r['token']}` · {r['ch']} · {r['age']}d\n"
    print(md)
    print(f"\n[feeds={nf} unique={nr} dry={DRY} target={TARGET}]")
    if not DRY:
        tid = channel_id_by_name(PCM_GUILD_ID, TARGET)
        if not tid:
            print("TARGET CHANNEL NOT FOUND in PCM guild"); raise SystemExit(1)
        r = send_message(tid, md)
        print('POST ->', tid, '|', r.get('_error', 'ok'))
