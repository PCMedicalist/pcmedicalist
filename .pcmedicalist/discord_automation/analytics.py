"""Guild census / health report -> markdown + optional Discord post.
Usage:
  python3 analytics.py                       # write /tmp/discord_analytics.md
  python3 analytics.py --post                # also post to #📈-guild-analytics
  python3 analytics.py --post --target NAME
Read-only except when --post is given (posts to PCM guild channel).
"""
import sys, json, subprocess
from common import (PCM_GUILD_ID, get_guild, send_message,
                    channel_id_by_name)

POST = '--post' in sys.argv
TARGET = None
if '--target' in sys.argv:
    TARGET = sys.argv[sys.argv.index('--target') + 1]
TARGET = TARGET or '📈-guild-analytics'
OUT = '/tmp/discord_analytics.md'

# ensure fresh audit
subprocess.run(['python3', 'audit.py', PCM_GUILD_ID, '/tmp/discord_audit.json'],
               check=True, capture_output=True)
rep = json.load(open('/tmp/discord_audit.json'))
g, ch, st = rep['guild'], rep['channels'], rep['msg_stats']
TEXTY = {'text', 'announcement', 'forum'}

active7 = sum(1 for c in ch if c['type'] in TEXTY and st.get(c['id'], {}).get('days_since_last', 999) < 7)
dead = [c for c in ch if c['type'] in TEXTY and (st.get(c['id'], {}).get('days_since_last', 999) > 120 or st.get(c['id'], {}).get('count_100', 0) <= 2)]
human = [c for c in ch if c['type'] in TEXTY and st.get(c['id'], {}).get('unique_authors', 0) >= 3]
from collections import Counter
by_cat = Counter(c.get('category') for c in ch if c['type'] in TEXTY)

md = (f"**📈 PCMedicalist Guild Analytics**\n\n"
      f"👥 ~{g['members']} members · 🟢 ~{g['presence']} online\n"
      f"📺 {len(ch)} channels · ✅ active<7d: {active7} · 🗑 stale: {len(dead)} · "
      f"🧑 human(≥3 authors): {len(human)}\n\n"
      f"**Healthy (keep/grow):** " + ", ".join(f"#{c['name']}" for c in sorted(human, key=lambda x: -st.get(x['id'], {}).get('unique_authors', 0))[:8]) + "\n")
md += "\n**By category:** " + " · ".join(f"{k}:{v}" for k, v in by_cat.most_common())

with open(OUT, 'w') as f:
    f.write(md)
print(md)
print(f"\nWROTE {OUT} | post={POST} target={TARGET}")
if POST:
    tid = channel_id_by_name(PCM_GUILD_ID, TARGET)
    if not tid:
        print("TARGET NOT FOUND"); raise SystemExit(1)
    r = send_message(tid, md)
    print('POST ->', tid, '|', r.get('_error', 'ok'))
    # Mirror to PCMedicalist Telegram group @baseline0xcodex (operator 2026-08-02).
    try:
        tg = subprocess.run(['hermes', 'send', '--to', 'telegram:@baseline0xcodex',
                             '--subject', '📈 Guild Analytics', md],
                            capture_output=True, text=True, timeout=60)
        print('TG MIRROR ->', 'ok' if (tg.returncode == 0 and 'sent' in tg.stdout.lower()) else 'FAIL', tg.stdout.strip()[:120])
    except Exception as e:
        print('TG MIRROR exception:', e)
