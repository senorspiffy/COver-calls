"""scripts/check_pipeline.py (items 026, 029; RI-007) and check_handoff.py --all (item 028)."""
import os
import shutil
import subprocess
import sys

import pytest

from conftest import REPO


def _item(root, item, files, scope="FULL", date="2026-10-31", waived=None, a1="A1 result: PASS (test)"):
    d = root / "work" / item
    d.mkdir(parents=True)
    lines = [f"# Work item {item}", f"Scope: {scope}", f"Date: {date}"]
    if waived:
        lines.append(f"Waived: {waived}")
    (d / "request.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for f in files:
        body = f"x\n{a1}\n" if f == "07-audit-task.md" and a1 else "x\n"
        (d / f).write_text(body, encoding="utf-8")


def _run(root, script, *args):
    r = subprocess.run([sys.executable, str(REPO / "scripts" / script), *args], cwd=root,
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


ALL = ["01-research.md", "02-improvements.md", "03-handoff.md", "04-build-plan.md",
       "05-build-report.md", "06-verification.md", "07-audit-task.md"]


def test_build_without_research_is_skipped(tmp_path):
    """The 024 case: request + 05 only."""
    _item(tmp_path, "024", ["05-build-report.md"])
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-10-31")
    assert code == 1
    assert "024: SKIPPED (FULL: missing 01 02 03 04 before 05)" in out


def test_result_before_fact_check_is_skipped(tmp_path):
    """The 023 case: a person-facing result with only R1 done."""
    _item(tmp_path, "023", ["01-research.md", "screen-summary.md"], scope="RESEARCH ONLY")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-10-31")
    assert code == 1
    assert "023: SKIPPED (RESEARCH ONLY: screen-summary.md written before 02 03)" in out


def test_complete_in_progress_and_fast_scope(tmp_path):
    _item(tmp_path, "100", ALL)
    _item(tmp_path, "101", ALL[:3])
    _item(tmp_path, "102", ["01-research.md", "03-handoff.md", "05-build-report.md",
                            "06-verification.md", "07-audit-task.md"], scope="FAST")
    _item(tmp_path, "103", ["01-research.md", "02-improvements.md", "03-handoff.md", "07-audit-task.md"],
          scope="RESEARCH ONLY")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-10-31")
    assert code == 0
    assert "100: complete (FULL)" in out
    assert "101: in progress (FULL: next 04)" in out
    assert "102: complete (FAST)" in out
    assert "103: complete (RESEARCH ONLY)" in out


def test_fast_scope_never_skips_verification(tmp_path):
    _item(tmp_path, "104", ["01-research.md", "03-handoff.md", "05-build-report.md", "07-audit-task.md"],
          scope="FAST")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-10-31")
    assert code == 1 and "104: SKIPPED (FAST: missing 06 before 07)" in out


def test_waived_steps_are_excused_and_printed(tmp_path):
    _item(tmp_path, "105", ["05-build-report.md", "06-verification.md", "07-audit-task.md"],
          waived="01 02 03 04 (person, 2026-10-31: built before 026)")
    _item(tmp_path, "106", ["01-research.md", "03-handoff.md", "04-build-plan.md", "05-build-report.md",
                            "06-verification.md", "07-audit-task.md"], waived="02 (A1, 2026-11-01: no claims)")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-10-31")
    assert code == 0
    assert "105: complete (FULL; Waived: 01 02 03 04 (person, 2026-10-31: built before 026))" in out
    assert "106: complete (FULL; Waived: 02 (A1, 2026-11-01: no claims))" in out


def test_fact_check_and_verification_waivable_only_by_person(tmp_path):
    """Item 031: run-item says R3 and I3 are never skipped; an agent's waiver of 03 or 06 is SKIPPED."""
    _item(tmp_path, "107", ["01-research.md", "02-improvements.md", "04-build-plan.md",
                            "05-build-report.md", "07-audit-task.md"], waived="03 06 (A1, 2026-11-01: test)")
    _item(tmp_path, "108", ALL[:5] + ALL[6:], waived="06 (I3, 2026-11-01: test)")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-10-31")
    assert code == 1
    assert "107: SKIPPED (FULL: 03 06 can be waived only by the person; Waived: 03 06 (A1, 2026-11-01: test))" in out
    assert "108: SKIPPED (FULL: 06 can be waived only by the person;" in out
    assert "SKIPPED: 107, 108" in out


def test_stuck_after_one_day(tmp_path):
    """Item 029: request.md only and a day old → STUCK; opened today → not started."""
    _item(tmp_path, "009", [], date="2026-10-30")
    _item(tmp_path, "025", [], date="2026-10-31")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-10-31")
    assert code == 0
    assert "009: STUCK (FULL, opened 2026-10-30, 1 day(s) with request.md only)" in out
    assert "025: not started (FULL)" in out
    assert "STUCK: 009" in out


def test_check_handoff_all_legacy_and_fail(tmp_path):
    """Item 028: a LEGACY item is not a failure; a new item with the same gaps is."""
    for item in ("002", "031"):
        d = tmp_path / "work" / item
        d.mkdir(parents=True)
        (d / "03-handoff.md").write_text("# 03\n## Fact check\n| a | b |\n|---|---|\n| x | y |\n",
                                         encoding="utf-8")
    code, out = _run(tmp_path, "check_handoff.py", "--all")
    assert code == 1
    assert "002: LEGACY (" in out
    assert "031: FAIL: no Totals line" in out
    assert "FAIL on 031" in out


def test_repo_pipeline_has_no_skipped_items():
    """The real work/ folder: no item may skip a step (RI-007)."""
    code, out = _run(REPO, "check_pipeline.py")
    assert code == 0, out


def test_no_tracked_pycache():
    """Item 030: compiled files are ignored, never committed."""
    files = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True).stdout
    assert [f for f in files.splitlines() if "__pycache__" in f] == []


def test_complete_needs_a1_result(tmp_path):
    """Item 033: every step present but no `A1 result:` line → awaiting A1 (listed, exit 0)."""
    _item(tmp_path, "110", ALL, a1=None)
    _item(tmp_path, "111", ALL)
    _item(tmp_path, "112", ALL, date="2026-10-30", a1=None)
    _item(tmp_path, "017", ALL, date="2026-10-30", a1=None)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-01")
    assert code == 0
    assert "110: awaiting A1 (FULL)" in out
    assert "111: complete (FULL)" in out
    # Item 035: opened before 2026-10-31 but not on the pre-033 list (the 009-016 case)
    assert "112: awaiting A1 (FULL)" in out
    assert "017: complete (FULL)" in out
    assert "AWAITING A1: 110, 112" in out
    assert "OPEN BRANCHES" not in out   # not a git repo: branch scan skipped


def _git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", *args], cwd=cwd, env=env, check=True, capture_output=True)


def _repo_with_open_branch(tmp_path):
    """origin + clone. main: item 040 request only (and a recurring-issues line). Branch
    `fix`, pushed and not merged: 040 fully built, and its own recurring-issues line."""
    origin, repo = tmp_path / "origin.git", tmp_path / "repo"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    _git(tmp_path, "clone", "-q", str(origin), str(repo))
    _git(repo, "checkout", "-q", "-b", "main")
    _item(repo, "040", [], date="2026-10-30")
    (repo / "logs").mkdir()
    (repo / "logs" / "recurring-issues.md").write_text("RI\n", encoding="utf-8")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "main")
    _git(repo, "push", "-q", "origin", "main")
    _git(repo, "checkout", "-q", "-b", "fix")
    for f in ALL:
        (repo / "work" / "040" / f).write_text("x\nA1 result: PASS (test)\n", encoding="utf-8")
    (repo / "logs" / "recurring-issues.md").write_text("RI\nfrom fix\n", encoding="utf-8")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "fix")
    _git(repo, "push", "-q", "origin", "fix")
    _git(repo, "checkout", "-q", "main")
    return repo


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_item_built_on_open_branch_is_in_pr_not_stuck(tmp_path):
    """Item 034 (RI-009): the 2026-11-01 case, 009-016 done in PR #7 but reported STUCK."""
    repo = _repo_with_open_branch(tmp_path)
    code, out = _run(repo, "check_pipeline.py", "--today", "2026-11-02")
    assert code == 0
    assert "040: IN PR (origin/fix has 01 02 03 04 05 06 07; was STUCK here)" in out
    assert "STUCK: none" in out
    assert "IN PR: 040" in out
    assert "  origin/fix: items 040; merges cleanly; edits logs/recurring-issues.md (item 036)" in out


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_open_branch_conflict_is_reported(tmp_path):
    """Item 034: PR #7 conflicted with main and nobody said so."""
    repo = _repo_with_open_branch(tmp_path)
    (repo / "logs" / "recurring-issues.md").write_text("RI\nfrom main\n", encoding="utf-8")
    _git(repo, "commit", "-q", "-am", "daily audit")
    code, out = _run(repo, "check_pipeline.py", "--today", "2026-11-02")
    assert code == 0
    assert "  origin/fix: items 040; CONFLICTS: logs/recurring-issues.md; edits" in out
