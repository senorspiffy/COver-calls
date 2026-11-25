# 04 Build plan - 100
Fit verdict: FIT

Fit check: this is pipeline tooling only (scripts/check_pipeline.py and its test). It changes no trading rule, no position size or cap, and no file the bot reads, so the ~$3k account and the 001 strategy text are unaffected. No rule the person follows changes, so no 001 text update and no new request is needed. It conflicts with nothing built. 093's `WAIVED_LINE` / `PERSON_DATED` (PR #37) are reused as they are. `_build_waived` has one caller (L736), and the fix only narrows it (03 Self-check row 9). Real results: 0 of the 2 called items change (023 and 057; 001 is LEGACY). 024 and 062 are FULL, so `_build_waived` is never called for them, and 024's 093 result stays pinned by `test_person_waiver_helper_on_item_024`. This meets request.md's "work/062 and work/024 unchanged".

Recurring issues checked (logs/recurring-issues.md, read first):
- RI-001 (ESCALATED): no filter or window rule. The one count-like rule (which RESEARCH ONLY items are excused) has a dated count in 03 step 1: 3 files, 2 called, 0 True before, 0 after, Grep 2026-11-24. It is pinned by the step 5 output diff (IDENTICAL) and by the 9-case parametrized test. No count is asserted without being measured.
- RI-010 (ESCALATED): no step duty moves out of a checked field. This file ends with the `Log fields:` line (no shell, item 072). The orchestrator writes the log line with `--log`.
- RI-014 (OPEN): no git read and no new file read. `test_read_census` must stay green (step 5). M-F2 is a temporary mutation inside `_read` and is never committed.
- Also applied, GUARDED: RI-002 (every absent input gives False or the strict reason; Missing inputs table), RI-007 (narrowing only, never False to True), RI-008 (`re.match`, not `prefixmatch`; py_compile on 3.11), RI-012 (anchored `.match` plus in-text negatives plus mutations back to `.search`).

## Extra research (with sources)
1. `UnicodeError.object` is "The object the codec was attempting to encode or decode", and `start` is "The first index of invalid data in `object`". The docs also give the example `err.object[err.start:err.end]` (https://docs.python.org/3/library/exceptions.html, fetched 2026-11-24). This confirms that M-F2 can rebuild the text from the exception alone, with no new read call, so the census stays green, and that `_read`'s `not UTF-8 at byte {err.start}` is an absolute offset into the file bytes. The page gives no type for `.object` on decode errors. I2 must confirm that it is the bytes (`isinstance(err.object, bytes)`) when running M-F2. If it is not, record that in 05 and re-derive M-F2.
2. Recount of the N-g index against the fixture writer: `_waived_item` writes a `bytes` request as-is, with no `# Work item` / `Date:` header (tests L4511-4512). So the offset of `\xff` is len(REQ_FULL_093) = 12 + 20 + 26 + 1 = 59, all ASCII. This agrees with 03 Self-check row 10. A `str` request would get a header and shift the index. The plan keeps the fixture as bytes.
3. An edge case R3 did not cover, out of scope and not changed here: `classify` (L753) allows a 03/06 waiver when `who == "person"`, with no date required. So `Waived: 03 06 (person: x)` counts as the person's waiver, while `_build_waived` and the 093 helper require a date. This is not RI-012: `who` comes from an anchored `re.match` on group 2, not from a substring search. It is a looser format rule than templates/request.md L5 (`(<who>, <date>: <why>)`). I make no change, because changing it would alter item 031's rule and its real results. I note it for A1 to decide whether it needs its own item.
4. Mutant equivalence (03 R1-12) re-checked against parse_request L617. If `PERSON_DATED.match(g2)` holds, then `[^,:)]+` after `(` takes `person` plus any spaces up to the `,`. Strip and lower give "person". So `who == "person"` is implied, and removing it is correct.

## Files to create/change
1. `scripts/check_pipeline.py`
   - `_build_waived(text)` (L624-628) becomes:
     ```
     _, _, (steps, _, _) = parse_request(text)
     m = WAIVED_LINE.search(text)
     return WAIVE_BUILD <= set(steps) and bool(m and PERSON_DATED.match(m.group(2)))
     ```
     Keep `bool(...)`: the test asserts `is counts`.
   - New docstring: item 062 and item 100. The first Waived line excuses 04 05 06 only when the text after the step numbers starts with `(person, YYYY-MM-DD:` (PERSON_DATED.match, anchored, RI-012). A person form quoted later never counts. This is a format check on the documented form, not proof of who wrote it. The anchor implies who = person. Known gaps, unchanged: `person` is case-sensitive (fails safe), the date is not validated, and only the first Waived line is read.
   - The comment at L538-541 also names `_build_waived` (item 100) as a user of the PERSON_DATED `.match` rule.
   - No other line changes. `WAIVE_BUILD_BY_PERSON` stays, because PERSON_DATED is built from it.
2. `tests/test_pipeline_check.py`
   - `test_build_waiver_needs_person_date_and_all_three` (L1215-1226): add two cases, each with `# item 100 (RI-012)`:
     - `('Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")', False)` (the F1 line)
     - `("Waived: 04 05 06 (person) x (person, 2026-11-13: ok)", False)` (first bracket closed, no date)
   - `test_batch_waiver_missing_inputs_strict` (L4586-4601): the N-g param becomes `REQ_FULL_093.encode("utf-8") + b"\xff"`. Keep the `[("990", "no line before I2")]` assert and the path-in-`_UNREAD` assert. Inside the `isinstance(req, bytes)` branch, add `assert cp._UNREAD[<path>] == "not UTF-8 at byte 59", cp._UNREAD`. Docstring: N-g is a valid person waiver plus one bad byte (item 100, F2).

## Tests and checks
- Before the fix (I2, base code): both new cases fail, each returning True. The new N-g passes. Paste the counts.
- After the fix: all 9 `test_build_waiver...` cases pass (2 True, 7 False).
- Mutations: run each one alone on a scratch copy and restore it afterwards. I2 runs them and I3 re-runs them. 05 and 06 list the failing test names and the pytest line for each:
  - M-a: `who == "person" and bool(WAIVE_BUILD_BY_PERSON.search(waived_line))`. Both new cases fail.
  - M-a2: bare `WAIVE_BUILD_BY_PERSON.search(waived_line)`. The 2 new cases and the `(I2 ... copied ...)` case fail.
  - M-b: `PERSON_DATED.search(m.group(2))`. Both new cases fail.
  - M-c: date optional (`\(\s*person\s*[,:]`). `(person: ok)` fails, and so do N-b, N-d, N-j and `test_person_dated_anchor`.
  - M-d: subset check dropped. `Waived: 04 (person, ...)` fails.
  - M-F2: in `_read`'s decode-error branch, after `_UNREAD[shown] = ...`, add `return err.object.decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n"), None`. The new N-g fails. Run it once more with the old `b"\xff"` fixture: N-g passes there, which is the F2 evidence. Record any other failures.
- Real data: run `python3 scripts/check_pipeline.py` with the base script and then with the fixed script on the branch head. The diff must be empty (IDENTICAL).
- Full suite: `python3 -m pytest -q`. The count must be base + 2 passed.
- `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` must exit 0.
- These must stay green: `test_person_waiver_helper_on_item_024`, `test_read_census`, `test_person_dated_anchor`, `test_research_code_rules`, `test_inbox_quoted_scope_and_waiver_are_not_read`.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1: anchored `_build_waived`, `who` check removed, no shared helper, docstring, L538-541 comment | Files 1 (all four bullets) |
| Step 2: two in-text negatives, 9 cases (2 True) | Files 2, first bullet; Tests "Before" and "After" |
| Step 3: N-g = REQ_FULL_093 + `\xff`; strict reason; `_UNREAD` path; `not UTF-8 at byte 59` | Files 2, second bullet; Extra research 2 |
| Step 4: mutations M-a, M-a2, M-b, M-c, M-d, M-F2 (plus M-F2 on the old fixture) | Tests "Mutations" (all 6, plus the old-fixture run) |
| Step 5: output diff IDENTICAL, suite base + 2, py_compile 3.11, 024/census/anchor tests green | Tests "Real data", "Full suite", py_compile, "must stay green" |
| Prevention guardrail (steps 2-4) | Files 2 and Tests "Mutations" (M-a/M-a2/M-b killed by the new cases; M-F2 killed by the new N-g) |
| Missing inputs: request.md missing at the tip | Unchanged code path (L734); existing `test_research_code_rules`, which must stay green |
| Missing inputs: no Waived line / empty group 2 / undated, other who, quoted, or `Person` | 9-case test: `(person: ok)`, `(I2, ...)`, the two new cases, the two-line case; empty group 2 via M-d / the `04` case. See Guardrail tests |
| Missing inputs: no Scope line | Unchanged; N-i (FULL default) stays green |
| Missing inputs: second Waived line ignored | Existing two-line case (L1221) and N-j |
| Missing inputs: request.md unreadable or missing in batch_log_items | New N-g (unreadable) and N-h (missing), both unchanged in their expectation |
| R1 OQ2 shared helper | DROPPED: 02 AGAINST 2. Widens 093's audited code; both sites already share WAIVED_LINE/PERSON_DATED |
| R1 guardrail 4's batch_log_items replace-decode mutation | DROPPED: 03 found it WRONG (already killed by today's N-g and the census); replaced by M-F2 |

## Guardrail tests
- Feasibility: the RESEARCH ONLY excuse rule (3 files, 2 called, 0 True before and after, Grep 2026-11-24) → step 5 output diff IDENTICAL, plus `test_build_waiver_needs_person_date_and_all_three` (9 cases, 2 True).
- Missing inputs: no `Waived:` line → covered by RES_160 with no Waived line. 03 does not pin this as a named case, so I add one more planned case: `("", False)` (RES_160 + "\n"; `m` is None → False), marked `# item 100 (absent)`. The suite count then becomes base + 3, and the 9-case count in 03 becomes 10 cases (2 True, 8 False). I2 records the change in 05.
- Missing inputs: empty group 2 → `("Waived: 04 05 06", False)`, also added with `# item 100 (absent)` (`PERSON_DATED.match("")` is None). That makes 11 cases (2 True, 9 False), so the suite count is base + 4.
- Missing inputs: quoted, undated, other who → the two new cases plus the existing `(person: ok)`, `(I2, ...)` and `(I2 ... copied ...)` cases.
- Missing inputs: unreadable request.md → new N-g with `not UTF-8 at byte 59`. Missing request.md → N-h.
- Missing inputs: second Waived line → the L1221 case and N-j.

Change from 03 (FIT, not WITH CHANGES, because this only adds absent-case tests and changes no rule): the two absent-case parametrize rows above. Expected counts are corrected below.

## Expected result
- `_build_waived` returns False for the F1 line and for `(person) x (person, <date>: ...)`, and True only for an anchored `(person, YYYY-MM-DD:` form with 04 05 06 waived.
- `test_build_waiver_needs_person_date_and_all_three` has 11 cases (2 True, 9 False), all passing. The 2 new in-text cases fail on the base code.
- The new N-g passes on the base and fixed code and fails under M-F2. The old fixture passes under M-F2.
- All 6 mutations are killed by named tests.
- The check_pipeline output is IDENTICAL before and after. The suite count is base + 4 passed with no new failures. py_compile 3.11 exits 0.
- Files changed: 2 (scripts/check_pipeline.py, tests/test_pipeline_check.py).

Log fields: FIT | 2 files planned
