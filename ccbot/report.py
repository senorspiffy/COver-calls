"""Markdown/CSV reports. Plain tables in registry order; nothing sorted or highlighted by result."""
import datetime as dt
import math

from . import BANNER_MODELLED, BANNER_SYNTHETIC


def _fmt(x, kind="num"):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    if kind == "pct":
        return f"{x * 100:.2f}%"
    if kind == "usd":
        return f"${x:,.2f}"
    if isinstance(x, float):
        return f"{x:.4g}"
    return str(x)


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def banners(synthetic, modelled=True):
    out = [f"> **{BANNER_MODELLED}**"] if modelled else []
    if synthetic:
        out.append(f"> **{BANNER_SYNTHETIC}**")
    return "\n".join(out)


def cost_lines(cfg):
    f, sp = cfg["fees"], cfg["spread"]
    unv = ", ".join(f["_unverified"])
    return [f"- Spread model: {sp['model']} (base ${sp['value']:.2f}/contract, floor ${sp['floor']:.2f})",
            f"- Fees per option fill: commission ${f['commission']}, reg_per_contract ${f['reg_per_contract']}, "
            f"SEC {f['sec_rate']} x sell notional, CAT {f['cat_rate']} x notional; assignment_fee ${f['assignment_fee']}",
            f"- UNVERIFIED fee values: {unv}",
            "- Share trades: no fees modelled. Idle cash earns 0%.",
            f"- Volatility multiplier k = {cfg['k']}: multiplies the vol input (the `iv` column when present, else "
            f"trailing realised vol). k UNCALIBRATED (no real option snapshots yet)."]


METRIC_COLS = [("cagr", "CAGR", "pct"), ("vol", "Vol", "pct"), ("max_dd", "Max DD", "pct"),
               ("sharpe", "Sharpe", "num"), ("fills", "Fills", "num"), ("premium", "Premium", "usd"),
               ("spread_paid", "Spread paid", "usd"), ("fees_paid", "Fees", "usd"),
               ("excess_vs_bh", "Excess vs B&H (CAGR)", "pct")]


def missing_lines(missing, results, cfg, asset_type):
    """One line per absent optional CSV column (005), counted on V0 at the base setting."""
    reasons = results[("V0", cfg["spread"]["value"], cfg["k"])].reasons
    out = []
    for col in missing:
        if col == "earnings" and asset_type == "etf":
            out.append("- earnings: not supplied (ETF: no earnings, nothing blocked)")
        else:
            code = {"earnings": "EARNINGS_UNKNOWN", "dividend": "DIVIDEND_UNKNOWN"}[col]
            out.append(f"- {col}: not supplied ({reasons.get(code, 0)} days blocked, {code})"
                       + ("; buy and hold n/a" if col == "dividend" else ""))
    return out or ["- none"]


def backtest_report(grid, results, wf, bh_metrics, cfg, meta, asof, missing=()):
    """grid: DataFrame from variants.run_grid. Returns (markdown, csv)."""
    from .variants import REGISTRY, expand

    base_spread, base_k = cfg["spread"]["value"], cfg["k"]
    df_dates = next(iter(results.values())).equity.index
    lines = [f"# Backtest report - {meta['ticker']} - {asof}", "", banners(meta.get("synthetic", False)), "",
             "## Data", f"- Ticker: {meta['ticker']}; source: {meta['source']}; synthetic: {meta.get('synthetic')}; "
             f"asset type: {meta.get('asset_type')}",
             f"- Dates: {df_dates[0]:%Y-%m-%d} to {df_dates[-1]:%Y-%m-%d} ({len(df_dates)} trading days)",
             f"- Starting cash ${cfg['cash']:,}; cash buffer ${cfg['cash_buffer']}; r = {cfg['r']}",
             "", "## Costs and assumptions", *cost_lines(cfg),
             f"- Strike: grid strike with |delta| nearest {cfg['target_delta']}, traded if in "
             f"{cfg['tolerance']}; in_band = {cfg['band']}. Calls never below cost basis.",
             f"- Monthly expiry: {cfg['monthly_dte']} DTE, else the nearest monthly within "
             f"{cfg['monthly_slack_days']} days of that window (in_window=False).",
             "", "## Missing inputs", *missing_lines(missing, results, cfg, meta.get("asset_type")),
             "", "## Variants (pre-registered)",
             table(["ID", "Rule"], [[v.id, v.name] for v in REGISTRY]), "",
             "## Buy and hold (same start, cash, dividends)",
             f"n/a ({bh_metrics['na_reason']})" if bh_metrics.get("na_reason") else
             table(["CAGR", "Vol", "Max DD", "Sharpe"],
                   [[_fmt(bh_metrics[c], k) for c, k in (("cagr", "pct"), ("vol", "pct"),
                                                           ("max_dd", "pct"), ("sharpe", "num"))]]), ""]
    lines.append("## Full-period results, one table per sensitivity setting")
    for spread in sorted(grid["spread"].unique()):
        for k in sorted(grid["k"].unique()):
            sub = grid[(grid["spread"] == spread) & (grid["k"] == k)]
            lines += ["", f"### spread ${spread:.2f}, k {k}",
                      table(["Config"] + [h for _, h, _ in METRIC_COLS],
                            [[r["config"]] + [_fmt(r[c], f) for c, _, f in METRIC_COLS] for _, r in sub.iterrows()])]
    lines += ["", f"## No-trade reasons (days), spread ${base_spread:.2f}, k {base_k}",
              table(["Config", "Reasons"],
                    [[c.label, ", ".join(f"{k} {n}" for k, n in sorted(results[(c.label, base_spread, base_k)]
                                                                       .reasons.items()))]
                     for c in expand(cfg)])]
    if wf is not None:
        lines += ["", f"## Walk-forward (spread ${base_spread:.2f}, k {base_k})",
                  "Expanding window. Only V4's θ is chosen (highest compounded train return); other variants "
                  "are fixed. Selection uses calendar-year slices of each full-period run, which is an "
                  "approximation because runs are path-dependent.", "",
                  table(["Variant", "Train", "Test", "Chosen", "OOS return", "B&H return"],
                        [[r["variant"], r["train"], r["test"], r["chosen"], _fmt(r["oos_return"], "pct"),
                          _fmt(r["bh_return"], "pct")] for _, r in wf["folds"].iterrows()]),
                  "", "### Stitched out-of-sample",
                  table(["Variant", "OOS years", "OOS CAGR", "B&H OOS CAGR"],
                        [[r["variant"], r["oos_years"], _fmt(r["oos_cagr"], "pct"), _fmt(r["bh_oos_cagr"], "pct")]
                         for _, r in wf["summary"].iterrows()]),
                  "", f"### Held-out years ({', '.join(map(str, wf['holdout']))}), reported once",
                  "Excluded from every selection step above.", "",
                  table(["Variant", "Config", "Held-out CAGR", "B&H held-out CAGR", "Excess"],
                        [[r["variant"], r["heldout_config"], _fmt(r["heldout_cagr"], "pct"),
                          _fmt(r["bh_heldout_cagr"], "pct"), _fmt(r["heldout_excess"], "pct")]
                         for _, r in wf["summary"].iterrows()]),
                  "", "## Overfitting check",
                  f"- PBO (CSCV, S=8, monthly returns, held-out years excluded) across {wf['n_configs']} "
                  f"configs: " + (f"{wf['pbo']:.3f}" if not math.isnan(wf["pbo"]) else
                                  f"n/a (needs >= 8 non-held-out months and >= 2 configs; "
                                  f"have {wf['pbo_months']} months)")]
    lines += [f"- Configs tested: {len(grid)}", "", "No variant was selected for live use.", ""]
    return "\n".join(lines), grid.to_csv(index=False)


def _days_to(d, asof):
    return (d - asof).days if d else "n/a"


def daily_report(scan):
    asof = dt.date.fromisoformat(scan["date"])
    lines = [f"# Daily scan - {scan['date']} - {scan['variant']} - broker {scan['broker']}", "",
             banners(scan["synthetic"], scan["modelled"]), ""]
    if scan["banner"]:
        lines += [f"> **{scan['banner']}**", ""]
    if scan.get("early_close"):
        lines += ["> Early close today: 1:00 p.m. ET (1:15 p.m. for eligible options); run the scan before then.", ""]
    if scan["skipped"]:
        lines += ["Already scanned for this date and variant: no new decision was made.", ""]
    pos = scan["positions"]
    o = pos["option"]
    lines += ["## Positions",
              f"- Ticker: {pos['ticker'] or 'none'}; shares {pos['shares']}; cost basis {_fmt(pos['basis'], 'usd')}; "
              f"cash {_fmt(pos['cash'], 'usd')}; equity {_fmt(scan['equity'], 'usd')}",
              f"- Open option: {o['kind']} {o['strike']} exp {o['expiry']} x{o['qty']} sold at {o['premium']}"
              if o else "- Open option: none", "",
              "## Screen", f"- Passing: {', '.join(scan['passing']) or 'none'}",
              f"- Rejected: {', '.join(f'{t} ({r})' for t, r in scan['rejects'].items()) or 'none'}",
              *[f"- {t}: passed {n} of last {k} logged scans" + (f" (history short: {k} < 10)" if k < 10 else "")
                for t, (n, k) in scan.get("pass_history", {}).items()], "",
              "## Today's decision",
              table(["Action", "Reason", "Contract", "Limit", "TIF", "Delta", "in_band", "in_window", "Status", "Fill"],
                    [[r["action"], r["reason"], r["contract"] or "-", r["limit"] if r["limit"] is not None else "-",
                      r["tif"] or "-", _fmt(r["delta"]), r["in_band"], r["in_window"], r["status"],
                      r["fill"] if r["fill"] is not None else "-"] for r in scan["decisions"]]),
              "", "## Context"]
    ctx = scan["context"]
    if ctx:
        lines += [f"- Underlying {ctx['ticker']} at {_fmt(ctx['price'], 'usd')}",
                  f"- Vol percentile (252 d): {_fmt(ctx['vol_pct']) if ctx['vol_pct'] is not None else 'n/a'}"
                  f"{'' if ctx['vol_pct'] is not None else ' (fewer than 252 days of history)'}",
                  f"- Spread at the chosen strike: {_fmt(ctx['spread'], 'usd') if ctx['spread'] is not None else 'n/a'}",
                  f"- Days to earnings: "
                  f"{_days_to(_date(ctx['next_earnings']), asof) if ctx.get('earnings_known', True) else 'n/a (not supplied)'}; "
                  f"days to ex-dividend: {_days_to(_date(ctx['ex_div_date']), asof) if ctx['ex_div_date'] else 'n/a (not supplied)'}"]
    else:
        lines.append("- No ticker to trade today.")
    lines += ["", "## Would each variant act today?",
              table(["Variant", "Action", "Reason"], [[v, a, r] for v, (a, r) in scan["would_act"].items()]),
              "", f"Broker {scan['broker']}; dry-run: {scan['dry_run']}. No order reaches a live account; "
              "live trading is not built.", ""]
    return "\n".join(lines)


def _date(x):
    return dt.date.fromisoformat(x) if x else None


def weekly_report(date, trades, scans, cfg):
    """trades: DataFrame of state/paper_trades.csv; scans: list of scan dicts up to `date`."""
    first, last = scans[0], scans[-1]
    p0 = first["context"]["price"] if first["context"] else None
    p1 = last["context"]["price"] if last["context"] else None
    equity0 = cfg["cash"]
    paper = last["equity"] - equity0
    if p0 and p1 and first["context"]["ticker"] == last["context"]["ticker"]:
        lots = int((equity0 - cfg["cash_buffer"]) // (p0 * 100))
        if lots < 1:
            bh_text = "n/a (100 shares cost more than cash − buffer)"
        else:
            bh = lots * 100 * (p1 - p0)
            bh_text = _fmt(bh, "usd") + f" ({lots * 100} sh {first['context']['ticker']}, {first['date']} to " \
                                        f"{last['date']}, dividends not included)"
    else:
        bh_text = "n/a (no common ticker priced on the first and last scan)"
    fills = trades[trades["status"] == "FILLED"]
    opt = fills[fills["action"].isin(["SELL_CALL", "SELL_PUT", "BUY_TO_CLOSE"])]
    spread_paid = float(((opt["mid"] - opt["fill"]).abs() * 100 * opt["qty"]).sum()) if len(opt) else 0.0
    orders = trades[trades["action"].isin(["SELL_CALL", "SELL_PUT", "BUY_TO_CLOSE", "BUY_SHARES"])]
    breaches = orders[(orders["in_band"].astype(str) == "False") | (orders["status"] != "FILLED")]
    lines = [f"# Weekly paper report - week ending {date}", "",
             banners(last["synthetic"], last["modelled"]), "",
             f"- Scans: {len(scans)} ({first['date']} to {last['date']})",
             f"- Paper P/L: {_fmt(paper, 'usd')} (equity {_fmt(last['equity'], 'usd')} vs start {_fmt(equity0, 'usd')})",
             f"- Buy-and-hold P/L: {bh_text}",
             f"- Fills: {len(fills)} ({len(opt)} option fills); spread paid {_fmt(spread_paid, 'usd')}",
             f"- Rule breaches (in_band False or order not filled): {len(breaches)}", ""]
    if len(breaches):
        lines.append(table(["Date", "Action", "Contract", "in_band", "Status"],
                           [[r["date"], r["action"], r["contract"], r["in_band"], r["status"]]
                            for _, r in breaches.iterrows()]))
    lines += ["", "Live trading is not built.", ""]
    return "\n".join(lines)
