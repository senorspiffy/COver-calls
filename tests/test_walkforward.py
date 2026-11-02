import numpy as np
import pandas as pd
import pytest

from ccbot.backtest import Result
from ccbot.variants import expand
from ccbot.walkforward import folds, pbo_cscv, pbo_na_reason, walk_forward


def test_folds_and_holdout():
    years = list(range(2016, 2026))
    fl, held = folds(years, 3, 2)
    assert [t for _, t in fl] == [2019, 2020, 2021, 2022, 2023]
    assert held == [2024, 2025]
    for train, test in fl:
        assert test not in train and not set(train + [test]) & set(held)
        assert train == list(range(2016, test))


def _fake_results(cfg, seed, holdout_seed=None):
    idx = pd.bdate_range("2016-01-04", "2025-12-31")
    out = {}
    for i, v in enumerate(expand(cfg)):
        rng = np.random.default_rng(seed + i)
        r = rng.normal(0.0003, 0.01, len(idx))
        if holdout_seed is not None:
            late = idx.year >= 2024
            r[late] = np.random.default_rng(holdout_seed + i).normal(0.0, 0.03, late.sum())
        eq = pd.Series(cfg["cash"] * np.cumprod(1 + r), index=idx)
        out[(v.label, cfg["spread"]["value"], cfg["k"])] = Result(pd.DataFrame(), eq, {}, {})
    return out, idx


def test_holdout_never_seen_by_selection(cfg):
    a, idx = _fake_results(cfg, 1)
    b, _ = _fake_results(cfg, 1, holdout_seed=99)   # same history, different held-out years
    bh = pd.Series(cfg["cash"] * np.linspace(1, 2, len(idx)), index=idx)
    wa = walk_forward(a, bh, cfg, cfg["spread"]["value"], cfg["k"])
    wb = walk_forward(b, bh, cfg, cfg["spread"]["value"], cfg["k"])
    assert wa["folds"].equals(wb["folds"])
    assert list(wa["summary"]["heldout_config"]) == list(wb["summary"]["heldout_config"])
    assert wa["holdout"] == [2024, 2025] and wa["pbo"] == wb["pbo"]


def test_pbo_noise_is_about_half():
    R = np.random.default_rng(7).normal(size=(96, 20))
    assert pbo_cscv(R) == pytest.approx(0.5, abs=0.15)


def test_pbo_dominant_strategy_is_low():
    R = np.random.default_rng(7).normal(size=(96, 20))
    R[:, 3] += 5
    assert pbo_cscv(R) < 0.1


@pytest.mark.parametrize("T", [0, 1, 7])
def test_pbo_undefined_on_too_few_months(T):
    """Regression guardrail (002, I3 re-verification): with < S=8 periods PBO is NaN, never 0.0."""
    R = np.random.default_rng(3).normal(size=(T, 8))
    assert np.isnan(pbo_cscv(R))
    assert np.isnan(pbo_cscv(np.random.default_rng(3).normal(size=(24, 1))))   # one config: nothing to rank


def test_pbo_na_names_each_cause():
    """009: the n/a text names the condition that failed, one test per cause."""
    rng = np.random.default_rng(5)
    assert pbo_na_reason(rng.normal(size=(24, 4))) is None
    assert pbo_na_reason(rng.normal(size=(7, 4))) == "needs >= 8 non-held-out months, have 7"
    assert pbo_na_reason(rng.normal(size=(24, 1))) == "needs >= 2 configs, have 1"
    R = rng.normal(size=(24, 4))
    R[3, 2] = np.nan
    assert pbo_na_reason(R) == "1 month(s) with a non-finite return"
    assert np.isnan(pbo_cscv(R))
    assert pbo_na_reason(np.full((5, 1), np.nan)) == ("needs >= 8 non-held-out months, have 5; "
                                                     "needs >= 2 configs, have 1; 5 month(s) with a non-finite return")
