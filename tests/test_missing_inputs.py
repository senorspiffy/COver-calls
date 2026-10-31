"""RI-002 guardrail (005/006): drop each optional input in MISSING_POLICY and check that the run
gives the named reason or n/a, with no exception and no invented number."""
import datetime as dt
import shutil
import warnings

import pandas as pd
import pytest

from conftest import SAMPLE
from ccbot.__main__ import main
from ccbot.backtest import bh_na_reason, buy_and_hold, run_backtest
from ccbot.bot import run_daily
from ccbot.broker.sim import SimBroker
from ccbot.data import OPTIONAL_CSV_COLUMNS, OPTIONAL_SNAPSHOT_FIELDS, load_prices, load_snapshots
from ccbot.missing import MISSING_POLICY
from ccbot.screen import feasible_universe
from ccbot.variants import BY_ID

DATE = dt.date(2026, 10, 30)
ROWS = 300


def _csv_without(tmp_path, ticker, col):
    """First ROWS rows of a sample CSV with `col` dropped (meta sidecar kept)."""
    p = tmp_path / f"{ticker}.csv"
    pd.read_csv(SAMPLE / f"{ticker}.csv", dtype=str).head(ROWS).drop(columns=col).to_csv(p, index=False)
    shutil.copy(SAMPLE / f"{ticker}.meta.json", tmp_path / f"{ticker}.meta.json")
    return p


def _backtest_md(tmp_path, path):
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        assert main(["backtest", "--data", str(path), "--quick", "--asof", "2026-10-30", "--out", str(tmp_path)]) == 0
    return (tmp_path / f"backtest_{path.stem}_2026-10-30.md").read_text(encoding="utf-8")


def _scan(tmp_path, cfg, df, meta):
    broker = SimBroker(cfg, snapshots=df, meta=meta, ledger_path=tmp_path / "state" / "sim_ledger.json")
    scan = run_daily(DATE, broker, cfg, state_dir=tmp_path / "state", reports_dir=tmp_path / "reports")
    return scan, (tmp_path / "reports" / f"daily_{DATE}.md").read_text(encoding="utf-8")


def _no_option_sold(res):
    return not res.trades["action"].isin(["SELL_CALL", "SELL_PUT"]).any()


def drop_csv_earnings(tmp_path, cfg):
    p = _csv_without(tmp_path, "SYNTH_B", "earnings")          # a stock
    s = load_prices(p)
    res = run_backtest(s, BY_ID["V0"], cfg)
    assert res.reasons["EARNINGS_UNKNOWN"] > 0 and _no_option_sold(res)
    md = _backtest_md(tmp_path, p)
    assert f"- earnings: not supplied ({res.reasons['EARNINGS_UNKNOWN']} days blocked, EARNINGS_UNKNOWN)" in md


def drop_csv_dividend(tmp_path, cfg):
    p = _csv_without(tmp_path, "SYNTH_A", "dividend")          # an ETF that pays dividends
    s = load_prices(p)
    res = run_backtest(s, BY_ID["V0"], cfg)
    assert res.reasons["DIVIDEND_UNKNOWN"] > 0 and _no_option_sold(res)
    assert bh_na_reason(s, cfg) == "dividend: not supplied" and buy_and_hold(s, cfg).isna().all()
    md = _backtest_md(tmp_path, p)
    assert "- dividend: not supplied (" in md and "n/a (dividend: not supplied)" in md


def drop_csv_iv(tmp_path, cfg):
    p = _csv_without(tmp_path, "SYNTH_A", "iv")
    s = load_prices(p, rv_window=cfg["rv_window"])
    assert s.vol.iloc[:cfg["rv_window"]].isna().all()           # realised vol, warm-up stays NaN
    assert run_backtest(s, BY_ID["V0"], cfg).reasons["VOL_WARMUP"] > 0
    assert "else trailing realised vol" in _backtest_md(tmp_path, p)


def drop_snapshot_oi(tmp_path, cfg):
    df, meta = load_snapshots(SAMPLE / "SYNTH_SNAPSHOTS.csv")
    df["oi"] = float("nan")
    assert feasible_universe(cfg, df, cfg["cash"], DATE)[1]["SYNTH_A"] == "OI_UNKNOWN"
    scan, _ = _scan(tmp_path, cfg, df, meta)
    assert [d["reason"] for d in scan["decisions"]] == ["UNIVERSE_EMPTY"]


def drop_snapshot_next_earnings(tmp_path, cfg):
    df, meta = load_snapshots(SAMPLE / "SYNTH_SNAPSHOTS.csv")
    df["ask"] = (df["bid"] + 0.05).round(2)                     # so SYNTH_B (a stock) reaches the test
    df["next_earnings"] = None
    assert feasible_universe(cfg, df, cfg["cash"], DATE)[1]["SYNTH_B"] == "EARNINGS_UNKNOWN"
    broker = SimBroker(cfg, snapshots=df, meta=meta, ledger_path=tmp_path / "l.json")
    broker.advance(DATE)
    assert broker.get_underlying_quote("SYNTH_B").earnings_known is False
    assert broker.get_underlying_quote("SYNTH_A").earnings_known is True    # an ETF: known none


def drop_snapshot_ex_div_date(tmp_path, cfg):
    df, meta = load_snapshots(SAMPLE / "SYNTH_SNAPSHOTS.csv")
    df["ex_div_date"] = None
    scan, md = _scan(tmp_path, cfg, df, meta)
    assert "days to ex-dividend: n/a (not supplied)" in md
    assert "SELL_CALL" in [d["action"] for d in scan["decisions"]]   # not a decision input today


def drop_snapshot_iv(tmp_path, cfg):
    df, meta = load_snapshots(SAMPLE / "SYNTH_SNAPSHOTS.csv")
    df["iv"] = float("nan")
    scan, md = _scan(tmp_path, cfg, df, meta)
    assert "SELL_CALL" in [d["action"] for d in scan["decisions"]]   # quotes carry their own delta
    assert scan["equity"] != scan["equity"] and "equity n/a" in md     # NaN, shown as n/a


def drop_bh_benchmark(tmp_path, cfg):
    p = tmp_path / "X.csv"
    df = pd.read_csv(SAMPLE / "SYNTH_A.csv").head(ROWS)
    df["close"] = df["close"] * 1.5
    df.to_csv(p, index=False)
    s = load_prices(p)
    assert bh_na_reason(s, cfg) == MISSING_POLICY["bh_benchmark"][1] and buy_and_hold(s, cfg).isna().all()
    assert f"n/a ({MISSING_POLICY['bh_benchmark'][1]})" in _backtest_md(tmp_path, p)


def drop_broker_div_next(tmp_path, cfg):
    # Known gap, pinned so that a fix has to update the policy: broker Days carry div_next 0.0.
    df, meta = load_snapshots(SAMPLE / "SYNTH_SNAPSHOTS.csv")
    broker = SimBroker(cfg, snapshots=df, meta=meta, ledger_path=tmp_path / "l.json")
    broker.advance(DATE)
    assert broker.get_underlying_quote("SYNTH_A").div_next == 0.0
    assert MISSING_POLICY["broker.div_next"][0] == "known_gap"


DROPS = {"csv.earnings": drop_csv_earnings, "csv.dividend": drop_csv_dividend, "csv.iv": drop_csv_iv,
         "snapshot.oi": drop_snapshot_oi, "snapshot.next_earnings": drop_snapshot_next_earnings,
         "snapshot.ex_div_date": drop_snapshot_ex_div_date, "snapshot.iv": drop_snapshot_iv,
         "bh_benchmark": drop_bh_benchmark, "broker.div_next": drop_broker_div_next}


@pytest.mark.parametrize("key", list(MISSING_POLICY))
def test_drop_each_input(tmp_path, cfg, key):
    assert key in DROPS, f"MISSING_POLICY[{key!r}] has no drop test"
    DROPS[key](tmp_path, cfg)


def test_policy_lists_every_optional_input():
    keys = {f"csv.{c}" for c in OPTIONAL_CSV_COLUMNS} | {f"snapshot.{c}" for c in OPTIONAL_SNAPSHOT_FIELDS}
    assert keys <= set(MISSING_POLICY)
    assert set(DROPS) == set(MISSING_POLICY)
