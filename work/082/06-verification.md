# 06 Verification - 082
Verdict: FAIL (round 1)
Sent back to: I2

## I1 audit (plan vs research)
04 follows 03's map steps 1-10 row by row (04 Rule trace has one row per map step, per changed fact-check row and per Missing-inputs row). The changes it makes are sourced and argued:
- Change 1 (fixture helpers write a Suite line). R3 missed this. 04 cites `_item`, `_rd_item` and the 05 rewrite sites. I2's baseline runs confirm it was needed.
- Change 2 (S2 is its own function). Reason: `test_shipped_probes_well_formed` matches `def <name>(`.
- Change 3 (S0 and W added). These are absent-input cases that 03 did not cover.
- Change 4 (marker order).
- Change 5 (SUITE_FROM = max(87, `--next-id`), moved to I2).
- Change 6 (the subject rule covers only the commit that adds a log line). This narrows 03 step 8's "Every step commit". 04 gives the reason: an earlier code commit has no `--log` line to copy.
- Change 7 (the e813e1f subject is read by I2).

The only drop is F19 / FOR 3(e), and 03 dropped it too. I found no unsourced additions. One gap is shared by 03 and 04 (see I2 audit, finding 1): neither lists a negative fixture for `Suite:` appearing inside other text. 04's RI-012 line covers only the compare (whole-string `!=`) and never the line reader `line.startswith("Suite:")`.

## I2 audit (build vs plan)
I compared `git show daa5d22` with 04 Files 1-9, line by line:
- check_pipeline.py: SUITE_FROM = 87, comment as planned. `_last_log_line` and `_suite_lines` are in the plan's exact form. The `incomplete()` block has the three reasons, the one-line anchor `            elif suites[0] != field:` and a one-call 084 gate shaped like the VERDICT gate. There is one docstring paragraph. `log_fields_ok`, `_md_lines`, `SHALLOW_LINE`, `_logged` and the 081/084/086 code are unchanged.
- probe_guardrails.py: RECORDED, `_recorded_marker` (change-4 order), the marker in `_probe_all`, the comment, and the new last entry.
- Tests and texts: all as planned.
- RULE_PATHS diffs are additions only. `git diff --word-diff` shows two removed words, both planned rewrites: the end of the `incomplete()` docstring and "printed only." in the probe comment.
- Counts: `git diff --stat HEAD~1 HEAD -- . ':!work' ':!logs'` gives 9 files changed, 329 insertions(+), 24 deletions(-), as 05 says.
- 05 `Suite:` line = I2 log field = `672 passed, 1 skipped in 90.14s (0:01:30)`.

05's 5 deviations, each checked:
1. Probes ran in a scratch clone. Now moot: the build is committed and I re-ran `--ref HEAD` on daa5d22 (below). The I2 line (01:37) comes before commit 01:38:09, and LOG TIME is none.
2. The plan's mutant `state != "in"` is equivalent. Confirmed: it survives in my run too (304 passed). A fence opener or closer starts with 0-3 spaces and a backtick or tilde, never `Suite:`. The "state ignored" mutant fails S5.
3. `_batch_item(full=True)` writes a Suite line. Fixture text only, and no assertion changed (diff read).
4. S13 is a one-commit repo, not 084's two-branch shape. Its assertions match the plan's, and the gate-removed mutant fails S13.
5. Docstring placement. Fine.

Connectivity: every new function has a caller (`_suite_lines` and `_last_log_line` are called only from `incomplete()`; `_recorded_marker` from `_probe_all`; RECORDED from the marker and from the format test). Every branch has a named result.

**Finding 1 (FAIL, item 059 / RI-012 rule in i3 step 3): no negative test for `Suite:` inside other text.**
- `_suite_lines` classifies 05 lines by the code word `Suite:` with `line.startswith("Suite:")`. Being at column 0 is the whole rule: i2-builder.md now tells I2 to "Write the label inline in backticks elsewhere in 05".
- No fixture has `Suite:` inside a line, or an indented ` Suite:` line, outside a fence. So two mutants in `_suite_lines` survive the whole test file:
  - `"Suite:" in line` → `304 passed in 37.82s`
  - `line.lstrip().startswith("Suite:")` → `304 passed in 39.10s`
- The case is real. 082's own 05 has 11 "out" lines containing `Suite:`. Only one of them is the column-0 label:

```
fixed: ['672 passed, 1 skipped in 90.14s (0:01:30)']
in-mutant count: 11
```

  Under the `in` mutant, every future 05 that writes the label inline (as the new i2 text says to) would be INCOMPLETE. That would be loud, but nothing in the suite pins it.
- Fix for I2 (tests only, no code change): add a fixture S14. Its 05 has the column-0 line `Suite: 1 passed` and also:
  - a prose line `the \`Suite:\` line above is copied as printed`
  - a list item `- \`Suite: 2 passed\` was round 1`
  - an indented line `   Suite: 2 passed`

  It expects `INCOMPLETE: none`. Then show that both mutants above fail it, in a scratch worktree, and paste the counts in 05. Re-run the suite and refresh 05's `Suite:` line and the I2 log field to match.

Not a finding, for Audit: the build commit daa5d22's subject is `Item 082: I2 build - ...`, not `Item 082: ` + the I2 `--log` line, which is the subject rule this commit itself adds to run-item.md. The rule was not in force before this commit, and no check reads commit text (text pin only, 05 Known limits). The next 082 commit should follow it.

## Tests re-run (output)
Full suite in the scratch worktree /tmp/claude-0/wt082 at daa5d22 (clean, `git status --porcelain` 0 lines):
```
$ python3 -B -m pytest -q -p no:cacheprovider | tail -3
........................................................................ [ 96%]
.........................                                                [100%]
672 passed, 1 skipped in 88.69s (0:01:28)
$ python3 -B -m pytest -q -p no:cacheprovider -rs | grep -i SKIP
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
```
`test_every_py_compiles_on_oldest_python` ran (not skipped: python3.11 is on PATH, python3.10 is not). tests/test_safety.py: `9 passed in 0.99s`. In the repo: `python3.11 -m py_compile scripts/check_pipeline.py scripts/probe_guardrails.py tests/test_pipeline_check.py tests/test_probe_guardrails.py tests/test_real_data_field.py` → ok. `git rev-parse --is-shallow-repository` → false.

check_handoff (03 exists):
```
$ python3 scripts/check_handoff.py 082
sources count (unique URLs in 01-research.md): 6
fact-check rows: 75
totals line: 75 rows -> 64 as-is, 11 fixed, 0 removed
PASS
exit 0
```

Probes, in /tmp/claude-0/wt082 at daa5d22 (exit 0; FAILED detail lines left out, they match 05 run 2):
```
$ python3 -B scripts/probe_guardrails.py --ref HEAD
ref HEAD = daa5d22a402ea4012849786e1f86b5762f1ff64b
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, ...; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; ...
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, ...; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; ...
RI-013-067-1b (RI-013): 1 failed, 16 passed, ...; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; ...
RI-002-046-tickers-key (RI-002): 1 failed, 22 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 22 passed; ...
RI-007-064-work-py (RI-007): 8 failed, 296 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 8 failed, 82 passed; ...
RI-009-037-clash-line (RI-009): 1 failed, 303 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; ...
RI-010-049-rules-line (RI-010): 1 failed, 303 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; ...
RI-011-052-merge-tree (RI-011): 1 failed, 303 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; ...
RI-012-059-bare-429 (RI-012): 1 failed, 17 passed, ...; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 17 passed; ...
RI-006-082-suite (RI-006): 5 failed, 299 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_suite_line_dropped_middle_is_incomplete failed: yes; HOLDS; recorded 2026-11-21 (082/05): 5 failed, 299 passed; ...
TOTAL: 10 probes, 10 hold, 0 not held, 0 anchor missing, 0 error; 340.6 s
exit 0
```
There is no `(live differs)` or `(recorded unreadable)` marker. The full output is in /tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3-082-probe.txt.

Mutations:
- Where: a scratch clone of the worktree at daa5d22 (/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3-082-mut), with `git checkout -- .` before each mutant.
- Script: /tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3tools/mutate.py. It is I2's 27 anchor pairs, which I read against the code, plus 4 of mine (`I3:`).
- Each run is the whole named test file, with PYTHONDONTWRITEBYTECODE=1.
```
compare removed (scripts/check_pipeline.py): 5 failed, 299 passed in 38.61s; target test_suite_line_dropped_middle_is_incomplete failed: yes
field in suite (scripts/check_pipeline.py): 1 failed, 303 passed in 35.59s; target test_suite_line_part_of_field_is_incomplete[S3-tail] failed: yes
suite in field (scripts/check_pipeline.py): 1 failed, 303 passed in 36.51s; target test_suite_line_part_of_field_is_incomplete[S4-note] failed: yes
first wins (scripts/check_pipeline.py): 1 failed, 303 passed in 37.03s; target test_two_suite_lines_are_incomplete failed: yes
last wins (scripts/check_pipeline.py): 1 failed, 303 passed in 38.22s; target test_two_suite_lines_are_incomplete failed: yes
fence ignored (no state test) (scripts/check_pipeline.py): 1 failed, 303 passed in 38.23s; target test_suite_line_inside_fence_is_not_read failed: yes
fence: state != 'in' (plan's form) (scripts/check_pipeline.py): 304 passed in 38.13s; target test_suite_line_inside_fence_is_not_read failed: NO
fallback to earlier well-formed I2 (scripts/check_pipeline.py): 1 failed, 303 passed in 39.44s; target test_suite_with_malformed_last_i2_line_never_falls_back failed: yes
first I2 line (scripts/check_pipeline.py): 2 failed, 302 passed in 36.25s; target test_suite_compared_with_last_i2_line failed: yes
>= -> > (scripts/check_pipeline.py): 1 failed, 303 passed in 36.40s; target test_suite_line_dropped_middle_is_incomplete failed: yes
cutoff removed (scripts/check_pipeline.py): 2 failed, 302 passed in 37.64s; target test_suite_below_cutoff_not_checked failed: yes
084 gate removed (scripts/check_pipeline.py): 1 failed, 303 passed in 36.39s; target test_suite_gate_follows_rule_file_of_05_commit[S13-not-seen] failed: yes
{n,} -> {n} (scripts/check_pipeline.py): 1 failed, 303 passed in 37.00s; target test_i3_verdict_reader[longer-close] failed: yes
_logged no left pipe (scripts/check_pipeline.py): 1 failed, 303 passed in 35.81s; target test_uncommitted_step_with_lookalike_log_lines_is_listed failed: yes
SHALLOW fullmatch -> match (scripts/check_pipeline.py): 1 failed, 303 passed in 37.16s; target test_shallow_file_unreadable_not_checked failed: yes
SHALLOW fullmatch -> search (scripts/check_pipeline.py): 1 failed, 303 passed in 36.14s; target test_shallow_file_unreadable_not_checked failed: yes
{40} -> {40,} (scripts/check_pipeline.py): 1 failed, 303 passed in 37.02s; target test_shallow_file_unreadable_not_checked failed: yes
recorded deleted from a shipped entry (scripts/probe_guardrails.py): 1 failed, 13 passed in 7.69s; target test_shipped_probes_well_formed failed: yes
live-differs branch removed (scripts/probe_guardrails.py): 1 failed, 13 passed in 7.93s; target test_recorded_failed_count_differs_is_marked failed: yes
compare failed+passed (scripts/probe_guardrails.py): 1 failed, 13 passed in 7.57s; target test_recorded_failed_count_same_is_not_marked failed: yes
compare full string (scripts/probe_guardrails.py): 1 failed, 13 passed in 6.34s; target test_recorded_failed_count_same_is_not_marked failed: yes
live n/a branch removed (scripts/probe_guardrails.py): 1 failed, 13 passed in 6.11s; target test_recorded_without_live_results_is_na failed: yes
a1 marker clause deleted (.claude/agents/a1-auditor.md): 1 failed, 13 passed in 6.24s; target test_a1_text_marks_probe_markers_as_information failed: yes
a1 unshallow sentences deleted (.claude/agents/a1-auditor.md): 1 failed, 303 passed in 34.73s; target test_unshallow_sentence_same_in_three_files failed: yes
run-item step-5 sentence deleted (.claude/commands/run-item.md): 1 failed, 303 passed in 34.40s; target test_run_item_commit_subject_rule failed: yes
run-item I2 sentence deleted (.claude/commands/run-item.md): 1 failed, 303 passed in 35.47s; target test_run_item_commit_subject_rule failed: yes
template Suite line deleted (templates/build-report.md): 2 failed, 302 passed in 36.11s; target test_suite_label_in_template_and_i2_text failed: yes
I3: Suite: anywhere in line (scripts/check_pipeline.py): 304 passed in 37.82s; target ? failed: NO
I3: indented Suite: accepted (scripts/check_pipeline.py): 304 passed in 39.10s; target ? failed: NO
I3: no I2 line compared as empty field (scripts/check_pipeline.py): 11 failed, 293 passed in 38.55s; target test_suite_with_no_i2_line_adds_no_suite_entry failed: yes
I3: recorded unreadable treated as match (scripts/probe_guardrails.py): 1 failed, 13 passed in 7.82s; target test_holds_exits_0 failed: yes
```
Results:
- My counts match 05's for all 27 of I2's mutants. 26 fail their target. The one survivor is the equivalent `state != "in"` mutant (deviation 2).
- 2 of my 4 survive (finding 1).
- RI-002 step: 082 removes no default, so there is no default to put back. Instead I made the absent value count as a match: no I2 line read as an empty field. That fails S8 and 10 other tests. An unreadable `recorded` treated as matching fails `test_holds_exits_0`.
- The data-window edge checks (before the first value, after the last, gaps) do not apply: 082 reads no data series. The cutoff edges SF and SF-1 are pinned by S1/S2 and S10.
- The item 062 picker rule does not apply: no simulator or replay is involved.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat HEAD~1 HEAD`: .claude/agents/a1-auditor.md, .claude/agents/i2-builder.md, .claude/commands/run-item.md, scripts/check_pipeline.py, scripts/probe_guardrails.py, templates/build-report.md, tests/test_pipeline_check.py, tests/test_probe_guardrails.py, tests/test_real_data_field.py; no TRIGGER path, no ccbot/realtest.py change)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014, RI-012, RI-002, RI-006, RI-007, RI-008, RI-009 (what each check found:)
- RI-001 (ESCALATED): 082 adds one selecting rule, the Suite line. 05 gives its counts: 0 of 82 05 files in scope, 10 of 10 RECORDED. I re-ran the probes: all 10 `recorded` values fullmatch, since there is no `(recorded unreadable)` marker.
- RI-010 (ESCALATED): this 06 has its RI and check_pipeline lines. The log line is written by `--log`. The I2 line is timed before its commit (LOG TIME none, LOG BATCH none).
- RI-014 (OPEN): `--is-shallow-repository` is false. The unshallow sentence is pinned in 3 files, and its deletion mutant fails. The 3 SHALLOW mutants fail.
- RI-012 (GUARDED, checked by step 3): FAIL. See finding 1: the `Suite:` reader has no negative test with the code word inside other text.
- RI-002: absent inputs are not read as matches (my 2 mutants fail).
- RI-006: every count here is copied from command output.
- RI-007: Scope FULL. 01-05 exist, and SKIPPED none.
- RI-008: py311 compile ok, and the compile test ran.
- RI-009: all mutations and probes ran outside the repo.

## Pipeline line (step 2)
check_pipeline line: `082: in progress (FULL: next 06)`
Run in /home/claude/cover-calls before this file was written (exit 0): INCOMPLETE none, SKIPPED none, UNTRACKED CHANGE none, LOG TIME none, LOG BATCH none (082 not named), RULE NOT SEEN only 083's line.

## Sent back / sent to Audit
Sent back to I2 (round 1): add the S14 negative fixture (finding 1), show that the `"Suite:" in line` and `line.lstrip().startswith` mutants fail it, re-run the suite, and refresh 05's `Suite:` line and the I2 field. No code change is expected. No 07: not sent to Audit.
