import io

import pandas as pd
import pytest

from ccbot import BANNER_MODELLED, BANNER_SYNTHETIC
from ccbot.backtest import metrics
from ccbot.report import backtest_report
from ccbot.variants import run_grid
from ccbot.walkforward import walk_forward


@pytest.fixture(scope="module")
def quick(synth_a):
    from ccbot.config import load_config
    from conftest import REPO
    cfg = load_config(REPO / "config" / "default.json")
    grid, results, bh = run_grid(synth_a, cfg, quick=True)
    wf = walk_forward(results, bh, cfg, cfg["spread"]["value"], cfg["k"])
    return backtest_report(grid, results, wf, metrics(bh, None, cfg), cfg, synth_a.meta, "2026-10-30"), grid


def test_banners_and_fixed_text(quick):
    (md, _), _ = quick
    for text in (BANNER_MODELLED, BANNER_SYNTHETIC, "No variant was selected for live use", "k UNCALIBRATED",
                 "UNVERIFIED fee values: reg_per_contract, assignment_fee", "PBO", "Configs tested: 8"):
        assert text in md


def test_rows_in_registry_order(quick):
    (md, csv), grid = quick
    table = md.split("### spread $0.05, k 1.0")[1].split("\n\n")[0]
    ids = [line.split("|")[1].strip() for line in table.splitlines()[3:]]
    assert ids == ["V0", "V1", "V2", "V3", "V4 θ50", "V4 θ66", "V4 θ80", "V5"]
    for vid in ("V0", "V1", "V2", "V3", "V4", "V5"):
        assert f"| {vid}" in md
    assert len(pd.read_csv(io.StringIO(csv))) == len(grid) == 8


def test_heldout_reported_once(quick):
    (md, _), _ = quick
    assert md.count("### Held-out years (2024, 2025), reported once") == 1
