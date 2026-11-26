"""Stale .pyc survives a mutant run unless both bytecode guards are set (item 107; RI-013 family).

Worked example (03): m.py `X = 1\\n` (6 bytes) is imported once unguarded, so src/__pycache__/m.*.pyc holds X = 1.
The mutant `X = 2\\n` is also 6 bytes and gets the old mtime back with os.utime, so the timestamp pyc still
validates (int(st_mtime) and size match). Unguarded, `-B` only, or PYTHONDONTWRITEBYTECODE=1 only: the stale pyc is
read, test_m passes (exit 0) and `import m` prints 1, a false survivor. With PYTHONDONTWRITEBYTECODE=1 and
PYTHONPYCACHEPREFIX=<new empty dir> the in-tree pyc is ignored: exit 1 (mutant killed), prints 2, nothing written."""
import os
import subprocess
import sys

STRIP = ("PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX", "PYTEST_ADDOPTS", "PYTHONSAFEPATH")


def _env(**extra):
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env.update(extra)
    return env


def _pytest(src, env, *pre):
    return subprocess.run([sys.executable, *pre, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                           f"--rootdir={src}", "test_m.py"], cwd=src, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=120)


def _import_x(src, env):
    r = subprocess.run([sys.executable, "-c", "import m; print(m.X)"], cwd=src, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=120)
    return r.stdout.strip()


def _stale(tmp_path):
    """src/ with a valid pyc for X = 1 and source X = 2 of the same size and mtime."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    m = src / "m.py"
    m.write_text("X = 1\n", encoding="utf-8")
    (src / "test_m.py").write_text("from m import X\ndef test_x():\n    assert X == 1\n", encoding="utf-8")
    st = os.stat(m)
    r = _pytest(src, _env())
    assert r.returncode == 0, r.stdout + r.stderr
    assert list((src / "__pycache__").glob("m.*.pyc")), "setup wrote no src/__pycache__/m.*.pyc (item 107)"
    m.write_text("X = 2\n", encoding="utf-8")
    os.utime(m, ns=(st.st_atime_ns, st.st_mtime_ns))
    now = os.stat(m)
    assert int(now.st_mtime) == int(st.st_mtime), "precondition int(st_mtime) differs (item 107)"
    assert now.st_size == st.st_size == 6, f"precondition size {now.st_size} != {st.st_size} or != 6 (item 107)"
    return src


def test_stale_pyc_survives_without_full_guard(tmp_path):
    """Cases (a) unguarded, (b) `-B` only, (c) PYTHONDONTWRITEBYTECODE=1 only: the stale pyc is read, exit 0."""
    src = _stale(tmp_path)
    r = _pytest(src, _env())
    assert r.returncode == 0, "stale case not reproduced on this Python (item 107)\n" + r.stdout + r.stderr
    assert _import_x(src, _env()) == "1"
    r = _pytest(src, _env(), "-B")
    assert r.returncode == 0, "(b) -B only: " + r.stdout + r.stderr
    r = _pytest(src, _env(PYTHONDONTWRITEBYTECODE="1"))
    assert r.returncode == 0, "(c) PYTHONDONTWRITEBYTECODE=1 only: " + r.stdout + r.stderr


def test_guard_kills_stale_mutant(tmp_path):
    """Case (d): both guards, prefix a new empty sibling of src: exit 1, `import m` prints 2, no file written."""
    src = _stale(tmp_path)
    prefix = tmp_path / "pyc-guard"
    prefix.mkdir()
    env = _env(PYTHONDONTWRITEBYTECODE="1", PYTHONPYCACHEPREFIX=str(prefix))
    r = _pytest(src, env)
    assert r.returncode == 1, "(d) full guard did not kill the mutant (item 107)\n" + r.stdout + r.stderr
    assert _import_x(src, env) == "2"
    assert [p for p in prefix.rglob("*") if p.is_file()] == []
