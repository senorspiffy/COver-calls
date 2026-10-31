"""CSV loaders with strict checks. Schema: date,close[,iv][,dividend][,earnings].
An absent optional column is NaN and named in PriceSeries.missing (policy: missing.py)."""
import json
import math
from dataclasses import dataclass, replace
from pathlib import Path

import pandas as pd


class DataError(ValueError):
    pass


OPTIONAL_CSV_COLUMNS = ("iv", "dividend", "earnings")
OPTIONAL_SNAPSHOT_FIELDS = ("oi", "next_earnings", "ex_div_date", "iv")
SNAPSHOT_COLUMNS = [
    "ts", "underlying", "underlying_price", "symbol", "expiry", "strike", "type",
    "bid", "ask", "iv", "delta", "oi", "next_earnings", "ex_div_date", "asset_type",
]


@dataclass
class PriceSeries:
    df: pd.DataFrame          # index: date; columns close, dividend, earnings[, iv]
    meta: dict
    vol: pd.Series            # annualised decimal vol input, already multiplied by k
    k: float = 1.0
    missing: tuple = ()       # absent dividend/earnings columns (NaN, never 0)

    @property
    def ticker(self):
        return self.meta["ticker"]

    def scaled(self, k):
        """Same series with the vol input re-scaled to multiplier k."""
        return replace(self, vol=self.vol / self.k * k, k=k)


def load_meta(path):
    """`<file>.meta.json` sidecar; missing means user-supplied, non-synthetic stock."""
    path = Path(path)
    side = path.with_suffix(".meta.json")
    meta = {"ticker": path.stem, "source": "user-supplied", "synthetic": False,
            "asset_type": "stock", "notes": ""}
    if side.exists():
        meta.update(json.loads(side.read_text(encoding="utf-8")))
    return meta


def _fail(row, msg):
    raise DataError(f"row {row + 2}: {msg}")  # +2: header line and 1-based lines


def realized_vol(close, window):
    """Trailing annualised vol: vol[t] uses the `window` log returns ending at t
    (closes t-window..t only). NaN for t < window (warm-up). Never back- or
    forward-filled, so no value depends on a later close."""
    rets = (close / close.shift(1)).map(math.log)
    return rets.rolling(window).std() * math.sqrt(252)


def load_prices(path, k=1.0, rv_window=20):
    try:
        raw = pd.read_csv(path, dtype=str)
    except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise DataError(f"cannot read {path}: {exc}") from exc
    for col in ("date", "close"):
        if col not in raw.columns:
            raise DataError(f"{path}: missing column '{col}'")
    dates = pd.to_datetime(raw["date"], format="%Y-%m-%d", errors="coerce")
    for i in range(len(raw)):
        if pd.isna(dates[i]):
            _fail(i, f"date '{raw['date'][i]}' is not ISO YYYY-MM-DD")
        if i and dates[i] == dates[i - 1]:
            _fail(i, f"duplicate date {raw['date'][i]}")
        if i and dates[i] < dates[i - 1]:
            _fail(i, f"dates not ascending at {raw['date'][i]}")
    df = pd.DataFrame(index=pd.DatetimeIndex(dates, name="date"))
    num = lambda c: pd.to_numeric(raw[c], errors="coerce").to_numpy()  # noqa: E731
    df["close"] = num("close")
    missing = tuple(c for c in ("dividend", "earnings") if c not in raw)
    for c in ("dividend", "earnings"):
        df[c] = float("nan") if c in missing else num(c)
    if "iv" in raw:
        df["iv"] = num("iv")
    for i, (_, r) in enumerate(df.iterrows()):
        if not r["close"] > 0:
            _fail(i, f"close must be > 0 (got {raw['close'][i]})")
        if "iv" in df and not 0 < r["iv"] < 5:
            _fail(i, f"iv must be in (0, 5) (got {raw['iv'][i]})")
        if "earnings" not in missing and r["earnings"] not in (0, 1):
            _fail(i, f"earnings must be 0 or 1 (got {raw['earnings'][i]})")
        if "dividend" not in missing and not r["dividend"] >= 0:
            _fail(i, f"dividend must be >= 0 (got {raw['dividend'][i]})")
    if "earnings" not in missing:
        df["earnings"] = df["earnings"].astype(int)
    base = df["iv"] if "iv" in df else realized_vol(df["close"], rv_window)
    return PriceSeries(df=df, meta=load_meta(path), vol=base * k, k=k, missing=missing)


def load_snapshots(path):
    """Quote snapshot log (bundled sample or the bot's own log). Returns (df, meta)."""
    try:
        df = pd.read_csv(path, dtype={"symbol": str, "underlying": str})
    except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise DataError(f"cannot read {path}: {exc}") from exc
    missing = [c for c in SNAPSHOT_COLUMNS if c not in df.columns]
    if missing:
        raise DataError(f"{path}: missing columns {missing}")
    for col in ("ts", "expiry", "next_earnings", "ex_div_date"):
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    return df, load_meta(path)
