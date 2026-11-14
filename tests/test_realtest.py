"""Item 061: real-quote test runs end to end on a small fake data set in DoltHub's format."""
import dataclasses
import gzip
import inspect
import math
import re
import shutil
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ccbot import costs, expiries, realtest as rt
from ccbot.pricing import bs_price, bs_delta


def _fridays(d0, d1):
    d = d0 + timedelta(days=(4 - d0.weekday()) % 7)
    while d <= d1:
        yield d
        d += timedelta(days=7)


def _make(root, tk, seed, years=3.2, vol=0.30, drift=0.05, div=0.25):
    rng = np.random.default_rng(seed)
    d0 = date(2019, 1, 2)
    days = [d0 + timedelta(days=i) for i in range(int(365 * years)) if (d0 + timedelta(days=i)).weekday() < 5]
    rets = rng.normal(drift / 252, vol / math.sqrt(252), len(days))
    close = 20 * np.exp(np.cumsum(rets))
    (root / "prices").mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"date": days, "act_symbol": tk, "close": close.round(2)}).to_csv(root / "prices" / f"{tk}.csv", index=False)
    exd = [d for d in days if d.month in (2, 5, 8, 11) and d.day in (10, 11, 12) and d.weekday() < 5][::1]
    exd = sorted({(d.year, d.month): d for d in exd}.values())
    (root / "dividends").mkdir(exist_ok=True)
    pd.DataFrame({"ex_date": exd, "act_symbol": tk, "amount": div}).to_csv(root / "dividends" / f"{tk}.csv", index=False)
    (root / "splits").mkdir(exist_ok=True)
    pd.DataFrame(columns=["ex_date", "act_symbol", "to_factor", "for_factor"]).to_csv(root / "splits" / f"{tk}.csv", index=False)
    (root / "earnings").mkdir(exist_ok=True)
    ed = sorted({(d.year, d.month): d for d in reversed(days) if d.month in (1, 4, 7, 10) and d.day >= 25}.values())
    pd.DataFrame({"act_symbol": tk, "date": ed, "when": "Before market open"}).to_csv(root / "earnings" / f"{tk}.csv", index=False)
    px = dict(zip(days, close))
    rows, vh = [], []
    snaps = [d for d in days if d.weekday() in (0, 2, 4)]
    fr = list(_fridays(days[0], days[-1] + timedelta(days=90)))
    for d in snaps:
        S = px[d]
        iv = vol * 1.15
        vh.append({"date": d, "act_symbol": tk, "iv_current": iv, "hv_current": vol})
        for e in fr:
            dte = (e - d).days
            if not 5 <= dte <= 80 or not (dte <= 10 or e.day >= 15 and e.day <= 21):
                continue
            for k in np.arange(round(S * 0.8 * 2) / 2, S * 1.3, 0.5):
                T = dte / 365
                m = bs_price(S, k, T, 0.03, 0, iv, "C")
                sp = max(0.02, 0.05 * m)
                rows.append({"date": d, "act_symbol": tk, "expiration": e, "strike": round(float(k), 2),
                             "call_put": "Call", "bid": round(max(m - sp / 2, 0), 2), "ask": round(m + sp / 2, 2),
                             "vol": iv, "delta": bs_delta(S, k, T, 0.03, 0, iv, "C")})
    (root / "options").mkdir(exist_ok=True)
    with gzip.open(root / "options" / f"{tk}.csv.gz", "wt") as f:
        pd.DataFrame(rows).to_csv(f, index=False)
    (root / "volhist").mkdir(exist_ok=True)
    pd.DataFrame(vh).to_csv(root / "volhist" / f"{tk}.csv", index=False)
    return days


@pytest.fixture(scope="module")
def data_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("real")
    days = None
    for i, tk in enumerate(["AAA", "BBB", "CCC", "SPY"]):
        days = _make(root, tk, seed=i)
    lines = ["Cboe BXM history", "DATE,BXM"] + [f"{d.month:02d}/{d.day:02d}/{d.year},{100 * 1.0002 ** i:.2f}" for i, d in enumerate(days)]
    (root / "BXM_History.csv").write_text("\n".join(lines))
    return root


CFG = rt.DEFAULT_CFG
FACTS = {tk: {"asset_type": "stock"} for tk in ("AAA", "BBB", "CCC")}
DATA = Path(__file__).resolve().parents[1] / "data" / "real"


def test_simulate_no_lookahead_and_accounting(data_root):
    td = rt.load_ticker(data_root, "AAA", FACTS)
    assert not td.warnings
    df, trades = rt.simulate(td, rt.BOT_RULE, CFG)
    assert df.index[0] == min(td.chain)
    assert trades and all(t.close_date >= t.open_date for t in trades)
    assert all(t.open_date in td.chain for t in trades)            # sold only on quote days
    # no call is held through an earnings date under the bot rule
    assert not any(rt._earnings_between(td, t.open_date, t.expiration) for t in trades)
    assert all(math.isfinite(t.close_cost) for t in trades)
    # truncating the future must not change the past
    cut = df.index[len(df) // 2]
    df2, _ = rt.simulate(td, rt.BOT_RULE, CFG, end=cut)
    assert np.allclose(df2.cc.values, df.cc.loc[:cut].values)
    assert df.bh.iloc[0] == pytest.approx(1.0)


def test_bid_fills_cost_more_than_mid(data_root):
    td = rt.load_ticker(data_root, "BBB", FACTS)
    bid = rt.simulate(td, dataclasses.replace(rt.BOT_RULE, fill="bid"), CFG)[0].cc.iloc[-1]
    mid = rt.simulate(td, dataclasses.replace(rt.BOT_RULE, fill="mid"), CFG)[0].cc.iloc[-1]
    assert bid < mid


def test_run_end_to_end(data_root, tmp_path):
    grid = [rt.Config(d, w, True, m) for d in (0.2, 0.275) for w in ((30, 45),) for m in ("hold", "take50")]
    s = rt.run(data_root, tmp_path, ["AAA", "BBB", "CCC", "SPY"], CFG, grid=grid, mc_paths=200, min_years=1,
               facts=FACTS)
    assert s["tickers"] == ["AAA", "BBB", "CCC"]  # SPY is the benchmark, not pooled
    for f in ("bot_rule_by_ticker.csv", "grid_in_sample.csv", "walkforward_by_ticker.csv", "walkforward_picks.csv", "summary.json"):
        assert (tmp_path / f).exists()
    picks = pd.read_csv(tmp_path / "walkforward_picks.csv")
    assert (pd.to_datetime(picks.test_from) > pd.to_datetime(picks.train_from)).all()
    assert "bxm_cagr" in s["bxm_vs_spy"]
    assert s["monte_carlo_2_stocks_1yr"]["paths_used"] == 200
    assert set(s["counts_bot_rule_bid"]) == {"AAA", "BBB", "CCC"}
    assert s["counts_bot_rule_bid"]["AAA"]["rej_OK"] > 0
    br = pd.read_csv(tmp_path / "bot_rule_by_ticker.csv")
    assert ((br.called_away_pct >= 0) & (br.called_away_pct <= 1)).all()
    # IV in the fake data is 1.15x true vol, so sold IV should beat realized on average
    assert (br[br.config.str.endswith("bid")].iv_minus_rv > 0).mean() >= 2 / 3


# ---------------------------------------------------------------- the bot's entry rule (061/04 changes 1.1-1.6)

def _cal(a, b, holidays=()):
    return expiries.business_days(a, b, holidays)


def test_pick_uses_the_bots_pickers():
    """A1 061: first monthly expiry in 30-45 DTE (not the one nearest 37.5), delta band [0.20, 0.35]."""
    today = date(2024, 1, 2)
    e1, e2 = date(2024, 2, 16), date(2024, 3, 15)          # 45 and 73 DTE, both third Fridays
    wk = date(2024, 2, 9)                                   # weekly at 38 DTE: not a monthly
    g = pd.DataFrame({"expiration": [e1, e1, e1, wk, e2], "strike": [11.0, 12.0, 13.0, 12.0, 12.0],
                      "bid": [0.5, 0.3, 0.1, 0.3, 0.6], "ask": [0.55, 0.35, 0.15, 0.35, 0.65],
                      "iv": 0.3, "delta": [0.45, 0.31, 0.12, 0.28, 0.4]})
    monthly = expiries.third_fridays(_cal(date(2024, 1, 1), date(2024, 4, 30)))
    r, code = rt._pick(g, today, rt.BOT_RULE, CFG, monthly, 0.0)
    assert code == "OK" and (r.expiration, r.strike, r.in_window) == (e1, 12.0, True)
    g.loc[1, "delta"] = 0.36                                 # nearest delta now outside [0.20, 0.35]
    assert rt._pick(g, today, rt.BOT_RULE, CFG, monthly, 0.0) == (None, "NO_STRIKE_IN_TOLERANCE")


def _old_is_monthly(e):
    """The deleted realtest._is_monthly, kept here to show what it missed."""
    return 15 <= e.day <= 21 and e.weekday() == 4 or 16 <= e.day <= 22 and e.weekday() == 3 \
        and (e + timedelta(days=1)).day <= 21


def test_pick_thursday_monthly_2022_04_14():
    """Good Friday 2022-04-15: the April monthly expired Thursday 04-14 (061/04 extra research 1)."""
    today, thu, may = date(2022, 3, 14), date(2022, 4, 14), date(2022, 5, 20)
    monthly = expiries.third_fridays(_cal(date(2022, 3, 1), date(2022, 6, 30), [date(2022, 4, 15)]))
    assert thu in monthly
    g = pd.DataFrame({"expiration": [thu, thu, may], "strike": [10.0, 11.0, 11.0], "bid": [0.6, 0.3, 0.5],
                      "ask": [0.65, 0.35, 0.55], "iv": 0.3, "delta": [0.5, 0.28, 0.35]})
    r, code = rt._pick(g, today, rt.BOT_RULE, CFG, monthly, 0.0)
    assert code == "OK" and r.expiration == thu and (thu - today).days == 31
    # the old home-made test rejected it, and nothing else was in reach
    assert not _old_is_monthly(thu)
    old = sorted(e for e in g.expiration.unique() if _old_is_monthly(e))
    assert expiries.pick_expiry(today, old, (30, 45), 7) is None


def test_pick_unquoted_bot_expiry_is_no_expiry():
    today = date(2024, 1, 2)
    monthly = expiries.third_fridays(_cal(date(2024, 1, 1), date(2024, 4, 30)))   # 02-16 is the bot's pick
    g = pd.DataFrame({"expiration": [date(2024, 2, 9), date(2024, 3, 15)], "strike": [11.0, 11.0],
                      "bid": [0.3, 0.5], "ask": [0.35, 0.55], "iv": 0.3, "delta": [0.28, 0.3]})
    assert rt._pick(g, today, rt.BOT_RULE, CFG, monthly, 0.0) == (None, "NO_EXPIRY")


@pytest.mark.parametrize("case,basis,want", [
    ("below", 11.5, (12.0, "OK")),              # nearest-delta strike 11 < basis -> first strike >= basis
    ("above_band_fail", 12.5, (None, "BASIS_ABOVE_BAND")),   # 13 has delta 0.12 < 0.20
    ("at_or_above", 11.0, (11.0, "OK")),        # strike == basis: unchanged
])
def test_basis_floor(case, basis, want):
    today, e = date(2024, 1, 2), date(2024, 2, 16)
    monthly = expiries.third_fridays(_cal(date(2024, 1, 1), date(2024, 4, 30)))
    g = pd.DataFrame({"expiration": e, "strike": [10.0, 11.0, 12.0, 13.0], "bid": [0.6, 0.3, 0.15, 0.05],
                      "ask": [0.65, 0.35, 0.2, 0.1], "iv": 0.3, "delta": [0.45, 0.28, 0.21, 0.12]})
    r, code = rt._pick(g, today, rt.BOT_RULE, CFG, monthly, basis)
    assert ((None if r is None else r.strike), code) == want


def _tiny(earnings=(), asset_type="stock", chain_days=(date(2024, 1, 2),), quotes_at=None, close=10.5):
    """A hand-made ticker: flat close, one 2024-02-16 expiry (45 DTE from 01-02), strikes 10-13.
    quotes_at: {date: (bid, ask)} for the 11 strike on later days (take50 tests)."""
    days = _cal(date(2024, 1, 2), date(2024, 3, 29))
    e = date(2024, 2, 16)
    base = pd.DataFrame({"expiration": e, "strike": [10.0, 11.0, 12.0, 13.0], "bid": [0.6, 0.3, 0.15, 0.05],
                         "ask": [0.65, 0.35, 0.2, 0.1], "iv": 0.3, "delta": [0.45, 0.28, 0.21, 0.12]})
    chain, quotes = {}, {}
    for d in chain_days:
        g = base.copy()
        if quotes_at and d in quotes_at:
            g.loc[g.strike == 11.0, ["bid", "ask"]] = quotes_at[d]
        chain[d] = g
        for k, b, a, v, dl in zip(g.strike, g.bid, g.ask, g.iv, g.delta):
            quotes[(d, e, round(k, 3))] = (b, a, v, dl)
    return rt.TickerData("TINY", pd.Series(close, index=days), {}, {}, sorted(earnings), chain, pd.DataFrame(),
                         asset_type=asset_type, volhist_na="volhist: not supplied", quote_rows_dropped=0,
                         earnings_gaps=0, quotes=quotes)


def test_earnings_today_blocks():
    df, tr = rt.simulate(_tiny(earnings=[date(2024, 1, 2)]), rt.BOT_RULE, CFG)
    assert tr == [] and df.attrs["counts"]["rej_EARNINGS_BLACKOUT"] == 1     # a <= e, like screen._reject
    df, tr = rt.simulate(_tiny(earnings=[date(2024, 6, 1)]), rt.BOT_RULE, CFG)
    assert len(tr) == 1 and tr[0].strike == 11.0                               # control: no earnings in the life


def test_stock_without_earnings_sells_nothing():
    df, tr = rt.simulate(_tiny(earnings=[]), rt.BOT_RULE, CFG)
    assert tr == [] and df.attrs["counts"]["rej_EARNINGS_UNKNOWN"] == 1 and df.attrs["counts"]["rej_OK"] == 0
    df, tr = rt.simulate(_tiny(earnings=[date(2023, 10, 1)]), rt.BOT_RULE, CFG)   # only a past date
    assert tr == [] and df.attrs["counts"]["rej_EARNINGS_UNKNOWN"] == 1


def test_etf_without_earnings_sells():
    asset, warn = rt._asset_type("SPY", {})
    assert (asset, warn) == ("etf", None)
    df, tr = rt.simulate(_tiny(earnings=[], asset_type=asset), rt.BOT_RULE, CFG)
    assert len(tr) == 1 and df.attrs["counts"]["rej_EARNINGS_UNKNOWN"] == 0


@pytest.mark.parametrize("day,outcome", [(date(2024, 1, 8), "bought_back"),   # 6 days of 45: first third
                                         (date(2024, 2, 1), "expired")])      # 30 days of 45: hold
def test_take50_only_in_first_third(day, outcome):
    td = _tiny(earnings=[date(2024, 6, 1)], chain_days=(date(2024, 1, 2), day), quotes_at={day: (0.10, 0.14)})
    df, tr = rt.simulate(td, dataclasses.replace(rt.BOT_RULE, manage="take50"), CFG)
    assert tr[0].premium == 0.3 and tr[0].outcome == outcome
    if outcome == "bought_back":
        assert tr[0].close_date == day and tr[0].close_cost == 0.14


@pytest.mark.parametrize("px", [0.01, 0.30, 2.50])
def test_fees_match_costs_fees(px):
    assert rt.opt_fees(px, 100, True, CFG) == costs.fees("sell", px, 1, CFG)["total"]
    assert rt.opt_fees(px, 250, False, CFG) == pytest.approx(costs.fees("buy", px, 2.5, CFG)["total"])


def test_sales_under_3_cents_are_counted_not_blocked():
    td = _tiny(earnings=[date(2024, 6, 1)])
    td.chain[date(2024, 1, 2)].loc[1, ["bid", "ask"]] = (0.02, 0.04)
    df, tr = rt.simulate(td, rt.BOT_RULE, CFG)
    assert len(tr) == 1 and tr[0].premium == 0.02 and df.attrs["counts"]["sub_3c_sales"] == 1


# ---------------------------------------------------------------- missing data (061/04 change 1.8, RI-002)

DROP_CASES = ["prices", "options", "dividends", "splits", "earnings", "volhist", "BXM_History.csv", "asset_type"]


def _copy(data_root, dst, tk="AAA"):
    for kind, ext in (("prices", ".csv"), ("dividends", ".csv"), ("splits", ".csv"), ("earnings", ".csv"),
                      ("options", ".csv.gz"), ("volhist", ".csv")):
        (dst / kind).mkdir(parents=True, exist_ok=True)
        shutil.copy(data_root / kind / f"{tk}{ext}", dst / kind / f"{tk}{ext}")
    shutil.copy(data_root / "BXM_History.csv", dst / "BXM_History.csv")
    for kind, ext in (("prices", ".csv"), ("dividends", ".csv"), ("splits", ".csv"), ("options", ".csv.gz")):
        shutil.copy(data_root / kind / f"SPY{ext}", dst / kind / f"SPY{ext}")
    return dst


@pytest.mark.parametrize("kind", DROP_CASES)
def test_drop_input(kind, data_root, tmp_path):
    root = _copy(data_root, tmp_path)
    reason = rt.REALTEST_MISSING[kind]
    if kind in ("prices", "options", "dividends", "splits"):
        ext = ".csv.gz" if kind == "options" else ".csv"
        (root / kind / f"AAA{ext}").unlink()
        with pytest.raises(FileNotFoundError) as e:
            rt.load_ticker(root, "AAA", FACTS)
        assert str(e.value) == reason.removeprefix("ticker skipped: ")
        s = rt.run(root, tmp_path / "out", ["AAA", "SPY"], CFG, grid=[rt.BOT_RULE], mc_paths=10, min_years=1,
                   facts=FACTS)
        assert s["skipped"] == {"AAA": reason.removeprefix("ticker skipped: ")} and s["tickers"] == ["SPY"]
    elif kind == "earnings":
        (root / "earnings" / "AAA.csv").unlink()
        td = rt.load_ticker(root, "AAA", FACTS)
        assert td.earnings == [] and "earnings: not supplied" in "; ".join(td.warnings)
        df, tr = rt.simulate(td, rt.BOT_RULE, CFG)
        assert tr == [] and df.attrs["counts"]["rej_EARNINGS_UNKNOWN"] > 0 and df.attrs["counts"]["rej_OK"] == 0
    elif kind == "volhist":
        (root / "volhist" / "AAA.csv").unlink()
        td = rt.load_ticker(root, "AAA", FACTS)
        df, tr = rt.simulate(td, rt.BOT_RULE, CFG)
        s = rt.summarize(td, rt.BOT_RULE, df, tr, CFG)
        assert math.isnan(s["atm_iv_minus_next30d_rv"]) and math.isnan(s["atm_pct_iv_above_rv"])
        assert s["atm_na_reason"] == "volhist: not supplied" and s["atm_na_reason"] in reason
    elif kind == "BXM_History.csv":
        (root / "BXM_History.csv").unlink()
        b = rt.bxm_vs_spy(root, date(2019, 1, 1), date(2023, 1, 1), FACTS)
        assert b == {"error": "BXM_History.csv: not supplied"} and b["error"] in reason
    elif kind == "asset_type":
        td = rt.load_ticker(root, "AAA", {})
        assert td.asset_type == "stock" and any(w.startswith("asset_type: ") for w in td.warnings)


def test_realtest_missing_lists_every_input():
    src = inspect.getsource(rt.load_ticker) + inspect.getsource(rt.bxm_vs_spy)
    files = set(re.findall(r'root\)? / "([^"]+)"', src))
    assert files == {"prices", "dividends", "splits", "earnings", "options", "volhist", "BXM_History.csv"}
    assert files | {"asset_type"} == set(rt.REALTEST_MISSING) == set(DROP_CASES)


def test_nan_iv_rows_dropped_and_counted(data_root, tmp_path):
    root = _copy(data_root, tmp_path)
    oc = pd.read_csv(root / "options" / "AAA.csv.gz")
    oc.loc[0, "vol"], oc.loc[1, "vol"], oc.loc[2, "delta"] = float("nan"), 0.0, float("nan")
    with gzip.open(root / "options" / "AAA.csv.gz", "wt") as f:
        oc.to_csv(f, index=False)
    td = rt.load_ticker(root, "AAA", FACTS)
    assert td.quote_rows_dropped == 3
    assert any(w.startswith("options: 3 quote rows dropped") for w in td.warnings)
    assert all(np.isfinite(g.iv).all() and (g.iv > 0).all() and np.isfinite(g.delta).all() for g in td.chain.values())


def test_nan_dividend_amount_skips(data_root, tmp_path):
    root = _copy(data_root, tmp_path)
    dv = pd.read_csv(root / "dividends" / "AAA.csv")
    dv.loc[1, "amount"] = float("nan")
    dv.to_csv(root / "dividends" / "AAA.csv", index=False)
    with pytest.raises(ValueError, match="DIVIDEND_UNKNOWN"):
        rt.load_ticker(root, "AAA", FACTS)


def _returns(n=800):
    idx = pd.RangeIndex(n)
    return pd.DataFrame({"A": 0.0, "B": 0.0}, index=idx), pd.DataFrame({"A": 0.02, "B": 0.02}, index=idx)


def test_monte_carlo_no_fill():
    cc, bh = _returns()
    bh.loc[100:299, "A"] = float("nan")          # filling these with 0 would pull bh returns down
    mc = rt.monte_carlo(cc, bh, n_paths=50)
    assert mc["paths_used"] == 50
    want = 1.02 ** 252 - 1
    assert all(v == pytest.approx(want) for v in mc["bh_ret"].values())
    assert all(v == pytest.approx(0.0) for v in mc["cc_ret"].values())


def test_monte_carlo_too_few_names_na():
    cc, bh = _returns()
    mc = rt.monte_carlo(cc[["A"]], bh[["A"]], n_paths=10)
    assert set(mc) == {"na"} and "need 2" in mc["na"]


def test_walk_forward_empty_training_block_not_picked():
    def curve(a, b):
        idx = [d.date() for d in pd.date_range(a, b)]
        return pd.DataFrame({"cc": np.linspace(1, 1.1, len(idx)), "bh": np.linspace(1, 1.2, len(idx))}, index=idx)
    cfgs = [rt.Config(0.15, (30, 45)), rt.Config(0.45, (30, 45))]
    per = {"A": curve("2020-01-01", "2020-03-01"), "B": curve("2022-06-01", "2023-06-01")}
    oos, bh, picks = rt.walk_forward({c.name: per for c in cfgs}, cfgs)
    assert picks[0]["picked"] is None and picks[0]["reason"] == "no training data"
    assert math.isnan(picks[0]["train_excess_logret"])
    assert any(p["picked"] for p in picks)                       # later blocks have training data
    first_test = min(date.fromisoformat(p["test_from"]) for p in picks if p["picked"])
    assert oos.index.min() >= first_test                          # nothing from an unpicked block


def test_walk_forward_block_keeps_first_day():
    idx = [d.date() for d in pd.date_range("2020-01-01", "2023-01-01")]
    df = pd.DataFrame({"cc": np.linspace(1, 2, len(idx)), "bh": np.linspace(1, 2, len(idx))}, index=idx)
    c = rt.Config(0.15, (30, 45))
    oos, bh, picks = rt.walk_forward({c.name: {"A": df}}, [c])
    assert date.fromisoformat(picks[0]["test_from"]) in oos.index


def test_premium_yield_na_zero_years():
    td = _tiny(earnings=[date(2024, 6, 1)])
    df, tr = rt.simulate(td, rt.BOT_RULE, CFG, end=date(2024, 1, 2))
    s = rt.summarize(td, rt.BOT_RULE, df, tr, CFG)
    assert s["years"] == 0 and math.isnan(s["premium_yield_per_yr"])


# ---------------------------------------------------------------- feasibility on committed data (061/04 guardrail tests)
# Measured by I2 on 2026-11-14 from data/real (fetched 2026-11-13), period from 2020-01-01.

REAL_BAC = {   # 0.15/14-24 and the +/-0.075 tolerance are grid-only variants, not bot rules
    rt.BOT_RULE: dict(calls_sold=24, rej_OK=24, rej_NO_EXPIRY=369, rej_EARNINGS_UNKNOWN=20,
                      rej_EARNINGS_BLACKOUT=104, rej_NO_STRIKE_IN_TOLERANCE=11, rej_BASIS_ABOVE_BAND=296,
                      open_at_end=0, in_window=11, slack=13, sub_3c_sales=1, snap_days=1271, snap_days_no_close=55),
    rt.Config(0.15, (14, 24)): dict(calls_sold=70, rej_OK=70, rej_NO_EXPIRY=0, rej_EARNINGS_UNKNOWN=20,
                                    rej_EARNINGS_BLACKOUT=52, rej_NO_STRIKE_IN_TOLERANCE=4, rej_BASIS_ABOVE_BAND=529,
                                    open_at_end=0, in_window=61, slack=9, sub_3c_sales=7, snap_days=1271,
                                    snap_days_no_close=55),
    rt.Config(0.45, (30, 45)): dict(calls_sold=19, rej_OK=19, rej_NO_EXPIRY=397, rej_EARNINGS_UNKNOWN=20,
                                    rej_EARNINGS_BLACKOUT=57, rej_NO_STRIKE_IN_TOLERANCE=37, rej_BASIS_ABOVE_BAND=367,
                                    open_at_end=0, in_window=10, slack=9, sub_3c_sales=0, snap_days=1271,
                                    snap_days_no_close=55),
}
INFO = {"open_at_end", "sub_3c_sales", "snap_days_no_close"}


@pytest.fixture(scope="module")
def bac():
    return rt.load_ticker(DATA, "BAC")


@pytest.mark.parametrize("rule", list(REAL_BAC), ids=lambda r: r.name)
def test_real_counts_bac(bac, rule):
    df, tr = rt.simulate(bac, rule, CFG, start=date(2020, 1, 1))
    got = dict(calls_sold=len(tr), **df.attrs["counts"])
    assert got == REAL_BAC[rule]
    assert df.index[0] == date(2020, 1, 6)                       # start 2020-01-01 -> first snapshot used
    assert bac.asset_type == "stock" and bac.quote_rows_dropped == 10
    if rule == rt.BOT_RULE:                                      # every window rule has candidates (RI-001)
        assert all(v > 0 for k, v in got.items() if k not in INFO)


def test_real_min_years_filter():
    tks = sorted(p.name.split(".")[0] for p in (DATA / "options").glob("*.csv.gz"))
    skipped = set()
    for tk in tks:
        try:
            rt.eligible(rt.load_ticker(DATA, tk), date(2020, 1, 1), 3.0)
        except (FileNotFoundError, ValueError, KeyError):
            skipped.add(tk)
    assert len(tks) == 22 and skipped == {"ITUB", "KGC", "PBR", "VALE"}
