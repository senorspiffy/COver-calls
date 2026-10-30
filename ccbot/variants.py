"""Pre-registered variants. All run every time; reported in registry order, never by result."""
from dataclasses import dataclass, replace

import pandas as pd


@dataclass(frozen=True)
class Variant:
    id: str
    name: str
    expiry_kind: str = "monthly"
    profit_take: bool = False
    up_day_only: bool = False
    iv_theta: float = 0.0       # 0 = IV filter off
    wheel: bool = False

    @property
    def label(self):
        return f"{self.id} θ{self.iv_theta:g}" if self.id == "V4" else self.id


REGISTRY = (
    Variant("V0", "baseline: monthly 30-45 DTE, delta 0.25-0.30, hold to expiry"),
    Variant("V1", "V0 + buy back at <= 50% of premium in first third of life", profit_take=True),
    Variant("V2", "weekly 5-9 DTE, hold", expiry_kind="weekly"),
    Variant("V3", "V0, entry only after an up day", up_day_only=True),
    # θ is free and chosen walk-forward; 66 (ORATS C5) is only the bot's default.
    Variant("V4", "V0 + enter only if vol percentile (252 d) > θ", iv_theta=66),
    Variant("V5", "wheel: V0, then a 30-45 DTE CSP after assignment", wheel=True),
)
BY_ID = {v.id: v for v in REGISTRY}


def expand(cfg):
    """Every (variant, θ) config in registry order (V4 once per θ)."""
    out = []
    for v in REGISTRY:
        thetas = cfg["sweeps"]["v4_theta"] if v.id == "V4" else [v.iv_theta]
        out += [replace(v, iv_theta=t) for t in thetas]
    return out


def run_grid(series, cfg, quick=False):
    """One row per (variant, θ, spread, k), in registry order. Returns (rows, results)."""
    from .backtest import buy_and_hold, build_days, metrics, run_backtest

    spreads = [cfg["spread"]["value"]] if quick else cfg["sweeps"]["spread"]
    ks = [cfg["k"]] if quick else cfg["sweeps"]["k"]
    bh = buy_and_hold(series, cfg)
    bh_cagr = metrics(bh, None, cfg)["cagr"]
    rows, results = [], {}
    days_by_k = {k: build_days(series.scaled(k)) for k in ks}
    for spread in spreads:
        run_cfg = {**cfg, "spread": {**cfg["spread"], "model": "fixed", "value": spread}}
        for k in ks:
            for v in expand(cfg):
                res = run_backtest(series, v, run_cfg, days=days_by_k[k])
                results[(v.label, spread, k)] = res
                rows.append({"variant": v.id, "config": v.label, "theta": v.iv_theta if v.id == "V4" else None,
                             "spread": spread, "k": k, **res.metrics,
                             "excess_vs_bh": res.metrics["cagr"] - bh_cagr})
    return pd.DataFrame(rows), results, bh
