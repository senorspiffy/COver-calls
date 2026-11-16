#!/usr/bin/env python3
"""Diff two realtest report dirs over every summary.json key and every CSV row (item 067, RI-013).

Usage: python3 scripts/diff_reports.py <before_dir> <after_dir> [--max-rows N]

Exit codes: 0 = no change, 1 = changes, 2 = error (the error line goes to stderr, nothing else
is reported as a result).

Rules:
- Files: the union of names in both dirs, sorted. A .json or .csv on one side only prints
  `ONLY IN BEFORE/AFTER: <f>` (a CSV with its row count). Any other file or subdir prints
  `NOT COMPARED: <f>` and is counted in TOTAL, never skipped silently.
- JSON: parsed with parse_constant, so bare NaN/Infinity/-Infinity become floats and are counted
  per side (`NaN tokens: before a, after b`). The walk recurses through dicts (union of keys) and
  lists (index-aligned). A leaf is equal only if both sides have the same type and an equal value,
  or both are float NaN. `1` vs `1.0`, `true` vs `1` and `null` vs `0` print as TYPE changes.
  Containers are never compared with `==`. Every JSON change is printed (no cap).
- CSV: read with csv.reader, cells compared as exact strings (no tolerance). Rows are matched by
  the key in KEYS (trades_*.csv by open_date) when all key columns are on both sides, otherwise by
  row index with a `MATCH <f>: index (<why>)` line. A duplicate key, a duplicate header name or a
  ragged row exits 2.

Known limits (not handled here):
- JSON lists are index-aligned. If walkforward_picks gains a leading window, every later item
  shows as changed. walkforward_picks.csv is key-matched on (train_from, test_from), so its CSV
  section gives the true count. Both views are printed.
- In a CSV, pandas writes NaN, None and '' all as an empty cell, so they cannot be told apart.
  Cell-by-cell string comparison is only meaningful when both runs used the same python/pandas.
"""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

KEYS = {
    "walkforward_picks.csv": ("train_from", "test_from"),
    "walkforward_by_ticker.csv": ("ticker",),
    "bot_rule_by_ticker.csv": ("ticker", "config"),
    "grid_in_sample.csv": ("ticker", "config"),
}
TRADES_KEY = ("open_date",)


class DiffError(Exception):
    """An input that cannot be compared. main() prints it to stderr and exits 2."""


def load_json(path):
    """Return (obj, nan_count). NaN/Infinity/-Infinity map to float and are counted."""
    path = Path(path)
    count = [0]

    def _const(name):
        count[0] += 1
        return float(name)

    try:
        text = path.read_text(encoding="utf-8")
        obj = json.loads(text, parse_constant=_const)
    except (ValueError, UnicodeDecodeError) as exc:
        raise DiffError(f"BAD JSON {path.name}: {exc}") from None
    return obj, count[0]


def _is_nan(x):
    return type(x) is float and math.isnan(x)


def _join(path, key):
    return f"{path}.{key}" if path else str(key)


def diff_json(a, b, path=""):
    """Every difference between two parsed JSON values, one line each."""
    out = []
    if type(a) is dict and type(b) is dict:
        for k in sorted(set(a) | set(b)):
            p = _join(path, k)
            if k not in b:
                out.append(f"REMOVED {p} = {a[k]!r}")
            elif k not in a:
                out.append(f"ADDED {p} = {b[k]!r}")
            else:
                out.extend(diff_json(a[k], b[k], p))
        return out
    if type(a) is list and type(b) is list:
        if len(a) != len(b):
            out.append(f"LENGTH {path}: {len(a)} -> {len(b)}")
        for i in range(max(len(a), len(b))):
            p = f"{path}[{i}]"
            if i >= len(b):
                out.append(f"REMOVED {p} = {a[i]!r}")
            elif i >= len(a):
                out.append(f"ADDED {p} = {b[i]!r}")
            else:
                out.extend(diff_json(a[i], b[i], p))
        return out
    if type(a) is not type(b):
        out.append(f"TYPE {path}: {type(a).__name__} {a!r} -> {type(b).__name__} {b!r}")
        return out
    if a == b or (_is_nan(a) and _is_nan(b)):
        return out
    out.append(f"{path}: {a!r} -> {b!r}")
    return out


def read_csv(path):
    """Return (header, rows). A 0-byte file or an empty first row gives ([], [])."""
    path = Path(path)
    name = path.name
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            header = None
            rows = []
            for row in reader:
                if header is None:
                    header = row
                    if len(set(header)) != len(header):
                        dups = sorted({c for c in header if header.count(c) > 1})
                        raise DiffError(f"DUPLICATE COLUMN {name}: {dups}")
                    continue
                if not header or len(row) != len(header):
                    raise DiffError(f"BAD ROW {name} line {reader.line_num}: "
                                    f"{len(row)} fields, header has {len(header)}")
                rows.append(row)
    except (csv.Error, UnicodeDecodeError) as exc:
        raise DiffError(f"BAD CSV {name}: {exc}") from None
    return (header or []), rows


def key_for(name):
    if name in KEYS:
        return KEYS[name]
    if name.startswith("trades_") and name.endswith(".csv"):
        return TRADES_KEY
    return None


def _index_rows(name, header, rows, key):
    idx = [header.index(c) for c in key]
    out = {}
    for r in rows:
        k = tuple(r[i] for i in idx)
        out.setdefault(k, []).append(r)
    for k, rs in out.items():
        if len(rs) > 1:
            raise DiffError(f"DUPLICATE KEY {name}: {_show_key(k)} ({len(rs)} rows)")
    return {k: rs[0] for k, rs in out.items()}


def _show_key(k):
    return k[0] if len(k) == 1 else "(" + ", ".join(k) + ")"


def diff_csv(name, before, after, max_rows):
    """Diff two (header, rows) pairs. Returns (lines, counts)."""
    ha, ra = before
    hb, rb = after
    lines = []
    counts = {"rows_changed": 0, "rows_added": 0, "rows_removed": 0, "columns_changed": 0}
    if ha != hb:
        added = [c for c in hb if c not in ha]
        removed = [c for c in ha if c not in hb]
        order = "" if added or removed else " (order changed)"
        lines.append(f"COLUMNS {name}: added {added} removed {removed}{order}")
        counts["columns_changed"] = 1
    common = [c for c in hb if c in ha]
    ia = {c: ha.index(c) for c in common}
    ib = {c: hb.index(c) for c in common}

    key = key_for(name)
    why = None
    if key is None:
        why = "no key for this file name"
    else:
        for side, h in (("before", ha), ("after", hb)):
            if not h:
                why = f"columns [] in {side}"
                break
            missing = [c for c in key if c not in h]
            if missing:
                why = f"key column {', '.join(missing)} missing in {side}"
                break

    # pairs: (label, row_a or None, row_b or None) in after-file order, removed last
    changed_lines, removed_lines = [], []
    by_col = {c: 0 for c in common}
    if why is None:
        match = "key"
        ma = _index_rows(name, ha, ra, key)
        mb = _index_rows(name, hb, rb, key)
        idx_b = [hb.index(c) for c in key]
        idx_a = [ha.index(c) for c in key]
        pairs = []
        for r in rb:
            k = tuple(r[i] for i in idx_b)
            pairs.append((_show_key(k), ma.get(k), r))
        for r in ra:
            k = tuple(r[i] for i in idx_a)
            if k not in mb:
                pairs.append((_show_key(k), r, None))
    else:
        match = "index"
        lines.append(f"MATCH {name}: index ({why})")
        pairs = []
        for i in range(max(len(ra), len(rb))):
            pairs.append((f"row {i}", ra[i] if i < len(ra) else None, rb[i] if i < len(rb) else None))

    matched = 0
    for label, a, b in pairs:
        if a is None:
            counts["rows_added"] += 1
            changed_lines.append(f"  ADDED {label}")
        elif b is None:
            counts["rows_removed"] += 1
            removed_lines.append(f"  REMOVED {label}")
        else:
            matched += 1
            diffs = []
            for c in common:
                va, vb = a[ia[c]], b[ib[c]]
                if va != vb:
                    by_col[c] += 1
                    diffs.append(f"{c}: {va!r} -> {vb!r}")
            if diffs:
                counts["rows_changed"] += 1
                changed_lines.append(f"  {label}: " + "; ".join(diffs))

    cols = ", ".join(f"{c}={n}" for c, n in by_col.items() if n) or "none"
    lines.append(f"CSV {name}: match {match}, rows {len(ra)} -> {len(rb)}, matched {matched}, "
                 f"added {counts['rows_added']}, removed {counts['rows_removed']}, "
                 f"changed {counts['rows_changed']}; by column: {cols}")
    row_lines = changed_lines + removed_lines
    if max_rows and len(row_lines) > max_rows:
        lines.extend(row_lines[:max_rows])
        lines.append(f"  ... {len(row_lines) - max_rows} more")
    else:
        lines.extend(row_lines)
    return lines, counts


def _check_dir(p):
    p = Path(p)
    if not p.is_dir():
        raise DiffError(f"MISSING DIR: {p}")
    if not any(f.is_file() and f.suffix in (".json", ".csv") for f in p.iterdir()):
        raise DiffError(f"EMPTY DIR: {p}")
    return p


def diff_dirs(before, after, max_rows=20):
    """Diff two report dirs. Returns (lines, totals). Raises DiffError on any input it can't compare."""
    da, db = _check_dir(before), _check_dir(after)
    names = sorted({f.name for f in da.iterdir()} | {f.name for f in db.iterdir()})
    t = {"files": len(names), "only_before": 0, "only_after": 0, "not_compared": 0,
         "json_changes": 0, "rows_changed": 0, "rows_added": 0, "rows_removed": 0,
         "columns_changed": 0}
    lines = []
    for n in names:
        fa, fb = da / n, db / n
        kind = Path(n).suffix
        a_ok = fa.is_file() and kind in (".json", ".csv")
        b_ok = fb.is_file() and kind in (".json", ".csv")
        if not ((a_ok or not fa.exists()) and (b_ok or not fb.exists())):
            lines.append(f"NOT COMPARED: {n}{'/' if fa.is_dir() or fb.is_dir() else ''}")
            t["not_compared"] += 1
            continue
        if not fb.exists() or not fa.exists():
            side, f = ("BEFORE", fa) if fa.exists() else ("AFTER", fb)
            extra = f" ({len(read_csv(f)[1])} rows)" if kind == ".csv" else ""
            lines.append(f"ONLY IN {side}: {n}{extra}")
            t["only_before" if side == "BEFORE" else "only_after"] += 1
            continue
        if kind == ".json":
            ja, na = load_json(fa)
            jb, nb = load_json(fb)
            changes = diff_json(ja, jb)
            lines.append(f"JSON {n}: NaN tokens: before {na}, after {nb}; changes {len(changes)}")
            lines.extend(changes)
            t["json_changes"] += len(changes)
        else:
            cl, c = diff_csv(n, read_csv(fa), read_csv(fb), max_rows)
            lines.extend(cl)
            for k, v in c.items():
                t[k] += v
    total = (f"TOTAL: files {t['files']}, only-before {t['only_before']}, only-after {t['only_after']}, "
             f"not compared {t['not_compared']}, json changes {t['json_changes']}, "
             f"csv rows changed {t['rows_changed']} added {t['rows_added']} removed {t['rows_removed']}, "
             f"columns changed {t['columns_changed']}")
    lines.append(total)
    if not _has_change(t):
        lines.append("no change")
    return lines, t


def _has_change(t):
    return any(t[k] for k in ("only_before", "only_after", "json_changes", "rows_changed",
                              "rows_added", "rows_removed", "columns_changed"))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Diff two realtest report dirs (item 067).")
    ap.add_argument("before_dir")
    ap.add_argument("after_dir")
    ap.add_argument("--max-rows", type=int, default=20, help="row lines per CSV (0 = all)")
    args = ap.parse_args(argv)
    if args.max_rows < 0:
        print("BAD ARG: --max-rows must be >= 0", file=sys.stderr)
        return 2
    try:
        lines, totals = diff_dirs(args.before_dir, args.after_dir, args.max_rows)
    except DiffError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 1 if _has_change(totals) else 0


if __name__ == "__main__":
    sys.exit(main())
