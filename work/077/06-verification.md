# 06 Verification - 077
Verdict: FAIL (round 1)
Sent back to: I2

All test runs, mutations and probes were made in my own scratch worktree of the build commit 3006b73 (`scratchpad/077-I3/wt`, detached), never in the repo. The stale `scratchpad/077-I3` from the cut-off run was deleted first and `git worktree prune` was run. The build diff checked is 3006b73^ (f96aa5e) .. 3006b73.

## I1 audit (plan vs research)
- 03 is READY. `python3 scripts/check_handoff.py 077`:
  ```
  sources count (unique URLs in 01-research.md): 4
  fact-check rows: 74
  totals line: 74 rows -> 64 as-is, 10 fixed, 0 removed
  PASS
  ```
- Every 03 map step (1-6), decision D1-D5, Exact rule (`_md_lines`, `uncommitted_steps`), correction and Missing-inputs row is in 04's Rule trace with a plan line. One test is DROPPED with a reason (branch `git show` failure needs a corrupted object store; written as a docstring gap).
- 04's additions beyond 03 are each sourced and reasoned in "Changes against 03":
  - change 1, the a1-auditor.md clauses (RI-010: no reader for the two new lines; .claude/ is in RULE_PATHS, so it goes to the person in PR review);
  - changes 2 and 4, surviving mutations closed with extra T5/T-P3/T4 ids;
  - change 3, the PRE_A1_LINE sentence that conflicted with 03's own formula, kept as a known gap;
  - changes 5-7, the extra grep, the P5f shallow assert, P5h/P5b and the docstrings.
  No unsourced addition.
- Gap in 04, the cause of this FAIL: its RI-012 line credits "one shared A1 reader and log regex", but no test puts the A1 pattern or the log-line pattern inside other text (see problem 1).

## I2 audit (build vs plan)
- Files in 3006b73: .claude/agents/a1-auditor.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, tests/test_real_data_field.py (the 4 planned files), plus work/077/05-build-report.md and the I2 log line in logs/implementation/2026-11-20.md. Nothing outside the plan.
- scripts/check_pipeline.py, line by line against 04 Files 1:
  - Step 2: `failed` is collected right after `classify`, filtered by `skipped` after the 062 merge loop, and added to the dict. Its docstring key is there. `main` prints `BRANCH FAIL:` in its own loop after BRANCH SKIPPED (05 deviation 3, no behaviour change). The exit expression has no branch term. The module docstring reads "Three more lines", has the BRANCH FAIL entry with 03's text, and gap (x) is removed.
  - Step 3: `_a1_results` is used at L436, L443 and L717. The new I3 FAIL branch's condition and detail text match 04 exactly. Gap (w) is rewritten with the PRE_A1_LINE/LEGACY wording.
  - Step 4: `FENCE_OPEN` and `_md_lines` match 03 Exact rules (comments stripped first, `fullmatch` opener, backtick-info rule, closer `" {0,3}C{n,}[ \t]*"`). `i3_verdict` reads `out` rows only. In `_field_gap` the heading is found on an `out` row, the section ends at an `out` `## ` row, and "unclosed" is returned only in the for-else when `open_at_end` is True. Docstrings and the two known gaps are there.
  - Step 5: `_log_text`/`_logged` are factored out, and `incomplete()` keeps 076's lines. `uncommitted_steps` matches 03 Exact rules: one `ls-tree -r --name-only HEAD -- work/` call, no `--full-tree`, `(msg, True)` on failure, no `_walk`. The only addition is a `d.is_dir()` skip (05 deviation 2). `main` prints the line after REAL-DATA FIELD and has the exit term. The docstring entry has gaps (a)-(c).
- tests: every planned test and assert is present (BF1-BF3, the 038 test asserts, T5 full detail, T8, T-P3 with 180 and 185, T-P3b with 184 and 017, P5a-P5h, the head-run and repo-test asserts, 9 T4 ids, 4 t12 ids, 2 t23 strings, `test_a1_text_names_077_lines`).
- a1-auditor.md: both clauses use 04's exact text.
- Connectivity, re-done by grep: `_md_lines` is called at L357/L805, `_a1_results` at L436/L443/L717, `_log_text`/`_logged` at L491/L499/L512/L514, `uncommitted_steps` at L982, and `b["failed"]` at L1039. The new lines' consumer is A1 job B (pinned by `test_a1_text_names_077_lines`).
- Real tree, the base checker (3006b73^'s check_pipeline.py) vs the head, same tree: base exit 0, head exit 0, `diff`:
  ```
  93a94
  > UNCOMMITTED STEP: none
  ```
  This matches 05. BRANCH FAIL lines: 0.
- Python: `python3.11 -m py_compile` on the 3 changed .py files gives no output. `test_every_py_compiles_on_oldest_python` PASSED (python3.11; there is no python3.10 on PATH). It did not skip.

## Tests re-run (output)
Full suite in the head worktree:
```
553 passed, 1 skipped in 100.08s (0:01:40)
```
The skip is `tests/test_calendar.py:110: could not import 'exchange_calendars'` (as before). `-k t23`: `3 passed, 36 deselected in 0.03s`.

My mutations, each alone in the head worktree and restored after its run (`scratchpad/077-I3/tools/mut.py`; `git -C wt status` clean afterwards):
```
t23 i3 even if->unless | 1 failed, 2 passed, 36 deselected in 0.04s
t23 run-item never give->you may give | 1 failed, 2 passed, 36 deselected in 0.04s
BF in exit | 2 failed, 18 passed, 191 deselected in 8.50s
BF skipped filter dropped | 1 failed, 210 deselected in 2.89s
P3 if a1: | 1 failed, 1 passed, 209 deselected in 2.85s
P3 a1[0] | 1 failed, 210 deselected in 0.47s
fence closer any length | 2 failed, 248 deselected in 0.34s
fence closer lstrip | 1 failed, 210 deselected in 0.12s
backtick-info dropped | 1 failed, 210 deselected in 0.11s
ls-tree fail -> none | 1 failed, 210 deselected in 0.24s
uncommitted exit term dropped | 1 failed, 210 deselected in 0.22s
uncommitted no log test | 1 failed, 210 deselected in 0.18s
uncommitted ls-files (index) | 1 failed, 210 deselected in 0.26s
PROBE _a1_results unanchored | 553 passed, 1 skipped in 88.87s (0:01:28)
PROBE _logged substring | 553 passed, 1 skipped in 99.58s (0:01:39)
PROBE _logged no trailing pipe | 553 passed, 1 skipped in 103.71s (0:01:43)
```
The 13 planned mutations I re-ran are all killed, which agrees with 05. The 3 RI-012 probes survive the whole suite:
- `re.findall(r"A1 result:\s*(\w+)", text)`, unanchored;
- `item in text and agent in text`;
- `\|\s*{agent}\s*\|\s*{item}` with no trailing `\|`.

The code as built is right. A direct probe on 3006b73 gives:
- `_a1_results("x\nsee A1 result: PASS (quoted)\n")` → `[]`;
- `_logged` → False for `| R1 | 1510 |`, for `| R2 | 151 | see R1 notes` and for `| I2 | 151 | R1 x`;
- `_logged` → True for `| R1 | 151 |`.

The substring mutant gives True for all four. Nothing pins this behaviour.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 3006b73^ 3006b73`: .claude/agents/a1-auditor.md, logs/implementation/2026-11-20.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, tests/test_real_data_field.py, work/077/05-build-report.md; no TRIGGER or TRIGGER_DIRS path)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-014, RI-002, RI-007, RI-008, RI-009, RI-010, RI-012, RI-013 (RI-003, RI-004, RI-005, RI-006, RI-011 not applicable: no calendar, worked example, hand total or branch-diff change)
- RI-001 (ESCALATED): no trading filter or window. The counts were re-measured: 0 BRANCH FAIL and `UNCOMMITTED STEP: none` on the real tree, and 1 of 1 t23 clause hit each (mutations kill t23). The detectors have non-zero fixture counts (BF1/BF2/T8, P5a/P5b/P5e/P5f/P5h, T-P3).
- RI-014 (OPEN): `_walk` is neither called nor changed (diff read). P5f asserts `--is-shallow-repository` == `true`.
- RI-002: a failing ls-tree is never `none`. The "ls-tree fail -> none" mutation fails P5h. A missing logs/ folder lists the file (P5b).
- RI-007: SKIPPED wins over BRANCH FAIL (BF3; filter-drop mutation killed). The 053 new-item rule is kept.
- RI-008: py_compile on 3.11, and the oldest-Python test passed.
- RI-009: all work was in the scratch worktree.
- RI-010: the A1 duty for both new lines is pinned by `test_a1_text_names_077_lines`.
- RI-012: **FAIL**, problem 1. The fence classifier has negative ids with the pattern inside other text (`info`, `backtick-info`, `4-space-close`). The two text readers that 077 makes shared and gives new decisions to have none:
  - `_a1_results` decides the new "06 FAIL after A1 PASS" detail;
  - `_logged` decides whether a step file is a cut-off run for UNCOMMITTED STEP.
- RI-013: whole-output diff of the real tree, base vs head, pasted above.

## Pipeline line (step 2)
check_pipeline line: `077: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))`

## Sent back / sent to Audit
Sent back to I2 (tests only; the code logic is right). No 07 this round.
1. **RI-012 / item 059: there are no negative tests for the two text readers that 077's new decisions rest on.** All three probes above pass the full suite (553 passed). Add the following, then show in 05 that each of the three probe mutations fails at least one of them:
   - (a) `_a1_results` / T-P3: an item with 06 FAIL whose 07 holds the pattern only inside other text, e.g. `x\nsee A1 result: PASS (quoted)\n` (and/or an indented `  A1 result: PASS`). Want the old detail `needs a later PASS round in 06 (item 071)`, not the new-item detail. This kills the unanchored mutation.
   - (b) `_logged` / UNCOMMITTED STEP: a P5a variant where the logs hold lines with the agent and ID inside other text but no `| R1 | 151 |` line. For example `12:00 | R1 | 1510 | x`, `12:00 | R2 | 151 | see R1 notes` and `12:00 | I2 | 151 | R1 x` (plus `logged=False` for 151's R1). Want the exact P5A line and exit 1. This kills the substring and no-trailing-pipe mutations.

   No change to scripts/check_pipeline.py is needed. Report the new test count and the full suite in 05. 04 already names RI-012 for these readers, so this is the test that line promised, not a new rule.
