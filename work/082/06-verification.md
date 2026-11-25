# 06 Verification - 082
Verdict: PASS (round 2; earlier rounds: FAIL round 1)
Sent back to: none

Head verified: 85bf4c4 ("Item 082: 02:06 | I2 | 082 | 1 files changed | tests 1 failed, 672 passed, 1 skipped in 88.54s (0:01:28)"), branch daily-fixes/2026-11-20, parent 8a9f32a (my round 1 FAIL). `git diff --stat 8a9f32a HEAD`: logs/implementation/2026-11-21.md +1, tests/test_pipeline_check.py +11, work/082/05-build-report.md +65/-1. Outside work/, logs/ and tests/, the diff is empty, so round 2 changes no code. Scratch work: the clean worktree /tmp/claude-0/wt082b at 85bf4c4 (`git status --porcelain` 0 lines before and after, `--is-shallow-repository` false), and the clones `i3-082r2-{ctl,in,lstrip,probe}` in /tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/. Outputs are in the same folder: `i3-082r2-full.txt` and `i3-082r2-probe.txt` (at HEAD), and `i3-082r2-probe-green.txt` (scratch commit). All runs used python3 -B. In the repo I changed only this file, 07 and my log line.

## I1 audit (plan vs research)
Round 2 changes no plan: 04 is not in `git diff 8a9f32a HEAD`. The round-1 audit stands (see Round 1 below): 04 follows 03, and its 7 changes are sourced. Finding 1 was the gap shared by 03 and 04 (no negative fixture for `Suite:` inside other text). It was a test-only gap, and I2 closed it in the build, as I asked. No unsourced addition.

## I2 audit (build vs plan)
Round 2 is the one fixture I asked for in round 1 (finding 1). I checked it line by line against `git show 85bf4c4 -- tests/test_pipeline_check.py`:
- `test_suite_inside_other_text_is_not_read` (S14) uses `_suite_item`. Its 05 holds `x`, the column-0 line `Suite: 1 passed` and the three lines I named: the prose line ``the `Suite:` line above is copied as printed``, the list item ``- `Suite: 2 passed` was round 1`` and the indented line `   Suite: 2 passed`. It asserts `INCOMPLETE: none` and exit 0. The I2 field is `_suite_item`'s default `tests 1 passed`, so only the column-0 line is read, and it matches.
- No other line changed. 05's Round 2 section reports it accurately. File counts: 1 file changed outside work/ and logs/, which matches the I2 field `1 files changed`.
- 05's column-0 `Suite:` line, `1 failed, 672 passed, 1 skipped in 88.54s (0:01:28)`, equals the tests part of the I2 log field (02:06). `_suite_lines` on the committed 082/05 returns exactly that one line (spot check below), so 082's own 05 would pass its own check even though 082 < SUITE_FROM.
- The round-1 "for Audit" note is resolved. The round-2 commit subject is exactly `Item 082: ` + the I2 `--log` line, which is the run-item.md rule this item adds.
- The 1 failure (`test_repo_pipeline_has_no_skipped_items`) is the known repo state, `082: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))` (line 108 of my pytest output). This PASS round clears it once 06, 07 and my log line are committed: the test runs check_pipeline on a worktree of HEAD (item 066), so in the uncommitted tree it still fails. At scratch commit 823c059, which holds these files, tests/test_pipeline_check.py gives `0 failed, 305 passed` (probe baseline below). check_pipeline in the working tree gives exit 0 (see Pipeline line).

Connectivity: no new function or branch. S14 runs under pytest and reaches `_suite_lines` through `incomplete()`.

## Tests re-run (output)
Full suite in /tmp/claude-0/wt082b at 85bf4c4 (clean):
```
$ python3 -B -m pytest -q -p no:cacheprovider -rs
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
E         082: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
1 failed, 672 passed, 1 skipped in 89.46s (0:01:29)
real	1m29.855s
```
These are the same counts as 05's Suite line. `test_every_py_compiles_on_oldest_python` ran: the only skip is the calendar one, and python3.11 is on PATH (python3.10 is not). tests/test_safety.py: `9 passed in 0.85s`. `python3.11 -m py_compile tests/test_pipeline_check.py` → ok.

The S14 mutants, each in its own clone of the worktree at 85bf4c4. `_suite_lines` line 684, `if state == "out" and line.startswith("Suite:")]`, is replaced once in each clone (count asserted to be 1); ctl is unmutated. Command: `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py`:
```
== ctl
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 304 passed in 36.63s
== in            ("Suite:" in line)
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_suite_inside_other_text_is_not_read
2 failed, 303 passed in 36.33s
== lstrip        (line.lstrip().startswith("Suite:"))
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_suite_inside_other_text_is_not_read
2 failed, 303 passed in 40.77s
```
Both mutants that survived round 1 (`304 passed`) now fail S14, and S14 is the only test that each mutant breaks beyond ctl. The counts match 05 Round 2 exactly.

Spot check: `_suite_lines` run in the worktree on each line by itself:
```
'Suite: 1 passed' ['1 passed']
'the `Suite:` line above is copied as printed' []
'- `Suite: 2 passed` was round 1' []
'   Suite: 2 passed' []
'```\nSuite: 9\n```' []
'<!-- Suite: 9 -->' []
082 05: ['1 failed, 672 passed, 1 skipped in 88.54s (0:01:28)']
```
The inline-backtick and list lines kill `in`, and the indented line kills `lstrip`. Lines inside fences and comments stay unread.

check_handoff (03 exists), in the repo:
```
$ python3 scripts/check_handoff.py 082
sources count (unique URLs in 01-research.md): 6
fact-check rows: 75
totals line: 75 rows -> 64 as-is, 11 fixed, 0 removed
PASS
exit 0
```

Probes. Run 1 was at HEAD 85bf4c4 in /tmp/claude-0/wt082b. The 5 tests/test_pipeline_check.py probes give ERROR because that file's baseline is red: it is only the known repo test (082 at I3 FAIL). The other 5 hold. The lines that matter:
```
$ python3 -B scripts/probe_guardrails.py --ref HEAD
baseline tests/test_pipeline_check.py: 1 failed, 304 passed, 0 errors, 0 skipped; 35.4 s
RI-006-082-suite (RI-006): pytest not run; target tests/test_pipeline_check.py::test_suite_line_dropped_middle_is_incomplete failed: n/a; ERROR (baseline: exit 1, 1 failed, 304 passed, 0 errors, 0 skipped); recorded 2026-11-21 (082/05): 5 failed, 299 passed (live n/a); code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 0.0 s
TOTAL: 10 probes, 5 hold, 0 not held, 0 anchor missing, 5 error; 147.6 s
exit 1
```
Run 2 used a green baseline, as I2 did in round 1 (05 deviation 1). In a scratch clone of the worktree (i3-082r2-probe) I copied this 06 and 07 and ran `--log I3 082 "PASS | sent to audit: yes"` (written 02:14 in the clone only). I committed that as scratch commit 823c059; in the clone, check_pipeline gives `082: awaiting A1 (FULL)`, exit 0. FAILED detail lines are left out. RI-006-082-suite's 5 are test_suite_compared_with_last_i2_line, test_suite_line_dropped_middle_is_incomplete, both test_suite_line_part_of_field_is_incomplete cases and test_unfilled_template_suite_line_is_incomplete, the same 5 as 05:
```
$ python3 -B scripts/probe_guardrails.py --ref HEAD --repo <scratch clone>
ref HEAD = 823c0592df505f6e2fd0927c3895d38b1e845e68
baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors, 0 skipped; 26.0 s
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_leading_edge_100_days_blocks failed: yes; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 73.7 s
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_interior_gap_180_blocks failed: yes; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 24.0 s
baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors, 0 skipped; 1.0 s
RI-013-067-1b (RI-013): 1 failed, 16 passed, 0 errors, 0 skipped; target tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict failed: yes; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; code check: n/a (tests/test_diff_reports.py runs scripts/diff_reports.py as REPO/scripts/diff_reports.py (SCRIPT), REPO from tests/conftest.py); 2.0 s
baseline tests/test_missing_inputs.py: 0 failed, 23 passed, 0 errors, 0 skipped; 1.4 s
RI-002-046-tickers-key (RI-002): 1 failed, 22 passed, 0 errors, 0 skipped; target tests/test_missing_inputs.py::test_ticker_fields_cover_file_and_code failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 22 passed; code check: n/a (config/tickers.json is data: tests/test_missing_inputs.py test_ticker_fields_cover_file_and_code reads tickers.json from Path(__file__).resolve().parents[1]); 2.9 s
baseline tests/test_pipeline_check.py: 0 failed, 305 passed, 0 errors, 0 skipped; 35.0 s
RI-007-064-work-py (RI-007): 8 failed, 297 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_research_only_work_py_is_research_code failed: yes; HOLDS; recorded 2026-11-20 (078/05): 8 failed, 82 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 70.8 s
RI-009-037-clash-line (RI-009): 1 failed, 304 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_same_id_on_main_and_open_branch_is_a_clash failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 35.4 s
RI-010-049-rules-line (RI-010): 1 failed, 304 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_rules_branch_is_reported failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 36.1 s
RI-011-052-merge-tree (RI-011): 1 failed, 304 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_criss_cross_branch_lists_only_its_own_changes failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 38.1 s
baseline tests/test_webull_sandbox.py: 0 failed, 18 passed, 0 errors, 0 skipped; 1.9 s
RI-012-059-bare-429 (RI-012): 1 failed, 17 passed, 0 errors, 0 skipped; target tests/test_webull_sandbox.py::test_429_inside_other_text_is_not_retried failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 17 passed; code check: ccbot.broker.webull_sandbox is ccbot/broker/webull_sandbox.py in the worktree; 4.3 s
RI-006-082-suite (RI-006): 5 failed, 300 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_suite_line_dropped_middle_is_incomplete failed: yes; HOLDS; recorded 2026-11-21 (082/05): 5 failed, 299 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 37.2 s
TOTAL: 10 probes, 10 hold, 0 not held, 0 anchor missing, 0 error; 324.7 s
exit 0
```
No `(live differs)` and no `(recorded unreadable)` marker appeared. RI-006-082-suite is now `5 failed, 300 passed`, not `299`, because S14 adds one test that the probe mutant leaves green. `recorded` is compared on the failed count only, so this is correct and not a marker.

RI-002 step: round 2 removes no default. The round-1 absent-input mutants still apply unchanged: no code changed. The data-window edge checks and the item 062 picker rule do not apply (no data series, no simulator or replay). Text classifier (item 059 / RI-012): S14 is the negative test with the code word inside other text, and both substring/strip mutants fail it. This is what made round 1 FAIL, and it is now met.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 8a9f32a HEAD`: logs/implementation/2026-11-21.md, tests/test_pipeline_check.py, work/082/05-build-report.md; item total as in round 1: .claude/agents/a1-auditor.md, .claude/agents/i2-builder.md, .claude/commands/run-item.md, scripts/check_pipeline.py, scripts/probe_guardrails.py, templates/build-report.md, tests/test_pipeline_check.py, tests/test_probe_guardrails.py, tests/test_real_data_field.py; no TRIGGER path, no ccbot/realtest.py change)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014, RI-002, RI-006, RI-007, RI-008, RI-009, RI-012, RI-013 (what each check found:)
- RI-001 (ESCALATED): there is no new rule or window in round 2. The one selecting rule (Suite line) is unchanged, and its counts are in 05 round 1.
- RI-010 (ESCALATED): this 06 has its Verdict, Sent back, RI and check_pipeline lines, plus 07. My log line is written by `--log` after this file. The I2 02:06 line comes before its commit (02:07:10), and LOG TIME is none.
- RI-014 (OPEN): `--is-shallow-repository` is false in the worktree and in every clone. S14 uses no git.
- RI-002: no default was removed or added in round 2.
- RI-006: every count here is copied from command output. 05's Suite line equals the I2 field. The `recorded` values are compared on the failed count only, and no `(live differs)` marker appeared.
- RI-007: Scope FULL. 01-05 exist, and SKIPPED is none.
- RI-008: the compile test ran (not skipped), and the py311 compile of the changed test file is ok.
- RI-009: mutants, probes and the full run ran outside the repo. The repo tree is unchanged except for 06, 07 and the log.
- RI-012 (GUARDED): finding 1 is closed. S14 kills `"Suite:" in line` and `line.lstrip().startswith`.
- RI-013: no report effect, no realtest change.

## Pipeline line (step 2)
check_pipeline line: `082: awaiting A1 (FULL)` (run in /home/claude/cover-calls after this file, 07 and the log line; exit 0)

## Sent back / sent to Audit
PASS. Not sent back. Sent to Audit: work/082/07-audit-task.md.

## Round 1 (FAIL, kept for the record)
Verdict round 1: FAIL. Sent back to I2 (finding 1).

### I1 audit (plan vs research)
04 follows 03's map steps 1-10 row by row (04 Rule trace has one row per map step, per changed fact-check row and per Missing-inputs row). The changes it makes are sourced and argued:
- Change 1 (fixture helpers write a Suite line). R3 missed this. 04 cites `_item`, `_rd_item` and the 05 rewrite sites. I2's baseline runs confirm it was needed.
- Change 2 (S2 is its own function). Reason: `test_shipped_probes_well_formed` matches `def <name>(`.
- Change 3 (S0 and W added). These are absent-input cases that 03 did not cover.
- Change 4 (marker order).
- Change 5 (SUITE_FROM = max(87, `--next-id`), moved to I2).
- Change 6 (the subject rule covers only the commit that adds a log line). This narrows 03 step 8's "Every step commit". 04 gives the reason: an earlier code commit has no `--log` line to copy.
- Change 7 (the e813e1f subject is read by I2).

The only drop is F19 / FOR 3(e), and 03 dropped it too. I found no unsourced additions. One gap is shared by 03 and 04 (see I2 audit, finding 1): neither lists a negative fixture for `Suite:` appearing inside other text. 04's RI-012 line covers only the compare (whole-string `!=`) and never the line reader `line.startswith("Suite:")`.

### I2 audit (build vs plan)
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

### Tests re-run (output)
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

### Real-data effect (diff_reports output, pasted)
not required (`git diff --stat HEAD~1 HEAD`: .claude/agents/a1-auditor.md, .claude/agents/i2-builder.md, .claude/commands/run-item.md, scripts/check_pipeline.py, scripts/probe_guardrails.py, templates/build-report.md, tests/test_pipeline_check.py, tests/test_probe_guardrails.py, tests/test_real_data_field.py; no TRIGGER path, no ccbot/realtest.py change)

### Recurring issues checked (step 0)
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

### Pipeline line (step 2)
check_pipeline line: `082: in progress (FULL: next 06)`
Run in /home/claude/cover-calls before this file was written (exit 0): INCOMPLETE none, SKIPPED none, UNTRACKED CHANGE none, LOG TIME none, LOG BATCH none (082 not named), RULE NOT SEEN only 083's line.

### Sent back / sent to Audit
Sent back to I2 (round 1): add the S14 negative fixture (finding 1), show that the `"Suite:" in line` and `line.lstrip().startswith` mutants fail it, re-run the suite, and refresh 05's `Suite:` line and the I2 field. No code change is expected. No 07: not sent to Audit.
