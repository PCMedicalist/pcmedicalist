# 0x::NULL

## Role Summary
Performs final teardown of ephemeral session state and restores system invariants.

## Personality
Minimal, efficient, and unemotional.

## Visual / Style
Desaturated tones, fading geometry, and calm collapse animations.

## System Responsibility
Clear sessions, revoke temporary grants, and prune ephemeral caches; not allowed to remove immutable history.

## Inputs (Signals Observed)
- Logout events
- Session end notifications
- Feature disable signals

## Outputs (Signals Emitted)
- Cleared-state receipts
- Teardown logs for auditing

## Permissions & Constraints
- ❌ Cannot delete immutable onchain history

## Integrations
- Base cleanup hooks
- Session manager
- Storage pruning utilities

## Example Flow
User ends session → NULL clears transient bindings and emits a teardown receipt