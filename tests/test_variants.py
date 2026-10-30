import datetime as dt
from dataclasses import replace

import pandas as pd

from helpers import write_path
from ccbot.backtest import run_backtest
from conftest import head
from ccbot.rules import REASONS
from ccbot.variants import BY_ID, REGISTRY, run_grid


def _n(res, action):
    return int((res.trades["action"] == action).sum()) if len(res.trades) else 0


def test_registry_ids():
    assert [v.id for v in REGISTRY] == ["V0", "V1", "V2", "V3", "V4", "V5"]


def test_v3_never_enters_on_falling_series(tmp_path, cfg):
    s = write_path(tmp_path / "fall.csv", [30 - 0.05 * i for i in range(120)], start=dt.date(2026, 1, 5))
    assert _n(run_backtest(s, BY_ID["V3"], cfg), "SELL_CALL") == 0
    assert _n(run_backtest(s, BY_ID["V0"], cfg), "SELL_CALL") > 0


def test_v4_theta_zero_equals_v0(synth_a, cfg, runs):
    v4 = run_backtest(synth_a, replace(BY_ID["V4"], iv_theta=0), cfg)
    assert v4.trades.equals(runs["V0"].trades)


def test_fill_counts(runs, cfg):
    r = runs
    v0 = r["V0"].metrics["fills"]
    # No ratio band is fitted to the observed 1.9x (05 deviation 4). 03's "~4x" assumed a
    # weekly sale every week, but the shared rules block V2 more often than V0: weekly
    # 5-9 DTE has no expiry on Mon/Tue, and at 5-9 DTE delta jumps past the [0.20, 0.35]
    # tolerance between $1 strikes, which gives NO_STRIKE_IN_TOLERANCE and BASIS_ABOVE_BAND.
    # So the test checks what follows from the rules: more fills than monthly V0; at most one
    # sale per weekly expiry; every sale on Wed-Fri at 5-9 DTE. The upper 5x is the plan's.
    v2 = r["V2"].trades[r["V2"].trades["action"] == "SELL_CALL"]
    dte = (pd.to_datetime(v2["expiry"]) - pd.to_datetime(v2["date"])).dt.days
    assert v0 < r["V2"].metrics["fills"] < 5 * v0
    assert v2["expiry"].is_unique and dte.between(*cfg["weekly_dte"]).all()
    assert pd.to_datetime(v2["date"]).dt.weekday.isin([2, 3, 4]).all()
    assert r["V1"].metrics["fills"] >= v0
    assert _n(r["V5"], "SELL_PUT") >= 1


def test_run_grid_rows_in_registry_order(synth_a, cfg):
    grid, results, _ = run_grid(head(synth_a, 300), cfg)
    assert len(grid) == (5 + 3) * 4 * 3 == 96 == len(results)
    per_setting = grid[(grid["spread"] == 0.05) & (grid["k"] == 1.0)]["config"].tolist()
    assert per_setting == ["V0", "V1", "V2", "V3", "V4 θ50", "V4 θ66", "V4 θ80", "V5"]


def test_every_reason_code_is_produced(runs):
    seen = set().union(*(r.reasons for r in runs.values()))
    seen |= set().union(*(set(r.trades["action"]) for r in runs.values()))
    assert "BUY_TO_CLOSE" in set(runs["V1"].trades["action"])   # PROFIT_TARGET_HIT exits
    # OK = every fill; EARNINGS_BLACKOUT, VOL_WARMUP: test_backtest; UNIVERSE_EMPTY: test_screen_bot
    assert set(REASONS) - seen == {"OK", "EARNINGS_BLACKOUT", "UNIVERSE_EMPTY", "PROFIT_TARGET_HIT", "VOL_WARMUP"}
