# 04 Build plan - 110
Fit verdict: FIT WITH CHANGES

Input: work/110/03-handoff.md (Status READY; check_handoff PASS, 50 rows -> 40 as-is, 10 fixed, 0 removed, run by the orchestrator 2026-11-25 23:36 UTC). Branch daily-fixes/2026-11-25.

Fit check:
- ~$3k account and strategy rules: not touched. This item changes only checker text (scripts/check_pipeline.py docstring and one comment) and adds one test. No ccbot/ code, no config, no 001 rule, no template.
- Existing code: both residuals stay NO-GO, so SUMMARY_LINE, `_STATS_PARTS`, `_STATS`, I2_TIMED, LOG_FORMAT, `_run_seconds`, `batch_log_items`, every `*_FROM` constant and `_rule_seen` stay as they are. I checked the three places step 3 edits on this branch today (Grep, 2026-11-25): the gap (w) parenthetical `(only lowers Σ)` in the module docstring's LOG BATCH "Known gaps" list; the Item 103 paragraph ending `See work/103/03-handoff.md before proposing it.`; and the comment above `_N = r"[1-9]\d*"` that starts `# Item 076: the parts of pytest's summary line`. Each old string appears exactly once in the repo outside work/ (Grep `only lowers|left out on purpose|full-suite run has none`: 2 hits, both in check_pipeline.py). No test pins either old string, so nothing existing breaks.
- No clash with work in flight: 108 (being built now) and 105/109 may touch scripts/check_pipeline.py and tests/test_pipeline_check.py. This plan names every place by function, test or comment text, not by line number. The new test goes right after `test_check_pipeline_docstring_records_103_no_go`, so a test 108 adds elsewhere is not affected. If 105 or 109 has already rewritten the gap (w) sentence or the Item 103 paragraph by the time I2 builds, I2 edits whatever text is there and keeps the asserted strings below.
- Changes to 03 (why the verdict is FIT WITH CHANGES):
  1. Comment (iii) says "counting -k runs". pytest also deselects through `-m` and `--deselect` (Extra research 1), so the comment says "deselected runs (-k/-m/--deselect)". The asserted string `measured to change nothing (item 110)` stays the same.
  2. 03's test checks only that `only lowers Σ` is gone. If the whole (w) parenthetical were deleted, that test would still pass. Add a positive assert on the new (ii) wording, so (ii) is pinned on both sides like (i) and (iii).
  3. The new paragraph (i) goes in as a separate paragraph directly after the Item 103 paragraph and before the `RULES BRANCH` entry, at the same 18-space indent, still inside the module docstring.

## Extra research (with sources)
1. Where deselected tests come from. pytest's collection docs say: "Tests can individually be deselected during collection by passing the --deselect=item option", and "pytest allows multiple --deselect options" (https://docs.pytest.org/en/9.0.x/example/pythoncollection.html, fetched 2026-11-25). `-m` marker selection also prints `N deselected` (https://docs.pytest.org/en/8.3.x/example/markers.html, as R3 verified: `2 passed, 2 deselected in 0.12s` from `-m`). So `N deselected` does not always mean a `-k` run, and a comment that says it does would be a new inexact statement. Change 1 above fixes this. The decision does not change: R1's script matched any `N deselected` part, whatever caused it (03 Measured count (b)).
2. Simpler method check. I considered a `deselected` exemption or a per-file flag instead of text. 03 measured 0 max changes and 0 LOG BATCH changes over 59 items, so any code costs more than it gains. Text plus a pin test is the smallest record, and it follows 103's precedent (`test_check_pipeline_docstring_records_103_no_go`, which joins the docstring on whitespace so line wrapping does not matter). Nothing simpler would still be pinned by a test.
3. Edge case R3 missed: the (w) gap text is about runs pasted *outside* the read sections, not about deselected runs. The copy-filter argument still holds there. Today an unread 05 run outside the sections cannot remove a 06 value equal to it from `kept06` (the `kept06 = [v for v in t06 if all(round(v * 100) != round(c * 100) for c in t05)]` line in `batch_log_items`). So leaving it out can keep an I3 time that would otherwise be dropped, which raises Σ. The (ii) wording "can lower Σ, or raise it when 06 copies such a run, which the copy filter then keeps" is therefore right for gap (w) as written. Nothing to add.

## Files to create/change
1. `scripts/check_pipeline.py`. Text only (module docstring and one `#` comment). No code line changes.
   - (i) Add a new paragraph directly after the Item 103 paragraph (the one ending `See work/103/03-handoff.md before proposing it.`), at the same indent:
     `Item 110 (gap w, RI-010): 103's two residuals were measured at 4404a28 and are documented no-gos (see work/110/03-handoff.md): (a) a summary line directly under a `#{1,2} round N` wrapper with no sub-heading: 4 in 58 files of work/076-104, all correctly quoted (084/05 mutants), 0 at 092 and later; (b) `N deselected` runs: 34 files would gain values, 0 per-file maxes and 0 LOG BATCH results change over 59 checked items. If (b) is ever built, add deselected to SUMMARY_LINE only, never to _STATS (the I2 field refuses it).`
     Wrap it to the docstring's existing width, about 105 columns.
   - (ii) In the LOG BATCH "Known gaps" list, replace `(only lowers Σ)` (right after `(w) runs pasted outside the two sections are not read`) with `(can lower Σ, or raise it when 06 copies such a run, which the copy filter then keeps; item 110)`.
   - (iii) In the comment above `_N = r"[1-9]\d*"`, replace the second line `# each at most once. "deselected" left out on purpose: a full-suite run has none.` with:
     `# each at most once. "deselected" left out on purpose: the I2 field is a full-suite run, which has none;`
     `# for SUMMARY_LINE (LOG BATCH) counting deselected runs (-k/-m/--deselect) was measured to change nothing (item 110).`
     (This is change 1. The first comment line, `# Item 076: ...`, stays as it is.)
2. `tests/test_pipeline_check.py`. Add one test directly after `test_check_pipeline_docstring_records_103_no_go`:
   ```
   def test_check_pipeline_docstring_records_110_no_go():
       """Item 110: the docstring records 103's residuals (a)/(b) as measured no-gos, gap (w) no longer says
       "only lowers", and the _STATS_PARTS comment says why deselected is left out."""
       doc = " ".join(_cp().__doc__.split())
       assert "Item 110 (gap w, RI-010)" in doc
       assert "0 per-file maxes" in doc
       assert "work/110/03-handoff.md" in doc and (REPO / "work/110/03-handoff.md").is_file()
       assert "or raise it when 06 copies such a run" in doc          # change 2: (ii) pinned positively
       assert "only lowers Σ" not in doc
       src = (REPO / "scripts/check_pipeline.py").read_text(encoding="utf-8")
       assert "measured to change nothing (item 110)" in src
       assert '"deselected" left out on purpose: a full-suite run has none.' not in src
   ```
   Every check is a literal `in` or `not in` on a fixed string this item owns, with two negatives (RI-012). The source file is read with a fixed encoding.

No other file. templates/build-report.md and templates/verification.md already carry the item-091 sentence (03 row on 02 Recommendation (a)). work/110/02 is not edited: R3 recorded its typo fix ("059 items" -> "the 59 checked items") in 03.

## Tests and checks
1. New test passes: `python3 -m pytest tests/test_pipeline_check.py -k records_110_no_go` -> `1 passed, <n> deselected`.
2. It fails on today's file: run it before the edit (or on a scratch copy without the edit) -> 1 failed (the first assert, `Item 110 (gap w, RI-010)`).
3. Mutations, in a scratch copy only (never in the repo). The I2/I3 scratch dir follows the `i2-110-r<N>-<8 chars>` / `i3-...` rule. Each must make the new test fail:
   - M1: remove paragraph (i) -> fails on `Item 110 (gap w, RI-010)`.
   - M2: restore `(only lowers Σ)` -> fails on `or raise it when 06 copies such a run` and on `only lowers Σ`.
   - M3: delete the (ii) parenthetical entirely -> fails on `or raise it when 06 copies such a run` (killed only because of change 2).
   - M4: restore the old comment line -> fails on `measured to change nothing (item 110)` and on the old-text negative.
   - M5: delete work/110/03-handoff.md in the scratch copy -> fails on `.is_file()`.
4. Text-only guard: in `git diff -U0 -- scripts/check_pipeline.py` for 110's own commit, every `+`/`-` line is inside the module docstring (before the first `import`) or is a `#` comment line. No regex, constant or code line changes. Before and after the edit, `python3 -I -c "import importlib.util,sys; s=importlib.util.spec_from_file_location('cp','/home/claude/cover-calls/scripts/check_pipeline.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.SUMMARY_LINE.pattern); print(m._STATS)"` prints the same two lines.
5. Steps 1 and 2 (no-gos): `git diff --stat` for 110's commit lists only scripts/check_pipeline.py, tests/test_pipeline_check.py and work/110/ files, with no templates/ file. `test_i2_summary_line_refused[R9]` (`3 passed, 1 deselected in 0.12s` refused) still passes, along with all `test_i2_summary_line_accepted` rows.
6. `test_check_pipeline_docstring_records_103_no_go` still passes: paragraph (i) sits after 103's paragraph and does not change its text.
7. Full suite: base count + 1 passed, with the same failures and skips as the base run on this branch at build time. 108/105/109 may change the base count, so I2 records the base from its own pre-edit run, not from a number written here.
8. `python3 scripts/check_pipeline.py` on the branch: no new INCOMPLETE / LOG BATCH / RULE NOT SEEN entry caused by 110. LOG BATCH results for every item are the same as before the edit, because no code changed.
9. Python minimum (RI-008): the new test has no f-strings and no 3.11+ syntax. I3 runs `python3.11 -m py_compile tests/test_pipeline_check.py scripts/check_pipeline.py` where python3.11 is available.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Decision (a) NO-GO / map step 1: no wrapper-heading rule, no heading-wording rule, no `*_FROM`, no template change | Files to create/change: nothing added for (a) beyond docstring (i); Tests and checks 4, 5 (diff guard, no templates/) |
| Decision (b) NO-GO / map step 2: SUMMARY_LINE, `_STATS_PARTS`, `_STATS`, I2_TIMED, LOG_FORMAT unchanged | Tests and checks 4 (SUMMARY_LINE.pattern and `_STATS` same before and after), 5 (`test_i2_summary_line_refused[R9]` passes) |
| Map step 3 (i): Item 110 paragraph after the Item 103 paragraph | Files 1 (i); test asserts `Item 110 (gap w, RI-010)`, `0 per-file maxes`, `work/110/03-handoff.md` + `.is_file()`; mutations M1, M5 |
| Map step 3 (ii): `(only lowers Σ)` -> `(can lower Σ, or raise it when 06 copies such a run, which the copy filter then keeps; item 110)` | Files 1 (ii); test negative `only lowers Σ` + positive `or raise it when 06 copies such a run` (change 2); M2, M3 |
| Map step 3 (iii): `_STATS_PARTS` comment rewritten | Files 1 (iii), worded "deselected runs (-k/-m/--deselect)" instead of "-k runs" (change 1, Extra research 1); test asserts `measured to change nothing (item 110)` + old-text negative; M4 |
| Map step 3 test `test_check_pipeline_docstring_records_110_no_go`, next to 103's | Files 2 |
| Map step 3 guard (diff `-U0` inside docstring or `#` lines; SUMMARY_LINE/_STATS equal) and full suite base + 1 | Tests and checks 4, 7 |
| Map step 4: watch for A1 (re-run R1's script on new 05/06; triggers: an `A` line at >=099 classed R; `FILES WHOSE MAX CHANGED` > 0; any `batch_log_items[...] same=False`) | DROPPED: not a build step. It is an A1 daily-review note with no code and no item (03 map step 4 says "watch only; no filter"). The paragraph (i) pointer to work/110/03-handoff.md is where the triggers can be found. |
| Correction for 02 ("did not happen in 059 items" -> "the 59 checked items") | DROPPED: already recorded in 03 (Correction line); 02 is a research record and is not edited at build time. No code text uses it. |
| Fact-check fixes (01 F10, F15, 02 L16, FOR 1, FOR 3, AGAINST 2/3, Recommendation (a), L18) | Only F10 / FOR 1 ("only lowers Σ") reaches code: Files 1 (ii). FOR 3 ("SUMMARY_LINE only, never _STATS") reaches code: Files 1 (i) last sentence. The rest are 03 text only: DROPPED from the build (no code statement to change) |
| Missing inputs table (05/06 absent, unreadable, open fence, R/Q class, 045-075 lines, out-of-section lines, margins) | DROPPED: these are inputs of R1's measurement script, which stays in 01 and is not built. The built code adds no input. |
| Person-followed rule (001: slack, tolerance, cap) | None changed. No 001 text update and no request needed. |

## Guardrail tests
- Feasibility: no filter or window rule is built (both are NO-GO), so no count has to be pinned. The measured counts 03 records (4 of 58 files, Q = 4, R = 0; 34 files, 0 maxes, 6 of 6 keys same, 59 checked; dated 2026-11-25 at 4404a28) go into docstring (i). `test_check_pipeline_docstring_records_110_no_go` pins `0 per-file maxes` and the pointer to 03. The 103 test pins its own counts in the same way.
- Missing inputs: no optional input is added to the code. The one file the new test reads besides the module is work/110/03-handoff.md. If it is absent, `.is_file()` fails loudly (mutation M5); it is never treated as present. The source read of scripts/check_pipeline.py is a required file; if it is missing, the test errors instead of passing.

## Expected result
- scripts/check_pipeline.py: module docstring has the Item 110 paragraph after the Item 103 paragraph, and gap (w) reads `(can lower Σ, or raise it when 06 copies such a run, which the copy filter then keeps; item 110)`. The `_STATS_PARTS` comment names the I2 reason and the item-110 measurement. No code, regex or constant changes, and SUMMARY_LINE.pattern and `_STATS` are byte-identical.
- tests/test_pipeline_check.py: one new test, passing. It fails on today's text and under M1-M5.
- Full suite: base + 1 passed, same failures and skips as the base. check_pipeline output for every item is unchanged except for whatever this item's own step files add.
- Both residuals of 103 are closed as measured no-gos with a pinned pointer, which closes RI-010's 2026-11-25 near miss "`## Round N (...)` wrapper / `deselected` -> 110".

Recurring issues checked (item 013), against this plan:
- RI-001 (ESCALATED): no filter rule is built. Every number in docstring (i) is copied from 03's dated measurement (4404a28, 2026-11-25) and is stated as measured, not as a law ("measured at 4404a28"). The watch triggers stay with A1.
- RI-014 (OPEN): the only git use is `git diff` / `git diff --stat` on 110's own commit (Tests and checks 4, 5), which does not depend on clone depth. No check depends on history depth.
- RI-010 (GUARDED; 110 is its near miss): closed as two documented no-gos with a pin test. No log line is written by me; the orchestrator runs `--log I1`.
- GUARDED entries also checked: RI-002 (no value is defaulted; a missing 03 fails the test, M5); RI-004/RI-005 (each asserted string is a substring of the planned text: `Item 110 (gap w, RI-010)`, `0 per-file maxes`, `work/110/03-handoff.md` in (i); `or raise it when 06 copies such a run` in (ii); `measured to change nothing (item 110)` in (iii); each fails on today's file); RI-006 (no hand totals; full-suite base is taken from I2's own run); RI-007 (Scope FULL, goes through I2/I3/A1); RI-008 (no new syntax; py_compile on 3.11, Tests and checks 9); RI-012 (literal fixed-string checks with two negatives); RI-003/RI-009/RI-011/RI-013 n/a (no calendar, branch listing, merge-base or realtest change).

Log fields: FIT WITH CHANGES | 2 files planned
