# 05 Build report - 088
Built on daily-fixes/2026-11-21, base 8013486 (04 commit); HEAD at build time 4de4e37 (other items' R3 commits only; `git diff --stat 8013486 4de4e37 -- scripts tests` is empty).

Before-state (step 0 of 04), `python3 scripts/check_pipeline.py` on the worktree before the first edit (2026-11-21 23:37 UTC, exit 1):
```
INCOMPLETE: 089 (no log line for R3)
RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)
```
The `INCOMPLETE: 089` entry was another agent's 089/03, not yet committed then (UNCOMMITTED STEP said the same). It was committed in d34a744 before the after-run.

## Changes made (file: what changed)
- `scripts/check_pipeline.py`:
  - `_anchor_env()` now returns `(env, failed)` and reads `rev-parse --verify -q HEAD` once per run. The outcomes are: `None` gives "no git"; exit 0 gives `(None, False)`; exit 1 gives `("unborn HEAD", False)`; any other exit gives `("git rev-parse --verify HEAD failed (exit <n>)", True)`. The docstring states the exit-1 known gap.
  - `_rule_seen`: the per-pair `head` block is removed, and the docstring is updated.
  - `main`: `(env, env_failed), not_seen = _anchor_env(), []`, and `or env_failed` is added to the exit expression.
  - The module docstring's RULE NOT SEEN paragraph is rewritten: uncommitted 05/06, unborn, failed verify (exit 1), and the call counts.
- `tests/test_pipeline_check.py`:
  - new tests: (u) `test_rule_anchor_uncommitted_step_is_strict`, (u-s) `test_suite_gate_uncommitted_05_is_strict`, (h) `test_rule_anchor_unborn_head_is_strict` (stage-B form), `test_anchor_env_reads_head_once` (including the M-h row), `test_anchor_env_failure_exits_1`;
  - d1 gains the ls-tree row;
  - GIT_CENSUS: `("_rule_seen","_git")` is deleted and `("_anchor_env","_git")` is now 2 with its reason. The total stays 47.
  - E1 is NOT applied (see Deviations 1).

File counts:
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → 2

## Connectivity check
- [x] Every new function or rule is used:
  - `_anchor_env`'s tuple is unpacked in `main`;
  - `env` goes to `incomplete` → `_rule_seen` and to the RULE NOT SEEN print;
  - `env_failed` goes to the exit expression;
  - each new test pins a branch (mutations below).
- [x] Every input has a source and every output has a consumer:
  - the verify result → `env` → the `RULE NOT SEEN: not checked (...)` line;
  - `failed` → exit 1.
- [x] Every branch ends in a defined result:
  - `_git` None → "no git";
  - 0 → anchors read;
  - 1 → "unborn HEAD", strict;
  - other → not checked + exit 1.
  - The inbox early return already returns 1.
- [x] No leftover TODOs or unused files. The scratch worktree /tmp/claude-0/scratch/i2-088/wt was removed (`git worktree list` no longer shows it).
- Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 38 hits, none new. `git diff --stat -- ccbot/` is empty.
  - The only changed matching line in the diff is outside ccbot: `scripts/check_pipeline.py` exit expression `... or env_failed else 0`. Reason: the `0` is the existing clean-exit value, and `env_failed` only adds a way to reach 1.
  - No dataclass or numeric default was added.
  - No `>`/`<` test on possibly-NaN values was added; the new comparisons are on integer git exit codes from a non-None tuple.

## Test output (pasted, not summarized)
Suite: 678 passed, 1 skipped in 85.99s (0:01:25)

`python3 -m pytest -q` from the repo root, last lines:
```
........................................................................ [ 95%]
...............................                                          [100%]
678 passed, 1 skipped in 85.99s (0:01:25)
```
`python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` → exit 0 (RI-008).

Mutations (scratch worktree `/tmp/claude-0/scratch/i2-088/wt` of HEAD, files copied in; `pytest -q tests/test_pipeline_check.py -k "rule or anchor or suite or census"`; outputs as printed):

Stage A (today's code):

| Mutation | Test file | Result |
|---|---|---|
| M-c (`if head[1] != 0: return False, ""`) | HEAD (no new d1 rows) | `30 passed, 275 deselected`. Survived, as expected before the rows |
| M-d (ls-tree `if why: return False, ""`) | HEAD (no new d1 rows) | `30 passed, 275 deselected`. Survived |
| M-c | stage A (rows added) | `FAILED test_rule_anchor_git_failure_is_incomplete`, `1 failed, 32 passed` |
| M-d | stage A | `FAILED test_rule_anchor_git_failure_is_incomplete`, `1 failed, 32 passed` |
| M-a (`if not sha: return False, ""`) | stage A | `FAILED test_rule_anchor_uncommitted_step_is_strict`, `FAILED test_suite_gate_uncommitted_05_is_strict`, `2 failed, 31 passed` |
| M-b (`head is None or ==1: return False, ""`) | stage A | `FAILED test_rule_anchor_unborn_head_is_strict`, `1 failed, 32 passed` |

Stage B (built code, final test file):

| Mutation | Result |
|---|---|
| unmutated | `36 passed, 274 deselected` |
| M-b' (exit-1 branch removed) | `FAILED test_rule_anchor_unborn_head_is_strict`, `1 failed, 35 passed` |
| M-e (`== 1` → `!= 0`) | `FAILED test_anchor_env_reads_head_once`, `1 failed, 35 passed` |
| M-f (`or env_failed` dropped) | `FAILED test_anchor_env_failure_exits_1`, `1 failed, 35 passed` (after Deviations 2; with the plan's fixture it gave `36 passed`) |
| M-g (`_rule_seen` env set → `False, ""`) | `10 failed, 26 passed`, including `test_rule_not_seen_shallow_and_no_git` (e1/e2) and `test_rule_anchor_unborn_head_is_strict` (plus 8 Suite tests) |
| M-h (verify None → `(None, False)`) | `FAILED test_anchor_env_reads_head_once`, `1 failed, 35 passed` |
| census probe (old `rev-parse --verify` call back in `_rule_seen`) | `FAILED test_git_call_census`, `1 failed, 35 passed` |
| M-d on stage B | `FAILED test_rule_anchor_git_failure_is_incomplete`, `1 failed, 35 passed` |

E1 probe (`"RULE NOT SEEN:"` appended to GIT_LINES; `-k "all_git_fails or malformed_shallow or non_utf8_shallow"`):

| Code | Result |
|---|---|
| stage-A code | `FAILED test_all_git_fails_no_line_says_none`, `FAILED test_non_utf8_shallow_line_no_traceback`, `2 failed, 2 passed` |
| stage-B code | `FAILED test_non_utf8_shallow_line_no_traceback`, `1 failed, 3 passed` |

After-state check, `python3 scripts/check_pipeline.py` on the built worktree (exit 0):
```
INCOMPLETE: none
RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)
```
`diff before.txt after.txt`:
- The RULE NOT SEEN line is identical.
- The other differences are other items moving on: 087/090/091 `next 03` → `next 04`; `INCOMPLETE: 089 ...` → `none` and `UNCOMMITTED STEP: 089 ...` → `none`, because 089's 03 was committed in d34a744.

Feasibility (gate reach, real fixture output):
- TESTS + VERDICT gates are reached by item 150 in (u) and (h). Both print `INCOMPLETE: 150 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed>"; 06 Verdict is PASS but has no 'Sent back to: none' line (item 071))`.
- SUITE gate: (u-s) item 151 prints `INCOMPLETE: 151 (05 has no 'Suite:' line (item 082))`.
- (u) pin: `git log --diff-filter=A ... work/150/05-build-report.md` → `(0, "")`.
- (h) pins: `rev-parse --verify -q HEAD` → returncode 1; `--is-shallow-repository` → `false`; line `RULE NOT SEEN: not checked (unborn HEAD)`.
- HEAD: 083 = 2 pairs, both `cfc0634`, unchanged.

## Real-data effect (diff_reports output, pasted)
not required (scripts/check_pipeline.py | 47, tests/test_pipeline_check.py | 119; no ccbot/ or config/ file)

## Deviations from plan
1. **Sent back to I1: E1 makes fixture (c) fail on both stage-A and stage-B code.**
   - The plan says that in (b) and (c) "the shallow file is malformed → `"unreadable"` → `not checked (shallow clone; ...)`".
   - Measured in (c) (non-UTF-8 shallow line):
     - `git rev-parse --is-shallow-repository` exits 128 (`fatal: bad shallow line`), so `_shallow_boundaries` is not "sure";
     - `read_text` raises UnicodeDecodeError → `"full"`;
     - `rev-parse --verify -q HEAD` exits 0 → env None;
     - item 150 is complete, so no gate fires and the line reads `RULE NOT SEEN: none` (`1 failed, 3 passed`, above).
   - The "unreadable" result the plan expects comes from 089's `_shallow_boundaries` decode change, which is not built yet. 088 builds first.
   - I did not improvise a workaround (skipping the line in (c) or changing `_shallow_boundaries`), so E1 is left out and GIT_LINES is unchanged.
   - Options for I1: (a) apply E1 to (a) and (b) only; (b) move E1 to 089, after its decode change; (c) build 088 after 089.
   - E1 did catch the stage-A gap in (a) as planned (fails on stage A, passes on stage B). The failed-verify path is also pinned by `test_anchor_env_failure_exits_1` and `test_anchor_env_reads_head_once`.
2. **`test_anchor_env_failure_exits_1` fixture: item 150 is complete (`_item(repo, "150", ALL)`), not `_defective`.**
   - With the (i)-shape `_defective` item, a set env makes 150 strict → INCOMPLETE → exit 1 anyway. So M-f (`or env_failed` dropped) survived (`36 passed`).
   - With a complete item the unpatched run exits 0 and the patched run reaches 1 only through `env_failed`, so M-f fails (above).
   - I also added `INCOMPLETE: none` as an assert on the patched run. This fits the plan's "clean repo (which exits 0)" wording, but I1 and I3 should confirm it.
3. The (h) stage-A form (`RULE NOT SEEN: none`, `cp._anchor_env() is None`, `_rule_seen(..., None)`) was used for the M-b run, then changed to the stage-B form as in plan step 6. The stage-A test file was kept in scratch only and is now removed.

Recurring issues checked (open/ESCALATED; others re-read):
- RI-001 (ESCALATED): every gate-reach claim has its fixture and real printed line (Feasibility). E1's "(c) is unreadable" claim was computed and found false, so it was not assumed (Deviations 1).
- RI-010 (ESCALATED): the log line is written only by `check_pipeline.py --log`, and the Suite line is copied as printed.
- RI-014 (OPEN): a failed verify gives `not checked (...)` + exit 1, never `none` (M-e, M-f, M-h fail). (c) shows one remaining `none` under a bad shallow file, sent to I1.
- RI-002: the unknown anchor (uncommitted, unborn, failed verify, verify None) stays strict, with a fixture for each.
- RI-008: py_compile with python3.11 exits 0.
- RI-009: mutations ran only in a scratch worktree, which is removed. Only my files are staged.
- RI-012: `env_failed` is a bool, with no text match.
- RI-006: file counts are taken from commands (above).

RI-014: guardrail extended (088: HEAD verify read once, failed verify → exit 1). Status unchanged (OPEN). The E1 pin is pending I1 (Deviations 1).
RI-002: GUARDED, unchanged. Unknown anchors are strict, pinned by (u), (u-s) and (h).
