# 01 Research brief - 076

## Question
The I2 log field `tests <pass>/<total>` has no written meaning. The bug: 072 logged `tests 411/411` for 411 passed, 1 skipped, and 073 logged `tests 414/415` for the same kind of run. What should the field mean, and how can `check_pipeline.py --log I2` refuse a field that is ill-formed or inconsistent? This is RI-006 (a hand-counted total in a log line), found before merge. Nothing here touches trading, quotes or the $3k account's rules. It is process tooling only.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### Repo facts (read on 2026-11-19, no shell; file:line refs, not URLs)
- R-1. `LOG_FORMAT["I2"] = r"\d+ files? changed \| tests \d+/\d+\b.*"` and `LOG_HINT["I2"] = ("<n> files changed | tests <pass>/<total>", "2 files changed | tests 9/9")`. Nothing defines `<total>` (scripts/check_pipeline.py L234, L244).
- R-2. i2-builder.md L25 gives the same `tests <pass>/<total>` text, also with no definition (.claude/agents/i2-builder.md L25).
- R-3. The format is applied in two places:
  - `write_log` refuses a non-match with exit 2 (check_pipeline.py L426-431).
  - `INCOMPLETE` re-checks every existing log line of items `>= LOG_CHECK_FROM` (= 45) against the same regex (L190, L394-399).
  - So if the regex is tightened, the lines already written for 045-075 become INCOMPLETE and main goes red. Either the old form stays valid for those items, or the new form needs a cutoff constant (the same pattern as `LOG_CHECK_FROM`, `VERDICT_FROM`, `WHOLE_DIFF_FROM`).
- R-4. The regex ends in `\b.*`, so any trailing text passes. Earlier I2 lines use this for notes such as `(1 skipped: exchange_calendars)` (064, logs/implementation/2026-11-15.md L5) and `(round 2: test case added)` (062, 2026-11-13.md L6).
- R-5. Several tests pin the current text and the I1 plan must update them:
  - tests/test_pipeline_check.py L562 and L566 pin the hint text `<n> files changed | tests <pass>/<total>` exactly.
  - L548-550 require every `LOG_HINT` example to fit its `LOG_FORMAT`.
  - `FIELDS["I2"] = "1 files changed | tests 1/1"` (L16) is used by many fixtures, and literal `tests 1/1` / `tests 9/9` lines appear at L380, L390, L404, L412, L428, L442-443, L533, L537 and L557.
- R-6. No other script parses the tests field. The only matches for `tests <pass>`, `<pass>/<total>` and `tests \d+/\d+` outside logs/ and work/ are i2-builder.md L25, check_pipeline.py L244 and tests/test_pipeline_check.py (Grep).
- R-7. How earlier lines filled `<total>`, from logs/implementation/*.md checked against 05 build reports:
  - Total includes the skip: 064 `316/317 (1 skipped: exchange_calendars)`; 074 `453/454` with 05 L59 `453 passed, 1 skipped`.
  - Total includes a failure and a skip: 070 `383/385` with 05 L224 `1 failed, 383 passed, 1 skipped`; 070 `403/405` with 05 L290 `1 failed, 403 passed, 1 skipped`; 069 `399/401` with 05 L259 `1 failed, 399 passed, 1 skipped`; 061 `292/294` with 05 L156; 063 `297/299` with 05 L99.
  - So most lines already use total = passed + failed + skipped (+ errors). The split was not checked for every other line, e.g. 047's `196/197` and 049-056.
- R-8. Two lines leave the skip out:
  - 072: `411/411` for `411 passed, 1 skipped` (logs/audit/2026-11-18-072.md L72-76).
  - 058, newly found here: logs/implementation/2026-11-12.md L13 `tests 218/218`, while work/058/05-build-report.md L11 says `218 passed, 1 skipped`. So this is a second case of the same slip, not a one-off.
- R-9. One line counts a different scope. 065's `tests 49/49` was a single test file, not the suite (logs/audit/2026-11-18-072.md L74). The field never said which run it counts.
- R-10. The `pass/total` form hides failures. `383/385` reads the same whether the 2 are skips or failures; 070's 2 were 1 failed and 1 skipped (R-7).
- R-11. The skip count depends on the machine, so the same commit can give different counts:
  - tests/test_calendar.py L110 uses `pytest.importorskip("exchange_calendars")`.
  - tests/test_pipeline_check.py L48 and others skip when `git` is not on PATH, and tests/test_probe_guardrails.py L19 does the same.
  - tests/test_safety.py L119 skips with no python3.10/3.11.
- R-12. The project pins no pytest version (`dev = ["pytest"]`, pyproject.toml L13). It sets `testpaths = ["tests"]` (L20). The installed pytest version is UNVERIFIED (R1 has no shell).

### pytest behaviour (external)
- P-1. The final "summary stats line" is the line at the end of the run. The docstring example is `"=== 12 passed, 2 errors in Xs==="` [https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py].
- P-2. The parts of that line follow `KNOWN_TYPES` order, with unknown types added at the end. On main, `KNOWN_TYPES` starts `("failed", "passed", "skipped", "deselected", "xfailed", "xpassed", "warnings", "error",` and then `"subtests passed", "subtests failed", "subtests skipped"` [https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py].
  - So **failed comes before passed**: `1 failed, 383 passed, 1 skipped` (matches 070/05 L224).
  - The regex A1 proposed in logs/audit/2026-11-18-072.md L93, `tests \d+ passed(, \d+ (failed|skipped|...))*`, would refuse every run with a failure, and would accept "failed" written after "passed", which pytest never prints. Do not use that regex as written.
  - Whether the installed pytest has the `subtests` keys is UNVERIFIED (R-12).
- P-3. Plural forms come from `pluralize`: `if noun not in ["error", "warnings", "test"]` (other nouns are left as they are), `noun = noun.replace("warnings", "warning")`, `return count, noun + "s" if count != 1 else noun`. This gives `1 error` / `2 errors` and `1 warning` / `2 warnings` [https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py].
- P-4. With nothing to report, the line is `no tests ran` [https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py].
- P-5. `deselected` is a stats key filled by `pytest_deselected`, i.e. tests left out by selection and not run [https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py]. `-k` "will run tests whose keywords match the given expression" [https://docs.pytest.org/en/stable/how-to/usage.html].
- P-6. The docs' example final line is `1 failed, 1 passed, 1 skipped, 1 xfailed, 1 xpassed, 1 error in 0.12s` [https://docs.pytest.org/en/stable/how-to/output.html].
- P-7. "`pytest` counts and lists *skip* and *xfail* tests separately." A skip means "you expect your test to pass only if some conditions are met" [https://docs.pytest.org/en/stable/how-to/skipping.html].
- P-8. Exit code 0 is "All tests were collected and passed successfully". Exit code 1 is "Tests were collected and run but some of the tests failed". Exit code 5 is "No tests were collected" [https://docs.pytest.org/en/stable/reference/exit-codes.html].
- P-9. `warnings` is a KNOWN_TYPES key (P-2) but it counts warnings, not tests, so it must not be added to any test total. Inference from P-2/P-3, not a pytest statement.

## Numbers used (show the math)
- 072: 411 passed + 1 skipped = 412 collected and run. The logged 411/411 is off by 1. Under total = passed + failed + skipped + errors it should read 411/412 (R-8).
- 058: 218 passed + 1 skipped = 219. The logged 218/218 should read 218/219 (R-8).
- 070 round 2: 1 failed + 383 passed + 1 skipped = 385. The logged 383/385 already fits that definition (R-7). It still hides that 1 of the 2 was a failure (R-10).
- An "inconsistent" check `--log` can do on its own: in the old form, refuse pass > total. In the verbatim form (option B), refuse parts out of KNOWN_TYPES order, a repeated type, or a wrong plural. Neither check can find 072's mistake: 411/411 is internally consistent. Only a form that copies pytest's line (B), or a cross-check against an actual run (C), closes that gap.

## Fit for a ~$3k account
- No effect on trading logic, quotes, fees, taxes or position size. This is log hygiene in scripts/check_pipeline.py, .claude/agents/i2-builder.md and tests/test_pipeline_check.py only.
- RULES change (.claude/): it needs the person's OK in PR review, as for 072.

## Options for R2/R3/I1 (research, not a decision)
- **A. Keep `tests <pass>/<total>` and write the definition down.**
  - Definition: from the last line of the full-suite run `python3 -m pytest -q` at repo root, pass = passed, and total = passed + failed + skipped + errors + xfailed + xpassed. Deselected and warnings are not counted (P-5, P-9).
  - `--log` refuses pass > total.
  - Smallest change, and every 045-075 line stays valid (all have pass ≤ total, R-7/R-8).
  - It does not stop a 411/411-type slip, because the arithmetic is still done by hand, which is the RI-006 root cause.
- **B. Field is pytest's summary line, verbatim** (A1's "better" option, with the order fixed per P-2).
  - Example: `8 files changed | tests 411 passed, 1 skipped` (an optional ` in 64.87s` can be dropped or allowed).
  - Regex built from KNOWN_TYPES order: `(\d+ failed, )?\d+ passed(, \d+ skipped)?(, \d+ deselected)?(, \d+ xfailed)?(, \d+ xpassed)?(, \d+ warnings?)?(, \d+ errors?)?`.
    - Requiring `passed` refuses `no tests ran` (P-4).
    - Whether `0 passed` is possible, and whether an all-failed run prints `passed` at all, is UNVERIFIED: `_build_normal_summary_stats_line` loops over keys with reports, so a type with 0 reports is likely left out. I1 should check this on a fixture or on the installed pytest.
  - No arithmetic is done by hand, failures stay visible (fixes R-10), and the lines can be compared.
  - Needs a cutoff (e.g. `TESTS_FORMAT_FROM = 76`): items 045-075 keep the old regex in INCOMPLETE (R-3), and new items must use the new one.
  - The hint text, the fixtures and the pinned refusal strings all change (R-5).
- **C. Cross-check the log against 05.** The log's numbers must equal the last full-suite summary line pasted in 05's "Test output" section.
  - Closes the 072 gap.
  - But 05 holds many summary lines (mutations, single files, R-7/R-8 references), so choosing "the full-suite line" from text risks RI-012 (classifying by a substring of free text). It would need a fixed label in templates/build-report.md, like 070's TOTAL line.
  - Bigger, and it overlaps 077 (also check_pipeline.py).
- **D. `--log` runs pytest itself.** Rejected as out of scope:
  - about 60 s per run (`414 passed, 1 skipped in 64.87s`, logs/audit/2026-11-18-072.md L39);
  - the suite tests check_pipeline.py itself (recursive);
  - and the results depend on the machine (R-11).
- Under any option, the i2 text should say which run the field counts: the full suite, `python3 -m pytest -q` from the repo root (R-9). No option can detect a single-file run from the field alone, except that B shows `deselected` for `-k` runs (not for a file path). That limit should be written down.

## Open questions
1. Which option, A or B (with or without C)? B removes the hand arithmetic, which is the RI-006 root cause. A is the smallest change.
2. Under B, can the `in Ns` timing and trailing notes like `(round 2: ...)` (R-4) stay allowed, or must the field end at the summary?
3. Is the installed pytest version one with the `subtests` KNOWN_TYPES keys (P-2)? I1/I2 must check with `python3 -m pytest --version` (UNVERIFIED here).
4. Does the installed pytest print `0 passed` or leave `passed` out when every test fails (B regex)? UNVERIFIED.
5. Order with 077 and 079: both also change scripts/check_pipeline.py (brief: 075 -> 076 -> 077 -> 078 -> 079). 076's edits are LOG_FORMAT/LOG_HINT/write_log and a cutoff constant. 077 adds `BRANCH FAIL:` / `UNCOMMITTED STEP:` (work/077/request.md L10-13). Neither request names the same function, so a textual conflict looks unlikely, but this is UNVERIFIED until 077's plan exists.
6. Should the 058 line (R-8) be added to the RI-006 note as a second occurrence of the same slip? That is A1's decision in the daily review. Not edited here (brief rule).

Log fields: brief written | <sources count from `python3 scripts/check_handoff.py 076`>
