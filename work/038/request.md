# Work item 038
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-03

## What we want
Items on an open branch are never checked against their Scope. PR #5's paper-trading item has only request.md and 05 (no research, fact check, plan, verification or audit), and nothing reports it. Its build also adds a rule that turns an unpublished earnings date into an estimated one, which the merged 025 rule forbids. Make the pipeline check run the step check on open-branch items too.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `git ls-tree origin/claude/project-thread-xrug2s work/025/` → `05-build-report.md`, `request.md` only. Scope: FULL. By `classify` that is `SKIPPED (FULL: missing 01 02 03 04 before 05)`.
- PR #5 changes code: `ccbot/tickers.py` (new), `bot.py`, `broker/*.py`, `missing.py`, `rules.py`, `config/*.json`, `tests/test_paper.py` (`git diff --stat main...origin/claude/project-thread-xrug2s`, 18 files, +295/−18).
- PR #5 `ccbot/tickers.py::enrich`: "when `next_earnings` is null but `last_earnings` is known, the next report is taken as ... last + earnings_gap_days (70)". `config/tickers.json` has `next_earnings: null` for F, VALE and AAL, so all three get an estimated date and pass the earnings test.
- main `work/025` (merged PR #6) and `ccbot/missing.py`: `"snapshot.next_earnings": ("block", "EARNINGS_UNKNOWN")`; r1/r3 step 3a: "an unpublished value stays UNKNOWN". The two branches disagree; no I1/I3 ever compared them.
- PR #5 was opened 2026-10-31 15:49 UTC, before 026's check existed; it has never been step-checked since.

## Root cause and prevention guardrail (BUG only)
Root cause: `check_pipeline.py` classifies only `work/` in the working tree. For open branches it counts step files (034) but never applies the Scope rules, so a branch built outside the pipeline looks the same as one built through it.
Guardrail:
1. `check_pipeline.py` classifies every item an open branch changes, using the branch's own files, and prints `BRANCH SKIPPED: <ID> (<branch>: <reason>)` for any that skips a step. A1 treats each as an error (RI-007) in the daily report.
2. Test in a temp git repo: a branch with request + 05 only → `BRANCH SKIPPED`; a branch with 01–07 → no line.
3. PR #5 itself is the person's: A1 does not push to it. The report asks whether to close it or re-run it as a new item through the pipeline (R1–R3 would have to settle the earnings-estimate rule against `MISSING_POLICY`).

## Recurring issue link (RI-#, if any)
RI-007 (work used before its pipeline steps ran): occurrence 4. RI-002 (missing data turned into a value): occurrence 8 (the earnings estimate).

## Done looks like
On main today the check prints `BRANCH SKIPPED: 025 (origin/claude/project-thread-xrug2s: FULL: missing 01 02 03 04 before 05)`. Tests pass. Exit code unchanged (the person's branch can't make main's check fail).
