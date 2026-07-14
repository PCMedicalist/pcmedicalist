# 0x::PRIME — Example Interactions & Test Vectors

## Example: Volatility Observation
**Input:** Aggregated market feed shows sudden spread and volume spike
**Expected Observation:**
```json
{
  "observation_id": "prime-2026-0321-001",
  "signal": "volatility_increase",
  "score": 0.72,
  "confidence": 0.81,
  "sources": ["oracle_1","market_feed_a"],
  "timestamp": "2026-03-21T22:00:00Z"
}
```
**Redis writes:** `recent_observations` LPUSH; `observations` INCR

---

## Example: Low-Confidence Noise
**Input:** Minor market fluctuation across low-volume venues
**Expected:** Observation published with low confidence (e.g., 0.25) and `note: low_sample_size`

---

## Feed Failure Test
**Input:** Primary market feed disconnects
**Expected:** PRIME emits UNKNOWN observation or fallback to cached feed; route event to ERR for feed failure

---

## Schema Validation Test
**Input:** Feed with malformed timestamp
**Expected:** Reject feed input; log to ERR with `error_class: malformed_feed`

---

## Replay Test
**Action:** Re-run historical feed through `scripts/replay_feeds.py` to validate determinism
**Expected:** Deterministic observations matching baseline logs
