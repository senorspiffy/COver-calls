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


def _passing_b(df):
    """SYNTH_B's rows at $14 with a $0.05 spread, so only the earnings test can reject it."""
    b = df[df["underlying"] == "SYNTH_B"].copy()
    b["ask"] = (b["bid"] + 0.05).round(2)
    return b


def test_blank_oi_is_rejected_oi_unknown(cfg):
    df, _ = _snaps()
    a = df[df["underlying"] == "SYNTH_A"].copy()
    assert feasible_universe(cfg, a, 3000, DATE)[0] == ["SYNTH_A"]
    a["oi"] = float("nan")
    assert feasible_universe(cfg, a, 3000, DATE)[1]["SYNTH_A"] == "OI_UNKNOWN"


def test_blank_earnings_stock_rejected_earnings_unknown(cfg):
    df, _ = _snaps()
    b = _passing_b(df)
    assert feasible_universe(cfg, b, 3000, DATE)[0] == ["SYNTH_B"]     # control: passes with a date
    b["next_earnings"] = None
    assert feasible_universe(cfg, b, 3000, DATE)[1]["SYNTH_B"] == "EARNINGS_UNKNOWN"


def test_scan_outside_holiday_table_changes_nothing(tmp_path, cfg):
    """007: past the holiday table the scan refuses before the ledger or any log is written."""
    import pytest
    with pytest.raises(ValueError, match="holiday table covers"):
        _run(tmp_path, cfg, date=dt.date(2028, 10, 2))
    assert not (tmp_path / "state").exists()


def test_pass_history_counts_last_10(tmp_path, cfg):
    """003: the pass count is information only. It never blocks an order."""
    from ccbot.screen import pass_history
    scans = [{"passing": ["SYNTH_A"]}] * 2 + [{"passing": ["SYNTH_A"] if i % 3 == 0 else []} for i in range(10)]
    assert len(scans) == 12 and pass_history(scans, "SYNTH_A") == (4, 10)
    assert pass_history(scans[:3], "SYNTH_A") == (3, 3) and pass_history(scans[:3], "SYNTH_B") == (0, 3)
    real, _ = _run(tmp_path / "seed", cfg)
    scans_dir = tmp_path / "state" / "scans"
    scans_dir.mkdir(parents=True)
    for i in range(10):     # 10 earlier logged scans in which nothing passed
        d = f"2026-10-{10 + i}"
        (scans_dir / f"{d}.json").write_text(json.dumps({**real, "date": d, "passing": []}, default=str))
    scan, _ = _run(tmp_path, cfg)
    assert [d["action"] for d in scan["decisions"]] == ["BUY_SHARES", "SELL_CALL"]
    assert scan["pass_history"] == {"SYNTH_A": [1, 10], "SYNTH_B": [0, 10], "SYNTH_C": [0, 10]}
