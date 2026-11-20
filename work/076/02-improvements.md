# 02 Improvements - 076

Why the full language search and not N/A: 076 is a BUG item, but option B (R1) would build the log check from pytest's printed summary line. That line's format is an outside fact (a third-party tool's output), so the exception for "no new external claims" does not apply. Option A alone would have been N/A.

## What past logs say
- logs/audit/2026-11-18-072.md L72-76 (point 3): 072's `tests 411/411` should be `411/412`. The root cause is that `<total>` is undefined in i2-builder.md L25 and in LOG_FORMAT. A1 named this the RI-006 shape. L88-95 (P2) proposes both a written definition and, as "better", pytest's line copied verbatim.
- logs/recurring-issues.md L77-78, RI-006: GUARDED, plus a 2026-11-19 near miss (072 vs 073) that is not counted. R1 found a second case of the same slip (058, `218/218` for `218 passed, 1 skipped`, 01 R-8). Adding it to the RI note is A1's call, and is not edited here.
- A1's draft regex (072 audit L93) puts `passed` first. pytest prints `failed` before `passed` (01 P-2), so that regex would refuse 070's real line `1 failed, 383 passed, 1 skipped`. Do not copy it.
- RI-012 (recurring-issues.md L138-141) is about classifying by a substring of free text. It applies to option C (picking "the full-suite line" out of 05's text) unless 05 gets a fixed label.
- Precedent: R2 for 072 used "Languages: N/A" because its option A relied on no outside fact (work/072/02-improvements.md L43). This item differs because of option B (see top).
- The last full language cycle was 073 with German, Korean and Portuguese (logs/research/2026-11-18.md L9). So this cycle picks 3 others.

## 3 ways FOR
1. **Take option B, the verbatim summary line, because the format is easy to copy and check exactly.** This is the change that removes the hand arithmetic, which is RI-006's root cause.
   - The core order is stable. `KNOWN_TYPES` lists the same core keys in the same order in pytest 7.4.x (`"failed", "passed", "skipped", "deselected", "xfailed", "xpassed", "warnings", "error"`) and in 9.0.x and main [https://pytest.org/en/7.4.x/_modules/_pytest/terminal.html] [https://docs.pytest.org/en/9.0.x/_modules/_pytest/terminal.html].
   - A count of zero is never printed. `_build_normal_summary_stats_line` adds a part only `if reports:` [https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py]. So the regex can require strict order, with each type optional.
   - With `-q` the line has no `=` padding. The code sets `display_sep = self.verbosity >= 0` (same source), and the Japanese source shows a bare `4 passed in 0.02s`. I2 can paste the last line of `python3 -m pytest -q` as it is.
2. **B shows what `pass/total` hides.** Failures, xfails and skips are named, not folded into one number (01 R-10).
   - French and Italian tutorials both say an xfail test runs but is counted as neither passed nor failed: "il ne sera pas comptabilisé parmi les tests réussis ou échoués" [https://www.guru99.com/fr/pytest-tutorial.html].
   - So under option A, the definition must also list xfailed and xpassed, as R1's option A does. Under B the line names them, so there is nothing to define.
   - 070's `383/385` (1 failed and 1 skipped) would have read `1 failed, 383 passed, 1 skipped` (01 R-7).
3. **Improvement on R1's B regex: accept real lines that R1's version refuses.**
   - (a) An all-failed run. Zero counts are not printed (FOR 1), so a run with no passes prints `N failed in Xs` with no `passed` part. R1's `(\d+ failed, )?\d+ passed...` refuses it. Instead, require at least one known part, in KNOWN_TYPES order, with each type at most once. Refuse `no tests ran` and an empty field.
   - (b) The `subtests passed/failed/skipped` keys, which exist in 9.0.x and main but not in 7.4.x (FOR 1 sources). The installed pytest version is still UNVERIFIED (01 R-12), so either allow these keys or check `python3 -m pytest --version` in I1.
   - (c) Do not pin the timing. Older output reads `in 0.07 seconds` (guru99 fr/it) and current output reads `in 0.12s` (Russian docs). Allow an optional ` in <anything>`, then the existing trailing-note tail (01 R-4), and pin all of this with tests.
   - (d) Keep a cutoff constant (for example `TESTS_FORMAT_FROM = 76`) so the lines for 045-075 stay valid under INCOMPLETE (01 R-3).

## 3 ways AGAINST
1. **B on its own still does not catch the 072 slip.** If I2 retypes the line and leaves out the skip, `tests 411 passed` is well-formed under any B regex: `skipped` is optional because zero counts are not printed (FOR 1).
   - So B removes the arithmetic but not the omission. Only copying verbatim, or a cross-check (option C), closes that gap.
   - This is a reasoning chain from 01's "Numbers used" and the `if reports:` fact. The i2 text must say "paste the last line of the run as it is", and 05 should carry that same line under a fixed label, so that I3 and A1 can compare the two without RI-012-style text guessing.
2. **pytest's terminal text is human output, not a contract, and pytest is not pinned** (`dev = ["pytest"]`, pyproject.toml L13).
   - The text has changed between versions. The timing went from `seconds` to `s` (AGAINST evidence in FOR 3c), and 9.x added three `subtests` keys that 7.4.x lacks.
   - Unknown types are added at the end (`list(KNOWN_TYPES) + unknown_types`, main terminal.py), and a plugin can add them.
   - So a strict regex can refuse a true line after a pytest upgrade. That would make `--log` exit 2 in the middle of a step, a self-inflicted red.
   - Mitigation (reasoning, not a source): allow unknown `\d+ [a-z ]+` parts after the known ones, or accept that a refused line is loud and gets fixed in a follow-up.
   - The pass ≤ total check under A has no such coupling.
3. **Cost and churn compared with A.**
   - B needs a cutoff constant, a new hint text, and changes to the `FIELDS["I2"]` fixture and about 10 literal fixture lines plus 2 pinned hint strings (01 R-5). It also needs a RULES change to i2-builder.md, which needs the person's OK.
   - It splits the log history into two formats (045-075 `p/t`, and 076+ verbatim), so comparisons across the boundary need translating.
   - It edits the same file as 077 and 079 (brief), which raises the merge-order risk (01 Q5, UNVERIFIED until 077's plan exists).
   - Option A is a few lines and keeps one format. It does not fix the root cause (01 option A).

## Findings by language
Random languages this cycle: French, Russian, Italian (073 used German, Korean, Portuguese)

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | FOR: the order is fixed and zero counts are never printed, so a strict regex is possible. HOLE: unknown types are added at the end, and `-q` drops the `=` padding. | https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/terminal.py ; https://pytest.org/en/7.4.x/_modules/_pytest/terminal.html | `if reports:` ; `display_sep = self.verbosity >= 0` ; 7.4.x `KNOWN_TYPES = ( "failed", "passed", "skipped", "deselected", "xfailed", "xpassed", "warnings", "error", )` | (English source) A part is printed only when there are reports of that type. The `=` separator is used only at verbosity 0 or higher. 7.4.x has no `subtests` keys. |
| Mandarin Chinese | HOLE: skip reasons appear only with `-rs`, so a log note like 064's `(1 skipped: exchange_calendars)` is extra information, not part of the line. Keep the trailing-note tail allowed. Example line shows the skips counted. | https://cnblogs.com/a-wyw/p/16198885.html | 用-rs执行，跳过原因才会显示 ; `1 passed, 2 skipped in 0.04s` | Only when run with -rs are the skip reasons shown. |
| Spanish | HOLE (wording): a skipped test is in the plan but was not executed, so a definition that says "total tests run" is wrong for skips. Say "collected" or "reported", not "run". 01's "412 collected and run" should read "412 collected (411 run, 1 skipped)". Deselected tests are left out of the report entirely. | https://allurereport.org/es/docs/test-statuses | "Una prueba omitida (gris) es una prueba que fue incluida en el plan de pruebas pero que no se ejecutó." | "A skipped (grey) test is a test that was included in the test plan but was not executed." |
| Japanese | FOR: `-q` gives a compact line that is easy to paste verbatim. | https://enu23456.hatenablog.com/entry/2022/11/08/184211 | 「pytest -qすると、結果の出力文がコンパクトになる。」 ; `4 passed in 0.02s` | "When you run pytest -q, the result output becomes compact." |
| French | FOR: xfail runs but is counted as neither passed nor failed, so `pass/total` must list it and B names it. HOLE: tests can be filtered at run time, and filtered tests show as `deselected`, which is not part of any total. | https://www.guru99.com/fr/pytest-tutorial.html ; https://gouarin.github.io/python-packaging-2023/pytest | "Le test ayant échoué sera exécuté, mais il ne sera pas comptabilisé parmi les tests réussis ou échoués." ; "vous pouvez tagger vos tests (slow, skip, etc.) et les filtrer à l'exécution." | "The test marked as failed (xfail) will be run, but it will not be counted among the passed or failed tests." ; "you can tag your tests (slow, skip, etc.) and filter them at run time." |
| Russian | HOLE: a `-k` or `-m` run shows `deselected`, but a file-path subset shows nothing (01 R-9), so the field cannot prove a full-suite run. Also the current timing form is `in 0.12s`. | https://pytest-docs-ru.readthedocs.io/ru/latest/example/markers.html | "Опцию -k командной строки можно использовать, чтобы указать подстроку, которая должна присутствовать в именах тестов" ; `3 passed, 1 deselected in 0.12s` | "The -k command-line option can be used to give a substring that must be present in the test names." |
| Italian | AGAINST (format drift): an older-pytest example ends `in 0.07 seconds`, not `in 0.07s`, so do not pin the timing. FOR: the full order `failed, passed, skipped, xfailed, xpassed` matches KNOWN_TYPES. | https://www.guru99.com/it/pytest-tutorial.html | "Il test contrassegnato come fallito verrà eseguito, ma non verrà conteggiato come parte dei test falliti o superati." ; `1 failed, 1 passed, 2 skipped, 1 xfailed, 1 xpassed in 0.07 seconds` | "The test marked as failed will be run, but will not be counted as part of the failed or passed tests." |

## Holes to watch out for (summary)
- **Verbosity:** `-qq` (verbosity below -1) prints no summary line at all (main terminal.py, `summary_stats`, from the fetched source and paraphrased). The i2 text must name exactly `python3 -m pytest -q` from the repo root.
- **All-failed run:** it prints no `passed` part, so a regex that requires `passed` refuses a real line (FOR 3a). Whether I2 should ever log such a run is a policy choice for I1.
- **Omission:** B's regex cannot see a skip that was left out (AGAINST 1). Pair B with "paste as printed" and a fixed-label line in 05. A cross-check against 05 (C) needs that label to avoid RI-012.
- **Unknown or plugin types and the `subtests` keys:** decide whether to allow them or refuse them. The installed pytest version is UNVERIFIED (01 R-12). Whether a `pytest_terminal_summary` hook can print lines after the stats line, so that "the last line" is not the stats line, is UNVERIFIED.
- **`warnings` and `deselected`:** neither is a test count. Never add them to a total under A (01 P-5, P-9).
- **Wording of A's definition:** say "collected" or "reported", not "run". Skips are not executed (Spanish row).
- **Single-file runs** (065's `49/49`) cannot be detected from the field under either option. Write that limit down (01 R-9).
- **Cutoff:** without `TESTS_FORMAT_FROM` (or an equivalent), tightening the regex turns the lines for 045-075 INCOMPLETE and main goes red (01 R-3).

Log fields: 3 for / 3 against | languages: English, Mandarin Chinese, Spanish, Japanese, French, Russian, Italian
