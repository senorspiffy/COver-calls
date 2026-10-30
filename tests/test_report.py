import io

import pandas as pd
import pytest

from ccbot import BANNER_MODELLED, BANNER_SYNTHETIC
from ccbot.backtest import metrics
from ccbot.report import backtest_report
from ccbot.variants import run_grid
from ccbot.walkforward import walk_forward


@pytest.fixture(scope="module")
def quick(synth_a):
    from ccbot.config import load_config
    from conftest import REPO
    cfg = load_config(REPO / "config" / "default.json")
    grid, results, bh = run_grid(synth_a, cfg, quick=True)
    wf = walk_forward(results, bh, cfg, cfg["spread"]["value"], cfg["k"])
    return backtest_report(grid, results, wf, metrics(bh, None, cfg), cfg, synth_a.meta, "2026-10-30"), grid


def test_banners_and_fixed_text(quick):
    (md, _), _ = quick
    for text in (BANNER_MODELLED, BANNER_SYNTHETIC, "No variant was selected for live use", "k UNCALIBRATED",
                 "UNVERIFIED fee values: reg_per_contract, assignment_fee", "PBO", "Configs tested: 8"):
        assert text in md


def test_rows_in_registry_order(quick):
    (md, csv), grid = quick
    table = md.split("### spread $0.05, k 1.0")[1].split("\n\n")[0]
    ids = [line.split("|")[1].strip() for line in table.splitlines()[3:]]
    assert ids == ["V0", "V1", "V2", "V3", "V4 θ50", "V4 θ66", "V4 θ80", "V5"]
    for vid in ("V0", "V1", "V2", "V3", "V4", "V5"):
        assert f"| {vid}" in md
    assert len(pd.read_csv(io.StringIO(csv))) == len(grid) == 8


def test_heldout_reported_once(quick):
    (md, _), _ = quick
    assert md.count("### Held-out years (2024, 2025), reported once") == 1


def _scan(tmp_path, cfg, date, n_prior=0, ts=None):
    import datetime as dt
    import json
    from conftest import SAMPLE
    from ccbot.bot import run_daily
    from ccbot.broker.sim import SimBroker
    from ccbot.data import load_snapshots
    df, meta = load_snapshots(SAMPLE / "SYNTH_SNAPSHOTS.csv")
    if ts:
        df = df.assign(ts=ts)
    scans = tmp_path / "state" / "scans"
    scans.mkdir(parents=True, exist_ok=True)
    seed = None
    for i in range(n_prior):
        if seed is None:
            seed = run_daily(dt.date(2026, 10, 30), SimBroker(cfg, snapshots=df.assign(ts=dt.date(2026, 10, 30)),
                             meta=meta, ledger_path=tmp_path / "seed.json"), cfg,
                             state_dir=tmp_path / "seed", reports_dir=tmp_path / "seed_r")
        d = f"2026-09-{10 + i}"
        (scans / f"{d}.json").write_text(json.dumps({**seed, "date": d}, default=str))
    broker = SimBroker(cfg, snapshots=df, meta=meta, ledger_path=tmp_path / "state" / "sim_ledger.json")
    run_daily(date, broker, cfg, state_dir=tmp_path / "state", reports_dir=tmp_path / "reports")
    return (tmp_path / "reports" / f"daily_{date}.md").read_text()


def test_daily_report_shows_pass_history(tmp_path, cfg):
    import datetime as dt
    short = _scan(tmp_path / "a", cfg, dt.date(2026, 10, 30), n_prior=2)
    assert "- SYNTH_A: passed 3 of last 3 logged scans (history short: 3 < 10)" in short
    full = _scan(tmp_path / "b", cfg, dt.date(2026, 10, 30), n_prior=9)
    assert "- SYNTH_A: passed 10 of last 10 logged scans" in full and "(history short" not in full


def test_early_close_banner_2026_12_24(tmp_path, cfg):
    import datetime as dt
    day = dt.date(2026, 12, 24)
    md = _scan(tmp_path / "a", cfg, day, ts=day)
    assert "> Early close today: 1:00 p.m. ET (1:15 p.m. for eligible options); run the scan before then." in md
    assert "Early close" not in _scan(tmp_path / "b", cfg, dt.date(2026, 10, 30))


@pytest.fixture(scope="module")
def infeasible_csv(tmp_path_factory, synth_a):
    """SYNTH_A's first 600 rows with closes x 1.5: s0 = $36, so 100 sh > cash - buffer (006)."""
    p = tmp_path_factory.mktemp("bh") / "SYNTH_A_X15.csv"
    df = synth_a.df.iloc[:600].copy()
    df["close"] = (df["close"] * 1.5).round(4)
    df.reset_index().assign(date=lambda d: d["date"].dt.strftime("%Y-%m-%d")).to_csv(p, index=False)
    return p


def test_bh_na_line_backtest(tmp_path, infeasible_csv):
    import warnings
    from ccbot.__main__ import main
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        assert main(["backtest", "--data", str(infeasible_csv), "--quick", "--asof", "2026-10-30",
                     "--out", str(tmp_path)]) == 0
    md = (tmp_path / "backtest_SYNTH_A_X15_2026-10-30.md").read_text()
    bh = md.split("## Buy and hold")[1].split("##")[0]
    assert "n/a (100 shares cost more than cash − buffer)" in bh and "%" not in bh
    grid = pd.read_csv(tmp_path / "backtest_SYNTH_A_X15_2026-10-30.csv")
    assert grid["excess_vs_bh"].isna().all()


def test_bh_na_line_weekly(cfg):
    from ccbot.report import weekly_report
    scans = [{"date": d, "context": {"ticker": "X", "price": p}, "equity": 3000.0, "synthetic": True,
              "modelled": True} for d, p in (("2026-10-26", 36.0), ("2026-10-30", 37.0))]
    trades = pd.DataFrame(columns=["status", "action", "mid", "fill", "qty", "in_band", "date", "contract"])
    md = weekly_report("2026-10-30", trades, scans, cfg)
    assert "- Buy-and-hold P/L: n/a (100 shares cost more than cash − buffer)" in md
    ok = weekly_report("2026-10-30", trades, [{**s, "context": {"ticker": "X", "price": 24.0}} for s in scans], cfg)
    assert "- Buy-and-hold P/L: $0.00 (100 sh X" in ok
