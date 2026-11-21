# 05 Build report - 084

Built on daily-fixes/2026-11-20 at HEAD d44b687 (081's I2 build: `_git_ok`, GIT_CENSUS). Nothing committed or pushed. No brokerage connection; no data or ticker input touched.

## Step 0 (read-only, before any edit)
```
$ git rev-parse --is-shallow-repository
false
$ git status --porcelain -- scripts/check_pipeline.py tests/test_pipeline_check.py
(empty: 081's build is committed in d44b687)
$ <the plan's per-item loop>
071 05-build-report.md ba78fb0 VERDICT_FROM=1 TESTS_FORMAT_FROM=0
071 06-verification.md 166e8b4 VERDICT_FROM=1 TESTS_FORMAT_FROM=0
072 05-build-report.md bb5a32e VERDICT_FROM=0 TESTS_FORMAT_FROM=0
072 06-verification.md e54a77e VERDICT_FROM=0 TESTS_FORMAT_FROM=0
073 05-build-report.md 5f3f6bb VERDICT_FROM=0 TESTS_FORMAT_FROM=0
073 06-verification.md d7bea9e VERDICT_FROM=0 TESTS_FORMAT_FROM=0
074 05-build-report.md b54c1b2 VERDICT_FROM=1 TESTS_FORMAT_FROM=0
074 06-verification.md b2dbe17 VERDICT_FROM=1 TESTS_FORMAT_FROM=0
075 05-build-report.md f47deb5 VERDICT_FROM=1 TESTS_FORMAT_FROM=0
075 06-verification.md f3521ff VERDICT_FROM=1 TESTS_FORMAT_FROM=0
076 05-build-report.md 266a6a2 VERDICT_FROM=1 TESTS_FORMAT_FROM=1
076 06-verification.md a1de083 VERDICT_FROM=1 TESTS_FORMAT_FROM=1
077 05-build-report.md 3006b73 VERDICT_FROM=1 TESTS_FORMAT_FROM=1
077 06-verification.md d703779 VERDICT_FROM=1 TESTS_FORMAT_FROM=1
078 05-build-report.md e4c19dd VERDICT_FROM=1 TESTS_FORMAT_FROM=1
078 06-verification.md 32b16fb VERDICT_FROM=1 TESTS_FORMAT_FROM=1
079 05-build-report.md e820bd7 VERDICT_FROM=1 TESTS_FORMAT_FROM=1
079 06-verification.md 627a2a0 VERDICT_FROM=1 TESTS_FORMAT_FROM=1
080 05-build-report.md 42b0378 VERDICT_FROM=1 TESTS_FORMAT_FROM=1
080 06-verification.md e01e1e9 VERDICT_FROM=1 TESTS_FORMAT_FROM=1
081 05-build-report.md d44b687 VERDICT_FROM=1 TESTS_FORMAT_FROM=1
081 06-verification.md not committed
082 05-build-report.md not committed
082 06-verification.md not committed
083 05-build-report.md cfc0634 VERDICT_FROM=0 TESTS_FORMAT_FROM=0
083 06-verification.md cfc0634 VERDICT_FROM=0 TESTS_FORMAT_FROM=0
084 05-build-report.md not committed
084 06-verification.md not committed
085 05-build-report.md ceb00ce VERDICT_FROM=1 TESTS_FORMAT_FROM=1
085 06-verification.md f976a05 VERDICT_FROM=1 TESTS_FORMAT_FROM=1
086 05-build-report.md not committed
086 06-verification.md not committed
$ python3 scripts/check_pipeline.py | grep -E '^INCOMPLETE:'
INCOMPLETE: 083 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed>"; 06 Verdict is PASS but has no 'Sent back to: none' line (item 071))
```
Send-back conditions, each checked: (i) 083 05 and 06 both at cfc0634, both constants 0: holds for the design. (ii) 076 05 TESTS_FORMAT_FROM=1, 076 06 VERDICT_FROM=1: control possible. (iii) 071 06 VERDICT_FROM=1. (iv) no `GIT FAILED` or `NO FILE` line. (v) baseline names 083 only. Expected set: TESTS gate (ID >= 76, 05 constant 0) = {083}; VERDICT gate (ID >= 71, 06 constant 0) = {072, 073, 083}; failing today = {083}; intersection = {083}. No send-back; build went ahead.

Feasibility numbers (re-counted from the table): VERDICT gate reaches 10 items with a committed 06 at 071-079 and 083 (plus 080, 085 now committed: 12 on HEAD); TESTS gate 5 at 076-079 and 083 (plus 080, 081, 085: 8 on HEAD). Suppressed set {083}, matching the plan.

## Changes made (file: what changed)
- `scripts/check_pipeline.py`:
  - Module docstring: new `RULE NOT SEEN (item 084, RI-010)` paragraph (anchor rule, line forms, `not checked` forms, git-failed and no-file entries, gaps: WHOLE_DIFF_FROM not gated, row 6 cross-check stays at CHECKLIST_FROM, rows 1-3 and write_log numeric).
  - New constant `RULE_FILE = "scripts/check_pipeline.py"` (after VERDICT_FROM).
  - New `_anchor_env()`: `"no git"` when `_git("rev-parse", "--git-dir")` is None; `"shallow clone; run git fetch --unshallow"` when `_shallow_boundaries()` is a non-empty list or `"unreadable"`; else None.
  - New `_rule_seen(item_dir, step, const, env)`: as planned. `(None, "")` for env set, unborn HEAD (`rev-parse --verify -q HEAD` exit 1) or no add commit; `(None, "<step> anchor: git failed (item 084)")` on a failed rev-parse (other non-zero), log, ls-tree or show; `(None, "<step> anchor <sha7> has no scripts/check_pipeline.py (item 084)")` when ls-tree exits 0 with empty output; else `(bool(re.search(rf"^{const} = ", text, re.M)), sha7)`. No `--first-parent`. log/ls-tree/show go through `_git_ok`.
  - `log_fields_ok(..., new_rule=True)` and `log_hint(..., new_rule=True)`: `not new_rule` selects I2_BEFORE / LOG_HINT_BEFORE. `write_log` unchanged (defaults).
  - `incomplete(item_dir, logs, env=None, not_seen=None)`: TESTS gate and VERDICT gate as planned; the git call is made only when the check would fire and the ID is at or above the cutoff. A `seen is None` note is its own entry; `seen is False` drops the reason (I2 only if every I2 line of the item passes I2_BEFORE, otherwise the old hint) and appends the pair to `not_seen`. Row 6 cross-check untouched.
  - `main()`: `env, not_seen = _anchor_env(), []` once; `incomplete(d, env=env, not_seen=not_seen)`; after the `INCOMPLETE:` print, `RULE NOT SEEN: not checked (<env>)` / `<ID> (<pair>; <pair>; item 084), ...` / `none`. Exit expression unchanged.
  - Scope lock: no change to CHECKLIST_FROM, LOG_CHECK_FROM, TESTS_FORMAT_FROM, VERDICT_FROM, LOG_TIME_EXCEPT, WHOLE_DIFF_FROM, the cross-check block, LEGACY, PRE_A1_LINE, write_log's refusal, late_log_lines.
- `tests/test_pipeline_check.py`:
  - GIT_CENSUS: 3 new entries with reasons (`_anchor_env`/_git 1, `_rule_seen`/_git 1, `_rule_seen`/_git_ok 3); the census total `41` becomes `46` (see Deviations).
  - `test_repo_pipeline_has_no_skipped_items`: loud `pytest.skip` in a shallow clone; asserts the exact `RULE NOT SEEN:` line (set {083}) and `INCOMPLETE: none`. Existing asserts unchanged.
  - New helpers `_defective`, `_rules_repo`, `_merge_main_into_rules`, `_pick` and tests (a) `test_rule_not_seen_item_merged_beside_rules_branch`, (b) `test_rule_not_seen_still_checks_old_rule`, (c) `test_unseen_item_that_passes_is_not_listed`, (d1) `test_rule_anchor_git_failure_is_incomplete`, (d2) `test_rule_anchor_without_rule_file`, (e1/e2) `test_rule_not_seen_shallow_and_no_git`, (f1) `test_rule_seen_positive_control_on_head`, (g) `test_write_log_stays_numeric`.
- `.claude/commands/run-item.md`: the planned line, directly after the `RULES BRANCH` line.

File counts (commands as run):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
3
```
3 files changed, 0 new (plus this 05 under work/).

## Connectivity check
- [x] every new function/rule is used: `_anchor_env` called in `main()`; `_rule_seen` called twice in `incomplete()` and by (d1), (f1); `RULE_FILE` used in `_rule_seen`; `new_rule` passed by `incomplete()`; `not_seen` filled by `incomplete()` and printed by `main()`. The run-item.md line names the `RULE NOT SEEN:` line that exists.
- [x] every input has a source, every output has a consumer: inputs are the item's log lines, its 05/06 add commit (git log), and that commit's RULE_FILE (git show). Outputs: INCOMPLETE entries (exit 1), the `RULE NOT SEEN:` line (read by A1/I3; pinned by (f2)).
- [x] every branch ends in a defined result: no git -> `not checked (no git)`, strict; shallow -> `not checked (shallow ...)`, strict; unborn HEAD / uncommitted step -> strict, no note; git failure -> strict + `anchor: git failed` entry; RULE_FILE absent -> strict + `has no scripts/check_pipeline.py` entry; constant present -> strict; constant absent and old rule passes -> listed; constant absent and old rule fails -> INCOMPLETE with the old hint, not listed. No combination yields `none` without a read.
- [x] no leftover TODOs or unused files (`git diff | grep -n TODO`: none; no new file).

Missing-data policy:
```
$ grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l
38
```
All 38 hits are in ccbot/, which this item does not change (`git diff --stat -- ccbot/ config/ data/` is empty): 0 new or changed hits. The same pattern over the diff of scripts/check_pipeline.py gives no hit. No dataclass field added. The new `<` tests compare `int(item)` with integer cutoffs (no NaN possible). The one "or" default (`not_seen = [] if not_seen is None else not_seen`) is a fresh list for callers that pass none, not a data default.

Recurring issues checked (item 013), open or ESCALATED:
- RI-001 (ESCALATED): checked. Gate counts re-measured in step 0 (above); suppressed set pinned to {083} by (f2).
- RI-010 (ESCALATED): checked. Each exemption is printed by ID and step; positive control (f1) on 076; M2 shows a renamed constant fails it.
- RI-014 (OPEN): checked. Shallow -> `not checked` (e1, M5); git failure -> entry, never "not seen" (d1, M3); the repo self-test and (f1) skip loudly in a shallow clone.
- Also GUARDED ones the plan names: RI-002 (unknown anchor is never "not seen": d1, d2), RI-006 (log tests field is pytest's line as printed), RI-007 (Scope FULL), RI-011 (no `--first-parent`: M4), RI-008 (compiled with python3.11).

Guardrail status lines for A1:
- RI-010: guardrail extended (084): RULE NOT SEEN lists every exempted (ID, step) pair; set {083} pinned by test_repo_pipeline_has_no_skipped_items; M1, M2 fail tests.
- RI-014: no new occurrence; 084's anchor reads are not checked in a shallow clone (test_rule_not_seen_shallow_and_no_git, M5) and failed git reads are entries (test_rule_anchor_git_failure_is_incomplete, M3).

## Test output (pasted, not summarized)
Baseline at d44b687 before any edit:
```
$ python3 -m pytest -q 2>&1 | tail -3
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 602 passed, 1 skipped in 77.48s (0:01:17)
```
After the build:
```
$ python3 -m pytest -q 2>&1 | tail -2
....................................                                     [100%]
611 passed, 1 skipped in 83.69s (0:01:23)
$ python3.11 -m py_compile scripts/check_pipeline.py && echo py311 OK
py311 OK
$ python3 scripts/check_pipeline.py | grep -E '^(INCOMPLETE|RULE NOT SEEN|UNCOMMITTED|SKIPPED)'; echo exit=${PIPESTATUS[0]}
INCOMPLETE: none
RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)
UNCOMMITTED STEP: none
SKIPPED: none
exit=0
```
Re-run after this 05 was written (the line used in the I2 log line):
```
$ python3 -m pytest -q 2>&1 | tail -1
611 passed, 1 skipped in 76.25s (0:01:16)
```
9 more tests than baseline (8 new + the fixed self-test): 602 + 1 failed -> 611 passed. `test_git_call_census` passes with the 5 new calls.

Mutations (run in a copied folder under the scratchpad, `cp -a` of the repo, never in the repo; copy deleted afterwards; `-k "rule_not_seen or unseen or rule_anchor or rule_seen or write_log_stays or repo_pipeline"`):
```
== M1   (_rule_seen returns (None, "") at once: gate off, numeric only)
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_rule_not_seen_item_merged_beside_rules_branch
FAILED tests/test_pipeline_check.py::test_rule_not_seen_still_checks_old_rule
FAILED tests/test_pipeline_check.py::test_rule_anchor_git_failure_is_incomplete
FAILED tests/test_pipeline_check.py::test_rule_anchor_without_rule_file
FAILED tests/test_pipeline_check.py::test_rule_not_seen_shallow_and_no_git
FAILED tests/test_pipeline_check.py::test_rule_seen_positive_control_on_head
7 failed, 2 passed, 238 deselected in 6.06s
== M2   (pattern rf"^{const}_X = ")
FAILED tests/test_pipeline_check.py::test_rule_not_seen_item_merged_beside_rules_branch
FAILED tests/test_pipeline_check.py::test_rule_not_seen_still_checks_old_rule
FAILED tests/test_pipeline_check.py::test_rule_seen_positive_control_on_head
3 failed, 6 passed, 238 deselected in 3.87s
== M3   (failed add-commit log returns (False, "x"))
FAILED tests/test_pipeline_check.py::test_rule_anchor_git_failure_is_incomplete
1 failed, 8 passed, 238 deselected in 4.35s
== M4   (--first-parent added to the add-commit git log)
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_rule_not_seen_item_merged_beside_rules_branch
FAILED tests/test_pipeline_check.py::test_rule_not_seen_still_checks_old_rule
FAILED tests/test_pipeline_check.py::test_rule_anchor_git_failure_is_incomplete
FAILED tests/test_pipeline_check.py::test_rule_not_seen_shallow_and_no_git
FAILED tests/test_pipeline_check.py::test_rule_seen_positive_control_on_head
6 failed, 3 passed, 238 deselected in 4.27s
== M5   (_anchor_env returns None in a shallow clone)
FAILED tests/test_pipeline_check.py::test_rule_not_seen_shallow_and_no_git
1 failed, 8 passed, 238 deselected in 3.71s
restored
```
M4's failure in (a) is at the `RULE NOT SEEN:` assert (150 is "seen" through the merge commit). M1-M5 each fail the test the plan names: M1 (a) and (f2); M2 (f1) and (a); M3 (d1); M4 (a); M5 (e1).

Extra research 2 pinned: (d2) asserts `git ls-tree --name-only <sha> -- scripts/check_pipeline.py` gives `(0, "")` for an absent path; it passes, so the absent-path text is used.

## Real-data effect (diff_reports output, pasted)
not required (git diff --stat: .claude/commands/run-item.md, scripts/check_pipeline.py, tests/test_pipeline_check.py; no TRIGGER path or TRIGGER_DIRS file)

## Deviations from plan
1. Fixture (a) shape: the plan puts item 150 with the rule file and says "branch `rules` from the first commit". If 150 were in the root commit, the rules branch would hold it too, the merge would be a no-op and M4 could not fail. I put the rule file alone in the root commit, 150 in a second commit on main, and `rules` off the root, so the merge brings 150 in as in PR #33 + main. This is the shape the plan's M4 needs; nothing else changes.
2. 151's log lines use date 2026-11-01 (own log files), because both branches adding `logs/implementation/2026-10-31.md` made `git merge main` conflict.
3. `test_git_call_census`'s `assert sum(seen.values()) == 41` becomes `== 46`. The plan says no existing assertion is edited, but 081's census (comment: "A new git call adds or bumps one entry with its reason (items 084, 086 build on this)") needs the total bumped for the 5 new calls; the caller's brief asked for this update.
4. `_rule_seen` makes one raw `_git("rev-parse", "--verify", "-q", "HEAD")` call to tell an unborn HEAD (exit 1, strict, no note) from a git failure (other non-zero, note), instead of parsing `_git_ok`'s reason string (RI-012). Recorded in GIT_CENSUS with that reason.
5. `_anchor_env`'s no-git probe is `_git("rev-parse", "--git-dir")` (the plan says "when `_git` gives None" without naming the command).

---

# Round 2 (I3 FAIL F1, work/084/06-verification.md; 2026-11-21, base HEAD 416835f)

Scope of this round: only F1. Files changed: scripts/check_pipeline.py (module docstring only) and tests/test_pipeline_check.py (one new parametrized test). 086's code in HEAD (LOG BATCH, rule D) was not touched.

## Round 2 changes (file: what changed)
- tests/test_pipeline_check.py: `EMBEDDED_RULES` (4 rule-file texts) and `test_rule_seen_ignores_constant_inside_other_text[form]` (RI-012 negative test, placed after `test_rule_seen_positive_control_on_head`). Each case builds a tmp repo: root commit has `scripts/check_pipeline.py` = `CHECKLIST_FROM = 41` plus both constants only inside other text; a second commit adds item 150 (`_defective`: old-form I2 line, no Sent-back line). Forms: `comment` (`# VERDICT_FROM = 71 ...`, `# TESTS_FORMAT_FROM = 76 ...`), `longer name` (`OLD_VERDICT_FROM = 71`, `OLD_TESTS_FORMAT_FROM = 76`), `string` (`x = "VERDICT_FROM = 71"`, `y = "TESTS_FORMAT_FROM = 76"`), and `all three` (I3's exact probe text: comment, `OLD_VERDICT_FROM = 71`, `OLD_TESTS_FORMAT_FROM = 76`, `x = "VERDICT_FROM = 71"`). Asserts: `_rule_seen(work/150, "05", "TESTS_FORMAT_FROM", None) == (False, sha7)` and `_rule_seen(work/150, "06", "VERDICT_FROM", None) == (False, sha7)`; the CLI's `RULE NOT SEEN:` line equals `SEEN_150` with that sha7 (both pairs listed); `INCOMPLETE: none`; exit 0.
- scripts/check_pipeline.py: module docstring, end of the RULE NOT SEEN paragraph, names the rule and the remaining gap: "The constant counts only at the start of a line, so a comment, a longer name (OLD_TESTS_FORMAT_FROM = 76) or a string is not it (RI-012, round 2 test); a column-0 `<CONST> = ` line inside a triple-quoted string would still read as seen (strict: the new rule is kept, never a false "not seen")." No code line changed.

File counts (from commands):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
2
$ git diff --stat
 scripts/check_pipeline.py    |  5 ++++-
 tests/test_pipeline_check.py | 33 +++++++++++++++++++++++++++++++++
 2 files changed, 37 insertions(+), 1 deletion(-)
```

## Round 2 deviation from plan
6. (F1, I3 round 1) The plan's test list had no RI-012 negative test for the `^<CONST> = ` match; added as above at I3's request. It is parametrized over the three forms plus I3's combined text, so each form is pinned on its own (a mutation that only handled one form would still fail the others).

## Round 2 connectivity check
- The new test is collected and run by the suite (4 cases pass). It calls `_rule_seen` directly and the CLI (`_run`), so both the return value and the `RULE NOT SEEN` / `INCOMPLETE` output are its consumers.
- No new function or branch in scripts/check_pipeline.py; docstring only. No TODO in the diff (`git diff -U0 | grep -E "^\+" | grep TODO`: no hit).
- Missing-data grep: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` -> 38, all pre-existing; this round changes no ccbot/ file and the diff's added lines have no hit. No dataclass field or `>`/`<` test was added (014). No feasibility test is named by the plan for this round.
- `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` -> OK (no output).

## Round 2 test output (pasted)
New test alone (repo):
```
$ python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py -k "constant_inside"
....                                                                     [100%]
4 passed, 273 deselected in 3.11s
```
Full suite (repo, round-2 tree):
```
$ python3 -m pytest -q -p no:cacheprovider
...
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated - Asserti...
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
4 failed, 637 passed, 1 skipped in 80.69s (0:01:20)
```
The 4 failures are pre-existing at HEAD 416835f, not from this round. Shown in the scratch copy with both round-2 files reset to HEAD (`git checkout -- scripts/check_pipeline.py tests/test_pipeline_check.py` there, never in the repo):
```
== HEAD 416835f, no round-2 edits
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
4 failed, 269 passed in 33.64s
```
- `test_old_06_without_round_headers_unchanged`, `test_i3_fail_target_not_stated`, `test_pass_without_sent_back_none_is_incomplete`: 086's round-1 text (its own 05 says 3 tests conflict with planned text; 086 is back with I1). 086's, not 084's.
- `test_repo_pipeline_has_no_skipped_items`: the repo's own pipeline state, not code. `python3 scripts/check_pipeline.py` in the repo exits 1 with `I3 FAIL: 081, 084, 086` (the open send-backs, 084 included, until a later PASS round); `INCOMPLETE: none`, and its `RULE NOT SEEN:` line is the expected 083 pair. It fails identically at HEAD.

## Round 2 mutations (scratch copy, never the repo)
Scratch copy: `cp -a /home/claude/cover-calls /tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i2-084-r2-mut/repo`. Each mutation edits line 644 of that copy's scripts/check_pipeline.py from a saved original; after the runs the file was restored and `cmp` with the repo file was identical (`restored-identical`).
```
== M6
    return re.search(rf"{const} = ", text) is not None, sha[:7]
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[all three]
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[comment]
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[longer name]
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[string]
4 failed, 7 passed, 266 deselected in 2.00s
== M7
    return (const in text), sha[:7]
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[all three]
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[comment]
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[longer name]
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[string]
4 failed, 7 passed, 266 deselected in 2.07s
restored-identical
```
(`-k "constant_inside or rule_not_seen or unseen or rule_anchor or rule_seen"`.) Whole tests/test_pipeline_check.py under each mutation (I3 ran this and got 247 passed, i.e. both survived):
```
== M6 (whole tests/test_pipeline_check.py)
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[all three]
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[comment]
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[longer name]
FAILED tests/test_pipeline_check.py::test_rule_seen_ignores_constant_inside_other_text[string]
8 failed, 269 passed in 33.54s
== M7 (whole tests/test_pipeline_check.py)
(same 8 FAILED lines)
8 failed, 269 passed in 33.72s
restored-identical
```
The 4 extra failures are the pre-existing ones above; the 4 new ones are this round's test. M6 and M7 no longer survive.

## Round 2 recurring issues checked
Read logs/recurring-issues.md first. Open/ESCALATED entries checked: RI-001, RI-010, RI-014; also RI-012 (the subject of F1) and RI-002.
RI-001: ESCALATED, unchanged; this round computes nothing from a window or rule set.
RI-002: GUARDED, unchanged; no value defaulted; the new test's (False, sha7) is only reached on a read rule file, and the docstring gap is strict (reads as seen, keeps the new rule).
RI-010: ESCALATED, unchanged by this round; 084's guardrail now also pinned against embedded-constant false "not seen" (the 083-style false INCOMPLETE in reverse).
RI-012: GUARDED; 084's constant match now has its negative test (comment, longer name, string); M6 and M7 each fail it. Remaining gap named in the docstring (column-0 line in a triple-quoted string, strict).
RI-014: OPEN, unchanged; the new test runs in a full tmp repo (not shallow); shallow behaviour is (e1)'s, untouched.
