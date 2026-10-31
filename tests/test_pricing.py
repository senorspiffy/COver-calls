import math
import random

import pytest

from ccbot.pricing import bs_delta, bs_price, pick_strike, strike_grid


def test_hull_example():
    assert bs_price(42, 40, 0.5, 0.10, 0, 0.20, "C") == pytest.approx(4.76, abs=0.01)
    assert bs_price(42, 40, 0.5, 0.10, 0, 0.20, "P") == pytest.approx(0.81, abs=0.01)


def test_put_call_parity():
    rng = random.Random(1)
    for _ in range(20):
        S, K, T = rng.uniform(5, 50), rng.uniform(5, 50), rng.uniform(0.02, 2)
        r, q, sig = rng.uniform(0, 0.08), rng.uniform(0, 0.05), rng.uniform(0.1, 0.8)
        lhs = bs_price(S, K, T, r, q, sig, "C") - bs_price(S, K, T, r, q, sig, "P")
        assert lhs == pytest.approx(S * math.exp(-q * T) - K * math.exp(-r * T), abs=1e-9)


def test_call_delta_in_unit_interval_and_decreasing():
    deltas = [bs_delta(24, k, 35 / 365, 0.04, 0, 0.25, "C") for k in strike_grid(24)]
    assert all(0 < d < 1 for d in deltas)
    assert all(a > b for a, b in zip(deltas, deltas[1:]))
    assert -1 < bs_delta(24, 25, 35 / 365, 0.04, 0, 0.25, "P") < 0


def test_expiry_gives_intrinsic():
    assert bs_price(30, 25, 0, 0.04, 0, 0.3, "C") == 5
    assert bs_price(20, 25, 0, 0.04, 0, 0.3, "P") == 5
    assert bs_price(20, 25, 0, 0.04, 0, 0.3, "C") == 0
    assert bs_delta(30, 25, 0, 0.04, 0, 0.3, "C") == 1


def test_strike_grid_steps():
    g = strike_grid(24)
    assert all(b - a == pytest.approx(0.5) for a, b in zip(g, g[1:]) if b < 25)
    g30 = [k for k in strike_grid(30) if k >= 25]
    assert g30[0] == 25 and all(b - a == pytest.approx(1.0) for a, b in zip(g30, g30[1:]))
    assert all(k == int(k) for k in g30)


def _chain(S, sigma, dte):
    T = dte / 365
    return [(k, bs_delta(S, k, T, 0.04, 0, sigma, "C")) for k in strike_grid(S)]


def test_pick_strike_in_tolerance():
    k, d = pick_strike(_chain(24, 0.25, 35), 0.275, (0.20, 0.35))
    assert 0.20 <= d <= 0.35 and k > 24


def test_pick_strike_none_when_band_has_no_strike():
    # 7 DTE, low vol, $1 grid at $30: delta jumps past the narrow 0.25-0.30 band
    chain = _chain(30, 0.15, 7)
    assert not any(0.25 <= d <= 0.30 for _, d in chain)
    assert pick_strike(chain, 0.275, (0.25, 0.30)) is None
