# 03 Research hand-off - 102
Status: READY
Scope note: Parts 1 and 2 only. Part 3 (the i1-reviewer sentence, a RULE_PATHS edit under `.claude/`) is out of scope and waits for the person's OK. Nothing here proposes wording for it. `.claude/agents/i1-reviewer.md` has 0 matches for `mutant|_FROM|boundary` (Grep, R3 re-run). Every change below is in `tests/`, which is in CODE_PATHS but not RULE_PATHS (scripts/check_pipeline.py L524-526). R3 has no shell, so every "killed" or "survives" below comes from reading and tracing the code. I2 must run each one and I3 must re-run it (step 5).

Recurring issues checked (item 013), all open or ESCALATED entries:
- RI-001 (ESCALATED). Every cutoff rule `int(ID) >= FROM` has its boundary IDs computed in the Feasibility column and Self-check. Each claim that a mutant is killed or survives is marked as traced, not run. Step 5 makes I2/I3 run all 15 mutants (14 shifts plus the moved loop).
- RI-010 (ESCALATED). This item is the 098 near miss "commit_step trailer-refusal order untested -> 102". Each refusal row and each cutoff gets a named killing test (steps 1-4). The R3 log line is not written by hand: see the note after Self-check.
- RI-014 (OPEN). No git call is added to scripts/. The new check_pipeline fixtures need no git (`_rule_seen` returns `(None, "")` when env is set, L910-911). The commit_step fixtures use a fresh `git init`, so clone depth cannot affect them.
- GUARDED entries also checked:
  - RI-002: a recorder that sees no call is `calls == []`, never "skipped"; Missing inputs.
  - RI-004/005: Self-check.
  - RI-006: totals are left to check_handoff.
  - RI-007: Scope FULL, code allowed.
  - RI-009: other agents are on 099-101/103/104, so re-read line numbers after a rebase (step 6).
  - RI-012: assertions match exact INCOMPLETE entries or stderr reasons, never a bare number.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 Q: in A1's mutant the `_trailer_ok` loop moves to just before commit-tree, and it survives (40 passed) | logs/audit/2026-11-24-098.md L45-46, N1 L50-53 | VERIFIED | |
| 01 Q Part 3: `.claude/` is in RULE_PATHS (L524); i1-reviewer.md has no mutant/_FROM/boundary text | scripts/check_pipeline.py L524; Grep i1-reviewer.md: 0 matches | VERIFIED | |
| 01 RI read: RI-010 ESCALATED names 102 as a near miss; RI-001 ESCALATED; "before any git call" is asserted at commit_step L13 and L159 | logs/recurring-issues.md L119, L7; scripts/commit_step.py L13, L159 | VERIFIED | |
| 01 1.1: the trailer loop is first (L158-160); the first git call is rev-parse L161; every later git call goes through `run` (L161, L167, L189, L195, L200-205, L212-215, L225) | scripts/commit_step.py L108-115, L118-140, L156-230 | VERIFIED | |
| 01 1.2: T-b runs a child process (`_cli`) and compares only HEAD + `.git/index` (`_state`); loose objects are not compared | tests/test_commit_step.py L59-66, L295-309 | VERIFIED | |
| 01 1.3: default values are evaluated once, at def time, so patching `cs.run` does not reach main -> commit | https://docs.python.org/3/reference/compound_stmts.html; commit_step.py L156, L244 | VERIFIED | |
| 01 1.4: module `run` calls `subprocess.run` at call time; subprocess.run doc quote | commit_step.py L61-67; https://docs.python.org/3/library/subprocess.html | VERIFIED | |
| 01 1.5: existing `run=lambda a, env=None, input=None: ...` wrappers | tests/test_commit_step.py L178-186, L225-233 | VERIFIED | |
| 01 1.6: monkeypatch undo and `MonkeyPatch.context()` quotes; the test's `_g` calls subprocess.run too | https://docs.pytest.org/en/stable/how-to/monkeypatch.html; tests/test_commit_step.py L29-32 | VERIFIED | |
| 01 1.7: the no-value row is refused in `main` (L235-238); the main-level form covers 6 of 6 rows, `commit(run=rec)` covers 5 | commit_step.py L233-244 | VERIFIED (in part) | "Covers" is right, but only 5 of the 6 rows can kill the moved-loop mutant. The no-value row returns before `commit` under any reordering inside `commit`, so it is a guard row, not a kill row (02 AGAINST 3b) |
| 01 1.8: under the mutant the recorder's first entry is `rev-parse --show-toplevel`, so `calls == []` fails wherever the loop sits after L160 | code trace, commit_step.py L156-212 | VERIFIED (traced, not run) | |
| 01 1.9: `hash-object -w` writes the object; `write-tree` creates a tree; the mutant leaves loose objects | https://git-scm.com/docs/git-hash-object; https://git-scm.com/docs/git-write-tree; test_commit_step.py L44-50 | VERIFIED (traced, not run) | |
| 01 2.1: the 7 values and their gate sites | scripts/check_pipeline.py L433, L437, L438, L441, L444, L498, L502; L811, L814, L824, L827, L1032, L1049, L1055, L1066, L1087, L1097, L1174, L1385, L1507, L2017 | VERIFIED | |
| 01 2.2: a test that reads its boundary from the constant (SF, `cp.TIMED_FROM`) can't kill a shift; a literal ID or a literal value assert can | tests/test_pipeline_check.py L3680-3712, L4402-4405, L5428-5434 | VERIFIED | |
| 01 2.3 CHECKLIST_FROM row: FROM-1 killed by test_incomplete_06_and_missing_log_line (040); FROM+1 not killed | tests/test_pipeline_check.py L422-433, L329, L446, L783, L815-821 | VERIFIED (in part) | Correction: "041 ... with no step files" is not quite right. L821 writes 041's 01 on branch `next`. That test asserts only OPEN BRANCHES / RULES BRANCH lines (L831-834), so the conclusion (no FROM+1 kill) still holds |
| 01 2.3 LOG_CHECK_FROM row: FROM-1 killed (044 at L502-511, L538); FROM+1 not killed | tests/test_pipeline_check.py L502-511, L515-538 | VERIFIED | |
| 01 2.3 TESTS_FORMAT_FROM row: both sides killed by test_i2_tests_field_cutoff and test_old_i2_hint_fits_old_format | tests/test_pipeline_check.py L724-749, L759-768 | VERIFIED | |
| 01 2.3 SUITE_FROM row: neither side killed (S1-S4 use SF) | tests/test_pipeline_check.py L3680-3712; Grep `"086"`/`"087"`: 0 | VERIFIED | |
| 01 2.3 TIMED_FROM row: FROM-1 killed by L4392 and L704-712; FROM+1 only by `== 90` (L4405) | tests/test_pipeline_check.py L704-712, L4380-4405 | VERIFIED (new source) | One more FROM-1 kill: test_batch_not_computable_strict_from_090 row 089 (L4459-4474). FROM+1 is still killed only by the value assert, with no literal-090 behavior pin (Grep `"090"`: 0) |
| 01 2.3 WHOLE_DIFF_FROM row: t7 (069) kills FROM-1; t7b/t7c/t7d (`== 70`) kill FROM+1 | tests/test_real_data_field.py L116-157 | VERIFIED | |
| 01 2.3 VERDICT_FROM row: neither side killed (T3 uses 060/065/173) | tests/test_pipeline_check.py L2180-2193 | VERIFIED | |
| 01 2.4: a VERDICT_FROM=70 mutant may add an entry to test_real_data_field's 070 item and still pass (startswith / in) | tests/test_real_data_field.py L129-147 | UNSUPPORTED (left open) | Kept only as a question for I2's run. The map does not rely on it: the new VERDICT rows kill both shifts on their own |
| 01 2.5: `_item` always writes a 05 Suite line equal to the I2 field and a 06 with a Verdict | tests/test_pipeline_check.py L35-66 | VERIFIED | |
| 01 2.6: TESTS_FORMAT/SUITE/TIMED/VERDICT are `_rule_seen`-gated when a check fires (L1057, L1067, L1115, L1183); non-git fixtures get the strict entry | check_pipeline.py L903-928, L1057, L1067, L1115, L1183; tests L3684-3688, L2180-2193 | VERIFIED (new source) | The cited L2976-2977 / L3001-3002 are git cases (an uncommitted 05, an unborn HEAD). The no-git path is L910-911: env is set, so the result is `(None, "")`, and S0 (L3688) and T3 (L2192) show the strict entry with no git |
| 01 2.7: CHECKLIST_FROM and LOG_CHECK_FROM stay numeric | check_pipeline.py L383 | VERIFIED | |
| 01 2.8: one shift changes every site; per-site counts LOG_CHECK 3, TESTS_FORMAT 3, TIMED 4 | check_pipeline.py gate lines (row 2.1) | VERIFIED | |
| 01 2.9: SCRATCH_FROM literal parametrize `ids=["FROM", "FROM-1"]`; pytest parametrize quote | tests/test_pipeline_check.py L5428; https://docs.pytest.org/en/stable/how-to/parametrize.html | VERIFIED | |
| 01 2.10 CHECKLIST fixture: `_item("041", ALL, logged=False)` gives `041 (no log line for R1 R2 R3 I1 I2 I3)`; 040 gives none | check_pipeline.py L1032-1048 (041 < 45 has no format check; 041 < 71 has no verdict check; no I3 line, so no L1190-1203 entry) | VERIFIED (traced, not run) | |
| 01 2.10 LOG_CHECK fixture: 045 + `see 05 \| tests 1/1` gives the item-045 entry; 044 gives none | check_pipeline.py L1049-1083, L468 (045 < 76 uses I2_BEFORE) | VERIFIED (traced, not run) | |
| 01 2.10 SUITE fixture: `_suite_item("x\n", item="087")` gives `INCOMPLETE: 087 (05 has no 'Suite:' line (item 082))`; 086 gives none | check_pipeline.py L1097-1121; tests L3658-3668 (the default I2 field is timed and well-formed) | VERIFIED (traced, not run) | |
| 01 2.10 VERDICT fixture: `_item("071", ALL, verdict=None)` gives the item-071 entry; 070 gives none; with no git, REAL-DATA makes no entry | check_pipeline.py L1172-1189, L2024-2029 (`real_data_field` returns None without git) | VERIFIED (traced, not run) | |
| 01 2.10 TIMED fixture: `_log("I2","090","1 file changed \| tests 5 passed")` gives exit 2 with the timed hint; 089 gives exit 0 | check_pipeline.py L814; tests L4380-4392 | VERIFIED (in part) | Both IDs need `_request(root, item)` first. Without it, --log refuses with item 047 (L480-484), which is also exit 2. So the FROM row must assert `TIMED_HINT` in stderr, not only exit 2 |
| 01 2.10 last line: each row gets its own `assert cp.<NAME> == <N>` | design | WRONG (as placed) | Moved (02 AGAINST 1). With a value assert in every row, each shift "kill" comes from the value assert, so the rows prove nothing. The value asserts go in one separate `test_from_values` (step 4), and step 5 runs the shifts with it deselected |
| 01 Numbers: 2 + 1 + 2 + 2 = 7 constants by pin state | row 2.3 | VERIFIED | |
| 01 Numbers: 14 shifts; 8 expected killed today, 6 survive (CHECKLIST+1, LOG_CHECK+1, SUITE±1, VERDICT±1) | 7 × 2 = 14; 3 × 2 + 2 = 8; 14 − 8 = 6 | VERIFIED | |
| 01 Numbers: boundary arithmetic `int(ID) >= FROM` for 41/45/87/71/90 | Self-check rows 1-5 | VERIFIED | |
| 01 Numbers: T-b has 6 rows, 5 `_trailer_ok` refusals + 1 usage refusal | tests/test_commit_step.py L295-302 | VERIFIED | |
| 01 Fit: tests/ is in CODE_PATHS, not RULE_PATHS | check_pipeline.py L524-526 | VERIFIED | |
| 02 past logs: audit L45-46, N1 L50-53, residuals L54-55 | logs/audit/2026-11-24-098.md | VERIFIED | |
| 02 past logs: RI-010 near miss -> 102; RI-001 ESCALATED | logs/recurring-issues.md L119, L7 | VERIFIED | |
| 02 past logs: 092-095, 097, 098 logged `languages: N/A`; 096 got the full search | logs/research/2026-11-24.md L9-17 | VERIFIED | |
| 02 FOR 1: `cs.subprocess` is the shared module; `setattr(cs, "subprocess", SimpleNamespace(run=rec))` rebinds only commit_step's global, which `run` looks up at call time | https://docs.python.org/3/reference/executionmodel.html; commit_step.py L45, L64 | VERIFIED | |
| 02 FOR 1: `subprocess` is used only at L45 and L64 | Grep `subprocess` commit_step.py: 2 lines | VERIFIED | |
| 02 FOR 1: this form reaches main's default `run`, so all 6 rows go through `cs.main` | commit_step.py L156, L244 | VERIFIED (in part) | 6 rows are covered and 5 can kill (row 01 1.7). The test names the no-value row as a guard |
| 02 FOR 1: a recorder that appends and then raises makes any git call fail loudly | commit_step.py L63-66 | VERIFIED (in part) | Its exception must not be FileNotFoundError (or a subclass): `run` turns that into None (L65-66), which becomes the "no git" refusal, exit 2. That hides the order bug. Use a dedicated `class GitCalled(Exception)` |
| 02 FOR 2: the mutant runs hash-object -w (L203) and write-tree (L205) before it refuses; the fixture log yields one blob | commit_step.py L118-140, L198-205; tests/test_commit_step.py L48, L275 | VERIFIED | |
| 02 FOR 2: a before/after set of files under `.git/objects` (os.walk, no git) fails under the mutant and keeps `_cli` | traced: `update-index --add` (L201) also writes the R05 blob | VERIFIED (traced, not run) | |
| 02 FOR 3: literal-ID parametrize; 4 constants × 2 rows = 8 rows close the 6 survivors; helpers exist | tests/test_pipeline_check.py L35-36, L698, L3658, L5428 | VERIFIED | |
| 02 FOR 3: non-git fixtures need no RULE_FILE setup | check_pipeline.py L910-911 | VERIFIED | |
| 02 AGAINST 1: a value assert in each behavior row masks whether the row pins anything | reasoning; tests L4405 | VERIFIED | Adopted in step 4 |
| 02 AGAINST 2: 10 sites across LOG_CHECK/TESTS_FORMAT/TIMED; the LOG_CHECK pin goes through L1049 only; about 14 operator mutants | check_pipeline.py sites; 1+3+3+1+4+1+1 = 14 | VERIFIED | Residual (a) |
| 02 AGAINST 3a: `cs.main` skips L247-248 and real argv, so keep T-b's `_cli` | commit_step.py L247-248 | VERIFIED | |
| 02 AGAINST 3b: the no-value row cannot kill the mutant; 5 rows kill | commit_step.py L235-238 | VERIFIED | |
| 02 AGAINST 3c: a recorder returning None makes commit raise "no git" (L162-163) | commit_step.py L61-67, L161-163 | WRONG (in part) | That holds only for a recorder passed as `run=`. In FOR 1's form the recorder replaces `subprocess.run`, so returning None raises AttributeError at L67 (`r.stdout`). The order bug is masked only if the recorder raises FileNotFoundError (row FOR 1 above). Raising GitCalled avoids both |
| 02 Holes: there are 10 numeric `*_FROM` cutoffs, not 7 | check_pipeline.py L433-454, L498, L502, comments L449/L453 | VERIFIED | UNTRACKED_FROM (L528) is an 11th `*_FROM` name, but it is a commit SHA, not an ID cutoff |
| 02 Holes: ROUND_BUILD_FROM 098 FROM-1 row "not checked (UNVERIFIED)" | tests/test_pipeline_check.py L5183-5195 | VERIFIED (new source) | Resolved: literal rows `099-at-cutoff` and `098-below-cutoff`. ROUND_HEADING_FROM has 092 (L5101) and 091 (L5127). SCRATCH_FROM has 097/096 (L5428). All 3 are pinned both ways and out of scope |
| 02 Holes: VERDICT 070 may interact with REAL-DATA FIELD in test_real_data_field.py | tests/test_real_data_field.py L129 | UNSUPPORTED (left open) | Same as row 01 2.4: I2 records the result and nothing relies on it. In test_pipeline_check (no git), `real_data_field` returns None (L2028-2029) |
| 02 Languages N/A: only official tool docs | the 7 URLs above, each fetched by R3 (2026-11-24) | VERIFIED | |
**Totals:** 58 rows checked → **46 VERIFIED as-is**, **12 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None. Two claims were moved or corrected rather than dropped: 01 2.10's per-row value assert (now step 4) and 02 AGAINST 3c's "no git" path (corrected).

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | tests/test_commit_step.py: lift T-b's 6 `(args, why)` rows and ids into a module constant `TB_ROWS` (T-b unchanged in behavior). New `test_trailer_refusals_make_no_git_call(repo, monkeypatch, capsys, args, why)` over `TB_ROWS`. It defines `class GitCalled(Exception)` (never an OSError), `calls = []`, and `def rec(cmd, **kw): calls.append(list(cmd)); raise GitCalled(cmd)`. Then `monkeypatch.setattr(cs, "subprocess", types.SimpleNamespace(run=rec))` and `code = cs.main(list(args))`. Asserts: `code == 2`, `why in capsys.readouterr().err`, `calls == []`. The docstring names `no-value` as the guard row (refused in `main` L236-238, so it cannot kill the mutant) | `repo` fixture (cwd = repo top via monkeypatch.chdir); TB_ROWS | 6 test rows | Real code: 6 pass. Mutant M1 (A1's: the L159-160 loop moved to just before L211/L212): the 5 `_trailer_ok` rows fail (GitCalled raised at the L161 rev-parse), and `no-value` passes. 05 pastes the failing IDs | 5 of 6 rows reach `commit` (L244); 1 of 6 is refused in `main`. Each of the 5 hits its `_trailer_ok` branch: Self-check row 7 |
| 2 | tests/test_commit_step.py T-b: also compare `_objects(r) = {p for p in os.walk(r/".git"/"objects")}` (relative file paths, no git call) before and after `_cli` | `repo` fixture | equal sets | Real code: unchanged (0 git calls before refusal). Mutant M1: the 5 `_trailer_ok` rows fail, because the R05 blob (update-index --add L201), the filtered log blob (L203) and the tree (L205) are new objects. `no-value` passes | 5 of 6 rows write ≥ 2 new objects under M1: the R05 "05\n" blob and the log blob (H+L_HEAD+L150, which differs from HEAD's log) are not in the root commit, plus ≥ 1 tree; 0 of 6 on real code |
| 3 | tests/test_pipeline_check.py: `test_from_cutoff_boundary`, parametrized with literal IDs and ids `<NAME>-FROM` / `<NAME>-FROM-1`, 10 rows. **CHECKLIST** 041/040: `_item(root, id, ALL, logged=False)`, `--today 2026-11-04`; FROM: `"041 (no log line for R1 R2 R3 I1 I2 I3)" in INCOMPLETE line`; FROM-1: `INCOMPLETE: none`. **LOG_CHECK** 045/044: `_item(root, id, ALL)` + appended `12:00 \| I2 \| <id> \| see 05 \| tests 1/1` to logs/implementation/2026-10-31.md, `--today 2026-11-05`; FROM: `"045 (log line for I2 does not match its format (item 045)" in` it; FROM-1: none. **SUITE** 087/086: `_suite_item(root, "x\n", item=id)` + `_inc`; FROM: `== "INCOMPLETE: 087 (05 has no 'Suite:' line (item 082))"`; FROM-1: `== "INCOMPLETE: none"`. **VERDICT** 071/070: `_item(root, id, ALL, verdict=None)`, `--today 2026-11-18`; FROM: `"071 (06 has no readable 'Verdict: PASS' or 'Verdict: FAIL' line (item 071))" in` it; FROM-1: none. **TIMED** 090/089: `_request(root, id)`, `_log(root, "I2", id, "1 file changed \| tests 5 passed")`; FROM: `code == 2 and f'"{TIMED_HINT}"' in err`; FROM-1: `code == 0`. Each row has its own tmp root. No value asserts in these rows | `_item`, `_suite_item`, `_inc`, `_run`, `_pick`, `_log`, `_request`, TIMED_HINT | 10 test rows | Real code: 10 pass. Each shift mutant fails its named row (Self-check rows 1-5) | Per constant, 1 of 2 boundary IDs is checked (FROM ≥ FROM) and 1 is not (FROM-1 < FROM). 5 constants × 2 = 10 rows, from the gates L1032, L1049, L1097, L1174, L814 |
| 4 | tests/test_pipeline_check.py: one separate `test_from_values` asserting CHECKLIST_FROM 41, LOG_CHECK_FROM 45, TESTS_FORMAT_FROM 76, SUITE_FROM 87, TIMED_FROM 90, WHOLE_DIFF_FROM 70, VERDICT_FROM 71. The existing `== 90` (L4405) and `== 70` (test_real_data_field L155) stay | `_cp()` | 1 test | Fails under each of the 14 shifts. It is deselected in step 5's behavior runs | 7 of 7 constants listed |
| 5 | 05 Mutations table (I2) and I3 re-run. M1 (moved loop), plus the 14 shifts (each constant ±1), each run as `python3 -m pytest -q tests/test_commit_step.py tests/test_pipeline_check.py tests/test_real_data_field.py -k "not test_from_values and not test_timed_hint_fits_timed_format and not test_t7d"` so value asserts can't take the kill. For each mutant, 05 pastes the pytest summary and the failing test IDs. Each must include the named behavior test from the Self-check kill table. Rows 01 2.4 / 02 Holes (070 interaction): 05 records whether test_real_data_field changed under VERDICT_FROM=70 | 04 mutant list | 05 Mutations table, 06 re-run | Every one of the 15 mutants fails at least one named behavior test. Any mutant that survives sends the item back | 15 mutants: 1 + 7 × 2 |
| 6 | Build order: steps 1-2 (commit_step tests), then 3-4. Re-read every cited line number after rebasing on any of 099-101/103/104 that merges first | branch state | – | Line refs in 04 match the rebased files; the full suite passes | – |

Residuals (follow-up items, not built here):
- (a) Per-site operator mutants (`>=` → `>` or a single site rewritten): 14 sites across the 7 constants (1+3+3+1+4+1+1). LOG TIME (L1385) and LOG BATCH (L1507) need git fixtures. Do not call the cutoffs "fully pinned"; they are pinned against shifts only.
- (b) Part 3, the i1-reviewer sentence: pending the person's OK (RULE_PATHS).

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| git binary (commit_step tests) | not on PATH | module `pytestmark = NO_GIT` skip, reported as a skip in the pytest summary, never a pass |
| recorded git calls (step 1) | none made | `calls == []` is the asserted value, not a default. Any call raises GitCalled and errors the test |
| `.git/objects` listing (step 2) | unreadable | os.walk errors are not swallowed (no onerror), so the test errors, never passes |
| `_rule_seen` anchor (step 3 fixtures) | no git in tmp root | `(None, "")` → strict entry (L910-911). The rows assert that strict text |
| REAL-DATA FIELD for 070 (step 3 VERDICT-FROM-1) | no git | `real_data_field` returns None (L2028-2029): no INCOMPLETE entry, so `INCOMPLETE: none` is the expected value |
| request.md for the --log rows (step 3 TIMED) | missing | refused with item 047 (exit 2). The FROM row therefore asserts TIMED_HINT in stderr, so a missing request can't pass as the timed refusal |
| Screen tickers (`ccbot/screen.TESTS`, `MISSING_POLICY`) | n/a | n/a: there is no ticker screen in this item (test-only pipeline work) |

## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| 1 CHECKLIST_FROM pins | checked iff int(ID) >= 41 | 41 >= 41 true (entry); 40 >= 41 false (none). Shift 42: 41 >= 42 false → CHECKLIST-FROM fails. Shift 40: 40 >= 40 true → CHECKLIST-FROM-1 fails (and the existing L428-433) | pass |
| 2 LOG_CHECK_FROM pins | format checked iff int(ID) >= 45 | 45 >= 45 true; 44 >= 45 false. Shift 46 → LOG_CHECK-FROM fails; shift 44 → LOG_CHECK-FROM-1 fails (and the existing L502-511). `see 05 \| tests 1/1` vs I2_BEFORE `\d+ files? changed \| tests (\d+)/(\d+)`: "see" is not `\d+` → no match → bad | pass |
| 3 SUITE_FROM pins | Suite check iff int(ID) >= 87 and 05 exists | 87 >= 87 true; 86 >= 87 false. Shift 88 → SUITE-FROM fails; shift 86 → SUITE-FROM-1 fails. 05 = `_scratch_line` ("" for IDs < 97) + "x\n" → 0 Suite lines → NO_SUITE fires. Default I2 field `1 files changed \| tests 1 passed in 0.01s` is well-formed at 087/086 (≥ 76) | pass |
| 4 VERDICT_FROM pins | verdict-line check iff int(ID) >= 71 | 71 >= 71 true; 70 >= 71 false. Shift 72 → VERDICT-FROM fails; shift 70 → VERDICT-FROM-1 fails. verdict=None with sent_back auto → `{...}.get(None)` = None → no Verdict and no Sent-back line → `_i3_verdict_text` verdict None | pass |
| 5 TIMED_FROM pins | time required iff int(ID) >= 90 | 90 >= 90 true → `tests 5 passed` (no ` in <s>s`) refused, exit 2 with TIMED_HINT; 89 >= 90 false → accepted, exit 0. Shift 91 → TIMED-FROM fails (exit 0); shift 89 → TIMED-FROM-1 fails (and the existing L4392) | pass |
| 6 Shift kill table (behavior tests only) | each of 14 shifts has ≥ 1 named behavior kill | CHECKLIST ±1: rows 1. LOG_CHECK ±1: rows 2. TESTS_FORMAT +1/−1: test_i2_tests_field_cutoff (076 refuses 9/9 / 075 accepts 9/9). SUITE ±1: rows 3. TIMED ±1: rows 5. WHOLE_DIFF +1: t7b; −1: t7. VERDICT ±1: rows 4. 2+2+2+2+2+2+2 = 14 | pass |
| 7 Step 1/2 worked rows vs `_trailer_ok` (L145-153) | CR/LF → `": "` → key fullmatch `[A-Za-z0-9-]+` → value.strip() | `Co Authored: x`: has `": "`, key `Co Authored` has a space → key refusal. `Key:value`: no `": "` → refusal. `Key:   `: `": "` at index 3, key `Key` ok, value `"  "`.strip() = "" → empty value. `Key: a\nb`, `Key: a\rb`: CR/LF first. 5 of 5 refuse inside `commit`; `("--trailer",)`: len 1 < 2 → usage in `main` | pass |
| 8 M1 vs step 1 | first `run` call after the moved loop | the mutant's loop sits after L161 → rev-parse is call 1 → rec raises GitCalled (not caught: `run` catches only FileNotFoundError, `commit` only Refused) → 5 rows error | pass |
| 9 Mutant count | 1 + 7 × 2 | 1 + 14 = 15 | pass |
| 10 Per-site residual | sites per constant | 1 (L1032) + 3 (L1049, L1385, L1507) + 3 (L811, L824, L1066) + 1 (L1097) + 4 (L814, L827, L1055, L1087) + 1 (L2017) + 1 (L1174) = 14 | pass |
| 11 Totals | as-is + fixed + removed = rows | 46 + 12 + 0 = 58 | pass |

Log line: not written by R3. R3 has no shell, and the orchestrator asked for 03 only. After check_handoff, the orchestrator runs `python3 scripts/check_pipeline.py --log R3 102 "<as-is> verified, <fixed> fixed, <removed> removed | READY"` with the counts copied from the script output (item 045).

`check_handoff output (run by the orchestrator 2026-11-24 23:29 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 6
fact-check rows: 58
totals line: 58 rows -> 46 as-is, 12 fixed, 0 removed
PASS
```
