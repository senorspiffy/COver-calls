import datetime as dt

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
