"""CLI: python -m ccbot make-sample | backtest | scan | report. Exit codes: 0 ok, 2 bad input, 3 live refused."""
import argparse
import datetime as dt
import sys
import time
from pathlib import Path

from .broker.base import LiveTradingDisabled
from .config import ConfigError, load_config
from .data import DataError

DEFAULT_CONFIG = "config/default.json"


def _date(s):
    try:
        return dt.date.fromisoformat(s)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not a YYYY-MM-DD date: {s}") from exc


def parser():
    p = argparse.ArgumentParser(prog="ccbot", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("make-sample", help="regenerate the SYNTHETIC sample data")
    s.add_argument("--out", default="data/sample")
    b = sub.add_parser("backtest", help="run every pre-registered variant and write a report")
    b.add_argument("--data", default="data/sample/SYNTH_A.csv")
    b.add_argument("--config", default=DEFAULT_CONFIG)
    b.add_argument("--asof", type=_date, default=dt.date.today())
    b.add_argument("--quick", action="store_true", help="base spread and k only")
    b.add_argument("--out", default="reports")
    for name in ("scan", "report"):
        c = sub.add_parser(name, help="daily paper scan" if name == "scan" else "rebuild reports from state/")
        c.add_argument("--date", type=_date, required=True)
        c.add_argument("--config", default=DEFAULT_CONFIG)
        c.add_argument("--weekly", action="store_true")
        c.add_argument("--state-dir", default="state")
        c.add_argument("--out", default="reports")
        if name == "scan":
            c.add_argument("--broker", choices=["sim", "webull-sandbox"], default="sim")
            c.add_argument("--snapshots", default="data/sample/SYNTH_SNAPSHOTS.csv")
            c.add_argument("--variant", default="V0", choices=["V0", "V1", "V2", "V3", "V4", "V5"])
            c.add_argument("--live", action="store_true", help="refused: live trading is not built")
    return p


def cmd_make_sample(a):
    from .synth import write_samples
    for name in write_samples(a.out):
        print(Path(a.out) / name)


def cmd_backtest(a):
    from .backtest import bh_na_reason, metrics
    from .data import load_prices
    from .report import backtest_report
    from .variants import run_grid
    from .walkforward import walk_forward

    cfg = load_config(a.config)
    series = load_prices(a.data, k=cfg["k"], rv_window=cfg["rv_window"])
    t0 = time.time()
    grid, results, bh = run_grid(series, cfg, quick=a.quick)
    wf = walk_forward(results, bh, cfg, cfg["spread"]["value"], cfg["k"])
    bh_m = metrics(bh, None, cfg)
    bh_m["na_reason"] = bh_na_reason(series, cfg)
    md, csv = backtest_report(grid, results, wf, bh_m, cfg, series.meta, a.asof, series.missing)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = out / f"backtest_{series.ticker}_{a.asof.isoformat()}"
    stem.with_suffix(".md").write_text(md, encoding="utf-8")
    stem.with_suffix(".csv").write_text(csv, encoding="utf-8")
    print(f"{len(grid)} configs in {time.time() - t0:.1f} s -> {stem}.md, {stem}.csv")


def cmd_scan(a):
    from .bot import run_daily
    from .broker import make_broker
    from .data import load_snapshots

    if a.live:
        raise LiveTradingDisabled("Live trading is not built.")
    cfg = load_config(a.config)
    ledger = Path(a.state_dir) / "sim_ledger.json"
    if a.broker == "sim":
        snaps, meta = load_snapshots(a.snapshots)
        broker = make_broker("sim", cfg, snapshots=snaps, meta=meta, ledger_path=ledger)
    else:
        broker = make_broker("webull-sandbox", cfg, ledger_path=ledger,
                             token_dir=Path(a.state_dir) / "webull_token")
    scan = run_daily(a.date, broker, cfg, a.variant, a.weekly, a.state_dir, a.out)
    if scan["skipped"]:
        print(f"already scanned {scan['date']} for {scan['variant']}: no new orders; reports re-rendered")
    for d in scan["decisions"]:
        print(f"{scan['date']} {scan['variant']} {d['action']} {d['reason']} {d['contract'] or ''} "
              f"limit={d['limit']} status={d['status']}")
    if scan["banner"]:
        print(scan["banner"])
    print(f"reports in {a.out}/ (daily_{scan['date']}.md)")


def cmd_report(a):
    from .bot import regenerate
    for p in regenerate(a.date, a.state_dir, a.out, load_config(a.config), a.weekly):
        print(p)


def main(argv=None):
    a = parser().parse_args(argv)
    try:
        {"make-sample": cmd_make_sample, "backtest": cmd_backtest, "scan": cmd_scan,
         "report": cmd_report}[a.cmd](a)
    except LiveTradingDisabled as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 3
    except (ConfigError, DataError, ValueError, FileNotFoundError, ImportError, LookupError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
