# 05 Build report - 108
Scratch dir: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-108-r1-kedvvhhy

Base: f4f55a7 (HEAD when the build started). During the build other items committed only work/ and logs/ files (4d34f75, 447457a, a796abf, adbe255, 96e6268, 222fb58). `git diff --stat f4f55a7 HEAD -- scripts/ templates/ .claude/ config/ ccbot/ tests/` printed nothing, so the base for code is unchanged.

## Changes made (file: what changed)
- tests/test_pipeline_check.py (only file changed):
  - `SE_FIELD` and its comment are deleted. New `_se_fields()` under the `# Item 101 (RI-014)` comment returns `(timed, untimed)` from `_field("I2", RH_ID)`. It asserts that ` | tests ` is present, strips ` in <s>s` with `re.sub(..., count=1)` (keyword form, as the plan requires), and asserts that the strip changed the text.
  - `_se_timed05` takes both edits (log line and `Suite:` line) from `_se_fields()`, not from literal strings. `_se_edit` is unchanged.
  - `SE_CASES` has a new `("timed05alt", "05", _se_timed05)` case, giving ids `timed05alt-shallow` and `timed05alt-nogit`. `SE_ALT_I2 = "2 files changed | tests 3 passed in 0.02s"` is defined next to it.
  - `test_shallow_elif_branch_goes_to_unchecked` now takes `monkeypatch` and calls `monkeypatch.setitem(FIELDS, "I2", SE_ALT_I2)` for `timed05alt` before setup. The precondition is now `if case.startswith("timed05"):`. It reads the log back with `cp._log_text`, then checks `whys == []`, exactly one I2 line for RH_ID via `cp.LOG_LINE.match` per line, `f == untimed`, and that `f` passes LOG_FORMAT and fails I2_TIMED. The docstring has the plan's sentence for item 108.
  - Whitespace: 2 blank lines before `# Item 101 (RI-014)` (was 3) and before `def test_round_build_missing_inputs` (was 1).

File counts (command, number):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → `0`
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → `1`

## Connectivity check
- [x] every new function/rule is used: `_se_fields` is called by `_se_timed05` and by the precondition. `SE_ALT_I2` is used by the `monkeypatch.setitem` call. The `timed05alt` case is collected (see the ids below).
- [x] every input has a source, every output has a consumer: `FIELDS["I2"]` (or the patched value) → `_field` → `_se_fields` → the edits and the precondition. The fixture log is read back through the checker's own `_log_text` and `LOG_LINE`.
- [x] every branch ends in a defined result: no time in the field → `assert untimed != timed`. No ` | tests ` → an assert. Unreadable log → `assert whys == []`. 0 or 2+ I2 lines → `assert len(own_i2) == 1`. Edit text missing → `_se_edit`'s `assert old in text`. Each of these fails by name; none is skipped.
- [x] no leftover TODOs or unused files: `grep -rn SE_FIELD tests/` → 0 hits. No new files.
- Missing-data grep: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` → `38`. All are existing hits: ccbot/ is not changed (`git diff --stat HEAD -- ccbot/` is empty), so there are 0 new or changed hits. 014 patterns: no dataclass is added and no `>`/`<` comparison is added (the new assertions are `==`, `!=`, `in` and `len(...) == 1`).

## Test output (pasted, not summarized)
Base full suite (before the edit, at f4f55a7), `python3 -m pytest -q`:
```
1011 passed, 1 skipped in 126.34s (0:02:06)
```
Step 1 (`_se_fields`, `_se_timed05` and the precondition, before the new case), `python3 -m pytest -q tests/test_pipeline_check.py -k shallow_elif_branch`:
```
14 passed, 504 deselected in 3.06s
```
After all edits, same command:
```
16 passed, 504 deselected in 2.88s
```
Collected ids (`--collect-only -q -k shallow_elif_branch`), last two lines plus the count:
```
tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05alt-shallow]
tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05alt-nogit]
16/520 tests collected (504 deselected) in 0.09s
```
One-off probe: run in the scratch worktree with PYTHONDONTWRITEBYTECODE=1, `__pycache__` cleared and `-p no:cacheprovider`. The `_se_edit(... RH_DAY ..., timed, untimed)` line is removed from `_se_timed05`, so ` in <s>s` stays in the log:
```
E           AssertionError: ('1 files changed | tests 1 passed in 0.01s', '1 files changed | tests 1 passed')
tests/test_pipeline_check.py:5421: AssertionError        (x2, timed05-*)
E           AssertionError: ('2 files changed | tests 3 passed in 0.02s', '2 files changed | tests 3 passed')
tests/test_pipeline_check.py:5421: AssertionError        (x2, timed05alt-*)
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-nogit]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05alt-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05alt-nogit]
4 failed, 12 passed, 504 deselected in 1.18s
```
Line 5421 of the probe file (one line shorter than the build) is `assert f == untimed`. The plan expected the `timed05-*` cases to fail; `timed05alt-*` fail at the same assertion with the patched field. The file was restored by copy: `cmp` gave no output and printed `restored`.

Mutants: run in the scratch worktree of HEAD with the built test file copied in, one at a time, on the line under `# item 090: TIMED gate` (`elif unsure("05"):   # item 095: anchor not read in a shallow clone`). Each was restored with `git checkout HEAD -- scripts/check_pipeline.py` in the worktree; `cmp` against a copy gave no output (`restored-cp`).
- M-timed (`elif unsure("05"):` → `elif False:`):
```
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05alt-shallow]
2 failed, 14 passed, 504 deselected in 1.06s
```
- K-timed (`unsure("05")` → `unsure("06")`):
```
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05alt-shallow]
2 failed, 14 passed, 504 deselected in 1.01s
```
Both match the plan: `2 failed, 14 passed`, with exactly the named ids failing.

Other checks:
- `grep -rn SE_FIELD tests/ | wc -l` → `0`
- `python3.11 -m py_compile tests/test_pipeline_check.py && echo py311 ok` → `py311 ok`
- `git diff --stat HEAD -- scripts/ templates/ .claude/ config/ ccbot/ | wc -l` → `0`
- `python3 scripts/check_pipeline.py` → `exit 0`. Its 105-110 lines are all `in progress`, and 108 shows `108: in progress (FULL: next 05)`. One earlier run gave exit 1 with `INCOMPLETE: 109 (no log line for R3)` and `UNCOMMITTED STEP: 109 03-handoff.md`. That was item 109's R3 in progress, and it cleared once 222fb58 was committed. It is not a defect of this build.
- `git stash list | wc -l` → `0`. The scratch worktree was removed and pruned with `git worktree remove --force` and `git worktree prune`.

Full suite after the build, `python3 -m pytest -q` (base + 2 passed, same skips):
```
1013 passed, 1 skipped in 126.84s (0:02:06)
```
Suite: 1013 passed, 1 skipped in 126.84s (0:02:06)

## Real-data effect (diff_reports output, pasted)
not required (tests/test_pipeline_check.py only; `git diff --stat` lists `tests/test_pipeline_check.py | 38 +++++++++++++++++++++++++++++---------`)

## Deviations from plan
- None in the code. The probe also fails the `timed05alt-*` cases, which the plan did not name. They fail at the same `assert f == untimed`, as expected from the shared setup. `SE_ALT_I2` sits directly after `SE_CASES` (the plan says "next to `SE_CASES`").

## Recurring issues checked (item 013)
- RI-001 (ESCALATED): no filter or window rule. The counts are measured: 16 collected, exactly 1 I2 line per fixture (pinned by `len(own_i2) == 1`), and each strip changes the text (pinned by `untimed != timed`).
- RI-014 (OPEN): the shallow TIMED branch is pinned by M-timed and K-timed, each with 2 named failing ids.
- RI-002 (GUARDED): every absent or unchanged case asserts by name (Connectivity check). ccbot/ is unchanged, and the grep has 0 new hits.
- RI-006: every count is copied from a command's printed output.
- RI-008: py311 compile ok, and `re.sub` takes `count=` as a keyword.
- RI-009: probes ran only in the scratch worktree, with no stash (`STASH: none`).
- RI-010: the log line is written with `check_pipeline.py --log`.
- RI-012: no substring classification. The read-back uses the anchored `LOG_LINE`.
- RI-003, RI-004, RI-005, RI-007, RI-011, RI-013: not touched by a test-only change to this fixture.

RI-014: OPEN, unchanged (108 is an EFFICIENCY follow-up to 101; both TIMED mutants killed)
RI-001: ESCALATED, unchanged (no new rule or window)
