# 03 Research hand-off - 066
Status: READY

Recurring issues checked (item 013), against this file: RI-001 (ESCALATED; the "holds however items are launched" claim is computed, not asserted: probe with an uncommitted work/999 fails the old test (1 failed) and passes the new one (1 passed), Feasibility col.), RI-002 (ESCALATED; no missing input becomes a pass: no git skips with a reason, git present but no HEAD or not a repo fails loudly with git's stderr, never a silent fallback to `REPO`, see Missing inputs). Also checked: RI-006 (counts below come from `check_handoff.py` and pytest output, not by hand), RI-008 (the new code uses only 3.10 syntax; `test_every_py_compiles_on_oldest_python` covers it), RI-009 (the test only runs `git worktree add/remove` with `cwd=REPO`, never stash/checkout/reset in `REPO`; all R3 probes ran in scratch worktrees, removed afterwards, `git worktree list` shows only the main tree), RI-010 (option B chosen, so no new duty that lives only in rule text). RI-003, RI-004, RI-005, RI-007, RI-011 and RI-012 don't apply: there's no calendar, price example, branch diff or error parsing here.

Sources: repo on daily-fixes/2026-11-15, read at 4404063, then 1402b36 (065's R2 commit landed during this step). R3 had a shell: pytest, git and `check_pipeline.py` were run. The git-worktree, pytest tmp_path and pytest parametrize pages were fetched on 2026-11-15. All probes ran in detached worktrees under the session scratchpad and were removed with `git worktree remove --force`. The repo tree was never edited (only `?? work/065/02-improvements.md` from 065 was seen, and 065 committed it at 1402b36).

**Pass count vs the request:** request.md L15 says "same pass count minus the merged cases". R1 (F14) and R2 (FOR 3) found that moving the three constant asserts out of the parametrized test removes no parametrized case and adds 1 test. A1 (the item's opener) accepts +1: the goal is that one break fails once, not 8 times. Target: **317 passed, 1 skipped**, measured on 1402b36's base of 316 passed, 1 skipped. If 065 lands tests first, the target is that base + 1.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 F1: the test runs the real script on REPO; `_run` = subprocess with cwd=root | tests/test_pipeline_check.py L139-144, L43-46 | VERIFIED | - |
| 01 F2: `main` iterdir (L590), `classify` exists (L250), `incomplete` reads every log on disk (L283-286); uncommitted counts the same | scripts/check_pipeline.py L250, L275-288, L590 | VERIFIED | - |
| 01 F3: 063 failure = `INCOMPLETE: 064 (no log line for I1)`; INCOMPLETE → exit 1 (L654) | work/063/05-build-report.md L95-101; check_pipeline.py L654 | VERIFIED | - |
| 01 F4: step file then `--log` line, so a shared-tree run between them sees INCOMPLETE | run-item.md L14; R3 probe: uncommitted work/999 request+01 with no R1 line → `INCOMPLETE: 999 (no log line for R1)`, `1 failed` | VERIFIED | - |
| 01 F5: run-item.md has no per-tree rule; L5 "one agent at a time" is per item | .claude/commands/run-item.md L1-16 (whole file) | VERIFIED | - |
| 01 F6: two items (065, 066) run in this tree now | caller's task; `git status` showed `?? work/065/02-improvements.md`; log 1402b36 "Item 065: R2" | VERIFIED | - |
| 01 F7: run-item.md edits need the person's OK; `.claude/` is under RULES BRANCH | work/064/06-verification.md L20; check_pipeline.py L59-61 | VERIFIED | - |
| 01 F8: option B works in a detached worktree of HEAD; git checks still run there | git-scm git-worktree; R3 run: `check_pipeline.py` in a HEAD worktree → exit 0, `RESEARCH CODE: none`, `UNTRACKED CHANGE: none`, `061: complete` | VERIFIED | - |
| 01 F9: `add -d` quote; linked worktree shares all but HEAD, index | https://git-scm.com/docs/git-worktree (fetched; both quotes exact) | VERIFIED | - |
| 01 F10: tmp_path is "a temporary directory unique to each test function" | https://docs.pytest.org/en/stable/how-to/tmp_path.html (exact) | VERIFIED | - |
| 01 F11: worktree cost UNVERIFIED; >100 files under data/; `git archive` copy breaks L143 | `git ls-files data \| wc -l` = 141; check_pipeline.py L650; R3 timing | Fixed (measured) | Measured on 1402b36: `worktree add --detach` 0.133 s, 35M on disk, remove 0.019 s; the whole test 0.54 s (`--durations`). The `git archive` point is VERIFIED (L650 prints "not checked (no git)" outside git, so L143 fails). |
| 01 F12: B needs a skip or fallback when there's no git/HEAD; form UNVERIFIED | R2 AGAINST 2; R3 measured run | Fixed (decided) | Skip only when git is not on PATH (`NO_GIT`). Git present but the worktree add fails → assert on its return code with stderr. No fallback to `REPO`. |
| 01 F13: 8 cases; 2 path asserts (L999-1000) + 3 constant asserts (L1001-1003); one run per argument set | tests L987-1003; https://docs.pytest.org/en/stable/how-to/parametrize.html ("will run three times using them in turn"; each case reported separately) | VERIFIED | - |
| 01 F14: a new test gives +1; folding into `test_research_code_rules` gives +0 | tests L841; R3 measured: 88 → 89 collected | VERIFIED | - |
| 01 F15: today's suite count UNVERIFIED | R3 `pytest -q` on 1402b36 | Fixed (measured) | 316 passed, 1 skipped in 47.11s (065 files committed at that point). |
| 01 Numbers: option A = 1 rule file, ~1 sentence, not enforced | run-item.md; F6, F7 | VERIFIED | - |
| 01 Numbers: option B = 6-10 changed lines (estimate) | none (estimate, UNVERIFIED in 01) | UNSUPPORTED | Removed. The map sets no line count; I1 plans the diff. |
| 01 Numbers: constant asserts 3 × 8 = 24 runs → 3; collected 8 → 9 | 3 × 8 = 24; tests L987-1003 | VERIFIED | - |
| 01 Numbers: 063 count 297 + 1 = 298 = 293 + 5 | work/063/05 L101-102 | VERIFIED | - |
| request L15 "same pass count minus the merged cases" | R1 F14, R2 FOR 3, measured 88 → 89 | Fixed | No case is merged away; the count is +1 (target 317 passed, 1 skipped). A1, who opened the item, accepts +1 (see the note above the table). |
| 02 Past logs: 063/05 L98-101 and audit L25 "not an error; efficiency → 066" | work/063/05 L98-101; logs/audit/2026-11-15.md L25 | VERIFIED | - |
| 02 Past logs: RI-010 root cause quote | logs/recurring-issues.md L118-120 | VERIFIED | - |
| 02 Past logs: RI-009 occ 2 (L115); i2 L19 scratch rule; I3 064/06 L47 and A1 063 L33 use `worktree add --detach` + `remove --force` | recurring-issues L115; i2-builder.md L19; 064/06 L47; logs/audit/2026-11-15-063.md L33 | Fixed | 064/06 L47 uses `git worktree add --detach` and `remove --force`. A1's L33 says "scratch git worktree ... removed afterwards with `git worktree remove` and `prune`" and doesn't name `--detach`/`--force`. The pattern is still in use. |
| 02 Past logs: 064/06 L48 mutation (i) failed all 8 cases | work/064/06 L48 | VERIFIED | - |
| 02 Past logs: no earlier attempt at either half | R3 grep "same tree\|one at a time per\|worktree per item" in logs/, .claude/, work/060-064: 2 hits (audit L25 = this item's origin; 062/05 L84 = unrelated) | VERIFIED | - |
| 02 FOR 1: script reads only work/ and logs/ relative to cwd; `_git` needs toplevel == cwd, which holds in a linked worktree; keep `REPO / "scripts"` | check_pipeline.py L359-366, L590; tests L44; R3 HEAD-worktree run exit 0 | VERIFIED | - |
| 02 FOR 2: concurrent runs don't collide (tmp_path + admin-name suffix quote) | https://git-scm.com/docs/git-worktree ("possibly appended with a number to make it unique ... test-next1"); tmp_path page | VERIFIED | - |
| 02 FOR 3: own test, not folded into `test_research_code_rules` (that one pins `_research_code`; L1003 pins `_is_code` with CODE_PATHS) | tests L841-870, L1001-1003 | VERIFIED | - |
| 02 AGAINST 1: the test no longer sees the running item's own uncommitted files; caught by the run-item L14 / I3 run | run-item.md L14; 064/06 L45 | VERIFIED | - |
| 02 AGAINST 2: `remove` refuses unclean without `--force`; killed run leaves an entry until prune/`gc.worktreePruneExpire`; `NO_GIT` L604; without git the test already fails | git-worktree page (exact quotes); tests L604; check_pipeline.py L650 | VERIFIED | Added from R3's run: `NO_GIT` is defined at L604, after this test (L139), so `@NO_GIT` there raises NameError at collection ("no tests collected, 1 error"). The map moves the `NO_GIT` line up next to `_run`. |
| 02 AGAINST 3: full checkout cost UNVERIFIED | R3 timing | Fixed (measured) | 0.133 s add, 35M, test 0.54 s. Not slow, so the `--no-checkout` variant isn't needed and isn't in the map. |
| 02 AGAINST 3: `--no-checkout` "to suppress checkout in order to make customizations" | git-worktree page (quote continues "such as configuring sparse-checkout") | VERIFIED | Not used (cost measured as low). |
| 02 AGAINST 3: `git sparse-checkout` in a linked worktree may turn on `extensions.worktreeConfig` in the shared config (R2: UNVERIFIED) | not on the git-worktree page (it only shows `git config extensions.worktreeConfig true` as a manual step); no other source cited | UNSUPPORTED | Removed as a reason. The map still uses no sparse-checkout, because the full checkout is already cheap. |
| 02 Holes: base count last cited 316 passed, 1 skipped (A1 on 063) | work/063/07-audit-task.md L25 | VERIFIED | Re-measured today: same, 316 passed, 1 skipped (1402b36). |
**Totals:** 34 rows checked → **26 VERIFIED as-is**, **6 fixed**, **2 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
- 01 Numbers "option B is about 6-10 changed lines": an estimate with no source. R3's scratch version of steps 1-3 is `1 file changed, 20 insertions(+), 4 deletions(-)` (reference only; I1 plans the real diff).
- 02 AGAINST 3 "`git sparse-checkout` in a linked worktree may turn on `extensions.worktreeConfig` in the shared repo config": not supported by the cited page. It is no longer needed as a reason (the full checkout costs 0.13 s).

## Implementation map
Option B. Only tests/test_pipeline_check.py changes. No change to `.claude/commands/run-item.md` or any rule file, scripts/, ccbot/ or config/. Never connect to a brokerage (nothing here does).

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | tests/test_pipeline_check.py: move the line `NO_GIT = pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")` from L604 up to just before `def _run` (L43). Nothing else moves. | the file | `NO_GIT` defined before L139 | `pytest --collect-only tests/test_pipeline_check.py` collects with no error (with `@NO_GIT` on L139 and the line still at L604: "no tests collected, 1 error", R3 measured). All existing `@NO_GIT` tests still collect. | – |
| 2 | `test_repo_pipeline_has_no_skipped_items` → `@NO_GIT`, takes `tmp_path`. `wt = tmp_path / "head"`. Run `git worktree add --detach -q <wt> HEAD` with `cwd=REPO`, and `assert add.returncode == 0, add.stderr`. In `try:` call `_run(wt, "check_pipeline.py")`, keeping `REPO / "scripts"` inside `_run` (unchanged). In `finally:` run `git worktree remove --force <wt>` with `cwd=REPO`. Keep the three asserts as they are (`code == 0, out`; `RESEARCH CODE: none`; `061: complete`). Docstring: "The committed work/ folder ... Runs on a detached worktree of HEAD, so another item's uncommitted step files in this tree don't fail it (item 066); run check_pipeline.py in the tree for uncommitted files." Inside REPO: no stash, checkout, reset or file writes. | REPO's HEAD; tmp_path | the same three asserts, on committed state | (a) The test passes on the branch. (b) Probe in a scratch worktree (where REPO = that tree): add an uncommitted `work/999/request.md` (Scope FULL) + `01-research.md` with no R1 line. Old body → `1 failed` with `INCOMPLETE: 999 (no log line for R1)`. New body → `1 passed`. (c) Afterwards `git worktree list` shows no entry under tmp_path. (d) `git -C REPO status --porcelain -uall` is the same before and after the run. (e) `--durations` time under 2 s. | Probe measured by R3 on 1402b36: old 1 failed, new 1 passed (1 of 1 cross-item case caught). Test time 0.54 s; add 0.133 s, 35M, remove 0.019 s. |
| 3 | Cut L1001-1003 (the three constant `_is_code` asserts) out of `test_work_code_pattern`, unchanged, into a new `test_is_code_examples()` right after it (`cp = _cp()`, docstring naming item 066). `test_work_code_pattern` keeps its 8 cases and 2 asserts. | tests L987-1003 | 8 parametrized cases + 1 new test | (a) `--collect-only tests/test_pipeline_check.py`: 88 → 89. (b) Mutation (i) from 064/06 (`_is_code` → `return f.startswith(paths)`) in a scratch worktree: `8 failed, 81 passed`. Only 2 `test_work_code_pattern` cases fail (the two `True` paths), plus `test_is_code_examples` once. It was 13 failed, 75 passed, with all 8 cases failing. | Measured by R3: 89 collected; mutation (i) 8 failed, 81 passed. |
| 4 | Full suite and pipeline check | the branch | counts in 05 | `python3 -m pytest -q -p no:cacheprovider`: 317 passed, 1 skipped (base 316 + 1, measured base on 1402b36). If 065 has committed tests by then, the target is the measured base + 1, and 05 states that base and which uncommitted 065 files were present. `python3 scripts/check_pipeline.py` in the tree as run-item L14 requires (this is now the only check that sees uncommitted step files). | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| `git` on PATH (step 2) | test skipped, not passed | `SKIPPED ... git not on PATH` (`NO_GIT`). Without git the old test already failed (L650 → L143), so no green result is lost. |
| A commit at HEAD / a git repo at REPO (step 2) | `worktree add` returns non-zero | Test fails with git's stderr (`assert add.returncode == 0, add.stderr`). No fallback to `_run(REPO, ...)`, which would quietly bring back the cross-item failure. |
| Worktree removal (step 2 `finally`) | `remove --force` fails (e.g. killed run) | Not checked inside the test, so it never masks the real assert. The stale entry shows in `git worktree list` and goes with `git worktree prune` or `gc.worktreePruneExpire` (git-worktree page). Check (c) in step 2 catches it in I3. |
| Uncommitted step files of the running item (step 2) | not seen by this test (by design) | Covered by the explicit `python3 scripts/check_pipeline.py` run (run-item L14, I3 06). The docstring says so. |

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Step 3 collected count | 88 existing − 0 cases removed + 1 new test | 88 − 0 + 1 = 89; measured 89 | OK |
| Step 4 suite target | base passed + 1 | 316 + 1 = 317 passed, 1 skipped unchanged | OK (base measured 316/1 on 1402b36) |
| Constant-assert runs | 3 asserts × cases | before 3 × 8 = 24; after 3 × 1 = 3 | OK |
| Step 3 mutation (i) failures | old failures − 8 pattern cases + pattern cases with `hit=True` (the L1000 assert fails only there) + 1 new test | 13 − 8 + 2 + 1 = 8 failed; total 89 − 8 = 81 passed; measured 8 failed, 81 passed | OK |
| Step 3 mutation (i) other failures stay | 13 − 8 = 5 non-pattern failures (research_code_rules + (a)(b)(d)(e)) | measured list: test_research_code_rules, research_only_work_py, py_added_to_completed_item, branch_work_py, branch_nested_py = 5 | OK |
| Step 2 probe triggers the rule | uncommitted 01 with no `\| R1 \| 999 \|` line → `incomplete` lists R1 (L285-287) → exit 1 (L654) | old: `INCOMPLETE: 999 (no log line for R1)`, 1 failed; new: HEAD has no work/999 → 1 passed | OK |
| Step 2 time | measured duration < 2 s | 0.54 s < 2 s | OK |
| Request "minus the merged cases" | parametrized cases removed | 8 → 8, so 0 merged; +1 test, accepted by A1 | Noted, not a mismatch |

`python3 scripts/check_handoff.py 066` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 3
fact-check rows: 34
totals line: 34 rows -> 26 as-is, 6 fixed, 2 removed
PASS
```
