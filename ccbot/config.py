"""Load and validate the JSON config. Every money value is in $."""
import copy
import json
from pathlib import Path


class ConfigError(ValueError):
    pass


DEFAULTS = {
    "cash": 3000,
    "cash_buffer": 200,
    "max_single_name_frac": 0.5,
    "max_positions": 2,
    "tickers_file": None,
    "earnings_gap_days": 70,
    "r": 0.04,
    "target_delta": 0.275,
    "band": [0.25, 0.30],
    "tolerance": [0.20, 0.35],
    "monthly_dte": [30, 45],
    "monthly_slack_days": 7,
    "weekly_dte": [5, 9],
    # item 058: per-ticker monthly DTE window (staggered expiries), e.g. {"VALE": [60, 75]}
    "monthly_dte_by_ticker": {},
    # item 058: open a new position only after a dip: today's close <= (1 - drop) x the highest
    # recorded close of the last `lookback` scans (today included), once >= min_days are recorded
    "dip_entry": None,
    "spread": {"model": "fixed", "value": 0.05, "floor": 0.01},
    "k": 1.0,
    "rv_window": 20,
    "fees": {
        "commission": 0,
        "reg_per_contract": 0.10,
        "sec_rate": 0.0000206,
        "cat_rate": 0.000003,
        "assignment_fee": 0,
        "_unverified": ["reg_per_contract", "assignment_fee"],
    },
    "screen": {"max_spread": 0.05, "min_oi": 500},
    "universe": ["SYNTH_A", "SYNTH_B", "SYNTH_C"],
    "sweeps": {"spread": [0.01, 0.03, 0.05, 0.10], "k": [0.8, 1.0, 1.2], "v4_theta": [50, 66, 80]},
    "walkforward": {"min_train_years": 3, "holdout_years": 2},
    "broker": "sim",
    "dry_run": True,
}


def _merge(base, over):
    out = copy.deepcopy(base)
    for key, val in over.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], val)
        else:
            out[key] = val
    return out


def validate(cfg):
    lo, hi = cfg["band"]
    tlo, thi = cfg["tolerance"]
    if not 0 < cfg["target_delta"] < 1:
        raise ConfigError("target_delta must be in (0, 1)")
    if not (tlo <= lo <= hi <= thi):
        raise ConfigError("band must lie inside tolerance")
    for name in ("monthly_dte", "weekly_dte"):
        a, b = cfg[name]
        if not 0 < a <= b:
            raise ConfigError(f"{name} must be 0 < min <= max")
    for t, rng in cfg["monthly_dte_by_ticker"].items():
        if not (isinstance(rng, list) and len(rng) == 2 and 0 < rng[0] <= rng[1]):
            raise ConfigError(f"monthly_dte_by_ticker[{t}] must be [min, max] with 0 < min <= max")
    dip = cfg["dip_entry"]
    if dip is not None:
        if not (0 < dip.get("drop", 0) < 1):
            raise ConfigError("dip_entry.drop must be in (0, 1)")
        lb, md = dip.get("lookback"), dip.get("min_days")
        if not (isinstance(lb, int) and isinstance(md, int) and 1 <= md <= lb):
            raise ConfigError("dip_entry needs integers 1 <= min_days <= lookback")
    if cfg["spread"]["model"] not in ("fixed", "pct_of_mid"):
        raise ConfigError("spread.model must be 'fixed' or 'pct_of_mid'")
    if cfg["spread"]["value"] < 0 or cfg["spread"]["floor"] < 0:
        raise ConfigError("spreads must be >= 0")
    if any(s < 0 for s in cfg["sweeps"]["spread"]):
        raise ConfigError("sweep spreads must be >= 0")
    if cfg["k"] <= 0 or any(k <= 0 for k in cfg["sweeps"]["k"]):
        raise ConfigError("k must be > 0")
    if not isinstance(cfg["earnings_gap_days"], int) or cfg["earnings_gap_days"] < 1:
        raise ConfigError("earnings_gap_days must be an integer >= 1")
    if not isinstance(cfg["max_positions"], int) or cfg["max_positions"] < 1:
        raise ConfigError("max_positions must be an integer >= 1")
    if cfg["cash"] <= 0:
        raise ConfigError("cash must be > 0")
    return cfg


def for_ticker(cfg, ticker):
    """cfg with this ticker's own monthly DTE window, if it has one (item 058); else cfg itself."""
    rng = cfg.get("monthly_dte_by_ticker", {}).get(ticker)
    return {**cfg, "monthly_dte": rng} if rng else cfg


def load_config(path=None, overrides=None):
    """Defaults, then the JSON file (if given), then `overrides`; validated."""
    cfg = copy.deepcopy(DEFAULTS)
    if path is not None:
        try:
            cfg = _merge(cfg, json.loads(Path(path).read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            raise ConfigError(f"cannot read config {path}: {exc}") from exc
    if overrides:
        cfg = _merge(cfg, overrides)
    return validate(cfg)
