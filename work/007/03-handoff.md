# 03 Research hand-off - 007
Status: READY

Checked 2026-10-30 by R3.
- Holidays were checked against NYSE's official page (nyse.com/markets/hours-calendars) and the NYSE Group release of 2025-12-23.
- The table was cross-checked with `exchange_calendars` 4.13.2 (XNYS) in a scratch venv.
- I prototyped the fix with `pd.bdate_range(freq="C", holidays=…)` and the repo's `expiries` functions.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| F1: 2026 holidays Jan 1, Jan 19, Feb 16, Apr 3, May 25, Jun 19, Jul 3 (obs.), Sep 7, Nov 26, Dec 25; early closes Nov 27, Dec 24 at 1:00 p.m. (1:15 p.m. eligible options) | nyse.com + ir.theice.com release (fetched) | VERIFIED | – |
| F2: 2027 holidays Jan 1, Jan 18, Feb 15, Mar 26, May 31, Jun 18 (obs.), Jul 5 (obs.), Sep 6, Nov 25, Dec 24 (obs.); only early close Nov 26 | same | VERIFIED | – |
| R2 FOR 2: 2028 is in the same release, "R3 must copy them" | same | VERIFIED. **2028 holidays:** Jan 17, Feb 21, Apr 14, May 29, Jun 19, Jul 4, Sep 4, Nov 23, Dec 25 (9 days; New Year's Day 2028 is a Saturday and not observed). **Early closes:** Jul 3 and Nov 24, 2028 | – |
| F3: exchange_calendars XNYS gives the same 20 closed weekdays for 2026–2027, with early closes 2026-11-27, 2026-12-24, 2027-11-26 | re-run | VERIFIED. 2028 also matches (9 days; early closes 2028-07-03, 11-24) | – |
| F10: `start="2026-01-01"` raises `DateOutOfBounds` | re-run | **WRONG as stated** | In 4.13.2, `get_calendar("XNYS", start="2026-01-01")` works. The error I hit is the default **end** (about 1 year from today, 2027-10-29). A dev-only cross-check must pass explicit `start` and `end` (e.g. `end="2029-01-31"`) |
| F4: Cboe Rule 4.5(d): "…the Short Term Option Expiration Date for Short Term Option Weekly Expirations will be the first business day immediately prior to that Friday." | SEC 34-104643 ex5 (fetched) | VERIFIED | – |
| F5: OCC By-Laws, short-term options expire "on the first business day immediately prior to that Friday" | SEC 34-94646 ex5 (fetched) | VERIFIED | – |
| F6: Siebert 2022: "the monthly options which would normally expire on April 15th will be changed to expire on April 14th"; MIAX weeklies → Thu Apr 14 | siebert.com, miaxglobal.com (fetched) | VERIFIED | – |
| F7: no rule text found for standard monthlies falling on a holiday | Cboe/OCC exhibits (fetched): neither has it | VERIFIED as UNVERIFIED | The map relies on F6 + F8 (verified), and a test pins the Thursday date. A wrong assumption is fail-safe: no quotes → `NO_EXPIRY` |
| F8: FINRA 2360(b)(23)(A)(ii): options "expiring on a day that is not a business day" … "on the last business day before their expiration" | govinfo FR 2014-07-02 (fetched) | VERIFIED | – |
| F9: both packages install; Python 3.13.17 | re-run (`exchange_calendars` 4.13.2 installed) | VERIFIED for exchange_calendars; pandas_market_calendars not re-checked (not used) | – |
| Affected expiries: monthly 2026-06-19 → Thu 06-18, 2027-06-18 → Thu 06-17; no Good Friday is a third Friday | prototype | VERIFIED | – |
| Holiday weekly Fridays 2026-04-03, 07-03, 12-25, 2027-01-01, 03-26, 12-24 → Thursdays 04-02, 07-02, 12-24, 2026-12-31, 03-25, 12-23 | prototype | VERIFIED | – |
| OCC symbols carry the moved date (`…260618C…`) | – | UNVERIFIED (no source found) | Not asserted in the map. Symbols use the exchange expiration date, which Cboe 4.5(d) says *is* the Thursday. Check the paper log at the 2026-12-24 weekly |
| R1/request test: "scan for 2026-12-21 picks the 2026-12-24 weekly" | prototype + `weekly_dte: [5, 9]` | **WRONG** | 12-24 is 3 DTE from Monday 12-21, outside 5–9. The bot correctly returns None (as it does every Mon/Tue, `test_weekly_5_to_9_dte`). The correct dates are **2026-12-16/17/18 → (2026-12-24, True)**. On a Mon–Fri calendar these give 12-25, so the test catches the bug |
| R1 test: 2026-05-20 → monthly 06-18 (DTE 29) | prototype | VERIFIED: `pick_expiry(…, (30,45), 7)` = (06-18, False). Mon–Fri gives (06-19, True) | – |
| Request/R2: the OCC fallback `fridays(business_days(exp, exp))` on Thu 06-18 → `[]` | re-run | VERIFIED | Also: a holiday-aware window [06-18, 06-19] **still** returns `[]`, because `fridays` stops at the calendar's last day (06-18) before reaching Friday 06-19. The fallback needs a window that runs past the Friday (step 4) |
| R2 AGAINST 3: early closes are a separate hazard and must not go in the holiday list | NYSE page | VERIFIED: 2026-12-24 is both an early close and the moved weekly expiry | step 5 |
| Mandarin/Turkish/Japanese rows | fetched | VERIFIED (see 003/03) | – |

## Removed claims
- "2026-12-21 → 12-24 weekly" as a test (WRONG, replaced).
- "start=2026-01-01 raises" (WRONG, corrected).

## Implementation map
| Step | Change | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | **New `config/holidays.json`:** `{"source": "https://www.nyse.com/markets/hours-calendars", "release": "NYSE Group, 2025-12-23", "checked": "2026-10-30", "covers": ["2026-01-01", "2028-12-31"], "holidays": [29 dates from the fact check], "early_closes": ["2026-11-27", "2026-12-24", "2027-11-26", "2028-07-03", "2028-11-24"]}`. Early closes stay out of `holidays`. | NYSE page | config file | `tests/test_calendar.py::test_holiday_table_matches_nyse`: an exact set of the 29 dates plus the 5 early closes |
| 2 | `expiries.business_days(start, end, holidays=None)`. With `None`, it stays Mon–Fri (backtest `extend` and existing tests are unchanged). Otherwise `pd.bdate_range(start, end, freq="C", holidays=holidays)`. Add `load_holidays()` (reads step 1, cached). Add a comment on `_move_back` saying it looks back ≤ 4 days, which is enough for one holiday. | step 1 | calendar | Existing calendar tests pass unchanged |
| 3 | `expiries.scan_calendar(today, days=120)` passes the holidays. It **raises `ValueError("holiday table covers 2026-01-01..2028-12-31; add NYSE dates for <year> (source …)")`** if `today − 35` or `today + days` is outside `covers`. It never falls back to Mon–Fri. (With `days=120`, scans start raising from 2028-09-02, so 2029 must be added before then.) | step 1 | calendar or error | `::test_scan_calendar_raises_outside_table` for 2028-10-01 and 2025-12-15 |
| 4 | `webull_sandbox.py` L165: `exps = [e for e in expiries.fridays(expiries.scan_calendar(exp_from, days=(exp_to - exp_from).days + 7)) if exp_from <= e <= exp_to]`. The window runs past the Friday, so a holiday Friday moves back to Thursday. | step 3 | Thursday symbols | `tests/test_webull_sandbox.py::test_occ_fallback_builds_thursday_symbols`: make the SDK listing raise; for exp 2026-06-18 the result is non-empty and every symbol contains `260618` |
| 5 | Early-close warning: `report.daily_report` adds `> Early close today: 1:00 p.m. ET (1:15 p.m. for eligible options); run the scan before then.` when the scan date is in `early_closes`. It is information only, with no scheduling code. | step 1 | report line | `tests/test_report.py::test_early_close_banner_2026_12_24` |
| 6 | **Expiry tests (BUG guardrail, RI-003):** `::test_monthly_moves_to_thursday`: `third_fridays(scan_calendar(2026-05-20))` has 06-18 and not 06-19; `pick_expiry(2026-05-20, …, (30,45), 7) == (06-18, False)`; 2027-06-17 is in `third_fridays(scan_calendar(2027-05-20))`. `::test_weekly_moves_to_thursday`: for 2026-12-16, 12-17 and 12-18, `pick_expiry(d, fridays(scan_calendar(d)), (5,9)) == (2026-12-24, True)`; 2026-12-23 → (2026-12-31, True); 2026-12-21 → None. | steps 1–3 | tests | All fail on today's code (`scan_calendar` is Mon–Fri) and pass after |
| 7 | Optional dev check: `::test_table_matches_exchange_calendars` with `pytest.importorskip("exchange_calendars")` and `get_calendar("XNYS", start="2025-01-01", end="2029-01-31")`. Not a runtime dependency. | – | skipped test offline | Skips when the package is absent |
| 8 | A1: update RI-003 in `logs/recurring-issues.md` to GUARDED, citing steps 1, 3 and 6. Follow-up check: the paper log on 2026-12-16 to 12-18 should show `…261224…` symbols (this checks the UNVERIFIED OCC-date item). | – | log entry | A1 |
