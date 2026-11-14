# Work item 064
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-14

## What we want
Python files under `work/` (diagnostic scripts such as `work/061/diag_keep.py`) are seen by `check_pipeline.py`'s code checks, or the rules say diagnostics live under `scripts/` with a test. Pick the smaller change.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `scripts/check_pipeline.py` L135 `CODE_PATHS` and L140 `RESEARCH_CODE_PATHS` do not include `work/`, so `work/061/diag_keep.py` (committed in 279a4e0) is invisible to UNTRACKED CHANGE and RESEARCH CODE.
- 061 A1 audit (logs/audit/2026-11-14-061.md): its lookback lambda has a dead `... or True else True` branch. A1 reproduced its output, so no wrong number. I3 reviewed and re-ran it (061/06 L218-227), but no check or test exercises its logic. (Corrected 2026-11-14 by A1 after 064 R1.)
- The same gap shape as 053 (e): code that produces numbers for the person sits outside the paths the checks read.

## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY).

## Recurring issue link (RI-#, if any)
Related to RI-007 (no new occurrence: 061 went through I1-I3 and A1 checked the script).

## Done looks like
A fixture with a `.py` file under `work/<ID>/` in a RESEARCH ONLY item is flagged (or the rule text plus a test pins where diagnostics go); existing work/ markdown is not flagged; 061 on main stays `complete`; suite green.
