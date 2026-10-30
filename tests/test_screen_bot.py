import datetime as dt
import json

import pandas as pd

from conftest import REPO, SAMPLE
from ccbot.bot import run_daily
from ccbot.broker.sim import SimBroker
from ccbot.config import DEFAULTS, load_config
from ccbot.data import load_snapshots
from ccbot.screen import feasible_universe, universe_banner

DATE = dt.date(2026, 10, 30)   # a Friday


def _snaps():
    return load_snapshots(SAMPLE / "SYNTH_SNAPSHOTS.csv")


def test_screen_on_sample(cfg):
    df, _ = _snaps()
    passing, rejects = feasible_universe(cfg, df, cfg["cash"], DATE)
    assert passing == ["SYNTH_A"]
    assert rejects == {"SYNTH_B": "SPREAD", "SYNTH_C": "PRICE_CAP"}
    assert universe_banner(passing, rejects) is None


def test_shipped_config_has_a_passing_ticker():
    """001 guardrail: a universe rule must have at least one passing ticker on the sample."""
    shipped = load_config(REPO / "config" / "default.json")
    assert shipped == load_config(None) and json.loads((REPO / "config" / "default.json").read_text()) == DEFAULTS
    df, _ = _snaps()
    assert feasible_universe(shipped, df, shipped["cash"], DATE)[0]


def test_single_name_cap_and_earnings(cfg):
    df, _ = _snaps()
    b = df[df["underlying"] == "SYNTH_B"].copy()
    b["underlying_price"] = 20.0
    assert feasible_universe(cfg, b, 3000, DATE)[1]["SYNTH_B"] == "SINGLE_NAME_CAP"
    a = df[df["underlying"] == "SYNTH_A"].copy()
    a["next_earnings"] = dt.date(2026, 12, 1)
    assert feasible_universe(cfg, a, 3000, DATE)[1]["SYNTH_A"] == "EARNINGS"


def _run(tmp_path, cfg, date=DATE, **kw):
    df, meta = _snaps()
    broker = SimBroker(cfg, snapshots=df, meta=meta, ledger_path=tmp_path / "state" / "sim_ledger.json")
    scan = run_daily(date, broker, cfg, state_dir=tmp_path / "state", reports_dir=tmp_path / "reports", **kw)
    return scan, broker


def test_universe_empty_blocks_orders(tmp_path):
    cfg = load_config(None, {"cash": 2000, "screen": {"max_spread": 0.01}})
    scan, broker = _run(tmp_path, cfg)
    report = (tmp_path / "reports" / f"daily_{DATE}.md").read_text()
    assert "UNIVERSE EMPTY: rule PRICE_CAP has no passing ticker" in report
    trades = pd.read_csv(tmp_path / "state" / "paper_trades.csv")
    assert list(trades["reason"]) == ["UNIVERSE_EMPTY"] and broker.n_orders == 0


def test_scan_sells_call_and_is_idempotent(tmp_path, cfg):
    scan, _ = _run(tmp_path, cfg)
    sell = [d for d in scan["decisions"] if d["action"] == "SELL_CALL"][0]
    assert sell["contract"].startswith("SYNTH_A261218C") and sell["tif"] == "DAY" and sell["in_window"] is False
    n = len(pd.read_csv(tmp_path / "state" / "paper_trades.csv"))
    again, broker = _run(tmp_path, cfg)
    assert again["skipped"] and len(pd.read_csv(tmp_path / "state" / "paper_trades.csv")) == n
    assert broker.n_orders == 0
    assert len(pd.read_csv(tmp_path / "state" / "paper_snapshots.csv")) > 0


def test_weekly_report_only_on_friday(tmp_path, cfg):
    _run(tmp_path, cfg)
    assert (tmp_path / "reports" / f"weekly_{DATE}.md").exists()
    t = tmp_path / "thu"
    df, meta = _snaps()
    thursday = dt.date(2026, 10, 29)
    df = pd.concat([df, df.assign(ts=thursday)])
    for weekly, expect in ((False, False), (True, True)):
        d = t / str(weekly)
        broker = SimBroker(cfg, snapshots=df, meta=meta, ledger_path=d / "state" / "l.json")
        run_daily(thursday, broker, cfg, weekly=weekly, state_dir=d / "state", reports_dir=d / "reports")
        assert (d / "reports" / f"weekly_{thursday}.md").exists() is expect
