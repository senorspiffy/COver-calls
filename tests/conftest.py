"""Every test runs offline: socket connects raise."""
import socket
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SAMPLE = REPO / "data" / "sample"


def _blocked(*args, **kwargs):
    raise RuntimeError("network disabled in tests")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", _blocked)
    monkeypatch.setattr(socket, "getaddrinfo", _blocked)


@pytest.fixture
def cfg():
    from ccbot.config import load_config
    return load_config(REPO / "config" / "default.json")


@pytest.fixture(scope="session")
def runs(synth_a):
    """Every registry variant on SYNTH_A with the shipped config (run once)."""
    from ccbot.backtest import run_backtest
    from ccbot.config import load_config
    from ccbot.variants import REGISTRY
    cfg = load_config(REPO / "config" / "default.json")
    return {v.id: run_backtest(synth_a, v, cfg) for v in REGISTRY}


def head(series, n):
    from dataclasses import replace
    return replace(series, df=series.df.iloc[:n], vol=series.vol.iloc[:n])


@pytest.fixture(scope="session")
def synth_a():
    from ccbot.data import load_prices
    return load_prices(SAMPLE / "SYNTH_A.csv")
