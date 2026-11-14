# Work item 062
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-13

## What we want
A RESEARCH ONLY item cannot add or change code (ccbot/, scripts/, tests/, config/) without the I1-I3 steps that check code, unless the person waives them by name. `check_pipeline.py` reports it, on main and on open branches.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- Item 061 (PR #26, `origin/claude/project-thread-ltyppm`, c663855) is `Scope: RESEARCH ONLY` (01, 02, 03, 07 only) but adds `ccbot/realtest.py` (570 lines), `scripts/fetch_real_data.py` (177), `tests/test_realtest.py` (111). No 04 build plan, no 06 verification. `check_pipeline.py` shows `061: awaiting A1 (RESEARCH ONLY)`, `BRANCH SKIPPED: none`.
- What an I3 check would have caught: 061/02 says "the bot rule is tested exactly as configured", but `realtest._pick` picks the expiry nearest the window midpoint (37.5 DTE) and accepts delta within ±0.12 of 0.275, while the bot (`ccbot/expiries.pick_expiry`, `ccbot/rules.py` line 286-304, `config/default.json` `tolerance` [0.20, 0.35]) takes the first expiry in 30-45 DTE (7-day slack) and only strikes with delta 0.20-0.35.
- A1 probe (scratch copy, 061 data, bid fills, 17 stocks) with the bot's own expiry/strike choice: median excess -1.7 pts/yr (061: -1.8), A2 4 of 17 within 1 pt (061: 6 of 17), 1,170 calls (061: 1,161). The pass/fail verdict does not change (A2 still fails), but the reported numbers are not the bot rule's.

## Root cause and prevention guardrail (BUG only)
Root cause: RESEARCH ONLY means "no 04-06 files", and nothing says it also means "no code". So a research item can ship a simulator that re-implements the bot's rules, and nobody compares it to `ccbot/` or `config/` (the I1/I3 job). RI-007's check compares an item's files to its Scope, not the item's commits.
Guardrail:
1. `check_pipeline.py`: a RESEARCH ONLY item whose commits (main or open branch) change files under `ccbot/`, `scripts/`, `tests/` or `config/` is SKIPPED (`BRANCH SKIPPED:` on a branch) with the file list, unless request.md has `Waived: 04 05 06 (person, <date>: ...)`. Test with a fixture.
2. run-item.md and r3-fact-checker.md: RESEARCH ONLY items write no code; a research item that needs code is FULL (or gets the person's waiver).
3. i3-verifier.md: a simulator or replay that claims to test "the bot rule" must call the bot's own pickers (`pick_expiry`, `pick_strike`, config values) or have a test that shows it picks the same contract.

## Recurring issue link (RI-#, if any)
RI-007 (ESCALATED), occurrence 6.

## Done looks like
A scratch item shaped like 061 (RESEARCH ONLY + a ccbot/ file) shows SKIPPED / BRANCH SKIPPED and exit 1; with the person's `Waived: 04 05 06` line it passes; rules text updated; suite green. 061's own simulator fix stays with PR #26 (A1 does not push to a branch it didn't open).
