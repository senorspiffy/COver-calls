# 01 Research brief - 109
## Question
Which `*_FROM` cutoff comparison sites in scripts/check_pipeline.py have no test at FROM (and at FROM-1) that fails when that one site's comparison is moved off by one (`>=` -> `>`, `<` -> `<=`, or the site alone compared to FROM-1)? What fixture would pin each gap with a named parametrized id? Source of the ask: logs/audit/2026-11-25-102.md L46-47 (residual (a)); 102 pinned the 7 constants against whole-constant shifts only (tests/test_pipeline_check.py L5861-5864).

Recurring issues read: RI-001 (a rule asserted but never measured; here "the cutoff is pinned" was measured only for shifts) and RI-010 (the 102 near miss "14 cutoff sites -> 109", logs/recurring-issues.md L119). No log has earlier work on 109 (Grep of logs/ for 109: only that RI-010 mention). work/102/01-research.md finding 2.8 already named this mutant class as an open question.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
### 1. Mutant classes
1.1 A per-site comparison mutant is the standard "comparison operator" mutation: "The comparison operator mutates comparison operators to catch off-by-one and boundary condition bugs"; the table maps `>=` to `>` and `<` to `<=`. [https://pytest-gremlins.readthedocs.io/en/latest/guide/operators/]
1.2 A whole-constant shift is the separate "boundary operator": "shifts integer constants in comparisons by ± 1 to catch off-by-one errors". Such mutants survive when "Tests do not check boundary values (e.g., exactly 18)". [https://pytest-gremlins.readthedocs.io/en/latest/guide/operators/]
1.3 At a single site, `>= FROM` -> `> FROM` and `< FROM` -> `<= FROM` both change only the result for ID == FROM. So only a FROM row that goes through that site can kill them. A site-local `>= FROM-1` changes only ID == FROM-1, so it needs a FROM-1 row through that site. This is inference from the comparison semantics (Python integer `>=`/`<`), not run.
1.4 A test that builds its ID from the constant (`f"{cp.TIMED_FROM:03d}"`, tests/test_pipeline_check.py L4474-4476) cannot kill a shift (work/102/01-research.md 2.2), but it does kill a site-local mutant, because the constant itself is unchanged. Inference, not run.

### 2. The sites today (Grep `int(...) >=|< *_FROM` in scripts/check_pipeline.py)
2.1 There are 17 code comparison sites, not 14. The 14 that 102's A1 counted belong to the 7 constants that 102 pinned. 3 more belong to constants that 102 left out: ROUND_HEADING_FROM, SCRATCH_FROM and ROUND_BUILD_FROM. L490 and L557 match only in comments. UNTRACKED_FROM is a commit SHA used as a walk cutoff, not an integer comparison (L533, L1917). [scripts/check_pipeline.py]
| # | Constant (value) | Line | Function / check | Comparison |
|---|---|---|---|---|
| S1 | TESTS_FORMAT_FROM (76) | L822 | log_fields_ok, I2_BEFORE branch | `int(item) < ` |
| S2 | TIMED_FROM (90) | L825 | log_fields_ok, I2_TIMED branch | `int(item) >= ` |
| S3 | TESTS_FORMAT_FROM (76) | L835 | log_hint, LOG_HINT_BEFORE | `int(item) < ` |
| S4 | TIMED_FROM (90) | L838 | log_hint, LOG_HINT_TIMED | `int(item) >= ` |
| S5 | CHECKLIST_FROM (41) | L1043 | incomplete, entry gate | `int(item_dir.name) < ` |
| S6 | LOG_CHECK_FROM (45) | L1060 | incomplete, log-format check | `>= ` |
| S7 | TIMED_FROM (90) | L1066 | incomplete, TIMED `_rule_seen` gate | `>= ` |
| S8 | TESTS_FORMAT_FROM (76) | L1077 | incomplete, TESTS `_rule_seen` gate | `>= ` |
| S9 | TIMED_FROM (90) | L1098 | incomplete, BATCH_STRICT entry | `>= ` |
| S10 | SUITE_FROM (87) | L1108 | incomplete, Suite check | `>= ` |
| S11 | ROUND_HEADING_FROM (92) | L1133 | incomplete, round headings | `>= ` |
| S12 | ROUND_BUILD_FROM (99) | L1150 | incomplete, build-round headings | `>= ` |
| S13 | SCRATCH_FROM (97) | L1165 | incomplete, Scratch dir | `>= ` |
| S14 | VERDICT_FROM (71) | L1185 | incomplete, verdict line | `>= ` |
| S15 | LOG_CHECK_FROM (45) | L1396 | log_time_issues (LOG TIME, git blame) | `int(m[4]) >= ` |
| S16 | LOG_CHECK_FROM (45) | L1518 | batch_log_items (LOG BATCH) | `int(item) < ` |
| S17 | WHOLE_DIFF_FROM (70) | L2028 | real-data field | `int(item) < ` |
2.2 Count check: the 7 constants have 3 (TESTS_FORMAT: S1, S3, S8) + 4 (TIMED: S2, S4, S7, S9) + 1 + 3 (LOG_CHECK: S6, S15, S16) + 1 + 1 + 1 = 14. That matches A1's 14. Adding S11-S13 gives 17.

### 3. Existing coverage per site (from reading the tests; every "kills" / "survives" is UNVERIFIED until I2/I3 run the 17 x 2 site mutants)
| # | FROM row (site `>=`->`>` / `<`->`<=`) | FROM-1 row (site-local FROM-1) |
|---|---|---|
| S1 | kills: `test_i2_tests_field_cutoff` (076 `9/9` -> exit 2, L732-733) | kills: same test (075 `9/9` -> exit 0, L729) |
| S2 | kills: `test_from_cutoff_boundary[TIMED-FROM]` (090 untimed -> exit 2, L5874, L5884-5889) | kills: `[TIMED-FROM-1]` (089 -> exit 0); `test_log_i2_untimed_refused_from_090` L4464 |
| S3 | kills: `test_old_i2_hint_fits_old_format` (log_hint 076 == LOG_HINT, L768) | kills: same test (075 == LOG_HINT_BEFORE, L767) |
| S4 | kills: `[TIMED-FROM]` asserts `"{TIMED_HINT}"` in err (L5888); `test_timed_hint_fits_timed_format` L4475 | kills: `test_timed_hint_fits_timed_format` L4476 (TIMED_FROM-1 computed, unchanged under a site mutant) |
| S5 | kills: `[CHECKLIST-FROM]` (041) | kills: `[CHECKLIST-FROM-1]` (040) |
| S6 | kills: `[LOG_CHECK-FROM]` (045) | kills: `[LOG_CHECK-FROM-1]` (044); `test_malformed_log_line_is_incomplete` L504-511 |
| S7 | **none**: TIMED gate tests use 990 (`_timed_repo` L4484-4495, `test_timed_gate` L4499-4513) | equivalent (see 3.3) |
| S8 | **none**: TESTS gate tests use 150 (SEEN_150 L2743) and repo item 083 (L207) | equivalent (see 3.3) |
| S9 | **none**: `test_batch_not_computable_strict_from_090` uses 990 / 089 (L4531) | kills: same test, 089 row |
| S10 | kills: `[SUITE-FROM]` (087) | kills: `[SUITE-FROM-1]` (086) |
| S11 | kills: `test_stray_round_heading_is_incomplete[P1-at-cutoff-092]` (L5176) | kills: `test_read_or_unnamed_heading_is_not_stray[N3-below-cutoff]` (091, L5202) |
| S12 | kills: `test_round_build_heading_is_incomplete[099-at-cutoff]` (L5259) | kills: same, `[098-below-cutoff]` |
| S13 | kills: SCRATCH `ids=["FROM", "FROM-1"]` 097 (L5586) | kills: same, 096 |
| S14 | kills: `[VERDICT-FROM]` (071) | kills: `[VERDICT-FROM-1]` (070) |
| S15 | **none**: `test_log_line_after_its_commit_is_flagged` has only 150 and 044 (L518-538) | kills: same test (`"044" not in line`, L538) |
| S16 | **none**: no `batch_log_items` test at 045 (fixtures use 999, 990, 089, 079; L3113-3204, L4531-4566) | **none**: no row at 044 |
| S17 | kills: `test_t7b_cutoff_edge_item_070_is_checked` (tests/test_real_data_field.py L126-134) | kills: `test_t7_items_before_cutoff_are_not_checked` (069, L117-121) |
3.1 Totals: of 17 sites, 12 have both sides covered today (S1-S6, S10-S14, S17). 5 have no FROM row: S7, S8, S9, S15, S16. 1 also has no FROM-1 row: S16.
3.2 S7 and S8 behave the same under the mutant in a non-git fixture. With no git, `_rule_seen` returns `(None, "")`, so both the gated path and the skipped path keep `I2` in `bad` with the same hint (L1066-1094; non-git `(None, "")` per work/102/01-research.md 2.6). The mutant is visible only when `_rule_seen` returns False, i.e. a git fixture whose 05 was added under a RULE_FILE without that constant. Under the S7 mutant, item 090 skips the TIMED gate. It falls into the TESTS gate, where TESTS_FORMAT_FROM is seen, so it gets INCOMPLETE instead of `RULE NOT SEEN ... TIMED_FROM (090): judged by untimed I2 form`. Under the S8 mutant, item 076 skips the TESTS gate and gets INCOMPLETE instead of `RULE NOT SEEN ... TESTS_FORMAT_FROM (076): judged by I2_BEFORE`. Inference from L1066-1094, not run (UNVERIFIED).
3.3 The FROM-1 side of S7 and S8 looks like an equivalent mutant. At 089 (S7), `I2` is in `bad` only if the line fails LOG_FORMAT, so `all(log_fields_ok(..., timed=False))` is False and the gate is never entered. At 075 (S8), `bad` already means "fails I2_BEFORE" (S1), and the gate's `new_rule=False` re-check uses I2_BEFORE too, so `bad` is unchanged. In both cases no output changes. The only exception would be a git-failure `note` (L1069/L1079). Inference, not run (UNVERIFIED). R3 should decide whether these two get a documented "equivalent" row instead of a test.
3.4 S15 needs git (it reads `git blame --line-porcelain` committer-time, L1386-1399). The existing LOG TIME test already builds a repo with dated commits (L528-533), so adding a 045 line timed after the commit gives a FROM row in the same shape. Inference (UNVERIFIED).
3.5 S16 can be tested without git. `batch_log_items(work, logs, excepted)` is a plain function (L1486-1519), and `_batch_item` + `_bl` already drive it on 999 (L3108-3124). An 083-shaped flagged item at 045 (expect `flagged_ids == ["045"]`) and at 044 (expect not checked, `checked == 0`) would pin both sides. Inference (UNVERIFIED).
3.6 S9 can be tested without git. `test_batch_not_computable_strict_from_090` (L4531-4546) parametrized with `"090"` (strict) next to its `"089"` row gives the FROM row. Inference (UNVERIFIED).

### 4. Test shape and naming
4.1 pytest takes explicit ids: "we specified `ids` as a list of strings which were used as the test IDs", and "Use `pytest.param` to apply marks or set test ID to individual parametrized test." [https://docs.pytest.org/latest/example/parametrize.html]
4.2 `pytest.param(..., marks=...)` lets the git-only rows (S7, S8, S15) carry the repo's existing `NO_GIT` skip without skipping the non-git rows. Marks on single parameter sets: "It is also possible to mark individual test instances within parametrize". [https://docs.pytest.org/en/stable/how-to/parametrize.html]
4.3 Proposed id form: `<CONSTANT>@<check>-FROM` / `-FROM-1` (e.g. `TIMED@batch_strict-FROM`, `LOG_CHECK@log_batch-FROM-1`). An id holds no line number, so the ids stay stable when lines move. A design suggestion, not a sourced fact.
4.4 Census guardrail (RI-001: measure, don't assert): a test that runs a regex like `int\([^)]*\)\s*(>=|<)\s*([A-Z_]+_FROM)\b` over the check_pipeline.py source. It would count the matched sites per constant and compare that count with a hand table of site rows, so a new 18th site with no row fails. Today the regex should find 17 sites, matching the Grep in 2.1. The regex has not been run as a test (UNVERIFIED). Comment lines L490/L557 do not match it, because the comparison there is `>= TIMED_FROM` after "ID", with no `int(`.

## Numbers used (show the math)
- Sites: 14 (7 constants: 3 + 4 + 1 + 3 + 1 + 1 + 1) + 3 (ROUND_HEADING, ROUND_BUILD, SCRATCH, 1 each) = 17.
- Site mutants: 17 sites x 2 sides = 34. Covered today (by reading): 12 x 2 = 24, plus the FROM-1 side of S9 and of S15 = 26. Equivalent (3.3): S7 and S8 on the FROM-1 side = 2. Uncovered: 34 - 26 - 2 = 6. These are the FROM sides of S7, S8, S9, S15 and S16 (5) plus the FROM-1 side of S16 (1). Check: 5 + 1 = 6.
- New rows proposed: 6. 3 need git (S7 at 090, S8 at 076, S15 at 045) and 3 do not (S9 at 090, S16 at 045 and 044).
- Boundary arithmetic, rule "checked iff int(ID) >= FROM":
  - 090 >= 90 is checked. Under the mutant, 90 > 90 is false, so 090 is not checked.
  - 076: 76 < 76 is false, so 076 is new-form. Under the `<=` mutant, 76 <= 76 is true, so 076 is old-form.
  - 045: 45 < 45 is false, so 045 is checked. Under the `<=` mutant, it is skipped.
  - 044: 44 < 45 is true, so 044 is skipped. Under a site-local `< 44`, 044 is checked.

## Fit for a ~$3k account
Not applicable to trading. This is test-only pipeline work: no ticker, strike, premium, assignment, dividend, tax or commission is involved, so `ccbot/screen.TESTS` and `MISSING_POLICY` do not apply. The proposal changes only tests/test_pipeline_check.py (tests/ is in CODE_PATHS, not RULE_PATHS, per work/102/01-research.md "Fit"). It changes no rule text and no check behavior.

## Open questions
1. Scope: should 109 cover all 17 sites, or only the 14 that the request names? S11-S13 are already pinned both ways (3), so the difference is the census only.
2. S7 and S8 FROM-1: should these get a documented equivalent-mutant note, or a test that forces the git-failure `note` path?
3. The git-only rows (S7, S8, S15) skip where git is missing (`NO_GIT`). Is a skip acceptable for a guardrail row, given that I3/A1 run with git?
4. Should the census test (4.4) be part of 109's "Done looks like", so that a future site without a row fails?
5. Every "kills", "none" and "equivalent" in section 3 comes from reading the code. They are UNVERIFIED until I2/I3 run the 34 site mutants and name the failing id for each one.
