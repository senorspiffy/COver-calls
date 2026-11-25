# 03 Research hand-off - 092
Status: READY

R3 read the working tree of daily-fixes/2026-11-24 on 2026-11-24 (no shell, item 072). The rules file was .claude/agents/r3-fact-checker.md, the branch copy. External sources were re-fetched on 2026-11-24: docs.python.org pathlib, codecs, exceptions, sys, tutorial/appendix, ast; rfc-editor.org RFC 3629. Each quote in 01 F1-F9 matches the live page. Repo claims were checked by reading each cited line. Type BUG, Scope FULL. Code changes are expected and run through I1-I3, so no 07 is written now (that is only for RESEARCH ONLY).

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 F1: read_text opens and closes the file, with params as in open(); read_bytes returns a bytes object | docs.python.org/3/library/pathlib.html (fetched) | VERIFIED | - |
| 01 F2: exists() is True for a directory, so a directory named 01/03 passes L54/L59 and then the read raises | pathlib docs "existing file or directory"; check_handoff.py L54, L59 | VERIFIED | - |
| 01 F3: 'strict' is the default and raises UnicodeError or a subclass. L55/L62 have no errors= | codecs docs error-handler table; check_handoff.py L55, L62 | VERIFIED | - |
| 01 F4: C0, C1, F5-FF never appear in UTF-8 | RFC 3629 s.1 (fetched) | VERIFIED | - |
| 01 F5: ValueError > UnicodeError > UnicodeDecodeError. FileNotFound/IsADirectory/Permission are under OSError | exceptions docs hierarchy (fetched) | VERIFIED | - |
| 01 F6: UnicodeError.start is the first index of invalid data | exceptions docs (fetched) | VERIFIED | - |
| 01 F7: an uncaught exception goes to sys.excepthook, which prints the traceback to stderr | sys docs (fetched) | VERIFIED | - |
| 01 F8: a script that fails exits nonzero after the stack trace. Errors go to stderr. No exit number is given | tutorial/appendix.html (fetched) | VERIFIED | - |
| 01 F9: Call.func is often Name or Attribute, and attr is a bare string. The census matches ast.Attribute | ast docs (fetched); tests/test_pipeline_check.py L3795-3802 | VERIFIED | - |
| 01 F10: 2 reads, both strict, both in main, no try. No read_bytes or open( | check_handoff.py L46-87 (full file read) | VERIFIED | - |
| 01 F11: the exception propagates out of main and check_all L125. --all stops, with no summary | check_handoff.py L123-135 | VERIFIED | - |
| 01 F12: exit 1 is both "problem found" and the observed crash code. _run returns only (code, stdout) | check_handoff.py L87; tests L63-66; logs/audit/2026-11-22-089.md L53-54 | VERIFIED | - |
| 01 F13: with no 03, L59-61 return 0 | check_handoff.py L58-61 | VERIFIED | - |
| 01 F14: unique_urls("") is [], which would print 0. The R1 log takes that number | check_handoff.py L42-43, L56; .claude/commands/run-item.md L17 | VERIFIED | - |
| 01 F15: --all keeps only the lines that start with "FAIL: " (l[6:]) | check_handoff.py L126 | VERIFIED | - |
| 01 F16: a nonzero main for 002-008 prints LEGACY and is not added to failed | check_handoff.py L19-22, L129-130 | VERIFIED | - |
| 01 F17: --all calls main only for folders that have a 03, so 01 is never read otherwise | check_handoff.py L114-122 | VERIFIED | - |
| 01 F18: main uses the cwd-relative Path("work"), not check_all's work argument | check_handoff.py L47, L107 | VERIFIED | - |
| 01 F19: _read returns (text, None) or (None, "<path> unreadable"). The detail (byte offset or class name) goes only into _UNREAD | check_pipeline.py L517-542; tests L3761-3784 | VERIFIED | - |
| 01 F20: a lazy import inside _branch_with_handoff; commit_step.py L43 says "as check_handoff does" | check_handoff.py L94-95; commit_step.py L43 | VERIFIED | - |
| 01 F21: _UNREAD is cleared only by cp.main (L1932) and printed at L2078 | check_pipeline.py L517, L1932, L2078-2079 | VERIFIED | - |
| 01 F22: open_branches reads the working-tree request.md through _read and drops why. Known gap at docstring L85-87 | check_pipeline.py L1508-1511, L85-87 | VERIFIED | - |
| 01 F23: docstring L360 says "Known gap: scripts/check_handoff.py still reads its files strictly." | check_pipeline.py L360 (the only hit in the repo outside work/092) | VERIFIED | - |
| 01 F24: scripts/check_handoff.py is in RULE_PATHS, so the person must OK it at PR review | check_pipeline.py L463; 089 audit L92 | VERIFIED | - |
| 01 F25: test_read_census parses only check_pipeline.py. A twin over check_handoff.py would catch a restored strict read | tests L3787-3809 | VERIFIED | Map picks 0 raw reads (re-use cp._read) |
| 01 F26: fixtures (a)-(d), each needing no Traceback, the named line and exit 1, plus a clean twin (089 6a pattern) | tests L3812-3824 | VERIFIED | - |
| 01 F27: "M-d ... only (c) catches this" | check_handoff.py L84-86, L126; fixture design | WRONG | (b), (d) and (e) also assert the exact `FAIL: ` line, so they kill M-d too. M-c is killed only by (a), which is correct |
| 01 Numbers: 2 raw reads today, 0 after (re-use) | check_handoff.py L55, L62 | VERIFIED | - |
| 01 Numbers: exit code alone cannot tell a crash from a found problem | F8, F12 | VERIFIED | - |
| 01 Q5: how the orchestrator parses the sources line is UNVERIFIED | run-item.md L17; check_pipeline.py L480, L720-732, L1116-1121 | UNSUPPORTED | Now sourced: the orchestrator copies R1's count from the `sources count` line (run-item L17). write_log refuses any fields that fail log_fields_ok, with exit 2 and nothing written (L1116-1121). So a "not computed" value can never be logged |
| 02: 089/02 AGAINST 3 and hole 9 asked for a follow-up | work/089/02-improvements.md L76-78, L107 | VERIFIED | - |
| 02: 089 audit 07 point 9 and N1 propose this item | 089 audit L93-96, L103-105 | VERIFIED | - |
| 02: the 089 design (read_bytes, strict decode, (OSError, UnicodeDecodeError), missing_ok; census pins 2) | 089 audit L20-23, L38; tests L3805-3809 | VERIFIED | - |
| 02: 089 mutations M3/M5/M7/M10/M13/M14 each fail a named test | 089 audit L77-85 | VERIFIED | - |
| 02: the unfixed crash exits 1 | 089 audit L53-54 | VERIFIED | - |
| 02: RI-014 is the family and RI-002 the shape | logs/recurring-issues.md L152-158, L24-26 | VERIFIED | - |
| 02: 092 is STUCK; the R1 log has `brief written` with 7 | logs/audit/2026-11-24.md L28; logs/research/2026-11-24.md L5. R3 counted the unique URLs in 01: pathlib, codecs, rfc3629, exceptions, sys, tutorial/appendix, ast = 7 | VERIFIED | - |
| 02: the h2 test patches open_branches on the module object | tests L2602-2614 (L2607 takes sys.modules["check_pipeline"]) | VERIFIED | - |
| 02: languages N/A precedent for checker BUG items | logs/research/2026-11-21.md L10; work/089/02 L86-87 | VERIFIED | - |
| 02 FOR 1: cp._read already has the agreed contract | check_pipeline.py L526-542 | VERIFIED | - |
| 02 FOR 1: missing_ok gives (None, None) for no file and (None, why) for a directory | check_pipeline.py L537-542; tests L3773-3779 | VERIFIED | - |
| 02 FOR 1: a cp.open_branches attribute call keeps the monkeypatch working; a module-level from-import would not | Python name binding; tests L2607-2612 | VERIFIED | - |
| 02 FOR 1: detail "use cp._UNREAD[shown] ... or have _read return it" | tests L3767-3784 pin _read's 2-tuple; check_pipeline has many _read callers | UNSUPPORTED | Pick one: index cp._UNREAD[cp._shown(path)] right after the call, with no .get default. Do not change _read's return |
| 02 FOR 2: an unreadable 03 goes into problems, so the FAIL: prefix reaches check_all L126 | check_handoff.py L84-87, L126 | VERIFIED | The map adds: return before section() is called, so no row or Totals result is computed from nothing |
| 02 FOR 2: an unreadable 01 is a problem too, and the no-03 branch returns 1 if problems | check_handoff.py L58-61 | VERIFIED | - |
| 02 FOR 2: pin with `cp.LOG_FORMAT["R1"]` must not fullmatch | check_pipeline.py L480, L732, L1116-1117 | UNSUPPORTED | It holds, but write_log does not test LOG_FORMAT directly. It calls log_fields_ok, so the pin is on `cp.log_fields_ok("R1", "092", ...)` returning False, with a twin `brief written \| 7` returning True |
| 02 FOR 2: LEGACY becomes FAIL "if any problem line contains ` unreadable (`" | logs/recurring-issues.md RI-012 (never classify by substring); check_pipeline.py L423-427 (fullmatch practice) | WRONG | Use a named constant UNREADABLE_PROBLEM with .fullmatch on each problem, plus a negative test (map step 4) |
| 02 FOR 2: LEGACY's reason covers the template, not an unreadable file | check_handoff.py L21 | VERIFIED | - |
| 02 FOR 3: census twin over check_handoff.py expects {} and total 0; cp._read (attr _read) is not counted | tests L3798-3801 walker | VERIFIED | The map adds a positive control (2 `_read` attribute calls in main), so an empty census cannot pass by walking nothing |
| 02 FOR 3: "Re-use `_run3` with cwd=tmp_path" | tests L3738-3742: _run3 hard-codes scripts/check_pipeline.py | WRONG | Add a new helper `_run3h(root, *args)` that runs check_handoff.py and returns (code, stdout decoded with replace, stderr bytes). Leave _run3 unchanged |
| 02 FOR 3: 089 added _run3 for the stderr assert | 089 audit L11 | VERIFIED | - |
| 02 FOR 3: fixtures (a)-(e), each with a clean twin and b"\xff" | 01 F4, F26; check_handoff.py L19-22 | VERIFIED | - |
| 02 FOR 3: "M-e, catch only OSError ... so only (a) kills it" | every bad-byte fixture raises UnicodeDecodeError under M-e; tests L3768-3771 | WRONG | M-e is killed by test_read_contract and by fixtures (a), (b), (c) and (e). It is a check_pipeline mutation that 089 already covers, and it is not on 092's mutation list |
| 02 FOR 3: M-f (LEGACY before the unreadable check) is killed by (e) | check_handoff.py L129-130 | VERIFIED | - |
| 02 AGAINST 1: a single-item run imports nothing from check_pipeline today | check_handoff.py L46-87 | VERIFIED | - |
| 02 AGAINST 1: open PRs #31-#36 and seven STUCK items (092-098) | logs/audit/2026-11-24.md L18, L28 | VERIFIED | - |
| 02 AGAINST 1: importing inside main keeps usage working | check_handoff.py L138-141 (usage exits before main) | VERIFIED | - |
| 02 AGAINST 2: --log refuses the non-number. run-item L17 and r1 L19 describe only the number case | run-item.md L17 ("its exit code does not gate R1"); r1-researcher.md L19 | VERIFIED | - |
| 02 AGAINST 2: "the item sits like 092-098 did" | logs/audit/2026-11-24.md L28: 092-098 were STUCK because the 11-22 run died, not because a runbook line was missing | UNSUPPORTED | Reworded: with no R1 log line the item would show INCOMPLETE/STUCK in check_pipeline until R1 is re-run. Known gap recorded in 04/05 (map step 8) |
| 02 AGAINST 2: the LEGACY 03 files were readable on ae2f8c7 (--all: no new failures) | logs/audit/2026-11-24.md L31 | VERIFIED | - |
| 02 AGAINST 3: work.iterdir()/is_dir() can still raise, so the claim must be limited to "no traceback on an unreadable 01 or 03" | check_handoff.py L114 | VERIFIED | - |
| 02 AGAINST 3: the suite takes about 82 s | 089 audit L41 | VERIFIED | - |
| 02 AGAINST 3: check_handoff docstring L2-12 must name the new lines | check_handoff.py L2-13 | VERIFIED | - |
**Totals:** 63 rows checked → **55 VERIFIED as-is**, **8 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None. The 8 WRONG/UNSUPPORTED claims are each corrected in the Fix column and in the map below.
## Implementation map
All code changes are in scripts/check_handoff.py, the scripts/check_pipeline.py docstring (L360 only) and tests/test_pipeline_check.py. Nothing changes in ccbot/, config/ or data/. Every f-string must parse on Python 3.10: no reuse of the same quote type inside `{}` (RI-008).

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | check_handoff.py (script): add `_pipeline()`. It does `sys.path.insert(0, <scripts dir>)`, then `import check_pipeline`, and returns the module. Call it at the start of `main` and in `_branch_with_handoff`, which then calls `cp.open_branches()` as an attribute (no `from check_pipeline import ...` anywhere). | check_pipeline module | `cp` | test_check_handoff_open_branches_states (h2) and test_all_names_branch_with_handoff pass unchanged. A grep for `from check_pipeline import` in check_handoff.py finds 0 hits. | – |
| 2 | main, 01 read: `text01, why01 = cp._read(research, missing_ok=True)` replaces L54-56. If why01: `p = f"{why01} ({cp._UNREAD[cp._shown(research)]})"`, print `sources count (unique URLs in 01-research.md): not computed (<p>)` and append p to problems. Else, if text01 is not None, print the count as today. unique_urls is never called on None or "". | work/<ID>/01-research.md | sources line or not-computed line, plus a problem | Fixture (a): work/150 has 01 = b"\xff" + a clean 01 and no 03. Run `_run3h(tmp, "150")`. Expect exit 1, no `Traceback` in stderr, the exact line `sources count (unique URLs in 01-research.md): not computed (work/150/01-research.md unreadable (not UTF-8 at byte 0))`, `FAIL: work/150/01-research.md unreadable (not UTF-8 at byte 0)`, and no line matching `sources count \(unique URLs in 01-research.md\): \d+`. Twin: the clean 01 alone gives exit 0 and `...: 1` (one URL in the fixture). | – |
| 3 | main, 03 read: `text, why03 = cp._read(handoff, missing_ok=True)` replaces L58-62. (None, None) prints `no <path>; nothing else to check`, then any FAIL lines and `<n> problem(s)`, and returns `1 if problems else 0`. why03 appends `f"{why03} (<detail>)"`, prints the FAIL lines and `<n> problem(s)`, and returns 1 before section() runs. | work/<ID>/03-handoff.md | `FAIL: <path> unreadable (<detail>)`, exit 1 | Fixture (b): good 01, 03 = b"\xff" + clean 03. Expect exit 1, no Traceback, `FAIL: work/150/03-handoff.md unreadable (not UTF-8 at byte 0)`, and no `fact-check rows:` line. Fixture (d): 03-handoff.md is a directory. Expect `FAIL: work/150/03-handoff.md unreadable (IsADirectoryError)`, exit 1, no Traceback. Twin: the clean 03 gives `PASS`, exit 0. | – |
| 4 | check_all (rule): add the module constant `UNREADABLE_PROBLEM = re.compile(r"\S+ unreadable \((?:not UTF-8 at byte \d+\|[A-Z]\w*Error)\)")`. The LEGACY branch runs only when `not any(UNREADABLE_PROBLEM.fullmatch(p) for p in problems)`. Otherwise the item is FAIL. Use fullmatch, never a substring (RI-012). | problems parsed at L126 | `<ID>: FAIL: ...` for LEGACY IDs too | Fixture (e): work/003/03 = b"\xff" + clean 03 under `--all`. Expect `003: FAIL: work/003/03-handoff.md unreadable (not UTF-8 at byte 0)`, `FAIL on 003`, exit 1. Twin: an old-style 003 with no Totals line gives `003: LEGACY (`, exit 0. Negative unit test: `UNREADABLE_PROBLEM.fullmatch("no Totals line ('...')")` and `.fullmatch("x unreadable (not UTF-8 at byte 0); y")` are both None. test_check_handoff_all_legacy_and_fail is unchanged. | Rule applies to 7 IDs (002-008, LEGACY L21-22). Fixture (e): 1 of 1 FAIL, twin 1 of 1 LEGACY. Real tree: 0 of 7 expected unreadable (A1 `--all` on ae2f8c7 gave "no new failures", logs/audit/2026-11-24.md L31). I2 re-runs `python3 scripts/check_handoff.py --all` and pastes the count into 05 |
| 5 | --all end to end (no code beyond steps 2-4): fixture (c) has work/150, 151 and 152, each with a 03, and 151's 03 is bad. | work/ tree | per-item lines and summary | Expect `150: PASS`, `151: FAIL: work/151/03-handoff.md unreadable (not UTF-8 at byte 0)`, `152: PASS`, `FAIL on 151`, exit 1, no Traceback. Twin: all three clean gives `no new failures`, exit 0. Every folder has a 03, so no git call is made. | – |
| 6 | tests (guardrail): add `_run3h`, fixtures (a)-(e) with their twins, and `test_handoff_read_census`. The census uses the test_read_census walker on scripts/check_handoff.py and asserts `dict(seen) == {}` and `sum == 0`. As a positive control, it also asserts that main has exactly 2 `ast.Attribute` calls with attr `_read`. Add `test_r1_log_refuses_not_computed`: `cp.log_fields_ok("R1", "092", "brief written \| not computed (work/092/01-research.md unreadable (not UTF-8 at byte 0))") is False` and `cp.log_fields_ok("R1", "092", "brief written \| 7") is True`. The expected census is computed by AST, never typed from a hand count (RI-006). | check_handoff.py source | new tests | Full suite green (I2 pastes pytest's line as printed). `python3.11 -m py_compile` on both scripts and the test file. | – |
| 7 | mutations (I2 runs, I3 re-runs, one at a time, restored after each) | the step 2-4 code | named failing tests | M-a (L55-style `research.read_text(encoding="utf-8")` restored): the census twin and (a) fail. M-b (03 strict read restored): census, (b), (c), (d) and (e) fail. M-c (no-03 branch `return 0`): (a) fails. M-d (unreadable problem printed without `FAIL: `): (b), (c), (d) and (e) fail. M-f (LEGACY check before UNREADABLE_PROBLEM): (e) fails. Each mutation must fail at least one named test. | – |
| 8 | docstrings and known gaps: check_handoff.py L2-12 names the not-computed sources line, `FAIL: <path> unreadable (<detail>)`, exit 1, the LEGACY exception and the dependence on check_pipeline importing cleanly. check_pipeline.py L360 "Known gap: ... still reads its files strictly" is replaced by the gaps that remain: --all never reads 01 of an item with no 03 (01 F17), and open_branches' unreadable request.md is silent in check_handoff (01 F22). Claim only "no traceback on an unreadable 01 or 03" (iterdir may still raise). 04/05 record: import coupling (02 AGAINST 1); the orchestrator gets exit 1 and a refused `--log R1` for an unreadable 01 and must re-run R1 or fix the file (no .claude/ edit in this item); both files are RULE_PATHS, so the person's OK is needed at PR review. | docstrings | text | A grep for `still reads its files strictly` in scripts/ finds 0 hits. 05 lists the gaps. | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| work/<ID>/01-research.md (step 2) | missing: no sources line, as today. Nothing is computed and no 0 is printed. Unreadable: no count | `sources count (unique URLs in 01-research.md): not computed (<path> unreadable (<detail>))` + `FAIL: <path> unreadable (<detail>)`, exit 1 |
| work/<ID>/03-handoff.md (step 3) | missing: `no <path>; nothing else to check`, exit 0 unless a 01 problem makes it 1. Unreadable: no rows, Totals or Self-check computed | `FAIL: <path> unreadable (<detail>)`, exit 1 |
| detail in cp._UNREAD (steps 2-3) | cannot be absent: _read writes it before returning a why (check_pipeline.py L539-542). It is indexed directly, never `.get(..., default)`. A KeyError would be a bug, and every fixture's no-Traceback assert catches it | n/a (no default) |
| check_pipeline module (step 1) | import fails, so check_handoff crashes for every item | known gap, recorded in 04/05 (02 AGAINST 1). Not defaulted |
| 01 of an item with no 03, under --all | not read (unchanged) | known gap in the check_pipeline docstring (step 8), 01 F17 |
| request.md read by open_branches under --all | an unreadable file is silent in check_handoff | known gap in the docstring (step 8), 01 F22 |

## Recurring issues checked (item 013)
- RI-001 (ESCALATED): step 4 is the only rule that selects items. Its count is written in the Feasibility column (7 IDs; fixture 1 of 1 each way). No other filter or window rule.
- RI-010 (ESCALATED): no log line was typed here. The check_handoff line is left for the orchestrator, and --log is run by it (item 045/072).
- RI-014 (OPEN): this item is in its family. The guardrail is the shared reader, the census twin and the no-Traceback fixtures (steps 2-7).
- Also checked (GUARDED, relevant): RI-002 (no number from an unread file, step 2 plus the log_fields_ok pin); RI-004/005 (Self-check below); RI-006 (the census is computed by AST, and Totals are counted from the table: 63 rows); RI-008 (3.10 f-strings, py_compile); RI-012 (fullmatch, not substring, in step 4, with a negative test).

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Census today vs after (step 6) | raw read_text/read_bytes/open calls by AST | today: L55 read_text + L62 read_text = 2, read_bytes 0, open 0. After: both become cp._read (attr `_read`, not counted) = 0. Positive control: `_read` calls in main = 01 + 03 = 2 | OK |
| Detail of a b"\xff"-prefixed fixture | UnicodeDecodeError.start of the first invalid byte | 0xFF never appears in UTF-8 (RFC 3629), so the decode fails at index 0, giving `not UTF-8 at byte 0`. Precedent: tests L3769-3771, BAD b"\xff\xfe" gives byte 0 | OK |
| Clean 03 twin gives PASS (step 3) | rows == Totals total and as-is + fixed + removed == total, with a Self-check heading | Fixture 03: header, `\|---\|`, one data row. fact_rows = rows[2:] minus separators = 1. Totals `1 rows checked → 1 VERIFIED as-is, 0 fixed, 0 removed`: 1 == 1, and 1 + 0 + 0 = 1. `## Self-check` present | PASS |
| check_all prefix strip (steps 3-5) | l[6:] for l starting "FAIL: " | len("FAIL: ") = 4 + 1 + 1 = 6, so `FAIL: work/151/03-handoff.md unreadable (not UTF-8 at byte 0)` becomes `work/151/03-handoff.md unreadable (not UTF-8 at byte 0)` | OK |
| UNREADABLE_PROBLEM on (e) (step 4) | fullmatch `\S+ unreadable \((not UTF-8 at byte \d+ or [A-Z]\w*Error)\)` | `work/003/03-handoff.md` is \S+, then ` unreadable (`, then `not UTF-8 at byte 0`, then `)` at the end: match, so FAIL. `IsADirectoryError` matches [A-Z]\w*Error. `no Totals line (...)` has no ` unreadable (`: no match, so LEGACY stays. `... byte 0); y`: trailing text, so no fullmatch | OK |
| LEGACY count (step 4) | len(LEGACY) | 002, 003, 004, 005, 006, 007, 008 = 7 | OK |
| (c) summary (step 5) | failed list from check_all | 150 PASS (code 0), 151 code 1 and not LEGACY, so failed = [151]; 152 PASS. Prints `FAIL on 151`, exit 1 | OK |
| R1 log refusal (step 6) | fullmatch `brief written \| \d+` | `brief written \| not computed (...)`: after `\| ` the next char is `n`, not a digit, so False and write_log returns 2 (L1116-1121). `brief written \| 7`: match, True | OK |
| Exit 1 is not proof | crash exit vs problem exit | both are 1 (089 audit L53-54; L87), so every fixture also asserts no `Traceback` in stderr bytes and the exact line, and has a clean twin at exit 0 | OK |
| 01 sources count | unique URLs in 01 (orchestrator's count) | pathlib, codecs, rfc3629, exceptions, sys, tutorial/appendix, ast = 7, which matches logs/research/2026-11-24.md L5 | OK |
| Totals of this file | rows in the Fact check table | 30 rows on 01 + 33 rows on 02 = 63; fixed 8 (01 F27, 01 Q5, FOR 1 detail, FOR 2 R1 pin, FOR 2 LEGACY substring, FOR 3 _run3, FOR 3 M-e, AGAINST 2 analogy); 55 + 8 + 0 = 63 | OK |
`check_handoff output (run by the orchestrator 2026-11-24 18:19 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 7
fact-check rows: 63
totals line: 63 rows -> 55 as-is, 8 fixed, 0 removed
PASS
```
