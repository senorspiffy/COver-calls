"""Black-Scholes-Merton pricer (dividend yield q). T is in years of 365 days."""
import math


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _d1_d2(S, K, T, r, q, sigma):
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    return d1, d1 - sigma * math.sqrt(T)


def bs_price(S, K, T, r, q, sigma, kind):
    """kind 'C' or 'P'. T <= 0 or sigma <= 0 gives intrinsic value."""
    if T <= 0 or sigma <= 0:
        return max(S - K, 0.0) if kind == "C" else max(K - S, 0.0)
    d1, d2 = _d1_d2(S, K, T, r, q, sigma)
    if kind == "C":
        return S * math.exp(-q * T) * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    return K * math.exp(-r * T) * norm_cdf(-d2) - S * math.exp(-q * T) * norm_cdf(-d1)


def bs_delta(S, K, T, r, q, sigma, kind):
    """Call delta in (0, 1), put delta in (-1, 0); {0, 1} / {-1, 0} at T <= 0."""
    if T <= 0 or sigma <= 0:
        if kind == "C":
            return 1.0 if S > K else 0.0
        return -1.0 if S < K else 0.0
    d1, _ = _d1_d2(S, K, T, r, q, sigma)
    if kind == "C":
        return math.exp(-q * T) * norm_cdf(d1)
    return math.exp(-q * T) * (norm_cdf(d1) - 1.0)


def grid_range(lo, hi):
    """Listed-style strikes in [lo, hi]: $0.50 steps below $25, whole dollars at $25+."""
    out = []
    k = math.ceil(lo * 2 - 1e-9) / 2
    while k <= hi + 1e-9:
        if k >= 25 and k != int(k):
            k = float(math.ceil(k))
            continue
        out.append(round(k, 2))
        k += 0.5 if k < 25 else 1.0
    return out


def strike_grid(S, lo_mult=0.7, hi_mult=1.3):
    return grid_range(S * lo_mult, S * hi_mult)


def pick_strike(chain, target, tolerance):
    """chain: iterable of (strike, delta). Returns the (strike, delta) whose |delta|
    is nearest |target|, or None if that |delta| is outside `tolerance`."""
    best = None
    for strike, delta in chain:
        gap = abs(abs(delta) - abs(target))
        if best is None or gap < best[0]:
            best = (gap, strike, delta)
    if best is None:
        return None
    _, strike, delta = best
    lo, hi = tolerance
    return (strike, delta) if lo <= abs(delta) <= hi else None
