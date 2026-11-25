# 04 Build plan - 099
Fit verdict: FIT WITH CHANGES

Fit check. The ~$3k account, the strategy rules (001) and ccbot/ are not touched. The only file that changes is tests/test_pipeline_check.py, in its 092 block (`_run3h` through `test_handoff_read_census`). scripts/ and .claude/ stay as they are, so this needs no RULE_PATHS approval and no rule text the person follows changes (001: none; nothing to update or open). It does not conflict with built code: `_ok3` is used only inside the 092 block (Grep over tests/: 24 hits, all at L3980-4074), so deleting it breaks nothing else. Items 100-104 run on the same branch, and 100 (`_build_waived`) and others may edit the same test file. So 03 step 0 holds: the build waits for its turn, and every anchor below is a function name, never a line number. I1 has no shell, so nothing here was run. Every line count below is my own trace of scripts/check_handoff.py at HEAD, and it matches 03's Self-check S2-S10. I2's step 1 measurement is still the gate. There are four changes to 03:
- C1 (simpler helper). In place of 03's `_unread(item, n, detail)` (its file-name rule `0<n>-....md` is ambiguous), use `_unread(path, detail)`, which returns `f"{path} unreadable ({detail})"` with path as the posix relative string (e.g. `"work/150/03-handoff.md"`). It does one thing and has no name table.
- C2 (step 7 made exact). `check_handoff.py --all` reads `Path("work")` relative to cwd and imports check_pipeline from its own folder (`_pipeline`, `Path(__file__).resolve().parent`). "At base and head" therefore means: one cwd (the head repo root), and two script copies, base's (from a scratch worktree at the base commit) and head's. Run `python3 <base-wt>/scripts/check_handoff.py --all` and `python3 scripts/check_handoff.py --all` from the same cwd, then `cmp` stdout and compare the exit codes. This is the same method as 092's audit (logs/audit/2026-11-24-092.md L35-36). Running each at its own tree would compare different work/ folders, because 100-104 commit in between, and could show a false difference.
- C3 (step 5 made exact). Parametrize with explicit `ids=["n1", "n2", "p"]` so the step 6 names `test_check_all_unreadable_problem_call_site[n1]`/`[n2]` exist as written. Besides `count == 1`, the fake records its argument, and the test asserts it was called with `"003"`. Import with `sys.path.insert(0, str(REPO / "scripts"))` only if it is not already there, as `test_unreadable_problem_fullmatch_only` does. Monkeypatch undoes `main` after the test (pytest monkeypatch doc).
- C4 (keep the old extra asserts). The existing negative asserts (`not any(... "sources count ... \d+")` in (a), `not any(l.startswith("fact-check rows:"))` in (b), `not any(l.startswith("FAIL:"))` in (a) clean, `not any(l.startswith("sources count"))` in (c), `any(l.startswith("003: LEGACY ("))` in (e)) are implied by the whole pins but stay, so no assert is removed (I3 can check that the diff only adds asserts, apart from the `_ok3` → `_exact3` swap).

## Extra research (with sources)
1. `redirect_stdout`: "Context manager for temporarily redirecting `sys.stdout` to another file object ... It also has no effect on the output of subprocesses", and "This context manager is reentrant" ([contextlib](https://docs.python.org/3/library/contextlib.html), fetched 2026-11-24). Two points follow for step 5. (a) The fake main's `print` looks up `sys.stdout` when it is called, so inside `check_all` its line goes into the StringIO and is filtered by L163. capsys sees only check_all's own prints, which gives exactly the lines 03 expects. (b) The subprocess fixtures (a)-(f) are not affected by any in-process redirect, so the two kinds of test cannot leak into each other.
2. Check by trace (no shell): A1-2 cannot be killed by any file fixture. The problem strings main builds are fixed text (L106, L112, L117, L119) or `<path> unreadable (<detail>)` (L86, L96) with `path` = `work/00[2-8]/0[13]-....md` (no space). On those, `.search` and `.fullmatch` agree in 7 of 7 forms. The fake main is the only simple way. Patching `cp._UNREAD` to put a `;` in the detail would also work, but it depends on check_pipeline internals, so it is rejected.
3. Edge R3 left out: in (a) bad, the `no work/150/03-handoff.md; nothing else to check` line is true (03 is absent) and is printed before the FAIL line (L99, then `_report` at L101). The whole pin for (a) bad is therefore 4 lines in this order: the not-computed sources line, the `no` line, the FAIL line, `1 problem(s)`. The current `_ok3` list leaves out `1 problem(s)`. Step 4's absent-claim assert must skip (a), and 03 already says so.
4. Edge: under `-k "handoff or unreadable_problem or check_all"`, `test_handoff_read_census` (killed by M-a/M-b in audit L40-41) is still selected because its name contains "handoff". The re-run of 092's mutants is comparable to audit L40-43. `test_r1_log_refuses_not_computed` is not selected, and no 092 mutant is listed as killing it.

## Files to create/change
1. tests/test_pipeline_check.py (092 block only):
   - Add `_unread(path, detail)` (C1).
   - Add `_exact3(code, out, err, want_code, lines)`. It asserts `b"Traceback" not in err`, `out.splitlines() == lines` (message shows `out`), `code == want_code`, and `err == b""` only if I2's step 1 measured b"" on all 15 runs. Otherwise there is no err pin, and 05 says `stderr pin: n/a (not measured empty on all 15 runs)`.
   - Delete `_ok3`. Every call becomes `_exact3` with the measured whole list:
     - (a) bad: 4 lines (research 3). (a) clean: `sources count (unique URLs in 01-research.md): 1`, `no work/150/03-handoff.md; nothing else to check`.
     - (b) bad: 3 lines (S2). (b) clean: 4 lines (`sources count ...: 1`, `fact-check rows: 1`, `totals line: 1 rows -> 1 as-is, 0 fixed, 0 removed`, `PASS`).
     - (c) bad --all: 4 lines. (c) clean --all: 4 lines. (c) clean single 150: 3 lines (`fact-check rows: 1`, `totals line: ...`, `PASS`).
     - (d) bad: 2 lines. (d) clean: 3 lines.
     - (e) bad --all: 2 lines. (e) clean --all: the full LEGACY line with `2 known problem(s)`, then `no new failures`.
     - (f) bad --all: 2 lines. (f) clean --all: 2 lines.
   - New single runs: `_run3h(bad, "151")` in `test_handoff_all_one_bad_03` and `_run3h(bad, "003")` in `test_handoff_legacy_bad_03_is_fail`. Each is pinned to `[FAIL: work/<id>/03-handoff.md unreadable (not UTF-8 at byte 0), 1 problem(s)]` with exit 1.
   - The absent-claim assert `not any(re.fullmatch(r"no \S+; nothing else to check", l) for l in out.splitlines())`, with a message naming A1-3, on (b) bad, (d) bad, single 151 and single 003.
   - New `test_check_all_unreadable_problem_call_site(tmp_path, monkeypatch, capsys, problem, want_code, want_lines)` as in 03 step 5, plus C3. Its docstring names check_handoff's `check_all` lines `main(d.name)`, `l[6:]` and `UNREADABLE_PROBLEM.fullmatch` by text (L162, L163, L166 at HEAD).
   - Update the block's comment header with one line: item 099, whole-output pins, and the A1-2/A1-3 kill map.

05 (I2) and 06 (I3) are step files and are not counted. Files planned: 1.

## Tests and checks
- Step 1 (gate): I2 measures the 15 runs at HEAD before editing (13 existing + single 151 + single 003, using the (c)/(e) bad trees). For each run, 05 pastes the whole stdout, the exit code and the stderr bytes. Any difference from the lists above or 03's Self-check means stop and send back to R3 with `EXPECTED OUTPUT MISMATCH: <run> <diff>`.
- Steps 2-5: the edited and new tests above. `grep -n "_ok3" tests/test_pipeline_check.py` must give no hits.
- Step 6 mutations: scratch worktree, one at a time, restored, `-k "handoff or unreadable_problem or check_all"`.
  - A1-3 (delete `return _report(problems)` under `if why03:`) must fail at least test_handoff_bad_03, test_handoff_03_is_directory, test_handoff_all_one_bad_03 (single 151) and test_handoff_legacy_bad_03_is_fail (single 003).
  - A1-2 (`.search` for `.fullmatch` in check_all) must fail `test_check_all_unreadable_problem_call_site[n1]` and `[n2]`, and must not fail `[p]`.
  - M-a, M-b, M-f and A1-1 must still fail at least the tests in audit L40-43.
  - Restored: all pass. 05 lists the failing test names per mutant.
- Step 7: `git diff <base> -- scripts/ .claude/` is empty; the `--all` cmp as in C2; the full suite line `python3 -m pytest -q` pasted whole.
- Step 8: the kill map in 05 in 03's words: A1-3 → (b), (d), single 151 in (c), single 003 in (e); A1-2 → call-site n1/n2 only; the `--all` pins of (c), (e) kill neither.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 0 shared-file turn, commit_step | Fit check (wait for turn, anchors by name); I2 names the base commit in 05 |
| Step 1 measure 15 runs first, stop on mismatch | Tests and checks "Step 1 (gate)" |
| Step 2 strict helper, `_ok3` deleted, err pin only if measured, shared constants | Files 1 `_exact3`, `_unread` (C1), every call swapped; grep no hits |
| Step 3 single runs 151 and 003 | Files 1 "New single runs" |
| Step 4 absent-claim fullmatch on 4 runs, not `startswith("no ")` | Files 1 absent-claim assert; (a) excluded (research 3) |
| Step 5 call-site test n1, n2, p, fake count, git skipped | Files 1 new test + C3 (ids, called-with "003") |
| Step 6 mutations A1-3, A1-2, re-run M-a/M-b/M-f/A1-1 | Tests and checks "Step 6" |
| Step 7 shipped output unchanged | Tests and checks "Step 7"; C2 defines the cmp |
| Step 8 kill map wording | Tests and checks "Step 8" |
| Missing inputs: measured stdout absent or differs | Step 1 gate → BLOCKED back to R3 |
| Missing inputs: stderr not measured b"" on all 15 | `_exact3` err pin conditional; 05 `stderr pin: n/a (...)` |
| Missing inputs: fake main not reached | `count == 1` and called-with "003" asserts; p fails if not reached |
| Missing inputs: base commit not recorded | 05 says `not checked (no base)` for step 7 |
| Missing inputs: ticker screen / MISSING_POLICY | n/a: no ticker, price or trading input |
| Removed claim (Windows) | DROPPED: removed in 03; Linux-only suite |
| Self-check S1-S11 | S1 → step 1 (15 runs); S2-S4 → step 2/3 lists; S4b, S6 → step 8 kill map; S5 → call-site cases; S7, S8 → (e)/(c) clean pins; S9 → maintenance cost noted; S10 → absent-claim regex; S11 → 03 totals only |

## Guardrail tests
- Feasibility: the absent-claim selector (`no \S+; nothing else to check`) is visible in 4 of 4 single-item unreadable-03 runs under A1-3 and in 0 of 3 `--all` bad runs (S4b, traced). The pins are test_handoff_bad_03, test_handoff_03_is_directory, the single 151 run in test_handoff_all_one_bad_03, and the single 003 run in test_handoff_legacy_bad_03_is_fail.
- Feasibility: the `.search` vs `.fullmatch` separation shows in 0 of 7 real problem forms and in 2 of 3 fake cases (S5, S6). The pins are test_check_all_unreadable_problem_call_site[n1], [n2] and the positive control [p].
- Feasibility: the run count of 15 (S1) is pinned by I2's 05 measurement table, 15 rows.
- Missing inputs: fake main not reached → the call-site test fails on `count == 1` (it never passes as LEGACY by default).
- Missing inputs: stderr not measured empty → no `err == b""` pin; `b"Traceback" not in err` stays in `_exact3`.
- Missing inputs: base absent → step 7 is reported `not checked (no base)`, never "unchanged".

## Expected result
- The 6 existing 092 fixture tests pin the whole stdout of all 13 runs. The 2 new single runs and the new 3-case call-site test pass at HEAD. scripts/ is unchanged, and `check_handoff.py --all` output is byte-identical between base and head scripts.
- A1-3 now fails 4 named tests and A1-2 fails 2 named cases (it survived both before, audit L44-45). The 092 mutants still fail their tests.
- Suite: today's 821 passed, 1 skipped (092 audit; other items on the branch may change it) plus 3 new test cases (the call-site parametrization). The two new single runs sit inside existing tests. The exact line is pasted by I2.

Recurring issues checked (item 013):
- RI-001 (ESCALATED): there is no new selecting rule without a count. Each selector (absent-claim regex, fake cases, run count) has a traced count and a pinning test (Guardrail tests).
- RI-010 (ESCALATED): I typed no log line. The last line below is copied by the orchestrator into `--log I1`. I2 must paste the step 1 measurement and step 6 results as script output, not from this plan.
- RI-014 (OPEN): no git read is added. Every fixture folder has a 03, so `_branch_with_handoff` is never called, and the call-site test creates work/003/03-handoff.md for the same reason. Clone depth cannot change a result.
- GUARDED entries, also checked: RI-002 (stderr is not assumed empty, and the base is not assumed; Missing inputs); RI-004/005 (every expected list re-traced against check_handoff.py by me, and the (a) bad 4-line gap found, research 3); RI-006 (counts come from traces and I2's measurement, never typed totals); RI-007 (FULL scope, tests only); RI-009 (shared branch, built in turn); RI-012 (target: the call-site negative test); RI-013 (whole-output pins are this item's point; no realtest change); RI-003/RI-008 (no calendar change, and no new nested f-string quotes).

Log fields: FIT WITH CHANGES | 1 files planned
