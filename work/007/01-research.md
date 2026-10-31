# 01 Research brief - 007
## Question
Which days is the US equity/options market closed in 2026–2027, how do monthly and weekly expiries move when their Friday is a holiday, and can the repo use a calendar package or should it hard-code a table?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- F1. NYSE Group's 2026 holidays (release dated Dec 23, 2025) are Jan 1 (Thu), Jan 19, Feb 16, **Apr 3 (Good Friday)**, May 25, **Jun 19 (Fri)**, **Jul 3 (Fri, observed)**, Sep 7, Nov 26 and **Dec 25 (Fri)**. Early closes (1:00 p.m., or 1:15 p.m. for eligible options) are Nov 27 and Dec 24. [https://ir.theice.com/press/news-details/2025/NYSE-Group-Announces-2026-2027-and-2028-Holiday-and-Early-Closings-Calendar/]
- F2. NYSE's 2027 holidays are **Jan 1 (Fri)**, Jan 18, Feb 15, **Mar 26 (Good Friday)**, May 31, **Jun 18 (Fri, Juneteenth observed)**, Jul 5 (Mon, observed), Sep 6, Nov 25 and **Dec 24 (Fri, Christmas observed)**. The only early close is Nov 26. [same URL]
- F3. A cross-check with `exchange_calendars` 4.13.2 (calendar `XNYS`, run today in a scratch directory) lists exactly the same 20 closed weekdays for 2026–2027, and early closes on 2026-11-27, 2026-12-24 and 2027-11-26. [https://pypi.org/project/exchange-calendars/] (run output, 2026-10-30)
- F4. Weeklies, Cboe Rule 4.5(d): "if the Exchange is not open for business on a Friday, the Short Term Option Expiration Date for Short Term Option Weekly Expirations will be the first business day immediately prior to that Friday." [https://www.sec.gov/files/rules/sro/cboe/2026/34-104643-ex5.pdf]
- F5. OCC's By-Laws define a short term option the same way: if the Friday is not a business day, the option expires on "the first business day immediately prior to that Friday." [https://www.sec.gov/files/rules/sro/occ/2022/34-94646-ex5.pdf]
- F6. Monthlies, precedent: in April 2022, when Good Friday fell on the third Friday, "the monthly options which would normally expire on April 15th will be changed to expire on April 14th." [https://www.siebert.com/company/client-news/2022/04/14/market-closure-in-observance-of-good-friday] (a broker notice). MIAX gave the same Thursday date for its weeklies that week. [https://www.miaxglobal.com/alert/2022/04/04/miax-exchange-group-holiday-schedule-good-friday-2022]
- F7. I could not find the OCC By-Laws or Cboe rule text for standard (third-Friday) expiries falling on a holiday. The rule "monthly moves to the prior business day" rests on F6 and on matching F4/F5. UNVERIFIED as rule text.
- F8. FINRA Rule 2360(b)(23)(A)(ii)–(iii): for options "expiring on a day that is not a business day", the exercise procedures apply "on the last business day before their expiration". [https://www.govinfo.gov/content/pkg/FR-2014-07-02/html/2014-15477.htm]
- F9. Both packages install here. `pip install --dry-run` would install `exchange_calendars-4.13.2` (pulls in korean_lunar_calendar, pyluach, toolz, tzdata) and `pandas_market_calendars-5.5.0` (which also pulls in exchange_calendars). Python 3.13.17. The real install into a scratch dir worked and gave a harmless dateutil warning from an unrelated package (conan). (run output, 2026-10-30)
- F10. XNYS in exchange_calendars 4.13.2 has no sessions before 2026-01-02 when you ask for `start="2026-01-01"`, which raises `DateOutOfBounds`. You must ask for a start before the dates you query. (run output)

## Numbers used (show the math)
- Expiry dates affected in 2026–2027, from F1/F2: third Fridays are 2026-06-19 → **Thu 2026-06-18** and 2027-06-18 → **Thu 2027-06-17**. None of the Good Fridays is a third Friday (2026-04-03 and 2027-03-26; the third Fridays are 04-17 and 03-19).
- Weekly Fridays that are holidays: 2026-04-03, 2026-07-03, 2026-12-25, 2027-01-01, 2027-03-26 and 2027-12-24. These move to Thursday 04-02, 07-02, 12-24, 2026-12-31, 03-25 and 12-23.
- OCC symbols use the moved date. The June 2026 monthly $26 call is `XXX260618C00026000`, not `…260619…`. That this is the OCC symbol date is UNVERIFIED, but it follows from F4/F6 (the symbol carries the expiration date).

## Fit for a ~$3k account
- The fix needs no extra spend. The behaviour stays fail-safe, but the bot must see the right DTE and symbol, otherwise it sits out monthly cycles. That matters on 2026-06-18 and 2027-06-17.
- Recommended design: a hard-coded, sourced table in `config/holidays.json` (F1/F2, with source URL and as-of date). It adds no dependency, works offline, and is easy to test. Optionally cross-check it against `exchange_calendars` in a dev-only test, skipped if the package is absent.
- Code shape: `business_days(start, end, holidays)` drops the holidays. `scan_calendar` passes them. The existing `_move_back` already moves a missing Friday back to the prior trading day (≤ 4 days), so the monthly and weekly logic is right once the calendar is right. The Thursday OCC fallback (`webull_sandbox.py` L165) must call `fridays(scan_calendar…)` over a window that includes the Friday, or a new `expiry_days(exp_from, exp_to)`. Today it builds `business_days(exp, exp)` for a single Thursday, so `fridays` never sees a Friday.
- Guardrail: `scan_calendar` should fail loudly (raise) when asked for a date past the table's last year (2027-12-31), instead of silently going back to a Mon–Fri calendar. This is the same policy as the RI-002 sentinel in 005.
- Tests: 2026-12-21 → weekly 2026-12-24; 2026-05-20 → monthly 2026-06-18 (DTE 29); fallback on 2026-06-18 → Thursday symbols ≠ []; 2027-06-17 monthly; query past 2027-12-31 → error.

## Open questions
- Exact OCC/Cboe rule text for standard monthlies on a holiday (F7).
- Whether Webull's contract list returns the Thursday date (sandbox not reachable; UNVERIFIED).
- 2028 table: NYSE published it in the same release (F1 URL), but I did not record it here.
