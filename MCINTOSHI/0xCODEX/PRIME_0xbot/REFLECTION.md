# 0x::PRIME — Reflection & Introspection

## Self-Check Schedule
| Check | Frequency | Output |
|-------|-----------|--------|
| Observation quality metrics | Every 5 min | Log precision/recall proxies vs baseline |
| Feed health | Every 1 min | Alert if any source missing |
| Confidence distribution | Every 10 min | Log median/variance |
| Heartbeat | Every 30s | Redis key updated |

## Anomaly Detection
| Anomaly | Indicator | Response |
|---------|-----------|----------|
| Feed drift | Statistical divergence from baseline | Alert; route to ERR for analysis |
| Confidence collapse | Confidence median < threshold | Alert and reduce publish rate |
| High false-positive rate | Observations rejected downstream | Re-evaluate model and thresholds

## Introspection Tools
- `redis-cli lrange agent:0xPRIMEbot:recent_observations 0 9`
- Metrics dashboards (Prometheus/Grafana) for confidence and feed health

## Audit Log Schema
```json
{
  "event": "observation_emitted",
  "observation_id": "prime-2026-0321-001",
  "signal": "volatility_increase",
  "score": 0.72,
  "confidence": 0.81,
  "sources": ["oracle_1","market_feed_a"],
  "timestamp": "2026-03-21T22:00:00Z"
}
```

## Review Cadence
- Weekly model and threshold sanity check
- Monthly feed provider review
