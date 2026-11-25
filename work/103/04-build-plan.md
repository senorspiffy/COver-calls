# 04 Build plan - 103
Fit verdict: FIT WITH CHANGES

Fit check. The decision in 03 is NO-GO on the broad rule and on 02's narrow rule. No checker rule, no `*_FROM` constant and no cutoff are planned, so there is nothing that touches the ~$3k account, the strategy rules (001) or any trading code. It does not conflict with 091 (`ROUND_HEADING_FROM`) or 098 (`ROUND_BUILD_FROM`), and both stay as they are.

The change: 03 plans no file change and treats 03 itself as the "documented no-go" (request.md L15). A future reader is unlikely to find it there. The two places that send a reader toward the broad rule still read as open:
- scripts/check_pipeline.py module docstring L194 ("Known gaps: (w) runs pasted outside the two sections are not read") and L210 ("Known gaps: runs with no heading of their own").
- work/098/04-build-plan.md L75/L85 ("broad rule DROPPED ... needs a shell measurement").

So this plan adds one docstring sentence after the item 098 paragraph (L212-217) that records the measured no-go and points to work/103/03-handoff.md, plus one text-pin test so the pointer can't be removed silently. I3 can mutate it. This follows the precedent of `test_check_pipeline_docstring_names_094` (tests/test_pipeline_check.py L5688-5692). work/098 is a completed item and is not edited (RI-007, 053 precedent). logs/recurring-issues.md belongs to A1 (036), so A1 adds the RI-010 note in the daily review.

## Extra research (with sources)
1. pytest's summary line can include `deselected`. In pytest 9.0.x `KNOWN_TYPES` is `("failed", "passed", "skipped", "deselected", "xfailed", "xpassed", "warnings", "error", "subtests passed", ...)`, and `_build_normal_summary_stats_line` appends `"%d %s" % pluralize(count, key)` for each key, so a `-k`/`-m` run prints e.g. `269 passed, 8 deselected in 33.6s` ([pytest 9.0.x _pytest/terminal.py](https://docs.pytest.org/en/9.0.x/_modules/_pytest/terminal.html)). `_STATS_PARTS` (check_pipeline.py L463-465) leaves out `deselected` on purpose (L459-460). After `269 passed`, `_END` takes `, ` and then needs ` in `, so `SUMMARY_LINE` does not match. This confirms 03 step 3 residual (b): subset runs are invisible to LOG BATCH and would also be invisible to any broad summary-line rule. That weakens FOR 2 in 02 a little further ("checks what LOG BATCH needs"). It is a note only and changes nothing in the decision.
2. The template sections 03 relies on are confirmed: templates/build-report.md L4 `## Connectivity check` and L9-10 (`## Test output (pasted, not summarized)` plus the 091 sentence "never under a `###` heading or a `Round N ...` heading"). Nothing in the template forbids base-failure evidence under Connectivity check, which matches 03 L9.
3. Docstring placement: the 18-space-indented usage text is printed by `sys.exit(__doc__)` (L2203, L2208). `_rule_seen` counts a constant only at column 0 (docstring L384-387), so an indented sentence that names `ROUND_BUILD_FROM` cannot read as a rule. The planned text names no `<CONST> = ` anyway.

## Files to create/change
1. `scripts/check_pipeline.py`: module docstring only. Insert these lines right after L217 (`(round N)' (item 098)`, gated on that file like ROUND_HEADING_FROM.`) and before L218 (`  RULES BRANCH ...`), indented 18 spaces like L212-217:
   ```
                     Item 103 (gap w, RI-010): a broad rule (any SUMMARY_LINE outside a read section
                     of 05/06 is INCOMPLETE) was measured and is a documented no-go (item 103): in
                     work/076-098, 30 of 152 summary lines sit outside, 14 of them correctly quoted
                     (mutants, base-failure, audit evidence), 0 at 092-098; a `#{1,2} round N` wrapper
                     variant also flags 6 quoted of 9. See work/103/03-handoff.md before proposing it.
   ```
   No code line, constant, regex or function changes. I2 must Read L203-220 right before editing, because other items on this branch (099-102, 104) may move line numbers. Anchor on the text, not the number.
2. `tests/test_pipeline_check.py`: add one test after `test_check_pipeline_docstring_names_094` (L5688-5692):
   ```python
   def test_check_pipeline_docstring_records_103_no_go():
       """Item 103: the module docstring records the broad SUMMARY_LINE rule as a measured no-go and points to its 03."""
       doc = " ".join(_cp().__doc__.split())
       assert "documented no-go (item 103)" in doc
       assert "30 of 152 summary lines" in doc and "14 of them correctly quoted" in doc
       assert "See work/103/03-handoff.md" in doc and (REPO / "work/103/03-handoff.md").is_file()
   ```
   This adds no fixture and no git call.

Not changed (by decision in 03): no template, agent file, `*_FROM`, `SUMMARY_LINE`, `_section_flags` or `stray_run_headings`.

## Tests and checks
- `python3 -m pytest -q tests/test_pipeline_check.py -k "docstring"`: the new test and the 094 docstring test pass.
- `python3 -m pytest -q` (full suite): base count + 1 passed, no new failure. I2 pastes the base and after lines, and the `Suite:` line equals the I2 log tests field (082/090 rules).
- `python3 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` with python3.11 where available (RI-008).
- `python3 scripts/check_pipeline.py`: no new INCOMPLETE line for 076-098 and no new entry for 103 beyond the normal in-progress state (03 step 1 check).
- `git diff --stat` for 103's commits lists only work/103/, logs/, scripts/check_pipeline.py (docstring lines only, +5) and tests/test_pipeline_check.py (+1 test). `git diff -U0 scripts/check_pipeline.py` shows only added lines between the L217 and L218 anchors.
- I3 mutation: delete the inserted sentence, then the new test gives 1 failed. Change "14 of them" to "13 of them" in the docstring, then 1 failed.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Decision: NO-GO on the broad rule | Files 1 (docstring records it, with the measured counts); Files 2 pins it. No rule code. |
| Decision: NO-GO on 02's narrow rule | Files 1 (sentence "a `#{1,2} round N` wrapper variant also flags 6 quoted of 9"); no rule code. |
| Map step 1: no code/test/template/agent change; 03 is the record | Changed to FIT WITH CHANGES: a docstring-only pointer and one text-pin test (reason above: 03 alone is not where future readers look). No rule code, no `*_FROM`, no cutoff. The step-1 check is widened in Tests and checks (diff lists also the two files, docstring and test only). |
| Map step 2: narrow rule not built | Same as the narrow-rule row: nothing built. |
| Map step 3 residual (a): bare suite line under a `## Round N (...)` wrapper is seen by neither rule | DROPPED: 03 leaves it to A1's daily review with R1's script on items >= 099. No item is opened here. The docstring's existing L210 "runs with no heading of their own" still names it. |
| Map step 3 residual (b): `deselected` runs never match SUMMARY_LINE | DROPPED: note only (03). Confirmed by Extra research 1 (pytest 9.0.x KNOWN_TYPES). No change. |
| Measured count (03 L5-9): 30 / 152, 14 Q, 0 at 092-098 | Files 1 (numbers copied from 03 L6-8), Files 2 (pins "30 of 152" and "14 of them"). |
| Missing inputs: absent 05/06, unreadable 05/06, open fence, R/Q borderline, no 05/06 >= 099 | DROPPED: these are rows of R1's one-off measurement script (01 L26-58), which is not built. The planned test reads only the module docstring and checks that work/103/03-handoff.md is a file. |
| Self-check: cutoff n/a | Kept: no cutoff is taken. |
| R3 log line by the orchestrator via `--log` | Not I1's to plan; the orchestrator runs it (03 L101). |
| 001 person-followed rules (slack, tolerance, cap) | Not touched; no request needed. |

## Guardrail tests
- Feasibility: no filter or window rule is built, so no count needs pinning. The no-go's own counts (broad rule 30 hits / 152 lines; narrow rule 9 hits, work/076-098 05/06, 2026-11-24, m103-out.txt L77) are non-zero, dated in 03, and now pinned in text by `test_check_pipeline_docstring_records_103_no_go`.
- Missing inputs: the only input of the new test is the module docstring plus the path work/103/03-handoff.md. The absent case: if the sentence is missing, or the 03 file is gone or renamed, the test fails (`is_file()` is asserted, not assumed). No optional data input is added.

## Expected result
- check_pipeline.py behaves exactly as before. Its usage text carries a 5-line "Item 103" note after the 098 paragraph, so anyone reading the Known gaps for gap (w) finds the measured no-go and its 03.
- Full suite: base + 1 passed. `check_pipeline.py` output for 076-098 is unchanged.
- 103 closes as a documented no-go. The broad and narrow rules are both not built, and residuals (a) and (b) are left to A1's daily review.

Recurring issues checked (item 013), open and ESCALATED: RI-001 (ESCALATED): no unmeasured filter is planned, and every number in the docstring comes from 03's measured run. RI-010 (ESCALATED): this is the gap-(w) near miss, closed as a no-go. My log line is not typed by hand: I have no shell, so the orchestrator must run `python3 scripts/check_pipeline.py --log I1 103 "FIT WITH CHANGES | 2 files planned"` after this file is written. RI-014 (OPEN): no git call is planned, and the test is independent of clone depth. GUARDED, also checked: RI-002 (the test asserts the file exists and never assumes it), RI-007 (Scope FULL, all of I2/I3 still run, no edit to completed 098 files), RI-008 (py_compile 3.11), RI-012 (the test uses literal substrings over normalized docstring text, not error classification; no new matching rule).
Log fields: FIT WITH CHANGES | 2 files planned
