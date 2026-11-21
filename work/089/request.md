# Work item 089
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-21
## What we want
A non-UTF-8 byte in any file under logs/ or a step file never crashes scripts/check_pipeline.py; the file is reported as unreadable and the run exits 1.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/audit/2026-11-21-086.md finding 1 and work/086/05 Deviation 1: one log file of bytes `\xff\xfe` → `UnicodeDecodeError` traceback, exit 1, at 7eb51b0 and pre-086 129120b. Path: `main` → `incomplete` → `_log_text`; `orphan_log_lines` decodes the same way. 086's `_item_lines` already reports `<file> unreadable`.
- work/081/03 (R1 F10): strict `read_text(encoding="utf-8")` on working-tree step files, left out of 081's scope.
- logs/audit/2026-11-21-081.md F3: a non-UTF-8 `.git/shallow` line gives the wrong UNTRACKED CHANGE reason ("cutoff not in HEAD's history") because `_shallow_boundaries` returns "full" on UnicodeDecodeError when `sure` is False.
## Root cause and prevention guardrail (BUG only)
Root cause: every reader decodes on its own, strictly; only some catch the error.
Guardrail: one shared reader returning (text, why); every logs/ and work/ read goes through it (census-style test like 081's GIT_CENSUS); end-to-end no-traceback test; N13 gains the `_run` assert; `_shallow_boundaries` returns "unreadable" on decode error whatever `sure` is, test (c) asserts the UNTRACKED CHANGE text.
## Recurring issue link (RI-#, if any)
RI-014 family (checker result depends on repo state). Found by I2/I3/A1 probes before merge; not counted.
## Done looks like
Bad-byte fixtures in a log, a step file and .git/shallow: no traceback, named "unreadable" lines, exit 1; mutations fail named tests.
