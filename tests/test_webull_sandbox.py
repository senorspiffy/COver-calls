import builtins
import datetime as dt
import sys
from types import SimpleNamespace

import pytest

from ccbot.broker.base import LiveTradingDisabled, OptionOrder
from ccbot.broker.webull_sandbox import SANDBOX_HOST, TokenBucket, WebullSandboxBroker, load_sdk, to_sdk_payload

ENV = {"WEBULL_ENV": "sandbox", "WEBULL_APP_KEY": "k-test", "WEBULL_APP_SECRET": "s-test-value",
       "WEBULL_ACCOUNT_ID": "acct"}


class Resp:
    def __init__(self, body, status=200):
        self.body, self.status_code = body, status

    def json(self):
        return self.body


class FakeSDK:
    """Records endpoint overrides and client construction; never touches the network."""

    def __init__(self, ignore_overrides=False, contracts_error=False):
        self.built, self.calls = [], {"place_option": 0, "preview_option": 0, "snapshot": []}
        sdk = self

        class Resolver:
            def __init__(self):
                self.map = {}

            def resolve(self, req):
                default = {"api": "api.webull.com", "quotes-api": "data-api.webull.com"}[req.api_type]
                return default if ignore_overrides else self.map.get(req.api_type, default)

        class ApiClient:
            def __init__(self, key, secret, region):
                self._endpoint_resolver = Resolver()

            def set_logger(self, logger):
                pass

            def set_token_dir(self, path):
                self.token_dir = path

            def add_endpoint(self, region, host, api_type="api"):
                self._endpoint_resolver.map[api_type] = host

        def order_v2():
            def place_option(account, orders):
                sdk.calls["place_option"] += 1
                return Resp({})

            def preview_option(account, orders):
                sdk.calls["preview_option"] += 1
                return Resp({})
            return SimpleNamespace(place_option=place_option, preview_option=preview_option)

        def list_option_contracts(**kw):
            if contracts_error:
                raise RuntimeError("not supported on sandbox")
            return Resp({"data": [{"symbol": "X261218C00026000"}]})

        def get_option_snapshot(symbols, category):
            sdk.calls["snapshot"].append(len(symbols.split(",")))
            return Resp([])

        def TradeClient(api):
            sdk.built.append("trade")
            return SimpleNamespace(order_v2=order_v2())

        def DataClient(api):
            sdk.built.append("data")
            return SimpleNamespace(instrument=SimpleNamespace(list_option_contracts=list_option_contracts),
                                   option_market_data=SimpleNamespace(get_option_snapshot=get_option_snapshot),
                                   market_data=SimpleNamespace(get_snapshot=lambda *a: Resp([{"price": "24.1"}])))

        self.ApiClient, self.TradeClient, self.DataClient = ApiClient, TradeClient, DataClient
        self.ResolveEndpointRequest = lambda region, api_type: SimpleNamespace(region_id=region, api_type=api_type)


def _broker(tmp_path, cfg, sdk=None, **kw):
    return WebullSandboxBroker(cfg, env=kw.pop("env", ENV), sdk=sdk or FakeSDK(),
                               ledger_path=tmp_path / "ledger.json", token_dir=tmp_path / "tok",
                               limiter=TokenBucket(1000, sleep=lambda s: None), **kw)


def _sell():
    return OptionOrder("X", dt.date(2026, 12, 18), 26.0, "C", "SELL_TO_OPEN", 1, 0.30)


def test_default_is_dry_run_and_sandbox(tmp_path, cfg):
    b = _broker(tmp_path, cfg)
    assert b.dry_run is True
    assert b.api._endpoint_resolver.map["api"] == SANDBOX_HOST
    assert b.get_underlying_quote("X").close == 24.1


def test_live_flag_refused(tmp_path, cfg):
    with pytest.raises(LiveTradingDisabled):
        _broker(tmp_path, cfg, live=True)


@pytest.mark.parametrize("env", [{**ENV, "WEBULL_ENV": "production"}, {k: v for k, v in ENV.items() if k != "WEBULL_ENV"}])
def test_non_sandbox_env_refused(tmp_path, cfg, env):
    with pytest.raises(LiveTradingDisabled):
        _broker(tmp_path, cfg, env=env)


def test_production_host_refused_before_clients_built(tmp_path, cfg):
    sdk = FakeSDK(ignore_overrides=True)
    with pytest.raises(LiveTradingDisabled, match="not the sandbox"):
        _broker(tmp_path, cfg, sdk=sdk)
    assert sdk.built == []


def test_missing_keys_message_has_no_secret(tmp_path, cfg):
    env = {"WEBULL_ENV": "sandbox", "WEBULL_APP_KEY": "k-test"}
    with pytest.raises(ValueError) as e:
        _broker(tmp_path, cfg, env=env)
    assert "WEBULL_APP_SECRET" in str(e.value) and "k-test" not in str(e.value)


def test_dry_run_never_places(tmp_path, cfg):
    sdk = FakeSDK()
    b = _broker(tmp_path, cfg, sdk=sdk)
    b.ledger.state.shares = 100
    assert b.submit(_sell()).status == "DRY_RUN"
    assert sdk.calls["place_option"] == 0 and sdk.calls["preview_option"] == 0
    p = _broker(tmp_path, cfg, sdk=sdk, preview=True)
    p.ledger.state.shares = 100
    assert p.submit(_sell()).status == "DRY_RUN"
    assert sdk.calls["place_option"] == 0 and sdk.calls["preview_option"] == 1


def test_snapshot_chunks_of_20(tmp_path, cfg):
    sdk = FakeSDK()
    b = _broker(tmp_path, cfg, sdk=sdk)
    b.get_option_snapshots([f"X261218C{i:08d}" for i in range(45)])
    assert sdk.calls["snapshot"] == [20, 20, 5]


def test_missing_sdk_message(monkeypatch):
    real = builtins.__import__

    def fake_import(name, *a, **kw):
        if name.startswith("webull"):
            raise ImportError("No module named 'webull'")
        return real(name, *a, **kw)
    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.delitem(sys.modules, "webull", raising=False)
    with pytest.raises(ImportError, match=r"ccbot\[webull\]"):
        load_sdk()


def test_payload_shape():
    p = to_sdk_payload(_sell())
    assert (p["order_type"], p["time_in_force"], p["side"], p["option_strategy"]) == ("LIMIT", "DAY", "SELL", "SINGLE")
    assert len(p["legs"]) == 1 and p["legs"][0]["option_type"] == "CALL" and p["limit_price"] == "0.30"


def test_contract_list_fallback(tmp_path, cfg):
    exp = dt.date(2026, 12, 18)
    ok = _broker(tmp_path, cfg).list_option_contracts("X", exp, exp, 25, 27)
    assert ok == ["X261218C00026000"]
    fb = _broker(tmp_path, cfg, sdk=FakeSDK(contracts_error=True)).list_option_contracts("X", exp, exp, 25, 27)
    assert "X261218C00026000" in fb and "X261218P00025000" in fb


def test_sandbox_day_is_not_earnings_known(tmp_path, cfg):
    """005: the sandbox gives no earnings date, so a stock entry blocks (never 'no earnings')."""
    from ccbot.rules import Market, State, decide_entry
    from ccbot.variants import BY_ID
    b = _broker(tmp_path, cfg)
    b.advance(dt.date(2026, 10, 30))
    day = b.get_underlying_quote("X")
    assert day.asset_type == "stock" and day.next_earnings is None and day.earnings_known is False
    assert b.quotes_have_oi is True    # blank OI from the sandbox is OI_UNKNOWN in the screen

    class Stub(Market):
        def chain(self, day, expiry, kind):
            raise AssertionError("the chain must not be read when earnings are unknown")
    st = State(cash=600.0, ticker="X", shares=100, basis=24.0)
    assert decide_entry(st, day, BY_ID["V0"], cfg, Stub([dt.date(2026, 12, 4)], [])).reason == "EARNINGS_UNKNOWN"


def test_occ_fallback_builds_thursday_symbols(tmp_path, cfg):
    """RI-003 guardrail (007): 2026-06-19 is a holiday, so the June monthly is Thu 06-18."""
    exp = dt.date(2026, 6, 18)
    fb = _broker(tmp_path, cfg, sdk=FakeSDK(contracts_error=True)).list_option_contracts("X", exp, exp, 25, 27)
    assert fb and all("260618" in s for s in fb)
