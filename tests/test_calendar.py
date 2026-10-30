import datetime as dt

import pytest

from ccbot.backtest import ModelMarket
from ccbot.expiries import business_days, fridays, pick_expiry, scan_calendar, third_fridays

D = dt.date


def test_known_third_fridays():
    tf = third_fridays(business_days(D(2026, 1, 1), D(2026, 12, 31)))
    assert D(2026, 11, 20) in tf and D(2026, 12, 18) in tf and len(tf) == 12


def test_missing_friday_moves_back():
    days = [d for d in business_days(D(2026, 11, 1), D(2026, 11, 30)) if d != D(2026, 11, 20)]
    assert third_fridays(days) == [D(2026, 11, 19)]
    assert D(2026, 11, 19) in fridays(days)


def test_monthly_coverage_on_synth_a(synth_a, cfg):
    # Monthlies are 28 or 35 days apart, so a 15-day window often has none (strict) and
    # even 30-45 +/- 7 misses ~3 days before a 5-week gap; those days give NO_EXPIRY.
    dates = [d.date() for d in synth_a.df.index]
    m = ModelMarket("SYNTH_A", dates, cfg)
    slack = sum(bool(m.pick(d, "monthly", cfg["monthly_dte"], cfg["monthly_slack_days"])) for d in dates)
    strict = sum(bool(m.pick(d, "monthly", cfg["monthly_dte"], 0)) for d in dates)
    assert slack / len(dates) > 0.94 and strict / len(dates) < 0.7


def test_weekly_5_to_9_dte():
    days = business_days(D(2026, 1, 1), D(2026, 12, 31))
    fr = fridays(days)
    for d in days[:-10]:
        pick = pick_expiry(d, fr, (5, 9))
        if d.weekday() in (2, 3, 4):     # Wed, Thu, Fri: next week's Friday is 9, 8, 7 DTE
            assert pick and 5 <= (pick[0] - d).days <= 9 and pick[1]
        else:                            # Mon, Tue: 4 / 3 or 11 / 10 DTE, none in 5-9
            assert pick is None


def test_live_scan_rule_2026_10_30(cfg):
    today = D(2026, 10, 30)
    pick = pick_expiry(today, third_fridays(scan_calendar(today)), cfg["monthly_dte"], cfg["monthly_slack_days"])
    assert pick == (D(2026, 12, 18), False)
    assert pick_expiry(today, third_fridays(scan_calendar(today)), cfg["monthly_dte"], 0) is None


def test_monthly_coverage_2016_2025(cfg):
    """RI-001 guardrail (004): pins the coverage numbers 001 step 4 cites (Mon-Fri, no holidays)."""
    cal = business_days(D(2016, 1, 1), D(2026, 3, 31))
    tf = third_fridays(cal)
    days = [d for d in cal if d <= D(2025, 12, 31)]
    strict = [pick_expiry(d, tf, cfg["monthly_dte"], 0) is not None for d in days]
    slack = [pick_expiry(d, tf, cfg["monthly_dte"], cfg["monthly_slack_days"]) is not None for d in days]
    run = longest = 0
    for ok in slack:
        run = 0 if ok else run + 1
        longest = max(longest, run)
    assert (len(days), sum(strict), sum(slack)) == (2609, 1440, 2483)
    assert longest <= 3


HOLIDAYS = {D(2026, 1, 1), D(2026, 1, 19), D(2026, 2, 16), D(2026, 4, 3), D(2026, 5, 25), D(2026, 6, 19),
            D(2026, 7, 3), D(2026, 9, 7), D(2026, 11, 26), D(2026, 12, 25),
            D(2027, 1, 1), D(2027, 1, 18), D(2027, 2, 15), D(2027, 3, 26), D(2027, 5, 31), D(2027, 6, 18),
            D(2027, 7, 5), D(2027, 9, 6), D(2027, 11, 25), D(2027, 12, 24),
            D(2028, 1, 17), D(2028, 2, 21), D(2028, 4, 14), D(2028, 5, 29), D(2028, 6, 19), D(2028, 7, 4),
            D(2028, 9, 4), D(2028, 11, 23), D(2028, 12, 25)}
EARLY = {D(2026, 11, 27), D(2026, 12, 24), D(2027, 11, 26), D(2028, 7, 3), D(2028, 11, 24)}


def _table():
    from ccbot.expiries import load_holidays
    t = load_holidays()
    return t, {D.fromisoformat(x) for x in t["holidays"]}, {D.fromisoformat(x) for x in t["early_closes"]}


def test_holiday_table_matches_nyse():
    """RI-003 guardrail (007): the exact NYSE 2026-2028 closures and early closes."""
    t, hol, early = _table()
    assert hol == HOLIDAYS and len(t["holidays"]) == 29
    assert early == EARLY and not early & hol
    assert t["covers"] == ["2026-01-01", "2028-12-31"] and "nyse.com" in t["source"]


@pytest.mark.parametrize("today", [D(2028, 10, 1), D(2025, 12, 15)])
def test_scan_calendar_raises_outside_table(today):
    with pytest.raises(ValueError, match=r"holiday table covers 2026-01-01\.\.2028-12-31.*nyse\.com"):
        scan_calendar(today)


def test_monthly_moves_to_thursday():
    tf = third_fridays(scan_calendar(D(2026, 5, 20)))
    assert D(2026, 6, 18) in tf and D(2026, 6, 19) not in tf
    assert pick_expiry(D(2026, 5, 20), tf, (30, 45), 7) == (D(2026, 6, 18), False)
    assert D(2027, 6, 17) in third_fridays(scan_calendar(D(2027, 5, 20)))


def test_weekly_moves_to_thursday():
    for d in (D(2026, 12, 16), D(2026, 12, 17), D(2026, 12, 18)):
        assert pick_expiry(d, fridays(scan_calendar(d)), (5, 9)) == (D(2026, 12, 24), True)
    assert pick_expiry(D(2026, 12, 23), fridays(scan_calendar(D(2026, 12, 23))), (5, 9)) == (D(2026, 12, 31), True)
    assert pick_expiry(D(2026, 12, 21), fridays(scan_calendar(D(2026, 12, 21))), (5, 9)) is None


def test_table_matches_exchange_calendars():
    """Dev-only cross-check; skips when exchange_calendars is not installed (not a dependency)."""
    xc = pytest.importorskip("exchange_calendars")
    cal = xc.get_calendar("XNYS", start="2025-01-01", end="2029-01-31")
    sessions = {s.date() for s in cal.sessions}
    weekdays = business_days(D(2026, 1, 1), D(2028, 12, 31))
    assert {d for d in weekdays if d not in sessions} == HOLIDAYS
    assert {e.date() for e in cal.early_closes if D(2026, 1, 1) <= e.date() <= D(2028, 12, 31)} == EARLY
