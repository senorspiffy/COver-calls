# 05 Build report - 062
## Changes made (file: what changed)
Files, from the commands in 012:
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0 (new)
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → 5 (changed)

- scripts/check_pipeline.py:
  - step 1: `RESEARCH_CODE_PATHS = ("ccbot/", "config/", "scripts/", "tests/")`, `WAIVE_BUILD = {"04", "05", "06"}`, and `WAIVE_BUILD_BY_PERSON` (the date regex `\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:`). `read_request(path)` is now a one-line wrapper for the new `parse_request(text)`, which returns the same value. `_build_waived(text)` is True only when `WAIVE_BUILD <= set(steps)`, `who == "person"` and the first Waived line matches the date regex.
  - step 2: `_research_code(files, request_text_of)` works on paths only. It returns [] if the unit has no code, or if a FULL/FAST item's 04/05 is in the unit (gap g). LEGACY items are skipped. A missing tip request.md is flagged `RESEARCH ONLY check: no request.md at the tip, item 062`. A RESEARCH ONLY item without the person's waiver is flagged `RESEARCH ONLY: changes <code> with no 04-06; needs Scope FULL or "Waived: 04 05 06 (person, <date>: <why>)" on the item's single Waived: line (item 062)`.
  - step 3:
    - `_walk(cutoff)` holds 053's cutoff checks and first-parent walk. It returns `(units, None)` or `(None, (text, failed))`, and a diff-tree failure is `(sha, None)`.
    - `untracked_changes(cutoff, walked=None)` gives the same output as before; the 053 fixtures pass unchanged.
    - New `research_code(cutoff, walked=None)` returns None without git, `("not checked (see UNTRACKED CHANGE)", {})` when `_walk` fails, and otherwise `(summary, {ID: (sha7, detail)})`, reading request.md from the working tree.
    - `main()` walks once and passes the result to both checks. A flagged ID's line becomes `SKIPPED (<sha7> <detail>)`, placed after the LEGACY override and before IN PR. Flagged IDs with no request.md dir are printed after the loop and added to `skipped`. `RESEARCH CODE: ...` is printed right after UNTRACKED CHANGE. The exit line is unchanged.
  - step 4: `open_branches` keeps `requests[item]` (the tip request.md text, or None) from the existing `theirs` call. After the per-item loop, it builds one unit per ref, `changed(*RESEARCH_CODE_PATHS)` + `work/<i>/<f>`, and runs `_research_code` on it. A flag merges into an existing SKIPPED entry as `old; detail`, or is appended. The print and the exit code are unchanged.
  - step 5: docstring `RESEARCH CODE` entry under UNTRACKED CHANGE, with gaps (g)-(j).
- tests/test_pipeline_check.py:
  - `_branch_adds(..., extra=())` writes the extra paths with `_write`; the default changes nothing for old callers.
  - `test_repo_pipeline_has_no_skipped_items` now also asserts `RESEARCH CODE: none`.
  - New tests: `test_build_waiver_needs_person_date_and_all_three` (7 cases; the 7th added in round 2), `test_research_code_rules`, fixtures (1) `test_research_only_branch_with_code_is_branch_skipped`, (2a)+(2b) `test_research_only_branch_waiver_needs_the_person`, (3) `test_research_only_head_commit_with_code_is_skipped`, (4) `test_research_only_work_files_only_not_flagged`, (5) `test_full_item_build_in_same_commit_covers_research_code`, (6) `test_second_waived_line_is_not_read`, (7) `test_rescoped_to_full_is_not_research_but_still_skipped`, (8) `test_legacy_research_item_with_code_not_flagged`, (9) `test_research_code_without_git`, (10) `test_research_code_cutoff_missing_not_checked`.
- .claude/commands/run-item.md L8, .claude/agents/r3-fact-checker.md L22, .claude/agents/i3-verifier.md step 3 (L14): the 03 map step 7 sentences are appended word for word. `grep -c 062` gives 1 in each. The i3 names exist: `ccbot/expiries.py:72 pick_expiry`, `ccbot/pricing.py:53 pick_strike`, and `config/default.json` keys `target_delta`, `tolerance`, `monthly_dte`, `monthly_slack_days`.

## Connectivity check
- [x] Every new function or rule is used:
  - `parse_request` is used by `read_request`, `_build_waived` and `_research_code`.
  - `_build_waived` and `_research_code` are used by `research_code` (HEAD) and `open_branches` (branch).
  - `_walk` is used by `main`, `untracked_changes` and `research_code`.
  - `RESEARCH_CODE_PATHS` is used by `_research_code` and `changed()`. `WAIVE_BUILD` and `WAIVE_BUILD_BY_PERSON` are used by `_build_waived`.
  - The three rule sentences are in their agent files.
- [x] Every input has a source and every output has a consumer:
  - Inputs: the first-parent walk after UNTRACKED_FROM, request.md in the working tree or `git show <ref>:`, and merge-tree `changed()`.
  - Outputs: the `<ID>: SKIPPED` line plus `skipped` (exit 1), `BRANCH SKIPPED:` lines, and the `RESEARCH CODE:` summary line read by A1.
- [x] Every branch ends in a defined result:
  - no git → `not checked (no git)`;
  - cutoff unusable → `not checked (see UNTRACKED CHANGE)`, with 053 reporting it and setting the exit;
  - diff-tree failure → 053's entry (exit 1), and the research check treats the unit as having no files;
  - no code → nothing to flag;
  - covered by FULL/FAST 04/05 → none (gap g, documented);
  - LEGACY → skipped (documented);
  - no tip request.md → flagged;
  - a flagged item with no request.md dir on HEAD → printed after the loop and counted in SKIPPED;
  - several commits flagging the same item → one line with the details joined by `;`.
- [x] No leftover TODOs or unused files (`grep -n TODO scripts/check_pipeline.py` → nothing).

Missing-data grep: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` → 29 hits, all existing. This item changes nothing under ccbot/ (`git diff --stat -- ccbot/` is empty), so 0 hits are new or changed. The same patterns in my scripts/ diff give one hit:
- `texts[i] is not None and parse_request(texts[i])[0] in ("FULL", "FAST")` (scripts/check_pipeline.py `_research_code`): a building item with no request.md does not cover the unit, so the unit goes on to the flag loop, where the missing request.md is itself flagged. Absent data blocks; it never passes.

014 patterns: no new dataclass and no numeric default. There is no new `>`/`<` on values that could be NaN; the tests are set inclusion and string equality.

Feasibility tests the plan names (real numbers from this run):
- HEAD flag rule: `RESEARCH CODE: none` on this HEAD (0 flags; plan expected 0).
- Branch flag rule: 1 flag, `BRANCH SKIPPED: 061 (origin/claude/project-thread-ltyppm: ...)` (plan expected 1).
- Waiver rule: 2 of 7 strings count (6 in round 1, plus the copied-bracket case from round 2; the parametrized test passes with exactly the 2 True cases).

## Test output (pasted, not summarized)
Before the change: `python3 -m pytest -q tests/test_pipeline_check.py` → `52 passed in 7.77s`.

After the change:
```
$ python3 -m pytest -q tests/test_pipeline_check.py
.....................................................................    [100%]
69 passed in 10.23s
$ python3 -m pytest -q
........................................................................ [ 56%]
........................................................................ [ 84%]
.......................................                                  [100%]
254 passed, 1 skipped in 26.61s
$ python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py && echo COMPILE_OK
COMPILE_OK
```

`git fetch origin`, then `python3 scripts/check_pipeline.py` on this HEAD (exit=0). Relevant lines:
```
ID CLASH: none
BRANCH SKIPPED: 061 (origin/claude/project-thread-ltyppm: RESEARCH ONLY: changes ccbot/realtest.py scripts/fetch_real_data.py tests/test_realtest.py with no 04-06; needs Scope FULL or "Waived: 04 05 06 (person, <date>: <why>)" on the item's single Waived: line (item 062))
A1 FAIL: none
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
RESEARCH CODE: none
ORPHAN LOG: none
SKIPPED: none
```
I compared this with HEAD's committed script (`git show HEAD:scripts/check_pipeline.py`) run on the same tree, using `diff old new`. There are only two added lines, the `BRANCH SKIPPED: 061 ...` line and `RESEARCH CODE: none`, so no new SKIPPED on this HEAD.

Mutation probes (scratch copy of the repo in the session scratchpad, deleted afterwards; the repo was not touched), running the 062 tests (`-k "research or waiver or rescoped or legacy_research or second_waived or full_item_build"`):
- M1, drop the Scope test in `_research_code`: `test_research_code_rules` and `test_rescoped_to_full_is_not_research_but_still_skipped` FAIL (2 failed, 16 passed).
- M2, drop `WAIVE_BUILD <=`: the `Waived: 04 (person, 2026-11-13: x)` case FAILs (1 failed, 17 passed).
- M3, drop `who == "person"` (corrected after I3 round 1): in round 1 this probe failed 0 tests (0 failed, 18 passed), and I wrongly called the who check redundant. It is not: `WAIVE_BUILD_BY_PERSON.search` scans the whole Waived line, so `Waived: 04 05 06 (I2, 2026-11-13: copied "(person, 2026-11-12: ok)")` matches the regex, and only the who check stops it. Round 2 adds that string as a False case to `test_build_waiver_needs_person_date_and_all_three`. M3 rerun on a scratch copy: `FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (I2, 2026-11-13: copied "(person, 2026-11-12: ok)")-False]`, 1 failed, 18 passed.
- M4, drop the regex only: the `(person: ok)` case FAILs. M5, drop both who and the regex: 3 FAIL.
- Regex anchoring, probed and not built: with the regex anchored to the first bracket (`^Waived:\s*[0-9 ,]+\(\s*person...`), the 062 tests pass (19 passed). But M3 then fails 0 tests again (19 passed), because the anchored regex alone rejects the copied bracket and the who check becomes untestable. The plan's regex is kept, so each of the two checks is pinned by its own case. This is noted for I1.

Round 2 (after I3 round 1), with the copied-bracket case added:
```
$ python3 -m pytest -q tests/test_pipeline_check.py
70 passed in 8.89s
$ python3 -m pytest -q
255 passed, 1 skipped in 24.58s
```

## Deviations from plan
- Fixtures (2a)/(2b) are one test, `test_research_only_branch_waiver_needs_the_person`, with two branches in one repo: `ok` (160, person's waiver) and `bad` (161, I2 waiver, `ccbot/y.py`). The plan had "the same branch" twice. The assertions are the plan's.
- In fixture (5), item 161 has 01-05 (FULL, in progress) instead of only 05. With only 05 it would be SKIPPED by classify, which is not what the fixture is about. It still pins gap (g).
- `untracked_changes` and `research_code` take an optional `walked`, so `main()` walks the history once ("both HEAD checks share one walk"). Called alone, each still walks for itself.
- When several HEAD commits flag the same item, the details are joined with `;` behind the first sha7. The plan's dict holds one entry per ID and did not say what to do with a second flag.
- `WAIVE_BUILD_BY_PERSON` is a named constant for the plan's regex (no change in meaning).
- Round 2 (after I3 round 1): one test case added (the copied person bracket), and the 04 mutation line corrected. The regex is not anchored (see M3).

## Notes for the person (03 map step 8; A1 repeats them in the report)
- (a) PR #26 (item 061, origin/claude/project-thread-ltyppm) now shows as `BRANCH SKIPPED: 061`. Before it merges after 062, it needs `Waived: 04 05 06 (person, <date>: <why>)` as the single Waived line in work/061/request.md, or a FULL re-run of 061. Otherwise main's check exits 1 after the merge.
- (b) The request's "exit 1" in "Done looks like" applies to the HEAD fixture. BRANCH SKIPPED stays exit 0, as designed in 038. The person may override this.
- (c) Gap (h), RESEARCH ONLY edits to .claude/ or templates/ (left to 053 only), is offered as a separate item.
- (d) A1's note that 061's three R-log lines share one commit (logs/audit/2026-11-13.md L22) is not covered by this item. It goes to A1 as an open gap.

## Recurring issues checked (I2)
Read logs/recurring-issues.md first. I checked the output against each open or ESCALATED entry:
- RI-001 (ESCALATED): the three feasibility numbers are computed above (HEAD 0, branch 1, waiver 2 of 7).
- RI-007 (ESCALATED): this item.
- RI-011 (OPEN): the branch side uses `changed()` from merge-tree; only the existing fallback uses `HEAD...ref`.
- RI-012 (OPEN): items come from paths only. The negative waiver test puts "person" inside I2's text.

Also checked:
- RI-002: missing-data grep and reasons above.
- RI-008: py_compile with python3.11 passes, with no 3.12-only syntax. `requires-python = ">=3.10"`.
- RI-009: the mutations ran in a scratch copy.
- RI-010: the log line is written with `--log`.

RI-001: feasibility numbers recorded (HEAD 0 / branch 1 / waiver 2 of 7); no change to status.
RI-007: guardrail built (062); GUARDED when merged and a RESEARCH ONLY fixture with a ccbot/ file gives SKIPPED (`test_research_only_head_commit_with_code_is_skipped`, passing here).
RI-011: not affected; the branch side uses merge-tree `changed()`.
RI-012: not affected; items come from paths only, and there is a negative waiver test with "person" in another who's text.
