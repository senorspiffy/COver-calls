# 04 Build plan - 101
Fit verdict: FIT

Fit check: this item adds tests only. It touches no trading rule, no ticker, DTE or delta filter and no account-size limit, so the ~$3k account and the 001 strategy rules are untouched. It does not conflict with existing code. It unit-tests `scripts/check_pipeline.py::incomplete` (L995-1189) exactly as 095 built it, and it changes nothing under scripts/, templates/ or .claude/. Scope stays FULL with 03's widening to Scratch (5 branches, 7 cases, 14 ids). It shares one file with the open items 099, 100 and 102-104 (RI-009), so the new test goes after P-e, found by its name, and not at the end of the file. That keeps the hunk away from other items' end-of-file appends.

Tool limit: this I1 has no shell (item 072). Every claim below comes from reading the source. I2 runs it.

Recurring issues checked (item 013):
- RI-001 (ESCALATED): there is no ticker/DTE/delta filter. The only windows are the ID cutoffs. I re-read them: SUITE_FROM 87 (L441), TIMED_FROM 90 (L444), ROUND_HEADING_FROM 92 (L447), SCRATCH_FROM 97 (L451), ROUND_BUILD_FROM 99 (L454), CHECKLIST_FROM 41, LOG_CHECK_FROM 45. Fixture ID 150 clears all of them. The plan pins this with an assert in the test (below), so nothing is just assumed.
- RI-010 (ESCALATED): I write no log line. The last line of this file is the `Log fields:` line, and the orchestrator runs `--log`. I2/I3 must paste the 14-id run and each mutant's failing ids (step 3).
- RI-014 (OPEN): the item's own RI. Its status is unchanged by 101, which adds tests only (03 step 5).
- GUARDED, also checked: RI-002 (`unchecked` and `committed` are never None in these cases, and the absent cases are listed below); RI-006 (the 14 and 12 counts are re-derived below, not copied); RI-009 (shared test file, placement by name); RI-012 (exact list equality, BATCH_STRICT passed as the constant); RI-013 (03 step 4 whole-output diff kept).

## Extra research (with sources)
1. **Test ids: use one parametrize with explicit ids, not stacked decorators.** Stacked `parametrize` decorators "exhaust parameters in the order of the decorators" (https://docs.pytest.org/en/stable/how-to/parametrize.html, section "stacking"). The page does not document how stacked ids are put together, and step 3's expected failures are written as `<case>-<mode>`. So build one list of 14 `pytest.param(..., id=f"{case}-{mode}")` from a comprehension over `CASES × (("shallow", cp.SHALLOW_TEXT), ("nogit", "no git"))`, so each id is fixed by the code. Use the ids exactly as 03 spells them: `timed05`, `batch05`, `suite05`, `rh05`, `rh06`, `scratch05`, `scratch06`, each with `-shallow` and `-nogit`.
2. **The `\|` in 03 step 2 is Markdown escaping.** The Python literal is `"1 files changed | tests 1 passed"` with a bare `|`. With a backslash, LOG_FORMAT would not match and the precondition would fail for the wrong reason.
3. **Round-build check cannot fire as well.** ROUND_BUILD_HEADING is `#{1,6} round \d+ build\b` (re.I, L495). RH_P1's `## Round 2` and rh06's `## Round 1` have no `build`, so at ID 150 (>= 99) the rh cases give only the 091 entry. This matches P1/P3 in `test_stray_round_heading_is_incomplete`, whose INCOMPLETE line holds exactly one entry.
4. **The scratch cases leave the other checks alone.** Deleting the `Scratch dir:` line (from `_scratch_line`, L24-27) keeps 05's `Suite:` line and 06's Verdict/Sent back/RI lines. `scratch_dir_problems` then returns exactly `["<step> has no Scratch dir: line (item 097)"]` (L965). `+=` at L1169 makes that one `unchecked` pair.
5. **The no-git strict path adds no note.** With env set, `_rule_seen` returns `(None, "")` (L910-911). So `sha7` is "", and the `[sha7]` tails at L1095/L1121/L1138/L1171 add nothing, and so does `note` at L1084. `got == [entry]` is exact.

## Files to create/change
1 file:
- `tests/test_pipeline_check.py`: add after `test_round_build_shallow_goes_to_unchecked` (P-e; find it by name):
  - `SE_ID = RH_ID` (just an alias; the asserts use `RH_ID`) and a list `SE_CASES` of `(case, gated_step, setup)`, where setup is a small function of `(tmp_path)` that returns `(d, batch_nc, entry)`:
    - timed05: `_rh_item(tmp_path)`. In `tmp_path/"logs"/"implementation"/f"{RH_DAY}.md"` replace `tests 1 passed in 0.01s` with `tests 1 passed`. In 05 replace `Suite: 1 passed in 0.01s` with `Suite: 1 passed`. Entry `I2_ENTRY`. Gated file 05.
    - batch05: `_rh_item(tmp_path)`, `batch_nc={RH_ID: cp.BATCH_STRICT[0]}`. Entry `f"LOG BATCH not computable: {cp.BATCH_STRICT[0]} (item 090)"`. 05.
    - suite05: `_rh_item(tmp_path)`, then remove the `Suite:` line from 05. Entry `"05 has no 'Suite:' line (item 082)"`. 05.
    - rh05: `_rh_item(tmp_path, body05=RH_P1)`. Entry `f"05 heading '### Test output (round 2, pasted)' {RH_USE}"`. 05.
    - rh06: `_rh_item(tmp_path, body06="## Round 1\n### Tests re-run (output)\n2 passed in 1.50s\n")`. Entry `f"06 heading '### Tests re-run (output)' {RH_USE}"`. 06.
    - scratch05 / scratch06: `_rh_item(tmp_path)`, then remove the line starting `Scratch dir:` from 05 / 06. Entry `f"{step} has no Scratch dir: line (item 097)"`. 05 / 06.
  - `test_shallow_elif_branch_goes_to_unchecked(tmp_path, case, step, setup, env)`, parametrized over the 14 explicit ids (research 1). Body:
    1. `cp = _cp()`. Assert that `int(RH_ID)` is at least each of `cp.SUITE_FROM, cp.TIMED_FROM, cp.ROUND_HEADING_FROM, cp.SCRATCH_FROM, cp.ROUND_BUILD_FROM` (RI-001: the cutoff feasibility is pinned in code).
    2. Run setup. Each edit asserts that its target text was there before it was replaced or removed (`assert old in text`), so a fixture drifting under the other open items fails by name and never passes as a no-op.
    3. For timed05 only: the precondition from 03 step 2, with a bare `|` (research 2).
    4. `u = []`, then `got = cp.incomplete(d, logs=tmp_path / "logs", env=env, not_seen=[], batch_nc=batch_nc, unchecked=u, committed={f"work/{RH_ID}/{cp.STEPS[step]}"})`.
    5. Shallow: `assert got == [] and u == [(RH_ID, entry)], (u, got)`. No git: `assert got == [entry] and u == [], (u, got)`.
    - No `@NO_GIT` (no git call is made with env set; `test_git_call_census` counts scripts/ only).
- No change under scripts/, templates/, .claude/ or config/. No 001 rule text changes, because no rule the person follows is touched.

## Tests and checks
- `python3 -m pytest -q tests/test_pipeline_check.py -k shallow_elif_branch` → `14 passed in <s>s`, pasted in 05.
- Full suite: the base count + 14 passed, both lines pasted (I2's tests field = the full-suite line as printed, with its time).
- 03 step 3 mutants (I2 in 05, I3 re-runs in 06), on a scratch copy only, restored and `cmp`'d after each: M-timed L1062, M-batch L1091, M-suite L1118, M-rh L1135, M-scratch L1168 (`elif False`); K-timed `unsure("06")` at L1062, K-batch, K-suite, K-rh `unsure("05")` at L1135, K-scratch `unsure("05")` at L1168. Re-read the line numbers after any rebase.
- 03 step 4: `git diff --stat <base> HEAD -- scripts/ templates/ .claude/` is empty. `check_pipeline.py` output, full clone, base vs head, is diffed and pasted (only 101's own item lines may change).
- Extra fixture-drift check (research 4/5): before the 14 cases are trusted, I2 runs one mutant with the `Scratch dir:` removal disabled in scratch05. The test must fail through its `assert old in text` / list assert and must not pass.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Scope note: FULL, widened to Scratch L1168 (5 branches, 7 cases, 14 ids) | Files: SE_CASES scratch05/scratch06; 14 explicit ids |
| Scope note: "Done" = 5 elif-False + 5 step-key mutants each fail only their named ids; full-clone output unchanged | Tests and checks: 03 step 3 mutants; 03 step 4 diff |
| Step 1: one parametrized test after P-e, found by name, 14 ids | Files: `test_shallow_elif_branch_goes_to_unchecked`, placed after P-e |
| Step 1: fixtures timed05 / batch05 / suite05 / rh05 / rh06 / scratch05 / scratch06 with the given entries | Files: SE_CASES, 7 entries as written in 03 (texts re-read at L1064-1065, L1092, L1109, L1129-1130, L965) |
| Step 1: `committed` holds only the gated file | Files: body step 4 (`cp.STEPS[step]`) |
| Step 1: exact asserts in both modes | Files: body step 5 |
| Step 1: no `@NO_GIT`; helpers by name | Files: last bullet; research 5 |
| Step 1 Feasibility: ID 150 clears 5 of 5 cutoffs | Files: body step 1 (cutoff assert in code) |
| Step 2: timed05 precondition with `log_fields_ok` timed=False / timed | Files: body step 3, with a bare `|` (research 2) |
| Step 3: 10 mutants, 12 expected failing ids, no-git ids green | Tests and checks: mutant bullet. I2/I3 paste the ids |
| Step 4: no change under scripts/ templates/ .claude/; output diff | Tests and checks: step 4 bullet |
| Step 5: 05/06 say these are unit tests of `incomplete`; printed line covered by 095 M5/M11; RI-014 unchanged | Expected result, last paragraph (I2 writes it in 05, I3 checks it in 06) |
| Missing inputs: `unchecked` None → strict | DROPPED: already pinned by existing tests (095; `unsure()` L1029-1030); this item always passes a list. Not a new optional input |
| Missing inputs: `committed` None with SHALLOW_TEXT | DROPPED: already pinned by T-a6 (095); passing None here would make the K-mutants impossible to kill |
| Missing inputs: gated file not in `committed` | Built in: this is what kills K-rh / K-scratch (rh06/scratch06 have only 06's file; the 05-branch cases have only 05's file) |
| Missing inputs: env None | DROPPED: would call git; out of scope (the census test covers git call sites) |
| Missing inputs: batch_nc None / ID missing / non-strict reason | DROPPED: unchanged L1086-1087, covered by 090's tests; the other 6 cases pass `batch_nc=None` and get no LOG BATCH entry, which the exact `got`/`u` lists confirm |
| Missing inputs: unreadable logs / 05 / 06 | DROPPED: unchanged code, covered by 089/091/097 tests (e.g. `test_round_build_missing_inputs`) |
| Missing inputs: screen tickers n/a | DROPPED: no ticker screen in this item |
| Self-check rows (cutoffs, TIMED field, Suite pairing, 14 cases, 8 of 8 coverage, 12 mutant ids, K-rh kill, strict text, totals) | Re-derived below in Guardrail tests / Expected result |

## Guardrail tests
- Feasibility: ID cutoffs (87/90/92/97/99) → the cutoff assert at the top of `test_shallow_elif_branch_goes_to_unchecked`. 150 ≥ 99 ≥ 97 ≥ 92 ≥ 90 ≥ 87, 5 of 5, and it is pinned in code.
- Feasibility: each fixture fires exactly one entry → the exact-list asserts in both modes (an extra entry or a missing one fails).
- Missing inputs: `committed` without the gated file → the rh06 / scratch06 shallow ids under K-rh / K-scratch; the 05 ids under K-timed / K-batch / K-suite (all `unsure("06")` → False).
- Missing inputs: env "no git" (no anchor read) → the 7 `-nogit` ids (strict, `got == [entry]`).
- Missing inputs: `unchecked` None, `committed` None → existing 095 tests (T-a6, `unsure()` guard), not duplicated (DROPPED rows above).

## Expected result
- `tests/test_pipeline_check.py -k shallow_elif_branch` → 14 passed. The full suite is the base + 14, with no other count changing.
- Mutants, re-derived. elif False: M-timed 1 (`timed05-shallow`), M-batch 1, M-suite 1, M-rh 2 (`rh05-shallow`, `rh06-shallow`), M-scratch 2 (`scratch05-shallow`, `scratch06-shallow`) = 7. Step key: K-timed, K-batch, K-suite 1 each, K-rh 1 (`rh06-shallow`), K-scratch 1 (`scratch06-shallow`) = 5. Total 12 failing ids over 10 mutants. Every `-nogit` id stays green under every mutant. Coverage of the `elif unsure` sites in `incomplete` goes from 3 of 8 to 8 of 8.
- No diff under scripts/, templates/ or .claude/. The full-clone `check_pipeline.py` output changes only in 101's own item lines.
- 05/06 say plainly that these are unit tests of `incomplete`, and that the printed `INCOMPLETE NOT CHECKED:` line and the `committed` wiring from `_head_work_files` stay covered by 095 M5/M11. RI-014 stays OPEN until 079/081/088-095 merge.

Log fields: FIT | 1 files planned
