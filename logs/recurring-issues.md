# Recurring issues

Kept by A1. Read by every R and I agent (R1, R2, R3, I1, I2, I3) before every item. One entry per root cause.
Any entry with 3+ occurrences is ESCALATED: the guardrail didn't hold and the person is told.

<!-- Entry format:
## RI-001: Rule or window assumed to have candidates, never computed
Status: ESCALATED (4 occurrences, all found 2026-10-30). The systemic guardrail is now in place (003/004, uncommitted), but it has not been tested at the stage where the errors arose. Reviewed in the follow-up audit, 2026-10-30.
Root cause: a filter (universe price/asset cap, DTE window, delta band, weekday window) is written as a rule or test expectation without anyone computing how many tickers/days/strikes pass it. "Always found" or "exists" is asserted, not measured.
Guardrail(s) added:
- Code (002): `screen.feasible_universe` + "UNIVERSE EMPTY" banner, `tests/test_screen_bot.py::test_universe_empty_blocks_orders`, `::test_shipped_config_has_a_passing_ticker`. Synthetic data only.
- Code (002): `tests/test_calendar.py` coverage asserts; Mon/Tue weekly → None.
- Fix 003: 001 step 1 now states a dated screen result ("0 tickers confirmed on monthly quotes", `work/001/03-handoff.md` § Correction 2026-10-30). The "5 of last 10" count is built as information only (`screen.pass_history`, `test_pass_history_counts_last_10`, `test_daily_report_shows_pass_history`).
- Fix 004: 001 steps 4/5/8/11/Alt. 1 state the bot's rule (30–45, else ±7 d slack; nearest 0.275Δ in [0.20, 0.35]).
- Guardrail tests (004): `test_calendar.py::test_monthly_coverage_2016_2025` pins 1,440 / 2,483 / 2,609 and fails with `monthly_slack_days: 0` (17 failed, 05). `test_pricing.py::test_tolerance_finds_strike_on_bs_grid`. A1 re-ran them: pass.
- Process (003/004): Feasibility column in `templates/research-handoff.md` (0 or blank → BLOCKED); Rule trace and Guardrail tests in `templates/build-plan.md`; r3 step 1 feasibility text; i1 step 1a; i3 step 3. A1 confirmed each is present in `git diff` (additions only). These need the person's OK in PR review.
Why still ESCALATED: every occurrence was a process error at R3 → I1, and the process guardrail has never run. The 003–008 hand-offs were written before the column existed, so none has a Feasibility column (grep, 2026-10-30). The code tests pin only the two windows already found. They would not catch the next unmeasured rule. **Move to GUARDED when:** the process edits are approved and committed, and the first R3 hand-off after that fills the Feasibility column with a computed, re-runnable count for every filter rule (A1 checks it).
Occurrences: 4
- 2026-10-30 | 003 (fixed) | work/001/03-handoff.md step 1 | "diversified ETF ≤ $28" – no diversified ETF passes; the 4 that pass do so only at Δ0.11–0.23 (002/03 L114)
- 2026-10-30 | 004 (fixed) | 001 step 4, 002/03 step 6, 002/04 test_calendar | "30–45 DTE always found" – A1 measured 55.2% of 2016–2025 days; none on 2026-10-30
- 2026-10-30 | 004 (fixed) | 001 step 5 | 0.25–0.30Δ band often has no listed strike (~0.10Δ per $0.50 strike, 002/04 research 1); code uses [0.20, 0.35]
- 2026-10-30 | 002 (fixed by I2, 05 deviation 3) | 002/04 test_calendar | "Weekly picks 5–9 DTE on every Monday" – 0 of 522 Mondays

## RI-002: Missing or uncomputable data silently turned into a value
Status: ESCALATED (9 occurrences). 2026-11-05: 041 is merged (PR #11, 2026-11-05 00:23 UTC) and holds: A1 probe F 2026-11-20 → ex_div None, dividend/div_next NaN; 11-09 → div_next 0.15; stale guard removed → 2 failed. Its GUARDED condition is not met: `TICKER_FIELDS` is a hand list, `enrich` already reads `asset_type` and `last_earnings` outside it, and adding `"foo_date": null` to F in tickers.json leaves `tests/test_missing_inputs.py` green (20 passed, A1 scratch copy) → 046. No new occurrence (both unlisted keys fail safe: no asset_type → Day default "stock", no last_earnings → EARNINGS_UNKNOWN). 041/05: "RI-002: guardrail built (041); GUARDED when merged and a new unlisted tickers.json key fails the enumeration test." 2026-11-04: the 2026-11-03 occurrence (038, earnings estimate) is settled: the person chose the estimate as a labelled house rule (040, 001 § Correction Step 3) and merged PR #5. New occurrence in 040's `tickers.enrich`: a past ex-dividend date becomes dividend/div_next 0.0, and tickers.json has no MISSING_POLICY rows (041). 2026-11-03: the broker code path is now GUARDED on main (014 merged in PR #7, 2026-11-02; A1 re-ran `div_next` 0.0 → `test_day_float_defaults_are_nan` fails). New occurrence on open PR #5 (038), so the entry stays ESCALATED. The guardrail added in 005/006 works for loader inputs. Two occurrences on the broker path got past it (014), and one in research text (025, fixed and merged in PR #6, 2026-10-31). 2026-11-01: no new occurrence. 2026-11-02: correction, 014 was not "not started": it is built in PR #7 (2026-10-31, unmerged; see RI-009). A1 re-ran its two mutations in scratch: both fail a test.
Root cause: when a value cannot be computed from the data available, the code fills, defaults, or tie-breaks it into a number (or into "OK") instead of keeping it NaN/n/a/unknown and saying why.
Guardrail(s) added:
- Standing rule (002/04 Revision 2). Tests (002): `test_realized_vol_uses_only_past_closes`, `test_no_option_sold_during_vol_warmup`, `test_pbo_undefined_on_too_few_months[0,1,7]`, `test_short_csv_reports_pbo_na_without_warnings`. They still pass.
- Fix 005: `EARNINGS_UNKNOWN`, `OI_UNKNOWN`, `DIVIDEND_UNKNOWN`. `Day.earnings_known` (default False, so a bare Day fails safe). `PriceSeries.missing`. `## Missing inputs` report section.
- Fix 006: `bh_lots` (no `max(1,`), `bh_na_reason`, B&H n/a with reason, weekly report n/a.
- Guardrail (005/006): `ccbot/missing.py::MISSING_POLICY` (9 rows); `tests/test_missing_inputs.py::test_drop_each_input[9]` + `test_policy_lists_every_optional_input`; `test_benchmark_cash_never_negative`; the widened grep in i2; the r3 step 3a and i1 step 1a policy lines; the i3 mutation step. A1 re-ran the mutations in scratch: `max(1,` in `bh_lots` → 3 failed; `else 0` in data.py → 2 failed; removing the screen's `EARNINGS_UNKNOWN` → 2 failed.
- Built (014, merged PR #7 2026-11-02; GUARDED for the code path): `Day.q/dividend/div_next` default to NaN; sim sets dividend/div_next from the ex-date (unknown amount → NaN → `DIVIDEND_UNKNOWN` / `EARLY_ASSIGN_CHECK_NA` events); `q` is a labelled fallback; `_reject` returns `CAPITAL_UNKNOWN` and its cap tests fail closed; policy rows `broker.dividend`, `broker.q`, `model.oi`, `derived.capital`; tests `test_every_day_default_is_listed`, `test_day_float_defaults_are_nan`, `test_broker_capability_flags_have_policy_rows`, `test_drop_each_input[broker.*, model.oi, derived.capital]`. Mutations: q default 0.0 → 1 failed; no CAPITAL_UNKNOWN → 1 failed; `>` cap test → 1 failed; div_next 0.0 → 1 failed.
- Fix 025 (merged PR #6): r1/r3 step 3a report each screened ticker's bot reject code; an unpublished value stays UNKNOWN (`MISSING_POLICY`); `test_drop_each_input[snapshot.next_earnings]` pins blank earnings → `EARNINGS_UNKNOWN`. A1 checked both agent files 2026-11-01.
Built (041, merged PR #11 2026-11-05): past `ex_div_date` → unknown (NaN); `tickers.*` policy rows; `TICKER_FIELDS` in the enumeration test; drop tests; `test_enrich_past_ex_div_is_unknown`.
Proposed (046): the enumeration reads the keys from config/tickers.json and from `f.get(...)`/`f[...]` in ccbot/tickers.py, so an unlisted key fails; rows for `tickers.asset_type` and `tickers.last_earnings`.
Why still ESCALATED: 2026-11-05: the 041 enumeration lists keys by hand, so the next new key can be missed the same way (probe above). **Move to GUARDED when** 046 is merged and an unlisted key in tickers.json or tickers.py fails a test. 2026-11-04: a new input path (tickers.json, 040) came in outside the enumeration, the same gap as 014's. **Move to GUARDED when** 041 is merged and its enumeration test fails on a new unlisted tickers.json key. Earlier: `test_policy_lists_every_optional_input` enumerates only `OPTIONAL_CSV_COLUMNS` and `OPTIONAL_SNAPSHOT_FIELDS`. Values that enter as dataclass defaults (`Day.q/dividend/div_next = 0.0`) or derived values (`capital`) are outside it, and the review grep cannot see them. I2 and I3 each flagged one (05 "Finding", 07 §1). A1 reproduced both. **Move to GUARDED when** 014's extended enumeration test is in and fails on the 0.0 defaults. 2026-10-31: the policy is enforced only in code. Research (023) filled an unknown earnings date with reasoning and told the person F and VALE pass. 025's research rule is now in r1/r3 (2026-10-31); still needs 014. 2026-11-02: 014's `test_day_float_defaults_are_nan` fails when `div_next` defaults to 0.0 (A1, scratch); GUARDED once PR #7 is merged.
Occurrences: 9
- 2026-10-30 | 002 (fixed) | ccbot/data.py::realized_vol | warm-up vol back-filled from later closes (look-ahead); I3 06 first pass
- 2026-10-30 | 002 (fixed) | ccbot/walkforward.py::pbo_cscv | empty CSCV blocks → NaN → PBO 0.000; held-out config tie-broken on 0 train years; I3 06 Re-verification
- 2026-10-30 | 005 (fixed) | ccbot/data.py L78–79, screen.py L36/L39, webull_sandbox.py L144 | missing earnings/OI/dividend treated as none/pass; earnings blackout never runs on the sandbox broker
- 2026-10-30 | 006 (fixed) | ccbot/backtest.py L121, report.py L168 | B&H forces 1 lot when 100 sh > cash − buffer → cash −$600 benchmark
- 2026-10-30 | 014 | ccbot/rules.py L75–77, broker/sim.py L67–71, broker/webull_sandbox.py L144 | broker `Day.q/dividend/div_next` = 0.0 → `DIVIDEND_UNKNOWN` can never fire on the broker path. SYNTH_A's snapshot ex-div is 2026-12-18 and today's call `SYNTH_A261218C00026000` expires that day, but the rules saw `div_next = 0.0` (A1 probe)
- 2026-10-30 | 014 | ccbot/screen.py::_reject L28/L30 | NaN capital passes PRICE_CAP and SINGLE_NAME_CAP (`x > NaN` is False). The probe with capital NaN lets SYNTH_C through, while at $3,000 it gets PRICE_CAP
- 2026-10-31 | 025 | work/023/01-research.md L70/L79, screen-summary.md, work/001/03-handoff.md Correction "Step 1 and 9(a)" | F and VALE reported as passing; next earnings dates unpublished → `EARNINGS_UNKNOWN` by 001 step 3 and `screen._reject`
- 2026-11-03 | 038 | PR #5 (claude/project-thread-xrug2s) ccbot/tickers.py::enrich | unpublished next earnings estimated as last report + 70 days for F, VALE, AAL, so they pass instead of `EARNINGS_UNKNOWN`; written 2026-10-31 before 025's rule, never through R3/I3. Settled 2026-11-03 by the person's decision (040)
- 2026-11-04 | 041 | ccbot/tickers.py::enrich L48–52 (040, on main) | past ex_div_date (F, 2026-11-10) → dividend/div_next 0.0 on 2026-11-20 instead of unknown; next ex-date unpublished. No `tickers.*` rows in MISSING_POLICY

## RI-003: Scan calendar ignores exchange holidays
Status: GUARDED (since 2026-10-30, 007; merged in PR #2, 2026-10-31)
Root cause: `expiries.business_days` is Mon–Fri with no holiday list, so holiday-moved expiries get the wrong date or symbol.
Guardrail(s) added (007):
- Fix: `config/holidays.json` (NYSE 2026–2028: 29 holidays, 5 early closes; A1 checked each date against the NYSE rules). `scan_calendar` raises outside `covers` and never falls back to Mon–Fri. `Broker.calendar`. The Thursday OCC fallback in webull_sandbox and sim. Early-close banner.
- Tests: `test_holiday_table_matches_nyse`, `test_scan_calendar_raises_outside_table[2]`, `test_monthly_moves_to_thursday`, `test_weekly_moves_to_thursday`, `test_occ_fallback_builds_thursday_symbols`, `test_early_close_banner_2026_12_24`, `test_scan_outside_holiday_table_changes_nothing`; `test_table_matches_exchange_calendars` (skips offline; I3 ran it in a scratch venv: pass). Mon–Fri mutation → 3 failed (05, 06). A1: the suite passes; `scan --date 2028-10-01` → exit 2, no state dir; the 2026-12-16 calendar includes Thursday 2026-12-24.
- Follow-ups (not guardrail gaps): (1) the paper log for 2026-12-16 to 12-18 should show `…261224…` symbols (OCC date still UNVERIFIED); A1 checks it then. (2) The scan refuses from **2028-09-03** (A1: 09-02 ok, 09-03 raises). Add the 2029 NYSE dates before then. The refusal is loud, so this can't fail silently.
Occurrences: 1
- 2026-10-30 | 007 (fixed) | ccbot/expiries.py, webull_sandbox.py L165 | June 2026 monthly computed as 06-19 (holiday); Thursday OCC fallback → []

## RI-004: Worked example not checked against the rule it shows
Status: GUARDED (since 2026-10-30, 008; merged in PR #2, 2026-10-31)
Root cause: R3 checks an example's arithmetic but not whether each step meets the rule's thresholds/tick.
Guardrail(s) added (008):
- Fix: 001 § Correction, worked example: limit $0.23 (48.9% of $0.47), profit $23.80, day ≤ 11 of 35. A1 re-computed: 0.5 × 0.47 = 0.235 → $0.23 at the $0.01 tick; (0.47 − 0.23) × 100 − 0.20 = 23.80; 11 × 3 = 33 ≤ 35, 12 × 3 = 36 > 35.
- Test: `test_backtest.py::test_worked_example_50pct_exit` (ask 0.23 → exit, 0.24 → hold; day 11 exit, day 12 hold). It passes. I3 showed the two original claims fail as assertions on the old code.
- Process: the r3 step 1 worked-example sentence (in `git diff`; needs the person's OK). It has not yet run on a new example. 015 moves it to its own step 1b so it isn't buried.
Occurrences: 1
- 2026-10-30 | 008 (fixed) | work/001/03-handoff.md worked example | 50% buy-back "fills at $0.24" = 51.1% of $0.47; V1 code (`ask ≤ 0.5 × premium`) would not fire

## RI-005: Numbers in the hand-off not re-checked against the rule they belong to
Status: GUARDED (PR #3 merged 2026-10-31). Overlaps RI-004: item 018 and item 008 are the same 50% example, found by two separate runs.
Root cause: R3 changes a rule (adds a buffer, sets a % trigger) but does not re-derive the thresholds and worked-example numbers from that rule's own formula, so the text and the check disagree.
Guardrail(s) added: Self-check section in `templates/research-handoff.md` + R3 duty 5 + A1 spot-check (017, 018); merged in PR #3. A1 checked every 025–030 Self-check 2026-11-01.
Occurrences: 2
- 2026-10-30 | 017 | work/001/03-handoff.md step 1, step 9(a) | "2 at ≥ $5.6k" / "one ≤ $55" fail step 1's own check `(price × 100 × positions) ≤ cash − $200` (need $5,800 / $5,700)
- 2026-10-30 | 018 | work/001/03-handoff.md worked example | 50% exit filled at $0.24 on a $0.47 sale = 51.1% (> 50% trigger)

## RI-006: Hand-counted totals in hand-off and logs
Status: GUARDED (PR #3 merged 2026-10-31)
Root cause: R3 counts fact-check rows by hand and "fixed" vs "removed" is undefined, so totals, the removed list and the log line drift apart.
Guardrail(s) added: `scripts/check_handoff.py` run by R3, I3, A1 + fixed/removed definitions in template (019); merged in PR #3. `--all` with LEGACY list since 028.
Occurrences: 1
- 2026-10-30 | 019 | work/001/03-handoff.md Totals + logs/research/2026-10-30.md 17:33 | 77 rows in table vs "76 rows → 60/12/4"; removed list has 7 entries vs "4 removed"

## RI-007: Work used before its pipeline steps ran
Status: GUARDED (4 occurrences; since 2026-11-05). 2026-11-05: 038 (PR #10) and 042 (PR #11) are merged; both conditions met. A1 probes on a scratch copy of main: `Scope: FAST (I2, 2026-11-05)` → `SKIPPED (FAST needs (person, <date>)...)`; last A1 line FAIL → `A1 FAIL`, exit 1; 040's line is now `Scope: FAST (person, 2026-11-03)` and matches its recorded decision. `check_pipeline.py` on main: SKIPPED none, A1 FAIL none. 042/05 and 038/05 guardrail status copied here. 2026-11-04: PR #5 settled (merged with the person's FAST decision as 040; 01/03/06 written before merge). 038 is built in PR #10 (038/05: "RI-007: guardrail built (038); GUARDED when merged and PR #5 is closed or re-run under its own ID"). New gap (probe, no occurrence, like 031): any `Scope: FAST` line passes whoever wrote it, and `A1 result: FAIL` counts as complete (042). 2026-11-03: 031 and 035 are merged (PR #8, #9) and hold on main (`test_fact_check_and_verification_waivable_only_by_person`, `test_complete_needs_a1_result`; 009–016 got A1 lines in 5de9838). New occurrence: PR #5 has request + 05 only, and the check never applies Scope rules to open branches (038). 035/05: "RI-007: 035 closes the 033 date gap; still ESCALATED until 031 and 035 are merged." 2026-11-01: 026 is merged and `check_pipeline.py` shows SKIPPED: none, which met the condition below. A1 kept it ESCALATED because the guardrail can be bypassed: a `Waived: 03 06` line from anyone turns an item with no fact check or verification into `complete` (probe, 031). No step has been skipped since; the 023/024 waivers were approved by the person (PR #6). 2026-11-02: 031 is in PR #8 (unmerged). Second gap found: 033's `awaiting A1` is keyed on the request date, so 009–016 (dated 10-30, built 10-31 in PR #7) would show complete unaudited (A1 probe on a scratch merge) → 035.
Root cause: run-item.md has no rule for a person asking to go faster, and no check compares an item's files with its Scope. Steps are skipped silently; fixes made in other threads skip the pipeline entirely.
Guardrail(s) added: 026 (merged PR #6): `scripts/check_pipeline.py` + `tests/test_pipeline_check.py` (A1 daily, I3 per item); `Scope: FAST (person, <date>)` may skip R2/I1, never R3 or I3; `Waived:` lines; a fix made outside the pipeline gets a work item the same day.
Built (031, merged PR #8): a waiver of 03 or 06 counts only when the person gave it; otherwise SKIPPED.
Built (035, merged PR #9): every item except a closed pre-033 list needs an `A1 result:` line before it shows complete.
Built (038, merged PR #10 2026-11-05): `BRANCH SKIPPED:` for open-branch items that skip a step.
Built (042, merged PR #11 2026-11-05): FAST counts only as `FAST (person, <date>)`; last A1 line FAIL → `A1 FAIL`.
**Move to GUARDED when:** PR #10 (038) and 042 are merged. (PR #5's condition is met: re-run as 040.)
Occurrences: 4
- 2026-10-31 | 026 | work/023 | RESEARCH ONLY item stopped after R1 (no 02/03/07); result changed 001 and opened 024
- 2026-10-31 | 026 | work/024 | FULL item built and merged with only request + 05 ("short path"); no I3
- 2026-10-31 | 026 | commits d994307, cf3ba3b | UTF-8 fix with no work item or log line; first commit missed 6 calls and added 3.12-only syntax (027)
- 2026-11-03 | 038 | PR #5 work/025 (branch claude/project-thread-xrug2s) | 18 files of code/config with request + 05 only (no 01–04, 06, 07); `classify` → SKIPPED; never reported because the check skips open-branch Scope

## RI-008: Code not checked against the minimum Python the project declares
Status: GUARDED (027 merged PR #6; 2026-11-01 A1 compiled every tracked `.py` with python3.11: no errors). 032 proposes running that compile as a test.
Root cause: tests run only on the machine's Python (3.13); `pyproject.toml` says ≥ 3.10.
Guardrail(s) added (027): `test_fstrings_parse_on_python_310` + `test_same_quote_check_catches_the_027_line`; I3 step 2 runs `python3.11 -m py_compile` where available.
Occurrences: 1
- 2026-10-31 | 027 | scripts/check_handoff.py L49 | `f"...{...read_text(encoding="utf-8")...}"` → SyntaxError on Python 3.11

## RI-009: Work on unmerged branches invisible to the audit
Status: GUARDED (3 occurrences; since 2026-11-05). 2026-11-05: 037 is merged (PR #10) and holds: `--next-id` → 045 on main (used for today's 045, 046), `ID CLASH: none`; `test_same_id_on_main_and_open_branch_is_a_clash`, `test_next_id_counts_open_branches`, `test_open_branch_line_shows_last_commit_age` pass. No open branch today (all 11 remote branches are merged into main). 2026-11-04: no new occurrence. PR #5 merged and renumbered 040, so the 025 clash is gone. 037 is built in PR #10 (037/05: "RI-009: guardrail built (037); moves to GUARDED when merged and new items take their ID from --next-id"); A1 took 041–044 from `--next-id` on a scratch merge of PR #10 and main. 2026-11-03: 034 is merged (PR #9) and lists open branches, but it joins items by ID: PR #5 and main each have their own `work/025`, so `IN PR: none` while PR #5 waits (037). Why the guardrail didn't hold: it assumed one ID = one item across branches; nothing stops two threads taking the same next number. 034/05: "RI-009: guardrail built (034); moves to GUARDED when merged and the next daily audit shows IN PR correctly."
Root cause: `check_pipeline.py` and A1's daily review read only the working tree (main). A fix branch waiting for the person's merge is outside it, so STUCK means "not on main", and new branches are built without the rules open PRs add.
Guardrail(s) added: Built (034, merged PR #9): `check_pipeline.py` reports `IN PR (<branch>)` for items whose steps exist on an unmerged remote branch, and an `OPEN BRANCHES:` line with each branch's items and merge conflicts against HEAD; A1 lists both at the top of the daily report. Built (036, merged PR #9): fix branches don't edit this file. Built (037, merged PR #10 2026-11-05): `ID CLASH:` line and `--next-id` over HEAD and open branches.
**Move to GUARDED when:** 037 is merged and the daily check shows the 025 clash (or PR #5 is settled) with `--next-id` used for new items.
Occurrences: 3
- 2026-11-01 | 034 | logs/audit/2026-11-01.md | 009–016 reported STUCK and 014 "not started"; all eight were done in PR #7 (2026-10-31 22:39 UTC). PR #7's conflicts with main went unreported
- 2026-11-01 | 034 | work/032/06-verification.md | PR #8 built without PR #7's "scratch copy, never in the repo" i3 rule; I2's in-repo `git checkout` restore wiped the uncommitted 031 edit (re-applied)
- 2026-11-03 | 037 | work/025 on main vs PR #5 | two different items numbered 025; check_pipeline reports `025: complete`, `IN PR: none`; PR #5 unflagged through two audits

## RI-010: A step's own checklist skipped, with nothing to check it
Status: ESCALATED (3 occurrences). 2026-11-05: 043 is merged (PR #11) and its fixtures hold (A1 probe: item with no log lines and no RI line → INCOMPLETE, exit 1). New occurrence in 043's own first run: the 12 log lines for 041–044 all read `23:10`, but the commit that added them (a975744) is 2026-11-04 22:24:41 UTC, 46 minutes earlier; I1/I2 fields are `see 04` / `see 05` instead of `<n> files planned` / `<files changed>`; 043/06 says the repo check ran "before the 041–044 log lines were written". **Why the guardrail didn't hold:** 043 checks that a `| <agent> | <ID> |` line exists, not that it was written when the step ran or that its fields follow the agent's format, so a batch of lines typed at the end passes. 043/05: "RI-010: guardrail built (043); GUARDED when merged and 041–044 show no INCOMPLETE on main." (met in letter only).
Root cause: some step duties (I3 step 0 "name the recurring issues checked", step 2 "paste the check_pipeline line", every agent's log line) exist only in the agent text; the template has no field for them and no script checks them, so files written outside run-item skip them first.
Guardrail(s) added: Built (043, merged PR #11 2026-11-05): `Recurring issues checked:` and `check_pipeline line:` fields in `templates/verification.md`; `INCOMPLETE:` in `check_pipeline.py` for items from 041 on.
Proposed (045): `check_pipeline.py --log <agent> <ID> <fields>` writes the line with the current UTC time and refuses fields that don't match the agent's format; `INCOMPLETE` for a malformed line and `LOG TIME:` for a line whose time is after the commit that added it (items from 045 on).
**Move to GUARDED when:** 045 is merged and the first items after it have every log line written by `--log` (A1 checks `LOG TIME: none`).
Occurrences: 3
- 2026-10-31 | 043 | work/013–016/06-verification.md (a95a51a, the commit that added i3 step 0) | no recurring issue named in any of the four
- 2026-11-03 | 043 | work/040/06-verification.md; logs/ | no RI named, no check_pipeline line; R1/R3/I3 for 040 have no log line
- 2026-11-04 | 045 | logs/research/2026-11-04.md, logs/implementation/2026-11-04.md (a975744, 22:24:41 UTC) | 12 lines for 041–044 timed 23:10, after their commit; I1/I2 fields `see 04` / `see 05`; written in one batch after I2's test run (043/06)
