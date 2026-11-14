# 03 Research hand-off - 064
Status: READY (step 7 run by the orchestrator with a shell on 2026-11-14 after R3 finished: `check_handoff.py 064` PASS, counts match the Totals line; output pasted below.)

Recurring issues checked (item 013), against this file: RI-001 (the WORK_CODE filter's pass count is computed in Feasibility: 1 of 484 paths; the history impact is a measured gate in step 0, not asserted), RI-002 (Missing inputs: a failed branch `git diff` gives an empty list, named as a gap and not passed silently; nothing defaults), RI-004 (each fixture is checked against the rule it shows, see Self-check; this caught two fixture shapes that would have failed for an unrelated reason), RI-005 (every expected line is re-derived from the code), RI-006 (counts must come from check_handoff.py, which was not run, hence BLOCKED), RI-007 (this item; the new rule also makes a diagnostic committed without a step file an UNTRACKED CHANGE), RI-008 (no new syntax beyond 3.10; `test_every_py_compiles_on_oldest_python` covers it), RI-010 (log lines via `--log` only; the caller writes them), RI-011 (branch changes come from `changed()`, which already uses the merge-tree result, item 052), RI-012 (negative cases that contain `.py` but must not match). RI-003 and RI-009 do not apply (no calendar or branch-listing change).

Sources: repo at daily-fixes/2026-11-14, read with Read, Grep and Glob (no shell, so no `git` or `pytest`). The reflogs were read as text: `.git/logs/refs/heads/daily-fixes/2026-11-14` (branch created from d3827c7, then 5 commits for 063 R1/R2 and 064 R1/request/R2) and `.git/logs/refs/remotes/origin/main` (05a33fd -> 9fcc76a fast-forward -> d3827c7 push). git-scm diff-tree page fetched 2026-11-14. The docs.python.org str.startswith entry was fetched twice but cut off before that entry.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 F1: CODE_PATHS (L135) and RESEARCH_CODE_PATHS (L140) have no work/ | scripts/check_pipeline.py L135, L140 | VERIFIED | - |
| 01 F2: both checks use only a prefix test (L198, L481) | check_pipeline.py L198, L481 | VERIFIED | - |
| 01 F3: adding "work/" to a tuple flags all markdown, A1 daily commits and every RESEARCH ONLY 01 | L198, L481; a1-auditor.md L20 | VERIFIED | - |
| 01 F4: str.startswith takes a tuple (docs URL) | docs page cut off before the entry, twice | UNSUPPORTED by the cited URL | Fixed with a repo source: L198/L481 pass tuples, and `test_research_only_head_commit_with_code_is_skipped` (tests L891-901) flags `ccbot/x.py` through that call. Option A doesn't depend on any new startswith behaviour. |
| 01 F5: HEAD units come from `diff-tree -r --name-only --no-renames`, recursive, so work/061/diag_keep.py is already in `files` | L462; git-scm git-diff-tree ("Recurse into sub-trees"; "Show only the name of each changed file in the post-image tree"; "Turn off rename detection") | VERIFIED (quote shortened, meaning kept) | - |
| 01 F6: branch unit = changed(RESEARCH_CODE_PATHS) + every top-level tip file of touched items | L382-389, L417 | VERIFIED | - |
| 01 F7: branch keeps only 2-slash paths, so nested work/<ID>/sub/x.py is unseen there | L382 `n.count("/") == 2`, L388 `len(parts) == 3` | VERIFIED | - |
| 01 F8: docstring gaps (e) L81-82, (h) L93; work/*.py not named | L81-82, L93 | VERIFIED | - |
| 01 F9: test_untracked_from_is_fixed asserts the exact CODE_PATHS tuple | tests/test_pipeline_check.py L798-803 | VERIFIED | - |
| 01 F10: fixtures to keep and copy, and the helpers that take any path | tests L226-240, L608-611, L863-870, L891-901, L905-910 | VERIFIED | - |
| 01 F11: run-item.md L8 lists code as ccbot/, scripts/, tests/, config/; r3 L22 BLOCKED rule | run-item.md L8; r3-fact-checker.md L22 | VERIFIED | - |
| 01 F12: only non-markdown file under work/ besides .gitkeep is work/061/diag_keep.py | Glob `work/**/*.[!m]*` (2026-11-14): 2 hits, .gitkeep and diag_keep.py | VERIFIED | - |
| 01 F13: 061 is Scope FULL (person, 2026-11-14) with A1 result PASS | work/061/request.md L3-4; 07 L34 | VERIFIED | - |
| 01 F14: dead `or True else True` branch; effective rule is known AND a date in [d-120, d] | diag_keep.py L12-13 (a conditional expression binds loosest: `(A and B) if (not X or True) else True`, and `not X or True` is True); 06 L225-226; audit L83-84 | VERIFIED | - |
| 01 F15: request L12 was wrong; I3 did review the script | 06 L201, L209, L218-227; audit L39, L81-84 | VERIFIED | Already applied: request.md L12 now reads "I3 reviewed and re-ran it ... but no check or test exercises its logic" (A1, 2026-11-14). Nothing more to change. |
| 01 F16: test_every_py_compiles_on_oldest_python covers work/*.py | tests/test_safety.py L114-128 (`git ls-files "*.py"`; a git pathspec `*` also matches `/`); 06 L220 | VERIFIED | - |
| 01 F17: option A leaves 9fcc76a unflagged in RESEARCH CODE, because the unit holds 061's 04/05 and gap (g) applies | L198-205; RI-007 status (main: RESEARCH CODE none) | VERIFIED in result; premise fixed | Without git I can't see that 9fcc76a's diff holds 061/04 and 05. Stronger reason from the code: in `_research_code`, `code` is only tested for emptiness (L199) and quoted in the text (L213). 9fcc76a already changes ccbot/realtest.py (PR #26, RI-002/RI-007), so `code` is already non-empty, and adding diag_keep.py can't change that unit's result (today `none`). |
| 01 F18: main keeps UNTRACKED CHANGE none (UNVERIFIED in 01) | L477-486; reflogs | Fixed (narrowed) | The same argument applies at L481-485: the result depends on `items` and `_open_at`, not on which code files are listed, so 9fcc76a's result can't change. Only a first-parent commit whose only code is a work/*.py can newly flag. diag_keep.py is the only such file (F12). It came in through PR #26 (279a4e0 on the branch, 06 L245), and d3827c7, A1's push after 9fcc76a, is the only other main commit before this branch. Whether d3827c7 or this branch's 5 commits touch diag_keep.py is not checked (no git). Map step 0 gates it. |
| 01 F19: option B needs rule text in 3 files, a test, and either a move that edits 4 of 061's files or an allowlist; no "diagnos" rule exists today | run-item.md L8, L16; Grep `(?i)diagnos` in .claude/: 0 hits; 061 01 L28, L204; 05 L246, L251; 06 L201, L209; 07 L26 | VERIFIED | - |
| 01 Numbers: option A newly counts 1 file and 0 markdown | Glob (F12); regex needs `\.py$` | VERIFIED | Measured: 1 of 484 paths (Feasibility). |
| 01 Numbers: option A touches 2 files | 02 AGAINST 2(iii) | WRONG | 4 files: scripts/check_pipeline.py and tests/test_pipeline_check.py (logic), plus 1 line each in .claude/agents/a1-auditor.md L20 and .claude/commands/run-item.md L8, which otherwise go stale. |
| 01 Numbers: "2 files < 4 files" | 01 option B estimate; 02 AGAINST 2(iii) | WRONG | 4 (A) vs at least 5 (B): run-item.md, i2-builder.md, i3-verifier.md, a test file with an allowlist, and a1-auditor.md L20, which B needs too. A is still the smaller change, and it is enforced by code. |
| 01 Fit: option A makes the file visible but doesn't test its logic | L204-205 gap (g); 053 open-item rule | VERIFIED | - |
| 01 Open Q6: sources count 2 unique URLs | check_handoff.py URL_RE applied by hand to 01 L12, L13 | VERIFIED (hand emulation) | The log count must come from the script output (RI-006). |
| 02: RI-007 status already names this gap (064, EFFICIENCY); not a new occurrence | recurring-issues.md L85; request L19 | VERIFIED | - |
| 02: 061/06 L222-227 quote | 06 L222-227 | VERIFIED | - |
| 02: 061/06 L245-247 merge probe (--no-ff into 29a2b28, UNTRACKED none, RESEARCH CODE none) | 06 L245-247; 07 L34 | VERIFIED | - |
| 02: a unit flagged on HEAD stays flagged; the named never-add lists | 062/02 L21 ("for good"); 053/02 L4; check_pipeline.py L119, L131 | VERIFIED | - |
| 02: RI-012 needs a negative test containing the pattern | recurring-issues.md L138-141 | VERIFIED | - |
| 02: RI-010 favours a check over agent text | recurring-issues.md L120 | VERIFIED | - |
| 02 FOR 1: `^work/\d{3}/.+\.py$` skips .gitkeep and non-item folders, matches nested paths on HEAD, and leaves CODE_PATHS and test L803 unchanged | STEP_FILE L143; L462; tests L803 | VERIFIED | Self-check rows 1-8 run each path. |
| 02 FOR 2: expected outputs of fixtures (a)-(e) | L193-216, L467-490; tests L19-41 (`_item`), L53-58, L629-645, L857-901 | Fixed | (c) the full line is `UNTRACKED CHANGE: <sha7> work/150/x.py` + WHY_053 + ` (cutoff <cutoff7> from --untracked-from)`, as in tests L644-645. (a) must also assert `UNTRACKED CHANGE: none` (160 is open), as in L901. (e) "open FULL item with diag.py + its 05" as request + 05 alone is `170: SKIPPED (FULL: missing 01 02 03 04 before 05)` (tests L53-58), exit 1. It needs 01-05 (`_item(repo, "170", ALL[:5])`, logged) + diag.py in one commit. |
| 02 FOR 2(c): flagging a .py added to completed item 150 is the intended rule | run-item.md L16; tests L634-645 | VERIFIED | - |
| 02 FOR 3: `changed("work/")` filtered by WORK_CODE sees nested files and counts only changed files, while the step-file part of `unit` "stays as it is" | L375-379, L385-389, L417 | Fixed | As written it contradicts itself: today's `files[i]` part is every top-level tip file, .py included, so an unchanged tip .py would still count. The step-file part must be filtered: `for f in files[i] if f in STEPS.values()`. `_research_code` reads only step files from `files` (L201, L203), so nothing is lost. |
| 02 AGAINST 1: option B "edits 6 commands across 4 of 061's files" | Grep `diag_keep` in work/061: 01 L28, L204; 05 L246, L251; 06 L201, L209; 07 L26 | WRONG | 7 lines across 4 files (2 + 2 + 2 + 1). 01 F19's "4 of 061's files" is right. |
| 02 AGAINST 1: new docstring gap (k) | docstring L77-97 has gaps (a)-(j) | VERIFIED | - |
| 02 AGAINST 2(i): "Today that is only 279a4e0's file, inside merge 9fcc76a" | reflogs; L481-485 | Fixed (narrowed) | Same as 01 F18: 9fcc76a's result can't change. d3827c7 and the branch's own 5 commits are not checked without git, so step 0 gates them. |
| 02 AGAINST 2(ii): a diagnostic committed without a step file trips UNTRACKED CHANGE, even in its own open item's folder | L484-486 (no STEP_FILE match -> no items -> flagged) | VERIFIED | - |
| 02 AGAINST 2(iii): a1-auditor L20 and run-item L8 go stale; both under .claude/ (RULE_PATHS) | a1-auditor.md L20; run-item.md L8; L133 | VERIFIED | - |
| 02 AGAINST 3: name "(e) other script types" next to gap (e) | docstring L81-82 (gap (e) already exists) | Fixed | The label (e) is taken. Extend gap (e)'s own text ("...; other script types under work/ (.sh, .ipynb, files with no extension) are not checked") instead of adding a second (e). |
| 02: no external claims, so languages N/A | 02 L20-32 | VERIFIED | - |

**Totals:** 41 rows checked → **31 VERIFIED as-is**, **10 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None. Each WRONG or UNSUPPORTED row was corrected in place (see Fix).

## Implementation map
Option A (R1, R2, confirmed here). Files: scripts/check_pipeline.py, tests/test_pipeline_check.py, .claude/agents/a1-auditor.md, .claude/commands/run-item.md. Nothing under work/061 changes (run-item.md L16).

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 0 | Gate (I2, before committing the rule): apply steps 1-2 in the working tree and run the repo check on this branch. Run it once before the change too, as a baseline. | `python3 scripts/check_pipeline.py` after `git fetch origin` | the `061:`, `UNTRACKED CHANGE:` and `RESEARCH CODE:` lines, before and after | After the change: `061: complete`, `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`, the same as the baseline. Any new entry: stop and go back to I1, with no exception list unless the person agrees. Also count the first-parent units after UNTRACKED_FROM whose only code is a work/*.py: `git rev-list --first-parent 694bf4d..HEAD`, each through `git diff-tree -r --name-only --no-renames <c>^1 <c>`, keeping units with a WORK_CODE match and no CODE_PATHS match. Expected: 0 such units (d3827c7 and the 063/064 commits are the only unknowns). | Not computed here (no git); I2 computes it as the step's output. Lines expected to change: 0 (01 F17/F18). |
| 1 | check_pipeline.py: add `WORK_CODE = re.compile(r"^work/\d{3}/.+\.py$")` next to RESEARCH_CODE_PATHS, with a comment (item 064). At L198 use `f.startswith(RESEARCH_CODE_PATHS) or WORK_CODE.match(f)`, and the same with CODE_PATHS at L481. CODE_PATHS and RESEARCH_CODE_PATHS stay as they are. | changed paths of each unit | the code list now includes work/<ID>/**/*.py | Unit asserts added to `test_research_code_rules`: `rc(["work/160/diag.py", "work/160/01-research.md"], texts.get)` gives 1 flag starting `RESEARCH ONLY: changes work/160/diag.py with no 04-06;`; `rc(["work/160/diag.py.md", "work/160/notes.md", "work/160/01-research.md"], ...) == []`; `rc(["work/tmp/x.py", "work/.gitkeep", "work/160/01-research.md"], ...) == []`. A new `test_work_code_pattern` runs each path in Self-check rows 1-8. `test_untracked_from_is_fixed` is unedited and passes. | WORK_CODE matches 1 of 484 paths under work/ (working tree 2026-11-14: Grep finds 483 non-empty files, plus the empty .gitkeep; Glob `work/**/*.[!m]*` finds 2 non-.md files). Re-run: `git ls-files work \| python3 -c "import re,sys;print(sum(bool(re.match(r'^work/\d{3}/.+\.py$',l)) for l in sys.stdin))"` -> 1 |
| 2 | Branch unit L417: `changed(*RESEARCH_CODE_PATHS) + [f for f in changed("work/") if WORK_CODE.match(f)] + [f"work/{i}/{f}" for i in sorted(touched) for f in files[i] if f in STEPS.values()]`. The `files[i]` used by classify (L410) is unchanged. | merge-tree diff (`changed`), the tip's ls-tree | the branch unit holds the changed work .py files (nested included) and the tip's step files | Branch fixtures (d)-(f) in step 3 | Nested branch fixture: 1 flagged of 1; a tip .py the branch doesn't change: 0 flagged of 1 |
| 3 | tests/test_pipeline_check.py, fixtures (all `@NO_GIT`). (a) `_history`, then `_item(repo, "160", ["01-research.md"], scope="RESEARCH ONLY", date="2026-11-11")` + `_write(repo, "work/160/diag.py")` in one commit: exit 1, `160: SKIPPED (<c7> RESEARCH ONLY: changes work/160/diag.py` on exactly one `160:` line, `RESEARCH CODE: 160`, `UNTRACKED CHANGE: none`. (b) `_history`, then `work/150/x.py` alone: exit 1, line == `UNTRACKED CHANGE: <c7> work/150/x.py{WHY_053} (cutoff <cutoff7> from --untracked-from)`. (c) `_history`, then `_item(repo, "170", ALL[:5], date="2026-11-11")` (01-05, logged, FULL) + `work/170/diag.py` in one commit: `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`, no `170: SKIPPED`. (d) `_repo_with_open_branch`, `_branch_adds(repo, "res", "160", RES_STEPS, RES_160, extra=["work/160/diag.py"])`: exit 0, `BRANCH SKIPPED: 160 (origin/res: RESEARCH ONLY: changes work/160/diag.py`. (e) the same with `extra=["work/160/sub/x.py"]`: `BRANCH SKIPPED: 160 (origin/res: RESEARCH ONLY: changes work/160/sub/x.py`. (f) `_repo_with_open_branch`. On local main, `_item(repo, "160", ["01-research.md"], scope="RESEARCH ONLY", waived="04 05 06 (person, 2026-11-13: test)")` + `work/160/diag.py` in one commit. Then `_branch_adds(repo, "res", "160", ["02-improvements.md"], RES_160)`, which rewrites request.md without the waiver and adds 02 but leaves diag.py unchanged. Expect no `changes work/160/diag.py` in any `BRANCH SKIPPED:` line. The existing `test_research_only_work_files_only_not_flagged` stays as the markdown-only case. | fixtures | 6 new tests + the step-1 unit asserts | `python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py`: all pass. | (a) 1 of 1 flagged; (b) 1 of 1; (c) 0 of 1; (d) 1 of 1; (e) 1 of 1; (f) 0 of 1 |
| 4 | Docstring: in the 053 paragraph (L68-73) and the 062 paragraph (L83-84), say `work/<ID>/**/*.py` counts as code (item 064). Extend gap (e) (L81-82): "other script types under work/ (.sh, .ipynb, files with no extension) are not checked". Add (k): "a work/<ID>/*.py in a FULL/FAST item is covered by that item's steps; its logic is checked only by I3's re-run (064)". Add (l): "on a branch, a failed `git diff` gives an empty change list, so its code is not seen until it reaches HEAD". Extend the (i) note: "nested work .py files are seen on branches through changed('work/')". | - | docstring text | I3 reads the docstring against steps 1-2. | - |
| 5 | Rule text, one line each: a1-auditor.md L20, add `work/<ID>/*.py` to the listed paths; run-item.md L8, add `work/<ID>/*.py` to "(ccbot/, scripts/, tests/, config/)". | - | 2 lines | Grep `work/<ID>/\*.py` in each file: 1 hit each. The branch shows a `RULES BRANCH:` line (expected; check_pipeline.py is in RULE_PATHS anyway). | - |
| 6 | I3 mutations, in a scratch copy: (i) drop `or WORK_CODE.match(f)` at L198 and L481; (ii) restore L417's unfiltered `files[i]` part. | scratch copy | failing test names | (i): fixtures (a), (b), (d), (e) and the step-1 positive unit assert fail. (ii): (f) fails. | - |
| 7 | Whole-repo check after commit: the full suite, then the repo check. | repo | suite count, check lines | `python3 -m pytest -q -p no:cacheprovider`: green (293 + new tests passed, 1 skipped for exchange_calendars). `check_pipeline.py`: `061: complete`, `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`, exit 0. I2 commits the code with its 05 (gap (b)). | - |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| HEAD unit's changed files (`diff-tree`, L462) | diff-tree fails, so `files` is None | Existing: `<sha7> (git diff-tree failed)` in UNTRACKED CHANGE, exit 1. Never an empty list. |
| git itself | no git or no HEAD | Existing: `UNTRACKED CHANGE: not checked (no git)`, `RESEARCH CODE: not checked (no git)` |
| Cutoff UNTRACKED_FROM | missing from a shallow or full clone | Existing: `not checked (... shallow clone ...)` or an error with exit 1. RESEARCH CODE: `not checked (see UNTRACKED CHANGE)` |
| Item's request.md (HEAD working tree / branch tip) | file absent | Existing: `RESEARCH ONLY check: no request.md at the tip, item 062`. Flagged, never passed. |
| Branch change list (`changed()`, L375-379) | git diff fails, so `[]` is returned | No report text today: the branch's code, work .py files included, goes unseen. Branch lines are information only (exit unchanged), and HEAD's 053/062 judge the code once it is merged. Named as docstring gap (l) in step 4, so it is visible rather than silent. |
| Non-ASCII path (quoted by git, starts with `"`) | WORK_CODE doesn't match | Existing gap (f) (no -z); it covers work/ paths too. |

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| 1. WORK_CODE on work/061/diag_keep.py | `re.match(r"^work/\d{3}/.+\.py$", p)` | "061" fits \d{3}, ".+" = "diag_keep", ends ".py" | match (as the map says) |
| 2. WORK_CODE on work/160/sub/x.py | same | \d{3} = 160, ".+" = "sub/x" (`.` matches `/`), ends ".py" | match: nested is seen (HEAD; branch via step 2) |
| 3. WORK_CODE on work/160/diag.py.md | same | ends ".md"; `$` needs ".py" at the end | no match (negative fixture is correct) |
| 4. WORK_CODE on work/.gitkeep | same | ".gitkeep" is not \d{3}/ | no match |
| 5. WORK_CODE on work/tmp/x.py | same | "tmp" is not \d{3} | no match |
| 6. WORK_CODE on work/160/01-research.md | same | ends ".md" | no match: no markdown flagged |
| 7. WORK_CODE on work/1600/x.py | same | \d{3} = "160", next char "0" is not "/" | no match (IDs are 3 digits, as in STEP_FILE) |
| 8. WORK_CODE on work/160/x.pyc | same | after ".py" comes "c", so `$` fails | no match (compiled files are not code) |
| 9. Fixture (a) on RESEARCH CODE | L198-216: code non-empty; items {160}; 160 RESEARCH ONLY, no 04/05, no waiver | code = [work/160/diag.py], so 1 flag | `RESEARCH CODE: 160`, exit 1 |
| 10. Fixture (a) on UNTRACKED CHANGE | L481-486: items {160}; `_open_at(parent, 160)`: 07 absent, so True | `any([True])` = True, not flagged | `UNTRACKED CHANGE: none` |
| 11. Fixture (b) | items = {} (x.py is not a STEP_FILE); `any([])` = False | flagged; text = sha7 + " work/150/x.py" + WHY_053 + cutoff note (L486-490, L472) | exit 1, line as in step 3(b) |
| 12. Fixture (c) | classify: 01-05 present, no gap, so in progress (with request + 05 alone it would be SKIPPED, tests L53-58). 053: items {170}, open, so not flagged. 062: built = {170} (05 in files), FULL, so gap (g) gives [] | - | `none` / `none`, no SKIPPED |
| 13. Fixture (f) | step 2: the branch's `changed("work/")` = [work/160/02-improvements.md, work/160/request.md]; WORK_CODE gives []; the step-file part = 01, 02 | code = changed(RESEARCH_CODE_PATHS) + [] = [], so `_research_code` returns [] at L199-200 | no `changes work/160/diag.py`. With the old L417, `files[i]` holds diag.py, code = [work/160/diag.py], and 160 (RESEARCH ONLY, no waiver at the tip) is flagged, so the test fails, as mutation (ii) expects |
| 14. Feasibility count | 483 non-empty files (Grep offset 440 + 43 more) + 1 empty .gitkeep | 440 + 43 = 483; 483 + 1 = 484; non-.md files = 2 (.gitkeep, diag_keep.py); WORK_CODE passes diag_keep.py only | 1 of 484 |
| 15. 01 F17/F18: 9fcc76a unchanged | `_research_code`: `code` used at L199 (empty?) and L213 (text); 053: L482 (empty?) and L486 (text) | 9fcc76a's code was already non-empty (ccbot/realtest.py), so adding 1 entry changes only text inside a line that is not printed (current result none) | result unchanged |
| 16. 02 AGAINST 1 count | Grep `diag_keep` command lines in 061's 01/05/06/07 | 2 + 2 + 2 + 1 = 7 | 7 lines across 4 files (fixed from 6) |
| 17. Option sizes | A: 2 logic + 2 rule-text files; B: run-item, i2, i3, a test file, a1-auditor | 2 + 2 = 4; 3 + 1 + 1 = 5 | 4 < 5: A is smaller (fixed from "2 < 4") |
| 18. diag_keep L12-13 precedence | `lambda: A and B if C else True`, with C = `not X or True` | C = True for any X, so the lambda is always A and B | dead branch confirmed |

`python3 scripts/check_handoff.py 064` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 41
totals line: 41 rows -> 31 as-is, 10 fixed, 0 removed
PASS
```
