"""Fill prices and fees. Fee values come from config; two are UNVERIFIED (see config)."""
import math

CONTRACT = 100


def round_tick(x):
    """Nearest $0.01, never below $0.00."""
    return max(0.0, math.floor(x * 100 + 0.5 + 1e-9) / 100)


def half_spread(mid, cfg):
    sp = cfg["spread"]
    if sp["model"] == "fixed":
        return sp["value"] / 2
    return max(sp["value"] * mid, sp["floor"]) / 2


def fill_price(mid, side, cfg):
    """side 'sell' fills at mid - h, 'buy' at mid + h."""
    h = half_spread(mid, cfg)
    return round_tick(mid - h if side == "sell" else mid + h)


def fees(side, price, qty, cfg):
    f = cfg["fees"]
    notional = price * CONTRACT * qty
    out = {
        "commission": f["commission"] * qty,
        "reg": f["reg_per_contract"] * qty,
        "sec": f["sec_rate"] * notional if side == "sell" else 0.0,
        "cat": f["cat_rate"] * notional,
    }
    out["total"] = sum(out.values())
    return out


def assignment_cost(cfg):
    return cfg["fees"]["assignment_fee"]
