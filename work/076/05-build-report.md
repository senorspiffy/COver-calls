# 05 Build report - 076
Base: HEAD f3521ff (075 built, I3 PASS). Built in the working tree, not committed.

Status: BUILT, with one plan defect sent back to I1 (Deviation 2: mutation m1 survives; the plan's claim that it fails T2 R3/R4 is wrong). Everything else in 04 is built, and every other named test and mutation behaves as the plan says.

## Changes made (file: what changed)
- `scripts/check_pipeline.py`:
  - Next to `LOG_CHECK_FROM`: `TESTS_FORMAT_FROM = 76`, `_N`, `_END`, `_STATS_PARTS`, `_STATS`, `_TAIL` (03's code block, verbatim) and `I2_BEFORE`.
  - `LOG_FORMAT["I2"]` is the inline plain string `rf"\d+ files? changed \| tests {_STATS}{_TAIL}"`, so the dict is still plain strings keyed by agent.
  - `LOG_HINT["I2"]` holds the new hint and the example `2 files changed | tests 9 passed, 1 skipped in 3.21s`.
  - New `LOG_HINT_BEFORE = {"I2": ("<n> files changed | tests <pass>/<total> (pass <= total)", "2 files changed | tests 9/9")}`.
  - New `log_fields_ok(agent, item, fields)` and `log_hint(agent, item)`.
  - `incomplete()` uses `log_fields_ok(m[3], m[4], m[5])` and `log_hint(a, item_dir.name)`.
  - `write_log()` uses `log_fields_ok`, with the `\d{3}` check ahead of it in the `or` chain (change 4), and `log_hint(agent, item)` in the refusal text. The unknown-agent text is unchanged.
  - Module docstring: the `TESTS_FORMAT_FROM` definition, the total definition (deselected and warnings are not tests), pass <= total, and the note limit.
  - `log_hint` has a `\d{3}` guard that the plan did not have (Deviation 1).
- `.claude/agents/i2-builder.md` L25: replaced with 04's text word for word. This is a RULES change and needs the person's OK in PR review. The L20 sentence pinned by `test_agent_texts_name_item_071` is untouched.
- `tests/test_pipeline_check.py`:
  - `FIELDS["I2"] = "1 files changed | tests 1 passed"`.
  - New `I2_BEFORE_FIELD` and `_field(agent, item)`, used in `_item` (was L44) and in `test_log_time_exception_is_named_and_closed` (was L516, items 048/150).
  - L380/L390 now read `9 passed, 1 skipped in 3.21s`. L404, L412, L442 and L537 now read `tests 1 passed`.
  - L428, L443, L533 and L557 keep the `see 05` lines, malformed on purpose.
  - L562/L566 expect the new hint.
  - New tests: T1 `test_i2_summary_line_accepted` (15 cases: A1-A14 + the FIELDS form), T2 `test_i2_summary_line_refused` (17 cases: R1-R14 with R6/R7 separate and R11 as `411 passed,` and `411 passed, `, plus ANSI and `=`-padded), T3 `test_i2_tests_field_cutoff`, T4 `test_i2_text_defines_tests_field`, T5 `test_old_i2_hint_fits_old_format` (also checks `log_hint` on both sides of the cutoff), and T6 `test_log_refuses_non_numeric_id_without_crash`. Helpers `_request` and `_log`.
  - tests/test_real_data_field.py needs no edit: it imports `_item`, which now goes through `_field`, so its 069/070 fixtures get the old form.

File counts (pathspec excludes work/ and logs/, so A1's 075 files are not counted):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
3
$ git diff --stat
 .claude/agents/i2-builder.md |   2 +-
 scripts/check_pipeline.py    |  52 +++++++++++++--
 tests/test_pipeline_check.py | 155 ++++++++++++++++++++++++++++++++++++++++---
 3 files changed, 190 insertions(+), 19 deletions(-)
```
0 new + 3 changed = 3 files, which matches 04's "3 files".

## Connectivity check
- [x] Every new function and rule is used:
  - `log_fields_ok` is called in `incomplete()` and `write_log()`.
  - `log_hint` is called in both refusal texts.
  - `TESTS_FORMAT_FROM`, `I2_BEFORE` and `LOG_HINT_BEFORE` are read by those two functions.
  - `_N`, `_END`, `_STATS_PARTS`, `_STATS` and `_TAIL` build `LOG_FORMAT["I2"]`.
  - `_field` is used at both fixture sites. `I2_ACCEPT` and `I2_REFUSE` feed T1/T2.
- [x] Every input has a source and every output has a consumer. The input is I2's pasted pytest summary line (`--log`) or a committed log line (`incomplete`). The outputs are exit 2 with a hint on stderr, or an INCOMPLETE entry in the checker report (A1 reads it).
- [x] Every branch ends in a defined result:
  - Unknown agent: refused with the agent list.
  - Non-3-digit ID: refused with the current hint (T6). It is never a traceback.
  - Item < 76: `I2_BEFORE`. No match or pass > total gives a refusal or INCOMPLETE with the old hint.
  - Item >= 76: `LOG_FORMAT["I2"]`. No match gives a refusal or INCOMPLETE with the new hint.
  - An absent or empty summary line, or `no tests ran`, is refused (T2 R1/R14). It is never defaulted.
- [x] No TODOs (`git diff | grep -n "TODO\|FIXME"`: 0 hits) and no unused files.
- Missing-data grep `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` gives 37 hits. ccbot/ is unchanged in this item, so none of them is new. The same grep over the check_pipeline.py diff: 0 hits.
- 014 patterns:
  - No dataclass fields were added.
  - The new comparisons are `int(m[1]) <= int(m[2])` (only after `I2_BEFORE` fullmatched both as `\d+`) and `int(item) < TESTS_FORMAT_FROM`. In `write_log` the item is checked as `\d{3}` first. In `incomplete` it comes from `LOG_LINE`'s `(\d{3})`. In `log_hint` it is guarded. None of them can see NaN or None.
- Feasibility (the plan names these):
  - Committed I2 lines for items 045-075: 36. That is the plan's 35 for 045-074, plus 075's `23:51 | I2 | 075 | 1 files changed | tests 488/489`, written after the plan.
  - `log_fields_ok` refuses 0 of 36.
  - Equal pass/total cases: 065 49/49, 058 218/218, 072 411/411. pass > total: 0.
  - Command: a python loop over `logs/implementation/*.md` with `LOG_LINE` and `log_fields_ok` (output: `36 lines 045-075, bad 0`). `grep -hE "\| I2 \| 0(4[5-9]|[5-7][0-9]) \|" logs/implementation/*.md | wc -l` → 36.
  - New form: T1 A1-A3 are the real 072, 074 and 070 lines, and all 3 pass.

## Test output (pasted, not summarized)
```
$ env | grep -E "PYTEST_ADDOPTS|PY_COLORS|FORCE_COLOR"
(no output)
$ python3 -m pytest --version
pytest 9.1.1
$ python3 -m pytest -q          # repo root, after the Deviation 1 fix
...
524 passed, 1 skipped in 85.49s (0:01:25)
```
Before the Deviation 1 fix, `python3 -m pytest -q tests/test_pipeline_check.py` gave `1 failed, 185 passed in 23.95s` (FAILED `test_log_refuses_non_numeric_id_without_crash`, `assert (1 == 2)`). A direct run showed the cause: `ValueError: invalid literal for int() with base 10: 'abc'` in `log_hint`, which was reached from `write_log`'s refusal text.

Repo check:
```
$ python3 scripts/check_pipeline.py ; echo exit $?
exit 0
I3 FAIL: none
A1 FAIL: none
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
ORPHAN LOG: none
SKIPPED: none
```
`test_repo_pipeline_has_no_skipped_items` passes within the full suite above.

Mutations (scratch worktree `/tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/076-I2/wt` at f3521ff, with the 3 built files copied in, RI-009; command `python3 -m pytest -q tests/test_pipeline_check.py`; the unmutated baseline gave `186 passed in 24.13s`):
```
== m1   _END -> (?:, )?
186 passed in 23.99s                                    <- SURVIVES (Deviation 2)
== m2   pass <= total removed
FAILED tests/test_pipeline_check.py::test_i2_tests_field_cutoff
1 failed, 185 passed in 23.45s
== m3   TESTS_FORMAT_FROM = 77
FAILED tests/test_pipeline_check.py::test_i2_tests_field_cutoff
FAILED tests/test_pipeline_check.py::test_old_i2_hint_fits_old_format
2 failed, 184 passed in 23.75s
== m4   TESTS_FORMAT_FROM = 75
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_i2_tests_field_cutoff
FAILED tests/test_pipeline_check.py::test_old_i2_hint_fits_old_format
3 failed, 183 passed in 23.27s
== m5   deselected added to _STATS_PARTS
FAILED tests/test_pipeline_check.py::test_i2_summary_line_refused[3 passed, 1 deselected in 0.12s]
1 failed, 185 passed in 23.57s
== m6   incomplete() back to bare re.fullmatch(LOG_FORMAT[...])
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_same_id_on_main_and_open_branch_is_a_clash
FAILED tests/test_pipeline_check.py::test_i2_tests_field_cutoff
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
6 failed, 180 passed in 23.71s
== m7   \d{3} check moved after log_fields_ok
FAILED tests/test_pipeline_check.py::test_log_refuses_non_numeric_id_without_crash
1 failed, 185 passed in 24.02s
```
m2-m7 each fail the test the plan named. m1 does not. The worktree's check_pipeline.py was restored after the runs.

## Real-data effect (diff_reports output, pasted)
not required (.claude/agents/i2-builder.md, scripts/check_pipeline.py, tests/test_pipeline_check.py; none is in TRIGGER or TRIGGER_DIRS)

## Deviations from plan
1. **`log_hint` guard (plan incomplete; T6 requires it).** 04 specifies `log_hint` as `int(item) < TESTS_FORMAT_FROM` with no guard. `write_log` calls it in the refusal text, which also runs for a non-numeric ID. So `--log I2 abc ...` crashed with a traceback and exit 1, even with change 4's order, and 04's own T6 failed. I added `re.fullmatch(r"\d{3}", item) and` before the `int()`, so a bad ID gets the current hint and exit 2. With the guard T6 passes and m7 still fails T6. I1/I3: please confirm.
2. **m1 survives: 04's mutation claim is wrong. Sent back to I1.** 04 says m1 (`_END` → `(?:, )?`) "fails T2 (R3/R4 order cases)". It does not, because the order is enforced by the fixed sequence of optional groups in `_STATS`, not by `_END`. `_END` only requires the `, ` separator (or the end) between parts. Checked directly against the built regex and the m1 regex:
   ```
   '411 passed, 1 failed'       real: False m1: False
   '1 skipped, 411 passed'      real: False m1: False
   '411 passed, '               real: False m1: False   (fields are .strip()ped)
   '411 passed,'                real: False m1: False
   '411 passed1 skipped'        real: False m1: True
   '1 failed1 passed in 1.00s'  real: False m1: True
   ```
   No case in 03's Self-check has parts with no separator, so T2 cannot kill m1. Per my rule 1 I have not added a case on my own. Suggested fix for I1: add a refuse case such as `411 passed1 skipped` to T2 (and to 03's Self-check), with m1 expected to fail it. The code is correct; only the test coverage of `_END` is missing.
3. Minor: T2's R11 has two variants, `411 passed,` and `411 passed, `. `write_log` strips the fields, so the second is the same input as the first after `.strip()`. It is kept because it matches 03's listing.

Follow-up (from 04, not built): option C, or an I3 duty that compares I2's log field with 05 Test output using a fixed `Suite:` label.

Recurring issues checked (step 0; `logs/recurring-issues.md` read first; RI-014 is the only OPEN entry, and none are ESCALATED in a way that touches this item):
RI-014: OPEN, not touched. `_walk` and clone depth are unchanged, and the new tests use tmp dirs without git.
RI-006: guardrail built (076). From item 076 the I2 tests field is pytest's line as printed (no hand count), and before 076 pass > total is refused. GUARDED when merged and mutation m2 (or m3) fails `test_i2_tests_field_cutoff` on main.
RI-012: checked. Full-line `re.fullmatch` only, with no substring tests.
RI-002: checked. An absent, empty or `no tests ran` field is refused, never defaulted (T2).
RI-010: checked. The i2 text is pinned by T4. It claims no I3/A1 cross-check that no agent runs.
RI-009: checked. Mutations ran only in the scratch worktree. The repo tree has only the 3 built files modified.
RI-001: checked. Feasibility re-counted with commands (36/36 above).
