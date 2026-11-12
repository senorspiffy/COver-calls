"""Item 058: staggered expiries (monthly_dte_by_ticker) and the dip reserve (dip_entry)."""
import datetime as dt

import pandas as pd
import pytest

from conftest import REPO, SAMPLE
from ccbot.bot import run_daily
from ccbot.broker.sim import SimBroker
from ccbot.config import ConfigError, for_ticker, load_config
from ccbot.data import SNAPSHOT_COLUMNS, load_snapshots
from ccbot.screen import feasible_universe

DATE = dt.date(2026, 10, 30)
SEVEN = ["F", "VALE", "AAL", "T", "PFE", "HBAN", "CMCSA"]


def _run(tmp_path, cfg):
    df, meta = load_snapshots(SAMPLE / "SYNTH_SNAPSHOTS.csv")
    broker = SimBroker(cfg, snapshots=df, meta=meta, ledger_path=tmp_path / "state" / "sim_ledger.json")
    scan = run_daily(DATE, broker, cfg, state_dir=tmp_path / "state", reports_dir=tmp_path / "reports")
    return scan, broker


def _history(tmp_path, closes):
    """Write prior underlying rows for SYNTH_A, one per business day before DATE."""
    days = pd.bdate_range(end=DATE - dt.timedelta(days=1), periods=len(closes))
    rows = [dict.fromkeys(SNAPSHOT_COLUMNS) | {"ts": d.date().isoformat(), "underlying": "SYNTH_A",
                                                "underlying_price": c, "asset_type": "etf"}
            for d, c in zip(days, closes)]
    (tmp_path / "state").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=SNAPSHOT_COLUMNS).to_csv(tmp_path / "state" / "paper_snapshots.csv", index=False)


def test_for_ticker_uses_its_own_window(cfg):
    c = load_config(None, {"monthly_dte_by_ticker": {"VALE": [60, 75]}})
    assert for_ticker(c, "VALE")["monthly_dte"] == [60, 75]
    assert for_ticker(c, "F") is c and c["monthly_dte"] == [30, 45]


def test_bad_windows_and_dip_rules_are_refused():
    with pytest.raises(ConfigError):
        load_config(None, {"monthly_dte_by_ticker": {"VALE": [75, 60]}})
    with pytest.raises(ConfigError):
        load_config(None, {"dip_entry": {"drop": 1.5, "lookback": 20, "min_days": 5}})
    with pytest.raises(ConfigError):
        load_config(None, {"dip_entry": {"drop": 0.05, "lookback": 3, "min_days": 5}})


def test_screen_checks_the_tickers_own_window(cfg):
    df, _ = load_snapshots(SAMPLE / "SYNTH_SNAPSHOTS.csv")
    assert "SYNTH_A" in feasible_universe(cfg, df, cfg["cash"], DATE)[0]
    late = {**cfg, "monthly_dte_by_ticker": {"SYNTH_A": [200, 230]}}   # no such expiry in the sample
    assert feasible_universe(late, df, cfg["cash"], DATE)[1]["SYNTH_A"] == "NO_EXPIRY"


def test_no_dip_rule_until_enough_history(tmp_path, cfg):
    c = {**cfg, "dip_entry": {"drop": 0.05, "lookback": 20, "min_days": 5}}
    scan, broker = _run(tmp_path, c)
    a = [d for d in scan["decisions"] if d["ticker"] == "SYNTH_A"]
    assert [d["reason"] for d in a] == ["NO_DIP"] and broker.n_orders == 0
    trades = pd.read_csv(tmp_path / "state" / "paper_trades.csv")
    assert "1 of 5 closes recorded" in trades.loc[trades["ticker"] == "SYNTH_A", "detail"].iloc[0]


def test_no_entry_without_a_5pct_dip(tmp_path, cfg):
    _history(tmp_path, [24.5, 24.6, 24.4, 24.3, 24.2])   # high 24.6; 24.10 is only 2% below
    scan, broker = _run(tmp_path, {**cfg, "dip_entry": {"drop": 0.05, "lookback": 20, "min_days": 5}})
    assert [d["reason"] for d in scan["decisions"] if d["ticker"] == "SYNTH_A"] == ["NO_DIP"]
    assert broker.n_orders == 0


def test_dip_opens_the_position(tmp_path, cfg):
    _history(tmp_path, [26.0, 25.8, 25.5, 25.0, 24.8])   # high 26.00; 24.10 is 7.3% below
    scan, broker = _run(tmp_path, {**cfg, "dip_entry": {"drop": 0.05, "lookback": 20, "min_days": 5}})
    acts = [d["action"] for d in scan["decisions"] if d["ticker"] == "SYNTH_A"]
    assert "SELL_CALL" in acts and broker.n_orders > 0


def test_lookback_drops_old_highs(tmp_path, cfg):
    _history(tmp_path, [30.0] + [24.3] * 5)   # the 30.00 high is outside a 5-scan lookback
    scan, _ = _run(tmp_path, {**cfg, "dip_entry": {"drop": 0.05, "lookback": 5, "min_days": 5}})
    assert [d["reason"] for d in scan["decisions"] if d["ticker"] == "SYNTH_A"] == ["NO_DIP"]


def test_budget_accounts_match_the_057_versions():
    st = load_config(REPO / "config" / "stagger.json")
    base = load_config(REPO / "config" / "dip_base.json")
    res = load_config(REPO / "config" / "dip_reserve.json")
    for c in (st, base, res):
        assert c["universe"] == SEVEN and c["broker"] == "webull-paper"
    assert st["cash"] == 20000 and st["max_positions"] == 7
    assert {t: for_ticker(st, t)["monthly_dte"] for t in SEVEN} == {
        "F": [30, 45], "AAL": [30, 45], "PFE": [30, 45], "CMCSA": [30, 45],
        "VALE": [60, 75], "T": [60, 75], "HBAN": [60, 75]}
    assert base["cash"] + res["cash"] == 20000 and base["dip_entry"] is None
    assert res["max_positions"] == 1 and res["dip_entry"] == {"drop": 0.05, "lookback": 20, "min_days": 5}
