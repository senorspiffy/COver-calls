"""Expanding-window walk-forward with a held-out tail, plus PBO by CSCV (Bailey et al.).

Selection uses calendar-year returns cut from each config's full-period run. Runs are
path-dependent, so this is an approximation (stated in the report)."""
import itertools
import math

import numpy as np
import pandas as pd


def yearly_returns(equity, start_value):
    last = equity.groupby(equity.index.year).last()
    prev = last.shift(1)
    prev.iloc[0] = start_value
    return last / prev - 1


def monthly_returns(equity, start_value):
    last = equity.groupby(equity.index.to_period("M")).last()
    prev = last.shift(1)
    prev.iloc[0] = start_value
    return last / prev - 1


def folds(years, min_train, holdout):
    """Expanding (train_years, test_year) pairs and the held-out years (never in a fold)."""
    years = sorted(years)
    held = years[len(years) - holdout:] if holdout else []
    usable = years[:len(years) - holdout] if holdout else years
    out = [(usable[:n], usable[n]) for n in range(min_train, len(usable))]
    for train, test in out:
        assert test not in train and not set(train + [test]) & set(held)
    return out, held


def compound(yearly, years):
    return float(np.prod([1 + yearly[y] for y in years]) - 1)


def annualise(total, n_days):
    return (1 + total) ** (252 / n_days) - 1 if n_days else float("nan")


def select(yearly_by_config, train_years):
    """Config with the highest compounded return over train_years only (first wins ties)."""
    scores = {c: compound(y, train_years) for c, y in yearly_by_config.items()}
    return max(scores, key=lambda c: (scores[c], -list(scores).index(c)))


def walk_forward(results, bh, cfg, spread, k):
    """results: {(label, spread, k): Result}. Uses the base spread/k configs."""
    from .variants import REGISTRY, expand

    start = cfg["cash"]
    wf = cfg["walkforward"]
    any_eq = next(iter(results.values())).equity
    days_per_year = any_eq.groupby(any_eq.index.year).size()
    fold_list, held = folds(list(days_per_year.index), wf["min_train_years"], wf["holdout_years"])
    bh_y = yearly_returns(bh, start)
    fold_rows, summary_rows = [], []
    for v in REGISTRY:
        configs = [c.label for c in expand(cfg) if c.id == v.id]
        yearly = {c: yearly_returns(results[(c, spread, k)].equity, start) for c in configs}
        oos = {}
        for train, test in fold_list:
            chosen = select(yearly, train)
            oos[test] = yearly[chosen][test]
            fold_rows.append({"variant": v.id, "train": f"{train[0]}-{train[-1]}", "test": test,
                              "chosen": chosen, "oos_return": yearly[chosen][test], "bh_return": bh_y[test]})
        pre = [y for y in days_per_year.index if y not in held]
        chosen_h = select(yearly, pre) if pre else None   # None: nothing to select on
        years_oos = list(oos)
        n_oos, n_held = int(days_per_year[years_oos].sum()), int(days_per_year[held].sum())
        stitched = annualise(compound(oos, years_oos), n_oos)
        held_r = annualise(compound(yearly[chosen_h], held), n_held) if chosen_h else float("nan")
        bh_held = annualise(compound(bh_y, held), n_held)
        summary_rows.append({"variant": v.id, "oos_years": f"{years_oos[0]}-{years_oos[-1]}" if oos else "-",
                             "oos_cagr": stitched, "bh_oos_cagr": annualise(compound(bh_y, years_oos), n_oos),
                             "heldout_config": chosen_h or "not selected (no train years)",
                             "heldout_years": "-".join(map(str, held)),
                             "heldout_cagr": held_r, "bh_heldout_cagr": bh_held,
                             "heldout_excess": held_r - bh_held})
    matrix = pd.DataFrame({key: monthly_returns(r.equity, start) for key, r in results.items()})
    matrix = matrix[[p.year not in held for p in matrix.index]]
    return {"folds": pd.DataFrame(fold_rows), "summary": pd.DataFrame(summary_rows),
            "holdout": held, "pbo": pbo_cscv(matrix.to_numpy()), "pbo_months": matrix.shape[0],
            "n_configs": matrix.shape[1]}


def pbo_cscv(R, S=8):
    """Probability of backtest overfitting. R: T x N returns (rows = periods)."""
    R = np.asarray(R, dtype=float)
    T, N = R.shape
    if T < S or N < 2 or not np.isfinite(R).all():
        return float("nan")  # too little data: PBO is undefined, never a score (report prints n/a)
    blocks = np.array_split(np.arange(T - T % S), S)
    logits = []
    for is_idx in itertools.combinations(range(S), S // 2):
        is_rows = np.concatenate([blocks[i] for i in is_idx])
        oos_rows = np.concatenate([blocks[i] for i in range(S) if i not in is_idx])
        best = int(np.argmax(R[is_rows].mean(axis=0)))
        ranks = pd.Series(R[oos_rows].mean(axis=0)).rank().to_numpy()
        w = ranks[best] / (N + 1)
        logits.append(math.log(w / (1 - w)))
    return float(np.mean(np.array(logits) <= 0))
