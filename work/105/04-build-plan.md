# 04 Build plan - 105
Fit verdict: FIT WITH CHANGES

Fit check. This item is pipeline tooling only. It does not touch ccbot/, config/, the ~$3k account rules or the 001 strategy, so it cannot change a trade. It is consistent with existing code. The fix applies the same anchored check (`PERSON_DATED.match` on WAIVED_LINE group 2) that `_build_waived` (100) and `_person_waived_before_i2` (093) already use to the third gate, `classify`. It only narrows acceptance (03 Self-check row 11). Real effect: 0 of 2 real Waived items change (023 waives 02 only; 024 is dated), and 0 open-branch items. Re-checked 2026-11-25 by Grep `^Waived:` in work/: 023 L4, 024 L4, and a quote in 062/06 L49 that is not a request.md.

Changes to 03 (why "WITH CHANGES"):
- C1. Two absent-case rows are added to the new test, so every row in 03's Missing inputs table has a test. Row 12 is an empty group 2 (`Waived: 03 06`). Row 13 is a dated second Waived line after an undated first one (gap j). 03 listed both as inputs but had no row for them. The test now has 13 rows (9 negative, 4 positive), and the suite grows by +13, not +11. A new mutation M-h goes with row 13.
- C2. Every row's expected detail string is spelled out in full below. 03 said "exact (status, detail)" but did not list the in-progress details.
- C3. 03 step 4's kill lists are short. M-b also kills _build_waived case 7 (the I2 copied row) and N-c and N-d of `test_batch_waiver_not_excused_stays_strict`. M-f also kills `test_person_waiver_helper_on_item_024` and `test_batch_person_waiver_before_i2_excused`. M-a does not kill R12, because who "" still blocks it. These are corrections to the kill lists only. No 03 expected value changes.
- C4. `scripts/check_pipeline.py` is itself in RULE_PATHS, so this branch will show a `RULES BRANCH:` line and the docstring edit is a rule-text change. Both go to the person in the PR (see Rule text, below).

Line numbers below are from the current branch and are given only to help find things. Items 108, 109 and 110 may move them, so every place is named by its function or test.

## Extra research (with sources)
1. Python `re` docs, 3.15.2, fetched 2026-11-25 (https://docs.python.org/3/library/re.html):
   - "even in MULTILINE mode, this will only match at the beginning of the string and not at the beginning of each line". This confirms the anchor that M-b and rows R3, R4 and R13 rely on.
   - `match()` is "soft deprecated in favor of ... prefixmatch()" since 3.15. Also: "We do not plan to remove the older match() name ... code supporting older versions of Python should continue to use match()". So we keep `.match` (project declares >= 3.10, RI-008). This confirms 03 R1-9.
   - "(Dot.) In the default mode, this matches any character except a newline". So WAIVED_LINE group 2 stays on one line, and R13's second line can never become part of group 2 (confirms R1-10).
   - IGNORECASE: "Perform case-insensitive matching". With re.I, `Person` would match, which is what M-c tests (R5).
2. An edge case R3 did not list (no code change; it goes in the docstring as a known gap). PERSON_DATED is a str pattern, and in str patterns `\d` matches any Unicode decimal digit and `\s` any Unicode space (same docs page, `\d` and `\s` entries). So a date written in Arabic-Indic digits passes the format. This is the same class of gap as the "date not validated" gap 03 already records (2026-13-45). It only opens for a text that already starts `(person,`. FAST_BY_PERSON and WAIVE_BUILD_BY_PERSON share it. Fixing it (re.ASCII or `[0-9]`) would change three gates, so it is out of scope. The gap is noted in the `_person_dated` docstring. No follow-up item is needed unless the person asks for one.
3. A whitespace edge was checked by hand, and no change is needed. In `Waived:\t03\t06 (person, 2026-11-20: x)`, group 1 `[0-9 ,]+` stops at the tab, so steps = [03] and group 2 = `\t06 (person...`. The anchored match fails at `0`, so the item is SKIPPED. The base code also gives SKIPPED here (who regex fails, who = ""). It fails safe, before and after the fix.

## Files to create/change
1. `scripts/check_pipeline.py`
   - New function `_person_dated(text) -> bool`. Place it just above `_build_waived`. Body: `m = WAIVED_LINE.search(text)`, then `return bool(m and PERSON_DATED.match(m.group(2)))`. Docstring:
     - it reads only the first `Waived:` line;
     - its text after the step numbers must start with `(person, YYYY-MM-DD:` (anchored, RI-012; re.match, not prefixmatch, RI-008);
     - this is a format check on the documented form, not proof of who wrote it;
     - known gaps: `person` is case-sensitive (fails safe), the date is not validated (2026-13-45, and Unicode digits match `\d`), and a later Waived line is never read.
   - `_build_waived`: replace the two-line search/match with `return WAIVE_BUILD <= set(steps) and _person_dated(text)`. Behaviour does not change. Keep the docstring, but say the check goes through `_person_dated`.
   - `_person_waived_before_i2`: drop the local `m = WAIVED_LINE.search(...)`. The condition becomes `if (_person_dated(req_text) and pre and set(pre) <= set(waived) and not any(...))`. Behaviour does not change.
   - The comment above `WAIVED_LINE` / `PERSON_DATED` (item 093 block): PERSON_DATED is used only through `_person_dated` (by 093, 100, and from 105 by classify).
   - `classify`:
     - Unpack as `scope, opened, (waived, waived_line, _) = parse_request(req_text)`.
     - Add `dated = _person_dated(req_text)`.
     - Set `blocked = [s for s in waived if s in PERSON_ONLY and not dated]`.
     - The message becomes `f"{scope}: {' '.join(blocked)} can be waived only by the person, as (person, <date>: <why>){extra}"`.
     - The FAST check before it is unchanged.
   - Module docstring, the "03 (fact check) and 06 (verification) can be waived only by the person" sentence. Replace it with 03 step 2's text: "03 (fact check) and 06 (verification) can be waived only by the person, in the documented form: the line's text after the step numbers must start with `(person, YYYY-MM-DD:` (items 031, 105); otherwise the item is SKIPPED. This is a format check, not proof of who wrote it. `person` is case-sensitive (fails safe); the date is not validated; only the first Waived line is read."
   - `parse_request` is unchanged. Its 3-tuple and the `who` element are kept, because other callers unpack the 3-tuple. After this change, `who` has no reader. Its docstring may say so ("who: kept for the tuple shape; no gate reads it since 105"). Do not remove it in this item.
2. `tests/test_pipeline_check.py`
   - New `test_person_only_waiver_needs_dated_form`, parametrized with ids R1-R13. Place it right after `test_fact_check_and_verification_waivable_only_by_person`, so it is away from the shallow-elif area that 108 is editing.
     - Each row makes `d = tmp_path / "work" / "998"`.
     - It writes `request.md` = `"Scope: FULL\nDate: 2026-11-25\nWaived: " + row + "\n"`, and empty files for the setup's steps (names from the module's `STEPS`, or the test file's existing ALL/STEP_NAMES list).
     - It asserts `_cp().classify(d, dt.date(2026, 11, 25)) == (status, detail)`.
     - Use `dt` the way the file already does. If there is no `dt` import, use `datetime.date`.
     - Setups: A = 01 02 04 05, B = 01 02 03 04 05, C = 01 02 04 05, D = 01 03 04 05.
     - Let MSG = `can be waived only by the person, as (person, <date>: <why>)`. The rows:

       | id | setup | row (after `Waived: `) | expected |
       |---|---|---|---|
       | R1 | A | `03 06 (person)` | `("SKIPPED", "FULL: 03 06 MSG; Waived: 03 06 (person)")` |
       | R2 | A | `03 06 (person: x)` | `("SKIPPED", "FULL: 03 06 MSG; Waived: 03 06 (person: x)")` |
       | R3 | A | `03 06 (person: x "(person, 2026-11-19: ok)")` | SKIPPED, `FULL: 03 06 MSG; Waived: <row>` |
       | R4 | A | `03 06 (person) x (person, 2026-11-13: ok)` | SKIPPED, `FULL: 03 06 MSG; Waived: <row>` |
       | R5 | B | `06 (Person, 2026-11-20: x)` | SKIPPED, `FULL: 06 MSG; Waived: <row>` |
       | R6 | B | `06 (person: x)` | SKIPPED, `FULL: 06 MSG; Waived: <row>` |
       | R7 | C | `03 (person: x)` | SKIPPED, `FULL: 03 MSG; Waived: <row>` |
       | R8 | A | `03 06 (person, 2026-11-20: ok)` | `("in progress", "FULL: next 07; Waived: 03 06 (person, 2026-11-20: ok)")` |
       | R9 | B | `06 (person, 2026-11-20: ok)` | `("in progress", "FULL: next 07; Waived: <row>")` |
       | R10 | C | `03 (person, 2026-11-20: ok)` | `("in progress", "FULL: next 06; Waived: <row>")` |
       | R11 | D | `02 (A1, 2026-11-01: x)` | `("in progress", "FULL: next 06; Waived: <row>")` |
       | R12 (C1, absent) | A | `03 06` | `("SKIPPED", "FULL: 03 06 MSG; Waived: 03 06")` |
       | R13 (C1, gap j) | A | `03 06 (person: x)\nWaived: 03 06 (person, 2026-11-20: ok)` | `("SKIPPED", "FULL: 03 06 MSG; Waived: 03 06 (person: x)")`. waived_line is the first line only |

       Write MSG out in full in the test, as a module constant `PERSON_ONLY_MSG`, so a change to the wording fails one place.
   - Add a docstring to the new test: "Item 105: classify accepts a 03/06 waiver only in the documented form `(person, YYYY-MM-DD:` anchored at the text after the step numbers (RI-012). Rows R1-R7, R12 and R13 are negatives (in-text, case, one-step and absent forms); R8-R11 are positives, one per setup."
   - `test_fact_check_and_verification_waivable_only_by_person`. Change the 107 assert to `"107: SKIPPED (FULL: 03 06 can be waived only by the person, as (person, <date>: <why>); Waived: 03 06 (A1, 2026-11-01: test))"` and the 108 prefix assert to `"108: SKIPPED (FULL: 06 can be waived only by the person, as (person, <date>: <why>);"`. The `SKIPPED: 107, 108` assert and the exit code stay as they are. Its docstring gets "; item 105: and only in the dated form".
   - `test_batch_waiver_not_excused_stays_strict`: flip N-b and N-d from `False` to `True`, each with a trailing `# item 105: undated 03 waiver`. Add a docstring sentence: "From item 105, an undated 03 waiver (N-b, N-d) is also SKIPPED by classify." N-a, N-c, N-e and N-f stay as they are.
   - Unchanged, but must stay green:
     - `test_research_only_branch_waiver_needs_the_person` (its substring assert still holds);
     - `test_build_waiver_needs_person_date_and_all_three` (11 cases);
     - `test_person_dated_anchor`, `test_person_waiver_helper_on_item_024`, `test_batch_person_waiver_before_i2_excused`, `test_batch_waiver_missing_inputs_strict` (N-g to N-j);
     - `test_waived_steps_are_excused_and_printed`, `test_unreadable_request`, `test_research_code_rules`.

Not changed (rule text, for the person): `templates/request.md` L5 and `.claude/commands/run-item.md` L10 describe only `<who> = person`. 03 step 6 keeps them as a proposal in the PR text, not an edit. See Rule trace.

## Tests and checks
1. Before the code change, run the new and updated tests on the base code, and record the result in 05:
   - R1-R7 and R13 fail (each gives in progress);
   - R12 fails on its message (old wording);
   - R8-R11 pass;
   - the updated 107 and 108 asserts fail;
   - flipped N-b and N-d fail.

   Expected on base: 12 failed (9 rows + test_fact_check... + N-b + N-d), 4 passed among these.
2. After steps 1-2, run the full suite: `python3 -m pytest -q`. Expected: the base count + 13 passed, the same skips as base, 0 failed. Paste the last line as printed (I2 log format).
3. `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` exits 0 (RI-008).
4. Mutations. I2 runs them and I3 re-runs them, on a scratch copy only, one at a time, restoring each before the next. In 05 and 06, give each mutation's pytest counts and the failing test ids. The _build_waived case numbers are positions 1-11 in `test_build_waiver_needs_person_date_and_all_three`'s parameter list.
   - M-a: classify back to `who` and `who != "person"`, keeping the new message. R1-R7 and R13 fail; R5 fails because lower() gives "person". R12 still passes, because who "" blocks it, as on base.
   - M-b: `PERSON_DATED.search(m.group(2))` in `_person_dated`. These fail:
     - R3 and R4;
     - _build_waived cases 7-9 (the I2 copied, `(person: x "...")` and `(person) x` rows);
     - N-c and N-d.
   - M-c: `re.match(PERSON_DATED.pattern, m.group(2), re.I)` in `_person_dated`. R5 fails.
   - M-d: classify `not (dated or s == "06")`. R5 and R6 fail; R1-R4, R12 and R13 fail on the message (`03` only).
   - M-e: classify `not (dated or s == "03")`. R7 fails; R1-R4, R12 and R13 fail on the message (`06` only).
   - M-f: `PERSON_DATED.match(m.group(0))` in `_person_dated`. These fail:
     - R8-R10;
     - `test_waived_steps_are_excused_and_printed` (085);
     - _build_waived cases 1-2;
     - `test_person_waiver_helper_on_item_024` and `test_batch_person_waiver_before_i2_excused`.
   - M-g: `blocked = list(waived) if not dated else []`. R11 and `test_waived_steps_are_excused_and_printed` (106) fail.
   - M-h (new, kills a multi-line reader, C1): `_person_dated` reads any Waived line (`any(PERSON_DATED.match(x.group(2)) for x in WAIVED_LINE.finditer(text))`). These fail:
     - R13;
     - `test_batch_waiver_missing_inputs_strict[N-j]`;
     - _build_waived case 6.

   Each mutation must be killed by at least one row of `test_person_only_waiver_needs_dated_form`. M-f and M-g must also be killed by the named older test.
5. Real-data check (RI-014). In a full clone, not a shallow one, run `python3 scripts/check_pipeline.py` with the base script and with the head script. Diff the whole output, including OPEN BRANCHES, BRANCH SKIPPED and RULES BRANCH. Expected: identical, except lines naming item 105 itself, and the RULES BRANCH line, which now names scripts/check_pipeline.py on this branch. Exit codes are equal. If the clone is shallow, the "not checked" lines must also be identical.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map step 1: `_person_dated` helper, used by `_build_waived` and `_person_waived_before_i2`, behaviour unchanged, comment update | Files 1: `_person_dated`, `_build_waived`, `_person_waived_before_i2`, comment bullets; Tests 2 (the unchanged-test list stays green) |
| Map step 2: classify uses `dated`, `blocked = ... not dated`, new message, module docstring, parse_request unchanged | Files 1: `classify`, module docstring and `parse_request` bullets |
| Map step 3(a): new parametrized test, 11 rows, setups A-D | Files 2: `test_person_only_waiver_needs_dated_form` R1-R11, with R12 and R13 added (C1) |
| Map step 3(b): 107 and 108 message asserts updated | Files 2: `test_fact_check_and_verification_waivable_only_by_person` bullet |
| Map step 3(c): N-b and N-d flip to True, with a comment and docstring | Files 2: `test_batch_waiver_not_excused_stays_strict` bullet |
| Map step 3(d): the research-only branch test substring is unchanged | Files 2: unchanged list, `test_research_only_branch_waiver_needs_the_person` |
| Map step 4: mutations M-a to M-g | Tests 4, M-a to M-g, with the corrected kill lists (C3) and new M-h |
| Map step 5: full-output diff in a full clone, suite, py_compile | Tests 2, 3, 5 (suite +13 from C1, not +11) |
| Map step 6: propose rule text for templates/request.md L5 and run-item.md L10 in the PR, with no edit | Rule text, below: PR note for the person; these two files are not in `git diff` |
| Prevention guardrail: one anchored check used by all three gates; in-text negatives | Files 1 (`_person_dated` used three times); Tests 4 (M-a, M-b, M-c, M-d, M-e, M-h each killed by a named row) |
| Missing inputs: unreadable request.md gives UNREADABLE | Existing `test_unreadable_request` (unchanged, must stay green) |
| Missing inputs: no Waived line gives normal step rules | Existing no-waiver pipeline tests, e.g. `test_stuck_after_one_day` (unchanged) |
| Missing inputs: empty group 2 gives SKIPPED | R12 (C1) |
| Missing inputs: date missing gives SKIPPED | R1, R2, R6, R7 |
| Missing inputs: other who, `Person`, or the form quoted later gives SKIPPED | updated 107/108 asserts, R5, R3, R4 |
| Missing inputs: second Waived line ignored | R13 (C1), M-h |
| Missing inputs: date validity not checked (known gap) | DROPPED: no test pins it on purpose. A test that accepted 2026-13-45 would lock a known gap in place. It is documented in the `_person_dated` docstring and the module docstring, the same as for 093/100 |
| Self-check rows 1-8 | R1-R11 expected values (Files 2 table) |
| Self-check row 9: row count 11 | Replaced: 13 rows (9 negative, 4 positive), C1 |
| Self-check row 10: N-b and N-d flip; INCOMPLETE still present | Files 2: N-b and N-d bullet (the WAIVE_STRICT and exit 1 asserts are unchanged) |
| Self-check row 11: monotone, 0 of 2 real items change | Tests 5 (output diff identical) |
| Self-check row 12: message asserts | Files 2: 107/108 updated; the research-only branch substring is unchanged |

Rule text (001 and process rules the person follows). This item does not change a strategy rule. It does tighten a process rule's enforcement, and both the code docstring (scripts/check_pipeline.py, a RULE_PATH) and the PR proposal are flagged for the person's review:
- PR description, required section "Rule text for your review (item 105)". First, quote today's wording:
  - templates/request.md L5: `03 and 06 only with <who> = person (item 031)`
  - .claude/commands/run-item.md L10: `Only the person may waive 03 or 06 (<who> = person)`

  Then propose, for each of the two: "03 and 06 only as `(person, <date>: <why>)` (items 031, 105)".

  Then say that the module docstring in scripts/check_pipeline.py already states the new rule, and that this branch shows a RULES BRANCH line for it.

  If the person approves, the two text edits go in a new work item, not this branch. RULE_PATHS edits need the person's OK (049).

## Guardrail tests
- Feasibility: real PERSON_ONLY waivers, 1 of 1 dated (024) → `test_person_waiver_helper_on_item_024` (reads the real work/024, unchanged) plus Tests 5 (the real-output diff shows 024 unchanged, 0 of 2 Waived items change).
- Feasibility: the accept branch can be reached → R8, R9, R10 (dated, per setup) and the existing 085 assert in `test_waived_steps_are_excused_and_printed`.
- Feasibility: the non-PERSON_ONLY waiver is untouched → R11 and the 106 assert.
- Feasibility: the block branch can be reached for each step → R6 (06 only), R7 (03 only), R1 (both).
- Feasibility: 0 open-branch items with a Waived line (logs/audit/2026-11-25.md L19) → Tests 5 (BRANCH SKIPPED lines are identical).
- Missing inputs: group 2 empty → R12.
- Missing inputs: date missing → R1, R2, R6, R7.
- Missing inputs: who not `person` (other agent, case, quoted) → the 107/108 asserts, R5, R3, R4.
- Missing inputs: first line undated, second line dated → R13.
- Missing inputs: request.md unreadable → `test_unreadable_request` (unchanged).
- Missing inputs: no Waived line → the existing no-waiver pipeline tests (unchanged).

## Expected result
- `classify` gives SKIPPED for any 03 or 06 waiver whose first Waived line's text after the step numbers does not start with `(person, YYYY-MM-DD:`. The message names the form. The dated person form, and any waiver of steps other than 03/06, behave exactly as before.
- All three person-waiver gates (`classify`, `_build_waived`, `_person_waived_before_i2`) go through the one helper `_person_dated`.
- Real repo: `check_pipeline.py` output is identical before and after, except for item 105's own lines and RULES BRANCH. Exit code is the same.
- Suite: base + 13 passed, 0 failed. py_compile exits 0. Mutations M-a to M-h are each killed by a named test.

Recurring issues checked (item 013), read in logs/recurring-issues.md on 2026-11-25:
- RI-001 (ESCALATED): every filter or window rule has a non-zero dated count (1 real dated PERSON_ONLY waiver, 024; 0 undated; 0 open-branch items; 2 real Waived items) and a test that pins it (Guardrail tests, Feasibility).
- RI-014 (OPEN): nothing in the change reads git. Tests 5 asks for a full-clone diff, plus identical "not checked" lines if shallow.
- RI-002: every absent or unreadable input has an absent-case test and gives SKIPPED or UNREADABLE, never a pass (R12, R13 added).
- RI-004/RI-005: the expected details for all 13 rows, and each mutation's kill list, are re-derived from classify's code path (need/have, then `next`).
- RI-006: no hand-counted totals in a log. The suite count comes from pytest as printed.
- RI-007: FULL item through I1-I3. The plan changes no step file of another item.
- RI-008: `.match` is kept, not prefixmatch (3.15 docs), and py_compile on 3.11.
- RI-009: places are named by function and test so the plan survives 108/109/110 being built first.
- RI-010: the log line comes from the orchestrator via `--log`. None is typed here.
- RI-012: an anchored match with in-text negative rows (R3, R4), and M-b and M-h kill a scanning reader.

Log fields: FIT WITH CHANGES | 2 files planned
