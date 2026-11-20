# 06 Verification - 076
Verdict: FAIL (round 1)
Sent back to: I1 I2
<!-- On every round, FAIL too, update these two lines first. Verdict: its first word is PASS or FAIL (bold allowed), then the latest round. Sent back to: I1, I2 or I1 I2 on FAIL, none on PASS. check_pipeline.py reads the first Verdict and Sent back line outside code fences (item 071). -->
Head commit verified: 266a6a2 (I2 build), on 068b01e (075 A1 PASS). Scratch worktree: /tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/076-I3/wt (detached at 266a6a2).

## I1 audit (plan vs research)
- 04 follows 03's decision: option B from 076, old `<pass>/<total>` plus pass <= total for 045-075, C and D left out. 03's regex (`_N`, `_END`, `_STATS_PARTS`, `_STATS`, `_TAIL`, `I2_BEFORE`) is carried over verbatim. `LOG_FORMAT` stays plain strings keyed by agent (03 constraint, 077).
- 04's four changes are sourced and justified: (1) `_field` for fixture IDs < 76 (checked: `_item` writes FIELDS for 048/050/060/065-070 fixtures); (2) the limit sentence reworded so it does not claim an I3/A1 duty that no agent file has (RI-010); (3) `LOG_HINT_BEFORE` as a separate dict; (4) the `\d{3}` check ahead of `int(item)` in `write_log`, pinned by T6. Extra research (PYTEST_ADDOPTS, colour, collection errors, notes) is sourced and adds only refuse cases, not code.
- **Defect P1 (plan, I1): mutation m1's expected result is wrong.** 04 says m1 (`_END` -> `(?:, )?`) "Fails T2 (R3/R4 order cases)", and Expected result says "m1-m7 each fail at least one named test". The order is enforced by the fixed sequence of optional groups in `_STATS`, not by `_END` (my m8 below: swapping failed/passed in `_STATS_PARTS` fails R3 and A3/A13). `_END`'s remaining job is to require the `, ` separator between parts, and no Self-check or T2 case covers that, so m1 survives (I2 found this; I reproduced it). The guardrail's own named check is therefore not met.
- **Defect P2 (plan, I1): `log_hint` as specified crashes on a non-numeric ID.** 04 gives `log_hint` an unguarded `int(item)`; `write_log` calls it in the refusal text, so 04's own T6 fails as planned. I2's Deviation 1 guard is needed (see I2 audit), but it is not in the plan.

## I2 audit (build vs plan)
- scripts/check_pipeline.py: every planned line is present (constants, inline `LOG_FORMAT["I2"]`, both hints, `LOG_HINT_BEFORE`, `log_fields_ok`, `log_hint`, `incomplete()` and `write_log()` call sites with the order comment, docstring with total definition and note limit). Checked against the diff of 266a6a2 line by line.
- .claude/agents/i2-builder.md L25: equals 04's quoted text word for word (python check: `i2 text verbatim: True`). RULES change: needs the person's OK in PR review. The 071 sentence is untouched.
- tests/test_pipeline_check.py: FIELDS, `I2_BEFORE_FIELD`, `_field` at both sites, the literal-line edits, and T1-T6 (6 new test functions; T1 15 cases, T2 17 cases) as planned.
- **Deviation 1 (`\d{3}` guard in `log_hint`): accepted on its merits.** It is the minimal fix for P2, it keeps the refusal exit 2 instead of a traceback, and it is pinned: with the guard removed, `test_log_refuses_non_numeric_id_without_crash` fails (1 failed, 185 passed, below). It must be written into 04 by I1 so the plan matches the build.
- **Deviation 2 (m1 survives): confirmed, and it blocks PASS.** I2 correctly did not add a test outside the plan (I2 rule 1). Fix verified in scratch: adding refuse cases `411 passed1 skipped` and `1 failed1 passed in 1.00s` to `I2_REFUSE` passes unmutated (34 passed) and kills m1 (2 failed). Both must go into 03/04's Self-check list and T2 via I1, then be built by I2.
- Connectivity re-done: `log_fields_ok` is called in `incomplete()` and `write_log()`; `log_hint` in both refusal texts; `TESTS_FORMAT_FROM`, `I2_BEFORE`, `LOG_HINT_BEFORE` read by those; `_field` used at both fixture sites. No new readers of `LOG_FORMAT["I2"]` elsewhere. No TODO.
- Feasibility re-run: 37 committed I2 lines for items >= 045 (035 for 045-074, plus 075 `488/489` and 076's own line); `log_fields_ok` refuses 0. 076's I2 line `3 files changed | tests 524 passed, 1 skipped in 85.49s (0:01:25)` equals 05's full-suite line as pasted.
- Guardrail catches the original error (scratch dir, no git): `--log I2 076 "8 files changed | tests 411/411"` -> refused, exit 2; `... tests 411 passed, 1 skipped in 64.87s` -> written, exit 0; `--log I2 075 "... tests 412/411"` -> refused with the `<pass>/<total> (pass <= total)` hint, exit 2. Known limit (documented in i2 text and docstring): an old-form `411/411` for an item < 76 is still accepted.
- RI-012: classification is `re.fullmatch` of the whole field. T2 has the pattern inside other text both before (`\x1b[32m411 passed\x1b[0m`, `===== 411 passed in 1.00s =====`) and after (`411 passed in 64.87s extra`, `411 passed garbage`).
- RI-002 (removed default put back, scratch only): restoring the pre-076 I2 definition `\d+ files? changed \| tests \d+/\d+\b.*` for all items -> 41 failed, 145 passed. m2 (pass <= total removed) -> `test_i2_tests_field_cutoff` fails. Restored; worktree `git status` clean.
- Edges of the cutoff window: 074/075 accepted old, 076/077 new (T3 checks 074, 075, 076, 077 in INCOMPLETE); 044 not checked (`test_malformed_log_line_is_incomplete`).
- Rule the person follows (001): unchanged (process tooling only). No simulator or picker involved (item 062 n/a).

## Tests re-run (output)
```
$ env | grep -E "PYTEST_ADDOPTS|PY_COLORS|FORCE_COLOR"
(no output)
$ python3 -m pytest --version
pytest 9.1.1
$ which python3.10 python3.11
/usr/bin/python3.11
$ python3 -m pytest -q        # worktree at 266a6a2
524 passed, 1 skipped in 85.42s (0:01:25)
$ python3 -m pytest -q -rs tests/test_safety.py     # includes test_every_py_compiles_on_oldest_python (python3.11; no python3.10 on PATH)
9 passed in 1.02s
$ python3 -m pytest -q tests/test_pipeline_check.py   # unmutated baseline
186 passed in 22.39s
```
Mutations (scratch worktree, `python3 -m pytest -q tests/test_pipeline_check.py`, file restored after each):
```
== m1 _END -> (?:, )?
186 passed in 24.67s                                  <- SURVIVES
== m8 failed/passed swapped in _STATS_PARTS  (my own: shows order is held by the group sequence)
FAILED tests/test_pipeline_check.py::test_i2_summary_line_accepted[1 failed, 383 passed, 1 skipped in 58.86s]
FAILED tests/test_pipeline_check.py::test_i2_summary_line_accepted[1 failed, 1 passed, 2 skipped, 1 xfailed, 1 xpassed in 0.07 seconds]
FAILED tests/test_pipeline_check.py::test_i2_summary_line_refused[411 passed, 1 failed]
3 failed, 183 passed in 24.29s
== dev1 guard removed from log_hint
FAILED tests/test_pipeline_check.py::test_log_refuses_non_numeric_id_without_crash
1 failed, 185 passed in 24.35s
== old regex restored for I2 (pre-076 definition)
41 failed, 145 passed in 24.59s
== m2 pass<=total removed
FAILED tests/test_pipeline_check.py::test_i2_tests_field_cutoff - assert (0 =...
1 failed, 185 passed in 23.81s
== proposed fix: "411 passed1 skipped", "1 failed1 passed in 1.00s" added to I2_REFUSE, unmutated
34 passed, 154 deselected in 2.75s
== proposed fix, with m1
FAILED tests/test_pipeline_check.py::test_i2_summary_line_refused[411 passed1 skipped]
FAILED tests/test_pipeline_check.py::test_i2_summary_line_refused[1 failed1 passed in 1.00s]
2 failed, 32 passed, 154 deselected in 2.86s
```
check_handoff:
```
$ python3 scripts/check_handoff.py 076 ; echo exit $?
sources count (unique URLs in 01-research.md): 5
fact-check rows: 54
totals line: 54 rows -> 44 as-is, 10 fixed, 0 removed
PASS
exit 0
```

## Real-data effect (diff_reports output, pasted)
not required (.claude/agents/i2-builder.md, scripts/check_pipeline.py, tests/test_pipeline_check.py; none is in TRIGGER or TRIGGER_DIRS)

## Recurring issues checked (step 0)
Recurring issues checked: RI-014 (only OPEN entry: no change to `_walk` or clone depth, new tests use tmp dirs without git; none ESCALATED), RI-006 (this item's root cause: the guardrail catches the original `411/411` for items >= 076, shown above; m2/m3/m4 killed; m1 not - FAIL), RI-012 (fullmatch, negative cases with the pattern inside other text before and after), RI-002 (absent/empty/`no tests ran` refused; old definition restored in scratch -> 41 failed), RI-010 (i2 text pinned by T4, claims no unowned I3/A1 duty), RI-009 (all mutations in the scratch worktree; repo tree clean), RI-001 (feasibility re-run: 37 lines, 0 refused), RI-001 escalated entry checked: no rule window involved.

## Pipeline line (step 2)
check_pipeline line: `076: I3 FAIL (FULL; sent back to I1 I2, needs a later PASS round in 06 (item 071))` (run after this file and the 00:17 --log I3 line; exit 1, `I3 FAIL: 076`, `INCOMPLETE: none`, as expected in a FAIL round)

## Sent back / sent to Audit
Not sent to Audit (no 07). Sent back:
1. **I1** (P1): fix m1's expected result. Add refuse cases `411 passed1 skipped` and `1 failed1 passed in 1.00s` (separator missing between parts) to the Self-check / T2 list, with m1 expected to fail them; correct the claim that `_END` enforces order (the group sequence does; optionally add m8 as a named mutation for order).
2. **I1** (P2): add the `re.fullmatch(r"\d{3}", item)` guard in `log_hint` to the plan (I2 Deviation 1, accepted here), with m-mutation "guard removed -> T6 fails".
3. **I2**: build the two new T2 cases, re-run m1 (must fail them) and the full suite, update 05 and the I2 log line with the new full-suite line as printed. No other code change is needed.
