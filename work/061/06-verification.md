# 06 Verification - 061
Verdict: FAIL (round 1)

Checked at HEAD 6d7d78f (branch claude/project-thread-ltyppm), 2026-11-14 (I3). The code matches the plan
and every test and probe holds. The FAIL is about 01, the text the person reads: it does not give the
floor-off result, two proposed rules claim more than the grid shows, and the earnings-hole limitation has
no measured impact. 03's Missing-inputs table is also stale. Fixes F1-F4 go to I2. No code change is needed.

## I1 audit (plan vs research)
- 03's map says "no bot or config change". 04 keeps that: its `git diff --stat` check covers bot, rules, screen,
  costs, expiries, pricing, missing and config/, and I re-ran it (0 lines).
- Every change 04 adds has a source:
  - 03's fact-check row "Bot rule tested exactly as configured: WRONG".
  - The bot code: rules.py L253-255 (take50 first third), L296 (EARNINGS_UNKNOWN), L308-312 (basis floor);
    screen.py L31 and L48; costs.fees; expiries.third_fridays.
  - Three web sources for the 2022-04-14 Thursday monthly.
  - No unsourced additions.
- The Rule trace covers every 03 row, and each DROPPED row gives a reason (the $0.03 floor; the RI-012-shaped
  fetch retry).
- One plan choice is weak but labelled. 1.4 only warns on gaps of more than 120 days between earnings dates, and
  it does not cover a hole before the first date (see Earnings hole below).

## I2 audit (build vs plan)
I read `ccbot/realtest.py` against 04 1.1-1.10, item by item. Each is built as planned, and 05 lists all 9
deviations:
- 1.1: `_pick` (calendar, `third_fridays`, quoted-or-`NO_EXPIRY`, `_is_monthly` deleted).
- 1.2: basis floor (same logic as rules.py L308-312; basis = first close, then re-buy close + $0.01;
  split-adjusted, deviation 2).
- 1.3: `_tolerance` from cfg.
- 1.4: `a <= e <= b`, `_earnings_known`, ETF exempt, gap count.
- 1.5: `(d - open) * 3 <= life`.
- 1.6: no $0.03 floor; `sub_3c_sales` counted.
- 1.7: `costs.fees`, `cfg["r"]`.
- 1.8: every RI-002 point (`REALTEST_MISSING` with 8 rows, `_read`, skips, asserts, NaN plus reason, joint dropna,
  `picked: None`, bxm errors, narrowed except).
- 1.9: counts.
- 1.10: pct_change before slicing.

Tests in 04's table: all present. `test_drop_input` has 8 cases (7 planned plus asset_type).

Connectivity, re-done:
- AST scan: every top-level def and constant in realtest.py is used. `BOT_RULE` is used only by the tests and is a
  public constant.
- No module outside realtest imports it (grep).
- No TODO or FIXME.
- `python3.11 -m py_compile ccbot/realtest.py tests/test_realtest.py`: OK.
- `git status --short`: clean.

Grep reasons in 05: the 4 lines 05 gives reasons for check out. The plan's pattern can't see three `.get(`
lines, and all three are harmless:
- L161 `divs.get(d, 0.0) + a` adds up dividends paid on the same date.
- L235 `td.close.get(d)` is in the `_check_units` warning heuristic only.
- L776 `curves.get(bot.name) or {...}` recomputes the curves when they are missing.

## Tests re-run (output)
Full suite, `python3 -m pytest -q -p no:cacheprovider`:
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 292 passed, 1 skipped in 58.14s
```
- The skip is `tests/test_calendar.py:110: could not import 'exchange_calendars'`.
- `tests/test_safety.py`: 9 passed. python3.11 is on PATH, so `test_every_py_compiles_on_oldest_python` ran;
  python3.10 is not on PATH.
- `tests/test_realtest.py`: `38 passed in 28.08s`.

`python3 scripts/check_handoff.py 061`:
```
sources count (unique URLs in 01-research.md): 4
fact-check rows: 10
totals line: 10 rows -> 1 as-is, 9 fixed, 0 removed
PASS
```

RI-001 feasibility:
- `test_real_counts_bac` ×3 and `test_real_min_years_filter` pass. Their pinned values match 05's table (BAC bot
  rule: 24 calls, 369 NO_EXPIRY, 296 BASIS_ABOVE_BAND, 11 in window / 13 slack).
- I recomputed 01's numbers from `reports/real/` and all match: 250 calls; IV > RV 63.2%; mean P&L -0.083%; median
  gap +0.30; A2 13/17; A3 17/17; A4 0.0986 vs 0.0940; drawdown saved 0.78; walk-forward median -2.2e-16 with 8
  positive; reject totals 7,333 / 6,809 / 1,327 / 648 / 210; in-window 71, slack 179, sub-3c 8; early exercises 3,
  assigned 44; T/VZ/AAL calls 1/3/4; BXM 7.93% vs SPY 14.80%; fits_3k AAL and F; MC paths_used 10000.

RI-002 mutations, run in a scratch `git worktree` of HEAD under the scratchpad and removed afterwards. In each,
one removed default is put back; file restored = True.

| Mutation (removed default put back) | Result | Failing test |
|---|---|---|
| `premium_yield` `/ max(years, 1e-9)` | 1 failed, 37 passed | test_premium_yield_na_zero_years |
| Monte Carlo `.fillna(0)` for `.dropna()` | 1 failed, 37 passed | test_monte_carlo_no_fill |
| NaN dividend amount → 0.0 | 1 failed, 37 passed | test_nan_dividend_amount_skips |
| every dividends file read as empty (dividends silently none) | 2 failed, 36 passed | test_nan_dividend_amount_skips, test_drop_input[dividends] |
| walk-forward empty block → `configs[0]` | 1 failed, 37 passed | test_walk_forward_empty_training_block_not_picked |

## Open points from I2 (judged)
1. **03 Missing-inputs table is stale.** Its 3 rows don't match `REALTEST_MISSING`, which has 8 rows:
   - volhist is now NaN plus `atm_na_reason`, not "column absent".
   - BXM text is "BXM_History.csv: not supplied".
   - KGC's reason is "no option quotes".
   - prices, dividends, splits, earnings and asset_type have no row at all.

   I3 writes 06/07 only, so this goes back as **F4**.
2. **Earnings hole before the first date (BAC, CSX, USB) and inside gaps of more than 120 days (CMCSA, MDLZ, MO, T,
   VZ).** It has the RI-002 shape: an unknown earnings date in the call's life is read as "no earnings".
   - Measured in scratch: a stock gets EARNINGS_UNKNOWN unless a date also exists in the prior 120 days. Result:
     **247 calls (from 250); IV > RV 64.0%; mean P&L -0.095%; median gap +0.30; A2 13/17; A3 17/17; A4 0.099 vs
     0.094**. BAC drops 24 → 22, USB 11 → 10, OXY 8 → 7, CSX goes 37 → 38.
   - No A row changes. It is a research-only backtest; the bot path uses snapshot `next_earnings` with
     EARNINGS_UNKNOWN, so it is not affected.
   - Judgement: acceptable as a labelled limitation, and the build need not block. But 01 must give the measured
     impact (**F3**). A1 decides whether this counts as an RI-002 occurrence.
3. **01's proposed rules on a grid with less than 0.5 pt spread.**
   - Rule 1 is fine: it says the case is gone.
   - Rule 3 is fine.
   - Rule 2 claims too much: "a weak lean to letting in-the-money calls be assigned" rests on +0.4 / +0.3 / +0.2
     medians when most variants rarely sell.
   - Rule 4 claims too much: "skipping earnings is now worth ~0.1 pt/yr".
   - The grid line "57 of the 60 variants beat holding on the median stock" needs the same caveat as the verdict:
     they beat holding mostly by selling few calls.
   - Rule 4b (bid vs mid) is a direct cost, not noise, and is fine. → **F2**.
4. **The cost-basis floor dominates, and 01 leaves out the floor-off result.**
   - 01 states the dominance plainly: "the passes on A2-A5 mostly show that the rule rarely sold calls, not that
     selling calls paid".
   - 01 states that the gate still fails on A1: "A1 fails pooled ... The 'more than $5k' gate stays closed".
   - But 01 never gives the floor-off result (grep for 955, -1.38 and "floor off": no hits). Its "Why it moved:
     250 calls, not 942" compares against the old run, which differed in 7 ways, so it does not isolate the floor.
     **Required fix F1.**
   - My scratch numbers (bot rule, bid; A5 not re-run, because it needs the full grid):

| Start | Floor | Calls | IV>RV | Mean P&L | Median gap | A2 (≥9) | A3 | A4 cc vs hold | T/VZ/AAL calls |
|---|---|---|---|---|---|---|---|---|---|
| 2020-01-01 | on (as built) | 250 | 63.2% | -0.083% | +0.30 | 13 | 17 | 0.099 vs 0.094 | 1/3/4 |
| 2020-01-01 | off | 955 | 59.7% | -0.277% | -1.38 | 8 | 16 | 0.068 vs 0.094 | 61/58/63 |
| 2020-04-01 | on | 342 | 64.6% | -0.301% | +0.24 | 9 | 17 | 0.291 vs 0.284 | 14/6/9 |
| 2020-04-01 | off | 918 | 61.2% | -0.241% | -1.81 | 8 | 17 | 0.209 vs 0.284 | 59/56/61 |
| 2021-01-04 | on | 238 | 64.3% | -0.372% | +0.06 | 13 | 17 | 0.177 vs 0.175 | 7/2/5 |
| 2021-01-04 | off | 801 | 60.7% | -0.208% | -1.39 | 8 | 16 | 0.122 vs 0.175 | 52/49/53 |
| 2022-01-03 | on | 166 | 66.9% | -0.086% | +0.46 | 15 | 17 | 0.109 vs 0.087 | 11/8/8 |
| 2022-01-03 | off | 653 | 59.9% | -0.175% | -1.30 | 8 | 15 | 0.083 vs 0.087 | 42/39/43 |

   - A1 fails in all 8 runs.
   - With the floor off, A2 and A4 fail from every start, so the A2/A4 flip comes from the floor alone.
   - With the floor on, A2 and A4 pass from every start. But the margins are thin (A2 9 of 17 from 2020-04-01,
     where 9 is needed; A4 within 0.003-0.022), and the call count swings from 166 to 342 with the start date.
   - The 2020-01-06 basis sitting before the COVID crash explains T's 1 call. From 2020-04-01, T sells 14.
5. **`test_repo_pipeline_has_no_skipped_items` / UNTRACKED CHANGE for 49680f8, bdd67c9, 20b89e7.**
   - `untracked_changes` judges each first-parent commit after `UNTRACKED_FROM` on its own files. 061 becoming
     FULL, its 04-06 files, or an A1 PASS do not change it: those three commits changed code with no 01-06 step
     file, and they are history.
   - On this branch it stays red (gap (b): each direct commit is its own unit).
   - On main it clears **when the PR lands as a merge commit**. Probe, in a scratch worktree of origin/main
     (29a2b28) running `git merge --no-ff claude/project-thread-ltyppm`, then `check_pipeline.py`: the result is
     `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`, exit 0. The reason is that the merge is one unit, it carries
     `work/061/01-05`, and 061 is open at main's parent (no 07 there).
   - A squash or rebase merge would bring it back (gap (c)).
   - No exception list exists, and `UNTRACKED_FROM` says "never move it forward". So the only other way to clear it
     on the branch is a new item that changes check_pipeline.py, and the person would decide that.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (feasibility tests re-run and passing; pinned BAC counts match 05; 01's totals
recomputed from reports/real and matching), RI-002 (5 mutations each fail ≥ 1 test; grep reasons checked plus 3
harmless `.get(` hits; earnings hole measured: no A row changes, F3), RI-007 (ESCALATED: this 06 is the I3 step
061 skipped; UNTRACKED CHANGE is still on the branch and clears only via a merge commit, probe above),
RI-008 (python3.11 compile OK; python3.10 not on PATH), RI-010 (log line via `--log`), RI-011 (OPEN; no
branch-diff code touched), RI-012 (OPEN; the fetch retry substring was DROPPED by 04 with a reason and not
changed). GUARDED and looked at: RI-009 (probes in scratch worktrees, removed afterwards; `git worktree list`
shows only the repo).

## Pipeline line (step 2)
check_pipeline line: `061: in progress (FULL: next 07)`
(Taken after this 06 and its `--log` line: `INCOMPLETE: none`, `SKIPPED: none`. Before 06: `next 06`. The check reads "next 07" from the file's presence; the verdict above is FAIL, so no 07 is written until a re-verification passes.)

## Sent back / sent to Audit
Not sent to Audit. Sent back to **I2**. No code change; these are 01/03 text fixes. Then re-verify.
- **F1 (required).** In 01's Verdict, next to the floor-on result, add the bot rule with the floor off: 955 calls,
  mean P&L -0.28%, median gap -1.38, A2 8/17 (fail), A3 16/17, A4 0.068 vs 0.094 (fail). Say that the rest of the
  04 changes leave A2 and A4 failing, so the flip comes from the floor alone. Add the start-date line: from
  2020-04-01 / 2021-01-04 / 2022-01-03, the floor-on result passes A2 with 9 / 13 / 15 and fails A1 every time;
  floor-off fails A2 and A4 every time. Label all of this a scratch diagnostic, not in `reports/`, and give the
  command. Putting it in `reports/` would be a plan change, so it goes to I1.
- **F2.** Rules 2 and 4: replace "weak lean" and "worth ~0.1 pt/yr" with "no measurable difference (within the
  grid's < 0.5 pt spread)". Add to the grid paragraph that 57 of 60 beat holding mostly because the floor kept them
  out of the market.
- **F3.** In 01's earnings bullet, add the measured impact: blocking with no date in the prior 120 days gives 247
  calls, and A1-A4 are unchanged (numbers above).
- **F4.** 03 Missing inputs: replace the 3 stale rows with the 8 `REALTEST_MISSING` rows, add a dated note
  "(I2, 2026-11-14, after 061/04 build)", then re-run `check_handoff.py 061`. This is the same arrangement as I2's
  earlier 03 edit; if the coordinator prefers, R3 does it.
- Minor, not required: 02-improvements.md still says "Not modelled: the cost-basis floor". It needs a dated note,
  or 01's revision covers it.
