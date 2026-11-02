# 02 Improvements - 032
## What past logs say
See `logs/audit/2026-11-01.md` and `logs/recurring-issues.md` (RI-007, RI-008).
## 3 ways FOR
1. Runs on every pytest, including fixes made outside the pipeline (the RI-008 case).
2. Catches any 3.12+ syntax, not one pattern.
3. Removes a manual step from I3.
## 3 ways AGAINST
1. Skips where neither 3.10 nor 3.11 is installed (e.g. the person's VPS may only have one Python).
2. Compiles syntax only; 3.12-only stdlib calls are not caught.
3. Adds a subprocess (~0.1 s).
## Findings by language
Languages: N/A (no new external claims). This changes code, wording or process inside this repo only, so no outside source in any language could confirm or contradict it.
## Holes to watch out for (summary)
See AGAINST list.
