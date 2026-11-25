# 01 Research brief - 089
Branch daily-fixes/2026-11-21 (working tree as read by R1 on 2026-11-21 UTC). Type BUG, Scope FULL, opened by A1. No brokerage connection; no ccbot/, config/ or data/ change is in question. R1 read the code but ran no command (r1-researcher.md L19: no shell). Each line number below is from this tree. Where the audits name other line numbers (086 audit L54: `main` L1516, `incomplete` L669, `_log_text` L581 at 7eb51b0), the code has moved since.

Read first: logs/recurring-issues.md (RI-014, RI-002, RI-010), logs/audit/2026-11-21-086.md finding 1, logs/audit/2026-11-21-081.md F3, work/086/05-build-report.md (Deviation 3 (ii), N13/M14), work/081/03-handoff.md rows 26 and 50 (F10), scripts/check_pipeline.py, tests/test_pipeline_check.py (`_run` L62, `GIT_CENSUS` L2369, test (c) L2476, N13 L3060).

## Question
1. Which readers in scripts/check_pipeline.py decode a file under logs/, work/ or .git/ strictly without catching the error? What does each one do today when it meets a non-UTF-8 byte?
2. What do Python and git document about the behaviour this depends on: strict decoding, the exception classes, the exit status and traceback of an uncaught error, and the `.git/shallow` format?
3. What must a shared reader, a census test and an end-to-end test pin, so that a mutation which brings back the crash, or the wrong shallow reason, fails a named test?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### Python and git behaviour
- F1. `Path.read_text(encoding=None, errors=None, newline=None)`: "The file is opened and then closed. The optional parameters have the same meaning as in open()." [https://docs.python.org/3/library/pathlib.html]
- F2. `Path.read_bytes()` returns "the binary contents of the pointed-to file as a bytes object", so reading bytes never decodes. [https://docs.python.org/3/library/pathlib.html]
- F3. The errors default is strict. For TextIOWrapper: "Pass 'strict' to raise a ValueError exception if there is an encoding error (the default of None has the same effect)". [https://docs.python.org/3/library/io.html]
- F4. Codec handler 'strict': "Raise UnicodeError (or a subclass), this is the default." [https://docs.python.org/3/library/codecs.html]
- F5. Codec handler 'replace': "On decoding, use � (U+FFFD, the official REPLACEMENT CHARACTER)". 'surrogateescape': "On decoding, replace byte with individual surrogate code ranging from U+DC80 to U+DCFF". [https://docs.python.org/3/library/codecs.html]
- F6. "UTF-8 byte sequences have a structure that doesn't allow arbitrary byte sequences." [https://docs.python.org/3/library/codecs.html]
- F7. "The octet values C0, C1, F5 to FF never appear" in UTF-8, so the fixture bytes `\xff\xfe` (086 audit L54) and `\xff` (081 audit P2) can never decode under strict UTF-8. [https://www.rfc-editor.org/rfc/rfc3629]
- F8. Exception tree: `ValueError` → `UnicodeError` → `UnicodeDecodeError`. `FileNotFoundError`, `IsADirectoryError` and `PermissionError` sit under `OSError`. So `except OSError` alone does not catch a decode error, and `except UnicodeDecodeError` alone does not catch a directory named `2026-11-19.md`. [https://docs.python.org/3/library/exceptions.html]
- F9. UnicodeError has the attributes `encoding`, `reason`, `object`, `start` and `end`, and "err.object[err.start:err.end] gives the particular invalid input". A reason text can therefore name the byte offset without printing file content. [https://docs.python.org/3/library/exceptions.html]
- F10. When an exception other than SystemExit is uncaught, "the interpreter calls sys.excepthook", which "prints out a given traceback and exception to sys.stderr". [https://docs.python.org/3/library/sys.html]
- F11. On an unhandled error with input from a file, the interpreter "exits with a nonzero exit status after printing the stack trace", and "All error messages are written to the standard error stream". The docs give no specific code. [https://docs.python.org/3.12/tutorial/appendix.html]
- F12. The crash's observed exit code is 1, the same as check_pipeline's own "problems found" exit: the 086 audit L54 reports "`UnicodeDecodeError`, exit 1". So an exit-code assert cannot tell a crash from a correct run. The test helper `_run` (tests/test_pipeline_check.py L62-65) returns only `(returncode, stdout)` and drops stderr. A `_run`-only assert of `code == 1` passes on the traceback too. The test has to check stderr for `Traceback` (as test (c) L2484 does) **and** the `unreadable` text on stdout. [https://docs.python.org/3/library/sys.html; logs/audit/2026-11-21-086.md L54; tests/test_pipeline_check.py L62-65]
- F13. `$GIT_DIR/shallow` "lists commit object names and tells Git to pretend as if they are root commits", and "Each line contains exactly one object name." So any byte that is not a hex digit, non-UTF-8 bytes included, makes a malformed file, not an absent one. [https://git-scm.com/docs/shallow]
- F14. The gitrepository-layout entry for `shallow`: "This file is ignored if $GIT_COMMON_DIR is set and "$GIT_COMMON_DIR/shallow" will be used instead." (079's reason for reading via `--git-common-dir`.) [https://git-scm.com/docs/gitrepository-layout]
- F15. `--is-shallow-repository`: "When the repository is shallow print "true", otherwise "false"." `--git-common-dir`: "Show $GIT_COMMON_DIR if defined, else $GIT_DIR." Neither text says what happens when the shallow file is malformed. A1 observed exit 128 from the flag on a bad line (081 audit L12, P2 L52). [https://git-scm.com/docs/git-rev-parse; logs/audit/2026-11-21-081.md L12, L52]
- F16. In `ast.Call`, "`func` is the function, which will often be a Name or Attribute object". `ast.Attribute` has `attr`, "a bare string giving the name of the attribute". GIT_CENSUS's walker (L2423-2427) matches only `ast.Name` callees (`_git`, `_git_ok`). A read census must match `ast.Attribute` with `attr` in {read_text, read_bytes, open}, because `f.read_text(...)` is an Attribute call. [https://docs.python.org/3/library/ast.html; tests/test_pipeline_check.py L2423-2427]

### Census of file reads in scripts/check_pipeline.py (Grep `read_text|read_bytes|open\(`, R1 read each site)
- F17. The file has 21 `.read_text(` calls. All use `encoding="utf-8"` with no `errors=`, so all are strict (F3). 5 are inside a try that catches UnicodeDecodeError, and 16 are not. There is no `read_bytes`. The one `.open(` is the append in `write_log` L825 (a write). [scripts/check_pipeline.py (Grep, Read)]
- F18. The 16 uncaught sites, by function, file read and today's result on a bad byte (traceback, per F10/F12). [scripts/check_pipeline.py (Read)]

| # | Line | Function | Reads | Path under |
|---|---|---|---|---|
| 1 | L413 | `read_request` | work/<ID>/request.md | work/ |
| 2 | L472 | `i3_verdict` | work/<ID>/06 (its docstring says "None = unreadable", but the read is strict) | work/ |
| 3 | L527 | `classify` (FAST check) | request.md | work/ |
| 4 | L551 | `classify` (I3 FAIL branch) | 07 | work/ |
| 5 | L558 | `classify` (complete branch) | 07 | work/ |
| 6 | L591 | `_log_text` | logs/research/*.md, logs/implementation/*.md (glob `*.md`, not `????-??-??.md`) | logs/ |
| 7 | L673 | `_last_log_line` | logs/implementation/????-??-??.md | logs/ |
| 8 | L698 | `incomplete` | 06 | work/ |
| 9 | L729 | `incomplete` (Suite check) | 05 | work/ |
| 10 | L763 | `incomplete` (I3 loop) | logs/implementation/????-??-??.md | logs/ |
| 11 | L836 | `orphan_log_lines` | logs/{research,implementation}/????-??-??.md | logs/ |
| 12 | L1125 | `open_branches` (ID clash) | working-tree work/<ID>/request.md | work/ |
| 13 | L1306 | `research_code.request_text_of` | request.md | work/ |
| 14 | L1402 | `real_data_field` (070 field gap) | 05, 06 | work/ |
| 15 | L1478 | `_inbox_gate` | templates/daily-audit.md | templates/ (outside logs/ and work/) |
| 16 | L1495 | `inbox_section` | newest logs/audit/YYYY-MM-DD.md | logs/ |

- F19. The 5 caught sites each give a different result. [scripts/check_pipeline.py L782-784, L792-795, L888-892, L913-916, L1193-1198]
  - `_sent_back` L782 skips the file. This is on purpose (refusal side, 086 docstring L776-777).
  - `_sent_back` L793 (07) gives `results = []`, also the refusal side.
  - `_item_lines` L889 gives `<file> unreadable`.
  - `_run_seconds` L914 gives `<file> unreadable`.
  - `_shallow_boundaries` L1196 gives "unreadable" if `sure`, else "full".
- F20. The 086 audit (L54) gives the crash path as `main` → `incomplete` → `_log_text`, in a tmp tree with no git. With git, `main` calls `uncommitted_steps()` (L1539) before the classify/incomplete loop (L1542-1566). `uncommitted_steps` calls `_log_text` at L610 once `ls-tree` succeeds, so in a git repo the first traceback would come from there. This is R1's reading of the call order only; no run was made (UNVERIFIED by run). [scripts/check_pipeline.py L604-610, L1532-1566]
- F21. The readers do not all read the same set of files. `_log_text` globs `*.md`, while `_last_log_line`, the I3 loop, `orphan_log_lines`, `_sent_back` and `_item_lines` glob `????-??-??.md`. A shared reader that also unified the globs would change which files `_logged` sees. That is a behaviour change beyond 089's "never crashes", and R2/R3 should decide it explicitly. [scripts/check_pipeline.py L591-592, L672, L762, L835, L780, L886]
- F22. Each consumer uses the text for something different, so "unreadable" has a different safe side in each. [scripts/check_pipeline.py (Read)]
  - In `_logged` (via `_log_text`), a lost file can hide a log line. That gives a false `no log line for X` in INCOMPLETE (L700-704), or a false UNCOMMITTED STEP entry (L617-619).
  - In `orphan_log_lines`, a lost file can hide an orphan, which is a silent pass (RI-002 shape).
  - In `classify`, an unreadable request.md has no status at all today.
  - Of the request's three named targets (`_log_text`, `orphan_log_lines`, the I3 loop), only `orphan_log_lines` would pass silently if it skipped the file. The other two would give a wrong entry. Either way the request's "named unreadable line, exit 1" is needed.
- F23. `main`'s exit expression (L1643-1645) has no term for an unreadable file. A shared reader that only returns `(text, why)` is not enough: some printed line has to carry `why`, and the exit has to depend on it. Otherwise the 089 "exit 1" fixture could pass for other reasons (the same gap as 081 audit F1 A8/A9, where (a)/(b) exit 1 for several reasons at once). [scripts/check_pipeline.py L1643-1645; logs/audit/2026-11-21-081.md L95]
- F24. The inbox path returns 1 early at L1639-1641, before the general exit. An unreadable daily report read at L1495 would need its own `(text, True)` result there. [scripts/check_pipeline.py L1637-1641]

### `_shallow_boundaries` (081 audit F3)
- F25. Today, when the flag does not say "true" (`sure` False, e.g. git died with 128), any OSError or UnicodeDecodeError gives "full" (L1197-1198). [scripts/check_pipeline.py L1188-1198]
  - `_walk` L1218 then sees `shallow[1] != 0` and `"full" != "unreadable"`, and falls through to L1220: `cutoff ... not in HEAD's history (squash/rebase or wrong SHA)`, failed True.
  - This is the wrong reason A1 saw in P2 (081 audit L103).
- F26. If a decode error gives "unreadable" whatever `sure` is, `_walk` L1218-1219 returns `not checked (shallow clone; run git fetch --unshallow)` with failed **False**. The UNTRACKED CHANGE line then no longer adds to the exit (L1643 `untracked[1]`). The run still exits 1 in A1's P2, through the git-dies lines (MAIN AHEAD, OPEN BRANCHES; 081 audit L42-43, L52). So test (c)'s `returncode == 1` stays true, but it no longer comes from UNTRACKED CHANGE. The request's text assert is what pins F3. [scripts/check_pipeline.py L1218-1219, L1643; logs/audit/2026-11-21-081.md L42-52]
- F27. Side effect: `_anchor_env` (L629-631) maps "unreadable" to `shallow clone; run git fetch --unshallow`. After the fix, P2 prints `RULE NOT SEEN: not checked (shallow clone; ...)` instead of trying anchors whose git calls die. That is the strict side (084 docstring L626), but it is a second changed line, and 05/06's whole-output diff should list it (RI-013). [scripts/check_pipeline.py L623-632]
- F28. In the `sure`-False case, a missing file (FileNotFoundError) giving "full" matches 079's docstring ("A flag git can't give and no file is "full""). A file that exists but can't be read (PermissionError, IsADirectoryError) still gives "full", the same proof-of-existence gap as the decode case. The request names only the decode error. Open question 2. [scripts/check_pipeline.py L1184-1187; https://docs.python.org/3/library/exceptions.html]
- F29. Test (c) (L2476-2487) asserts no `Traceback` in stderr, exit 1, and no git line ending `: none`. The wrong-reason line (`... not in HEAD's history ...`) satisfies all three, which is why F3 survived. [tests/test_pipeline_check.py L2476-2487]

### Existing test pattern to reuse
- F30. N13 (`test_batch_unreadable_log_file_makes_every_item_not_computable`, L3060-3071) writes `b"\xff\xfe"` to logs/implementation/2026-11-19.md and calls `_bl` (the unit `batch_log_items`), not the CLI. The same fixture run through `_run`/subprocess with git absent or present is the end-to-end case the request means by "N13 gains the `_run` assert". That assert must read stderr (F12). [tests/test_pipeline_check.py L3060-3071, L62-65]
- F31. GIT_CENSUS (L2369-2397) maps `(innermost function, callee)` to `(count, reason)`, and `test_git_call_census` asserts exact equality plus a pinned total (47, L2432). A read census in the same shape would key `(function, "read_text")`. Its expected state would be: every logs/ and work/ read goes through the one shared reader, plus listed exceptions with reasons, e.g. the template read L1478 and test-only reads. [tests/test_pipeline_check.py L2369-2432]

## Numbers used (show the math)
- read_text sites: 21 by Grep (L413, 472, 527, 551, 558, 591, 673, 698, 729, 763, 782, 793, 836, 889, 914, 1125, 1196, 1306, 1402, 1478, 1495).
  - Caught: 5 (L782, 793, 889, 914, 1196). Uncaught: 21 − 5 = 16 (table F18).
  - Of the 16: under logs/ 5 (L591, 673, 763, 836, 1495); under work/ 10 (L413, 472, 527, 551, 558, 698, 729, 1125, 1306, 1402); templates/ 1 (L1478). 5 + 10 + 1 = 16.
- 081/03 row 26 listed 10 sites plus L686 = 11 (an older tree). Today's 16 is higher because 082/084/086 code was added after it. The census should be computed by AST at build time, never copied from either number (RI-006).
- No money numbers. This item does not touch the account.

## Fit for a ~$3k account
- No trading effect. check_pipeline.py is process tooling, with no ccbot/, config/, data/ or broker path.
- The risk it guards: a crash in the daily check (exit 1 with a traceback) looks like "problems found" (F12). A1 could then read a partial output as a full audit, and the lines after the crash (ORPHAN LOG, INBOX, SKIPPED) would never print. The fix keeps the audit trail that gates every code change honest. It does not change any trade rule.

## Open questions
1. What does "unreadable" mean for each consumer (F22)? Options:
   - (a) One `UNREADABLE: <file> (...)` line, exit 1, with each consumer treating the file as empty. This risks false INCOMPLETE/UNCOMMITTED entries beside it.
   - (b) Each consumer prints its own `not checked (<file> unreadable)`.
   R2/R3 decide. Either way `main`'s exit needs a term for it (F23), and `_sent_back`'s skip stays on the refusal side (F19).
2. `_shallow_boundaries` with `sure` False: should PermissionError/IsADirectoryError also give "unreadable", or only UnicodeDecodeError, as the request says (F28)?
3. Should the shared reader unify the glob (`*.md` vs `????-??-??.md`, F21), or keep each caller's file set unchanged? R1 suggests unchanged, because 089 is a crash fix.
4. Is templates/daily-audit.md (L1478) in scope? The request says logs/ and work/. R1 suggests a census entry with a reason, or the same reader.
5. scripts/check_handoff.py L55 and L62 also read 01/03 strictly (Grep). The request names only check_pipeline.py. Does it stay out of scope, or become a follow-up item?
6. Should the reason text name the byte offset (F9), e.g. `unreadable (not UTF-8 at byte 0)`? It must never print the file's bytes: PEP 538 strict stdout, 081/03 row 7.
7. F20 (with git, the first crash comes from `uncommitted_steps`) is from code reading only. I1/I2 should confirm it with a run on the fixture.
