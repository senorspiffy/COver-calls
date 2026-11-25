# 03 Research hand-off - 089
Status: READY

R3 read the rules file .claude/agents/r3-fact-checker.md (no shell, item 072), request.md, 01, 02, logs/recurring-issues.md, scripts/check_pipeline.py, scripts/check_handoff.py, tests/test_pipeline_check.py, logs/audit/2026-11-21-086.md, logs/audit/2026-11-21-081.md, logs/audit/2026-11-19-079.md, work/081/02, work/081/03, work/086/02, work/086/05 and work/088, 090, 091 request.md. Every external URL in 01/02 was fetched on 2026-11-21 (python docs pathlib, io, codecs, exceptions, sys, functions, os, ast, tutorial appendix 3.12; RFC 3629; git-scm shallow, gitrepository-layout, git-rev-parse; PEP 538), and each quote matches. Line numbers are from this tree (daily-fixes/2026-11-21, before 088 is built). The build order is 088, then 089, then 090 and 091, so I1 re-finds every line by its text after 088 lands.

Decisions on R1's open questions (Q) and R2's options:
- Q1: R2's hybrid, corrected (rows 52, 53). There is one `UNREADABLE:` line with its own exit term. Each consumer whose answer depends on the lost text says `not checked (<file> unreadable)` instead of computing from "".
- Q2: in `_shallow_boundaries`, only a missing file (FileNotFoundError), or a failed `--git-common-dir`, keeps today's "full" when `sure` is False. Any other read failure (decode error, PermissionError, IsADirectoryError) gives "unreadable" whatever `sure` is. That failure also goes on the UNREADABLE line (R2 AGAINST 2 option A), so exit 1 no longer depends on git dying.
- Q3: globs stay as they are. Feasibility: 44 of 44 log files on this tree match both `*.md` and `????-??-??.md` (Glob 2026-11-21: 22 research + 22 implementation, 2026-10-30 to 2026-11-21, no 11-08; `.gitkeep` matches neither), so the real-repo file sets are the same.
- Q4: templates/daily-audit.md (L1478) uses the same reader.
- Q5: scripts/check_handoff.py L55/L62 are outside this item's code. The request says check_pipeline.py. I1 lists them in 05 as a follow-up for A1 to open today (step 9). They are not left silent.
- Q6: yes, but only on the UNREADABLE line: `not UTF-8 at byte N` (N = `err.start` on the whole file's bytes), or the OSError class name. File content is never printed.
- Q7: F20 is confirmed by reading the call order (L1532-1539: open_branches, research_code and real_data_field read no log file). Fixture 6e pins it with a run.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 1. 01 F1: read_text "The file is opened and then closed. The optional parameters have the same meaning as in open()" | https://docs.python.org/3/library/pathlib.html | VERIFIED | |
| 2. 01 F2: read_bytes returns "the binary contents of the pointed-to file as a bytes object" | https://docs.python.org/3/library/pathlib.html | VERIFIED | |
| 3. 01 F3: TextIOWrapper "Pass 'strict' to raise a ValueError exception if there is an encoding error (the default of None has the same effect)" | https://docs.python.org/3/library/io.html | VERIFIED | The sentence goes on with ", or pass 'ignore' ..."; the quoted part is exact |
| 4. 01 F4: 'strict' "Raise UnicodeError (or a subclass), this is the default." | https://docs.python.org/3/library/codecs.html | VERIFIED | |
| 5. 01 F5: 'replace' on decoding uses U+FFFD; 'surrogateescape' maps bytes to U+DC80-U+DCFF | https://docs.python.org/3/library/codecs.html | VERIFIED | |
| 6. 01 F6: "UTF-8 byte sequences have a structure that doesn't allow arbitrary byte sequences" | https://docs.python.org/3/library/codecs.html | VERIFIED | Part of a longer sentence ("However that's not possible with UTF-8, as ...") |
| 7. 01 F7: "The octet values C0, C1, F5 to FF never appear", so the bytes \xff\xfe and \xff never decode | https://www.rfc-editor.org/rfc/rfc3629 | VERIFIED | Section 1 |
| 8. 01 F8: ValueError > UnicodeError > UnicodeDecodeError; FileNotFoundError, IsADirectoryError, PermissionError under OSError | https://docs.python.org/3/library/exceptions.html | VERIFIED | |
| 9. 01 F9: UnicodeError attributes encoding/reason/object/start/end; "err.object[err.start:err.end] gives the particular invalid input" | https://docs.python.org/3/library/exceptions.html | VERIFIED | The page's own example decodes b"\xff" |
| 10. 01 F10: uncaught non-SystemExit exception, "the interpreter calls sys.excepthook", which "prints out a given traceback and exception to sys.stderr" | https://docs.python.org/3/library/sys.html | VERIFIED | |
| 11. 01 F11: input from a file, "exits with a nonzero exit status after printing the stack trace"; "All error messages are written to the standard error stream" | https://docs.python.org/3.12/tutorial/appendix.html | VERIFIED | |
| 12. 01 F12: the crash exits 1 (086 audit L54); `_run` returns only (returncode, stdout) (L62-65); test (c) checks stderr (L2484) | logs/audit/2026-11-21-086.md L54; tests/test_pipeline_check.py L62-65, L2484 | VERIFIED | |
| 13. 01 F13: shallow "lists commit object names ..."; "Each line contains exactly one object name." | https://git-scm.com/docs/shallow | VERIFIED | |
| 14. 01 F14: "This file is ignored if $GIT_COMMON_DIR is set and "$GIT_COMMON_DIR/shallow" will be used instead." | https://git-scm.com/docs/gitrepository-layout | VERIFIED | |
| 15. 01 F15: --is-shallow-repository and --git-common-dir texts; no word on a malformed file; A1 saw exit 128 | https://git-scm.com/docs/git-rev-parse; logs/audit/2026-11-21-081.md L12, L52 | VERIFIED | |
| 16. 01 F16: ast.Call func "will often be a Name or Attribute object"; Attribute.attr "a bare string giving the name of the attribute"; GIT_CENSUS walker matches ast.Name only | https://docs.python.org/3/library/ast.html; tests/test_pipeline_check.py L2423-2427 | VERIFIED | Walker test at L2425 |
| 17. 01 F17: 21 `.read_text(` calls, all `encoding="utf-8"` with no errors=; 5 caught, 16 not; no read_bytes; one `.open(` (write_log L825, append) | scripts/check_pipeline.py (Grep for read_text, read_bytes, open( on 2026-11-21) | VERIFIED | R3's Grep gives the same 21 lines; the only `errors=` in the file is `_git`'s subprocess call L1018 |
| 18. 01 F18: the 16 uncaught sites table (lines, functions, files) | scripts/check_pipeline.py L413-L1495 (Read) | VERIFIED | L551/L558 read work/<ID>/07 (STEPS["07"]); some sites are reached only on a branch (e.g. L551 only after a 06 FAIL) |
| 19. 01 F19: the 5 caught sites and their results | scripts/check_pipeline.py L781-784, L792-795, L888-892, L913-916, L1193-1198 | VERIFIED | |
| 20. 01 F20: with git, the first log read in main is uncommitted_steps → _log_text (L610), after open_branches, _walk, _anchor_env, untracked_changes, research_code, real_data_field | scripts/check_pipeline.py L1532-1539, L604-610 | VERIFIED | By code reading: none of the earlier calls reads logs/. Pinned by a run in step 6e |
| 21. 01 F21: _log_text globs `*.md`; _last_log_line, the I3 loop, orphan_log_lines, _sent_back, _item_lines glob `????-??-??.md` | scripts/check_pipeline.py L592, L672, L762, L835, L780, L886 | VERIFIED | R3 count: 44 of 44 log files match both globs today |
| 22. 01 F22: a lost file gives false `no log line for` (L700-704) or UNCOMMITTED STEP (L617-619); orphans silently hidden; classify has no status (crash) | scripts/check_pipeline.py L617-619, L700-704, L831-838, L525-527 | VERIFIED | |
| 23. 01 F23: main's exit expression (L1643-1645) has no term for an unreadable file | scripts/check_pipeline.py L1643-1645 | VERIFIED | |
| 24. 01 F24: the inbox path returns 1 early (L1639-1641), so an unreadable daily report "would need its own (text, True) result there" | scripts/check_pipeline.py L1637-1641 | WRONG | The early return is an unconditional `return 1`, so no new term is needed there. The UNREADABLE line must be printed before it (step 4). An unreadable daily report gives `INBOX: not checked (<name> unreadable)` with failed False, and the UNREADABLE term carries exit 1 |
| 25. 01 F25: sure False + decode error → "full" → _walk L1220 wrong reason, failed True | scripts/check_pipeline.py L1188-1198, L1213-1220; logs/audit/2026-11-21-081.md L103-104 | VERIFIED | |
| 26. 01 F26: "unreadable" in that case gives the not-checked tuple with failed False; exit 1 then comes from MAIN AHEAD / OPEN BRANCHES | scripts/check_pipeline.py L1218-1219, L1643; logs/audit/2026-11-21-081.md L42-43, L52 | VERIFIED | Under step 5 the UNREADABLE line also carries it |
| 27. 01 F27: _anchor_env maps "unreadable" to the shallow text, so RULE NOT SEEN changes in P2 | scripts/check_pipeline.py L623-632 | VERIFIED | |
| 28. 01 F28: sure False, missing file → "full" matches 079's docstring; PermissionError/IsADirectoryError also give "full" today | scripts/check_pipeline.py L1184-1198 | VERIFIED | |
| 29. 01 F29: test (c) asserts no Traceback, exit 1, no `: none`; the wrong-reason line passes all three | tests/test_pipeline_check.py L2476-2487 | VERIFIED | |
| 30. 01 F30: N13 writes b"\xff\xfe" to logs/implementation/2026-11-19.md and calls _bl, not the CLI | tests/test_pipeline_check.py L3060-3071, L2874-2876 | VERIFIED | |
| 31. 01 F31: GIT_CENSUS maps (function, callee) → (count, reason); exact equality plus pinned total 47 | tests/test_pipeline_check.py L2369-2432 | VERIFIED | |
| 32. 01 Numbers: 21 sites, 5 caught, 16 uncaught; 5 logs/ + 10 work/ + 1 templates/ = 16 | scripts/check_pipeline.py (Grep) | VERIFIED | Re-added by R3 |
| 33. 01 Numbers: 081/03 row 26 listed 10 sites plus L686 = 11 | work/081/03-handoff.md L42 | VERIFIED | |
| 34. 01 Fit: no trading effect (no ccbot/, config/, data/ or broker path) | request.md; scripts/check_pipeline.py | VERIFIED | |
| 35. 01 Fit: after a crash the later lines (ORPHAN LOG, INBOX, SKIPPED) never print | scripts/check_pipeline.py L1635-1642 | VERIFIED | |
| 36. Request evidence: 086/05 Deviation 1 (round 2) and the 086 audit finding 1 crash at 7eb51b0 and 129120b | work/086/05-build-report.md L412; logs/audit/2026-11-21-086.md L53-57 | VERIFIED | It is round 2's Deviation 1 (L412); round 1's Deviation 1 (L209) is a different issue |
| 37. Request evidence: 081 audit F3 cause (flag exits 128, sure False, decode error → "full") | logs/audit/2026-11-21-081.md L103-105 | VERIFIED | |
| 38. 02: 079 audit L38/L88, non-UTF-8 shallow crashed earlier, in `_git`; 081 fixed `_git` | logs/audit/2026-11-19-079.md L38, L88; scripts/check_pipeline.py L1017-1018 | VERIFIED | L88: "raised from subprocess inside _git" (L38 names its caller open_branches) |
| 39. 02: 081/02 AGAINST 1 (L63) kept F10 out; AGAINST 2 (L68) ORPHAN LOG still tracebacks | work/081/02-improvements.md L63, L68 | VERIFIED | |
| 40. 02: RI-014 (L152-158) is the family; RI-002 (L24-37) is the shape to avoid | logs/recurring-issues.md | VERIFIED | |
| 41. 02: X2 killed by test_shallow_file_unreadable_not_checked (079 audit L79); the sure-False branch was never pinned | logs/audit/2026-11-19-079.md L79; tests/test_pipeline_check.py L1619-1634, L2476-2487 | VERIFIED | |
| 42. 02: 086 LOG BATCH not_computable leaves the exit unchanged (L956-961, L1628-1629, L1643-1645) | scripts/check_pipeline.py | VERIFIED | |
| 43. 02: _sent_back's skip is the refusal side (docstring L776-777) | scripts/check_pipeline.py L773-796 | VERIFIED | |
| 44. 02: GIT_CENSUS shape; walker matches ast.Name only (L2425) | tests/test_pipeline_check.py L2369-2432 | VERIFIED | |
| 45. 02: PEP 538, stdout is strict outside the C locale and its coercion targets (via 081/02 L66) | https://peps.python.org/pep-0538/; work/081/02-improvements.md L66 | VERIFIED | PEP text: "For other locales, the default error handler for the standard streams is strict." |
| 46. 02: N13 L3071 asserts why.endswith(f"{bad.as_posix()} unreadable") | tests/test_pipeline_check.py L3071 | VERIFIED | |
| 47. 02: 088, 090, 091 all edit scripts/check_pipeline.py next to 089's lines | work/088, 090, 091 request.md | VERIFIED | |
| 48. 02: languages N/A precedent (081/02 L15, L89; 086/02 L54) | work/081/02-improvements.md L15, L89; work/086/02-improvements.md L54 | VERIFIED | |
| 49. 02 FOR 1: catch both OSError and UnicodeDecodeError; a directory matching `*.md` is an IsADirectoryError traceback today | https://docs.python.org/3/library/exceptions.html; scripts/check_pipeline.py L591-592 | VERIFIED | `_item_lines`'s `????-??-??.md` also matches a directory, but it already catches OSError |
| 50. 02 FOR 1: with read_bytes().decode("utf-8"), err.object is the whole file's bytes, so err.start is the file offset | https://docs.python.org/3/library/exceptions.html ("object: The object the codec was attempting to encode or decode") | VERIFIED | |
| 51. 02 FOR 1: with read_text, err.object is "whatever chunk TextIOWrapper hands the decoder" (UNVERIFIED by R2) | none | UNSUPPORTED | Removed. The map uses read_bytes, so nothing depends on it |
| 52. 02 FOR 1: one bad log file turns into "~90 misleading INCOMPLETE entries" | scripts/check_pipeline.py L307, L694-695; Glob work/*/request.md | WRONG | At most 51. `incomplete` returns [] below CHECKLIST_FROM = 41 (L307, L694), and there are 91 items, 001-091 (Glob, 2026-11-21): 91 − 40 = 51 (items 041-091) |
| 53. 02 FOR 1: the new `or unreadable` term joins L1643 "and the early-return path" | scripts/check_pipeline.py L1639-1641 | WRONG | The early return already returns 1 unconditionally. Only L1643 gets the term; the UNREADABLE line must print before L1639 (step 4) |
| 54. 02 FOR 1: ID CLASH is not in the exit expression | scripts/check_pipeline.py L1600-1601, L1643-1645 | VERIFIED | |
| 55. 02 FOR 2: read_request is called from classify (also on branch temp trees, L1141) and real_data_field (L1393) | scripts/check_pipeline.py L525, L1141, L1393 | VERIFIED | |
| 56. 02 FOR 3: a read census must match ast.Attribute calls with attr in {read_text, read_bytes, open} plus a builtin `open` Name | https://docs.python.org/3/library/ast.html | VERIFIED | |
| 57. 02 FOR 3: `_run` decodes stdout strictly (encoding="utf-8") and returns a 2-tuple many tests unpack | tests/test_pipeline_check.py L62-65 | VERIFIED | |
| 58. 02 FOR 3 mutation list: "drop it from the inbox early return" | scripts/check_pipeline.py L1639-1641 | WRONG | No such term can exist (row 53), so the mutation can't be killed. It is replaced by "UNREADABLE printed after the INBOX early return" (step 8, M6) |
| 59. 02 AGAINST 1: check_pipeline.py is in RULE_PATHS; the person's OK is needed at PR review | logs/audit/2026-11-21-086.md L12 | VERIFIED | |
| 60. 02 AGAINST 1: whole-output diff precedent (`98a99`) | logs/audit/2026-11-21-086.md L10 | VERIFIED | |
| 61. 02 AGAINST 2: git exits 128 on a bad shallow line; git docs say nothing about a malformed file | logs/audit/2026-11-21-081.md L12, L52; https://git-scm.com/docs/git-rev-parse | VERIFIED | P1 (L47) shows `--git-common-dir` still works with a bad file (the malformed text was read) |
| 62. 02 AGAINST 2 option A: routing a shallow read failure into UNREADABLE makes it exit 1 on its own | scripts/check_pipeline.py L1643-1645 (after step 4) | VERIFIED | Adopted (step 5) |
| 63. 02 AGAINST 3: scripts/check_handoff.py L55 and L62 read 01/03 strictly | scripts/check_handoff.py L55, L62 | VERIFIED | Follow-up, step 9 |
| 64. 02 AGAINST 3: the suite already runs about 88 s | logs/audit/2026-11-21-086.md L31 (87.57s) | VERIFIED | |
| 65. 02 AGAINST 3: tests call cp.main several times in one process | tests/test_pipeline_check.py L2443, L2449 | VERIFIED | |
| 66. 02 languages table: os docs, surrogateescape for file names, "undecodable bytes are replaced by a Unicode character U+DCxx on decoding" | https://docs.python.org/3/library/os.html | VERIFIED | |
| 67. 02 languages table: 'surrogatepass' quote, "Otherwise these codecs treat the presence of surrogate code point in str as an error." | https://docs.python.org/3/library/codecs.html | VERIFIED | |
| 68. 02 languages table: open() newline None, universal newlines, "translated into '\n'" | https://docs.python.org/3/library/functions.html | VERIFIED | |
| 69. 02 hole 4: the newline risk is in "re.M `$` patterns (e.g. LOG_LINE on joined text)" | scripts/check_pipeline.py L400, L465, L673, L706, L715, L763, L836 | WRONG | LOG_LINE is only applied to splitlines() rows, never to joined text. Every reader strips or splitlines, so CRLF changes no verdict found by R3. The real risk is a lone `\r`: read_text turns it into `\n`, and `_a1_results` (`^A1 result:`, re.M, L465) then matches; raw decode would not. Step 1 normalises, and fixture 6h kills the mutation |
| 70. 02 hole 2: a non-UTF-8 file name becomes a U+DCxx str, and printing it to strict stdout raises UnicodeEncodeError | https://docs.python.org/3/library/os.html; https://docs.python.org/3/library/codecs.html; https://peps.python.org/pep-0538/ | VERIFIED | Under C.UTF-8 (a coercion target) stdout uses surrogateescape, so the crash depends on the locale; step 1 renders with backslashreplace either way |
**Totals:** 70 rows checked → **64 VERIFIED as-is**, **5 fixed**, **1 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
- Row 51: R2's own UNVERIFIED reasoning that read_text's decode error object is "whatever chunk TextIOWrapper hands the decoder". There is no source for it, and nothing in the map needs it.

## Implementation map
Build after 088 is committed on this branch. Re-find each line below by its text, not its number. Scope: scripts/check_pipeline.py and tests/test_pipeline_check.py only. check_handoff.py is step 9 (a follow-up). RULE_PATHS change: the person's OK is needed at PR review. Prevention guardrail (BUG): steps 1, 4 and 7 (one reader, one exit term, and a read census that fails on any new raw read), plus the end-to-end fixtures and mutations in steps 6 and 8.

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | Script: add `_read(path, missing_ok=False) -> (text, why)`. It reads `path.read_bytes()`, decodes with `.decode("utf-8")`, then normalises newlines with `.replace("\r\n", "\n").replace("\r", "\n")` (the same as read_text's universal newlines, row 68). It catches `(OSError, UnicodeDecodeError)`. On success it gives (text, None). With missing_ok and FileNotFoundError it gives (None, None) and records nothing. Any other failure gives (None, f"{path.as_posix()} unreadable") (086's exact text, so N13 L3071 holds) and records `_UNREAD[path.as_posix()] = detail`. The detail is `not UTF-8 at byte {err.start}` for a decode error, else `type(err).__name__` (never errno text, never file content). The rendered path uses `.encode("utf-8", "backslashreplace").decode("utf-8")` (row 70). `_UNREAD` is a module dict, cleared by main (step 4); it holds reasons only, never file text (02 hole 10). | a file path | (text, why); one `_UNREAD` entry per failed path | Unit test `test_read_contract`: a valid file gives (text, None); b"\xff\xfe" gives (None, "<p> unreadable") with detail `not UTF-8 at byte 0`; a directory gives detail `IsADirectoryError`; missing + missing_ok gives (None, None) with `_UNREAD` unchanged; b"a\rb\r\nc" gives "a\nb\nc" | – |
| 2 | Script: route all 21 read_text sites through `_read`. The per-site results are in the table below. Remove the 5 local try/excepts, keeping their result (`_sent_back` still skips; `_item_lines`/`_run_seconds` keep `<file> unreadable`). `read_request` takes the text (or classify reads it once and parses it, so L413 and L527 become one read). Add `_i3_verdict_text(text)`. `i3_verdict(path)` stays, as a wrapper that returns (None, None) when `_read` fails (its docstring; the tests at L2317/L2323 call it). `_log_text(logs)` returns (text, [why...]). Globs stay unchanged (Q3). | the 21 sites (row 17) | the same verdicts on readable files; `not checked (... unreadable)` text on unreadable ones | Read census (step 7) plus fixtures 6a-6j. Whole-output diff (step 10) | 21 of 21 read_text sites today (Grep 2026-11-21, L413-L1495); after the build, 0 outside `_read`. I1 recounts by AST after 088 |
| 3 | Script, consumers: never compute from "". (i) `uncommitted_steps`: if `_log_text` gave whys, return (f"not checked ({'; '.join(whys)}; item 089)", False). (ii) `incomplete`: for an item with at least one step file 01-06 and an unreadable log, one entry `log lines not checked (<whys>; item 089)` replaces the unlogged check, the format check, the Suite check's log read and the I3-line comparison. 06 unreadable: `06 not checked (<why>; item 089)` replaces the RI line, verdict and I3 checks. 05 unreadable at the Suite check: `05 not checked (<why>; item 089)`. (iii) `orphan_log_lines` returns (orphans, whys); the ORPHAN LOG line prints the orphans or `none`, then `; not checked: <whys>` when there are whys. It is never a bare `none` when a file was lost (RI-002). (iv) `classify`: request.md, 06 or 07 unreadable gives status `UNREADABLE`, detail `<why>`. (v) `real_data_field`: request/05/06 unreadable adds gap `<step> not checked (<why>; item 089)`. (vi) `research_code.request_text_of`: unreadable gives flag `RESEARCH ONLY check: <why> (item 089)` (strict). (vii) `open_branches` L1125: unreadable `mine` means no clash compare (recorded in `_UNREAD`). (viii) `inbox_section` L1495: (f"not checked ({newest.name} unreadable)", False). (ix) `_inbox_gate` L1478: (f"not checked ({path.name} not committed; its {INBOX_TEMPLATE} unreadable)", False) | `_read` whys | not-checked texts | Fixture 6e (an item with step files and a bad log gives an INCOMPLETE entry with `log lines not checked` and no `no log line for`); 6a (ORPHAN LOG not a bare `none`); 6d (`150: UNREADABLE`) | Upper bound for (ii): 51 items (041-091) can get an entry; see Self-check |
| 4 | Script, main: `_UNREAD.clear()` is the first statement of `main()`. After `inbox, inbox_bad = inbox_section()` and before printing INBOX, print `UNREADABLE: ` followed by `", ".join(f"{p} ({d})" for p, d in sorted(_UNREAD.items()))`, or `none`. Set `unreadable = bool(_UNREAD)`. Add `or unreadable` to the L1643 exit expression only (rows 53, 58). | `_UNREAD` | one new line between ORPHAN LOG and INBOX; exit term | 6a: the bad twin exits 1 and the clean twin exits 0. 6i: main twice in one process (bad, then fixed) gives `UNREADABLE: none` and exit 0 the second time. 6j: with `inbox_section` monkeypatched to ("x", True) and a bad log, the UNREADABLE line is still printed | – |
| 5 | Script, `_shallow_boundaries`: read through `_read(p, missing_ok=True)`. Results: text None and why None (missing file) → "unreadable" if sure else "full" (unchanged, 079). why set → "unreadable" whatever `sure` is (it is recorded in `_UNREAD`). A failed `--git-common-dir` keeps today's `raise`/"full" path (not a read). The malformed-line rule (SHALLOW_LINE) is unchanged and is not an UNREADABLE entry. GIT_CENSUS is unchanged: 089 adds no git call. | flag, `--git-common-dir`, the shallow file | "unreadable" for any existing unreadable file | Test (c) gains three asserts: `UNTRACKED CHANGE: not checked (shallow clone; run git fetch --unshallow)`; an UNREADABLE line containing `shallow (not UTF-8 at byte 41)`; `RULE NOT SEEN: not checked (shallow clone; run git fetch --unshallow)`. test_shallow_file_unreadable_not_checked (L1619) still passes unedited | – |
| 6 | Tests: add a helper `_run3(root, *args) -> (code, stdout, stderr)` (stdout decoded with "replace"; `_run` unchanged). Each fixture asserts no `Traceback` in stderr. 6a, log bad byte, no git, isolated (see Self-check): the tree is work/150/request.md only (FULL, Date = --today) plus logs/implementation/2026-11-19.md. The clean twin (`# Implementation log\n`) gives exit 0 and `UNREADABLE: none`. The bad twin (b"\xff\xfe") gives exit 1, `UNREADABLE: logs/implementation/2026-11-19.md (not UTF-8 at byte 0)`, and an ORPHAN LOG line that is not `none`. 6b: the same tree with a directory named 2026-11-19.md gives `(IsADirectoryError)` and exit 1. 6c, step file: work/150/06-verification.md = b"# 06\n\xff" (incomplete reads 06 whenever it exists, L697-698) gives `UNREADABLE: work/150/06-verification.md (not UTF-8 at byte 5)` and exit 1. 6d: request.md = b"Scope: FULL\n\xff" gives `150: UNREADABLE (work/150/request.md unreadable)`, `(not UTF-8 at byte 12)` and exit 1. 6e, git present (NO_GIT mark): an item with 01 uncommitted and a bad log gives `UNCOMMITTED STEP: not checked (logs/implementation/2026-11-19.md unreadable; item 089)` and no `no log line for` in INCOMPLETE. 6f: N13's CLI twin through `_run3`. 6h, CR fixture: a complete item whose 07 is "# 07\rA1 result: PASS\r" gives `complete` (today's read_text result). 6i, 6j: see step 4. | tmp trees | named tests | Each test fails on its mutation (step 8) and passes on the build | Bad twins 6a, 6b and 6d are checked against a clean twin that exits 0; see Self-check |
| 7 | Tests: `test_read_census`, the same shape as GIT_CENSUS. An AST walk over scripts/check_pipeline.py counts, by innermost function, each `ast.Call` whose func is an `ast.Attribute` with attr in {read_text, read_bytes, open}, or an `ast.Name` `open`. Expected: `{("_read", "read_bytes"): 1, ("write_log", "open"): 1}`, each with a reason (`the reader`; `append write, item 045`), and the total pinned to 2. | script AST | census pass/fail | A raw read_text in any function fails it (M5) | Today's tree gives 21 read_text + 1 open = 22 calls (Grep), so the test fails before the build and passes after |
| 8 | Mutations, each run on a scratch copy and each failing a named test. M1: `_read` catches only OSError → 6a (Traceback). M2: catches only UnicodeDecodeError → 6b. M3: `or unreadable` dropped from L1643 → the 6a bad twin exits 0. M4: `_UNREAD.clear()` dropped → 6i. M5: one site back to a raw read_text → census. M6: UNREADABLE printed after the INBOX early return → 6j. M7: `_shallow_boundaries` back to `"unreadable" if sure else "full"` on a read failure → the test (c) text. M8: shallow failure not recorded → the test (c) UNREADABLE assert. M9: orphan_log_lines drops its whys → the 6a ORPHAN LOG assert. M10: incomplete computes from "" → 6e. M11: newline normalisation dropped → 6h and test_read_contract. M12: `why` text changed → N13 L3071. | scratch copies | failing test names in 05 | I2 lists each mutation with its failing test; I3 re-runs them | – |
| 9 | Process note (no code here): I1 writes in 05 that scripts/check_handoff.py L55/L62 still read strictly (row 63), as a follow-up for A1 to open today. 091's per-exit-term tests (pt 1) must include 089's `unreadable` term; 091 builds after 089. | rows 47, 63 | 05 line | A1 sees the follow-up in 05 | – |
| 10 | Check on the real repo: whole-output diff of `check_pipeline.py` before and after 089 (both on the post-088 tree, same args). Expected: exactly one added line, `UNREADABLE: none`, between ORPHAN LOG and INBOX, and no other change (RI-013). | real tree | diff in 05 and 06 | `diff` shows one added hunk of 1 line. Any real unreadable file would instead show as an UNREADABLE entry, and I2 records it in 05 | – |

Per-site results after the build (steps 2 and 3). The result on a readable file is the same as today.

| Site (today's line) | Unreadable result | Exit |
|---|---|---|
| read_request L413 / classify L527 (request.md) | `<ID>: UNREADABLE (<why>)` | UNREADABLE term |
| i3_verdict L472 via classify/incomplete (06) | classify UNREADABLE; incomplete `06 not checked (<why>; item 089)` | UNREADABLE + INCOMPLETE |
| classify L551, L558 (07) | `<ID>: UNREADABLE (<why>)` | UNREADABLE term |
| _log_text L591 (uncommitted_steps, incomplete) | step 3 (i), (ii) | UNREADABLE (+ INCOMPLETE for items with steps) |
| _last_log_line L673; I3 loop L763 | step 3 (ii) | UNREADABLE + INCOMPLETE |
| incomplete L698 (06), L729 (05) | step 3 (ii) | UNREADABLE + INCOMPLETE |
| _sent_back L782, L793 | skip / [] (unchanged, refusal side) | n/a (--log path) |
| orphan_log_lines L836 | `ORPHAN LOG: <orphans or none>; not checked: <whys>` | UNREADABLE term |
| _item_lines L889; _run_seconds L914 | unchanged `<file> unreadable` (LOG BATCH not computable) | now also the UNREADABLE term (stricter than today: a bad 05/06 read only here was exit 0) |
| open_branches L1125 | no clash compare | UNREADABLE term |
| _shallow_boundaries L1196 | step 5 | UNREADABLE term |
| request_text_of L1306 | `RESEARCH ONLY check: <why> (item 089)` | SKIPPED + UNREADABLE |
| real_data_field L1393 (via read_request), L1402 | `<step> not checked (<why>; item 089)` | INCOMPLETE + UNREADABLE |
| _inbox_gate L1478 | step 3 (ix) | UNREADABLE term |
| inbox_section L1495 | `INBOX: not checked (<name> unreadable)` | UNREADABLE term |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| logs/research, logs/implementation folders (_log_text, _last_log_line, I3 loop, orphan_log_lines, _item_lines) | unchanged: no files, nothing logged (today's behaviour, not a read failure) | unreadable file: `UNREADABLE: <file> (<detail>)` + each consumer's `not checked (<file> unreadable ...)`; never `none` alone |
| a log path that is a directory | n/a (it exists) | `UNREADABLE: <path> (IsADirectoryError)` |
| work/<ID>/request.md (classify, real_data_field, research_code, open_branches) | unchanged: not listed / `no request.md` texts (062, 070) | `<ID>: UNREADABLE (work/<ID>/request.md unreadable)` or `RESEARCH ONLY check: <why> (item 089)`; UNREADABLE line |
| work/<ID>/05, 06, 07 (classify, incomplete, real_data_field, _run_seconds) | unchanged: step missing | `05/06 not checked (<why>; item 089)` in INCOMPLETE, `<ID>: UNREADABLE (...)` in classify; UNREADABLE line |
| newest logs/audit/YYYY-MM-DD.md (inbox_section) | unchanged: `not checked (no daily report)` | `INBOX: not checked (<name> unreadable)`; UNREADABLE line |
| templates/daily-audit.md (_inbox_gate, uncommitted report) | unchanged: ok False → `not checked (... has no ## Inbox)` | `not checked (<name> not committed; its templates/daily-audit.md unreadable)`; UNREADABLE line |
| <git-common-dir>/shallow (_shallow_boundaries) | flag true → "unreadable" (not an UNREADABLE entry); flag not true → "full" (079, unchanged) | exists but unreadable (any flag) → "unreadable" + `UNREADABLE: <path> (<detail>)` |
| `git rev-parse --git-common-dir` output | failure: unchanged ("unreadable" if sure else "full") | not a file read; no UNREADABLE entry |
| byte offset in the detail | only for UnicodeDecodeError (err.start on the whole file's bytes) | other errors: the OSError class name; never errno text or file bytes |

## Self-check
Recurring issues checked:
- RI-001 (ESCALATED): every selector rule has a computed count (globs 44/44, census 21 → 0, INCOMPLETE ≤ 51, fixture isolation by exit terms). None is written as "always".
- RI-010 (ESCALATED): R3 writes no log line; the orchestrator runs `--log` (item 045). The map adds no step-order rule.
- RI-014 (OPEN): this item's family. Step 5 removes the wrong shallow reason, and test (c) pins it.
- Also checked, all GUARDED:
  - RI-002: no "" → none; ORPHAN LOG is never a bare none when a file is lost.
  - RI-004/RI-005: the rows below.
  - RI-006: Totals from counting the 70 table lines one by one; 64 + 5 + 1 = 70. The orchestrator's check_handoff run confirms.
  - RI-012: classification is by exception class, never by message text.
  - RI-013: the step 10 whole-output diff.

| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Step 1 / 6a offset for b"\xff\xfe" | detail = `not UTF-8 at byte {err.start}`; 0xFF is never valid UTF-8 (RFC 3629) | the first byte is invalid → err.start = 0 | `(not UTF-8 at byte 0)` ✓ |
| Step 6c offset for b"# 06\n\xff" | err.start = the number of valid bytes before 0xFF | "#", " ", "0", "6", "\n" = 5 bytes → 5 | `(not UTF-8 at byte 5)` ✓ |
| Step 6d offset for b"Scope: FULL\n\xff" | the same | "Scope: FULL" = 11 chars + "\n" = 12 → 12 | `(not UTF-8 at byte 12)` ✓ |
| Step 5 / test (c) offset | test (c) writes `c.encode() + b"\n\xff\n"`, c = `git rev-parse HEAD` (L1047-1049, SHA-1, 40 hex) | 40 + 1 = 41 | `shallow (not UTF-8 at byte 41)` ✓ (a 64-hex SHA-256 repo would give 65; the fixture uses git's default) |
| Step 3 (ii) entry bound | entries only for items ≥ CHECKLIST_FROM = 41 (L307, L694) among 91 items 001-091 (Glob) | 91 − 40 = 51 | ≤ 51, not ~90 (row 52) ✓ |
| Steps 2 and 7, census | 21 read_text sites (Grep) → after the build, only `_read`'s read_bytes and write_log's open | 21 + 1 open = 22 today; 1 + 1 = 2 after | pinned total 2 ✓ |
| Q3 glob feasibility | files matching `*.md` = files matching `????-??-??.md` in logs/research + logs/implementation | 22 + 22 = 44 each; `.gitkeep` matches neither | 44 of 44 ✓ |
| Step 4 / 6a isolation (clean twin exits 0) | exit = 1 if and only if an L1643-1645 term or the inbox early return fires; no-git tree, item 150 request only, Date = --today | classify → "not started" (age 0 < 1, L535), not skipped or failed. incomplete: no step file → []. late/untracked/real/uncommitted/branches/ahead are None or 0 without git. batch: no I2 and no bad log → skipped. orphans: the log has no LOG_LINE → []. inbox: no logs/audit → (not checked, False) | every term is falsy → exit 0 ✓ |
| Step 4 / 6a isolation (bad twin exits 1 only through UNREADABLE) | the same terms with b"\xff\xfe" | batch: bad_logs → not_computable (not in the exit, L1645). incomplete: no step file → no entry. orphans: whys only, list [] → falsy. `_UNREAD` = 1 entry → unreadable True | exit 1 comes from `or unreadable` only, so M3 gives 0 and fails 6a ✓ |
| Step 4 / 6d isolation | classify → UNREADABLE (not in skipped/stuck/failed lists); no step files; no logs | only `_UNREAD` is non-empty | exit 1 only through UNREADABLE ✓ |
| Step 4, inbox early return (row 53) | L1639-1641 `if inbox_bad: ... return 1` | an unconditional 1, so there is no term to add | UNREADABLE is printed before it; M6 is killed by 6j ✓ |
| Step 5, sure-False path (081 P2) | flag exit 128 → sure False; `--git-common-dir` still works (P1 L47 read the malformed text); decode error → why set → "unreadable" | `_walk` L1218: shallow[1] != 0 and "unreadable" → not checked, failed False; exit 1 from UNREADABLE (and the git-died lines) | wrong reason gone ✓ |
| Step 1, newline (row 69) | read_text: `\r` and `\r\n` → `\n` (open() docs); `_read` does the same replace | "# 07\rA1 result: PASS\r" → "# 07\nA1 result: PASS\n" → `^A1 result:` matches (re.M) | 6h is `complete` before and after; M11 → `awaiting A1` ✓ |
| Step 1, N13 text | why = f"{path.as_posix()} unreadable"; `_bl` passes an absolute root, so path.as_posix() = bad.as_posix() | endswith holds | N13 unedited ✓ |

`check_handoff output (run by the orchestrator 2026-11-21 23:39 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 11
fact-check rows: 70
totals line: 70 rows -> 64 as-is, 5 fixed, 1 removed
PASS
```
