# 04 Build plan - 066
Fit verdict: FIT WITH CHANGES

Input: work/066/03-handoff.md (Status: READY, `check_handoff.py 066` PASS as pasted), 01, 02, request.md. Repo read on daily-fixes/2026-11-15 at 416970e ("Item 066: R3 hand-off (READY)"). Item 065 is in the same tree; this plan touches nothing of 065's.

**Fit check.**
- ~$3k account / strategy rules: not affected. This is test-suite infrastructure only. No ccbot/, config/, scripts/ or rule-text change, and no brokerage contact.
- Existing code: the handoff's line references hold at 416970e. `_run` is at tests/test_pipeline_check.py L43-46, `test_repo_pipeline_has_no_skipped_items` at L139-144 (its `_run(REPO, ...)` at L141), `NO_GIT` at L604, the first `@NO_GIT` user at L635, and `test_work_code_pattern` at L987-1003 (constant asserts at L1001-1003). `test_research_code_rules` is at L841. `_git` in check_pipeline.py L359-367 needs `--show-toplevel` == cwd, and that holds in a linked worktree (03, 01 F8). `INCOMPLETE: <ids or none>` is printed at check_pipeline.py L643. L141 is the only `_run(REPO, ...)` in tests/. The other `cwd=REPO` uses (L149, L808, L813, test_safety L120/L127) read git metadata only, which uncommitted step files don't affect.
- Conflicts: none with anything built. run-item.md L14 already requires an in-tree `check_pipeline.py` run at the end of each item, so that run remains the check that sees uncommitted step files (02 AGAINST 1).
- **Change from 03 (why "WITH CHANGES"):** the new behaviour is a filter: "the repo test sees committed state only". The 03 map pins it only with R3's one-off manual probe (step 2 (b)). If someone put `_run(REPO, ...)` back, no suite test would fail. I1 step 1a requires a planned test that pins every filter rule. So the worktree logic moves into a small helper `_run_head`, and a fixture test uses that helper on a throwaway repo that has an uncommitted item. This adds one more test (target +2, not +1). It is still one file, and it reuses the existing `_history`/`_item` fixtures.

Recurring issues checked (item 013), against this file: RI-001 (ESCALATED). The committed-only filter has a dated non-zero count in 03 (1 of 1 cross-item case caught, R3 probe on 1402b36, 2026-11-15), and this plan adds a suite test that pins it (T2). RI-002 (ESCALATED). No missing input becomes a pass. No git → skip with a reason. A git failure → assert with stderr. There is no fallback to `REPO`, and the T2 absent-case is listed under Guardrail tests. Also checked: RI-006 (the counts below are derived from 03's measured numbers with the arithmetic shown, and I2 re-measures them), RI-008 (3.10-safe syntax only: no `match`, no new imports beyond `pathlib.Path` if it isn't already imported, and `test_every_py_compiles_on_oldest_python` covers it), RI-009 (git runs only `worktree add/remove` with `cwd=REPO` or the fixture repo; no stash/checkout/reset in REPO; I1 created no worktrees), RI-010 (this file is written before its `--log` line, and the line goes through `check_pipeline.py --log`). RI-003, RI-004, RI-005, RI-007, RI-011 and RI-012 don't apply: there is no calendar, worked price example, Scope/commit rule, branch diff or error-text parsing here.

## Extra research (with sources)
1. **git-worktree flags** (https://git-scm.com/docs/git-worktree, fetched 2026-11-15). The page says "`-q`, `--quiet`: With `add`, suppress feedback messages". It also says "`--detach`: With `add`, detach `HEAD` in the new worktree", and it recommends a "throwaway worktree not associated with any branch" via `git worktree add -d <path>` "to do testing without disturbing existing development". That confirms the planned `add --detach -q <wt> HEAD`. The page doesn't say what `add` does when `<path>` already exists as a plain directory, so the plan uses a path that doesn't exist yet (`tmp_path / "head"`, which pytest never creates).
2. **The script under test is the working-tree one; the data is committed.** `_run` calls `REPO / "scripts" / script` and stays unchanged. So in the worktree run, the *current* (possibly uncommitted) check_pipeline.py runs against *committed* work/ and logs/. This is intended: an I2 edit to check_pipeline.py is still tested by this test before it's committed. I2 must not "fix" it to call `wt / "scripts"`, because that would test HEAD's script and hide an uncommitted script regression. The docstring says so.
3. **A simpler pin than a manual probe** (repo code, tests L464-470, L604-627). `_history(tmp_path)` already builds a git repo with complete item 150 committed as the cutoff, and `_item(..., logged=False)` writes step files with no log lines. Together they reproduce 063's failure shape (an uncommitted step file with no log line) in about 8 lines, without touching REPO. That makes R3's probe (b) a permanent test.
4. **Edge case R3 didn't cover:** what HEAD means when REPO is itself a linked worktree (as in I3/A1 scratch probes). `git worktree add` run with `cwd` in a linked worktree resolves `HEAD` to *that* worktree's HEAD (each worktree has its own HEAD, 01 F9 quote "shares all but HEAD, index"). So a scratch-worktree probe tests the probe's commit, as intended. The page has no specific note on running `add` from a linked worktree, so I3 confirms this once by running the test inside its scratch worktree (check C5).

## Files to create/change
Only **tests/test_pipeline_check.py** (1 file). Nothing under scripts/, ccbot/, config/, .claude/ or logs/ except this step's own log line.

1. **Move `NO_GIT`** (03 step 1). Move the line `NO_GIT = pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")` from L604 to just before `def _run` (L43). Nothing else moves. Every existing `@NO_GIT` (L635 onward) still resolves.
2. **New helper `_run_head(root, tmp, script, *args)`**, placed right after `_run`:
   - Docstring: "`_run` on a detached worktree of `root`'s HEAD, so only committed work/ and logs/ are seen (item 066). The script itself is still `REPO/scripts` (the working-tree copy)."
   - `wt = tmp / "head"`
   - `add = subprocess.run(["git", "worktree", "add", "--detach", "-q", str(wt), "HEAD"], cwd=root, capture_output=True, text=True, encoding="utf-8")`
   - `assert add.returncode == 0, add.stderr`
   - `try: return _run(wt, script, *args)`
   - `finally: subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=root, capture_output=True)` (result not checked, see Missing inputs)
3. **`test_repo_pipeline_has_no_skipped_items`** (03 step 2): add `@NO_GIT` and a `tmp_path` parameter. Replace the body line `code, out = _run(REPO, "check_pipeline.py")` with `code, out = _run_head(REPO, tmp_path, "check_pipeline.py")`. Keep the three asserts unchanged (`code == 0, out`; `"RESEARCH CODE: none"`; `"061: complete"`). New docstring: "The committed work/ folder: no item may skip a step (RI-007). Runs on a detached worktree of HEAD, so another item's uncommitted step files in this tree don't fail it (item 066); run check_pipeline.py in the tree for uncommitted files (run-item.md)."
4. **New `test_head_run_ignores_uncommitted_item(tmp_path)`** (the pin added by I1), `@NO_GIT`, placed right after `_history` (after L627, since it uses `_history`/`_item`):
   - `repo, cutoff = _history(tmp_path)`
   - `_item(repo, "151", ["01-research.md"], date="2026-11-11", logged=False)`, uncommitted, with no R1 line (063's shape)
   - `args = ("--today", "2026-11-11", "--untracked-from", cutoff)`
   - `code, out = _run(repo, "check_pipeline.py", *args)`, then `assert code == 1 and "INCOMPLETE: 151" in out`. This is the control: the tree-level run still sees it.
   - `code, out = _run_head(repo, tmp_path, "check_pipeline.py", *args)`, then `assert "INCOMPLETE: none" in out, out` and `assert code == 0, out`
   - `wl = subprocess.run(["git", "worktree", "list"], cwd=repo, capture_output=True, text=True).stdout`, then `assert str(tmp_path / "head") not in wl`. Cleanup is pinned in the suite, not only by I3's check.
   - If I2 measures a code other than 0 on the HEAD run for a reason unrelated to 066 (another check line in the fixture), drop only that `code == 0` assert, keep the INCOMPLETE asserts, and state the line in 05.
5. **Split the constant asserts** (03 step 3): cut L1001-1003 unchanged out of `test_work_code_pattern` into a new `def test_is_code_examples():`, placed right after it, with docstring "Item 066: fixed `_is_code` examples, checked once instead of in every pattern case.", `cp = _cp()`, then the three asserts. `test_work_code_pattern` keeps its 8 cases and its 2 asserts (L999-1000).

## Tests and checks
| # | Check | Expected |
|---|---|---|
| C1 | `python3 -m pytest --collect-only -q tests/test_pipeline_check.py` | collects with no error; 88 → **90** (+1 `test_is_code_examples`, +1 `test_head_run_ignores_uncommitted_item`) |
| C2 | `python3 -m pytest -q -p no:cacheprovider` (full suite) | **318 passed, 1 skipped**. Base measured by R3 on 1402b36 is 316/1, so 316 + 2. If 065 has committed tests by then, the target is I2's measured base + 2. 05 states that base and lists any uncommitted 065 files present. |
| C3 | Pin mutation A (scratch worktree only, never REPO): `_run_head` body replaced by `return _run(root, script, *args)` | `test_head_run_ignores_uncommitted_item` fails (`INCOMPLETE: 151`), 1 failed |
| C4 | Mutation (i) from 064/06 (`_is_code` → `return f.startswith(paths)`, scratch worktree) | 2 `test_work_code_pattern` cases (the `True` paths) + `test_is_code_examples` once + the 5 non-pattern tests listed in 03's self-check = **8 failed, 82 passed** (90 − 8). 03 measured 8 failed / 81 passed at 89 collected, and the new T2 doesn't call `_is_code` on a changed path. If T2 does fail, 05 explains why. |
| C5 | R3's probe (b), rerun in a scratch worktree where REPO = that tree: an uncommitted `work/999/request.md` (Scope FULL) + `01-research.md`, no R1 line | old body: 1 failed `INCOMPLETE: 999 (no log line for R1)`; new body: 1 passed. This also confirms extra-research point 4 (HEAD = the scratch tree's HEAD). |
| C6 | `git -C REPO status --porcelain -uall` before and after C2 | identical |
| C7 | `git -C REPO worktree list` after C2 | no entry under pytest's tmp dir |
| C8 | `python3 -m pytest --durations=5 tests/test_pipeline_check.py` | the repo test < 2 s (03: 0.54 s) and the T2 fixture < 2 s |
| C9 | `python3 scripts/check_pipeline.py` in the tree (run-item L14) | 066 not SKIPPED/INCOMPLETE, and `LOG TIME:` doesn't name it |

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1: move `NO_GIT` above `_run` | Files 1; C1 |
| Step 2: repo test on a detached HEAD worktree, `@NO_GIT`, `tmp_path`, assert add rc with stderr, `finally` remove `--force`, 3 asserts kept, docstring, nothing written in REPO | Files 2-3 (logic moved into `_run_head`, same behaviour); C2, C6, C7, C8 |
| Step 2 check (b) probe old fails / new passes | Files 4 (made a permanent test, T2) + C3; C5 kept as a manual rerun |
| Step 2 check (c) no worktree left | Files 4 last assert (in-suite) + C7 |
| Step 2 check (d) REPO status unchanged | C6 |
| Step 2 check (e) < 2 s | C8 |
| Step 3: three constant asserts → `test_is_code_examples`; 8 cases + 2 asserts kept | Files 5; C1, C4 |
| Step 4: full suite target (03: 317 passed, 1 skipped = 316 + 1) | Changed to **318 passed, 1 skipped** (316 + 2) because of the I1-added T2; C2 |
| Step 4: in-tree `check_pipeline.py` run | C9 |
| Correction "Pass count vs the request" (+1 accepted by A1, nothing merged away) | Kept. Now +2: one test pins the new filter, the other is 03's split. The request's "same pass count minus the merged cases" still has 0 merged cases. 05 says so. |
| Correction 01 F12: skip only without git; git failure → assert with stderr; no fallback to REPO | Files 2 (assert in `_run_head`), Files 3 (`@NO_GIT`); Guardrail tests below |
| Correction 01 F11 / 02 AGAINST 3: full checkout is cheap, no `--no-checkout`, no sparse-checkout | Kept: plain `worktree add --detach` |
| Removed claims (6-10 lines estimate; sparse-checkout config claim) | DROPPED: removed in 03, nothing to build |
| Map header: no change to run-item.md, rule files, scripts/, ccbot/, config/; no brokerage | Files: only tests/test_pipeline_check.py |
| Missing input: running item's own uncommitted files not seen by this test | Docstring in Files 3 points to the run-item in-tree run; C9 |
| Rule text the person follows (001: slack, tolerance, cap) | Not changed; no rule-text update or new request needed |

## Guardrail tests
- Feasibility: "the repo test sees committed state only" → `test_head_run_ignores_uncommitted_item`. Its dated count: 1 of 1 cross-item case caught (R3 probe on 1402b36, 2026-11-15; 063's real failure on 2026-11-15). The test's control assert (`INCOMPLETE: 151` on the direct run) proves the fixture triggers the rule (count 1, not 0) before it checks that the HEAD run doesn't see it. Mutation A (C3) shows the test fails if the filter is removed.
- Feasibility: "constant `_is_code` examples are checked once" → `test_is_code_examples` plus C4: mutation (i) fails it once, not 8 times (03: 3 × 8 = 24 runs → 3).
- Missing inputs: `git` not on PATH → both git-using tests are skipped by `@NO_GIT` with reason "git not on PATH", never passed. This is pinned by the existing `NO_GIT` marker semantics. No new skip path.
- Missing inputs: no HEAD / not a repo at `root` → `_run_head`'s `assert add.returncode == 0, add.stderr` fails loudly. I2 runs the absent case once in a scratch dir: `_run_head(<empty tmp dir>, ...)` → AssertionError carrying git's "not a git repository" stderr, and records it in 05. There's no permanent test, since an empty dir never occurs in the real call, and the assert line itself is the guard.
- Missing inputs: worktree removal fails (killed run) → not asserted inside `finally`, so it never masks the real assert. A stale entry shows in `git worktree list` (C7) and is cleared by `git worktree prune`.

## Expected result
One file changed (tests/test_pipeline_check.py). `test_repo_pipeline_has_no_skipped_items` checks committed state through `_run_head`, so another item's uncommitted step files in the same tree (063/064, 065/066) no longer fail it. The in-tree `check_pipeline.py` run from run-item.md stays the check for uncommitted files. A fixture test pins that behaviour. The three constant `_is_code` asserts run once in `test_is_code_examples`, so mutation (i) fails 1 extra test instead of all 8 pattern cases. Collected in the file: 88 → 90. Full suite: 318 passed, 1 skipped (base 316/1 + 2, or the measured base + 2 if 065 lands tests first). REPO's status and worktree list are unchanged after the run.
