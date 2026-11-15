# 04 Build plan - 064
Fit verdict: FIT WITH CHANGES

Recurring issues checked (item 013), against this plan: RI-001 (the one filter, WORK_CODE, has a dated non-zero count in 03 (1 of 484 paths, 2026-11-14; I1 re-ran Glob `work/**/*.py` on 2026-11-14: 1 hit, `work/061/diag_keep.py`) and a repo test that pins it, see Guardrail tests), RI-002 (ESCALATED: each absent input has a planned absent-case test, including a failed `diff-tree` and a failed branch `diff`; nothing defaults to "none" without saying so), RI-007 (this item; the gate in step 0 and the real-repo test keep main from going red for good), RI-010 (log lines only via `--log`, written by the caller; the new run-item text puts the "commit a diagnostic with its step file" duty where `check_pipeline.py` enforces it, not only in agent text), RI-012 (negative paths that contain `.py` but must not match; the predicate uses the path, never commit text). Also checked: RI-004/RI-005 (each fixture is re-derived against `classify` as well as 053/062; this caught that fixture (f) as written in 03 would also print a `BRANCH SKIPPED: 160` from `classify`, see change C2), RI-008 (no syntax beyond 3.10; `re.fullmatch` exists since 3.4), RI-011 (branch changes come from `changed()`, which uses the merge-tree result). RI-003, RI-006 and RI-009 don't apply (no calendar, hand count or branch-listing change; the 03 counts came from check_handoff.py PASS).

## Fit check
- ~$3k account: no trading, pricing, screen or sizing change. This is pipeline tooling. It matters because work/ diagnostics produce numbers the person reads (061's 247-call figure, which 063 also uses).
- Current rules: it fits 053 (UNTRACKED CHANGE), 062 (RESEARCH CODE) and run-item L16 ("a follow-up to a completed item is a new item"). It widens what counts as code but changes no step, scope or waiver rule.
- Existing code: two call sites (`_research_code` L198, `untracked_changes` L481) and the branch unit (L417). `CODE_PATHS`, `RESEARCH_CODE_PATHS` and `test_untracked_from_is_fixed` (L803) stay unchanged.
- Conflicts: none with built code. The only risk is history: a first-parent unit after UNTRACKED_FROM whose only code is a work/*.py with no open-item step file would turn main red for good. Step 0 gates this before the rule is committed. `test_repo_pipeline_has_no_skipped_items` (tests L139-143) turns red in the suite if it happens.
- Item 063 (same branch, built at the same time): **no file overlap.** 063 plans ccbot/realtest.py, tests/test_realtest.py, .claude/agents/r3-fact-checker.md and .claude/agents/i3-verifier.md (063/03 map step 7, L83). 064 changes scripts/check_pipeline.py, tests/test_pipeline_check.py, .claude/agents/a1-auditor.md and .claude/commands/run-item.md. Three interactions to watch (no shared lines):
  1. Once 064's rule is committed, any `.py` that 063's I2/I3 put under work/063/ must be committed together with a 063 step file (063 is FULL and open, so it is then covered). A bare commit of it becomes an `UNTRACKED CHANGE` entry. Glob on 2026-11-14 finds none under work/063.
  2. Keep 063's and 064's code in separate commits, each with its own 05 (gap (a)). Both items are open, so mixing them would pass the check while hiding which item covers which code.
  3. The real-repo test (L139) and `check_pipeline.py` in step 7 judge both items. A 063 SKIPPED/INCOMPLETE state mid-build is 063's, not a 064 failure. I2 says which item a red line belongs to.

Changes to 03 (why "WITH CHANGES"):
- C1. Use one helper and `fullmatch`: `WORK_CODE = re.compile(r"work/\d{3}/.+\.py")` and `def _is_code(f, paths): return f.startswith(paths) or WORK_CODE.fullmatch(f) is not None`, called at L198 and L481. This gives one mutation point instead of two. `fullmatch` needs the whole string to match, while `$` also matches "just before the newline at the end of the string" (Python re docs). That can't happen with today's split paths, but it removes the edge. Self-check rows 1-8 of 03 give the same results under `fullmatch`.
- C2. Fixture (f) is rebuilt. As written in 03, main holds 01 + diag.py and the branch adds only 02, so the tip has diag.py and no 03. `classify` (L238-241) counts any non-step file as a result and returns `SKIPPED: diag.py written before 03`, so a `BRANCH SKIPPED: 160` line appears for a reason that has nothing to do with 064. The new shape: main holds 01 02 03 + diag.py + the person's waiver, and the branch adds 07 and drops the waiver. The tip is then `complete` by classify, and the assertion can be the strong one: no `BRANCH SKIPPED: 160` line at all.
- C3. An edge R1-R3 did not name: before 064, `classify` already flags a work/<ID>/*.py written before 03 (same L238-241 rule). In fixture (a), the 062 detail replaces that classify line (main L571-572). The fixture asserts that, so mutation (i) still fails on `RESEARCH CODE: 160` and not on another SKIPPED line.
- C4. Absent-case tests for the inputs in 03 § Missing inputs that had none (see Guardrail tests).
- C5. The feasibility count gets a repo test that pins it (RI-001).
- C6. run-item.md L16 gets one sentence: a work/<ID>/*.py diagnostic is committed together with that item's step file. 03 AGAINST 2(ii) shows the new rule makes a bare diagnostic commit an UNTRACKED CHANGE. Agents (R1, I3) must be told in the rules, not find out from a red check (step 1a, last sentence). This stays in a file 03 already plans to change, so the count stays 4.
- C7. The real-repo test pins the request's Done line "061 on main stays `complete`".

## Extra research (with sources)
1. Python `re`: "`$` Matches the end of the string or just before the newline at the end of the string"; "`.` (Dot.) In the default mode, this matches any character except a newline"; `fullmatch`: "If the whole string matches the regular expression pattern, return a corresponding Match". The docs page also marks `re.match` "Soft deprecated since version 3.15 ... in favor of ... prefixmatch()". That is one more reason to use `fullmatch` for a new pattern. Source: https://docs.python.org/3/library/re.html (fetched 2026-11-14). Effect: C1. `.` matching `/` (03 Self-check row 2) is confirmed: only a newline is excluded.
2. `git diff-tree -r --name-only --no-renames` lists deleted paths as well as added and changed ones (no rename pairing). Source: https://git-scm.com/docs/git-diff-tree (cited in 01 F5 and 03). Effect: a later commit that deletes or moves `work/061/diag_keep.py` is a code change under 053 and needs an open item's step file in the same commit. That is the same as for ccbot/ (`test_rename_out_of_code_path_is_flagged`, tests L786-795). No extra test; I2 names it in the docstring sentence of step 4.
3. Repo edge (C3): `classify` L238-241 already treats a non-step file before 03 as a "result for the person". So an R1/R2 diagnostic in a RESEARCH ONLY item was partly visible before 064 (SKIPPED by classify on HEAD), but not after 03 exists. That is the 061 shape: R1 wrote diag_keep.py with 01 present and was found only by I3 reading it. 064 closes the after-03 case.
4. Simpler method considered: one combined `CODE_GLOBS` list with `fnmatch` instead of a prefix tuple plus a regex. Rejected: it would change `CODE_PATHS`' type and its exact-tuple assert (L803), and `fnmatch`'s `*` also matches `/`, so the ID shape `\d{3}` is harder to say. The regex follows `STEP_FILE` (L143).

## Files to create/change
4 files. Nothing under work/061 changes (run-item L16).

| # | File | Change |
|---|---|---|
| 1 | scripts/check_pipeline.py | After L140: `# Item 064: a .py file under a work item's folder (any depth) is code for 053 and 062.` + `WORK_CODE = re.compile(r"work/\d{3}/.+\.py")`. New `_is_code(f, paths)` (C1) next to `_build_waived`. L198: `code = [f for f in files if _is_code(f, RESEARCH_CODE_PATHS)]`. L481: `code = [f for f in files if _is_code(f, CODE_PATHS)]`. L417: `unit = changed(*RESEARCH_CODE_PATHS) + [f for f in changed("work/") if WORK_CODE.fullmatch(f)] + [f"work/{i}/{f}" for i in sorted(touched) for f in files[i] if f in STEPS.values()]`. Classify's use of `files[i]` (L410) is unchanged. Docstring: 03 step 4 text, with gap (e) extended (not a second "(e)"), new (k) and (l), the (i) note, and the deletion sentence (Extra research 2). |
| 2 | tests/test_pipeline_check.py | The tests listed under Tests and checks. |
| 3 | .claude/agents/a1-auditor.md | L20: "...that changes ccbot/, config/, scripts/, tests/, .claude/ or templates/" → add "or a `.py` file under work/<ID>/ (item 064)"; "A1's daily commits change only logs/ and work/" → "...only logs/ and work/ markdown". |
| 4 | .claude/commands/run-item.md | L8: "(ccbot/, scripts/, tests/, config/)" → "(ccbot/, scripts/, tests/, config/, or a `.py` file under work/<ID>/; item 064)". L16, after "I2 commits each code change together with its 05 change.": add "A diagnostic `.py` under work/<ID>/ is code too: commit it together with that item's step file (item 064)." (C6) |

Rule text the person follows: files 3 and 4 are that text, changed in the same plan (step 1a). Both are RULE_PATHS. On this branch they need the person's OK in PR review, like every .claude/ edit.

## Tests and checks
All new git tests are `@NO_GIT`. `cp = _cp()`.

Unit tests (no git):
- `test_work_code_pattern` (parametrize over 03 Self-check rows 1-8). Expect a match for `work/061/diag_keep.py` and `work/160/sub/x.py`. Expect no match for `work/160/diag.py.md`, `work/.gitkeep`, `work/tmp/x.py`, `work/160/01-research.md`, `work/1600/x.py` and `work/160/x.pyc`. Plus `_is_code` asserts: `_is_code("work/160/diag.py", cp.RESEARCH_CODE_PATHS)` True, `_is_code("ccbot/x.py", cp.RESEARCH_CODE_PATHS)` True and `_is_code("work/160/notes.md", cp.CODE_PATHS)` False.
- `test_research_code_rules`, three new asserts: `rc(["work/160/diag.py", "work/160/01-research.md"], texts.get)` gives 1 flag for 160, detail starting `RESEARCH ONLY: changes work/160/diag.py with no 04-06;`. `rc(["work/160/diag.py.md", "work/160/notes.md", "work/160/01-research.md"], texts.get) == []`. `rc(["work/tmp/x.py", "work/.gitkeep", "work/160/01-research.md"], texts.get) == []`. Absent request: `rc(["work/160/diag.py", "work/160/01-research.md"], lambda i: None) == [("160", "RESEARCH ONLY check: no request.md at the tip, item 062")]`.
- `test_work_code_counts_repo_diagnostics` (feasibility pin, C5; no git). Take every file under `REPO / "work"` as a posix path relative to REPO. The WORK_CODE matches include `work/061/diag_keep.py`, and none of them end in `.md`. No exact count is asserted, so a new diagnostic (for example from 063) doesn't break it. The dated count is 1 on 2026-11-14 (03).

HEAD fixtures (`_history` / `_research`):
- (a) `test_research_only_work_py_is_research_code`: `_item(repo, "160", ["01-research.md"], scope="RESEARCH ONLY", date="2026-11-11")` + `_write(repo, "work/160/diag.py")`, one commit c. Expect exit 1, `f"160: SKIPPED ({c[:7]} RESEARCH ONLY: changes work/160/diag.py"` in out, exactly one `160:` line, `"written before"` not in out (C3: the 062 detail replaces classify's), `line == "RESEARCH CODE: 160"`, and `"UNTRACKED CHANGE: none"` in out.
- (b) `test_py_added_to_completed_item_is_untracked`: `_write(repo, "work/150/x.py")` alone, commit c. Expect exit 1 and `line == f"UNTRACKED CHANGE: {c[:7]} work/150/x.py{WHY_053} (cutoff {cutoff[:7]} from --untracked-from)"`.
- (c) `test_open_full_item_covers_its_work_py`: `_item(repo, "170", ALL[:5], date="2026-11-11")` + `work/170/diag.py`, one commit. Expect exit 0, `UNTRACKED CHANGE: none (cutoff ...)`, `RESEARCH CODE: none`, and `"170: SKIPPED"` not in out.
- Absent input (diff-tree failed): `test_failed_diff_tree_is_an_entry_not_none(tmp_path, monkeypatch)`: `_history`, then `monkeypatch.chdir(repo)` and `walked = ([("ab" * 20, None)], None)`. Expect `cp.untracked_changes(cutoff, walked)` to start `"abababa (git diff-tree failed) (item 053:"` with `[1] is True`, and `cp.research_code(cutoff, walked)[0] == "none"` (053 owns the failure, 062 L497).
- Absent input (no git): `test_work_code_without_git`: tmp_path (no repo), `_item(tmp_path, "160", ["01-research.md", "02-improvements.md", "03-handoff.md"], scope="RESEARCH ONLY", date="2026-11-13")` + `work/160/diag.py`. Expect exit 0, `RESEARCH CODE: not checked (no git)` and `UNTRACKED CHANGE: not checked (no git)`.

Branch fixtures (`_repo_with_open_branch`, `_research(repo, _root(repo))`):
- (d) `test_research_only_branch_work_py_is_branch_skipped`: `_branch_adds(repo, "res", "160", RES_STEPS, RES_160, extra=["work/160/diag.py"])`. Expect exit 0, `"BRANCH SKIPPED: 160 (origin/res: RESEARCH ONLY: changes work/160/diag.py"` in out, and `"SKIPPED: none"` in out. (Tip classify: 01 02 03 07 present, so diag.py is not "before 03"; the line comes from 062 only.)
- (e) `test_research_only_branch_nested_py_is_seen`: the same with `extra=["work/160/sub/x.py"]`. Expect `"BRANCH SKIPPED: 160 (origin/res: RESEARCH ONLY: changes work/160/sub/x.py"`.
- (f) `test_branch_unchanged_tip_py_not_counted` (C2): on local main, `_item(repo, "160", ["01-research.md", "02-improvements.md", "03-handoff.md"], scope="RESEARCH ONLY", date="2026-11-11", waived="04 05 06 (person, 2026-11-13: test)")` + `_write(repo, "work/160/diag.py")`, then `_commit(repo)`. Then `_branch_adds(repo, "res", "160", ["07-audit-task.md"], RES_160)`, which drops the waiver at the tip, adds 07 and leaves diag.py unchanged. Expect exit 0, `"BRANCH SKIPPED: 160"` not in out, and `RESEARCH CODE: none`. Derivation: `changed("work/")` = [work/160/07-audit-task.md, work/160/request.md], so WORK_CODE gives []. The step part is 01 02 03 07, so code = [] and `_research_code` returns []. The tip classify is 01 02 03 07 = complete. On HEAD: the waiver is the person's, so 062 is none, and 160 is open, so 053 is none.
- Absent input (branch diff failed, gap (l)): `test_branch_diff_failure_hides_code_gap_l(tmp_path, monkeypatch)`: build (d), then `monkeypatch.chdir(repo)`. Wrap `cp._git` so that `args[0] == "diff"` returns `("", 1)` and every other call goes to the real `_git`. Call `cp.open_branches(dt.date(2026, 11, 13))` and expect no `origin/res` entry's `skipped` to contain "changes work/160/diag.py". This pins today's information-only behaviour, named as docstring gap (l). If someone later makes it loud, the test must change on purpose.

Real repo:
- `test_repo_pipeline_has_no_skipped_items` (L139): add `assert "061: complete" in out` (C7). The existing exit-0 assert and `RESEARCH CODE: none` cover 03 step 0/7 on every suite run.
- `test_untracked_from_is_fixed`: unedited, passes.

Step 0 gate (I2, before committing the rule; 03 step 0, unchanged): run `git fetch origin` and `python3 scripts/check_pipeline.py` as a baseline. Apply file 1 in the working tree and run it again. The `061:`, `UNTRACKED CHANGE:` and `RESEARCH CODE:` lines must be the same as the baseline: `complete` / `none` / `none`. Also count the first-parent units in `694bf4d..HEAD` whose `diff-tree` lists a WORK_CODE path and no CODE_PATHS path. Expect 0. Paste the command and the count in 05. A non-zero count means stop and go back to I1, with no exception list without the person's OK.

I3 mutations (scratch copy, never in the repo):
- (i) `_is_code` returns `f.startswith(paths)` only. Expected to fail: (a), (b), (d), (e), the positive work-path assert in `test_research_code_rules`, and `_is_code("work/160/diag.py", ...)` in `test_work_code_pattern`.
- (ii) L417's step part restored to unfiltered `files[i]` (step 1 kept). Expected to fail: (f).
- (iii) `WORK_CODE` without its end anchor (`work/\d{3}/.+\.py.*`). Expected to fail: the `diag.py.md` and `.pyc` parametrize cases (RI-012).
- `test_work_code_counts_repo_diagnostics` is a feasibility pin, not a mutation target.

Commands: `python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py`, then the full suite `python3 -m pytest -q -p no:cacheprovider`, then `python3 scripts/check_pipeline.py`, and `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` where python3.11 exists (RI-008).

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map step 0: gate, baseline and after, plus the first-parent unit count, expected 0 | Tests and checks § Step 0 gate. Real-repo test L139 + C7 |
| Map step 1: WORK_CODE next to RESEARCH_CODE_PATHS; L198/L481 `startswith or match`; tuples unchanged | Files #1 (via `_is_code` + `fullmatch`, C1); `test_work_code_pattern`; `test_research_code_rules` asserts; `test_untracked_from_is_fixed` unedited |
| Map step 2: branch unit L417 = changed code + changed work .py + step-filtered `files[i]`; classify's `files[i]` unchanged | Files #1 L417; fixtures (d), (e), (f) |
| Map step 3 (a)-(f) fixtures | (a), (b), (c), (d), (e) as in 03. (f) rebuilt (C2: 03's shape trips classify's result-before-03 rule). 03's "(b)/(c)" lettering is kept: (b) = completed item 150, (c) = open FULL 170 |
| Map step 4: docstring (053 and 062 paragraphs; gap (e) extended; (k); (l); the (i) note) | Files #1 docstring, plus the deletion sentence (Extra research 2) |
| Map step 5: a1-auditor L20 and run-item L8, one line each | Files #3 and #4. Also run-item L16 (C6) |
| Map step 6: I3 mutations (i), (ii) | Tests and checks § I3 mutations (i), (ii). Plus (iii) for RI-012 |
| Map step 7: full suite + repo check after commit; I2 commits code with its 05 | Tests and checks § Commands; 063 interaction 2 (separate commits) |
| Missing inputs: HEAD diff-tree fails → entry, never empty | `test_failed_diff_tree_is_an_entry_not_none` |
| Missing inputs: no git | `test_work_code_without_git` (existing `test_research_code_without_git` covers ccbot/) |
| Missing inputs: cutoff missing (shallow / full) | Existing `test_cutoff_missing_in_shallow_clone_not_checked`, `test_cutoff_missing_in_full_repo_fails`, `test_research_code_cutoff_missing_not_checked`. The input is the same and the new path adds no branch |
| Missing inputs: request.md absent at the tip | `test_research_code_rules` absent-request assert with a work .py |
| Missing inputs: branch change list `[]` on diff failure (gap l) | `test_branch_diff_failure_hides_code_gap_l` + docstring (l) |
| Missing inputs: non-ASCII path quoted, WORK_CODE no match (gap f) | DROPPED as a test: the existing gap (f) (no `-z`) applies to every path the same way, and 064 doesn't change how paths are read. Named in the docstring as covering work/ too |
| Fact-check fix F4 (startswith tuple: repo source instead of docs) | No plan line needed. `_is_code` keeps the existing tuple call, pinned by the existing `test_research_only_head_commit_with_code_is_skipped` |
| Fact-check fixes F17/F18 (9fcc76a unchanged; other units gated by step 0) | Step 0 gate + real-repo test |
| Fact-check fix: option A is 4 files, not 2; B is ≥ 5 | Files table: 4 files |
| Fact-check fix FOR 2: (c) full line text; (a) also asserts UNTRACKED none; (e)→ needs 01-05 | Fixtures (b) full-line equality, (a) `UNTRACKED CHANGE: none`, (c) `ALL[:5]` |
| Fact-check fix FOR 3: step part must be filtered by `STEPS.values()` | Files #1 L417; fixture (f); mutation (ii) |
| Fact-check fix AGAINST 1: 7 lines across 4 of 061's files | No plan line needed: option B is not built, and 061 is not edited |
| Fact-check fix AGAINST 3: extend gap (e), don't add a second (e) | Files #1 docstring |
| 02 Holes: `.py` only, no other script types | Files #1 (`\.py` only) + gap (e) text; `.pyc` negative case |
| 02 Holes: 061 not edited | Files table note; nothing under work/061 changes |

## Guardrail tests
- Feasibility: WORK_CODE (1 of 484 paths under work/, 03 Feasibility, 2026-11-14; I1 Glob `work/**/*.py` 2026-11-14 → 1) → `test_work_code_counts_repo_diagnostics` (includes `work/061/diag_keep.py`, no `.md`), plus `test_work_code_pattern` rows 1-8.
- Feasibility: branch unit, nested 1 of 1 flagged, unchanged tip .py 0 of 1 → fixtures (e) and (f).
- Feasibility: fixture counts (a) 1/1, (b) 1/1, (c) 0/1, (d) 1/1, (e) 1/1, (f) 0/1 → the six fixtures by name above.
- Missing inputs: HEAD `diff-tree` output → `test_failed_diff_tree_is_an_entry_not_none`.
- Missing inputs: git → `test_work_code_without_git`.
- Missing inputs: cutoff → existing three cutoff tests (unchanged path).
- Missing inputs: tip request.md → `test_research_code_rules` absent-request assert.
- Missing inputs: branch `git diff` → `test_branch_diff_failure_hides_code_gap_l` (pins gap (l), information-only).

## Expected result
- `tests/test_pipeline_check.py`: every existing test passes unedited except the one added assert in L139's test. New tests: `test_work_code_pattern` (8 parametrized cases plus the `_is_code` asserts), `test_work_code_counts_repo_diagnostics`, (a), (b), (c), (d), (e), (f), `test_failed_diff_tree_is_an_entry_not_none`, `test_work_code_without_git`, `test_branch_diff_failure_hides_code_gap_l`, plus 4 asserts in `test_research_code_rules`. That is 11 new test functions, 18 collected with the 8 parametrize cases.
- Full suite green: main's 293 passed / 1 skipped (exchange_calendars) + 064's new tests + whatever 063 adds. I2 reports the measured count, not this sum.
- `python3 scripts/check_pipeline.py` on the branch: `061: complete`, `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`, exit 0 (for 064's part; see 063 interaction 3). `RULES BRANCH:` is not printed for HEAD itself; on origin it is expected once pushed (check_pipeline.py and .claude/ are RULE_PATHS).
- Mutations (i)-(iii) each fail the named tests in a scratch copy.
- Grep `work/<ID>/` in a1-auditor.md L20 and run-item.md L8/L16 gives the new text. `git diff` on the two .claude files shows only those edits.
- Not closed by this item (stated so A1 doesn't find it again): the logic of a diagnostic in a FULL/FAST item is checked only by I3's re-run (gap (k)). Other script types under work/ are not checked (gap (e)).
