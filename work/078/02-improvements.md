# 02 Improvements - 078

## What past logs say
- **074's own audit is the source of all three parts.** logs/audit/2026-11-18-074.md gives P1 (remaining GUARDED probes, L77), P2 (skip gap, L78-82) and P3 (the fixed `code check: n/a` text, L83). The mutant table (L51-61) names two survivors: `== "failed"` -> `!= "passed"` (9 passed) and "baseline target-status check removed" (9 passed). A1 also checked the shipped code by hand: a `pytest.skip("x")` replacement gives NOT HELD, exit 1 (L63) [repo: logs/audit/2026-11-18-074.md].
- **074/02 AGAINST 3 still applies.** A green probe list shows only that each hand-picked mutant is caught. It does not show that the root cause is covered (RI-002 escalated three times through paths no probe touched) [repo: work/074/02-improvements.md L36-38].
- **074/02 put the CLI/fixture probes (RI-007, RI-010) out of scope** because they needed a second entry type [repo: work/074/02-improvements.md L27]. R1 finding 20 says the fixture tests added by 064 and 049 now make anchor-shaped probes possible for both. I agree, with the caveat in AGAINST 3.
- **The recorded probes in logs/recurring-issues.md, compared with R1's N1-N6:**
  - RI-011 L132: "merge-tree diff disabled (`HEAD...ref` only) -> `test_criss_cross_branch_lists_only_its_own_changes` fails (1 failed, 69 passed)". This is the same failure mode as N1.
  - RI-012 L139: "bare `"429" in low` restored in `_rate_limited` -> ... (1 failed, 292 passed)". This is the same as N2.
  - RI-007 L85: the 064 GUARDED-again condition is a *positive* probe on main ("RESEARCH ONLY item with 01 plus work/<ID>/diag.py ... gives `RESEARCH CODE: <ID>`"), not a mutation. No later RI-007 status line records it as met.
  - RI-010 L119: the recorded probe is the CLI `--log I2 999 "x"` -> refused, exit 2.
  - RI-009 L109: the recorded result is that three tests pass on main. No mutation is recorded.
  - So only N1, N2 and N3 reproduce a recorded A1 probe. N4, N5 and N6 are new mutations with `recorded: none` [repo: logs/recurring-issues.md].
- **064 is on main.** RI-007's text last says "PR #28 open, unmerged" (2026-11-16). PR #30 merged 2026-11-17 23:39 UTC (RI-013 L144), and logs/audit/2026-11-17.md L8 says "Merging #30 merges #28 and #29 too". So the 064 lines R1 uses (`_is_code`, L311) should be on origin/main. I read this in the logs and did not check it on main: UNVERIFIED until I2 greps origin/main.
- **probe_guardrails.py itself is not on main.** logs/audit/2026-11-19.md L47 ran it "from PR #32 head" with `--ref origin/main`. PR #32 is open (logs/audit/2026-11-18.md L60). So today the PROBES list comes from the branch, and the anchors are matched against main (see AGAINST 2).
- **Language precedent:** 074 (the same script) logged `languages: N/A` (logs/research/2026-11-18.md L10), as did the tooling items 045, 049, 052, 067 and 070 (work/074/02 L41).

## 3 ways FOR
1. **Pin the skip case at two levels, so the mutant dies even where git is missing.** Every fixture test in tests/test_probe_guardrails.py carries `@NO_GIT` (L80, L95, L139, L150, L191). R1's fixtures (a) and (b) would also need git. So on a machine without git both survivors live again, and the suite shows only skips. That is the RI-002 failure mode this item cites.
   - Keep R1's (a) and (b) as written. (a) is the mutated run skipping the target: `NOT HELD`, `1 skipped`, `failed: no`, exit 1. (b) is the baseline skipping the target: `ERROR (baseline: target skipped)`. Put them in one new test so `TOTAL: 13 probes` (L130) does not change.
   - Also add git-free `classify` cases to `test_classify_missing_or_bad_junit` (L172-188), which already builds junit by hand:
     - (i) a target `<testcase>` holding `<skipped type="pytest.skip" message="x"/>`, rc 0 -> `NOT HELD`;
     - (ii) the strict-xfail XPASS shape, `<skipped message="xfail-marked test passes unexpectedly"/>`, rc 1 -> `NOT HELD`.
   - Both shapes come from pytest's writer: `append_skipped` writes `ET.Element("skipped", type="pytest.skip", ...)`, and `append_failure` with `wasxfail` writes `self._add_simple("skipped", "xfail-marked test passes unexpectedly")` [https://docs.pytest.org/en/stable/_modules/_pytest/junitxml.html, fetched 2026-11-19]. Case (i) kills `!= "passed"` with no git. Case (ii) pins R1 finding 4's fail-safe reading of XPASS.
   - The "baseline status check removed" mutant lives in `_run_probe` (L224-231), so only the git fixture (b) can kill it. That is acceptable: on a machine without git the script exits 2 anyway (L251-253).
   - Done-looks-like test for I2/I3: re-run A1's two mutants (logs/audit/2026-11-18-074.md L60-61) and show each one failing at least one test.
2. **Make the per-entry reason a checked claim, not just moved text (RI-010: "a check that exists only in text no script runs").** Moving the string into each entry fixes P3's false sentence, but a new entry could still carry a false reason, and nothing would notice.
   - Take R1 finding 10's shape: `module` or `no_module_reason`, and with neither, `ERROR (probe entry lacks module or no_module_reason)`.
   - Then add two cheap structural checks in `test_shipped_probes_well_formed`, where the anchors are already checked against the working tree:
     - (a) the reason names the probe's own file (`p["file"]` or its basename appears in `no_module_reason`). This is exactly the check that would have caught the fixture's "tests run pkg/mod.py by path" sentence;
     - (b) the test file's text contains the mutated file's basename.
   - Grep today: `check_pipeline.py"` / `diff_reports.py"` / `tickers.json` occur 58 times in tests/test_pipeline_check.py, once in test_diff_reports.py and twice in test_missing_inputs.py. So (b) holds for all five reason-carrying entries [repo: Grep count over tests/, 2026-11-19].
   - (b) is a weak proxy. It shows that the test mentions the file, not that it loads the worktree copy, and the reason text should not claim more.
   - A stronger option for the four check_pipeline probes (R3/I1 to choose): an optional `module_path: "scripts"` key, so that `module_file` puts `wt/scripts` on sys.path and imports `check_pipeline`. That is the same import `_cp()` does (tests/test_pipeline_check.py L862-865). It gives a real `code check: check_pipeline is scripts/check_pipeline.py in the worktree` and avoids R1 finding 12's namespace-package problem. It costs one more key and one fixture case. Reasoning only, not run.
3. **Close the non-.py hole before shipping N3, and record measured per-file counts.**
   - The only content check `_run_probe` runs on a mutation is `compile()` for `.py` files (L207-211). For `config/tickers.json` (N3), a malformed replacement would make `json.loads` in `test_ticker_fields_cover_file_and_code` (tests/test_missing_inputs.py L255) raise during the call phase. pytest writes that as `<failure>` (`if report.when == "call": reporter.append_failure(report)`) [https://docs.pytest.org/en/stable/_modules/_pytest/junitxml.html], and the probe would print HOLDS for the wrong reason (R1 trap 21).
   - Fix: add a `.json` branch next to the compile check, `json.loads(mutated)` -> `ERROR (mutation is not valid JSON: <msg>)`. Pin it with one fixture probe in the mixed run, which changes that test's TOTAL line, or in the new skip test. On invalid input `json.loads` raises `JSONDecodeError`, a subclass of `ValueError` [https://docs.python.org/3/library/json.html; cited by R1, not re-fetched].
   - The fix is about 4 lines, inside the request's "anchor-shaped first" scope. Without it, N3 is the one probe whose HOLDS can't be trusted.
   - For `recorded` (R1 open question 4), use what I2 measures on origin/main, for example `2026-11-19 (078/05): <n> failed, <m> passed`. Do not use the RI text's counts. RI-012's "292 passed" is a whole-suite count (R1 finding 15), and RI-002's "22 passed" is from before `test_drop_each_input` was parametrized over MISSING_POLICY (tests/test_missing_inputs.py L238). Copying them would print a `recorded` that no run of the probe's own file can reproduce, which A1 would then read as drift.

## 3 ways AGAINST
1. **Daily runtime roughly doubles, mostly from tests/test_pipeline_check.py.**
   - That file has 112 `def test_` functions today (Grep count; parametrized cases not counted). At 062 it had 52 tests, which took 7.77 s (work/062/05-build-report.md L56, via R1).
   - Scaling linearly gives 7.77 / 52 = 0.149 s per test, x 112 = 16.7 s per run, x 5 runs (1 baseline + N1, N4, N5, N6) = 84 s. Add test_webull_sandbox.py and test_missing_inputs.py (1 baseline + 1 mutated run each, sizes not measured). Today's 3 probes take 104.5-127.7 s (logs/audit/2026-11-18-074.md L43; logs/audit/2026-11-19.md L47), so the total would be about 190-250 s.
   - Every figure past 104.5-127.7 s is an UNVERIFIED linear guess. git-fixture tests do not scale linearly with test count, and the 600 s per-run timeout (L246) is not at risk on these numbers.
   - Mitigation: I2 records each new probe's seconds from the script's own per-probe timing in 05, and a1-auditor.md's runtime note is updated to the measured total. No code change.
2. **Anchors have to match two different trees, and the shipped test checks only one.**
   - `test_shipped_probes_well_formed` reads `REPO / p["file"]`, which is the working tree (L209-210). The daily run is `--ref origin/main`.
   - Before 078 is built, 076, 077 and 079 all change scripts/check_pipeline.py (brief L3), and 077 point 2 (`BRANCH FAIL:`) is likely to edit `open_branches()`, where three of R1's anchors are (L519 N1, L539 N6, L551 N4) [repo: work/077/request.md L10; scripts/check_pipeline.py L498-578].
   - If 077 reformats any of those lines, an anchor copied from main fails the well-formed test on the branch. An anchor copied from the branch gives `ANCHOR MISSING (count 0)` in every daily run until the PR merges. PR #32 has been open since 2026-11-18, and items have sat in PR for days (logs/audit/2026-11-17.md L8: PR #28 3 days).
   - Cost of getting it wrong: a red daily line that invites the "loosen the anchor" fix 074/02 AGAINST 2 warned about.
   - Mitigation: I2 greps each anchor on `git show origin/main:<file>` and on the built branch, and pastes both counts in 05. It runs the script with `--ref origin/main` and with `--ref HEAD`, and both must print `9 hold`. Any anchor that differs between the two is a finding, not something to tune.
3. **Three of the six probes delete a whole feature, so they prove less than "GUARDED" suggests.**
   - N4 (`clashes.append(item)` -> `pass`), N6 (`rules = []`) and, to a lesser degree, N5 remove the output line itself. Almost any test that reads that line catches them.
   - They do not probe the subtle condition each RI was about:
     - RI-009's real bug was two items with one ID, and its subtle guard is the merge-base condition at L549.
     - RI-010's 048 cause was a branch cut before the rules changed and lines typed by hand. N6 only checks that the `RULES BRANCH:` line can say something.
     - RI-007's recorded 064 condition is a positive probe on main (`RESEARCH CODE: <ID>`), which no mutation replaces.
   - A finer N4 (drop the `and all(... cat-file ... for b in bases)` term at L549) relies on L280 (`040 (origin/fix)` not a clash). That only fires if the shared 040 request text differs between main and the branch at the time of the check (L550, `theirs[0] != mine.read_text(...)`). I did not trace the fixture far enough to know whether it does, so whether the finer mutant is killed is UNVERIFIED.
   - Risk: A1's daily "9 hold" reads as full coverage of RI-007/009/010, the same over-reading 074/02 AGAINST 3 named.
   - Mitigation: ship the coarse N4/N6 as R1 proposes, since they are honest and cheap. Give them ids that say what they cut (for example `RI-009-037-clash-line`, `RI-010-049-rules-line`). The a1-auditor.md sentence that the script covers only the listed probes stays, and the RI-007 positive probe stays an A1 task.

## Findings by language
Languages: N/A (no new external claims). 078 is an EFFICIENCY item: fixture tests, a probe-entry key and six data entries in a repo-internal audit script. It adds or changes no fee, trading rule, market statistic or trade behaviour (R1 "Fit for a ~$3k account": tooling only). The only outside facts it uses are pytest, Python and JSON tool behaviour, cited to official English docs above (the junitxml source was re-fetched 2026-11-19). This follows the precedent for 074, the same script, which logged `languages: N/A` (logs/research/2026-11-18.md L10).
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
1. **All-skipped exit code.** R1 finding 7 is still UNVERIFIED. My search found only the exit-code pages, which do not say what code a run where every test skips gets. R1's fixture (b) avoids the question by adding a passing `test_ok`. Keep it, and do not write a fixture file that holds only skips.
2. **The fixture tests are all `@NO_GIT`.** Without git they skip, so the git-free `classify` cases (FOR 1) are the only guard on that machine. I3 should run the `!= "passed"` mutant once with those cases alone (`-k classify`) to show they kill it.
3. **N3 must be valid JSON, or it gives a false HOLDS** (FOR 3). Even if the `.json` check is not built, I2 must show in 05 that the mutated tickers.json parses (`python3 -c "import json; json.load(open(...))"` in the scratch worktree).
4. **The N3 anchor is two lines and depends on indentation** (`"F": {\n    "asset_type": "stock",`). A reformat of tickers.json, or a key added before `asset_type` in F (data edits happen there: RI-007 occurrence 3ba835e), breaks it loudly. Acceptable, but I1 should know.
5. **Baselines are shared.** Four probes share one tests/test_pipeline_check.py baseline (L221-223), so one red or skip-turned-fail test there turns all four into ERROR (R1 trap 23). The file has a REPO-state test (L849-854, the shallow check, skipped by an early `return` when the repo is shallow). It runs against the worktree's shared .git and should pass, but whether it does in a detached worktree of origin/main is UNVERIFIED until I2's baseline line.
6. **Anchors on main vs on the branch** (AGAINST 2). Paste both grep counts per anchor, and run both `--ref` values.
7. **`recorded` counts** (FOR 3). Use per-file counts measured on main, labelled with the date and 078/05. N2's RI figure is whole-suite.
8. **`test_shipped_probes_well_formed` hard-codes 3** (L205-206, L214-217). Update it to 9 and to the new target list. It should also require `module` or the reason key on every entry (R1 finding 10 iii).
9. **Moved reason text must not over-claim.** For example, "imports check_pipeline via `_cp()` (tests/test_pipeline_check.py L862-865) and runs it by path via `_run` (L51-54)" is true. "Verified to load the worktree file" is not, unless the `module_path` option in FOR 2 is built.

Log fields: 3 for / 3 against | languages: N/A
