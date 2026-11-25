# 03 Research hand-off - 100
Status: READY

Recurring issues checked (logs/recurring-issues.md, read first): the open and ESCALATED entries RI-001 (ESCALATED), RI-010 (ESCALATED) and RI-014 (OPEN). Also the GUARDED entries RI-002, RI-004, RI-005, RI-006, RI-007, RI-008 and RI-012. How each was applied:
- RI-001: every rule is counted, not asserted. On HEAD there are 3 RESEARCH ONLY request.md files (001, 023, 057; 001 is LEGACY and skipped at L732). 0 of them waive 04 05 06, so the fix changes 0 real `_build_waived` results. There are 9 fixture cases, of which 2 are True. Counts are in the Feasibility column.
- RI-010: no step duty is moved out of a checked field. Log line: R3 had no shell in this run, so the orchestrator writes it with `check_pipeline.py --log` (see the end of this file).
- RI-014: the fix reads no git and adds no file read. `test_read_census` stays at 2.
- RI-002: an absent, unreadable or empty input gives False (flagged) or the strict reason, never a pass (Missing inputs).
- RI-004/005: Self-check below. It covers the N-g byte index and every fixture against the anchored rule.
- RI-006: totals are left to check_handoff.
- RI-007: the fix only narrows what counts as a person build waiver. No line goes from False to True (Self-check row 9).
- RI-008: `re.match`, not `prefixmatch`. Step 5 runs `py_compile` on 3.11.
- RI-012: the anchored `.match` on group 2, plus in-text negatives and a mutation back to `.search`.
- RI-003, RI-009, RI-011 and RI-013 do not apply: no calendar, branch diff, merge base or realtest output is involved.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| R1-1: `WAIVE_BUILD_BY_PERSON` is unanchored; `_build_waived` = subset and who == person and `.search(waived_line)` on the whole first Waived line | scripts/check_pipeline.py L536-537, L624-628 | VERIFIED | - |
| R1-2: who = `re.match(r"\s*\(\s*([^,:)]+)", group 2)`, stripped and lower-cased; `(person: x ...)` gives "person" | check_pipeline.py L612-621 | VERIFIED | - |
| R1-3: the F1 line meets all three conditions; the who check guards only against a different first who (062/06 case) | check_pipeline.py L617, L628; work/062/06-verification.md L47-54 | VERIFIED | - |
| R1-4: A1 reproduced True on 1b10d90; 093's R2 FOR1, R3 and I3 found it, and I3 probed it | logs/audit/2026-11-24-093.md L58-62; work/093/02 L51, 03 L42, 06 L109 | VERIFIED | 093's I1 also named it (04 L137), as the request says |
| R1-5: `search` "Scan through *string* looking for the first location..."; prefixmatch/match "checks for a match only at the beginning of the string" | https://docs.python.org/3/library/re.html (3.15.2 page) | VERIFIED | The second quote is in the "search() vs. prefixmatch()" section, not the function entry |
| R1-6: `match` "Soft deprecated since version 3.15"; "code supporting older versions of Python should continue to use `match()`"; the project requires >= 3.10 | https://docs.python.org/3/library/re.html; pyproject.toml L9 | VERIFIED | - |
| R1-7: WAIVED_LINE and PERSON_DATED (from WAIVE_BUILD_BY_PERSON.pattern); the 093 helper uses `.search` then `.match(group 2)` | check_pipeline.py L538-543, L631-645 | VERIFIED | - |
| R1-8: parse_request reads Waived through the same `WAIVED_LINE.search` | check_pipeline.py L616 | VERIFIED | - |
| R1-9: fix = `m = WAIVED_LINE.search(text)` and `bool(m and PERSON_DATED.match(m.group(2)))` in `_build_waived`, plus a docstring change | check_pipeline.py L624-628, L640-642 | VERIFIED | Adopted (step 1) |
| R1-10: under the fix the F1 group 2 is refused; `test_person_dated_anchor` already pins the regex half | check_pipeline.py L543; tests/test_pipeline_check.py L4538-4545 | VERIFIED | - |
| R1-11: the 7 existing cases keep their results under the fix | tests L1215-1226; check_pipeline.py L542 | VERIFIED | Re-derived case by case in Self-check row 3 |
| R1-12: after the fix `who == "person"` is implied, so its deletion is an equivalent mutant; `(Person, ...)` is still refused (case-sensitive) | check_pipeline.py L537, L543, L617, L621 | VERIFIED | If PERSON_DATED matches group 2, who's `[^,:)]+` takes `person` plus spaces up to the `,` → "person". Decision: remove the check (step 1) |
| R1-13: `_build_waived` has one caller (L736); `_research_code` serves HEAD and open branches | check_pipeline.py L736, L1782, L1960; work/062/05-build-report.md L26 | VERIFIED | - |
| R1-14: real request.md `Waived:` lines exist only in 023 (A1, RESEARCH ONLY) and 024 (person, FULL); 062 is FULL with no Waived line | Grep `^Waived:\|^Scope:` work/*/request.md, 2026-11-24 | VERIFIED | Count added: there are 3 RESEARCH ONLY request.md files (001, 023, 057), and 0 of them waive 04-06 |
| R1-15: the fix changes no real `_build_waived` result; 024's 093 result comes from the helper, pinned by `test_person_waiver_helper_on_item_024` | work/023, 024 request.md L3-4; check_pipeline.py L732-736; tests L4557-4563 | VERIFIED | 057 (no Waived line) is False before and after. 001 is LEGACY (L732) |
| R1-16: the excuse is reached only when `_read(request.md, missing_ok=True)` gives why None and text not None | check_pipeline.py L1551-1557 (`_read` at L1553) | VERIFIED | - |
| R1-17: `_read` is strict UTF-8; on a decode error it returns `(None, "<path> unreadable")` and records `not UTF-8 at byte <n>` | check_pipeline.py L593-609 | VERIFIED | - |
| R1-18: "The octet values C0, C1, F5 to FF never appear." | https://www.rfc-editor.org/rfc/rfc3629 | VERIFIED | - |
| R1-19: N-g is `b"\xff"` alone, so it can't tell "never excused" from "nothing to excuse"; "only `test_read_census` catches such a bypass" | tests L4586-4601; logs/audit/2026-11-24-093.md L53-55 | WRONG (part) | First half VERIFIED. Second half WRONG: N-g also asserts the path is in `_UNREAD`, so a bypass of `_read` (raw or replace-decode read in batch_log_items) already fails N-g as well as the census. The only gap is a bypass inside `_read` that still records `_UNREAD` but returns text. An example is `err.object` (UnicodeError.object, "The object the codec was attempting to encode or decode", https://docs.python.org/3/library/exceptions.html) decoded with "replace". It needs no new read call, so the census passes. Step 4 M-F2 uses this |
| R1-20: A1's probe: `_read` on a valid person waiver plus `\xff` gives `(None, "<path> unreadable")` | logs/audit/2026-11-24-093.md L53-54 | VERIFIED | - |
| R1-21: `_waived_item` writes bytes as-is (no header), so REQ_FULL_093 bytes + `\xff` has a valid FULL 01-04 person waiver as its readable part | tests L4500, L4503-4517 | VERIFIED | - |
| R1 Numbers: feasibility, 2 real Waived lines, 0 RESEARCH ONLY with 04-06 waived, 0 results change | Grep above | VERIFIED | The denominator is also given as 3 RESEARCH ONLY files (R1-14) |
| R1 Numbers: 7 cases today (2 True); adding F1 gives 8 (2 True) | tests L1215-1224 | VERIFIED | The map adds one more negative (closed first bracket), so 9 cases, 2 True (Self-check row 4) |
| R1 Numbers: N-g 0xFF at byte index 59 (12 + 20 + 26 + 1), marked UNVERIFIED by R1 | REQ_FULL_093 at tests L4500; R3 recount character by character | VERIFIED | R3 recount: "Scope: FULL\n" 12, "Waived: 01 02 03 04 " 20, "(person, 2026-11-20: test)" 26, "\n" 1 → 59. `err.start` is "The first index of invalid data in object" (exceptions doc), so the detail is `not UTF-8 at byte 59`. The step 3 assert uses it |
| R1 guardrail 1: the anchored fix plus docstring; optional shared helper | R1-9 | VERIFIED | Decision: no shared helper (02 AGAINST 2). The two call sites share WAIVED_LINE and PERSON_DATED. Recorded as accepted |
| R1 guardrail 2: add the F1 line as False to `test_build_waiver_needs_person_date_and_all_three` | tests L1215-1226 | VERIFIED | - |
| R1 guardrail 3: M-a (`.search(waived_line)`) and M-b (`PERSON_DATED.search(group 2)`) fail the F1 case; M-c (date dropped) fails `(person: ok)` | Self-check rows 5-7 | VERIFIED | - |
| R1 guardrail 4: N-g becomes REQ_FULL_093 + `\xff`; mutation "batch_log_items reads request.md with a replace-decode instead of `_read`" makes N-g fail | tests L4586-4601; check_pipeline.py L1553 | WRONG | That mutation also fails today's N-g (`_UNREAD` assert) and `test_read_census` (a new read_bytes call), so it does not show F2's gain. Replaced by M-F2 (in `_read`'s decode-error branch, after recording `_UNREAD`, return the `err.object` replace-decode with why None). By reading: old N-g passes under M-F2 and new N-g fails (step 4) |
| R1 guardrail 5: the check_pipeline output before and after is identical; the 024 helper test stays green | 093 audit L30-32 precedent | VERIFIED | - |
| R2 logs: 093's R2 flagged this hole by reasoning ("may need its own item") | work/093/02-improvements.md L51 | VERIFIED | - |
| R2 logs: templates/request.md documents `Waived: <steps> (<who>, <date>: <why>)` | templates/request.md L5 | VERIFIED | - |
| R2 logs: RI-012 family; near miss before merge, not counted | logs/recurring-issues.md RI-012 (L140); work/100/request.md L14 | VERIFIED | - |
| R2 FOR1: reuse 093's audited anchor; A1 killed M3, M4 and MA | 093 audit L38-44; check_pipeline.py L543, L640-642 | VERIFIED | - |
| R2 FOR2: L736 is the only caller and it runs only for RESEARCH ONLY; 0 of 2 real Waived lines change | check_pipeline.py L736 | VERIFIED | - |
| R2 FOR3: the hardened N-g kills a replace-decode mutation; "today's `b"\xff"` alone ... the same mutation survives N-g" | tests L4598-4600 | WRONG (part) | The first half holds. The second half is WRONG for a replace-decode in batch_log_items: today's N-g `_UNREAD` assert kills it. Only M-F2 (inside `_read`, still recording) survives today's N-g. Corrected in step 4 |
| R2 AGAINST1: removing the who check leaves `(I2, ...)` cases pinned if PERSON_DATED is loosened | tests L1219, L1223 | VERIFIED | Self-check row 8 |
| R2 AGAINST2: a shared helper widens 093's review (re-run M3/M4/MA) | 093 audit L38-44 | VERIFIED | Minimal edit chosen |
| R2 AGAINST3: the anchor is a format gate, not proof of authorship; the docstring must not overclaim; only a line whose first bracket is not the dated person form goes from True to False | check_pipeline.py L617; work/024/request.md L4 | VERIFIED | Precise set: who-lower is "person" and a dated form appears later, but group 2 does not start with the case-sensitive dated form. Examples: `(person: ...`, `(person) ...`, `(Person, <date>: ... "(person, <date>: ...)")`. No line goes from False to True (Self-check row 9) |
| R2 Holes: keep `bool(...)` (the test asserts `is counts`) | tests L1226 | VERIFIED | - |
| R2 Holes: `.match` on group 2, not parse_request's `waived_line` (group 0 starts with `Waived:`) | check_pipeline.py L620 | VERIFIED | - |
| R2 Holes: M-d (subset dropped) fails `Waived: 04 (person, ...)` | tests L1218 | VERIFIED | - |
| R2 Holes: the N-g mutation must reach the excuse: the helper returns [01..04] on the replace-decoded text | check_pipeline.py L631-645 | VERIFIED | By reading under M-F2: the text is REQ_FULL_093 + "�". Line 2's group 2 is `(person, 2026-11-20: test)`, Scope FULL, pre 01-04 all waived, files dropped → list → excused reason. I2/I3 confirm by running it |
| R2 Holes: first line only; `.*` without DOTALL does not cross a newline | check_pipeline.py L542; tests L1221 | VERIFIED | - |

**Totals:** 43 rows checked → **40 VERIFIED as-is**, **3 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None. The three WRONG rows (R1-19, R1 guardrail 4, R2 FOR3) are kept with corrections. All three rest on one wrong idea: that today's N-g cannot kill any bypass. The corrected mutation is M-F2.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | scripts/check_pipeline.py `_build_waived`: change it to `_, _, (steps, _, _) = parse_request(text)`, `m = WAIVED_LINE.search(text)`, `return WAIVE_BUILD <= set(steps) and bool(m and PERSON_DATED.match(m.group(2)))`. Remove `who == "person"`: it is implied by the anchor, and keeping it would be an equivalent mutant (R1 OQ1). No shared helper (OQ2, accepted: both call sites use WAIVED_LINE and PERSON_DATED). Docstring: the first Waived line excuses 04 05 06 only when the text after the step numbers starts with `(person, YYYY-MM-DD:` (PERSON_DATED.match, anchored, RI-012). This is a format check on the documented form, not proof of who wrote it. The anchor implies who = person. Known gaps unchanged: `person` is case-sensitive (fails safe), the date is not validated, and only the first Waived line is read. Comment L538-541: add `_build_waived` (item 100) as a user of the `.match` rule. | request.md text | bool | Steps 2 and 4. Real data, step 5 | RESEARCH ONLY request.md on HEAD: 3 (001, 023, 057). `_build_waived` is called for 2 (001 is LEGACY, L732). True before: 0 of 2. True after: 0 of 2. Changed: 0. Source: Grep `^Scope:\|^Waived:` work/*/request.md, 2026-11-24. When the result is False, the item is flagged with the RESEARCH ONLY text at L737-739 (named on the RESEARCH CODE / SKIPPED lines). Open branches: covered by the step 5 output diff |
| 2 | tests/test_pipeline_check.py `test_build_waiver_needs_person_date_and_all_three`: add `('Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")', False)` (the N-d twin, the F1 line) and `("Waived: 04 05 06 (person) x (person, 2026-11-13: ok)", False)` (first bracket closed undated), each with a `# item 100 (RI-012)` comment. | RES_160 + line | 9 cases | Both new cases fail on the base code (each returns True: who = "person" and `.search` finds the dated form). All 9 pass after step 1 | 9 cases: 2 True, 7 False (Self-check rows 3-4) |
| 3 | `test_batch_waiver_missing_inputs_strict` N-g: the fixture becomes `REQ_FULL_093.encode("utf-8") + b"\xff"`. Keep `== [("990", "no line before I2")]` and the path-in-`_UNREAD` assert. Add `cp._UNREAD[path] == "not UTF-8 at byte 59"`, so the decode fails at the bad byte and not earlier. Docstring: N-g is a valid person waiver plus one bad byte (item 100). | fixture | test | Passes on base and fixed code. Under M-F2 the first assert fails (step 4) | 1 fixture; byte index 59 (Self-check row 10) |
| 4 | Mutations, run by I2 and re-run by I3 on a scratch copy, one at a time and restored. M-a: `_build_waived` back to `who == "person" and bool(WAIVE_BUILD_BY_PERSON.search(waived_line))` → both new step 2 cases fail. M-a2: bare `WAIVE_BUILD_BY_PERSON.search(waived_line)` with no who check → the 2 new cases and the `(I2 ... copied ...)` case fail. M-b: `PERSON_DATED.search(m.group(2))` → both new cases fail. M-c: date optional (`\(\s*person\s*[,:]` in WAIVE_BUILD_BY_PERSON) → `(person: ok)` fails, and so do 093's N-b, N-d, N-j and the anchor test. M-d: subset check dropped → `Waived: 04 (person, ...)` fails. M-F2: in `_read`, decode-error branch, after `_UNREAD[shown] = ...`, `return err.object.decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n"), None` → new N-g fails. Run it also once against the old `b"\xff"` fixture: N-g passes there. That is the F2 evidence. Record any other failures it causes. | code | named failing test per mutation | 05/06 list each mutation with its failing test names and pytest counts. Each must be killed by a named test. M-F2 on the old fixture must show N-g passing | 6 mutations (M-a, M-a2, M-b, M-c, M-d, M-F2) |
| 5 | Real-data and regression check (I2, I3). Run `python3 scripts/check_pipeline.py` on the branch head vs the base script. Run the full suite. Run `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py`. | repo | output diff, pytest line | The `diff` is empty (IDENTICAL). `test_person_waiver_helper_on_item_024`, `test_read_census` and `test_person_dated_anchor` pass. The suite count is the base count + 2 (two new parametrized cases). py_compile exit 0 | 0 real results change (step 1 count) |

Prevention guardrail (BUG): steps 2-4. These are the two in-text negatives on `_build_waived` (RI-012) and M-a/M-a2/M-b, each killed by a named test, so `.search` over the whole line cannot come back. The hardened N-g plus M-F2 pins "unreadable request.md is never excused" by its own test, not only by `_UNREAD` and the census.

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| request.md at the unit's tip (`_research_code`, L734) | None | unchanged: `RESEARCH ONLY check: no request.md at the tip, item 062` |
| first `Waived:` line (step 1, `WAIVED_LINE.search`) | no line | `m` is None → False → flagged with the L737-739 RESEARCH ONLY text; never a pass |
| text after the step numbers (group 2) | empty (`Waived: 04 05 06`) | `PERSON_DATED.match("")` None → False → flagged |
| `(person, YYYY-MM-DD:` at the start of group 2 | no date / other who / quoted later / `Person` | False → flagged (step 2 cases) |
| Scope line | none | parse_request's FULL → `_build_waived` not called; FULL rules apply (strictest) |
| second `Waived:` line | ignored | first line decides (tests L1221); documented gap |
| request.md in batch_log_items (step 3) | unreadable | strict `no line before I2`, path on UNREADABLE with `not UTF-8 at byte <n>`; never excused (N-g, M-F2) |
| request.md in batch_log_items | missing | strict `no line before I2` (N-h, unchanged) |

## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| 1. F1 line, base code | subset ∧ who == "person" ∧ `.search(line)` | {04,05,06} ⊆ {04,05,06}; who: `\(` then `[^,:)]+` = "person" stops at `:`; search finds `(person, 2026-11-19:` in the quote | True (bug, A1-reproduced) |
| 2. F1 line, fixed | subset ∧ `PERSON_DATED.match(g2)` | g1 = `04 05 06 `, g2 = `(person: x "(person, 2026-11-19: ok)")`; `\s*\(\s*person\s*` ok, then `,` needed, `:` found → None | False |
| 3. 7 existing cases, fixed | same | `04 05 06 (person, 2026-11-13: ok)`: g2 starts with the form → True. `02 04 05 06 (person, ...)`: g1 = `02 04 05 06 ` → True. `04 (person, ...)`: {04,05,06} ⊄ {04} → False. `(I2, ...)`: `person` meets `I` → False. `(person: ok)`: `:` not `,` → False. Two-line: first g2 `(A1, 2026-10-31: x)` → False, and {02} ⊄. `(I2 ... copied ...)`: False | 2 True, 5 False (unchanged) |
| 4. New case `(person) x (person, 2026-11-13: ok)` | base: who stops at `)` → "person"; search finds the later form → True. Fixed: g2 `(person) x ...`, `\s*,` meets `)` → None | base True, fixed False | 9 cases: 2 True, 7 False |
| 5. M-a | who ∧ `.search(line)` | F1: True (row 1); `(person) x ...`: True (row 4) | both new cases fail → killed |
| 6. M-b | `PERSON_DATED.search(g2)` | F1 g2 holds `(person, 2026-11-19:` at offset 12 → match; `(person) x (person, ...` → match | both new cases fail → killed |
| 7. M-c / M-d | `\(\s*person\s*[,:]` on `(person: ok)`; subset dropped on `04 (person, 2026-11-13: x)` | `:` accepted → True ≠ False; anchor matches → True ≠ False | killed (`(person: ok)` case; `04` case) |
| 8. who check removed, then PERSON_DATED loosened to `\s*\(` + anything | `(I2, 2026-11-13: person said ok)` | the remaining requirement still needs `person` first; a loosening that drops `person` lets `(I2, ...` match → True ≠ False | the `(I2, ...)` cases still pin who (02 AGAINST 1) |
| 9. Monotone: no False → True | fixed True ⇒ base True? | match(g2) ⇒ who = "person" (row 12 of fact check) and the search on the line finds it, since g2 is a substring of group 0 | holds; the fix only narrows. Real: 0 of 2 called items change |
| 10. N-g byte index | `err.start` = len(REQ_FULL_093 bytes) | 12 + 20 + 26 + 1 = 59 (all ASCII, 1 byte each) | `_UNREAD[path] == "not UTF-8 at byte 59"` |
| 11. N-g under M-F2 | helper on REQ_FULL_093 + "�" | Scope FULL; g2 `(person, 2026-11-20: test)` matches; pre = [01,02,03,04] ⊆ waived; 01-04 dropped by `_waived_item` | excused reason ≠ `"no line before I2"` → new N-g fails; old `b"\xff"` → "�", no Scope/Waived → strict → passes |
| 12. Suite count | base + new parametrized cases | step 2 adds 2 cases; step 3 changes 1 fixture (no new case) | base + 2 |

`check_handoff output (run by the orchestrator 2026-11-24 23:25 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 43
totals line: 43 rows -> 40 as-is, 3 fixed, 0 removed
PASS
```

Note for the orchestrator: R3 had no shell in this run, so it could not run `check_handoff.py` or `check_pipeline.py --log`. Run `python3 scripts/check_handoff.py 100`, paste its output above, and then write the log line with `python3 scripts/check_pipeline.py --log R3 100 "<as-is> verified, <fixed> fixed, <removed> removed | READY"`, taking the counts from the script's totals line.
