"""Download free historical data for the real-quote covered-call test (item 061).

Sources (all free, no login, no API key):
  * DoltHub post-no-preference/options  - option_chain (bid/ask/IV/delta per strike) and
    volatility_history (IV and historical vol per day)
  * DoltHub post-no-preference/stocks   - ohlcv (unadjusted daily prices), dividend, split
  * DoltHub post-no-preference/earnings - earnings_calendar
  * Cboe                                 - BXM index daily history

Stdlib only. Run from the repo root:
    python scripts/fetch_real_data.py                 # every ticker, resumes where it stopped
    python scripts/fetch_real_data.py --tickers F,T   # a subset
Writes data/real/<kind>/<TICKER>.csv(.gz) plus data/real/SOURCES.json. Safe to re-run:
a finished file is skipped unless --force.
"""
import argparse
import csv
import gzip
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

API = "https://www.dolthub.com/api/v1alpha1/post-no-preference/{db}/master"
BXM_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/BXM_History.csv"
TICKERS = ["F", "VALE", "AAL", "T", "VZ", "PFE", "KMI", "CMCSA", "KEY", "HBAN", "PBR",
           "ITUB", "KGC", "OXY", "CSX", "BMY", "USB", "PYPL", "MO", "MDLZ", "BAC", "SPY"]
PAGE = 1000           # DoltHub returns at most 1000 rows per query
OUT = Path("data/real")
UA = {"User-Agent": "ccbot-research/0.1"}


def get(url, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            wait = 2 ** i * 2
            print(f"  retry {i + 1}/{tries} in {wait}s: {e}", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"failed after {tries} tries: {url[:200]}")


def sql(db, q, tries=4):
    url = API.format(db=db) + "?q=" + urllib.parse.quote(q)
    for i in range(tries):
        d = json.loads(get(url))
        if "deadline exceeded" not in str(d.get("query_execution_message")) or i == tries - 1:
            break
        print(f"  server timeout, retry {i + 1}/{tries - 1}", flush=True)
        time.sleep(10 * (i + 1))
    if d.get("query_execution_status") not in ("Success", "RowLimit"):
        raise RuntimeError(f"{db}: {d.get('query_execution_status')} {d.get('query_execution_message')}\n{q}")
    time.sleep(0.4)
    return d.get("rows", []) or []


def paged(db, q_base, order):
    rows, off = [], 0
    while True:
        part = sql(db, f"{q_base} ORDER BY {order} LIMIT {PAGE} OFFSET {off}")
        rows += part
        if len(part) < PAGE:
            return rows
        off += PAGE


def write(path, rows, gz=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    opener = gzip.open if gz else open
    with opener(tmp, "wt", newline="", encoding="utf-8") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    tmp.replace(path)
    print(f"  wrote {path} ({len(rows)} rows)", flush=True)


def schemas():
    out = {}
    for db, tables in {"options": ["option_chain", "volatility_history"],
                       "stocks": ["ohlcv", "dividend", "split"],
                       "earnings": ["earnings_calendar"]}.items():
        for t in tables:
            out[f"{db}.{t}"] = sql(db, f"DESCRIBE `{t}`")
    return out


def date_chunks(start, end, n):
    """Weekdays from start to end as SQL IN-lists of n dates. DoltHub times out on
    date range scans (PK is date-first but ranges are not index-optimised); IN-lists are fast."""
    days, d = [], start
    while d <= end:
        if d.weekday() < 5:
            days.append(d.isoformat())
        d += timedelta(days=1)
    for i in range(0, len(days), n):
        part = days[i:i + n]
        yield part[0], "(" + ",".join(f"'{x}'" for x in part) + ")"


def chunked(db, q_fmt, order, start, n):
    rows = []
    for first, inl in date_chunks(start, date.today(), n):
        rows += paged(db, q_fmt.format(dates=inl), order)
    return rows


def fetch_ticker(tk, start, force):
    s = tk.replace("'", "")
    jobs = {
        OUT / "prices" / f"{tk}.csv": ("stocks", f"SELECT * FROM ohlcv WHERE date IN {{dates}} AND act_symbol='{s}'", "date"),
        OUT / "dividends" / f"{tk}.csv": ("stocks", f"SELECT * FROM dividend WHERE act_symbol='{s}'", "ex_date"),
        OUT / "splits" / f"{tk}.csv": ("stocks", f"SELECT * FROM split WHERE act_symbol='{s}'", "ex_date"),
        OUT / "earnings" / f"{tk}.csv": ("earnings", f"SELECT * FROM earnings_calendar WHERE act_symbol='{s}'", "date"),
        OUT / "volhist" / f"{tk}.csv": ("options", f"SELECT * FROM volatility_history WHERE date IN {{dates}} AND act_symbol='{s}'", "date"),
    }
    for path, (db, q, order) in jobs.items():
        if path.exists() and not force:
            continue
        print(f"{tk}: {path.parent.name}", flush=True)
        write(path, chunked(db, q, order, start, 120) if "{dates}" in q else paged(db, q, order))
    # Calls only, 5-80 days to expiry: everything a 1-week to 2-month covered call can use.
    opath = OUT / "options" / f"{tk}.csv.gz"
    if opath.exists() and not force:
        return
    rows = []
    for first, inl in date_chunks(start, date.today(), 20):
        q = (f"SELECT * FROM option_chain WHERE date IN {inl} AND act_symbol='{s}' "
             f"AND call_put = 'Call' AND expiration >= DATE_ADD(date, INTERVAL 5 DAY) "
             f"AND expiration <= DATE_ADD(date, INTERVAL 80 DAY)")
        part = paged("options", q, "date, expiration, strike")
        rows += part
        print(f"{tk}: options {first} (+{len(part)}, total {len(rows)})", flush=True)
    write(opath, rows, gz=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", default=",".join(TICKERS))
    ap.add_argument("--start", default="2019-01-01")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    start = date.fromisoformat(a.start)
    OUT.mkdir(parents=True, exist_ok=True)
    sch = OUT / "SCHEMAS.json"
    if not sch.exists():
        sch.write_text(json.dumps(schemas(), indent=1), encoding="utf-8")
    bxm = OUT / "BXM_History.csv"
    if not bxm.exists() or a.force:
        bxm.write_bytes(get(BXM_URL))
        print(f"  wrote {bxm}", flush=True)
    failed = []
    for tk in [t.strip().upper() for t in a.tickers.split(",") if t.strip()]:
        try:
            fetch_ticker(tk, start, a.force)
        except Exception as e:  # keep going; report at the end
            print(f"{tk}: FAILED {e}", flush=True)
            failed.append(tk)
    (OUT / "SOURCES.json").write_text(json.dumps({
        "fetched": date.today().isoformat(),
        "dolthub": "https://www.dolthub.com/repositories/post-no-preference (options, stocks, earnings)",
        "bxm": BXM_URL, "start": a.start, "failed": failed}, indent=1), encoding="utf-8")
    print("FAILED: " + ",".join(failed) if failed else "ALL OK")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
