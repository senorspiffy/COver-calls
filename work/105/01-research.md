# 01 Research brief - 105
## Question
`classify` in scripts/check_pipeline.py accepts a person's waiver of 03 (fact check) or 06 (verification) when the first `Waived:` line's who is `person`, even with no date. The undated forms `Waived: 03 06 (person)` and `(person: x)` are accepted. 062/100 (build waiver) and 093 (LOG BATCH excuse) already require the dated form `(person, YYYY-MM-DD: <why>)`. Questions:
(a) Where is the loose check, and what is the smallest anchored fix that reuses PERSON_DATED?
(b) Which real items and existing tests change result?
(c) Which negative tests and which mutation pin it (RI-012 guardrail)?

This is a repo-internal bug. Every finding cites a repo file and line, read on branch daily-fixes/2026-11-25 on 2026-11-25. Only the Python regex facts have a web source. I had no shell, so behaviour claims are by reading, except the probe A1 ran (finding 5).

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
1. The module docstring states the rule as: a `Waived: <steps> (<who>, <date>: <why>)` line excuses those steps, and "03 (fact check) and 06 (verification) can be waived only by the person: <who> must be `person`, otherwise the item is SKIPPED (item 031)". [repo: scripts/check_pipeline.py L16-18]
2. `PERSON_ONLY = ("03", "06")`. [repo: scripts/check_pipeline.py L429-430]
3. `parse_request` takes `who` as `re.match(r"\s*\(\s*([^,:)]+)", waived.group(2))`, stripped and **lower-cased**. That is the text after the first `(` up to the first `,`, `:` or `)`. The date part is never read. [repo: scripts/check_pipeline.py L618-627]
4. `classify` blocks only on who: `blocked = [s for s in waived if s in PERSON_ONLY and who != "person"]`. If nothing is blocked, it goes on to `need = [s for s in REQUIRED[scope] if s not in waived]`, so 03/06 are excused. `who` has no other reader in the file. [repo: scripts/check_pipeline.py L760-767; grep `who` in scripts/check_pipeline.py]
5. A1 probe (FULL item 998 with 01 02 04 05, no 03/06): `(person: x)` and `(person)` give `in progress`, `(I2: person said)` gives `SKIPPED`, and `(person, 2026-11-20: ok)` gives `in progress`. A1 rated it real, low severity. [repo: logs/audit/2026-11-25-100.md L61-75]
6. The anchored pieces already exist. `WAIVED_LINE = re.compile(r"^Waived:\s*([0-9 ,]+)(.*)$", re.M)` (group 2 = the text after the step numbers) and `PERSON_DATED = re.compile(r"\s*" + WAIVE_BUILD_BY_PERSON.pattern)`, where `WAIVE_BUILD_BY_PERSON = r"\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:"`. The comment says PERSON_DATED "is used only with .match on WAIVED_LINE group 2". [repo: scripts/check_pipeline.py L542-549]
7. `_build_waived` (100) and `_person_waived_before_i2` (093) both use the same shape: `m = WAIVED_LINE.search(text)`, then `bool(m and PERSON_DATED.match(m.group(2)))`. [repo: scripts/check_pipeline.py L637-639, L650-655]
8. `re.match`/`prefixmatch` matches "zero or more characters at the beginning of *string*", and "Even in MULTILINE mode, this will only match at the beginning of the string". `re.search` will "Scan through *string* looking for the first location". [https://docs.python.org/3/library/re.html]
9. `match()` is "Soft deprecated since version 3.15" in favour of `prefixmatch()`, but the docs say to "Use that name when you need to retain compatibility with older Python versions". The project declares >= 3.10 (RI-008), so the fix should keep `.match`, as the L546-547 comment says. [https://docs.python.org/3/library/re.html; repo: logs/recurring-issues.md RI-008; scripts/check_pipeline.py L546-547]
10. In default mode `.` "matches any character except a newline", so WAIVED_LINE group 2 never runs past the first `Waived:` line. [https://docs.python.org/3/library/re.html; repo: scripts/check_pipeline.py L548]
11. Proposed fix (smallest, by reading): in `classify`, block a PERSON_ONLY step unless the first Waived line's group 2 `PERSON_DATED.match`es. For example, `m = WAIVED_LINE.search(req_text)`; `dated = bool(m and PERSON_DATED.match(m.group(2)))`; `blocked = [s for s in waived if s in PERSON_ONLY and not dated]`. Then update the docstring at L16-18. [repo: scripts/check_pipeline.py L548-549, L760-766]
12. By reading, the fix gives these results: `(person)` and `(person: x)` give `[^,]`/no `,` after `person`, so no match and SKIPPED. `(A1, 2026-11-01: test)` gives no match and SKIPPED (unchanged). `(person: x "(person, 2026-11-19: ok)")` (quoted) gives no match, because `.match` cannot move to the quote, so SKIPPED. `(person, 2026-11-20: ok)` matches (unchanged). 093's `test_person_dated_anchor` already asserts the anchor on `(person: x)`, the quoted form and `(Person, ...)`. [repo: scripts/check_pipeline.py L542, L549; tests/test_pipeline_check.py L4610-4617]
13. Side effect on case: today `who` is lower-cased, so `Waived: 03 (Person, 2026-11-20: x)` is accepted. PERSON_DATED is case-sensitive, so after the fix that line is SKIPPED. This fails safe, and it is the same rule as FAST_BY_PERSON, `_build_waived` and the 093 helper ("`person` is case-sensitive ... fails safe"). [repo: scripts/check_pipeline.py L577, L623-627, L635, L647-649]
14. After the fix, `who` from `parse_request` has no reader in `classify`. Its only use is L764 (finding 4). [repo: scripts/check_pipeline.py L760, L764]
15. Real data: only two request.md files have a `Waived:` line. work/023 has `02 (A1, 2026-10-31, ...)`, which waives no PERSON_ONLY step. work/024 has `01 02 03 04 (person, 2026-10-31: ...)`, which waives 03 in the dated form. [repo: grep `^Waived:` work/*/request.md, 2026-11-25; work/023/request.md L4; work/024/request.md L4]
16. So 023 is unchanged (blocked is empty before and after). 024 is unchanged: its group 2 begins with `(person, 2026-10-31:`, and PERSON_DATED's leading `\s*` allows a space. A1 grepped the same two lines. [repo: work/024/request.md L4; scripts/check_pipeline.py L549; logs/audit/2026-11-25-100.md L73-74]
17. Existing tests that keep their result by reading: `test_fact_check_and_verification_waivable_only_by_person` (107 `03 06 (A1, ...)` and 108 `06 (I3, ...)` are still SKIPPED with the same message, if the message text is unchanged), and `test_waived_steps_are_excused_and_printed` (085 is dated person and 106 waives 02 only). [repo: tests/test_pipeline_check.py L133-153]
18. **Existing tests that change result.** In `test_batch_waiver_not_excused_stays_strict`, rows N-b `Waived: 01 02 03 04 (person: test)` and N-d `Waived: 01 02 03 04 (person: x "(person, 2026-11-19: ok)")` assert `("990: SKIPPED" in out) == False`. Both waive 03 undated, so after the fix both give `990: SKIPPED`, and their `skipped` value must change to True. These rows pin today's loose behaviour as a side assertion. [repo: tests/test_pipeline_check.py L4638-4655]
19. N-j (`(person: no date)` first line, waiving 03) is in `test_batch_waiver_missing_inputs_strict`, which asserts only `_bl(...)["not_computable"]`, not the classify status. By reading it is unaffected. UNVERIFIED: I did not check whether `batch_log_items` reads `classify`'s result. [repo: tests/test_pipeline_check.py L4658-4676]
20. `test_build_waiver_needs_person_date_and_all_three` calls only `_build_waived`, not `classify`. Its `(person: ok)` and quoted rows waive 06, but they are unaffected. [repo: tests/test_pipeline_check.py L1215-1230]
21. 031 asked only that "its 'who' is `person`". Its example was dated (`Waived: 03 (person, 2026-11-01: ...)`), but no 031 file decided that undated should pass. [repo: work/031/request.md L20]
22. The rule files describe the who only. templates/request.md L5 says "03 and 06 only with <who> = person (item 031)", and run-item.md L10 says "Only the person may waive 03 or 06 (`<who>` = `person`)". Both already show the `(<who>, <date>: <why>)` form. [repo: templates/request.md L5; .claude/commands/run-item.md L10]

## Numbers used (show the math)
- Feasibility (RI-001): real request.md files with a `Waived:` line = 2 (023, 024). Of these, files that waive 03 or 06 = 1 (024), and it is dated. Undated PERSON_ONLY waivers = 0, so 0 real `classify` results change (findings 15-16).
- Existing test rows whose expected value flips = 2 (N-b, N-d, finding 18). Other classify waiver tests = 2 (L133, L144), and both are unchanged by reading.
- Suggested new negative rows for a classify test (FULL item, 01 02 04 05 present, no 03/06), each expected SKIPPED: `03 06 (person)`, `03 06 (person: x)`, `03 06 (person: x "(person, 2026-11-19: ok)")` (quoted), `06 (Person, 2026-11-20: x)` (case). One positive row: `03 06 (person, 2026-11-20: ok)`, not SKIPPED. That is 4 negative + 1 positive = 5 rows.

## Fit for a ~$3k account
Not a trading change. It only affects how the pipeline check accepts the person's waiver of R3's fact check and I3's verification. There is no effect on capital, assignment, dividends, taxes, commissions or liquidity.

## Proposed guardrail (for R3/I1 to check; not decided here)
1. Code: finding 11. Reuse WAIVED_LINE + `PERSON_DATED.match` on group 2 (anchored, `.match` not `.search`) in `classify`. Optionally add one shared helper, `_person_dated(text)`, used by `_build_waived`, `_person_waived_before_i2` and `classify`, so the anchored check is written once (open question 2). Update the docstring at L16-18.
2. Tests: a named classify test (for example `test_person_only_waiver_needs_dated_form`) with the 5 rows above. Flip N-b and N-d to `skipped=True`, with a comment naming 105.
3. Mutations (each must fail the named test):
   - (M-a) back to `who != "person"`: the `(person)` and `(person: x)` rows fail.
   - (M-b) `PERSON_DATED.search(group 2)`: the quoted row fails.
   - (M-c) `who` compared without the dated check but case-insensitive: the `(Person, ...)` row fails.
4. Real data: `check_pipeline.py` output before and after must be identical on the branch (findings 15-16), and `test_person_waiver_helper_on_item_024` stays green.

## Open questions
1. Message text: keep "can be waived only by the person" for the undated case (then L151's assert stays unchanged), or add "needs (person, <date>: <why>)" for the undated case? A new text needs a new assert. Recommendation: keep one text, and name the dated form in it only if L151 is updated in the same item.
2. Should one shared helper replace the three copies of `m = WAIVED_LINE.search(...)` + `PERSON_DATED.match`? That is a small refactor, and all three helpers' tests must stay green.
3. `who` becomes unused (finding 14). Keep it in `parse_request`'s return value (no caller change), or remove it? Removing it changes the 3-tuple that every caller unpacks.
4. Should templates/request.md L5 and run-item.md L10 say "03 and 06 only as `(person, <date>: <why>)`"? These are RULE_PATHS edits (049 `RULES BRANCH:`), so they need the person's OK in review.
5. Known gaps, unchanged and out of scope: the date is not validated (2026-13-45 matches), and only the first `Waived:` line is read (gap j).
