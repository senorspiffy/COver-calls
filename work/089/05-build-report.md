# 05 Build report - 089
Base: daily-fixes/2026-11-21 at 4a6cdc8 (088 I3), then 33add8e (A1's 088 commit: logs/audit + work/088/07 only; `git diff --stat 4a6cdc8 33add8e -- scripts tests` is empty). Every line was re-found by its text, not by 04's line numbers.

## Changes made (file: what changed)
- scripts/check_pipeline.py
  - New `_UNREAD = {}`, `_shown(path)` and `_read(path, missing_ok=False)` (04 Files 1-3). The reader is `read_bytes().decode("utf-8")`, then `.replace("\r\n", "\n").replace("\r", "\n")`. It catches `(OSError, UnicodeDecodeError)`; with missing_ok, FileNotFoundError gives (None, None); anything else gives `(None, "<shown> unreadable")` and records `not UTF-8 at byte <n>` or the exception class name.
  - `read_request` deleted (Grep: no other caller in scripts/ or tests/). `classify` and `real_data_field` now call `_read` + `parse_request`. classify reads request.md once (FAST check uses the same text).
  - `_i3_verdict_text(text)` added; `i3_verdict(path)` kept as a wrapper ((None, None) when unreadable).
  - `classify`: request.md / 06 / both 07 sites unreadable → `("UNREADABLE", why)`.
  - `_log_text` → `(text, whys)`; `uncommitted_steps` → `not checked (<whys>; item 089)`, False.
  - `incomplete`: 06 read once (`06 not checked (...; item 089)` replaces the RI-line, verdict and I3-line checks); log whys → one `log lines not checked (...; item 089)` entry for an item with any 01-06 file, replacing the unlogged, format, Suite and I3-line checks; Suite block reads 05 via `_read` (`05 not checked (...)`). Probe anchor `            elif suites[0] != field:` is byte-identical (C12 green).
  - `_last_log_line`, the I3 loop, `_sent_back`, `_item_lines`, `_run_seconds`: try/excepts replaced with `_read` and the same result.
  - `orphan_log_lines` → `(orphans, whys)`; main prints the two 04 change-2 forms.
  - `open_branches`: `mine_text` via `_read`; compare `theirs != mine_text`; `                clashes.append(item)` byte-identical.
  - `_shallow_boundaries`: common-dir failure → `"unreadable" if sure else "full"`; `_read(..., missing_ok=True)`; why → "unreadable" always; missing → `"unreadable" if sure else "full"`; docstring (item 089). No git call added or removed (GIT_CENSUS total 47 unchanged).
  - `research_code.request_text_of`: `_read`; an unread item's flag detail becomes `RESEARCH ONLY check: <why> (item 089)` (keyed by item, never by matching the detail text, RI-012).
  - `real_data_field`: request unreadable → `request.md not checked (<why>; item 089)` and 05/06 still checked; 05/06 unreadable → `<step> not checked (<why>; item 089)`.
  - `_inbox_gate` working template and `inbox_section` newest report: the 04 Files 17/18 texts.
  - `main`: `_UNREAD.clear()` first; the UNREADABLE line after `inbox_section()` and before INBOX; `or unreadable` in the final return only.
  - Module docstring: UNREADABLE (item 089) paragraph, written from the code.
- tests/test_pipeline_check.py
  - `_run3`, `_tree`, `_pick1`, constants LOG/BAD/CLEAN_LOG; 20 new tests (04 Tests table, names below); test (c) gains the three 04 asserts; N13 gains the 6f `_run3` asserts; GIT_LINES gains `"RULE NOT SEEN:"` (E1, see Deviations 1).

File counts:
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → `0`
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → `2`

## Connectivity check
- [x] every new function/rule is used: `_read` has 21 call sites (every former read); `_shown` is called by `_read` (key and why); `_i3_verdict_text` by `i3_verdict`, `classify`, `incomplete`; `_UNREAD` is filled by `_read`, cleared and printed by `main`, and feeds `unreadable` → exit; `_run3`/`_tree`/`_pick1` used by the new tests.
- [x] every input has a source, every output has a consumer: each `why` goes into a printed line (classify line, INCOMPLETE, UNCOMMITTED STEP, ORPHAN LOG, LOG BATCH, REAL-DATA FIELD, RESEARCH CODE, INBOX) and every unread path into UNREADABLE + exit 1.
- [x] every branch ends in a defined result: `_read` success / missing_ok-missing / failure; `_shallow_boundaries` common-dir failure / why / missing / text; classify request / 06 / 07 failure → UNREADABLE; open_branches classify of a tmp copy returning UNREADABLE is not SKIPPED/FAIL but its path is on UNREADABLE (exit 1), so not silent. The `_last_log_line` / I3-loop skips are reachable only by a race (they run only when `_log_text` read every file) and the race's file is still on UNREADABLE.
- [x] no leftover TODOs or unused files: `grep -n TODO scripts/check_pipeline.py` → no output; `read_request` removed with its last caller.

Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 38 hits, all pre-existing; `git diff --stat -- ccbot/` is empty, so no new or changed hit. The same pattern over my diff of scripts/check_pipeline.py gives:
- docstring text "06 or 07" (x2): words, not code.
- `elif ver_text is not None and not re.search(...)`: ver_text is None only when 06 is absent (no check) or unreadable (handled by the branch before, with an entry).
- `ok = tpl_text is not None and INBOX_HEAD.search(...)`: None only when the template is missing, which keeps today's `not checked (... has no ## Inbox)`; unreadable returns before it.
- `if verdict is not None and not log_whys`: the I3-line compare runs only on a readable verdict and full logs; a lost log already has its entry.
- `... or env_failed or unreadable else 0`: the exit code; `unreadable` only adds a route to 1.
No new dataclass or numeric default; no new `>`/`<` test.

Feasibility numbers (04 Guardrail tests):
- read census: 22 raw reads before (21 `read_text(` + 1 `.open(`, Grep on 4a6cdc8) → 2 after (`test_read_census`: `{("_read","read_bytes"): 1, ("write_log","open"): 1}`).
- byte offsets: 0 (6a, 6l, T-is, T-ig), 5 (6c), 12 (6d), 41 (test (c)): each asserted and passing.
- CHECKLIST_FROM bound: 6e, 040 gets no INCOMPLETE entry, 150 gets exactly one (`INCOMPLETE: 150 (log lines not checked (logs/implementation/2026-11-19.md unreadable; item 089))`).
- exit isolation: 6a clean twin exit 0 / bad twin exit 1; 6d INCOMPLETE none, exit 1.
- globs: unchanged code (`*.md` in `_log_text`, `????-??-??.md` elsewhere).
- GIT_CENSUS: total 47, unchanged (test_git_call_census passes).

## Test output (pasted, not summarized)
Full suite, repo root, 2026-11-22 ~00:10 UTC, after the last edit:
```
$ python3 -m pytest -q
........................................................................ [ 92%]
...................................................                      [100%]
698 passed, 1 skipped in 88.82s (0:01:28)
```
Suite: 698 passed, 1 skipped in 88.82s (0:01:28)

Before the build, 088's 05 reports `678 passed, 1 skipped`; +20 = the 20 new tests: test_read_contract, test_read_census, test_unreadable_log_exits_1_alone (6a), test_unreadable_log_directory (6b), test_unreadable_06 (6c), test_unreadable_request (6d), test_unreadable_log_consumers_say_not_checked (6e), test_cr_only_07_reads_as_lines (6h), test_unreadable_cleared_between_runs (6i), test_unreadable_printed_before_inbox_early_return (6j), test_orphan_log_with_unreadable_file (6k), test_unreadable_07 (6l), test_unreadable_05_at_suite_check (6m), test_shallow_file_unreadable_whatever_the_flag (T-sh), test_real_data_field_unreadable_request_and_05 (T-rd), test_research_code_unreadable_request (T-rc), test_unreadable_request_still_clashes (T-ob), test_inbox_unreadable_daily_report (T-is), test_inbox_unreadable_working_template (T-ig), test_sent_back_unreadable_log_is_no_send_back (T-sb2). 6f is inside N13 (04 row "N13 (edit) ... plus the 6f `_run3` assert").

Other checks:
```
$ python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py && echo "py311 compile OK"
py311 compile OK
$ python3 -m pytest -q tests/test_pipeline_check.py tests/test_probe_guardrails.py
344 passed in 40.65s
```

E1 (tests (a), (b), (c) with `"RULE NOT SEEN:"` in GIT_LINES), on the build: all three pass (in the full suite above; also `-k "non_utf8_shallow_line or all_git_fails or malformed_shallow_real_git_nothing"` on the scratch copy → 3 passed before the probe). With M7 put back (scratch), (c) fails at the GIT_LINES loop on `RULE NOT SEEN: none` (`1 failed, 2 passed, 327 deselected in 1.65s`), so E1 has teeth after the decode change, as 088/06 Deviation 1 predicted.

Mutations: scratch worktree `/tmp/claude-0/scratch/i2-089/wt` (git worktree add --detach at 33add8e plus my two files), one mutation at a time, `python3 -m pytest -q tests/test_pipeline_check.py`; worktree removed after (`git worktree list` no longer shows it).

| ID | Result | Failing tests |
|---|---|---|
| M1 catch OSError only | 20 failed, 310 passed | incl. test_unreadable_log_exits_1_alone (6a), test_read_contract, test (c) |
| M2 catch UnicodeDecodeError only | 5 failed, 325 passed | test_unreadable_log_directory (6b), test_read_contract, test_shallow_file_unreadable_whatever_the_flag, test_shallow_file_unreadable_not_checked, test_shallow_flag_unknown_no_file_is_full |
| M3 `or unreadable` dropped | 6 failed, 324 passed | test_unreadable_log_exits_1_alone (6a), 6b, 6d, 6i, 6l, T-ob |
| M4 `_UNREAD.clear()` dropped | 2 failed, 328 passed | test_unreadable_cleared_between_runs (6i), 6j |
| M5 classify request.md back to read_text | 3 failed, 327 passed | test_read_census, 6d, T-ob |
| M6 UNREADABLE printed after the INBOX early return | 2 failed, 328 passed | test_unreadable_printed_before_inbox_early_return (6j), 6a (line order) |
| M7 shallow why → `"unreadable" if sure else "full"` | 2 failed, 328 passed | test_non_utf8_shallow_line_no_traceback (c), T-sh |
| M8 shallow failure not recorded | 2 failed, 328 passed | (c), T-sh |
| M9 orphan whys dropped | 2 failed, 328 passed | 6a, 6k |
| M10 incomplete computes from "" | 1 failed, 329 passed | test_unreadable_log_consumers_say_not_checked (6e) |
| M11 newline normalisation dropped | 2 failed, 328 passed | test_cr_only_07_reads_as_lines (6h), test_read_contract |
| M12 why text changed | 13 failed, 317 passed | incl. test_batch_unreadable_log_file_makes_every_item_not_computable (N13), test_batch_unreadable_06_is_not_computable (N11) |
| M13 clash skipped when mine unreadable | 1 failed, 329 passed | test_unreadable_request_still_clashes (T-ob) |
| M14 classify 06 unreadable → verdict None | 1 failed, 329 passed | test_unreadable_06 (6c, its 151 case; see Deviations 2) |
| M15 real_data_field skips unreadable request | 1 failed, 329 passed | test_real_data_field_unreadable_request_and_05 (T-rd) |
| M16 research_code drops the unread detail | 1 failed, 329 passed | test_research_code_unreadable_request (T-rc) |

Step 10, whole-output diff on the real repo (cwd /home/claude/cover-calls, no args, after `git fetch origin`; before = `git show HEAD:scripts/check_pipeline.py` at 33add8e (same script as 4a6cdc8), after = the working-tree build):
```
$ python3 /tmp/claude-0/scratch/i2-089/tools/base.py > before.txt; echo "base exit $?"
base exit 0
$ python3 scripts/check_pipeline.py > after.txt; echo "build exit $?"
build exit 0
$ diff before.txt after.txt
109a110
> UNREADABLE: none
```
Exactly one added line, between ORPHAN LOG and INBOX (111 → 112 lines); no real unreadable file in the repo. RI-013: met.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: scripts/check_pipeline.py, tests/test_pipeline_check.py; neither is in TRIGGER/TRIGGER_DIRS)

## Deviations from plan
1. **E1 added (GIT_LINES gains `"RULE NOT SEEN:"`).** 04 L10 assumed it was already in and L157 said GIT_LINES unchanged; it was not in at d6715d5. 088's I3 deferred it to 089 (work/088/06 Deviation 1, 07 point 3), and the orchestrator told me to apply it after the decode change. Applied after `_shallow_boundaries`; (a), (b), (c) pass; the M7 probe shows (c) then catches `RULE NOT SEEN: none`.
2. **6c gets a second item (151, complete with ALL, 06 not UTF-8).** In 04's 6c tree, item 150 has only request.md + 06, so classify returns SKIPPED (missing 01-05) before it reads 06. M14 would then survive 6c, and 6l covers only the 07 sites. The 151 case asserts `151: UNREADABLE (work/151/06-verification.md unreadable)`, and M14 fails on it. 150's INCOMPLETE entry is also `no log line for I3` (its 06 has no I3 log line), so the assert pins the whole entry. This is a test addition only, with no code change. I3: please judge it.
3. 6f is implemented inside N13 (one test, as 04's N13 row says), not as a separate test.
4. T-sh resets `_UNREAD` with `.clear()` between stages after one `monkeypatch.setattr(cp, "_UNREAD", {})`, as 04's research note asks.
No other deviation.

Follow-ups (04 / 03 step 9):
- scripts/check_handoff.py L55/L62 still read strictly (03 row 63); A1 to open an item today.
- 091 point 1's per-exit-term tests: 089's `unreadable` term is already pinned by 6a/M3; 091 should not add a duplicate.
- 090: any new read must go through `_read`; test_read_census fails otherwise.

Recurring issues checked:
- RI-001 (ESCALATED): every count above is from a run (census 22 → 2, offsets 0/5/12/41, 6e's 040 bound, 16 mutations, diff 1 line). Nothing is assumed: 04's 6c claim for M14 was computed and is false (Deviation 2).
- RI-010 (ESCALATED): my log line is written only with `check_pipeline.py --log`, right after this file, then committed with 05 and the code in one commit.
- RI-014 (OPEN): this item. A non-UTF-8 or unreadable shallow file is never "full" now (M7/M8 fail (c) and T-sh); with E1, RULE NOT SEEN is in GIT_LINES. No reader can raise or compute from "" (M1/M2/M10).
- RI-002 (GUARDED): ORPHAN LOG and ID CLASH are never a bare none for lost input (M9, M13); real_data_field and research_code stay strict (M15, M16).
- RI-012 (GUARDED): the detail comes from the exception class and `err.start`. The research_code replacement is keyed by item, never by matching the detail text.
- RI-013 (GUARDED): whole-output diff above (one line).
- RI-008 (GUARDED): py_compile with python3.11 OK.
- RI-009 (GUARDED): mutations only in the scratch worktree (removed). I staged only my own files.
- RI-006 (GUARDED): file counts come from the commands above. The Suite line was copied from the pytest output.

Guardrail status (A1 copies on main, item 036):
- RI-014: guardrail extended (089). The shallow file decode error is "unreadable" whatever the flag (M7/M8 → test (c), T-sh), and every repo read is `_read` (census, M5). GIT_LINES includes RULE NOT SEEN (E1). Status unchanged until merged: OPEN.
- RI-002: unchanged, GUARDED. 089 adds `not checked` forms (M9, M13, M15, M16 fail named tests).
