# 01 Research brief - 093
## Question
An item numbered 090 or higher that has the person's `Waived: 01 02 03 04 (person, <date>: ...)` line has no R1-I1 log line, so LOG BATCH reports `not computable: no line before I2`. From TIMED_FROM (90) on, `incomplete()` turns that reason into `INCOMPLETE: <ID> (LOG BATCH not computable: no line before I2 (item 090))`, which is exit 1 and counts as an A1 error. That is a false error for a shape the rules allow. Questions:
(a) Where do the rule and the waiver meet in the code?
(b) What exact condition should excuse the reason, and what must stay strict?
(c) Should the per-round bound apply to waived items?
(d) Which fixtures and mutations pin the fix?
How many real items are affected today?

This is a repo-internal bug (scripts/check_pipeline.py). Nearly every finding below cites a repo file and line, read on branch daily-fixes/2026-11-24 on 2026-11-24. Only the Python regex facts have a web source. Trading limits (the $3k account, assignment, taxes, liquidity) do not apply.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
1. The rules allow the waiver. run-item.md L10 says a step waived after the fact goes on a `Waived: <steps> (<who>, <date>: <why>)` line in request.md, and only the person may waive 03 or 06. [repo: .claude/commands/run-item.md L10]
2. The precedent is real. work/024/request.md L4 reads `Waived: 01 02 03 04 (person, 2026-10-31: approved by merging PR #6 ...)`. 024 is below LOG_CHECK_FROM (45), so LOG BATCH never checks it. [repo: work/024/request.md L4; scripts/check_pipeline.py L389]
3. Log lines are owed only for step files that exist. `incomplete()` builds `unlogged` from `AGENT[s]` for each `s` whose `STEPS[s]` file exists (L904-907). An item with 01-04 waived and no 01-04 files therefore owes no R1-I1 line, and has none. [repo: scripts/check_pipeline.py L904-907; tests/test_pipeline_check.py L4193 comment "no step files before 05: no R1-I1 log lines owed"]
4. In `batch_log_items`, `before` holds the item's lines ordered before its first I2. When it is empty, the item gets `not_computable` reason `"no line before I2"` and the loop moves on (L1353-1356). The whole-item bound is never computed for such an item. [repo: scripts/check_pipeline.py L1353-1356]
5. `BATCH_STRICT` includes `"no line before I2"` (L428). In `incomplete()`, a reason found in BATCH_STRICT by equality, for an ID >= TIMED_FROM, becomes `LOG BATCH not computable: <reason> (item 090)`. The only gate is `_rule_seen(item_dir, "05", "TIMED_FROM")` (L936-943). Neither function reads request.md or the waiver. [repo: scripts/check_pipeline.py L428, L936-943]
6. The docstring says this outcome is intended: "strict: a person's `Waived: 01 02 03 04` item, 024's shape, has no line before I2 and is INCOMPLETE too; no waiver excuses it" (L174-175). That sentence has to change with the fix. [repo: scripts/check_pipeline.py L174-175]
7. A test pins the current behaviour. `test_batch_no_line_before_i2_strict_from_090[990]` writes `Waived: 01 02 03 04 (person, 2026-11-20: test)`, deletes 01-04, and asserts `INCOMPLETE: 990 (LOG BATCH not computable: no line before I2 (item 090))`. The [089] case asserts `INCOMPLETE: none`. [repo: tests/test_pipeline_check.py L4184-4200]
8. A1 confirmed this as a BUG (F1). A1's root cause: the 090 claim that "no line before I2" is "impossible for every Scope" was never checked against the Waived path. A1 also wrote: "The per-round bound and the round rule keep running for waived items", and called it a near miss because no real item >= 090 has such a waiver. [repo: logs/audit/2026-11-22-090.md L90-101]
9. How waivers are parsed now. `parse_request` reads only the first `^Waived:` line (re.M). It takes `who` from the first `(` after the step numbers, `[^,:)]+`, lower-cased (L545-554). `classify` SKIPs a waiver of 03 or 06 whose `who != "person"` (L669-671). That check does not require a date, so `Waived: 03 (person: x)` passes classify. [repo: scripts/check_pipeline.py L545-554, L669-671, L377]
10. A stricter person form already exists for item 062. `_build_waived` requires `who == "person"` and `WAIVE_BUILD_BY_PERSON` = `\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:` (L475-476, L557-561). The repo also has a non-person waiver that contains a person quote: work/062/06-verification.md L49 is `Waived: 04 05 06 (I2, 2026-11-13: copied from 061 "(person, 2026-11-12: ok)")`. `WAIVE_BUILD_BY_PERSON.search` alone would match that line. `_build_waived` is safe only because it also checks `who`, which comes from the first parenthesis. [repo: scripts/check_pipeline.py L475-476, L557-561; work/062/06-verification.md L49]
11. Python's `re.search()` "checks for a match anywhere in the string". `prefixmatch()` / `match()` check "only at the beginning of the string". `fullmatch()` checks that the whole string matches. So a person check has to be anchored at the waiver's first parenthesis, not found by search (RI-012). [https://docs.python.org/3/library/re.html]
12. With `re.MULTILINE`, `^` "matches at the beginning of the string and at the beginning of each line". This is why `parse_request`'s `^Waived:` finds the line anywhere in request.md, but only the first such line (re.search). [https://docs.python.org/3/library/re.html]
13. The current Python docs mark `re.match` as "soft deprecated since version 3.15" in favour of `prefixmatch()`. The project declares Python >= 3.10 (RI-008), where only `match` exists, so new code should keep using `match`/`fullmatch`. [https://docs.python.org/3/library/re.html; repo: logs/recurring-issues.md RI-008]
14. "Every step before I2" depends on Scope. REQUIRED is FULL `01 02 03 04 05 ...`, FAST `01 03 05 06 07`, RESEARCH ONLY `01 02 03 07` (L373-375). The steps before 05 are FULL {01, 02, 03, 04} and FAST {01, 03}. A RESEARCH ONLY item has no I2 line unless 04-06 are waived, and with no I2 line `batch_log_items` skips it (L1312-1314). [repo: scripts/check_pipeline.py L373-375, L1312-1314]
15. Per-round bound. For each timed I2 line, `prev` is the item's latest earlier line. When there is none, the code does `continue`, so the first I2 round of a waived item is not evaluated. Docstring L1298-1299: "the whole-item rule's 'no line before I2' covers it". Later I2 rounds (after an I3 FAIL send-back) have a prev (the I3 line) and are already evaluated. The per-round loop runs before the `before` check, whatever the waiver (L1323-1341). [repo: scripts/check_pipeline.py L1295-1300, L1323-1341]
16. Affected items today: none. A grep for `^Waived:` under work/ finds work/023/request.md (A1, item 023 < 090), work/024/request.md (person, 024 < 090) and one quoted line in work/062/06 (not a request.md). None is numbered 090 or higher. [repo: grep `^Waived:` work/, 2026-11-24]

## Numbers used (show the math)
- Steps before I2 under each Scope, from REQUIRED (L373-375): FULL = [01, 02, 03, 04] (4 steps), FAST = [01, 03] (2 steps), RESEARCH ONLY = no I2 unless 04-06 are waived.
- Feasibility: 0 real items >= 090 have any `Waived:` line in request.md (finding 16). 1 fixture (990) has the shape. The fix changes no real item's output today. It removes a false exit 1 for the next person-waived item.
- Cutoffs involved: LOG_CHECK_FROM = 45, TIMED_FROM = 90 (L389, L396). 024 < 45, so it was never checked.

## Fit for a ~$3k account
Not a trading change. It only affects how the pipeline check reports work items, so there is no effect on capital, assignment, dividends, taxes, commissions or liquidity.

## Proposed guardrail (for R3/I1 to check; not decided here)
1. Excuse condition. `no line before I2` is excused only when all three hold:
   - the item's first `Waived:` line has who == "person" (parse_request);
   - the same line matches the dated form `(person, YYYY-MM-DD:` anchored at its first parenthesis. For example, `.match` of `\s*\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:` on parse_request's group 2, or `who == "person"` plus WAIVE_BUILD_BY_PERSON, the way `_build_waived` does it. Never a bare `.search` (finding 10, the 062/06 L49 case);
   - every step in `REQUIRED[scope]` before "05" is in the waived set.

   Any other waiver stays INCOMPLETE. Every other BATCH_STRICT reason (`no pytest time ...`, `log line with no valid time`) stays strict for waived items too.
2. Keep it visible, never silent (RI-002). The excused item should still appear on the LOG BATCH line, e.g. `not computable: 990: no line before I2 (steps before I2 waived by the person: <Waived line>)`, but with no INCOMPLETE entry. Two ways to build it (open question 1):
   - (i) `batch_log_items` reads request.md and emits a distinct reason string, which is not in BATCH_STRICT by equality;
   - (ii) `incomplete()` checks the waiver at L937.
3. Per-round bound. Keep it as it is for waived items. Later rounds are already bounded, and the first round has no prev under any rule (finding 15). Optional, needs R3 to check the order rule: bound I3's run alone (t06 from 06 only) between the first I2 line and the last I3 line. This assumes I3 starts its re-run after I2's log line, which the run-item order (I2 logs right after writing 05, then I3 runs) suggests but no test pins (UNVERIFIED).
4. Fixtures:
   - flip [990] to `INCOMPLETE: none` (exit 0, LOG BATCH still names it);
   - non-person twins that stay `INCOMPLETE: 990 (LOG BATCH not computable: no line before I2 (item 090))`:
     - (a) `(A1, 2026-11-20: test)` with 03 waived. Note that classify also gives SKIPPED here, so assert both;
     - (b) `(person: test)` with no date;
     - (c) the 062/06-style `(I2, 2026-11-20: copied "(person, 2026-11-19: ok)")`;
     - (d) person-dated but `Waived: 01 02 04`, i.e. not every step before I2. Here 03 must exist, so this variant has an R3 line or an unlogged entry. Pick the shape so it is really "no line before I2", or drop it;
   - a FAST (person) item with `Waived: 01 03 (person, <date>: ...)` that passes.
5. Mutations:
   - excuse removed → flipped [990] fails;
   - `who` check dropped (search only) → twin (c) fails;
   - date check dropped → twin (b) fails;
   - REQUIRED-subset check dropped → (d) or a partial-waiver twin fails.
6. Docstring L174-175 ("no waiver excuses it") and 093's own line must be rewritten to match.

## Open questions
1. Where should the excuse live: in `batch_log_items` (reads request.md, LOG BATCH text says why) or in `incomplete()` (keeps batch_log_items free of request.md)? Under (i), an unreadable request.md must give an unreadable reason, never "excused". classify already returns UNREADABLE for it (L662-664).
2. Should a person waiver without a date excuse it? classify accepts it for 03/06 (finding 9), but 093's request asks for `(person, <date>: ...)`. Recommendation: require the date, as 062 does.
3. Gap (j), L251: only the first `Waived:` line is read. A second line that waives 04 is ignored, so such an item stays INCOMPLETE. That fails loud, so the gap is acceptable, but it should be documented.
4. Should the optional I3-only bound (proposal 3) be built? It needs the order assumption confirmed (UNVERIFIED).
