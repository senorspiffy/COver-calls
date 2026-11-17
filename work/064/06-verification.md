# 06 Verification - 064
Verdict: PASS (round 1)
<!-- On every re-verification, update this line first: it must show the latest round. -->

Verified on branch daily-fixes/2026-11-14 at HEAD 779a414 (I2 build commit), 2026-11-15. Type EFFICIENCY (not a BUG), so the BUG-only parts of step 3 (fix + prevention guardrail) are covered by the equivalent checks below: the new rule is mutated three ways (plus one extra mutation of my own) and replayed on the 061 shape.

## I1 audit (plan vs research)
04 follows 03's verified hand-off (Option A, 4 files, nothing under work/061). Every map step 0-7 and every Missing-inputs row has a line in 04's Rule trace; the one DROPPED row (gap (f) test) gives a reason (the path reading is unchanged and gap (f) already covers it).

The changes C1-C7 are sourced or derived from the repo:
- C1 (`_is_code` + `fullmatch`): sourced to the Python re docs (Extra research 1). It gives the same results on 03 Self-check rows 1-8. I re-ran them through the shipped pattern: the 8 parametrized cases pass.
- C2 (fixture (f) rebuilt): the reason holds. `classify` flags a non-step file written before 03 (`check_pipeline.py` L262 `written before`). My probe below shows that rule firing on a 01-only RESEARCH ONLY item on the pre-064 script (`999: SKIPPED (RESEARCH ONLY: diag.py written before 02 03)`). So 03's shape would have tripped classify for a reason unrelated to 064.
- C3 (classify already sees a .py before 03): confirmed by the same probe. C4/C5/C7 add tests only. C6 (run-item L16 sentence) follows from 03 AGAINST 2(ii) and stays inside a file 03 already planned to change (still 4 files).
- No unsourced additions. Mutation (iii) and the absent-input tests are additions, but each one traces to RI-012 or an 03 Missing-inputs row.

## I2 audit (build vs plan)
Line by line against 04 § Files (from `git show 779a414`):
- scripts/check_pipeline.py: `WORK_CODE = re.compile(r"work/\d{3}/.+\.py")` with the item-064 comment, after RESEARCH_CODE_PATHS. `_is_code(f, paths)` = `f.startswith(paths) or WORK_CODE.fullmatch(f) is not None`. It is called at `_research_code` and `untracked_changes`. The branch unit is `changed(*RESEARCH_CODE_PATHS) + [f for f in changed("work/") if WORK_CODE.fullmatch(f)] + [... files[i] if f in STEPS.values()]`. `STEPS.values()` holds the 7 step filenames (L121-123). Classify's `files[i]` is untouched. `CODE_PATHS` and `RESEARCH_CODE_PATHS` are unchanged. Docstring: gap (e) extended (no second "(e)"), (f) under work/ too, the 053 sentence plus the deletion/move sentence, the 062 branch-unit text, the (i) note, and (k) and (l). This matches 04.
- tests/test_pipeline_check.py: the `061: complete` assert, 4 asserts in `test_research_code_rules` (including the absent-request case), and the 11 new functions named in 04. 70 -> 88 collected, as 05 says.
- .claude/agents/a1-auditor.md L20 and .claude/commands/run-item.md L8/L16: exactly the 04 text, no other edits in the diff. Both are RULE_PATHS and need the person's OK in PR review (the rule text the person follows changed in this same item).
- 05's deviations (mutation (i) fails all 8 parametrize cases, (iii) also fails `test_research_code_rules`) are stricter than planned. Accepted. Cause: `test_work_code_pattern` repeats three constant `_is_code` asserts in every parametrized case. Harmless, but each case is then not about its own path only (note for A1, not a defect).
- Connectivity re-done: `WORK_CODE` is used by `_is_code` and the branch unit; `_is_code` by both call sites. The outputs go to the existing `RESEARCH CODE:`, `UNTRACKED CHANGE:`, `<ID>: SKIPPED` and `BRANCH SKIPPED:` lines (shown in the probe below). No new files, no TODOs.
- Grep reasons in 05 checked: on the added lines of `git show -U0 779a414 -- scripts tests`, the missing-data grep hits only the two comment lines (`or 0` inside "for 053"). As 05 says, these are comments, not code. ccbot/ is unchanged.
- Step 0 gate re-done: `for c in $(git rev-list --first-parent 694bf4d..HEAD) ...` gives `9fcc76a... work=1 code=19` and `only-work units: 0 of 20`. 05 has 0 of 19: the 20th unit is 779a414 itself, which has no work .py. Feasibility: `git ls-files work` -> 490 paths; WORK_CODE fullmatch -> 1 (`work/061/diag_keep.py`). 03 said 1 of 484 on 2026-11-14; the 6 new paths are 063/064 markdown. The cited number matches (RI-001).

## Tests re-run (output)
`python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py`
```
88 passed in 11.22s
```
`python3 -m pytest -q -p no:cacheprovider -rs` (full suite)
```
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
316 passed, 1 skipped in 52.58s
```
`tests/test_safety.py::test_every_py_compiles_on_oldest_python` -> `1 passed` (it ran: python3.11 is at /usr/bin/python3.11; python3.10 is not on PATH).

`python3 scripts/check_handoff.py 064`
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 41
totals line: 41 rows -> 31 as-is, 10 fixed, 0 removed
PASS
```
`python3 scripts/check_pipeline.py` (before 06 was written): exit 0. `061: complete (FULL)`, `063: in progress (FULL: next 06)`, `064: in progress (FULL: next 06)`, `INCOMPLETE: none`, `LOG TIME: none (...048...)`, `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`, `SKIPPED: none`, `RULES BRANCH: none`, `ID CLASH: none`. 061 stays complete.

Mutations: scratch worktree `git worktree add --detach .../scratchpad/i3-064 779a414`, run with `python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py`. Each mutation was restored with `git checkout` inside the worktree, and the worktree was removed afterwards (`git worktree remove --force`; `git worktree list` no longer shows it). The repo working tree was never edited.
- (i) `_is_code` -> `return f.startswith(paths)`: `13 failed, 75 passed`. Failed: test_research_code_rules, all 8 test_work_code_pattern cases, (a) test_research_only_work_py_is_research_code, (b) test_py_added_to_completed_item_is_untracked, (d) test_research_only_branch_work_py_is_branch_skipped, (e) test_research_only_branch_nested_py_is_seen. Same as 05.
- (ii) branch step part back to unfiltered `for f in files[i]]`: `1 failed, 87 passed` (test_branch_unchanged_tip_py_not_counted). Same as 05.
- (iii) `WORK_CODE` -> `r"work/\d{3}/.+\.py.*"`: `3 failed, 85 passed` (test_research_code_rules, `[work/160/diag.py.md-False]`, `[work/160/x.pyc-False]`). Same as 05.
- (iv, my own) the `changed("work/")` term dropped from the branch unit: `2 failed, 86 passed` (fixtures (d) and (e)). The branch half of the rule is pinned as well.

Replay of the original gap (the 061 shape: a RESEARCH ONLY item with 01 02 03, then a later commit adding `work/999/diag.py` with a 03 edit). Run in the same scratch worktree:
```
NEW (779a414):
999: SKIPPED (9b531e0 RESEARCH ONLY: changes work/999/diag.py with no 04-06; needs Scope FULL or "Waived: 04 05 06 (person, <date>: <why>)" on the item's single Waived: line (item 062))
UNTRACKED CHANGE: none
RESEARCH CODE: 999
OLD (779a414^ check_pipeline.py):
999: in progress (RESEARCH ONLY: next 07)
UNTRACKED CHANGE: none
RESEARCH CODE: none
```
The old check passes the shape and the new one flags it. That is the request's "Done looks like".

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (WORK_CODE count re-run: 1 of 490 tracked work/ paths, which matches 03's dated 1 of 484 plus 6 new markdown files; the step-0 count is 0 of 20 units), RI-002 (ESCALATED; no default added; each absent input ends in a defined line: diff-tree failed -> 053 entry, no git -> not checked, missing request.md -> flag, branch diff failed -> gap (l), pinned by a test; the 05 grep hits are comments only), RI-007 (this item; the replay above shows the new flag, and 061 stays complete), RI-008 (test_every_py_compiles_on_oldest_python ran with python3.11: pass), RI-010 (no log line written by me; the orchestrator writes it with --log; `INCOMPLETE: none`, `LOG TIME: none`), RI-011 (the branch unit uses `changed()`, which uses the merge-tree result; no new diff call), RI-012 (the match is a whole-path `fullmatch`, never on commit text; negatives `diag.py.md`, `.pyc`, `work/1600/x.py`, `work/tmp/x.py`; mutation (iii) fails 3). RI-003, RI-004, RI-005, RI-006 and RI-009 are GUARDED and not touched (no calendar, worked example, hand-off number, hand count or branch listing change; check_handoff PASS). Step-3 simulator rule (item 062): not applicable, no simulator or replay of the bot's rule.

## Pipeline line (step 2)
check_pipeline line: `064: awaiting A1 (FULL)`

This is the line after 06 and 07 were written. With 06 alone it was `064: in progress (FULL: next 07)`.

After 06 was written, the run also prints `INCOMPLETE: 064 (no log line for I3)` and exits 1. This is expected: the orchestrator writes the I3 line with `--log` after this file. Re-run after that line exists: the INCOMPLETE entry should be gone, with exit 0.

## Sent back / sent to Audit
Sent to Audit: work/064/07-audit-task.md. Nothing sent back to I1 or I2.
Notes for A1 (not defects): (1) `test_work_code_pattern` repeats constant asserts in every parametrized case. (2) Gaps (e), (k) and (l) stay open by design: other script types under work/ are not checked; a diagnostic's logic in a FULL/FAST item is checked only by I3; a failed branch diff hides branch code. (3) The two .claude/ rule edits need the person's OK in PR review.
