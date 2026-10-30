import datetime as dt
import filecmp
import math
import random

import pandas as pd
import pytest

from conftest import SAMPLE
from ccbot.data import DataError, load_prices, realized_vol
from ccbot.synth import write_samples

GOOD = "date,close,iv,dividend,earnings\n2026-01-05,10,0.3,0,0\n2026-01-06,11,0.3,0,0\n"


@pytest.mark.parametrize("body,match", [
    ("date,close\n2026-01-06,10\n2026-01-05,11\n", "not ascending"),
    ("date,close\n2026-01-05,10\n2026-01-05,11\n", "duplicate"),
    ("date,close\n2026-01-05,-1\n", "close must be > 0"),
    ("date,close,iv\n2026-01-05,10,7\n", "iv must be in"),
    ("date,close,earnings\n2026-01-05,10,2\n", "earnings must be 0 or 1"),
    ("date,close\n01/05/2026,10\n", "not ISO"),
])
def test_bad_files_raise(tmp_path, body, match):
    p = tmp_path / "bad.csv"
    p.write_text(body)
    with pytest.raises(DataError, match=match):
        load_prices(p)


def test_realized_vol_of_constant_return_is_zero(tmp_path):
    p = tmp_path / "c.csv"
    p.write_text("date,close\n" + "".join(f"2026-01-{d:02d},{10 * 1.01 ** d:.10f}\n" for d in range(1, 31)))
    s = load_prices(p)
    assert s.vol.abs().max() < 1e-9
    rv = realized_vol(s.df["close"], 5)
    assert rv.iloc[:5].isna().all() and rv.iloc[5:].notna().all()   # warm-up stays NaN, never backfilled


def test_realized_vol_uses_only_past_closes(tmp_path, cfg):
    """Regression guardrail (002, I3 FAIL): with no iv column, the vol used on day t
    must depend only on closes up to and including t. Rewriting every close after t
    must leave vol[0..t] unchanged, for every t."""
    rng = random.Random(7)
    dates = [dt.date(2026, 1, 1) + dt.timedelta(days=i) for i in range(60)]
    closes = [20.0]
    for i in range(59):
        closes.append(closes[-1] * math.exp(rng.gauss(0, 0.06 if i < 20 else 0.005)))  # volatile, then calm

    def load(cs):
        p = tmp_path / "noiv.csv"
        p.write_text("date,close\n" + "".join(f"{d},{c:.6f}\n" for d, c in zip(dates, cs)))
        return load_prices(p, k=1.2, rv_window=cfg["rv_window"]).vol.to_numpy()

    base = load(closes)
    assert "iv" not in pd.read_csv(tmp_path / "noiv.csv").columns
    assert all(math.isnan(v) for v in base[:cfg["rv_window"]])
    for t in range(len(closes) - 1):
        changed = closes[:t + 1] + [c * rng.uniform(0.5, 2.0) for c in closes[t + 1:]]
        vol = load(changed)
        j = max(t + 1, cfg["rv_window"])
        assert vol[j] != base[j]                     # the edit does reach the later vols
        for i in range(t + 1):
            assert (math.isnan(base[i]) and math.isnan(vol[i])) or base[i] == vol[i], (t, i)


def test_meta_flags(tmp_path, synth_a):
    assert synth_a.meta["synthetic"] is True and synth_a.meta["asset_type"] == "etf"
    p = tmp_path / "x.csv"
    p.write_text(GOOD)
    meta = load_prices(p).meta
    assert meta["synthetic"] is False and meta["asset_type"] == "stock" and meta["source"] == "user-supplied"


def test_k_scales_vol_input(synth_a):
    assert (synth_a.scaled(1.2).vol / synth_a.vol).round(12).eq(1.2).all()


def test_samples_byte_identical(tmp_path):
    names = write_samples(tmp_path / "a")
    write_samples(tmp_path / "b")
    match, mismatch, errors = filecmp.cmpfiles(tmp_path / "a", tmp_path / "b", names, shallow=False)
    assert match == names and not mismatch and not errors
    _, mismatch, _ = filecmp.cmpfiles(tmp_path / "a", SAMPLE, names, shallow=False)
    assert not mismatch, "checked-in sample differs from the generator"


def test_synth_a_shape(synth_a):
    df = synth_a.df
    assert len(df) == 2520 and df["close"].iloc[0] == 24.0
    assert df["earnings"].sum() == 0 and (df["dividend"] > 0).sum() >= 36
