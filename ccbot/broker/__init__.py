"""Broker factory. Imports are lazy so the Webull SDK is never imported unless asked for."""


def make_broker(name, cfg, **kw):
    if name == "sim":
        from .sim import SimBroker
        return SimBroker(cfg, **kw)
    if name == "webull-sandbox":
        from .webull_sandbox import WebullSandboxBroker
        return WebullSandboxBroker(cfg, **kw)
    raise ValueError(f"unknown broker '{name}' (use 'sim' or 'webull-sandbox')")
