# 01 Research brief - 074

## Question
Can every GUARDED / "Move to GUARDED when" mutation probe in logs/recurring-issues.md become one committed, re-runnable check (for example `scripts/probe_guardrails.py`)? Each entry would hold the file, an exact anchor, the replacement, the test file and the test that must fail. It must edit only a scratch copy, print one line per probe and exit 1 when a target test passes or an anchor count is not 1. This brief covers four things: (a) which RI probes fit that anchor + replacement + target-test shape and which don't; (b) the exact specs for the three probes A1 ran 2026-11-18; (c) the documented behaviour of the tools the script relies on; (d) the traps that would let a probe "hold" when it shouldn't.

Inputs read: work/074/request.md; logs/recurring-issues.md RI-001 to RI-013; logs/audit/2026-11-18.md; logs/efficiency/2026-11-18.md; ccbot/realtest.py L374-411; scripts/diff_reports.py (whole file, the dict branch is L75-87); tests/test_realtest.py; tests/test_diff_reports.py; tests/conftest.py; pyproject.toml; .gitignore; work/067/06-verification.md L85-122; .claude/agents/a1-auditor.md. No earlier item covers this topic (Grep of logs/ for "074" and "probe_guardrails": only today's audit and efficiency lines).

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### A. Repo facts (each one read from the file named)
1. The three probes A1 ran 2026-11-18 were built by hand in a session scratchpad on a scratch worktree of main 4d690a3, with the "repo tree not edited" [repo: logs/audit/2026-11-18.md L44-48]. No `scripts/*probe*` file exists (Glob, this branch).
2. The RI-002 063 probe text (`td.earnings[0] <= d and`) is gone from ccbot/realtest.py. The logic now sits in `_earnings_state` (L391-405) [repo: work/074/request.md L11; ccbot/realtest.py L391-405].
3. The RI-013 probe "mutation 1b" was only ever in I3's scratch script `.../scratchpad/i3-067/mut_i3.py`, which no longer exists. 06 records the result ("1 failed, 16 passed ... target test_a_nested_key_and_list_in_dict failed: True") but not the edit's exact text [repo: work/067/06-verification.md L96, L104, L121].
4. Exact anchors in today's tree, one hit each (Grep over ccbot/ and scripts/):
   - `    if i == 0:\n        return "before_first"` is at ccbot/realtest.py L397-398.
   - `    if _is_gap(td.earnings[i - 1], td.earnings[i]):\n        return "interior_gap"` is at L403-404.
   - `                out.extend(diff_json(a[k], b[k], p))` is at scripts/diff_reports.py L86.
   [repo: ccbot/realtest.py L397-404; scripts/diff_reports.py L86]
5. tests/conftest.py sets `REPO = Path(__file__).resolve().parents[1]`, and tests/test_diff_reports.py runs `REPO / "scripts" / "diff_reports.py"` in a subprocess. Run from a scratch copy, these tests therefore exercise the copy's script, not the repo's [repo: tests/conftest.py L7; tests/test_diff_reports.py L8-12].
6. pyproject sets `pythonpath = ["tests"]` only. `ccbot` has to be importable some other way, either the cwd that `python -m pytest` adds or an installed package [repo: pyproject.toml L19-21]. No `ccbot` dist was found under /usr/local/lib (Glob). Whether an editable install exists somewhere else is UNVERIFIED (I have no shell).
7. tests/test_realtest.py reads `data/real` (`DATA = .../data/real`, used in test_real_counts_bac, test_real_interior_gap_mo and test_real_min_years_filter). .gitignore does not exclude data/, so a worktree of a commit contains it if it is committed [repo: tests/test_realtest.py L84, L545-577; .gitignore]. That data/real is tracked at 4d690a3 is UNVERIFIED (no git).
8. Runtimes from the request: the realtest probes take about 50 s and 26 s. I3's diff_reports runs took 0.68-1.47 s [repo: work/074/request.md L19; work/067/06-verification.md L98-117].
9. The project already has a precedent for "scratch copy, never in the repo". RI-009 occurrence 2: an in-repo `git checkout` restore by I2 wiped an uncommitted edit [repo: logs/recurring-issues.md RI-009 occurrence 2026-11-01 | 034].

### B. Specs for the three 2026-11-18 probes (exact strings; `\n` = newline, 4/8/16 leading spaces as in the file)
| # | name | file | anchor (count must be 1) | replacement | test file | target test | A1 result 2026-11-18 |
|---|---|---|---|---|---|---|---|
| P1 | RI-002 063 leading edge | ccbot/realtest.py | `    if i == 0:\n        return "before_first"` | `    if i == 0:\n        return "known"` | tests/test_realtest.py | `test_leading_edge_100_days_blocks` (proposed; see 10) | 9 failed, 41 passed |
| P2 | RI-002 065 interior gap | ccbot/realtest.py | `    if _is_gap(td.earnings[i - 1], td.earnings[i]):\n        return "interior_gap"` | `    if False:\n        return "interior_gap"` | tests/test_realtest.py | `test_interior_gap_180_blocks` (proposed; see 11) | 4 failed, 46 passed |
| P3 | RI-013 067 mutation 1b | scripts/diff_reports.py | `                out.extend(diff_json(a[k], b[k], p))` | `                if not (path and type(a[k]) is dict):\n                    out.extend(diff_json(a[k], b[k], p))` (proposed; see 12) | tests/test_diff_reports.py | `test_a_nested_key_and_list_in_dict` | 1 failed, 16 passed |

10. P1 wording: the RI-002 status text says "`_earnings_state` `i == 0` returns "known" instead of "before_first"". That reads as keeping the `if` and changing only the return value, which is the P1 replacement above [repo: logs/recurring-issues.md RI-002 status 2026-11-18]. One loose reading, "replace the two lines with `return "known"`", would make the whole function return "known" for every day. That form also kills the 065 checks, so its 9 failures would not isolate the leading edge. Which form A1 typed is UNVERIFIED, because A1's script was in a session scratchpad.
    - Target choice (code reading, not a test run): `_edge(100)` lists only 2024-04-11, so on 2024-01-02 `bisect_right` gives i = 0. With the mutation that day is "known", and the 2024-02-16 expiry is before the earnings date. A call would sell and `tr == []` would fail [repo: tests/test_realtest.py L245-254; ccbot/realtest.py L396-398]. That the 9 failures include this test is UNVERIFIED until I2 runs it.
11. P2 replacement: putting a bare `if False:` in place of the two-line anchor would leave `return "known"` at the same indent as the `if`. That is an IndentationError: the module fails to import, the whole file errors at collection, and the result would not be "4 failed, 46 passed". A1's counts therefore imply that only the condition was changed and the `return "interior_gap"` body was kept, which is the P2 replacement above (reasoning from ccbot/realtest.py L401-405 and A1's counts; UNVERIFIED against A1's script).
    - Target choice (code reading): the sale day 2024-01-02 lies inside 2023-10-25 to 2024-04-22 (180 d > 120). With `if False:` it is "known", so a call sells and `tr == []` fails [repo: tests/test_realtest.py L273-280].
12. P3 replacement: I3's exact edit is not recorded (finding 3). The proposed form skips recursion only when the value is a dict and the parent dict is below the root. With it, in test_a:
    - `monte_carlo_2_stocks_1yr.cc_ret` is a dict under a non-root dict, so it is skipped and the line `monte_carlo_2_stocks_1yr.cc_ret.50: 0.0689 -> 0.0686` disappears.
    - `walkforward_picks[1].picked` is a string, so it is still reported.
    - Expected: test_a fails (its line-42 assert and "json changes 2") [repo: tests/test_diff_reports.py L33-44; scripts/diff_reports.py L78-87]. That this gives exactly 1 failed, 16 passed, matching I3's and A1's 1b, is UNVERIFIED until I2 runs it. If the counts differ, record the measured counts. Do not adjust the mutation to match.

### C. RI-001 to RI-013: which "Move to GUARDED when" conditions and probes are mechanically re-runnable
Sorting rule: "mechanical" means the probe is a single text edit to one tracked file, with a named test that must fail. "Not mechanical" means it is a process condition, a merge/PR condition, a CLI or fixture-commit probe, or a probe whose anchor is not recorded anywhere.
| RI | Probe / condition (from recurring-issues.md) | Mechanical? | Why / what is missing |
|---|---|---|---|
| RI-001 | GUARDED when the process edits are approved and the first R3 hand-off fills Feasibility with computed counts. Code probe: `monthly_slack_days: 0` → test_calendar `test_monthly_coverage_2016_2025` 17 failed | Process condition: no. Code probe: yes, once the anchor is fixed | `"monthly_slack_days": 7,` appears in both config/default.json L13 and ccbot/config.py L23 [repo, Grep]. Which file 04/05 edited is not stated in the RI text (UNVERIFIED); per-file count = 1 in each |
| RI-002 | 063 leading edge (P1), 065 interior gap (P2) | Yes | Specs in section B |
| RI-002 | 046: `"foo_date": null` added to F in config/tickers.json → `test_ticker_fields_cover_file_and_code` (1 failed, 22 passed, 2026-11-07..11) | Yes | Insertion into a JSON entry; I1 has to pick an anchor that is unique in config/tickers.json (not checked here) |
| RI-002 | Older code probes: `max(1,` in `bh_lots` → 3 failed; `else 0` in data.py → 2 failed; removing the screen's `EARNINGS_UNKNOWN` → 2 failed; 014: `q` default 0.0 → 1, no CAPITAL_UNKNOWN → 1, `>` cap test → 1, `div_next` 0.0 → `test_day_float_defaults_are_nan`; 041 stale guard removed → 2 failed | Yes in shape; anchors not recorded | Each needs I1 to rebuild the anchor from current code and name the target test; several target tests are not named in the RI text |
| RI-003 | Mon-Fri mutation → 3 failed (007/05, 06) | Yes in shape | Anchor not in the RI text; rebuild from work/007/05 |
| RI-004 | Test exists (`test_worked_example_50pct_exit`); process sentence in r3 | No | No mutation is recorded; I3 checked the old claims against the old code |
| RI-005, RI-006 | Template/self-check and `check_handoff.py` | No | Process plus a script; no mutation probe is recorded |
| RI-007 | Fixture commits (RESEARCH ONLY item 999 with code → `RESEARCH CODE: 999`, `Scope: FAST (I2, ...)` → SKIPPED) | No (not anchor-shaped) | The probe builds a git fixture and checks CLI output. It needs a different entry type: "command + expected output/exit" |
| RI-008 | py_compile on python3.11 | No | A compile check that already runs as a test; no mutation |
| RI-009 | `--next-id` use, ID CLASH | No | Fixture tests exist; the condition is about process |
| RI-010 | `--log I2 999 "x"` → refused, exit 2 | No (not anchor-shaped) | CLI probe; fits the same "command + expected exit" type as RI-007 |
| RI-011 | merge-tree diff disabled (`HEAD...ref` only) → `test_criss_cross_branch_lists_only_its_own_changes` 1 failed, 69 passed | Yes in shape; anchor not recorded | The merge-tree call is at scripts/check_pipeline.py L440 [repo, Grep]; the exact replacement is not in the RI text |
| RI-012 | bare `"429" in low` restored in `_rate_limited` → `test_429_inside_other_text_is_not_retried` 1 failed, 292 passed | Yes in shape; anchor not recorded | `_rate_limited` is at ccbot/broker/webull_sandbox.py L64 [repo, Grep]; the replacement has to be rebuilt |
| RI-013 | 067 mutation 1b (P3) | Yes | Spec in section B (replacement proposed) |

Count: 3 probes are specified now (P1-P3). About 13 more are anchor-shaped with no recorded anchor: RI-001 slack 0, RI-002 046 plus 8 older ones, RI-003, RI-011, RI-012. 2 are CLI/fixture-shaped (RI-007, RI-010). The rest are process conditions. These counts come from the table above, not from a script.

### D. Tool behaviour the script relies on (official docs)
13. `git worktree add` creates a linked worktree. `-d`/`--detach` detaches HEAD in it. `remove` "refuses to remove an unclean worktree unless `--force` is used", and a mutated tree is unclean. `prune` cleans up the metadata of worktrees whose directories are gone [https://git-scm.com/docs/git-worktree].
14. A worktree checks out a commit, so it does not contain the working tree's uncommitted edits. This follows from 13: it "checkout[s] *<commit-ish>*" [https://git-scm.com/docs/git-worktree].
15. `tempfile.TemporaryDirectory` removes the directory and its contents when the context exits. `ignore_cleanup_errors` was added in 3.10 (the project floor is ≥3.10, pyproject L9). `delete` was added in 3.12, so the script must not use it [https://docs.python.org/3/library/tempfile.html].
16. `shutil.copytree(src, dst, symlinks=False, ignore=None, ...)` takes an `ignore` callable, and `ignore_patterns('*.pyc', 'tmp*')` builds one from globs. This is a stdlib-only alternative to a worktree that copies the working tree as it is and never touches `.git` [https://docs.python.org/3/library/shutil.html].
17. `subprocess.run` runs the child in `cwd` when one is given. When the `timeout` expires, "the child process will be killed and waited for", and then `TimeoutExpired` is raised. `returncode` is the exit status [https://docs.python.org/3/library/subprocess.html].
18. `python -m pytest` behaves like `pytest` except that it "will add the current directory to sys.path". In prepend import mode, pytest inserts the directory of a standalone conftest/test module at the front of sys.path [https://docs.pytest.org/en/stable/explanation/pythonpath.html]. With cwd = scratch root, `import ccbot` resolves to the scratch copy ahead of site-packages (sys.path order; that cwd comes before an editable install's path entry is my inference, UNVERIFIED).
19. pytest exit codes: 0 all passed; 1 "some of the tests failed"; 2 interrupted; 3 internal error; 4 usage error, "including ... a `conftest.py` that fails to import"; 5 no tests collected [https://docs.pytest.org/en/stable/reference/exit-codes.html].
20. `-r` defaults to `fE` (lists failures and errors). `--junit-xml=path` writes an XML result file [https://docs.pytest.org/en/stable/how-to/output.html].
21. The cache plugin (`cacheprovider`) writes `.pytest_cache` under rootdir. `-p no:NAME` deactivates a plugin [https://docs.pytest.org/en/stable/how-to/cache.html; https://docs.pytest.org/en/stable/how-to/plugins.html].
22. `py_compile.compile(file, doraise=True)` raises `PyCompileError` on a compile error [https://docs.python.org/3/library/py_compile.html].
23. Mutation-testing background: mutmut creates mutants and checks whether the tests catch them. It keeps its mutants in a `mutants/` directory, and writing a mutant into the source is a separate, explicit step (`mutmut apply`), with advice to commit first [https://mutmut.readthedocs.io/en/latest/]. Item 074 is a hand-picked mutant list rather than generated mutants. Running a full mutmut pass is not proposed (cost/runtime on realtest is UNVERIFIED).
24. Python `str.count(anchor)` counts non-overlapping occurrences, and `str.replace(old, new, 1)` replaces only the first. UNVERIFIED against the docs page: the fetched stdtypes page was cut off before the str methods.

### E. Traps that make a probe "hold" falsely, and the check for each
25. Broken mutation. A replacement with a syntax or indent error fails every test in the file at collection, so "target failed" is true for the wrong reason (P2 shows how easily this happens, finding 11). Two checks: run `py_compile.compile(mutated, doraise=True)` before pytest (22), and accept a mutated run only when pytest's exit code is 1 and the error count is 0. Exit 2, 3, 4 or 5 is a probe ERROR line and exit 1 for the script (19).
26. Typo in the target name. A target node id that does not exist makes pytest report an error rather than a failure. Two checks: look the target up in the junit XML by exact `classname`/`name` (20), and treat "target not in results" as ERROR.
27. Target already failing. Run the unmutated copy first, at least the target test, and require it to pass. Otherwise a test that was red before the mutation is recorded as "probe holds". This adds runtime: realtest's `_tiny` tests do not load data_root, but the whole-file baseline would add about 50 s (the size is from finding 8; UNVERIFIED for the target-only run).
28. Wrong code under test. If `ccbot` were imported from another path (an installed package), the mutation would not apply and the target would pass. That gives exit 1, which fails safe but blames the guardrail. Check: in the scratch run, print `ccbot.__file__` once, or assert that it is under the scratch root (18, finding 6).
29. Writing to the repo tree. The repo is never opened for writing. Anchor checks read the repo file, but every edit goes to `<scratch>/<file>`. The script asserts `Path(scratch).resolve()` is not inside the repo, and tests it by hashing the repo files a probe touches before and after (fixture test). This matches the finding 9 precedent.
30. Fixture tests for the script (request "Done looks like"): a tiny temp project (`tmp_path`) with one module and one test, run three ways. (a) The mutation makes the target fail: "holds", exit 0. (b) The mutation leaves the target passing: exit 1. (c) The anchor is absent (count 0) or duplicated (count 2): exit 1, naming the probe, with pytest never run. Optionally (d) a mutation with a syntax error gives ERROR, exit 1 (from 25). This keeps the script's own tests fast and independent of realtest's 50 s.

## Numbers used (show the math)
- P1 total tests: 9 + 41 = 50. P2: 4 + 46 = 50. Same file, same total [repo: logs/audit/2026-11-18.md L45-46].
- P3: 1 + 16 = 17, which matches I3's "restored: 17 passed" [repo: work/067/06-verification.md L117].
- Daily runtime estimate without baselines: about 50 s + 26 s + about 1.5 s ≈ 78 s (realtest figures from request.md L19, diff_reports maximum 1.47 s from 067/06 L104). Whole-file baselines add one unmutated test_realtest.py run (one run serves P1 and P2; size UNVERIFIED, I have no shell) plus about 0.7 s for test_diff_reports.py (067/06 L117: 0.68 s).
- Anchor counts in today's tree: P1 1, P2 1, P3 1 (Grep, finding 4).

## Fit for a ~$3k account
- This is tooling only. It does not change the bot's trade decisions, sizing, cash buffer or reject codes, and nothing touches a broker.
- What it protects: RI-002's guardrails stop the real-quote backtest from counting calls sold across unknown earnings windows (EARNINGS_UNKNOWN), which is how a small account avoids earnings-gap assignment risk in the research numbers. RI-013 keeps before/after effects complete [repo: logs/recurring-issues.md RI-002, RI-013].
- Cost: about 1-2 minutes of local CPU per daily audit; no data fees, commissions or taxes.

## Open questions
1. Copy method: a `git worktree add --detach <tmp> <sha>` of main, as A1 did today, or a stdlib `shutil.copytree` of the working tree? The worktree tests committed code and needs `worktree remove --force` and `prune`. The copytree tests uncommitted edits too and never touches `.git` (13, 14, 16). The request says "scratch copy/worktree", so either is allowed: R2/R3 to decide. A1's daily use is on main's SHA, which favours the worktree. I1 and I2 on an open branch may want copytree.
2. P1 replacement form and P3 replacement: both are proposed from the RI text and the code, not copied from A1's or I3's scripts (findings 10, 12). I2 has to measure their counts. A1 should say whether its P1 kept the `if`.
3. Target test for P1 and P2: A1's 2026-11-18 line does not name one (logs/audit/2026-11-18.md L45-46). The proposals (findings 10, 11) need A1's or R3's OK.
4. Scope: only P1-P3 (the request's minimum), or also the 13 or so anchor-shaped probes in section C? Those need anchors rebuilt from 004/005/007/014/041/046/052/059 work files, roughly one I1 lookup each. The CLI probes (RI-007, RI-010) need a second entry type, which could be a follow-up item.
5. Is `ccbot` installed in the environment (editable or otherwise)? UNVERIFIED. Trap 28's assert covers it either way.
6. Should the probe table live in the script (a Python list) or in a data file next to it? The request asks for "one entry per probe" and nothing more. R3 to fix the format, and the a1-auditor.md line should name the exact command and say to paste its output.
