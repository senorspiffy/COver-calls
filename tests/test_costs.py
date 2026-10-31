import pytest

from ccbot.costs import fees, fill_price, half_spread


def test_spread_drag_matches_001(cfg):
    assert 104 * half_spread(0.50, cfg) * 100 == pytest.approx(260.00)
    one_cent = {**cfg, "spread": {"model": "fixed", "value": 0.01, "floor": 0.01}}
    assert 12 * half_spread(0.50, one_cent) * 100 == pytest.approx(6.00)


def test_fee_lines(cfg):
    sell = fees("sell", 0.47, 1, cfg)
    assert sell["sec"] == pytest.approx(47 * 0.0000206, abs=1e-12) == pytest.approx(0.000968, abs=1e-6)
    assert sell["cat"] == pytest.approx(0.000141, abs=1e-9)
    assert sell["reg"] == pytest.approx(0.10)
    assert sell["commission"] == 0
    assert sell["total"] == pytest.approx(0.10 + 47 * 0.0000206 + 47 * 0.000003)
    assert fees("buy", 0.47, 1, cfg)["sec"] == 0


def test_fill_never_negative(cfg):
    assert fill_price(0.01, "sell", cfg) == 0.0
    assert fill_price(0.50, "buy", cfg) == pytest.approx(0.53)


def test_pct_of_mid_floor(cfg):
    pct = {**cfg, "spread": {"model": "pct_of_mid", "value": 0.10, "floor": 0.01}}
    assert half_spread(0.05, pct) == pytest.approx(0.005)   # 10% of 0.05 < floor
    assert half_spread(2.00, pct) == pytest.approx(0.10)
