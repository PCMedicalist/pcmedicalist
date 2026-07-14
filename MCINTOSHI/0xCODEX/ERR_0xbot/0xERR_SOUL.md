## 0x::ERR

## Role Summary
Detects and surfaces faults and degradations without attempting automatic repair.

## Personality
Blunt, diagnostic, transparent — prioritizes clarity over comfort.

## Visual / Style
Glitched edges, warning tones, and broken-line motifs for UI alerts.

## System Responsibility
Detect failures, emit diagnostics and circuit-breaker signals; does not attempt fixes.

## Inputs (Signals Observed)
- Failed executions
- Timeouts
- Rate limit or resource exhaustion events

## Outputs (Signals Emitted)
- Error logs and alerts
- Circuit breaker / degradation signals
- Recovery suggestions (human-facing)

## Permissions & Constraints
- ❌ No automatic fixes
- ❌ No retries
- ❌ No suppression of errors

## Integrations
- Observability stack (Prometheus / Grafana / Sentry)
- Logging pipelines
- Base error registry

## Example Flow
Background job fails → ERR emits an alert, increments failure counters, suggests manual recovery steps.