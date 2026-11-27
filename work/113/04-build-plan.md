# 04 Build plan - 113
Fit verdict: FIT WITH CHANGES

## Recurring issues checked
I read logs/recurring-issues.md first (item 013) and checked this plan against each open or ESCALATED entry, plus the GUARDED entries this item touches:
- RI-001 (ESCALATED): no strategy filter or window rule is added. The one count in the map, step 0's open-branch list (n) and its 3-target hits (k), is measured by I2 on the build day. Zero is a defined result ("0 open branches; grep not run"). Nothing assumes a candidate exists. The template-line pins (count == 1) are exact counts, not "exists" claims.
- RI-014 (OPEN): step 0a checks for a shallow or single-branch clone before any branch read. If either holds, the result is "not computed" and the keep-`who` path (2-alt) is taken. It is never read as 0 branches.
- RI-002 (GUARDED): every uncomputable git read in step 0 is written down with a named reason and takes the safe path. Change C2 below adds the case 03 missed: a `git grep` exit status that the docs leave undefined.
- RI-009 (GUARDED, linked): T-RB tells the reader never to switch the checkout. The origin/main view is a three-dot diff, or for A1 a scratch worktree.
- RI-010 (GUARDED, linked): every new template line and docstring sentence has its own pin test and a mutant (M-a1, M-3, M-4), so no duty exists as text only.
- RI-012 (GUARDED): the pins are exact lines (`splitlines().count(...) == 1`) or exact substrings of the normalised docstring. C1's hit classification compares whole line text with HEAD's own hits, not a substring guess.
- RI-015 (GUARDED): mutants M-a1, M-b1, M-b2, M-3 and M-4 run with PYTHONDONTWRITEBYTECODE=1 and a fresh PYTHONPYCACHEPREFIX. 05 pastes the `True <pyc dir>` env-check line.
- RI-004/005/006: I re-derived 03's Self-check rows against the code read below. They hold, with the line numbers confirmed (see Extra research 3).
- RI-007, RI-008, RI-011, RI-013: not touched. This is a FULL item, uses no syntax newer than Python 3.10, makes no change to branch-diff logic and no change to realtest.

## Fit check
- Account and strategy: the change is to process tooling only (templates, the checker's docstring, and one return value nobody reads). It does not touch ccbot/, config/ or any rule in 001 that the person follows. The ~$3k account is unaffected and no 001 rule text changes.
- Existing code: every line 03 cites matches this checkout. That covers parse_request L628-638, unpacks L660, L672 and L781, `[0]`-only callers L760, L768, L1323 and L2080, test L1974/L1976, docstring L226-234, RULE_PATHS L539 and STRAY_RUN_HEADING L508. Grep finds `parse_request` in no other script or test (scripts/, tests/; work/ hits are prose).
- Conflicts: none with built code. All edits are RULE_PATHS, so the PR needs the person's OK (03 step 6).
- Template feed check: test S7 (`test_unfilled_template_suite_line_is_incomplete`, tests L3787-3796) feeds templates/build-report.md as a 05 and asserts the exact INCOMPLETE string. T-RB starts with a backtick, sits under `## Deviations from plan` (after the Real-data comment section), and holds no `Suite:`, `Scratch dir:`, `#` or pytest summary text. So S7, the Suite count (L3886), the Scratch dir pin (L5655) and `test_t7d_cutoff_constant_matches_template_comment` (tests/test_real_data_field.py L151) all stay as they are. No script reads the build-plan template's `## Tests and checks` or the build-report's `## Deviations from plan` (Grep in scripts/: 0 hits).
- Why WITH CHANGES: C1-C3 below. None changes 03's texts T-RB, D-RB or D-110.

## Changes to 03 (I1)
- C1 (step 0b, edge case 03 missed): the k count should count only new callers. When main has moved ahead, `git branch -r --no-merged HEAD` can list origin/main (docstring L238-239, item 051). The same goes for any branch carrying today's parse_request. Those refs hold the same 3-target sites this item edits (L660, L672, L781, tests L1974), and git merges or conflicts those textually; they are not new callers. Under 03's rule they would count as k >= 1 and force step 2-alt for no reason. The new rule: before any edit, I2 runs `git grep -n parse_request HEAD -- scripts tests` and keeps the hit texts (path plus line text, line number dropped). For each listed ref, a hit counts toward k only if it unpacks `[2]` into 3 targets (or indexes `[2][2]`) and its path plus line text is not in HEAD's set. 05 lists every hit as ref:path:line with "known site" or "new caller". The decision rule is otherwise unchanged: k = 0 means remove, k >= 1 means keep.
- C2 (step 0b, missing-input row): the git-grep page documents no general exit status (Extra research 1). 03's "1 = no match" is therefore not documented. The new rule: a ref's grep counts as "no match" only when it exits 1 with empty stdout and empty stderr. Exit 0 means hits. Anything else (another exit, or any stderr) is "<ref>: grep not computed (<exit>, <stderr>)" and takes step 2-alt.
- C3 (step 2, mutants): M-b2 is added. Leave L660 (`_build_waived`) at `(steps, _, _)`, and the suite must fail. `_build_waived` has direct tests (tests L1284), so a failure is expected. I2 records the count. If M-b2 survives, I2 adds a direct `_build_waived` call to the new step 2 test before going on. M-b1 (L672) stays as 03 wrote it.

## Extra research (with sources)
1. git grep and its exit status. https://git-scm.com/docs/git-grep (fetched 2026-11-26): `<tree>...` means "Instead of searching tracked files in the working tree, search blobs in the given trees". This confirms 03's rule that a bare `git grep` with no ref searches the working tree. The page gives exit status only for `-q` ("exit with status 0 when there is a match and with non-zero status when there isn't") and `-m 0`. It gives none for a plain run, hence C2.
2. `--no-merged` and origin/main. https://git-scm.com/docs/git-branch (03 R1-1): this lists refs whose tips are not reachable from HEAD. Once main gains commits after this branch was cut, origin/main is such a ref. The repo's own docstring confirms the case (L238-239: MAIN AHEAD, "origin/main and branches whose tip is already in it are then left out of OPEN BRANCHES"), hence C1.
3. Repo re-read (Read and Grep, 2026-11-26). parse_request L628-638 returns `who.group(1).strip().lower()`, and no caller reads it: L660, L672 and L781 bind it to `_`, and the only test use is L1974/L1976 (`who == ""`). `_build_waived` has direct tests at L1284, `cp._build_waived(...) is counts`. STRAY_RUN_HEADING at L508 is case-insensitive and anchored by `.match`, and T-RB's leading backtick cannot match it.

## Files to create/change
1. templates/build-plan.md: insert T-RB (03 Implementation map, word for word, one physical line) on the line after `## Tests and checks`.
2. templates/build-report.md: insert T-RB on the line after `## Deviations from plan`.
3. scripts/check_pipeline.py:
   - Module docstring: insert D-110 after L231 ("... never to _STATS (the I2 field refuses it).") at the 18-space indent, wrapped. Append D-RB after "Listed, not an error." (L234) at the 18-space indent, wrapped. The texts are word for word from 03.
   - If step 0 says remove (step 2): parse_request drops L634 and returns `(re.findall(r"\d\d", waived.group(1)), waived.group(0).strip()) if waived else ([], "")` as the inner value. The docstring L629-630 becomes `(scope, date, (waived steps, first Waived: line)) from request.md text. `who` removed: no gate read it since 105 (item 113).` The unpacks become L660 `_, _, (steps, _)`, L672 `scope, _, (waived, _)` and L781 `scope, opened, (waived, waived_line)`. In the `_build_waived` docstring, "The anchor implies who == "person"." becomes "The anchor requires `(person, `.". Module docstring L15-20 is left as it is (`<who>` there is the request.md field).
   - If step 0 says keep (step 2-alt): only docstring L630 changes, to 03's step 2-alt text with `<ref> unpacks 3` or `open-branch check not computed` filled in from step 0.
4. tests/test_pipeline_check.py:
   - Step 2: L1974 becomes `scope, _, (waived, line) = cp.parse_request(text)` and L1976 becomes `assert waived == [] and line == ""`. Add `test_parse_request_inner_is_steps_and_line`.
   - Step 2-alt: add `test_parse_request_docstring_defers_who_removal` instead; L1974/L1976 unchanged.
   - Add `RB_TEMPLATE_LINE` (the T-RB string) and `test_rules_branch_template_line` (parametrized over both templates).
   - Add `test_rules_branch_docstring_names_no_merged`.
   - Extend `test_check_pipeline_docstring_records_110_no_go`.
5. work/113/05-build-report.md (I2's own report): add the section "Pre-build check (item 113)" with the step 0 results and the C1 hit labels.

## Tests and checks
- Step 0 (I2, before any edit; no file change except 05). 0a: `git rev-parse --is-shallow-repository` must print false, and `git config --get-all remote.origin.fetch` must include `refs/heads/*`. Then `git fetch origin`, and list the refs with `git branch -r --no-merged HEAD --format='%(refname:short)'`, dropping `*/HEAD`, to get n. 0b: run only if n >= 1, with C1 and C2 applied, to get k. 0c: `git merge-base --is-ancestor origin/daily-fixes/2026-11-25 HEAD`, recording the exit code. The decision rule is 03's, as amended by C1/C2.
- `test_rules_branch_template_line[templates/build-plan.md, templates/build-report.md]`: `splitlines().count(RB_TEMPLATE_LINE) == 1`, `cp.STRAY_RUN_HEADING.match(RB_TEMPLATE_LINE) is None`, and `not RB_TEMPLATE_LINE.startswith(("Suite:", "Scratch dir:"))`.
- `test_parse_request_inner_is_steps_and_line` (step 2): `cp.parse_request("Scope: FULL\nWaived: 03 06 (person, 2026-11-26: x)\n")[2] == (["03", "06"], "Waived: 03 06 (person, 2026-11-26: x)")`, and `cp.parse_request("Scope: FULL\n")[2] == ([], "")`. The second assert is the absent-case test.
- `test_parse_request_docstring_defers_who_removal` (step 2-alt): the normalised `cp.parse_request.__doc__` contains "removal deferred (item 113" and "test_inbox_quoted_scope_and_waiver_are_not_read".
- `test_rules_branch_docstring_names_no_merged`: the normalised module docstring contains "so from a branch's own checkout that branch and its merged base are not listed and the line normally reads none (item 113)" and "(`git branch -r --no-merged HEAD`)".
- `test_check_pipeline_docstring_records_110_no_go` (extended): adds "re-run the fenced script in work/110/01-research.md" in doc, "don't copy these (item 113)" in doc, and `(REPO / "work/110/01-research.md").is_file()`. The existing 7 asserts are unchanged.
- Staying green: S7 `test_unfilled_template_suite_line_is_incomplete`, `test_suite_label_in_template_and_i2_text`, `test_scratch_dir_template_line[2]`, `test_round_heading_template_lines`, `test_t7d_cutoff_constant_matches_template_comment[2]`, and the L1284 `_build_waived` tests.
- Re-grep after a step 2 edit: `parse_request` in scripts/ and tests/ shows no 3-target inner unpack, and `\bwho\b` in check_pipeline.py matches no code line, only docstring prose.
- Mutants, each in a scratch copy with PYTHONDONTWRITEBYTECODE=1 and a fresh PYTHONPYCACHEPREFIX, never in the repo:
  - M-a1: delete T-RB from build-plan.md only. Exactly `test_rules_branch_template_line[templates/build-plan.md]` fails.
  - M-b1 (step 2): L672 left at 3 targets. The suite fails; I2 records the count.
  - M-b2 (step 2, C3): L660 left at 3 targets. The suite fails; I2 records the count.
  - M-3: remove D-RB. `test_rules_branch_docstring_names_no_merged` fails.
  - M-4: drop "don't copy these" from D-110. The extended 110 test fails.
- Whole-output check (03 step 5): `python3 scripts/check_pipeline.py` with the base and the head script in the full clone. The diff must be identical apart from lines naming 113. RULES BRANCH must be unchanged, normally `none`. Exit codes must be equal. 05 pastes the full-suite last line as `Suite:`.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Header: all edits RULE_PATHS; PR section "Rule text for your review (item 113)" | Fit check "Conflicts"; Expected result, PR text |
| Exact texts T-RB, D-RB, D-110, copied unchanged | Files 1, 2, 3 (word for word from 03) |
| Step 0a full-clone check, fetch, ref list n | Tests and checks, Step 0; Missing inputs rows 1-2 |
| Step 0b grep only if n >= 1; count k | Tests and checks, Step 0, amended by C1 (known sites excluded) and C2 (exit-status rule) |
| Step 0c base ancestry | Tests and checks, Step 0; Missing inputs row 4 |
| Step 0 decision rule (k = 0 remove, else or not computed keep) | Files 3/4, step 2 vs step 2-alt branches |
| Step 1 T-RB in both templates at the named lines | Files 1, 2; `test_rules_branch_template_line`; M-a1 |
| Step 1 pins staying green (S7, Suite, Scratch dir, round heading) | Tests and checks, "Staying green" (plus the t7d template test I1 added) |
| Step 2 return 2-tuple, drop L634, docstring L629-630 | Files 3, step 2 bullet |
| Step 2 unpacks L660, L672, L781 | Files 3, step 2 bullet |
| Step 2 `_build_waived` docstring reword; L15-20 unchanged | Files 3, step 2 bullet |
| Step 2 tests L1974/L1976 and the new inner test | Files 4; `test_parse_request_inner_is_steps_and_line` |
| Step 2 re-grep (no 3-target unpack; `who` only in prose) | Tests and checks, re-grep |
| Step 2 mutant M-b1 | Tests and checks, mutants; M-b2 added (C3) |
| Step 2-alt docstring L630 text and its test | Files 3/4, step 2-alt; `test_parse_request_docstring_defers_who_removal` |
| Step 3 D-RB after L234 and its pin; M-3 | Files 3; `test_rules_branch_docstring_names_no_merged`; M-3 |
| Step 4 D-110 after L231; extend 110 test; is_file; M-4 | Files 3; extended 110 test; M-4 |
| Step 5 whole-output check, RULES BRANCH unchanged, exit equal, Suite line | Tests and checks, whole-output check |
| Step 5 optional A1 scratch-worktree view of origin/main | Expected result (A1 optional; never an in-repo checkout) |
| Step 6 PR text: T-RB, D-RB, D-110, step 2/2-alt text, step 0 n, k | Expected result, PR text |
| Missing inputs rows 1-6 | Guardrail tests, Missing inputs |
| 001 rule text the person follows | DROPPED: no 001 rule (slack, tolerance, cap) is changed by this item |

## Guardrail tests
- Feasibility: no strategy filter or window rule is added. The step 0 count n/k is measured by I2 and recorded in 05, and n = 0 is a defined result (03 Missing inputs row 2). The template-line rule is pinned by `test_rules_branch_template_line` (count == 1 in each of the 2 templates; M-a1 makes it 0).
- Missing inputs:
  - Waived line absent in request.md → the second assert of `test_parse_request_inner_is_steps_and_line` (`([], "")`). In step 2-alt the existing L1976 (`line == "" and who == ""`) stays the pin.
  - Remote branch list not computable (shallow, single-branch, git error) → no code test (step 0 is a manual check). 05 says "open-branch check not computed (<why>)" and step 2-alt is taken. A1 checks that 05 holds the line.
  - Remote branch list empty → 05 "0 open branches; grep not run". `git grep` is not run.
  - Per-ref grep status undefined (C2) → "<ref>: grep not computed (<exit>, <stderr>)", and step 2-alt is taken.
  - origin/daily-fixes/2026-11-25 missing → "base ancestry not computed (<error>)". T-RB is unchanged.
  - origin/main missing for T-RB's three-dot diff → the git error is the result, never "no rule change". This is in T-RB's reader instructions; there is no code path.

## Expected result
- Both templates carry T-RB once. The checker docstring carries D-RB and D-110. Either parse_request's inner value is `(steps, line)` (step 2), or its docstring says why `who` stays (step 2-alt), as step 0 decides.
- The full suite is green, with 3 new tests (or 4 cases, since the template test is parametrized ×2), 1 extended test and 1 edited test (step 2 only). M-a1, M-b1, M-b2, M-3 and M-4 are each killed.
- check_pipeline.py output on the branch is unchanged apart from lines naming 113. RULES BRANCH reads `none` on this checkout, as T-RB now says it normally will.
- PR description section "Rule text for your review (item 113)": T-RB, D-RB, D-110, the step 2 or 2-alt docstring text word for word, and the step 0 result (n, k with C1 labels, the 0c exit). The person must approve it in PR review (RULE_PATHS).
- Optional for A1: from a scratch worktree of origin/main (never an in-repo checkout), RULES BRANCH names this branch with templates/build-plan.md, templates/build-report.md and scripts/check_pipeline.py.

Log fields: FIT WITH CHANGES | 4 files planned
