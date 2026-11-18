# Work item 074
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-18

## What we want
Every GUARDED/"Move to GUARDED when" mutation probe in logs/recurring-issues.md is a committed, re-runnable check (for example `scripts/probe_guardrails.py`): one entry per probe with the file, an exact anchor text, the replacement, the test file, and the test that must fail. A1 runs it in the daily review instead of rebuilding each probe by hand. A probe whose anchor no longer matches the code exits non-zero and names the probe (so a refactor can't silently retire a guardrail check).

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/recurring-issues.md RI-002 (2026-11-15 line): the 063 GUARDED probe is "leading-edge tests fail with `td.earnings[0] <= d and` removed". On main 4d690a3, `grep -n "td.earnings\[0\] <= d" ccbot/realtest.py` → no hit: 065 moved the logic into `_earnings_state` (ccbot/realtest.py L391-405). A1 had to rebuild the probe (`i == 0` returns "known": 9 failed, 41 passed) on 2026-11-18.
- RI-013's probe "mutation 1b" exists only as I3's scratch script for 067 (work/067/06-verification.md L96-104, path under a removed scratchpad). A1 rewrote it on 2026-11-18 (1 failed, 16 passed).
- Daily audits 2026-11-07 to 2026-11-11 each re-ran the RI-002 tickers.json probe by hand (recurring-issues.md RI-002 status text).

## Recurring issue link (RI-#, if any)
RI-010 (a check that exists only in text no script runs). Keeps RI-002 and RI-013 GUARDED checks honest.

## Done looks like
A script (stdlib + pytest subprocess) with at least the three probes A1 ran 2026-11-18 (RI-002 063 leading edge, RI-002 065 interior gap, RI-013 067 1b), editing only a scratch copy/worktree, never the repo tree; output one line per probe: name, failed/passed counts, target test failed yes/no; exit 1 if any probe's target test passes or an anchor is missing (anchor count != 1). Fixture tests for: probe holds, probe does not hold, anchor missing. a1-auditor.md daily review says to run it and paste its output. Runtime noted (the realtest probes take ~50 s and ~26 s).
