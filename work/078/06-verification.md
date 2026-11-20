# 06 Verification - 078
Verdict: PASS (round 1)
Sent back to: none

Head verified: e4c19dd ("Item 078: I2 build"), branch daily-fixes/2026-11-19, origin/main 00e5ab6. Not shallow (`git rev-parse --is-shallow-repository` → `false`). Scratch work only under /tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/078-I3/ (worktree `wt` at e4c19dd, mutant copy `copy`, probe outputs `probe_main.txt`, `probe_head.txt`).

## I1 audit (plan vs research)
- `python3 scripts/check_handoff.py 078` (re-run by I3):
  ```
  sources count (unique URLs in 01-research.md): 4
  fact-check rows: 50
  totals line: 50 rows -> 40 as-is, 6 fixed, 4 removed
  PASS
  exit 0
  ```
- 04 follows every 03 map step 1-8, the Missing inputs table (8 rows), and OQ1-OQ6. The Rule trace has one row per 03 rule. Nothing is dropped except the RI-010 `--log` probe, which 03 had already removed (F25).
- I1 additions C1-C8 each have a source or a reason:
  - C1 (strict XPASS is `<failure>`, not `<skipped>`): has 2 fetched pytest sources (Research 1). I3 confirmed it: in my mutant D run the fixture baseline printed `baseline tests/test_xfail.py: 1 failed, 1 passed, 0 errors, 0 skipped`. Adding s3 changes the step-1 TOTAL to `5 probes ... 4 error`. The new sum is right: 0 + 1 + 0 + 4 = 5.
  - C2 (`getattr` fallback): has the Python json docs as its source.
  - C3: the run's own date goes in `recorded`.
  - C4: the RI-014 shallow pre-check.
  - C5: the N4 anchor is re-counted after 077.
  - C6: HEAD is the 077 tree.
  - C7: the `_probe` default.
  - C8: targets are written out in full.
  - None of these adds scope. All are tooling only. No strategy rule, ccbot/, config/ or data/ file changes.
- The plan names 3 files. a1-auditor.md is flagged as a RULES file that needs the person's OK.

## I2 audit (build vs plan)
`git diff --stat HEAD~1 HEAD` lists exactly the 3 planned files, plus 05 and the I2 log line. Line by line against 04 Files 1-3:
- **scripts/probe_guardrails.py**
  - The `import json`, PROBES comment, RI-013 `no_module_reason`, 6 entries in plan order, `_run_probe` reason text, `.json` check after the `.py` compile check (`ValueError`, `getattr` fallback, no same-quote f-string), and `_probe_all` neither-key check after REQUIRED all match the plan. `REQUIRED`, `classify`, `read_junit` and `_baseline` are unchanged in the diff.
  - Byte check: a script compared every new entry's anchor, replacement, reason/module and target name, plus the RI-013 reason, with the 03 map rows 3 and 5. All 25 checks print True. For the 4 check_pipeline entries, `_CP_REASON` evaluates to the 03 step 5 reason text byte for byte.
- **tests/test_probe_guardrails.py**
  - Docstring, imports, the 3 FILES entries (test_skip.py byte for byte from 03 step 1), the `_probe` C7 default, the b assert, the new `test_skip_entry_and_json_cases` (s1, s2, s3, r0, j1, TOTAL, exit 1, 1 worktree), classify cases (i)/(ii), and the well-formed test (9 entries, 9 ids, exactly one key, basename, JSON parse, target list): all as planned.
- **.claude/agents/a1-auditor.md**: one sentence changed, "about 2 minutes (item 074)" → "about 4 minutes (items 074, 078)".
- Greps from the plan, re-run by I3:
  - `conftest L7` → 0.
  - `no_module_reason` → 10 (≥ 6).
  - `about 2 minutes` → no hits.
  - `read_text|write_text` → no hits (both files use bytes with explicit utf-8).
  - `@REC|@RUNTIME@` in scripts/ and tests/ → no hits.
  - `git diff --check HEAD~1 HEAD` → clean.
- Connectivity, re-done:
  - `json` is used by the JSON check. `_CP_REASON` is used by 4 entries.
  - The neither-key branch is reached by r0, and the JSON branch by j1. Mutants D and E below show that each one is live.
  - The 6 entries run in `main()`: my two real runs print all 9 lines.
  - `no_module_reason` is printed in each line's `code check: n/a (...)` field, which A1 pastes.
  - Every new branch ends in an ERROR line with `pytest not run`, or in a verdict.
- Deviation 1, `_CP_REASON` shared constant: **accepted**.
  - The plan says the 4 entries "share" the 03 reason. 03 asks for byte-identical strings, and the evaluated value is identical (byte check above).
  - The printed text in both of my runs is the 03 string.
  - Spelling it once removes 3 copies that could drift apart.
  - `test_shipped_probes_well_formed` checks the value, and mutant F (both basenames removed from `_CP_REASON`, I2) fails it.
- Deviation 2, placeholder `recorded` text (`@REC_N3@` / `@REC_CP@` / `@REC_N2@`) in 05's `--ref origin/main` and `--ref HEAD` pastes: **accepted, with I3's own run as the missing evidence**.
  - Step 7(c) takes `recorded` from that same run, so the field could not hold its final value during the run.
  - `recorded` is print-only. `classify` and the verdict read only the exit code and junit, so the placeholder cannot change any HOLDS.
  - 05 says so openly in two places.
  - What 05 lacks is a run that prints the shipped values. My run at e4c19dd supplies it (below): 0 `@REC` strings in either output. All 6 new `recorded` values equal the origin/main per-entry counts from my own run: N3 1/22, N5 8/82, N4/N6/N1 1/89, N2 1/17.
  - Note: on `--ref HEAD` the label `2026-11-20 (078/05): 1 failed, 89 passed` differs from the branch's own 1/212. This is by design: the label says the counts were measured on main for 078/05.
- Deviation 3 (HEAD moved to 6a2ca0c, audit-only) and deviation 4 (I2's first mutant F was set up wrong and redone): checked. `git diff --stat 62f0cc0 6a2ca0c -- ccbot/ config/ scripts/ tests/` shows no code change, and my probes ran at e4c19dd anyway.

## Tests re-run (output)
Targeted (repo root, Python 3.13.18, pytest 9.1.1):
```
$ python3 -m pytest -q tests/test_probe_guardrails.py tests/test_safety.py
19 passed in 8.67s
```
Full suite at e4c19dd (repo root):
```
$ python3 -m pytest -q
556 passed, 1 skipped in 113.36s (0:01:53)
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
```
This is the same as 05 (556 passed, 1 skipped; base 555 + 1 new test).

Oldest-Python compile: `python3 -m pytest -q tests/test_safety.py -k oldest -rs` → `1 passed`. It ran and did not skip: python3.11 is on PATH (`/usr/bin/python3.11`), python3.10 is not.

I3 mutants. They ran on a `git archive HEAD` copy at /tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/078-I3/copy, never in the repo. The script (scratchpad 078-I3/mut.py) asserts each anchor occurs once, runs `pytest -q tests/test_probe_guardrails.py`, then restores the file. Afterwards `diff -q` of the copy against the repo file shows them identical.
```
mutant A: exit 1   (classify `== "failed"` -> `!= "passed"`, the 074 surviving mutant)
  FAILED tests/test_probe_guardrails.py::test_skip_entry_and_json_cases - Asser...   (s1 ... HOLDS)
  FAILED tests/test_probe_guardrails.py::test_classify_missing_or_bad_junit - A...  (assert 'HOLDS' == 'NOT HELD')
  2 failed, 8 passed in 9.77s
mutant B: exit 1   (baseline `elif status != "passed"` branch removed)
  E  AssertionError: assert 'ERROR (baseline: target skipped)' in 's2 (RI-T): ... NOT HELD; ...
  1 failed, 9 passed in 6.59s
mutant C: exit 1   (fixed "conftest REPO, conftest L7" code text restored)
  FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
  1 failed, 9 passed in 6.37s
mutant D: exit 1   (neither-key check removed)
  E  KeyError: 'no_module_reason'
  1 failed, 9 passed in 6.54s
mutant E: exit 1   (.json check disabled)
  E  AssertionError: assert ('ERROR (mutation is not valid JSON: Expecting value, line 1)' in 'j1 (RI-T): 0 failed, 2 passed, ... NOT HELD; ...
  1 failed, 9 passed in 7.32s
mutant F2: exit 0  (N3 reason: only the 2nd "tickers.json" removed; "config/tickers.json" still in it) -> not a basename removal, wrong mutant
  10 passed in 6.86s
mutant F3: exit 1  (N3 reason with both "tickers.json" removed)
  E  AssertionError: RI-002-046-tickers-key  assert 'tickers.json' in 'config/data is data: ...'
  1 failed, 9 passed in 6.68s
mutant G: exit 1   (N2 gets both module and no_module_reason)
  FAILED tests/test_probe_guardrails.py::test_shipped_probes_well_formed - Asse...
  1 failed, 9 passed in 6.66s
mutant H: exit 1   (N4 entry loses its no_module_reason: neither key)
  E  AssertionError: RI-009-037-clash-line  assert False != False
  1 failed, 9 passed in 6.60s
```
Mutant F2 surviving is the same slip I2 made: the basename was still in the reason. The test checks that the basename is present, not where it appears. F3 is the correct form, and it fails the test. H is an extra I3 mutant: an entry with neither key is caught in the suite before any real run.

Real probe runs. I made these myself after 05 existed, at e4c19dd with the final `recorded` values, from my own worktree. They ran one after the other; my mutant runs overlapped part of the HEAD run, so its seconds are high. Lines are shown without the `FAILED` detail lines, and the shared check_pipeline reason is shortened to `(_CP_REASON)` here only; the raw files have the full text.
```
$ python3 scripts/probe_guardrails.py --ref origin/main; echo "exit $?"    (UTC 01:30:18 -> 01:34:23)
ref origin/main = 00e5ab65230fa23bce001047b6ec6d47748c8c99
baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors, 0 skipped; 34.4 s
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_leading_edge_100_days_blocks failed: yes; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 102.9 s
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_interior_gap_180_blocks failed: yes; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 35.1 s
baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors, 0 skipped; 1.4 s
RI-013-067-1b (RI-013): 1 failed, 16 passed, 0 errors, 0 skipped; target tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict failed: yes; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; code check: n/a (tests/test_diff_reports.py runs scripts/diff_reports.py as REPO/scripts/diff_reports.py (SCRIPT), REPO from tests/conftest.py); 2.8 s
baseline tests/test_missing_inputs.py: 0 failed, 23 passed, 0 errors, 0 skipped; 2.1 s
RI-002-046-tickers-key (RI-002): 1 failed, 22 passed, 0 errors, 0 skipped; target tests/test_missing_inputs.py::test_ticker_fields_cover_file_and_code failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 22 passed; code check: n/a (config/tickers.json is data: tests/test_missing_inputs.py test_ticker_fields_cover_file_and_code reads tickers.json from Path(__file__).resolve().parents[1]); 3.8 s
baseline tests/test_pipeline_check.py: 0 failed, 90 passed, 0 errors, 0 skipped; 16.9 s
RI-007-064-work-py (RI-007): 8 failed, 82 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_research_only_work_py_is_research_code failed: yes; HOLDS; recorded 2026-11-20 (078/05): 8 failed, 82 passed; code check: n/a (_CP_REASON); 33.2 s
RI-009-037-clash-line (RI-009): 1 failed, 89 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_same_id_on_main_and_open_branch_is_a_clash failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (_CP_REASON); 17.5 s
RI-010-049-rules-line (RI-010): 1 failed, 89 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_rules_branch_is_reported failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (_CP_REASON); 19.0 s
RI-011-052-merge-tree (RI-011): 1 failed, 89 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_criss_cross_branch_lists_only_its_own_changes failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (_CP_REASON); 21.6 s
baseline tests/test_webull_sandbox.py: 0 failed, 18 passed, 0 errors, 0 skipped; 4.0 s
RI-012-059-bare-429 (RI-012): 1 failed, 17 passed, 0 errors, 0 skipped; target tests/test_webull_sandbox.py::test_429_inside_other_text_is_not_retried failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 17 passed; code check: ccbot.broker.webull_sandbox is ccbot/broker/webull_sandbox.py in the worktree; 8.0 s
TOTAL: 9 probes, 9 hold, 0 not held, 0 anchor missing, 0 error; 244.2 s
exit 0

$ python3 scripts/probe_guardrails.py --ref HEAD; echo "exit $?"    (HEAD = e4c19dd, UTC 01:34:23 -> 01:40:00)
ref HEAD = e4c19dd1e015cc0aa972679435a9e28ebfbda859
baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors, 0 skipped; 38.3 s
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, ...; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 110.3 s
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, ...; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; ...; 37.4 s
baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors, 0 skipped; 1.3 s
RI-013-067-1b (RI-013): 1 failed, 16 passed, ...; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; code check: n/a (tests/test_diff_reports.py runs ...); 2.8 s
baseline tests/test_missing_inputs.py: 0 failed, 23 passed, 0 errors, 0 skipped; 1.9 s
RI-002-046-tickers-key (RI-002): 1 failed, 22 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 22 passed; code check: n/a (config/tickers.json is data: ...); 3.7 s
baseline tests/test_pipeline_check.py: 0 failed, 213 passed, 0 errors, 0 skipped; 32.0 s
RI-007-064-work-py (RI-007): 8 failed, 205 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 8 failed, 82 passed; code check: n/a (_CP_REASON); 64.0 s
RI-009-037-clash-line (RI-009): 1 failed, 212 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (_CP_REASON); 31.5 s
RI-010-049-rules-line (RI-010): 1 failed, 212 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (_CP_REASON); 35.2 s
RI-011-052-merge-tree (RI-011): 1 failed, 212 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (_CP_REASON); 38.0 s
baseline tests/test_webull_sandbox.py: 0 failed, 18 passed, 0 errors, 0 skipped; 7.3 s
RI-012-059-bare-429 (RI-012): 1 failed, 17 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 17 passed; code check: ccbot.broker.webull_sandbox is ccbot/broker/webull_sandbox.py in the worktree; 13.0 s
TOTAL: 9 probes, 9 hold, 0 not held, 0 anchor missing, 0 error; 336.4 s
exit 0
```
- Both refs: 9 of 9 HOLDS and exit 0, the same as 05's runs (226.7 s / 278.3 s).
- Every target is hit (`failed: yes`), and the per-file counts match 05's on both refs.
- No ANCHOR MISSING on either ref, so all 18 anchor counts are 1 (RI-001 feasibility re-measured).
- `grep -c "recorded @REC"` on both outputs → 0.
- After the runs, `git worktree list` shows only the repo, my `078-I3/wt` (removed after the runs with `git worktree remove`) and another agent's `wt32`. `git status` in the repo is clean.
- The a1-auditor.md "about 4 minutes" holds: main took 244.2 s ≈ 4.1 min under partial load, and 226.7 s in 05.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat HEAD~1 HEAD`: .claude/agents/a1-auditor.md, scripts/probe_guardrails.py, tests/test_probe_guardrails.py, work/078/05-build-report.md, logs/implementation/2026-11-20.md; none is ccbot/realtest.py or a TRIGGER file/dir, and the probes change TRIGGER files only inside their own detached worktree)

## Recurring issues checked (step 0)
Recurring issues checked: RI-014, RI-001, RI-002, RI-007, RI-009, RI-010, RI-011, RI-012, RI-013, RI-008, RI-006, RI-004, RI-005, RI-003
- RI-014 (OPEN): the repo is not shallow (`false`), so the test_pipeline_check baselines were green on both refs (90 / 213 passed). 078 adds no git walk. The shallow case would give a loud ERROR (C4), never a HOLDS. The fix is in 079, which must keep `test_shipped_probes_well_formed` green.
- RI-001 (ESCALATED in its header): I re-measured the feasibility numbers. 9/9 anchors count 1 on both refs (both runs are free of ANCHOR MISSING; the well-formed test checks the working tree), 9/9 target defs exist, 5/5 reason basenames pass (mutant F3 is live), and 9/9 hold. The numbers cited in 04 and 05 match.
- RI-002 (GUARDED; the request's link): a skipped target can no longer read as a pass. The 074 surviving mutant A now fails 2 tests, mutant B fails s2, and s3/classify (ii) pin the XPASS shapes. No default was removed in this item. Mutants A and B are its "put the bad default back" probes, and both fail. N3 (tickers.json key) holds on main.
- RI-007, RI-009, RI-010, RI-011: each now has a probe (N5, N4, N6, N1) that HOLDS on main and on the branch. A1 should copy the status lines from 05 to main.
- RI-012 (step 3): `classify` and the baseline check read junit tag names, not free text. The new code adds no substring matching of error or reply text; the JSON message is formatted, not matched. So the negative-test rule does not apply. N2 probes 059's own negative test, and it holds.
- RI-013: 067-1b still holds and now prints its own reason.
- RI-008: python3.11 compile test passed (not skipped). The new f-strings use no same-quote nesting.
- RI-006: every count above is pasted from a command.
- RI-004/RI-005: TOTAL sums re-derived (5 = 0 + 1 + 0 + 4; 13 unchanged; 9 = 9 hold).
- RI-003: n/a.

Item 062 (simulator must use the bot's pickers): n/a, no simulator or replay. Rule-text check (001): no strategy rule changes. The a1-auditor.md process text changes in this item.

## Pipeline line (step 2)
check_pipeline line: `078: awaiting A1 (FULL)` (exit 0, run after this file and the --log line were written)

## Sent back / sent to Audit
Sent to Audit (07-audit-task.md). Nothing is sent back. The RULES change in .claude/agents/a1-auditor.md needs the person's OK in PR review.
