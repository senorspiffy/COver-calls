# Work item 092
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-22
## What we want
scripts/check_handoff.py never crashes on a non-UTF-8 01 or 03; the file is reported unreadable and the run fails (exit 1).
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-22-089.md N1 (PR #36): check_handoff.py L55 and L62 still `read_text(encoding="utf-8")`; 089 fixed only check_pipeline.py (work/089/03 step 9 left it out of scope).
## Root cause and prevention guardrail (BUG only)
Root cause: each script decodes on its own; 089's shared reader covers one script.
Guardrail: both reads go through one reader returning (text, why); a read census test for check_handoff.py like test_read_census; end-to-end fixture asserting no Traceback and exit 1.
## Recurring issue link (RI-#, if any)
RI-014 family. Found by A1 before merge; near miss, not counted.
## Done looks like
A bad byte in 01 or 03 gives a named unreadable line and exit 1; mutation (strict read restored) fails a named test.
