# 02 Improvements - 109
## What past logs say
- request.md: EFFICIENCY, FULL, opened by A1. "Done looks like: Each site's off-by-one mutant fails a named test." The request names 14 sites (from logs/audit/2026-11-25-102.md L46-47, residual (a)).
- logs/audit/2026-11-25-102.md L33-37: 102's own mutants were whole-constant shifts only (VERDICT 71->72, SUITE 87->86, CHECKLIST 41->42), and each failed one named `test_from_cutoff_boundary` id. No per-site operator mutant was run. tests/test_pipeline_check.py L5861-5864 says the same in the FROM_ROWS comment ("Pinned against shifts only, not against per-site operator mutants (03 Residual a)").
- logs/recurring-issues.md RI-010 (L119) lists "14 cutoff sites -> 109" as a near miss, not counted. RI-001 (L7-22) is the "asserted, never measured" root cause. R1 measured 17, not 14. My own Grep of scripts/check_pipeline.py for `int(...) >=|< *_FROM` returns code lines 822, 825, 835, 838, 1043, 1060, 1066, 1077, 1098, 1108, 1133, 1150, 1165, 1185, 1396, 1518, 2028. That is 17, the same as R1 2.1. Lines 490 and 557 match only in comments.
- logs/efficiency/2026-11-25.md L3 runs 107 ("python -B for mutation runs") today. That item affects how 109's 34 mutants are run (see AGAINST 3). A1 ran the 102 mutants with `PYTHONDONTWRITEBYTECODE=1` (102 audit L29).
- No earlier attempt at 109: a Grep of logs/ for `\b109\b` finds only the RI-010 near miss, logs/audit/2026-11-24.md L85, the two logs/efficiency lines and R1's research log line.

## 3 ways FOR
1. **Do all 17 sites, not the request's 14, and make the census part of "Done looks like".** This is the RI-001 fix. The request's count of 14 was asserted, and R1 measured 17 (my Grep agrees: 17 code lines). S11-S13 (ROUND_HEADING, ROUND_BUILD, SCRATCH) are already pinned on both sides (R1 table 3), so moving to 17 costs only census rows, not new fixtures. Improvement to R1 4.4: R1's census regex matches only `int(<x>) >=|< NAME_FROM`. It would not see a future site written as `NAME_FROM <= int(x)`, `int(x) > NAME_FROM - 1`, `> NAME_FROM`, or `n >= NAME_FROM` without `int(`. An `ast` walk over `Compare` nodes that counts every comparison with any `*_FROM` Name on either side, minus the one known non-integer name UNTRACKED_FROM (L533), closes that hole. Today it should still give 17 (reasoning: no other `*_FROM` comparison appears in the Grep, and L490/L557 are comments, which `ast` never sees). UNVERIFIED until the test runs.
2. **The 6 missing rows are cheap. 3 of them need no git and extend fixtures that already exist.** Reasoning from the code I read:
   - S9 (L1098): add `("090", True)` to the existing `test_batch_not_computable_strict_from_090` parametrize (tests L4531), next to `("990", True)` and `("089", False)`. 090 is under fewer cutoffs than 990 (ROUND_HEADING 92, SCRATCH 97 and ROUND_BUILD 99 do not apply), so the exact `INCOMPLETE: 090 (LOG BATCH not computable: ...)` assert should hold. UNVERIFIED.
   - S15 (L1396): add one `23:10 | I2 | 045 | ...` line to `test_log_line_after_its_commit_is_flagged` (tests L521-522) and assert `"045 I2 (2026-11-04 23:10"` in the LOG TIME line. Its 044 line already kills the FROM-1 side (L538).
   - S16 (L1518): add a new pair at 045 / 044 for `batch_log_items`.
   - S7 and S8: give `_timed_repo` (L4484) an `item` parameter, since it hardcodes "990", and run it at 090 (TIMED) and 076 (TESTS). The expected texts are already in the code: `TIMED_FROM (090): judged by untimed I2 form` (L1072) and `TESTS_FORMAT_FROM (076): judged by I2_BEFORE` (L1086).
3. **Pin S16's FROM-1 side with a fixture that would actually be evaluated, and assert `checked`, not only `flagged_ids`.** In `batch_log_items` an item with no I2 line is skipped before any counting (L1521-1523: `if not i2 and not bad_logs: continue`). So a bare 044 dir is skipped by the I2 rule even under the site-local mutant `int(item) < 44`, and that mutant survives. The 044 row must be the same 083-shaped flagged item as the 045 row. Its expected result is `checked == 0` and `"044" not in flagged_ids`, and under the mutant both change (`checked` is incremented at L1525, L1529 and L1557). Also update the FROM_ROWS comment (tests L5861-5864), which says "not against per-site operator mutants". After 109 that sentence would be stale. Use R1's `<CONSTANT>@<check>-FROM` ids (R1 4.3) so every row names its site without a line number.

## 3 ways AGAINST
1. **S7 and S8 on the FROM-1 side are equivalent mutants. Writing tests to "kill" them adds fixtures with no behavior behind them.** My reasoning from L1066-1094 confirms R1 3.3. At 089 under the S7-local `>= 89`, "I2" is in `bad` only if some I2 line fails the untimed form, because S2 (L825) still applies timed only from 090. Then `all(log_fields_ok(..., timed=False))` over own_i2 is False, the TIMED branch is not entered, and control reaches the same `elif` as unmutated code. The S8 case at 075 is the same: `bad` already means "fails I2_BEFORE", and the gate's re-check is I2_BEFORE, so `bad` does not change. Forcing the git-failure `note` path (L1069/L1079) to make these visible would test `_rule_seen` failure handling, not the cutoff. Recommendation: one documented "equivalent" row per site in the census table (with this reasoning chain), not a test. Then the mutant count becomes 34 - 2 = 32 killable (R1 Numbers).
2. **3 of the 6 new rows (S7, S8, S15) are git fixtures. They skip without git and they add suite time.** S7, S8 and S15 can only be seen through `_rule_seen` or `git blame` (L1068, L1078, L1386). Where git is missing they skip (`NO_GIT`, or `skipif(shutil.which("git") is None)` at tests L514), so a guardrail row can be silently absent. Each row builds a repo and runs check_pipeline.py as a subprocess. The suite is already 1011 passed in 110.00s (102 audit L41), and LOG BATCH's per-round bound already looks at 74-93 s runs (check_pipeline.py L1503). The added seconds have not been measured (UNVERIFIED). Mitigation: put the git rows in the existing git tests (S15 is one more line in an existing repo, so no new repo is built) and give only S7/S8 new repos.
3. **Running 32-34 hand mutants is the costly part, and stale bytecode can produce false kills or false survivals.** "Done looks like" needs I2/I3 to apply each site mutant, run the tests and name the failing id. That is up to 34 runs of tests/test_pipeline_check.py, done by hand. The 102 audit ran only 3 (L33-35). If a mutate/restore happens within the same mtime second, a cached `.pyc` can be imported instead of the edited source. That is item 107's subject, run today (logs/efficiency/2026-11-25.md L3), and A1 avoided it with `PYTHONDONTWRITEBYTECODE=1` (102 audit L29). If 109 is built before 107 lands, 05/06 must state the bytecode setting for every mutant run. Otherwise a "killed" claim may not be reproducible (RI-005/RI-006 pattern: numbers not re-derived). Reasoning chain, not run.

## Findings by language
Languages: N/A (no new external claims). 109 is an EFFICIENCY item. Its fix adds tests and a census inside this repo, and it adds or changes no fee, rule, market statistic or other outside fact. R1's two pytest-doc citations support only test syntax, which this file does not extend.
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
- S16 FROM-1: a 044 fixture with no I2 line is skipped at L1521-1523, so the `< 44` mutant survives. The fixture must be 083-shaped and the test must assert `checked == 0`.
- Census regex: `int(...) >=|< NAME_FROM` misses reversed, `>`/`<=`, `- 1` and non-`int(` forms. Prefer an `ast` Compare walk, with UNTRACKED_FROM (a SHA, L533) excluded by name.
- Scope mismatch: the request says 14, the code has 17. R3 should restate "Done looks like" as 17 sites plus a census, or record why 3 are left out (they are already pinned).
- S7/S8 FROM-1 are equivalent (reasoning above). Document them, don't test them. The killable count is 32, not 34.
- `_timed_repo` hardcodes item "990" (tests L4491). It needs an item parameter for the 090/076 rows, and the existing `test_timed_gate` must keep passing unchanged.
- S15's 045 line: check that an I2 line for an item with no work/045 dir does not change the test's other asserts (ORPHAN LOG, item 047, may also fire). Exit code 1 is already expected. UNVERIFIED.
- FROM_ROWS comment (tests L5861-5864) becomes stale after 109. Update it in the same change.
- Mutation runs: state the bytecode setting (`python -B` / `PYTHONDONTWRITEBYTECODE=1`, item 107) for every one of the site mutants in 05/06.
- Every "kills/none/equivalent" in R1's section 3 and in this file is from reading code. All are UNVERIFIED until I2/I3 run the mutants.

Log fields: 3 for / 3 against | languages: N/A
