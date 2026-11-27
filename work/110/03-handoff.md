# 03 Research hand-off - 110
Status: READY (two documented no-gos plus a text-only docstring/comment correction; READY stands only once the orchestrator's check_handoff run below prints PASS)
Decision: (a) NO-GO. (b) NO-GO. No rule, regex, constant, cutoff or template change. Step 3 corrects two code-text statements that this item's measurement shows to be inexact, and pins the record with one test (same pattern as 103's docstring pointer, logs/audit/2026-11-25-103.md L27-31). request.md L15 allows "rule or no-go with reason"; this file is that record.

Measured count (orchestrator run of R1's script, 01 L36-146, on daily-fixes/2026-11-25 at 4404a28, 2026-11-25 23:28 UTC, exit 0, output 01 L151-270; SELF-TEST ok; no `REGEX NOT SUPERSET` line; no unreadable file and no `open_fence_at_end=True` line printed):
- Files read: 58 (work/076-104, 05 and 06).
- (a) `#{1,2} round N` wrapper headings that are none of opener/091/098: 28 = 26 at <092, 1 at 092-098 (094/05 `## Round 2 changes (file: what changed)`), 1 at >=099 (104/06 L108 `# Round 2 (2026-11-25, I3)`).
- (a) Summary lines directly under such a wrapper with no sub-heading: 4 = 2 SUMMARY_LINE (`A`) + 2 deselected-only (`A-DESEL`), all in 084/05 under `## Round 2 mutations (scratch copy, never the repo)` (L234). R = 0, Q = 4 (M6/M7 mutants: L243, L250, L264, L267). At 092-098: 0. At >=099: 0.
- (b) Deselected-only summary lines in files at >=076: 72 inside read sections (36 in 05, 36 in 06) + 11 outside (6 in 05, 5 in 06) = 83. Over all IDs >= LOG_CHECK_FROM (45): 34 files would gain read values (21 of them at >=076, from the B-IN lines; so 13 at 045-075), 0 files change their max, all six `batch_log_items` keys `same=True`, flagged_ids `[]`, checked 59.
- Why both are no-gos: (a) the only candidates are 4 correctly quoted lines below 092 and none at the newest shapes, so a rule flags only correct files (request L11, 103's test). (b) counting deselected runs changes 0 maxes and 0 LOG BATCH results across 59 checked items; the largest printed deselected run (23.78 s, 095/05 L82) sits 129.19 s under its file's max (152.97 s, L74).

Correction recorded for 02 (R2's own note): 02 AGAINST 3 says "did not happen in 059 items"; it should read "did not happen in the 59 checked items" (`checked: 59`, 01 L269). Item 059 is unrelated.

Recurring issues checked (item 013), open and ESCALATED entries:
- RI-001 (ESCALATED): every count in this file comes from the orchestrator's run (01 L151-270) or my own Grep/Glob re-runs, with dates and commands in the Feasibility column. No rule is built, so no filter goes unmeasured. "Never the per-file max" (01 F15) is stated only as the measured result over 045-104, not as a law.
- RI-014 (OPEN): no git command is used or proposed; step 3's check uses `git diff` only on the item's own commit, depth-independent.
- RI-010 (GUARDED; this item is its 2026-11-25 near miss "`## Round N (...)` wrapper / `deselected` → 110"): closed as two no-gos; 091/098 rules unchanged. I write no log line; the orchestrator runs `--log`.
GUARDED entries also checked: RI-002 (Missing inputs: an unmeasured value is n/a with a reason, never 0, e.g. the 045-075 deselected lines); RI-004/RI-005 (Self-check below, including the exact strings step 3's test asserts); RI-006 (totals left to check_handoff); RI-007 (Scope FULL; step 3 is a code-file text edit that goes through I1-I3); RI-012 (step 3's test uses literal `in` checks on fixed strings it owns, plus one negative); RI-008 (no new syntax); RI-003/009/011/013 n/a (no calendar, branch, diff or realtest change).

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 F1: 103 measured 30 of 152 outside, 0 at 092-098, 14 quoted; broad and narrow rules NO-GO, narrow 9 hits / 6 Q | work/103/03-handoff.md L5-9, L66-67; logs/audit/2026-11-25-103.md L17-25 (Read) | VERIFIED | |
| 01 F2: 103's residual (a) text and its suggested fix (template sentence L10 + heading rule) | work/103/03-handoff.md L68; work/103/02-improvements.md L54, L82 | VERIFIED | |
| 01 F3: narrow rule failed on 076/05 rows 1-4 and 084/05 rows 19-20; heading-wording rule costs more | work/103/03-handoff.md L50; work/103/02-improvements.md L20-23, L38-39, L64 | VERIFIED | |
| 01 F4: `_section_flags` opens at RUN_HEADING, closes at any out `#`/`##` row | scripts/check_pipeline.py L497, L1454-1468 (Read) | VERIFIED | |
| 01 F5: 091/098 rules flag headings only, from 92 and 99, each gated by `_rule_seen` | check_pipeline.py L452, L459, L498, L500, L1133-1164, L1471-1483 | VERIFIED | |
| 01 F6: 104/06 L108 wrapper; round-2 suite under `## Tests re-run (round 2)` L123, suite L136; mutant lines L145-162 start `BASE:`/`M56:`; the only `#{1,2} Round N` heading in 099-104 05/06 | Read work/104/06-verification.md L106-165; Grep `^#{1,2} [Rr]ound \d+` over work/{099..104}/0[56]-*.md → 1 hit (104/06 L108) | VERIFIED | |
| 01 F7: 05/06 exist for 099-104 only, none at 105-109 | Glob work/1[01][0-9]/0[5-7]-*.md → 100-104 only; 099/05, 099/06 in the script output (01 L215-216) | VERIFIED | |
| 01 F8: `deselected` left out of `_STATS_PARTS` on purpose; `--log` refuses it in I2 | check_pipeline.py L464-470, L117-118; tests/test_pipeline_check.py L679 (I2_REFUSE R9 `3 passed, 1 deselected in 0.12s`) | VERIFIED | |
| 01 F9: Σ uses the largest time per file, 06 copies dropped | check_pipeline.py L1571-1588 | VERIFIED | |
| 01 F10: leaving a run out can only lower Σ, so (b) can cause a missed flag but never a false one | check_pipeline.py L1582 (`kept06` drops any 06 value equal to a t05 value to 0.01 s) | WRONG | Fixed: true per file in isolation, not through the copy filter. Today a 06 value equal to a (uncounted) 05 deselected run is kept; with (b) it would be dropped. So leaving deselected runs out can also raise t06 (a 06 copy of a 05 `-k` run counts as I3 time), and counting them can lower Σ (02 AGAINST 3). Measured effect of the difference: none (all `same=True`, 59 items). The same imprecision is in the docstring gap (w) "(only lowers Σ)" L196, corrected by step 3. |
| 01 F11: KNOWN_TYPES order failed, passed, skipped, deselected, xfailed, xpassed, warnings, error, subtests ... | https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py (fetched 2026-11-25) | VERIFIED | |
| 01 F12: `pluralize` changes only error, warnings, test; `deselected` printed unchanged for every N | same URL (`if noun not in ["error", "warnings", "test"]: return count, noun`) | VERIFIED | |
| 01 F13: `pytest_deselected` → `self._add_stats("deselected", items)`; the normal summary prints every known type that has reports | same URL (`_build_normal_summary_stats_line`: `for key in known_types: ... if reports: parts.append(...)`) | VERIFIED | |
| 01 F14: Grep `deselected in \d` over work/*/0[56]-*.md: 308 occurrences in 49 files (053-104), upper bound only | R3 re-ran the Grep count 2026-11-25: "Found 308 total occurrences across 49 files", first 053, last 104 | VERIFIED | |
| 01 F15: a deselected run is never the per-file max: UNVERIFIED until the script runs | 01 L262 `FILES WHOSE MAX CHANGED: 0` (files at IDs 045-104, 4404a28); a file with only deselected runs would show None → value, so 0 also covers that case | UNSUPPORTED | Fixed (new source): measured, not general: over IDs 045-104 at 4404a28 no deselected run is above its file's max. Not a guarantee for future items (RI-001). |
| 01 L34: the script is read-only, stdlib-only, `main()` only under `__main__`, no git in `batch_log_items`/`_run_seconds` | check_pipeline.py L415-421, L2398, L182 ("No git"), L1433-1451, L1486-1594 (no `_git` call) | VERIFIED | |
| 01 L149-270: run on daily-fixes/2026-11-25 at 4404a28, exit 0, SELF-TEST ok, no REGEX NOT SUPERSET line | 01 L149-270 as pasted by the orchestrator (R3 has no shell; not re-run) | VERIFIED | |
| 01 OQ3: SUMMARY_LINE is shared with the I2 per-round bound and the I2 time; I2 fields cannot contain `deselected`, so that path is unchanged if only SUMMARY_LINE changes | check_pipeline.py L1535, L1579, L557 (`LOG_FORMAT["I2"]` uses `_STATS`); tests L679 | VERIFIED | |
| 02 L4: German, Russian, Italian not used in the last full-search cycle (104: French, Korean, Portuguese) | logs/research/2026-11-24.md L39 | VERIFIED | |
| 02 L7: 103 left (a) and (b) as documented residuals, no rule | logs/audit/2026-11-25-103.md L49-52; work/103/03-handoff.md L68 | VERIFIED | |
| 02 L8: RI-001 (counts never computed) no longer blocks: the script counted them | logs/recurring-issues.md L7-9; 01 L149 | VERIFIED | |
| 02 L9: request links RI-010 gap (w); docstring "only lowers Σ" | work/110/request.md L13; check_pipeline.py L194-196 | VERIFIED | |
| 02 L10: 103's A1 mutant run `1 failed, 506 deselected in 0.65s`; full suite 120.27 s | logs/audit/2026-11-25-103.md L38, L45 | VERIFIED | |
| 02 L13: wrapper headings 26 / 1 (094/05) / 1 (104/06) | 01 L153-256 (R3 counted 28 WRAP lines: 26 at 076-091, 094/05, 104/06); Grep work/094/05 headings L170 | VERIFIED | |
| 02 L14: 2 A + 2 A-DESEL lines, all in 084/05 under `## Round 2 mutations`, 0 at 092-098 and >=099 | 01 L183-186, L259-260 | VERIFIED | |
| 02 L15: all 4 are Q (M6/M7 mutants in a scratch copy); the A lines are 103's rows 19-20 | Read work/084/05-build-report.md L234-268 (L235 scratch copy, L237 `== M6`, L244 `== M7`, L243/L250/L264/L267); work/103/02-improvements.md L38-39 | VERIFIED | |
| 02 L16: deselected-only lines 72 in + 11 out = 83 | 01 L261; R3 counted the printed B-IN lines: 36 in 05, 36 in 06 | VERIFIED | |
| 02 L16: "Of the files checked, 34 would gain read values" | 01 script L118-125 (`maxes()` loops from LOG_CHECK_FROM = 45, check_pipeline.py L442) vs B-IN printing from TESTS_FORMAT_FROM = 76 (L443) | WRONG | Fixed: the 34 files span IDs 045-104, not the 58 files of the 72/11 count. 21 are at >=076 (distinct files in the B-IN lines); 13 are at 045-075, whose deselected lines were neither printed nor in the 72. Consistent with Grep: 15 files at 045-075 contain `deselected in \d` (053, 063×2, 066×2, 067×2, 068, 069×2, 071×2, 073×2, 075); 13 ≤ 15. |
| 02 L16: 0 maxes change, all six keys `same=True`, flagged `[]`, checked 59 | 01 L262-269 | VERIFIED | |
| 02 L17: no REGEX NOT SUPERSET, so the comparison is valid | 01 L151-270 (no such line); 01 L277 | VERIFIED | |
| 02 L18: largest printed deselected time 23.78 s (095/05) is not that file's max; margin UNVERIFIED | Grep `in \d+\.\d+s` on work/095/05-build-report.md: L74 `881 passed, 1 skipped in 152.97s`, L82 `37 passed, 396 deselected in 23.78s`, both inside `## Test output (pasted, not summarized)` (L57-109) | UNSUPPORTED | Fixed (new source): 095/05's max is 152.97 s; margin 152.97 − 23.78 = 129.19 s. |
| 02 FOR 1: pytest docs show `3 passed, 1 deselected in 0.12s`, `2 passed, 2 deselected in 0.12s`; `deselected` after `skipped` | https://docs.pytest.org/en/8.3.x/example/markers.html (fetched; 9 final lines with `deselected`, incl. both quoted); 01 F11 | VERIFIED | |
| 02 FOR 1: counting a deselected run "can only raise Σ", "cannot cause a false flag"; "72 in-section runs ... would become visible" | check_pipeline.py L1582; 01 L262 | WRONG | Fixed: it can also lower Σ through the copy filter (02 AGAINST 3, row on 01 F10). The visible set is the 72 lines at >=076 plus the unprinted lines in 13 files at 045-075 (≥ 72 + 13 = 85). Measured: no flag changes either way. |
| 02 FOR 2: an all-`-k` 05 or 06 gives `_run_seconds` no value, the file's term drops, or `not_computable` "no pytest time in 05/06/I2 line"; no item has this shape today | check_pipeline.py L1446-1450, L1583-1585; 01 L262 (MAX CHANGED 0 also rules out None → value) | VERIFIED | |
| 02 FOR 3: (b) is "one inserted `{N} deselected` part in `_STATS_PARTS` order", and the I2 path "sees no new input" | check_pipeline.py L468-471 (`_STATS` built from `_STATS_PARTS`), L476 (I2_TIMED), L501 (SUMMARY_LINE), L557 (`LOG_FORMAT["I2"]`); tests/test_pipeline_check.py L679, L715-721 | WRONG | Fixed: `_STATS_PARTS` feeds `_STATS`, which LOG_FORMAT["I2"], I2_TIMED and SUMMARY_LINE all use. Inserting there would make `--log` accept `deselected` and fail `test_i2_summary_line_refused[R9]`. If (b) is ever built, it needs its own stats pattern for SUMMARY_LINE only (01 L44-48). The "no `*_FROM`/`_rule_seen` gate needed" part is VERIFIED (flagged same=True over 59 items). |
| 02 AGAINST 1: (a) has no measured benefit; 4 Q at <092, 0 at >=092; a `mutation` exemption repeats 103's AGAINST 3 | 01 L183-186, L259-260; work/103/02-improvements.md L64 | VERIFIED | |
| 02 AGAINST 2: 0 of 34 maxes change; Σ uses max (L1583); deselected runs 0.07-23.78 s vs full suites 80-120 s | 01 L155-255 (printed range 0.07 s at 103/06 to 23.78 s at 095/05); work/095/05 L74 | WRONG | Fixed: the 0.07-23.78 s range covers the printed lines at >=076 only. Full suites in this data reach 152.97 s (095/05 L74), so the range is about 80-153 s. The conclusion is unchanged. |
| 02 AGAINST 3: copy filter `kept06` L1582 could drop a 06 full-suite time equal to a 05 deselected time; "did not happen in 059 items" | check_pipeline.py L1582; 01 L269 (`checked: 59`) | VERIFIED | Fixed (typo, R2's note): "059 items" → "the 59 checked items". |
| 02 AGAINST 3: SUMMARY_LINE is shared with the I2 field path (L1579) and "with item 103's pinned docstring test" | tests/test_pipeline_check.py L5853-5858 (asserts docstring phrases only); L670-690, L715-721 | WRONG | Fixed: the I2 sharing (L1579) is right. The 103 test pins docstring text, not SUMMARY_LINE. The tests that pin the shared `_STATS` are `I2_ACCEPT` / `I2_REFUSE` (`test_i2_summary_line_accepted/refused`), R9 being the deselected refusal. |
| 02 Recommendation (a): NO-GO; optionally add 103's template sentence (templates/build-report.md L10) | 01 L259-260; templates/build-report.md L10, templates/verification.md L9 (Grep `Round N`) | WRONG | Fixed: NO-GO stands. The template sentence is already there: build-report.md L10 and verification.md L9 both say runs go "never under a `###` heading or a `Round N ...` heading (item 091)". Nothing to add. |
| 02 Recommendation (b): NO-GO (documented); 72 in-section runs, 0 maxes, 0 LOG BATCH changes | 01 L261-269 | VERIFIED | |
| 02 English row: the collection line `collected 4 items / 1 deselected / 3 selected` has no ` in N.NNs`, so the variant does not match it | docs.pytest.org markers.html (fetched; e.g. "collected 4 items / 1 deselected / 3 selected"); 01 L48 (SUMMARY_D needs ` in (\d+\.\d+)`) | VERIFIED | |
| 02 Mandarin row: "我们可以记录那些被取消选择而未执行的测试用例" = "We can record the test cases that were deselected and not executed"; "2 passed, 1 deselected in 0.04s" | https://gavin-wang-note.github.io/2024/09/17/pytest_deselected (fetched; the full sentence begins "利用这个钩子函数，" "Using this hook function,") | VERIFIED | |
| 02 Spanish row: "2 failed, 2 deselected in 0.02 seconds"; "2 pruebas deseleccionadas por '-kmethod1'" = "2 tests deselected by '-kmethod1'" | https://www.guru99.com/es/pytest-tutorial.html (fetched) | VERIFIED | |
| 02 Japanese row: `-k` substring match on test names instead of `-m`; "1 passed, 3 deselected in 0.12s" | https://pytest-ja.readthedocs.io/stable/example/markers.html (fetched; quote and translation match) | VERIFIED | |
| 02 German row: "2 Tests von '-kmethod1' abgewählt" = "2 tests deselected by '-kmethod1'"; "2 failed, 2 deselected in 0.02 seconds" | https://www.guru99.com/de/pytest-tutorial.html (fetched) | VERIFIED | |
| 02 Russian row: "Опцию `-k` командной строки можно использовать, чтобы указать подстроку, которая должна присутствовать в именах тестов"; "1 passed, 3 deselected in 0.12s" | https://pytest-docs-ru.readthedocs.io/ru/latest/example/markers.html (fetched; translation matches) | VERIFIED | |
| 02 Italian row: "2 test deselezionati da '-kmethod1' ..." = "2 tests deselected by '-kmethod1' ..." | https://www.guru99.com/it/pytest-tutorial.html (fetched; translation matches) | VERIFIED | |
| 02 Holes: the 11 out-of-section deselected lines were counted but not printed or classified, and (b) would not count them | 01 script L104-110 (B-IN printed only when inside; 2 of the 6 out-05 are the printed A-DESEL lines) | VERIFIED | |
| 02 Holes: 03 should quote 83 (measured, >=076), not 308 (raw Grep, upper bound) | 01 L261; Grep re-run (row on 01 F14) | VERIFIED | |

**Totals:** 50 rows checked → **40 VERIFIED as-is**, **10 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None. Ten claims are kept with a correction or a new source (above). Nothing unverified reaches Implementation:
- 01 F10 / 02 FOR 1 "only lowers Σ / cannot cause a false flag": not true through the copy filter (L1582); measured effect nil.
- 01 F15 and 02 L18: UNVERIFIED upgraded with sources (MAX CHANGED 0; 095/05 max 152.97 s).
- 02 L16 "34 files": spans 045-104, not the 58 files.
- 02 FOR 3: inserting into `_STATS_PARTS` would loosen `--log`; a SUMMARY_LINE-only pattern is needed.
- 02 AGAINST 2: full-suite range is about 80-153 s.
- 02 AGAINST 3: typo "059 items" → "the 59 checked items"; the 103 test pins docstring text, not SUMMARY_LINE.
- 02 Recommendation (a): the template sentence already exists (item 091).

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | (a) NO-GO, recorded here. No rule for summary lines under a bare `#{1,2} round N` wrapper; no heading-wording rule; no `*_FROM`; no template change (build-report.md L10 and verification.md L9 already say so, item 091). | 01 L151-270; request.md L11, L15 | This 03 (Decision, Measured count) | `git diff --stat` over 110's commits shows no change to templates/ and no change to any regex or constant in scripts/check_pipeline.py (see step 3 check) | Candidate predicate: 4 lines (2 SUMMARY_LINE + 2 deselected-only) under a bare wrapper, of 58 files in work/076-104 05/06, at 4404a28, R1's script (01 L36-146). All 4 Q, 0 at >=092. Not built. |
| 2 | (b) NO-GO, recorded here. SUMMARY_LINE, `_STATS_PARTS`, `_STATS`, I2_TIMED and LOG_FORMAT unchanged. | 01 L261-269 | This 03 | Same diff check as step 1; `test_i2_summary_line_refused[R9]` still passes | Variant regex: 34 files (IDs 045-104) gain values; 0 of 34 change max; 0 of 6 `batch_log_items` keys change; 59 items checked; at 4404a28, R1's script. Not built. |
| 3 | Text only, in scripts/check_pipeline.py: (i) after the Item 103 paragraph (L218-222) add: "Item 110 (gap w, RI-010): 103's two residuals were measured at 4404a28 and are documented no-gos (see work/110/03-handoff.md): (a) a summary line directly under a `#{1,2} round N` wrapper with no sub-heading: 4 in 58 files of work/076-104, all correctly quoted (084/05 mutants), 0 at 092 and later; (b) `N deselected` runs: 34 files would gain values, 0 per-file maxes and 0 LOG BATCH results change over 59 checked items. If (b) is ever built, add deselected to SUMMARY_LINE only, never to _STATS (the I2 field refuses it)." (ii) L196 `(only lowers Σ)` → `(can lower Σ, or raise it when 06 copies such a run, which the copy filter then keeps; item 110)`. (iii) L465 comment → `# each at most once. "deselected" left out on purpose: the I2 field is a full-suite run, which has none; for SUMMARY_LINE (LOG BATCH) counting -k runs was measured to change nothing (item 110).` One new test `test_check_pipeline_docstring_records_110_no_go` in tests/test_pipeline_check.py, next to 103's (L5853). | This 03; check_pipeline.py L194-196, L218-222, L465 | Docstring and comment lines; 1 test | Test: `doc = " ".join(_cp().__doc__.split())`; assert `"Item 110 (gap w, RI-010)" in doc`, `"0 per-file maxes" in doc`, `"work/110/03-handoff.md" in doc`, `(REPO / "work/110/03-handoff.md").is_file()`, `"only lowers Σ" not in doc`; `src = (REPO / "scripts/check_pipeline.py").read_text(encoding="utf-8")`; assert `"measured to change nothing (item 110)" in src` and `'"deselected" left out on purpose: a full-suite run has none.' not in src`. Mutations in a scratch copy: remove paragraph (i) → the test fails; restore L196's old text → fails; restore L465's old text → fails. Guard: in `git diff -U0` of check_pipeline.py every `+`/`-` line sits inside the module docstring (L1-414) or is a `#` comment line; `python3 -I -c` import shows `SUMMARY_LINE.pattern` and `_STATS` equal before and after. Full suite: base count + 1 passed, same failures. | – |
| 4 | Watch, for A1's daily review (no item opened). Re-run R1's script (01 L36-146) when new 05/06 exist; revisit (a) if any `A` line at >=099 is R, revisit (b) if `FILES WHOSE MAX CHANGED` > 0 or any `batch_log_items[...] same=False`. | 01 script | A1 daily note | The three triggers above, read from the script's stdout | – (watch only; no filter) |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| work/<ID>/05 or 06 (R1 script loop, 01 L74-76) | Skipped, never counted as 0 lines. 105-109 have none (Glob, 2026-11-25): effect there is n/a, not 0. | n/a: no file (skipped) |
| Unreadable 05/06 (`cp._read`, 01 L77-79) | Prints `<ID>/<step>: <why>`, no count. This run: none printed. | `_read` reason |
| Fence open at file end (`_md_lines`, 01 L81-83) | Printed per file; in/out split suspect. This run: none printed. | `open_fence_at_end=True (in/out split suspect)` |
| R/Q class of an `A`/`A-DESEL` line (hand call) | Every one of the 4 is classed (Q, 084/05 L234-268). None is left unclassed. | Q with line reference |
| Deselected lines at 045-075 (in `maxes()` only) | Not printed and not in the 72/11 count; only their effect is measured (0 max changes). Their count is n/a, not 0. | n/a: not printed by the script (01 L104-110 start at TESTS_FORMAT_FROM) |
| The 11 out-of-section deselected lines at >=076 | Counted, not printed or classed (except the 2 A-DESEL); the decision does not depend on them. | n/a: not printed |
| Margin between a deselected run and its file's max | Printed only for 095/05 by R3's Grep (129.19 s). Other files: n/a, only "not above the max" is measured. | n/a: max values not printed |

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Request L11 build condition, (a) | build iff Q = 0 among candidates and R > 0 at or above the cutoff | candidates 2 A + 2 A-DESEL = 4; Q = 4, R = 0; at >=092: 0 + 0 = 0 | NO-GO, matches step 1 |
| (b) outcome | build iff any max or batch key changes | MAX CHANGED 0 of 34; 6 of 6 keys same=True; flagged [] = []; checked 59 = 59 | NO-GO, matches step 2 |
| Wrapper count | 26 + 1 + 1 = WRAP lines | R3 count of WRAP lines in 01 L153-256: 076-091 = 26, 094/05 = 1, 104/06 = 1; 26 + 1 + 1 = 28 | Matches |
| Deselected totals | in05 + in06 + out05 + out06 | 36 + 36 = 72; 6 + 5 = 11; 72 + 11 = 83 | Matches 01 L261 |
| Files gaining values | 34 = files at >=076 with B-IN + files at 045-075 | distinct B-IN files: 076/06, 077/06, 080/06, 084/05, 084/06, 086/06, 087/06, 093/05, 093/06, 094/05, 095/05, 099/05, 099/06, 100/05, 100/06, 101/05, 101/06, 102/05, 102/06, 103/05, 103/06 = 21; 34 − 21 = 13 ≤ 15 Grep files at 045-075 | Consistent |
| Per-file B-IN counts | 05 sum = 36, 06 sum = 36 | 05: 5 (084) + 1 (093) + 6 (094) + 1 (095) + 1 (099) + 5 (100) + 14 (101) + 2 (102) + 1 (103) = 36; 06: 3 (076) + 3 (077) + 1 (080) + 8 (084) + 1 (086) + 1 (087) + 1 (093) + 1 (099) + 3 (100) + 11 (101) + 2 (102) + 1 (103) = 36 | Matches |
| 095/05 margin | max − largest deselected | 152.97 − 23.78 = 129.19 s | Matches Measured count |
| Step 3 test strings vs proposed text | each asserted string is a substring of the new text (whitespace-joined) | "Item 110 (gap w, RI-010)": in (i); "0 per-file maxes": in (i) "0 per-file maxes and 0 LOG BATCH results"; "work/110/03-handoff.md": in (i); "measured to change nothing (item 110)": in (iii); "only lowers Σ": removed by (ii), found today only at L196 (Grep); old L465 text: removed by (iii), found today only at L465 (Grep) | Each assertion passes after the edit and fails on today's file |
| Step 3 numbers vs measurement | docstring figures = Measured count | 4 lines, 58 files, 0 at >=092, 34 files, 0 maxes, 59 items: each equals 01 L257-269 | Matches |
| Cutoff | n/a: no rule, no `*_FROM` | – | – |
| Worked examples | none in the map | – | – |

`check_handoff output (run by the orchestrator 2026-11-25 23:36 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 50
totals line: 50 rows -> 40 as-is, 10 fixed, 0 removed
PASS
```

R3 log line: not written (no shell). After check_handoff prints PASS, the orchestrator runs `python3 scripts/check_pipeline.py --log R3 110 "<as-is> verified, <fixed> fixed, <removed> removed | READY"`, with the counts from check_handoff's `totals line:` output, not from this file.
