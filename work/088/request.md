# Work item 088
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-21
## What we want
084's RULE NOT SEEN gate keeps the strict rule whenever it cannot tell (unborn HEAD, 05/06 not yet committed), and a test proves it.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-21-084.md finding 1: `if not sha: return None, ""` → `return False, ""`, and the unborn-HEAD return → `False, ""`, each survive tests/test_pipeline_check.py + tests/test_safety.py. Under the first, an item checked before its 05/06 is committed (run-item's end-of-run check) has a failing I2/verdict line dropped from INCOMPLETE. Finding 2: 03's call budget (2 git calls/pair) is stale; build makes 4 (`rev-parse --verify HEAD` repeated per pair).
## Root cause and prevention guardrail (BUG only)
Root cause: tests held only the git-failed and no-file cases strict; "unknown" paths had no fixture (RI-002: a default that fails open).
Guardrail: fixtures for an uncommitted 05 with a bad I2 line and for an unborn HEAD, each asserting INCOMPLETE and no RULE NOT SEEN entry; both mutations fail them. Read HEAD once in `_anchor_env`.
## Recurring issue link (RI-#, if any)
RI-002, RI-010 family. Found by A1 before merge; near miss, not counted.
## Done looks like
Both mutations fail named tests; git calls per pair stated from code.
