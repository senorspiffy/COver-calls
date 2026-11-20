# 03 Research hand-off - 086
Status: READY (on condition that the orchestrator's `check_handoff.py 086` run below prints PASS; if it does not, this is BLOCKED (check_handoff not PASS) until fixed)

R3 has no shell (item 072). Every check below was made with Read/Grep on the working tree (branch daily-fixes/2026-11-20, 2026-11-20) and two WebFetches. Counts that need code are marked for I2 to re-derive. Build on top of 081 and 084 (build order 081 -> 084 -> 086). All three change scripts/check_pipeline.py.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| #1 01 F1: `write_log` checks agent, ID, fields and request.md, then stamps `now` as HH:MM. It never reads other step files or log lines | scripts/check_pipeline.py L558-579 | VERIFIED | – |
| #2 01 F2: `late_log_lines` flags only `stated > commit` with seconds dropped, so 10:15 vs 10:15:48 passes | check_pipeline.py L610-612; logs/audit/2026-11-20-083.md L14 | VERIFIED | – |
| #3 01 F3: blame porcelain lists author, author-mail, author-time, author-tz, "similarly for committer". The unit is not stated in the docs | https://code.googlesource.com/git/+/HEAD/Documentation/git-blame.adoc?autodive=0 (fetched: the quote matches, no unit) | VERIFIED | 086 does not use blame (C and D need no git), so the unit does not matter here |
| #4 01 F4: LOG_LINE has minute resolution. Lines Δ minutes apart are < (Δ+1)×60 s apart | L297, L575 (`%H:%M`); bound: start ∈ [S, S+60), end ∈ [E, E+60) | VERIFIED | – |
| #5 01 F5: the pytest summary time is `timing.time() - self._sessionstarttime`, printed `f"{seconds:.2f}s"` under 60 s and `f"{seconds:.2f}s ({dt})"` from 60 s on | https://pytest.org/latest/_modules/_pytest/terminal.html (fetched, quoted) | VERIFIED | – |
| #6 01 F6: I2 runs the suite before 05 and its log line. I3 re-runs after 05 exists, writes 06, then logs | .claude/agents/i3-verifier.md L13, L16-18; i2-builder.md L25; run-item.md L16 (the orchestrator logs R1-I1, while I2 and I3 log themselves) | VERIFIED | – |
| #7 01 F7: "t05 + t06 ≥ (Δ+1)×60 s is arithmetically impossible" over the last round | derived; F5 `.2f` rounding | fixed | Three corrections. (a) It holds only under the run-item order and with one clock for log stamps and pytest (02 AGAINST 2). (b) Printed values are rounded to 0.01 s, so the real time is ≥ p − 0.005. The sound trigger is Σp − 0.005·k ≥ (Δ+1)×60, where k is the number of summed values. (c) The window is the whole item (start line before the first I2 line -> last I3 line), not the last round (see #16). Map step 1 |
| #8 01 F8: 083 05 `48.51s` (L12), 06 `47.57s` (L9); 48.51 + 47.57 = 96.08 ≥ 60; I1 and I3 both 10:15 | work/083/05 L12, 06 L9; logs/implementation/2026-11-20.md L18-20 | VERIFIED | Re-added: 48.51 + 47.57 = 96.08 |
| #9 01 F9: rule B is not a proof (one 47 s run fits in hh:mm:00-hh:mm:59) | F4 | VERIFIED | – |
| #10 01 F10: 35 FULL items with log lines (045-056, 058-079, 083); 057 is RESEARCH ONLY; "080-086 have no log lines yet" | grep `^Scope:` work/0[4-8]?/request.md; log grep | fixed | 35 and 057 are correct. Since R1 wrote, the research log holds R lines for 080, 081, 082, 084, 085 and 086 (logs/research/2026-11-20.md L6-18). None of them has an I line, so the 35 stands. If 081 and 084 are built before 086, they have I2/I3 lines and the count is 37 (map step 6) |
| #11 01 F11: the known batches among the 35 are 048 (LOG_TIME_EXCEPT) and 083 | recurring-issues.md L129-130; L239 | VERIFIED | – |
| #12 01 F12: Rule A (3+ lines of one item in one minute) flags 12 of 35 (047, 048, 050, 051, 052, 054, 055, 056, 058, 060, 061, 083); from 062 on, only 083 | R3 re-read every line of 045-083 in logs/research/*.md and logs/implementation/*.md | VERIFIED | – |
| #13 01 F13: from 062 on, the smallest same-item gap is 1 min, 4 times (062 I3F 23:46->I2 23:47; 063, 067, 068 R1->R2) | same grep | VERIFIED | Today's 080-086 R lines are also all ≥ 1 min apart per item |
| #14 01 F14: I2 and I3 in the same minute in 9 items (048, 050, 052, 054, 055, 056, 058, 059, 083); rule B flags 083 only and misses 048 | log grep; 05/06 grep | VERIFIED | 059's 0.55 s is a partial run (`tests/test_webull_sandbox.py`, 059/05 L14). Its full-suite line has no time (L15) |
| #15 01 F15: rule C flags 1 (083), 0 false positives; 4 not computable (048, 055, 056, 058 print no time) | 048/05 L8, 06 L6; 055/05 L8; 056/05 L6; 058/05 L11 | VERIFIED | Still 1 flagged under the corrected whole-item window (Self-check) |
| #16 01 F15 / 02 AGAINST 2: "only the last round can be checked, because 05/06 are rewritten each round" | work/069/05 `## Test output` at L48, L153, L244 (rounds 1-3 in order); 076/06 `## Tests re-run` at L26 (round 2) and L118 (round 1); 079/06 L17 and `## Round 1 (FAIL, kept for the record)` L106 | WRONG | Files keep earlier rounds, and the order (appended or prepended) differs per item. So "the last round's run" cannot be found reliably. The fix is a whole-item window, which every reported run falls inside (map step 1) |
| #17 01 F16: from 061 on (061, 063-079: 18 items, 26 I2->I3 rounds) the smallest I2->I3 gap is 3 min (069 r2, 58.61 s), the smallest round span is 8 min (069 r2), and the smallest last round is 9 min (066, 47.65 + 46.44 = 94.09 vs 600) | log grep (I2 lines: 2+1+1+1+1+1+1+3+3+1+1+1+1+1+2+2+1+2 = 26); 069/06 L115; 066/05 L35, 06 L28 | VERIFIED | – |
| #18 01 F17: rule (a) ("previous step's line exists") passes 083 (lines in order) | research L3-5, implementation L18-20 | VERIFIED | – |
| #19 01 F18: every past re-log of an earlier step came after an I3 FAIL line (061, 062, 076, 077, 079) or `A1 result: FAIL` (069 r3, 070 r3) | log grep; work/069/07 L22; work/070/07 L20 | VERIFIED | – |
| #20 01 F18: rule D's history count, and 061's second R3 line (11-14 00:06) "would have needed 04 absent" | not replayable from the repo (R1 says UNVERIFIED) | UNSUPPORTED | Removed. The map claims no history count for D. D is write-time only and is tested by fixtures |
| #21 01 F19: D needs no git; C needs no git and so works where LOG TIME prints "not checked (no git)" | L1128-1132 | VERIFIED | – |
| #22 01 F20: a repo-side LOG BATCH flags 083 on main; precedent `LOG_TIME_EXCEPT` "Never add a new item here"; `test_repo_pipeline_has_no_skipped_items` asserts exit 0 | L236-239; tests/test_pipeline_check.py L169-174, L551 | VERIFIED | – |
| #23 01 F21: 076/06 L17 quotes 05's `81.91s`; "take the last summary line in the `## Tests re-run` section" | 076/05 L59, 06 L17; 076/06 two `## Tests re-run` headings (L26, L118) | fixed | The quote is VERIFIED, but it sits in the I2 audit section, not in Tests re-run. "The last line of the section" is ambiguous because the heading repeats (#16). Map: take every summary line in every `## Tests re-run` section, keep the largest, and drop any value equal to a t05 value |
| #24 01 F22: 083 fixture lines as committed; `tests 344/344` is pre-076 form, INCOMPLETE under TESTS_FORMAT_FROM = 76 | research L3-5, implementation L18-20; L225, L281 | VERIFIED | – |
| #25 01 F23: 079 negative fixture "t06 89.70 s, sum 176.89 s" | 079/06 L144 is under `## Round 1 (FAIL, kept for the record)` (L106); the current `## Tests re-run` (L17) has `90.21s` (L23) | WRONG | Last round: 87.19 + 90.21 = 177.40 < 780. Whole-item window (map): 90.93 + 90.21 = 181.14 vs 164 min (Self-check). No flag either way |
| #26 01 M1-M3 mutations | derived | fixed | M1's boundary moves with the rounding margin: Δ0, 30.00 + 30.00 -> none, 30.00 + 30.01 -> flag. Dropping the `+1` needs a Δ1 fixture (45.00 + 45.00 -> none). M3's send-back test must use 076's order (I3 FAIL, then I1, then I2 with 06 present). Map step 5 |
| #27 01 Numbers table (per-item lines, max/min, I2->I3, largest 05/06 run) | log grep; 05/06 grep (e.g. 063 55.09/51.95 are `6 failed, 37 passed` mutation runs, 063/05 L115, 06 L81) | VERIFIED | It gives upper bounds, which is all the "no flag" argument needs |
| #28 01 Counts: "the tightest before 061 is 054 (Δ1, 22.90 s vs 120 s)" | 050: I1 22:21 -> I3 22:22, 22.92 s (050/05 L14) | fixed | 050 (22.92 s) and 054 (22.90 s) are both Δ1. 050 is 0.02 s tighter. Neither is near 120 |
| #29 01 Fit: check_pipeline.py is a RULE_PATH and needs the person's OK | L260 | VERIFIED | – |
| #30 02: RI-010 history (043 presence, 045 format plus not-after-commit, 049 exception) and the GUARDED condition | recurring-issues.md L118-130 | VERIFIED | – |
| #31 02: LOG_TIME_EXCEPT printed with its reason on the LOG TIME line; LEGACY same pattern | L1129-1132; L299-301 | VERIFIED | – |
| #32 02: 049/02 Holes: re-committing a line moves its blame | work/049/02-improvements.md L21 | VERIFIED | – |
| #33 02: no past write-time order check exists | write_log L558-579 | VERIFIED | – |
| #34 02: run-item L8 (R3 writes 07 for RESEARCH ONLY), L10 (FAST may skip R2/I1), L14 (send back on BLOCKED / NOT A FIT / FAIL), L16 (one step at a time; refusal goes back to the step) | .claude/commands/run-item.md | VERIFIED | L16 covers only R1-I1, and I2/I3 log themselves (#6) |
| #35 02: research log L10-13 has four lines from four items at 23:27 | logs/research/2026-11-20.md L10-13 (085, 080, 082, 084) | VERIFIED | – |
| #36 02 FOR 1: D refuses R1 in a batch at the end (02-06 exist), which catches 083 and untimed batches (048, 055, 058) | by construction; write_log | VERIFIED | – |
| #37 02 FOR 2: separate pinned `LOG_BATCH_EXCEPT = {"083"}` printed with its reason, fixtures (a) ID 999 copy, (b) real repo with the dict emptied, (c) real repo as is | precedent L239, test L551 | VERIFIED | Note for I1: 084 adds RULE NOT SEEN for format-rule cutoffs (084/03 L52). LOG BATCH starts at LOG_CHECK_FROM and is not put under 084's gate, so 083 is handled by the named exception only |
| #38 02 FOR 3: for items ≥ 076, t05 can come from the I2 log line; `_TAIL` parses `(0:01:01)` | L225, L234, L281 | VERIFIED | – |
| #39 02 FOR 3 / Holes: "t06 is the last summary line in 06's `## Tests re-run` section" | #16, #23 | fixed | Every `## Tests re-run` section, largest value, copies of t05 dropped |
| #40 02 AGAINST 1: D's exception applies "when the item's latest step line is a send-back verdict ... or 07's last `A1 result:` is FAIL" | 076: I3 FAIL 00:17, I1 00:20, I2 00:25 while 06 (round 1, 076/06 L98-176) exists; 069 r3: A1 FAIL (07 L22), I1 00:12, I2 00:20 with 06 present | WRONG | With that wording, 076's and 069's round-2/3 `--log I2` would be refused, because the latest line is I1 and 06 exists. Fix: D does not apply once the item has any send-back verdict line (R3 BLOCKED, I1 NOT A FIT, I3 FAIL, matched by LOG_FORMAT fullmatch) or any `A1 result: FAIL` line in 07. Known gap: D is off for the rest of such an item, and C covers its I rounds |
| #41 02 AGAINST 1: 07 never counts as a later step file (RESEARCH ONLY R3, and I3 writes 07 before its `--log`) | run-item L8; i3-verifier L16-18 | VERIFIED | – |
| #42 02 AGAINST 2: C's proof rests on the run-item order. With D alone the bound is > t06 only, and 083's 47.57 < 60 would not flag | run-item L16; 083/06 L9 | VERIFIED | – |
| #43 02 AGAINST 3: three closed lists; suite ~90 s | L239, L299, L21 of check_handoff.py; 079/05 L51 (87.19 s), L203 (90.93 s) | VERIFIED | – |
| #44 02 Languages: N/A (only repo-internal facts plus the sourced pytest format) | – | VERIFIED | – |

**Totals:** 44 rows checked → **34 VERIFIED as-is**, **9 fixed**, **1 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
- #20: rule D's history count, and the 061 second-R3 "04 absent at 00:06" case. These cannot be replayed from the repo. The map makes no history claim for D.

## Implementation map
Guardrail chosen (BUG, step 3): R1's pair, corrected. **C** `LOG BATCH:` in check_pipeline (history, proof-based, no git) plus **D** in `--log` (write time). Rules A, B and (a) are not built (#12, #14, #18).

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | scripts/check_pipeline.py: new `batch_log_items()` (rule C). For each item with ID ≥ LOG_CHECK_FROM that has an I2 line and a later I3 line: **start** = the item's latest log line (any agent, by file date + HH:MM, file order for ties) before its first I2 line; **end** = its last I3 line; Δ = whole minutes end − start. **t05** = the largest time among the item's I2 log lines (items ≥ TESTS_FORMAT_FROM) and every pytest summary line with a time inside every `## Test output` section of 05. **t06** = the largest time among summary lines in every `## Tests re-run` section of 06, excluding any value equal to a t05 candidate (copy guard, #23). Times are parsed with `_STATS`/`_TAIL`, including `(0:01:01)` and ` seconds`. k = the number of known values (1 or 2). **Flag when Σ − 0.005·k ≥ (Δ+1)×60.** Line: `LOG BATCH: <IDs or none>` + ` (not checked: 083: <reason>)` + `; not computable: <IDs> (<reason>)`. Flagged IDs add to exit 1, like LOG TIME. The docstring and output say "impossible under run-item order (L14, L16)", not "impossible" | logs/research/*.md, logs/implementation/*.md, work/<ID>/05, 06 | `LOG BATCH:` line; exit code | Fixtures in step 4: (a) `LOG BATCH: 999`; 079 negative -> none; boundary pair; Δ1 pair; copy guard; interleaved items -> none | 35 FULL items 045-056, 058-079, 083 (logs 2026-11-05..20, R3 log and 05/06 grep 2026-11-20): flagged 1 (083), not computable ≥ 4 (048, 055, 056, 058; exact set printed by the code), 30 not flagged. Largest ratio Σ/limit after 083 (1.60): 050 and 054 at 0.19, then 066 at 0.157. Not computed by code yet: I2 re-derives it with `python3 scripts/check_pipeline.py` and pastes the line |
| 2 | `LOG_BATCH_EXCEPT = {"083": "six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)"}` with "Never add a new item here", a separate dict (not LOG_TIME_EXCEPT). Excepted items are skipped and named with their reason on the LOG BATCH line, as at L1129-1131 | – | main exits 0; 083 stays visible | `test_log_batch_except_is_pinned`: `set(LOG_BATCH_EXCEPT) == {"083"}`; (c) the real repo prints `083` in the not-checked text | – |
| 3 | `write_log` (rule D), after the existing agent/ID/field/request checks, so their refusal texts stay the same (test L610-614): refuse (exit 2, nothing written) when any later step file of 01-06 exists in work/<ID>/ (later = AGENT order after this agent; 07 and other files never count), **unless** the item has a send-back verdict among its log lines (R3 `BLOCKED`, I1 `NOT A FIT`, I3 `FAIL`, each read from `re.fullmatch(LOG_FORMAT[agent], fields)` group 1, never a substring; RI-012) or an `A1 result: FAIL` line in 07, read the same way the existing A1-result check reads it. Message: `--log refused: work/<ID>/ already has <files> after <agent>'s step; redo those steps after this line (item 086)` | work/<ID>/0[1-6]*.md, logs, 07 | exit 2 or the line | Step 4 tests D1-D6 | 083 batch: R1 refused (02-06 present). Past send-back re-logs: 7 items (061, 062, 069, 070, 076, 077, 079), all exempt under the corrected exception (#19, #40). Existing `--log` tests: 9 `_log(` and 5 `"--log"` calls in tests/test_pipeline_check.py write only request.md, or are refused on format first (L610). 0 change result (grep 2026-11-20) |
| 4 | tests/test_pipeline_check.py: (a) tmp item 999 with 083's six lines (I2 field `2 files changed \| tests 344 passed, 1 skipped in 48.51s`), 05 `## Test output` 48.51s, 06 `## Tests re-run` 47.57s -> `LOG BATCH: 999`, exit 1; (b) real repo, `LOG_BATCH_EXCEPT` monkeypatched `{}` -> `LOG BATCH: 083` (RI-010 condition); (c) real repo -> `LOG BATCH: none` with 083 named; N1 079's real lines and runs -> none; N2 boundary Δ0 30.00+30.00 -> none, 30.00+30.01 -> flag; N3 Δ1 45.00+45.00 -> none; N4 copy guard Δ0, 05 40.00, 06 only 40.00 -> none; N5 untimed all-one-minute item -> listed not computable, not flagged; N6 three items' lines interleaved at one minute, each item spaced -> none; N7 a round-2 06 section above round 1 (076 layout) -> parsed. D1 `--log R1 999` with 02-06 present -> exit 2, names `02 03 04 05 06`; D2 the same with only 01 -> written; D3 076 order (I3 FAIL, I1, then `--log I2` with 06 present) -> written; D4 R3 BLOCKED, then `--log R1` with 03 present -> written; D5 I1 NOT A FIT -> R1 re-log written; D6 07 `A1 result: FAIL` -> I1 re-log written; D7 (RI-012) R3 line `... \| READY (was BLOCKED)` or I3 `PASS \| sent to audit: yes (FAIL fixed)` is **not** a send-back -> refused; D8 07 present alone never refuses | fixtures | pass | `python3 -m pytest -q` | – |
| 5 | Mutations (scratch worktree, never the repo): M1 `≥` -> `>` (N2 flag case fails); M1b drop `+1` (N3 fails); M2 ignore 06 (a fails); M3 drop copy guard (N4 fails); M4 missing time read as 60 s or flag (N5 fails); M5 remove D's later-file check (D1 fails); M6 remove D's send-back exception (D3-D6 fail); M7 verdict by substring (D7 fails); M8 add an item to LOG_BATCH_EXCEPT (pin test fails) | code | each ≥ 1 failed | pasted in 05; I3 re-runs them | – |
| 6 | 05 states by code the count "Done looks like" asks for: items checked (ID ≥ 045, I2 and I3 present), flagged, excepted, not computable, in progress. Expected on 2026-11-20 HEAD: 35 checked, 1 excepted (083), 0 flagged, ≥ 4 not computable. If 081 and 084 are built first: 37 checked, both expected not flagged | check_pipeline output | 05 numbers | I3 re-runs and compares | 35 of 35 measured by R3 (#10, #15); 081/084 depend on build |
| 7 | Rule text: run-item.md L14, "`LOG BATCH:` must not name it", plus D's refusal in the L16 list. A `LOG BATCH` entry in the check_pipeline.py docstring next to LOG TIME (L82-84). check_pipeline.py and .claude/ are RULE_PATHS, so the person's OK is needed in PR review | docs | text | grep for `LOG BATCH` in run-item.md and the docstring | – |
| 8 | 05 guardrail line: `RI-010: guardrail built (086); GUARDED when merged, fixture (b) gives LOG BATCH: 083 on main, and the next items have LOG BATCH: none`. Do not edit logs/recurring-issues.md (item 036). Do not add 083 to LOG_TIME_EXCEPT. D needs no 083 exception (write time only; say so in 05) | – | 05 line | A1 | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| pytest time in 05 `## Test output` / I2 log line (C, t05) | contributes nothing; never 0 s | if t06 is also absent: `not computable: <ID> (no pytest time in 05/06/I2 line)` |
| pytest time in 06 `## Tests re-run` (C, t06) | contributes nothing; k = 1 | same as above when t05 is also absent |
| t06 equal to a t05 value | dropped as a copy; never double-counted | none (k counts only kept values) |
| log line before the first I2 (C, start) | no window | `not computable: <ID> (no line before I2)` |
| I3 line after the I2 (C, end) | item in progress | not checked; counted as "in progress" in step 6 |
| 05/06 file unreadable or non-UTF-8 (C) | never a crash, never a pass by default | `not computable: <ID> (<file> unreadable)` |
| malformed log line (C, D) | ignored for C and D | INCOMPLETE reports it (045) |
| 07 (D exception) | no A1 FAIL exception; log verdicts still count | none |
| work/<ID>/ step files (D) | nothing later, so no refusal | none (request.md missing still refuses, 047) |

## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| C on 083 | Σ − 0.005·k ≥ (Δ+1)×60, Δ = 10:15 − 10:15 = 0, k = 2 | 48.51 + 47.57 = 96.08; 96.08 − 0.01 = 96.07 ≥ 60 | flag (matches fixture a, b) |
| N2 boundary (no flag) | same, Δ0, k2 | 30.00 + 30.00 = 60.00; 60.00 − 0.01 = 59.99 < 60 | none |
| N2 boundary (flag) | same | 30.00 + 30.01 = 60.01; 60.01 − 0.01 = 60.00 ≥ 60 | flag |
| N3 / M1b (+1 dropped) | Δ1: limit (1+1)×60 = 120 | 45.00 + 45.00 − 0.01 = 89.99 < 120 -> none; mutated limit 60: 89.99 ≥ 60 -> flag | test fails under M1b |
| N4 / M3 copy guard | Δ0, t06 = 40.00 = t05 -> dropped, k = 1 | 40.00 − 0.005 = 39.995 < 60 -> none; mutated 80.00 − 0.01 = 79.99 ≥ 60 -> flag | test fails under M3 |
| M2 (06 ignored) on 083 | Δ0, k1 | 48.51 − 0.005 = 48.505 < 60 | flag lost, so (a) fails |
| N1 079 (whole item) | start = I1 23:39 (11-19, latest line before I2 02:02); end = I3 02:22 (11-20); Δ = 21 + 120 + 22 = 163 | t05 = max(90.93 05 L203, I2 lines 90.93/87.19) = 90.93; t06 = 90.21 (L23; L144 is outside Tests re-run); 181.14 − 0.01 = 181.13 < 164×60 = 9840 | none |
| 050 (tightest Δ before 061) | Δ = 22:22 − 22:21 = 1, k1 | 22.92 − 0.005 = 22.915 < 120 | none |
| 066 (tightest from 061 on, 2 values) | I1 23:33 -> I3 23:42, Δ9 | 47.65 + 46.44 = 94.09 − 0.01 = 94.08 < 600 | none |
| 062 (2 rounds, short runs) | I1 23:37 -> last I3 23:49, Δ12 | 26.61 + 25.25 = 51.86 − 0.01 = 51.85 < 780 | none |
| Rounding margin | real ≥ printed − 0.005 (`.2f`); real span < (Δ+1)×60 | flag ⇒ Σreal ≥ Σp − 0.005k ≥ (Δ+1)×60 > span | sound (under run-item order, one clock) |
| D on the 083 batch | `--log R1` with later files 02-06 present, no send-back verdict | 5 later files ≥ 1 | refused (exit 2) |
| D on 076 round 2 | I3 FAIL line exists -> exception | `--log I2` with 06 present | written (02's latest-line wording would refuse it: #40) |
| Feasibility count | 12 + 22 + 1 | 045-056 = 12, 058-079 = 22, 083 = 1 | 35 |
| Rounds from 061 on | I2 lines per item | 2+1+1+1+1+1+1+3+3+1+1+1+1+1+2+2+1+2 = 26 | matches #17 |

Recurring issues checked (step 0): RI-001 (every rule has a stated count: C 1/35 flagged, D on 083 and the 7 send-back items. The not-computable set is a lower bound, and the code prints the exact one). RI-002 (a missing time is never 0 s or a flag; Missing inputs table). RI-004/RI-005 (boundary fixtures checked against the trigger after `.2f` rounding; Self-check). RI-006 (counts for the log come from check_handoff, run by the orchestrator). RI-007 (Scope FULL; RULE_PATHS change needs the person's OK). RI-009 (build on top of 081 and 084; same file). RI-010 (this item; GUARDED condition in step 8). RI-012 (send-back verdicts by LOG_FORMAT fullmatch, D7 negative test). RI-014 (C and D need no git, so clone depth cannot change them). RI-013 not applicable (no realtest change). RI-003, RI-008 and RI-011 are not touched (the new code must pass the existing 3.10 compile test).

`check_handoff output (run by the orchestrator 2026-11-20 23:39 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 44
totals line: 44 rows -> 34 as-is, 9 fixed, 1 removed
PASS
```
