# 03 Research hand-off - 101
Status: READY
Scope note: Scope stays **FULL** (request.md). The item adds tests only. Code is allowed under FULL, so the item 062 rule does not apply, and no 07 is written here. The scope is **widened by one branch**: the Scratch dir `elif unsure` (scripts/check_pipeline.py L1168, item 097) is added as a fifth branch. It has the same shape as the other four, and it also has no shallow test (grep of `unchecked=` in tests/test_pipeline_check.py: only L4970, L4973 and L5248, and none of them is a Scratch case). It costs 2 more cases. Leaving it out would repeat the gap this item closes (02 AGAINST 1). Once this is built, all 8 `elif unsure` sites in `incomplete` have a test of their own. "Done" becomes: 5 `elif False` mutations and 5 step-key mutations each fail only their named ids, and the full-clone output is unchanged.

Tool limit: this R3 has no shell (item 072). Every behaviour claim below was checked by reading the source at the cited lines, not by running it. Step 3 (mutant run) and step 4 (output diff) are the measured checks, and I2/I3 must paste their results.

Recurring issues checked (item 013):
- RI-001 (ESCALATED): there is no ticker, DTE or delta filter here. The only "window" rules are the ID cutoffs. Fixture ID 150 is checked against each of them in the Feasibility column and in the Self-check (5 of 5 cleared). No "always" or "every" is claimed without a count.
- RI-010 (ESCALATED): this R3 writes no log line and leaves the check_handoff line empty for the orchestrator. Step 3 asks I2/I3 to paste each mutant's result.
- RI-014 (OPEN): this is the item's own RI. The status does not change, because 101 adds tests to 095's code and no new guardrail (02, past logs). Step 4 keeps the full-clone output unchanged.
- GUARDED entries also checked:
  - RI-002: no input is filled in. `unchecked=None` stays strict (Missing inputs).
  - RI-004/005: Self-check below.
  - RI-006: counts are left to check_handoff.
  - RI-007: Scope is FULL.
  - RI-009: parallel items 099, 100 and 102-104 share tests/test_pipeline_check.py, so helpers are found by name (step 1).
  - RI-012: entries are compared by exact list equality and BATCH_STRICT is passed as the constant, never a substring.
  - RI-013: whole-output diff in step 4.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 F1 `$GIT_DIR/shallow` "lists commit object names and tells Git to pretend as if they are root commits" | https://git-scm.com/docs/shallow | VERIFIED | |
| 01 F2 `git clone --depth` writes `$GIT_DIR/shallow`; `git fetch --depth` updates it | https://git-scm.com/docs/shallow ("It also writes an appropriate $GIT_DIR/shallow"; "updating $GIT_DIR/shallow") | VERIFIED | |
| 01 F3 parametrize "enables parametrization of arguments for a test function" | https://docs.pytest.org/parametrize.html (loads, status 200) | VERIFIED | |
| 01 F4 `_rule_seen` returns `(None, "")` whenever `env` is set | scripts/check_pipeline.py L910-911 | VERIFIED | |
| 01 F5 `_unsure` True only when env == SHALLOW_TEXT and the step file is in `committed`, "or `committed` is None"; `unsure()` needs `unchecked is not None` | check_pipeline.py L983-985, L1029-1030 | WRONG (in part) | Precisely: `env == SHALLOW_TEXT and (committed is None or work/<ID>/<STEPS[step]> in committed)`. L983 returns False first for any other env, so `committed=None` with env "no git" is strict. The L1029-1030 part is right |
| 01 F6 TIMED L1062: ID >= TIMED_FROM (90, L444), I2 in `bad`, every own I2 line passes `timed=False`; `1 files changed \| tests 1 passed` passes LOG_FORMAT and fails I2_TIMED | check_pipeline.py L444, L471, L551, L811-816, L1055-1062 | VERIFIED | |
| 01 F7 TESTS L1076 covered by T-a / T-a3; T-a's `tests 9/9` fails LOG_FORMAT and the untimed form, so it takes TESTS, not TIMED | tests/test_pipeline_check.py L4877, L4886-4931; check_pipeline.py L1055, L1066-1080 | VERIFIED | |
| 01 F8 LOG BATCH L1091: `batch_nc[ID]` in BATCH_STRICT (L487), ID >= 90; `batch_nc` is a parameter | check_pipeline.py L487, L995, L1086-1095 | VERIFIED | |
| 01 F9 Suite L1118: ID >= 87, 05 exists, last I2 line passes the untimed form; fires on none / >1 / mismatch | check_pipeline.py L441, L1097-1121 | VERIFIED | |
| 01 F10 Round heading L1135: ID >= 92; keyed on the loop `step` (05, 06) | check_pipeline.py L447, L1122-1138 | VERIFIED | |
| 01 F11 Round build L1150 has P-e `test_round_build_shallow_goes_to_unchecked` | tests/test_pipeline_check.py L5239-5252 | VERIFIED | |
| 01 F12 Scratch dir L1168 has no shallow test: `unchecked=` only at L4970, L4973, L5248 | Grep `unchecked=` tests/test_pipeline_check.py (R3 re-run: 3 lines) | VERIFIED | |
| 01 F13 VERDICT L1186 covered by T-a (NO_SENT_BACK in the NOT CHECKED line) | tests/test_pipeline_check.py L4893-4894 | VERIFIED | |
| 01 F14 `_item` writes a clean item: timed I2 field, matching Suite, good Scratch lines from 97, Verdict PASS / Sent back none | tests/test_pipeline_check.py L17-19, L24-27, L52-58 | VERIFIED | |
| 01 F15 `_rh_item(body05=RH_P1)` fires only the round-heading check | tests/test_pipeline_check.py L5077, L5080-5089, L5097-5108 (P1 INCOMPLETE line holds only that entry) | VERIFIED | |
| 01 F16 under `elif False` each entry falls through to the strict path (L1081-1083, L1094, L1121, L1138) with the same text and no note (`seen` None, `sha7` "") | check_pipeline.py L1057-1058, L1081-1085, L1094-1095, L1121, L1138 | VERIFIED | By reading. Step 3 measures it |
| 01 F17 a test-only change cannot change full-clone output | design (no change under scripts/) | VERIFIED | Step 4 still diffs the output |
| 01 Numbers: 4 branches, round heading x2 → 5 shallow + 5 strict = 10 cases | arithmetic | VERIFIED | Scope note adds Scratch x2 → 7 + 7 = 14 (Self-check) |
| 01 Numbers: 8 `elif unsure` sites; 3 with a shallow test, 5 without | check_pipeline.py L1062, L1076, L1091, L1118, L1135, L1150, L1168, L1186 | VERIFIED | |
| 01 Numbers: cutoffs 90 / 87 / 92 (L441-447); RH_ID "150" clears all three | check_pipeline.py L441, L444, L447; tests L5075 | VERIFIED | |
| 01 Shape: `cp.incomplete(d, logs=..., env=..., not_seen=[], unchecked=u, committed={...})`; no `@NO_GIT` | check_pipeline.py L995-996, L910; P-e L5239-5248 has no NO_GIT | VERIFIED | |
| 01 Shape: TIMED fixture must rewrite `Suite:` to `Suite: 1 passed`, else Suite fires too | check_pipeline.py L1101-1102, L1112 | VERIFIED | |
| 01 Shape: LOG BATCH entry `LOG BATCH not computable: {BATCH_STRICT[0]} (item 090)` | check_pipeline.py L1092, L1094 | VERIFIED | |
| 01 Shape: Suite fixture with no `Suite:` line → `05 has no 'Suite:' line (item 082)` | check_pipeline.py L1108-1109 | VERIFIED | |
| 01 Shape: round-heading entry text per L1129-1130 (`RH_USE`) | check_pipeline.py L1129-1130; tests L5076 | VERIFIED | |
| 01 Fit: today the branches fail closed (entry back on INCOMPLETE, exit 1) | work/095/06-verification.md L31 | VERIFIED | |
| 02 past logs: TIMED probe left T-a "1 passed"; 4 branches "have no test of their own"; fails closed | logs/audit/2026-11-24-095.md L47, L63-66 | VERIFIED | |
| 02 past logs: RI-014 "Near miss, not counted: shallow elif branches untested → 101" | logs/recurring-issues.md L153 | VERIFIED | |
| 02 past logs: R2's re-read line list (L910-911, L983-985, L1029-1030, L1062/1091/1118/1135, L1081-1083/1094/1121/1138) | scripts/check_pipeline.py at those lines | VERIFIED | |
| 02 FOR 1: `committed` holding only the gated file kills `unsure("06")` in the 05 branches and `unsure("05")` at L1135 (06 case only) | check_pipeline.py L985, L1062, L1091, L1118, L1135 | VERIFIED | Same holds for `unsure("05")` at L1168 (scratch06 case only), step 3 |
| 02 FOR 2: in clean fixtures the exact lists hold (shallow `got == []`, `u == [(ID, entry)]`; no git `got == [entry]`, `u == []`) | check_pipeline.py L1032-1204 (no other check fires on a clean `_item`); tests L5108, L5136 | VERIFIED | |
| 02 FOR 2: dropping `bad.remove("I2")` is caught by membership; a second extra entry is caught only by exact lists | check_pipeline.py L1063, L1081-1083 | VERIFIED | |
| 02 FOR 2: the Suite field comes from the LAST I2 line, so replace the I2 field rather than append a line | check_pipeline.py L1098-1102, L931-945 | VERIFIED | |
| 02 FOR 3: pytest prints the id of a failing parametrized case | https://docs.pytest.org/en/stable/how-to/parametrize.html (`FAILED test_expectation.py::test_eval[6*9-42]`) | VERIFIED | |
| 02 FOR 3: with env set no git call is made, so `test_git_call_census` is untouched | check_pipeline.py L910-911; census counts call sites in scripts/ (work/098/03-handoff.md step 5) | VERIFIED | |
| 02 AGAINST 1: Scratch entry `05 has no Scratch dir: line (item 097)`; `+=` over problems; coverage 7 of 8 after 4 branches | check_pipeline.py L964-965, L1169 | VERIFIED | Taken into scope (Scope note) → 8 of 8 |
| 02 AGAINST 2: `main()` builds `committed` from `_head_work_files`; the printed-line wiring is covered by 095 M5 / M11 | check_pipeline.py L988-992; logs/audit/2026-11-24-095.md L41, L45 | VERIFIED | |
| 02 AGAINST 3: shared test file with open items 099, 100 and 102-104; nothing here was run yet | orchestrator task; 01 L7; 02 L60 | VERIFIED | |
| 02 AGAINST 3: TIMED precondition `log_fields_ok(..., timed=False) and not log_fields_ok(...)` holds for the fixture field | check_pipeline.py L811-816, L471, L551 | VERIFIED | |
| 02 Languages N/A, precedent 098/02 L75-76 | work/098/02-improvements.md L74-76 | VERIFIED | |
**Totals:** 40 rows checked → **39 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | tests/test_pipeline_check.py: append one test after P-e (find it by name, `test_round_build_shallow_goes_to_unchecked`), e.g. `test_shallow_elif_branch_goes_to_unchecked`. It is parametrized over 7 cases × {shallow, no git} = 14 explicit ids, each naming the branch, step and mode (`timed05-shallow`, `timed05-nogit`, `batch05-*`, `suite05-*`, `rh05-*`, `rh06-*`, `scratch05-*`, `scratch06-*`). Each case builds `d = _rh_item(tmp_path, ...)` (ID RH_ID 150, date RH_DAY) and then calls `cp.incomplete(d, logs=tmp_path/"logs", env=cp.SHALLOW_TEXT or "no git", not_seen=[], unchecked=u, committed={f"work/150/{gated file}"}, batch_nc=...)`. Fixtures: **timed05**: in `logs/implementation/<RH_DAY>.md` replace `tests 1 passed in 0.01s` with `tests 1 passed`, and in 05 replace `Suite: 1 passed in 0.01s` with `Suite: 1 passed`; entry `I2_ENTRY`. **batch05**: clean item, `batch_nc={"150": cp.BATCH_STRICT[0]}`; entry `f"LOG BATCH not computable: {cp.BATCH_STRICT[0]} (item 090)"`. **suite05**: delete the `Suite:` line from 05; entry `"05 has no 'Suite:' line (item 082)"`. **rh05**: `body05=RH_P1`; entry `f"05 heading '### Test output (round 2, pasted)' {RH_USE}"`. **rh06**: `body06="## Round 1\n### Tests re-run (output)\n2 passed in 1.50s\n"`; entry `f"06 heading '### Tests re-run (output)' {RH_USE}"`. **scratch05 / scratch06**: delete the `Scratch dir:` line from 05 / 06; entry `"<step> has no Scratch dir: line (item 097)"`. `committed` holds only 05's file for timed, batch, suite, rh05 and scratch05, and only 06's file for rh06 and scratch06. Asserts are exact: shallow `got == [] and u == [("150", entry)]`; no git `got == [entry] and u == []`. No `@NO_GIT`. Helpers are found by name, never by line | `_rh_item`, `I2_ENTRY`, `RH_USE`, `RH_P1`, `cp.BATCH_STRICT`, `cp.SHALLOW_TEXT` | 14 passing cases | `python3 -m pytest -q tests/test_pipeline_check.py -k shallow_elif_branch` → `14 passed`. The full suite is the base count + 14 passed, and I2 pastes both lines | Fixture ID 150 clears 5 of 5 cutoffs: SUITE_FROM 87, TIMED_FROM 90, ROUND_HEADING_FROM 92, SCRATCH_FROM 97, ROUND_BUILD_FROM 99 (Self-check row 1). Each of the 7 fixtures fires exactly 1 entry, read from source (01 F14-F15, 02 FOR 2). Step 1's run is the measurement |
| 2 | In the timed05 case, before the `incomplete` call, assert the precondition `cp.log_fields_ok("I2", "150", "1 files changed \| tests 1 passed", timed=False) and not cp.log_fields_ok("I2", "150", "1 files changed \| tests 1 passed")`, so a wrong fixture fails by name and cannot pass through the TESTS branch (02 AGAINST 3) | the fixture field | assertion | A fixture field with ` in 0.01s` left in makes the precondition fail (I2 tries it once and reports it in 05) | – |
| 3 | Mutant run (I2 in 05, re-run by I3 in 06), one at a time on a scratch copy of scripts/check_pipeline.py. Restore after each and `cmp` it with the original. **elif False**: M-timed L1062, M-batch L1091, M-suite L1118, M-rh L1135, M-scratch L1168. **Step key**: K-timed `unsure("06")` at L1062, K-batch at L1091, K-suite at L1118, K-rh `unsure("05")` at L1135, K-scratch `unsure("05")` at L1168. Line numbers are re-read after any rebase | scratch copy | per mutant: failing ids | Expected: M-timed → only `timed05-shallow`; M-batch → only `batch05-shallow`; M-suite → only `suite05-shallow`; M-rh → `rh05-shallow`, `rh06-shallow`; M-scratch → `scratch05-shallow`, `scratch06-shallow`; K-timed / K-batch / K-suite → the same single id as their M; K-rh → only `rh06-shallow`; K-scratch → only `scratch06-shallow`. Every no-git id stays green. Any other result is pasted and explained, never dropped | 10 mutants, 12 expected failing ids in total (Self-check row 6) |
| 4 | No change under scripts/, templates/ or .claude/. Full-clone output unchanged | base and head of the branch | empty diff | `git diff --stat <base> HEAD -- scripts/ templates/ .claude/` is empty. `python3 scripts/check_pipeline.py` output on the base vs the head of a full clone, diffed, gives only the 101 item-line changes (RI-013 practice; pasted) | – |
| 5 | 05/06 text: state that these are unit tests of `incomplete`. The printed `INCOMPLETE NOT CHECKED:` line and the `committed` wiring stay covered by 095 M5/M11 (not claimed here). RI-014 status is unchanged (OPEN until 079/081/088-095 merge) | – | 05/06 lines | I3 reads them | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| `unchecked` (`incomplete` parameter) | None | Nothing moves; every gated entry stays on the return value (strict, L1029-1030). The test always passes a list |
| `committed` (`incomplete` parameter) | None with env SHALLOW_TEXT | Every gated entry is treated as not checked (T-a6, L985). The test never passes None, so step-key mutants stay killable |
| `committed` | gated file not in it | `_unsure` False → strict entry (this is what kills the K-mutants) |
| `env` (`incomplete` parameter) | None | `_rule_seen` would call git. The test always passes SHALLOW_TEXT or "no git", so no git call is made (L910) |
| `batch_nc` | None / ID not in it / reason not in BATCH_STRICT | No LOG BATCH entry (L1086-1087, equality) |
| log files under `logs/` | unreadable | `log lines not checked (<whys>; item 089)`, never a pass (unchanged; not part of these fixtures) |
| 05/06 file | unreadable | `<step> round headings not checked` / `<step> scratch dir not checked` / `05 not checked`, never `none` (unchanged) |
| Screen tickers (`ccbot/screen.TESTS`, `MISSING_POLICY`) | n/a | n/a: there is no ticker screen in this item (pipeline checker tests only) |

## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Fixture ID vs cutoffs | fires iff int(ID) >= cutoff | 150 >= 87, 150 >= 90, 150 >= 92, 150 >= 97, 150 >= 99: all true, 5 of 5 | pass |
| TIMED fixture field | I2_TIMED needs ` in \d+\.\d+s` after the stats; LOG_FORMAT's _TAIL makes it optional | `1 files changed \| tests 1 passed`: no ` in ` → I2_TIMED no match → `log_fields_ok` (timed) False → I2 in `bad`; `1 passed` then end of string satisfies _END `(?=$...)` → LOG_FORMAT fullmatch → timed=False True → TIMED gate | pass |
| TIMED Suite pairing | `field = last[5].split(" \| tests ", 1)[1]` must equal the Suite line | field = `1 passed`; Suite rewritten to `1 passed` → equal, so Suite does not fire; left as `1 passed in 0.01s` it would differ → a second entry | pass |
| Case count | branches × steps × modes | TIMED 1 + LOG BATCH 1 + Suite 1 + round heading 2 + Scratch 2 = 7 cases; × 2 modes = 14 ids | pass |
| Coverage | covered sites / `elif unsure` sites | before: TESTS, round build, VERDICT = 3 of 8; after: 3 + 5 = 8 of 8 | pass |
| Mutant expected ids | sum of shallow ids each mutant should fail | elif False: 1 + 1 + 1 + 2 + 2 = 7; step key: 1 + 1 + 1 + 1 + 1 = 5; total 12 over 10 mutants | pass |
| K-rh kill | with committed = {06 file}, `unsure("05")` → `work/150/05-build-report.md` in committed? | no → False → strict → rh06-shallow `got == []` fails; rh05-shallow has the 05 file, so `unsure("05")` is still True there (passes, as expected) | pass |
| Strict path text | elif False entry == unsure entry | TIMED: L1064-1065 and L1082-1083 both use `log_hint("I2", "150", new_rule=True)`; no note, since `sha7` is "" (L1058). LOG BATCH: L1092 = L1094, and `[sha7]` is skipped because sha7 is "". Suite / RH: `[fired] + []` | pass |
| Totals | as-is + fixed + removed = rows | 39 + 1 + 0 = 40 | pass |

`check_handoff output (run by the orchestrator 2026-11-24 23:25 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 40
totals line: 40 rows -> 39 as-is, 1 fixed, 0 removed
PASS
```
