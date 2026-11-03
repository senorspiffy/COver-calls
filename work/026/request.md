# Work item 026
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-10-31

## What we want
Work reached the person and `main` with pipeline steps skipped and no record. Find each gap, close it where it can still be closed (verify 024, fact-check 023), and add a check that shows skipped steps every day.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- 023 (`Scope: RESEARCH ONLY`): only `request.md`, `01-research.md`, `screen-summary.md`. No `02-improvements.md`, `03-handoff.md`, `07-audit-task.md`; no R2/R3 log lines (`logs/research/2026-10-31.md` has the R1 line only). Its result was still used to change 001 (commit 0416b5c) and open 024.
- 024 (`Scope: FULL`): only `request.md` and `05-build-report.md`. No 01–04, 06, 07. 05 says "Short path: no separate I1 plan file". `.claude/commands/run-item.md` has no short path. Merged to `main` in PR #4. 024's request asked "RI-001: compute how often two names pass together before relying on it"; no count exists.
- The UTF-8 fix (commits d994307, cf3ba3b, "Found on the Windows VPS: 20 tests failed") has no work item and no log line; the first commit missed 6 calls in `bot.py`, and it introduced the Python 3.12-only line in item 027.
- R1's 023 log line says "3 source families"; `python3 scripts/check_handoff.py 023` says 10 unique URLs. r1 step: "take it from the script, never count by hand".

## Root cause and prevention guardrail (BUG only)
Root cause: nothing checks that an item's step files exist before its result is used or merged, and run-item.md does not say what to do when the person asks to go faster. Steps are skipped silently and fixes made in other threads skip the pipeline entirely.
Guardrail: `scripts/check_pipeline.py` lists, for every work item, the step files its Scope requires and which are missing (exit 1 if any item has a later step without the earlier ones, or a result without 06/07). A test pins it on fixtures. A1 runs it daily; I3 runs it on its item. run-item.md: a person's request to go faster is recorded in request.md as `Scope: FAST (person, <date>)`, which may skip R2 and I1 but never R3's fact check (for claims) or I3. Any code fix found outside the pipeline gets a work item the same day.

## Recurring issue link (RI-#, if any)
RI-007 (new; 3 occurrences: 023, 024, UTF-8 fix)

## Done looks like
The script and its test exist; it flags 023 and 024 on the old files and passes once they are complete; 024 has a real I3 verification (tests, mutations, caps); 023 has a fact-check hand-off with Self-check; run-item.md, daily-audit.md and i3 name the script and the FAST scope.
