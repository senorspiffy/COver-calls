# 04 Build plan - 067
Fit verdict: FIT WITH CHANGES

Why: research tooling only (scripts/, tests/, templates/, work/067/05). No trading effect, nothing in ccbot/, config/, 001 or reports/real/ changes, and nothing connects to a brokerage. It suits the ~$3k account (no cost, no position change) and conflicts with nothing built. The scope is 03's map with these changes:
1. **Trigger text (step 3).** R3's widened trigger lists 8 paths, so it is too long for one short sentence. The template uses the caller's wording instead: "Required when the item changes ccbot/realtest.py or a module/file it reads (list in work/067/03-handoff.md)". I checked the list in 03 row "01 OQ5" against the code: realtest imports only ccbot.costs, ccbot.expiries, ccbot.config and ccbot.pricing (realtest.py L54-57). costs.py and pricing.py import only `math`. expiries reads config/holidays.json (L10). config.load_config reads only the path it is given (config.py L104-114). realtest reads config/default.json and config/tickers.json (L60-61, L137) and the `--data` dir. The list is complete.
2. **Step 4 runs are not repeated.** The orchestrator is already running both 065 realtest runs: base `e129253^` into `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/065-before` and head `c659560` into `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/065-after`, from worktrees `.../scratchpad/wt-before` and `.../scratchpad/wt-after`. I2 diffs those dirs. I2 does not create worktrees, does not re-run realtest and does not remove the orchestrator's worktrees.
3. **The data-identity check changes.** data/real is tracked in git (it is present in the `wt-before` checkout, and .gitignore has no `data` line), so each worktree may have read its own copy. 03's single hash of the repo's data/real is not enough. See step 4.
4. **Edge case R3 missed: a ticker with 0 trades.** `pd.DataFrame([]).to_csv(...)` writes no header row (an empty or near-empty file). The script must read that as `columns [], rows 0`, not as an error or a crash. Test (l).
5. **TOTAL line.** It gains `not compared <n>`, so a stray file is counted and not only printed.
6. **068 reuse.** 068 will reuse diff_reports.py, so the CLI, the line formats and the exit codes are fixed by the tests below. The module also exposes `diff_dirs()` for import.

## Extra research (with sources)
- Python csv docs (https://docs.python.org/3/library/csv.html): `csv.reader` returns each row as a list of str. A blank line comes back as an empty list. Opening with `newline=''` is required for correct quoted-newline handling. So an empty or blank first line gives header `[]` and is handled as "no columns" (change 4). R3 already sourced the same page for the reader choice.
- pandas `to_csv` on an empty frame: I found no primary doc stating the exact bytes. A search ([lightrun pandas issue page](https://lightrun.com/answers/pandas-dev-pandas-dataframeto_csv-with-empty-dataframe-probleme-quoting), [pandas test_to_csv.py mirror](https://opensource.netapp.com/perfsrv/pandas/tests/io/formats/test_to_csv.py)) gave no usable quote: the first page fetched as an unrelated blog index. The value is UNVERIFIED. I2 measures it once with `python3 -c "import pandas as pd; print(repr(pd.DataFrame([]).to_csv(index=False)))"`, pastes the result in 05, and test (l) covers a 0-byte file, `"\n"`, and whatever that command prints.
- realtest.py L795/L805: SPY has no trades file. L697-698: a "no training data" window writes bare `NaN` into summary.json. L809-812: the earnings lead/gap NaN becomes null. These confirm 03's Missing inputs rows.
- Known limit, documented in the script's docstring and not built here: JSON lists are index-aligned. If `walkforward_picks` gains a leading window (the start date moves), every later JSON item shows as changed. walkforward_picks.csv is key-matched on (train_from, test_from), so the CSV section gives the true count. Both views are printed.

## Files to create/change
1. **scripts/diff_reports.py** (new, stdlib only: argparse, csv, json, math, pathlib, sys; must compile on 3.10; no QUOTE_STRINGS/QUOTE_NOTNULL). Build as 03 step 1, with these functions and fixed formats:
   - `load_json(path) -> (obj, nan_count)`: `json.loads(text, parse_constant=...)` maps NaN/Infinity/-Infinity to float and counts them. Bad JSON → `DiffError("BAD JSON <f>: <err>")`.
   - `diff_json(a, b, path="") -> list[str]`: recursive over dicts (union of keys, sorted; `ADDED <p> = v` / `REMOVED <p> = v`) and lists (index-aligned; `LENGTH <p>: a -> b`, extra items ADDED/REMOVED). A leaf is equal iff `type(a) is type(b)` and (`a == b` or both are float NaN). A same-type change prints `<p>: repr(a) -> repr(b)`. A different-type change prints `TYPE <p>: <type> repr(a) -> <type> repr(b)`, for example `TYPE x: int 1 -> float 1.0`. Containers are never compared with `==`. Paths look like `a.b.50` or `walkforward_picks[5].picked`.
   - `read_csv(path) -> (header, rows)`: `open(newline='', encoding='utf-8')` with `csv.reader`. A 0-byte file, or a first row that is `[]`, gives `([], [])`. Rows after an empty header are `BAD ROW`. A duplicate header name or a ragged row → `DiffError`.
   - `KEYS = {"walkforward_picks.csv": ("train_from", "test_from"), "walkforward_by_ticker.csv": ("ticker",), "bot_rule_by_ticker.csv": ("ticker", "config"), "grid_in_sample.csv": ("ticker", "config")}`, plus `trades_*.csv` → `("open_date",)`. A key is used only if all its columns are on both sides. Otherwise the match is by index, with `MATCH <f>: index (<why>)`.
   - `diff_csv(name, before, after, max_rows) -> (lines, counts)`: the `COLUMNS` line first, then the `CSV <f>: match <key|index>, rows a -> b, matched m, added x, removed y, changed c; by column: <col>=n, ...` line. Then up to max_rows row lines: changed and added rows in after-file order, then removed rows in before-file order. Then `  ... k more`. Duplicate key → `DiffError("DUPLICATE KEY <f>: <key> (<n> rows)")`.
   - `diff_dirs(before, after, max_rows=20) -> (lines, totals)`. `main(argv=None) -> int`: exit 0 = no change, 1 = changes, 2 = error. On exit 2 the error line goes to stderr and nothing else is reported as a result. The last line is `TOTAL: files <n>, only-before <n>, only-after <n>, not compared <n>, json changes <n>, csv rows changed <n> added <n> removed <n>, columns changed <n>`, followed by `no change` when every change count is 0 (`not compared` counts a stray file but does not by itself make it a change).
   - Missing or non-dir path → `MISSING DIR: <p>`. A dir with no .json and no .csv → `EMPTY DIR: <p>`. Both exit 2.
2. **tests/test_diff_reports.py** (new): 03 step 2 cases (a)-(k), plus (l)-(p) below. The script runs through `subprocess.run([sys.executable, str(REPO / "scripts" / "diff_reports.py"), ...], capture_output=True, text=True)`.
3. **templates/build-report.md**: new section after `## Test output`:
   ```
   ## Real-data effect (diff_reports output, pasted)
   <!-- Required when the item changes ccbot/realtest.py or a module/file it reads (list in work/067/03-handoff.md). Paste: before/after SHA, --data path(s) and their hash, python/pandas version, the command, and the whole output down to TOTAL. Otherwise: `not required (<git diff --stat file list>)`. -->
   ```
4. **templates/verification.md**: the same section after `## Tests re-run (output)`, with this extra sentence in the comment: "I3 re-runs diff_reports.py on the same dirs and compares its TOTAL line with 05's."
5. **work/067/05-build-report.md** (I2's own report): uses the new section for 065's full effect, from the orchestrator's dirs (step 4 below).

Nothing in ccbot/, config/, reports/real/, 001 or work/068 changes. templates/ is in RULE_PATHS, so the PR needs the person's OK on the template edits.

## Tests and checks
New tests in tests/test_diff_reports.py (fixtures in `tmp_path`):
- (a) nested dict `monte_carlo_2_stocks_1yr.cc_ret.50: 0.0689 -> 0.0686` and the list-in-dict change `walkforward_picks[1].picked: ...`; exit 1.
- (b) identical dirs with a bare `NaN` leaf and empty CSV cells → `NaN tokens: before 1, after 1`, `no change`, exit 0.
- (c) `1` -> `1.0`, `true` -> `1` and `null` -> `0` → three `TYPE` lines.
- (d) trades_XYZ.csv only in after → `ONLY IN AFTER: trades_XYZ.csv (2 rows)`, exit 1.
- (e) walkforward_by_ticker AAL,BAC,CSX → AAL,ABC,BAC,CSX → `match key`, `matched 3, added 1, removed 0, changed 0`.
- (f) 25 changed grid rows → 20 row lines + `... 5 more`, `changed 25`; with `--max-rows 0` → 25 lines.
- (g) duplicate open_date → exit 2, `DUPLICATE KEY`.
- (h) a header column added → `COLUMNS` line.
- (i) a missing dir and an empty dir → exit 2, `MISSING DIR` and `EMPTY DIR`.
- (j) list length 10 -> 9 → `LENGTH`.
- (k) CSV cell 0.0689 -> 0.0686 → `changed 1` (no tolerance).
- (l) trades_ZZZ.csv with 0 bytes on both sides, and the measured pandas empty-frame text (step 1 research) on both sides → `columns []`/`rows 0 -> 0`, no error, exit 0 for that file.
- (m) bad summary.json → exit 2, `BAD JSON`.
- (n) key column `ticker` only in after → `COLUMNS` line + `MATCH walkforward_by_ticker.csv: index (key column ticker missing in before)`.
- (o) a ragged CSV row → exit 2, `BAD ROW`.
- (p) `test_committed_reports_self_diff`: `diff_reports.py reports/real reports/real` → exit 0, `no change`, and `match key` for walkforward_picks, walkforward_by_ticker, bot_rule_by_ticker, grid_in_sample and every trades_*.csv. This pins key uniqueness on real files without pinning row counts, which change if the person regenerates reports/real.
- Also importable: `from scripts.diff_reports import diff_dirs` works, or, if scripts/ is not a package, the file loads with importlib as the existing scripts tests do. I2 follows the existing pattern in tests/test_pipeline_check.py.

Checks I2 pastes in 05:
- `python3 -m pytest -q tests/test_diff_reports.py` → all pass. Full suite = base + 16 new, 1 skipped as before. `test_every_py_compiles_on_oldest_python` passes.
- `grep -nE "QUOTE_(STRINGS|NOTNULL)" scripts/diff_reports.py` → no hit.
- `grep -n "Real-data effect (diff_reports output, pasted)" templates/build-report.md templates/verification.md` → 1 hit each.
- `python3 scripts/diff_reports.py reports/real reports/real` → `no change`, exit 0, `rows 1020 -> 1020` (grid) and `54 -> 54` (bot_rule).

**Step 4: 065's full effect (no re-run)**
1. Wait until both orchestrator dirs are complete: each has summary.json and 22 files (17 trades + 4 aggregate + summary). If either is incomplete, or the run failed, stop and report to the orchestrator (the script would exit 2 with `EMPTY DIR` or show `ONLY IN`). Do not re-run.
2. Get from the orchestrator, and paste, the exact command and `--data` path of each run. Paste `git rev-parse e129253^` (expect 5883ba4…), `git -C <wt-before> rev-parse HEAD` and `git -C <wt-after> rev-parse HEAD` (must equal `e129253^` and c659560). Paste `git diff --stat e129253 c659560 -- ccbot config` (expect empty) and `git diff --stat e129253^ c659560 -- data/real` (expect empty).
3. Data identity: hash every `--data` dir actually used with `find <dir> -type f | sort | xargs sha256sum | sha256sum`, run from inside `<dir>` so the paths are relative. If the runs used two worktree copies, the two hashes must match. Then `find <dir> -type f -newer <out>/trades_AAL.csv` must list nothing for each dir. If any of these differ, do not report the diff and tell the orchestrator.
4. Paste `python3 -c "import sys, pandas; print(sys.version, pandas.__version__)"` for the interpreter the runs used.
5. `python3 scripts/diff_reports.py <065-before> <065-after>`: paste the whole output (exit 1 expected) in the new section. Check it against 03 step 4: `walkforward_picks[5].picked` and `[9].picked` with the audit values, walkforward_picks.csv `picked=2`, walkforward_by_ticker.csv `matched 17` and `excess_cagr=11`, `monte_carlo_2_stocks_1yr.cc_ret.50` rounds 0.0689 -> 0.0686, `counts_bot_rule_bid.MO.calls_sold: 23 -> 21` and `MDLZ ... 34 -> 31`, no `bxm_vs_spy` line.
6. Count `excess_cagr > 0` rows in each walkforward_by_ticker.csv (one-liner pasted, rule stated: strictly > 0). A1 got 6 -> 5.
7. Report any mismatch as found, without adjusting it. Put the effect list in the PR text.

**Mutations (I3, scratch copy only, never in the repo):**
1. Recursion cut to top level (compare `before[k] != after[k]`, print only k) → (a) fails. This is the request's guardrail.
2. Key → index for walkforward_by_ticker → (e) fails.
3. Both-NaN check removed → (b) fails.
4. `EMPTY DIR` check removed → (i) fails.
5. `type(a) is type(b)` removed (plain `==`) → (c) fails.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 scripts/diff_reports.py (a) files, ONLY IN, NOT COMPARED | Files 1 `diff_dirs`; tests (d), (p); TOTAL `not compared` added (change 5) |
| Step 1 (b) JSON parse_constant, NaN count, recursion, TYPE, no container `==`, no cap | Files 1 `load_json`, `diff_json`; tests (a), (b), (c), (j), (m) |
| Step 1 (c) CSV reader, header first, duplicate header, key per file, index fallback, string cells, capped rows | Files 1 `read_csv`, `KEYS`, `diff_csv`; tests (e), (f), (g), (h), (k), (n), (o), (l) |
| Step 1 (d) TOTAL line, `no change`, exit 0/1/2 | Files 1 `main`; tests (a), (b), (i) |
| Step 1 check: self-diff of reports/real, no QUOTE_ grep | Test (p); Checks grep |
| Step 2 tests (a)-(k) + mutations | Tests (a)-(k) as listed, (c) extended with null; Mutations 1-3 kept, 4-5 added |
| Step 3 templates field + trigger | Files 3, 4. Trigger shortened to the caller's sentence (change 1); 03's list referenced by path |
| Step 3 I3 compares TOTAL with 05 | Files 4 comment |
| Step 4 two worktrees + realtest runs | DROPPED: the runs are already made by the orchestrator into 065-before/065-after. Replaced by Step 4 items 1-2 (verify SHAs, no re-run) |
| Step 4 data hash before/after | Changed: hash each `--data` dir used, match across worktrees, `-newer` check (Step 4 item 3; change 3) |
| Step 4 python/pandas version | Step 4 item 4 |
| Step 4 expected values (picks 2, excess_cagr 11/17, MC, MO/MDLZ, no bxm line, 6 -> 5) | Step 4 items 5-6 |
| Step 4 remove worktrees, `git worktree list` | DROPPED: the worktrees belong to the orchestrator, which removes them |
| Missing inputs: missing/empty dir | Test (i), mutation 4 |
| Missing inputs: one-side file | Test (d) |
| Missing inputs: bad JSON | Test (m) |
| Missing inputs: NaN/Infinity | Test (b), mutation 3 |
| Missing inputs: null vs value | Test (c) (`null` -> `0`) |
| Missing inputs: key column one side | Test (n) |
| Missing inputs: duplicate key | Test (g) |
| Missing inputs: ragged row | Test (o) |
| Missing inputs: empty cell | Test (b) (empty cells both sides → equal); docstring states NaN/'' can't be told apart |
| Missing inputs: ticker skipped on one run | Test (d) (ONLY IN for its trades file); `skipped.*` covered by (a)-style JSON recursion |
| Missing inputs: SHA/diff mismatch (step 4) | Step 4 item 2: paste actual, never substitute |
| Missing inputs: data changed between runs | Step 4 item 3: do not report, tell the orchestrator |
| Implementation map: no change to ccbot/config/reports/real/001 | Files list (last paragraph) |

No rule the person follows (001) changes, so no rule-text update is needed (item 001 check).

## Guardrail tests
- Feasibility: CSV key uniqueness (picks 10/10, by_ticker 17/17, bot_rule (ticker, config) 54/54, grid 1,020/1,020, trades open_date 250/250, R3 counts on committed reports/real) → test (p) `test_committed_reports_self_diff` (exit 0 and `match key` for every keyed file; a duplicate would exit 2). Row counts `1020 -> 1020`, `54 -> 54` are pasted in 05, not pinned.
- Feasibility: no-tolerance rule (0.0003 change) → tests (a) and (k).
- Feasibility: cap rule (25 changed, N=20 → 5 more) → test (f).
- Missing inputs: before_dir/after_dir absent or empty → (i). One-side file → (d). Bad JSON → (m). NaN token → (b). null vs value → (c). Key column on one side → (n). Duplicate key → (g). Ragged row → (o). Empty cell → (b). 0-trade ticker file (new) → (l).
- RI-013 guardrail: mutation 1 → (a) fails.

## Expected result
- scripts/diff_reports.py and tests/test_diff_reports.py exist, 16 new tests pass, and the full suite is base + 16 with 1 skipped. Mutations 1-5 each fail their test.
- Both templates have the `Real-data effect (diff_reports output, pasted)` section with the short trigger sentence.
- work/067/05 holds 065's full diff from the orchestrator's 065-before/065-after dirs, with SHAs, data hashes, versions and the TOTAL line. It shows the walk-forward (2 of 10 picks), by-ticker (11 of 17, positive 6 -> 5) and Monte Carlo (0.0689 -> 0.0686) effects, or reports any mismatch as found.
- Follow-up (not built, RI-010 pattern): nothing checks that the new field is filled when the trigger files change. A check_pipeline check is a candidate item.

Recurring issues checked (item 013):
- RI-001: every filter/key rule has a dated count from 03 and a test (p), (a), (k), (f).
- RI-002: every Missing inputs row maps to an absent-case test or a stop rule. The new 0-trade file case is (l). No absent input becomes `no change`.
- RI-007: Scope FULL, the plan goes through I2/I3. I1 wrote no code and made no log line, by the caller's instruction.
- RI-008: stdlib only, no 3.12 csv options, the 3.10 compile test covers it.
- RI-010: the template field has no automated check. Noted as a follow-up, not built.
- RI-013: this item. Mutation 1 is the GUARDED probe.
- Not applicable: RI-003, RI-004/005 (no new worked example beyond 03's, which are reused unchanged), RI-006 (no hand totals here), RI-009, RI-011, RI-012.
