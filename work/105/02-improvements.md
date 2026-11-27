# 02 Improvements - 105
## What past logs say
- logs/recurring-issues.md RI-012 status (2026-11-25): "Near miss, not counted: undated person 03/06 waiver accepted → 105." This is the same family as 100 (`_build_waived` quoted-person `.search`) and 059 (substring classification). Root cause: classification by a loose pattern instead of the documented form.
- logs/audit/2026-11-25-100.md L61-75 (R1 finding 5): A1 probed FULL item 998. `(person: x)` and `(person)` gave `in progress`, `(I2: person said)` gave `SKIPPED`, and `(person, 2026-11-20: ok)` gave `in progress`. A1 rated it real, low severity.
- work/100/02-improvements.md (100's R2) already chose `WAIVED_LINE.search` + `PERSON_DATED.match(group 2)` wrapped in `bool(...)`, and it floated a shared `_person_dated(text)` helper (its FOR 1 and AGAINST 2). 100 shipped without the helper: `_build_waived` L637-639 and `_person_waived_before_i2` L650-653 each still have their own copy (read 2026-11-25).
- RI-007, "Built (031, merged PR #8)": "a waiver of 03 or 06 counts only when the person gave it". 031 checked only who, which is the gap this item closes (R1 finding 21).
- RI-008: the project declares Python >= 3.10, so keep `re.match` and not `prefixmatch` (comment at scripts/check_pipeline.py L546-547).
- I re-read the code on 2026-11-25. R1's citations hold: `parse_request` L618-627 (`who` = text up to the first `,` `:` `)`, lower-cased), `classify` L760 and L764 (`blocked = [s for s in waived if s in PERSON_ONLY and who != "person"]`), and the regexes at L542, L548-549. The docstring at L16-18 says only "<who> must be `person`".
- **R1 finding 19's UNVERIFIED point is now settled by reading.** `batch_log_items` (L1486-1596) never calls `classify`. Its only callers are L1783 (`open_branches`) and L2243 (`main`). So N-j (tests L4662), which asserts only `_bl(...)["not_computable"]`, is not affected.
- Real data, re-grepped 2026-11-25: `^Waived:` appears in a request.md only in work/023 L4 (`02 (A1, ...)`) and work/024 L4 (`01 02 03 04 (person, 2026-10-31: ...)`). It also appears in work/062/06-verification.md L49, which is a quote and not a request.md. This matches R1 findings 15-16.

## 3 ways FOR
1. **Use the same rule as the four sibling checks, written once.**
   - Reasoning chain: FAST (L577, `FAST_BY_PERSON`), the build waiver (L639, item 100) and the LOG BATCH excuse (L653, item 093) all accept the person only in the dated form `(person, YYYY-MM-DD`. Only the 03/06 check in `classify` (L764) accepts `(person)` or `(person: x)`. Yet 03 and 06 are the strongest waivers: the L12-13 docstring says R3 and I3 are "never" skipped by FAST.
   - Bringing L764 in line removes the one place where the weaker form unlocks the stronger exception.
   - Recommendation (R1 open question 2): add one helper, `_person_dated(text)` returning `bool(m and PERSON_DATED.match(m.group(2)))` with `m = WAIVED_LINE.search(text)`, and call it from all three places. Then a fourth copy cannot drift. 100's R2 suggested the same helper, and it was not built, so this is the second time it has come up.
2. **Zero real results change, so the risk is small and measurable.**
   - Reasoning chain: there are 2 real Waived lines. 023 waives {02}, which contains no PERSON_ONLY step, so `blocked` is empty before and after. 024's group 2 is ` (person, 2026-10-31: ...`, and PERSON_DATED's leading `\s*` allows the space, so it matches before and after.
   - Changed real classify results: 0 of 2. Existing test rows whose expected value flips: 2 (N-b and N-d at tests L4640 and L4642, both `False` to `True`). The classify tests at L133 and L144 stay the same by reading. 107 and 108 use `(A1, ...)` and `(I3, ...)`, so they are blocked before and after, with the same message if the text is kept.
   - I2 and I3 can show the zero change with a before/after diff of `check_pipeline.py` output on the branch, the same check A1 used for 093 and 100.
3. **Strong negative rows are already written and can be reused, so the RI-012 guardrail is cheap.**
   - Reasoning chain: `test_person_dated_anchor` (tests L4610-4617) already pins the regex half: `(person: x)`, the quoted form and `(Person, ...)` all give None. 100's `_build_waived` cases (L1220, L1224, L1225) hold three shapes that fit a classify test with no changes.
   - Recommendation: R1's 5 rows plus 100's `(person) x (person, 2026-11-13: ok)` shape (L1225), giving 5 negative rows and 1 positive row.
   - Today the L1225 shape gives who = "person" (it stops at `)`), so classify accepts it. After the fix `.match` fails at `)`, so it is SKIPPED. That row kills mutation M-a (back to who) just as `(person)` does, and also a mutation that runs `.search` over the whole Waived line (group 0), which R1's M-b (group 2 `.search`) does not fully cover.

## 3 ways AGAINST
1. **The SKIPPED message becomes misleading for the new case.**
   - Reasoning chain: L766 prints "`<steps>` can be waived only by the person". For `Waived: 03 (person: x)` the person is already named, so the message points at the wrong fault and a reader may "fix" it by changing nothing.
   - Keeping the text keeps the L151 and L152 asserts green (R1 open question 1). But it trades clarity for a smaller diff in a check whose whole job is to explain why an item is stopped.
   - Recommendation: append the form, e.g. "... can be waived only by the person as (person, <date>: <why>)". L151 and L152 then need updating in the same item. L152 asserts only a prefix ending in "person;", so it would also need its text changed. That is 2 asserts. I3 must confirm both are updated and still fail under mutation M-a.
2. **Open-branch items are also re-classified, and the 2-file real-data count does not cover them.**
   - Reasoning chain: `open_branches` writes each branch item's files into a scratch dir and calls `classify` at L1783. A SKIPPED result goes into `skipped` (L1784-1785), which feeds the BRANCH SKIPPED output.
   - Any unmerged remote branch whose request.md has an undated `(person` waiver of 03 or 06 would newly show BRANCH SKIPPED, and the check would exit 1.
   - R1 grepped only the working tree (finding 15). I had no shell and could not list remote branches, so the claim that no open branch is affected is UNVERIFIED.
   - Guardrail: I2 runs `check_pipeline.py` on the branch before and after and diffs the OPEN BRANCHES and BRANCH SKIPPED lines too, not just the per-item lines.
3. **This is a format gate, not proof of who wrote it, and it narrows something 031 never explicitly decided.**
   - Reasoning chain: any writer can type `(person, 2026-11-25: ok)`, and the fixed code accepts it just as the old code accepted `(person)`. The gain is consistency and an explicit date (traceable to a PR or conversation), not authenticity. 100's R2 AGAINST 3 made the same point for `_build_waived`.
   - 031's text asked only that who is `person` (R1 finding 21). Templates/request.md L5 and run-item.md L10 describe the who only, though both show the dated form. So the code change tightens a rule the person approved in looser words.
   - Editing those two files is a RULE_PATHS change (049 `RULES BRANCH:`) that needs the person's OK (R1 open question 4).
   - Recommendation: change the code docstring (L16-18) in this item and word it as "the line has the documented person form (person, <date>: <why>)". Propose the template and run-item wording to the person in the PR instead of editing it silently.

## Findings by language
Random languages this cycle: none (N/A)
Languages: N/A (no new external claims). 105 is a BUG fix inside scripts/check_pipeline.py and its tests: one regex check reused from 093/100, two flipped test rows, and a docstring. It adds or changes no fee, market rule or statistic. The only outside facts (Python `re.match` anchoring, `.` excluding newline, `match` soft-deprecated in 3.15) are already sourced in 01 findings 8-10 from docs.python.org, and this review adds none.

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| All 7 | N/A (no new external claims) | - | - | - |

## Holes to watch out for (summary)
- **Keep `bool(...)` and use group 2, not group 0.** `m and PERSON_DATED.match(...)` returns None or a Match object. That works in `not dated`, but a helper shared with `_build_waived` must return a real bool because tests L1226 assert `is counts`. Run `.match` on `WAIVED_LINE.search(req_text).group(2)`, never on `waived_line` (group 0, which starts with `Waived:`, so it always fails). That slip would also block 024 and 085, so it would be caught.
- **Only gate when a PERSON_ONLY step is waived.** The shape is `blocked = [s for s in waived if s in PERSON_ONLY and not dated]`. Do not move the dated check outside the list filter, or 023 and test 106 (`02 (A1, ...)`, no 03/06) would turn SKIPPED. Test L141 would catch that, but name the row.
- **Mutations to name (I3).** (M-a) back to `who != "person"`: the `(person)`, `(person: x)` and `(person) x (person, ...)` rows fail. (M-b) `PERSON_DATED.search(group 2)`: the quoted row fails. (M-c) dated check made case-insensitive (`re.I`): the `(Person, ...)` row fails. (M-d) the dated check dropped for 06 only (e.g. `s == "03" and not dated`): a 06-only row is needed, such as `06 (person: x)` or `06 (Person, 2026-11-20: x)` from R1's list.
- **Case change fails safe but is a real change.** `(Person, 2026-11-20: x)` goes from accepted to SKIPPED (R1 finding 13). The real data has 0 such lines. Say so in the docstring, using the same wording as L647-649.
- **`who` becomes dead in classify.** Keep the 3-tuple, because changing it changes every caller's unpacking (L637, L650, L760), but rename it to `_` at L760. Otherwise a later edit may read it again as if it were the rule.
- **Unchanged known gaps.** The date is not validated (2026-13-45 matches), only the first Waived line is read (gap j), and nothing checks that the date is on or before the item's Date. Keep these listed in the docstring.
- **Real-data and branch check.** `check_pipeline.py` output before and after must be identical, including OPEN BRANCHES and BRANCH SKIPPED (AGAINST 2), and `test_person_waiver_helper_on_item_024` must stay green.

Log fields: 3 for / 3 against | languages: N/A
