"""scripts/check_pipeline.py (items 026, 029; RI-007) and check_handoff.py --all (item 028)."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import REPO


AGENTS = {"01": "R1", "02": "R2", "03": "R3", "04": "I1", "05": "I2", "06": "I3"}
# One well-formed field set per agent (item 045, LOG_FORMAT).
FIELDS = {"R1": "brief written | 0", "R2": "3 for / 3 against | languages: N/A",
          "R3": "1 verified, 0 fixed, 0 removed | READY", "I1": "FIT | 1 files planned",
          "I2": "1 files changed | tests 1 passed", "I3": "PASS | sent to audit: yes"}
# Item 076: items before TESTS_FORMAT_FROM (76) keep the old I2 form `<pass>/<total>`.
I2_BEFORE_FIELD = "1 files changed | tests 1/1"


def _field(agent, item):
    """The well-formed log field for this agent and item (item 076: old I2 form below 76)."""
    return I2_BEFORE_FIELD if agent == "I2" and int(item) < 76 else FIELDS[agent]


def _item(root, item, files, scope="FULL", date="2026-10-31", waived=None, a1="A1 result: PASS (test)",
          logged=True, verdict="PASS", sent_back="auto"):
    """A fixture item. Its 06 carries the step-0 line and each step gets its log line (item 043).
    Item 071: 06 starts with `Verdict: <verdict> (round 1)` (none when verdict is None) and
    `Sent back to: <t>` (auto: none on PASS, I2 on FAIL; none when sent_back is None)."""
    if scope == "FAST":
        scope = "FAST (person, 2026-10-31)"
    d = root / "work" / item
    d.mkdir(parents=True)
    lines = [f"# Work item {item}", f"Scope: {scope}", f"Date: {date}"]
    if waived:
        lines.append(f"Waived: {waived}")
    (d / "request.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for f in files:
        body = f"x\n{a1}\n" if f == "07-audit-task.md" and a1 else "x\n"
        if f == "06-verification.md":
            t = {"PASS": "none", "FAIL": "I2"}.get(verdict) if sent_back == "auto" else sent_back
            body = (f"Verdict: {verdict} (round 1)\n" if verdict is not None else "") \
                + (f"Sent back to: {t}\n" if t is not None else "") + body + "Recurring issues checked: RI-007\n"
        (d / f).write_text(body, encoding="utf-8")
        agent = AGENTS.get(f[:2])
        if agent and logged:
            log = root / "logs" / ("research" if agent[0] == "R" else "implementation") / f"{date}.md"
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("a", encoding="utf-8") as fh:
                field = "FAIL | sent to audit: no" if agent == "I3" and verdict == "FAIL" else _field(agent, item)
                fh.write(f"12:00 | {agent} | {item} | {field}\n")


NO_GIT = pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")


def _run(root, script, *args):
    r = subprocess.run([sys.executable, str(REPO / "scripts" / script), *args], cwd=root,
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


def _run_head(root, tmp, script, *args):
    """`_run` on a detached worktree of `root`'s HEAD, so only committed work/ and logs/ are seen
    (item 066). The script itself is still `REPO/scripts` (the working-tree copy)."""
    wt = tmp / "head"
    add = subprocess.run(["git", "worktree", "add", "--detach", "-q", str(wt), "HEAD"], cwd=root,
                         capture_output=True, text=True, encoding="utf-8")
    assert add.returncode == 0, add.stderr
    try:
        return _run(wt, script, *args)
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=root, capture_output=True)


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


@NO_GIT
def test_repo_pipeline_has_no_skipped_items(tmp_path):
    """The committed work/ folder: no item may skip a step (RI-007). Runs on a detached worktree of
    HEAD, so another item's uncommitted step files in this tree don't fail it (item 066); run
    check_pipeline.py in the tree for uncommitted files (run-item.md)."""
    code, out = _run_head(REPO, tmp_path, "check_pipeline.py")
    assert code == 0, out
    assert "RESEARCH CODE: none" in out                 # item 062
    assert "061: complete" in out                      # item 064: 061 stays complete with work/ .py as code
    assert "I3 FAIL: none" in out  # item 071
    assert "UNCOMMITTED STEP: none" in out             # item 077


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


def _root(repo):
    """The fixture's root commit: its own cutoff for the item-053 check (--untracked-from)."""
    return subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"], cwd=repo, capture_output=True,
                          text=True, check=True).stdout.split()[0]


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
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-02")
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
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-02")
    assert code == 0
    assert "  origin/fix: items 040; CONFLICTS: logs/recurring-issues.md; edits" in out


def _branch_adds(repo, branch, item, files, request_text=None, extra=(), bodies=None):
    """Push branch `branch` off main that adds work/<item> with `files` (item 037/038 tests),
    plus the paths in `extra` (item 062). `bodies` {file name: text} replaces a file's default
    body (item 077)."""
    _git(repo, "checkout", "-q", "-b", branch, "main")
    for path in extra:
        _write(repo, path)
    d = repo / "work" / item
    d.mkdir(parents=True, exist_ok=True)
    (d / "request.md").write_text(request_text or f"# Work item {item}\nScope: FULL\nDate: 2026-10-31\n",
                                  encoding="utf-8")
    for f in files:
        (d / f).write_text((bodies or {}).get(f, "x\nA1 result: PASS (test)\n"), encoding="utf-8")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", branch)
    _git(repo, "push", "-q", "origin", branch)
    _git(repo, "checkout", "-q", "main")


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_same_id_on_main_and_open_branch_is_a_clash(tmp_path):
    """Item 037 (RI-009): main's 025 (A1 BUG) and PR #5's 025 (person's IDEA) hid PR #5."""
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "pr5", "050", ["05-build-report.md"], "# Work item 050\nType: IDEA\nScope: FULL\nDate: 2026-10-31\n")
    _item(repo, "050", ALL)                     # main adds its own 050 after the branch left
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "main 050")
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-03")
    assert code == 0
    assert "ID CLASH: 050 (origin/pr5)" in out
    # an item both sides share from the merge base (040 on origin/fix) is not a clash
    assert "040 (origin/fix)" not in out.split("ID CLASH:")[1].splitlines()[0]


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_next_id_counts_open_branches(tmp_path):
    """Item 037: the next ID is above every open branch's items, not only HEAD's."""
    repo = _repo_with_open_branch(tmp_path)
    assert _run(repo, "check_pipeline.py", "--next-id")[1].strip() == "041"
    _branch_adds(repo, "other", "057", [])
    assert _run(repo, "check_pipeline.py", "--next-id")[1].strip() == "058"


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_open_branch_item_that_skips_steps_is_reported(tmp_path):
    """Item 038 (RI-007): PR #5 had request + 05 only and nothing said so."""
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "short", "060", ["05-build-report.md"])
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-03")
    assert code == 0                               # a branch never fails main's check
    assert "BRANCH SKIPPED: 060 (origin/short: FULL: missing 01 02 03 04 before 05)" in out
    assert "BRANCH SKIPPED: 040" not in out        # origin/fix has 01-07 for 040
    assert "SKIPPED: none" in out
    assert "BRANCH FAIL: 060" not in out and "BRANCH FAIL: 040" not in out   # item 077


@NO_GIT
def test_branch_i3_fail_is_listed(tmp_path):
    """Item 077 (BF1): an open-branch item whose 06 is FAIL is listed; the exit code is unchanged."""
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "i3fail", "181", ALL[:6],
                 bodies={"06-verification.md": "Verdict: FAIL (round 1)\nSent back to: I2\nx\n"})
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-03")
    assert ("BRANCH FAIL: 181 (origin/i3fail: I3 FAIL; FULL; sent back to I2, needs a later PASS round in 06 "
            "(item 071))") in out, out
    assert code == 0, out


@NO_GIT
def test_branch_a1_fail_is_listed(tmp_path):
    """Item 077 (BF2): an open-branch item whose last A1 line is FAIL is listed. Its 06 has no
    `Verdict:` line, so it is not an I3 FAIL (an unreadable branch verdict is never a FAIL)."""
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "a1fail", "182", ALL, bodies={"07-audit-task.md": "x\nA1 result: FAIL (test)\n"})
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-03")
    assert "BRANCH FAIL: 182 (origin/a1fail: A1 FAIL; FULL; sent back, needs a later A1 PASS line (item 042))" in out, out
    assert code == 0, out


@NO_GIT
def test_branch_skipped_wins_over_branch_fail(tmp_path):
    """Item 077 (BF3, 03 H2): an A1 FAIL item the 062 merge adds to BRANCH SKIPPED is not listed twice."""
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "rofail", "183", ["01-research.md", "02-improvements.md", "03-handoff.md", "07-audit-task.md"],
                 "# Work item 183\nScope: RESEARCH ONLY\nDate: 2026-10-31\n", extra=("ccbot/x.py",),
                 bodies={"07-audit-task.md": "x\nA1 result: FAIL (test)\n"})
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-03")
    assert "BRANCH SKIPPED: 183 (" in out, out
    assert "BRANCH FAIL: 183" not in out, out


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_open_branch_line_shows_last_commit_age(tmp_path):
    """Item 039: a branch waiting for days stands out."""
    repo = _repo_with_open_branch(tmp_path)
    when = subprocess.run(["git", "log", "-1", "--format=%cs", "origin/fix"], cwd=repo,
                          capture_output=True, text=True).stdout.strip()
    import datetime as dt
    today = dt.date.fromisoformat(when) + dt.timedelta(days=3)
    out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", today.isoformat())[1]
    assert f"(item 036); last commit {when} (3 days)" in out


def test_fast_needs_person_and_date(tmp_path):
    """042: FAST shortens the pipeline only when the person asked, with a date."""
    files = ["01-research.md", "03-handoff.md", "05-build-report.md", "06-verification.md", "07-audit-task.md"]
    _item(tmp_path, "110", files, scope="FAST (I2, 2026-11-04)")
    _item(tmp_path, "111", files, scope="FAST (person, 2026-11-03)")
    d = tmp_path / "work" / "112"
    _item(tmp_path, "112", files)
    (d / "request.md").write_text("# Work item 112\nScope: FAST\nDate: 2026-10-31\n", encoding="utf-8")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-04")
    assert code == 1
    assert "110: SKIPPED (FAST needs (person, <date>)" in out
    assert "112: SKIPPED (FAST needs (person, <date>)" in out
    assert "111: complete (FAST)" in out


def test_a1_fail_is_not_complete(tmp_path):
    """042: the last A1 line decides; FAIL is not complete and exits 1."""
    _item(tmp_path, "120", ALL, a1="A1 result: FAIL (2026-11-04, test)")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-04")
    assert code == 1 and "120: A1 FAIL" in out and "A1 FAIL: 120" in out


def test_later_a1_pass_clears_fail(tmp_path):
    _item(tmp_path, "121", ALL, a1="A1 result: FAIL (2026-11-04, test)\nA1 result: PASS (2026-11-05, re-run)")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-05")
    assert code == 0 and "121: complete (FULL)" in out and "A1 FAIL: none" in out


def test_incomplete_06_and_missing_log_line(tmp_path):
    """043: from 041 on, 06 names the recurring issues checked and every step has a log line."""
    _item(tmp_path, "130", ALL, logged=False)
    _item(tmp_path, "131", ALL)
    (tmp_path / "work" / "131" / "06-verification.md").write_text("Verdict: PASS (round 1)\nSent back to: none\nx\n",
                                                               encoding="utf-8")
    _item(tmp_path, "040", ALL, logged=False)          # before CHECKLIST_FROM: not re-checked
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-04")
    assert code == 1
    assert "130 (no log line for R1 R2 R3 I1 I2 I3)" in out
    assert "131 (06 has no 'Recurring issues checked: RI-...' line)" in out
    assert "040 (" not in out.split("INCOMPLETE:")[1]


def test_complete_item_with_logs_is_not_incomplete(tmp_path):
    _item(tmp_path, "132", ALL)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-04")
    assert code == 0 and "INCOMPLETE: none" in out


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_all_names_branch_with_handoff(tmp_path):
    """044: a hand-off that exists only on an open branch is IN PR, not 'no hand-off'."""
    repo = _repo_with_open_branch(tmp_path)
    _item(repo, "041", [])
    code, out = _run(repo, "check_handoff.py", "--all")
    assert "040: IN PR (origin/fix)" in out
    assert "041: no hand-off" in out


def test_log_writes_utc_line(tmp_path):
    """045: --log stamps the current UTC time and files the line under the agent's team."""
    import datetime as dt
    (tmp_path / "work" / "150").mkdir(parents=True)
    (tmp_path / "work" / "150" / "request.md").write_text("# Work item 150\n", encoding="utf-8")
    before = dt.datetime.now(dt.timezone.utc).replace(second=0, microsecond=0)
    code, out = _run(tmp_path, "check_pipeline.py", "--log", "I2", "150",
                     "2 files changed | tests 9 passed, 1 skipped in 3.21s")
    after = dt.datetime.now(dt.timezone.utc)
    assert code == 0
    logs = list((tmp_path / "logs" / "implementation").glob("*.md"))
    assert len(logs) == 1 and not (tmp_path / "logs" / "research").exists()
    text = logs[0].read_text(encoding="utf-8")
    assert text.startswith("# Implementation log - ")
    line = text.splitlines()[-1]
    stamp = dt.datetime.fromisoformat(f"{logs[0].stem}T{line[:5]}+00:00")
    assert before <= stamp <= after
    assert line[5:] == " | I2 | 150 | 2 files changed | tests 9 passed, 1 skipped in 3.21s"


@pytest.mark.parametrize("agent, fields", [("I2", "see 05"), ("I1", "FIT | see 04"), ("R9", "x"),
                                           ("R1", "brief written | many")])
def test_log_refuses_bad_fields(tmp_path, agent, fields):
    """045: the 2026-11-04 placeholders are refused and nothing is written."""
    code, _ = _run(tmp_path, "check_pipeline.py", "--log", agent, "150", fields)
    assert code == 2 and not (tmp_path / "logs").exists()


def test_log_refuses_item_without_request(tmp_path):
    """047: a well-formed line for an ID with no work/<ID>/request.md is refused, nothing written."""
    (tmp_path / "work" / "999").mkdir(parents=True)   # folder alone is not enough
    code, _ = _run(tmp_path, "check_pipeline.py", "--log", "I2", "999", "1 file changed | tests 1 passed")
    assert code == 2 and not (tmp_path / "logs").exists()


def test_orphan_log_line_is_reported(tmp_path):
    """047: a log line for an item with no work folder is ORPHAN LOG (exit 1); real items are not."""
    _item(tmp_path, "150", ALL)
    with (tmp_path / "logs" / "implementation" / "2026-10-31.md").open("a", encoding="utf-8") as fh:
        fh.write("12:05 | I2 | 999 | 1 file changed | tests 1 passed\n")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-05")
    line = [l for l in out.splitlines() if l.startswith("ORPHAN LOG:")][0]
    assert code == 1
    assert line == "ORPHAN LOG: 999 (logs/implementation/2026-10-31.md)"
    shutil.rmtree(tmp_path / "logs" / "implementation")
    shutil.rmtree(tmp_path / "logs" / "research")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-05")
    assert "ORPHAN LOG: none" in out


def test_malformed_log_line_is_incomplete(tmp_path):
    """045: from 045 on a line must match its agent's format; 041-044's `see 05` is not re-checked."""
    for item in ("150", "044"):
        _item(tmp_path, item, ALL)
        with (tmp_path / "logs" / "implementation" / "2026-10-31.md").open("a", encoding="utf-8") as fh:
            fh.write(f"12:00 | I2 | {item} | see 05 | tests 1/1\n")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-05")
    assert code == 1
    assert "150 (log line for I2 does not match its format (item 045)" in out
    assert "044 (" not in out.split("INCOMPLETE:")[1].splitlines()[0]


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_log_line_after_its_commit_is_flagged(tmp_path):
    """045: the 2026-11-04 case. A line timed 23:10 in a commit made at 22:24:41 UTC is LOG TIME;
    a line in the commit's own minute is fine; items before 045 are not checked."""
    _item(tmp_path, "150", ALL, logged=False)
    log = tmp_path / "logs" / "implementation" / "2026-11-04.md"
    log.parent.mkdir(parents=True)
    log.write_text("22:24 | I1 | 150 | FIT | 1 files planned\n23:10 | I2 | 150 | 1 files changed | tests 1 passed\n"
                   "23:10 | I2 | 044 | see 05 | tests 182/184\n", encoding="utf-8")
    research = tmp_path / "logs" / "research" / "2026-11-04.md"
    research.parent.mkdir(parents=True)
    research.write_text("".join(f"22:00 | {a} | 150 | {FIELDS[a]}\n" for a in ("R1", "R2", "R3")), encoding="utf-8")
    (tmp_path / "logs" / "implementation" / "2026-11-05.md").write_text("09:00 | I3 | 150 | PASS | sent to audit: yes\n",
                                                                    encoding="utf-8")
    env = {**os.environ, "GIT_AUTHOR_DATE": "2026-11-04T22:24:41+00:00",
           "GIT_COMMITTER_DATE": "2026-11-04T22:24:41+00:00"}
    for cmd in (["init", "-q"], ["add", "-A"],
                ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"]):
        subprocess.run(["git", *cmd], cwd=tmp_path, check=True, env=env)
    code, out = _run(tmp_path, "check_pipeline.py", "--untracked-from", _root(tmp_path), "--today", "2026-11-05")
    line = [l for l in out.splitlines() if l.startswith("LOG TIME:")][0]
    assert code == 1
    assert "150 I2 (2026-11-04 23:10 after commit 2026-11-04 22:24 UTC)" in line
    assert "150 I3 (2026-11-05 09:00" in line
    assert "I1" not in line and "044" not in line and "R1" not in line


def test_log_time_not_checked_outside_git(tmp_path):
    _item(tmp_path, "150", ALL)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-05")
    assert code == 0 and "LOG TIME: not checked (no git)" in out
    assert "UNTRACKED CHANGE: not checked (no git)" in out


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_rules_branch_is_reported(tmp_path):
    """049 (RI-010): 048 was built on main while PR #12 changed the logging rules. An open branch
    that changes .claude/, templates/ or the check scripts is named; one that changes only work/
    and logs/ is not."""
    repo = _repo_with_open_branch(tmp_path)
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-02")
    assert "RULES BRANCH: none" in out
    _git(repo, "checkout", "-q", "-b", "rules")
    agent = repo / ".claude" / "agents" / "x.md"
    agent.parent.mkdir(parents=True)
    agent.write_text("new rule\n", encoding="utf-8")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "rules")
    _git(repo, "push", "-q", "origin", "rules")
    _git(repo, "checkout", "-q", "main")
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-02")
    line = [l for l in out.splitlines() if l.startswith("RULES BRANCH:")][0]
    assert line == "RULES BRANCH: origin/rules changes .claude/agents/x.md; build new items on top of it (item 049)"
    assert "origin/fix" not in line


def _commit_all(root, when):
    env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    if not (root / ".git").exists():
        subprocess.run(["git", "init", "-q"], cwd=root, check=True, env=env)
    for cmd in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"]):
        subprocess.run(["git", *cmd], cwd=root, check=True, env=env)


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_log_time_exception_is_named_and_closed(tmp_path):
    """049: the 2026-11-07 case. 048's lines say 20:40, their commit is 20:20. 048 is named with
    its reason, not flagged; the same late line for 150 is still flagged. The list stays {048}."""
    sys.path.insert(0, str(REPO / "scripts"))
    import check_pipeline
    assert set(check_pipeline.LOG_TIME_EXCEPT) == {"048"}
    for item in ("048", "150"):
        _item(tmp_path, item, ALL, date="2026-11-07", logged=False)
        log = tmp_path / "logs" / "implementation" / "2026-11-07.md"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write(f"20:40 | I3 | {item} | PASS | sent to audit: yes\n")
        research = tmp_path / "logs" / "research" / "2026-11-07.md"
        research.parent.mkdir(parents=True, exist_ok=True)
        with research.open("a", encoding="utf-8") as fh:
            fh.write("".join(f"20:00 | {a} | {item} | {FIELDS[a]}\n" for a in ("R1", "R2", "R3")))
        with log.open("a", encoding="utf-8") as fh:
            fh.write("".join(f"20:00 | {a} | {item} | {_field(a, item)}\n" for a in ("I1", "I2")))
    _commit_all(tmp_path, "2026-11-07T20:20:51+00:00")
    code, out = _run(tmp_path, "check_pipeline.py", "--untracked-from", _root(tmp_path), "--today", "2026-11-08")
    line = [l for l in out.splitlines() if l.startswith("LOG TIME:")][0]
    assert code == 1
    assert line.startswith("LOG TIME: 150 I3 (2026-11-07 20:40 after commit 2026-11-07 20:20 UTC)")
    assert "048 I3" not in line
    assert "(not checked: 048: built before 045's --log rule reached main" in line


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_recommitted_log_line_is_checked_against_new_commit(tmp_path):
    """049, known gap (written in the docstring): blame gives a line's latest commit, so a late
    line that is edited in a later commit is no longer flagged."""
    _item(tmp_path, "150", ALL, date="2026-11-07", logged=False)
    log = tmp_path / "logs" / "implementation" / "2026-11-07.md"
    log.parent.mkdir(parents=True)
    log.write_text("20:40 | I2 | 150 | see 05 | tests 1/1\n", encoding="utf-8")
    _commit_all(tmp_path, "2026-11-07T20:20:00+00:00")
    _, out = _run(tmp_path, "check_pipeline.py", "--untracked-from", _root(tmp_path), "--today", "2026-11-08")
    assert "LOG TIME: 150 I2" in out
    log.write_text("20:40 | I2 | 150 | 1 files changed | tests 1 passed\n", encoding="utf-8")
    _commit_all(tmp_path, "2026-11-07T22:00:00+00:00")
    _, out = _run(tmp_path, "check_pipeline.py", "--untracked-from", _root(tmp_path), "--today", "2026-11-08")
    assert "LOG TIME: none" in out


def test_log_hints_match_formats():
    """050: one plain-word hint per agent format, and each hint's example fits its regex."""
    import re
    sys.path.insert(0, str(REPO / "scripts"))
    import check_pipeline
    assert set(check_pipeline.LOG_HINT) == set(check_pipeline.LOG_FORMAT)
    for agent, (_, example) in check_pipeline.LOG_HINT.items():
        assert re.fullmatch(check_pipeline.LOG_FORMAT[agent], example), agent


def test_malformed_log_line_names_expected_format(tmp_path):
    """050: the 2026-11-07 case (048's `see 04` / `see 05`): INCOMPLETE and --log say what they want."""
    _item(tmp_path, "150", ALL)
    with (tmp_path / "logs" / "implementation" / "2026-10-31.md").open("a", encoding="utf-8") as fh:
        fh.write("12:00 | I1 | 150 | FIT | see 04\n12:00 | I2 | 150 | see 05 | tests 1/1\n")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-05")
    assert code == 1
    assert ('150 (log line for I1 I2 does not match its format (item 045): '
            'I1 wants "FIT or FIT WITH CHANGES or NOT A FIT | <n> files planned"; '
            'I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed>")') in out
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "check_pipeline.py"), "--log", "I2", "150", "see 05"],
                       cwd=tmp_path, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 2
    assert r.stderr.strip() == ('--log refused: I2 | 150 | see 05 does not match '
                                '"<n> files changed | tests <last line of python3 -m pytest -q, as printed>"')


# Item 076: the I2 tests field from TESTS_FORMAT_FROM on is pytest's summary line as printed
# (03 Self-check A1-A14 accept, R1-R14 refuse; A1-A3 are the real 072, 074 and 070 lines).
I2_ACCEPT = [
    "411 passed, 1 skipped in 64.87s",                                     # A1
    "453 passed, 1 skipped in 68.26s (0:01:08)",                           # A2
    "1 failed, 383 passed, 1 skipped in 58.86s",                           # A3
    "2 failed in 0.05s",                                                   # A4
    "411 passed, 1 skipped",                                               # A5
    "255 passed, 1 skipped (round 2: test case added)",                    # A6
    "411 passed, 1 skipped, 3 warnings in 60.00s",                         # A7
    "1 passed, 1 warning in 0.10s",                                        # A8
    "1 error in 1.00s",                                                    # A9
    "2 errors in 1.00s",                                                   # A10
    "21 warnings in 1.00s",                                                # A11
    "3 failed, 3 subtests passed in 0.12s",                                # A12
    "1 failed, 1 passed, 2 skipped, 1 xfailed, 1 xpassed in 0.07 seconds",  # A13
    "9 passed, 1 skipped in 3.21s",                                        # A14 (hint example)
    "1 passed",                                                            # FIELDS["I2"]
]
I2_REFUSE = [
    "no tests ran",                                                        # R1
    "411/412",                                                             # R2
    "411 passed, 1 failed",                                                # R3
    "1 skipped, 411 passed",                                               # R4
    "411 passed, 1 skipped, 1 skipped",                                    # R5
    "1 errors",                                                            # R6
    "2 error",                                                             # R7
    "1 warnings",                                                          # R8
    "3 passed, 1 deselected in 0.12s",                                     # R9
    "0 passed",                                                            # R10
    "411 passed,",                                                         # R11
    "411 passed, ",                                                        # R11 (trailing space)
    "411 passed in 64.87s extra",                                          # R12
    "411 passed garbage",                                                  # R13
    "",                                                                    # R14
    "\x1b[32m411 passed\x1b[0m",                                           # colour (PY_COLORS=1)
    "===== 411 passed in 1.00s =====",                                     # padded (PYTEST_ADDOPTS=-v)
    "411 passed1 skipped",                                                 # R15 no `, ` between parts (_END)
    "1 failed1 passed in 1.00s",                                           # R16 same, with timing (_END)
]


def _request(root, item):
    (root / "work" / item).mkdir(parents=True, exist_ok=True)
    (root / "work" / item / "request.md").write_text(f"# Work item {item}\n", encoding="utf-8")


def _log(root, agent, item, fields):
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "check_pipeline.py"), "--log", agent, item, fields],
                       cwd=root, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stderr


@pytest.mark.parametrize("case", I2_ACCEPT)
def test_i2_summary_line_accepted(tmp_path, case):
    """076 T1: from item 076 on, pytest's summary line as printed is accepted and written."""
    _request(tmp_path, "150")
    code, err = _log(tmp_path, "I2", "150", f"1 files changed | tests {case}")
    assert code == 0, err
    text = next((tmp_path / "logs" / "implementation").glob("*.md")).read_text(encoding="utf-8")
    assert text.splitlines()[-1][5:] == f" | I2 | 150 | 1 files changed | tests {case}"


@pytest.mark.parametrize("case", I2_REFUSE)
def test_i2_summary_line_refused(tmp_path, case):
    """076 T2: a line that is not pytest -q's summary line (order, plurals, deselected, colour,
    padding, absent) is refused, exit 2, nothing written."""
    _request(tmp_path, "150")
    code, _ = _log(tmp_path, "I2", "150", f"1 files changed | tests {case}")
    assert code == 2 and not (tmp_path / "logs").exists()


def test_i2_tests_field_cutoff(tmp_path):
    """076 T3: items before 76 keep `<pass>/<total>` with pass <= total; 76 on the summary line.
    --log and INCOMPLETE apply the same rule per item."""
    for item in ("075", "076"):
        _request(tmp_path, item)
    assert _log(tmp_path, "I2", "075", "1 files changed | tests 9/9")[0] == 0
    code, err = _log(tmp_path, "I2", "075", "1 files changed | tests 10/9")
    assert code == 2 and '"<n> files changed | tests <pass>/<total> (pass <= total)"' in err
    code, err = _log(tmp_path, "I2", "076", "1 files changed | tests 9/9")
    assert code == 2 and "as printed" in err
    assert _log(tmp_path, "I2", "076", "1 files changed | tests 9 passed")[0] == 0

    root = tmp_path / "inc"
    for item in ("074", "075", "076", "077"):
        _item(root, item, ALL)
    code, out = _run(root, "check_pipeline.py", "--today", "2026-11-05")
    assert "INCOMPLETE: none" in out, out
    with (root / "logs" / "implementation" / "2026-10-31.md").open("a", encoding="utf-8") as fh:
        fh.write("12:01 | I2 | 075 | 1 files changed | tests 10/9\n12:01 | I2 | 076 | 1 files changed | tests 9/9\n")
    code, out = _run(root, "check_pipeline.py", "--today", "2026-11-05")
    inc = [l for l in out.splitlines() if l.startswith("INCOMPLETE:")][0]
    assert code == 1
    assert "075 (log line for I2" in inc and "076 (log line for I2" in inc, inc
    assert "074 (" not in inc and "077 (" not in inc, inc
    assert 'I2 wants "<n> files changed | tests <pass>/<total> (pass <= total)"' in inc
    assert 'I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed>"' in inc


def test_i2_text_defines_tests_field():
    """076 T4 (RI-010): the i2 text says what the tests field is."""
    text = (REPO / ".claude" / "agents" / "i2-builder.md").read_text(encoding="utf-8")
    assert "python3 -m pytest -q" in text and "as printed" in text and "(item 076)" in text
    assert "<pass>/<total>" not in text


def test_old_i2_hint_fits_old_format():
    """076 T5: the hint for items before 76 has an example that fits I2_BEFORE."""
    import re
    sys.path.insert(0, str(REPO / "scripts"))
    import check_pipeline
    example = check_pipeline.LOG_HINT_BEFORE["I2"][1]
    assert re.fullmatch(check_pipeline.I2_BEFORE, example)
    assert check_pipeline.log_fields_ok("I2", "075", example)
    assert check_pipeline.log_hint("I2", "075") == check_pipeline.LOG_HINT_BEFORE["I2"][0]
    assert check_pipeline.log_hint("I2", "076") == check_pipeline.LOG_HINT["I2"][0]


def test_log_refuses_non_numeric_id_without_crash(tmp_path):
    """076 T6: the ID check runs before log_fields_ok's int(item): a refusal, not a traceback."""
    code, err = _log(tmp_path, "I2", "abc", "1 files changed | tests 1 passed")
    assert code == 2 and "--log refused" in err and "Traceback" not in err
    assert not (tmp_path / "logs").exists()


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_branch_behind_main_says_main_ahead(tmp_path):
    """Item 051: on PR #15's branch after the 11-08 audit, origin/main and a thread branch
    sitting on main were listed as open branches with a false item-036 warning."""
    repo = _repo_with_open_branch(tmp_path)
    _item(repo, "041", [], date="2026-11-09")              # A1's daily commit on main
    (repo / "logs" / "recurring-issues.md").write_text("RI\ndaily\n", encoding="utf-8")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "daily audit")
    _git(repo, "push", "-q", "origin", "main")
    _git(repo, "push", "-q", "origin", "main:mirror")      # a thread branch on main's commit
    _git(repo, "checkout", "-q", "fix")
    out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-09")[1]
    assert "MAIN AHEAD: origin/main has 1 commits not in HEAD; merge it before building (item 051)" in out
    assert "origin/main:" not in out and "origin/mirror:" not in out
    assert "(item 036)" not in out
    assert _run(repo, "check_pipeline.py", "--next-id")[1].strip() == "042"   # main's 041 still counts
    _git(repo, "checkout", "-q", "main")
    out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-09")[1]
    assert "MAIN AHEAD" not in out
    assert "origin/fix: items 040" in out


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_criss_cross_branch_lists_only_its_own_changes(tmp_path, monkeypatch):
    """Item 052 (RI-011): PR #16 was cut from PR #15's branch and merged main; then main merged
    PR #15. Two merge bases, so `HEAD...ref` credited PR #16 with PR #15's items and rule files.
    Commit dates as on 2026-11-07..10: git's `...` then picks main's newer daily commit as the base."""
    repo = _repo_with_open_branch(tmp_path)               # origin/fix carries item 040
    monkeypatch.setenv("GIT_COMMITTER_DATE", "2026-11-07T22:00:00Z")
    _git(repo, "checkout", "-q", "fix")
    (repo / ".claude").mkdir()
    (repo / ".claude" / "rule.md").write_text("rule\n", encoding="utf-8")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "fix: rule change")
    _git(repo, "push", "-q", "origin", "fix")
    _git(repo, "checkout", "-q", "-b", "next")            # built on top of the open PR
    _git(repo, "checkout", "-q", "main")
    monkeypatch.setenv("GIT_COMMITTER_DATE", "2026-11-09T22:16:00Z")
    _item(repo, "041", [], date="2026-11-09")             # A1's daily commit on main
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "daily audit")
    _git(repo, "push", "-q", "origin", "main")
    monkeypatch.setenv("GIT_COMMITTER_DATE", "2026-11-09T22:19:00Z")
    _git(repo, "checkout", "-q", "next")
    _git(repo, "merge", "-q", "--no-edit", "main")
    (repo / "work" / "041" / "01-research.md").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "next: 041")
    _git(repo, "push", "-q", "origin", "next")
    _git(repo, "checkout", "-q", "main")
    monkeypatch.setenv("GIT_COMMITTER_DATE", "2026-11-09T23:34:00Z")
    _git(repo, "merge", "-q", "--no-ff", "--no-edit", "fix")   # the person merges the open PR
    _git(repo, "push", "-q", "origin", "main")
    bases = subprocess.run(["git", "merge-base", "--all", "HEAD", "origin/next"], cwd=repo,
                           capture_output=True, text=True).stdout.split()
    assert len(bases) == 2                                # the criss-cross this test is about
    out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-10")[1]
    assert "origin/next: items 041;" in out
    assert "RULES BRANCH: none" in out
    assert "(item 036)" not in out
    assert "ID CLASH: none" in out


# Item 053 (RI-007): code, config, tests or rules changed outside an open work item.
WHY_053 = (" (item 053: code, config, tests or rules changed with no step file of an open work item;"
           " a follow-up to a completed item is a new item)")


def _write(repo, path, text="x\n"):
    f = repo / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")


def _commit(repo, msg="c"):
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", msg)
    return _commit_sha(repo)


def _history(tmp_path):
    """A plain repo whose first commit is the cutoff: item 150 complete (A1 PASS) and config/x.json."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _item(repo, "150", ALL)
    _write(repo, "config/x.json", "{}\n")
    return repo, _commit(repo, "cutoff")


@NO_GIT
def test_head_run_ignores_uncommitted_item(tmp_path):
    """Item 066: `_run_head` sees committed state only. An uncommitted step file with no log line
    (063's shape) fails the in-tree run but not the HEAD-worktree run; no worktree is left."""
    repo, cutoff = _history(tmp_path)
    _item(repo, "151", ["01-research.md"], date="2026-11-11", logged=False)
    args = ("--today", "2026-11-11", "--untracked-from", cutoff)
    code, out = _run(repo, "check_pipeline.py", *args)
    assert code == 1 and "INCOMPLETE: 151" in out, out          # control: the tree run sees it
    assert "UNCOMMITTED STEP: 151 01-research.md (" in out, out  # item 077
    code, out = _run_head(repo, tmp_path, "check_pipeline.py", *args)
    assert "INCOMPLETE: none" in out, out
    assert "UNCOMMITTED STEP: none" in out, out
    assert code == 0, out
    wl = subprocess.run(["git", "worktree", "list"], cwd=repo, capture_output=True, text=True).stdout
    assert str(tmp_path / "head") not in wl


# Item 077 (RI-010): a step file neither in HEAD nor logged is a cut-off run.
P5A = "UNCOMMITTED STEP: 151 01-research.md (not in HEAD, no R1 log line; a cut-off run? item 077)"


def _uncommitted(repo, cutoff=None):
    args = ("--today", "2026-11-11") + (("--untracked-from", cutoff) if cutoff else ())
    code, out = _run(repo, "check_pipeline.py", *args)
    pick = lambda p: [l for l in out.splitlines() if l.startswith(p)][0]
    return code, out, pick("UNCOMMITTED STEP:"), pick("INCOMPLETE:")


@NO_GIT
def test_uncommitted_unlogged_step_is_listed(tmp_path):
    """P5a: an uncommitted 01 with no R1 line is listed (exit 1)."""
    repo, cutoff = _history(tmp_path)
    _item(repo, "151", ["01-research.md"], logged=False)
    code, out, line, _ = _uncommitted(repo, cutoff)
    assert line == P5A, out
    assert code == 1, out


@NO_GIT
def test_uncommitted_step_with_lookalike_log_lines_is_listed(tmp_path):
    """P5a2 (item 077 round 2, RI-012): log lines holding the agent and ID only inside other text
    (another ID, another agent's column, a field) are not the step's `| R1 | 151 |` line."""
    repo, cutoff = _history(tmp_path)
    _item(repo, "151", ["01-research.md"], logged=False)
    log = repo / "logs" / "research" / "2026-11-11.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("12:00 | R1 | 1510 | x\n12:00 | R2 | 151 | see R1 notes\n12:00 | I2 | 151 | R1 x\n",
                   encoding="utf-8")
    code, out, line, _ = _uncommitted(repo, cutoff)
    assert line == P5A, out
    assert code == 1, out


@NO_GIT
def test_uncommitted_step_without_logs_folder_is_listed(tmp_path):
    """P5b: no logs/ folder means no file is logged; item 040 is below CHECKLIST_FROM, so this check
    alone gives exit 1."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "config/x.json", "{}\n")
    cutoff = _commit(repo, "cutoff")
    _item(repo, "040", ["01-research.md"], logged=False)
    assert not (repo / "logs").exists()
    code, out, line, inc = _uncommitted(repo, cutoff)
    assert line == ("UNCOMMITTED STEP: 040 01-research.md (not in HEAD, no R1 log line; a cut-off run? "
                    "item 077)"), out
    assert inc == "INCOMPLETE: none", out
    assert code == 1, out


@NO_GIT
def test_uncommitted_but_logged_steps_are_quiet(tmp_path):
    """P5c: uncommitted 01-06 that each have their log line are not listed (exit 0)."""
    repo, cutoff = _history(tmp_path)
    _item(repo, "152", ALL[:6])
    code, out, line, inc = _uncommitted(repo, cutoff)
    assert line == "UNCOMMITTED STEP: none" and inc == "INCOMPLETE: none", out
    assert code == 0, out


@NO_GIT
def test_committed_unlogged_step_is_incomplete_not_uncommitted(tmp_path):
    """P5d: a committed step with no log line is 043's INCOMPLETE, not an uncommitted step."""
    repo, cutoff = _history(tmp_path)
    _item(repo, "153", ["01-research.md"], logged=False)
    _commit(repo, "153 R1")
    code, out, line, inc = _uncommitted(repo, cutoff)
    assert inc == "INCOMPLETE: 153 (no log line for R1)", out
    assert line == "UNCOMMITTED STEP: none", out


@NO_GIT
def test_staged_step_is_still_uncommitted(tmp_path):
    """P5e: `git add` is not a commit: HEAD's tree decides, never the index."""
    repo, cutoff = _history(tmp_path)
    _item(repo, "151", ["01-research.md"], logged=False)
    _git(repo, "add", "work/151/01-research.md")
    code, out, line, _ = _uncommitted(repo, cutoff)
    assert line == P5A, out
    assert code == 1, out


@NO_GIT
def test_uncommitted_step_in_shallow_clone(tmp_path):
    """P5f (03 F39): ls-tree HEAD sees the whole tip tree in a shallow clone. The clone's committed
    039 01 has no log line (below CHECKLIST_FROM, so not INCOMPLETE): listed only if ls-tree missed it."""
    repo, cutoff = _history(tmp_path)
    _item(repo, "039", ["01-research.md"], logged=False)
    _commit(repo, "039 R1")
    clone = tmp_path / "clone"
    _git(tmp_path, "clone", "-q", "--depth", "1", f"file://{repo}", str(clone))
    shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=clone,
                             capture_output=True, text=True).stdout.strip()
    assert shallow == "true"
    _item(clone, "152", ALL[:6])
    code, out, line, _ = _uncommitted(clone, cutoff)
    assert line == "UNCOMMITTED STEP: none", out
    assert "UNTRACKED CHANGE: not checked (cutoff " in out, out
    assert code == 0, out
    _item(clone, "151", ["01-research.md"], logged=False)
    code, out, line, _ = _uncommitted(clone, cutoff)
    assert line == P5A, out
    assert code == 1, out


def test_uncommitted_step_without_git(tmp_path):
    """P5g: outside git the check says so, never none."""
    _item(tmp_path, "151", ["01-research.md"], logged=False)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-11")
    assert "UNCOMMITTED STEP: not checked (no git)" in out, out


@NO_GIT
def test_uncommitted_step_ls_tree_failure_fails(tmp_path):
    """P5h: unborn HEAD: ls-tree HEAD fails, which is an error (exit 1), never none (RI-002)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _item(repo, "154", ["01-research.md"])
    code, out, line, _ = _uncommitted(repo)
    assert line == "UNCOMMITTED STEP: git ls-tree HEAD failed (item 077)", out
    assert code == 1, out


def test_a1_text_names_077_lines():
    """Item 077 (RI-010): A1's job B names both new lines, so they have a reader."""
    text = (REPO / ".claude" / "agents" / "a1-auditor.md").read_text(encoding="utf-8")
    assert "`UNCOMMITTED STEP:` entry" in text
    assert "`BRANCH FAIL:` line" in text


def _untracked(repo, cutoff):
    code, out = _run(repo, "check_pipeline.py", "--today", "2026-11-11", "--untracked-from", cutoff)
    return code, [l for l in out.splitlines() if l.startswith("UNTRACKED CHANGE:")][0]


@NO_GIT
def test_completed_item_note_with_config_is_untracked(tmp_path):
    """The 3ba835e shape: a note in a completed item's 05 plus config and test edits."""
    repo, cutoff = _history(tmp_path)
    _write(repo, "work/150/05-build-report.md", "x\n## Follow-up\n")
    _write(repo, "config/x.json", '{"a": 1}\n')
    _write(repo, "tests/t.py")
    c = _commit(repo, "follow-up")
    code, line = _untracked(repo, cutoff)
    assert code == 1
    assert line == (f"UNTRACKED CHANGE: {c[:7]} config/x.json tests/t.py{WHY_053}"
                    f" (cutoff {cutoff[:7]} from --untracked-from)")


@NO_GIT
def test_new_item_step_file_covers_code(tmp_path):
    repo, cutoff = _history(tmp_path)
    _item(repo, "151", ["01-research.md"], date="2026-11-11")
    _write(repo, "ccbot/x.py")
    ok = _commit(repo, "151 R1 + code")
    code, line = _untracked(repo, cutoff)
    assert code == 0 and line == f"UNTRACKED CHANGE: none (cutoff {cutoff[:7]} from --untracked-from)"
    _item(repo, "154", [], date="2026-11-11")                  # request.md alone is not a step file
    _write(repo, "ccbot/z.py")
    bad = _commit(repo, "154 request + code")
    code, line = _untracked(repo, cutoff)
    assert code == 1 and line.startswith(f"UNTRACKED CHANGE: {bad[:7]} ccbot/z.py (item 053")
    assert ok[:7] not in line


@NO_GIT
def test_merge_bringing_untracked_commit_is_flagged(tmp_path):
    repo, cutoff = _history(tmp_path)
    _git(repo, "checkout", "-q", "-b", "side")
    _write(repo, "work/150/05-build-report.md", "x\n## Follow-up\n")
    _write(repo, "config/x.json", '{"a": 1}\n')
    _write(repo, "tests/t.py")
    side = _commit(repo, "follow-up")
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "--no-edit", "side")
    merge = _commit_sha(repo)
    code, line = _untracked(repo, cutoff)
    assert code == 1
    assert line.startswith(f"UNTRACKED CHANGE: {merge[:7]} config/x.json tests/t.py (item 053")
    assert side[:7] not in line


def _commit_sha(repo):
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True,
                          check=True).stdout.strip()


@NO_GIT
def test_cutoff_missing_in_shallow_clone_not_checked(tmp_path):
    repo, cutoff = _history(tmp_path)
    _item(repo, "151", ["01-research.md"], date="2026-11-11")
    _commit(repo, "151 R1")
    clone = tmp_path / "clone"
    _git(tmp_path, "clone", "-q", "--depth", "1", f"file://{repo}", str(clone))
    shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=clone,
                             capture_output=True, text=True).stdout.strip()
    assert shallow == "true"
    code, line = _untracked(clone, cutoff)
    assert code == 0
    assert line == (f"UNTRACKED CHANGE: not checked (cutoff {cutoff[:7]} not in this shallow clone;"
                    f" run git fetch --unshallow) (cutoff {cutoff[:7]} from --untracked-from)")


@NO_GIT
def test_cutoff_missing_in_full_repo_fails(tmp_path):
    repo, _ = _history(tmp_path)
    code, line = _untracked(repo, "0" * 40)
    assert code == 1
    assert line.startswith("UNTRACKED CHANGE: cutoff 0000000 not in HEAD's history (squash/rebase or wrong SHA)")
    _git(repo, "checkout", "-q", "-b", "side")
    _item(repo, "151", ["01-research.md"], date="2026-11-11")
    side = _commit(repo, "side")
    _git(repo, "checkout", "-q", "main")
    code, line = _untracked(repo, side)                        # exists, but not an ancestor of HEAD
    assert code == 1
    assert line.startswith(f"UNTRACKED CHANGE: cutoff {side[:7]} not in HEAD's history")


@NO_GIT
def test_commits_before_cutoff_ignored(tmp_path):
    repo, _ = _history(tmp_path)
    _write(repo, "work/150/05-build-report.md", "x\n## Follow-up\n")
    _write(repo, "config/x.json", '{"a": 1}\n')
    later = _commit(repo, "follow-up, before the cutoff")
    code, line = _untracked(repo, later)
    assert code == 0 and line == f"UNTRACKED CHANGE: none (cutoff {later[:7]} from --untracked-from)"


@NO_GIT
def test_audit_file_never_covers_code(tmp_path):
    repo, cutoff = _history(tmp_path)
    _item(repo, "151", ALL, date="2026-11-11", a1=None)        # awaiting A1, no code
    _commit(repo, "151 built")
    _write(repo, "work/151/07-audit-task.md", "x\nA1 result: PASS (test)\n")
    _write(repo, "ccbot/x.py")
    c = _commit(repo, "A1 PASS + code")
    code, line = _untracked(repo, cutoff)
    assert code == 1 and line.startswith(f"UNTRACKED CHANGE: {c[:7]} ccbot/x.py (item 053")


@NO_GIT
def test_pr_merge_with_a1_pass_on_branch_is_covered(tmp_path):
    """The PR #16/#17 shape: the branch's 07 already has A1 PASS; at main (C^1) 152 is absent."""
    repo, cutoff = _history(tmp_path)
    _git(repo, "checkout", "-q", "-b", "pr")
    _item(repo, "152", ALL, date="2026-11-11")
    _write(repo, "scripts/y.py")
    _commit(repo, "152 + code")
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "--no-edit", "pr")
    code, line = _untracked(repo, cutoff)
    assert code == 0 and line == f"UNTRACKED CHANGE: none (cutoff {cutoff[:7]} from --untracked-from)"


@NO_GIT
def test_a1_fail_item_covers_its_rework(tmp_path):
    repo, cutoff = _history(tmp_path)
    _item(repo, "153", ALL, date="2026-11-11", a1="A1 result: PASS (test)\nA1 result: FAIL (test)")
    _commit(repo, "153 sent back")
    _write(repo, "work/153/05-build-report.md", "x\nrework\n")
    _write(repo, "ccbot/x.py")
    _commit(repo, "153 rework")
    assert _untracked(repo, cutoff)[1] == f"UNTRACKED CHANGE: none (cutoff {cutoff[:7]} from --untracked-from)"
    _write(repo, "work/153/07-audit-task.md", "x\nA1 result: FAIL (test)\nA1 result: PASS (test)\n")
    _commit(repo, "153 passes")
    _write(repo, "work/153/05-build-report.md", "x\nrework\nmore\n")
    _write(repo, "ccbot/x.py", "y\n")
    c = _commit(repo, "after PASS")
    line = _untracked(repo, cutoff)[1]
    assert line.startswith(f"UNTRACKED CHANGE: {c[:7]} ccbot/x.py (item 053")


@NO_GIT
def test_legacy_and_pre_a1_items_never_cover(tmp_path):
    repo, cutoff = _history(tmp_path)
    _write(repo, "work/002/05-build-report.md")                # PRE_A1_LINE
    _write(repo, "config/x.json", '{"a": 1}\n')
    pre = _commit(repo, "002 note + config")
    _write(repo, "work/005/05-build-report.md")                # LEGACY
    _write(repo, "config/x.json", '{"a": 2}\n')
    legacy = _commit(repo, "005 note + config")
    code, line = _untracked(repo, cutoff)
    assert code == 1
    assert line.startswith(f"UNTRACKED CHANGE: {pre[:7]} config/x.json; {legacy[:7]} config/x.json (item 053")


@NO_GIT
def test_rename_out_of_code_path_is_flagged(tmp_path):
    repo, cutoff = _history(tmp_path)
    _item(repo, "151", ["01-research.md"], date="2026-11-11")
    _write(repo, "ccbot/x.py")
    _commit(repo, "151 + code")
    (repo / "attic").mkdir()
    _git(repo, "mv", "ccbot/x.py", "attic/x.py")       # porcelain diff would show only attic/x.py
    c = _commit(repo, "move out")
    code, line = _untracked(repo, cutoff)
    assert code == 1 and line.startswith(f"UNTRACKED CHANGE: {c[:7]} ccbot/x.py (item 053")


def test_untracked_from_is_fixed():
    """053: the cutoff is a fixed commit after 3ba835e and in HEAD's history; never moved forward."""
    sys.path.insert(0, str(REPO / "scripts"))
    import re
    import check_pipeline
    assert check_pipeline.CODE_PATHS == ("ccbot/", "config/", "scripts/", "tests/", ".claude/", "templates/")
    assert re.fullmatch(r"[0-9a-f]{40}", check_pipeline.UNTRACKED_FROM)
    if shutil.which("git") is None:
        return
    shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=REPO,
                             capture_output=True, text=True).stdout.strip()
    if shallow != "false":
        return
    for a, b in (("3ba835e", check_pipeline.UNTRACKED_FROM), (check_pipeline.UNTRACKED_FROM, "HEAD")):
        assert subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=REPO).returncode == 0, (a, b)


# Item 062 (RI-007): a RESEARCH ONLY item that changes code without I1-I3.
RES_160 = "# Work item 160\nScope: RESEARCH ONLY\nDate: 2026-11-13\n"
RES_STEPS = ["01-research.md", "02-improvements.md", "03-handoff.md", "07-audit-task.md"]


def _cp():
    sys.path.insert(0, str(REPO / "scripts"))
    import check_pipeline
    return check_pipeline


@pytest.mark.parametrize("waived, counts", [
    ("Waived: 04 05 06 (person, 2026-11-13: ok)", True),
    ("Waived: 02 04 05 06 (person, 2026-11-13: ok)", True),
    ("Waived: 04 (person, 2026-11-13: x)", False),
    ("Waived: 04 05 06 (I2, 2026-11-13: person said ok)", False),
    ("Waived: 04 05 06 (person: ok)", False),
    ("Waived: 02 (A1, 2026-10-31: x)\nWaived: 04 05 06 (person, 2026-11-13: ok)", False),
    # I3 round 1: the person's bracket copied into another who's text (RI-012)
    ('Waived: 04 05 06 (I2, 2026-11-13: copied "(person, 2026-11-12: ok)")', False),
])
def test_build_waiver_needs_person_date_and_all_three(waived, counts):
    assert _cp()._build_waived(RES_160 + waived + "\n") is counts


def test_research_code_rules():
    rc = _cp()._research_code
    texts = {"160": RES_160, "161": "# Work item 161\nScope: FULL\nDate: 2026-11-13\n",
             "001": "# Work item 001\nScope: RESEARCH ONLY\nDate: 2026-10-29\n",
             "162": RES_160 + "Waived: 04 05 06 (person, 2026-11-13: ok)\n"}
    shape_061 = ["ccbot/x.py", "work/160/01-research.md"]
    flags = rc(shape_061, texts.get)
    assert len(flags) == 1 and flags[0][0] == "160"
    assert flags[0][1].startswith("RESEARCH ONLY: changes ccbot/x.py with no 04-06;")
    assert rc(shape_061 + ["work/161/05-build-report.md"], texts.get) == []          # gap (g)
    assert rc(["ccbot/x.py", "work/161/01-research.md"], texts.get) == []           # FULL, no 04/05
    assert rc(["work/160/01-research.md", "work/160/02-improvements.md"], texts.get) == []
    assert rc(["ccbot/x.py", "work/001/01-research.md"], texts.get) == []           # LEGACY
    assert rc(["ccbot/x.py", "work/162/01-research.md"], texts.get) == []           # person's waiver
    assert rc(shape_061, lambda i: None) == [("160", "RESEARCH ONLY check: no request.md at the tip, item 062")]
    # item 064: a .py under work/<ID>/ is code; look-alike paths are not (RI-012)
    flags = rc(["work/160/diag.py", "work/160/01-research.md"], texts.get)
    assert len(flags) == 1 and flags[0][0] == "160"
    assert flags[0][1].startswith("RESEARCH ONLY: changes work/160/diag.py with no 04-06;")
    assert rc(["work/160/diag.py.md", "work/160/notes.md", "work/160/01-research.md"], texts.get) == []
    assert rc(["work/tmp/x.py", "work/.gitkeep", "work/160/01-research.md"], texts.get) == []
    assert rc(["work/160/diag.py", "work/160/01-research.md"], lambda i: None) == [
        ("160", "RESEARCH ONLY check: no request.md at the tip, item 062")]


def _research(repo, cutoff):
    code, out = _run(repo, "check_pipeline.py", "--today", "2026-11-13", "--untracked-from", cutoff)
    return code, out, [l for l in out.splitlines() if l.startswith("RESEARCH CODE:")][0]


@NO_GIT
def test_research_only_branch_with_code_is_branch_skipped(tmp_path):
    """The 061 shape (PR #26): RESEARCH ONLY 01 02 03 07 plus ccbot/ code on an open branch."""
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "res", "160", RES_STEPS, RES_160, extra=["ccbot/x.py"])
    code, out, _ = _research(repo, _root(repo))
    assert code == 0                                   # a branch never fails main's check (038)
    assert "BRANCH SKIPPED: 160 (origin/res: RESEARCH ONLY: changes ccbot/x.py" in out
    assert "SKIPPED: none" in out


@NO_GIT
def test_research_only_branch_waiver_needs_the_person(tmp_path):
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "ok", "160", RES_STEPS, RES_160 + "Waived: 04 05 06 (person, 2026-11-13: ok)\n",
                 extra=["ccbot/x.py"])
    _branch_adds(repo, "bad", "161", RES_STEPS,
                 RES_160.replace("160", "161") + "Waived: 04 05 06 (I2, 2026-11-13: person said ok)\n",
                 extra=["ccbot/y.py"])
    code, out, _ = _research(repo, _root(repo))
    assert code == 0
    assert "BRANCH SKIPPED: 160" not in out
    line = [l for l in out.splitlines() if l.startswith("BRANCH SKIPPED: 161 ")]
    assert len(line) == 1
    assert "can be waived only by the person" in line[0]
    assert "RESEARCH ONLY: changes ccbot/y.py" in line[0]


@NO_GIT
def test_research_only_head_commit_with_code_is_skipped(tmp_path):
    repo, cutoff = _history(tmp_path)
    _item(repo, "160", ["01-research.md"], scope="RESEARCH ONLY", date="2026-11-11")
    _write(repo, "ccbot/x.py")
    c = _commit(repo, "160 R1 + code")
    code, out, line = _research(repo, cutoff)
    assert code == 1
    assert f"160: SKIPPED ({c[:7]} RESEARCH ONLY: changes ccbot/x.py" in out
    assert len([l for l in out.splitlines() if l.startswith("160:")]) == 1
    assert line == "RESEARCH CODE: 160"
    assert "UNTRACKED CHANGE: none" in out


@NO_GIT
def test_research_only_work_files_only_not_flagged(tmp_path):
    repo, cutoff = _history(tmp_path)
    _item(repo, "160", ["01-research.md"], scope="RESEARCH ONLY", date="2026-11-11")
    _commit(repo, "160 R1")
    code, out, line = _research(repo, cutoff)
    assert line == "RESEARCH CODE: none" and code == 0, out


@NO_GIT
def test_full_item_build_in_same_commit_covers_research_code(tmp_path):
    """Gap (g) pinned: a FULL item's 05 in the same unit covers the code."""
    repo, cutoff = _history(tmp_path)
    _item(repo, "160", ["01-research.md"], scope="RESEARCH ONLY", date="2026-11-11")
    _item(repo, "161", ALL[:5], date="2026-11-11")
    _write(repo, "ccbot/x.py")
    _commit(repo, "160 R1 + 161 built + code")
    code, out, line = _research(repo, cutoff)
    assert line == "RESEARCH CODE: none"
    assert "160: SKIPPED" not in out


@NO_GIT
def test_second_waived_line_is_not_read(tmp_path):
    """Gap (j): the 023 shape, two Waived lines; only the first counts."""
    repo, cutoff = _history(tmp_path)
    _item(repo, "160", ["01-research.md"], scope="RESEARCH ONLY", date="2026-11-11",
          waived="02 (A1, 2026-10-31: x)\nWaived: 04 05 06 (person, 2026-11-13: ok)")
    _write(repo, "ccbot/x.py")
    _commit(repo, "160 + code")
    code, out, line = _research(repo, cutoff)
    assert code == 1 and line == "RESEARCH CODE: 160"


@NO_GIT
def test_rescoped_to_full_is_not_research_but_still_skipped(tmp_path):
    repo, cutoff = _history(tmp_path)
    _item(repo, "160", RES_STEPS, date="2026-11-11")
    _write(repo, "ccbot/x.py")
    _commit(repo, "160 FULL + code")
    code, out, line = _research(repo, cutoff)
    assert line == "RESEARCH CODE: none"
    assert "160: SKIPPED (FULL: missing 04 05 06 before 07" in out
    assert code == 1


@NO_GIT
def test_legacy_research_item_with_code_not_flagged(tmp_path):
    repo, cutoff = _history(tmp_path)
    _item(repo, "001", ["01-research.md"], scope="RESEARCH ONLY", date="2026-11-11")
    _write(repo, "ccbot/x.py")
    _commit(repo, "001 + code")
    code, out, line = _research(repo, cutoff)
    assert line == "RESEARCH CODE: none"
    assert "001: LEGACY" in out


def test_research_code_without_git(tmp_path):
    _item(tmp_path, "160", ["01-research.md"], scope="RESEARCH ONLY", date="2026-11-13")
    _write(tmp_path, "ccbot/x.py")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-13")
    assert code == 0
    assert "RESEARCH CODE: not checked (no git)" in out


@NO_GIT
def test_research_code_cutoff_missing_not_checked(tmp_path):
    repo, _ = _history(tmp_path)
    code, out, line = _research(repo, "0" * 40)
    assert code == 1                                   # from UNTRACKED CHANGE (053), not twice
    assert line == "RESEARCH CODE: not checked (see UNTRACKED CHANGE)"


# Item 064 (RI-007): a .py file under work/<ID>/ is code for 053 and 062.
@pytest.mark.parametrize("path, hit", [
    ("work/061/diag_keep.py", True),
    ("work/160/sub/x.py", True),
    ("work/160/diag.py.md", False),
    ("work/.gitkeep", False),
    ("work/tmp/x.py", False),
    ("work/160/01-research.md", False),
    ("work/1600/x.py", False),
    ("work/160/x.pyc", False),
])
def test_work_code_pattern(path, hit):
    cp = _cp()
    assert (cp.WORK_CODE.fullmatch(path) is not None) is hit
    assert cp._is_code(path, cp.CODE_PATHS) is hit


def test_is_code_examples():
    """Item 066: fixed `_is_code` examples, checked once instead of in every pattern case."""
    cp = _cp()
    assert cp._is_code("work/160/diag.py", cp.RESEARCH_CODE_PATHS) is True
    assert cp._is_code("ccbot/x.py", cp.RESEARCH_CODE_PATHS) is True
    assert cp._is_code("work/160/notes.md", cp.CODE_PATHS) is False


def test_work_code_counts_repo_diagnostics():
    """Feasibility pin (RI-001): the real work/ folder holds at least 061's diagnostic (1 of 484
    paths on 2026-11-14, item 064 03). No exact count, so a new diagnostic doesn't break it."""
    cp = _cp()
    paths = [f.relative_to(REPO).as_posix() for f in (REPO / "work").rglob("*") if f.is_file()]
    hits = [p for p in paths if cp.WORK_CODE.fullmatch(p)]
    assert "work/061/diag_keep.py" in hits
    assert not [p for p in hits if p.endswith(".md")]


@NO_GIT
def test_research_only_work_py_is_research_code(tmp_path):
    """Fixture (a): the 061 shape with the code under work/<ID>/ instead of ccbot/."""
    repo, cutoff = _history(tmp_path)
    _item(repo, "160", ["01-research.md"], scope="RESEARCH ONLY", date="2026-11-11")
    _write(repo, "work/160/diag.py")
    c = _commit(repo, "160 R1 + diagnostic")
    code, out, line = _research(repo, cutoff)
    assert code == 1
    assert f"160: SKIPPED ({c[:7]} RESEARCH ONLY: changes work/160/diag.py" in out
    assert len([l for l in out.splitlines() if l.startswith("160:")]) == 1
    assert "written before" not in out                 # the 062 detail replaces classify's (C3)
    assert line == "RESEARCH CODE: 160"
    assert "UNTRACKED CHANGE: none" in out


@NO_GIT
def test_py_added_to_completed_item_is_untracked(tmp_path):
    """Fixture (b): a diagnostic added to a completed item's folder is a follow-up with no item."""
    repo, cutoff = _history(tmp_path)
    _write(repo, "work/150/x.py")
    c = _commit(repo, "150 diagnostic")
    code, line = _untracked(repo, cutoff)
    assert code == 1
    assert line == f"UNTRACKED CHANGE: {c[:7]} work/150/x.py{WHY_053} (cutoff {cutoff[:7]} from --untracked-from)"


@NO_GIT
def test_open_full_item_covers_its_work_py(tmp_path):
    """Fixture (c): an open FULL item's step files cover its own diagnostic."""
    repo, cutoff = _history(tmp_path)
    _item(repo, "170", ALL[:5], date="2026-11-11")
    _write(repo, "work/170/diag.py")
    _commit(repo, "170 built + diagnostic")
    code, out, line = _research(repo, cutoff)
    assert code == 0, out
    assert f"UNTRACKED CHANGE: none (cutoff {cutoff[:7]} from --untracked-from)" in out
    assert line == "RESEARCH CODE: none"
    assert "170: SKIPPED" not in out


@NO_GIT
def test_failed_diff_tree_is_an_entry_not_none(tmp_path, monkeypatch):
    """A failed diff-tree is 053's entry, never "none"; 062 does not report it twice."""
    cp = _cp()
    repo, cutoff = _history(tmp_path)
    monkeypatch.chdir(repo)
    walked = ([("ab" * 20, None)], None)
    text, failed = cp.untracked_changes(cutoff, walked)
    assert text.startswith("abababa (git diff-tree failed) (item 053:")
    assert failed is True
    assert cp.research_code(cutoff, walked)[0] == "not checked (see UNTRACKED CHANGE)"   # item 079
    assert cp.research_code(cutoff, ([("ab" * 20, ["ccbot/x.py"])], None))[0] == "none"   # 2-tuple (C2)


# Item 079 (RI-014): a shallow boundary on or below the walk gives "not checked", never an entry.
def _shallow(repo, *shas):
    """Write `shas` as the shallow file of `repo` (in its --git-common-dir) and check git sees it."""
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=repo, capture_output=True,
                            text=True, check=True).stdout.strip()
    (Path(repo) / common / "shallow").write_text("".join(s + "\n" for s in shas), encoding="utf-8")
    flag = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=repo, capture_output=True,
                          text=True, check=True).stdout.strip()
    assert flag == "true"


def _unshallow(repo):
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=repo, capture_output=True,
                            text=True, check=True).stdout.strip()
    (Path(repo) / common / "shallow").unlink()


def _graph(tmp_path, shape):
    """Fixture graphs on `_history` (C = cutoff); non-code files under notes/. Returns (repo, C, {name: sha}).
    a: C -> P -> B on main, D (parent C) on side, M = merge(B, D).
    b: C -> T on main, C -> Q -> B2 on side, M = merge(T, B2)."""
    repo, c = _history(tmp_path)
    sha = {"C": c}
    if shape == "a":
        _write(repo, "notes/p.md"); sha["P"] = _commit(repo, "P")
        _write(repo, "notes/b.md"); sha["B"] = _commit(repo, "B")
        _git(repo, "checkout", "-q", "-b", "side", c)
        _write(repo, "notes/d.md"); sha["D"] = _commit(repo, "D")
        _git(repo, "checkout", "-q", "main")
        _git(repo, "merge", "-q", "--no-ff", "--no-edit", "side")
    else:
        _write(repo, "notes/t.md"); sha["T"] = _commit(repo, "T")
        _git(repo, "checkout", "-q", "-b", "side", c)
        _write(repo, "notes/q.md"); sha["Q"] = _commit(repo, "Q")
        _write(repo, "notes/b2.md"); sha["B2"] = _commit(repo, "B2")
        _git(repo, "checkout", "-q", "main")
        _git(repo, "merge", "-q", "--no-ff", "--no-edit", "side")
    sha["M"] = _commit_sha(repo)
    return repo, c, sha


def _lines(repo, cutoff, cwd=None):
    code, out = _run(cwd or repo, "check_pipeline.py", "--today", "2026-11-11", "--untracked-from", cutoff)
    pick = lambda p: [l for l in out.splitlines() if l.startswith(p)][0]
    return code, out, pick("UNTRACKED CHANGE:"), pick("RESEARCH CODE:"), pick("REAL-DATA FIELD:")


def _shallow_text(b, cutoff):
    return (f"UNTRACKED CHANGE: not checked (shallow boundary {b[:7]}; run git fetch --unshallow)"
            f" (cutoff {cutoff[:7]} from --untracked-from)")


@NO_GIT
def test_shallow_boundary_inside_walk_not_checked(tmp_path):
    """(a) S n R = {B}: P is hidden behind B, so the answer is not checked, never none or an entry."""
    repo, c, sha = _graph(tmp_path, "a")
    _shallow(repo, sha["B"])
    code, out, untracked, research, real = _lines(repo, c)
    assert untracked == _shallow_text(sha["B"], c), out
    assert research == "RESEARCH CODE: not checked (see UNTRACKED CHANGE)", out
    assert real == "REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)", out
    assert code == 0, out
    _unshallow(repo)                                            # control: the full answer
    code, out, untracked, _, _ = _lines(repo, c)
    assert untracked == f"UNTRACKED CHANGE: none (cutoff {c[:7]} from --untracked-from)", out


@NO_GIT
def test_shallow_boundary_on_second_parent_not_checked(tmp_path):
    """(b) B2 is off the first-parent walk: only the whole-range check (cutoff..HEAD) sees it."""
    repo, c, sha = _graph(tmp_path, "b")
    _shallow(repo, sha["B2"])
    code, out, untracked, _, _ = _lines(repo, c)
    assert untracked == _shallow_text(sha["B2"], c), out
    assert code == 0, out


@NO_GIT
def test_full_clone_same_graph_unchanged(tmp_path):
    """(c1) graph (a) with no shallow file: today's answer."""
    repo, c, _ = _graph(tmp_path, "a")
    code, out, untracked, research, _ = _lines(repo, c)
    assert untracked == f"UNTRACKED CHANGE: none (cutoff {c[:7]} from --untracked-from)", out
    assert research == "RESEARCH CODE: none", out
    assert code == 0, out


@NO_GIT
def test_unrelated_root_in_full_clone_stays_loud(tmp_path):
    """(c2) a real root U after the cutoff in a full clone stays a 053 entry (exit 1)."""
    repo, c = _history(tmp_path)
    _git(repo, "checkout", "-q", "--orphan", "u")
    _git(repo, "rm", "-rq", "--cached", ".")
    shutil.rmtree(repo / "work"); shutil.rmtree(repo / "config")
    _write(repo, "notes/u.md"); u = _commit(repo, "U")
    _git(repo, "merge", "-q", "--allow-unrelated-histories", "--no-edit", "main")
    m = _commit_sha(repo)
    _git(repo, "branch", "-f", "main", "u")
    _git(repo, "checkout", "-q", "main")
    assert _commit_sha(repo) == m
    flag = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=repo, capture_output=True,
                          text=True).stdout.strip()
    assert flag == "false"
    code, out, untracked, _, _ = _lines(repo, c)
    assert f"{u[:7]} (git diff-tree failed)" in untracked, out
    assert code == 1, out


def _below_graph(tmp_path):
    """(d) Z (root) -> Y (scripts/y.py) -> b' -> C (cutoff) -> T; M = merge --no-ff of T into a
    branch at Y, so M's first parent is Y. Returns (repo, C, {name: sha})."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    sha = {}
    _write(repo, "notes/z.md"); sha["Z"] = _commit(repo, "Z")
    _write(repo, "scripts/y.py"); sha["Y"] = _commit(repo, "Y")
    _write(repo, "notes/b.md"); sha["b"] = _commit(repo, "b'")
    _item(repo, "150", ALL)
    _write(repo, "config/x.json", "{}\n")
    sha["C"] = _commit(repo, "cutoff")
    _write(repo, "notes/t.md"); sha["T"] = _commit(repo, "T")
    _git(repo, "checkout", "-q", "-b", "m", sha["Y"])
    _git(repo, "merge", "-q", "--no-ff", "--no-edit", "main")
    sha["M"] = _commit_sha(repo)
    _git(repo, "branch", "-f", "main", "m")
    _git(repo, "checkout", "-q", "main")
    return repo, sha["C"], sha


@NO_GIT
def test_shallow_boundary_below_cutoff_entries_unconfirmed(tmp_path):
    """(d) S n R = 0 of 1, b' below the cutoff: the shallow walk finds Y and Z (2 entries) that a
    full clone never walks, so they are unconfirmed; the full view gives none."""
    repo, c, sha = _below_graph(tmp_path)
    _shallow(repo, sha["b"])
    code, out, untracked, research, _ = _lines(repo, c)
    assert untracked == (f"UNTRACKED CHANGE: not checked (shallow boundary {sha['b'][:7]} below the cutoff;"
                         f" 2 unconfirmed entries; run git fetch --unshallow) (cutoff {c[:7]} from --untracked-from)"), out
    assert research == "RESEARCH CODE: not checked (see UNTRACKED CHANGE)", out
    assert code == 0, out
    _unshallow(repo)                                            # control: the full answer
    code, out, untracked, _, _ = _lines(repo, c)
    assert untracked == f"UNTRACKED CHANGE: none (cutoff {c[:7]} from --untracked-from)", out


@NO_GIT
def test_shallow_boundary_in_linked_worktree(tmp_path):
    """(e) a linked worktree reads the shallow file of its common dir, never `.git/shallow`."""
    repo, c, sha = _graph(tmp_path, "a")
    _shallow(repo, sha["B"])
    wt = tmp_path / "wt"
    _git(repo, "worktree", "add", "-q", "--detach", str(wt), sha["M"])
    assert (wt / ".git").is_file()
    code, out, untracked, _, _ = _lines(repo, c, cwd=wt)
    assert untracked == _shallow_text(sha["B"], c), out
    assert code == 0, out


def _patched_git(monkeypatch, cp, table):
    """Wrap cp._git: an args tuple in `table` returns its value, the rest run git."""
    real = cp._git
    monkeypatch.setattr(cp, "_git", lambda *a: table[a] if a in table else real(*a))


@NO_GIT
def test_shallow_flag_unknown_no_file_is_full(tmp_path, monkeypatch):
    """Missing input: --is-shallow-repository unknown (exit 129) and no file is a full clone; a file is read."""
    cp = _cp()
    repo, c = _history(tmp_path)
    monkeypatch.chdir(repo)
    _patched_git(monkeypatch, cp, {("rev-parse", "--is-shallow-repository"): ("", 129)})
    assert cp._shallow_boundaries() == "full"
    (repo / ".git" / "shallow").write_text(c + "\n", encoding="utf-8")
    assert cp._shallow_boundaries() == [c]


@NO_GIT
def test_shallow_file_unreadable_not_checked(tmp_path, monkeypatch):
    """Missing input: the flag says true but the file is missing, or holds a malformed line (C3)."""
    cp = _cp()
    repo, c = _history(tmp_path)
    monkeypatch.chdir(repo)
    _patched_git(monkeypatch, cp, {("rev-parse", "--is-shallow-repository"): ("true\n", 0)})
    want = (None, (f"not checked (shallow clone; run git fetch --unshallow) (cutoff {c[:7]} from --untracked-from)",
                   False), None)
    assert cp._shallow_boundaries() == "unreadable"
    assert cp._walk(c) == want
    (repo / ".git" / "shallow").write_text(c + "\nzz\n", encoding="utf-8")
    assert cp._shallow_boundaries() == "unreadable"
    # git itself dies on the bad line (shallow.c "bad shallow line"), so 053's shallow branch
    # answers before 079's: still not checked, never none or an error.
    text, failed = cp._walk(c)[1]
    assert text.startswith("not checked (") and "run git fetch --unshallow" in text and failed is False


@NO_GIT
def test_empty_shallow_file_is_today_path(tmp_path, monkeypatch):
    """Missing input: an empty shallow file is S = [], so the walk is today's."""
    cp = _cp()
    repo, c = _history(tmp_path)
    _shallow(repo)
    monkeypatch.chdir(repo)
    _patched_git(monkeypatch, cp, {("rev-parse", "--is-shallow-repository"): ("true\n", 0)})
    assert cp._shallow_boundaries() == []
    assert cp.untracked_changes(c) == (f"none (cutoff {c[:7]} from --untracked-from)", False)


@NO_GIT
def test_shallow_rev_list_failure_is_loud(tmp_path, monkeypatch):
    """Missing input: the whole-range rev-list (no --first-parent) fails -> an error, never none."""
    cp = _cp()
    repo, c, sha = _graph(tmp_path, "a")
    _shallow(repo, sha["B"])
    monkeypatch.chdir(repo)
    _patched_git(monkeypatch, cp, {("rev-list", f"{c}..HEAD"): ("", 128)})
    assert cp._walk(c) == (None, (f"cutoff {c[:7]}: git rev-list failed (cutoff {c[:7]} from --untracked-from)",
                                  True), None)


@NO_GIT
def test_merge_base_failure_is_loud(tmp_path, monkeypatch):
    """Missing input: merge-base --is-ancestor <b'> <C> exits 128 -> an error (exit 1), never below."""
    cp = _cp()
    repo, c, sha = _below_graph(tmp_path)
    _shallow(repo, sha["b"])
    monkeypatch.chdir(repo)
    _patched_git(monkeypatch, cp, {("merge-base", "--is-ancestor", sha["b"], c): ("", 128)})
    want = f"cutoff {c[:7]}: git merge-base failed (cutoff {c[:7]} from --untracked-from)"
    assert cp._walk(c) == (None, (want, True), None)
    assert cp.untracked_changes(c) == (want, True)


@NO_GIT
def test_below_rule_real_data_entries(tmp_path, monkeypatch):
    """Step 5: with a boundary below the cutoff, REAL-DATA FIELD entries become the unconfirmed text
    and no INCOMPLETE entry is passed on."""
    cp = _cp()
    repo, c = _history(tmp_path)
    _item(repo, "160", [], date="2026-11-11")
    monkeypatch.chdir(repo)
    monkeypatch.setattr(cp, "_item_triggers", lambda cutoff: ({"160": ("abc1234", ["ccbot/realtest.py"])}, None))
    b = "cd" * 20
    assert cp.real_data_field(c, ([], None, None))[1] == {"160": ["no 05 for abc1234 changes ccbot/realtest.py"
                                                                  " (item 070)"]}       # control
    assert cp.real_data_field(c, ([], None, b)) == (cp._below_text(b, 1, c), {}, False)
    assert cp._below_text(b, 1, c) == (f"not checked (shallow boundary cdcdcdc below the cutoff; 1 unconfirmed"
                                       f" entries; run git fetch --unshallow) (cutoff {c[:7]} from --untracked-from)")


def test_work_code_without_git(tmp_path):
    _item(tmp_path, "160", ["01-research.md", "02-improvements.md", "03-handoff.md"], scope="RESEARCH ONLY",
          date="2026-11-13")
    _write(tmp_path, "work/160/diag.py")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-13")
    assert code == 0, out
    assert "RESEARCH CODE: not checked (no git)" in out
    assert "UNTRACKED CHANGE: not checked (no git)" in out


@NO_GIT
def test_research_only_branch_work_py_is_branch_skipped(tmp_path):
    """Fixture (d): an open branch's RESEARCH ONLY item adds a diagnostic."""
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "res", "160", RES_STEPS, RES_160, extra=["work/160/diag.py"])
    code, out, _ = _research(repo, _root(repo))
    assert code == 0
    assert "BRANCH SKIPPED: 160 (origin/res: RESEARCH ONLY: changes work/160/diag.py" in out
    assert "SKIPPED: none" in out


@NO_GIT
def test_research_only_branch_nested_py_is_seen(tmp_path):
    """Fixture (e): a .py one folder deeper under work/<ID>/ is code too."""
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "res", "160", RES_STEPS, RES_160, extra=["work/160/sub/x.py"])
    code, out, _ = _research(repo, _root(repo))
    assert code == 0
    assert "BRANCH SKIPPED: 160 (origin/res: RESEARCH ONLY: changes work/160/sub/x.py" in out


@NO_GIT
def test_branch_unchanged_tip_py_not_counted(tmp_path):
    """Fixture (f, plan C2): a .py already on main and unchanged by the branch is not the branch's code."""
    repo = _repo_with_open_branch(tmp_path)
    _item(repo, "160", ["01-research.md", "02-improvements.md", "03-handoff.md"], scope="RESEARCH ONLY",
          date="2026-11-11", waived="04 05 06 (person, 2026-11-13: test)")
    _write(repo, "work/160/diag.py")
    _commit(repo, "160 R1-R3 + diagnostic, waived by the person")
    _branch_adds(repo, "res", "160", ["07-audit-task.md"], RES_160)
    code, out, line = _research(repo, _root(repo))
    assert code == 0, out
    assert "BRANCH SKIPPED: 160" not in out
    assert line == "RESEARCH CODE: none"


@NO_GIT
def test_branch_diff_failure_hides_code_gap_l(tmp_path, monkeypatch):
    """Gap (l) pinned: a failed branch `git diff` gives an empty change list, so the branch's
    code is not seen (information only). Making it loud must change this test on purpose."""
    import datetime as dt
    cp = _cp()
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "res", "160", RES_STEPS, RES_160, extra=["work/160/diag.py"])
    monkeypatch.chdir(repo)
    real = cp._git
    monkeypatch.setattr(cp, "_git", lambda *args: ("", 1) if args[0] == "diff" else real(*args))
    found = cp.open_branches(dt.date(2026, 11, 13))
    res = [b for b in found if b["ref"] == "origin/res"]
    assert res
    assert not any("changes work/160/diag.py" in d for b in res for _, d in b["skipped"])


# Item 069 (RI-010): the daily report's Inbox section (INBOX:).
INBOX_OK = ("# Daily audit - 2026-11-18\n## Inbox (other projects asking us to test or try something; item 069)\n"
            "project-inbox: nothing new (2 seen before)\nhub: {sha}, nothing new\n## ESCALATED recurring issues\n")


INBOX_TPL = "# Daily audit\n## Inbox (x)\nproject-inbox: <fill in>\nhub: <fill in>\n"
OLD_TPL = "# Daily audit\n## Items reviewed\n"  # main's template before 069: no ## Inbox
OLD_REPORT = ("# Daily audit - 2026-11-17\n## Inbox\nNo project-inbox step yet. Hub (116c68c): "
              "nothing addressed to us.\n## Items reviewed\n")  # 2026-11-17.md's real shape


def _daily(root, name, body, template=INBOX_TPL, commit=True, git=True):
    """A daily report in `root`. With git, `root` becomes a repo on its first call and the report
    (with templates/daily-audit.md = `template`, unless None) is committed if `commit`."""
    (root / "work").mkdir(exist_ok=True)  # main() lists work/; these fixtures have no items
    if git and not (root / ".git").exists():
        _git(root, "init", "-q", "-b", "main")
    if template is not None:
        (root / "templates").mkdir(exist_ok=True)
        (root / "templates" / "daily-audit.md").write_text(template, encoding="utf-8")
    p = root / "logs" / "audit" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    if git and commit:
        return _commit(root)


def _inbox(root):
    """INBOX line of main(); in a repo with a commit the item-053 cutoff is HEAD, so the
    fixture's templates/ commits are not UNTRACKED CHANGEs."""
    head = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], cwd=root, capture_output=True,
                          text=True) if (root / ".git").exists() else None
    extra = ["--untracked-from", head.stdout.strip()] if head is not None and head.returncode == 0 else []
    code, out = _run(root, "check_pipeline.py", "--today", "2026-11-18", *extra)
    line = next((ln for ln in out.splitlines() if ln.startswith("INBOX: ")), None)
    return code, out, line


@NO_GIT
@pytest.mark.parametrize("sha", ["116c68c", "116c68c533cbd9d13bf3e81c1d833ab408102f84"])
def test_inbox_section_with_sha_passes(tmp_path, sha):
    """(i), (i-b): a 7- and a 40-char hub SHA both pass."""
    _daily(tmp_path, "2026-11-18.md", INBOX_OK.format(sha=sha))
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: none", out
    assert code == 0, out


@NO_GIT
def test_inbox_unread_channels_pass(tmp_path):
    """(ii): UNREAD is a valid line for each channel (never shown as nothing new)."""
    _daily(tmp_path, "2026-11-18.md", "## Inbox (x)\nproject-inbox: UNREAD: not reachable (x)\n"
                                      "hub: UNREAD: not reachable (y)\n")
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: none", out
    assert code == 0, out


@NO_GIT
def test_inbox_heading_missing_fails(tmp_path):
    """(iii)."""
    _daily(tmp_path, "2026-11-18.md", "# Daily audit - 2026-11-18\n## ESCALATED recurring issues\n")
    code, out, line = _inbox(tmp_path)
    assert line.startswith("INBOX: 2026-11-18.md (no ## Inbox"), out
    assert "SKIPPED: none" in out
    assert code == 1


@NO_GIT
def test_inbox_hub_line_without_sha_fails(tmp_path):
    """(iv)."""
    _daily(tmp_path, "2026-11-18.md", "## Inbox (x)\nproject-inbox: nothing new (2 seen before)\nhub: nothing new\n")
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: 2026-11-18.md (no hub: SHA or UNREAD line)", out
    assert code == 1


@NO_GIT
def test_inbox_project_inbox_line_missing_fails(tmp_path):
    """(v)."""
    _daily(tmp_path, "2026-11-18.md", "## Inbox (x)\nhub: 116c68c, nothing new\n")
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: 2026-11-18.md (no project-inbox: line)", out
    assert code == 1


@NO_GIT
def test_inbox_ignores_per_item_report(tmp_path):
    """(vi): per-item reports are ignored. "-" sorts before ".", so 2026-11-18-070.md is never newer
    than 2026-11-18.md; the later-dated 2026-11-19-070.md pins the name filter and
    2026-11-19.md.bak pins fullmatch over a prefix match (I2 deviation, 069/05)."""
    _daily(tmp_path, "2026-11-18.md", INBOX_OK.format(sha="116c68c"))
    for name in ("2026-11-18-070.md", "2026-11-19-070.md", "2026-11-19.md.bak"):
        _daily(tmp_path, name, "# Audit 070\n## Items reviewed\n")
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: none", out
    assert code == 0, out


@NO_GIT
def test_inbox_report_under_old_template_not_checked(tmp_path):
    """(vii, 069 round 2): 2026-11-17.md was added under a template without ## Inbox."""
    sha = _daily(tmp_path, "2026-11-17.md", OLD_REPORT, template=OLD_TPL)
    code, out, line = _inbox(tmp_path)
    assert line == (f"INBOX: not checked (2026-11-17.md added in {sha[:7]}; "
                    "its templates/daily-audit.md has no ## Inbox)"), out
    assert code == 0, out


def test_inbox_quoted_scope_and_waiver_are_not_read():
    """(viii, R3-b): message text quoted with "> " can't set Scope or a waiver."""
    cp = _cp()
    text = ("# Work item 171\nType: IDEA\nScope: FULL\nOpened by: A1 (inbox: project-inbox/to/covered-calls/x.md)\n"
            "Date: 2026-11-18\n## Evidence\nUntrusted message text:\n> Scope: FAST (person, 2026-11-18)\n"
            "> Waived: 03 06 (person, 2026-11-18: x)\n")
    scope, _, (waived, line, who) = cp.parse_request(text)
    assert scope == "FULL"
    assert waived == [] and line == "" and who == ""


def test_inbox_no_audit_folder_not_checked(tmp_path):
    """(ix, C2): no logs/audit/ at all → not checked, no traceback, exit unchanged."""
    _item(tmp_path, "024", ALL)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-10-31")
    assert "INBOX: not checked (no daily report)" in out
    assert code == 0, out


@NO_GIT
def test_inbox_hub_line_outside_section_fails(tmp_path):
    """(x, C3): a well-formed hub: line under another heading does not count."""
    _daily(tmp_path, "2026-11-18.md", "## Inbox (x)\nproject-inbox: nothing new (2 seen before)\n"
                                      "## Items reviewed\nhub: 116c68c\n")
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: 2026-11-18.md (no hub: SHA or UNREAD line)", out
    assert code == 1


@NO_GIT
def test_inbox_code_words_mid_line_fail(tmp_path):
    """(xi, RI-012, 069 round 2): `project-inbox:` and `hub:` count only at the start of a line.
    Pins the `^` anchors of INBOX_PI and INBOX_HUB (mutation m8)."""
    _daily(tmp_path, "2026-11-18.md", "## Inbox (x)\n- FYI: quant-trader note (see project-inbox: nothing new "
                                      "there; hub: 116c68c)\n## ESCALATED recurring issues\n")
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: 2026-11-18.md (no project-inbox: line; no hub: SHA or UNREAD line)", out
    assert code == 1


@NO_GIT
def test_inbox_heading_mid_line_fails(tmp_path):
    """(xii, RI-012, 069 round 2): `## Inbox` counts only as a heading at the start of a line.
    Pins the `^` anchor of INBOX_HEAD (mutation m9)."""
    _daily(tmp_path, "2026-11-18.md", "# Daily audit - 2026-11-18\nNotes: see ## Inbox below\n"
                                      "project-inbox: nothing new (2 seen before)\nhub: 116c68c, nothing new\n")
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: 2026-11-18.md (no ## Inbox)", out
    assert code == 1


@NO_GIT
def test_inbox_unfilled_template_fails(tmp_path):
    """(xiii, 069 round 2): templates/daily-audit.md copied as-is must fail both channel lines,
    so a report whose placeholder lines were never filled in can't pass INBOX."""
    template = (REPO / "templates" / "daily-audit.md").read_text(encoding="utf-8")
    assert "## Inbox" in template and "<fill in>" in template
    _daily(tmp_path, "2026-11-18.md", template)
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: 2026-11-18.md (no project-inbox: line; no hub: SHA or UNREAD line)", out
    assert code == 1


def _old_then_template(root, name="2026-11-25.md"):
    """(xiv history) c1 old template; c2 adds an old-format report (dated after 2026-11-18, so the
    date is irrelevant); c3 changes the template to INBOX_TPL (the merge). Returns c2's SHA."""
    _daily(root, "2026-11-10.md", OLD_REPORT, template=OLD_TPL)
    c2 = _daily(root, name, OLD_REPORT, template=OLD_TPL)
    (root / "templates" / "daily-audit.md").write_text(INBOX_TPL, encoding="utf-8")
    _commit(root)
    return c2


def _not_checked(name, sha):
    return f"INBOX: not checked ({name} added in {sha[:7]}; its templates/daily-audit.md has no ## Inbox)"


@NO_GIT
def test_inbox_old_report_after_template_change_not_checked(tmp_path):
    """(xiv, A1 P1): an old-format report added before the template change stays unchecked
    after it, on any date; the gate reads the adding commit, not HEAD."""
    c2 = _old_then_template(tmp_path)
    code, out, line = _inbox(tmp_path)
    assert line == _not_checked("2026-11-25.md", c2), out
    assert code == 0, out


@NO_GIT
def test_inbox_old_report_edited_after_template_change_not_checked(tmp_path):
    """(xiv-b): editing the old report after the merge keeps its adding commit (--diff-filter=A)."""
    c2 = _old_then_template(tmp_path)
    with (tmp_path / "logs" / "audit" / "2026-11-25.md").open("a", encoding="utf-8") as fh:
        fh.write("A1 note appended later.\n")
    _commit(tmp_path)
    code, out, line = _inbox(tmp_path)
    assert line == _not_checked("2026-11-25.md", c2), out
    assert code == 0, out


@NO_GIT
@pytest.mark.parametrize("into", ["main", "t"])
def test_inbox_old_report_through_real_merge_not_checked(tmp_path, into):
    """(xiv-c): report on `main`, template change on `t`, `git merge --no-ff` either way; the
    path-limited log follows the TREESAME parent to the report's own adding commit."""
    _daily(tmp_path, "2026-11-10.md", OLD_REPORT, template=OLD_TPL)
    _git(tmp_path, "branch", "t")
    report = _daily(tmp_path, "2026-11-25.md", OLD_REPORT, template=OLD_TPL)
    _git(tmp_path, "checkout", "-q", "t")
    (tmp_path / "templates" / "daily-audit.md").write_text(INBOX_TPL, encoding="utf-8")
    _commit(tmp_path)
    if into == "main":
        _git(tmp_path, "checkout", "-q", "main")
        _git(tmp_path, "merge", "-q", "--no-ff", "-m", "merge t", "t")
    else:
        _git(tmp_path, "merge", "-q", "--no-ff", "-m", "merge main", "main")
    assert (tmp_path / "logs" / "audit" / "2026-11-25.md").is_file()
    assert "## Inbox (x)" in (tmp_path / "templates" / "daily-audit.md").read_text(encoding="utf-8")
    code, out, line = _inbox(tmp_path)
    assert line == _not_checked("2026-11-25.md", report), out
    assert code == 0, out


NEW_NO_HUB = "## Inbox (x)\nproject-inbox: nothing new (2 seen before)\n## Items reviewed\n"


@NO_GIT
def test_inbox_new_report_after_template_change_still_checked(tmp_path):
    """(xv, A1 send-back 1): a report added under the new template is checked from day one."""
    _old_then_template(tmp_path)
    _daily(tmp_path, "2026-11-26.md", NEW_NO_HUB)
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: 2026-11-26.md (no hub: SHA or UNREAD line)", out
    assert code == 1, out


@NO_GIT
def test_inbox_uncommitted_report_uses_working_template(tmp_path):
    """(xv-b): an uncommitted report is judged by the working-tree template (here with Inbox)."""
    _old_then_template(tmp_path)
    _daily(tmp_path, "2026-11-26.md", NEW_NO_HUB, commit=False)
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: 2026-11-26.md (no hub: SHA or UNREAD line)", out
    assert code == 1, out


@NO_GIT
def test_inbox_uncommitted_report_old_working_template_not_checked(tmp_path):
    """(xv-c): uncommitted report, working template without ## Inbox -> not checked."""
    _daily(tmp_path, "2026-11-10.md", OLD_REPORT, template=OLD_TPL)
    _daily(tmp_path, "2026-11-26.md", NEW_NO_HUB, template=OLD_TPL, commit=False)
    code, out, line = _inbox(tmp_path)
    assert line == ("INBOX: not checked (2026-11-26.md not committed; "
                    "its templates/daily-audit.md has no ## Inbox)"), out
    assert code == 0, out


@NO_GIT
@pytest.mark.parametrize("hub", ["116c68", "2026-11-18", "116c68c533cbd9d13bf3e81c1d833ab408102f84a"])
def test_inbox_hub_value_not_a_sha_fails(tmp_path, hub):
    """(xvi, A1 P2, RI-001): 6 hex, a date and 41 hex are not a hub SHA; pins both ends of {7,40}."""
    _daily(tmp_path, "2026-11-18.md", INBOX_OK.format(sha=hub))
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: 2026-11-18.md (no hub: SHA or UNREAD line)", out
    assert code == 1, out


def test_inbox_no_git_not_checked(tmp_path):
    """(xvii): no git repo -> not checked, never none."""
    _daily(tmp_path, "2026-11-18.md", INBOX_OK.format(sha="116c68c"), git=False)
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: not checked (no git)", out
    assert code == 0, out


@NO_GIT
def test_inbox_only_per_item_reports_not_checked(tmp_path):
    """(xvii-b): a repo whose logs/audit/ holds only per-item reports."""
    _daily(tmp_path, "2026-11-18-070.md", "# Audit 070\n## Items reviewed\n")
    code, out, line = _inbox(tmp_path)
    assert line == "INBOX: not checked (no daily report)", out
    assert code == 0, out


@NO_GIT
def test_inbox_shallow_clone_not_checked(tmp_path):
    """(xviii): in a depth-1 clone every file looks added in the boundary commit (new template),
    so the old report would fail; the shallow guard makes it not checked."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _old_then_template(repo)
    clone = tmp_path / "clone"
    _git(tmp_path, "clone", "-q", "--depth", "1", f"file://{repo}", str(clone))
    (clone / "work").mkdir(exist_ok=True)
    code, out, line = _inbox(clone)
    assert line == "INBOX: not checked (shallow clone; run git fetch --unshallow)", out
    assert code == 0, out


@NO_GIT
def test_inbox_git_log_failure_fails(tmp_path, monkeypatch):
    """(xix): a failing `git log` is a failure, not hidden as not checked."""
    _daily(tmp_path, "2026-11-18.md", INBOX_OK.format(sha="116c68c"))
    cp = _cp()
    real = cp._git
    monkeypatch.setattr(cp, "_git", lambda *args: ("", 128) if args[0] == "log" else real(*args))
    monkeypatch.chdir(tmp_path)
    assert cp.inbox_section() == ("2026-11-18.md (git log failed)", True)


@NO_GIT
def test_inbox_template_absent_at_adding_commit_not_checked(tmp_path):
    """(xx): no templates/ at all when the report was added -> not checked."""
    c1 = _daily(tmp_path, "2026-11-18.md", OLD_REPORT, template=None)
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "daily-audit.md").write_text(INBOX_TPL, encoding="utf-8")
    _commit(tmp_path)
    code, out, line = _inbox(tmp_path)
    assert line == _not_checked("2026-11-18.md", c1), out
    assert code == 0, out


@NO_GIT
def test_inbox_repo_without_commits_checks_content(tmp_path, monkeypatch):
    """(xxi): no HEAD yet; the uncommitted report is judged by the working template and checked."""
    _daily(tmp_path, "2026-11-18.md", INBOX_OK.format(sha="116c68c"), commit=False)
    cp = _cp()
    monkeypatch.chdir(tmp_path)
    assert cp.inbox_section() == ("none", False)


# Item 071: I3's verdict and send-back target in 06 (templates/verification.md L2-3).
def test_i3_fail_shows_and_exits_1(tmp_path):
    """T1: a 06 FAIL with no 07 is I3 FAIL, not `in progress (next 07)`, and exits 1."""
    _item(tmp_path, "171", ALL[:6], verdict="FAIL")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    assert code == 1, out
    assert "171: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))" in out
    assert "I3 FAIL: 171" in out and "A1 FAIL: none" in out and "INCOMPLETE: none" in out


def _rounds_item(root, item, files):
    """T2: line 2 rewritten to PASS above a round-1 FAIL body; I3 logged FAIL 23:50 and PASS 00:00
    across UTC midnight; the other steps logged in the fixture's well-formed format."""
    _item(root, item, files, logged=False)
    (root / "work" / item / "06-verification.md").write_text(
        f"# 06 Verification - {item}\nVerdict: PASS (round 2; earlier rounds: FAIL round 1)\nSent back to: none\n"
        "Recurring issues checked: RI-007\n# Round 1\nVerdict: FAIL (round 1)\nSent back to: I2\n", encoding="utf-8")
    for team, date, lines in (
            ("research", "2026-11-17", [f"10:00 | {a} | {item} | {FIELDS[a]}" for a in ("R1", "R2", "R3")]),
            ("implementation", "2026-11-17", [f"11:00 | {a} | {item} | {FIELDS[a]}" for a in ("I1", "I2")]
             + [f"23:50 | I3 | {item} | FAIL | sent to audit: no"]),
            ("implementation", "2026-11-18", [f"00:00 | I3 | {item} | PASS | sent to audit: yes"])):
        log = root / "logs" / team / f"{date}.md"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write("".join(l + "\n" for l in lines))


def test_later_pass_round_clears_i3_fail(tmp_path):
    """T2: the first Verdict line decides (a later round-1 FAIL is not read); log by date, then line."""
    _rounds_item(tmp_path, "172", ALL[:6])
    _rounds_item(tmp_path, "179", ALL)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    assert "172: in progress (FULL: next 07)" in out
    assert "179: complete (FULL)" in out
    assert "I3 FAIL: none" in out and "INCOMPLETE: none" in out
    assert code == 0, out


def test_old_06_without_round_headers_unchanged(tmp_path):
    """T3: below VERDICT_FROM a missing verdict line is not checked; from 071 it is INCOMPLETE."""
    _item(tmp_path, "060", ALL, verdict=None)
    (tmp_path / "work" / "060" / "06-verification.md").write_text(
        "Verdict: PASS\nx\nRecurring issues checked: RI-007\n", encoding="utf-8")
    _item(tmp_path, "065", ALL, verdict=None)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    assert code == 0, out
    assert "060: complete (FULL)" in out and "065: complete (FULL)" in out and "INCOMPLETE: none" in out
    _item(tmp_path, "173", ALL, verdict=None)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    assert code == 1, out
    assert "173 (06 has no readable 'Verdict: PASS' or 'Verdict: FAIL' line (item 071))" in out
    assert "065 (" not in out.split("INCOMPLETE:")[1]


UNFILLED = "Verdict: PASS | FAIL (round <n>; earlier rounds: <verdicts>)\n"


@pytest.mark.parametrize("text, want", [
    # read as a verdict
    ("Verdict: PASS (round 3; earlier rounds: FAIL round 1)\n", ("PASS", None)),
    ("Verdict: **FAIL** (x)\n", ("FAIL", None)),
    ("Verdict: **PASS**. note\n", ("PASS", None)),
    # unreadable: None, never PASS (RI-002, RI-012)
    (UNFILLED, (None, None)),
    ("Verdict: **PASS** | FAIL\n", (None, None)),
    ("Verdict: PASS/FAIL\n", (None, None)),
    ("Verdict: pass\n", (None, None)),
    ("Verdict: PASSED\n", (None, None)),
    ("see 05. Verdict: FAIL\n", (None, None)),
    ("  Verdict: FAIL\n", (None, None)),
    (UNFILLED + "x\nVerdict: FAIL (round 1)\n", (None, None)),
    ("```\nVerdict: PASS (round 1)\n", (None, None)),                     # unclosed fence (C6)
    # skipped text: fences and HTML comments
    ("```\nVerdict: FAIL (pasted)\n```\nVerdict: PASS (round 1)\n", ("PASS", None)),
    # item 077: CommonMark 0.31.2 §4.5 fences (_md_lines)
    pytest.param("~~~\nVerdict: FAIL (pasted)\n~~~\nVerdict: PASS (round 1)\n", ("PASS", None), id="tilde"),
    pytest.param("````\n```\nVerdict: FAIL (pasted)\n````\nVerdict: PASS (round 1)\n", ("PASS", None), id="longer"),
    pytest.param("    ```\nVerdict: PASS (round 1)\n    ```\n", ("PASS", None), id="4-space"),
    pytest.param("\t```\nVerdict: PASS (round 1)\n", ("PASS", None), id="tab"),
    pytest.param("```\n```py\nVerdict: FAIL (pasted)\n```\nVerdict: PASS (round 1)\n", ("PASS", None), id="info"),
    pytest.param("```\nVerdict: FAIL (pasted)\n    ```\nVerdict: FAIL (inside)\n```\nVerdict: PASS (round 1)\n",
                 ("PASS", None), id="4-space-close"),
    pytest.param("```x`y\nVerdict: PASS (round 1)\n", ("PASS", None), id="backtick-info"),
    pytest.param("~~~x`y\nVerdict: FAIL (pasted)\n~~~\nVerdict: PASS (round 1)\n", ("PASS", None), id="tilde-info"),
    pytest.param("~~~\nVerdict: FAIL (pasted)\n```\nVerdict: FAIL (inside)\n~~~\nVerdict: PASS (round 1)\n",
                 ("PASS", None), id="mixed"),
    ("<!--\nVerdict: FAIL (old)\n-->\nVerdict: PASS (round 1)\n", ("PASS", None)),
    # targets: full-line match only
    ("Verdict: FAIL (round 1)\nSent back to: I1 I2\n", ("FAIL", "I1 I2")),
    ("Verdict: FAIL (round 1)\nSent back to: I2 (tests only)\n", ("FAIL", None)),
    ("Verdict: FAIL (round 1)\nSent back to: <I1 | I2 | I1 I2 | none>\n", ("FAIL", None)),
    ("Verdict: FAIL (round 1)\nx Sent back to: I2\n", ("FAIL", None)),
])
def test_i3_verdict_reader(tmp_path, text, want):
    """T4: the reader's anchored first-line rule (D1-D4)."""
    f = tmp_path / "06.md"
    f.write_text(text, encoding="utf-8")
    assert _cp().i3_verdict(f) == want


def test_i3_fail_beats_older_a1_fail(tmp_path):
    """T5: the 069/070 order: 06 FAIL after an older 07 A1 FAIL shows I3 FAIL (D7)."""
    _item(tmp_path, "174", ALL, verdict="FAIL", a1="A1 result: FAIL (2026-11-17, test)")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    assert code == 1, out
    assert "174: I3 FAIL (" in out and "I3 FAIL: 174" in out and "A1 FAIL: none" in out
    assert "174: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))" in out   # item 077


NEW_ITEM = ("I3 FAIL (FULL; sent back to I2; 06 FAIL after A1 PASS in 07: a follow-up to a completed item is a "
            "new item (run-item, items 053, 077))")


def test_i3_fail_after_a1_pass_is_a_new_item(tmp_path):
    """Item 077 (T-P3): a 06 FAIL whose 07 ends in A1 PASS names the new-item rule (the last A1 line decides)."""
    _item(tmp_path, "180", ALL, verdict="FAIL")
    _item(tmp_path, "185", ALL, verdict="FAIL", a1="A1 result: FAIL (r1)\nA1 result: PASS (r2)")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    assert code == 1, out
    for i in ("180", "185"):
        line = [l for l in out.splitlines() if l.startswith(f"{i}: ")][0]
        assert line == f"{i}: {NEW_ITEM}", out
        assert "needs a later PASS round" not in line
    assert "I3 FAIL: 180, 185" in out


def test_i3_fail_with_no_a1_line_keeps_old_detail(tmp_path):
    """Item 077 (T-P3b): a 07 with no `A1 result:` line keeps the old detail, PRE_A1_LINE items too
    (known gap: _open_at calls 017 closed)."""
    _item(tmp_path, "184", ALL, verdict="FAIL", a1=None)
    _item(tmp_path, "017", ALL, verdict="FAIL", a1=None)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    assert code == 1, out
    for i in ("184", "017"):
        assert f"{i}: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))" in out, out


def test_i3_fail_with_a1_pass_only_inside_text_keeps_old_detail(tmp_path):
    """Item 077 round 2 (T-P3c, RI-012): an `A1 result: PASS` that is not at column 0 (inside a sentence,
    or indented) is not an A1 line, so the old detail stays."""
    _item(tmp_path, "186", ALL, verdict="FAIL", a1="see A1 result: PASS (quoted)")
    _item(tmp_path, "187", ALL, verdict="FAIL", a1="  A1 result: PASS (indented)")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    assert code == 1, out
    for i in ("186", "187"):
        line = [l for l in out.splitlines() if l.startswith(f"{i}: ")][0]
        assert line == f"{i}: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))", out
    assert "I3 FAIL: 186, 187" in out


def test_i3_fail_target_not_stated(tmp_path):
    """T6: the target is never defaulted (RI-002); from 071 a FAIL without one is INCOMPLETE."""
    _item(tmp_path, "175", ALL[:6], verdict="FAIL", sent_back=None)
    _item(tmp_path, "178", ALL[:6], verdict="FAIL", sent_back="none")
    _item(tmp_path, "066", ALL[:6], verdict="FAIL", sent_back=None)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    assert code == 1, out
    for i in ("175", "178", "066"):
        assert f"{i}: I3 FAIL (FULL; sent back to: not stated, needs a later PASS round in 06 (item 071))" in out
    for i in ("175", "178"):
        assert f"{i} (06 Verdict is FAIL but has no 'Sent back to: I1, I2 or I1 I2' line (item 071))" in out
    assert "066 (" not in out.split("INCOMPLETE:")[1]
    assert "sent back to I2" not in out


def test_06_verdict_disagrees_with_last_i3_log(tmp_path):
    """T7: from CHECKLIST_FROM, 06's verdict must match the last I3 log line's first word (D6)."""
    for i in ("176", "040"):
        _item(tmp_path, i, ALL[:6])
        with (tmp_path / "logs" / "implementation" / "2026-10-31.md").open("a", encoding="utf-8") as fh:
            fh.write(f"12:30 | I3 | {i} | FAIL | sent to audit: no\n")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    assert code == 1, out
    assert "176 (06 Verdict says PASS, last I3 log line says FAIL (item 071))" in out
    assert "040 (" not in out.split("INCOMPLETE:")[1]


@NO_GIT
def test_i3_fail_with_more_steps_on_branch_is_in_pr(tmp_path):
    """T8: an I3 FAIL item whose open branch has more step files is IN PR (D8)."""
    origin, repo = tmp_path / "origin.git", tmp_path / "repo"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    _git(tmp_path, "clone", "-q", str(origin), str(repo))
    _git(repo, "checkout", "-q", "-b", "main")
    _item(repo, "177", ALL[:6], verdict="FAIL")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "main")
    _git(repo, "push", "-q", "origin", "main")
    _branch_adds(repo, "fix", "177", ["07-audit-task.md"])
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-18")
    assert "177: IN PR (origin/fix has " in out and "; was I3 FAIL here)" in out
    assert "I3 FAIL: none" in out and "IN PR: 177" in out
    assert "BRANCH FAIL: 177 (origin/fix: I3 FAIL; " in out          # item 077


def test_verification_template_lines_unfilled(tmp_path):
    """T10: the shipped template's top lines are unreadable until filled."""
    cp = _cp()
    tpl = REPO / "templates" / "verification.md"
    assert cp.i3_verdict(tpl) == (None, None)
    lines = tpl.read_text(encoding="utf-8").splitlines(keepends=True)
    assert lines[1].startswith("Verdict:") and lines[2].startswith("Sent back to:")
    lines[1:3] = ["Verdict: PASS (round 1)\n", "Sent back to: none\n"]
    f = tmp_path / "06.md"
    f.write_text("".join(lines), encoding="utf-8")
    assert cp.i3_verdict(f) == ("PASS", "none")


def test_pass_without_sent_back_none_is_incomplete(tmp_path):
    """T11 (C1): from 071 a PASS needs `Sent back to: none`; a stale or missing field is INCOMPLETE."""
    _item(tmp_path, "180", ALL, sent_back="I2")
    _item(tmp_path, "181", ALL, sent_back=None)
    _item(tmp_path, "182", ALL)
    _item(tmp_path, "067", ALL, sent_back="I2")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    assert code == 1, out
    rest = out.split("INCOMPLETE:")[1]
    for i in ("180", "181"):
        assert f"{i} (06 Verdict is PASS but has no 'Sent back to: none' line (item 071))" in rest
    assert "182 (" not in rest and "067 (" not in rest


def test_malformed_last_i3_line_is_not_replaced(tmp_path):
    """T12 (C2): a malformed last I3 line is 045's; an earlier well-formed line is never used."""
    _item(tmp_path, "183", ALL)
    log = tmp_path / "logs" / "implementation" / "2026-10-31.md"
    log.write_text(log.read_text(encoding="utf-8").replace(
        "12:00 | I3 | 183 | PASS | sent to audit: yes\n",
        "12:00 | I3 | 183 | FAIL | sent to audit: no\n12:05 | I3 | 183 | see 06\n"), encoding="utf-8")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-18")
    rest = out.split("INCOMPLETE:")[1]
    assert "183 (log line for I3 does not match its format (item 045)" in rest
    assert "06 Verdict says" not in rest
    assert code == 1, out


@pytest.mark.parametrize("path, must, must_not", [
    (".claude/agents/i3-verifier.md", ["On FAIL write no 07", "Sent back to:", "(item 071)"], ["5. On PASS, write"]),
    (".claude/agents/i2-builder.md", ["not a defect of this build (item 071)"], []),
])
def test_agent_texts_name_item_071(path, must, must_not):
    """T13 (C5, RI-010): the two agent sentences stay in place."""
    text = (REPO / path).read_text(encoding="utf-8")
    assert all(m in text for m in must) and not any(m in text for m in must_not)
