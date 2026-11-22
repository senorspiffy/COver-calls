"""scripts/commit_step.py (item 091, 086 F4, RI-010): a step commit carries only its own item's log lines."""
import importlib.util
import os
import shutil
import subprocess
import sys

import pytest

from conftest import REPO

_spec = importlib.util.spec_from_file_location("commit_step", REPO / "scripts" / "commit_step.py")
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)

NO_GIT = pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
pytestmark = NO_GIT

IDENT = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
         "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
LOG = "logs/implementation/2026-11-21.md"
H = "# Implementation log - 2026-11-21\n\n"
L_HEAD = "09:00 | I2 | 149 | 1 files changed | tests 1 passed in 0.01s"
L150 = "10:00 | I2 | 150 | 1 files changed | tests 1 passed in 0.01s"
L151 = "10:00 | I3 | 151 | PASS | sent to audit: yes"
R05 = "work/150/05-build-report.md"


def _g(repo, *args):
    r = subprocess.run(["git", *args], cwd=repo, env={**os.environ, **IDENT}, capture_output=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.decode("utf-8")


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """HEAD: the log with title, blank and L_HEAD. Working tree: + L151 then L150 (151's line first,
    so the append mutant reorders T2), 150's new 05, and a staged foreign file x.txt."""
    for k, v in IDENT.items():
        monkeypatch.setenv(k, v)
    r = tmp_path / "repo"
    (r / "logs" / "implementation").mkdir(parents=True)
    _g(tmp_path, "init", "-q", "-b", "main", str(r))
    (r / LOG).write_bytes((H + L_HEAD + "\n").encode("utf-8"))
    (r / "README.md").write_text("x\n", encoding="utf-8")
    _g(r, "add", "-A")
    _g(r, "commit", "-q", "-m", "root")
    (r / LOG).write_bytes((H + L_HEAD + "\n" + L151 + "\n" + L150 + "\n").encode("utf-8"))
    (r / "work" / "150").mkdir(parents=True)
    (r / R05).write_text("05\n", encoding="utf-8")
    (r / "work" / "151").mkdir(parents=True)
    (r / "work" / "151" / "06-verification.md").write_text("06\n", encoding="utf-8")
    (r / "x.txt").write_text("foreign\n", encoding="utf-8")
    _g(r, "add", "x.txt")
    monkeypatch.chdir(r)
    return r


def _state(r):
    return _g(r, "rev-parse", "HEAD"), (r / ".git" / "index").read_bytes()


def _cli(r, *args):
    p = subprocess.run([sys.executable, str(REPO / "scripts" / "commit_step.py"), *args], cwd=r,
                       env={**os.environ, **IDENT}, capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout, p.stderr


def test_t1_commits_only_own_line_and_named_path(repo):
    """T1: HEAD gets the 05 and the log with HEAD's lines + L150 only; x.txt stays staged and out of the
    commit; the working log is byte-identical (4 of 5 lines kept: 3 from HEAD + 1 own; L151 dropped)."""
    before = (repo / LOG).read_bytes()
    code, out, err = _cli(repo, "150", f"Item 150: {L150}", R05)
    assert code == 0, err
    head = _g(repo, "rev-parse", "HEAD").strip()
    assert out == f"{head[:7]} Item 150: {L150}\n"
    assert set(_g(repo, "show", "--name-only", "--format=", "HEAD").split()) == {R05, LOG}
    assert _g(repo, "show", f"HEAD:{LOG}") == H + L_HEAD + "\n" + L150 + "\n"
    assert _g(repo, "diff", "--cached", "--name-only").split() == ["x.txt"]
    assert (repo / LOG).read_bytes() == before
    assert _g(repo, "log", "-1", "--format=%s") == f"Item 150: {L150}\n"
    assert not [f for f in os.listdir(repo / ".git") if f.startswith("commit_step-")]   # temp index removed


def test_t2_second_item_keeps_working_order(repo):
    """T2: after T1, 151's commit makes HEAD's log equal the working file (L151 stays before L150)."""
    assert _cli(repo, "150", f"Item 150: {L150}", R05)[0] == 0
    code, _, err = _cli(repo, "151", f"Item 151: {L151}", "work/151/06-verification.md")
    assert code == 0, err
    assert _g(repo, "show", f"HEAD:{LOG}").encode("utf-8") == (repo / LOG).read_bytes()
    assert _g(repo, "diff", "--name-only").split() == []


def _edit_head_line(r):
    (r / LOG).write_bytes((r / LOG).read_bytes().replace(b"| 149 | 1 files", b"| 149 | 2 files"))


@pytest.mark.parametrize("setup, args, why", [
    (_edit_head_line, ("150", f"Item 150: {L150}", R05), f"{LOG}: committed lines changed; nothing committed"),
    (lambda r: (r / LOG).write_bytes((r / LOG).read_bytes() + b"\xff\n"), ("150", f"Item 150: {L150}", R05),
     f"{LOG} unreadable"),
    (None, ("150", "Item 150: wrong", R05), f"subject must be 'Item 150: {L150}'"),
    (lambda r: (r / LOG).write_bytes((r / LOG).read_bytes() + (L150.replace("10:00", "10:01") + "\n").encode("utf-8")),
     ("150", "Item 150: x", R05), "2 log lines of 150 in one commit"),
    (None, ("150", f"Item 150: {L150}", "work/150/missing.md"), "work/150/missing.md not found"),
    (None, ("150", f"Item 150: {L150}", "work/150"), "work/150 is a directory"),
    (None, ("150", f"Item 150: {L150}", R05, LOG), f"{LOG}: log files are found by the helper"),
    (None, ("15", "Item 15: x", R05), "ID '15' is not 3 digits"),
], ids=["edited-head-line", "non-utf8", "wrong-subject", "two-own-lines", "missing-path", "directory",
        "named-log", "bad-id"])
def test_t3_refusals_write_nothing(repo, setup, args, why):
    """T3: each refusal exits 2 with its reason; HEAD and the shared .git/index bytes are unchanged."""
    if setup:
        setup(repo)
    before = _state(repo)
    code, out, err = _cli(repo, *args)
    assert code == 2, (out, err)
    assert why in err, err
    assert _state(repo) == before


@pytest.mark.parametrize("own", [True, False], ids=["with-own-line", "no-own-line"])
def test_t3_absolute_log_path_is_refused(repo, own):
    """T3 (06 F1): the log file named by its absolute path is refused like the relative form, HEAD and
    .git/index unchanged. no-own-line is I3's probe B: the working log gains only 151's line, so a
    whole-file stage would not be overridden by a filtered blob and would carry 151's line."""
    if not own:
        (repo / LOG).write_bytes((H + L_HEAD + "\n" + L151 + "\n").encode("utf-8"))
    before = _state(repo)
    code, out, err = _cli(repo, "150", f"Item 150: {L150}" if own else "Item 150: note", R05, str(repo / LOG))
    assert code == 2, (out, err)
    assert f"{repo / LOG}: log files are found by the helper" in err, err
    assert _state(repo) == before


def test_t3_absolute_named_path_is_committed_relative(repo):
    """T3 (06 F1): a non-log file named by its absolute path is committed under its repo-relative name;
    x.txt stays staged and out of the commit."""
    code, out, err = _cli(repo, "150", f"Item 150: {L150}", str(repo / R05))
    assert code == 0, err
    assert set(_g(repo, "show", "--name-only", "--format=", "HEAD").split()) == {R05, LOG}
    assert _g(repo, "show", f"HEAD:{R05}") == "05\n"
    assert _g(repo, "diff", "--cached", "--name-only").split() == ["x.txt"]


def test_t3_absolute_path_through_symlinked_dir(repo, tmp_path):
    """T3 (06 F1): an absolute path that reaches the repo through a symlinked directory is inside the
    repo top (the parent is resolved), and is committed under its repo-relative name."""
    (tmp_path / "link").symlink_to(repo, target_is_directory=True)
    code, out, err = _cli(repo, "150", f"Item 150: {L150}", str(tmp_path / "link" / R05))
    assert code == 0, err
    assert set(_g(repo, "show", "--name-only", "--format=", "HEAD").split()) == {R05, LOG}


@pytest.mark.parametrize("form", ["absolute", "relative"])
def test_t3_path_outside_repo_is_refused(repo, tmp_path, form):
    """T3 (06 F1): a path outside the repo top, absolute or `../`, is refused; nothing written."""
    (tmp_path / "outside.md").write_text("o\n", encoding="utf-8")
    arg = str(tmp_path / "outside.md") if form == "absolute" else "../outside.md"
    before = _state(repo)
    code, out, err = _cli(repo, "150", f"Item 150: {L150}", R05, arg)
    assert code == 2, (out, err)
    assert f"{arg} is outside the repo top" in err, err
    assert _state(repo) == before


def test_t3_head_moved_is_refused(repo, capsys):
    """T3: `old` is not HEAD (HEAD moved after it was read): update-ref refuses, HEAD unchanged."""
    _g(repo, "commit", "-q", "-m", "x committed")           # HEAD moves past the root
    parent = _g(repo, "rev-parse", "HEAD~1").strip()
    before = _state(repo)
    assert cs.commit("150", f"Item 150: {L150}", [R05], old=parent) == 2
    err = capsys.readouterr().err
    assert f"HEAD moved ({parent[:7]} -> {before[0][:7]}); re-run (item 091)" in err, err
    assert _state(repo) == before


@pytest.mark.parametrize("cmd", ["ls-tree", "cat-file", "read-tree", "write-tree"])
def test_t3_git_failure_is_refused(repo, capsys, cmd):
    """T3: a failing ls-tree / cat-file (or a temp-index command) is `git <cmd> failed`, exit 2."""
    before = _state(repo)
    real = cs.run
    assert cs.commit("150", f"Item 150: {L150}", [R05],
                     run=lambda a, env=None, input=None: (b"", 128) if a[0] == cmd else real(a, env, input)) == 2
    assert f"git {cmd} failed (exit 128); nothing committed (item 091)" in capsys.readouterr().err
    assert _state(repo) == before


def test_t3_no_git_and_not_a_repo(tmp_path, monkeypatch, capsys):
    """T3: git missing (run gives None) and a dir that is not a work tree: exit 2."""
    monkeypatch.chdir(tmp_path)
    assert cs.commit("150", "s", ["a"], run=lambda a, env=None, input=None: None) == 2
    assert "no git (item 091)" in capsys.readouterr().err
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
    assert cs.commit("150", "s", ["a"]) == 2
    assert "not the top of a git work tree" in capsys.readouterr().err


def test_t3_unborn_head(tmp_path, monkeypatch, capsys):
    """T3: a repo with no commit: exit 2, `no HEAD commit`."""
    for k, v in IDENT.items():
        monkeypatch.setenv(k, v)
    _g(tmp_path, "init", "-q", "-b", "main", str(tmp_path / "r"))
    (tmp_path / "r" / "a").write_text("a\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path / "r")
    assert cs.commit("150", "s", ["a"]) == 2
    assert "no HEAD commit (item 091)" in capsys.readouterr().err


def test_t4_new_log_file_is_staged(repo):
    """T4: a log file not in HEAD (ls-tree exit 0, empty) is staged with its title and own line only; a
    new file with no line of this item is not staged."""
    new, research = "logs/implementation/2026-11-22.md", "logs/research/2026-11-22.md"
    (repo / new).write_text(f"# Implementation log - 2026-11-22\n\n{L151}\n{L150}\n", encoding="utf-8")
    (repo / "logs" / "research").mkdir()
    (repo / research).write_text("# Research log - 2026-11-22\n\n10:00 | R1 | 151 | brief written | 0\n",
                                 encoding="utf-8")
    (repo / LOG).write_bytes((H + L_HEAD + "\n" + L151 + "\n").encode("utf-8"))   # no 150 line here
    code, _, err = _cli(repo, "150", f"Item 150: {L150}", R05)
    assert code == 0, err
    assert _g(repo, "show", f"HEAD:{new}") == f"# Implementation log - 2026-11-22\n\n{L150}\n"
    assert set(_g(repo, "show", "--name-only", "--format=", "HEAD").split()) == {R05, new}


def test_t5_reset_failure_exits_1_after_commit(repo, capsys):
    """T5: the commit is made but the shared-index reset fails: exit 1, the message names the sha."""
    old = _g(repo, "rev-parse", "HEAD").strip()
    real = cs.run
    code = cs.commit("150", f"Item 150: {L150}", [R05],
                     run=lambda a, env=None, input=None: (b"", 1) if a[0] == "reset" else real(a, env, input))
    new = _g(repo, "rev-parse", "HEAD").strip()
    assert code == 1 and new != old
    assert f"commit {new[:7]} made; run git reset -q -- {R05} {LOG} (item 091)" in capsys.readouterr().err


def test_filter_log_rule():
    """The filter as a function: HEAD None keeps every non-foreign line; CRLF lines are kept whole."""
    work = (H + L151 + "\r\n" + L150 + "\r\n").encode("utf-8")
    assert cs.filter_log(work, None, "150") == ((H + L150 + "\r\n").encode("utf-8"), [L150])
    with pytest.raises(cs.Refused):
        cs.filter_log(H.encode("utf-8"), (H + L150 + "\n").encode("utf-8"), "150")


def test_filter_log_pattern_inside_other_text():
    """06 F2 (RI-012): the owner is group 4 of a whole-line LOG_LINE match. A 151 line that holds
    `| 150 |` later in its text is 151's (dropped, not 150's); a line that quotes a log line after
    other text (`note: ...`) is no log line (kept, not counted)."""
    inner = "01:05 | I2 | 151 | see 150 | I3 | 150 | x"
    note = "note: 01:06 | I2 | 151 | quoted"
    work = (H + inner + "\n" + note + "\n" + L150 + "\n").encode("utf-8")
    out, own = cs.filter_log(work, H.encode("utf-8"), "150")
    assert out == (H + note + "\n" + L150 + "\n").encode("utf-8")
    assert own == [L150]


# Text pins (item 091 step 6): the run-item sentence and the two agent pointers, once each.
COMMIT_RULE = ("Every commit that carries a logs/research or logs/implementation line, made by the orchestrator, "
               "I2, I3 or A1, is made with `python3 scripts/commit_step.py <ID> \"<subject>\" <paths>...`, never "
               "with `git add` of a logs/research or logs/implementation file, `git add -A`, `git commit -a` or "
               "`git commit <log path>`. The helper does not split two items' edits inside one code file, so "
               "items that change the same file are built (I2-I3) one after another, never in parallel (item 091).")
POINTER = ("Commit with `python3 scripts/commit_step.py <ID> \"<subject>\" <paths>...` (run-item.md, item 091): "
           "it commits only this item's own log lines.")


def test_commit_rule_texts():
    run = (REPO / ".claude" / "commands" / "run-item.md").read_text(encoding="utf-8")
    assert run.count(COMMIT_RULE) == 1
    for f in ("i2-builder.md", "i3-verifier.md"):
        assert (REPO / ".claude" / "agents" / f).read_text(encoding="utf-8").count(POINTER) == 1, f
