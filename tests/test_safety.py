import re
import socket

import pytest

from conftest import REPO

PROD = ("api.webull.com", "data-api.webull.com", "events-api.webull.com")


def test_network_guard():
    with pytest.raises(RuntimeError, match="network disabled"):
        socket.create_connection(("example.com", 80))


def _files(*parts):
    for part in parts:
        p = REPO / part
        yield from ([p] if p.is_file() else (f for f in p.rglob("*") if f.is_file() and "__pycache__" not in f.parts))


def test_production_hosts_only_in_deny_list():
    for f in _files("ccbot", "config", "scripts", "README.md"):
        for n, line in enumerate(f.read_text(errors="ignore", encoding="utf-8").splitlines(), 1):
            if any(h in line for h in PROD):
                assert f.name == "webull_sandbox.py" and line.startswith("_DENY = "), f"{f}:{n}"


def test_no_committed_secrets():
    pattern = re.compile(r"APP_SECRET\s*=\s*\S+")
    skip = {".git", "work", "logs", ".pytest_cache", "__pycache__", "state"}
    for f in REPO.rglob("*"):
        if f.is_file() and not skip & set(f.relative_to(REPO).parts):
            for line in f.read_text(errors="ignore", encoding="utf-8").splitlines():
                assert not pattern.search(line), f"{f}: {line}"


def test_place_option_appears_once():
    count = sum(f.read_text(encoding="utf-8").count("place_option") for f in _files("ccbot") if f.suffix == ".py")
    assert count == 1


def test_sdk_not_imported_by_package():
    import importlib
    import sys
    for mod in ("ccbot.__main__", "ccbot.broker", "ccbot.broker.webull_sandbox", "ccbot.bot"):
        importlib.import_module(mod)
    assert "webull" not in sys.modules


def test_every_text_file_call_names_utf8():
    """Windows defaults to cp1252, which cannot write the θ in variant labels (VPS run, 2026-10-31).
    Every read_text/write_text in the package and scripts must say encoding="utf-8"."""
    bad = []
    for f in [*REPO.glob("ccbot/**/*.py"), *REPO.glob("scripts/*.py")]:
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r"\.(read_text|write_text)\(", text):
            depth, k = 1, m.end()
            while depth:
                depth += {"(": 1, ")": -1}.get(text[k], 0)
                k += 1
            if 'encoding="utf-8"' not in text[m.end():k]:
                bad.append(f"{f.name}:{text.count(chr(10), 0, m.start()) + 1}")
    assert bad == []
