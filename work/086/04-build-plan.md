# 04 Build plan - 086
Fit verdict: FIT WITH CHANGES

I1 had no shell in this run. I ran no git command, no pytest and no `check_pipeline.py`. Code facts come from reading `scripts/check_pipeline.py`, `tests/test_pipeline_check.py`, `.claude/commands/run-item.md`, `templates/build-report.md`, `templates/verification.md`, the logs and work/076, 079, 083 on daily-fixes/2026-11-20, before 081 and 084 land. Functions are named instead of line numbers, because 081 and 084 edit the same file first (build order 081 -> 084 -> 086). The orchestrator writes the I1 log line: `python3 scripts/check_pipeline.py --log I1 086 "FIT WITH CHANGES | 3 files planned"`.

Recurring issues checked (item 013), open or ESCALATED entries:
- **RI-001** (ESCALATED). Every window and filter below has a dated count: C flags 1 of 35 (083, 2026-11-20); D refuses R1 on 083's batch shape and exempts the 7 send-back items. Two filters are new here, the anchored summary-line match (3 test-ID lines in 076's 05/06 today) and the copy guard. I2 recounts both in step 0. Nothing is stated as "always".
- **RI-010** (ESCALATED, this item). It is met by fixture (b) (083 flagged on real data with the exception emptied) and by D1. `LOG_BATCH_EXCEPT` is a pinned, printed, separate dict, and 083 is not added to `LOG_TIME_EXCEPT`.
- **RI-014** (OPEN). C and D make no git call, so clone depth cannot change them. 081's call-site census dict is unchanged, and the census test proves it. Fixture (b) needs no git, so there is no shallow skip.
- Also checked (GUARDED): RI-002 (a missing time is never 0 s and never a flag; not computable is printed), RI-004/RI-005 (every fixture number re-derived against the trigger below), RI-006 (log fields come from `--log`), RI-007 (Scope FULL; RULE_PATHS change needs the person's OK), RI-008 (3.10 compile test), RI-009 (built on top of 081 and 084), RI-012 (verdicts by fullmatch group, summary lines anchored at the line start: change 2). RI-003, RI-011 and RI-013 are not touched.

## Fit check
- **~$3k account.** Process only. Nothing in ccbot/, config/ or data/ changes. No trade rule the person follows changes (no slack, tolerance or cap), so no 001 rule text is updated. Nothing connects to a brokerage.
- **Existing code.** C is a new reader beside `late_log_lines` and prints next to LOG TIME. D is a new refusal inside `write_log`, after its current checks. Neither conflicts with anything built. 084's scope lock ("`write_log`'s refusal stays numeric") is about 084's own changes. D leaves the format refusal and its text first and untouched, so 084's test (g) (`--log I2 083 "... tests 344/344"` refused) still exits 2 on format before D runs.
- **081.** 081 changes `late_log_lines`, `main()`'s branch lines and the exit expression, and adds a census test of every `_git(`/`_git_ok(` call. 086 adds **no** git call. If I2 finds it needs one, it goes through 081's `_git_ok` with a census entry and reason. Place the LOG BATCH print directly after whatever LOG TIME print 081 leaves, and add the flag to whatever exit expression 081 leaves.
- **084.** 084 changes `incomplete()`, `log_fields_ok(..., new_rule=True)`, `log_hint(...)` and adds `RULE NOT SEEN:` after INCOMPLETE. 086 calls `re.fullmatch(LOG_FORMAT[agent], ...)` directly for verdicts and never reads I2's format, so 084's gate does not touch it. 084's extended `test_repo_pipeline_has_no_skipped_items` gets one more assert (below). Keep its shallow skip as is.
- **Changes to 03 (why "WITH CHANGES"):**
  1. **R3's verdict is group 2, not group 1.** `LOG_FORMAT["R3"]` is `\d+ (verified|as-is), ... \| (READY|BLOCKED)\b.*`, so group 1 is `verified`/`as-is`. 03 step 3 reads every verdict from group 1, which would never see BLOCKED. Use an explicit table `SEND_BACK = {"R3": (2, "BLOCKED"), "I1": (1, "NOT A FIT"), "I3": (1, "FAIL")}`. D4 pins it, and mutation M6b (group 1 for R3) makes D4 fail.
  2. **Summary lines must be anchored at the line start (RI-012).** 076/05 L39 and 06 L57, L138 hold `FAILED tests/...::test_i2_summary_line_accepted[1 failed, 383 passed, 1 skipped in 58.86s]`. That is a test ID, because the I2 parametrize cases are pytest summary strings, not a run. A search anywhere in the line would read 58.86 s as a run. Rule: after `strip()`, the line must start with an optional `=+ ` border, then a non-empty `_STATS` match, then ` in <d>.<dd>s` or ` seconds`. Trailing text is allowed (076/05 L29 `... in 22.02s        (FAILED ...)`, 06 L136 `<- SURVIVES`). Fixture N8 and mutation M9.
  3. **C reads every LOG_LINE-shaped line of the item, whatever its fields.** 03's Missing-inputs row "malformed log line: ignored for C" is unsound for C. If a malformed last I3 line is ignored, the end moves earlier and Δ shrinks, which can turn into a false flag. Use `LOG_LINE.match` (time, agent, ID) and ignore the fields for start/end/I2 detection. D still reads verdicts by fullmatch only, so a malformed verdict line is not a send-back (the safe side, and INCOMPLETE reports it). Fixture N10.
  4. **Section bounds.** A section starts at a line `^## Test output\b` (05) or `^## Tests re-run\b` (06) whose `_md_lines` state is "out". It ends at the next "out" line matching `^#{1,2} ` (076/06 uses `# Round 1 (kept as written ...)`, a level-1 heading). Summary lines count in state "out" or "in" (pytest output is usually fenced). HTML comments are already dropped by `_md_lines`. Runs written under other headings (076/05 round 2 sits under `## Round 2 build`) are not read. They only lower Σ, which is the safe side; this is listed as a known gap.
  5. **Start-line ties.** 03 says "file order for ties". The logs are two files, so: implementation lines with the same stamp as the first I2 line count as before it only if they sit above it in the same file. Research lines with a stamp ≤ the first I2's stamp count as before (R steps come before I steps in run-item order, and an R re-run can only follow a send-back verdict, which is after the first I2). Fixture N9 (FAST shape, no I1 line).
  6. **D is per item.** The orchestrator's note for today: research steps of different items interleave on this branch. D reads only `work/<ID>/` and the lines with that ID. Test D9: another item's 02-06 present does not refuse this item's R1.
  7. **Clock caveat in the docstring.** pytest's duration is `timing.time() - self._sessionstarttime` (Extra research 1), and `time.time()` "can return a lower value than a previous call if the system clock has been set back" (Extra research 2). The log stamp is also wall clock (`dt.datetime.now(utc)`). A clock step during a run can move both. The docstring says "impossible under the run-item order on one steady clock". The 083 margin is 36.07 s.

## Extra research (with sources)
1. **pytest's printed time is wall-clock session time, from `time.time()`.** In `pytest_sessionstart` (`@hookimpl(trylast=True)`): `self._sessionstarttime = timing.time()`. In `summary_stats`: `session_duration = timing.time() - self._sessionstarttime`. `format_session_duration`: `f"{seconds:.2f}s"` under 60, else `f"{seconds:.2f}s ({dt})"` with `dt = datetime.timedelta(seconds=int(seconds))`. [https://pytest.org/latest/_modules/_pytest/terminal.html] Three consequences. The session starts after the interpreter starts, so the real process time is ≥ the printed time, which is the safe direction for C. `.2f` gives the 0.005 margin (03 #7). The `(0:01:25)` suffix is an int timedelta and is ignored, because the seconds are already read.
2. **`time.time()` is not monotonic:** "While this function normally returns non-decreasing values, it can return a lower value than a previous call if the system clock has been set back between the two calls." `time.monotonic()` is "a clock that cannot go backwards". [https://docs.python.org/3/library/time.html] Neither the stamp nor pytest uses a monotonic clock, so change 7 records this as a known gap and does not claim proof against clock steps.
3. **Edge case R3 missed: summary strings inside test IDs** (change 2). Grep of work/076/0[56]-*.md, 2026-11-20: 3 `FAILED ...[... in 58.86s]` lines (05 L39; 06 L57, L138). This repo's own tests are parametrized with pytest summary lines (`I2_ACCEPT`/`I2_REFUSE`), so any 05/06 that pastes a failing case carries one.
4. **Edge case R3 missed: R3's group index** (change 1). This comes from reading `LOG_FORMAT`; no outside source is needed.

## Files to create/change
3 files (plus I2's own work/086/05).

1. `scripts/check_pipeline.py`
   - Module docstring: a `LOG BATCH` entry directly after the LOG TIME entry, and a sentence in the `--log` paragraph for D. Text to cover:
     - the formula (`Σ − 0.005·k ≥ (Δ+1)×60`) and the whole-item window (start = the item's latest line before its first I2 line, end = its last I3 line);
     - which lines are read (the anchored summary rule, the two sections, I2 log fields) and the copy guard;
     - "impossible under the run-item order on one steady clock (run-item L14, L16)";
     - `LOG_BATCH_EXCEPT`;
     - not computable is listed, never flagged;
     - exit 1 when an item is flagged;
     - known gaps: (w) runs outside the two sections are not read; (x) fast or untimed suites can't be flagged, D covers those; (y) after any send-back verdict D is off for that item, and C covers only its I rounds; (z) clock steps (change 7);
     - for D: the refusal, the send-back table, and that 07 and other files never count.
   - New constants next to `LOG_TIME_EXCEPT`:
     - `LOG_BATCH_EXCEPT = {"083": "six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)"}`, with the comment "Never add a new item here".
     - `BATCH_ROUND = 0.005` (pytest `.2f`).
     - `SEND_BACK = {"R3": (2, "BLOCKED"), "I1": (1, "NOT A FIT"), "I3": (1, "FAIL")}` (change 1).
     - `SUMMARY_LINE = re.compile(rf"(?:=+ )?(?={_N} )(?:{_STATS}) in (\d+\.\d+)(?:s| seconds)\b")`, used with `.match` on the stripped line (change 2). I2 may write it another way, but it must keep three properties: anchored at the start, at least one stats part, seconds in group 1.
   - New `_item_lines(logs) -> dict[str, list[tuple[datetime, str, str, int, int]]]`: per ID, every LOG_LINE-shaped line as (stamp, agent, team, file index, line index), stamp = file stem date + HH:MM (UTC). Files are read as `logs/research/????-??-??.md` and `logs/implementation/????-??-??.md`. An unreadable file (OSError, UnicodeDecodeError) is returned in a separate list of names, never skipped silently (it makes every item with lines of that date not computable).
   - New `_run_seconds(path, heading) -> tuple[list[float], str | None]`: every SUMMARY_LINE value inside every section that starts with `heading` (change 4). It returns `([], "<file> unreadable")` when the read fails, and `([], None)` when the file is absent.
   - New `batch_log_items(work=Path("work"), logs=Path("logs"), excepted=None) -> dict` (rule C). `excepted=None` means `LOG_BATCH_EXCEPT`. The dict keys are `flagged` (list of entry strings), `flagged_ids`, `excepted` (list of (ID, why) whose request.md exists), `not_computable` (list of (ID, reason)), `checked` (int), `in_progress` (list of IDs). For each ID ≥ LOG_CHECK_FROM with `work/<ID>/` present:
     - no I2 line: skipped (not counted);
     - first I2 line and no later I3 line: `in_progress`;
     - in `excepted`: counted in `checked`, listed in `excepted`, not evaluated;
     - start: the latest line before the first I2 line (change 5); none means not computable `(no line before I2)`;
     - end: the last I3 line (by stamp, then file and line order);
     - Δ = (end − start) in whole minutes;
     - t05: the largest of the seconds from the item's I2 log fields (the text after `tests `, matched with SUMMARY_LINE) and `_run_seconds(05, "## Test output")`;
     - t06: the largest of `_run_seconds(06, "## Tests re-run")` after dropping any value equal (to 0.01) to a t05 candidate;
     - k = the number of known values;
     - if k = 0: not computable `(no pytest time in 05/06/I2 line)`; an unreadable file gives `(<file> unreadable)`;
     - otherwise flag when `t05 + t06 − BATCH_ROUND·k ≥ (Δ+1)·60`. Entry: `<ID> (<Σ:.2f> s of pytest runs between <start %Y-%m-%d %H:%M> and <end %H:%M> UTC, limit <(Δ+1)·60> s; impossible under the run-item order, item 086)`.
   - `write_log` (rule D): after the existing agent/ID/field check and after the request.md check, so both refusal texts and their order stay the same:
     - `later = [STEPS[s] for s in sorted(AGENT) if s > step_of(agent) and (Path("work")/item/STEPS[s]).exists()]` (01-06 only, never 07 or other files);
     - if `later` and not `_sent_back(item)`: print `--log refused: work/<ID>/ already has <later files joined by space> after <agent>'s step; write this line before the later steps run, then redo those steps (item 086)` to stderr and return 2, writing nothing.
   - New `_sent_back(item, logs=Path("logs")) -> bool`: True if any log line of the item with agent in SEND_BACK has `re.fullmatch(LOG_FORMAT[a], fields.strip())` and group n == the verdict word, or if work/<ID>/07 exists and `_a1_results(text)` contains `FAIL` (case-insensitive, as `classify` reads it). An unreadable 07 counts as not FAIL (the refusal side).
   - `main()`: call `batch = batch_log_items()` and print after the LOG TIME line:
     - `LOG BATCH: <'; '.join(flagged) or 'none'>`;
     - plus ` (not checked: <ID>: <why>; ...)` when `excepted` is non-empty;
     - plus `; not computable: <ID> (<reason>), ...` when `not_computable` is non-empty.
     - Add `or batch["flagged"]` to the exit expression. The text and exit code are the same with or without git.
   - Scope lock: no change to `late_log_lines`, `LOG_TIME_EXCEPT`, `LOG_FORMAT`, `log_fields_ok`, `log_hint`, `incomplete`, `classify`, or any git call.
2. `tests/test_pipeline_check.py`: the new tests below, plus one assert in `test_repo_pipeline_has_no_skipped_items`. No existing assertion is edited.
3. `.claude/commands/run-item.md`:
   - L14, after "`LOG TIME:` must not name it": add ", and `LOG BATCH:` must not name it (item 086)".
   - L16, after "a `--log` refusal (exit 2) goes back to the step.": add "`--log` also refuses while a later step file (01-06) of the same item exists, unless the item was sent back (R3 BLOCKED, I1 NOT A FIT, I3 FAIL, or `A1 result: FAIL`): log each step before the next one runs (item 086)."
   - This is a RULE_PATHS change and needs the person's OK at PR review.

## Tests and checks
**Step 0 (read-only, I2, before any edit, after 081 and 084 have landed):** with a throwaway script in the scratchpad (never in the repo) that imports nothing new, count over work/0[4-8]?/0[56]-*.md and paste the numbers into 05:
- (i) lines where an unanchored search finds a summary time but the anchored match does not (expected ≥ 3, 076). If 0, stop and send back to I1: change 2 has no real case.
- (ii) items where the copy guard drops a 06 value (count stated, 0 allowed). The guard only lowers Σ, and N4 pins it.
- (iii) the C table per item (start, end, Δ, t05, t06, k, ratio Σ/limit). Send back to I1 if any item other than 083 is flagged, or if 083 is not flagged with the exception emptied.

**New tests (none needs git):**
- C fixtures. Each fixture is a tmp_path tree with `work/<ID>/request.md`, 05/06 text and log files, and calls `batch_log_items(work, logs, excepted={})` in-process:
  - (a) ID 999 with 083's six lines at 10:15 (research R1-R3, implementation I1, I2, I3). The I2 field is `2 files changed | tests 344 passed, 1 skipped in 48.51s`. 05 has `## Test output` with `344 passed, 1 skipped in 48.51s`, and 06 has `## Tests re-run` with `344 passed, 1 skipped in 47.57s`. Expect `flagged_ids == ["999"]`. Also via `_run(... "check_pipeline.py")`: `LOG BATCH: 999 (` is in stdout and exit 1.
  - (b) `batch_log_items(REPO/"work", REPO/"logs", excepted={})`: `"083" in flagged_ids` (RI-010's "its 083 fixture is flagged", on real data).
  - (c) Add to `test_repo_pipeline_has_no_skipped_items`: `"LOG BATCH: none (not checked: 083: six lines written in one batch" in out`.
  - `test_log_batch_except_is_pinned`: `set(LOG_BATCH_EXCEPT) == {"083"}` and `"083" not in LOG_TIME_EXCEPT`.
  - N1: 079's real lines (R1 23:25, R2 23:28, R3 23:35, I1 23:39 on 11-19; I2 02:02, I3 02:10 FAIL, I2 02:15, I3 02:22 on 11-20), I2 fields as committed, 05 90.93, 06 90.21: not flagged.
  - N2: Δ0, 05 30.00, 06 30.00: not flagged. 06 30.01: flagged.
  - N3: Δ1 (I1 10:00, I2/I3 10:01), 45.00 + 45.00: not flagged.
  - N4: Δ0, 05 40.00, 06 only 40.00: not flagged (copy dropped, k = 1).
  - N5: all six lines in one minute, 05/06 without times: `not_computable` names it with `(no pytest time in 05/06/I2 line)`; not flagged; `_run` exit 0.
  - N6: three items with lines interleaved in one minute (today's 23:27 pattern), each item's own I1 -> I3 ≥ 5 min, 30 s runs: none flagged.
  - N7: 06 with `# Round 2` ... `## Tests re-run` 50.00 ... `# Round 1 (kept ...)` ... `## Tests re-run` 10.00, 05 20.00, Δ0: t06 = 50.00, flagged (70 − 0.01 ≥ 60). Section bounds and the largest value are both pinned.
  - N8 (change 2): 05 `## Test output` with `FAILED tests/x.py::t[1 failed, 2 passed in 59.00s]` and `1 failed, 2 passed in 1.00s`, 06 `2.00s`, Δ0: not flagged.
  - N9 (change 5, FAST shape): research R1 10:10, R3 10:15; implementation I2 10:15, I3 10:15; 05 40.00, 06 39.00: flagged (start R3 10:15, Δ0, 78.99 ≥ 60).
  - N10 (change 3): I1/I2/I3 at 10:00, then a malformed `10:05 | I3 | 999 | PASS | see 06`, 05 50.00, 06 49.00: not flagged (Δ5, 98.99 < 360).
  - N11: 06 unreadable (bytes `\xff`): `not_computable` reason names the file; no traceback.
  - N12: an I2 line and no later I3 line: in `in_progress`, not flagged.
- D fixtures. Each uses `_log` (subprocess) in tmp_path with `_request`, and asserts the exit code, the stderr text and whether the log file changed:
  - D1: `--log R1 999` with 01-06 present: exit 2, stderr names `02-improvements.md 03-handoff.md 04-build-plan.md 05-build-report.md 06-verification.md`, no logs/ written.
  - D2: only 01 present: written.
  - D3 (076 order): lines I1, I2, then `I3 | FAIL | sent to audit: no`, then `--log I1` and `--log I2` with 05 and 06 present: both written.
  - D4: a `R3 | 5 verified, 0 fixed, 0 removed | BLOCKED` line, then `--log R1` with 02 and 03 present: written.
  - D5: `I1 | NOT A FIT | 0 files planned`, then `--log R1` with 02-04 present: written.
  - D6: 07 with `A1 result: FAIL (test)` and 05/06 present, then `--log I1`: written.
  - D7 (RI-012): an R3 line `... | READY (was BLOCKED)` and an I3 line `PASS | sent to audit: yes (FAIL fixed)` are not send-backs, so `--log R1` with 02 present is refused.
  - D8: 01 and 07 present (RESEARCH ONLY shape), `--log R3` with 03 present: written; 07 never counts.
  - D9 (change 6): item 998 with 01-06 present and item 999 with only 01: `--log R1 999` written.
  - D10: bad fields plus later files present: the existing format refusal text, unchanged (D runs after it).
- Mutations (I2 in a scratch worktree, never the repo; I3 re-runs): M1 `≥` -> `>` (N2 flag case fails); M1b drop `+1` (N3 fails); M2 ignore 06 (a fails); M3 drop the copy guard (N4 fails); M4 missing time read as 60 s (N5 fails); M5 remove D's later-file check (D1 fails); M6 remove `_sent_back` (D3-D6 fail); M6b R3 verdict from group 1 (D4 fails); M7 verdict by substring `"FAIL" in fields` (D7 fails); M8 add "048" to LOG_BATCH_EXCEPT (pin fails); M9 SUMMARY_LINE `.search` instead of `.match` (N8 fails); M10 skip malformed lines for C (N10 fails); M11 section ends only at `## ` (N7 fails).
- Checks: full `python3 -m pytest -q` passes; `python3.11 -m py_compile scripts/check_pipeline.py` if present (RI-008); 081's census test passes unchanged; `python3 scripts/check_pipeline.py` prints `LOG BATCH: none (not checked: 083: ...)` plus the not-computable list, and its exit code is unchanged by 086.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map step 1: `batch_log_items()` rule C, whole-item window, t05/t06, Σ − 0.005·k ≥ (Δ+1)×60, line text, exit 1 | Files 1: `batch_log_items`, `_item_lines`, `_run_seconds`, `BATCH_ROUND`, `main()` print + exit; fixtures (a), N1-N12 |
| Map step 1 Feasibility: 1 flagged (083) of 35, ≥ 4 not computable | Step 0 (iii) re-derives the counts with code; (b) pins 083 flagged; (c) pins none on HEAD with 083 excepted |
| Map step 2: `LOG_BATCH_EXCEPT = {"083"}`, separate dict, printed with reason | Files 1 constant; `test_log_batch_except_is_pinned`; (c); M8 |
| Map step 3: D in `write_log`, after the existing checks; send-back exception; message | Files 1: `write_log` addition, `_sent_back`, `SEND_BACK` (change 1: R3 group 2); D1-D10; M5, M6, M6b, M7 |
| Map step 3 Feasibility: 083 batch refused; 7 past send-back items exempt; existing `--log` tests unchanged | D1 (083 shape), D3 (076/061/062/077/079 shape: I3 FAIL), D6 (069/070 shape: A1 FAIL); D10 + full suite for the existing tests |
| Map step 4: tests (a), (b), (c), N1-N7, D1-D8 | All kept; N8-N12, D9, D10 added (changes 2-6) |
| Map step 5: mutations M1-M8 | M1-M8 kept; M6b, M9-M11 added |
| Map step 6: count stated in 05 by code (checked, flagged, excepted, not computable, in progress) | `batch_log_items` returns them; I2 pastes them (Expected result) |
| Map step 7: run-item L14 and L16 text; docstring entry | Files 3; Files 1 docstring |
| Map step 8: 05 guardrail line, no edit to recurring-issues.md, no 083 in LOG_TIME_EXCEPT, D needs no 083 exception | Expected result line; pin test asserts `"083" not in LOG_TIME_EXCEPT` |
| Fact check #7 (rounding margin, run-item order, whole-item window) | `BATCH_ROUND`; the docstring wording; change 7 adds the clock caveat |
| Fact check #10 (35 items; 37 if 081 and 084 are built first) | Expected result: 35 plus the items 080-086 that have I2 and I3 lines when I2 runs |
| Fact check #16 (files keep earlier rounds; whole-item window) | Window in `batch_log_items`; N7 (round 2 above round 1) |
| Fact check #20 removed (D's history count) | DROPPED: not replayable; D is tested by fixtures only |
| Fact check #23 / #39 (every Tests re-run section, largest, copies dropped) | `_run_seconds` + copy guard; N4, N7; change 4 adds level-1 heading bounds |
| Fact check #25 (079 numbers 90.93 + 90.21) | N1 uses them |
| Fact check #26 (M1 boundary 30.00/30.01, Δ1 45/45, M3 with 076 order) | N2, N3, D3 |
| Fact check #28 (050 tightest before 061) | Step 0 (iii) table |
| Fact check #40 (D off once any send-back verdict or A1 FAIL) | `_sent_back`; known gap (y) in the docstring |
| Fact check #41 (07 never a later file) | D8 |
| Missing inputs: time absent in 05/06/I2 line | k counts known values only; N5; M4 |
| Missing inputs: t06 equal to t05 | copy guard; N4; M3 |
| Missing inputs: no line before I2 | not computable `(no line before I2)`; covered by the `batch_log_items` branch (fixture: I2 as the item's first line, folded into N12's file) |
| Missing inputs: no I3 after I2 | in_progress; N12 |
| Missing inputs: 05/06 unreadable | `_run_seconds` reason; N11 |
| Missing inputs: malformed log line | C: counted by LOG_LINE (change 3, N10); D: not a send-back (D7) |
| Missing inputs: 07 absent | `_sent_back` reads log verdicts only; D2 |
| Missing inputs: step files absent | no refusal; D2; the request.md refusal unchanged (D10, `test_log_refuses_item_without_request`) |
| Request L13 rule (a) "previous step's line exists" | DROPPED: passes 083 (03 #18) |
| Request L13 rule (b) I2/I3 same minute + 30 s | DROPPED: not a proof (03 #9); C replaces it |
| Request L17 Done looks like (083 flagged, spaced none, past count stated) | (a), (b), N1, step 0 (iii), Expected result |

## Guardrail tests
- Feasibility: C window, 1 of 35 flagged on 2026-11-20 (083) → (b), plus (c) for the exception; I2 recomputes all 35 in step 0 (iii).
- Feasibility: C boundary, 30.00 + 30.01 at Δ0 → N2; Δ1 → N3.
- Feasibility: anchored summary filter, 3 test-ID lines in 076 (grep 2026-11-20) → N8, M9; I2 recounts in step 0 (i).
- Feasibility: copy guard, count from step 0 (ii) (0 allowed, it only lowers Σ) → N4.
- Feasibility: D refusal, 083's batch shape (5 later files) → D1; exception, 7 past send-back items in 3 shapes → D3, D4/D5, D6.
- Missing inputs: pytest time → N5; t06 copy → N4; line before I2 / I3 after I2 → N12; unreadable 05/06 → N11; malformed log line → N10, D7; 07 → D2/D6; step files → D2.

## Expected result
- 3 files changed (scripts/check_pipeline.py, tests/test_pipeline_check.py, .claude/commands/run-item.md).
- On this branch, `python3 scripts/check_pipeline.py` prints `LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048 (...), 055 (...), 056 (...), 058 (...)[, others as printed]`. The exit code is unchanged by 086.
- 05 states, from `batch_log_items()`: checked = 35 plus the items 080-086 that have both I2 and I3 lines at that moment; excepted 1 (083); flagged 0; not computable ≥ 4 (exact set printed); in progress as printed. With `excepted={}`: flagged exactly {083}.
- The full suite passes (count as printed by pytest: today's count plus about 26 new tests). M1-M11 each fail ≥ 1 named test.
- 05 guardrail line: `RI-010: guardrail built (086); GUARDED when merged, fixture (b) gives 083 flagged on main, and the next items have LOG BATCH: none`. D needs no 083 exception (write time only); say so in 05. Do not edit logs/recurring-issues.md, and do not add 083 to LOG_TIME_EXCEPT.

Log fields: FIT WITH CHANGES | 3 files planned

## Round 2
Fit verdict (round 2): FIT WITH CHANGES

Written 2026-11-21 UTC by I1 after I3's round-1 FAIL (work/086/06-verification.md, P1-P3 and "Sent back" points 1-4) and 05 Deviations 1-5. The round-1 text above is kept as written; where it differs from this section, **this section wins**. I1 again had no shell: no git, no pytest, no `check_pipeline.py`. Facts come from reading 05, 06, `scripts/check_pipeline.py` (docstring L105-126, `main()` L1553) and `tests/test_pipeline_check.py` (L411, L489, L2162, L2272, L2285, L2318-2343, L2945-3024) on daily-fixes/2026-11-20 at 416835f + the I3 FAIL files. The orchestrator writes the I1 log line: `python3 scripts/check_pipeline.py --log I1 086 "FIT WITH CHANGES | 2 files planned"`. Rule D allows it, because 086 now has an `I3 | FAIL` line (D3 shape).

Fit check (round 2): unchanged. Process only, no ccbot/config/data change, no rule the person follows changes, no brokerage. The round-2 changes are a print-format fix, test-number fixes and acceptance of I2's not-flag additions, so nothing new conflicts with 081, 084 or the scope lock.

### R2-1. Not-computable text format (I3 P1, point 1): option (a)
Decision: **(a)**. Each not-computable entry is printed as `<ID>: <reason>`, and entries are joined by `; `. This is the same shape as the `not checked:` part of the same line. Placement is unchanged (LOG BATCH stays directly after LOG TIME, so after INCOMPLETE), and **no existing assertion is edited**.

Why (a) and not (b) or (c):
- (b) moves the line in front of INCOMPLETE and away from LOG TIME, so it would break the "LOG BATCH directly after LOG TIME" rule and the one-line diff against HEAD's output that 05 showed.
- (c) weakens three existing guards (`"<ID> (" not in <everything after INCOMPLETE:>`) to cover only the INCOMPLETE line. Those guards exist to catch an INCOMPLETE entry printed anywhere later. Weakening tests to fit new output is the wrong direction.
- (a) is the shape the line already uses. I2's scratch probe of (a) found only N5's assert changes (05 Deviation 1).

Exact text, replacing round-1 Files 1 `main()` third bullet:
- plus `; not computable: <ID>: <reason>; <ID>: <reason>; ...` when `not_computable` is non-empty. In code: `"; not computable: " + "; ".join(f"{i}: {why}" for i, why in batch["not_computable"])`.

So the real-repo line becomes `LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048: no pytest time in 05/06/I2 line; 054: no pytest time in 05/06/I2 line; ...`.

I checked the other `split("INCOMPLETE:")` asserts against (a). L411 (040) and L489/L2285 (044, 040) are below LOG_CHECK_FROM = 45, so C never lists them. L2340 (183) asserts that text is present, and `"06 Verdict says" not in rest` holds, because no not-computable reason contains it. The only reasons are `no pytest time in 05/06/I2 line`, `no line before I2`, `log line with no valid time` and `<file> unreadable`, and none contains `(`. A flagged entry still prints `<ID> (` on purpose. None of the three fixtures has a time, so none can be flagged.

Files changed for R2-1:
- `scripts/check_pipeline.py`: the `main()` print (L1553), and the docstring L120 `as \`not computable: <ID> (<reason>)\`` changed to `as \`not computable: <ID>: <reason>\` (entries joined by "; ")`.
- `tests/test_pipeline_check.py`: N5's assert (L2952), which is 086's own new test, not an existing one. It becomes `"LOG BATCH: none; not computable: 999: no pytest time in 05/06/I2 line" in out.splitlines()`.
- New mutation **M12**: restore the round-1 format `f"{i} ({why})"`. Expect `test_old_06_without_round_headers_unchanged`, `test_i3_fail_target_not_stated`, `test_pass_without_sent_back_none_is_incomplete` and N5 to fail. That pins the format with the existing tests.

### R2-2. N2 and N3 values (I3 P2, point 2): I2's values adopted
Round-1 N2's non-flag case (30.00 + 30.00) and N3 (45.00 + 45.00) are replaced. The copy guard drops an equal 06 value, which made k = 1 in both. Re-derived against `round(t05 + t06 − 0.005·k, 3) ≥ (Δ+1)·60` with k = 2:
- **N2 (Δ0, limit 60):**
  - flag case: 05 30.00, 06 30.01, so 60.01 − 0.01 = 60.00 ≥ 60, flagged. This kills M1 (`>`: 60.00 > 60 is false).
  - non-flag case: 05 29.99, 06 30.01, so 60.00 − 0.01 = 59.99 < 60, not flagged.
  - The values differ by more than 0.01, so the copy guard keeps both (k = 2).
- **N3 (Δ1, I1 10:00, I2/I3 10:01, limit 120):** 05 45.00, 06 45.01, so 90.01 − 0.01 = 90.00 < 120, not flagged. M1b (limit Δ·60 = 60) flags it at 90.00 ≥ 60, which kills M1b.
- The round-1 Guardrail tests line "C boundary, 30.00 + 30.01 at Δ0 → N2; Δ1 → N3" stands with these numbers. Fact check #26's "Δ1 45/45" is replaced by 45.00/45.01, for the same copy-guard reason.

These are the numbers already built and pasted in 05 (M1 and M1b lines), so this is a plan change only and the code needs no rebuild for it.

### R2-3. I2's Deviation 3 (I3 P3, point 3): all five accepted
- **(i) Accepted.** `in_progress` = "no I3 line after the item's **last** I2 line". Round-1 Files 1 `batch_log_items` bullet 2 ("first I2 line and no later I3 line") is replaced by: "no I3 line after the last I2 line: `in_progress`". Reason: a round-2 I2 run logged after the last I3 would fall outside [start, last I3]. The window would then miss that I2 run's time, and the proof would not hold for it. The start rule is unchanged: the latest line before the **first** I2 line.
  - New test **N12b**: lines I1 10:00, I2 10:00, I3 10:00 FAIL, I2 10:30, with no later I3, gives `in_progress == ["999"]`, not flagged and not checked.
  - Mutation **M13**: key in_progress on the first I2. N12b then fails, because the item is evaluated.
- **(ii) Accepted.** An unreadable log file makes **every** item `not computable (<file> unreadable)`. The lines inside an unreadable file cannot be attributed to an item, so "items with lines of that date" is not knowable, and a lost line could move start or end. This is the not-flag side, and it is loud: every item is listed with the file named.
  - New test **N13**: two items with good 05/06 and spaced lines, plus a third log file of bytes `\xff\xfe`. Expect `flagged == []`, and both items in `not_computable` with a reason ending `<that file> unreadable`. No traceback, and `_run` exit 0 when nothing else is wrong.
  - Mutation **M14**: skip unreadable log files silently. N13 fails.
- **(iii) Accepted.** A LOG_LINE-shaped line with an impossible time (e.g. `25:00`, `10:61`) gives `not computable (log line with no valid time)` and never a crash. A silent skip would be wrong here: dropping the line could shorten the window (the round-1 change 3 reasoning).
  - New test **N14**: 083-shaped item 999 with one line `25:00 | I3 | 999 | PASS | sent to audit: yes`. Expect `not_computable == [("999", "log line with no valid time")]` and no traceback.
- **(iv) Accepted.** The flag test is `round(t05 + t06 − BATCH_ROUND·k, 3) >= limit`. The inputs have at most 2 decimals and BATCH_ROUND·k has 3, so the true value is exact at 3 decimals and the rounding removes only binary float error. The Python tutorial shows the same effect with `0.1 + 0.1 + 0.1 == 0.3` → `False`. [https://docs.python.org/3/tutorial/floatingpoint.html] The limit `(Δ+1)·60` is an integer and so exact. `round(x, 3)` of a value whose 3-decimal form is exactly 60.000 returns 60.0. The rounding therefore matters only at exact equality. There it settles the M1 boundary the way the docstring states it (≥).
  - Pin: I2 searches, by a scratch loop (never in the repo), for 2-decimal pairs a ≠ b with |a − b| > 0.01, a + b − 0.01 == 60.00 in decimal, and float `a + b - 0.01 < 60`. I2 states the count in 05.
  - If the count is ≥ 1, add the first pair as a third N2 case (flagged) and mutation **M15** (`round` removed), which that case must fail.
  - If the count is 0 at Δ0, repeat at limit 120 (Δ1, a + b − 0.01 == 120.00). If both counts are 0, write `M15: no below-limit pair exists (count 0 at 60 and 120); round() kept as harmless` in 05. No test is added then, and this is not a defect.
- **(v) Accepted.** `_item_lines` returns 6-tuples `(stamp, agent, team, file index, line index, fields)`. The fields are needed for the I2 seconds and are not used for start/end. This replaces round-1's 5-tuple signature.

### R2-4. Expected-result bar (I3 point 4): "no failure caused by 086"
Round-1 Expected result "The full suite passes" is replaced by the bar below. A failure is "not caused by 086" only when all three of these hold, and I2 shows each in 05 (I3 re-checks):
1. The same test ID also fails at the base commit (the commit before 086's code), run in a scratch worktree, never the repo.
2. It fails there for the same stated reason. Today the reason is `I3 FAIL: 081, 084` (exit 1) in `test_repo_pipeline_has_no_skipped_items`. That is the correct state of those items while their I3 rounds are open (item 071 rule).
3. No other test fails. On this branch today the allowed set is exactly {`test_repo_pipeline_has_no_skipped_items`}, and the 3 P1 tests must pass. Any other failure, or any of the 3 P1 tests failing, means FAIL.

The (c) assert sits after `code == 0`, so it does not run while that test fails. I2 therefore pastes the real `LOG BATCH:` line from `python3 scripts/check_pipeline.py` and shows that it contains `LOG BATCH: none (not checked: 083: six lines written in one batch`. When 081 and 084 reach a later PASS round, the test must pass with (c) included. A1 checks that on the next daily run.

### Round-2 build steps for I2
1. Change the `main()` print to format (a), and change docstring L120 (R2-1).
2. Change N5's assert (R2-1). Add N12b, N13 and N14 (R2-3 (i)-(iii)). Add the N2 third case only if the R2-3 (iv) search finds a pair.
3. Keep N2/N3 as built (R2-2). Leave every other test, the run-item.md text and the scope lock as built in round 1.
4. Re-run in this order:
   - the full suite: the only allowed failure is the R2-4 one, and the 3 P1 tests pass;
   - `-k "batch or log_"`;
   - M1-M11 and the new M12, M13, M14 (and M15 if added), each with its failing test named;
   - `python3.11 -m py_compile scripts/check_pipeline.py`;
   - `python3 scripts/check_pipeline.py`, with its LOG BATCH line pasted. That line must use format (a), and its exit code must be unchanged against HEAD's script on the same tree (one added line).
5. In 05, add a `## Round 2 build` section and keep round 1.

### Rule trace (round 2 additions)
| Source (I3 06 / 05 Deviation) | Plan line, or DROPPED: <reason> |
|---|---|
| 06 P1 / point 1, 05 Dev 1: not-computable format | R2-1 (a); `main()` + docstring L120; N5 assert; M12 pins it with the 3 existing tests |
| 06 P2 / point 2, 05 Dev 2: N2/N3 values | R2-2; N2 30.00+30.01 flag, 29.99+30.01 no flag; N3 45.00+45.01 < 120; M1, M1b |
| 06 P3 (i), 05 Dev 3 (i): in_progress on last I2 | R2-3 (i); N12b; M13 |
| 06 P3 (ii), 05 Dev 3 (ii): unreadable log file → every item not computable | R2-3 (ii); N13; M14 |
| 06 P3 (iii), 05 Dev 3 (iii): invalid HH:MM → not computable | R2-3 (iii); N14 |
| 06 P3 (iv), 05 Dev 3 (iv): `round(..., 3) >= limit` | R2-3 (iv); dated count by I2 search; N2 third case + M15, or the stated count 0 |
| 06 P3 (v), 05 Dev 3 (v): 6-tuple | R2-3 (v); signature text only, covered by N1-N14 |
| 06 point 4: "full suite passes" bar | R2-4 |
| 05 Dev 4: spaced control in (a) | Accepted as built (exit 1 shown to come from LOG BATCH) |
| 05 Dev 5: D needs no 083 exception | Accepted as built; round-1 Expected result already says so |

Missing-data policy (round 2): every not-computable branch now has an absent-case test. N5 covers k = 0, N11 an unreadable 05/06, N12 no line before I2, N12b an open round, N13 an unreadable log file and N14 an invalid time. None of them yields 0 s, 60 s or a flag (RI-002).

### Recurring issues checked (round 2, item 013)
- **RI-001 (ESCALATED):** the new N2/N3 numbers were re-derived against the copy guard and the flag test above. The R2-3 (iv) pair search has a dated count stated by I2, and 0 is allowed. Nothing is asserted as "always".
- **RI-010 (ESCALATED, this item):** unchanged. (b), D1 and the pin test stay. Format (a) keeps (c)'s text `LOG BATCH: none (not checked: 083: ...`, because only the not-computable part changes.
- **RI-014 (OPEN):** no git call is added in round 2 (census stays 46).
- **RI-002 (GUARDED):** see the missing-data policy line above. M4, M13 and M14 apply.
- **RI-004/RI-005 (GUARDED):** this round's own defect, N2/N3 not re-derived against the plan's own copy guard, is fixed in R2-2. Every number in this section was re-derived against `round(Σ − 0.005·k, 3) ≥ (Δ+1)·60` with k after the guard.
- **RI-012 (GUARDED):** unchanged (D7, N8, M7, M9).

### Expected result (round 2)
- 2 files changed in round 2 (`scripts/check_pipeline.py`, `tests/test_pipeline_check.py`). The round-1 total stays 3 files, because run-item.md is unchanged from round 1.
- The real-repo LOG BATCH line is in format (a), as in R2-1. The exit code is unchanged by 086.
- Full suite: meets the R2-4 bar. The 3 P1 tests pass. New cases are 29 (+ 1 if the R2-3 (iv) pair exists), against 26 in round 1.
- M1-M14 (and M15 if added) each fail ≥ 1 named test.
- The 05 guardrail line is unchanged from round 1.

Log fields (round 2): FIT WITH CHANGES | 2 files planned
