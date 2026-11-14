# 07 Audit task - 061
A1, please check:
- **Pipeline checks.**
  - `check_handoff.py 061` → PASS.
  - `check_pipeline.py` → 061 awaiting A1.
  - 06 Verdict line reads PASS round 2 (FAIL round 1).
- **Merge-commit requirement (RI-007, item 053 gap (c)).**
  - On the branch, `UNTRACKED CHANGE: 49680f8 ...; bdd67c9 ...; 20b89e7 ...` keeps
    `test_repo_pipeline_has_no_skipped_items` red. Those are 061's RESEARCH ONLY commits of 2026-11-13.
  - It clears on main only if the PR lands as a merge commit (`--no-ff`). I3 probed this on a scratch merge with
    origin/main 29a2b28: exit 0, `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`.
  - A squash or rebase merge brings it back. Re-run `check_pipeline.py` on main after the merge.
  - Decide whether RI-007 occurrence 6 (062) is settled by this.
- **Open question for the person: the cost-basis floor.**
  - It alone flips A2/A4 to pass. Floor on: 250 calls, A2 13/17. Floor off: 955 calls, A2 8/17, A4 fail.
  - It kept T to 1 call in about 7 years, because the basis was set on 2020-01-06, before the COVID drop.
  - A1 fails in every run, so the scale-up gate stays closed either way.
  - No bot change was made. Confirm that 01 puts this to the person (proposed rule 8, and the Verdict table) and
    that it is raised in the daily report.
- **Earnings hole (RI-002 shape).**
  - BAC, CSX and USB have no earnings date before April 2020, and 5 stocks have gaps of more than 120 days. An
    unknown date inside a call's life is read as "no earnings".
  - It is accepted as a labelled limitation with measured impact: 247 vs 250 calls, no A row changes.
  - Decide whether it counts as an RI-002 occurrence.
- **Reproducing.**
  - `python3 work/061/diag_keep.py start` and `... earn` (run from the repo root, about 2-3 min each) should
    reproduce 01's floor and start-date table and the earnings impact.
  - The script is under work/, outside CODE_PATHS, so check_pipeline doesn't check it. Decide whether work/*.py
    should count as code. The script has a dead `or True` branch; its effective rule matches 01.
- **Scope.** `git diff --stat` of bot, rules, screen, costs, expiries, pricing, missing and config/ across 061 is
  empty.
- **Mutation spot-check.** Optional. The suggested probe is Monte Carlo `.fillna(0)` →
  `test_monte_carlo_no_fill` fails, or basis floor off → `test_basis_floor` and `test_real_counts_bac` fail.
A1 result: PASS (2026-11-14, logs/audit/2026-11-14-061.md: A1 re-ran on 3fd5db8: pytest 292 passed, 1 failed (known UNTRACKED CHANGE line for 49680f8/bdd67c9/20b89e7), 1 skipped; check_handoff 061 PASS; every 01 headline recomputed from reports/real; diag_keep.py start and earn reproduce 01 exactly; 3 mutations each fail a test; scratch merge --no-ff onto origin/main 29a2b28 -> check_pipeline exit 0, UNTRACKED CHANGE none; land PR #26 as a merge commit only)
