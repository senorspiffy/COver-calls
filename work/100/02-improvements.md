# 02 Improvements - 100
## What past logs say
- logs/audit/2026-11-24-093.md L58-62 (F1): A1 reproduced on 1b10d90 that `_build_waived('Scope: RESEARCH ONLY\nWaived: 04 05 06 (person: x "(person, 2026-11-19: ok)")\n')` returns True. Root cause: `WAIVE_BUILD_BY_PERSON.search` runs over the whole Waived line. A1's guardrail: use `PERSON_DATED.match(group 2)`, add an N-d-style negative test, and run a mutation back to `.search` that the test must kill.
- logs/audit/2026-11-24-093.md L53-55, L63-64 (F2): `_read` on a valid person waiver plus `\xff` returns `(None, "<path> unreadable")`. N-g's fixture is `b"\xff"` alone, so only test_read_census pins the "never excused" rule.
- work/093/02-improvements.md L51 (093's R2, Holes): this exact hole in `_build_waived` (then L561) was flagged by reasoning, with "it may need its own item". This item is that follow-up.
- logs/recurring-issues.md RI-012: "Error type guessed from a substring of free text". The root cause is "classification by short-pattern search". This bug is the same family, a near miss found before merge (request.md L14), not counted.
- RI-008: the project declares Python >= 3.10, so use `re.match`, not `prefixmatch` (already in the comment at scripts/check_pipeline.py L538-541).
- Real data, re-grepped on 2026-11-24: `^Waived:` appears in a request.md only in 023 (`(A1, ...`) and 024 (`(person, 2026-10-31: ...`). It also appears in work/062/06-verification.md L49, which is a quote and not a request.md. This agrees with R1 findings 14-15.
- templates/request.md L5 documents the form as `Waived: <steps> (<who>, <date>: <why>)`, so `(who, date:` immediately follows the steps. An anchored match enforces the documented form and adds no new rule.

## 3 ways FOR
1. **Reuse 093's audited anchor (`WAIVED_LINE` group 2 + `PERSON_DATED.match`) instead of writing a third pattern.**
   - Reasoning chain: `PERSON_DATED` is built from `WAIVE_BUILD_BY_PERSON.pattern` (L543), so the dated-person text exists in one place.
   - `_person_waived_before_i2` already uses `WAIVED_LINE.search(text)` and then `PERSON_DATED.match(m.group(2))` (L640-642). A1 passed it with mutations M3, M4 and MA killed (093 audit L38-44).
   - parse_request reads the same first line through the same `WAIVED_LINE.search` (L616). The fixed `_build_waived` therefore cannot disagree with parse_request about which line it judges.
   - `test_person_dated_anchor` (tests L4538-4545) already asserts `PERSON_DATED.match('(person: x "(person, 2026-11-19: ok)")') is None`, so the regex half of the fix is pinned today.
   - Suggested shape (by reading, not run): a small helper `_person_dated(text)` that returns `bool(m and PERSON_DATED.match(m.group(2)))` with `m = WAIVED_LINE.search(text)`. Both callers use it, so 062 and 093 cannot drift (R1 open question 2).
2. **The fix provably changes no real output, so it is low risk.**
   - Reasoning chain: L736 is the only caller, and it calls `_build_waived` only when `parse_request(...)[0] == "RESEARCH ONLY"`. Of the 2 real request.md Waived lines, 023 is RESEARCH ONLY but has steps {02}, so the `WAIVE_BUILD <= set(steps)` check is False before and after. 024 is FULL, so the function is never called for it.
   - Changed real results: 0 of 2. I2 and I3 should still diff the `check_pipeline.py` output against base, which should be IDENTICAL, as A1 did for 093 (audit L30-32).
   - The 7 existing `test_build_waiver_needs_person_date_and_all_three` cases keep their results by reading (R1 finding 11). Today 2 of 7 are True. After adding the F1 case, 2 of 8 are True.
3. **Harden N-g so the "unreadable is never excused" rule is pinned by its own test (F2).**
   - Reasoning chain: with `REQ_FULL_093.encode("utf-8") + b"\xff"`, the readable prefix is a full person waiver of 01-04. `_waived_item` drops 01-04 by default (tests L4503, L4509-4510).
   - Suppose a mutation reads request.md with `errors="replace"`. The text would then reach `_person_waived_before_i2`: Scope FULL, a person-dated 01-04, and no pre-05 files. That gives the excused reason, so `== [("990", "no line before I2")]` fails and the mutation is killed (by reading).
   - Today's `b"\xff"` alone gives no Scope (FULL default) and no Waived line, so the same mutation survives N-g (093 audit L53-55).
   - Keep the `_UNREAD` membership assert, which RI-002/RI-014 make the visible signal. Assert only the path, not the byte index: R1's count of 59 is UNVERIFIED.

## 3 ways AGAINST
1. **Dropping `who == "person"` (R1 open question 1) removes a defence that a later edit might need.**
   - Reasoning chain: after the fix, a passing `PERSON_DATED.match(group 2)` implies parse_request's `who` is "person" (R1 finding 12). The mutation that deletes the check therefore survives every test, and I3 would report it as unkilled.
   - Removing the check makes the anchor the single rule, which is cleaner. The cost is that the anchor alone carries the RI-012 protection. If someone later loosens `PERSON_DATED` (for example, makes the date optional, which is mutation MA in the 093 audit), nothing else stops `(I2, ...)`.
   - That case is still pinned: the `(I2, 2026-11-13: person said ok)` case and the copied-quote case (tests L1219, L1223) fail if `PERSON_DATED` stops requiring `person` first.
   - Recommendation: remove the check and say in the docstring that the anchor implies who. Do not leave an untestable line (an RI-002-style silent assumption). R3/I1 should decide.
2. **A shared helper touches 093's freshly audited code, which widens the change and the review.**
   - Reasoning chain: changing `_person_waived_before_i2` (L639-645) to call a new helper means 093's tests must be re-run and re-mutated. These are excused[FAST/FULL], not_excused[N-a..N-f], missing_inputs[N-g..N-j] and helper_on_item_024.
   - It adds one file region to I1's plan and a few more I3 mutations. This is EFFICIENCY cost, not risk, but it is real.
   - The smallest fix (R1 finding 9) is a one-line change inside `_build_waived` only. If the helper is chosen, I3 must re-run A1's 093 mutation list M3/M4/MA against the helper, and each must still be killed.
   - Otherwise, do the minimal edit and record "two call sites, one pattern" as accepted. Both already share `PERSON_DATED`, so the drift risk is limited to the `WAIVED_LINE.search` + `.match(group 2)` glue.
3. **The anchor is a format gate, not proof that the person wrote the line, so the docstring must not overclaim.**
   - Reasoning chain: any agent with write access can type `Waived: 04 05 06 (person, 2026-11-24: ok)` into a request.md, and the fixed code accepts it exactly as the old code did. The fix closes only the quoted-text shape (RI-012). It does not close forged authorship.
   - The real authorship evidence in the repo is outside the regex. For example, 024's line records "approved by merging PR #6" (work/024/request.md L4), and RI-007 says only the person may waive 03/06.
   - So I1/I2 should word the docstring as "the line has the documented person form", not "the person waived". Otherwise a reader may think the check is stronger than it is (an RI-002-style silent overclaim).
   - Behaviour change for honest lines is close to zero. `who` already requires group 2 to start with `(` (L617, `re.match`), so free text before the bracket is refused today too. Only a line whose first bracket is an undated or malformed `(person ...` with a dated person form later goes from True to False. That is exactly the F1 shape, and it fails safe. 0 real items are affected.

## Findings by language
Random languages this cycle: none (N/A)
Languages: N/A (no new external claims). 100 is a BUG fix inside scripts/check_pipeline.py and its tests (regex anchoring and a test fixture). It adds or changes no fee, market rule or statistic. The only outside facts (Python `re.search` vs `match` semantics, and RFC 3629 saying 0xFF never appears in UTF-8) are already sourced in 01 findings 5, 6 and 18, and this review adds none.

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| All 7 | N/A (no new external claims) | - | - | - |

## Holes to watch out for (summary)
- **Return type must stay a real bool.** The test asserts `_build_waived(...) is counts` (tests L1226). `m and PERSON_DATED.match(...)` without `bool(...)` returns None or a Match object, and every case fails. Keep `bool(...)`.
- **Group 2, not group 0.** `.match` must run on `WAIVED_LINE.search(text).group(2)`. Do not run it on parse_request's `waived_line`, which is group 0 stripped and starts with `Waived:`, so `.match` would always fail. That error would refuse the two True cases, so it is caught, but it is an easy slip.
- **Mutations to name (I3).** (M-a) back to `WAIVE_BUILD_BY_PERSON.search(waived_line)`: the new F1 case fails. (M-b) `PERSON_DATED.search(group 2)`: the F1 case fails. (M-c) date optional: `(person: ok)` fails. (M-d) subset check dropped: `Waived: 04 (person, ...)` fails. If `who` is kept, its deletion survives and must be recorded as such (AGAINST 1).
- **N-g mutation must really reach the excuse.** With replace-decode the text ends in U+FFFD after the Waived line. Check that `_person_waived_before_i2` still returns ["01", "02", "03", "04"] for it, so the N-g assert fails under the mutation. This is by reading and UNVERIFIED until I3 runs it.
- **First line only.** The two-line case (tests L1221) must stay False. `WAIVED_LINE` has `.*` without DOTALL, so group 2 does not cross a newline.
- **Unchanged known gaps.** Case-sensitive `person` (fails safe), date not validated (2026-13-45), and only the first Waived line read. Keep them in the `_build_waived` docstring, as 093 L635-638 does, so the gaps stay visible.
- **Real-data check.** check_pipeline.py output on the branch, before vs after, must be identical, and `test_person_waiver_helper_on_item_024` must stay green.

Log fields: 3 for / 3 against | languages: N/A
