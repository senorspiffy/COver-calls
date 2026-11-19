"""scripts/probe_guardrails.py (item 074; RI-002, RI-009, RI-010, RI-012, RI-013).

Every test but the last runs main() on a small committed fixture repo. The real probes
(about 2 minutes) are never run here: scripts/ is not collected (pyproject testpaths)."""
import hashlib
import importlib.util
import shutil
import subprocess
import tempfile

import pytest

from conftest import REPO

_spec = importlib.util.spec_from_file_location("probe_guardrails", REPO / "scripts" / "probe_guardrails.py")
pg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pg)

NO_GIT = pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")

FILES = {
    "pkg/__init__.py": "",
    "pkg/mod.py": "def f():\n    return 1\n# marker\nG = 1\n",
    "pkg/twice.py": "# marker\n# marker\n",
    "tests/test_mod.py": "from pkg import mod\n\n\ndef test_f():\n    assert mod.f() == 1\n\n\n"
                         "def test_g():\n    assert mod.G == 1\n",
    "tests/test_red.py": "def test_ok():\n    assert True\n\n\ndef test_bad():\n    assert False\n",
    "tests/test_slow.py": "import time\n\n\ndef test_sleep():\n    time.sleep(5)\n",
}


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t",
                           "-c", "commit.gpgsign=false", *args],
                          capture_output=True, text=True, encoding="utf-8")


def _fixture(tmp_path):
    """A committed repo with no pyproject and no .gitignore, on purpose (04 Research 1, 4)."""
    root = tmp_path / "repo"
    for name, body in FILES.items():
        f = root / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(body.encode("utf-8"))
    assert _git(root, "init", "-q").returncode == 0
    assert _git(root, "add", ".").returncode == 0
    assert _git(root, "commit", "-q", "-m", "fixture").returncode == 0
    return root


def _probe(pid, **kw):
    p = {"id": pid, "ri": "RI-T", "file": "pkg/mod.py", "anchor": "return 1",
         "replacement": "return 2", "test_file": "tests/test_mod.py",
         "target": "tests/test_mod.py::test_f"}
    p.update(kw)
    return {k: v for k, v in p.items() if v is not None}


def _line(out, pid):
    hits = [ln for ln in out.splitlines() if ln.startswith(pid + " (")]
    assert len(hits) == 1, out
    return hits[0]


def _hashes(root):
    return {str(f.relative_to(root)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted(root.rglob("*")) if f.is_file() and ".git" not in f.relative_to(root).parts}


def _worktrees(root):
    out = _git(root, "worktree", "list", "--porcelain").stdout
    return sum(1 for ln in out.splitlines() if ln.startswith("worktree "))


def _main(root, capsys, probes, *extra):
    code = pg.main(["--repo", str(root), *extra], probes=probes)
    return code, capsys.readouterr().out


@NO_GIT
def test_holds_exits_0(tmp_path, capsys, monkeypatch):
    """(a) plus PYTEST_ADDOPTS dropped (C4) and --rootdir (C1): `-k test_g` would skip test_f."""
    root = _fixture(tmp_path)
    monkeypatch.setenv("PYTEST_ADDOPTS", "-k test_g")
    code, out = _main(root, capsys, [_probe("a", module="pkg.mod", recorded="99 failed")])
    line = _line(out, "a")
    assert "HOLDS" in line and "1 failed, 1 passed, 0 errors" in line, out
    assert "recorded 99 failed" in line
    assert "    FAILED tests.test_mod::test_f" in out
    assert "PYTEST_ADDOPTS ignored" in out
    assert out.splitlines()[0].startswith("ref HEAD = ")
    assert code == 0


@NO_GIT
def test_mixed_run_reports_every_probe(tmp_path, capsys):
    root = _fixture(tmp_path)
    before = _hashes(root)
    probes = [
        _probe("c1", anchor="nosuch", replacement="x"),
        _probe("a", module="pkg.mod"),
        _probe("b", anchor="# marker", replacement="# changed"),
        _probe("b2", anchor="G = 1", replacement="G = 2"),
        _probe("c2", file="pkg/twice.py", anchor="# marker", replacement="# x"),
        _probe("d", replacement="return ("),
        _probe("d2", anchor="# marker", replacement="import nosuchmod_074"),
        _probe("e", target="tests/test_mod.py::test_typo"),
        _probe("f", test_file="tests/test_red.py", target="tests/test_red.py::test_ok"),
        _probe("k", file="pkg/absent.py"),
        _probe("l", test_file="tests/test_nofile.py", target="tests/test_nofile.py::test_x"),
        _probe("i1", module="pkg.nosuch"),
        _probe("i2", module="pkg"),
    ]
    code, out = _main(root, capsys, probes)
    sha = _git(root, "rev-parse", "HEAD").stdout.strip()
    assert "ANCHOR MISSING (count 0)" in _line(out, "c1") and "pytest not run" in _line(out, "c1")
    assert "HOLDS" in _line(out, "a")
    assert "NOT HELD" in _line(out, "b") and "recorded: none" in _line(out, "b")
    assert "code check: n/a" in _line(out, "b")
    assert "NOT HELD" in _line(out, "b2") and "    FAILED tests.test_mod::test_g" in out
    assert "ANCHOR MISSING (count 2)" in _line(out, "c2")
    assert "ERROR (mutation does not compile" in _line(out, "d")
    assert "; ERROR (pytest exit 2);" in _line(out, "d2")
    assert "ERROR (baseline: target not found)" in _line(out, "e")
    assert "ERROR (baseline:" in _line(out, "f") and "1 failed" in _line(out, "f")
    assert f"ANCHOR MISSING (file not in {sha})" in _line(out, "k")
    assert "ERROR (baseline: pytest exit 4)" in _line(out, "l")
    assert "ERROR (code under test is" in _line(out, "i1") and "ModuleNotFoundError" in _line(out, "i1")
    assert "ERROR (code under test is " in _line(out, "i2") and "/pkg/__init__.py)" in _line(out, "i2")
    assert "TOTAL: 13 probes, 1 hold, 2 not held, 3 anchor missing, 7 error" in out
    assert out.count("baseline tests/test_mod.py:") == 1
    assert code == 1
    # (g) the repo is never written and no worktree is left
    assert _hashes(root) == before
    assert _git(root, "status", "--porcelain").stdout == ""
    assert _worktrees(root) == 1


@NO_GIT
def test_timeout(tmp_path, capsys):
    """(h) sleep 5 s against --timeout 1 (C6)."""
    root = _fixture(tmp_path)
    probe = _probe("h", test_file="tests/test_slow.py", target="tests/test_slow.py::test_sleep")
    code, out = _main(root, capsys, [probe], "--timeout", "1")
    assert "ERROR (baseline: timeout 1 s)" in _line(out, "h")
    assert code == 1
    assert _worktrees(root) == 1


@NO_GIT
@pytest.mark.parametrize("case", ["no_git", "bad_ref", "scratch_inside"])
def test_setup_errors_exit_2(tmp_path, capsys, monkeypatch, case):
    root = _fixture(tmp_path)
    extra = []
    if case == "no_git":
        monkeypatch.setattr(pg.shutil, "which", lambda name: None)
        want = "SETUP: git not found"
    elif case == "bad_ref":
        extra = ["--ref", "nosuch"]
        want = "SETUP: ref nosuch not found"
    else:
        (root / "scratch").mkdir()
        monkeypatch.setattr(tempfile, "tempdir", str(root / "scratch"))
        want = "SCRATCH INSIDE REPO"
    code, out = _main(root, capsys, [_probe("a")], *extra)
    assert want in out
    assert "a (" not in out and "TOTAL" not in out
    assert code == 2
    assert _worktrees(root) == 1


def test_classify_missing_or_bad_junit(tmp_path):
    t = "tests/test_mod.py::test_f"
    assert pg.classify(1, tmp_path / "none.xml", t, None)[0] == "ERROR (no junit result)"
    bad = tmp_path / "bad.xml"
    bad.write_bytes(b"not xml")
    assert pg.classify(1, bad, t, None)[0] == "ERROR (no junit result)"
    other = tmp_path / "other.xml"
    other.write_bytes(b'<testsuites><testsuite><testcase classname="tests.test_mod" name="test_g"/>'
                      b"</testsuite></testsuites>")
    assert pg.classify(0, other, t, None)[0] == "ERROR (target not run)"
    err = tmp_path / "err.xml"
    err.write_bytes(b'<testsuites><testsuite><testcase classname="tests.test_mod" name="test_f">'
                    b'<error message="x"/></testcase></testsuite></testsuites>')
    assert pg.classify(1, err, t, None)[0] == "ERROR (1 errors)"
    assert pg.classify(3, other, t, None)[0] == "ERROR (pytest exit 3)"
    assert pg.classify(None, other, t, 7)[0] == "ERROR (timeout 7 s)"
    assert pg.junit_key("tests/test_x.py::test_y[1-a]") == ("tests.test_x", "test_y[1-a]")


@NO_GIT
def test_unrestored_worktree_stops(tmp_path, capsys, monkeypatch):
    root = _fixture(tmp_path)
    monkeypatch.setattr(pg, "worktree_clean", lambda wt: False)
    code, out = _main(root, capsys, [_probe("first"), _probe("second")])
    assert "ERROR (worktree not restored)" in _line(out, "first")
    assert "second (" not in out
    assert "STOPPED: 1 probes not run" in out
    assert code == 1
    assert _worktrees(root) == 1


def test_shipped_probes_well_formed():
    """C12: every shipped anchor occurs once in the working tree and every target def exists."""
    assert len(pg.PROBES) == 3
    assert len({p["id"] for p in pg.PROBES}) == 3
    for p in pg.PROBES:
        assert all(p.get(k) for k in pg.REQUIRED), p["id"]
        text = (REPO / p["file"]).read_bytes().decode("utf-8")
        assert text.count(p["anchor"]) == 1, p["id"]
        name = p["target"].split("::")[-1]
        tests = (REPO / p["test_file"]).read_bytes().decode("utf-8")
        assert f"def {name}(" in tests, p["id"]
    assert [p["target"] for p in pg.PROBES] == [
        "tests/test_realtest.py::test_leading_edge_100_days_blocks",
        "tests/test_realtest.py::test_interior_gap_180_blocks",
        "tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict"]
