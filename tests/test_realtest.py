"""Item 061: real-quote test runs end to end on a small fake data set in DoltHub's format."""
import gzip
import math
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from ccbot import realtest as rt
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
    ed = [d for d in days if d.month in (1, 4, 7, 10) and d.day == 25]
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


def test_simulate_no_lookahead_and_accounting(data_root):
    td = rt.load_ticker(data_root, "AAA")
    assert not td.warnings
    df, trades = rt.simulate(td, rt.BOT_RULE)
    assert df.index[0] == min(td.chain)
    assert trades and all(t.close_date >= t.open_date for t in trades)
    assert all(t.open_date in td.chain for t in trades)            # sold only on quote days
    # no call is held through an earnings date under the bot rule
    assert not any(rt._earnings_between(td, t.open_date, t.expiration) for t in trades)
    # truncating the future must not change the past
    cut = df.index[len(df) // 2]
    df2, _ = rt.simulate(td, rt.BOT_RULE, end=cut)
    assert np.allclose(df2.cc.values, df.cc.loc[:cut].values)
    assert df.bh.iloc[0] == pytest.approx(1.0)


def test_bid_fills_cost_more_than_mid(data_root):
    td = rt.load_ticker(data_root, "BBB")
    bid = rt.simulate(td, rt.Config(fill="bid"))[0].cc.iloc[-1]
    mid = rt.simulate(td, rt.Config(fill="mid"))[0].cc.iloc[-1]
    assert bid < mid


def test_run_end_to_end(data_root, tmp_path):
    grid = [rt.Config(d, w, True, m) for d in (0.2, 0.275) for w in ((30, 45),) for m in ("hold", "take50")]
    s = rt.run(data_root, tmp_path, ["AAA", "BBB", "CCC", "SPY"], grid=grid, mc_paths=200, min_years=1)
    assert s["tickers"] == ["AAA", "BBB", "CCC"]  # SPY is the benchmark, not pooled
    for f in ("bot_rule_by_ticker.csv", "grid_in_sample.csv", "walkforward_by_ticker.csv", "walkforward_picks.csv", "summary.json"):
        assert (tmp_path / f).exists()
    picks = pd.read_csv(tmp_path / "walkforward_picks.csv")
    assert (pd.to_datetime(picks.test_from) > pd.to_datetime(picks.train_from)).all()
    assert "bxm_cagr" in s["bxm_vs_spy"]
    br = pd.read_csv(tmp_path / "bot_rule_by_ticker.csv")
    assert ((br.called_away_pct >= 0) & (br.called_away_pct <= 1)).all()
    # IV in the fake data is 1.15x true vol, so sold IV should beat realized on average
    assert (br[br.config.str.endswith("bid")].iv_minus_rv > 0).mean() >= 2 / 3


def test_pick_uses_the_bots_pickers():
    """A1 061: first monthly expiry in 30-45 DTE (not the one nearest 37.5), delta band [0.20, 0.35]."""
    today = date(2024, 1, 2)
    e1, e2 = date(2024, 2, 16), date(2024, 3, 15)          # 45 and 73 DTE, both third Fridays
    wk = date(2024, 2, 9)                                   # weekly at 38 DTE: not a monthly
    g = pd.DataFrame({"expiration": [e1, e1, e1, wk, e2], "strike": [11.0, 12.0, 13.0, 12.0, 12.0],
                      "bid": [0.5, 0.3, 0.1, 0.3, 0.6], "ask": [0.55, 0.35, 0.15, 0.35, 0.65],
                      "iv": 0.3, "delta": [0.45, 0.31, 0.12, 0.28, 0.4]})
    r = rt._pick(g, 10.5, today, rt.BOT_RULE)
    assert (r.expiration, r.strike) == (e1, 12.0)
    g.loc[1, "delta"] = 0.36                                 # nearest delta now outside [0.20, 0.35]
    assert rt._pick(g, 10.5, today, rt.BOT_RULE) is None
