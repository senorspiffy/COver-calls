# 06 Verification - 088
Verdict: PASS (round 1)
Sent back to: none

Verified at head d6715d5 (I2 build commit) in my own worktree `/tmp/claude-0/scratch/i3-088/head`; mutations in `/tmp/claude-0/scratch/i3-088/mut` (both removed after). `git rev-parse --is-shallow-repository` → false.

## I1 audit (plan vs research)
- 04 follows 03's map step by step: step 1 fixtures (u), (u-s), (h); step 2 d1 rows + M-c/M-d before-run; step 3 `_anchor_env` → `(env, failed)`, `_rule_seen` head block removed, `or env_failed` in the exit expression; step 4 census (`("_rule_seen","_git")` deleted, `("_anchor_env","_git")` 1 → 2, total 47); step 5 docstrings with the call counts; two stages so A1's mutations are shown on the code A1 mutated. The Rule trace has a row for every 03 step and decision; the two DROPPED rows (anchor cache, "costs 0" claim) are the ones 03 removed.
- Additions not in 03, each with a stated source: (1) build order (088 first, re-read on today's HEAD); (2) (u-s) as its own test (S13 body commits first); (3) M-h for the verify-None branch; (4) the exit-1 "known gap" docstring, sourced from git's `builtin/rev-parse.c` (`die_no_single_rev`); (5) patching `cp._anchor_env` rather than `_git` because `_inbox_gate` runs the same command (code, grep). All acceptable.
- (6) E1 (`"RULE NOT SEEN:"` in GIT_LINES) is an I1 addition sourced from RI-014. Its premise was wrong: 04 said (b) and (c) give `"unreadable"` → `not checked (shallow clone; ...)`. On today's code (c) (non-UTF-8 shallow line) gives `RULE NOT SEEN: none`. I re-ran it (below). That result only holds after 089's `_shallow_boundaries` decode change. This is a factual error in 04, but it adds no code to 088, and I2 caught it by computing it rather than assuming it (RI-001). Not a FAIL reason, see Deviation 1.

## I2 audit (build vs plan)
Line by line, `git diff d6715d5~1 d6715d5 -- scripts tests`:
- `_anchor_env`: no git → `("no git", False)`; shallow/unreadable → `(shallow text, False)`; verify `None` → `("no git", False)`; 0 → `(None, False)`; 1 → `("unborn HEAD", False)`; other → `("git rev-parse --verify HEAD failed (exit <n>)", True)`. Docstring has the contract, the exit-1 known gap and "read once (item 088)". Matches 04.
- `_rule_seen`: head block (old L643-648) deleted, `failed = ...` kept before `log`; docstring updated. Matches.
- `main`: `(env, env_failed), not_seen = _anchor_env(), []` and `or env_failed` at the end of the exit expression; the RULE NOT SEEN print is unchanged. Matches. `_anchor_env` has one caller (L1548), `incomplete` has one caller (L1579, passes env), so no path calls `_rule_seen` with an unread HEAD and env None except unit tests.
- Module docstring L273-281: uncommitted 05/06 strict with no entry, unborn → `not checked (unborn HEAD)`, failed verify → `not checked (...)` + exit 1, counts 3 wrapper calls = 6 processes per full pair, +1 per run, early exits 0/1/2, at most 3 pairs, pre-088 4 = 8. Matches 03 step 5 and the code (log, ls-tree, show are the only 3 `_git_ok` calls left in `_rule_seen`).
- Tests: (u), (u-s), (h) stage-B form, `test_anchor_env_reads_head_once` (exit 0, 128, None), `test_anchor_env_failure_exits_1`, d1 ls-tree row, census. All as planned, except:

Deviations (05), judged:
1. **E1 not applied.** Accepted. Confirmed by my own probe: with E1 on d6715d5, `test_non_utf8_shallow_line_no_traceback` fails with `RULE NOT SEEN: none` (`1 failed, 3 passed`). The `none` comes from `_shallow_boundaries` reading a bad shallow file as "full", which is item 089's subject (non-UTF-8 shallow line), not 088's HEAD read. The failed-verify path E1 was meant to pin is already pinned twice (M-e, M-f, M-i, M-h below each fail a named test). Option (b) in 05 (move E1 to 089, after its decode change) is the right one. **089's 04 currently says "GIT_LINES unchanged" (L157) and assumes GIT_LINES already ends with `"RULE NOT SEEN:"` (L10). That is not true at d6715d5.** 089's I2 must add E1 after its decode change and show (a), (b), (c) pass (07 point 3). Applying E1 to (a)/(b) only (option a) would need a second tuple for one test, which is not simpler.
2. **`test_anchor_env_failure_exits_1` uses a complete item 150 (`_item(..., ALL)`), not `_defective`.** Accepted. 04 asked for a "clean repo (which exits 0)", and `_defective` does not exit 0 once env is set. With the plan's literal fixture, M-f survived (I2: `36 passed`). With I2's fixture, M-f fails (my re-run below). The added `INCOMPLETE: none` assert pins that exit 1 comes from `env_failed` alone.
3. The stage-A form of (h) was used only for the M-b run and was then replaced by the stage-B form, as in plan step 6. Fine.

Connectivity re-done: `env` → `incomplete` → `_rule_seen` and → the RULE NOT SEEN print (L1629); `env_failed` → exit expression (L1658); the inbox early return already returns 1. No unused code. `git status --porcelain -- . ':!work' ':!logs'` at HEAD: clean except other agents' work/ files. Missing-data grep reason in 05 checked: the only new `else 0` is the existing clean-exit value of main's return, and `env_failed` only adds a route to 1. No new numeric or dataclass default.

check_handoff (re-run by I3, 2026-11-21 23:51 UTC, exit 0):
```
sources count (unique URLs in 01-research.md): 5
fact-check rows: 38
totals line: 38 rows -> 28 as-is, 9 fixed, 1 removed
PASS
```

## Tests re-run (output)
Full suite, my own run at d6715d5 (`/tmp/claude-0/scratch/i3-088/head`, `python3 -m pytest -q -p no:cacheprovider`), last lines:
```
...............................                                          [100%]
678 passed, 1 skipped in 82.60s (0:01:22)
```
Skip: `tests/test_calendar.py:110: could not import 'exchange_calendars'` (known). This equals 05's `678 passed, 1 skipped`.
`tests/test_safety.py::test_every_py_compiles_on_oldest_python` ran (python3.11 on PATH; python3.10 absent): `1 passed, 8 deselected`.

Mutations (RI-002), my own, scratch worktree of d6715d5, `pytest -q tests/test_pipeline_check.py -k "rule or anchor or suite or census"`, file restored with `git checkout` after each:

| Mutation | Result |
|---|---|
| none | `36 passed, 274 deselected` |
| M-a (A1's finding 1: `if not sha: return False, ""`) | FAILED `test_rule_anchor_uncommitted_step_is_strict`, `test_suite_gate_uncommitted_05_is_strict`; `2 failed, 34 passed` |
| M-b' (A1's finding 2 at head: exit-1 branch removed) | FAILED `test_rule_anchor_unborn_head_is_strict` (line reads `not checked (... failed (exit 1))`); `1 failed, 35 passed` |
| M-b'' (unborn → `(None, False)`) | FAILED `test_rule_anchor_unborn_head_is_strict`; `1 failed, 35 passed` |
| M-e (`== 1` → `!= 0`) | FAILED `test_anchor_env_reads_head_once`; `1 failed, 35 passed` |
| M-f (`or env_failed` dropped) | FAILED `test_anchor_env_failure_exits_1`; `1 failed, 35 passed` |
| M-g (`_rule_seen` env set → `False, ""`) | `10 failed, 26 passed` (e1/e2, (h), 8 Suite tests) |
| M-h (verify None → `(None, False)`) | FAILED `test_anchor_env_reads_head_once`; `1 failed, 35 passed` |
| M-i (new, I3: failed verify → `failed False`) | FAILED `test_anchor_env_reads_head_once`; `1 failed, 35 passed` |
| M-d (ls-tree failure → `False, ""`) | FAILED `test_rule_anchor_git_failure_is_incomplete`; `1 failed, 35 passed` |
| census probe (old `rev-parse --verify` call put back in `_rule_seen`) | FAILED `test_git_call_census`; `1 failed` |
| E1 probe (`"RULE NOT SEEN:"` appended to GIT_LINES) | FAILED `test_non_utf8_shallow_line_no_traceback` (`RULE NOT SEEN: none`); `1 failed, 3 passed` |

BUG checks:
- Fix in place: the unknown anchor (uncommitted 05/06, unborn, failed verify, verify None) is strict at head.
- Guardrail in place and it catches the original error: A1's two surviving mutations were `return False, ""` on the `if not sha` line and on the unborn return. The first (M-a) is literally the same edit at head and fails (u) and (u-s). The second no longer exists as a line after the move (the unborn return moved into `_anchor_env`); its equivalents M-b' and M-b'' fail (h). I2's stage-A run in 05 showed M-b failing (h) on pre-move code.
- RI-001 feasibility: (u) and (h) reach the TESTS and VERDICT gates (they print `INCOMPLETE: 150 (log line for I2 ...; 06 Verdict is PASS but has no 'Sent back to: none' line (item 071))`), and (u-s) reaches SUITE (`INCOMPLETE: 151 (05 has no 'Suite:' line (item 082))`). These are pinned by exact asserts in the tests that passed above. No rule text cites a count.
- Data-hole edges: not applicable (no data window).
- Rule the person follows (001): not changed.
- Text-match classification (RI-012, item 059): none added. Exit 1 comes from the bool `env_failed`, never from the env text. No negative test is needed.
- Simulator/replay (item 062): not applicable.

## Real-data effect (diff_reports output, pasted)
not required (scripts/check_pipeline.py | 47, tests/test_pipeline_check.py | 119; no TRIGGER file changed)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014, RI-002, RI-012, RI-008, RI-009 (open/ESCALATED: RI-001, RI-010, RI-014)
- RI-001 (ESCALATED): every gate-reach claim is from a run, not assumed. 04's E1 claim about (c) was computed and is false today; recorded, sent to 089.
- RI-010 (ESCALATED): my log line is written only via `check_pipeline.py --log`, right after this file. My pytest run above (82.60 s) took place between I2's line (23:46) and mine.
- RI-014 (OPEN): a failed HEAD verify gives `not checked (...)` + exit 1, never `none` (M-e, M-f, M-h, M-i fail). One remaining `none` under a non-UTF-8 shallow file belongs to 089 (E1 probe). Status unchanged: OPEN. The guardrail was extended by 088.
- RI-002 (GUARDED): A1's removed-default mutation was put back in scratch and fails 2 tests (M-a).
- RI-012 (GUARDED): bool, no text match.
- RI-008 (GUARDED): the oldest-Python compile test ran with python3.11 and passed; python3.10 is absent.
- RI-009 (GUARDED): mutations ran only in the scratch worktree, which is removed. I staged only my own files.

## Pipeline line (step 2)
check_pipeline line: `088: awaiting A1 (FULL)` (exit 0, 23:53 UTC, after 06 and the --log line were written)

## Sent back / sent to Audit
Sent to Audit: work/088/07-audit-task.md.
