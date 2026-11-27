# 03 Research hand-off - 109
Status: READY
Scope note: FULL (request.md). Every change below is in `tests/` (CODE_PATHS, not RULE_PATHS: scripts/check_pipeline.py L529, L531). Nothing changes in scripts/, ccbot/, config/, templates/ or .claude/. R3 has no shell. Every "kills", "survives" and "equivalent" below comes from reading and tracing the code at branch daily-fixes/2026-11-25. I2 must run all 34 site mutants and I3 must re-run them (step 8).

"Done looks like" restated (request said 14 sites, the code has 17): every one of the 17 `int(<ID>) >=|< <NAME>_FROM` sites has a named test that fails under its FROM-side mutant. Every FROM-1-side mutant also fails a named test, except S7 FROM-1, which is a documented equivalent mutant. A census test fails when an 18th site is added with no row. So 33 of 34 site mutants are killed and 1 is documented as equivalent.

Recurring issues checked (item 013), all open or ESCALATED entries:
- RI-001 (ESCALATED). The request's "14 sites" was asserted. The code has 17 (Grep of `_FROM` in scripts/check_pipeline.py, code lines L822, 825, 835, 838, 1043, 1060, 1066, 1077, 1098, 1108, 1133, 1150, 1165, 1185, 1396, 1518, 2028). Every cutoff row has its boundary IDs computed in the Feasibility column and Self-check. The census (step 1) is the measure-not-assert guardrail for future sites.
- RI-014 (OPEN). The 4 git rows (steps 2, 3, 5) each use a fresh `git init` in tmp, so clone depth cannot affect them. No git call is added to scripts/.
- GUARDED entries also checked:
  - RI-002: a skipped git row is never a pass (Missing inputs). `checked == 0` is asserted, not defaulted.
  - RI-004/005: Self-check.
  - RI-006: totals are left to check_handoff.
  - RI-007: Scope FULL, test code allowed.
  - RI-009: 107, 108 and 110 also run today and may touch the same test file, so re-read line numbers after a rebase (step 9).
  - RI-010: this item is the "14 cutoff sites -> 109" near miss (L119).
  - RI-012: rows assert exact lines or exact entry text.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 Q: source is the 102 audit residual (a); FROM_ROWS comment says "shifts only" | logs/audit/2026-11-25-102.md L46-47; tests/test_pipeline_check.py L5861-5864 | VERIFIED | |
| 01 RI read: RI-010 near miss "14 cutoff sites -> 109"; RI-001 root cause | logs/recurring-issues.md L119, L7-22 | VERIFIED | |
| 01: no earlier work on 109; 102/01 2.8 named the per-site class | Grep logs/ `109`; work/102/03-handoff.md L45 (row 01 2.8) | VERIFIED | |
| 01 1.1: comparison operator quote; `>=`->`>`, `<`->`<=` | https://pytest-gremlins.readthedocs.io/en/latest/guide/operators/ (fetched 2026-11-25) | VERIFIED | The table also maps `>=`->`<` and `<`->`>`. 1.1 names a subset, which is still correct |
| 01 1.2: boundary operator "shifts integer constants in comparisons by ± 1"; such mutants survive when "Tests do not check boundary values (e.g., exactly 18)" | same URL | WRONG (in part) | The first quote is right. The "exactly 18" bullet is under the **comparison** operator. The boundary operator's bullet is "Tests do not use boundary values" |
| 01 1.3: a single-site `>=`->`>` / `<`->`<=` changes only ID == FROM; site-local FROM-1 changes only ID == FROM-1 | Python int comparison semantics | VERIFIED | |
| 01 1.4: a constant-built ID (`f"{cp.TIMED_FROM:03d}"`) kills a site mutant, not a shift | tests/test_pipeline_check.py L4474-4476 | VERIFIED | |
| 01 2.1: 17 code sites at the listed lines and constants | Grep `_FROM` in scripts/check_pipeline.py; constants L438-459, L503, L507 | VERIFIED | |
| 01 2.1 table S15: function "log_time_issues" | scripts/check_pipeline.py L1366 | WRONG | The function is `late_log_lines` (L1366-1403). S17 is in `_item_triggers` (L2012) |
| 01 2.1: UNTRACKED_FROM is a SHA walk cutoff (L533, L1917), not an integer comparison | scripts/check_pipeline.py L533, L1822, L1917 | VERIFIED (in part) | Not an integer cutoff, as stated. But it does appear in one Compare node: L1822 `cutoff != UNTRACKED_FROM` (`_note`). An ast census must exclude it by name (step 1) |
| 01 2.1: L490 and L557 match only in comments | scripts/check_pipeline.py L490 (comment line), L557 (trailing `# items >= TESTS_FORMAT_FROM`) | VERIFIED | |
| 01 2.2: 3 + 4 + 1 + 3 + 1 + 1 + 1 = 14; + 3 = 17 | 2.1 table | VERIFIED | |
| 01 3 S1: both sides killed by test_i2_tests_field_cutoff | tests L729, L732-733; check_pipeline L822 | VERIFIED (traced, not run) | |
| 01 3 S2: [TIMED-FROM] and [TIMED-FROM-1], L4464 | tests L5874-5890, L4464 | VERIFIED (traced, not run) | |
| 01 3 S3: test_old_i2_hint_fits_old_format both sides | tests L767-768; check_pipeline L835 | VERIFIED (traced, not run) | |
| 01 3 S4: [TIMED-FROM] TIMED_HINT in err; L4475/L4476 | tests L5888, L4475-4476; check_pipeline L838 | VERIFIED (traced, not run) | |
| 01 3 S5: [CHECKLIST-FROM]/[-FROM-1] | tests L5866-5867, L5892-5896; check_pipeline L1043 | VERIFIED (traced, not run) | |
| 01 3 S6: [LOG_CHECK-FROM]/[-FROM-1]; L504-511 | tests L5868-5869, L504-511; check_pipeline L1060 | VERIFIED (traced, not run) | |
| 01 3 S7: no FROM row (gate tests use 990); FROM-1 equivalent | tests L4484-4513; check_pipeline L1066-1067 | VERIFIED (traced, not run) | |
| 01 3 S8: no FROM row; FROM-1 equivalent | tests L2743, L4484-4513; check_pipeline L1077-1086, L935 | WRONG (in part) | "No FROM row" is right. FROM-1 is **not** equivalent. Under `>= 75`, item 075 with a failing I2_BEFORE line enters the TESTS gate, so `_rule_seen` runs. If the 05 anchor commit has no RULE_FILE, it returns `(None, "05 anchor <sha7> has no scripts/check_pipeline.py (item 084)")` (L935), and L1095-1096 adds that note as an INCOMPLETE entry. Real code never calls it at 075. Killable: step 3 |
| 01 3 S9: no FROM row; FROM-1 killed by the 089 row | tests L4531-4546; check_pipeline L1098 | VERIFIED (traced, not run) | |
| 01 3 S10: [SUITE-FROM]/[-FROM-1] | tests L5870-5871, L5903-5905; check_pipeline L1108 | VERIFIED (traced, not run) | |
| 01 3 S11: P1-at-cutoff-092 / N3-below-cutoff (091) | tests L5176-5177, L5202-5204 | VERIFIED (traced, not run) | |
| 01 3 S12: 099-at-cutoff / 098-below-cutoff | tests L5258-5270 | VERIFIED (traced, not run) | |
| 01 3 S13: SCRATCH ids FROM / FROM-1 (097/096) | tests L5586-5592 | VERIFIED (traced, not run) | |
| 01 3 S14: [VERDICT-FROM]/[-FROM-1] | tests L5872-5873, L5906-5909; check_pipeline L1185 | VERIFIED (traced, not run) | |
| 01 3 S15: no FROM row; FROM-1 killed by `"044" not in line` | tests L514-538; check_pipeline L1396 | VERIFIED (traced, not run) | |
| 01 3 S16: no rows at 045 or 044 | Grep tests `_bl(` / `_batch_item(`: IDs 999, 990, 089 and 079-shaped 999 only | VERIFIED | |
| 01 3 S17: t7b (070) / t7 (069) | tests/test_real_data_field.py L116-134; check_pipeline L2028 | VERIFIED (traced, not run) | |
| 01 3.1: 12 sites covered both sides; 5 without FROM row; S16 without FROM-1 | rows above | VERIFIED | |
| 01 3.2: S7/S8 mutants invisible with no git (`(None, "")`); visible when `_rule_seen` is False | check_pipeline L921-922, L1066-1094 | VERIFIED (traced, not run) | |
| 01 3.3: S7 and S8 FROM-1 equivalent except a git-failure note | check_pipeline L1066-1094, L923-938 | WRONG (in part) | S7 FROM-1 is equivalent. At 089, `"I2" in bad` means some I2 line fails LOG_FORMAT, so `all(... timed=False)` (also LOG_FORMAT below 90) is False and the gate is never entered. S8 FROM-1 is killable by the no-RULE_FILE note (L935), which a plain git fixture reaches without any git failure. That is the same shape as test_rule_anchor_without_rule_file (tests L2860-2877) |
| 01 3.4: LOG TIME test already builds a dated-commit repo | tests L528-533 | VERIFIED | |
| 01 3.5: batch_log_items is a plain function; `_batch_item`/`_bl` drive it; 083-shaped rows at 045/044 | check_pipeline L1486-1557; tests L3062-3124 | VERIFIED | |
| 01 3.6: S9 by adding `"090"` to the existing parametrize | tests L4531-4546 | WRONG (in part) | The strict branch hard-codes `"INCOMPLETE: 990 (LOG BATCH ..."` (L4543). Adding the row also needs `f"INCOMPLETE: {item} (..."`. With that change the row holds: 090 is under SUITE and VERDICT like 990, and the ROUND_HEADING, SCRATCH and ROUND_BUILD checks do not apply to it |
| 01 4.1: pytest `ids` and `pytest.param` quotes | https://docs.pytest.org/latest/example/parametrize.html (fetched 2026-11-25) | VERIFIED | |
| 01 4.2: "It is also possible to mark individual test instances within parametrize" | https://docs.pytest.org/en/stable/how-to/parametrize.html (fetched 2026-11-25) | VERIFIED | |
| 01 4.3: id form `<CONSTANT>@<check>-FROM` / `-FROM-1` | design | VERIFIED (design, adopted) | |
| 01 4.4: the census regex finds the 17 sites; comment lines don't match | the 17 code lines all read `int(<x>) >=|< NAME_FROM` | VERIFIED (traced, not run) | Superseded by the ast census (02 FOR 1, step 1) |
| 01 Numbers: 34 site mutants; 26 covered today | 17 × 2; 12 × 2 + 2 | VERIFIED | |
| 01 Numbers: 2 equivalent, 6 uncovered, 6 new rows (3 git, 3 not) | rows 01 3 S8 / 3.3 above | WRONG | 1 equivalent (S7 FROM-1) and 7 uncovered, so 7 new rows. 4 need git (S7@090, S8@076, S8@075, S15@045) and 3 do not (S9@090, S16@045, S16@044). 26 + 7 + 1 = 34 |
| 01 Numbers: boundary arithmetic 090/076/045/044 | Self-check | VERIFIED | |
| 01 Fit: tests/ is in CODE_PATHS, not RULE_PATHS | check_pipeline L529, L531 | VERIFIED | |
| 02 past logs: request is EFFICIENCY, FULL, A1, 14 sites | work/109/request.md | VERIFIED | |
| 02 past logs: 102's mutants were shifts only (L33-37); FROM_ROWS comment | logs/audit/2026-11-25-102.md L33-37; tests L5861-5864 | VERIFIED | |
| 02 past logs: RI-010 L119; Grep gives the 17 code lines | logs/recurring-issues.md L119; Grep | VERIFIED | |
| 02 past logs: 107 runs today; A1 used PYTHONDONTWRITEBYTECODE=1 | logs/efficiency/2026-11-25.md L3; 102 audit L29 | VERIFIED | |
| 02 past logs: no earlier 109 attempt; the listed matches | Grep logs/ `109`: audit/2026-11-24.md L85, efficiency 11-24 L5 / 11-25 L3, research 11-25 L9/L12, RI L119 | VERIFIED | |
| 02 FOR 1: ast Compare census, exclude UNTRACKED_FROM by name, gives 17 | check_pipeline Grep; L1822 is the one UNTRACKED_FROM Compare | VERIFIED (traced, not run) | 18 Compare nodes hold a `*_FROM` Name; 17 after the exclusion |
| 02 FOR 1: S11-S13 already pinned both ways | rows 01 3 S11-S13 | VERIFIED | |
| 02 FOR 2 S9: add `("090", True)`; exact assert should hold | tests L4531-4546 | WRONG (in part) | Same fix as row 01 3.6: the assert must use `{item}` |
| 02 FOR 2 S15: one 045 line + assert `"045 I2 (2026-11-04 23:10"` | tests L521-522, L536 | VERIFIED (traced, not run) | |
| 02 FOR 2 S7/S8: `_timed_repo` with an item param at 090 and 076; texts at L1072/L1086 | tests L4480-4495; check_pipeline L1072, L1086 | WRONG (in part) | S7@090 is right. S8@076 as written changes nothing: `_timed_repo`'s I2 line `1 files changed \| tests 1 passed` fits LOG_FORMAT at 076, so `"I2" not in bad` and no gate runs. The row needs an I2_BEFORE-form line (`tests 9/9`, which fails LOG_FORMAT per tests L732) and a RULE_FILE without TESTS_FORMAT_FROM (step 2) |
| 02 FOR 3: S16 FROM-1 must be 083-shaped (L1521-1523 skip); assert `checked`; L1525/L1529/L1557 | check_pipeline L1520-1557 | VERIFIED | |
| 02 FOR 3: FROM_ROWS comment goes stale; use R1 ids | tests L5861-5864 | VERIFIED | |
| 02 AGAINST 1: S7/S8 FROM-1 equivalent; 32 killable | rows 01 3.3 above | WRONG (in part) | Only S7 FROM-1 is equivalent. 33 are killable |
| 02 AGAINST 2: git rows skip without git; suite 1011 passed in 110.00s; 74-93 s runs; added time not measured | 102 audit L41; check_pipeline L1503; tests L514, L69 | VERIFIED | The added time stays unmeasured. I2 records it (step 8) |
| 02 AGAINST 2 mitigation: S15 is one more line in an existing repo | tests L515-538 | VERIFIED | |
| 02 AGAINST 3: mutants by hand; stale `.pyc` risk; item 107 | logs/efficiency/2026-11-25.md L3; 102 audit L29 | VERIFIED (reasoning, adopted in step 8) | |
| 02 Languages N/A: no new external claims | 02 text | VERIFIED | |
| 02 Holes: S15's 045 line with no work/045 also gives ORPHAN LOG; the test already expects exit 1 and asserts only the LOG TIME line | tests L533-538; check_pipeline L1351-1363 | VERIFIED (traced, not run) | |
| 02 Holes: `_timed_repo` hard-codes "990" | tests L4491 | VERIFIED | |
**Totals:** 62 rows checked → **52 VERIFIED as-is**, **10 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None. The corrected claims were the pytest-gremlins bullet attribution, S15's function name, the UNTRACKED_FROM Compare at L1822, the S8 FROM-1 "equivalent" claim (in 4 places), and the S9 and S8@076 fixture details.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | tests/test_pipeline_check.py: `SITE_ROWS`, 17 rows `(site, function, constant, from_kill, from1_kill)`: S1 log_fields_ok/TESTS_FORMAT_FROM, S2 log_fields_ok/TIMED_FROM, S3 log_hint/TESTS_FORMAT_FROM, S4 log_hint/TIMED_FROM, S5-S14 incomplete (CHECKLIST, LOG_CHECK, TIMED, TESTS_FORMAT, TIMED, SUITE, ROUND_HEADING, ROUND_BUILD, SCRATCH, VERDICT), S15 late_log_lines/LOG_CHECK_FROM, S16 batch_log_items/LOG_CHECK_FROM, S17 _item_triggers/WHOLE_DIFF_FROM. `from_kill`/`from1_kill` name the killing test node id from the 01 S-table plus steps 2-6. S7's `from1_kill` is the text `EQUIVALENT: at 089 "I2" in bad means an I2 line fails LOG_FORMAT, so all(timed=False) is False and the gate is never entered`. New `test_from_site_census`: `ast.parse` scripts/check_pipeline.py. For each top-level FunctionDef and each `ast.Compare` inside it, take the set of `ast.Name` ids ending `_FROM` in `ast.walk(compare)` minus `{"UNTRACKED_FROM"}`. Count one per (function, name). Assert the Counter equals the Counter of SITE_ROWS' (function, constant). Also assert each named test function exists in the module (`globals()`). The census is not keyed on the operator, so it stays green under every site mutant | scripts/check_pipeline.py source; SITE_ROWS | 1 census test, 17 rows | Real code: pass (17 = 17). In a scratch copy, adding `if int(item) >= SUITE_FROM: pass` to any function fails it (18 vs 17). Under each of the 34 site mutants it still passes (step 8), so it never takes a kill | 17 sites of 17 matched: Grep `_FROM`, scripts/check_pipeline.py at daily-fixes/2026-11-25 (code lines L822 … L2028). Per function: 2 + 2 + 10 + 1 + 1 + 1 = 17. 18 Compare nodes hold a `*_FROM` Name; L1822 (UNTRACKED_FROM) is excluded |
| 2 | tests/test_pipeline_check.py: `_timed_repo(tmp_path, rules, commit_05=True, item="990", i2="1 files changed \| tests 1 passed")` (defaults keep test_timed_gate unchanged; it passes `i2=(i2,), item=item` to `_suite_item`). New `@NO_GIT test_rule_gate_cutoff_boundary`, 2 rows. **`TIMED@incomplete_timed_gate-FROM`**: item 090, rules TIMED_RULES, default i2. Expect `RULE NOT SEEN: 090 (05 added in {sha7} without TIMED_FROM (090): judged by untimed I2 form; item 084)` and `INCOMPLETE: none`. **`TESTS_FORMAT@incomplete_tests_gate-FROM`**: item 076, rules `"VERDICT_FROM = 71\nSUITE_FROM = 87\nTIMED_FROM = 90\n"` (no TESTS_FORMAT_FROM), i2 `1 files changed \| tests 9/9`. Expect `RULE NOT SEEN: 076 (05 added in {sha7} without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; item 084)` and `INCOMPLETE: none` | `_timed_repo`, `_suite_item`, `_pick`, TIMED_RULES, TIMED_05, SUITE_DAY | 2 rows | Real code: 2 pass. S7 `>`: 090 skips the TIMED gate. The TESTS gate sees TESTS_FORMAT_FROM (True), so I2 stays bad: `INCOMPLETE: 090 (... I2 wants "{TIMED_HINT}")` and the row fails. S8 `>`: 076 skips the TESTS gate, so `INCOMPLETE: 076 (... I2 wants "<n> files changed \| tests <last line of python3 -m pytest -q, as printed>")` and the row fails | 090 ≥ 90 enters the TIMED gate; 076 ≥ 76 enters the TESTS gate; 076 < 90 skips TIMED. Both fixtures put "I2" in `bad`: `tests 1 passed` fails I2_TIMED at 090, and `tests 9/9` fails LOG_FORMAT at 076 (tests L732). Self-check rows 1-2 |
| 3 | Same file: new `@NO_GIT test_tests_gate_not_entered_below_cutoff`, id `TESTS_FORMAT@incomplete_tests_gate-FROM-1`. Repo with **no** scripts/check_pipeline.py (shape of tests L2860-2871): `_defective(repo, "075", i2="1 files changed \| tests 10/9")`, `sha = _commit(...)`, run `--untracked-from sha --today 2026-11-02`. Assert, in the INCOMPLETE line: `'075 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed \| tests <pass>/<total> (pass <= total)"'` is in it; `f"06 anchor {sha[:7]} has no scripts/check_pipeline.py (item 084)"` is in it (this proves the fixture really is in the no-RULE_FILE state); `"05 anchor"` is not in it | `_defective`, `_commit`, `_git`, `_run`, `_pick` | 1 row | Real code: pass (75 ≥ 76 false, so the TESTS gate is never called and there is no 05 note). S8 site-local `>= 75`: the gate runs, `_rule_seen` → (None, "05 anchor … has no …") → note appended (L1095-1096), so the row fails | 75 < 76 (I2_BEFORE applies); `10/9`: 10 ≤ 9 false, so "I2" is in `bad`; 75 < 90 (no TIMED gate); 75 ≥ 71, so the VERDICT check fires on `_defective`'s missing Sent back line and gives the 06 note. Self-check row 3 |
| 4 | Same file: `test_batch_not_computable_strict_from_090` parametrize becomes `[("990", True), ("090", True), ("089", False)]`, ids `["990", "TIMED@batch_strict-FROM", "TIMED@batch_strict-FROM-1"]`. Strict assert `inc == f"INCOMPLETE: {item} (LOG BATCH not computable: log line with no valid time (item 090))"` | `_six`, `_batch_item`, `_run`, `_pick` | 3 rows (1 new) | Real code: 3 pass. S9 `>`: 090 gets no strict entry, so `INCOMPLETE: none` and the row fails. S9 `>= 89`: the 089 row fails (already today) | 090 ≥ 90 strict; 089 < 90 text only. Self-check row 4 |
| 5 | Same file, `test_log_line_after_its_commit_is_flagged`: add `23:10 \| I2 \| 045 \| 1 files changed \| tests 1 passed in 0.01s\n` to the 2026-11-04 implementation log. Assert `"045 I2 (2026-11-04 23:10 after commit 2026-11-04 22:24 UTC)" in line`. Docstring names site `LOG_CHECK@log_time` FROM (045) and FROM-1 (044, existing assert) | existing repo fixture | 1 more assert | Real code: pass. S15 `>`: 45 > 45 is false, so 045 is not listed and the test fails. S15 `>= 44`: `"044" not in line` fails (already today) | 045 ≥ 45 checked; 044 < 45 not. 23:10 > 22:24. Self-check row 5 |
| 6 | Same file: new `test_batch_log_check_cutoff_boundary`, ids `LOG_CHECK@log_batch-FROM` / `-FROM-1`. Fixture per row: `r, i = _six("10:15")`; `_batch_item(tmp_path, item, r, i, "344 passed, 1 skipped in 48.51s", "344 passed, 1 skipped in 47.57s", full=True)`; `res = _bl(tmp_path)` (excepted = {}). 045: `res["flagged_ids"] == ["045"] and res["checked"] == 1`. 044: `res["flagged_ids"] == [] and res["checked"] == 0 and res["not_computable"] == [] and res["in_progress"] == []` | `_six`, `_batch_item`, `_bl` | 2 rows | Real code: 2 pass. S16 `<=`: 045 skipped, so checked 0 and FROM fails. S16 `< 44`: 044 evaluated, so checked 1 and flagged, and FROM-1 fails | 45 < 45 false (evaluated); 44 < 45 true (skipped). Both rows have I2 lines, so L1522 does not skip either. Self-check row 6 |
| 7 | Same file: rewrite the FROM_ROWS comment (L5861-5864). It now says the 7 constants are pinned against shifts here, and per-site operator mutants are pinned by SITE_ROWS (item 109) | – | comment | Grep the file for `shifts only, not against per-site`: 0 | – |
| 8 | 05 Mutations table (I2) and the I3 re-run, in a scratch worktree. 34 site mutants: for each S1-S17, (a) the FROM side (`>=`->`>` or `<`->`<=` at that line only) and (b) the FROM-1 side (`>= NAME - 1` or `< NAME - 1` at that line only). Each run: `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -q -p no:cacheprovider -rs tests/test_pipeline_check.py tests/test_real_data_field.py` (item 107). For each mutant, 05 pastes the summary line and the failing ids. Each must include the SITE_ROWS kill for that side, and `test_from_site_census` must not be among them. S7(b) is run too and must survive (documented equivalent). 05 also pastes the unmutated run's time, and `-rs` shows that none of the 4 git rows (steps 2, 3, 5) was skipped | 04 mutant list | 05 table, 06 re-run | 33 of 34 mutants fail at least their named row. S7(b) passes. Any other survivor, or a census failure under a mutant, sends the item back | 34 = 17 × 2. 33 killable = 26 today + 7 new rows; 1 equivalent |
| 9 | Build order: steps 1-7 in one commit after rebasing on any of 107, 108 or 110 that merges first. Then re-run the step 1 Grep and re-read every cited line | branch state | – | The census passes on the rebased file and the line refs in 04 match. The full suite passes | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| git binary (steps 2, 3, 5 rows) | not on PATH | `NO_GIT` / skipif skip, reported in the pytest summary as skipped, never as passed. Step 8 requires `-rs` to show 0 skips for these ids. A skipped row does not count as a kill |
| `_rule_seen` anchor RULE_FILE (step 2) | constant absent from the anchor's RULE_FILE | `False` → the RULE NOT SEEN entry the row asserts (the intended state) |
| RULE_FILE in the anchor tree (step 3) | file absent (intended) | `(None, "<step> anchor <sha7> has no scripts/check_pipeline.py (item 084)")` (L935). The row asserts the 06 note is present to prove the fixture's state |
| LOG_BATCH_EXCEPT (step 6) | – | `_bl` passes `excepted={}`, so the module exception (083) cannot change the 045/044 rows |
| work/045 dir (step 5) | absent | ORPHAN LOG entry (item 047). The test already expects exit 1 and reads only the LOG TIME line |
| site mutant result (step 8) | not run or not pasted | the item is not done. A "killed" claim without a pasted failing id is UNVERIFIED, never counted |
| Screen tickers (`ccbot/screen.TESTS`, `MISSING_POLICY`) | n/a | n/a: there is no ticker screen in this item (test-only pipeline work) |

## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| 1 S7 FROM (step 2) | TIMED gate iff "I2" in bad and int(ID) >= 90 | 90 >= 90 true → gate → `_rule_seen` False (TIMED_RULES has no TIMED_FROM) → RULE NOT SEEN. Mutant 90 > 90 false → elif: 90 >= 76 → TESTS gate, TESTS_FORMAT_FROM in TIMED_RULES → True → I2 stays bad → INCOMPLETE. Expected lines differ | pass |
| 2 S8 FROM (step 2) | TESTS gate iff "I2" in bad and int(ID) >= 76 | `9/9` at 076: S1 76 < 76 false → LOG_FORMAT → fails (tests L732) → bad. 76 >= 90 false → elif 76 >= 76 true → seen False → I2_BEFORE: 9 <= 9 true → removed, RULE NOT SEEN. Mutant 76 > 76 false → stays bad → INCOMPLETE | pass |
| 3 S8 FROM-1 (step 3) | gate entered iff int(ID) >= 76 (mutant >= 75) | `10/9` at 075: 75 < 76 → I2_BEFORE: 10 <= 9 false → bad. Real 75 >= 76 false → no 05 note. Mutant 75 >= 75 true → note `05 anchor … has no …` → extra entry. 75 >= 71 → VERDICT fires → 06 note in both | pass |
| 4 S9 (step 4) | strict iff nc in BATCH_STRICT and int(ID) >= 90 | nc "log line with no valid time" is in BATCH_STRICT (L492). 090: 90 >= 90 strict; mutant 90 > 90 false → none. 089: 89 >= 90 false; mutant `>= 89` true → entry | pass |
| 5 S15 (step 5) | listed iff int(ID) >= 45 and stated > commit | 045: 45 >= 45, 23:10 > 22:24 → listed; mutant 45 > 45 false. 044: 44 >= 45 false; mutant `>= 44` true → listed | pass |
| 6 S16 (step 6) | evaluated iff int(ID) >= 45 (skip iff < 45) | 045: 45 < 45 false → evaluated. t05 = 48.51, t06 = 47.57, k = 2: 48.51 + 47.57 − 2 × 0.005 = 96.07 ≥ (0 + 1) × 60 = 60 → flagged, checked 1. 044: 44 < 45 → skipped, checked 0. Mutants: `<=` → 045 skipped; `< 44` → 044 evaluated | pass |
| 7 Census count (step 1) | Σ sites per function | log_fields_ok 2 + log_hint 2 + incomplete 10 + late_log_lines 1 + batch_log_items 1 + _item_triggers 1 = 17; Compare nodes with `*_FROM` 18 − 1 (L1822 UNTRACKED_FROM) = 17 | pass |
| 8 Mutant count (step 8) | 17 × 2; covered + new + equivalent | 34. 12 × 2 + 2 (S9, S15 FROM-1) = 26; new 7 (S7a, S8a, S8b, S9a, S15a, S16a, S16b); equivalent 1 (S7b): 26 + 7 + 1 = 34; killable 33 | pass |
| 9 Totals | as-is + fixed + removed = rows | 52 + 10 + 0 = 62 | pass |

Log line: not written by R3. R3 has no shell, and the orchestrator asked for 03 only. After check_handoff, the orchestrator runs `python3 scripts/check_pipeline.py --log R3 109 "<as-is> verified, <fixed> fixed, <removed> removed | READY"` with the counts copied from the script output (item 045).

`check_handoff output (run by the orchestrator 2026-11-25 23:39 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 3
fact-check rows: 62
totals line: 62 rows -> 52 as-is, 10 fixed, 0 removed
PASS
```
