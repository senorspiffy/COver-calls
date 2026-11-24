# 03 Research hand-off - 093
Status: READY

Recurring issues checked (logs/recurring-issues.md, read first): RI-001 (ESCALATED), RI-010 (ESCALATED), RI-014 (OPEN), and the GUARDED entries RI-002, RI-003, RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-011, RI-012, RI-013. How each was applied:
- RI-001: the excuse is counted, not asserted: real items 090-098 (9) with any `Waived:` line = 0. Every fixture is traced to the branch it must reach (Self-check rows 6-13).
- RI-010: no non-waived item gets weaker. Only the exact person-waived shape changes. The unbounded first round is written into the reason text and the docstrings.
- RI-014: the excuse reads only work/ files, no git. The `_rule_seen` TIMED_FROM gate is unchanged.
- RI-002: the excused item stays on the LOG BATCH line. An unreadable or absent request.md gives the strict reason.
- RI-004/005: Self-check below.
- RI-006: totals are left to check_handoff.
- RI-007: only the person, with a date.
- RI-008: `re.match` is used, not `prefixmatch` (3.15+).
- RI-012: anchored `.match` plus in-text negatives N-c and N-d.
- RI-003, RI-009, RI-011 and RI-013 do not apply: no calendar, branch, merge-base or realtest path is involved.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| R1-1: run-item allows `Waived: <steps> (<who>, <date>: <why>)`; only the person waives 03/06 | .claude/commands/run-item.md L10 | VERIFIED | - |
| R1-2: 024 has `Waived: 01 02 03 04 (person, 2026-10-31: ...)`; 024 < LOG_CHECK_FROM 45 | work/024/request.md L4; check_pipeline.py L389, L1309 | VERIFIED | - |
| R1-3: log lines owed only for existing step files (`unlogged`) | check_pipeline.py L904-907; tests L4193 | VERIFIED | - |
| R1-4: empty `before` gives `"no line before I2"` and `continue` | check_pipeline.py L1353-1356 | VERIFIED | - |
| R1-5: BATCH_STRICT has the reason; equality test at L937; only gate `_rule_seen(...TIMED_FROM)`; no request.md read | check_pipeline.py L428, L936-943 | VERIFIED | - |
| R1-6: docstring says "no waiver excuses it" | check_pipeline.py L174-175 | VERIFIED | - |
| R1-7: `test_batch_no_line_before_i2_strict_from_090[990]` pins INCOMPLETE; [089] none | tests/test_pipeline_check.py L4184-4200 | VERIFIED | - |
| R1-8: A1 F1 confirmed BUG, near miss, per-round bound keeps running | logs/audit/2026-11-22-090.md L90-101 | VERIFIED | (A1's own test citation L4074-4090 is stale; R1's L4184-4200 is right) |
| R1-9: parse_request reads first `^Waived:` only; who = `[^,:)]+` lower-cased; classify SKIPs non-person 03/06; no date needed | check_pipeline.py L545-554, L669-671 | VERIFIED | - |
| R1-10: `_build_waived` = who == person + `WAIVE_BUILD_BY_PERSON.search`; 062/06 L49 quote shape | check_pipeline.py L475-476, L557-561; work/062/06-verification.md L49 | VERIFIED | - |
| R1-11: `search` "checks for a match anywhere"; match/prefixmatch "only at the beginning"; fullmatch whole string | https://docs.python.org/3/library/re.html | VERIFIED | - |
| R1-12: MULTILINE `^` "matches at the beginning of the string and at the beginning of each line" | https://docs.python.org/3/library/re.html | VERIFIED | - |
| R1-13: `match` "Soft deprecated since version 3.15" for `prefixmatch` (added 3.15); project >= 3.10 | https://docs.python.org/3/library/re.html; pyproject.toml L9 | VERIFIED | - |
| R1-14: pre-05 steps FULL {01-04}, FAST {01,03}; "RESEARCH ONLY has no I2 line unless 04-06 are waived" | check_pipeline.py L373-375, L1312-1314 | WRONG (part) | Corrected: RESEARCH ONLY's REQUIRED has no 05, so it normally has no I2 line whether or not 04-06 are waived (a 062 waiver means code without I1-I3, still no I2 line). Any item with no I2 line is skipped (L1313-1314). FULL/FAST sets VERIFIED. |
| R1-15: per-round loop runs before the `before` check; no prev → `continue`; docstring L1298-1299 | check_pipeline.py L1295-1300, L1323-1341 | VERIFIED | prev and before use the same order rule (L1329-1330 vs L1353), so "first I2 has no prev" is the same as "before is empty" |
| R1-16: `^Waived:` in work/ only in 023, 024, 062/06 | Grep `^Waived:` work/, 2026-11-24 | VERIFIED | Count added: 9 items numbered 090-098 exist (work/09*/request.md), 0 have a Waived line |
| R1 Numbers: steps before I2 per Scope | check_pipeline.py L373-375 | VERIFIED | - |
| R1 Numbers: LOG_CHECK_FROM 45, TIMED_FROM 90 | check_pipeline.py L389, L396 | VERIFIED | - |
| R1 Feasibility: 0 real items >= 090 with a waiver; fix changes no real output | Grep above | VERIFIED | - |
| R1 proposal 3: optional I3-only bound, assuming I3 starts after I2's line | none (R1 marks UNVERIFIED) | UNSUPPORTED | Removed (not built; recorded as gap) |
| R1 proposal 4(a): `(A1, ...)` waiving 03 is also SKIPPED by classify | check_pipeline.py L669-671 | VERIFIED | - |
| R1 proposal 4(d): partial waiver `01 02 04` twin, shape undecided | check_pipeline.py L672-681, L1353 | WRONG (unresolved shape) | Fixed: 03 absent, no log lines, so `before` is empty (really reaches the branch). classify gives SKIPPED (missing 03 before 05), and the strict entry must stay (fixture N-e). |
| R1/R2 mutation: "who check dropped → twin (c) fails" | parse_request L550 vs anchored pattern | WRONG | With the anchored `.match` of `\s*\(\s*person\s*,\s*date\s*:` on the text after the step numbers, `who == "person"` is implied, so dropping it is an equivalent mutant that no fixture can kill. Replaced by M2 (match→062's who+search, killed by N-d) and M3 (bare search, killed by N-c, N-d). |
| R2 FOR1: `(person: x "(person, 2026-11-19: ok)")` gives who = person and `.search` finds the quoted dated form, so `_build_waived` has the same latent hole | check_pipeline.py L550, L561 (regex read by R3: `[^,:)]+` stops at `:` → "person"; search hits `(person, 2026-11-19:`) | VERIFIED | By reading, not run. I3 probes it. The 062 fix is a follow-up item, not 093. |
| R2 FOR2: `excepted` branch already reads request.md existence | check_pipeline.py L1349-1351 | VERIFIED | - |
| R2 AGAINST2: a waived step file whose log line is ordered after I2 empties `before` for a non-waiver reason | check_pipeline.py L1353 (research rows count only if stamp <= first I2's) | VERIFIED | Mitigation adopted: excuse needs every pre-05 step file absent (fixture N-f) |
| R2 AGAINST3: first round unbounded (L1331-1332), whole-item bound not computed (L1354-1356) | check_pipeline.py | VERIFIED | - |
| R2 RI status: RI-010 ESCALATED 5 occ. with "waiver gap → 093" near miss; RI-012, RI-002 GUARDED | logs/recurring-issues.md L119, L140, L25 | VERIFIED | - |
| R2 Holes: "FULL 01 02 04 should not, because 03 exists and is logged, so before is not empty anyway" | check_pipeline.py L1353 | WRONG (part) | Holds only if R3's line is before I2. With 03 absent the branch is reached, and the subset check alone decides (N-e) |

**Totals:** 29 rows checked → **24 VERIFIED as-is**, **4 fixed**, **1 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
1. R1 proposal 3 / R2 FOR3 option: an I3-only bound between the first I2 line and the last I3 line. It rests on an order assumption that is UNSUPPORTED (no test or rule text pins that I3 starts after I2's log line). Not built. It is recorded as a known gap in the docstring (step 4).

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | scripts/check_pipeline.py: add `WAIVED_LINE = re.compile(r"^Waived:\s*([0-9 ,]+)(.*)$", re.M)` and make `parse_request` use it (one source). Add `PERSON_DATED = re.compile(r"\s*\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:")`, used only with `.match` on WAIVED_LINE group 2 (RI-012; `match`, not `prefixmatch`, RI-008). `_build_waived` is left unchanged here (follow-up item for its latent hole, R2 FOR1). | request.md text | constants | Existing parse_request/classify/_build_waived tests stay green. Unit: `PERSON_DATED.match` is True for `(person, 2026-11-20: x)` and False for `(person: x)`, `(I2, 2026-11-20: "(person, 2026-11-19: ok)")` and `(person: x "(person, 2026-11-19: ok)")` | – |
| 2 | Add helper `_person_waived_before_i2(req_text, item_dir)`. It returns the list `pre = [s for s in REQUIRED[scope] if s < "05"]` only when all four hold: (a) a first Waived line exists and `PERSON_DATED.match(group 2)`; (b) `set(pre) <= set(waived)`; (c) `pre` is not empty; (d) no `item_dir / STEPS[s]` exists for s in pre. Otherwise it returns None. Only the first Waived line is read (gap j: a second line is ignored, so the item stays strict). | req_text, item_dir | list or None | Fixtures F1, F2 (pass), N-a to N-f (strict); mutations M2-M7 | Real items 090-098: excused 0 of 9 (none has a Waived line, Grep 2026-11-24); the other 9 of 9 keep the strict reason. Fixtures: 2 of 8 excused (F1 FULL, F2 FAST), 6 of 8 strict. Empty result = the strict reason `no line before I2` → `INCOMPLETE ... (item 090)`, named and counted on the LOG BATCH and INCOMPLETE lines |
| 3 | `batch_log_items` at L1354: when `before` is empty, `text, why = _read(d / "request.md", missing_ok=True)`. If `why is None and text is not None` and the helper returns pre, the reason is `no line before I2 (<pre joined by " "> waived by the person, first I2 round not bounded, item 093)`. Otherwise it stays exactly `"no line before I2"`. An unreadable request.md is also recorded on UNREADABLE by `_read` (exit 1). No ";" inside the reason (LOG BATCH joins entries with "; ", L2064). | rows, request.md | not_computable entry | F1/F2: LOG BATCH contains `not computable: 990: no line before I2 (`. N-g: `_bl(...)["not_computable"] == [("990", "no line before I2")]`. Existing L3160 test (no Waived line) unchanged | – |
| 4 | `incomplete()` code unchanged: the new reason is not in BATCH_STRICT by equality (L937). Docstrings: rewrite L162-165 and L171-175 (person-dated waiver of every pre-05 step with the files absent is excused, listed, first round unbounded; any other waiver strict). Rewrite L1292-1300 (no-prev round of an excused item is not evaluated by anything in LOG BATCH; LOG TIME still applies) and note gap (j) applies to 093 too. | – | text | Unit: `excused_reason not in cp.BATCH_STRICT` and `excused_reason.startswith("no line before I2 (")`. A1 reads the docstring diff | – |
| 5 | tests/test_pipeline_check.py: flip `[990]` of `test_batch_no_line_before_i2_strict_from_090` to `INCOMPLETE: none`. Add a parametrized pass test over `[s for s in cp.REQUIRED if "05" in cp.REQUIRED[s]]` (FULL, FAST; guardrail: a new Scope with an I2 step gets the test automatically). FAST request: `Scope: FAST (person, 2026-11-20)` + `Waived: 01 03 (person, 2026-11-20: test)`. 01-04 are deleted in each fixture. | `_batch_item(..., full=True)` as in L4190-4197 | tests | F1, F2: INCOMPLETE line `INCOMPLETE: none`, and LOG BATCH names 990 with the excused reason. I2 records the exit code the [089] twin gives today and asserts the same | – |
| 6 | Negative fixtures (same shape as L4190-4197, item 990; each asserts the INCOMPLETE line contains `990 (` and `LOG BATCH not computable: no line before I2 (item 090)`): N-a `(A1, 2026-11-20: test)` (also `990: SKIPPED`); N-b `(person: test)`; N-c `(I2, 2026-11-20: copied "(person, 2026-11-19: ok)")` (also SKIPPED); N-d `(person: x "(person, 2026-11-19: ok)")`; N-e `Waived: 01 02 04 (person, 2026-11-20: test)` with 03 absent (also SKIPPED: missing 03 before 05); N-f person-dated `01 02 03 04`, 01-research.md kept, R1 research line at 10:10 after I2 10:00. N-g (unit via `_bl`): request.md written as bytes `b"\xff"` gives exactly `("990", "no line before I2")` | fixtures | tests | Each passes on the fixed code | – |
| 7 | Mutations, run by I2 and re-run by I3 on a scratch copy: M1 helper always None → F1, F2 fail; M2 anchored match → `who == "person" and WAIVE_BUILD_BY_PERSON.search(line)` → N-d fails; M3 bare `WAIVE_BUILD_BY_PERSON.search(line)` → N-c, N-d fail; M4 pattern `\s*\(\s*person\b` (date dropped) → N-b fails; M5 subset check dropped → N-e fails; M6 `pre` from `REQUIRED["FULL"]` always → F2 fails; M7 file-absent check dropped → N-f fails; M8 unreadable request.md treated as "" and excused → N-g fails. The `who` check is not a separate mutation: it is implied by the anchored match (equivalent mutant) | code | named failing test per mutation | 05/06 list each mutation with its failing test name | – |

Prevention guardrail (BUG): steps 5-7. The parametrized-over-REQUIRED pass test plus the strict negatives N-a to N-g, each pinned by a mutation, so neither the false INCOMPLETE nor a loosened excuse can come back. Follow-up for A1 to open: `_build_waived` (062) has the same `(person: x "(person, date: ...)")` hole (R2 FOR1); I3 probes it on 093's branch.

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| work/<ID>/request.md (step 3, `_read(missing_ok=True)`) | missing | strict `no line before I2` → `INCOMPLETE: <ID> (LOG BATCH not computable: no line before I2 (item 090))`; classify reports the item separately |
| request.md unreadable (non-UTF-8, OSError) | `_read` returns why | strict reason, plus the path on the UNREADABLE line (item 089), exit 1; never excused |
| first `Waived:` line (step 2) | none | strict reason |
| `(person, YYYY-MM-DD:` at the first parenthesis | no date / not person / quoted only | strict reason (N-a to N-d) |
| a pre-05 step in the waived set | not waived | strict reason (N-e) |
| second `Waived:` line | ignored (gap j) | strict reason; documented, fails loud |
| Scope line | none | parse_request's FULL (run-item L8 rule, the strictest pre-05 set, not a pass) |
| pre-05 step file | present | strict reason (N-f) |

## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| 1. pre-05 set FULL | `[s for s in REQUIRED["FULL"] if s < "05"]` | "01"…"04" < "05" True; "05","06","07" < "05" False → [01,02,03,04] | matches 01 R1-14 |
| 2. pre-05 set FAST | same on ["01","03","05","06","07"] | → [01,03] | matches F2 waiver `01 03` |
| 3. Scopes in parametrized pass test | `"05" in REQUIRED[s]` | FULL yes, FAST yes, RESEARCH ONLY ["01","02","03","07"] no → 2 cases | 2 = F1, F2 |
| 4. strict gate cutoff | id >= TIMED_FROM (90) | 990 >= 90 strict path; 089 < 90 text only | fixtures use 990; [089] unchanged |
| 5. real-item count | items 090-098 with `^Waived:` | 9 folders, Grep hits only 023, 024, 062/06 → 0 of 9 | excuse changes 0 real outputs |
| 6. F1 trigger | `PERSON_DATED.match(g2)`, g2 = `(person, 2026-11-20: test)` (g1 = `01 02 03 04 `) | `(` `person` `,` ` 2026-11-20` `:` all match; {01..04} ⊆ {01..04}; files deleted | excused → INCOMPLETE none |
| 7. F2 trigger | g2 `(person, 2026-11-20: test)`; waived {01,03} ⊇ {01,03}; FAST_BY_PERSON on `Scope: FAST (person, 2026-11-20)` | all match; classify need = [05,06,07] present | excused |
| 8. N-b | match on `(person: test)` | after `person`, `\s*,` meets `:` → None; who = "person" so classify passes | strict; M4 (`\(\s*person\b`) would match → excused → N-b fails |
| 9. N-c | match on `(I2, 2026-11-20: copied "(person, 2026-11-19: ok)")` | `\(\s*person` meets `I` → None; whole-line search finds `(person, 2026-11-19:` | strict; M3 excuses it → fails |
| 10. N-d | match on `(person: x "(person, 2026-11-19: ok)")` | anchored: fails at `:`. who = `[^,:)]+` → "person"; search finds the quoted form | strict; M2 and M3 both excuse → fail |
| 11. N-e | {01,02,03,04} ⊆ {01,02,04} | 03 missing → False; no 03 file and no log lines → before empty (branch reached) | strict; M5 excuses → fails |
| 12. N-f | files absent for pre | 01-research.md exists → False; R1 10:10 > I2 10:00 so research row not in before (L1353) → branch reached | strict; M7 excuses → fails |
| 13. N-g | `_read` on b"\xff" | UnicodeDecodeError → why set → strict exact string | `("990","no line before I2")`; M8 excuses → fails |
| 14. reason text vs strict set | equality in BATCH_STRICT (L937) | `"no line before I2 (01 02 03 04 waived by the person, first I2 round not bounded, item 093)"` ≠ each of the 3 entries; contains no "; " | not strict; [990] LOG BATCH substring assertion `not computable: 990: no line before I2` still holds |

`check_handoff output (run by the orchestrator 2026-11-24 18:16 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 29
totals line: 29 rows -> 24 as-is, 4 fixed, 1 removed
PASS
```
