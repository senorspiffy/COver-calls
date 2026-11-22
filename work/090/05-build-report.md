# 05 Build report - 090

Built on branch daily-fixes/2026-11-21, base HEAD d3aa031 (088 d6715d5 and 089 0ad4d62 already committed; `git diff --stat fd73de1 d3aa031 -- scripts/ tests/ .claude/ templates/` is empty). I re-read every line of 04's table by its text after 089 landed. All new readers go through 089's `_read`. `git rev-parse --is-shallow-repository` printed `false`.

File counts (item 012):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → `0` new
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → `7` changed (6 planned + `tests/test_real_data_field.py`, see Deviations 1)

## Changes made (file: what changed)
- `scripts/check_pipeline.py`:
  - Constants: `TIMED_FROM = 90`, `I2_TIMED`, `LOG_HINT_TIMED`, `SHALLOW_TEXT`, `VERDICT_OF` (03/04 patterns with VERDICT_LINE's `(?![ \t*]*[|/])` lookahead; 06 = VERDICT_LINE), `BATCH_STRICT`. `_TAIL`, `LOG_FORMAT`, LOG_TIME_EXCEPT, LOG_BATCH_EXCEPT, SUITE_FROM and `_rule_seen` are unchanged.
  - `log_fields_ok(..., timed=True)` and `log_hint(..., timed=True)`: from TIMED_FROM the I2 field must fullmatch I2_TIMED and the timed hint is used. `write_log` passes neither argument, so it stays numeric.
  - `incomplete(..., batch_nc=None)`:
    - TIMED gate on 05. Not seen: the pair `judged by untimed I2 form`. A None note: strict. Seen: the timed hint.
    - Any other bad I2 line keeps the TESTS gate (now an `elif`).
    - Step 2: a BATCH_STRICT reason (compared by equality) for an ID ≥ 90 gives `LOG BATCH not computable: <reason> (item 090)`, gated on 05 the same way. The not-seen pair is `LOG BATCH not computable as text only`.
    - The Suite guard reads the untimed form (Deviations 2).
  - `batch_log_items`: per-round I2 bound, placed after the `r[0] is None` check and before `first, last_i2`, and skipped for excepted items.
    - prev follows 086's order rule. Δ is whole minutes. A round is flagged when `round(t - 0.005, 3) >= (Δ+1)*60`, with the planned entry text.
    - An ID is appended to `flagged_ids` only once, also by the whole-item rule (Deviations 3).
  - New `_first_verdict`, new `_round_refusal` with rules (a), (b) and (c), and `write_log`'s new `elif sent:` branch (rule D is unchanged when the item was not sent back).
  - New `_is_shallow`, which `_anchor_env` now uses.
  - `late_log_lines(shallow)` returns False when shallow. `main_ahead(shallow)` returns None when shallow and the ref exists.
  - `open_branches(today, shallow=None)`: when shallow, `behind` is False, MAIN is skipped, every dict has `"shallow"`, and an unrelated ref gets the shallow error text.
  - `main`:
    - env is computed first, and `shallow = env == SHALLOW_TEXT`.
    - `batch` is computed before the item loop and passed as `batch_nc`.
    - New print lines: `MAIN AHEAD: not checked (...)`, `LOG TIME: not checked (...)`, and `  <ref>: not checked (...)<age>`.
    - The exit expression is unchanged.
  - Docstring updates: the TIMED_FROM paragraph, rule D replaced by the round rule (a)-(c), the LOG BATCH bound and the rewritten gaps (x)/(y), and the LOG TIME, MAIN AHEAD and OPEN BRANCHES shallow sentences with their known gaps (shared shallow base, refs already in main listed, single-branch clone). The MAIN AHEAD sentence explains why the exact shallow 0 was declined. The person's-waiver gap is in the docstring too (Deviations 4).
- `tests/test_pipeline_check.py`: the B0 fixture sweep (list below) and 22 new test functions, 31 collected cases (counted: `grep -c '^def test_'` after the `# Item 090` marker → 22; each name matched in `pytest --collect-only -q` → 31).
- `.claude/commands/run-item.md`: the L12 UNSHALLOW sentence is replaced. The L17 last sentence is replaced with 04's text.
- `.claude/commands/daily-audit.md`, `.claude/agents/a1-auditor.md`: the same new UNSHALLOW sentence, byte for byte (`test_unshallow_sentence_same_in_three_files`).
- `.claude/agents/i2-builder.md` L25: added "From item 090 (TIMED_FROM) the field must keep pytest's ` in <s>s` time; `--log` refuses it without one." It is pinned by `test_i2_and_run_item_texts_name_item_090`, which also pins the new run-item L17 text.
- `tests/test_real_data_field.py`: its two `Suite: 1 passed` literals now follow `FIELDS["I2"]` (`SUITE`). This was not planned (Deviations 1).

B0 sweep: tests edited for the timed field. The edits change fixture values only; no assertion's meaning changed.
1. `FIELDS["I2"]` → `1 files changed | tests 1 passed in 0.01s`. `_item`'s Suite line follows it.
2. `test_waived_steps_are_excused_and_printed`: item 105 → 085 (Deviations 4).
3. `test_log_refuses_item_without_request` (L464): the field is timed and the test gains `"item 047" in err`.
4. `test_orphan_log_line_is_reported` (L472): field timed.
5. `test_log_line_after_its_commit_is_flagged` (L502): field timed.
6. `test_recommitted_log_line_is_checked_against_new_commit` (L597): field timed.
7. `test_malformed_log_line_names_expected_format`: both I2 hint strings → the timed hint (item 150 ≥ 90).
8. `test_i2_summary_line_accepted`: item 150 → 089, so A5, A6 and `1 passed` keep their 076 meaning.
9. `test_completed_item_note_with_config_is_untracked`, `test_merge_bringing_untracked_commit_is_flagged`, `test_commits_before_cutoff_ignored`: their 05 Suite line is `1 passed in 0.01s` (3 tests).
10. `test_malformed_shallow_real_git_nothing_none` ((b)): field timed. Its assertions are unedited.
11. `NEW_I2_WANT` → the LOG_HINT_TIMED words (used by 5 tests: L2677, L2723, L2746, L2772 and INC_150).
12. `_defective`: 05 gains `## Test output\n1 passed in 0.01s`, so LOG BATCH is computable and only the 084 gates fire.
13. `_impl` default timed.
14. `_suite_item` default `(FIELDS["I2"],)`. Suite tests changed with it:
    - S3/S4 run on `SF` (they are about an untimed field).
    - S7 expects `1 passed in 0.01s`.
    - S9's first line is timed.
    - S11/S12 and S14 use timed values.
15. D3 (`test_log_after_i3_fail_is_written`): 06 `Verdict: FAIL (round 1)` and timed I2 fields. D4/D5: 03 `Status: BLOCKED (x)` and 04 `Fit verdict: NOT A FIT` (Test 13).
16. N5 (`test_batch_untimed_item_is_not_computable`): rewritten on 089, with a 990 twin (Test 5).
17. `UNSHALLOW` constant updated (Test 22).

Count: 20 existing test functions with edited bodies (the list above; `git diff -U0 tests/test_pipeline_check.py | grep -E '^@@' | grep -oE 'def test_[a-z0-9_]+' | sort -u | wc -l` → 20), plus the constants `FIELDS`, `NEW_I2_WANT` and `UNSHALLOW` and the helpers `_defective`, `_impl` and `_suite_item`. In `tests/test_real_data_field.py`, 2 literals were edited; 24 tests reach them through `_rd_item`.

New tests, mapped to 04's numbering:
- T1 `test_log_i2_untimed_refused_from_090`
- T2 `test_timed_hint_fits_timed_format` (a new function; `test_log_hints_match_formats` was left as is)
- T3 `test_timed_gate`, plus `test_timed_gate_not_seen_keeps_suite_check`
- T4 `test_batch_not_computable_strict_from_090` [990, 089]
- T5 the N5 rewrite above, plus `test_batch_no_line_before_i2_strict_from_090` [990, 089]
- T6 `test_round_bound_delta0_boundary` [60.00, 60.01]
- T7 `test_round_bound_round2_batch`
- T8 `test_round_bound_delta1_limit_120`
- T9 `test_round_bound_interleaved_items`
- T10 `test_round_bound_fast_prev_is_research`
- T11 `test_round_bound_on_repo_data`
- T12 `test_round_bound_end_to_end`
- T14 `test_round_content_refusal` (7 cases), plus `test_round_unreadable_07_keeps_rule_d`
- T15 `test_round_open_refuses_later_step`
- T16 `test_round_069_shape`
- T17 `test_round_unreadable_log_refused`
- T18 `test_shallow_three_readers_not_checked`
- T19 `test_shallow_docs_only_orphan_exit_0`
- T20 `test_open_branches_default_computes_shallow`: includes the `_is_shallow` rows "unreadable", boundaries, [] and "full", and `main_ahead(shallow=True)` with no ref → 0
- Text pin: `test_i2_and_run_item_texts_name_item_090`

## Connectivity check
- [x] Every new function or rule is used:
  - `_is_shallow` ← `_anchor_env`, `open_branches`
  - `_first_verdict` ← `_round_refusal` ← `write_log`
  - `I2_TIMED` / `LOG_HINT_TIMED` ← `log_fields_ok` / `log_hint`
  - `BATCH_STRICT` ← `incomplete`
  - `VERDICT_OF` ← `_first_verdict`, `_round_refusal`
  - `SHALLOW_TEXT` ← `_anchor_env`, `main`
  - `TIMED_FROM` ← `log_fields_ok`, `log_hint`, `incomplete`
  - The `shallow` args of `late_log_lines`, `main_ahead` and `open_branches` ← `main`. `check_handoff.open_branches()` computes it: `python3 scripts/check_handoff.py --all` → `no new failures`, exit 0.
- [x] Every input has a source and every output has a consumer:
  - `batch_nc` comes from `batch_log_items()` in main and feeds the INCOMPLETE entries.
  - Round refusals go to stderr with exit 2.
  - Per-round flags join `batch["flagged"]`, which reaches the LOG BATCH line and exit 1.
  - The not-checked lines are printed by main.
  - The `"shallow"` dict key is read by main's unrelated-ref print.
- [x] Every branch ends in a defined result:
  - `_first_verdict` gives a word, `absent`, `<file> unreadable` or `no readable <label> line`.
  - `_round_refusal` refuses with a reason on an unreadable log, an unreadable request.md, or a log line with no valid time. Otherwise (a), (b) or (c) refuses, or it returns None.
  - The per-round bound skips a round with no time (not evaluated) or no prev (the whole-item `no line before I2` covers that case). It never reads 0 s.
  - `main_ahead`: no ref → 0, shallow → None, error → str.
  - `late_log_lines`: no git → None, shallow → False.
- [x] No leftover TODOs or unused files: `grep -n "TODO" scripts/check_pipeline.py` → none. The scratch worktree `/tmp/claude-0/scratch/i2-090/wt` was removed (`git worktree list` shows only the repo and another agent's `/tmp/claude-0/wt35`).
- Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 38 hits, all in ccbot/. That folder is untouched (`git diff --stat -- ccbot/` is empty), so none of them is new. On this item's diff, the same grep plus `or {}`, `or []` and `: float =` finds three hits:
  - `nc = (batch_nc or {}).get(item_dir.name)`: no batch dict means the caller did not ask for step 2. main always passes one, so nothing passes on absent data.
  - `if last is not None and log_fields_ok(..., timed=False)`: this guard already existed. With no I2 line, 043/045 already report the item, and the untimed form keeps the Suite check running (Deviations 2).
  - `start = marks[-1] if marks else 0`: with no send-back or terminal line, (c) starts at the item's first row, as 04 says. That is a stricter start, not a pass.
  - No dataclass and no numeric default were added. The only `>=` on data is `round(t - BATCH_ROUND, 3) >= limit`, where t is a float parsed from a matched `\d+\.\d+` (never NaN or None), and a round with no time is skipped before the test. The step comparisons use fixed codes.

## Test output (pasted, not summarized)
`python3 -m pytest -q` from the repo root, final tree (only the last 3 lines are shown; the one failure is explained below):
```
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 758 passed, 1 skipped in 83.34s (0:01:23)
```
Suite: 1 failed, 758 passed, 1 skipped in 83.34s (0:01:23)

The one failure is the item-071 case in i2-builder.md step 3 and is not caused by this build. 087's I3 committed `Verdict: FAIL` (e4edcb0, `I3 | 087 | FAIL`) while I was building. `check_pipeline.py` then prints `087: I3 FAIL (FULL; sent back to I1 I2, ...)` and `I3 FAIL: 087` and exits 1. It prints the same with the base script (`git show HEAD:scripts/check_pipeline.py`, d3aa031, run on the same tree, exit 1); the whole-output diff is below. No other line of the repo run is an error.

Done checks:
- `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py tests/test_real_data_field.py` → ok (RI-008).
- GIT_CENSUS is unchanged and still totals 47: `test_git_call_census` passes, and the build adds no `_git`/`_git_ok` call site. 089's read census passes: `test_read_census` still counts 2, and the new readers use `_read`.
- Whole-output diff (RI-013), full clone, both scripts run on the same working tree at 00:5x UTC:
  - `python3 /tmp/claude-0/scratch/i2-090/base_check_pipeline.py > before.txt` (exit 1)
  - `python3 scripts/check_pipeline.py > after.txt` (exit 1)
  - `diff before.txt after.txt` → exit 0, `0 lines` (112-line output).
  - An earlier pair at fd73de1, before 087's I3 FAIL, was also identical (exit 0 both).
  - Expected and found: no real item ≥ 90 has an I2 line, there are 0 per-round flags, and the clone is full.

Mutations (scratch worktree `/tmp/claude-0/scratch/i2-090/wt` = HEAD plus these 7 files; driver `/tmp/claude-0/scratch/i2-090/tools/mutate.py`). Each mutation was run against its named test and against all of tests/test_pipeline_check.py, then reverted. `test_repo_pipeline_has_no_skipped_items` fails in every row: that is the 087 baseline above.

| ID | Mutation | Target result | Whole file | Target among failed |
|---|---|---|---|---|
| M1 | write_log passes timed=False | 1 failed | 2 failed, 359 passed | test_log_i2_untimed_refused_from_090 |
| M2 | `_TAIL` time mandatory | 1 failed | 10 failed, 351 passed | test_i2_tests_field_cutoff |
| M3 | I2_TIMED `.*in ...` (time in note) | 1 failed | 5 failed, 356 passed | test_log_i2_untimed_refused_from_090 |
| M4 | step 2 ID test dropped | 1 failed, 1 passed | 11 failed, 350 passed | test_batch_not_computable_strict_from_090[089-False] |
| M5 | `+1` dropped in the bound | 1 failed | 41 failed, 320 passed | test_round_bound_delta1_limit_120 |
| M6 | prev = the item's first line | 1 failed | 3 failed, 358 passed | test_round_bound_round2_batch |
| M7 | per-item filter removed | 1 failed | 3 failed, 358 passed | test_round_bound_interleaved_items (+ on_repo_data) |
| M8 | no round close in (b) | 1 failed | 2 failed, 359 passed | test_round_069_shape |
| M9 | substring verdict | 2 failed, 5 passed | 3 failed, 358 passed | test_round_content_refusal[06-earlier-fail], [04-unfilled] |
| M10 | unreadable → still sent back | 1 failed, 6 passed | 2 failed, 359 passed | test_round_content_refusal[06-unreadable] |
| M11 | `shallow = False` in main | 2 failed | 3 failed, 358 passed | test_shallow_three_readers_not_checked, test_shallow_docs_only_orphan_exit_0 |
| M12 | main_ahead returns SHALLOW_TEXT | 1 failed | 6 failed, 355 passed | test_shallow_docs_only_orphan_exit_0 |
| M13 | late_log_lines returns [SHALLOW_TEXT] | 1 failed | 10 failed, 351 passed | test_shallow_docs_only_orphan_exit_0 |
| M14 | shallow MAIN skip removed | 1 failed | 4 failed, 357 passed | test_shallow_docs_only_orphan_exit_0 |
| M15 | (a) dropped | 1 failed | 2 failed, 359 passed | test_round_open_refuses_later_step |
| M16 | (c) dropped | 1 failed | 2 failed, 359 passed | test_round_069_shape |
| M17 | lookahead dropped from VERDICT_OF 04 | 1 failed, 6 passed | 2 failed, 359 passed | test_round_content_refusal[04-unfilled] |

M12 and M13 also fail the existing shallow tests (test_cutoff_missing_in_shallow_clone_not_checked, test_inbox_shallow_clone_not_checked, test_uncommitted_step_in_shallow_clone and others). This shows the not-checked returns keep the exit unchanged.

Fixture counts for the shallow tests (feasibility; `/tmp/claude-0/scratch/i2-090/tools/shallow_probe.py` ran T18's source repo through the base and the 090 script):
```
[full clone, base script, exit 1]
  origin/claude-x: items none; merges cleanly; last commit 2026-11-21 (0 days)
LOG TIME: 150 I3 (2026-11-20 23:59 after commit 2026-11-20 01:30 UTC)
[full clone, 090 script, exit 1]
  origin/claude-x: items none; merges cleanly; last commit 2026-11-21 (0 days)
LOG TIME: 150 I3 (2026-11-20 23:59 after commit 2026-11-20 01:30 UTC)
[d1 clone, base script, exit 1]
MAIN AHEAD: origin/main has 1 commits not in HEAD; merge it before building (item 051)
  origin/claude-x: no common history with HEAD; not scanned (item 081); last commit 2026-11-21 (0 days)
BRANCH ERROR: origin/claude-x (no common history with HEAD; 2 file(s) on checked paths (first: .claude/x.md) not checked (item 081))
LOG TIME: none
[d1 clone, 090 script, exit 1]
MAIN AHEAD: not checked (shallow clone; run git fetch --unshallow)
  origin/claude-x: not checked (shallow clone; run git fetch --unshallow); last commit 2026-11-21 (0 days)
BRANCH ERROR: origin/claude-x (shallow clone; 2 file(s) on checked paths (first: .claude/x.md) not checked; run git fetch --unshallow (item 090))
LOG TIME: not checked (shallow clone; run git fetch --unshallow)
```
The full clone has 1 late line; the base script at depth 1 shows `none`. MAIN AHEAD is 0 in the full clone (no line) and a false 1 at depth 1. That matches A1's 081 probes.

Re-derivations (`python3 /tmp/claude-0/scratch/i2-090/tools/rederive.py`, run from the repo root at d3aa031, read-only):

1. The 17-round table. 03's 17 rounds, all `ok`; 083's untimed line is not evaluated:
```
rounds 17, flagged 0, max ratio 0.3066 (077 01:02 91.97/300)
```
Per round, as t − 0.005 / limit:
- 076: 85.485/1800, 81.905/360
- 077: 77.785/3240, 91.965/300
- 078: 92.655/6300
- 079: 90.925/8640, 87.185/360
- 080: 77.875/480
- 081: 74.435/1440, 86.105/960
- 082: 90.135/6600, 88.535/420
- 084: 76.245/2520, 80.685/960
- 085: 79.785/480
- 086: 77.465/2940, 83.515/1080

This matches 03's Self-check line for line.

2. The (c) and (a) replay. 03 counted 30 lines. There are now 31: 087's round-2 `I1 11-22 00:26` (f52ad15) was logged by another agent during this build.
```
lines replayed 31, refused 0
```

3. (b) at the commit that added each line, using `git log -S"<line>"` and then `git show <sha>:work/<ID>/06-verification.md` read with `_first_verdict`. 03 counted 4 named lines plus 10 lines for git replay. There are 15 here: those 14, plus 087's I1. All say FAIL, so none would be refused:
```
061 I2 11-14 05:27 after I3: 06-verification.md at 279a4e0 says FAIL -> ok
062 I2 11-13 23:47 after I3: 06-verification.md at 2343440 says FAIL -> ok
069 I2 11-17 23:55 after I3: 06-verification.md at dc162cf says FAIL -> ok
070 I2 11-18 00:08 after I3: 06-verification.md at a237da7 says FAIL -> ok
076 I1 11-20 00:20 after I3: 06-verification.md at db3fb05 says FAIL -> ok
076 I2 11-20 00:25 after I3: 06-verification.md at e813e1f says FAIL -> ok
077 I2 11-20 01:02 after I3: 06-verification.md at f765ca5 says FAIL -> ok
079 I2 11-20 02:15 after I3: 06-verification.md at bff5839 says FAIL -> ok
081 I1 11-21 00:32 after I3: 06-verification.md at 129120b says FAIL -> ok
081 I2 11-21 00:47 after I3: 06-verification.md at e5297e7 says FAIL -> ok
082 I2 11-21 02:06 after I3: 06-verification.md at 85bf4c4 says FAIL -> ok
084 I2 11-21 00:40 after I3: 06-verification.md at 0583289 says FAIL -> ok
086 I1 11-21 00:43 after I3: 06-verification.md at 55893e5 says FAIL -> ok
086 I2 11-21 01:00 after I3: 06-verification.md at 91ade51 says FAIL -> ok
087 I1 11-22 00:26 after I3: 06-verification.md at f52ad15 says FAIL -> ok
```
069 I1 00:12 and 070 I2 00:24 are not in this list, because their I3 FAIL round was closed by I3 PASS (03 #13). They pass (c).

4. Template lines:
```
03: files 27, with a column-0 'Status:' line 27, _first_verdict readable 27: READY
04: files 27, with a column-0 'Fit verdict:' line 27, _first_verdict readable 27: FIT, FIT WITH CHANGES
templates/research-handoff.md: _first_verdict -> (None, 'no readable Status: line')
templates/build-plan.md: _first_verdict -> (None, 'no readable Fit verdict: line')
templates/verification.md: _first_verdict -> (None, 'no readable Verdict: line')
```

Feasibility numbers:
- TIMED_FROM: 0 items ≥ 90 have an I2 line (the after.txt INCOMPLETE line is none).
- Step 2: 0 of the 7 not-computable items (048, 054, 055, 056, 058, 059, 060) is ≥ 90.
- Per-round bound: 0 of 17 rounds flagged.
- (c): 0 of 31 lines refused. (b): 0 of 15.
- Shallow counts: as pasted above.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: .claude/agents/a1-auditor.md, .claude/agents/i2-builder.md, .claude/commands/daily-audit.md, .claude/commands/run-item.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, tests/test_real_data_field.py; no TRIGGER path)

## Deviations from plan
1. **7th file: `tests/test_real_data_field.py`.** It imports `_item` from test_pipeline_check and hard-codes 05's `Suite: 1 passed` in two places, so B0's timed `FIELDS["I2"]` broke 24 of its tests (Suite mismatch). B0 says to sweep fixtures for the timed field and record every edit; 04 listed only test_pipeline_check.py. The fix is two literals now read from `FIELDS` (`SUITE`). No assertion changed, and that file then passed 39 of 39. This is the same mechanical sweep B0 asked for, not a new design, so I made it and am reporting it here instead of sending the item back. The log line therefore says 7 files.
2. **Suite guard reads the untimed form** (`log_fields_ok(..., timed=False)` in the item-082 Suite check). Without this, an item ≥ 90 whose 05 predates TIMED_FROM (RULE NOT SEEN, no format entry) and whose I2 field is untimed would have its Suite check silently dropped, which RI-002 forbids. With the change the Suite check runs in both cases; a seen-rule item gets both entries. Pinned by `test_timed_gate_not_seen_keeps_suite_check`. 04 does not mention this guard.
3. **`flagged_ids` once per ID for the whole-item rule too.** 04 asked for this on the round flag only. Without the guard, an item flagged by both rules would be listed twice.
4. **Gap found: a person's `Waived: 01 02 03 04` item ≥ 90 has no line before I2 and is now INCOMPLETE** (`LOG BATCH not computable: no line before I2 (item 090)`), and no waiver excuses it. 03 #56 and 04 say this reason is "impossible for every Scope", but waivers make it possible (024's shape, < 90). It is strict (loud, never a silent pass), so I kept 04's rule. I named the gap in the LOG BATCH docstring, pinned it in `test_batch_no_line_before_i2_strict_from_090[990]` (that fixture uses this waiver), and moved `test_waived_steps_are_excused_and_printed`'s 105 to 085 so that test keeps its 031/042 meaning. **For I3/A1:** decide whether a person's waiver of 01-04 should excuse this reason (a possible new item).
5. **`_round_refusal` refuses when request.md is unreadable** (`<path> unreadable; order not checked (item 090)`) instead of reading the Scope as FULL. 04's missing-inputs list covers only an absent request.md (already 047's refusal). Picking a default Scope would break the missing-data policy.
6. **T2 is a new function** (`test_timed_hint_fits_timed_format`). I did not extend `test_log_hints_match_formats`, which only iterates LOG_HINT. M2 is still killed by the untimed 076 line (`test_i2_tests_field_cutoff`, L712); test_log_hints_match_formats is unedited.
7. **Re-derivation counts are 31 and 15, not 30 and 14.** 087's round-2 I1 line (f52ad15) was added in this checkout during the build. It passes both checks.
8. For A1, out of scope (04): a single-branch clone hides branches (Open Q5, RI-009), named in the OPEN BRANCHES docstring. Not built.

Recurring issues checked (item 013):
- RI-001 (ESCALATED): every filter, window and refusal has a computed count: 17/17 rounds 0 flagged, 31/31 lines 0 refused, 15/15 (b), 0/7 not-computable items ≥ 90, 27/27 template lines, and the shallow fixture counts. None says "always".
- RI-010 (ESCALATED): this item. See the RI-010 line below.
- RI-014 (OPEN): this item. See the RI-014 line below.
- Also checked (GUARDED):
  - RI-002: no absent time, prev, verdict, Scope or shallow state becomes a pass, 0 s or none. See Deviations 2, 4 and 5.
  - RI-004/005: the fixture numbers were re-run against their triggers. 60.00 → 59.995 < 60 is none; 60.01 → 60.005 is flagged; 80.00 at Δ0 is flagged; 86.00 at Δ1 is under 120; round 1 at 50.00 is under 660 (T6-T8, T12).
  - RI-006: file counts come from the commands above. The Suite line is pasted.
  - RI-008: py_compile on 3.11.
  - RI-009: the 088/089 build order; check_handoff's `open_branches()` caller was run.
  - RI-012: verdict words come from their group with the lookahead; BATCH_STRICT is compared by equality; M9 and M17 are killed.
  - RI-013: the whole-output diff is 0 lines.

RI-010: guardrail built (090). Same-minute (Δ0) I2 rounds are flagged in LOG BATCH, including rounds after a send-back. An untimed I2 field is refused from 090, and a not-computable batch is INCOMPLETE. After a send-back, `--log` checks the round, the sender's verdict and step order. Known open, in the docstring: I3's run is untimed; an I3 that FAILs again; A1 FAIL rounds get (c) only; Δ ≥ 1 batches. Stays ESCALATED until 090 is merged and an A1 probe on main flags a Δ0 round-2 I2 (test_round_bound_round2_batch's shape).
RI-014: guardrail built (090). In a depth-1 clone, LOG TIME, MAIN AHEAD and an unrelated open branch say `not checked (shallow clone; run git fetch --unshallow)`; origin/main is not listed; the exit is pinned at 0 (docs-only orphan) and at 1 (a branch with checked paths). The full-clone control is unchanged. GUARDED when 079, 081 and 090 are merged and M11 (shallow forced False) fails test_shallow_three_readers_not_checked on main.

