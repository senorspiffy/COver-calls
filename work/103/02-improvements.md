# 02 Improvements - 103
Languages: N/A (no new external claims). This EFFICIENCY item asks only about this repo's own LOG BATCH check and counts lines in this repo's own files. The fix would add or change no fee, rule or market fact.

Numbers are from the orchestrator measurement 2026-11-24, m103-out.txt (R1's script from 01, run on the branch head at about 23:18 UTC, exit 0). Line numbers (Lnn) are file lines, which I found with Grep/Read of each file and matched to the printed row text.

## What past logs say
- RI-001: a rule or window was assumed to have candidates but was never computed. 098 dropped this broad rule because no measurement existed [work/098/04-build-plan.md L75, L85]. That measurement now exists, so RI-001 no longer blocks the decision.
- RI-010 (gap w) is the reason the request was opened [work/103/request.md L13]. Item 091 (`STRAY_RUN_HEADING`, from 92) and item 098 (`ROUND_BUILD_HEADING`, from 99) are the heading rules that already exist [scripts/check_pipeline.py L447, L454, L493, L495].
- The request's decision rule: build only if the rule flags no correctly quoted run at or above the cutoff [work/103/request.md L11].

## Measured totals (m103-out.txt L77-90)
- 05: inside=60, outside=23. 06: inside=62, outside=7. That gives 30 OUT lines in total.
- Items with at least 1 outside line: 076, 077, 079, 081, 082, 084, 086, 087. All are below 092. Every file from 088 to 098 has outside=0 (m103-out.txt L55-76).

## Item (e): classification of all 30 OUT lines
R (real unread run) = a suite or test run that I2 or I3 made for this item, sitting under a wrapper heading that LOG BATCH does not open. Q (correctly quoted) = a mutant result, a base-failure or connectivity check, or audit evidence. These belong outside the run section in a correct file.

| # | File | Line | Printed row (short) | Section / nearest heading | Class | Why |
|---|---|---|---|---|---|---|
| 1 | 076/05 | L29 | 1 failed, 187 passed in 22.02s | ## Round 2 build | Q | mutation baseline in scratch wt2 (L26-28) |
| 2 | 076/05 | L36 | 3 failed, 185 passed in 22.11s | ## Round 2 build | Q | mutant m1 (L32) |
| 3 | 076/05 | L42 | 4 failed, 184 passed in 23.51s | ## Round 2 build | Q | mutant m8 (L37) |
| 4 | 076/05 | L46 | 2 failed, 186 passed in 22.13s | ## Round 2 build | Q | mutant m9 (L43) |
| 5 | 076/05 | L59 | 1 failed, 525 passed, 1 skipped in 81.91s | ## Round 2 build | R | "Full suite, round 2 (repo root)" (L50) |
| 6 | 077/06 | - | 553 passed, 1 skipped in 100.08s | # Round 1 (FAIL, kept for the record) / ### Tests re-run (output) | R | I3 round-1 suite, kept for the record |
| 7 | 079/05 | L51 | 1 failed, 568 passed, 1 skipped in 87.19s | ## Round 2 (I3 FAIL round 1, P1) / ### Test output | R | full suite (L46-48) |
| 8 | 079/05 | L57 | 1 failed, 264 passed in 33.38s | same | R | pipeline-check suites run (L54-56) |
| 9 | 079/06 | - | 568 passed, 1 skipped in 89.70s | ## Round 1 (FAIL, kept...) / ### Tests re-run (output) | R | I3 round-1 suite |
| 10 | 081/05 | L327 | 4 failed, 637 passed, 1 skipped in 84.71s | ## Round 2 (2026-11-21, I2) / ### Test output (round 2, pasted) | R | base run in a scratch copy, used as a comparison run (L321) |
| 11 | 081/05 | L336 | 4 failed, 642 passed, 1 skipped in 86.11s | same | R | build run (L329) |
| 12 | 082/05 | L444 | 1 failed, 304 passed in 33.67s | ## Round 2 (sent back...) / ### Mutation probes | Q | mutant |
| 13 | 082/05 | L448 | 2 failed, 303 passed in 34.68s | same | Q | mutant |
| 14 | 082/05 | L452 | 2 failed, 303 passed in 35.58s | same | Q | mutant |
| 15 | 082/05 | L469 | 1 failed, 672 passed, 1 skipped in 88.54s | same / ### Tests re-run (output) | R | round-2 suite |
| 16 | 082/06 | - | 672 passed, 1 skipped in 88.69s | ## Round 1 (FAIL, kept...) / ### Tests re-run (output) | R | I3 round-1 suite |
| 17 | 084/05 | L220 | 4 failed, 637 passed, 1 skipped in 80.69s | ## Round 2 test output (pasted) | R | full suite, round-2 tree (L212) |
| 18 | 084/05 | L229 | 4 failed, 269 passed in 33.64s | same | R | HEAD-base comparison run in scratch (L222-224) |
| 19 | 084/05 | L264 | 8 failed, 269 passed in 33.54s | ## Round 2 mutations | Q | mutant M6 |
| 20 | 084/05 | L267 | 8 failed, 269 passed in 33.72s | same | Q | mutant M7 |
| 21 | 084/06 | L144 | 247 passed in 32.20s | ## Round 1 (FAIL, kept...) / ### I2 audit | Q | I3's mutant evidence (M6/M7 survived; see 084/05 L253) |
| 22 | 084/06 | L146 | 247 passed in 33.08s | same | Q | same |
| 23 | 084/06 | L154 | 611 passed, 1 skipped in 86.05s | same / ### Tests re-run (output) | R | I3 round-1 suite |
| 24 | 086/05 | L327 | 4 failed, 642 passed, 1 skipped in 87.65s | ## Round 2 (2026-11-21, I2) / ### Test output (round 2, pasted) | R | pre-edit base run (L321) |
| 25 | 086/05 | L332 | 1 failed, 649 passed, 1 skipped in 83.52s | same | R | final run (L329) |
| 26 | 087/05 | L71 | 25 failed, 64 passed in 0.22s | ## Connectivity check | Q | base-failure check of the base parser |
| 27 | 087/05 | L222 | 25 failed, 67 passed in 0.21s | ## Round 2 / ### Base-failure check (round 2) | Q | base-failure check |
| 28 | 087/05 | L247 | 1 failed, 761 passed, 1 skipped in 84.74s | ## Round 2 / ### Test output (round 2, pasted) | R | round-2 suite |
| 29 | 087/05 | L258 | 92 passed in 0.07s | same | R | test_agent_tools.py run ("Other checks") |
| 30 | 087/06 | L112 | 25 failed, 64 passed in 0.21s | ## I2 audit (build vs plan) | Q | I3's base-failure evidence inside the audit |

Tally: R = 16 (12 in 05: rows 5, 7, 8, 10, 11, 15, 17, 18, 24, 25, 28, 29; 4 in 06: rows 6, 9, 16, 23). Q = 14 (11 in 05: rows 1-4, 12-14, 19, 20, 26, 27; 3 in 06: rows 21, 22, 30). 16 + 14 = 30 = 23 + 7.
Borderline: rows 10, 18 and 24 are base or before-edit comparison runs. I put them in R because the same kind of run is counted inside the read sections elsewhere (for example 084/05's round-1 Test output). If they were Q instead, R = 13 and Q = 17. The decision below is the same either way.

Where each real line is covered today. In 15 of the 16 R lines, the nearest heading is `### Test output ...`, `### Tests re-run (output)` or `## Round 2 test output (pasted)`. All of these match `STRAY_RUN_HEADING` = `#{1,6} (?:round \d+ )?(?:test output|tests re-run)\b` (re.I), and none of them matches the `RUN_HEADING` opener [scripts/check_pipeline.py L492-493]. The 16th, row 5, sits directly under `## Round 2 build`, which `ROUND_BUILD_HEADING` matches [L495]. So the heading rules from 092 and 099 already match the heading shape of every R line. I worked this out by matching each pattern against each heading by hand. I did not run `stray_run_headings` itself, so calling it fully covered is UNVERIFIED until a run confirms it.

## 3 ways FOR
1. A broad rule would close a hole the heading rules leave open: a suite line pasted directly under a wrapper with no run-shaped heading, for example `## Round 2 (2026-11-21, I2)` followed by a fence with no `### Test output` sub-heading. Neither 091 nor 098 matches that heading (01 finding 3), so LOG BATCH would skip the line without any warning. Row 5 shows this shape can happen (a suite line directly under a wrapper), and it was caught only because the wrapper happened to say "build".
2. The rule would check what LOG BATCH actually needs, the summary line itself, instead of guessing from heading wording. So it would not depend on I2/I3 choosing heading text that the regex expects. The measurement shows the heading wording varies a lot: 11 different section headings across the 30 OUT lines (m103-out.txt L79-90).
3. It can be built cheaply and safely. It reuses `_section_flags` and `SUMMARY_LINE` unchanged, which are the same objects `_run_seconds` uses (L1435-1437), and it follows the known `*_FROM` + `_rule_seen` gate pattern (01 finding 4). The cutoff could sit above 104, where no 05/06 exists yet (01 finding 8).

## 3 ways AGAINST
1. It fails the request's own condition. Measured, it would flag 14 correctly quoted lines (or 17 if the borderline rows count as quoted) in 6 files across 4 items: 076/05, 082/05, 084/05, 087/05, 084/06 and 087/06 (table above). These are mutant results, base-failure checks and audit evidence, which belong outside the run sections. Every I2 report with a mutation table would have the same shape (082/05 L438-452, 084/05 L234-267, 087/05 L226-233), so a broad rule would make correct files INCOMPLETE as a matter of routine. The request says build only if no correctly quoted run is flagged [request.md L11], so this is a no-go.
2. It adds nothing the data shows is missing. All 16 real unread lines sit under headings that the 091/098 patterns already match (above), and 088-098 have outside=0 since 091 took effect (m103-out.txt L55-76). So the measured benefit at or above 092 is 0 extra true flags, against 14 or more false flags in the shapes seen.
3. Allow-listing to fix the false flags (exempt `### Mutation*`, `Connectivity`, `Base-failure`, `I2 audit`, ...) turns it back into a heading-wording rule, with all of FOR 2's weakness and a longer list to maintain. Each new section name that I2 invents (for example 086/05's `### R2-3 (iv) rounding search`, L273) would need a fixture, a mutation and a cutoff. That costs more than the one uncovered shape it targets (FOR 1), and that shape has 0 instances in the data, so the benefit is UNVERIFIED.

## Recommendation for R3
NO-GO on the broad rule, because the measured count of 14 correctly quoted lines fails request L11. Record the measured counts and the table in 03 as the "documented no-go" that request.md L15 allows. Optional narrow follow-up, not needed on this evidence: flag a SUMMARY_LINE outside every read section only when its nearest heading is itself a `#{1,2} round \d+\b` wrapper with no sub-heading in between (the FOR 1 hole). In this data its only candidates are 076/05 rows 1-5, all already covered by the 098 heading rule from 99, so it would add 0 catches today. If R3 wants it anyway, it needs its own re-run of the measurement with that exact predicate (RI-001).

## Findings by language
Random languages this cycle: N/A (no new external claims; repo-internal EFFICIENCY item, so per the R2 exception no search is needed)
| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | N/A | - | - | - |
| Mandarin Chinese | N/A | - | - | - |
| Spanish | N/A | - | - | - |
| Japanese | N/A | - | - | - |
| N/A | N/A | - | - | - |
| N/A | N/A | - | - | - |
| N/A | N/A | - | - | - |

## Holes to watch out for (summary)
- Uncovered shape: a suite line directly under a `## Round N (...)` wrapper with no `Test output`/`Tests re-run`/`round N build` heading. Neither the 091 nor the 098 rule sees it. There are 0 instances in 076-098 apart from row 5, which the 098 rule covers.
- Coverage by 091/098 was checked by matching heading text to the regex by hand, not by running `stray_run_headings` over 076-087. That is UNVERIFIED until the orchestrator runs it (those items are below the cutoffs, so the live check never looks at them).
- The 06 "Round 1 kept for the record" runs sit under `### Tests re-run (output)`, a shape that `STRAY_RUN_HEADING` matches. 087/06 instead used `# Round 1` + `## Tests re-run`, which LOG BATCH reads. Item 103 does not decide which archive shape is right, but R3 should not build anything that pushes one shape over the other.
- Row 6 (077/06) and rows 9 and 16 (079/06, 082/06): file line numbers were not looked up. Their class comes from the printed section/nearest heading in m103-out.txt L9, L16, L29.
Log fields: 3 for / 3 against | languages: N/A
