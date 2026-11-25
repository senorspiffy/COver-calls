# 02 Improvements - 099
## What past logs say
- Source of the item: logs/audit/2026-11-24-092.md Mutations table (L38-47) and Findings N1/N2 (L51-58). A1-2 and A1-3 each give "13 passed | (survives)". N1 names the root cause: `_ok3` "only asserts that wanted lines are present ... never the whole output, so an extra false line passes."
- N2 adds: "Covered by the N1 guardrail if the (e) fixture pins whole output." R1 (01 R3) disputes this from the code. I agree after re-reading check_handoff.py:
  - L166 is reached only for a LEGACY ID (`002`-`008`, L29-30).
  - Every problem string `main` builds there is either fixed text without "unreadable" (L106, L112, L117, L119, L122) or exactly `<path> unreadable (<detail>)` (L86, L96).
  - So on every real input `.search` and `.fullmatch` give the same truth value, and no file fixture can kill A1-2. The request's guardrail sentence ("bad fixtures (b)-(e) compare the whole stdout ...; mutations ... each fail a named test") cannot be met for A1-2 by fixtures alone.
- logs/recurring-issues.md:
  - RI-012 (L139-142): root cause "tests only cover expected messages". GUARDED needs "its embedded-pattern negative test fails if the substring match is restored". Today that test (`test_unreadable_problem_fullmatch_only`, tests L4077-4085) pins the constant, not the call. A1-2 shows this gap.
  - RI-013 (L144-148) has the same shape in another area: "nothing diffs the whole output". This supports whole-output pins over line picks here.
  - RI-014 (L152-158) is OPEN. The request calls 099 a near miss, not counted.
- 092 precedent (work/092/02 L14, L23): monkeypatching a check_handoff collaborator works only through module-attribute lookup at call time. `check_all` calls `main(d.name)` as a module global (L162), so `monkeypatch.setattr(check_handoff, "main", fake)` reaches it. Reasoning from the code, UNVERIFIED until run. An in-process import of check_handoff already exists in the suite (tests L4079-4080).
- Languages precedent: 092-095, 097 and 098 (same checker family) all logged `languages: N/A` (logs/research/2026-11-24.md L9-15).

## 3 ways FOR
1. **Kill A1-3 where it can be seen, and say plainly where it cannot.**
   - Pin the whole stdout (`out.splitlines() == [...]`, list equality per 01 T4) on the single-item bad runs (b) `test_handoff_bad_03` and (d) `test_handoff_03_is_directory`. Use R1's expected lists (01 L36, L38).
   - Under A1-3, `no work/150/03-handoff.md; nothing else to check` is inserted before the FAIL line (01 R2). List equality fails on the extra element, so both tests fail by name.
   - Also add R6's single-item runs, `151` in (c) and `003` in (e), each with a whole pin. This gives four named kills instead of two.
   - (e) single expected output: `FAIL: work/003/03-handoff.md unreadable (not UTF-8 at byte 0)` / `1 problem(s)`, exit 1. `main` never consults LEGACY (L75-124).
   - Reasoning chain: under `--all`, L163 keeps only `FAIL: ` lines, so the false line never reaches stdout there (01 R1). A pin on the `--all` output of (c) and (e) is a guardrail for other regressions, not a kill for A1-3.
2. **Kill A1-2 at the call site with a fake `main` (01 R4). This is the missing RI-012 negative test.**
   - In tmp_path, create `work/003/03-handoff.md` (any bytes), so L152 `.exists()` is true and no git call happens.
   - `monkeypatch.setattr(check_handoff, "main", fake)`. The fake prints one crafted `FAIL: ` line and returns 1 (pytest monkeypatch, 01 T6). Read the output with `capsys.readouterr().out` (01 T7).
   - Parametrise over two negatives and one positive control:
     - `x unreadable (not UTF-8 at byte 0); y` (suffix);
     - `see work/003/03-handoff.md unreadable (IsADirectoryError)` (prefix with a space, so `\S+` under `.search` matches from `work/`);
     - exact `work/003/03-handoff.md unreadable (not UTF-8 at byte 0)` (must be FAIL under both forms).
   - Expected under `.fullmatch`, negatives: return 0, out lines exactly `003: LEGACY (written 2026-10-30, before the Totals/Self-check template (commit 77273f0); 1 known problem(s))` and `no new failures`. "1 known" because the fake prints one FAIL line.
   - Expected under `.search`: `003: FAIL: <line>`, `FAIL on 003`, return 1. Two named failing cases, so A1-2 is killed.
   - This is what moves RI-012 toward GUARDED: a negative test on the call, not only on the regex constant. Shipped code is not touched, so "shipped output unchanged" holds by construction.
3. **Use one strict helper for every fixture, plus a stderr pin if it is measured empty.**
   - Replace `_ok3(code, out, err, want_code, lines)` with an exact-match form: `assert out.splitlines() == lines, out`. Keep the `Traceback` assert and the exit-code assert. Apply it to (a)-(f), bad and clean runs alike (01 open question 2, first option).
   - Reasoning: one helper means a future fixture cannot pick the weak form by accident. (a) and (f) get pinned too. (a)'s correct `no ...` line becomes part of the exact list, so the request's "no such line" rule does not need a special case there.
   - Keep the explicit `assert not any(l.startswith("no ") ...)` only on (b), (d) and the new single runs. There it documents the A1-3 intent with a readable failure message. Under `--all` it is implied by the exact list.
   - If I2 measures stderr as exactly `b""` on every fixture, assert `err == b""`. That is stricter than "no Traceback" and costs nothing. UNVERIFIED (01 L42): measure it first.

## 3 ways AGAINST
1. **Exact pins are brittle and raise the cost of every later output change.**
   - About 12 subprocess runs (6 fixtures, bad and clean, plus 2 new single runs) will hard-code full output. Any later wording change in check_handoff.py, for example to the sources-count line (L87, L91) or `_report`'s count line (L71), must edit up to 8 lists in a test file shared with other items.
   - The expected lists in 01 are derived by reading code, not measured (01 open question 1). One wrong character makes a correct build fail. I2 must paste the real output before pinning and then confirm each pin by mutation. A list typed from 01 must not be trusted (RI-006 spirit: count by running, not by hand).
   - Mitigation: build each expected list from one shared constant per line kind, for example `UNREAD = "work/{id}/0{n}-....md unreadable (not UTF-8 at byte 0)"`. Then a wording change is a one-place edit.
2. **The fake-`main` test checks a contract, not behaviour that can happen today.**
   - By 01 R3, A1-2 cannot change any real `--all` result today. The test guards a future change: a new problem string that embeds the pattern, or a non-LEGACY use of the classifier. That is exactly RI-012's lesson, but a reviewer could fairly call it speculative.
   - The test is tied to two internals: that `check_all` calls the global `main`, and that it parses `FAIL: ` lines with `l[6:]`. A refactor (inlining `main`, passing problems back as a list) could make the fake bypass the code under test. The test would then pass vacuously or break for an unrelated reason.
   - Mitigations:
     - the positive-control row: the exact unreadable line must give FAIL, so a fake that is no longer reached shows up as a LEGACY result and the test fails;
     - assert that the fake was called once (a call counter);
     - put a comment on the test naming L162/L163/L166.
   - Alternative that touches shipped code, a classifier passed in as a parameter (01 open question 3), is ruled out by the request.
3. **Scope and process risk: the request overstates what fixtures (b)-(e) can prove, and the test file is shared.**
   - The request's guardrail text reads as if (c) and (e) whole-output pins kill both mutants. They kill neither: A1-3 is hidden under `--all` (01 R1), and A1-2 is unreachable from files (01 R3).
   - If 04/05 copy the request's wording, the RI-012 status note would claim a guard that does not exist. That is the RI-013 pattern (a reported effect from hand-picked fields). 04 must state the kill map: A1-3 → (b), (d), plus the new single runs in (c) and (e); A1-2 → the fake-`main` test only.
   - tests/test_pipeline_check.py is edited by other items on this branch (100-104 run in parallel). run-item.md L17 holds the shared-file rule (01 open question 5). Parallel edits to the same region (L3963-4119) risk a lost update. The build must take its turn.
   - Cost is small, under a minute of extra subprocess runs. 092's audit timed the suite at 144.60 s (logs/audit/2026-11-24-092.md L28).

## Findings by language
Random languages this cycle: N/A
Languages: N/A (no new external claims). 099 changes only this repo's own tests of scripts/check_handoff.py: assertion style, a monkeypatched fake, and expected output lines. It adds no fee, market rule, statistic or trading behaviour. The only outside facts (Python `re`, `print`, list equality, `contextlib.redirect_stdout`, pytest monkeypatch/capsys) are sourced by R1 from official English docs (01 T1-T7), the same as the 092 precedent (work/092/02 L67).

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | N/A (no new external claims; R1's T1-T7 cover the Python/pytest facts used) | | | |
| Mandarin Chinese | N/A | | | |
| Spanish | N/A | | | |
| Japanese | N/A | | | |

## Holes to watch out for (summary)
1. **`--all` hides A1-3.** L163 drops non-`FAIL: ` lines, so whole-output pins on the `--all` runs of (c) and (e) cannot kill it. Only single-item runs can: (b), (d), and the new `151` and `003` runs.
2. **No file fixture kills A1-2.** Do not record N2's "covered by (e)" as true. Use the fake-`main` test with a positive control and a call counter.
3. **"1 known problem(s)", not 2.** In the fake-`main` LEGACY line, the count is the number of FAIL lines the fake prints (1), unlike real fixture (e)'s clean run (2: no Totals, no Self-check).
4. **No git call.** The tmp `work/003/` must contain a `03-handoff.md`, or L152-153 calls `_branch_with_handoff` and real git.
5. **`main` reads cwd's `work/`, not the `work` argument.** L76 uses `Path("work")`. Real-`main` fixtures stay subprocess with `cwd=root`. Only the fake-`main` test may run in-process with `check_all(tmp_path / "work")`.
6. **Measure, then pin.** Every expected list in 01 is UNVERIFIED until I2 pastes real stdout. Run A1-2 and A1-3 one at a time after the change, and name the failing tests in 05.
7. **stderr.** Pin `err == b""` only if measured empty on every fixture. Otherwise keep the `Traceback` check.
8. **Shared file.** Wait for the shared-file turn (run-item.md L17) before editing tests L3963-4119, because 100-104 are on the same branch.
9. **Shipped code untouched.** `git diff -- scripts/` must be empty in 05. Otherwise "shipped output unchanged" is not shown, and RULE_PATHS approval applies.
10. **Kill map in 04/05.** Write it explicitly (A1-3 → named tests; A1-2 → the fake-`main` cases), so the RI-012 note is not copied from the request's wording.

Log fields: 3 for / 3 against | languages: N/A
