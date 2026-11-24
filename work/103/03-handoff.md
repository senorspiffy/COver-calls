# 03 Research hand-off - 103
Status: READY (documented no-go; valid only once the orchestrator's check_handoff run below prints PASS)
Decision: NO-GO on the broad rule. NO-GO on 02's optional narrow rule too. No code, test, template or agent-file change. request.md L15 allows "a documented no-go"; this file is that record.

Measured count (m103-out.txt, orchestrator run 2026-11-24 ~23:18 UTC, exit 0, R1's script from 01 L26-58, work/076-098 05/06, 46 of 46 files present, none unreadable, every file `open_fence_at_end=False`):
- 05: 60 inside, 23 outside. 06: 62 inside, 7 outside. Total: 152 summary lines, of which 30 sit outside every section LOG BATCH reads (L77). R3 re-added the per-file lines L6-76 and got the same 60 / 23 / 62 / 7.
- If the broad rule had applied to 076-098, it would have flagged 30 lines in 12 files across 8 items (076, 077, 079, 081, 082, 084, 086, 087; L78). 14 of those 30 are correctly quoted (mutants, base-failure checks, audit evidence). That is 17 of 30 if rows 10, 18 and 24 are counted as quoted. They are in 6 files across 4 items.
- 088-098 (22 files): 0 outside. 092-098 (14 files, at or above ROUND_HEADING_FROM = 92): 0 outside. So at the newest shapes the rule would flag nothing, true or false.
- Why it is still a no-go: the request's condition is "flags no correctly-quoted run" (request.md L11), and the measurement finds 14 such lines. Two of them sit directly under template sections where quoted evidence belongs: 087/05 L71 under `## Connectivity check` (templates/build-report.md L4) and 087/06 L112 under `## I2 audit (build vs plan)` (templates/verification.md L7). Both are base-failure evidence, which is correct there. Nothing in either template forbids pasting a run there, so a file that follows the template would go INCOMPLETE. The 0 count for 092-098 shows that recent items avoided the shape. It does not show that the shape can't come back (RI-001: a count, not an assertion).

Recurring issues checked (item 013), open and ESCALATED entries:
- RI-001 (ESCALATED): every count here comes from the orchestrator's run or from R3's Grep/Glob re-runs. No rule is built, so no filter goes unmeasured. The Feasibility column gives the measured hits for the broad rule and for the narrow rule.
- RI-010 (ESCALATED): this item is the gap-(w) near miss. It is closed as a no-go, and the 091/098 heading rules stay as they are. My log line is not typed by hand. I have no shell, so the orchestrator must write it with `--log` (see the end of this file).
- RI-014 (OPEN): no git command is used or proposed, so clone depth plays no part.
GUARDED entries also checked: RI-002 (Missing inputs: an absent or unreadable file prints a reason and never a count); RI-004/005 (Self-check); RI-006 (totals are left to check_handoff); RI-007 (Scope FULL; no code is added); RI-012 (no substring matching is proposed).

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 F1: LOG BATCH reads SUMMARY_LINE only inside sections opened by RUN_HEADING 05 `## Test output\b` / 06 `## Tests re-run\b`; closes at next out-of-fence `#`/`##`; in-fence rows count, marks don't; comments dropped | scripts/check_pipeline.py L492, L1422-1457, L652-669 (Read) | VERIFIED | |
| 01 F2: SUMMARY_LINE regex, `.match` on stripped line | check_pipeline.py L496, L1437 | VERIFIED | |
| 01 F3: 091/098 rules check heading text only; `## Round 2 (2026-11-21, I2)` matches neither | L493, L495 (STRAY needs `test output`/`tests re-run` after optional `round N `; ROUND_BUILD needs `build`), L1122-1153 | VERIFIED | |
| 01 F4: cutoffs 92 and 99, each with a `_rule_seen` gate | L447, L454, L1131, L1146 | VERIFIED | |
| 01 F5: 076/05 headings L1, L6, L85, L86, L121, L147, L205, L208; L6-84 in unread Round 2 build | Grep `^#{1,6} ` on work/076/05-build-report.md (R3 re-run) | VERIFIED | |
| 01 F6: 345 summary-like lines in 78 files (098) | work/098/01-research.md L59; work/098/03-handoff.md L43 | VERIFIED | |
| 01 F7: 194 lines over 46 files; 076/05 14, 076/06 18, 084/05 15, 084/06 18 | R3 re-ran R1's Grep pattern over work/076-098/0[56]-*.md: "Found 194 total occurrences across 46 files", same per-file counts | VERIFIED | |
| 01 F8: no 05/06 at 099 or later | Glob work/{099..105}/0[56]-*.md: no files (R3, 2026-11-24) | VERIFIED | |
| 01 F9: 098 dropped the broad rule for lack of a measurement | work/098/04-build-plan.md L75, L85 | VERIFIED | |
| 01 measurement is read-only: stdlib imports only, main only under `__main__` | check_pipeline.py L410-416, L2387 | VERIFIED | |
| 01 OQ1: 098/02 counted 39 `Round N` headings in 25 files | work/098/02-improvements.md L51 (hand listing there; not used in the decision) | VERIFIED | |
| 02: totals 05 in 60 / out 23, 06 in 62 / out 7, 30 OUT | m103-out.txt L77; R3 summed per-file lines L6-76 | VERIFIED | |
| 02: 8 items with an outside line, all below 092; 088-098 outside=0 | m103-out.txt L78, L55-76 | VERIFIED | |
| 02 table rows 1-5: 076/05 L29, L36, L42, L46 (Q, baseline + mutants m1/m8/m9), L59 (R, full suite) | Read work/076/05-build-report.md L26-60 | VERIFIED | |
| 02 table rows 6, 9, 16: line numbers "-" (not looked up) | Grep work/077,079,082/06 | VERIFIED | Fixed: 077/06 L118, 079/06 L144, 082/06 L187 (row text matches m103-out.txt L9, L16, L29) |
| 02 rows 7-8, 10-11, 24-25: 079/05 L51/L57, 081/05 L327/L336, 086/05 L327/L332 | Grep on those files (R3) | VERIFIED | |
| 02 rows 12-15: 082/05 L444/L448/L452 under `### Mutation probes` (Q), L469 under `### Tests re-run (output)` (R) | Read work/082/05-build-report.md L438-470 | VERIFIED | |
| 02 rows 17-20: 084/05 L220/L229 (R) under `## Round 2 test output`, L264/L267 (Q, M6/M7) under `## Round 2 mutations` | Read work/084/05-build-report.md L212-269 | VERIFIED | |
| 02 rows 21-23: 084/06 L144/L146 I3 mutant evidence (Q), L154 I3 round-1 suite (R) | Read work/084/06-verification.md L136-156 | VERIFIED | |
| 02 rows 26-29: 087/05 L71 Connectivity base-failure (Q), L222 base-failure r2 (Q), L247 suite (R), L258 test_agent_tools run (R) | Read work/087/05-build-report.md L62-73, L214-261 | VERIFIED | |
| 02 row 30: 087/06 L112 base-failure evidence under `## I2 audit` (Q) | Read work/087/06-verification.md L104-114 | VERIFIED | |
| 02 tally: R 16 (12 in 05 + 4 in 06), Q 14 (11 + 3); borderline gives R 13 / Q 17 | R3 recount of the 02 table: 12+4=16, 11+3=14, 16+14=30=23+7; 16-3=13, 14+3=17 | VERIFIED | |
| 02: Q lines in 6 files across 4 items | 076/05, 082/05, 084/05, 084/06, 087/05, 087/06; items 076, 082, 084, 087 | VERIFIED | |
| 02: the 15 R lines match STRAY_RUN_HEADING and row 5 matches ROUND_BUILD_HEADING; "UNVERIFIED until a run" | stray_run_headings L1460-1472 + _section_flags L1443-1457 | VERIFIED | Fixed (new source, derivation): a heading row is returned when it is "out", not inside, matches the pattern and is not the opener. Each R line is OUT with no `#`/`##` row between it and its nearest heading (otherwise section= would change), so that heading row has the same False flag. Each nearest heading matches: `### Test output (...)`, `### Tests re-run (output)`, `## Round 2 test output (pasted)` (STRAY, re.I) and `## Round 2 build` (ROUND_BUILD); none matches RUN_HEADING with re.match. Not executed, and the no-go does not depend on it. |
| 02: 11 different section headings across the 30 OUT lines | m103-out.txt L80-90 (11 rows) | VERIFIED | |
| 02 AGAINST 2: "088-098 have outside=0 since 091 took effect" | m103-out.txt L55-76; ROUND_HEADING_FROM = 92 (L447) | VERIFIED | Fixed: 088-098 (22 files) have 0 outside. Only 092-098 (14 files) are under the 091 rule; 088-091 are below it and also have 0. |
| 02 AGAINST 1: "Every I2 report with a mutation table would have the same shape (082/05 L438-452, 084/05 L234-267, 087/05 L226-233) ... as a matter of routine" | Read work/087/05-build-report.md L229-233; SUMMARY_LINE `.match` on the stripped line | WRONG | Fixed: mutation tables are not flagged. 087/05 L229-233 rows start with `\|`, so SUMMARY_LINE does not match. Only bare summary lines outside read sections are flagged (076/05, 082/05, 084/05, plus base-failure/audit lines in 087/05, 087/06, 084/06), and 092-098 have 0. The no-go holds on the count (14 > 0) and the template sections (087/05 L71, 087/06 L112), not on "routine". |
| 02 AGAINST 2: measured benefit at or above 092 = 0 extra true flags | m103-out.txt L63-76 (092-098 all outside=0) | VERIFIED | |
| 02 AGAINST 3: 086/05 has `### R2-3 (iv) rounding search` at L273 | Grep work/086/05-build-report.md | VERIFIED | |
| 02 FOR 1 / Holes: a suite line directly under a `## Round N (...)` wrapper with no run-shaped sub-heading is seen by neither rule; the only such R line in 076-098 is row 5 (098 rule) | m103-out.txt: OUT rows with nearest = section are L1-5, L33-36, L48, L53; of the R lines among them only L5 lacks a run-shaped heading (L33-34 `## Round 2 test output` matches STRAY) | VERIFIED | |
| 02 Recommendation: optional narrow rule (nearest heading is a `#{1,2} round \d+\b` wrapper, no sub-heading) has "only candidates 076/05 rows 1-5", adding 0 catches | m103-out.txt L1-5, L33-36 (nearest = section, heading `## Round 2 ...`) | WRONG | Fixed: with re.I the predicate matches 9 lines: rows 1-5 (076/05) and 17-20 (084/05). 6 of them are correctly quoted (rows 1-4 baseline/mutants, rows 19-20 M6/M7) and 3 are R (5, 17, 18). So the narrow rule also fails request.md L11 and is NO-GO. Case-sensitive (`round`), it matches 0 lines, since every heading says `Round`. |
| 02 Holes: 087/06 archives round 1 as `# Round 1` + `## Tests re-run (output)`, which LOG BATCH reads | Grep work/087/06-verification.md headings: L80 `# Round 1 (FAIL, kept as written)`, L145 `## Tests re-run (output)` | VERIFIED | |
| 02 Recommendation: NO-GO on the broad rule because the count of correctly quoted lines is 14 (request L11) | request.md L11, L15; m103-out.txt; table above | VERIFIED | |

**Totals:** 33 rows checked → **28 VERIFIED as-is**, **5 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None. Three claims were wrong (corrected above) and one was upgraded from UNVERIFIED, so nothing unverified reaches Implementation:
- 02 AGAINST 1 "every mutation table, routine": corrected (tables are not matched; 092-098 have 0 hits).
- 02's narrow follow-up "only rows 1-5, 0 catches": corrected (9 hits, 6 quoted, so NO-GO).
- 02 "since 091 took effect": the range is corrected.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | None to code, tests, templates or agent files. The broad rule (98 Residual (a)) is recorded as a documented no-go in this file. No `*_FROM` constant is added and no cutoff is taken. | m103-out.txt; request.md L11, L15 | This 03 (Decision and Measured count) | `git diff --stat` for 103's commits lists only work/103/ and logs/ files; `python3 scripts/check_pipeline.py` shows no new INCOMPLETE line for 076-098 | Broad rule: 30 hits out of 152 summary lines (46 files, work/076-098 05/06, as of 2026-11-24, m103-out.txt L77). 14 of 30 hits are correctly quoted, so it fails request L11. Not built. |
| 2 | None. 02's optional narrow rule (`#{1,2} round \d+\b` wrapper with no sub-heading) is also a no-go. | m103-out.txt L1-5, L33-36 | This 03 (Fact check row on the narrow rule) | Recount: OUT rows where nearest = section and the section matches `#{1,2} round \d+\b` (re.I) | Narrow rule: 9 hits out of 30 OUT lines (same files and dates). 6 of 9 are correctly quoted, so it fails request L11. Not built. |
| 3 | Residual, for A1's daily review (no item opened here). (a) Unseen shape: a bare suite line directly under a `## Round N (...)` wrapper with no run-shaped sub-heading is caught by neither the 091 nor the 098 rule. 076-098 have 0 such lines apart from 076/05 L59, which the 098 rule covers. If an item at 099 or later shows the shape, the better fix is the template sentence (templates/build-report.md L10) plus a heading rule, not a summary-line rule. (b) SUMMARY_LINE never matches `deselected` runs (L459-460, on purpose), for example 084/05 L243. Neither LOG BATCH nor any broad rule sees them. This is noted only. | m103-out.txt; check_pipeline.py L459-466 | none | A1 daily review: R1's script from 01, re-run on items 099 and later, shows an OUT line under a non-run wrapper | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| work/<ID>/05 or 06 file (R1's measurement loop, 01 L35-37) | Prints `<ID>/<step>: absent`. Never counted as 0 inside / 0 outside. (This run: 0 absent of 46.) | `absent` |
| Unreadable 05/06 (`cp._read`, 01 L38-40) | Prints `<ID>/<step>: <why>`. No count. (This run: 0.) | `_read` reason, e.g. `<path> unreadable (not UTF-8 at byte <n>)` |
| Fence open at the end of the file (`_md_lines` open_end) | Printed per file. The in/out split for that file would be suspect. (This run: all 46 False.) | `open_fence_at_end=True` |
| R/Q class of an OUT line (hand call, 01 (e)) | No line is left unclassed. Rows 10, 18 and 24 are borderline and are shown both ways (R 16/13, Q 14/17). | Borderline note in Measured count |
| 05/06 for items ≥ 099 | Not measurable (none exist). The effect at a new cutoff is n/a; it is not taken to be 0. | n/a: no files at ≥ 099 (Glob, 2026-11-24) |

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Request L11 build condition (broad) | build iff Q flagged = 0 | Q = 14 (or 17); 14 > 0 | NO-GO, matches Decision |
| Request L11 build condition (narrow) | build iff Q flagged = 0 among nearest=section, section ~ `#{1,2} round \d+\b` (re.I) | rows 1-5 + 17-20 = 5 + 4 = 9 hits; Q = rows 1-4, 19, 20 = 6; R = 5, 17, 18 = 3; 6 + 3 = 9; 6 > 0 | NO-GO, matches step 2 |
| Measured totals | sum of per-file inside/outside = TOTAL | 05 in: 8+2+9+2+4+2+4+1+3+3+2+2+1+2+1+3+1+1+2+1+3+1+2 = 60; 05 out: 5+2+2+4+4+2+4 = 23; 06 in: 15+1+11+1+2+2+4+1+2+2+2+3+1+1+1+2+1+1+2+1+4+1+1 = 62; 06 out: 1+1+1+3+1 = 7 | Matches L77 |
| Summary lines measured | inside + outside | 60 + 62 + 23 + 7 = 152; 23 + 7 = 30 | Matches step 1 Feasibility |
| Files with ≥1 OUT | count per-file outside > 0 | 05: 076, 079, 081, 082, 084, 086, 087 = 7; 06: 077, 079, 082, 084, 087 = 5; 7 + 5 = 12 | Matches "12 files" |
| R/Q split | R + Q = OUT | 16 + 14 = 30; borderline 13 + 17 = 30 | Consistent |
| Section-heading counts | m103 L80-90 sum = 30 | 5+5+4+4+3+2+2+2+1+1+1 = 30 | Consistent |
| Cutoff | n/a: no rule built, no `*_FROM` taken | – | – |
| Worked examples | none in the map | – | – |

`check_handoff output (run by the orchestrator 2026-11-24 23:26 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 33
totals line: 33 rows -> 28 as-is, 5 fixed, 0 removed
PASS
```

R3 log line: not written. R3 had no shell this run. After check_handoff prints PASS, the orchestrator runs `python3 scripts/check_pipeline.py --log R3 103 "<as-is> verified, <fixed> fixed, <removed> removed | READY"`, taking the three counts from the check_handoff `totals line:` output and not from this file.
