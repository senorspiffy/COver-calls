"""Hand-built price paths for tests."""
import datetime as dt

from ccbot.data import load_prices


def bdays(start, n):
    d, out = start, []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def write_path(path, closes, start=dt.date(2026, 10, 19), iv=0.25, dividends=None, earnings=None):
    """CSV with a fixed iv column; dividends/earnings: {date: value}."""
    dividends, earnings = dividends or {}, earnings or {}
    lines = ["date,close,iv,dividend,earnings"]
    for d, c in zip(bdays(start, len(closes)), closes):
        lines.append(f"{d},{c},{iv},{dividends.get(d, 0)},{earnings.get(d, 0)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return load_prices(path)
