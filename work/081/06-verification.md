# 06 Verification - 081
Verdict: FAIL (round 1; earlier rounds: none)
Sent back to: I1

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
