"""SYNTHETIC sample data (stdlib random, so files are byte-identical across numpy versions)."""
import datetime as dt
import json
import math
import random
from pathlib import Path

from . import costs
from .broker.base import occ_symbol
from .data import SNAPSHOT_COLUMNS
from .pricing import bs_delta, bs_price, strike_grid

SOURCE = "synthetic, seed 42"


def _bdays(start, n):
    d, out = start, []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def _third_friday(d):
    first = d.replace(day=1)
    return first + dt.timedelta(days=(4 - first.weekday()) % 7 + 14)


def make_series(seed, start, n_days, s0, drift, vols, p_switch, iv_mult, div, earnings_every):
    """2-regime Markov-switching GBM. Rows: (date, close, iv, dividend, earnings).
    Dividends fall on the 3rd Friday of Mar/Jun/Sep/Dec; earnings every N rows."""
    rng, dt_y = random.Random(seed), 1 / 252
    regime, s, rows = 0, s0, []
    for i, d in enumerate(_bdays(start, n_days)):
        if i:
            if rng.random() < p_switch:
                regime = 1 - regime
            sig = vols[regime]
            s *= math.exp((drift - 0.5 * sig * sig) * dt_y + sig * math.sqrt(dt_y) * rng.gauss(0, 1))
        dividend = div if div and d.month % 3 == 0 and d == _third_friday(d) else 0.0
        earnings = 1 if earnings_every and i % earnings_every == earnings_every - 23 else 0
        rows.append((d, round(s, 4), round(vols[regime] * iv_mult, 4), dividend, earnings))
    return rows


def _write_csv(path, rows):
    lines = ["date,close,iv,dividend,earnings"]
    lines += [f"{d.isoformat()},{c:.4f},{iv:.4f},{dv:.2f},{e}" for d, c, iv, dv, e in rows]
    path.write_text("\n".join(lines) + "\n")


def _write_meta(path, ticker, asset_type, notes):
    meta = {"ticker": ticker, "source": SOURCE, "synthetic": True, "asset_type": asset_type, "notes": notes}
    path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")


# One scan date, one monthly expiry (49 DTE: the 30-45 window has no monthly on 2026-10-30).
SNAP_TS, SNAP_EXPIRY, SNAP_R = dt.date(2026, 10, 30), dt.date(2026, 12, 18), 0.04
SNAP_UNDERLYINGS = [
    # ticker, price, iv, spread, oi, asset_type, next_earnings, ex_div_date
    ("SYNTH_A", 24.10, 0.275, 0.03, 900, "etf", "", "2026-12-18"),
    ("SYNTH_B", 14.00, 0.40, 0.12, 900, "stock", "2027-01-28", ""),
    ("SYNTH_C", 31.00, 0.25, 0.03, 900, "etf", "", ""),
]


def snapshot_rows():
    T = (SNAP_EXPIRY - SNAP_TS).days / 365
    rows = []
    for t, s, iv, spread, oi, asset, earn, exdiv in SNAP_UNDERLYINGS:
        for kind in ("C", "P"):
            for k in strike_grid(s):
                mid = bs_price(s, k, T, SNAP_R, 0.0, iv, kind)
                bid = costs.round_tick(mid - spread / 2)
                ask = round(bid + spread, 2)
                delta = bs_delta(s, k, T, SNAP_R, 0.0, iv, kind)
                rows.append(f"{SNAP_TS},{t},{s:.2f},{occ_symbol(t, SNAP_EXPIRY, kind, k)},{SNAP_EXPIRY},"
                            f"{k:.2f},{kind},{bid:.2f},{ask:.2f},{iv:.4f},{delta:.4f},{oi},{earn},{exdiv},{asset}")
    return rows


def write_samples(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    a = make_series(42, dt.date(2016, 1, 4), 2520, 24.0, 0.07, (0.25, 0.45), 0.02, 1.1, 0.10, 0)
    _write_csv(out / "SYNTH_A.csv", a)
    _write_meta(out / "SYNTH_A.meta.json", "SYNTH_A", "etf",
                "GBM, 2-regime vol 25%/45%, drift 7%/yr, iv = regime vol x 1.1, $0.10 quarterly dividend")
    b = make_series(42, dt.date(2025, 1, 2), 252, 14.0, 0.07, (0.35, 0.60), 0.02, 1.1, 0.0, 63)
    _write_csv(out / "SYNTH_B.csv", b)
    _write_meta(out / "SYNTH_B.meta.json", "SYNTH_B", "stock",
                "GBM, 2-regime vol 35%/60%, earnings flag every 63 rows, no dividend")
    (out / "SYNTH_SNAPSHOTS.csv").write_text("\n".join([",".join(SNAPSHOT_COLUMNS)] + snapshot_rows()) + "\n")
    _write_meta(out / "SYNTH_SNAPSHOTS.meta.json", "SYNTH_SNAPSHOTS", "etf",
                "BS quotes +/- a fixed spread; SYNTH_A passes, SYNTH_B fails SPREAD, SYNTH_C fails PRICE_CAP")
    return sorted(p.name for p in out.iterdir())
