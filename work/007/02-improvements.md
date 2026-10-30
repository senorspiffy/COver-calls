# 02 Improvements - 007
## What past logs say
- RI-003 (new, 1 occurrence). I3 first noted the Thursday OCC fallback in 002/06. The backtest is not affected (it uses the CSV's dates).
- `pyproject.toml` runtime dependencies are only `numpy` and `pandas`. A1 found external hosts blocked except PyPI, so tests must run offline.

## 3 ways FOR
1. **Use a sourced table in `config/holidays.json` (NYSE release, 007/01 F1/F2) passed to `pd.bdate_range(..., freq="C", holidays=...)`.** pandas already supports a custom holiday list, so `business_days` changes by one argument. The existing `_move_back` then gives Thu 2026-06-18 and Thu 2026-12-24 with no new logic. No new dependency, works offline, easy to test. This is the simplest fix that closes the bug (reasoning from the code, `ccbot/expiries.py`).
2. **Fail loudly past the table's end (R1).** `scan_calendar` raises for any date beyond the last listed year, so the code cannot silently go back to Mon–Fri (the RI-002 policy applied to calendars). R1 says the same NYSE release includes 2028, so add 2028 now. Its dates are not recorded in 007/01, so R3 must copy them from the source. The table then lasts until 2028-12-31.
3. **Cross-check against `exchange_calendars` in a dev-only test, skipped if the package is absent.** R1 found the 2026–2027 sets identical (007/01 F3). The table gets an independent check without making the package a runtime dependency (4 transitive packages, 007/01 F9, and a `DateOutOfBounds` gotcha, F10).

## 3 ways AGAINST
1. **A hand-kept table goes stale and misses unscheduled closures.** Someone must add 2029 before 2029, and an unexpected closure (e.g. a national day of mourning) is not in it. The raise in FOR 2 handles going stale, but nothing handles an unscheduled closure. `exchange_calendars` has the same gap until the package is updated, so this is not a reason to prefer it. On such a day the scan simply sees no quotes, which fails safe (request evidence).
2. **The rule for monthlies on a holiday rests on precedent, not rule text (007/01 F7 UNVERIFIED).** The Chinese row in the 003 table shows the direction is set by each exchange: Shanghai moves expiries *later* (顺延). For the US, a broker notice (F6) and the weekly rule (F4/F5) both say *earlier*. The code should cite that as the basis and keep the test on 2026-06-18, so a wrong assumption shows up as a failing test rather than in production.
3. **Early closes are a separate hazard that the table does not cover.** 2026-12-24 is an early close (1:00 p.m., 1:15 p.m. for eligible options, F1) *and* the moved weekly's expiry day. A scan run at the usual time could be after the close. Turkish (003 table) shows some exchanges even move expiry for half days. The US does not, so early closes must **not** go into the holiday list, but the bot needs an `early_close` list to schedule its scan or skip. Without that, the 12-24 test passes while the real scan is too late.

## Findings by language
See `work/003/02-improvements.md` § Findings by language (random: Arabic, Hindi, Turkish). Relevant: Mandarin Chinese (Shanghai moves holiday expiries later), Turkish (Borsa Istanbul moves expiry back even for half days), Japanese (the Nikkei index falls back to discretion for unlisted events, which the bot must not do).

## Holes to watch out for (summary)
- The Thursday OCC fallback (`webull_sandbox.py` L165) needs a window that includes the Friday, or an `expiry_days()` helper. The holiday table alone does not fix `fridays(business_days(exp, exp)) → []`.
- `_move_back` looks back at most 4 days. That is fine for single holidays, but say so in the code.
- Tests: 2026-12-21 → 12-24 weekly; 2026-05-20 → 06-18 monthly; fallback on 06-18 builds symbols; 2027-06-17; past-table date → raises.
- Whether Webull lists the Thursday date: UNVERIFIED. The sandbox log should be checked on 2026-12-21.
