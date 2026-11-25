# 04 Build plan - 070
Fit verdict: FIT WITH CHANGES

Fit check. This is pipeline tooling only. No ticker, premium, cap, 001 rule or broker path changes, so the ~$3k account is unaffected and no 001 text needs an update. Nothing connects to a brokerage. It fits the existing code: it reuses `_git`, `_walk`'s error tuple, `STEP_FILE`, `parse_request` and the `incomplete()` → `unfinished` → exit 1 path (check_pipeline.py L469-488, L586-588, L613-615, L654). It does not loosen 053/062. This is a RULES BRANCH (scripts/check_pipeline.py and templates/ are in RULE_PATHS, L146) stacked on PR #30, so the person must OK the PR, and it merges after #30. Changes to 03:

- **C1 (merge with 069).** 069/04 C1 plans its check_pipeline.py hunks around 070's: it leaves L650 and L654 alone, inserts in main only between L652 and L653, puts its constants after LEGACY (L181-183), its function after `next_id()` (after L562), and its docstring after L112. 070 must therefore use only these spots in check_pipeline.py: constants after LOG_TIME_EXCEPT (after L144, before RULE_PATHS); the docstring entry after the RESEARCH CODE entry (after L110, before the `--next-id` paragraph at L111); new functions after `research_code()` (after L540, before `MAIN =` at L543); main hunks only at L588 (add `real = ...` after `research = ...`), L613 (gaps line), after L650 (new print) and L654 (return). L651-653 stay untouched. **Tests go in a new file `tests/test_real_data_field.py`**, not at the end of tests/test_pipeline_check.py, because 069 appends its 11 tests to that file and two appends at EOF conflict. The new file imports the helpers (`from test_pipeline_check import _item, _git, _run, _history, _write, _commit, NO_GIT, ALL, _cp`). The repo already does this (tests/test_paper.py L8 imports from test_webull_sandbox).
- **C2 (missing absent-case tests).** 03's Missing inputs table has 4 rows with no test: git log failure, triggered ID with no request.md, no 05, and RESEARCH ONLY skip. Added as T15-T18 (below). The total is 18 functions, 21 collected.
- **C3 (T9 precision).** "Left ends in Constant config" means: a `BinOp(op=Div)` whose right is a str Constant, and whose left is `Constant("config")` or a `BinOp(op=Div)` whose right is `Constant("config")`. That matches realtest L60-61 (`ROOT / "config" / "default.json"`) and expiries L10 (`... .parents[1] / "config" / "holidays.json"`). T9 asserts that the derived set **equals** `set(TRIGGER)`, not just ⊆, so a stale extra entry fails too. Today both are 8.

## Extra research (with sources)
1. `--no-merges`: "Do not print commits with more than one parent. This is exactly the same as `--max-parents=1`." (https://git-scm.com/docs/git-log, fetched 2026-11-17). This confirms D3. A merge's own conflict resolution is not shown, which is gap (m), already listed.
2. Cross-test import (C1). In pytest's default `prepend` import mode, the first directory upward with no `__init__.py` (here tests/) goes on sys.path, so a test module can import another one by name (https://docs.pytest.org/pythonpath.html). tests/ has no `__init__.py` (Glob), and tests/test_paper.py L8 already relies on this.
3. Edge case R3 missed. realtest also reads data/real/BXM_History.csv (realtest.py L10 docstring). It is under the `data/real/` prefix, so it is covered. There is no other path literal (Grep `"config"`/`data/real` in the 6 modules: 3 config hits + L857).

## Files to create/change
1. `scripts/check_pipeline.py` (placement per C1):
   - After L144: `WHOLE_DIFF_FROM = 70`, `TRIGGER` (8 paths), `TRIGGER_DIRS = ("data/real/",)`, `REAL_DATA_FIELD`, and `TOTAL_LINE`, all exactly as in 03 step 1, each with an item-070 comment.
   - After L540: `_triggers(files)`, `_field_gap(text)` (03 step 2), `_item_triggers(cutoff)` (03 step 3: a single `git log --no-merges --no-renames --name-only --format=%x01%H <cutoff>..HEAD`, split on `\x01`, first line = sha, the remaining non-empty lines = files), and `real_data_field(cutoff, walked)` (03 step 4). `walked` is `None` without git. Otherwise `walked[1]` is `_walk`'s error. Return `(text, {ID: [entries]}, failed)`.
   - main: L588 `real = real_data_field(cutoff, walked)`; L613 `gaps = incomplete(d) + (real[1].get(d.name, []) if real else [])`; after L650 `print(f"REAL-DATA FIELD: {'not checked (no git)' if real is None else real[0]}")`; L654 add `or (real and real[2])`.
   - Docstring entry after L110: 03 step 6 text, with gaps (m)-(t).
2. `tests/test_real_data_field.py` (new): T1-T14 as in 03 step 8 (T9 per C3), plus:
   - **T15** git log fails: in-process, `monkeypatch.chdir(repo)`, wrap `check_pipeline._git` so that a call whose first arg is `"log"` returns `("", 128)`. Then `real_data_field(cutoff, _walk(cutoff))` == `("git log failed (item 070)", {}, True)`.
   - **T16** a commit with work/162/01-research.md + ccbot/realtest.py and no request.md → `REAL-DATA FIELD: 162 (no work/162/request.md here)`, exit 1.
   - **T17** 160 with 01-04 committed together with ccbot/realtest.py, no 05 → `INCOMPLETE: 160 (no 05 for <sha7> changes ccbot/realtest.py (item 070))`.
   - **T18** RESEARCH ONLY 163 with a trigger commit → no `163` in REAL-DATA FIELD (`none`); RESEARCH CODE names 163 (062's).
3. `templates/build-report.md` L10 and 4. `templates/verification.md` L8: the 03 step 7 replacement text.

## Tests and checks
- `python3 -m pytest -q tests/test_real_data_field.py`: 21 passed. Full suite = base + 21 (I2 pastes both counts from pytest). `test_repo_pipeline_has_no_skipped_items` still passes.
- Mutations (scratch copy, 03 step 8): first-parent units → T6 fails; file-wide TOTAL → T5; comments kept + substring → T2; `data/real/` removed → T11; `ccbot/pricing.py` removed → T9; an extra TRIGGER entry `ccbot/data.py` → T9 (C3 equality); `## ` in a fence ends the section → T12a; cutoff check removed → T7; RESEARCH ONLY skip removed → T18.
- Real-repo probe, 03 step 9: `REAL-DATA FIELD: none`; the rev-list count and the `time` before/after are pasted; the cutoff-63 positive control (expected 063, 065) is pasted with the actual line.
- `python3.11 -m py_compile scripts/check_pipeline.py tests/test_real_data_field.py` where available (RI-008).
- Merge probe (I2/I3, scratch): once 069 is built, `git merge-tree --write-tree` of the 069 and 070 branches shows no conflict in scripts/check_pipeline.py or tests/. If 069 is not built yet, A1 runs it.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 constants + `_triggers` | File 1, after L144 / L540 |
| Step 2 `_field_gap` (comments dropped, fences, section bounds, TOTAL fullmatch) | File 1; T1, T2, T4, T5, T10, T12 |
| Step 3 `_item_triggers` (non-merge, one git log, union, sha7) | File 1; T6, T11 |
| Step 4 `real_data_field` (no git / cutoff error / log fail / no request / RESEARCH ONLY / no 05 / 05 / 06 / 06 absent) | File 1; T8, T14, T15, T16, T18, T17, T2, T13 |
| Step 5 main wiring + exit | File 1 main hunks (C1 lines); T1, T2, T8, T16 |
| Step 6 docstring gaps (m)-(t) | File 1 docstring after L110 |
| Step 7 template comments | Files 3, 4 (grep checks from 03) |
| Step 8 tests + mutations | File 2 (+ C2, C3) |
| Step 9 real-repo probe + 069 hand check | Tests and checks |
| D1 8 paths + data/real/, not whole config/ | TRIGGER/TRIGGER_DIRS; T3, T9, T11 |
| D2 TOTAL proves a paste only | Docstring gap (o); no SHA parsing |
| D3 non-merge attribution | T6 + mutation |
| D4 INCOMPLETE + REAL-DATA FIELD line | main print after L650 |
| D5 fences | T12a/c |
| D6 commits only | Docstring gap (s) |
| D7 cutoff 70 | WHOLE_DIFF_FROM; T7 |
| Fact-check F6/F19/F22/02-FOR-2 corrections (fenced TOTALs, data/real/ outside 053, templates/ in 070, diff_dirs) | T12, gap (p), probe, T10 |

## Guardrail tests
- Feasibility: TRIGGER (8 paths, derived 2026-11-17 from realtest L54-61 + 3 config literals) → T9 (equality + existence). data/real/ prefix (1 literal, L857) → T11. Cutoff 70 (real repo 2026-11-17: 1 item ≥ 70, 0 touching TRIGGER → `none`, an empty result stated in 03) → T7 + the cutoff-63 positive control (expected 2: 063, 065). TOTAL matcher (4 of 4 real sections match, 03 step 2) → T10 tied to diff_dirs.
- Missing inputs: no git → T8; cutoff unusable → T14; git log fails → T15; no request.md → T16; no 05 → T17; 06 absent → T13; heading missing → T12b; blank/placeholder body → T2, T4; unclosed fence → T12c; no Scope line → FULL default (parse_request, existing); RESEARCH ONLY → T18.

## Expected result
The real repo shows `REAL-DATA FIELD: none`, no new INCOMPLETE line, and exit unchanged. From 070 on, an item whose own non-merge commits touch the 8 TRIGGER paths or data/real/ is INCOMPLETE until its 05 (and its 06 once that exists) has a diff_reports TOTAL line in the Real-data effect section. The templates point at TRIGGER. The 069 and 070 branches merge without conflict.

Recurring issues checked (item 013): RI-001 (ESCALATED): every selector has a dated count, and the empty real result is stated with a positive control. RI-002 (ESCALATED): every absent input has a named result and a test (C2 closes 4 untested rows). RI-013 (OPEN): this closes its "→ 070" gap. It does not prove the paste is current (gap o). RI-010 (GUARDED): script check + ID cutoff. RI-007: 053/062 unchanged, T18. RI-008: stdlib only, py_compile 3.11. RI-012: TOTAL is a fullmatch tied to diff_reports (T10). RI-011: no branch diff change.
