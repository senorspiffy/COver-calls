# 06 Verification - 053
Verdict: PASS
## I1 audit (plan vs research)
04's Rule trace covers 03 map steps 1–9, every Missing-inputs row (two DROPPED with reasons: the root-commit `C^1` cannot occur because the walk starts after the cutoff; no PBR screen PASS is claimed) and R3's three Self-check worked examples (fixtures a, h, g). Each of I1's seven changes has a source: 1–2 the four existing fixtures that assert `code == 0` in full repos without the real cutoff (would go red); 3 git-config `diff.renames` / git-diff `--no-renames` (extra research 1); 4 `classify()` L165–171 (042: last A1 FAIL = sent back); 5 closed lists `PRE_A1_LINE`/`LEGACY`; 6 R3's open question, decided from `RULE_PATHS` and the request's "code, config, tests or rules"; 7 03 fact rows (PBR reported 11-10 after the close), so `<` not `<=`, which fails safe. No unsourced additions. Not touched: the 001 rule text. Extra research 4 says the person's 040 rule ("estimated date = last report + `earnings_gap_days`", work/001/03-handoff.md L152) already means a report that has happened. I re-read L152 and agree. The merge-commit rule is one the person follows: it is in run-item.md and flagged in 05 "For the person".
## I2 audit (build vs plan)
`git show --stat 31d7d19` → the 9 planned files plus work/053/05 and the I2 log line. Line by line against plan "Files to create/change" 1–9:
- check_pipeline.py: `CODE_PATHS` (6 paths), `UNTRACKED_FROM = 694bf4d…` (= `31d7d19^1`, the commit holding 01–04, so the first code commit is the one that adds the constant), `_open_at`, `untracked_changes` (shallow/full split, `rev-list --first-parent --reverse`, `diff-tree -r --name-only --no-renames C^1 C`, 07 not in `STEP_FILE`), override note, `main()` parsing, exit term, docstring gaps (a)–(f). These match the plan. The deviations in 05 are two extra error branches (exit 1, never silent), usage text on a bare option, and a shared test helper. All three are stricter or equal, and I accept them.
- Tests: 12 new in test_pipeline_check.py, 1 in test_practice.py, 1 in test_paper.py (14, as planned). The 14 existing git-fixture runs pass `--untracked-from _root(...)`.
- run-item.md (new last paragraph) and a1-auditor.md L20 match plan files 3–4 (`grep -n 053` → 1 line each).
- tickers.json PBR: values unchanged; 3 source strings as plan file 5; no new keys. tickers.py `< day.date` guard and docstring line; missing.py text appended, effect `block`.
Connectivity re-done: `untracked_changes` is called from `main()`, `_open_at` from `untracked_changes`, `--untracked-from` is used only by fixtures, and the plain run uses the constant (my check_pipeline run below prints no override note). Missing-data grep over the `+` lines of `git diff -U0 694bf4d 31d7d19 -- ccbot/` → 0 hits, matching 05's "none new".
Ancestry: `merge-base --is-ancestor 694bf4d de5406c` → 1, `--is-ancestor de5406c 694bf4d` → 0, `--is-ancestor 694bf4d HEAD` → 0; `--is-shallow-repository` → false. `git show 3ba835e^:work/048/07-audit-task.md` → `A1 result: PASS (2026-11-07, …)`. `git diff --name-only de5406c^1 de5406c` → config/tickers.json, tests/test_practice.py, work/048/05-build-report.md (3 files, = 3ba835e's stat).

Guardrail would have caught the original error (BUG, step 3). Each probe ran in a scratch worktree under the session scratchpad, and all are removed (`git worktree list` shows only the repo):
- Worktree at de5406c, `check_pipeline.py --untracked-from 96b7f94` → `UNTRACKED CHANGE: de5406c config/tickers.json tests/test_practice.py (item 053: …) (cutoff 96b7f94 from --untracked-from)`, exit 1 (1 of 1).
- Worktree at HEAD, a 3ba835e-shaped commit after the real cutoff (append to work/048/05 + edit config/tickers.json), plain run → `UNTRACKED CHANGE: 8752fe7 config/tickers.json (item 053: …)`, exit 1. Reset afterwards.
- Worktree at HEAD, `--untracked-from 96b7f94` → only 87772a8 (the branch's merge of main, which brought 3ba835e) is flagged. e885a62 (051) and a541477 (052) are covered by their own items, so there are no false positives on 049–053's real commits.
- Worktree at origin/main (= HEAD's ancestor; `HEAD..origin/main` empty) with `merge --no-ff 31d7d19`, plain run → `UNTRACKED CHANGE: none`, exit 0 (the PR merge shape).

Mutations (plan check 6; scratch worktree; suite = test_pipeline_check + test_practice + test_paper, 64 tests; restored after each with `git checkout -- .`):
| Mutation | Result |
|---|---|
| drop `or (untracked and untracked[1])` from the exit | 7 failed: (a), (b), (c), (e), (g), (j), (k). The planned (a), (c), (g) are among them |
| `diff-tree --no-renames` → `-c diff.renames=true diff --name-only` | 1 failed: (k) `test_rename_out_of_code_path_is_flagged` |
| `_open_at`: drop the last-FAIL clause | 1 failed: (i) `test_a1_fail_item_covers_its_rework` |
| `_open_at`: drop the PRE_A1_LINE/LEGACY clause | 1 failed: (j) `test_legacy_and_pre_a1_items_never_cover` |
| tickers.py: remove the `< day.date` guard | 2 failed: `test_earnings_known_for_dec_18_on_2026_11_09`, `test_enrich_future_last_earnings_is_unknown` |
| tickers.py: `<` → `<=` | 1 failed: `test_enrich_future_last_earnings_is_unknown` (the 11-10 case) |
RI-002 probe (removed-default step): this item removed no default. The one fail-safe it adds is the guard, and removing it fails 2 tests (above). The standing probe also holds: `"foo_date": null` added to F in config/tickers.json → `test_ticker_fields_cover_file_and_code` fails (1 failed, 22 passed); restored.
RI-001: the feasibility counts are re-run by the tests that pin them. 11-09 → `{"PBR"}` (12 of 13) and 11-11 → `set()` (13 of 13) both pass, and both fail under the guard mutations. They match 03 Self-check, 04, 05 and the test docstrings ("12 of 13").
Minor, for A1 (not a FAIL): `test_untracked_from_is_fixed` uses bare `return` when git is missing or the clone is shallow, so the ancestry half passes silently instead of showing as skipped.
## Tests re-run (output)
```
$ python3 -m pytest -q
221 passed, 1 skipped in 25.35s
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars'
$ python3 scripts/check_handoff.py 053
sources count (unique URLs in 01-research.md): 13
fact-check rows: 55
totals line: 55 rows -> 48 as-is, 7 fixed, 0 removed
PASS
$ python3.11 -m py_compile scripts/check_pipeline.py ccbot/tickers.py && echo ok
ok
$ python3 scripts/check_pipeline.py   (before this file; exit 0)
053: in progress (FULL: next 06)
INCOMPLETE: none
LOG TIME: none (not checked: 048: …)
UNTRACKED CHANGE: none
ORPHAN LOG: none
SKIPPED: none
```
`tests/test_safety.py::test_every_py_compiles_on_oldest_python` ran (python3.11 on PATH, no python3.10) and passed. It is not the skipped test.
## Recurring issues checked (step 0)
Recurring issues checked: RI-007 (this item: the guardrail flags de5406c on real history and a 3ba835e-shaped commit after the real cutoff, exit 1; the exit-term mutation fails 7 tests), RI-002 (the guard fails safe to EARNINGS_UNKNOWN, the guard mutations fail 2 and 1 tests, the foo_date probe gives 1 failed, the missing-data grep finds 0 new hits, and no PBR value is filled), RI-001 (12/13 and 13/13 re-run by the pinned tests; the 1-of-1 commit count re-run), RI-008 (python3.11 py_compile ok; oldest-Python compile test ran), RI-009 / RI-011 (first-parent walk only, no merge-base; scratch merge into origin/main gives none), RI-010 (I1/I2 lines written by `--log` before their commits; this I3 line by `--log` right after this file), RI-006 (check_handoff PASS, 55 = 48 + 7 + 0), RI-003 / RI-004 / RI-005 (no new dates or worked examples; R3's three examples are fixtures a/h/g and pass).
RI-007: guardrail built and verified (053); GUARDED when merged and a commit shaped like 3ba835e after the cutoff gives `UNTRACKED CHANGE:` and exit 1 on main. On this branch the scratch probe already gives it.
RI-002: 053's report-day guard holds under mutation; whether the 3ba835e look-ahead is an occurrence is A1's call (05 "For A1").
## Pipeline line (step 2)
check_pipeline line: `053: in progress (FULL: next 07)` after this file; `053: awaiting A1 (FULL)` after 07 (exit 0, UNTRACKED CHANGE: none)
## Sent back / sent to Audit
Nothing sent back. Sent to Audit: yes (07-audit-task.md).
