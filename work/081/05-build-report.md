# 05 Build report - 081
Base: daily-fixes/2026-11-20 at d29efba (HEAD when the build started; the plan was read on ca9db5f's tree, and `git diff --stat ca9db5f d29efba -- scripts/check_pipeline.py scripts/check_handoff.py tests/test_pipeline_check.py .claude/agents/a1-auditor.md` is empty, so the plan's line numbers held). Not committed (orchestrator commits). No brokerage connection; every fixture is a temp git repo.

File counts (commands, item 012):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → `0`
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → `4`

```
 .claude/agents/a1-auditor.md |   4 +-
 scripts/check_handoff.py     |  25 +++--
 scripts/check_pipeline.py    | 231 +++++++++++++++++++++++++++++-----------
 tests/test_pipeline_check.py | 248 ++++++++++++++++++++++++++++++++++++++++++-
 4 files changed, 436 insertions(+), 72 deletions(-)
```

## Changes made (file: what changed)
- `scripts/check_pipeline.py`
  - `import os`.
  - `_git`: the `--show-toplevel` run reads bytes and compares `Path(os.fsdecode(top.stdout.strip())).resolve()` with `Path.cwd().resolve()`. The main run adds `errors="replace"`. The return contract is unchanged, and the docstring gains the decode sentence (item 081).
  - New `_git_ok(*args)` directly after `_git`, with exactly the plan's interface: `(stdout, None)`, `(None, "no git")`, or `(stdout, "git <args[0]> failed (exit <code>)")`. The reason never contains stderr.
  - `late_log_lines`: the `is None` probe is kept. `_git_ok("ls-tree", "-r", "--name-only", "HEAD", "--", "logs/research/", "logs/implementation/")` failing returns `["git ls-tree HEAD failed (item 081)"]` (change 1). A file not in that list is skipped as uncommitted. Blame goes through `_git_ok`, and a failure appends `<file> (git blame failed; item 081)`.
  - `open_branches`:
    - `git branch` returns None on "no git" and the reason string on any other failure.
    - `behind = isinstance(a := main_ahead(), int) and a > 0`.
    - Per-ref `errors = []`. `changed()` uses `_git_ok` for both diffs. Only a fallback failure is recorded, once per distinct reason (change 4).
    - `ls-tree`, `merge-base --all` and the request `show` go through `_git_ok`. The request is shown only when `"request.md" in files[item]`.
    - A failed body `show` records the error, and that item is not classified (change 3).
    - `is-ancestor`, `merge-tree`, `cat-file -e` and `log -1` stay on `_git`.
    - The dict gains `"errors"`. The three probe anchor lines are byte-identical (`grep -cxF` = 1 each).
  - `main_ahead`: `for-each-ref --format=%(refname) %(objectname) refs/remotes/origin/main`, then an exact refname match, then `rev-list --count HEAD..<sha>`. "no git" or no exact ref gives 0. Any other failure gives `"<why> (item 081)"`. A non-digit count with exit 0 gives `"git rev-list gave no count (item 081)"` (see Deviations).
  - `next_id` returns `(id, None)` or `(None, why)`. It reads `ls-tree -d --name-only <ref> -- work/` and takes `Path(line).name`.
  - `_inbox_gate`: `--is-shallow-repository` exit 128 returns `("<file> (git rev-parse failed (exit 128); item 081)", True)`.
  - `main`:
    - `--next-id` refusal: message to stderr, empty stdout, exit 2.
    - `blist` is used for IN PR, RULES BRANCH, ID CLASH, BRANCH SKIPPED and BRANCH FAIL.
    - `MAIN AHEAD: <error>` is printed for a str.
    - `OPEN BRANCHES:` prints none (`[]`), `<why> (item 081)` (str), the block (list), or no line (None).
    - When the branch list failed, IN PR, RULES BRANCH and ID CLASH say `not checked (see OPEN BRANCHES)`.
    - `BRANCH ERROR: <ref> (<why>)` lines follow BRANCH FAIL.
    - Exit is 1 also for a str branch list, any branch error, or a str ahead.
  - Docstring:
    - BRANCH FAIL's last sentence.
    - A new BRANCH ERROR entry, covering the OPEN BRANCHES none/absent/error states.
    - LOG TIME item-081 paragraph.
    - MAIN AHEAD exact ref and error line.
    - Gap (l) replaced by "a failed branch git diff is a BRANCH ERROR (item 081)".
    - `--next-id` refusal and unborn-HEAD note.
    - Known gap: `_shallow_boundaries` returns "full" when both reads fail, so the squash/rebase text is printed.
    - INBOX: exit 128.
- `scripts/check_handoff.py`: `_branch_with_handoff` returns `(ref, why)`. None gives `(None, None)`, and a str gives `(None, found)`. `check_all` prints `<ID>: not checked (open branches: <why>)` and appends that item to `failed`. The docstring is updated.
- `tests/test_pipeline_check.py`:
  - `test_branch_diff_failure_hides_code_gap_l` is renamed `test_branch_diff_failure_is_branch_error`. Its docstring says the change is on purpose. It asserts `res[0]["errors"] == ["git diff failed (exit 1)"]` (listed once across the 5 `changed()` calls), then via `main` it checks for `BRANCH ERROR: origin/res (git diff failed (exit 1))` and exit 1.
  - New: `GIT_LINES`, `GIT_CENSUS`, `_git_lines`, and 13 tests: `test_git_ok_contract`, `test_git_call_census`, (a) `test_all_git_fails_no_line_says_none`, (b) `test_malformed_shallow_real_git_nothing_none`, (c) `test_non_utf8_shallow_line_no_traceback`, (c2) `test_non_utf8_repo_path_is_still_git`, (d1) `test_uncommitted_log_file_is_skipped`, (d2) `test_next_id_orphan_branch_without_work`, (d3) `test_main_ahead_exact_ref_only`, (f) `test_branch_show_failure_skips_classify`, (g) `test_inbox_flag_die_is_loud`, (h1) `test_open_branches_none_line`, and (h2) `test_check_handoff_open_branches_states`.
- `.claude/agents/a1-auditor.md` (RULES: needs the person's OK in PR review). `git diff --word-diff=porcelain` shows 0 removed words and exactly 2 added runs:
  - L23: `every \`BRANCH ERROR:\` line (git could not read that branch; item 081),`
  - L29: `If \`--next-id\` refuses, fix the clone and re-run; never pick an ID by hand (item 081).`

## Connectivity check
- [x] Every new function/rule is used. `_git_ok` has 13 call sites (census). `errors` → `branch_errors` → `BRANCH ERROR:` lines and the exit code. The `main_ahead` str goes to the `MAIN AHEAD:` line and the exit code. The `next_id` why goes to the stderr refusal and exit 2. The `open_branches` str goes to `OPEN BRANCHES:` plus 3 `not checked` lines, the exit code, and check_handoff's `not checked` line, which counts as a failure. `GIT_CENSUS` is read by `test_git_call_census`. The 2 a1-auditor.md sentences name the new outputs (`BRANCH ERROR:`, the `--next-id` refusal).
- [x] Every input has a source, and every output has a consumer. All inputs are git outputs through `_git`/`_git_ok`. Every new output is a printed line read by A1 (a1-auditor L23/L29), and the exit codes are read by `test_repo_pipeline_has_no_skipped_items` and A1.
- [x] Every branch ends in a defined result:
  - `_git_ok` has 3 outcomes.
  - `open_branches`: None / str / list, with per-ref errors.
  - `changed()`: tree ok → list; fallback ok → list; fallback fail → error + `[]`.
  - Body show fail → error, no classify.
  - `main_ahead`: no git → 0; no exact ref → 0 (for-each-ref succeeded: a real answer); read fail → str; non-digit count → str.
  - `next_id`: no git → HEAD only; fail → refusal.
  - `_inbox_gate` 128 → loud, other codes → today's path.
  - `late_log_lines`: no git → None; ls-tree fail → entry; uncommitted → skip; blame fail → entry.
  - check_handoff: None / str / ref.
- [x] No leftover TODOs or unused files. `grep -n "TODO" scripts/check_pipeline.py scripts/check_handoff.py` → no hits. No new files.
- Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` → 38 hits). All are pre-existing: `git diff --stat -- ccbot/` is empty, and this item changes no ccbot/ file. I ran the same patterns (plus `else []`, `return 0`, `default=`) on the added lines of scripts/. Each hit and its reason:
  - `listing.splitlines() if why is None else []`: the error is already in `errors` → BRANCH ERROR, exit 1. The `[]` only stops the loop.
  - `bases.split() if why is None else []`: same. The clash test is skipped and the error is printed.
  - `theirs is not None and ...` (2): None means request.md is absent at the tip (a real answer) or the show failed (in `errors`). Never a pass.
  - `main_ahead` `return 0` (2): "no git" (benign, documented) and "no exact refs/remotes/origin/main" after a successful for-each-ref (a real answer). Failures return a str.
  - `next_id` `out.split() if why is None else []`: only reached on "no git" (HEAD-only count, as documented). Other reasons refuse.
  - `max(ids, default=0)`: pre-existing. IDs come only from successful reads.
  - `blist = ... else []`: None prints no branch lines (no git). A str prints the error and `not checked` lines, exit 1.
  - The `... else 0` in the exit expression: the exit code itself.
- Patterns the grep can't see (014): no dataclass is added. The new `>` tests are `a > 0` after `isinstance(a, int)` (in `open_branches`) and `ahead > 0` after the `isinstance(ahead, str)` branch, so ints only. No NaN is possible.
- Feasibility tests the plan names (real numbers):
  - (d1): the log file is not in HEAD's tree, so 0 of 1 log files are blamed → `LOG TIME: none`, exit 0.
  - (d2): orphan branch with 0 work IDs → `--next-id` = `(0, "041\n")`. Adding b099 → `(0, "100\n")`.
  - (d3): 0 of 1 refs under `refs/remotes/origin/main*` match exactly → no MAIN AHEAD line. `origin/main/x` is listed as an open branch.
  - (g): 128 → loud; `test_shallow_flag_unknown_no_file_is_full` (129) passes unchanged.
  - Census: 41 calls (`_git` 28, `_git_ok` 13), recounted by AST on the built file, the same as the plan's table, entry for entry.

## Recurring issues checked (item 013)
- RI-001 (ESCALATED): each disambiguation count is computed and pinned by a test. The numbers are in Feasibility above. Nothing says "always".
- RI-010 (ESCALATED): this 05 is followed by a `--log` line. Nothing is typed by hand. No log rule changed.
- RI-014 (OPEN, this item): the guardrail is extended. m2–m10 each fail their named test. m1 survives (see Deviations; sent back to I1).
- RI-002 (GUARDED): no failed git read becomes `none`, `0`, `[]` or an ID. Fixtures (a), (b) and (c) show every git-reading line present and none ending `: none`.
- RI-009 (GUARDED): `--next-id` refuses (exit 2, empty stdout) and never guesses. Probe RI-009-037 holds on the build (below).
- RI-008: `python3.11 -m py_compile scripts/check_pipeline.py scripts/check_handoff.py` → exit 0.
- RI-011: the merge-tree path and its anchor are unchanged. Probe RI-011-052 holds on the build.

RI-014: guardrail extended (081); GUARDED when 079 and 081 are merged and m2 fails fixture (b) on main.

## Test output (pasted, not summarized)
Base d29efba, before any edit: `python3 -m pytest -q` →
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 589 passed, 1 skipped in 76.31s (0:01:16)
```
Build (working tree), `python3 -m pytest -q` →
```
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 602 passed, 1 skipped in 74.44s (0:01:14)
```
The one failure is pre-existing and not this build's: 083 is INCOMPLETE under PR #33's rules (I2 log format; 06 has no `Sent back to: none`). Item 084 fixes it. 081, 082, 084 and 086 are in progress. The failing lines are the same at base and build. The real-repo whole-output compare is below: `diff` exit 0.

New tests: 602 − 589 = 13 (the renamed gap-(l) test is not new).

Real repo, `python3 scripts/check_pipeline.py`. Base = `git show d29efba:scripts/check_pipeline.py` run from the repo root. Build = working tree. `diff base_out.txt build_out.txt` → no output, exit 0 (base exit 1, build exit 1). The non-complete lines of the build:
```
080: awaiting A1 (FULL)
081: in progress (FULL: next 05)
082: in progress (FULL: next 05)
084: in progress (FULL: next 05)
086: in progress (FULL: next 05)
STUCK: none
AWAITING A1: 080
IN PR: none
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-20 (0 days)
RULES BRANCH: none
ID CLASH: none
I3 FAIL: none
A1 FAIL: none
INCOMPLETE: 083 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed>"; 06 Verdict is PASS but has no 'Sent back to: none' line (item 071))
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
RESEARCH CODE: none
REAL-DATA FIELD: none
UNCOMMITTED STEP: none
ORPHAN LOG: none
INBOX: not checked (2026-11-20.md added in 8f1e9f7; its templates/daily-audit.md has no ## Inbox)
SKIPPED: none
```
So there is an `OPEN BRANCHES` block, no `BRANCH ERROR:`, and the exit is unchanged. `--next-id`: base `087`, build `087`, exit 0. `check_handoff.py --all`: base and build outputs are identical (`diff` exit 0), both exit 0, last line `no new failures`.

Fixture lines (printed by a scratch script that imports the test helpers; git-reading lines only):
```
--- (a) exit 1
LOG TIME: git ls-tree HEAD failed (item 081)
OPEN BRANCHES: git branch failed (exit 128) (item 081)
IN PR: not checked (see OPEN BRANCHES)
RULES BRANCH: not checked (see OPEN BRANCHES)
ID CLASH: not checked (see OPEN BRANCHES)
MAIN AHEAD: git for-each-ref failed (exit 128) (item 081)
UNTRACKED CHANGE: cutoff 694bf4d not in HEAD's history (squash/rebase or wrong SHA)
RESEARCH CODE: not checked (see UNTRACKED CHANGE)
REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)
UNCOMMITTED STEP: git ls-tree HEAD failed (item 077)
INBOX: 2026-11-20.md (git rev-parse failed (exit 128); item 081)
(a) --next-id exit 2 stdout='' stderr=--next-id refused: git branch failed (exit 128); not counting open branches would risk an ID clash (item 037). Fix the clone (git fetch origin) and re-run.
--- (b) exit 1
LOG TIME: git ls-tree HEAD failed (item 081)
OPEN BRANCHES: git branch failed (exit 128) (item 081)
IN PR: not checked (see OPEN BRANCHES)
RULES BRANCH: not checked (see OPEN BRANCHES)
ID CLASH: not checked (see OPEN BRANCHES)
MAIN AHEAD: git rev-list failed (exit 128) (item 081)
UNTRACKED CHANGE: not checked (shallow clone; run git fetch --unshallow) (cutoff 663f37d from --untracked-from)
RESEARCH CODE: not checked (see UNTRACKED CHANGE)
REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)
UNCOMMITTED STEP: git ls-tree HEAD failed (item 077)
INBOX: 2026-11-20.md (git rev-parse failed (exit 128); item 081)
(b) --next-id (2, '')
--- (c) exit 1 traceback=False
LOG TIME: git ls-tree HEAD failed (item 081)
OPEN BRANCHES: git branch failed (exit 128) (item 081)
IN PR: not checked (see OPEN BRANCHES)
RULES BRANCH: not checked (see OPEN BRANCHES)
ID CLASH: not checked (see OPEN BRANCHES)
UNTRACKED CHANGE: cutoff e4c7780 not in HEAD's history (squash/rebase or wrong SHA) (cutoff e4c7780 from --untracked-from)
RESEARCH CODE: not checked (see UNTRACKED CHANGE)
REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)
UNCOMMITTED STEP: git ls-tree HEAD failed (item 077)
INBOX: not checked (no daily report)
--- (c2) exit 0 traceback=False
LOG TIME: none
OPEN BRANCHES: none
IN PR: none
RULES BRANCH: none
ID CLASH: none
UNTRACKED CHANGE: none (cutoff 9023528 from --untracked-from)
RESEARCH CODE: none
REAL-DATA FIELD: none
UNCOMMITTED STEP: none
INBOX: not checked (no daily report)
```
The (c) UNTRACKED CHANGE text is the squash/rebase wording. This is the documented known gap: `_shallow_boundaries` returns "full" when its reads fail. The reason is wrong, but the exit is still 1. The same wording appears in (a). In (c) there is no MAIN AHEAD line because the repo has no origin/main and for-each-ref succeeds with a bad shallow line (a real 0). Real git 2.43.0 with a `zz` shallow line, by exit code:
- exit 0: `rev-parse --show-toplevel`, `rev-parse HEAD`, `for-each-ref`;
- exit 128: `ls-tree -r HEAD`, `branch -r --no-merged HEAD`, `blame`, `rev-parse --is-shallow-repository`.

Mutations (scratch copy `cp -r scripts tests` to the scratchpad, never the repo; `python3 -m pytest -q <named test>`):
```
m1 -> (a) test_all_git_fails_no_line_says_none: 1 passed in 0.15s
m1 -> (b) test_malformed_shallow_real_git_nothing_none: 1 passed in 0.36s
m1b -> (a) test_all_git_fails_no_line_says_none: 1 failed in 0.20s
m2 -> (a) test_all_git_fails_no_line_says_none: 1 failed in 0.09s
m2 -> (b) test_malformed_shallow_real_git_nothing_none: 1 failed in 0.32s
m2 -> (h1) test_open_branches_none_line: 1 passed in 0.18s
m3 -> (a) test_all_git_fails_no_line_says_none: 1 failed in 0.10s
m3 -> (b) test_malformed_shallow_real_git_nothing_none: 1 failed in 0.37s
m4 -> (a) test_all_git_fails_no_line_says_none: 1 failed in 0.10s
m4b -> (d3) test_main_ahead_exact_ref_only: 1 failed in 0.31s
m5 -> (c) test_non_utf8_shallow_line_no_traceback: 1 failed in 0.16s
m6 -> (c2) test_non_utf8_repo_path_is_still_git: 1 failed in 0.16s
m7 -> (e) test_branch_diff_failure_is_branch_error: 1 failed in 0.25s
m8 -> (a) test_all_git_fails_no_line_says_none: 1 failed in 0.10s
m8 -> (g) test_inbox_flag_die_is_loud: 1 failed in 0.11s
m9 -> (census) test_git_call_census: 1 failed in 0.08s
m10 -> (f) test_branch_show_failure_skips_classify: 1 failed in 0.61s
restored: 10 passed in 1.73s
```
(h1 staying green under m2 is the plan's control. m1 surviving is a plan defect: see Deviations.)

Checks:
- `python3.11 -m py_compile scripts/check_pipeline.py scripts/check_handoff.py` → exit 0.
- Anchors: `grep -cxF` of `                clashes.append(item)`, `        rules = changed(*RULE_PATHS)` and `        tree = merge[0].split()[0] if conflicts is not None and merge[0].strip() else None` → 1, 1, 1.
- `probe_guardrails.py --ref HEAD`: I may not commit in the repo, so I ran it with `--repo <scratch clone>` on a scratch commit 6d52dca (d29efba + these 4 files). Result: `TOTAL: 9 probes, 5 hold, 0 not held, 0 anchor missing, 4 error; 129.5 s`. The same clone at base: `--ref d29efba` → `TOTAL: 9 probes, 5 hold, 0 not held, 0 anchor missing, 4 error; 129.6 s`. The 4 ERRORs are pre-existing in both: the tests/test_pipeline_check.py baseline has the 083 failure (`baseline ... 1 failed, 238 passed` build / `1 failed, 225 passed` base), so the 4 check_pipeline probes are not run.
- So I applied those 4 probes by hand in the scratch copy, with `--deselect tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`:
  ```
  RI-007-064 15 failed, 223 passed, 1 deselected in 25.51s | target failed: True
  RI-009-037 8 failed, 230 passed, 1 deselected in 26.48s | target failed: True
  RI-010-049 8 failed, 230 passed, 1 deselected in 24.46s | target failed: True
  RI-011-052 8 failed, 230 passed, 1 deselected in 25.19s | target failed: True
  ```
  All four hold on the build.

## Real-data effect (diff_reports output, pasted)
not required (scripts/check_pipeline.py, scripts/check_handoff.py, tests/test_pipeline_check.py, .claude/agents/a1-auditor.md)

## Deviations from plan
1. **Sent back to I1: m1 fails no test.** The plan says "m1: `continue` back at the blame failure in `late_log_lines` fails (a), (b)", and the Rule trace maps "blame of committed log fails | (b) (real die); m1". Measured: m1 → (a) 1 passed, (b) 1 passed. The cause: in (a) every git call returns 128, and in (b) real git with a bad shallow line exits 128 on `ls-tree -r HEAD`. So `late_log_lines` returns the ls-tree entry before any blame runs. The blame-failure entry is built, but no test pins it. I did not add an unplanned test. Suggested fix for I1 to plan: a fixture with a committed log file and `_patched_git` on only `("blame", "--line-porcelain", "--", "logs/implementation/<date>.md")` → `("", 128)`. It should expect `LOG TIME: logs/implementation/<date>.md (git blame failed; item 081)` and exit 1, with m1 failing it.
2. **Observation for I1/I3 (no code change): an orphan open branch is now a BRANCH ERROR.** Measured on the (d2) fixture, full run: exit 1, `origin/nowork: items none; merge not checked; ...`, `BRANCH ERROR: origin/nowork (git diff failed (exit 128))`, `BRANCH ERROR: origin/nowork (git merge-base failed (exit 1))`. This follows the plan, since `merge-base --all` goes through `_git_ok`. But merge-base exit 1 means "no common ancestor", which is a real answer, not a failure. Before 081 this branch printed `items none` silently. Loud is the safe side, so I kept it. I1 may want to decide whether an unrelated-history branch should be its own line.
3. `main_ahead` with exit 0 but a non-digit count: the plan's `f"{why} (item 081)"` would print `None (item 081)` (why is None there). I print `git rev-list gave no count (item 081)` instead. The result is the same (str → MAIN AHEAD line, exit 1). The text differs only so it is readable. No test pins this branch (git always prints a digit on exit 0).
4. Test (e) asserts `res[0]["errors"] == ["git diff failed (exit 1)"]` (equality, which also pins change 4's de-dup) instead of the plan's `in`. That is stricter, with the same intent.
5. Test (b) takes `_root(repo)` before writing `.git/shallow`, because `git rev-list --max-parents=0` dies (128) after it is written.

---

## Round 2 (2026-11-21, I2)
Base: daily-fixes/2026-11-20 at 55893e5 (code identical to 0583289: 55893e5 only adds work/086/04 and a log line). It includes 084 r1-r2 and 086 r1; their code was not touched. Not committed (orchestrator commits). No brokerage connection; every fixture is a temp git repo. Built from 04 "## Round 2" exactly; no deviations.

File counts (commands, item 012):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → `0`
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → `2`
```
 scripts/check_pipeline.py    |  46 ++++++++++++++-----
 tests/test_pipeline_check.py | 105 +++++++++++++++++++++++++++++++++++++++++--
 2 files changed, 137 insertions(+), 14 deletions(-)
```
The round-1 total stays 4 files (both files were already in round 1).

### Changes made (round 2)
- `scripts/check_pipeline.py`
  - `open_branches`: `when`/`last` moved up unchanged to just after the `behind` skip. A raw `mb = _git("merge-base", "--all", "HEAD", ref)` follows. When exit is 1 (no common ancestor), the branch's checked paths are listed with `_git_ok("ls-tree", "-r", "--name-only", ref, "--", "work/", RECURRING, *RULE_PATHS, *RESEARCH_CODE_PATHS)`, an `unrelated: True` dict is appended, and the loop continues. Its errors are the ls-tree reason, or the `no common history with HEAD; <n> file(s) on checked paths (first: <path>) not checked (item 081)` text, or nothing.
  - The old `_git_ok("merge-base", ...)` block was replaced by an `mb`-based one. The texts are the same: `git merge-base failed (exit <n>)` at the same point in the flow. `bases` is set only on exit 0.
  - The normal dict gains `"unrelated": False`. The docstring gains the `unrelated` field.
  - `main` OPEN BRANCHES loop: `age` moved to the top. `b.get("unrelated")` prints `  <ref>: no common history with HEAD; not scanned (item 081)<age>` and continues. BRANCH ERROR and the exit term are unchanged.
  - Module docstring, BRANCH ERROR entry: added the plan's no-common-history paragraph plus the known-gap sentence (check_handoff `_branch_with_handoff` does not read per-ref errors).
  - `late_log_lines` and `main_ahead`: no code change.
- `tests/test_pipeline_check.py`
  - `GIT_CENSUS`: `("open_branches", "_git")` 4 → 5 with the merge-base reason. `("open_branches", "_git_ok")` stays 5 with its new reason. Census total `== 46` → `== 47`. Recount on the built file: `test_git_call_census` passes at 47, so 086 r1 added no git calls (46 before + 1).
  - New helper `_orphan(repo, name, files)`. (d2) is left unchanged.
  - New tests: R2-a `test_blame_failure_of_committed_log_is_an_entry`, R2-b `test_unrelated_branch_without_checked_paths_is_not_an_error`, R2-c `test_unrelated_branch_with_work_is_branch_error`, R2-d `test_merge_base_die_is_branch_error`, R2-e `test_main_ahead_non_digit_count`. Each follows the plan's assertions.

### Connectivity check (round 2)
- [x] every new function/rule is used: `_orphan` is used by R2-b and R2-c. The `unrelated` key is read by `main` (`b.get`) and asserted in R2-b and R2-d.
- [x] every input has a source, every output has a consumer: merge-base exit 1 → ls-tree → the not-scanned line and/or BRANCH ERROR (exit 1). ls-tree failure → BRANCH ERROR.
- [x] every branch ends in a defined result: merge-base exit 0 → scanned. Exit 1 + 0 files → not-scanned line, exit unchanged. Exit 1 + ≥ 1 file → BRANCH ERROR. Exit 1 + ls-tree fails → BRANCH ERROR `git ls-tree failed (exit <n>)`. Other exit → BRANCH ERROR `git merge-base failed (exit <n>)`, branch still scanned. `mb is None` → `git merge-base failed (no git)`.
- [x] no leftover TODOs or unused files.
- Missing-data grep `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` → 38 hits, all pre-existing. ccbot/ is untouched, so there are no new hits. The same pattern on this round's check_pipeline.py diff:
  - `if mb is not None and mb[1] == 1`: None (no git) is not this branch. It falls to the error path below.
  - `bases = mb[0].split() if mb is not None and mb[1] == 0 else []`: `[]` only with an error already appended. This is round 1's behaviour.
  - `b.get("unrelated")`: hand-built test dicts lack the key, and absent means a normal scanned branch, not a pass of any check.
  - No numeric dataclass defaults and no new `>`/`<` tests.

### Recurring issues checked (round 2, item 013)
- RI-001: each new filter has a computed fixture count (below).
- RI-002: an unrelated branch is quiet only after a successful ls-tree shows 0 checked files. A failed ls-tree is an error (R2-b absent case, m14).
- RI-008: py_compile with python3.11 is OK.
- RI-009: `--next-id` still counts an orphan's work/ ID (R2-c: 151).
- RI-010: the log line is written by `--log`.
- RI-011: the anchors are byte-identical (1/1/1) and criss-cross passes.
- RI-012: unrelated is decided by exit code 1 only (R2-d, m13).
- RI-014: below.

RI-014: guardrail extended (081); GUARDED when 079 and 081 are merged and m2 fails fixture (b) on main.

### Feasibility numbers (measured)
- Blame: 1 of 2 committed log files failed → exactly 1 entry (R2-a passes with the exact list).
- `nowork`: 1 file (README.md), 0 on checked paths → not-scanned line, exit 0.
- `oldwork`: 1 file, 1 on checked paths → BRANCH ERROR, exit 1.
- merge-base 128 → `git merge-base failed (exit 128)`, `unrelated` False, 040 still in items.
- Census: 47.

I3's repro, real git (scratch pytest wrapper around `_repo_with_open_branch` + `_orphan`, `--today 2026-11-02`, so the age is negative because the commits are dated today):
```
NOWORK exit 0
040: IN PR (origin/fix has 01 02 03 04 05 06 07; was STUCK here)
OPEN BRANCHES (not merged into HEAD):
  origin/fix: items 040; merges cleanly; edits logs/recurring-issues.md (item 036); last commit 2026-11-21 (-19 days)
  origin/nowork: no common history with HEAD; not scanned (item 081); last commit 2026-11-21 (-19 days)
OLDWORK exit 1
040: IN PR (origin/fix has 01 02 03 04 05 06 07; was STUCK here)
OPEN BRANCHES (not merged into HEAD):
  origin/fix: items 040; merges cleanly; edits logs/recurring-issues.md (item 036); last commit 2026-11-21 (-19 days)
  origin/nowork: no common history with HEAD; not scanned (item 081); last commit 2026-11-21 (-19 days)
  origin/oldwork: no common history with HEAD; not scanned (item 081); last commit 2026-11-21 (-19 days)
BRANCH ERROR: origin/oldwork (no common history with HEAD; 1 file(s) on checked paths (first: work/150/request.md) not checked (item 081))
next-id (0, '151\n')
```

### Test output (round 2, pasted)
Base, in a scratch copy with both files reset to HEAD (`git checkout -- ...` in the copy only), `python3 -m pytest -q`:
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated - Asserti...
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
4 failed, 637 passed, 1 skipped in 84.71s (0:01:24)
```
Build (repo working tree), `python3 -m pytest -q`:
```
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated - Asserti...
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
4 failed, 642 passed, 1 skipped in 86.11s (0:01:26)
```
The same 4 failures appear at base and build, and none is 081's. Three come from 086's not-computable text (086 is back at I1). `test_repo_pipeline_has_no_skipped_items` fails while 081/084/086 are open. New tests: 642 − 637 = 5 (R2-a to R2-e).

Checks:
- `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` → OK.
- `grep -cxF` of the 3 anchor lines → 1, 1, 1.
- Real repo `python3 scripts/check_pipeline.py`, before the edit vs after → `diff before.txt after.txt` gives no output (both exit 1, from the open items). Every origin/* branch shares history with HEAD.

Mutations (scratch copy `/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/mut-081-r2-<epoch>/repo`, never the repo; the file was restored and `cmp` matched after each set):
```
m1 | test_blame_failure_of_committed_log_is_an_entry | 1 failed   (assert [] == ['logs/implementation/2026-10-31.md (git blame failed; item 081)'])
m11 | test_unrelated_branch_without_checked_paths_is_not_an_error | 1 failed   (assert code == 0: BRANCH ERROR, exit 1)
m12 | test_unrelated_branch_with_work_is_branch_error | 1 failed
m13 | test_merge_base_die_is_branch_error | 1 failed   (assert fix["unrelated"] is False: True)
m14 | test_unrelated_branch_without_checked_paths_is_not_an_error | 1 failed   (absent case: [] == ['git ls-tree failed (exit 128)'])
m15 | test_main_ahead_non_digit_count | 1 failed
m9 (extra _git("status") in open_branches) | test_git_call_census | 1 failed
```
Round-1 mutations re-run on the round-2 build (my reading of each round-1 site):
```
m1b -> test_all_git_fails_no_line_says_none: 1 failed
m2 -> test_all_git_fails_no_line_says_none: 1 failed
m2 -> test_malformed_shallow_real_git_nothing_none: 1 failed
m2 -> test_open_branches_none_line: 1 passed   (control, as planned)
m3 -> test_all_git_fails_no_line_says_none: 1 failed
m3 -> test_malformed_shallow_real_git_nothing_none: 1 failed
m7 -> test_branch_diff_failure_is_branch_error: 1 failed
m10 -> test_branch_show_failure_skips_classify: 1 failed
m8 -> test_all_git_fails_no_line_says_none: 1 failed
m8 -> test_inbox_flag_die_is_loud: 1 failed
```
m4/m4b/m5/m6 were not re-run: their sites (main_ahead return value, exact-refname filter, the decode settings) are not touched in round 2, and their tests (a), (d3), (c), (c2) pass.

### Real-data effect (round 2)
not required (scripts/check_pipeline.py, tests/test_pipeline_check.py)

### Deviations from plan (round 2)
None. Round 1 Deviation 1 is closed by R2-a/m1. Deviation 2 is closed by the no-common-history handling (R2-b to R2-d). Deviation 3 is pinned by R2-e/m15.
