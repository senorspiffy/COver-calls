# 05 Build report - 071
Base: 5f3f6bb (073's I2 build; HEAD is now d7bea9e, whose two commits after 5f3f6bb add only work/072/06-07 and work/073/06-07: `git diff --stat 5f3f6bb HEAD` lists those 4 files and 1 log). Branch daily-fixes/2026-11-18.

## Changes made (file: what changed)
- scripts/check_pipeline.py (Files 1a-1f):
  - 1a: after `WHOLE_DIFF_FROM = 70`, 03's 3 comment lines, `VERDICT_FROM = 71`, `VERDICT_LINE`, `SENT_BACK_LINE`, word for word.
  - 1b: new `i3_verdict(path)` directly before `def _is_code`, with the plan's docstring. It drops `<!--.*?-->` (re.S), toggles/skips ``` fences (`line.lstrip().startswith("```")`), and reads the first column-0 `Verdict:` line (`VERDICT_LINE.match`) and the first `Sent back to:` line (`SENT_BACK_LINE.fullmatch`). A seen but unreadable line stays None, and later lines are never read. It stops when both are seen. No walrus, `.match`/`.fullmatch` only (C4).
  - 1c: classify(): the planned `if "06" in have:` block, directly before `if len(have) == len(need):`.
  - 1d: incomplete(): before the final `return missing`, one `i3_verdict` call per item, then (a) unreadable verdict, (b) FAIL with no I1/I2/I1 I2, (d) PASS with no `none` (all ID ≥ VERDICT_FROM), and (c) the cross-check against the last `| I3 | <ID> |` LOG_LINE match over `sorted(logs/implementation/????-??-??.md)` in line order. It applies only when that last line fullmatches `LOG_FORMAT["I3"]` (C2), and there is no fallback.
  - 1e: main(): `i3_failed` list (7 lists), `"I3 FAIL"` in the IN PR tuple, `if status == "I3 FAIL": i3_failed.append(d.name)` after the A1 FAIL append, `I3 FAIL:` print before `A1 FAIL:`, and `or i3_failed` in the return.
  - 1f: docstring: the I3 FAIL entry after A1 FAIL, IN PR wording "stuck, not started, in progress or I3 FAIL here" (C3), and the Item 071 paragraph with the C1 and C2 edits and gaps (w)-(z). I re-wrapped the paragraph to 100 columns with `textwrap` and asserted that the joined words are identical.
- templates/verification.md (Files 2): the old comment line after line 2 is replaced by `Sent back to: <I1 | I2 | I1 I2 | none>` plus 03's new comment. Line 2 and 073's sentence are unchanged.
- .claude/agents/i3-verifier.md (Files 3): step 5 is replaced by 03's step-7 text. Step 2 (with 073's text) and step 4 are unchanged.
- .claude/agents/i2-builder.md (Files 4): 03's step-8 sentence is appended to step 3.
- tests/test_pipeline_check.py (Files 5):
  - `_item(..., verdict="PASS", sent_back="auto")` writes the 06 body as planned, and an I3 log field `FAIL | sent to audit: no` on FAIL.
  - Test 131 writes `Verdict: PASS (round 1)\nSent back to: none\nx\n`.
  - The repo test asserts `I3 FAIL: none`.
  - New tests T1-T8, T10-T13 (30 ids: 10 plain, T4 x18, T13 x2), plus helpers `_rounds_item` (T2) and `UNFILLED`.
- tests/test_real_data_field.py (Files 6): the `_rd_item` 06 body gets `Verdict: PASS (round 1)\nSent back to: none\n`.

File counts. These are restricted to the 6 planned paths (P = the 6 paths above), because I3 agents for 072/073 work in this tree in parallel. The unrestricted command gives the same numbers today:
```
$ git status --porcelain -uall -- $P | grep -c '^??'                          -> 0
$ git status --porcelain -uall -- $P | grep -c '^ M'                          -> 6
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'         -> 0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'         -> 6
```
Files planned 6, changed 6, new 0.

## Connectivity check
- [x] every new function/rule is used:
  - `i3_verdict` is called by classify() (1c), incomplete() (1d), T4 and T10.
  - VERDICT_FROM is used in incomplete(); VERDICT_LINE and SENT_BACK_LINE in i3_verdict.
  - `i3_failed` is printed and is in the exit code.
  - The agent sentences are pinned by T13.
- [x] every input has a source, every output has a consumer:
  - Inputs: 06 (I3, from the template's lines 2-3) and logs/implementation (`--log`).
  - Outputs: the item's status line, `I3 FAIL:`, the INCOMPLETE entries and the exit code. Their consumers are I2/I3 step 2, run-item and A1.
- [x] every branch ends in a defined result:
  - verdict None (INCOMPLETE from 071, not checked below 071, gap y);
  - FAIL with or without a target (`sent back to <t>` / `sent back to: not stated`, plus INCOMPLETE from 071);
  - PASS without `none` (INCOMPLETE from 071);
  - no I3 log line (043's existing entry); a malformed last line (045's entry, no cross-check, T12);
  - logs/implementation absent (the glob is skipped, so no lines; the existing orphan test's no-folder half still passes);
  - unclosed fence (None, T4).
- [x] no leftover TODOs or unused files. The scratch worktree was removed (`git worktree remove`).
- Missing-data policy:
  - `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` gives 37 hits, all pre-existing. ccbot/ is not changed by 071 (`git diff --stat -- ccbot/` is empty).
  - The same pattern over the added lines (`git diff -U0 -- scripts/ tests/ | grep -E "^\+.*(<pattern>| = 0\.0|: float = )"`) gives 0 hits (grep exit 1). No new or changed hit needs a reason.
  - 014 patterns: no dataclass was added. The only new comparison is `int(item_dir.name) >= VERDICT_FROM` (int, never NaN).
  - Nothing is defaulted: an unreadable verdict or target stays None and is never PASS or I2. `{"PASS": "none", "FAIL": "I2"}.get(verdict)` exists only in the test fixture, to build 06 text.
- Feasibility (real numbers, built code, 2026-11-18):
  - `i3_verdict` over all `work/*/06-verification.md`: 69 files, 69 PASS, 0 FAIL, 0 None. It is 69, not 03's 67, because I3 wrote 072's and 073's 06 during this build. Targets read: 072 `none`, 073 `none`, all others None (no field).
  - Real tree: `I3 FAIL: none`, `INCOMPLETE: none`, so all 29+ items from 041 agree with their last I3 log line.
  - Items ≥ 71 with a 06: 2 (072, 073), both `PASS`/`none`, so neither is flagged.

## Test output (pasted, not summarized)
Base full suite at 5f3f6bb, before any 071 edit:
```
$ python3 -m pytest -q
414 passed, 1 skipped in 62.74s (0:01:02)
$ python3 -m pytest -q tests/test_pipeline_check.py tests/test_real_data_field.py
155 passed in 24.29s
```
Before-fix probe: the new test file at the base code, in scratch worktree /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/wt071-base at 5f3f6bb:
```
$ python3 -m pytest -q tests/test_pipeline_check.py -k "i3_fail or later_pass or sent_back_none"
FAILED tests/test_pipeline_check.py::test_i3_fail_shows_and_exits_1 - Asserti...
FAILED tests/test_pipeline_check.py::test_later_pass_round_clears_i3_fail - A...
FAILED tests/test_pipeline_check.py::test_i3_fail_beats_older_a1_fail - Asser...
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated - Asserti...
FAILED tests/test_pipeline_check.py::test_i3_fail_with_more_steps_on_branch_is_in_pr
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
6 failed, 144 deselected in 2.41s
```
After the build:
```
$ python3 -m pytest -q tests/test_pipeline_check.py -k "i3_fail or later_pass or sent_back_none or i3_verdict or verdict_disagrees or old_06 or template_lines or malformed_last or item_071"
30 passed, 120 deselected in 3.74s
$ python3 -m pytest -q tests/test_pipeline_check.py tests/test_real_data_field.py
185 passed in 21.01s
$ python3 -m pytest -q
444 passed, 1 skipped in 61.41s (0:01:01)
$ python3 -m pytest -q tests/test_safety.py::test_every_py_compiles_on_oldest_python
1 passed in 0.08s
```
- 444 + 1 = 445 = 415 + 30 new ids. No new failure, and T8 ran (git present).
- test_real_data_field's count is unchanged: 185 - 155 = 30, all in test_pipeline_check.py.

I2 mutation spot-checks, in the same scratch worktree with the built files copied in, restored after each. I3 runs the full m1-m17 set.
```
m14 (d) removed                     -> FAILED test_pass_without_sent_back_none_is_incomplete
m15 last well-formed I3 line used   -> FAILED test_malformed_last_i3_line_is_not_replaced
m16 SENT_BACK .match                -> FAILED test_i3_verdict_reader[... Sent back to: I2 (tests only) ...-want15]
m17 lines sorted by HH:MM           -> FAILED test_later_pass_round_clears_i3_fail
m8  `or i3_failed` dropped          -> FAILED test_i3_fail_shows_and_exits_1, test_i3_fail_beats_older_a1_fail
m12 target defaults to I2           -> FAILED test_i3_fail_target_not_stated
```

Real tree, before commit (`python3 scripts/check_pipeline.py`, exit 0). All lines except the `complete`/`LEGACY` item lines:
```
071: in progress (FULL: next 05)
072: awaiting A1 (FULL)
073: awaiting A1 (FULL)
074: in progress (FULL: next 05)
STUCK: none
AWAITING A1: 072, 073
IN PR: none
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-18 (0 days)
RULES BRANCH: none
ID CLASH: none
I3 FAIL: none
A1 FAIL: none
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
RESEARCH CODE: none
REAL-DATA FIELD: none
ORPHAN LOG: none
INBOX: not checked (2026-11-18.md added in f103aa3; its templates/daily-audit.md has no ## Inbox)
SKIPPED: none
```
The exit code is unchanged (0), and 071 is not SKIPPED. This run was made before 05 existed, so 071 showed `next 05`. I3 re-runs it after the commit.

Greps:
```
grep -c "I3 FAIL" scripts/check_pipeline.py              -> 7   (>= 4)
grep -c "item 071" .claude/agents/i3-verifier.md         -> 1
grep -c "item 071" .claude/agents/i2-builder.md          -> 1
grep -c "^Sent back to:" templates/verification.md       -> 1
grep -c "same dirs" templates/verification.md            -> 0
grep -c "item 073" .claude/agents/i3-verifier.md         -> 1   (073 intact)
grep -c "python3 scripts/" templates/verification.md     -> 0
```
`python3 scripts/check_handoff.py 071`:
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 67
totals line: 67 rows -> 61 as-is, 6 fixed, 0 removed
PASS
```
(exit 0)

Existing 06 files from 071 on that the new check could flag (Extra research 4):
- `ls work/07[1-4]/06-verification.md` lists work/072/06-verification.md and work/073/06-verification.md. The plan expected 0; I3 wrote both during this build.
- Their lines 2-3 are `Verdict: PASS (round 1)` / `Sent back to: none` (072) and `Verdict: PASS (round 1; earlier rounds: none)` / `Sent back to: none` (073).
- `i3_verdict` reads ("PASS", "none") for both, and the real-tree run shows `INCOMPLETE: none`. **0 flagged.** No other item's file was edited.

## Real-data effect (diff_reports output, pasted)
not required (.claude/agents/i2-builder.md, .claude/agents/i3-verifier.md, scripts/check_pipeline.py, templates/verification.md, tests/test_pipeline_check.py, tests/test_real_data_field.py). That is the `git diff --stat` file list. No TRIGGER or TRIGGER_DIRS path is touched, and ccbot/realtest.py is unchanged.

## Deviations from plan
- Order of the before-fix probe: I made the code edits before writing the tests, so the plan's "write T1, T2, T5, T11 first" probe was run with the new test file against the unchanged base code (5f3f6bb) in a scratch worktree. The selection and result are the same as the planned probe (6 failed: T1, T2, T5, T11, plus T6 and T8, which also match `-k i3_fail`).
- The docstring paragraph was re-wrapped to 100 columns. The words are identical (asserted).
- `ls work/07[1-4]/06-verification.md` found 2 files, not the expected 0 (see above). Neither is flagged.
- No other deviation. The plan was complete; nothing was sent back to I1.

## Recurring issues checked (item 013)
RI-001 (ESCALATED), RI-002, RI-003, RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-010, RI-011, RI-012, RI-013 (all others GUARDED):
- RI-001: ESCALATED, unchanged. Every window has a measured count with the built code: 69/69 readable, 69 PASS, 0 FAIL; 2 items ≥ 71 with a 06, both `none`; `INCOMPLETE: none`.
- RI-002: GUARDED, unchanged. No value is defaulted: an unreadable verdict or target is None, never PASS or I2. T6 and the m12 probe show it. The grep gives 0 new hits.
- RI-003: GUARDED, unchanged. No calendar.
- RI-004/RI-005: GUARDED, unchanged. The T1 text was re-derived from the code and asserted literally.
- RI-006: GUARDED, unchanged. File counts come from commands; 30 new ids = 444+1 minus 414+1.
- RI-007: GUARDED, unchanged. The code, tests, template and agent edits are committed together with 05 (`UNTRACKED CHANGE: none`). SKIPPED still wins over I3 FAIL (the 1c anchor sits after every SKIPPED return).
- RI-008: GUARDED, unchanged. No possessive quantifiers, no `prefixmatch`, no walrus, `encoding="utf-8"`. The compile test passes.
- RI-009: GUARDED, unchanged. Text anchors were used (each asserted to occur once), probes ran in a scratch worktree, and 073's text is intact.
- RI-010: GUARDED, unchanged. The status now comes from fields a script reads, and T13 pins the agent text.
- RI-011: GUARDED, unchanged. No branch-diff change.
- RI-012: GUARDED, unchanged. Anchored `.match`/`.fullmatch` reads, with negative tests (T4 mid-line, indented, `**PASS** | FAIL`, `I2 (tests only)`, `x Sent back to: I2`).
- RI-013: GUARDED, unchanged. No realtest change.
