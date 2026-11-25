# 03 Research hand-off - 105
Status: READY

Recurring issues checked (item 013), read in logs/recurring-issues.md 2026-11-25: RI-001 (ESCALATED) and RI-014 (OPEN), the only entries not GUARDED; also RI-002, RI-004, RI-005, RI-006, RI-007 and RI-012, because they relate to this item.
- RI-001: every rule in the map has a computed count in Feasibility (real Waived lines, real PERSON_ONLY waivers, open-branch items, test rows). The accept branch is reachable: 1 of 1 real PERSON_ONLY waivers passes (024), plus test 085.
- RI-002: an absent or unreadable input never becomes a pass. A missing group 2, a missing date, another who or `Person` all give SKIPPED (Missing inputs table).
- RI-004/RI-005: each test row's expected status and message are re-derived from the rule in Self-check rows 1-11.
- RI-006: I did not count totals by hand for the log. The orchestrator runs check_handoff.
- RI-007: the item is FULL. Its code change goes through I1-I3, and the 031 rule (only the person waives 03/06) only gets stricter.
- RI-012: an anchored `.match` on group 2 with in-text negative rows (quoted form, `(person) x (person, ...)`). M-b kills a `.search`.
- RI-014: step 5 asks for the before/after output diff in a full clone. If the clone is shallow, the "not checked" lines must be identical too, and nothing in the change reads git.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| R1-1: the docstring says 03/06 can be waived only by the person, and that who must be `person` | scripts/check_pipeline.py L16-18 | VERIFIED | - |
| R1-2: `PERSON_ONLY = ("03", "06")` | check_pipeline.py L429-430 | VERIFIED | - |
| R1-3: parse_request takes who as `\s*\(\s*([^,:)]+)` on group 2, stripped and lower-cased; the date is never read | check_pipeline.py L618-627 | VERIFIED | - |
| R1-4: classify blocks only on `who != "person"`; who has no other reader | check_pipeline.py L760, L764-767; Grep `\bwho\b` (L760 and L764 are the only code uses) | VERIFIED | - |
| R1-5: A1 probe, item 998: `(person: x)` and `(person)` give in progress, `(I2: person said)` gives SKIPPED, the dated form gives in progress | logs/audit/2026-11-25-100.md L61-75 (probe lines L64-67) | VERIFIED | - |
| R1-6: WAIVED_LINE, PERSON_DATED and WAIVE_BUILD_BY_PERSON, with the "used only with .match on group 2" comment | check_pipeline.py L542-549 | VERIFIED | - |
| R1-7: _build_waived and _person_waived_before_i2 both use WAIVED_LINE.search, then PERSON_DATED.match on group 2 | check_pipeline.py L637-639, L650-655 | VERIFIED | - |
| R1-8: match anchors at the start of the string even in MULTILINE; search scans for the first location | https://docs.python.org/3/library/re.html (fetched 2026-11-25) | VERIFIED | - |
| R1-9: match() is soft-deprecated in 3.15 in favour of prefixmatch(), and the old name is kept for compatibility; the project declares 3.10 or later, so keep `.match` | docs.python.org re ("Use that name when you need to retain compatibility with older Python versions"); RI-008; check_pipeline.py L546-547 | VERIFIED | - |
| R1-10: in default mode `.` does not match a newline, so group 2 stays on the first Waived line | docs.python.org re; check_pipeline.py L548 | VERIFIED | - |
| R1-11: smallest fix: in classify, `dated` from PERSON_DATED.match on group 2, and `blocked` uses `not dated` | check_pipeline.py L548-549, L760-766 | VERIFIED | Built as a shared helper (map step 1, 02 FOR 1) |
| R1-12: after the fix, `(person)`, `(person: x)`, the quoted form and `(A1, ...)` give SKIPPED and the dated form passes; test_person_dated_anchor already pins the regex | check_pipeline.py L549; tests/test_pipeline_check.py L4610-4617 | VERIFIED | Self-check rows 1-4 |
| R1-13: `(Person, ...)` is accepted today because of lower(); after the fix it is SKIPPED (fails safe, same as FAST_BY_PERSON and 093) | check_pipeline.py L577, L627, L635, L647-649 | VERIFIED | - |
| R1-14: after the fix, who has no reader in classify | Grep `\bwho\b` | VERIFIED | Renamed to `_` at L760 (step 2) |
| R1-15: only work/023 and work/024 have a `Waived:` line in request.md | Grep `^Waived:` in work/ on 2026-11-25: 023 L4, 024 L4, plus 062/06-verification.md L49 (a quote, not a request.md) | VERIFIED | - |
| R1-16: 023 does not change; 024's group 2 starts with `(person, 2026-10-31:`, which matches | work/023/request.md L4; work/024/request.md L4; audit 2026-11-25-100.md L73-74 | VERIFIED | - |
| R1-17: test L133 and test L144 keep their result if the message is unchanged | tests L133-153 | VERIFIED | The message is changed (step 2), so the L151 and L152 asserts are updated (step 3). Their status is unchanged |
| R1-18: rows N-b and N-d in test_batch_waiver_not_excused_stays_strict flip to skipped=True | tests L4638-4655; `_waived_item` L4575-4589 (05, 06 and 07 present, 01-04 dropped) | VERIFIED | The INCOMPLETE and exit-1 assert is unchanged: incomplete() runs for every listed item (L2266) |
| R1-19: N-j is unaffected; marked UNVERIFIED (does batch_log_items read classify?) | Grep `classify\(`: calls only at L1783 (open_branches, from L1663) and L2243 (main); batch_log_items starts at L1486 | VERIFIED | Fixed: the UNVERIFIED point now has a source. batch_log_items never calls classify, so N-j is unchanged |
| R1-20: test_build_waiver_needs_person_date_and_all_three calls only _build_waived | tests L1215-1230 | VERIFIED | It stays green after the helper refactor (step 1) |
| R1-21: 031 asked only that who is `person`; its example was dated | work/031/request.md L20 | VERIFIED | - |
| R1-22: templates/request.md L5 and run-item.md L10 describe who only, and show the dated form | templates/request.md L5; .claude/commands/run-item.md L10 | VERIFIED | - |
| R1 Numbers: 2 real Waived lines, 1 waives 03/06 (dated), 0 undated, 0 real results change | Grep (R1-15) | VERIFIED | Open branches are added in R2-4 |
| R1 Numbers: 5 test rows (4 negative, 1 positive) | R1 and R2 mutation lists | VERIFIED | Fixed: 11 rows (7 negative, 4 positive). Added 06-only and 03-only rows (to kill M-d and M-e), the `(person) x (person, ...)` row (02 FOR 3), positives for each setup, and a 02-only row (M-g) |
| R2-1: classify's only callers are L1783 and L2243 | Grep `classify\(` | VERIFIED | - |
| R2-2: 024's group 2 is ` (person, 2026-10-31: ...` (leading space) | check_pipeline.py L548: group 1 `[0-9 ,]+` is greedy and takes the space after `04` | VERIFIED | Fixed: group 2 starts with `(`, with no space. The result is the same (match) |
| R2-3: tests "L1226 assert `is counts`" | tests L1230 (L1226 is a parameter row) | VERIFIED | Fixed: the line is L1230 |
| R2-4: no open branch carries an undated 03/06 waiver; marked UNVERIFIED by R2 | orchestrator's check_pipeline.py on main 2e0a15c, 2026-11-25; logs/audit/2026-11-25.md L19: the only open branch is claude/project-thread-f64g3k (journal/ only); BRANCH SKIPPED none | VERIFIED | Fixed: 0 open-branch items, so 0 BRANCH SKIPPED changes |
| R2-5: the L152 assert is a prefix that ends in "person;" | tests L152 | VERIFIED | - |
| R2-6: `.match` on group 0 always fails (group 0 starts with `Waived:`), so it would block 024 and 085 | check_pipeline.py L549, L626; tests L134-135 | VERIFIED | This is mutation M-f |
| R2-7: 100's R2 suggested the `_person_dated` helper, and 100 shipped without it | work/100/02-improvements.md L17; work/100/03-handoff.md L43; check_pipeline.py L637-639, L650-653 | VERIFIED | - |
| R2-8: the L12-13 docstring says R3 and I3 are never skipped by FAST | check_pipeline.py L12-13 | VERIFIED | - |
| R2-9: test L1287 (research-only branch waiver) asserts "can be waived only by the person" | tests L1274-1288 | VERIFIED | R3 addition: the new message keeps this substring, so L1287 is unchanged |

**Totals:** 33 rows checked → **28 VERIFIED as-is**, **5 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None. Five rows are kept with corrections: R1-19 and R2-4 (UNVERIFIED points now sourced), R1 test rows (extended from 5 to 11), and R2-2 and R2-3 (wrong detail and wrong line number; the results stand).

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | scripts/check_pipeline.py: add `_person_dated(text)`. It returns `bool(m and PERSON_DATED.match(m.group(2)))` with `m = WAIVED_LINE.search(text)`. Docstring: the first Waived line's text after the step numbers starts with `(person, YYYY-MM-DD:` (anchored, RI-012; re.match, not prefixmatch, RI-008). `person` is case-sensitive (fails safe), the date is not validated, and only the first Waived line is read. In `_build_waived`, use `return WAIVE_BUILD <= set(steps) and _person_dated(text)`. In `_person_waived_before_i2`, use `if (_person_dated(req_text) and pre and ...)`. Behaviour does not change. Update the comment at L543-547: PERSON_DATED is used only through `_person_dated` (by 093, 100 and from 105 classify). | request.md text | bool | Unchanged and green: test_build_waiver_needs_person_date_and_all_three (11 cases, `is counts`), test_batch_waiver_not_excused_stays_strict N-a, N-c, N-e, N-f, test_batch_waiver_missing_inputs_strict N-g to N-j, test_person_dated_anchor, test_person_waiver_helper_on_item_024, test_research_only_branch_waiver_needs_the_person | Callers: 3 (L639, L653, classify). Real: 024 is True before and after; 023 is False before and after |
| 2 | classify (L760-766): use `scope, opened, (waived, waived_line, _) = parse_request(req_text)`, `dated = _person_dated(req_text)` and `blocked = [s for s in waived if s in PERSON_ONLY and not dated]`. Message: `f"{scope}: {' '.join(blocked)} can be waived only by the person, as (person, <date>: <why>){extra}"`. Module docstring L16-18: "03 (fact check) and 06 (verification) can be waived only by the person, in the documented form: the line's text after the step numbers must start with `(person, YYYY-MM-DD:` (items 031, 105); otherwise the item is SKIPPED. This is a format check, not proof of who wrote it. `person` is case-sensitive (fails safe); the date is not validated; only the first Waived line is read." parse_request is unchanged (3-tuple kept). | request.md | status, detail | Step 3 tests; Self-check rows 1-11 | Real PERSON_ONLY waivers: 1 of 1 dated (024), so 1 passes before and after; 0 undated. Open-branch items: 0 (only branch f64g3k, journal/ only, logs/audit/2026-11-25.md L19). Real classify results changed: 0 of 2 Waived items |
| 3 | tests/test_pipeline_check.py. (a) New `test_person_only_waiver_needs_dated_form`, parametrized, 11 rows. It calls `_cp().classify(d, dt.date(2026, 11, 25))` on a tmp item `998` with request `Scope: FULL\nDate: 2026-11-25\nWaived: <row>\n` and empty step files. It asserts the exact (status, detail). Setup A has files 01 02 04 05, setup B has 01 02 03 04 05, setup C has 01 02 04 05, setup D has 01 03 04 05. Negatives give SKIPPED with `FULL: <steps> can be waived only by the person, as (person, <date>: <why>); Waived: <row>`: A `03 06 (person)`, A `03 06 (person: x)`, A `03 06 (person: x "(person, 2026-11-19: ok)")`, A `03 06 (person) x (person, 2026-11-13: ok)`, B `06 (Person, 2026-11-20: x)`, B `06 (person: x)`, C `03 (person: x)`. Positives give in progress: A `03 06 (person, 2026-11-20: ok)` (next 07), B `06 (person, 2026-11-20: ok)` (next 07), C `03 (person, 2026-11-20: ok)` (next 06), D `02 (A1, 2026-11-01: x)` (next 06). (b) Update L151 to `"107: SKIPPED (FULL: 03 06 can be waived only by the person, as (person, <date>: <why>); Waived: 03 06 (A1, 2026-11-01: test))"` and L152 to `"108: SKIPPED (FULL: 06 can be waived only by the person, as (person, <date>: <why>);"`. (c) Flip N-b and N-d to `True`, each with a `# item 105: undated 03 waiver` comment. Add a docstring note. (d) L1287 is unchanged. | fixtures | tests | On the base code, all 7 negative rows fail (each gives in progress) and all 4 positives pass. Flipped N-b and N-d and the updated L151 and L152 also fail on the base code. After steps 1-2, all pass | 11 rows: 7 SKIPPED, 4 in progress (Self-check rows 1-9). 2 flips, 2 asserts updated |
| 4 | Mutations. I2 runs them and I3 re-runs them on a scratch copy, one at a time, restoring each before the next. M-a: classify back to `who != "person"` (keep who): negative rows 1-7 fail. M-b: `PERSON_DATED.search(m.group(2))` in the helper: rows 3 and 4 fail, and so do _build_waived L1224 and L1225. M-c: helper dated check with `re.I`: row 5 fails. M-d: `not (dated or s == "06")`: rows 5 and 6 fail, and rows 1-4 fail on the message. M-e: `not (dated or s == "03")`: row 7 fails, and rows 1-4 fail. M-f: helper `.match(m.group(0))`: positives 8-10, test L140 (085) and _build_waived L1216-1217 fail. M-g: gate outside the filter (`blocked = list(waived) if not dated else []`): positive row 11 and L141 (106) fail. | code | a named failing test per mutation | 05 and 06 list each mutation with its pytest counts and failing test ids. Each must be killed by test_person_only_waiver_needs_dated_form, or by the named test for M-f and M-g as well | 7 mutations |
| 5 | Real-data and regression check (I2, I3). Run `python3 scripts/check_pipeline.py` with the base script and with the head script on the branch, in a full (not shallow) clone, and diff the whole output, including OPEN BRANCHES and BRANCH SKIPPED. Run the full suite, and `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py`. | repo | output diff, pytest line | The diff is IDENTICAL, apart from lines naming item 105 itself (its own step files). Exit codes are equal. The suite is the base count plus 11. py_compile exits 0. In a shallow clone, the "not checked" lines must also be identical (RI-014) | 0 real results change (step 2 count) |
| 6 | PR text only (no edit). Propose to the person that templates/request.md L5 and run-item.md L10 say "03 and 06 only as `(person, <date>: <why>)`". These are RULE_PATHS edits, which need the person's OK (049). | - | PR note | The PR description has the proposal. `git diff` does not touch these two files | – |

Prevention guardrail (BUG): steps 1-4. The anchored dated check is written once (`_person_dated`) and used by all three person-waiver gates. test_person_only_waiver_needs_dated_form has 7 in-text negatives (RI-012), so a return to the who check (M-a), a `.search` (M-b), a case-insensitive match (M-c) or a gate on one step only (M-d, M-e) each fails a named test.

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| request.md (classify L757) | unreadable | `UNREADABLE`, `<path> unreadable` (089, unchanged) |
| first `Waived:` line | no line | waived = [], blocked = [] → normal step rules (unchanged); nothing is excused |
| text after the step numbers (group 2) | empty (`Waived: 03 06`) | `_person_dated` gives False → SKIPPED `... can be waived only by the person, as (person, <date>: <why>)` (today: who "" → SKIPPED, same status) |
| date in the person bracket | missing (`(person)`, `(person: x)`) | SKIPPED (same text). Never accepted on who alone |
| who | other who, `Person`, or quoted later in the text | SKIPPED (same text) |
| second `Waived:` line | ignored | the first line decides (gap j, documented in the docstring) |
| date validity | 2026-13-45 | accepted as a format (known gap, documented). Not used as a value anywhere |

No ticker screen in this item, so screen.TESTS and MISSING_POLICY do not apply.

## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| 1. A `03 06 (person)` | g1 `[0-9 ,]+` = `03 06 `; g2 = `(person)`; PERSON_DATED.match: `\s*` "", `\(` "(", `person`, `\s*`, then `,` is needed but `)` is found | None → dated False; waived [03, 06] both PERSON_ONLY → blocked [03, 06] | SKIPPED `FULL: 03 06 can be waived only by the person, as (person, <date>: <why>); Waived: 03 06 (person)`. Base: who = "person" → in progress (a fail on base) |
| 2. A `03 06 (person: x)` | g2 `(person: x)`; `,` needed, `:` found | None → blocked [03, 06] | SKIPPED; base: who stops at `:` = "person" → in progress |
| 3. A quoted `(person: x "(person, 2026-11-19: ok)")` | `.match` is anchored at g2 start, so it fails at `:`; `.search` (M-b) finds `(person, 2026-11-19:` inside the quote | fixed None; M-b match | SKIPPED; M-b → in progress (killed) |
| 4. A `(person) x (person, 2026-11-13: ok)` | `.match` fails at `)`; who = "person" (stops at `)`); `.search` finds the later form | fixed None; M-a accepted; M-b accepted | SKIPPED; M-a and M-b killed |
| 5. B `06 (Person, 2026-11-20: x)` | `P` ≠ `p` (case-sensitive); base who lower-cased = "person" | fixed None → blocked [06]; files 01-05 → no gap reached | SKIPPED `FULL: 06 can be waived ...; Waived: 06 (Person, 2026-11-20: x)`; base and M-c → in progress next 07 (killed) |
| 6. B `06 (person: x)` / C `03 (person: x)` | blocked = PERSON_ONLY steps waived and not dated | B: [06]; C: [03] | SKIPPED with `06` / `03`. M-d: B → [] → need 01 02 03 04 05 07, have 01-05 → in progress next 07 (killed). M-e: C → [] → need 01 02 04 05 06 07, have 01 02 04 05 → in progress next 06 (killed) |
| 7. Positives A, B, C dated | `\s*\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:` on `(person, 2026-11-20: ok)` | `(` `person` `,` ` ` `2026-11-20` `:` → match → blocked [] | A: need 01 02 04 05 07, have 4, next 07. B: next 07. C: next 06. All in progress; M-f (match on g0 `Waived: ...`, `W` ≠ `(`) → SKIPPED (killed) |
| 8. D `02 (A1, 2026-11-01: x)` | 02 is not in PERSON_ONLY | blocked [] even though dated is False; need 01 03 04 05 06 07, have 01 03 04 05 | in progress next 06. M-g (blocked = waived when not dated) → SKIPPED (killed); L141 also kills it |
| 9. Row count | 7 negative + 4 positive | 7 + 4 = 11; on base, negatives that pass = 0 (each of rows 1-7 is in progress on base) | 11 rows; suite +11 |
| 10. N-b / N-d flip | FULL, 05 06 07 present, Waived 01 02 03 04 undated | fixed: blocked [03] → `990: SKIPPED` in out → True. INCOMPLETE is computed per item at L2266 whatever the status → WAIVE_STRICT is still present, exit 1 | `skipped` False → True for both; N-a, N-c, N-e, N-f are unchanged (N-f dated → match) |
| 11. Monotone (the fix only narrows) | fixed accepts ⇒ base accepts? | match on g2 ⇒ g2 starts `\s*\(\s*person\s*,` ⇒ who regex `[^,:)]+` = `person` + spaces → strip and lower → "person" ⇒ base accepts | holds: no SKIPPED → accepted transition. Real: 024 g2 `(person, 2026-10-31:` matches → unchanged; 023 waives {02} → unchanged; 0 of 2 change |
| 12. Message asserts | L151 full string, L152 prefix, L1287 substring | the new text inserts `, as (person, <date>: <why>)` before `{extra}` | L151 and L152 updated (2); L1287 still holds |

`check_handoff output (run by the orchestrator 2026-11-25 23:34 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 33
totals line: 33 rows -> 28 as-is, 5 fixed, 0 removed
PASS
```
