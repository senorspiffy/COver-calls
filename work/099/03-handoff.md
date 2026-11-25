# 03 Research hand-off - 099
Status: READY

R3 notes: no shell in this session (no Bash on R3's tools line), so nothing below was run. Each repo fact was checked by reading the cited line at HEAD of daily-fixes/2026-11-24-b (scripts/check_handoff.py, scripts/check_pipeline.py L582-609, tests/test_pipeline_check.py L3863-4119, logs/audit/2026-11-24-092.md, logs/recurring-issues.md, .claude/commands/run-item.md L17, work/092/02, logs/research/2026-11-24.md). I fetched all 6 external URLs and compared the quotes word for word. Every expected output is a code trace, so map step 1 makes I2 measure it before anything is pinned. All sources are in English, so there was no translation to check.

Recurring issues checked (item 013; open or ESCALATED entries: RI-001, RI-010, RI-014, plus the target RI-012):
- RI-001 (ESCALATED): this item adds no selecting rule. The only selectors are the mutant kill map and the fake-main cases, and every count is computed in the Feasibility column and the Self-check (e.g. A1-3 is visible in 4 of 4 single-item unreadable-03 runs and 0 of 3 `--all` bad runs; A1-2 in 0 of 7 real problem forms and 2 of 3 fake cases). Nothing says "always" without a count.
- RI-010 (ESCALATED): I typed no log line. The orchestrator writes the R3 line with `check_pipeline.py --log` after check_handoff, and the counts come from the script's `totals line`.
- RI-014 (OPEN): no new git read. In every fixture each work folder has a 03-handoff.md, so `_branch_with_handoff` and git are never called (L152-153). The fake-main test keeps that rule (map step 5). Clone depth cannot change any result here.
- RI-012 (GUARDED; this item is its "presence only" near miss): map step 5 is the embedded-pattern negative test at the call site (L166), not only on the constant.
- Also checked: RI-002 (stderr is never assumed empty; it gets a pin only if measured, see Missing inputs), RI-004/RI-005 (Self-check traces every expected line against the code path it shows), RI-006 (counts come from check_handoff, not from me).

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 T1: Pattern.search "Scan through string looking for the first location..."; Pattern.fullmatch "If the whole string matches..." | https://docs.python.org/3/library/re.html (fetched) | VERIFIED | |
| 01 T2: re.search "checks for a match anywhere in the string"; re.fullmatch "checks for entire string to be a match" | https://docs.python.org/3/library/re.html (fetched) | VERIFIED | |
| 01 T3: print signature has end='\n', so each print in check_handoff.py is one stdout line | https://docs.python.org/3/library/functions.html (fetched: default shown in the signature); check_handoff.py prints hold no embedded newline | VERIFIED | |
| 01 T4: list equality needs the same length and equal elements; a membership loop does not | https://docs.python.org/3/library/stdtypes.html (fetched, Common Sequence Operations) | VERIFIED | |
| 01 T5: redirect_stdout quote; check_all collects main's output with it (L160-163) | https://docs.python.org/3/library/contextlib.html (fetched); check_handoff.py L160-163 | VERIFIED | |
| 01 T6: monkeypatch.setattr quote and undo-after-test quote | https://docs.pytest.org/en/stable/how-to/monkeypatch.html (fetched) | VERIFIED | |
| 01 T7: readouterr namedtuple out/err; sys mode captures writes to sys.stdout/sys.stderr | https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html (fetched) | VERIFIED | |
| 01 Read first: Grep of logs/ for the 4 patterns finds only the 092 audit, RI file and 086's unrelated diff | Grep over logs/ (R3): 4 files, recurring-issues.md, audit 092, audit 086, audit 074 | WRONG | Also logs/audit/2026-11-18-074.md L7 ("paste its whole output" of probe_guardrails.py), which is unrelated to check_handoff. The conclusion stands: no earlier 01 covers this (Grep over work/*/01-research.md: only 099) |
| 01 Read first: RI-012 lists "check_handoff tests check presence only -> 099" as a near miss; RI-014 OPEN with 092 on PR #37 | logs/recurring-issues.md L140, L153 | VERIFIED | Note: the audit header (L3) records 092 on open PR #36 at audit time. Not load-bearing |
| 01 R1: check_all keeps only `FAIL: ` lines (L163), so under --all the A1-3 extra line is dropped; only single-item runs with an unreadable 03 can kill A1-3 | check_handoff.py L160-171 | VERIFIED | |
| 01 R2: under A1-3 the why03 path falls through to `text is None`, prints the false `no work/150/03-handoff.md; ...` line, then `_report`; exit code and FAIL line unchanged | check_handoff.py L95-101; check_pipeline.py L609; audit N1 L51-55 | VERIFIED | |
| 01 R3: every problem string main builds is fixed text (L106, L112, L117, L119, L122) or exactly `<path> unreadable (<detail>)` (L86, L96); LEGACY IDs fixed (L29-30); no file fixture separates .search from .fullmatch; N2's "covered by (e)" does not hold | check_handoff.py L29-30, L86, L96, L106-122; check_pipeline.py L606-609 | VERIFIED | |
| 01 R4: fake main patched on the module reaches check_all (global lookup at L162); a 03 file in tmp work/003 skips git (L152); expected .fullmatch vs .search outputs for the two negatives | check_handoff.py L152, L162-171; regex L33 traced (Self-check) | VERIFIED | Code trace; I2 measures it (map step 6) |
| 01 R5: R4 is the embedded-pattern negative test RI-012 asks for | logs/recurring-issues.md L140-142 | VERIFIED | |
| 01 R6: single runs `151` in (c) and `003` in (e) give `FAIL: work/<id>/03-handoff.md unreadable (not UTF-8 at byte 0)` / `1 problem(s)`, exit 1; main never consults LEGACY | check_handoff.py L75-124 (no LEGACY use) | VERIFIED | |
| 01 expected (a) bad and clean whole stdout | check_handoff.py L83-102; tests L3987-4005 | VERIFIED | Code trace; I2 measures (step 1) |
| 01 expected (b) bad (3 lines; under A1-3 the `no` line is inserted before FAIL) and clean (4 lines) | check_handoff.py L83-124; tests L4008-4019 | VERIFIED | Code trace; step 1 |
| 01 expected (c) bad --all, clean --all, clean single 150 | check_handoff.py L143-172; tests L4022-4036 | VERIFIED | Code trace; step 1 |
| 01 expected (d) bad 2 lines and clean 3 lines | check_handoff.py L93-124; check_pipeline.py L602-609; tests L4039-4047 | VERIFIED | Code trace; step 1 |
| 01 expected (e) bad --all and clean --all with 2 known problem(s) | check_handoff.py L104-124, L166-167; tests L4050-4061 | VERIFIED | Code trace; step 1 |
| 01 expected (f) bad --all and clean --all | check_handoff.py L83-91, L160-171; tests L4064-4074 | VERIFIED | Code trace; step 1 |
| 01: paths print with `/` (str(Path) on Linux; `_shown` uses as_posix, L590); the `no` line uses f"{handoff}" (L99) | check_pipeline.py L590; check_handoff.py L99 | VERIFIED | |
| 01: a Windows run would print differently | none (01 says not tested) | UNSUPPORTED | Removed: the suite runs on Linux, and nothing in the map depends on it |
| 01: stderr may be exactly empty on every fixture | none (01 says not run) | UNSUPPORTED | Kept only as a measure-first condition: pin `err == b""` only if step 1 measures b"" on all 15 runs; otherwise keep the Traceback check (Missing inputs) |
| 01: len("FAIL: ") == 6, hence l[6:] at L163 | check_handoff.py L163; audit L15 | VERIFIED | |
| 01: (e) clean LEGACY count is 2 (no Totals L112, no Self-check L122) | check_handoff.py L110-122; tests L4058 | VERIFIED | |
| 01: _h03 clean has 1 fact row and a matching Totals (1 = 1; 1+0+0 = 1) | tests L3972-3977; check_handoff.py L47-50, L110-119 | VERIFIED | |
| 01: BAD = b"\xff\xfe" fails at byte 0 | tests L3864; audit L14 (A1 measured start == 0) | VERIFIED | |
| 01: kill map: A1-3 by (b), (d), optional single runs in (c), (e); A1-2 only by the R4 test | derived from R1-R4 (rows above) | VERIFIED | Measured by I2 at step 6 |
| 01: no trading effect; check_handoff.py is not edited | request.md "Done looks like"; scope of change is tests only | VERIFIED | |
| 01: R1 and R3 counts come from this script | .claude/commands/run-item.md L17 | VERIFIED | |
| 02: audit Mutations table L38-47 and N1/N2 L51-58; A1-2 and A1-3 each "13 passed (survives)" | logs/audit/2026-11-24-092.md L38-58 | VERIFIED | |
| 02: R2 agrees with 01 R3 that N2's (e) remark does not hold | check_handoff.py L29-30, L86-122, L166 | VERIFIED | |
| 02: RI-012 root cause and GUARDED condition at L139-142; test_unreadable_problem_fullmatch_only (L4077-4085) pins the constant only | logs/recurring-issues.md L139-142; tests L4077-4085 | VERIFIED | |
| 02: RI-013 "nothing diffs the whole output" (L144-148) | logs/recurring-issues.md L146 | VERIFIED | |
| 02: RI-014 OPEN (L152-158); request calls 099 a near miss, not counted | logs/recurring-issues.md L153; request.md L14 | VERIFIED | |
| 02: 092 precedent: patch through module attribute at call time (work/092/02 L14, L23) | work/092/02-improvements.md L14, L23 | VERIFIED | |
| 02: an in-process import of check_handoff already exists (tests L4079-4080) | tests L4079-4080 | VERIFIED | |
| 02: R2 lines for 092-095, 097, 098 logged languages: N/A (L9-15) | logs/research/2026-11-24.md L9, L11-15 | VERIFIED | |
| 02 FOR 1: whole pins on (b), (d) and the new single runs kill A1-3; --all pins of (c), (e) do not | check_handoff.py L95-101, L163 | VERIFIED | |
| 02 FOR 1: (e) single expected `FAIL: work/003/03-handoff.md unreadable (not UTF-8 at byte 0)` / `1 problem(s)`, exit 1 | check_handoff.py L93-97, L67-72 | VERIFIED | |
| 02 FOR 2: fake main design (03 file present, monkeypatch, capsys, 2 negatives + positive control, expected 1 known problem) | check_handoff.py L152-171; T6, T7 | VERIFIED | |
| 02 FOR 3: keep an explicit `l.startswith("no ")` assert on (b), (d) and the new single runs | check_handoff.py L99, L171 | WRONG | The `startswith("no ")` form also hits `no new failures` (L171) if it is ever reused on an `--all` run. Use the request's exact form: no line fullmatches `no \S+; nothing else to check` (map step 4) |
| 02 AGAINST 1: "About 12 subprocess runs (6 fixtures, bad and clean, plus 2 new single runs)" | tests L3987-4074: (a) 2, (b) 2, (c) 3, (d) 2, (e) 2, (f) 2 runs | WRONG | 13 existing runs + 2 new = 15 (Self-check) |
| 02 AGAINST 1: a wording change to `_report`'s count line edits up to 8 lists | single-item runs that print a `_report` line: (a) bad, (b) bad/clean, (c) single clean, (d) bad/clean, new 151, new 003 = 8 | VERIFIED | |
| 02 AGAINST 2: fake main could pass vacuously after a refactor; mitigations positive control, call counter, comment | check_handoff.py L162-166 | VERIFIED | |
| 02 AGAINST 3: shared-file rule: items changing the same file are built one after another | .claude/commands/run-item.md L17 ("built (I2-I3) one after another, never in parallel (item 091)") | VERIFIED | |
| 02: suite timed 144.60 s in 092's audit | logs/audit/2026-11-24-092.md L28 | VERIFIED | |
| 02 Holes 4/5: a missing 03 triggers `_branch_with_handoff` (L152-153); main reads cwd-relative `Path("work")` (L76) | check_handoff.py L76, L152-153 | VERIFIED | |
| 02 Hole 9: check_handoff.py is RULE_PATHS, so `git diff -- scripts/` must be empty | logs/audit/2026-11-24-092.md L63 | VERIFIED | |
**Totals:** 50 rows checked → **45 VERIFIED as-is**, **4 fixed**, **1 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
- 01 L41: "a Windows run would differ (UNVERIFIED, not tested)". No source, not needed: the suite and the expected lists are Linux-only, and the map relies on nothing beyond as_posix / str(Path) on Linux.

## Implementation map
Type BUG. The prevention guardrail is steps 2-5, proven by step 6. Only tests/test_pipeline_check.py (092 block, L3963-4119) changes. scripts/ is not touched.

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 0 | Wait for the shared-file turn: 100-104 run on the same branch, and tests/test_pipeline_check.py is shared (run-item.md L17, item 091). Commit with `scripts/commit_step.py`. | run-item.md L17; `check_pipeline.py` OPEN BRANCHES | build starts only when no other item is mid-build on this file | 05 names the commit this build sits on and confirms no other item's uncommitted edit in the file | – |
| 1 | Measure first: at HEAD (tests not yet edited), I2 reproduces each of the 15 runs (13 existing: (a) 2, (b) 2, (c) 3, (d) 2, (e) 2, (f) 2; plus single `151` in (c) bad and `003` in (e) bad) and pastes whole stdout, exit code and stderr bytes in 05 | the fixture trees as built by tests L3987-4074 | 15 measured outputs | Each equals the Self-check expected list character for character. Any mismatch: stop, send back to R3 with the diff (reason EXPECTED OUTPUT MISMATCH), pin nothing | 15 of 15 runs listed (Self-check S1) |
| 2 | Add a strict helper `_exact3(code, out, err, want_code, lines)`: `b"Traceback" not in err`; `out.splitlines() == lines`; `code == want_code`; plus `err == b""` only if step 1 measured b"" on all 15 runs. Use it for every bad and clean run in (a)-(f) and delete `_ok3`, so no fixture can pick the weak form. Build the lines from shared constants (e.g. a `_unread(item, n, detail)` that returns `work/<item>/0<n>-....md unreadable (<detail>)`) | measured lists from step 1 | 13 runs whole-pinned | `grep -n "_ok3" tests/test_pipeline_check.py` gives no hits; suite passes | 13 of 13 existing runs pinned |
| 3 | Add the single-item runs `_run3h(bad, "151")` in (c) and `_run3h(bad, "003")` in (e), each whole-pinned: `["FAIL: work/<id>/03-handoff.md unreadable (not UTF-8 at byte 0)", "1 problem(s)"]`, exit 1 | the (c), (e) bad trees | 2 new pinned runs | pass at HEAD; fail under A1-3 (step 6) | 2 of 2 new runs |
| 4 | In (b), (d) and the two new single runs, assert that no line fullmatches `no \S+; nothing else to check` (the request's wording). Do not use `startswith("no ")`, which hits `no new failures` | the outputs of steps 2-3 | 4 explicit absent-claim asserts | each fails under A1-3 with a readable message (step 6) | 4 of 4 single-item unreadable-03 runs; (a) excluded because its 03 is really absent |
| 5 | New in-process test `test_check_all_unreadable_problem_call_site` (RI-012 call-site negative). In tmp_path, create `work/003/03-handoff.md` (any bytes) so L152 skips git. Import check_handoff via `sys.path`, then `monkeypatch.setattr(check_handoff, "main", fake)`. The fake counts its calls, prints one `FAIL: <problem>` line and returns 1. Run `check_all(tmp_path / "work")` and read `capsys.readouterr().out`. Parametrise 3 cases: (n1) `x unreadable (not UTF-8 at byte 0); y`, (n2) `see work/003/03-handoff.md unreadable (IsADirectoryError)`, (p) `work/003/03-handoff.md unreadable (not UTF-8 at byte 0)`. Comment names L162, L163, L166 | check_handoff module; tmp work/003 | n1, n2: return 0, out lines exactly `003: LEGACY (written 2026-10-30, before the Totals/Self-check template (commit 77273f0); 1 known problem(s))`, `no new failures`. p: return 1, `003: FAIL: work/003/03-handoff.md unreadable (not UTF-8 at byte 0)`, `FAIL on 003`. All 3: fake called exactly once | 3 cases pass at HEAD; under A1-2, n1 and n2 fail (step 6). A fake that is never reached fails p and the call counter | 2 of 3 cases separate .search from .fullmatch (Self-check S5) |
| 6 | Mutations in an I2 scratch worktree, one at a time, then restored: A1-3 (delete L97 `return _report(problems)`), A1-2 (`.search` for `.fullmatch` at L166). Re-run 092's M-a, M-b, M-f and A1-1 to show no test was weakened | `-k "handoff or unreadable_problem or check_all"` | failing test names per mutant in 05 | A1-3 fails at least test_handoff_bad_03, test_handoff_03_is_directory, test_handoff_all_one_bad_03, test_handoff_legacy_bad_03_is_fail. A1-2 fails test_check_all_unreadable_problem_call_site[n1] and [n2]. M-a/M-b/M-f/A1-1 still fail at least the tests in audit L40-43. Restored: all pass | A1-3: 4 of 4 kill sites; A1-2: 2 of 2 negatives |
| 7 | Show shipped output unchanged | base commit of the build | `git diff <base> -- scripts/` empty; full suite line; `python3 scripts/check_handoff.py --all` at base and head byte-identical (cmp) | all three in 05 | – |
| 8 | Write the kill map in 04/05 in these words, not the request's: A1-3 → (b), (d), single 151 in (c), single 003 in (e); A1-2 → the call-site test n1/n2 only; `--all` pins of (c), (e) kill neither mutant. The RI-012 guardrail note in 05 cites the call-site test | step 6 results | 05 kill-map section | the I3/A1 review matches it against step 6's output | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Measured whole stdout of the 15 runs (step 1) | not measured or differs from the Self-check lists | BLOCKED back to R3: `EXPECTED OUTPUT MISMATCH: <run> <diff>`. No list typed from 01 or 03 is pinned without the measurement |
| stderr bytes of the 15 runs (step 1/2) | not measured as exactly b"" on all 15 | no `err == b""` pin; keep `b"Traceback" not in err`. 05 says `stderr pin: n/a (not measured empty on all 15 runs)` |
| Fake main reached by check_all (step 5) | call counter not equal to 1 | the test fails (assert count == 1). It never passes as LEGACY by default |
| Base commit for the same-output check (step 7) | base not recorded | step 7 is `not checked (no base)` in 05, never "unchanged" |
| Ticker screen / MISSING_POLICY | not applicable: no ticker, price or trading input is read | n/a (test-only pipeline change) |

## Self-check
Every expected line below is traced through check_handoff.py at HEAD. No number was typed from 01 without that trace.

| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| S1 run count (step 1) | runs per fixture in tests L3987-4074 + new single runs | (a) 2 + (b) 2 + (c) 3 [bad --all, clean --all, clean 150] + (d) 2 + (e) 2 + (f) 2 = 13; 13 + 2 = 15 | 15 (02's "about 12" fixed) |
| S2 (b) bad exact list (step 2), A1-3 kill | lines = sources (01 good, 1 URL) + _report(1 problem) | `sources count (unique URLs in 01-research.md): 1`, `FAIL: work/150/03-handoff.md unreadable (not UTF-8 at byte 0)`, `1 problem(s)` = 3 lines. Under A1-3: L97 is gone, text is None, L99 adds `no work/150/03-handoff.md; nothing else to check` before `_report` → 4 lines; 4 ≠ 3 | killed |
| S3 (d) bad exact list | no 01 (missing_ok → no line) + _report(1) | `FAIL: work/150/03-handoff.md unreadable (IsADirectoryError)`, `1 problem(s)` = 2 lines; A1-3 → 3 lines | killed |
| S4 new single runs (step 3) | no 01 + _report(1); main has no LEGACY use (L75-124) | 151: `FAIL: work/151/03-handoff.md unreadable (not UTF-8 at byte 0)`, `1 problem(s)`; 003: the same with 003; 2 lines each, exit 1; A1-3 → 3 lines | killed (2 more sites) |
| S4b --all bad runs under A1-3 | check_all keeps only lines starting `FAIL: ` (L163) | (c), (e), (f) bad: the `no ...` line is dropped and code is still 1 → same stdout. 0 of 3 --all runs show A1-3 | as stated in step 8 |
| S5 n1 under .fullmatch / .search | L163 strips 6 chars: len("FAIL: ") = 4 letters + colon + space = 6 | problem `x unreadable (not UTF-8 at byte 0); y`. fullmatch: the pattern ends at `)` but the string continues `; y` → None → LEGACY with 1 known problem, return 0. search: `x unreadable (not UTF-8 at byte 0)` matches at 0 → FAIL, return 1 | n1 separates them |
| S5 n2 | regex `\S+ unreadable \((...)\)` | fullmatch: `\S+` must start at `s` and take `see`, but the next char is ` ` followed by `work`, not ` unreadable` → None. search: matches from `work/003/03-handoff.md` to the end → FAIL | n2 separates them |
| S5 p (positive control) | exact `<path> unreadable (<detail>)` | fullmatch and search both match → FAIL, `FAIL on 003`, return 1 | 0 of 1 separates (by design); fails if fake not reached |
| S5 LEGACY line text | f"{d.name}: LEGACY ({LEGACY[d.name]}; {len(problems)} known problem(s))" | `003: LEGACY (written 2026-10-30, before the Totals/Self-check template (commit 77273f0); 1 known problem(s))`; 1 = one FAIL line printed by the fake | matches step 5 |
| S6 A1-2 on real inputs | problem forms main can build under --all: L86, L96 (exact unreadable form), L106, L112, L117, L119, L122 (no "unreadable") | 7 forms; LEGACY paths `work/00[2-8]/0[13]-...md` have no space; detail `not UTF-8 at byte <n>` or class name. Forms where search ≠ fullmatch: 0 of 7 | no file fixture kills A1-2; step 5 needed |
| S7 (e) clean LEGACY count | L112 (no Totals) + L122 (no Self-check) | 1 + 1 = 2 → `003: LEGACY (...; 2 known problem(s))`, `no new failures`, exit 0 | as in 01 |
| S8 _h03 clean single run | fact_rows: rows[2:] of 3 `|` lines = 1; Totals in _h03 says total 1, 1 as-is, 0, 0 | 1 = 1; 1 + 0 + 0 = 1 → no problem → `fact-check rows: 1`, `totals line: 1 rows -> 1 as-is, 0 fixed, 0 removed`, `PASS` | as in 01 |
| S9 "up to 8 lists" (02 AGAINST 1) | single-item runs that reach `_report` | (a) bad, (b) bad, (b) clean, (c) clean 150, (d) bad, (d) clean, new 151, new 003 = 8; (a) clean returns 0 at L102 with no _report line | 8 |
| S10 step 4 absent-claim regex | `no \S+; nothing else to check` vs `no new failures` | `no new failures` has no `;` after one token → no fullmatch. `no work/150/03-handoff.md; nothing else to check` matches | safe on --all output too |
| S11 Fact-check totals | rows = VERIFIED + fixed + removed | 45 + 4 + 1 = 50; fixed rows: 01 Read-first grep, 01 stderr, 02 FOR 3, 02 AGAINST 1 = 4; removed: Windows = 1 | 50 |

`check_handoff output (run by the orchestrator 2026-11-24 23:26 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 6
fact-check rows: 50
totals line: 50 rows -> 45 as-is, 4 fixed, 1 removed
PASS
```
