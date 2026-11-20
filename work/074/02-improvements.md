# 02 Improvements - 074

## What past logs say
- No earlier item covers a committed probe script. A Grep of logs/ for "074" and "probe_guardrails" finds only the 2026-11-18 audit (L48, L54), the efficiency line (L3) and R1's log line [repo: logs/audit/2026-11-18.md; logs/efficiency/2026-11-18.md; logs/research/2026-11-18.md].
- RI-002's status text still names the old 063 probe (`td.earnings[0] <= d and`). That string has not been in the code since 065's `_earnings_state` refactor (ccbot/realtest.py L391-405). Nothing noticed until A1 tried to run it on 2026-11-18. This is the RI-010 pattern: a check that exists only in text no script runs [repo: logs/recurring-issues.md RI-002 status, RI-010 root cause].
- RI-013's probe "1b" was only ever in I3's scratch script, which has since been deleted. 067/06 records the result but not the edit [repo: work/067/06-verification.md L96, L104, L121].
- RI-009 occurrence 2026-11-01 | 034: an in-repo `git checkout` restore wiped an uncommitted edit. That is why the project rule is "scratch copy, never in the repo" [repo: logs/recurring-issues.md RI-009].
- The a1-auditor.md daily review has only the general sentence "check that every guardrail from past BUG items is still in place" (L36). It names no command [repo: .claude/agents/a1-auditor.md L36].
- **A1's actual 2026-11-18 probe script** (orchestrator scratch script, 2026-11-18, `/tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/probe.py`) settles R1's open questions 2 and 3 and findings 10-12:
  - P1 kept the `if i == 0:` and changed only the return value to "known". This matches R1's P1 replacement. The anchor in the script has no leading indent: `'if i == 0:\n        return "before_first"'`.
  - P2 replaced the two-line anchor with `'if False:\n        return "interior_gap"'`, keeping the return line. This matches R1's P2 replacement. R1's IndentationError concern (finding 11) does not apply.
  - P3 differs in text from R1's proposal. Anchor: `'                out.extend(diff_json(a[k], b[k], p))\n        return out'`. Replacement: `'                out.extend(diff_json(a[k], b[k], p) if not path or type(a[k]) is not dict else [])\n        return out'`. The logic is the same as R1's `if not (path and type(a[k]) is dict)` (De Morgan), but it is one line, so the file's line numbers don't change. Its anchor takes in the `return out` that closes the dict branch (scripts/diff_reports.py L86-87).
  - How the script works: it takes the worktree path as argv[1]. Each anchor is checked with `assert src.count(old) == 1`. Pytest is run with `-q -p no:cacheprovider` on the whole test file, and only the last stdout line is printed. The original file is restored in `finally`. There is no baseline run, no target-test check, no exit-code check, no timeout and no compile check.

## 3 ways FOR
1. **Copy A1's three specs verbatim, so the recorded counts are what the script reproduces.** A1's strings are the edits that actually produced 9 failed / 41 passed, 4 failed / 46 passed and 1 failed / 16 passed (logs/audit/2026-11-18.md L45-47; orchestrator scratch script, 2026-11-18). R1's P1 and P2 are the same text. R1's P3 is the same logic but adds a line. Copying A1's P3 keeps line numbers fixed, so tracebacks and the 067/06 line references stay comparable, and it removes the "UNVERIFIED against A1's script" notes in R1 findings 10-12.
   - Leading-indent choice: A1's P1/P2 anchors start at `if`. R1's table adds the 4-space indent. Both count 1 today (R1 finding 4, A1's assert passed). Keep A1's text so the run is a reproduction, not a new probe.
   - I2 must still measure. If a count differs from A1's, record the measured count and do not tune the mutation (R1 finding 12).
2. **Add the checks A1's hand script did not have.** These are what turn "it printed a summary line" into "the guardrail held".
   - (a) Target-test check. A1's script printed only pytest's last line, so the audit's "target test_a failed" for P3 is not in the script's output. P1 and P2 had no named target at all. Each entry needs a target node id, looked up by exact name in `--junit-xml` (R1 findings 20, 26). The proposed targets are R1's `test_leading_edge_100_days_blocks`, `test_interior_gap_180_blocks` and `test_a_nested_key_and_list_in_dict`. Only the third has a recorded run (067/06 L104).
   - (b) Anchor failures as a per-probe ERROR line, not `assert`. A bare `assert` stops the whole run at the first missing anchor, so later probes never run and are never named. Under `python -O`, "the current code generator emits no code for an `assert` statement" [https://docs.python.org/3/reference/simple_stmts.html], so the anchor check would vanish and `str.replace` on a missing anchor would silently change nothing. That probe would then "pass" as not holding, for the wrong reason.
   - (c) Accept a mutated run only with pytest exit 1 and 0 errors. Exits 2, 3, 4 and 5 mean ERROR [https://docs.pytest.org/en/stable/reference/exit-codes.html]. Run `py_compile` on the mutated file first (R1 traps 25, 22).
   - (d) Run the unmutated baseline of the target(s) first (R1 trap 27).
   - (e) Set a `subprocess.run(timeout=...)` [https://docs.python.org/3/library/subprocess.html].
3. **Recommended scope: the three probes now, as data entries; the rest as follow-up items.** Keep the probes as a module-level list of dicts in the script, each with name, RI, file, anchor, replacement, test file and target. Adding a probe is then one entry plus a fixture-free run. That meets "Done looks like" without blocking on anchor archaeology.
   - About 13 more probes are anchor-shaped but have no recorded anchor (RI-001 slack 0, RI-002's 046 and older ones, RI-003, RI-011, RI-012), per R1 section C. Each needs an I1 lookup in old work files and its own measured count, so open them as one follow-up EFFICIENCY item.
   - The CLI/fixture probes (RI-007, RI-010) need a second entry type ("command + expected exit/output"). That should be a separate follow-up so this item stays one mechanism.
   - In the same commit, the RI-002 and RI-013 status text in recurring-issues.md should name the probe by its script entry name instead of a code string. A1's daily commit does this, not the fix branch (RI-009 guardrail 036). A refactor then breaks the script, loudly, rather than leaving the text stale.

## 3 ways AGAINST
1. **Daily runtime.** Mutated runs are about 50 s + 26 s + 1.5 s ≈ 78 s (request L19; 067/06 L104). A whole-file baseline of tests/test_realtest.py would add another run of roughly that size (UNVERIFIED, no shell). With a whole-file baseline per probe, the realtest cost about doubles.
   - Mitigation: run the baseline on the target node ids only (`pytest file::name`). Run one baseline per test file, not per probe. Keep the full file for the mutated run, because the request wants failed/passed counts.
   - The target-only baseline runtime is UNVERIFIED. I2 should note it next to the 50 s / 26 s figures.
2. **Exact anchors make every refactor of a probed file a red audit, and invite loosening.** This is the intended behaviour (request L8), but it is a standing maintenance cost. Any edit to `_earnings_state` or the `diff_json` dict branch, even a reformat, makes the script exit 1 until someone rebuilds the entry. The risk is that whoever sees the red line "fixes" it with a shorter or regex anchor that still matches but no longer hits the guarded logic.
   - Mitigation (process, reasoning only): the probe file's entries change only in a work item whose I2 shows the new probe failing its target. The builder of any item that touches a probed file runs the script in its 05 (I2). A1 never edits an entry during the audit; it opens an item.
3. **A green probe list can be read as more than it proves.** Each entry shows that one hand-picked mutant is caught by one test. It does not show that the root cause is covered. RI-002 went GUARDED, then ESCALATED again three times through new input paths that no existing probe touched (tickers.json via 040/041, the broker defaults via 014, realtest's edges via 063) [repo: logs/recurring-issues.md RI-002 "Why the guardrails didn't hold"].
   - If the daily report pastes "3 probes hold" under "Guardrails still in place?", it can crowd out the judgement call A1 still has to make about new paths.
   - Mitigation: the a1-auditor.md line should say the script checks the recorded probes only, and that new input paths still need A1's review. Mutation tools such as mutmut generate mutants rather than taking a curated list, but a full pass is out of scope (R1 finding 23).

## Findings by language
Languages: N/A (no new external claims). 074 is an EFFICIENCY item: a repo-internal test script plus one agent-text line. It adds or changes no fee, rule, market statistic or trading behaviour (R1 "Fit for a ~$3k account"). The only outside facts it uses are git/pytest/Python tool behaviour, which R1 and this file cite to official English docs. This follows the precedent for the tooling items 045, 049, 052, 067 and 070 (all logged `languages: N/A`).
Random languages this cycle: N/A

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | N/A (no new external claims) | - | - | - |
| Mandarin Chinese | N/A | - | - | - |
| Spanish | N/A | - | - | - |
| Japanese | N/A | - | - | - |
| N/A | N/A | - | - | - |
| N/A | N/A | - | - | - |
| N/A | N/A | - | - | - |

## Holes to watch out for (summary)
1. **No baseline in A1's 2026-11-18 run.** P1's 9 failures and P2's 4 have never been shown to all come from the mutation. If some realtest tests fail in the worktree for other reasons, they inflate both counts.
   - Example: tests that read `data/real` (test_real_counts_bac, test_real_interior_gap_mo, test_real_min_years_filter; R1 finding 7) would fail if data/real is not tracked. Whether data/real is tracked at 4d690a3 is UNVERIFIED.
   - I2 must run the unmutated file once in the same scratch copy and report its counts. A non-green baseline is ERROR, not "holds".
2. **Target never checked by the script.** "Target test failed yes/no" must come from junit XML by exact name. A misspelled target must give ERROR, not "no" (R1 trap 26).
3. **`assert` for anchor counts.** It aborts the run at the first missing anchor and disappears under `-O` (FOR 2b). Use an explicit check that prints `<probe>: ANCHOR MISSING (count N)`, carries on with the other probes, and exits 1 at the end.
4. **Copy method.** Recommended: `git worktree add --detach <TemporaryDirectory>/wt <ref>`, with `--ref` defaulting to `HEAD`. The script prints the resolved SHA on its first line. In `finally`, run `git worktree remove --force` and then `git worktree prune` [https://git-scm.com/docs/git-worktree; R1 finding 13].
   - Why a worktree: it matches A1's measured runs, and GUARDED conditions are judged "on main" (committed code). A1's checkout is usually a daily-fixes branch with uncommitted audit edits, which a `shutil.copytree` of the working tree would pick up along with untracked reports/ and caches.
   - Cost: a worktree writes metadata under `.git/worktrees`. The working files are untouched. A killed run leaves a stale entry, which `prune` clears.
   - The fixture tests need a `git init` in `tmp_path`. This repo already builds git fixtures in tests/test_pipeline_check.py (RI-007, RI-011).
   - Alternative, not chosen: an optional `--copy` (copytree of the working tree) for I1/I2 checking uncommitted work. It can be a follow-up if wanted.
   - Before deleting anything, assert the scratch path is not inside the repo (R1 trap 29).
5. **Wrong code under test.** With `cwd` set to the worktree, `python -m pytest` puts the worktree first on sys.path [https://docs.pytest.org/en/stable/explanation/pythonpath.html]. Whether an installed `ccbot` could shadow it is UNVERIFIED, so assert that `ccbot.__file__` is under the scratch root once per run (R1 trap 28).
6. **P3 anchor spans two lines** (`... p))\n        return out`). A reformat of the line after L86 also breaks it. That is acceptable, since it fails loud, but I1 should know the anchor is two lines, not just L86.
7. **The a1-auditor.md line** must give the exact command, say to paste its output under "Guardrails still in place?", and say it covers only the listed probes (AGAINST 3).
8. **Restore by rewrite.** A1's script restores the original text in `finally` inside the worktree. With a throwaway worktree per run this is optional. If kept, restore from the bytes read, not from a re-read.

## Recommendation (scope and copy method)
- Scope now: P1, P2 and P3 with A1's exact strings (orchestrator scratch script, 2026-11-18), the per-probe ERROR handling and checks in FOR 2, and the three-plus fixture tests (holds / does not hold / anchor missing or duplicated; optionally a syntax-error mutation, which gives ERROR).
- Follow-ups:
  - (i) The ~13 anchor-shaped probes with no recorded anchors, as one EFFICIENCY item.
  - (ii) A "command + expected exit" entry type for RI-007 and RI-010.
  - (iii) Optional `--copy` mode.
- Copy method: a detached git worktree of `--ref` (default HEAD) in a TemporaryDirectory, removed with `--force` and then pruned. Never write to the repo's working files.
