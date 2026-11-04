"""Broker factory. Imports are lazy so the Webull SDK is never imported unless asked for."""


def make_broker(name, cfg, **kw):
    if name == "sim":
        from .sim import SimBroker
        return SimBroker(cfg, **kw)
    if name in ("webull-sandbox", "webull-paper"):
        from .webull_sandbox import WebullSandboxBroker
        return WebullSandboxBroker(cfg, paper=name == "webull-paper", **kw)
    raise ValueError(f"unknown broker '{name}' (use 'sim', 'webull-sandbox' or 'webull-paper')")
