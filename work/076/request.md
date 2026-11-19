# Work item 076
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-19

## What we want
The I2 log field `tests <pass>/<total>` has one defined meaning, so I2 lines are comparable.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/implementation/2026-11-18.md: `23:42 | I2 | 072 | 8 files changed | tests 411/411` while the suite collected 412 (411 passed, 1 skipped); 073's line the same day: `tests 414/415` (skip counted). logs/audit/2026-11-18-072.md point 3.
- `<total>` is defined in neither .claude/agents/i2-builder.md nor check_pipeline.py LOG_FORMAT; I2 types both numbers by hand.

## Root cause and prevention guardrail (BUG only)
Root cause: a hand-typed count with no definition (RI-006 pattern).
Guardrail: define total = passed + failed + skipped + errors in i2-builder.md and LOG_FORMAT docs, or take pytest's summary line as printed (`tests 411 passed, 1 skipped`); `--log` refuses pass > total; a test pins it.

## Recurring issue link (RI-#, if any)
RI-006 pattern. Found before merge; not counted (precedent 2026-11-18).

## Done looks like
`--log I2` refuses an ill-formed or inconsistent tests field; i2 text defines it; tests for both.
