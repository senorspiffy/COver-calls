# 05 Build report - 085
Built on branch daily-fixes/2026-11-20 at HEAD 289d321 (uncommitted). 085 was built first today (no other I2 ran before it), so tests/test_held_quote.py was in its 083 state when the build started, as 04 says.

## Changes made (file: what changed)
- tests/test_held_quote.py: added the imports from 04 (`pytest`, `run_daily`, `NoQuote`, `SimBroker`, `load_config`, `Portfolio`, `Quote`, `State`), the constants `HELD_SYM = "VALE261218C00013000"` and `HELD`, `class HeldQuotes` (C2: raises `ccbot.broker.base.NoQuote` for any ticker except VALE; C3: docstring wording), `_held_run(tmp_path, universe)`, `_widened(stub)`, `test_run_daily_passes_held_option_at_universe_site` (asserts i-iii) and `test_run_daily_passes_held_option_at_held_only_site` (asserts i-ii). I left the two 083 tests as they were. Nothing is written outside tmp_path.

File counts (commands run after the build):
- new: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0
- changed: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → 1
- `git diff --stat`: `tests/test_held_quote.py | 62 ++++++++++++++++++++++++++++++++++++++++++++++--` / `1 file changed, 60 insertions(+), 2 deletions(-)`

## Connectivity check
- [x] every new function/rule is used: `HeldQuotes` is used by `_held_run`. `_held_run` and `_widened` are used by both new tests. `HELD_SYM` and `HELD` are used by the stub and the fixture. Every new import is used.
- [x] every input has a source, every output has a consumer: the inputs are the synthetic fixture values (VALE close 9.83, the 13C quote, cash 1000, 200 shares), labelled synthetic in the docstring. The outputs are the `scan` dict and `stub.windows`, and pytest's assertions read both. Report and state files go to tmp_path and pytest removes them.
- [x] every branch ends in a defined result: the stub raises `NoQuote` for a ticker other than VALE, and bot.py L219-220 skips that ticker (this is the path Test B runs). The stub returns `[]` for a window that does not contain 13.0, so equity becomes NaN and the test fails (the mutation path). It returns `[]` for snapshots when HELD_SYM is not asked for. Held ticker with no quote at site (b): not reachable through SimBroker (C1). `advance` raises DataError first, which is a defined error and not a silent skip.
- [x] no leftover TODOs or unused files: `grep -n TODO tests/test_held_quote.py` finds nothing. No new files.
- Missing-data policy: the grep `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` gives 38 hits. All 38 were already there: `git diff --stat -- ccbot/` is empty, so none is new or changed. In the new test code: no dataclass has a numeric default (the only class is `HeldQuotes`, which is not a dataclass). The one comparison is `lo <= 13.0 <= hi` in the stub and in `_widened`. With NaN on either side it is False, so the stub returns no quote and the test fails. It cannot pass on NaN. Equity is checked with `pytest.approx(2962.0)` at default tolerance, and NaN never equals approx (E1).
- Feasibility numbers, measured by running `_held_run` in a scratch tmp dir:
  - Test A (universe ["VALE"]): equity 2962.0. rejects `{'VALE': 'NO_STRIKE_IN_TOLERANCE'}`. windows `[('VALE', '2026-12-18', 6.881, 13.0)]`. The 13C is inside 1 of 1 window, and the monthly pick is 2026-12-18 (1 candidate).
  - Test B (universe ["SYNTH_A"]): equity 2962.0. rejects `{'SYNTH_A': 'NO_QUOTES'}`. windows `[('VALE', '2026-12-18', 6.881, 13.0)]`, inside 1 of 1 window.
  - Delta tolerance: 0 of 1 fixture quote is in [0.20, 0.35] (delta 0.03), which matches VALE's NO_STRIKE_IN_TOLERANCE.
  - Without the widening, the window would be 6.881-12.779 (9.83 x 1.3), and 13 is outside it (0 of 1). I3 pins this with M1-M4.

## Test output (pasted, not summarized)
`python3 -m pytest -q tests/test_held_quote.py --durations=0`:
```
....                                                                     [100%]
============================== slowest durations ===============================
0.01s call     tests/test_held_quote.py::test_run_daily_passes_held_option_at_universe_site
0.01s call     tests/test_held_quote.py::test_run_daily_passes_held_option_at_held_only_site

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
4 passed in 2.30s
```

`python3.11 -m py_compile tests/test_held_quote.py` (python3.11 is at /usr/bin/python3.11): no output, exit 0.

Full suite `python3 -m pytest -q`, before the change (same HEAD 289d321, file in its 083 state):
```
1 failed, 570 passed, 1 skipped in 76.76s (0:01:16)
```
After the change:
```
1 failed, 572 passed, 1 skipped in 79.79s (0:01:19)
```
Passes went up by 2 and the skip count stayed at 1, as 04 expects. The one failure was there before the change and is not caused by 085: `FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`. The committed tree's check_pipeline.py reports `INCOMPLETE: 081 (no log line for R3), 083 (log line for I2 does not match its format (item 045) ...; 06 Verdict is PASS but has no 'Sent back to: none' line (item 071))`. This is the PR #33 format change on 083, which 084 fixes, plus 081 still in research.

Final `git status --short`: ` M tests/test_held_quote.py`, plus other items' untracked work/082/03-handoff.md and work/086/03-handoff.md, which are not mine. Nothing changed in state/ or reports/.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: tests/test_held_quote.py only; no ccbot/realtest.py or trigger file changed)

## Deviations from plan
- None in code.
- One note: 04 says "I2 builds 085 last", but per the caller's instruction 085 was built first today. This makes no difference, because 04 also says no other item touches this file, and the file was in its 083 state.
- The suite was not green before this change (1 failed, above). 04 asked for "the branch count before 085 plus 2", and that is what I got.

## Recurring issues checked
Read first: logs/recurring-issues.md.
- RI-001 (ESCALATED): every window and filter in this build has a measured count (above): 1 of 1 widened window, 0 of 1 unwidened, 0 of 1 quote in tolerance, 1 pick candidate.
- RI-002: no value is filled. A missing quote leaves equity NaN, and approx(2962.0) fails both NaN and an invented mark.
- RI-006: the pytest lines above are pasted as printed.
- RI-008: compiled with python3.11.
- RI-009: no mutation run in the repo. I3 runs M1-M4 on a scratch copy.
- RI-010 (ESCALATED): my log line is written with `check_pipeline.py --log` right after this file.
- RI-014 (OPEN): not applicable (no git or checker change).

RI-001: ESCALATED, unchanged (085 measured counts for all its windows; no process change)
RI-002: GUARDED, unchanged (085 adds a NaN-equity pin at both run_daily sites; no default added)
RI-010: ESCALATED, unchanged (I2 line written by --log)
