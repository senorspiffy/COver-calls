# 05 Build report - 101
Scratch dir: /tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i2-101-r1-d3wgdpjk

Built by I2 on branch `daily-fixes/2026-11-24-b`, plan commit 2fa5d1c. Scratch dir made with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i2-101-r1-", dir="/tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad"))'`. Mutants and output comparisons ran in `<scratch dir>/mut` and `<scratch dir>/base` (`git worktree add --detach`); probe files were restored with `cp` from a scratch copy and `git checkout HEAD -- <file>` inside that worktree, never in the main checkout, never with `git stash`. Both worktrees are removed before handback.

While I built, the branch moved from 2fa5d1c to 38f1911 (commits for 099, 100, 102, 103, 104: work/ and logs/ only). `git diff --stat 2fa5d1c 38f1911 -- scripts/ templates/ .claude/ tests/ ccbot/ config/` prints nothing, so the base suite count and the mutant line numbers still hold.

These are **unit tests of `incomplete`** (scripts/check_pipeline.py). The printed `INCOMPLETE NOT CHECKED:` line and the `committed` wiring from `_head_work_files` are not claimed here; they stay covered by 095 M5/M11.

## Changes made (file: what changed)
- `tests/test_pipeline_check.py`: inserted after `test_round_build_shallow_goes_to_unchecked` (P-e, found by name; the hunk sits before `test_round_build_missing_inputs`, away from the end of the file, RI-009):
  - `SE_FIELD = "1 files changed | tests 1 passed"` (bare `|`, plan research 2).
  - `_se_edit(path, old, new="")`: asserts `old in text`, then replaces it (no silent no-op on fixture drift). `_se_line(path, prefix)`: the one line starting with `prefix`, asserted present exactly once.
  - 7 setup functions `(tmp_path, cp) -> (d, batch_nc, entry)`: `_se_timed05`, `_se_batch05`, `_se_suite05`, `_se_rh05`, `_se_rh06`, and `_se_scratch(step)` for scratch05/scratch06, with the fixtures and entries exactly as in 04.
  - `SE_CASES` (7) and `SE_PARAMS`: 14 `pytest.param(..., id=f"{case}-{mode}")` over `("shallow", "nogit")`.
  - `test_shallow_elif_branch_goes_to_unchecked(tmp_path, case, step, setup, mode)`: cutoff assert (RH_ID 150 >= SUITE_FROM, TIMED_FROM, ROUND_HEADING_FROM, SCRATCH_FROM, ROUND_BUILD_FROM); setup; the timed05 precondition `log_fields_ok(..., timed=False) and not log_fields_ok(...)`; `cp.incomplete(d, logs=..., env=SHALLOW_TEXT or "no git", not_seen=[], batch_nc=batch_nc, unchecked=u, committed={f"work/{RH_ID}/{cp.STEPS[step]}"})`; exact asserts (shallow `got == [] and u == [(RH_ID, entry)]`; no git `got == [entry] and u == []`). No `@NO_GIT`.

File counts (item 012), before this 05 was written:
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
1
$ git diff --stat
 tests/test_pipeline_check.py | 83 ++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 83 insertions(+)
```
1 changed, 0 new, matching the plan's 1 file.

## Connectivity check
- [x] every new function/rule is used: `_se_edit` is called by `_se_timed05`, `_se_suite05` and `_se_scratch`; `_se_line` by `_se_suite05` and `_se_scratch`; each setup is in `SE_CASES`; `SE_CASES` feeds `SE_PARAMS`; `SE_PARAMS` feeds the parametrize; `SE_FIELD` is read by the timed05 precondition.
- [x] every input has a source, every output has a consumer: the fixtures come from `_rh_item` / `_item` (existing helpers); each case's `entry` goes into the exact asserts; the test result goes to the pytest run below and to the I2 log line.
- [x] every branch ends in a defined result: shallow → exact `unchecked`/`got` assert; nogit → exact strict assert; a missing fixture text → `assert old in text` / `len(hits) == 1` fails by name (drift checks D1-D3 below); the timed05 precondition fails by name if the field is timed.
- [x] no leftover TODOs or unused files: `git diff -U0 | grep -E "^\+" | grep -cE "TODO|fillna|nan_to_num|or 0|else 0|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)|: float = 0"` gives 0 (grep exit 1). Scratch files only in my scratch dir. The plan's `SE_ID = RH_ID` alias was left out (Deviations 1), so there is no unused name.
- Missing-data grep: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` → `38`, all from before this item (`git diff --stat -- ccbot/` is empty). No new or changed hit. No dataclass added. The one new comparison is `int(RH_ID) >= cutoff` (ints, never NaN).
- Feasibility numbers (plan's named checks): fixture ID 150 vs cutoffs 87/90/92/97/99 → 5 of 5 cleared, pinned in code by the cutoff assert; 14 cases, 14 passed; 10 mutants, 12 failing ids (below).

## Test output (pasted, not summarized)
Each later round's runs go under their own level-2 heading `## Test output (round N, pasted)`, never under a `###` heading or a `Round N ...` heading (item 091).

`python3 -m pytest -q tests/test_pipeline_check.py -k shallow_elif_branch`:
```
..............                                                           [100%]
14 passed, 485 deselected in 0.66s
```
`python3 -m pytest tests/test_pipeline_check.py -k shallow_elif_branch -v` (ids):
```
test_shallow_elif_branch_goes_to_unchecked[timed05-shallow] PASSED [  7%]
test_shallow_elif_branch_goes_to_unchecked[timed05-nogit] PASSED [ 14%]
test_shallow_elif_branch_goes_to_unchecked[batch05-shallow] PASSED [ 21%]
test_shallow_elif_branch_goes_to_unchecked[batch05-nogit] PASSED [ 28%]
test_shallow_elif_branch_goes_to_unchecked[suite05-shallow] PASSED [ 35%]
test_shallow_elif_branch_goes_to_unchecked[suite05-nogit] PASSED [ 42%]
test_shallow_elif_branch_goes_to_unchecked[rh05-shallow] PASSED [ 50%]
test_shallow_elif_branch_goes_to_unchecked[rh05-nogit] PASSED [ 57%]
test_shallow_elif_branch_goes_to_unchecked[rh06-shallow] PASSED [ 64%]
test_shallow_elif_branch_goes_to_unchecked[rh06-nogit] PASSED [ 71%]
test_shallow_elif_branch_goes_to_unchecked[scratch05-shallow] PASSED [ 78%]
test_shallow_elif_branch_goes_to_unchecked[scratch05-nogit] PASSED [ 85%]
test_shallow_elif_branch_goes_to_unchecked[scratch06-shallow] PASSED [ 92%]
test_shallow_elif_branch_goes_to_unchecked[scratch06-nogit] PASSED [100%]
```
Full suite at base (`<scratch>/base` worktree, 87789b2; same scripts/ and tests/ as 2fa5d1c), `python3 -m pytest -q` tail:
```
..........                                                               [100%]
945 passed, 1 skipped in 106.98s (0:01:46)
```
Full suite at head (main checkout, with the change), `python3 -m pytest -q` tail:
```
........................................................................ [ 97%]
........................                                                 [100%]
959 passed, 1 skipped in 104.52s (0:01:44)
```
945 + 14 = 959; the skip count is unchanged.

Suite: 959 passed, 1 skipped in 104.52s (0:01:44)

### Mutants (03 step 3; `<scratch>/mut` worktree at 38f1911 with the new test file copied in; `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, `__pycache__` cleared; restored with `cp` and `cmp` after each)
```
== M-timed L1062: elif False:   # item 095: anchor not read in a shallow clone
  [timed05-shallow]
1 failed, 13 passed, 485 deselected in 0.65s
  restored: cmp ok, git diff scripts/ empty
== M-batch L1091: elif False:    # item 095
  [batch05-shallow]
1 failed, 13 passed, 485 deselected in 0.73s
  restored: cmp ok, git diff scripts/ empty
== M-suite L1118: elif False:    # item 095
  [suite05-shallow]
1 failed, 13 passed, 485 deselected in 0.74s
  restored: cmp ok, git diff scripts/ empty
== M-rh L1135: elif False:    # item 095
  [rh05-shallow]
  [rh06-shallow]
2 failed, 12 passed, 485 deselected in 0.81s
  restored: cmp ok, git diff scripts/ empty
== M-scratch L1168: elif False:    # item 095
  [scratch05-shallow]
  [scratch06-shallow]
2 failed, 12 passed, 485 deselected in 0.83s
  restored: cmp ok, git diff scripts/ empty
== K-timed L1062: elif unsure("06"):   # item 095: anchor not read in a shallow clone
  [timed05-shallow]
1 failed, 13 passed, 485 deselected in 0.69s
  restored: cmp ok, git diff scripts/ empty
== K-batch L1091: elif unsure("06"):    # item 095
  [batch05-shallow]
1 failed, 13 passed, 485 deselected in 0.79s
  restored: cmp ok, git diff scripts/ empty
== K-suite L1118: elif unsure("06"):    # item 095
  [suite05-shallow]
1 failed, 13 passed, 485 deselected in 0.75s
  restored: cmp ok, git diff scripts/ empty
== K-rh L1135: elif unsure("05"):    # item 095
  [rh06-shallow]
1 failed, 13 passed, 485 deselected in 0.76s
  restored: cmp ok, git diff scripts/ empty
== K-scratch L1168: elif unsure("05"):    # item 095
  [scratch06-shallow]
1 failed, 13 passed, 485 deselected in 0.68s
  restored: cmp ok, git diff scripts/ empty
```
12 failing ids over 10 mutants (7 elif-False + 5 step-key), exactly the ids 03/04 expected; no `-nogit` id failed under any mutant.

Note for I3: my first mutant pass (without `PYTHONDONTWRITEBYTECODE`) gave wrong ids for M-rh (`suite05-shallow`) and K-suite (`batch05-shallow`). Cause: each mutant and its predecessor change the same number of bytes and were written within the same second, so Python reused the previous mutant's `.pyc` (mtime+size check). That run is discarded; the run above disables bytecode and clears `__pycache__`. Re-run mutants the same way.

### Fixture-drift checks (plan: Tests and checks, extra; same worktree, test copy restored with `cp` and `cmp` against the main checkout's file)
```
== D1: removal skipped (line kept)
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[scratch05-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[scratch05-nogit]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[scratch06-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[scratch06-nogit]
4 failed, 495 deselected in 0.98s
== D2: drifted target text (prefix not in file)
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[scratch05-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[scratch05-nogit]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[scratch06-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[scratch06-nogit]
4 failed, 495 deselected in 1.17s
== D3: timed05 precondition with ' in 0.01s' left in field
E            +  where True = <function log_fields_ok at 0x7fc1def38c20>('I2', '150', '1 files changed | tests 1 passed in 0.01s', timed=False)
E            +  and   True = <function log_fields_ok at 0x7fc1def38c20>('I2', '150', '1 files changed | tests 1 passed in 0.01s')
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-shallow]
FAILED tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked[timed05-nogit]
2 failed, 497 deselected in 0.80s
restored
```
D1 (removal disabled) fails through the exact list assert, D2 (drifted text) through `_se_line`'s assert, D3 (timed field) through the 03 step 2 precondition. The scratch05 and scratch06 ids share `_se_scratch`, so D1/D2 fail both. None passes.

### 03 step 4: no code-path change, full-clone output unchanged
`git rev-parse --is-shallow-repository` → `false`. `git diff --stat 2fa5d1c -- scripts/ templates/ .claude/ config/ ccbot/` → no output (only `tests/test_pipeline_check.py` differs).

`python3 scripts/check_pipeline.py` in `<scratch>/mut` at 38f1911, without the change (`git checkout HEAD -- tests/test_pipeline_check.py`) vs with it, whole output:
```
base(38f1911) exit 0
head(38f1911+test) exit 0
$ diff cp_base2.txt cp_head2.txt
(no output)
diff exit 0
```
126 lines each. Head summary lines:
```
INCOMPLETE: none
RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048: no pytest time in 05/06/I2 line; 054: no pytest time in 05/06/I2 line; 055: no pytest time in 05/06/I2 line; 056: no pytest time in 05/06/I2 line; 058: no pytest time in 05/06/I2 line; 059: no pytest time in 05/06/I2 line; 060: no pytest time in 05/06/I2 line
UNTRACKED CHANGE: none
STASH: none
SKIPPED: none
```
(An earlier comparison of a worktree at 87789b2 vs one at 38f1911 differed only in the `102:`/`103:` progress lines, from the other items' commits in between, not from this change; it was replaced by the same-commit comparison above.) 101's own item line moves from `next 05` once this 05 is committed; that is the only expected change, for I3 to see.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: `tests/test_pipeline_check.py | 83 +++`; no ccbot/, config/ or data/ file)

## Deviations from plan
1. `SE_ID = RH_ID` left out: the plan calls it "just an alias; the asserts use `RH_ID`", so it would be a name nothing reads (connectivity rule). The tests use `RH_ID` as planned.
2. Setup functions take `(tmp_path, cp)`, not `(tmp_path)`: batch05 needs `cp.BATCH_STRICT[0]` and scratch05/06 need `cp.STEPS[step]`, and `cp` is loaded by `_cp()` inside the test. Two small helpers (`_se_edit`, `_se_line`) carry the plan's "assert old in text" rule so it is written once.
No other change. No scripts/, templates/, .claude/ or config/ change; no 001 rule text change.

## Recurring issues checked (item 013)
- RI-001 (ESCALATED): no ticker/DTE/delta filter; the only windows are the ID cutoffs, and 150 clears 5 of 5, pinned by the cutoff assert.
- RI-010 (ESCALATED): the I2 log line is written with `check_pipeline.py --log` right after this file, and committed with `commit_step.py`; the 14 ids and every mutant's failing ids are pasted above.
- RI-014 (OPEN): this item's RI. 101 adds tests only; coverage of the `elif unsure` sites in `incomplete` goes from 3 of 8 to 8 of 8.
- Also checked: RI-002 (no defaulted value; exact lists, absent text fails), RI-006 (counts from commands: 945 + 14 = 959, 12 mutant ids counted from the output), RI-009 (placed by name, not at file end; scratch worktrees only), RI-012 (exact list equality; BATCH_STRICT passed as the constant), RI-013 (whole-output diff of check_pipeline).

RI-001: ESCALATED, unchanged (no filter in this item)
RI-010: ESCALATED, unchanged (no new occurrence)
RI-014: OPEN, unchanged (tests only; stays OPEN until 079/081/088-095 merge)
