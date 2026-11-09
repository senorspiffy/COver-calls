# 03 Research hand-off - 049
Status: READY
Recurring issues checked (R3): RI-010 (ESCALATED: the map adds a check the builder sees before building, not only after), RI-009 (RULES BRANCH extends 034 from files to rules), RI-007 (no step skipped for 048; its six step files exist), RI-002 (no data path changed).
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| `late_log_lines` has no way to name an exception | scripts/check_pipeline.py `def late_log_lines` (reads only LOG_CHECK_FROM) | VERIFIED |  |
| LEGACY / PRE_A1_LINE are closed, named lists with "Never add" | scripts/check_pipeline.py L76–77, L96–97 | VERIFIED | line numbers corrected: 01 said L109–111 / L80–82; the lists are at L96–97 and L76–77 |
| 048's 04 and 05 each list 4 files; 05 says 187 passed, 1 skipped | work/048/04-build-plan.md § Files, 05-build-report.md | VERIFIED |  |
| 65adf0c's parent 87c8573 has no `--log`/LOG TIME; PR #12's branch has `write_log` | `git log -1 --format=%P 65adf0c` → 87c8573; `git show 87c8573:scripts/check_pipeline.py \| grep -c "def write_log\|LOG TIME"` → 0; same on origin/daily-fixes/2026-11-05 → 1 | VERIFIED |  |
| `open_branches` reports work/ items, not rule files | scripts/check_pipeline.py `def open_branches` (`git diff --name-only HEAD...ref -- work/`) | VERIFIED |  |
| run-item's 034 rule covers only files you will change | .claude/commands/run-item.md L12 | VERIFIED |  |
| Re-committing a line moves its git blame to the new commit | R3 scratch repo: commit "one", rewrite line, commit "two" → `git blame --line-porcelain` → `summary two` | VERIFIED |  |
**Totals:** 7 rows checked → **6 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | logs/implementation/2026-11-07.md: 048's I1 → `FIT \| 4 files planned`, I2 → `4 files changed \| tests 187/188 (1 skipped)`; times unchanged | 048/04, 048/05 | log lines in format | `check_pipeline.py` → INCOMPLETE none | – |
| 2 | `LOG_TIME_EXCEPT = {"048": "<reason, item 049>"}` in check_pipeline.py (closed, "Never add a new item here"); `late_log_lines` skips those items; output `LOG TIME: none (not checked: 048: <reason>)` | committed logs | LOG TIME line | fixture: late line for 048 not flagged and named; late line for 150 still flagged; test pins the dict to {"048"} | – |
| 3 | `open_branches` adds `rules`: files the branch changes under `.claude/`, `templates/`, `scripts/check_pipeline.py`, `scripts/check_handoff.py`; main prints `RULES BRANCH: <ref> changes <files>; build new items on top of it (item 049)` or `RULES BRANCH: none`. No exit-code change | remote branches | RULES BRANCH line | fixture: branch editing `.claude/agents/x.md` → named; the existing `_repo_with_open_branch` (work/ and logs only) → `RULES BRANCH: none` | – |
| 4 | run-item.md: "if RULES BRANCH names a branch, build on top of it: its rules apply to the new item (item 049)"; a1-auditor.md: list RULES BRANCH lines at the top of the report | – | agent text | grep both files | – |
| 5 | Known gap written in the script docstring: a log line re-committed in a later commit is checked against that later commit (blame) | – | docstring | fixture test shows it (documents, does not fix) | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| git (RULES BRANCH) | not a repo / no git | no RULES BRANCH line, as OPEN BRANCHES today |
| merge base for a branch | `git diff HEAD...ref` fails | branch's rules = [] for that branch (printed nothing), same as its items |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| I2 total for 048 | passed + skipped | 187 + 1 = 188 | ✓ `tests 187/188` |
| I1 files for 048 | files in 04 § Files | 4 | ✓ |
| Totals | 6 + 1 + 0 | 7 | ✓ |
`python3 scripts/check_handoff.py 049` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 7
totals line: 7 rows -> 6 as-is, 1 fixed, 0 removed
PASS
```
