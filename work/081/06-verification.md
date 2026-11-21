# 06 Verification - 081
Verdict: PASS (round 2; earlier rounds: FAIL round 1)
Sent back to: none

Round 2 (2026-11-21) is at the end, under "# Round 2". The round 1 text below is kept as written.

All of my runs, mutations and probes were done in the clean worktree of HEAD d44b687 at /tmp/claude-0/wt081, or in a `git archive HEAD` copy of it in the scratchpad (`.../scratchpad/i3_081_x7q/tree`). Nothing ran in the repo except the final `check_handoff.py` / `check_pipeline.py` reads and the `--log` line. Note: the shared scratchpad was overwritten by another agent while my first mutation pass was running, so I threw that pass away and re-ran every mutation in a uniquely named directory. Every result below comes from the clean pass, with a `cmp` of the restore copy against HEAD after each mutation.

## I1 audit (plan vs research)
- The plan follows 03's map steps 1-13, and the Rule trace maps every 03 step, fact-check correction and Missing-inputs row to a plan line or to a DROPPED line with its reason. The 7 "changes to 03" (FIT WITH CHANGES) each give a reason that is a code fact (`main` joins `late` as a list, `_branch_adds` inherits work/, 5 `changed()` calls, `for b in None`), so they are not unsourced additions. Extra research items 1 and 3 are marked UNVERIFIED by doc, and each is pinned by a fixture ((c2), (d3)), and both fixtures pass.
- **Defect 1 (send-back, I1): planned mutation m1 has no test that can catch it.** Plan L163 says "m1: `continue` back at the blame failure in `late_log_lines` fails (a), (b)". The Rule trace L214 says "Missing input: blame of committed log fails | (b) (real die); m1". Both fixtures make `ls-tree -r HEAD` fail first: in (a) every `_git` returns 128, and in (b) real git 2.43 exits 128 on `ls-tree -r HEAD` with a bad shallow line. So `late_log_lines` returns the ls-tree entry before any blame runs. The blame-failure entry (check_pipeline.py L631) is reached by no test. `grep -rn "blame failed" tests/` gives no hits. My re-run: m1 → `238 passed, 1 deselected` (tests/test_pipeline_check.py). I2 reported the same. That one 03 Missing-inputs row (blame of a committed log fails) is unguarded, which is RI-014's failure mode (a failed git read read as none) at one site.
  Required: I1 plans a fixture in which ls-tree succeeds and only the blame of a committed log file fails. For example: a git repo with a committed `logs/implementation/<date>.md`, and `_patched_git` with `("blame", "--line-porcelain", "--", "logs/implementation/<date>.md"): ("", 128)`, expecting `LOG TIME: logs/implementation/<date>.md (git blame failed; item 081)` and exit 1. m1 is then re-mapped to that test.
- **Defect 2 (send-back, I1, decide and plan): a branch with unrelated history is now a false BRANCH ERROR.** The plan's own Interface rule says "Use raw `_git` only where a non-zero code is a real answer". But it sends `merge-base --all` through `_git_ok`, and `merge-base` exit 1 means "no common ancestor", which is a real answer. I reproduced this with real git (orphan branch `nowork`, README only, pushed):
  ```
  OPEN BRANCHES (not merged into HEAD):
    origin/nowork: items none; merge not checked; last commit 2026-11-21 (0 days)
  BRANCH ERROR: origin/nowork (git diff failed (exit 128))
  BRANCH ERROR: origin/nowork (git merge-base failed (exit 1))
  ```
  Here `git merge-base --all HEAD origin/nowork` gave exit 1 with no output, and `--next-id` gave `041`, exit 0 (correct). The `HEAD...ref` diff fails 128 for the same reason (no merge base). Before 081 this branch printed `items none` and exit 0. Now any unrelated-history remote branch (a docs or pages branch, say) turns the repo check, and `test_repo_pipeline_has_no_skipped_items`, red. This is the loud side, and I2 kept it as planned (05 Deviation 2), so it is not an I2 fault. But it contradicts the plan's Interface and has no test either way. I1 should decide: either merge-base exit 1 means `bases = []` (census reason) plus one explicit "unrelated history" line, or the current loud behaviour, pinned by a test and documented as intended. Plan that decision with a fixture.
- 05 Deviations 3-5: judged acceptable, no send-back.
  - 3: `git rev-list gave no count` instead of `None (item 081)`. This fixes a plan text bug. The result is the same (str, exit 1).
  - 4: equality is stricter than `in` and pins change 4's de-dup.
  - 5: `_root` is taken before `.git/shallow` is written. This is a fixture-order necessity.
  I1 may want to record 3 in the next plan round.

## I2 audit (build vs plan)
- I compared `git diff HEAD~1 HEAD` with plan "Files to create/change" line by line. `_git` (bytes + `os.fsdecode` top; `errors="replace"`), `_git_ok` (exact interface; the reason holds no stderr), `late_log_lines` (ls-tree list entry, uncommitted skip, blame entry), `open_branches` (None/str/list, per-ref `errors`, `changed()` fallback-only de-dup, request shown only if listed, body-show failure skips classify, `behind` walrus), `main_ahead` (for-each-ref exact match), `next_id` (`(id, why)`, `ls-tree -d <ref> -- work/`, `Path(line).name`), `_inbox_gate` 128, and `main` (`--next-id` refusal to stderr / exit 2, `blist`, `MAIN AHEAD` str, OPEN BRANCHES none/str/block/absent, `not checked (see OPEN BRANCHES)`, BRANCH ERROR lines, exit terms) all match the plan. The docstring entries are present. Scope lock held: `_walk`, `_shallow_boundaries`, `untracked_changes`, `research_code`, `real_data_field`, `_item_triggers`, `_open_at` and `uncommitted_steps` have no diff hunks.
- check_handoff.py: `(ref, why)` and the `not checked (open branches: <why>)` failure match plan Files 2.
- a1-auditor.md: `--word-diff=porcelain` shows 0 removed words and exactly the 2 added runs the plan names (L23 `BRANCH ERROR:`, L29 `--next-id` refusal). This is a RULES change, so it needs the person's OK in PR review.
- Tests: the 13 planned tests plus the renamed (e) are present. The census test passes on the built file (41 calls).
- Connectivity, re-done: `_git_ok` has 13 call sites (census test green). The `errors` list goes to the BRANCH ERROR lines and exit 1 (the orphan repro above shows it printed). The `main_ahead` str goes to the MAIN AHEAD line and exit 1 (fixtures a/b). The `next_id` why goes to the stderr refusal and exit 2 (fixture a). The `open_branches` str goes to OPEN BRANCHES plus 3 `not checked` lines, exit 1, and check_handoff's failure (h2). No orphan code, no TODO.
- I2 did not add the unplanned blame test, which was correct per its rules, and reported m1 instead. No I2 fault found.

## Tests re-run (output)
Full suite, worktree /tmp/claude-0/wt081 at d44b687, `python3 -m pytest -q`:
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 602 passed, 1 skipped in 78.91s (0:01:18)
```
This is the same as 05. The 1 failure is the known pre-existing one (083 INCOMPLETE under PR #33 rules; 084 fixes it).

Oldest-Python compile (items 027/032): `python3 -m pytest -q tests/test_safety.py -k oldest` → `1 passed, 8 deselected`. python3.11 is on PATH, so it ran and did not skip. `python3.11 -m py_compile scripts/check_pipeline.py scripts/check_handoff.py tests/test_pipeline_check.py` → exit 0.

`python3 scripts/check_handoff.py 081` (worktree):
```
sources count (unique URLs in 01-research.md): 10
fact-check rows: 53
totals line: 53 rows -> 38 as-is, 14 fixed, 1 removed
PASS
```
exit 0.

Mutations (scratch copy `.../scratchpad/i3_081_x7q/tree`, `python3 -m pytest -q tests/test_pipeline_check.py --deselect ...::test_repo_pipeline_has_no_skipped_items`; scratch baseline `238 passed`):
```
m1   (blame failure -> silent continue)      238 passed                 <- SURVIVES (Defect 1)
m1b  (ls-tree why -> tree = "")              3 failed: (a), (b), (c)
m2   (branch -r failure -> return [])        3 failed: (a), (b), (c)
m3   (next_id failure -> treated as [])      2 failed: (a), (b)
m4   (main_ahead failure -> 0)               1 failed: (a)
m4b  (exact refname filter dropped)          1 failed: (d3)
m5   (errors="replace" dropped)              1 failed: (c)
m6   (top run back to text/utf-8)            1 failed: (c2)
m7   (changed() [] without recording)        1 failed: (e)
m8   (_inbox_gate 128 branch disabled)       2 failed: (a), (g)
m9   (extra _git in main_ahead)              1 failed: census
m10  (classify kept after body failure)      1 failed: (f)
restored                                     238 passed
```
RI-002 step (put back a removed default): m2 restores the original `return []` for a failed `git branch -r`, and 3 tests fail. m3 restores the `[]` for a failed `next_id` branch read, and 2 tests fail.

Guardrail would have caught the original error: A1's malformed-shallow repro (a bad `.git/shallow` line, `OPEN BRANCHES` silent, `--next-id` printing `080`) is fixture (b). With the pre-081 behaviour put back (m2 / m3), (b) fails. With the build, (b) passes: every git-reading line is present and none ends in `: none`, exit 1, and `--next-id` gives `(2, "")`. The exception is the blame site (Defect 1).

RI-012 (text classification): the build classifies nothing by matching git's output text. `why == "no git"` and `why not in errors` compare reason strings the script builds itself, by exact equality or list membership. No substring test of free text was added, so no negative test is needed.

## Real-data effect (diff_reports output, pasted)
not required (.claude/agents/a1-auditor.md, scripts/check_handoff.py, scripts/check_pipeline.py, tests/test_pipeline_check.py; plus logs/implementation/2026-11-21.md and work/081/05-build-report.md). No ccbot/realtest.py, TRIGGER or TRIGGER_DIRS file changes.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-010, RI-014, RI-008, RI-009, RI-011, RI-012
- RI-001 (ESCALATED): I re-ran the plan's feasibility tests, and they pass on the build: (d1) 0 of 1 log files blamed → `LOG TIME: none`, (d2) 041 / 100, (d3) no MAIN AHEAD line, (g) 128 loud / 129 unchanged. The numbers 05 cites match the tests. No 001 rule text changes.
- RI-002 (GUARDED): the removed defaults put back (m2, m3) fail tests. One silent path remains testable-but-untested: the blame failure (Defect 1).
- RI-010 (ESCALATED): this 06 is followed by a `--log` line written by the script. Nothing is typed by hand.
- RI-014 (OPEN, this item): the guardrail is extended and 11 of the 12 mutations fail a test. It is not complete until m1 has a test (Defect 1). Status line, unchanged from 05 (step 13): "RI-014: guardrail extended (081); GUARDED when 079 and 081 are merged and m2 fails fixture (b) on main." m2 fails (b) on this build (above).
- RI-008: the oldest-Python compile test passed (python3.11), and py_compile gave exit 0.
- RI-009: `--next-id` refuses with exit 2 and empty stdout (fixture a/b). The orphan branch gives the correct 041.
- RI-011: the merge-tree path and its anchor lines are unchanged (no diff in those lines).
- RI-012: checked above. No text-matching classification was added.

## Pipeline line (step 2)
check_pipeline line: `081: I3 FAIL (FULL; sent back to I1, needs a later PASS round in 06 (item 071))` (run in /home/claude/cover-calls after this 06 and the I3 `--log` line; exit 1, which is expected in a FAIL round)

## Sent back / sent to Audit
Sent back to I1 (no 07 written):
1. Plan a test that reaches the blame-failure entry in `late_log_lines` (ls-tree succeeds, the blame of a committed log fails → `LOG TIME: <file> (git blame failed; item 081)`, exit 1), and re-map m1 and Rule-trace row "blame of committed log fails" to it. I2 then adds it, and m1 must fail it.
2. Decide how a branch with no common ancestor is reported. `merge-base --all` exit 1 and the `HEAD...ref` exit 128 it causes are currently BRANCH ERRORs (exit 1), which contradicts the plan's Interface rule for real-answer exit codes. Either make it a real answer with a census reason and its own line, or keep it loud on purpose. In both cases pin it with a fixture (the orphan `nowork` repro above).
3. Optional: fold 05 Deviation 3 (the `git rev-list gave no count` text) into the plan.

# Round 2 (2026-11-21, I3)
Verdict: PASS (round 2; earlier rounds: FAIL round 1)
Sent back to: none

Build verified: commit e5297e7 on daily-fixes/2026-11-20, checked out clean in the worktree /tmp/claude-0/wt081b (`git status --porcelain` empty). The repo HEAD has since moved to f562142, which holds 084 commits only. `git diff --stat e5297e7 HEAD -- work/081 scripts tests` is empty, so these results apply to the current tree. Mutations ran in a `git archive` copy, `/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3-081-r2-1795222262-2240/tree`. The orphan repros ran in `/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3-081-r2-orph2-1795222688-22824`. Nothing ran in /home/claude/cover-calls except check_pipeline.py (the line below) and the `--log` line.

## I1 audit (plan vs research), round 2
- Both round-1 send-backs are answered in 04 "## Round 2", and so is the optional one.
  - Defect 1 → R2-a. In that test, ls-tree succeeds and 1 of the 2 committed logs fails blame. m1 is re-mapped to it, and so is Rule-trace row "blame of committed log fails".
  - Defect 2 → an explicit decision: merge-base exit 1 is a real answer. The plan gives reasons against both alternatives. Quiet/loud are split by a successful ls-tree of the checked paths, pinned by R2-b, R2-c and R2-d.
  - Optional 3 → `main_ahead` note plus R2-e.
- Sources for the new claims:
  - The merge-base exit-1 meaning cites git's builtin/merge-base.c (`show_merge_base`). I measured it myself on git 2.43: orphan `nowork` → `git merge-base --all HEAD origin/nowork` exit 1, no output.
  - The merge-tree claim cites git-merge-tree docs.
  - Extra research item 3 (unrelated branch that carries work/) is a code-path fact, pinned by R2-c. It is not an unsourced rule.
- No RULES file is in round 2, so there is no new text for the person. The round-1 a1-auditor.md change still needs the person's OK in PR review.
- No unsourced additions found.

## I2 audit (build vs plan), round 2
I compared `git diff HEAD~1 HEAD` (e5297e7) line by line with 04 Round 2 "Files to change". 2 code files changed, as planned.
- `open_branches`:
  - `when`/`last` are moved up unchanged (removed below, added after the `behind` skip).
  - Raw `mb = _git("merge-base", "--all", "HEAD", ref)`, then the `mb[1] == 1` block. This is the exact plan text: ls-tree of `work/`, RECURRING, `*RULE_PATHS` and `*RESEARCH_CODE_PATHS`, then the errors expression and the `unrelated: True` dict, then `continue`.
  - The round-1 `_git_ok` merge-base block is replaced by the planned `mb` block, with the same texts.
  - The normal dict has `"unrelated": False`. The docstring has the `unrelated` entry.
- `main`: `age` is moved to the top of the loop, and `b.get("unrelated")` prints the not-scanned line and continues. BRANCH ERROR and the exit term have no diff.
- The module docstring paragraph and the known-gap sentence are present. `late_log_lines` and `main_ahead` have no diff.
- The 3 anchor lines are absent from the diff, and each occurs once in the file. RI-011 holds.
- Tests: `GIT_CENSUS` open_branches `_git` 4 → 5 with the merge-base reason, `_git_ok` stays 5 with the new reason, and the total is 47. The `_orphan` helper and R2-a to R2-e match the plan's assertions one for one. (d2) is unchanged.
- 05 says "no deviations", and I found none.
- Connectivity, re-done:
  - `unrelated` is read by `main`.
  - The unrelated `errors` reach BRANCH ERROR and exit 1. My oldwork repro below shows the line.
  - The ls-tree failure reaches BRANCH ERROR (R2-b absent case).
  - merge-base 128 still scans the branch and adds the error (R2-d).
  - `_orphan` is used by R2-b and R2-c.
  - No orphan code, no TODO.

## Tests re-run (output), round 2
Full suite, worktree /tmp/claude-0/wt081b at e5297e7, `python3 -m pytest -q`:
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated - Asserti...
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
4 failed, 642 passed, 1 skipped in 86.15s (0:01:26)
```
Same as 05 round 2, and 05's base run has the same 4 failures. None is 081's:
- Three come from 086's not-computable text (086 is being fixed).
- `test_repo_pipeline_has_no_skipped_items` fails while 081/084/086 are open.

New and pinned tests: `-k "blame_failure_of_committed or unrelated_branch or merge_base_die or non_digit_count or criss_cross or census or unrelated_root"` → `8 passed`.

Oldest Python (items 027/032): `tests/test_safety.py -k oldest` → `1 passed, 8 deselected`. python3.11 is on PATH (python3.10 is not), so the test ran and did not skip. `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` → OK.

`python3 scripts/check_handoff.py 081` (worktree), exit 0:
```
sources count (unique URLs in 01-research.md): 10
fact-check rows: 53
totals line: 53 rows -> 38 as-is, 14 fixed, 1 removed
PASS
```

Mutations. Scratch tree `/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3-081-r2-1795222262-2240/tree`. Command: `python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py`, with the 4 known failures deselected. Baseline: `277 passed, 1 skipped, 4 deselected`. Each mutation is asserted to match exactly once, and after each one the file was restored and `cmp` against the worktree file was OK.
```
m1   blame failure -> bare continue                 1 failed: test_blame_failure_of_committed_log_is_an_entry
m11  mb[1] == 1 branch disabled (if False)          2 failed: test_unrelated_branch_without_checked_paths_is_not_an_error, test_unrelated_branch_with_work_is_branch_error
m12  unrelated errors forced to []                  2 failed: ..._with_work_is_branch_error (named), ..._without_checked_paths_... (absent case; my m12 also zeroes the ls-tree reason)
m13  mb[1] == 1 widened to mb[1] != 0               1 failed: test_merge_base_die_is_branch_error
m14  unrelated ls-tree why ignored ([] if why)      1 failed: test_unrelated_branch_without_checked_paths_is_not_an_error
m15  main_ahead back to f"{why} (item 081)"         1 failed: test_main_ahead_non_digit_count
round-1 spot checks on the round-2 build:
m2   branch -r failure -> return []                 3 failed: (a) test_all_git_fails_no_line_says_none, (b) test_malformed_shallow_real_git_nothing_none, (c) test_non_utf8_shallow_line_no_traceback  (same as round 1)
m3   next_id branch-read failure ignored            2 failed: (a), (b)  (same as round 1)
m5   errors="replace" -> "strict"                   1 failed: (c)  (same as round 1)
m7   changed() fallback [] without recording        1 failed: test_branch_diff_failure_is_branch_error  (same as round 1)
m9   extra _git("status") before merge-base         1 failed: test_git_call_census
```
RI-002 step (put back a removed default): m1 puts back the silent `continue` at the blame site, the one site that was unguarded in round 1, and 1 test fails. m2 and m3 put back round 1's `return []` and `[]` defaults, and 3 and 2 tests fail.

Guardrail would have caught the original error: A1's evidence (all git reads fail → `LOG TIME: none`, OPEN BRANCHES missing, `--next-id` 080) is fixtures (a)/(b). With the pre-081 defaults put back (m2/m3) they fail, and on the build they pass. Round 1's remaining hole, the blame site, is now closed: m1 fails R2-a, where pre-081 code gives `[]` / `LOG TIME: none`.

Orphan-branch repro, real git 2.43. Bare origin with only e5297e7 as `main`, a clone checked out at e5297e7, dir `/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3-081-r2-orph2-1795222688-22824`:
- No other branch: exit 1 (from open items 081/084/086), `OPEN BRANCHES: none`.
- With `nowork` (README only; `merge-base --all` exit 1). Exit 1, the same as before (the items). No BRANCH ERROR. The whole `diff` against the no-branch run is:
  ```
  90c90,91
  < OPEN BRANCHES: none
  ---
  > OPEN BRANCHES (not merged into HEAD):
  >   origin/nowork: no common history with HEAD; not scanned (item 081); last commit 2026-11-21 (0 days)
  ```
  Round 1 printed `BRANCH ERROR: origin/nowork (git diff failed (exit 128))` and `(git merge-base failed (exit 1))` here. Both are gone.
- Adding orphan `oldwork` with `work/150/request.md`. The whole diff against the nowork run:
  ```
  91a92
  >   origin/oldwork: no common history with HEAD; not scanned (item 081); last commit 2026-11-21 (0 days)
  93a95
  > BRANCH ERROR: origin/oldwork (no common history with HEAD; 1 file(s) on checked paths (first: work/150/request.md) not checked (item 081))
  ```
  `--next-id` → `151`, exit 0 (RI-009: the orphan's ID is counted).

Extra probe (shallow clone; not a defect, passed to Audit). I made a toy repo with `fix` branched from main~2 and carrying work/150, then cloned it with `--depth 1 --no-single-branch`. In that clone `merge-base --all HEAD origin/fix` exits 1, though the branches share history. The checker prints `origin/fix: no common history with HEAD; not scanned` plus `BRANCH ERROR: origin/fix (no common history with HEAD; 1 file(s) on checked paths ... )`, exit 1, and RULE NOT SEEN / UNTRACKED CHANGE say "shallow clone; run git fetch --unshallow". So it stays loud. Round 1 was loud here too. The wording "no common history" is not accurate for a shallow clone, and a branch with no checked paths would be quiet. Such a branch holds nothing the scan reads, so nothing is hidden.

RI-012 (text classification): "unrelated" is decided by `mb[1] == 1`, git's exit code, never by stdout or stderr text. R2-d plus m13 pin that only 1 counts. No substring match on free text was added, so no negative test is needed (item 059 does not apply).
Item 062 (simulator): not applicable, no pickers are involved. 001 rule text: no rule the person follows changed.

## Real-data effect (diff_reports output, pasted)
not required (scripts/check_pipeline.py, tests/test_pipeline_check.py; plus logs/implementation/2026-11-21.md and work/081/05-build-report.md). No ccbot/realtest.py or TRIGGER/TRIGGER_DIRS file changed in round 1 or round 2.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-008, RI-009, RI-010, RI-011, RI-012, RI-014
- RI-001 (ESCALATED): I re-ran each round-2 feasibility count, and the numbers in 05 match:
  - blame: 1 of 2 → 1 entry (R2-a exact list)
  - nowork: 0 of 1 files on checked paths → quiet (my repro)
  - oldwork: 1 of 1 → loud (my repro)
  - merge-base 128 → error, branch still scanned (R2-d)
  - census: 47 (passes)
- RI-002 (GUARDED): the restored defaults (m1, m2, m3) fail tests. An unrelated branch is quiet only after a successful ls-tree. A failed ls-tree is an error (m14 fails R2-b's absent case).
- RI-008: oldest-Python test ran (python3.11) and passed. py_compile OK.
- RI-009 (GUARDED): `--next-id` counts an orphan's work/ ID (151, R2-c and my repro).
- RI-010 (ESCALATED; not 081's item): this 06 is written, then the I3 line via `--log`. Nothing is typed by hand.
- RI-011 (GUARDED): the anchor lines are not in the diff and occur once each. Criss-cross test passes.
- RI-012 (GUARDED): exit-code classification only (above).
- RI-014 (OPEN, this item): all round-2 and spot round-1 mutations fail their named tests. Round 1's unguarded blame site is closed. Status line (05, unchanged): "RI-014: guardrail extended (081); GUARDED when 079 and 081 are merged and m2 fails fixture (b) on main." m2 fails (b) on this build.

## Pipeline line (step 2)
check_pipeline line: `081: awaiting A1 (FULL)`. I ran it in /home/claude/cover-calls after this 06, 07 and the I3 `--log` line (`01:00 | I3 | 081 | PASS | sent to audit: yes`). It is not SKIPPED or INCOMPLETE, and `AWAITING A1: 081`. The script exits 1 because of other items (084/086 lines, not 081's).

## Sent back / sent to Audit
Sent back to: none. PASS, sent to Audit: work/081/07-audit-task.md.
