# 01 Research brief - 092
Branch daily-fixes/2026-11-24 (working tree as R1 read it on 2026-11-24 UTC; it carries open PRs #31-#36). Type BUG, Scope FULL, opened by A1. No brokerage connection. No ccbot/, config/ or data/ change is involved. R1 read the code and ran no command (r1-researcher.md L19: no shell). Every line number below is from this tree.

Read first: logs/recurring-issues.md (RI-014, RI-002, RI-012, RI-006), logs/audit/2026-11-22-089.md (07 point 9, N1), work/089/01-research.md (F1-F31, re-used where the same facts apply), scripts/check_handoff.py (all 141 lines), scripts/check_pipeline.py (`_UNREAD` L517, `_shown` L520-523, `_read` L526-542, docstring L342-360, `RULE_PATHS` L463, `open_branches` L1414-1512, `main` L1932 and L2078-2079), tests/test_pipeline_check.py (`_run` L63-66, `test_check_handoff_all_legacy_and_fail` L158-169, `test_check_handoff_open_branches_states` L2602-2614, `test_read_census` L3787-3809).

## Question
1. Where does scripts/check_handoff.py read 01 and 03, and what happens today when one of them holds a non-UTF-8 byte or cannot be read?
2. What has to change in each path (single item, `--all`, LEGACY, "no 03 yet") so that the result is a named unreadable line and exit 1, never a traceback and never a computed count?
3. What do the shared reader, the census test and the end-to-end fixture have to pin, so that bringing back the strict read fails a named test?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### Python behaviour the bug depends on (re-checked 2026-11-24)
- F1. `Path.read_text`: "The file is opened and then closed. The optional parameters have the same meaning as in open()." `Path.read_bytes` returns "the binary contents of the pointed-to file as a bytes object", so a bytes read never decodes. [https://docs.python.org/3/library/pathlib.html]
- F2. `Path.exists()` returns "True if the path points to an existing file or directory". A directory named `01-research.md` or `03-handoff.md` therefore passes the `exists()` guards at L54 and L59, and the read that follows raises. [https://docs.python.org/3/library/pathlib.html]
- F3. Error handler 'strict': "Raise UnicodeError (or a subclass), this is the default." `encoding="utf-8"` with no `errors=` (L55, L62) is strict. [https://docs.python.org/3/library/codecs.html]
- F4. "The octet values C0, C1, F5 to FF never appear" in UTF-8, so a fixture byte `\xff` can never decode. [https://www.rfc-editor.org/rfc/rfc3629]
- F5. Exception tree: `ValueError` → `UnicodeError` → `UnicodeDecodeError`. `FileNotFoundError`, `IsADirectoryError` and `PermissionError` are under `OSError`. One `except (OSError, UnicodeDecodeError)` covers the decode case and the directory/permission case, and neither class alone covers both. [https://docs.python.org/3/library/exceptions.html]
- F6. UnicodeError `start` is "The first index of invalid data in object", so a `not UTF-8 at byte <n>` detail can be built without printing any file content. [https://docs.python.org/3/library/exceptions.html]
- F7. When an exception is "raised and uncaught, the interpreter calls sys.excepthook", which "prints out a given traceback and exception to sys.stderr". [https://docs.python.org/3/library/sys.html]
- F8. When input comes from a file, the interpreter "exits with a nonzero exit status after printing the stack trace". "All error messages are written to the standard error stream". The docs give no specific exit number. [https://docs.python.org/3/tutorial/appendix.html]
- F9. In `ast.Call`, "func is the function, which will often be a Name or Attribute object". `ast.Attribute.attr` is "a bare string giving the name of the attribute". `research.read_text(...)` is an Attribute call, so the census must match `ast.Attribute` (as test_read_census L3798 does). [https://docs.python.org/3/library/ast.html; tests/test_pipeline_check.py L3795-3802]

### Today's code (scripts/check_handoff.py)
- F10. There are 2 file reads, both in `main`, both strict, neither in a try:
  - L55 `urls = unique_urls(research.read_text(encoding="utf-8"))` (01)
  - L62 `text = handoff.read_text(encoding="utf-8")` (03)

  The file has no `read_bytes` and no `open(`. Census today: `{("main", "read_text"): 2}`, total 2. [scripts/check_handoff.py L46-87 (Read)]
- F11. On a bad byte, or on a directory or unreadable file, either read raises out of `main` and out of `check_all` L125 (`code = main(d.name)` has no try). That gives a traceback on stderr and a nonzero exit (F7, F8). In `--all` the run stops at that item, so the later items and the `FAIL on ...` / `no new failures` summary never print. [scripts/check_handoff.py L123-135; F7; F8]
- F12. A crash is hard to tell from a correct run by exit code alone. The 089 audit observed exit 1 for the same kind of crash in check_pipeline.py, and exit 1 is also check_handoff's own "problem found" code (L87). A test that asserts only `code == 1` passes on the traceback too. The test helper `_run` (L63-66) captures stderr but returns only `(returncode, stdout)`. So the fixture needs its own subprocess call that keeps stderr and asserts that it has no `Traceback`, and it must also assert the named unreadable line on stdout. [logs/audit/2026-11-22-089.md L53-54; tests/test_pipeline_check.py L63-66; scripts/check_handoff.py L87]
- F13. The "no 03 yet" early return: when 03 does not exist, L59-61 print `no ... nothing else to check` and `return 0`. This is the exact state in which the orchestrator runs check_handoff right after R1 (r1-researcher.md L19). If only the L55 read is wrapped and its `why` is not turned into exit 1 before L61, an unreadable 01 gives exit 0. The request's "exit 1" for a bad 01 needs the 01 problem to count on this path as well. [scripts/check_handoff.py L53-61; .claude/agents/r1-researcher.md L19]
- F14. The sources count must not be computed from "" or None. `unique_urls("")` returns `[]`, and that would print `sources count (unique URLs in 01-research.md): 0`. The orchestrator copies that number into the R1 log line (`brief written | <sources count>`). A 0 from an unread file is the RI-002 shape (an uncomputable value turned into a number). The line should say that the count was not computed, and it should name the file. [scripts/check_handoff.py L42-43, L55-56; logs/recurring-issues.md RI-002 root cause]
- F15. `--all` sees only what `main` prints as `FAIL: ` lines: `problems = [l[6:] for l in ... if l.startswith("FAIL: ")]` (L126). An unreadable line that is printed in any other form is lost from the `<ID>: FAIL: ...` summary. It must be printed as `FAIL: <path> unreadable (...)`, or check_all must read it some other way. [scripts/check_handoff.py L123-133]
- F16. LEGACY masking: for items 002-008, a nonzero `main` prints `<ID>: LEGACY (...; <n> known problem(s))` and the item is not added to `failed` (L129-130). An unreadable 03 in a LEGACY item would then show as LEGACY and exit 0. LEGACY covers known count gaps (028), not unreadable files. Open question 1. [scripts/check_handoff.py L19-22, L127-133]
- F17. `--all` calls `main` only for folders that have a 03 (L115). A folder with only a bad 01 is printed `no hand-off` / `IN PR (...)` and its 01 is never read. Nothing crashes on that path today, and none of the request's paths covers it. Open question 2. [scripts/check_handoff.py L114-122]
- F18. `check_all(work=Path("work"))` takes a `work` argument, but `main` always uses `Path("work") / item` (L47), which is relative to the cwd. A unit test that calls `check_all(tmp_path / "work")` without a chdir does not read tmp_path's files in `main`. End-to-end fixtures should run the script by subprocess with `cwd=tmp_path`, as `_run` does. [scripts/check_handoff.py L47, L107; tests/test_pipeline_check.py L63-66, L2602-2614]

### The 089 reader and how check_handoff could use it
- F19. `check_pipeline._read(path, missing_ok=False)` returns `(text, None)` or `(None, "<path> unreadable")`. It catches `(OSError, UnicodeDecodeError)`, decodes strict UTF-8, maps `\r\n` and `\r` to `\n` (read_text's newline rule), and records the detail (`not UTF-8 at byte <n>` or the exception class name, never content) in the module dict `_UNREAD`, keyed by `_shown(path)`. [scripts/check_pipeline.py L517-542]
- F20. check_handoff already imports check_pipeline, but only lazily, inside `_branch_with_handoff` (L94-95, `sys.path.insert` then `from check_pipeline import open_branches`). scripts/commit_step.py L43 imports from check_pipeline "as check_handoff does". Using `_read` from check_handoff would satisfy the request's "one reader". It would mean importing check_pipeline at module level, or before the reads in `main`. [scripts/check_handoff.py L90-104; scripts/commit_step.py L43]
- F21. Side effect of re-using `_read`: each call adds to `check_pipeline._UNREAD`, which only `check_pipeline.main` clears (L1932) and prints (L2078). A check_handoff run would fill it and never print it. That does no harm on its own, but check_handoff must take `why` from the return value and not from `_UNREAD`. Within one `--all` run, `_UNREAD` keeps growing across items. [scripts/check_pipeline.py L517, L1932, L2078-2079]
- F22. Related gap, not in the request: in `--all`, `_branch_with_handoff` → `open_branches()` reads the working-tree request.md through `_read` (L1508, `mine_text, _ = ...`). check_handoff never reports a failure there. In check_pipeline itself the failure appears on `UNREADABLE:` (L2078). In check_handoff it is silent, so the clash text could differ (`theirs != None`), but nothing raises. This gap is beside the 089 docstring's known gap at L85-87 about per-ref errors. Open question 3. [scripts/check_pipeline.py L1507-1512, L85-87; scripts/check_handoff.py L90-104]
- F23. The check_pipeline docstring says at L360 "Known gap: scripts/check_handoff.py still reads its files strictly." After 092 that sentence is false and should be changed in the same build. RI-012/RI-013 practice: the docstring is part of the rule text. [scripts/check_pipeline.py L360]
- F24. `RULE_PATHS` includes `scripts/check_handoff.py` (L463), so the person's OK is needed at PR review, as for 089 (089 audit 07 point 8). [scripts/check_pipeline.py L463; logs/audit/2026-11-22-089.md L92]

### What the guardrail tests have to pin
- F25. Census: `test_read_census` (L3787-3809) parses only scripts/check_pipeline.py. A twin test over scripts/check_handoff.py, using the same walker and a `(function, call) → (count, reason)` dict with a pinned total, fails when anyone restores a raw `read_text` at L55 or L62 (the request's mutation). Expected after the fix: 0 raw reads if check_handoff uses `check_pipeline._read`, or exactly 1 (`read_bytes` inside its own reader) if it has its own reader. The census should be computed by AST in the test and never copied by hand (RI-006). [tests/test_pipeline_check.py L3787-3809; F9]
- F26. End-to-end fixtures each need these three asserts: no `Traceback` in stderr (F12), the named line on stdout, and exit 1. Cases implied by the request and F13-F16:
  - (a) bad byte in 01, no 03 → exit 1 and no `sources count ...: <n>` number (F13, F14);
  - (b) good 01, bad byte in 03 → exit 1 and a `FAIL: ... unreadable` line;
  - (c) `--all` with one bad 03 among good items → the later items still print, `<ID>: FAIL: ... unreadable ...`, `FAIL on <ID>`, exit 1 (F11, F15);
  - (d) a directory named 03-handoff.md → same as (b) with an `IsADirectoryError` detail (F2, F5).

  Each has a clean twin that exits 0 (or PASS). That way, exit 1 is shown to come from the unreadable file alone, which is 089's 6a pattern (`test_unreadable_log_exits_1_alone`, L3812). [tests/test_pipeline_check.py L3812-3814]
- F27. Mutations that the tests should kill: M-a, L55 back to strict `read_text` (census, (a)); M-b, L62 back (census, (b)); M-c, the 01 `why` dropped before the no-03 `return 0` (only (a) catches this); M-d, the unreadable line printed without the `FAIL: ` prefix (only (c) catches this). R1 derived these from F13 and F15. None has been run (UNVERIFIED by run).

## Numbers used (show the math)
- Raw reads in scripts/check_handoff.py today: 2 (L55, L62; `read_text` 2, `read_bytes` 0, `open` 0), from R1's Read of the full 141-line file. After the fix: 0 (re-use `_read`) or 1 (own reader). The test computes it (F25).
- Exit codes: correct "problem found" = 1 (L87). An uncaught exception gives nonzero (F8), observed as 1 for the same kind of crash in the 089 audit (L53-54). So exit code alone cannot separate them (F12).
- Sources in this brief: counted by `scripts/check_handoff.py 092` (orchestrator), not by R1.
- No money numbers. This item does not touch the account.

## Fit for a ~$3k account
- No trading effect. check_handoff.py is process tooling, with no ccbot/, config/, data/ or broker path.
- What it guards: the sources count in every R1 log line, and the fact-check totals A1 checks daily (`--all`). Today a bad byte crashes the run (F11). If the fix is half done, the run could report 0 sources or a LEGACY/exit 0 (F14, F16). Either way an unchecked research file could look checked before a rule change reaches the bot.

## Open questions
1. LEGACY (F16): should an unreadable 03 in items 002-008 be FAIL (exit 1) rather than LEGACY? R1 suggests FAIL. LEGACY excuses known count gaps, and a file nobody can read has not been checked.
2. `--all` and 01 (F17): today `--all` never reads 01. Should it stay that way (the request names only `main`'s reads), or should a bad 01 in `--all` also be a FAIL? R1 suggests unchanged scope, with the gap written in the docstring.
3. F22: should check_handoff report `open_branches`' unreadable request.md reads (from `check_pipeline._UNREAD`), or is that left for a follow-up item? It is not a crash.
4. Re-use `check_pipeline._read` or a local reader (F20, F21)? Re-use matches "one reader" and the 089 detail text. The import order and the `_UNREAD` growth need to be stated in the plan.
5. Exact wording of the lines, for R3: e.g. `FAIL: work/092/03-handoff.md unreadable (not UTF-8 at byte <n>)` and `sources count (unique URLs in 01-research.md): not computed (work/092/01-research.md unreadable (...))`. The orchestrator's parsing of the sources line must then refuse to log a count (F14). It is UNVERIFIED how the orchestrator parses that line; it is not in the repo files R1 read.
