# 05 Build report - 105
Scratch dir: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-105-r1-co_w6ctp

Made with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i2-105-r1-", dir="/tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad"))'`. Inside it: `base/` (a `git worktree add --detach` worktree at 1662121, the build base), `head/` (a detached worktree at 1662121 plus one scratch commit 495f724 that holds this build's two files and a placeholder work/105/05, used for the real-data diff and the mutations), and `pyc/` (a fresh PYTHONPYCACHEPREFIX per run). Every mutation run used PYTHONDONTWRITEBYTECODE=1. No `git stash` was used anywhere. Each probe file was restored with `git checkout HEAD -- scripts/check_pipeline.py` inside `head/`. Afterwards `git status --short | wc -l` in `head/` printed 0.

Base: the branch daily-fixes/2026-11-25 at 1662121, which already has 108 (4619802) and 110 (bc96b01). Later commits on the branch (d22432f, e031e3d, 84d3a1c, 04d0267) change only work/ and logs/ files of other items: `git diff --stat 1662121 HEAD -- scripts tests ccbot config templates .claude` is empty.

## Changes made (file: what changed)
File counts, from the commands:
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` printed 0 (new)
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` printed 2 (changed)

`git diff --stat`: `scripts/check_pipeline.py | 44 +++---`, `tests/test_pipeline_check.py | 51 +++---`, 2 files changed, 75 insertions(+), 20 deletions(-).

1. `scripts/check_pipeline.py`
   - New `_person_dated(text)`, placed just above `_build_waived`. It runs `WAIVED_LINE.search` and then `PERSON_DATED.match(m.group(2))`, and returns a bool. Its docstring says it reads only the first Waived line, the match is anchored (RI-012), it uses re.match and not prefixmatch (RI-008), and it is a format check, not proof of who wrote the line. It lists the known gaps: case-sensitive `person` (fails safe), the date is not validated (2026-13-45, Unicode digits match `\d`), and a later Waived line is never read.
   - `_build_waived` now returns `WAIVE_BUILD <= set(steps) and _person_dated(text)`. Its docstring names `_person_dated`.
   - `_person_waived_before_i2`: the local `m = WAIVED_LINE.search(...)` is dropped. The condition now starts `_person_dated(req_text) and pre and ...`, and the docstring names `_person_dated`.
   - The item 093 comment above `WAIVED_LINE`/`PERSON_DATED` now says PERSON_DATED is used only through `_person_dated` (by 093, 100 and, from 105, classify).
   - `classify` unpacks `(waived, waived_line, _)` and sets `dated = _person_dated(req_text)` and `blocked = [s for s in waived if s in PERSON_ONLY and not dated]`. The message is now `{scope}: {blocked} can be waived only by the person, as (person, <date>: <why>){extra}`. The FAST check is unchanged.
   - Module docstring: the 031 sentence is replaced with the plan's text (items 031, 105; documented form; a format check; case-sensitive; the date is not validated; only the first Waived line is read).
   - `parse_request`: the code is unchanged. Its docstring adds "who: kept for the tuple shape; no gate reads it since 105."
2. `tests/test_pipeline_check.py`
   - New module constants `PERSON_ONLY_MSG` (the wording, written once) and `SETUP_105` (setups A-D).
   - New `test_person_only_waiver_needs_dated_form`, parametrized with ids R1-R13 exactly as in the plan table, with the plan's docstring. It is placed right after `test_fact_check_and_verification_waivable_only_by_person`. It writes `work/998/request.md` plus empty step files (names from the existing `STEP_NAMES`), and asserts `classify(d, dt.date(2026, 11, 25)) == (status, detail)`. The file has no module-level `dt`, so the test uses a local `import datetime as dt`, the same way the file's other tests do.
   - `test_fact_check_and_verification_waivable_only_by_person`: the 107 and 108 asserts now use the new wording. The `SKIPPED: 107, 108` assert and `code == 1` are unchanged. The docstring adds "; item 105: and only in the dated form".
   - `test_batch_waiver_not_excused_stays_strict`: N-b and N-d are flipped to `True`, each with a trailing `# item 105: undated 03 waiver` comment (the existing `# N-b`/`# N-d` markers are kept after it). The docstring adds the plan's sentence.

Not changed (as planned): `templates/request.md` and `.claude/commands/run-item.md`. The proposed rule text for them goes in the PR text (plan, Rule text).

## Connectivity check
- [x] every new function/rule is used: `_person_dated` is called by `classify`, `_build_waived` and `_person_waived_before_i2` (3 callers, checked with grep). `PERSON_ONLY_MSG` and `SETUP_105` are read by the new test. `PERSON_DATED` is now read only inside `_person_dated` (grep `PERSON_DATED\.` gives 1 code hit).
- [x] every input has a source, every output has a consumer: the input is the request.md text (from `_read`). The output is classify's (status, detail), which is printed per item and in the `SKIPPED:` summary line (exit 1).
- [x] every branch ends in a defined result. No Waived line: dated False, waived [], blocked []. The normal step rules apply, unchanged (the `test_stuck_after_one_day` family is green). Empty group 2 (`Waived: 03 06`): SKIPPED (R12). Unreadable request.md: UNREADABLE before parsing (`test_unreadable_request` is green). An undated or other-who 03/06 waiver: SKIPPED. A non-03/06 waiver: unaffected (R11).
- [x] no leftover TODOs or unused files: `git diff | grep -n TODO` finds nothing, and no file was added. `who` in `parse_request` now has no reader. It is kept on purpose for the 3-tuple shape (plan Files 1, last bullet) and its docstring says so.
- Missing-data policy. `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` gives 38 hits. All of them predate this change: ccbot/ is not touched (`git diff --stat -- ccbot/` is empty), so there is no new or changed hit. Running the same pattern over this diff's added lines gives no hit. The same diff has no numeric dataclass default. Its only `<=` tests are set-subset tests (`WAIVE_BUILD <= set(steps)`, `set(pre) <= set(waived)`), which take no numeric NaN input. An absent or unparseable waiver text gives `_person_dated` False, so the item is blocked (SKIPPED), never passed.
- Feasibility numbers (plan, Guardrail tests). Real Waived items: 2 (023 waives 02 by A1; 024 waives 01 02 03 04, person-dated). Real PERSON_ONLY waivers: 1, and it is dated (024). Both show the same output before and after (Real-data effect, below). Open-branch items with a Waived line: 0 (`OPEN BRANCHES` lists one branch, `items none`, in both runs). The accept branch is reached by R8-R10 and 085. The block branch is reached per step by R6 (06), R7 (03) and R1 (both).

## Test output (pasted, not summarized)
1. Base code with the new and updated tests (main checkout, before the code edit). Command: `python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py -k "person_only_waiver_needs_dated_form or fact_check_and_verification_waivable or batch_waiver_not_excused_stays_strict"`
```
FAILED tests/test_pipeline_check.py::test_fact_check_and_verification_waivable_only_by_person
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R1]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R2]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R3]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R4]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R5]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R6]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R7]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R12]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R13]
FAILED tests/test_pipeline_check.py::test_batch_waiver_not_excused_stays_strict[N-b]
FAILED tests/test_pipeline_check.py::test_batch_waiver_not_excused_stays_strict[N-d]
12 failed, 8 passed, 514 deselected in 3.88s
```
   The failure reasons (`-vv`), in order: R1-R7 and R13 each fail on `At index 0 diff: 'in progress' != 'SKIPPED'`. R12 fails on `At index 1 diff: 'FULL: 03 06 can be waived only by the person; Waived: 03 06' != 'FULL: 03 06 can be waived only by the person, as (person, <date>: <why>); Waived: 03 06'`. R8-R11 pass. The 8 passed are R8-R11 plus N-a, N-c, N-e and N-f. This matches the plan: 12 failed, and the 4 positive rows pass.
2. The same group after the change, plus every "unchanged, must stay green" test in the plan (`-k` over person_only_waiver_needs_dated_form, fact_check_and_verification_waivable, batch_waiver_not_excused_stays_strict, research_only_branch_waiver, build_waiver_needs, person_dated_anchor, person_waiver_helper, batch_person_waiver_before_i2, batch_waiver_missing_inputs, waived_steps_are_excused, unreadable_request, research_code_rules):
```
46 passed, 488 deselected in 4.90s
```
3. `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` (Python 3.11.18): `py_compile exit 0`.
4. Base full suite, in `base/` at 1662121 (`env -u PYTEST_ADDOPTS PY_COLORS=0 python3 -m pytest -q -p no:cacheprovider`, PYTHONDONTWRITEBYTECODE=1):
```
1014 passed, 1 skipped in 217.75s (0:03:37)
```
5. Full suite after the change, from the repo root (`env -u PYTEST_ADDOPTS PY_COLORS=0 python3 -m pytest -q`, Python 3.13.18). This is base + 13 passed with the same 1 skip and 0 failed, as the plan expects.
```
1027 passed, 1 skipped in 138.84s (0:02:18)
```

Suite: 1027 passed, 1 skipped in 138.84s (0:02:18)

6. Mutations, run one at a time in `head/` on `scripts/check_pipeline.py`, each with the whole `tests/test_pipeline_check.py` (534 tests), and each restored with `git checkout HEAD -- scripts/check_pipeline.py` before the next. Every mutation also fails `test_repo_pipeline_has_no_skipped_items`. That is an artifact of the scratch worktree, not a kill. Control, unmutated `head/`: that test alone gives `1 failed, 533 deselected in 5.11s` with `INCOMPLETE: 105 (no log line for I2; 05 has no Scratch dir: line (item 097))`, because the placeholder 05 has no log line. Below it is listed as `repo*`.
   - M-a (`who` unpacked; `who != "person"`; new message kept): 11 failed, 523 passed. Fails R1, R2, R3, R4, R5, R6, R7, R13, N-b, N-d, repo*. R12 passes (who "" still blocks it), as the plan says. The plan's list leaves out N-b and N-d: with who = "person", the undated `(person: ...)` 03 waiver is not blocked.
   - M-b (`PERSON_DATED.search(m.group(2))`): 8 failed, 526 passed. Fails R3, R4, `_build_waived` cases 7, 8 and 9 (I2 copied; `(person: x "...")`; `(person) x`), N-c, N-d, repo*. This matches the plan.
   - M-c (`re.match(PERSON_DATED.pattern, m.group(2), re.I)`): 2 failed, 532 passed. Fails R5 and repo*. This matches the plan.
   - M-d (`not (dated or s == "06")`): 11 failed, 523 passed. Fails R1, R2, R3, R4, R5, R6, R12, R13, `test_fact_check_and_verification_waivable_only_by_person`, `test_research_only_branch_waiver_needs_the_person` and repo*. It covers the plan's list, plus the two older tests.
   - M-e (`not (dated or s == "03")`): 13 failed, 521 passed. Fails R1, R2, R3, R4, R7, R12, R13, `test_fact_check_and_verification_waivable_only_by_person`, N-a, N-b, N-c, N-d and repo*. It covers the plan's list, plus extra tests.
   - M-f (`PERSON_DATED.match(m.group(0))`): 16 failed, 518 passed. Fails R8, R9, R10, `test_waived_steps_are_excused_and_printed`, `_build_waived` cases 1 and 2, `test_person_waiver_helper_on_item_024`, `test_batch_person_waiver_before_i2_excused[FULL]` and `[FAST]`, `test_research_code_rules`, `test_research_only_branch_waiver_needs_the_person`, `test_branch_unchanged_tip_py_not_counted`, `test_batch_no_line_before_i2_strict_from_090[990-INCOMPLETE: none]`, `test_excused_reason_not_strict`, N-f and repo*. It covers the plan's list, including the named older tests.
   - M-g (`blocked = list(waived) if not dated else []`): 3 failed, 531 passed. Fails R11, `test_waived_steps_are_excused_and_printed` and repo*. This matches the plan (the 106 assert).
   - M-h (`any(PERSON_DATED.match(x.group(2)) for x in WAIVED_LINE.finditer(text))`): 3 failed, 531 passed. Fails R13, `test_batch_waiver_missing_inputs_strict[N-j]` and repo*. The plan's list also names `_build_waived` case 6. That case does not fail: `_build_waived` takes its steps from the first line only (`[02]`), so `WAIVE_BUILD <= set(steps)` is False with either reader. M-h is still killed by R13 (this item's test) and by N-j.
   - Result: all 8 mutations are killed by at least one row of `test_person_only_waiver_needs_dated_form`. M-f is also killed by `test_waived_steps_are_excused_and_printed` and `test_person_waiver_helper_on_item_024`. M-g is also killed by `test_waived_steps_are_excused_and_printed`.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat` lists only scripts/check_pipeline.py and tests/test_pipeline_check.py, so no TRIGGER file is touched).

Plan Tests 5, the checker's whole-output diff on real repo data. The clone is full (`git rev-parse --is-shallow-repository` prints `false`). Both runs used `python3 scripts/check_pipeline.py` with no arguments, in the two scratch worktrees at the same base tree: `base/` = 1662121, and `head/` = 1662121 + scratch commit 495f724 (this build plus a placeholder work/105/05).
```
base exit 0
head exit 1
105c105
< 105: in progress (FULL: next 05)
---
> 105: in progress (FULL: next 06)
120c120
< INCOMPLETE: none
---
> INCOMPLETE: 105 (no log line for I2; 05 has no Scratch dir: line (item 097))
diff exit 1
```
Each output has 132 lines. The only lines that differ name item 105 itself. Both come from the placeholder 05 in the scratch commit, which has no I2 log line. They are not an effect of the code change, and they cause the exit-code difference. All other lines are identical, including `023: complete (RESEARCH ONLY; Waived: 02 (A1, ...` and `024: complete (FULL; Waived: 01 02 03 04 (person, 2026-10-31: ...`, OPEN BRANCHES, ID CLASH and `RULES BRANCH: none`. So 0 of 2 real Waived items change, as 03 Self-check row 11 expects.

A second run, from the main checkout before any commit, compared the base script (`base/scripts/check_pipeline.py`) with the edited script, both on the same cwd. Output: `base exit 0`, `head exit 0`, `diff exit 0`, 132 lines.

## Deviations from plan
- Tests 5 expects the RULES BRANCH line to name scripts/check_pipeline.py "on this branch". In both runs it reads `RULES BRANCH: none`. RULES BRANCH reports open remote branches (`origin/*` not merged into HEAD), and this branch is not pushed (the orchestrator said not to push). The line will name this branch's rule change only once the branch is pushed and seen from another checkout. No code change was made for this. The PR text must still carry the "Rule text for your review (item 105)" section from the plan.
- Mutation kill lists (plan Tests 4). These are differences in observed results only. No code or test changed because of them. (a) M-a also kills N-b and N-d. (b) M-h does not kill `_build_waived` case 6, for the reason given above. It is still killed by R13 and N-j. (c) M-d, M-e and M-f kill more tests than listed. All of these are reported to I1/I3 as facts. None of them leaves a mutation unkilled, so I did not send the plan back.
- The comment form on N-b and N-d is `# item 105: undated 03 waiver               # N-b`: the plan's comment, with the existing id marker kept after it.

## Recurring issues checked (item 013)
Read logs/recurring-issues.md on 2026-11-25 before building. Each open or ESCALATED entry:
- RI-001 (ESCALATED): the count behind each rule was computed, not assumed: 2 real Waived items, 1 real PERSON_ONLY waiver (024, dated), 0 open-branch Waived items. The accept and block branches are both reached, by named rows. RI-001: checked, no new occurrence.
- RI-014 (OPEN): the change reads no git. The real-data diff was run in a full clone (`false` for shallow), so there are no "not checked" lines to compare. RI-014: checked, unchanged (OPEN).
- Also checked, from the plan's list: RI-002 (an absent or unparseable waiver blocks: R12, R13; the grep above), RI-006 (every count above is pasted from a command), RI-008 (py_compile 3.11 exit 0; `.match` kept), RI-009 (scratch worktrees made with mkdtemp; no stash; restored with `git checkout HEAD --` in scratch only), RI-010 (the log line is written by `--log`), RI-012 (anchored match; in-text negatives R3, R4; M-b and M-h killed).

Guardrail status lines for A1 to copy on main (item 036). This branch does not edit logs/recurring-issues.md.
RI-012: GUARDED, unchanged. The 105 near miss (an undated person 03/06 waiver accepted) is fixed on this branch: classify uses the anchored `_person_dated`, and M-a, M-b and M-h are each killed by R-rows.
RI-001: ESCALATED, unchanged; no new occurrence.
RI-014: OPEN, unchanged; no new occurrence.

Pipeline check: main checkout `python3 scripts/check_pipeline.py` exit 0 before commit (`SKIPPED: none`, `INCOMPLETE: none`, `I3 FAIL: none`, `A1 FAIL: none`).
