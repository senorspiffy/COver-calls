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


def _same_quote_fstrings(source):
    """Lines where a string inside an f-string's {...} uses the f-string's own quote.
    Python 3.12+ allows it (PEP 701); 3.10/3.11 raise SyntaxError (item 027)."""
    import io
    import tokenize
    if not hasattr(tokenize, "FSTRING_START"):   # 3.10/3.11: such a file does not even tokenize
        try:
            list(tokenize.generate_tokens(io.StringIO(source).readline))
            compile(source, "<check>", "exec")
        except (SyntaxError, tokenize.TokenError) as e:
            return [getattr(e, "lineno", 0)]
        return []
    bad, stack = [], []
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.FSTRING_START:
            if stack and len(stack[-1]) == 1 and tok.string.lstrip("rRbBfFuU")[0] == stack[-1]:
                bad.append(tok.start[0])
            stack.append(tok.string.lstrip("rRbBfFuU"))
        elif tok.type == tokenize.FSTRING_END:
            stack.pop()
        elif tok.type == tokenize.STRING and stack and len(stack[-1]) == 1:
            if tok.string.lstrip("rRbBfFuU")[0] == stack[-1]:
                bad.append(tok.start[0])
    return bad


def test_fstrings_parse_on_python_310():
    """pyproject says requires-python >= 3.10: no same-quote strings nested in f-strings (027, RI-008)."""
    bad = []
    for f in [*REPO.glob("ccbot/**/*.py"), *REPO.glob("scripts/*.py"), *REPO.glob("tests/*.py")]:
        bad += [f"{f.name}:{n}" for n in _same_quote_fstrings(f.read_text(encoding="utf-8"))]
    assert bad == []


def test_same_quote_check_catches_the_027_line():
    old = 'print(f"n: {len(u(r.read_text(encoding="utf-8")))}")\n'
    assert _same_quote_fstrings(old) == [1]
    assert _same_quote_fstrings('print(f"n: {len(u(r.read_text(encoding=\'utf-8\')))}")\n') == []
    assert _same_quote_fstrings('x = f"""a {d["k"]} b"""\n') == []
