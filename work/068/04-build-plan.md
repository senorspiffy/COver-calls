# 04 Build plan - 068
Fit verdict: FIT WITH CHANGES

Changes against 03 (each is an addition or a tightening; no 03 step is dropped):
- C1 (step 2/3): add one assert to `test_interior_gap_180_blocks` that pins the count prefix on a hand-built TickerData (`earnings_gaps=0`). 03's new test uses the load_ticker fixture, where `td.earnings_gaps == len(gap_pairs)`, so it cannot catch the mutation `len(gap_pairs)` -> `td.earnings_gaps` that 03 itself warns about (03 F16). The new assert does.
- C2 (step 3): count `"gap(s)"` in the joined warnings string instead of splitting on `"; "`. The kept gap line itself contains `"; "` (`...); no call sold inside them (EARNINGS_UNKNOWN)`), so a split works only by luck of which half holds `gap(s)`.
- C3 (step 7): the base run may be reused only if every input of realtest is the same at both commits, not only ccbot/realtest.py. realtest imports ccbot.costs, ccbot.expiries (which reads config/holidays.json), ccbot.config and ccbot.pricing, and reads config/default.json and config/tickers.json (realtest.py L54-61). The precondition becomes `git diff --stat c659560 <HEAD-before-068> -- ccbot/ config/` = empty, plus the same data/real used by both runs. This is 067/02 AGAINST 1's open point (it listed the imports as UNVERIFIED; they are listed here from L54-57).
- C4 (step 7): the "expected differences" become an exact, scripted transform of the base strings, not a prose description. Files other than summary.json and bot_rule_by_ticker.csv must be byte-identical.
- C5 (step 7c): SPY has no trades_SPY.csv and no grid_in_sample rows (realtest.py L798-805 and L823 loop over `data`, which has SPY popped, L795). Only its 3 bot_rule_by_ticker.csv rows are compared. 03 said "trades_<tk> rows for those 5 names and SPY".
- C6 (steps 5/6): the agent text names the same-inputs condition from C3 in a few words.

Fit check: research tooling only. Nothing trades, no 001 rule the person follows changes (the gap block, EARNINGS_GAP_WARN = 120 and every count stay as they are), and nothing touches the $3k account sizing (`fits_3k` is computed as before). No conflict with built code: the only reader of the deleted line's text is reports/real/ (grep `between dates` outside work/: reports/real/ and realtest.py L191 only). 067 (scripts/diff_reports.py, template fields) is not built and is not touched. `.claude/` edits need the person's OK in PR review.

## Extra research (with sources)
1. Reuse of the base run: the orchestrator has full runs of e129253^ and c659560 in a scratch dir. 03 step 7(a) needs a full run at HEAD-before-068. The c659560 run serves as that base only if C3's precondition holds. I1 had no shell, so I2 runs it first and pastes it in 05: `git diff --stat c659560 HEAD -- ccbot/ config/` (HEAD = branch head before any 068 commit). If it is not empty, I2 makes a base full run at HEAD-before-068 in a scratch worktree. Data: name the `--data` dir both runs used. If the c659560 run used a different data/real copy, `sha256sum` both trees (sorted file list) and paste the two totals. Sources: ccbot/realtest.py L54-61 (imports and config paths), work/067/02-improvements.md L10 (imports listed as UNVERIFIED there).
2. NaN in summary.json: `json.dumps` writes NaN as the bare token `NaN` by default (allow_nan=True), and `json.loads` reads it back as float nan, which is not equal to itself. Only `earnings_lead_days`/`earnings_gap_days` are turned into null (realtest.py L809-812). Other leaves, such as `atm_*`, can be NaN. So the inline comparison compares files as bytes first. For the two files that change, it compares JSON leaves by `repr()` and CSV cells as strings, so NaN==NaN can never make a false change. Source: Python docs, json module ("allow_nan", "parse_constant"): https://docs.python.org/3.13/library/json.html
3. Determinism: Monte Carlo uses `random.Random(seed=7)` (L715), and everything else is pandas/numpy arithmetic on the same inputs. Two runs of the same code and data on the same machine should give byte-identical CSVs and JSON. Any byte difference outside the two expected files is therefore a real finding, not noise. Source: realtest.py L711-744.
4. Warning order: the kept gap line comes from simulate (`df.attrs["warnings"]`) and is joined after load_ticker's warnings (L656). Deleting L190-191 removes one part and leaves the order of all the others unchanged. That is why the C4 transform (drop one `"; "` part, insert the count into the other) gives the new string exactly.

## Files to create/change
Planned: 5 files (0 new, 5 changed). Nothing under reports/, config/, scripts/, templates/ or work/067.

1. `ccbot/realtest.py`
   - `load_ticker`: delete L190-191 (`if gaps:` and the `warnings.append(f"earnings: {gaps} gap(s) > {EARNINGS_GAP_WARN} days between dates")`). Keep L189 `gaps = len(_gap_pairs(earnings))` and `earnings_gaps=gaps` (L233).
   - `simulate` L455: `f"earnings: {len(gap_pairs)} gap(s) > {EARNINGS_GAP_WARN} days between listed dates ("`. L456-458 unchanged. Never `td.earnings_gaps` here.
   - `_gap_pairs` docstring (L387-388): keep the meaning, and add "(one warning line, from simulate; item 068)" so nobody re-adds a load_ticker line.
2. `tests/test_realtest.py`
   - New `test_one_gap_warning_with_count_and_dates(data_root, tmp_path)`, docstring "item 068: one warning per gap, with count and dates". Body: `root = _copy(data_root, tmp_path)`. Drop AAA's Apr and Jul 2020 earnings rows exactly as L396-398 do. Then `td = rt.load_ticker(root, "AAA", FACTS)`, `df, tr = rt.simulate(td, rt.BOT_RULE, CFG)`, `s = rt.summarize(td, rt.BOT_RULE, df, tr, CFG)`, `(a, b), = rt._gap_pairs(td.earnings)`. Asserts:
     - `s["warnings"].count("gap(s)") == 1` (C2)
     - `f"earnings: 1 gap(s) > {rt.EARNINGS_GAP_WARN} days between listed dates ({a}→{b})" in s["warnings"]`
     - `s["earnings_gaps_gt120"] == 1 == td.earnings_gaps`
     - `not any("gap(s)" in w for w in td.warnings)` (load_ticker adds none)
   - `test_interior_gap_180_blocks` (L278-279): add `assert w[0].startswith(f"earnings: 1 gap(s) > {rt.EARNINGS_GAP_WARN} days between listed dates (")` (C1; `_tiny` sets `earnings_gaps=0`, L214).
3. `.claude/commands/run-item.md`: new last paragraph, 03 step 4's sentence, with C6's clause added after "once per step that publishes numbers": "...; a full run made at another commit counts as the base only if `git diff --stat <that commit> <base> -- ccbot/ config/` is empty and both used the same data (item 068)." Keep it one paragraph and one `item 068` mention.
4. `.claude/agents/i2-builder.md` step 3 (L20): append 03 step 5's sentence. Replace "unless a full run made there exists" with "unless a full run with the same inputs exists (`git diff --stat <its commit> <base> -- ccbot/ config/` empty, same data dir)". Addition only.
5. `.claude/agents/i3-verifier.md` step 2 (L13): append 03 step 6's sentence. Replace "if that run is gone or not from the base commit" with "if that run is gone or its inputs differ from the base's (same check as i2 step 3)". Addition only.

## Tests and checks
1. Precondition (I2, before coding, pasted in 05): `git diff --stat c659560 HEAD -- ccbot/ config/` → expected empty (the orchestrator's note says realtest.py is equal; the other files are unchecked). Record HEAD's SHA as "base".
2. `python3 -m pytest -q -p no:cacheprovider tests/test_realtest.py` → all pass (existing tests unchanged + 1 new).
3. Full suite `python3 -m pytest -q -p no:cacheprovider`. Measure the base count at the base commit first. Expected: base passed + 1, skipped unchanged, 0 failed.
4. Mutations (scratch worktree, never in the repo; paste each fail count in 05):
   - M1: restore L190-191 → `test_one_gap_warning_with_count_and_dates` fails (count 2 ≠ 1). Expected: ≥ 1 failed.
   - M2: drop `{len(gap_pairs)} ` from L455 → the new test and `test_interior_gap_180_blocks` fail. Expected: ≥ 2 failed.
   - M3: `len(gap_pairs)` → `td.earnings_gaps` in L455 → `test_interior_gap_180_blocks` fails ("0 gap(s)"). Expected: ≥ 1 failed.
   - M4 (guardrail still holds, from RI-002/065): remove the interior-gap block in `_earnings_state` (`if _is_gap(...): return "interior_gap"`) → ≥ 1 failed, as before 068.
5. Greps: `grep -n 'between dates"' ccbot/realtest.py` → 0 hits; `grep -c "item 068" .claude/commands/run-item.md .claude/agents/i2-builder.md .claude/agents/i3-verifier.md` → 1 each; `git diff --stat -- .claude/` shows additions only (each edited line is the old line + appended text).
6. Real-data check (03 step 7, with C3-C5). All outputs go to `<scratch>`, never `reports/`.
   a. Base: the orchestrator's c659560 full run if precondition 1 is empty, else `python3 -m ccbot.realtest --out <scratch>/base` in a scratch worktree at base. Head: `python3 -m ccbot.realtest --out <scratch>/head` at the 068 build commit. Paste both dirs, both SHAs and the `--data` dir (or the two data hashes, Extra research 1).
   b. Whole-output comparison: if `scripts/diff_reports.py` exists on the branch at build time, use it on base vs head and paste its output. Otherwise run this scratch, uncommitted stdlib script (kept under the scratchpad, path and full text pasted in 05):
      - list the union of files in both dirs. Any file on one side only → FAIL.
      - every file except summary.json and bot_rule_by_ticker.csv must be byte-identical (`filecmp.cmp(shallow=False)`). Print the count of identical files.
      - define `fix(s)`: split on `"; "`, remove the part matching `^earnings: (\d+) gap\(s\) > 120 days between dates$` (keep n), and in the remaining part starting `earnings: gap(s) > 120 days between listed dates (` insert `f"{n} "` after `earnings: `, then re-join. Applied to a string with no such part, it returns the string unchanged.
      - summary.json: walk both trees (dicts by key, lists by index). The key sets and list lengths must be equal. Every leaf must have `repr(head) == repr(base)`, except `counts_bot_rule_bid.<tk>.warnings`, which must equal `fix(base)`. Print the number of leaves compared and the number of warnings leaves that `fix` changed.
      - bot_rule_by_ticker.csv: `csv.reader`. Same header and same row count, and every cell equal as a string, except the `warnings` column, which must equal `fix(base)`. Print the rows compared and the rows `fix` changed.
      Expected: changed warnings leaves = 5 (CMCSA, MDLZ, MO, T, VZ), changed CSV rows = 15 (5 × 3 fills), every other leaf/cell/file identical. Any other result → stop and report to I1 (do not explain it away in 05).
   c. Time `python3 -m ccbot.realtest --tickers CMCSA,MDLZ,MO,T,VZ --out <scratch>/tk` (wall clock, `time`) and paste it. Then compare it with `<scratch>/head` using the same script logic restricted to: `counts_bot_rule_bid[tk]` and `skipped` entries for the 5 names, their trades_<tk>.csv files (byte-identical), their grid_in_sample.csv rows (by ticker, config) and their bot_rule_by_ticker.csv rows; SPY's 3 bot_rule_by_ticker.csv rows (C5). Expected: all equal. Not compared (portfolio-wide, 03 F5-F10): walkforward_*, monte_carlo, period, bxm_vs_spy, tickers, fits_3k.
   d. `git status --short reports` → empty.
7. `python3 scripts/check_pipeline.py` → 068 not SKIPPED, INCOMPLETE or in LOG TIME.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1: delete load_ticker L190-191, keep `gaps`/`earnings_gaps` | Files 1 (first bullet); Tests 5 grep; Tests 4 M1 |
| Step 2: count in the kept simulate line via `len(gap_pairs)` | Files 1 (second bullet); Tests 4 M2, M3 (C1) |
| Step 3: new one-gap test + 2 mutations | Files 2 (first bullet, C2 counting); Tests 4 M1, M2 |
| Step 4: run-item.md sentence | Files 3 (+C6 clause); Tests 5 grep |
| Step 5: i2-builder step 3 sentence | Files 4 (C6 wording); Tests 5 grep |
| Step 6: i3-verifier step 2 sentence | Files 5 (C6 wording); Tests 5 grep |
| Step 7(a): base and head full runs to scratch | Tests 1 precondition (C3) + Tests 6a |
| Step 7(b): whole-output comparison, 067 script or scratch stdlib, never a hand list | Tests 6b (C4 exact transform) |
| Step 7(c): time a `--tickers` run, its per-ticker outputs equal the full run | Tests 6c (C5: no SPY trades/grid rows) |
| Step 7 expected: only 5 warnings leaves + 15 CSV rows change; `git status --short reports` empty | Tests 6b expected, 6d |
| Step 8: suite base + 1, check_pipeline clean | Tests 3, 7 |
| Missing: `--out` absent | Files 3-5 text ("never the default `--out`"); Tests 6d |
| Missing: data/real/prices/SPY.csv absent | No code change; Tests 6b fails on any bxm_vs_spy difference |
| Missing: base full run gone / other commit | Tests 1 + 6a (make the base run); Files 3-5 C6 clause |
| Missing: 067 script not built | Tests 6b fallback script |
| Missing: `--tickers` time not measured | Tests 6c (measured, pasted) |
| Missing: requested ticker fails to load | Tests 6c compares `skipped` for the 5 names; a run where only SPY loads is not used |
| Missing: stock earnings file absent | existing `test_drop_input[earnings]` unchanged (no gap pairs → no gap line) |
| Missing: ETF earnings with gaps | DROPPED: no new test. The ETF path is unchanged by 068 except the deleted load_ticker line. `earnings_gaps_gt120` still carries the count (L189, L653, kept), and an ETF never reads earnings (L539). R3 accepted no ETF-only line (03 row "02 AGAINST 3"), and SPY's earnings file is empty (03 F21). |
| 03 Removed claim F13 (`--tickers` runtime) | Tests 6c measures it; no estimate written |
| 001 rule text the person follows | None changed (no slack, tolerance or cap; EARNINGS_GAP_WARN = 120 kept) |

## Guardrail tests
- Feasibility: step 3 fixture "exactly 1 gap" → `test_drop_input[earnings_interior_gap]` L400-402 (`td.earnings_gaps == 1`, pair 2020-01 → 2020-10) and the new test's `s["earnings_gaps_gt120"] == 1`.
- Feasibility: step 7 affected set "5 of 17 published tickers" (dated count: reports/real/summary.json, 03 Feasibility, 2026-11-16) → Tests 6b expected "5 warnings leaves, 15 CSV rows changed". Any other number fails the real-data check. This is a data check, not a unit test, because the count comes from data/real, which tests do not read.
- Missing inputs: interior-gap earnings (count prefix on hand-built data) → `test_interior_gap_180_blocks` new assert (M3).
- Missing inputs: interior-gap earnings (one line, load_ticker data) → `test_one_gap_warning_with_count_and_dates` (M1, M2).
- Missing inputs: stock earnings file absent → existing `test_drop_input[earnings]` (unchanged, must still pass).
- Missing inputs: empty earnings file → existing `test_empty_earnings_file_warns_and_lead_is_null` (unchanged).
- Missing inputs: `--out` absent → text rule only; Tests 6d (`git status --short reports` empty), checked by I3.

## Expected result
- One warning per earnings gap: `earnings: <n> gap(s) > 120 days between listed dates (<a>→<b>, ...); no call sold inside them (EARNINGS_UNKNOWN)` (or `; earnings not checked by this rule`). No count-only line. `earnings_gaps_gt120` and every block/count stay as they are.
- Suite: base + 1 passed, skipped unchanged. M1-M4 each fail ≥ the stated number of tests.
- Real data: base vs head differ only in 5 `counts_bot_rule_bid.<tk>.warnings` leaves and 15 `warnings` cells of bot_rule_by_ticker.csv, each equal to `fix(base)`. All other files are byte-identical and every other leaf/cell is equal. The `--tickers` run time is measured, and its per-ticker outputs equal the full run. reports/ untouched.
- Agent text: run-item.md, i2 step 3 and i3 step 2 each carry one `item 068` sentence: iterate with `--tickers <affected> --out <scratch>`, one full run per publishing step, base reuse only with the same inputs. Full runs per realtest item drop from 6 (065) to 2 when a same-inputs base run exists, else 3 (03 Self-check: 22.7-34.0 min vs 68.0 min), plus the measured `--tickers` runs.
- Guardrail status lines for 05: RI-013: 068 does not build 067's guardrail; 068's own real-data check is whole-output (Tests 6b). RI-002: unchanged (M4 still fails).

Recurring issues checked (item 013): RI-001 (ESCALATED). Both filter counts in 03 are dated and non-zero (fixture 1 gap; 5 of 17 tickers), and each has a planned check (Guardrail tests). RI-002 (ESCALATED). No value is defaulted. The kept line counts `len(gap_pairs)`, and C1/M3 pin that against hand-built `earnings_gaps=0`. NaN leaves are compared by repr, never dropped. M4 re-probes the 065 block. RI-013 (OPEN). Tests 6b compares every file, leaf and cell, with an exact expected transform; no hand-picked keys. Also checked: RI-007 (FULL scope, I1-I3 run; the `.py` comparison script stays in the scratchpad, uncommitted, so it is not a work/ `.py` under item 064), RI-009 (mutations and runs in scratch worktrees/dirs only), RI-010 (the I1 log line must be written with `python3 scripts/check_pipeline.py --log I1 068 "FIT WITH CHANGES | 5 files planned"` right after this file; I1 had no shell in this session, so the orchestrating session runs it), RI-004/005 (the M1-M3 expected fail reasons re-derived from the fixture: 2 lines vs 1; "0 gap(s)" from `_tiny`'s `earnings_gaps=0`). RI-003, RI-006, RI-008, RI-011, RI-012 don't apply: no calendar, no fact-check totals, only an f-string edit (3.10-safe), no branch diff, no text-classified errors.
