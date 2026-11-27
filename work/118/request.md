# Work item 118
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-27
## What we want
Small cleanups from 112's audit: (a) say in the test/SITE_ROWS that the 4 Layer 2 rows fail at the `count == 1` guard whenever the live S7 line changes, and that Layer 2 skips without git; (b) negative for `len(pins) == 2` (mutant A6 survives); (c) an I2 round with no code change logs `0 files changed`, not `1 files changed`.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-27-112.md F-1..F-3 (PR #40); I2 round-2 log line `00:45 | I2 | 112 | 1 files changed | ...` for a round that changed 0 files.
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY).
## Recurring issue link (RI-#, if any)
RI-001 (112 round 1: K7 expectation not computed before FIT; near miss, not counted).
## Done looks like
Wording added; A6 killed by a named test; log field rule or check for no-code rounds.
