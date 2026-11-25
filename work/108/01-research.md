# 01 Research brief - 108
## Question
Item 101's `timed05` case in `tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked` checks its TIMED-gate precondition against the constant `SE_FIELD`, not against the I2 field that the fixture actually wrote to its log. How can the test read that field back from the fixture's log line, so that:
(a) a change to the fixture's I2 field (`FIELDS["I2"]`) with no change to a constant still passes, and
(b) a mutation of the TIMED `elif unsure("05")` branch still fails `timed05-shallow`?
Type EFFICIENCY, Scope FULL, RI-014 (request.md). This is a test-only change. Nothing about trading or the account is involved.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
Repo facts are cited by file and line on branch daily-fixes/2026-11-25 (read 2026-11-25). External facts are cited by URL.

Where the request comes from
1. A1 judged the constant precondition "enough" and listed "read the timed05 precondition field from the fixture log line instead of `SE_FIELD`" as an optional EFFICIENCY follow-up, not a finding [logs/audit/2026-11-24-101.md L43-47, L65-67].
2. I3 recorded the same point as an observation: the precondition "tests the constant `SE_FIELD`, not the field read back from the fixture log file, which is what 03 step 2 literally asks" [work/101/06-verification.md L25].
3. 101's 03 step 2 itself wrote the precondition with the field hard-coded (`"1 files changed \| tests 1 passed"`), so the constant follows the hand-off text exactly [work/101/03-handoff.md L73].

What the test does now
4. `SE_FIELD = "1 files changed | tests 1 passed"` is defined at tests/test_pipeline_check.py L5332. Its only reader is the precondition at L5404 (grep `SE_FIELD`: L5332 and L5404 are the only code hits).
5. The precondition is `assert cp.log_fields_ok("I2", RH_ID, SE_FIELD, timed=False) and not cp.log_fields_ok("I2", RH_ID, SE_FIELD)` [tests/test_pipeline_check.py L5403-5404]. It never reads the log file, so it is true whatever the fixture wrote.
6. `_se_timed05` builds the fixture with `_rh_item(tmp_path)`, then hard-codes two edits: `"tests 1 passed in 0.01s"` → `"tests 1 passed"` in `logs/implementation/2026-11-21.md`, and `"Suite: 1 passed in 0.01s"` → `"Suite: 1 passed"` in 05 [tests/test_pipeline_check.py L5349-5353].
7. `_se_edit` asserts `old in text` before it replaces, so an edit whose text is missing fails by name [tests/test_pipeline_check.py L5335-5339].
8. The fixture's I2 field comes from `FIELDS["I2"] = "1 files changed | tests 1 passed in 0.01s"` via `_field("I2", item)` [tests/test_pipeline_check.py L17-19, L30-32]. `_item` writes one line per agent step file, `12:00 | I2 | <item> | <field>`, to `logs/implementation/<date>.md` [L60-66]. 05's `Suite:` line is the tests part of that same field (`split(' | tests ', 1)[1]`) [L52-53].
9. `RH_ID, RH_DAY = "150", "2026-11-21"`, and `_rh_item` calls `_item(root, item, ALL, date=RH_DAY)` [tests/test_pipeline_check.py L5150, L5155-5158]. The fixture therefore has exactly one I2 line for 150, in `logs/implementation/2026-11-21.md`.

Consequence for "Done looks like" (a)
10. If someone changes `FIELDS["I2"]` (for example its counts or time), the test today fails by name in `_se_edit` at L5351, because the literal `"tests 1 passed in 0.01s"` is no longer in the log. The constant precondition itself would still pass, because it never looks at the fixture (findings 5, 7). Done (a) asks for "still passes", so reading the field back at L5404 is not enough on its own. The two hard-coded edit strings in `_se_timed05` (L5351-5352) must also be derived from `_field("I2", RH_ID)` [inference from L5349-5353 and request.md L15].

How check_pipeline reads the field (the test should mirror this)
11. `LOG_LINE = re.compile(r"^(\d{2}):(\d{2}) \| (R1|R2|R3|I1|I2|I3) \| (\d{3}) \| (.*)$")`. Group 5 is the fields [scripts/check_pipeline.py L576].
12. `incomplete` collects `own_i2` = every LOG_LINE match with agent I2 and this item's ID from `_log_text(logs)`. It enters the TIMED gate when I2 is in `bad` (some line fails the timed format) and `all(log_fields_ok("I2", m[4], m[5], timed=False) for m in own_i2)` [scripts/check_pipeline.py L1060-1067].
13. `_log_text(logs)` joins every `logs/research/*.md` and `logs/implementation/*.md` file and returns `(text, whys)` [scripts/check_pipeline.py L843-856]. `_item_lines(logs)` returns `{ID: [(stamp, agent, team, file index, line index, fields), ...]}` [L1406-1430]. Either one gives the test the same lines `incomplete` reads.
14. The shallow branch under the TIMED gate is `elif unsure("05"):` at scripts/check_pipeline.py L1073-1076. A1 called it "M L1062" at commit c771a21, and the line has since moved down. Its `elif False` mutant failed only `timed05-shallow` [logs/audit/2026-11-24-101.md L30].
15. `log_fields_ok(..., timed=True)` applies `I2_TIMED` from TIMED_FROM (90) on. With `timed=False` it applies `LOG_FORMAT["I2"]`, where the time is optional [scripts/check_pipeline.py L449, L476, L557, L815-827].
16. In `I2_TIMED` the time is `in \d+\.\d+(?:s| seconds)`, right after the stats [scripts/check_pipeline.py L476]. A pattern that strips the fixture's time, such as `r" in \d+\.\d+s\b"`, follows that shape. Its exact form is left to I1/I2.

Python behaviour that matters for the precondition
17. `all()` returns True "if all elements of the iterable are true (or if the iterable is empty)" [https://docs.python.org/3/library/functions.html]. A read-back precondition shaped like L1067 (`all(... for m in own_i2)`) is vacuously true when no I2 line is found. The test must also assert that exactly one I2 line exists, or the read-back could pass on an empty log (RI-002 shape).
18. `re.sub` returns the string unchanged when the pattern is not found [https://docs.python.org/3/library/re.html]. A derived untimed field built with `re.sub` must therefore be asserted to differ from the timed field, or a time-less `FIELDS["I2"]` would make a silent no-op edit. `_se_edit`'s `old in text` covers the file, not the derivation.
19. `re.fullmatch` matches only when the whole string matches [https://docs.python.org/3/library/re.html]. That is the call `log_fields_ok` makes (L823-827), so feeding it the read-back field tests the same thing the checker tests.

## Numbers used (show the math)
- The fixture writes 6 log lines for item 150: one each for R1, R2, R3 (01, 02, 03), I1, I2, I3 (04, 05, 06). 07 has no agent in `AGENTS` [tests/test_pipeline_check.py L15, L60-66]. Exactly 1 of them is I2, so the read-back should assert `len(own_i2) == 1`.
- Current timed05 coupling points to the fixture literal: L5332 (`SE_FIELD`), L5351 (log edit), L5352 (05 Suite edit) = 3. Done (a) needs all 3 derived from `_field("I2", RH_ID)` (finding 10).
- Mutants that must still fail `timed05-shallow` (from 101/A1): `elif False` at the TIMED `elif unsure("05")` (now L1073), and its step key `unsure("06")` [logs/audit/2026-11-24-101.md L30, L35]. That is 2 mutants to re-run.

## Fit for a ~$3k account
Not applicable. This is a test-only change to the pipeline checker. It touches no trading, screen, pricing or order code and has no effect on capital, assignment, dividends, taxes, commissions or liquidity. It changes no output of the full-clone checker run (only `tests/test_pipeline_check.py` would change).

## Open questions
1. Scope of the fix. Should 108 change only L5404 (read the field back from the log, which meets the request's "What we want") or also derive L5351-5352 from `_field("I2", RH_ID)` (needed for Done (a), finding 10)? R2/R3 should pick one and say so. The brief recommends both, plus deleting `SE_FIELD` so nothing stale is left.
2. Which reader should the test use, `cp._item_lines(tmp_path / "logs")[RH_ID]` filtered to agent I2, or `cp.LOG_LINE` over `cp._log_text(...)[0]` exactly as `incomplete` does at L1064-1065? The second mirrors the checker most closely. The first is already the shared reader for LOG BATCH. Both are private names (leading `_`), which the test file already uses elsewhere (e.g. `cp._rule_seen` at L5424).
3. Should 05's `Suite:` edit be derived as the tests part of the derived untimed field (same `split(' | tests ', 1)[1]` as `_item` L53), so the 082 Suite check (L1112) keeps matching? This is UNVERIFIED by a run. R1 runs no commands, so I2 should confirm with a mutated `FIELDS["I2"]` (for example `2 files changed | tests 3 passed in 0.02s`) that `timed05-*` still pass. That is the Done (a) probe. Changing `FIELDS["I2"]` in place would also move many other tests, so the probe is better done by monkeypatching or a local override than by editing the shared constant.
4. Is A1's style nit (three blank lines before the 101 block at L5329-5331, and one blank line, not two, before `test_round_build_missing_inputs` at L5412-5413) in scope here? It is cosmetic, and R2 should decide.
