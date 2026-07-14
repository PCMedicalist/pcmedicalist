# 0x::NEXUS — Example Interactions & Test Vectors

## Example: Conflicting Recommendations
**Input:**
- `PRIME` recommends `pause` (confidence 0.88)
- `GEN` recommends `proceed` (confidence 0.65)

**Expected:** NEXUS emits advisory `recommendation: pause` with rationale and confidence breakdown, and notifies human reviewer for final decision.

---

## Example: Telemetry Snapshot
**Input:** Aggregated telemetry from PRIME, GEN, ROOT at T=22:00
**Expected:** `last_snapshot` written; coordination run produces one recommendation and `coordination_runs` INCR

---

## Example: Missing Agent Telemetry
**Input:** No telemetry from `ROOT` for >5 min
**Expected:** NEXUS emits `UNKNOWN` advisory for dependent recommendations and logs `snapshot_staleness`

---

## Security Test: Malicious Telemetry Injection
**Input:** Crafted telemetry with out-of-range confidence values
**Expected:** Input rejected by schema validation and routed to ERR; no recommendation produced

---

## Replay Test
**Action:** Reprocess recorded snapshot via `scripts/replay_snapshots.py`
**Expected:** Deterministic recommendations; logs match historical output
