# 04 Build plan - 092
Fit verdict: FIT WITH CHANGES

I1 read the branch copy of .claude/agents/i1-reviewer.md, logs/recurring-issues.md, work/092/request.md and 01-03, all of scripts/check_handoff.py, and scripts/check_pipeline.py L350-361, L463, L510-543 and L720-732. In tests/test_pipeline_check.py it read L1-70, L155-170, L420-432, L1190-1193, L2598-2615 and L3733-3829. I1 has no shell (item 072), so nothing was run.

Fit: this suits a ~$3k account. It is a checker-only BUG fix: nothing changes in ccbot/, config/ or data/, and no strategy rule (001 slack, tolerance or cap) is touched. It fits the existing code because it re-uses 089's `cp._read` contract unchanged. It does not conflict with work built later on this branch. A grep of work/093-098 finds no request that touches check_handoff.py. 093 edits check_pipeline.py's docstring at L162-175 and L1292-1300, not L360. Items 093-098 come after 092, so their new tests append after 092's.

The verdict is "with changes" because of three additions to the 03 map, none of which changes R3's design: (1) the `sys.path` insert is guarded so it does not grow once per item under `--all`; (2) a new fixture (f) for a bad 01 next to a good 03 under `--all`; (3) an absent-01 assert, because the 03 map pins no absent-01 case. All three are below.

## Extra research (with sources)
1. **The newline rule matches, so a PASS cannot turn into a FAIL.** Python's `open()` docs say: "if *newline* is `None`, universal newlines mode is enabled. Lines in the input can end in `'\n'`, `'\r'`, or `'\r\n'`, and these are translated into `'\n'`". Source: https://docs.python.org/3/library/functions.html#open, fetched 2026-11-24. `read_text` uses the same rule (01 F1: "params as in open()"). `cp._read` does `.replace("\r\n", "\n").replace("\r", "\n")` (check_pipeline.py L535). For every readable 01 or 03 the text is therefore the same as today, and the switch cannot change `section()`, `fact_rows()`, `TOTALS_RE` or `unique_urls()` results on real files. I2 confirms this with the `--all` run (Tests, check 4).
2. **One module object, so the h2 monkeypatch still reaches the call.** The import docs say: "The first place checked during import search is `sys.modules`. ... During import, the module name is looked up in `sys.modules` and if present, the associated value is the module satisfying the import". Source: https://docs.python.org/3/reference/import.html (5.3.1), fetched 2026-11-24. The test helper `_cp()` (tests L1190-1193) and h2 (L2605-2607) both import it under the plain name `check_pipeline`. So `import check_pipeline` inside check_handoff returns the same object that h2 patches. Because `cp.open_branches()` is looked up at call time, the patch applies (03 FOR 1, now sourced).
3. **Edge case R3 missed: a bad 01 next to a good 03 under `--all`.** `main` reads 01 whenever it runs, and under `--all` it runs for every folder that has a 03 (L114-125). A bad 01 with a good 03 crashes `--all` today. After the fix the 01 problem goes into `problems`, so check_all must report it as `FAIL`, even though all of the 03 checks pass. No 03 fixture covers this: (a) has no 03, and (b)-(e) have a good 01 or none. I1 adds fixture (f).
4. **Edge case: the `sys.path` insert repeats.** Today `_branch_with_handoff` inserts the scripts dir every time it is called (L94). If `_pipeline()` is called from `main` for each `--all` item, sys.path grows by one entry per item. That is harmless but untidy. `_pipeline()` inserts only when the dir is not already in `sys.path`.
5. **Edge case: absent 01 with a good 03.** The 03 Missing inputs table says a missing 01 gives "no sources line, as today", but no map step pins it. The clean items in fixture (c) are given no 01, and each asserts no `sources count` line plus `PASS`.

## Files to create/change
3 files. All are in RULE_PATHS (check_pipeline.py L463) or are tests, so the person's OK is needed at PR review.

1. **scripts/check_handoff.py**
   - `_pipeline()` (new). It sets `here = str(Path(__file__).resolve().parent)`, runs `if here not in sys.path: sys.path.insert(0, here)`, then `import check_pipeline` and `return check_pipeline`. There is no `from check_pipeline import` anywhere in the file.
   - `UNREADABLE_PROBLEM` (new module constant): `re.compile(r"\S+ unreadable \((?:not UTF-8 at byte \d+|[A-Z]\w*Error)\)")`.
   - `main(item)`
     - Call `cp = _pipeline()` after the `base.is_dir()` check. The usage path in `__main__` still exits before `main` runs.
     - **01 read:** `text01, why01 = cp._read(research, missing_ok=True)`.
       - If `why01`: `p = f"{why01} ({cp._UNREAD[cp._shown(research)]})"`, indexed directly with no `.get` default. Print `sources count (unique URLs in 01-research.md): not computed (<p>)` and append `p` to `problems`.
       - Elif `text01 is not None`: print the count as today.
       - `unique_urls` is never called on None.
     - **03 read:** `text, why03 = cp._read(handoff, missing_ok=True)`.
       - `(None, None)`: print `no <handoff>; nothing else to check`, then the `FAIL:` lines and `<n> problem(s)` if there are any problems. Return `1 if problems else 0`.
       - `why03`: append `f"{why03} ({cp._UNREAD[cp._shown(handoff)]})"`, print every `FAIL: ` line and `<n> problem(s)`, and return 1 before `section()` runs.
       - Readable: as today. An earlier 01 problem stays in `problems`, so the item ends `FAIL` and exits 1 even if all of the 03 checks pass.
     - Use one small `_report(problems)` helper (or an inline loop) so all three exits print `FAIL: ` in the same way.
   - `_branch_with_handoff`: `cp = _pipeline()` and then `found = cp.open_branches()`. The rest is unchanged.
   - `check_all`: change the LEGACY branch to `elif d.name in LEGACY and not any(UNREADABLE_PROBLEM.fullmatch(p) for p in problems):`. Otherwise the item falls through to `FAIL`. Use fullmatch, never a substring (RI-012).
   - Module docstring (L2-13) names:
     - the `not computed (...)` sources line;
     - `FAIL: <path> unreadable (<detail>)` with exit 1;
     - the claim, worded exactly: "no traceback on an unreadable 01 or 03; work/ listing errors under --all may still raise";
     - that an unreadable file is never LEGACY;
     - that the script depends on scripts/check_pipeline.py importing cleanly.
   - Every f-string must parse on Python 3.10: no reused quote type inside `{}` (RI-008).
2. **scripts/check_pipeline.py** (docstring only, L360)
   - Replace "Known gap: scripts/check_handoff.py still reads its files strictly." with the gaps that remain:
     - check_handoff reads 01 and 03 through `_read` (item 092);
     - `--all` never reads the 01 of an item with no 03 (01 F17);
     - check_handoff ignores the `why` from open_branches' `_read` of request.md (01 F22, L85-87).
   - No code change.
3. **tests/test_pipeline_check.py**
   - New tests go after `test_unreadable_log_exits_1_alone` (L3812 block) and re-use `BAD`.
   - `_run3h(root, *args)`: same body as `_run3`, but runs `scripts/check_handoff.py`. `_run3` is unchanged.
   - `_h03(d, body=b"")`: writes a clean 03 (header, `|---|`, one data row, `1 rows checked → 1 VERIFIED as-is, 0 fixed, 0 removed`, `## Self-check`) prefixed with `body`. Writes it UTF-8 encoded.
   - Fixture tests (a)-(f), one function each, each with its clean twin (see Tests and checks).
   - `test_unreadable_problem_fullmatch_only`.
   - `test_handoff_read_census`.
   - `test_r1_log_refuses_not_computed`.

## Tests and checks
Every subprocess fixture runs `_run3h(tmp, ...)` with cwd=tmp and asserts all three of these, because a crash also exits 1 (089 audit L53-54):
- `b"Traceback" not in err`;
- the exact named line is in `out.splitlines()`;
- the exit code.

- **(a) `test_handoff_bad_01_no_03`**
  - Setup: work/150/01-research.md is `BAD` + `"see https://x.example/a\n"`, and there is no 03.
  - Expect exit 1 and these exact lines:
    - `sources count (unique URLs in 01-research.md): not computed (work/150/01-research.md unreadable (not UTF-8 at byte 0))`
    - `FAIL: work/150/01-research.md unreadable (not UTF-8 at byte 0)`
    - `no work/150/03-handoff.md; nothing else to check`
  - No line may match `sources count \(unique URLs in 01-research.md\): \d+`.
  - Twin (same text, no BAD prefix): exit 0, `sources count (unique URLs in 01-research.md): 1`, and no `FAIL:` line.
- **(b) `test_handoff_bad_03`**
  - Setup: a good 01, and 03 is `_h03(d, BAD)`.
  - Expect exit 1, `FAIL: work/150/03-handoff.md unreadable (not UTF-8 at byte 0)`, `1 problem(s)`, and no `fact-check rows:` line.
  - Twin: `_h03(d)` gives `PASS`, exit 0.
- **(c) `test_handoff_all_one_bad_03`**
  - Setup: work/150, 151 and 152, each with only a 03 and no 01. 151's 03 is `_h03(d, BAD)`.
  - Expect `150: PASS`, `151: FAIL: work/151/03-handoff.md unreadable (not UTF-8 at byte 0)`, `152: PASS`, `FAIL on 151`, exit 1.
  - Twin: all three clean gives `no new failures`, exit 0.
  - Absent 01: single-item `_run3h(tmp, "150")` on the clean twin gives no line starting `sources count`, then `PASS`, exit 0.
  - No git call is made, because every folder has a 03.
- **(d) `test_handoff_03_is_directory`**
  - Setup: 03-handoff.md is a directory.
  - Expect `FAIL: work/150/03-handoff.md unreadable (IsADirectoryError)`, exit 1.
  - Twin: as in (b).
- **(e) `test_handoff_legacy_bad_03_is_fail`**
  - Setup: work/003/03 is `_h03(d, BAD)`, run with `--all`.
  - Expect `003: FAIL: work/003/03-handoff.md unreadable (not UTF-8 at byte 0)`, `FAIL on 003`, exit 1.
  - Twin: an old-style 003 with no Totals line gives a line starting `003: LEGACY (`, and `no new failures`, exit 0.
- **(f) `test_handoff_all_bad_01_good_03`** (new, I1)
  - Setup: work/151 has 01 = `BAD` + text and 03 = `_h03(d)`, run with `--all`.
  - Expect `151: FAIL: work/151/01-research.md unreadable (not UTF-8 at byte 0)`, `FAIL on 151`, exit 1.
  - Twin: a clean 01 gives `151: PASS`, exit 0.
- **`test_unreadable_problem_fullmatch_only`**
  - These must fullmatch: `work/003/03-handoff.md unreadable (not UTF-8 at byte 0)` and `work/003/03-handoff.md unreadable (IsADirectoryError)`.
  - These must give None: `no Totals line ('<n> rows checked -> ...')` and `x unreadable (not UTF-8 at byte 0); y`.
- **`test_handoff_read_census`**
  - Uses the same walker as `test_read_census` over scripts/check_handoff.py.
  - Asserts `dict(seen) == {}` and `sum(seen.values()) == 0`.
  - Positive control: the same walk counts exactly 2 `ast.Attribute` calls with attr `_read` inside `main`. The count comes from the AST, never from a hand count (RI-006).
- **`test_r1_log_refuses_not_computed`**
  - `cp.log_fields_ok("R1", "092", "brief written | not computed (work/092/01-research.md unreadable (not UTF-8 at byte 0))") is False`.
  - `cp.log_fields_ok("R1", "092", "brief written | 7") is True`.
- **Existing tests must pass unchanged:** `test_check_handoff_all_legacy_and_fail` (L158), `test_all_names_branch_with_handoff` (L425), `test_check_handoff_open_branches_states` (h2, L2602), `test_read_contract`, `test_read_census`.
- **Checks I2 runs:**
  1. The full suite. Paste pytest's last line as printed.
  2. `python3.11 -m py_compile scripts/check_handoff.py scripts/check_pipeline.py tests/test_pipeline_check.py`.
  3. Grep `from check_pipeline import` in scripts/check_handoff.py: 0 hits. Grep `still reads its files strictly` in scripts/: 0 hits.
  4. `python3 scripts/check_handoff.py --all` on the branch tree. Paste the summary line, which must not add a new FAIL (Extra research 1). Paste the LEGACY count: 7 expected, 0 unreadable.
- **Mutations** (I2 runs them, I3 re-runs them; one at a time, restored after each, in a scratch copy). Each must fail the named tests:

| Mutation | Must fail |
|---|---|
| M-a: 01 strict `read_text(encoding="utf-8")` restored | census, (a), (f) |
| M-b: 03 strict read restored | census, (b), (c), (d), (e) |
| M-c: no-03 branch `return 0` | (a) |
| M-d: unreadable problem printed without `FAIL: ` | (b), (c), (d), (e), (f) |
| M-f: LEGACY check without the UNREADABLE_PROBLEM guard | (e) |
| M-g (I1): `_report` not called on the why03 path, so the function returns 1 with no lines | (b), (d) |

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1: `_pipeline()`, `cp.open_branches()` as an attribute, no from-import | Files 1, `_pipeline` and `_branch_with_handoff`; h2 and L425 unchanged; grep check 3. The repeated sys.path insert is guarded (Extra research 4) |
| Step 2: 01 via `cp._read(missing_ok=True)`, not-computed line, problem, no unique_urls on None | Files 1, main 01 read; fixture (a) + twin; (f); absent-01 assert in (c) |
| Step 3: 03 via `cp._read`, (None, None) path returns `1 if problems else 0`, why03 returns 1 before section() | Files 1, main 03 read; fixtures (b), (d), (a) (the no-03 return) |
| Step 4: UNREADABLE_PROBLEM fullmatch before LEGACY | Files 1, check_all and constant; fixture (e) + twin; test_unreadable_problem_fullmatch_only |
| Step 5: `--all` end to end | Fixture (c) + twin; (f) added |
| Step 6: `_run3h`, fixtures, census with positive control, log_fields_ok pin | Files 3; Tests list |
| Step 7: mutations M-a, M-b, M-c, M-d, M-f | Tests, Mutations table (M-g added) |
| Step 8: docstrings and known gaps | Files 1 docstring; Files 2 L360; Known gaps under Expected result |
| Fact-check fix 01 F27 (M-d killed by (b), (d), (e) too) | Mutations table, M-d row |
| Fact-check fix FOR 1 detail: index `cp._UNREAD[cp._shown(path)]`, no `.get`, `_read` return unchanged | Files 1, main reads |
| Fact-check fix FOR 2: pin on `log_fields_ok`, not LOG_FORMAT | test_r1_log_refuses_not_computed |
| Fact-check fix FOR 2: fullmatch, not substring | Step 4 row |
| Fact-check fix FOR 3: new `_run3h`, `_run3` unchanged | Files 3 |
| Fact-check fix FOR 3: M-e is check_pipeline's, already covered by 089 | DROPPED: not a 092 mutation; test_read_contract already kills it (03 row, 02 FOR 3 M-e) |
| Fact-check fix Q5 and AGAINST 2: a refused `--log R1` leaves the item INCOMPLETE until R1 is re-run | Known gaps (runbook) under Expected result; no .claude/ edit in this item |
| Missing inputs: 01 missing or unreadable; 03 missing or unreadable; `_UNREAD` detail; check_pipeline import; 01 under --all; open_branches request.md | Guardrail tests, Missing inputs; Known gaps |
| Rule the person follows (001 slack, tolerance, cap) | No change: no strategy rule is touched. Rule text lives only in the check_handoff and check_pipeline docstrings, which this plan updates |

## Guardrail tests
- Feasibility: step 4, the LEGACY exception, applies to 7 IDs (002-008, check_handoff.py L21-22; 03 Feasibility column).
  - Fixture (e) gives 1 of 1 FAIL, and its twin 1 of 1 LEGACY.
  - Real tree: 0 of 7 expected unreadable (A1's `--all` on ae2f8c7 gave "no new failures", logs/audit/2026-11-24.md L31). I2 re-counts it with check 4.
  - No other filter or window rule.
- Missing inputs: work/<ID>/01-research.md.
  - Absent: the assert in (c) (no `sources count` line, PASS, exit 0).
  - Unreadable: (a) and (f).
- Missing inputs: work/<ID>/03-handoff.md.
  - Absent: the twin of (a), which has no 03 (`no ...; nothing else to check`, exit 0). (a) itself covers absent 03 plus an unreadable 01 (exit 1).
  - Unreadable: (b), (d), (e).
- Missing inputs: `cp._UNREAD` detail. It cannot be absent, because `_read` writes it before returning a why (L539-542). It is indexed directly. A KeyError would be a bug, and the no-Traceback assert in every fixture catches it.
- Missing inputs: check_pipeline import failure. It is not defaulted: check_handoff crashes for every item. This is a known gap, recorded below (02 AGAINST 1).
- Missing inputs: 01 of an item with no 03 under `--all`, and open_branches' request.md. Both are unchanged. They are known gaps, written into the L360 docstring.

## Expected result
- `python3 scripts/check_handoff.py <ID>` with a non-UTF-8 or directory 01 or 03:
  - prints `FAIL: <path> unreadable (<detail>)` (plus the not-computed sources line for 01);
  - exits 1;
  - prints no traceback.
- `--all` lists such an item as `<ID>: FAIL: ...`, even if it is a LEGACY ID, and keeps going through the remaining items.
- Readable files give the same output as today.
- check_handoff.py has 0 raw reads (census) and 2 `_read` calls.
- Every mutation fails a named test.
- Suite green; Python 3.11 compile clean.

Known gaps for 05 to repeat:
1. check_handoff now imports check_pipeline for every single-item run. A broken check_pipeline.py breaks it.
2. After R1, an unreadable 01 gives exit 1 and a `not computed` sources value. `--log R1` refuses that value (log_fields_ok), so the item shows INCOMPLETE until R1 is re-run or the file is fixed. run-item.md L17 does not say this. A `.claude/` edit needs the person's OK, so A1 may open a request for it.
3. `--all` never reads the 01 of an item with no 03.
4. Under `--all`, an unreadable request.md read by open_branches is silent.
5. A failing `work.iterdir()` or `is_dir()` may still raise.
6. Both scripts are RULE_PATHS, so the person's OK is needed at PR review.

## Recurring issues checked (item 013)
- RI-001 (ESCALATED): checked.
  - The only selecting rule is step 4's LEGACY exception. It has a dated count: 7 IDs, fixture 1 of 1 each way, and 0 of 7 unreadable on ae2f8c7 (2026-11-24 audit L31). I2 re-counts it.
  - No filter or window is asserted without a count.
- RI-010 (ESCALATED): checked.
  - No log line is typed here. The last line is the field string, which the orchestrator passes to `--log` (items 045, 072).
- RI-014 (OPEN): checked.
  - This item is in its family. The fix makes no git call. The guardrails are the shared reader, the census twin and the no-Traceback fixtures (a)-(f).
- Also checked (GUARDED, relevant):
  - RI-002: no number is computed from an unread file, and the log_fields_ok pin covers the R1 log.
  - RI-006: the census comes from the AST.
  - RI-008: f-strings parse on 3.10, and check 2 compiles with py_compile.
  - RI-012: fullmatch plus a negative test.

Log fields: FIT WITH CHANGES | 3 files planned
