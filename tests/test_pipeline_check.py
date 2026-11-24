"""scripts/check_pipeline.py (items 026, 029; RI-007) and check_handoff.py --all (item 028)."""
import os
import re
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
          "I2": "1 files changed | tests 1 passed in 0.01s", "I3": "PASS | sent to audit: yes"}
# Item 076: items before TESTS_FORMAT_FROM (76) keep the old I2 form `<pass>/<total>`.
I2_BEFORE_FIELD = "1 files changed | tests 1/1"


def _field(agent, item):
    """The well-formed log field for this agent and item (item 076: old I2 form below 76)."""
    return I2_BEFORE_FIELD if agent == "I2" and int(item) < 76 else FIELDS[agent]


def _item(root, item, files, scope="FULL", date="2026-10-31", waived=None, a1="A1 result: PASS (test)",
          logged=True, verdict="PASS", sent_back="auto"):
    """A fixture item. Its 06 carries the step-0 line and each step gets its log line (item 043).
    Item 071: 06 starts with `Verdict: <verdict> (round 1)` (none when verdict is None) and
    `Sent back to: <t>` (auto: none on PASS, I2 on FAIL; none when sent_back is None).
    Item 082: 05 is `x` plus a `Suite:` line equal to the tests part of this item's I2 field."""
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
        if f == "05-build-report.md":                         # item 082: the Suite line equals the I2 tests field
            body = f"x\nSuite: {_field('I2', item).split(' | tests ', 1)[1]}\n"
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
    _item(tmp_path, "085", ["05-build-report.md", "06-verification.md", "07-audit-task.md"],
          waived="01 02 03 04 (person, 2026-10-31: built before 026)")   # item 090: below TIMED_FROM (no line before I2)
    _item(tmp_path, "106", ["01-research.md", "03-handoff.md", "04-build-plan.md", "05-build-report.md",
                            "06-verification.md", "07-audit-task.md"], waived="02 (A1, 2026-11-01: no claims)")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-10-31")
    assert code == 0
    assert "085: complete (FULL; Waived: 01 02 03 04 (person, 2026-10-31: built before 026))" in out
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
    flag = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8")
    if flag.returncode != 0 or flag.stdout.strip() != "false":
        pytest.skip("REPO is a shallow clone: 083 is judged strictly (item 084); run git fetch --unshallow")
    code, out = _run_head(REPO, tmp_path, "check_pipeline.py")
    assert code == 0, out
    assert "RESEARCH CODE: none" in out                 # item 062
    assert "061: complete" in out                      # item 064: 061 stays complete with work/ .py as code
    assert "I3 FAIL: none" in out  # item 071
    assert "UNCOMMITTED STEP: none" in out             # item 077
    lines = out.splitlines()                           # item 084: the exempt set is exactly {083}
    assert [l for l in lines if l.startswith("RULE NOT SEEN:")] == [
        "RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; "
        "06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)"], out
    assert "INCOMPLETE: none" in lines, out
    assert ("LOG BATCH: none (not checked: 083: six lines written in one batch" in out), out   # item 086 (c)


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
    code, err = _log(tmp_path, "I2", "999", "1 file changed | tests 1 passed in 0.01s")
    assert code == 2 and "item 047" in err and not (tmp_path / "logs").exists()


def test_orphan_log_line_is_reported(tmp_path):
    """047: a log line for an item with no work folder is ORPHAN LOG (exit 1); real items are not."""
    _item(tmp_path, "150", ALL)
    with (tmp_path / "logs" / "implementation" / "2026-10-31.md").open("a", encoding="utf-8") as fh:
        fh.write("12:05 | I2 | 999 | 1 file changed | tests 1 passed in 0.01s\n")
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
    log.write_text("22:24 | I1 | 150 | FIT | 1 files planned\n23:10 | I2 | 150 | 1 files changed | tests 1 passed in 0.01s\n"
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
    log.write_text("20:40 | I2 | 150 | 1 files changed | tests 1 passed in 0.01s\n", encoding="utf-8")
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
            'I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed, with its ` in <s>s` '
            'time>")') in out
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "check_pipeline.py"), "--log", "I2", "150", "see 05"],
                       cwd=tmp_path, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 2
    assert r.stderr.strip() == ('--log refused: I2 | 150 | see 05 does not match '
                                '"<n> files changed | tests <last line of python3 -m pytest -q, as printed, with its '
                                '` in <s>s` time>"')


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
    "1 passed",                                                            # untimed (below TIMED_FROM)
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
    """076 T1: from item 076 on, pytest's summary line as printed is accepted and written. Item 090: on 089,
    the last ID before TIMED_FROM, so the untimed cases (A5, A6, `1 passed`) keep their 076 meaning."""
    _request(tmp_path, "089")
    code, err = _log(tmp_path, "I2", "089", f"1 files changed | tests {case}")
    assert code == 0, err
    text = next((tmp_path / "logs" / "implementation").glob("*.md")).read_text(encoding="utf-8")
    assert text.splitlines()[-1][5:] == f" | I2 | 089 | 1 files changed | tests {case}"


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
    log.write_text("12:00 | R1 | 1510 | x\n12:00 | R2 | 151 | see R1 notes\n12:00 | I2 | 151 | R1 x\n"
                   "12:00 | XR1 | 151 | x\n", encoding="utf-8")       # item 082: `_logged` needs the left `|`
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
    _write(repo, "work/150/05-build-report.md", "x\nSuite: 1 passed in 0.01s\n## Follow-up\n")
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
    _write(repo, "work/150/05-build-report.md", "x\nSuite: 1 passed in 0.01s\n## Follow-up\n")
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
    _write(repo, "work/150/05-build-report.md", "x\nSuite: 1 passed in 0.01s\n## Follow-up\n")
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
    _write(repo, "work/153/05-build-report.md", "x\nSuite: 1 passed\nrework\n")
    _write(repo, "ccbot/x.py")
    _commit(repo, "153 rework")
    assert _untracked(repo, cutoff)[1] == f"UNTRACKED CHANGE: none (cutoff {cutoff[:7]} from --untracked-from)"
    _write(repo, "work/153/07-audit-task.md", "x\nA1 result: FAIL (test)\nA1 result: PASS (test)\n")
    _commit(repo, "153 passes")
    _write(repo, "work/153/05-build-report.md", "x\nSuite: 1 passed\nrework\nmore\n")
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
    (repo / ".git" / "shallow").write_text(c + "\n" + c + "x\n", encoding="utf-8")    # item 082: 40 hex + x
    assert cp._shallow_boundaries() == "unreadable"
    (repo / ".git" / "shallow").write_text(c + "\n" + "a" * 41 + "\n", encoding="utf-8")   # 41 hex
    assert cp._shallow_boundaries() == "unreadable"
    # the malformed line's _walk result is pinned with real git, unpatched, in the next test


@NO_GIT
def test_malformed_shallow_line_real_git_not_checked(tmp_path):
    """Missing input, real git, no patching (I3 round 1 P1): a bad S line makes git die (exit 128)
    on --is-shallow-repository, --verify and --is-ancestor alike. The 053 block must not call that
    a squash/rebase: it is not checked (shallow clone). Other checks may still exit 1 (git died)."""
    repo, c = _history(tmp_path)
    (repo / ".git" / "shallow").write_text(c + "\nzz\n", encoding="utf-8")
    flag = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=repo,
                          capture_output=True, text=True)
    assert flag.returncode != 0 and "bad shallow line" in flag.stderr
    code, out, untracked, research, real = _lines(repo, c)
    assert untracked == (f"UNTRACKED CHANGE: not checked (shallow clone; run git fetch --unshallow)"
                         f" (cutoff {c[:7]} from --untracked-from)"), out
    assert research == "RESEARCH CODE: not checked (see UNTRACKED CHANGE)", out
    assert real == "REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)", out


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
def test_branch_diff_failure_is_branch_error(tmp_path, monkeypatch, capsys):
    """Gap (l) closed on purpose (item 081, RI-014): this test was test_branch_diff_failure_hides_code_gap_l,
    which pinned a failed branch `git diff` as an empty change list (the branch's code not seen, no
    error). Now the failure is recorded once per branch and printed as BRANCH ERROR (exit 1)."""
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
    assert res[0]["errors"] == ["git diff failed (exit 1)"]       # changed() runs 5 times: listed once
    assert not any("changes work/160/diag.py" in d for b in res for _, d in b["skipped"])
    code = cp.main(["--untracked-from", _root(repo), "--today", "2026-11-13"])
    out = capsys.readouterr().out
    assert "BRANCH ERROR: origin/res (git diff failed (exit 1))" in out, out
    assert code == 1


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
    pytest.param("```\nVerdict: FAIL (pasted)\n`````\nVerdict: PASS (round 1)\n", ("PASS", None), id="longer-close"),
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


# Item 081 (RI-014): a failed git read is an error or "not checked", never none, 0 or [].
GIT_LINES = ("LOG TIME:", "OPEN BRANCHES", "IN PR:", "RULES BRANCH:", "ID CLASH:", "MAIN AHEAD:",
             "UNTRACKED CHANGE:", "RESEARCH CODE:", "REAL-DATA FIELD:", "UNCOMMITTED STEP:", "INBOX:",
             "RULE NOT SEEN:")   # item 089 (E1, from 088): after 089's shallow decode change
# Every _git / _git_ok call in scripts/check_pipeline.py by (innermost function, callee): (count, reason).
# A new git call adds or bumps one entry with its reason (items 084, 086 build on this).
GIT_CENSUS = {
    ("uncommitted_steps", "_git"): (2, "is None no-git probe; ls-tree failure is 077's error"),
    ("late_log_lines", "_git"): (1, "no-git probe"),
    ("late_log_lines", "_git_ok"): (2, "ls-tree and blame failures are entries (081)"),
    ("_git_ok", "_git"): (1, "the helper"),
    ("open_branches", "_git"): (5, "is-ancestor 128 lists the ref (more); merge-tree 0/1 are answers, else "
                                   "'merge not checked'; cat-file non-zero = absent at base (a die gives a "
                                   "clash, loud); log -1 is age only (cosmetic); merge-base --all exit 1 = no "
                                   "common ancestor (git source: show_merge_base returns 1 only for an empty "
                                   "result) -> not-scanned line, other non-zero -> BRANCH ERROR (081 r2)"),
    ("open_branches", "_git_ok"): (5, "branch -r, ls-tree, show request/body -> BRANCH ERROR; ls-tree of an "
                                      "unrelated ref's checked paths (081 r2)"),
    ("changed", "_git_ok"): (2, "fallback failure -> BRANCH ERROR"),
    ("_open_at", "_git"): (1, "an absent 07 must read open; the same walk's diff-tree just succeeded (F8)"),
    ("_shallow_boundaries", "_git"): (2, "079: failure -> 'full' -> _walk loud (exit 1)"),
    ("_walk", "_git"): (7, "079: each failure is a not-checked or error tuple"),
    ("untracked_changes", "_git"): (1, "no-git probe"),
    ("research_code", "_git"): (1, "no-git probe"),
    ("real_data_field", "_git"): (1, "no-git probe"),
    ("_item_triggers", "_git"): (1, "070: 'git log failed', exit 1"),
    ("main_ahead", "_git_ok"): (2, "error string -> MAIN AHEAD line, exit 1"),
    ("next_id", "_git_ok"): (2, "refusal, exit 2"),
    ("_inbox_gate", "_git"): (4, "flag 128 loud (081); log failure loud (069); show failure -> not checked"),
    ("main", "_git"): (2, "no-git probes"),
    ("_anchor_env", "_git"): (2, "084: no-git probe; 088: rev-parse --verify HEAD read once: exit 1 = no commit "
                                 "(unborn) -> not checked, None -> no git, other non-zero -> not checked + exit 1"),
    ("_rule_seen", "_git_ok"): (3, "084: log/ls-tree/show failure -> 'anchor: git failed' entry, strict"),
}


def _git_lines(out):
    return {p: [l for l in out.splitlines() if l.startswith(p)] for p in GIT_LINES}


def test_git_ok_contract(monkeypatch):
    """Item 081: _git_ok's three results; the reason holds the command and code, never stderr."""
    cp = _cp()
    monkeypatch.setattr(cp, "_git", lambda *a: ("x", 0))
    assert cp._git_ok("status") == ("x", None)
    monkeypatch.setattr(cp, "_git", lambda *a: None)
    assert cp._git_ok("status") == (None, "no git")
    monkeypatch.setattr(cp, "_git", lambda *a: ("", 128))
    assert cp._git_ok("log", "-1") == ("", "git log failed (exit 128)")


def test_git_call_census():
    """Item 081: every git call site is counted with a reason, so a new raw _git call (whose
    failure could read as none) fails here until it is reviewed and added."""
    import ast
    import collections
    tree = ast.parse((REPO / "scripts" / "check_pipeline.py").read_text(encoding="utf-8"))
    seen = collections.Counter()

    def walk(node, fn):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, ast.Call) and isinstance(ch.func, ast.Name) and ch.func.id in ("_git", "_git_ok"):
                seen[(fn, ch.func.id)] += 1
            walk(ch, ch.name if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn)

    walk(tree, None)
    assert dict(seen) == {k: v[0] for k, v in GIT_CENSUS.items()}
    assert all(reason.strip() for _, reason in GIT_CENSUS.values())
    assert sum(seen.values()) == 47                    # 41 (081) + 5 (084) + 1 (081 r2)


def test_all_git_fails_no_line_says_none(tmp_path, monkeypatch, capsys):
    """(a) every git command exits 128: each git-reading line is there and none says none; exit 1.
    --next-id refuses (exit 2, empty stdout) instead of guessing from HEAD alone."""
    cp = _cp()
    _item(tmp_path, "150", [], date="2026-11-20")
    _daily(tmp_path, "2026-11-20.md", INBOX_OK.format(sha="a" * 7), git=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cp, "_git", lambda *a: ("", 128))
    code = cp.main(["--today", "2026-11-20"])
    out = capsys.readouterr().out
    for p, lines in _git_lines(out).items():
        assert lines, f"{p} missing:\n{out}"
        assert not any(l.rstrip().endswith(": none") for l in lines), out
    assert code == 1
    code = cp.main(["--next-id"])
    cap = capsys.readouterr()
    assert code == 2 and cap.out == ""
    assert "--next-id refused: git branch failed (exit 128)" in cap.err


@NO_GIT
def test_malformed_shallow_real_git_nothing_none(tmp_path):
    """(b) A1's repro, real git: a bad shallow line makes ls-tree, branch, blame and rev-list die
    (exit 128). No git-reading line says none, exit 1, and --next-id refuses (never `041`)."""
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "scratch-x", "099", [])
    _item(repo, "150", [], date="2026-11-20", logged=False)
    _write(repo, "logs/implementation/2026-11-20.md", "23:59 | I2 | 150 | 1 files changed | tests 1 passed in 0.01s\n")
    _daily(repo, "2026-11-20.md", INBOX_OK.format(sha="a" * 7), commit=False)
    _commit(repo, "late log")
    head, root = _commit_sha(repo), _root(repo)
    (repo / ".git" / "shallow").write_text(f"{head}\nzz\n", encoding="utf-8")
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", root, "--today", "2026-11-20")
    for p, lines in _git_lines(out).items():
        assert lines, f"{p} missing:\n{out}"
        assert not any(l.rstrip().endswith(": none") for l in lines), out
    assert code == 1, out
    assert _run(repo, "check_pipeline.py", "--next-id") == (2, "")


@NO_GIT
def test_non_utf8_shallow_line_no_traceback(tmp_path):
    """(c) a non-UTF-8 byte in git's output or error text is decoded with replace: no traceback,
    exit 1, and no git-reading line says none."""
    repo, c = _history(tmp_path)
    (repo / ".git" / "shallow").write_bytes(c.encode() + b"\n\xff\n")
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "check_pipeline.py"), "--untracked-from", c,
                        "--today", "2026-11-20"], cwd=repo, capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    assert b"Traceback" not in r.stderr, r.stderr
    assert r.returncode == 1, out
    for lines in _git_lines(out).values():
        assert not any(l.rstrip().endswith(": none") for l in lines), out
    # item 089: the shallow file is unreadable (not UTF-8), so the reason is shallow clone, never squash/rebase
    lines = out.splitlines()
    assert (f"UNTRACKED CHANGE: not checked (shallow clone; run git fetch --unshallow) (cutoff {c[:7]} from "
            f"--untracked-from)") in lines, out
    assert any(l.startswith("UNREADABLE: ") and "shallow (not UTF-8 at byte 41)" in l for l in lines), out
    assert "RULE NOT SEEN: not checked (shallow clone; run git fetch --unshallow)" in lines, out


@NO_GIT
def test_non_utf8_repo_path_is_still_git(tmp_path):
    """(c2) a repo whose path is not UTF-8 is still the top of a work tree (os.fsdecode on both
    sides), so the checks run instead of `not checked (no git)`."""
    repo = tmp_path / os.fsdecode(b"r\xff")
    try:
        repo.mkdir()
    except (OSError, UnicodeEncodeError) as e:
        pytest.skip(f"file system refuses a non-UTF-8 name: {e}")
    _git(repo, "init", "-q", "-b", "main")
    _item(repo, "150", ALL)
    c = _commit(repo, "cutoff")
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "check_pipeline.py"), "--untracked-from", c,
                        "--today", "2026-11-20"], cwd=repo, capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    assert b"Traceback" not in r.stderr, r.stderr
    assert "not checked (no git)" not in out, out
    assert "UNTRACKED CHANGE: none" in out, out


@NO_GIT
def test_uncommitted_log_file_is_skipped(tmp_path):
    """(d1) a log file not in HEAD's tree is uncommitted: it is not blamed (0 of 1 listed), so a
    late-looking line in it is not LOG TIME. The committed log is still checked."""
    repo, c = _history(tmp_path)
    _write(repo, "logs/implementation/2026-11-20.md", "23:59 | I3 | 150 | PASS | sent to audit: yes\n")
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", c, "--today", "2026-11-20")
    assert "LOG TIME: none" in out, out
    assert code == 0, out


@NO_GIT
def test_next_id_orphan_branch_without_work(tmp_path):
    """(d2) an orphan branch with no work/ adds no ID (041); with b099 open too the answer is 100."""
    repo = _repo_with_open_branch(tmp_path)
    _git(repo, "checkout", "-q", "--orphan", "nowork")
    _git(repo, "rm", "-rfq", ".")
    _write(repo, "README.md")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "orphan")
    _git(repo, "push", "-q", "origin", "nowork")
    _git(repo, "checkout", "-q", "-f", "main")
    assert _run(repo, "check_pipeline.py", "--next-id") == (0, "041\n")
    _branch_adds(repo, "b099", "099", [])
    assert _run(repo, "check_pipeline.py", "--next-id") == (0, "100\n")


@NO_GIT
def test_main_ahead_exact_ref_only(tmp_path):
    """(d3) refs/remotes/origin/main/x (one commit ahead) is not origin/main: no MAIN AHEAD line."""
    repo, c = _history(tmp_path)
    _git(repo, "checkout", "-q", "-b", "tmp")
    _write(repo, "notes/a.md")
    ahead = _commit(repo, "ahead")
    _git(repo, "checkout", "-q", "main")
    _git(repo, "branch", "-q", "-D", "tmp")
    _git(repo, "update-ref", "refs/remotes/origin/main/x", ahead)
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", c, "--today", "2026-11-20")
    assert "origin/main/x" in out, out                       # the ref is seen as an open branch
    assert "MAIN AHEAD" not in out, out


@NO_GIT
def test_branch_show_failure_skips_classify(tmp_path, monkeypatch, capsys):
    """(f) a branch step file git cannot show is a BRANCH ERROR and its item is not classified, so
    no false BRANCH SKIPPED is printed from an empty file. Control: unpatched, 060 is SKIPPED."""
    cp = _cp()
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "short", "060", ["05-build-report.md"])
    monkeypatch.chdir(repo)
    cp.main(["--untracked-from", _root(repo), "--today", "2026-11-20"])
    out = capsys.readouterr().out
    assert "BRANCH SKIPPED: 060 (origin/short:" in out and "BRANCH ERROR" not in out, out
    _patched_git(monkeypatch, cp, {("show", "origin/short:work/060/05-build-report.md"): ("", 128)})
    code = cp.main(["--untracked-from", _root(repo), "--today", "2026-11-20"])
    out = capsys.readouterr().out
    assert "BRANCH ERROR: origin/short (git show failed (exit 128))" in out, out
    assert "BRANCH SKIPPED: 060" not in out, out
    assert code == 1


@NO_GIT
def test_inbox_flag_die_is_loud(tmp_path, monkeypatch):
    """(g) --is-shallow-repository exit 128 (git died) is a failure; 129 keeps the 079 path
    (test_shallow_flag_unknown_no_file_is_full)."""
    cp = _cp()
    _daily(tmp_path, "2026-11-18.md", INBOX_OK.format(sha="a" * 7))
    monkeypatch.chdir(tmp_path)
    _patched_git(monkeypatch, cp, {("rev-parse", "--is-shallow-repository"): ("", 128)})
    text, failed = cp.inbox_section(Path("logs/audit"))
    assert failed is True
    assert "git rev-parse failed (exit 128)" in text


@NO_GIT
def test_open_branches_none_line(tmp_path):
    """(h1) a git repo with no remote branch says `OPEN BRANCHES: none`; without git there is no line."""
    repo, c = _history(tmp_path)
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", c, "--today", "2026-11-20")
    assert "OPEN BRANCHES: none" in out.splitlines(), out
    assert code == 0, out


def test_check_handoff_open_branches_states(tmp_path, monkeypatch, capsys):
    """(h2) check_handoff --all: a failed branch list is `not checked` and exit 1, never `no
    hand-off`; no git (None) is `no hand-off`, exit 0."""
    sys.path.insert(0, str(REPO / "scripts"))
    import check_handoff
    cp = sys.modules["check_pipeline"] if "check_pipeline" in sys.modules else _cp()
    (tmp_path / "work" / "150").mkdir(parents=True)
    monkeypatch.setattr(cp, "open_branches", lambda *a: "git branch failed (exit 128)")
    assert check_handoff.check_all(tmp_path / "work") == 1
    assert "150: not checked (open branches: git branch failed (exit 128))" in capsys.readouterr().out
    monkeypatch.setattr(cp, "open_branches", lambda *a: None)
    assert check_handoff.check_all(tmp_path / "work") == 0
    assert "150: no hand-off" in capsys.readouterr().out


# Item 084 (RI-010, RI-014): an item is judged by the rule in the tree of the commit that added its 05/06.
OLD_RULES = "CHECKLIST_FROM = 41\n"
NEW_RULES = "CHECKLIST_FROM = 41\nVERDICT_FROM = 71\nTESTS_FORMAT_FROM = 76\n"
SEEN_150 = ("RULE NOT SEEN: 150 (05 added in {sha} without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; "
            "06 added in {sha} without VERDICT_FROM (071): judged by no Sent-back check; item 084)")
NEW_I2_WANT = 'I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed, with its ` in <s>s` time>"'
NO_SENT_BACK = "06 Verdict is PASS but has no 'Sent back to: none' line (item 071)"


def _defective(root, item, i2="1 files changed | tests 9/9", date="2026-10-31"):
    """Item `item` with every step and log line, but 06 has no Sent back line and its I2 log line is `i2`."""
    _item(root, item, ALL, sent_back=None, date=date)
    with (root / "work" / item / "05-build-report.md").open("a", encoding="utf-8") as fh:
        fh.write("## Test output\n1 passed in 0.01s\n")     # item 090: a time, so LOG BATCH is computable
    log = root / "logs" / "implementation" / f"{date}.md"
    text = log.read_text(encoding="utf-8")
    old = f"12:00 | I2 | {item} | {FIELDS['I2']}\n"
    assert old in text
    log.write_text(text.replace(old, f"12:00 | I2 | {item} | {i2}\n"), encoding="utf-8")


def _rules_repo(tmp_path, i2="1 files changed | tests 9/9"):
    """The PR #33 + main shape. Root: RULE_FILE without the constants. main: item 150 (both defects).
    Branch rules off the root: the constants, then item 151 (both defects). Returns repo, root sha,
    150's add commit on main, and the rules commit; main is checked out."""
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "scripts/check_pipeline.py", OLD_RULES)
    root = _commit(repo, "root")
    _defective(repo, "150", i2)
    added = _commit(repo, "150 on main")
    _git(repo, "checkout", "-q", "-b", "rules", root)
    _write(repo, "scripts/check_pipeline.py", NEW_RULES)
    rules = _commit(repo, "rules")
    _defective(repo, "151", date="2026-11-01")              # own log files: the merge has no conflict
    _commit(repo, "151 on rules")
    _git(repo, "checkout", "-q", "main")
    return repo, root, added, rules


def _merge_main_into_rules(repo):
    _git(repo, "checkout", "-q", "rules")
    _git(repo, "merge", "-q", "--no-edit", "main")


def _pick(out, prefix):
    lines = [l for l in out.splitlines() if l.startswith(prefix)]
    assert len(lines) == 1, out
    return lines[0]


@NO_GIT
def test_rule_not_seen_item_merged_beside_rules_branch(tmp_path):
    """(a) 150 was built on main under a rule file without the constants: listed, not INCOMPLETE,
    before and after `rules` merges main. 151, built on `rules`, is still checked (M1, M2, M4)."""
    repo, root, added, _ = _rules_repo(tmp_path)
    args = ("--untracked-from", root, "--today", "2026-11-02")
    _, out = _run(repo, "check_pipeline.py", *args)
    assert _pick(out, "RULE NOT SEEN:") == SEEN_150.format(sha=added[:7]), out
    assert "150 (" not in _pick(out, "INCOMPLETE:"), out
    _merge_main_into_rules(repo)
    _, out = _run(repo, "check_pipeline.py", *args)
    assert _pick(out, "RULE NOT SEEN:") == SEEN_150.format(sha=added[:7]), out
    inc = _pick(out, "INCOMPLETE:")
    assert "150 (" not in inc, out
    assert f"151 (log line for I2 does not match its format (item 045): {NEW_I2_WANT}; {NO_SENT_BACK})" in inc, out


@NO_GIT
def test_rule_not_seen_still_checks_old_rule(tmp_path):
    """(b) 150's I2 line fails the old rule too (10/9): INCOMPLETE with the old hint; only its 06 pair is listed."""
    repo, root, added, _ = _rules_repo(tmp_path, i2="1 files changed | tests 10/9")
    _merge_main_into_rules(repo)
    _, out = _run(repo, "check_pipeline.py", "--untracked-from", root, "--today", "2026-11-02")
    assert _pick(out, "RULE NOT SEEN:") == (f"RULE NOT SEEN: 150 (06 added in {added[:7]} without VERDICT_FROM "
                                            "(071): judged by no Sent-back check; item 084)"), out
    inc = _pick(out, "INCOMPLETE:")
    assert ('150 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed | '
            'tests <pass>/<total> (pass <= total)")') in inc, out
    assert NO_SENT_BACK not in inc.split("151 (")[0], out


@NO_GIT
def test_unseen_item_that_passes_is_not_listed(tmp_path):
    """(c) the 073 case: added under the old rule file but its lines pass the new rules: not listed."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "scripts/check_pipeline.py", OLD_RULES)
    _item(repo, "152", ALL)
    root = _commit(repo, "root")
    _, out = _run(repo, "check_pipeline.py", "--untracked-from", root, "--today", "2026-11-02")
    assert _pick(out, "RULE NOT SEEN:") == "RULE NOT SEEN: none", out
    assert _pick(out, "INCOMPLETE:") == "INCOMPLETE: none", out


@NO_GIT
def test_rule_anchor_git_failure_is_incomplete(tmp_path, monkeypatch):
    """(d1) a failed add-commit log, ls-tree or show is strict plus an entry, never 'not seen' (M3; item
    088 added the ls-tree row; the HEAD verify row moved to test_anchor_env_reads_head_once)."""
    cp = _cp()
    repo, _, added, _ = _rules_repo(tmp_path)
    monkeypatch.chdir(repo)
    item = Path("work/150")
    log = ("log", "--no-renames", "--diff-filter=A", "--format=%H", "-1", "--", "work/150/05-build-report.md")
    ls = ("ls-tree", "--name-only", added, "--", "scripts/check_pipeline.py")
    for table in ({log: ("", 128)}, {("show", f"{added}:scripts/check_pipeline.py"): ("", 128)}, {ls: ("", 128)}):
        _patched_git(monkeypatch, cp, table)
        assert cp._rule_seen(item, "05", "TESTS_FORMAT_FROM", None) == (None, "05 anchor: git failed (item 084)")
        ns = []
        gaps = cp.incomplete(item, Path("logs"), env=None, not_seen=ns)
        assert f"log line for I2 does not match its format (item 045): {NEW_I2_WANT}" in gaps, gaps
        assert "05 anchor: git failed (item 084)" in gaps, gaps
        assert not [p for p in ns if p[1] == "05"], ns
        monkeypatch.undo()
        monkeypatch.chdir(repo)


@NO_GIT
def test_rule_anchor_without_rule_file(tmp_path):
    """(d2) the anchor commit has no scripts/check_pipeline.py: its own entry, strict, not listed.
    Pins that `git ls-tree <A> -- <path>` exits 0 with empty output for an absent path."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _defective(repo, "150")
    sha = _commit(repo, "no rule file")
    ls = subprocess.run(["git", "ls-tree", "--name-only", sha, "--", "scripts/check_pipeline.py"], cwd=repo,
                        capture_output=True, text=True)
    assert (ls.returncode, ls.stdout) == (0, "")
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", sha, "--today", "2026-11-02")
    inc = _pick(out, "INCOMPLETE:")
    assert f"05 anchor {sha[:7]} has no scripts/check_pipeline.py (item 084)" in inc, out
    assert f"06 anchor {sha[:7]} has no scripts/check_pipeline.py (item 084)" in inc, out
    assert NEW_I2_WANT in inc and NO_SENT_BACK in inc, out
    assert _pick(out, "RULE NOT SEEN:") == "RULE NOT SEEN: none", out
    assert code == 1, out


@NO_GIT
def test_rule_not_seen_shallow_and_no_git(tmp_path):
    """(e1) a shallow clone is not checked and strict (M5); unshallowed it is the control.
    (e2) without git: not checked, and 150's INCOMPLETE text is today's exactly."""
    repo, root, _, rules = _rules_repo(tmp_path / "g")
    _merge_main_into_rules(repo)
    args = ("--untracked-from", root, "--today", "2026-11-02")
    _shallow(repo, rules)
    _, out = _run(repo, "check_pipeline.py", *args)
    assert _pick(out, "RULE NOT SEEN:") == "RULE NOT SEEN: not checked (shallow clone; run git fetch --unshallow)", out
    assert "150 (" in _pick(out, "INCOMPLETE:"), out
    _unshallow(repo)
    _, out = _run(repo, "check_pipeline.py", *args)
    assert "150 (" not in _pick(out, "INCOMPLETE:"), out
    assert _pick(out, "RULE NOT SEEN:").startswith("RULE NOT SEEN: 150 ("), out

    plain = tmp_path / "plain"
    _defective(plain, "150")
    code, out = _run(plain, "check_pipeline.py", "--today", "2026-11-02")
    assert _pick(out, "RULE NOT SEEN:") == "RULE NOT SEEN: not checked (no git)", out
    assert _pick(out, "INCOMPLETE:") == (f"INCOMPLETE: 150 (log line for I2 does not match its format (item 045): "
                                         f"{NEW_I2_WANT}; {NO_SENT_BACK})"), out
    assert code == 1, out


@NO_GIT
def test_rule_seen_positive_control_on_head(monkeypatch):
    """(f1) on this repo: 076's 05 and 06 were added under both constants; 083's under neither (M2)."""
    flag = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8")
    if flag.returncode != 0 or flag.stdout.strip() != "false":
        pytest.skip("REPO is a shallow clone: no anchor is read (item 084); run git fetch --unshallow")
    cp = _cp()
    monkeypatch.chdir(REPO)
    assert cp._rule_seen(Path("work/076"), "05", "TESTS_FORMAT_FROM", None)[0] is True
    assert cp._rule_seen(Path("work/076"), "06", "VERDICT_FROM", None)[0] is True
    assert cp._rule_seen(Path("work/083"), "05", "TESTS_FORMAT_FROM", None) == (False, "cfc0634")
    assert cp._rule_seen(Path("work/083"), "06", "VERDICT_FROM", None) == (False, "cfc0634")


# Item 084 round 2 (RI-012): the constant inside other text is not the constant (F1 in work/084/06).
EMBEDDED_RULES = {
    "comment": "CHECKLIST_FROM = 41\n# VERDICT_FROM = 71 is item 071\n# TESTS_FORMAT_FROM = 76 is item 076\n",
    "longer name": "CHECKLIST_FROM = 41\nOLD_VERDICT_FROM = 71\nOLD_TESTS_FORMAT_FROM = 76\n",
    "string": 'CHECKLIST_FROM = 41\nx = "VERDICT_FROM = 71"\ny = "TESTS_FORMAT_FROM = 76"\n',
    "all three": ('CHECKLIST_FROM = 41\n# VERDICT_FROM = 71 is item 071\nOLD_VERDICT_FROM = 71\n'
                  'OLD_TESTS_FORMAT_FROM = 76\nx = "VERDICT_FROM = 71"\n'),
}


@NO_GIT
@pytest.mark.parametrize("form", sorted(EMBEDDED_RULES))
def test_rule_seen_ignores_constant_inside_other_text(tmp_path, monkeypatch, form):
    """(i) the anchor's RULE_FILE names each constant only in a comment, a longer name or a string:
    (False, sha7) for both, 150 is listed in RULE NOT SEEN and not INCOMPLETE (M6 no ^/re.M, M7 plain `in`).
    Known gap (docstring): a column-0 `<CONST> = ` line inside a triple-quoted string still reads as seen."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "scripts/check_pipeline.py", EMBEDDED_RULES[form])
    root = _commit(repo, "root")
    _defective(repo, "150")
    added = _commit(repo, "150 on main")
    cp = _cp()
    monkeypatch.chdir(repo)
    assert cp._rule_seen(Path("work/150"), "05", "TESTS_FORMAT_FROM", None) == (False, added[:7])
    assert cp._rule_seen(Path("work/150"), "06", "VERDICT_FROM", None) == (False, added[:7])
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", root, "--today", "2026-11-02")
    assert _pick(out, "RULE NOT SEEN:") == SEEN_150.format(sha=added[:7]), out
    assert _pick(out, "INCOMPLETE:") == "INCOMPLETE: none", out
    assert code == 0, out


# Item 088 (RI-002, RI-014): an unknown anchor (uncommitted 05/06, unborn HEAD) keeps the strict rule.
INC_150 = (f"INCOMPLETE: 150 (log line for I2 does not match its format (item 045): {NEW_I2_WANT}; "
           f"{NO_SENT_BACK})")


@NO_GIT
def test_rule_anchor_uncommitted_step_is_strict(tmp_path, monkeypatch):
    """(u) 150's 05 and 06 are in the tree but in no commit: `git log --diff-filter=A` exits 0 with no
    output, so no anchor is read; 150 stays INCOMPLETE with today's text and is not listed (M-a)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "scripts/check_pipeline.py", NEW_RULES)
    root = _commit(repo, "root")
    _defective(repo, "150")
    log = subprocess.run(["git", "log", "--no-renames", "--diff-filter=A", "--format=%H", "-1", "--",
                          "work/150/05-build-report.md"], cwd=repo, capture_output=True, text=True)
    assert (log.returncode, log.stdout) == (0, "")
    _, out = _run(repo, "check_pipeline.py", "--untracked-from", root, "--today", "2026-11-02")
    assert _pick(out, "INCOMPLETE:") == INC_150, out
    assert _pick(out, "RULE NOT SEEN:") == "RULE NOT SEEN: none", out
    cp = _cp()
    monkeypatch.chdir(repo)
    assert cp._rule_seen(Path("work/150"), "05", "TESTS_FORMAT_FROM", None) == (None, "")
    assert cp._rule_seen(Path("work/150"), "06", "VERDICT_FROM", None) == (None, "")


@NO_GIT
def test_rule_anchor_unborn_head_is_strict(tmp_path, monkeypatch):
    """(h) no commit at all (unborn HEAD): `rev-parse --verify -q HEAD` exits 1, so _anchor_env gives
    "unborn HEAD": not checked, no anchor is read and 150 keeps today's strict text (M-b, M-b', M-g).
    The exit code is not pinned: it is 1 via UNCOMMITTED STEP."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "scripts/check_pipeline.py", NEW_RULES)
    _defective(repo, "150")
    head = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], cwd=repo, capture_output=True, text=True)
    assert head.returncode == 1
    flag = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=repo, capture_output=True,
                          text=True)
    assert flag.stdout.strip() == "false"
    _, out = _run(repo, "check_pipeline.py", "--today", "2026-11-02")
    assert _pick(out, "INCOMPLETE:") == INC_150, out
    assert _pick(out, "RULE NOT SEEN:") == "RULE NOT SEEN: not checked (unborn HEAD)", out
    cp = _cp()
    monkeypatch.chdir(repo)
    assert cp._anchor_env() == ("unborn HEAD", False)
    assert cp._rule_seen(Path("work/150"), "05", "TESTS_FORMAT_FROM", "unborn HEAD") == (None, "")
    assert cp._rule_seen(Path("work/150"), "06", "VERDICT_FROM", "unborn HEAD") == (None, "")


@NO_GIT
def test_anchor_env_reads_head_once(tmp_path, monkeypatch):
    """Item 088: _anchor_env's HEAD verify. Exit 0 on a committed repo -> (None, False); another exit
    (128) -> not checked and failed (M-e); `_git` None for the verify alone -> "no git" (M-h)."""
    cp = _cp()
    repo, _ = _history(tmp_path)
    monkeypatch.chdir(repo)
    assert cp._anchor_env() == (None, False)
    verify = ("rev-parse", "--verify", "-q", "HEAD")
    _patched_git(monkeypatch, cp, {verify: ("", 128)})
    assert cp._anchor_env() == ("git rev-parse --verify HEAD failed (exit 128)", True)
    _patched_git(monkeypatch, cp, {verify: None})
    assert cp._anchor_env() == ("no git", False)


@NO_GIT
def test_anchor_env_failure_exits_1(tmp_path, monkeypatch, capsys):
    """Item 088 (RI-014): a failed HEAD verify prints not checked with the exit code and main exits 1;
    the same clean repo (150 complete, the (i) rule file) unpatched exits 0 (M-f). `_anchor_env` is patched, not `_git`, because
    _inbox_gate runs the same `rev-parse --verify -q HEAD` command."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "scripts/check_pipeline.py", EMBEDDED_RULES["comment"])
    root = _commit(repo, "root")
    _item(repo, "150", ALL)                                 # complete: no gate fires, so INCOMPLETE stays none
    _commit(repo, "150 on main")
    cp = _cp()
    monkeypatch.chdir(repo)
    args = ["--untracked-from", root, "--today", "2026-11-02"]
    assert cp.main(args) == 0, capsys.readouterr().out
    capsys.readouterr()
    monkeypatch.setattr(cp, "_anchor_env", lambda: ("git rev-parse --verify HEAD failed (exit 128)", True))
    code = cp.main(args)
    out = capsys.readouterr().out
    assert _pick(out, "RULE NOT SEEN:") == ("RULE NOT SEEN: not checked (git rev-parse --verify HEAD failed "
                                            "(exit 128))"), out
    assert _pick(out, "INCOMPLETE:") == "INCOMPLETE: none", out
    assert code == 1, out


def test_write_log_stays_numeric(tmp_path):
    """(g) --log never applies an old rule: 083's old-form I2 line is still refused (exit 2)."""
    _request(tmp_path, "083")
    code, err = _log(tmp_path, "I2", "083", "2 files changed | tests 344/344")
    assert code == 2 and "as printed" in err, err
    assert not (tmp_path / "logs").exists()


# Item 086 (RI-010): rule C (LOG BATCH) and rule D (--log refuses while a later step file exists).
I2_083 = "2 files changed | tests 344 passed, 1 skipped in 48.51s"


def _batch_item(root, item, research=(), impl=(), t05=None, t06=None, full=False):
    """A rule-C fixture: request.md, log lines (research / implementation: (date, HH:MM, agent, fields)),
    05 with a `## Test output` section and 06 with a `## Tests re-run` section holding the given text
    (None = no file). full=True also writes 01-04 and a complete 06/07, so check_pipeline's other checks
    pass and its exit code is LOG BATCH's. Item 082: with full=True, 05 also gets a `Suite:` line (above
    `## Test output`) equal to the tests part of the last I2 field in `impl`."""
    d = root / "work" / item
    d.mkdir(parents=True, exist_ok=True)
    (d / "request.md").write_text(f"# Work item {item}\nScope: FULL\nDate: 2026-11-20\n", encoding="utf-8")
    for team, rows in (("research", research), ("implementation", impl)):
        for date, hhmm, agent, fields in rows:
            log = root / "logs" / team / f"{date}.md"
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("a", encoding="utf-8") as fh:
                fh.write(f"{hhmm} | {agent} | {item} | {fields}\n")
    if t05 is not None:
        i2 = [f for _, _, agent, f in impl if agent == "I2"]
        suite = f"Suite: {i2[-1].split(' | tests ', 1)[1]}\n" if full and i2 else ""   # item 082 (full only)
        (d / "05-build-report.md").write_text(f"# 05\n{suite}## Test output (pasted, not summarized)\n{t05}\n"
                                              f"## Deviations from plan\n", encoding="utf-8")
    if t06 is not None:
        head = "Verdict: PASS (round 1)\nSent back to: none\nRecurring issues checked: RI-010\n" if full else ""
        (d / "06-verification.md").write_text(f"{head}## Tests re-run (output)\n{t06}\n## Findings\n",
                                              encoding="utf-8")
    if full:
        for s in ("01", "02", "03", "04"):
            (d / STEP_NAMES[s]).write_text("x\n", encoding="utf-8")
        (d / "07-audit-task.md").write_text("x\nA1 result: PASS (test)\n", encoding="utf-8")


STEP_NAMES = {"01": "01-research.md", "02": "02-improvements.md", "03": "03-handoff.md",
              "04": "04-build-plan.md", "05": "05-build-report.md", "06": "06-verification.md"}
BATCH_DAY = "2026-11-20"


def _six(t, i2=I2_083, i3="PASS | sent to audit: yes"):
    """083's six lines, all at minute t (research R1-R3, implementation I1, I2, I3)."""
    return ([(BATCH_DAY, t, "R1", "brief written | 0"), (BATCH_DAY, t, "R2", "3 for / 3 against | languages: N/A"),
             (BATCH_DAY, t, "R3", "4 verified, 0 fixed, 0 removed | READY")],
            [(BATCH_DAY, t, "I1", "FIT | 2 files planned"), (BATCH_DAY, t, "I2", i2), (BATCH_DAY, t, "I3", i3)])


def _impl(i1, i2, i3, item_i2="1 files changed | tests 1 passed in 0.01s"):
    return [(BATCH_DAY, i1, "I1", "FIT | 1 files planned"), (BATCH_DAY, i2, "I2", item_i2), (BATCH_DAY, i3, "I3", "PASS | sent to audit: yes")]


def _bl(root, excepted=None):
    cp = _cp()
    return cp.batch_log_items(root / "work", root / "logs", excepted={} if excepted is None else excepted)


def test_batch_083_shape_is_flagged(tmp_path):
    """086 (a): 083's batch (six lines in one minute, 48.51 + 47.57 s of pytest runs) is flagged, and
    check_pipeline exits 1 on it; the same item with spaced lines prints none and exits 0."""
    r, i = _six("10:15")
    _batch_item(tmp_path, "999", r, i, "```\n344 passed, 1 skipped in 48.51s\n```", "344 passed, 1 skipped in 47.57s",
                full=True)
    res = _bl(tmp_path)
    assert res["flagged_ids"] == ["999"] and res["checked"] == 1, res
    assert res["flagged"] == ["999 (96.08 s of pytest runs between 2026-11-20 10:15 and 10:15 UTC, limit 60 s; "
                              "impossible under the run-item order, item 086)"]
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-21")
    assert "LOG BATCH: 999 (" in out and code == 1, out
    spaced = tmp_path / "spaced"
    r, _ = _six("10:15")
    _batch_item(spaced, "999", r, _impl("10:20", "10:30", "10:40", I2_083), "344 passed, 1 skipped in 48.51s",
                "344 passed, 1 skipped in 47.57s", full=True)
    code, out = _run(spaced, "check_pipeline.py", "--today", "2026-11-21")
    assert "LOG BATCH: none" in out.splitlines() and code == 0, out


@NO_GIT
def test_batch_083_flagged_on_repo_data():
    """086 (b), RI-010's condition: on this repo's own work/ and logs/, with the exception emptied, 083
    is flagged."""
    cp = _cp()
    res = cp.batch_log_items(REPO / "work", REPO / "logs", excepted={})
    assert "083" in res["flagged_ids"], res


def test_log_batch_except_is_pinned():
    """086: the exception is exactly {083}, and 083 is not in LOG_TIME_EXCEPT (its lines are not after
    their commit). Never add a new item here (M8)."""
    cp = _cp()
    assert set(cp.LOG_BATCH_EXCEPT) == {"083"}
    assert "083" not in cp.LOG_TIME_EXCEPT


def test_batch_079_real_lines_not_flagged(tmp_path):
    """086 N1: 079's real lines (two I rounds over 11-19/11-20), 05 90.93, 06 90.21: not flagged."""
    research = [("2026-11-19", "23:25", "R1", "brief written | 9"),
                ("2026-11-19", "23:28", "R2", "3 for / 3 against | languages: N/A"),
                ("2026-11-19", "23:35", "R3", "32 verified, 4 fixed, 1 removed | READY")]
    impl = [("2026-11-19", "23:39", "I1", "FIT WITH CHANGES | 4 files planned"),
            ("2026-11-20", "02:02", "I2", "4 files changed | tests 568 passed, 1 skipped in 90.93s (0:01:30)"),
            ("2026-11-20", "02:10", "I3", "FAIL | sent to audit: no"),
            ("2026-11-20", "02:15", "I2", "2 files changed | tests 1 failed, 568 passed, 1 skipped in 87.19s (0:01:27)"),
            ("2026-11-20", "02:22", "I3", "PASS | sent to audit: yes")]
    _batch_item(tmp_path, "999", research, impl, "568 passed, 1 skipped in 90.93s (0:01:30)",
                "568 passed, 1 skipped in 90.21s (0:01:30)")
    res = _bl(tmp_path)
    assert res["flagged"] == [] and res["checked"] == 1 and res["not_computable"] == [], res


@pytest.mark.parametrize("t05, t06, end, flagged", [("30.00", "30.01", "10:00", True),
                                                     ("29.99", "30.01", "10:00", False),
                                                     ("0.02", "119.99", "10:01", True)])
def test_batch_boundary_delta0(tmp_path, t05, t06, end, flagged):
    """086 N2 (M1): Δ0, limit 60 s, k = 2: 30.00 + 30.01 - 0.01 = 60.00 >= 60 is flagged;
    29.99 + 30.01 - 0.01 = 59.99 is not. (Two distinct values: equal ones are a copy, N4.)
    Round 2, R2-3 (iv) (M15): no such pair falls below 60 in float, but at Δ1 (I2/I3 10:01, limit 120)
    float 0.02 + 119.99 - 0.01 is 119.99999999999999, the first of 6302 such pairs; round(..., 3) makes
    it the exact 120.000 >= 120, flagged."""
    _batch_item(tmp_path, "999", impl=_impl("10:00", end, end),
                t05=f"1 passed in {t05}s", t06=f"1 passed in {t06}s")
    assert (_bl(tmp_path)["flagged_ids"] == ["999"]) is flagged


def test_batch_delta1_limit_is_120(tmp_path):
    """086 N3 (M1b): Δ1 (I1 10:00, I2/I3 10:01) gives limit (1+1)*60 = 120 s: 45.00 + 45.01 - 0.01 = 90.00
    is not flagged (with the +1 dropped, 90.00 >= 60 would be)."""
    _batch_item(tmp_path, "999", impl=_impl("10:00", "10:01", "10:01"), t05="1 passed in 45.00s",
                t06="1 passed in 45.01s")
    res = _bl(tmp_path)
    assert res["flagged"] == [] and res["checked"] == 1 and res["not_computable"] == [], res


def test_batch_copy_of_05_in_06_is_dropped(tmp_path):
    """086 N4 (M3): 06 quotes only 05's 40.00 s: a copy, dropped, k = 1: 39.995 < 60, not flagged."""
    _batch_item(tmp_path, "999", impl=_impl("10:00", "10:00", "10:00"), t05="1 passed in 40.00s",
                t06="05 had:\n1 passed in 40.00s")
    res = _bl(tmp_path)
    assert res["flagged"] == [] and res["checked"] == 1 and res["not_computable"] == [], res


def test_batch_untimed_item_is_not_computable(tmp_path):
    """086 N5 (M4): six lines in one minute but no pytest time anywhere: listed not computable, never
    flagged, never read as 0 or 60 s; check_pipeline exits 0. Item 090: on 089 (below TIMED_FROM) it is text
    only; the 990 twin is also INCOMPLETE: its untimed I2 line and `LOG BATCH not computable` (exit 1)."""
    r, i = _six("10:15", i2="2 files changed | tests 3 passed")
    _batch_item(tmp_path, "089", r, i, "3 passed", "3 passed", full=True)
    res = _bl(tmp_path)
    assert res["flagged"] == [] and res["not_computable"] == [("089", "no pytest time in 05/06/I2 line")], res
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-21")
    assert "LOG BATCH: none; not computable: 089: no pytest time in 05/06/I2 line" in out.splitlines(), out
    assert "INCOMPLETE: none" in out.splitlines(), out
    assert code == 0, out
    twin = tmp_path / "twin"
    _batch_item(twin, "990", r, i, "3 passed", "3 passed", full=True)
    code, out = _run(twin, "check_pipeline.py", "--today", "2026-11-21")
    inc = _pick(out, "INCOMPLETE:")
    assert 'log line for I2 does not match its format (item 045): I2 wants "<n> files changed | tests <last line ' \
           'of python3 -m pytest -q, as printed, with its ` in <s>s` time>"' in inc, out
    assert "LOG BATCH not computable: no pytest time in 05/06/I2 line (item 090)" in inc, out
    assert code == 1, out


def test_batch_interleaved_items_not_flagged(tmp_path):
    """086 N6: three items' lines interleaved in one minute (the 23:27 pattern), each item's own
    I1 -> I3 at least 5 minutes, 30 s runs: none flagged (C is per item)."""
    for n, item in enumerate(("997", "998", "999")):
        _batch_item(tmp_path, item, [(BATCH_DAY, "23:27", "R1", "brief written | 1")],
                    _impl("23:27", f"23:3{n}", f"23:3{n + 2}"), "1 passed in 30.00s", "1 passed in 30.50s")
    res = _bl(tmp_path)
    assert res["flagged"] == [] and res["checked"] == 3 and res["not_computable"] == [], res


def test_batch_sections_and_largest_value(tmp_path):
    """086 N7 (M11): a level-1 `# Round 1` heading ends the round-2 `## Tests re-run` section; the 80.00 s
    under it is outside both sections. t06 is the largest in-section value (50.00, not the last 10.00):
    Σ = 20.00 + 50.00 = 70.00, flagged (69.99 >= 60)."""
    t06 = ("1 passed in 50.00s\n# Round 1 (kept as written)\n1 passed in 80.00s\n"
           "## Tests re-run (output)\n1 passed in 10.00s")
    _batch_item(tmp_path, "999", impl=_impl("10:00", "10:00", "10:00"), t05="1 passed in 20.00s", t06=t06)
    res = _bl(tmp_path)
    assert res["flagged_ids"] == ["999"] and res["flagged"][0].startswith("999 (70.00 s of"), res


def test_batch_summary_in_test_id_is_not_a_run(tmp_path):
    """086 N8 (M9, RI-012): a pytest summary inside a FAILED test ID (076/05 L39) is not read; only a
    line that starts with the summary is. 1.00 + 2.00 is not flagged (59.00 + 2.00 would be)."""
    t05 = "FAILED tests/x.py::t[1 failed, 2 passed in 59.00s]\n1 failed, 2 passed in 1.00s"
    _batch_item(tmp_path, "999", impl=_impl("10:00", "10:00", "10:00"), t05=t05, t06="2 passed in 2.00s")
    res = _bl(tmp_path)
    assert res["flagged"] == [] and res["checked"] == 1 and res["not_computable"] == [], res


def test_batch_research_line_at_i2_minute_is_before(tmp_path):
    """086 N9 (FAST shape, no I1): R3 10:15 in the research log counts as before I2 10:15, so start is
    10:15, Δ0 and 40.00 + 39.00 - 0.01 = 78.99 >= 60 is flagged."""
    research = [(BATCH_DAY, "10:10", "R1", "brief written | 1"), (BATCH_DAY, "10:15", "R3", "1 verified, 0 fixed, 0 removed | READY")]
    impl = [(BATCH_DAY, "10:15", "I2", "1 files changed | tests 1 passed"), (BATCH_DAY, "10:15", "I3", "PASS | sent to audit: yes")]
    _batch_item(tmp_path, "999", research, impl, "1 passed in 40.00s", "1 passed in 39.00s")
    assert _bl(tmp_path)["flagged_ids"] == ["999"]


def test_batch_malformed_last_line_still_ends_the_window(tmp_path):
    """086 N10 (M10): a malformed `10:05 | I3 | 999 | PASS | see 06` still marks when I3 logged, so the
    window is 10:00 -> 10:05 (Δ5, limit 360) and 98.99 s is not flagged."""
    impl = _impl("10:00", "10:00", "10:00") + [(BATCH_DAY, "10:05", "I3", "PASS | see 06")]
    _batch_item(tmp_path, "999", impl=impl, t05="1 passed in 50.00s", t06="1 passed in 49.00s")
    res = _bl(tmp_path)
    assert res["flagged"] == [] and res["checked"] == 1 and res["not_computable"] == [], res


def test_batch_unreadable_06_is_not_computable(tmp_path):
    """086 N11: a non-UTF-8 06 is not computable with the file named, never a crash or a pass."""
    _batch_item(tmp_path, "999", impl=_impl("10:00", "10:00", "10:00"), t05="1 passed in 50.00s")
    (tmp_path / "work" / "999" / "06-verification.md").write_bytes(b"\xff\xfe 1 passed in 49.00s\n")
    res = _bl(tmp_path)
    assert res["flagged"] == [] and len(res["not_computable"]) == 1, res
    item, why = res["not_computable"][0]
    assert item == "999" and why.endswith("work/999/06-verification.md unreadable"), res


def test_batch_open_round_and_no_line_before_i2(tmp_path):
    """086 N12: an I2 line with no I3 after it is in progress, not flagged; an item whose first line is
    I2 is not computable (no line before I2)."""
    _batch_item(tmp_path, "998", impl=[(BATCH_DAY, "10:00", "I2", "1 files changed | tests 1 passed in 50.00s")],
                t05="1 passed in 50.00s")
    _batch_item(tmp_path, "999", impl=[(BATCH_DAY, "10:00", "I2", "1 files changed | tests 1 passed in 50.00s"),
                                       (BATCH_DAY, "10:00", "I3", "PASS | sent to audit: yes")],
                t05="1 passed in 50.00s", t06="1 passed in 49.00s")
    res = _bl(tmp_path)
    assert res["in_progress"] == ["998"] and res["flagged"] == [], res
    assert res["not_computable"] == [("999", "no line before I2")], res


def test_batch_open_round_keyed_on_last_i2(tmp_path):
    """086 N12b (M13, round 2 R2-3 (i)): I1, I2, I3 FAIL at 10:00, then a round-2 I2 at 10:30 with no
    I3 after it: the round is open, so the item is in progress, not flagged and not checked (its
    round-2 run lies after the last I3, outside the window)."""
    impl = [(BATCH_DAY, "10:00", "I1", "FIT | 1 files planned"),
            (BATCH_DAY, "10:00", "I2", "1 files changed | tests 1 passed in 50.00s"),
            (BATCH_DAY, "10:00", "I3", "FAIL | sent to audit: no"),
            (BATCH_DAY, "10:30", "I2", "1 files changed | tests 1 passed in 50.00s")]
    _batch_item(tmp_path, "999", impl=impl, t05="1 passed in 50.00s", t06="1 passed in 49.00s")
    res = _bl(tmp_path)
    assert res["in_progress"] == ["999"] and res["flagged"] == [] and res["checked"] == 0, res
    assert res["not_computable"] == [], res


def test_batch_unreadable_log_file_makes_every_item_not_computable(tmp_path):
    """086 N13 (M14, round 2 R2-3 (ii)): a log file that is not UTF-8 can't be attributed to an item,
    and a lost line could move start or end, so every item is not computable with that file named;
    never skipped silently, never flagged, no traceback."""
    for item in ("998", "999"):
        _batch_item(tmp_path, item, impl=_impl("10:00", "10:20", "10:40"), t05="1 passed in 30.00s",
                    t06="1 passed in 31.00s")
    bad = tmp_path / "logs" / "implementation" / "2026-11-19.md"
    bad.write_bytes(b"\xff\xfe")
    res = _bl(tmp_path)
    assert res["flagged"] == [] and [i for i, _ in res["not_computable"]] == ["998", "999"], res
    assert all(why.endswith(f"{bad.as_posix()} unreadable") for _, why in res["not_computable"]), res
    # 089 6f: the same tree through the CLI: no traceback, exit 1, the file on UNREADABLE (item 089)
    code, out, err = _run3(tmp_path, "--today", "2026-11-20")
    assert b"Traceback" not in err, err
    assert code == 1, out
    assert "UNREADABLE: logs/implementation/2026-11-19.md (not UTF-8 at byte 0)" in out.splitlines(), out
    batch = [l for l in out.splitlines() if l.startswith("LOG BATCH:")][0]
    assert ("not computable: 998: logs/implementation/2026-11-19.md unreadable; "
            "999: logs/implementation/2026-11-19.md unreadable") in batch, out


def test_batch_invalid_log_time_is_not_computable(tmp_path):
    """086 N14 (round 2 R2-3 (iii)): an 083-shaped item with one more line timed 25:00 is not
    computable (log line with no valid time), never a crash and never a silent skip (dropping the line
    could shorten the window)."""
    r, i = _six("10:15")
    _batch_item(tmp_path, "999", r, i + [(BATCH_DAY, "25:00", "I3", "PASS | sent to audit: yes")],
                "344 passed, 1 skipped in 48.51s", "344 passed, 1 skipped in 47.57s")
    res = _bl(tmp_path)
    assert res["flagged"] == [] and res["not_computable"] == [("999", "log line with no valid time")], res


def _steps(root, item, steps):
    for s in steps:
        (root / "work" / item / STEP_NAMES[s]).write_text("x\n", encoding="utf-8")


def _log_line(root, team, item, agent, fields):
    log = root / "logs" / team / "2000-01-01.md"             # never today's file, which --log writes
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"10:00 | {agent} | {item} | {fields}\n")


def _written(root, agent, item):
    team = "research" if agent[0] == "R" else "implementation"
    return any(f" | {agent} | {item} | " in f.read_text(encoding="utf-8")
               for f in (root / "logs" / team).glob("*.md") if f.name != "2000-01-01.md")


def test_log_refused_after_later_steps(tmp_path):
    """086 D1 (M5): `--log R1` with 01-06 present (083's batch shape) is refused, exit 2, the later files
    named, nothing written."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", ("01", "02", "03", "04", "05", "06"))
    code, err = _log(tmp_path, "R1", "999", "brief written | 0")
    assert code == 2, err
    assert ("--log refused: work/999/ already has 02-improvements.md 03-handoff.md 04-build-plan.md "
            "05-build-report.md 06-verification.md after R1's step") in err, err
    assert not (tmp_path / "logs").exists()


def test_log_written_when_no_later_step(tmp_path):
    """086 D2: only 01 present: R1's line is written."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", ("01",))
    code, err = _log(tmp_path, "R1", "999", "brief written | 0")
    assert code == 0, err
    assert _written(tmp_path, "R1", "999")


def test_log_after_i3_fail_is_written(tmp_path):
    """086 D3 (M6): 076's order: I1, I2, then `I3 | FAIL`; the round-2 `--log I1` and `--log I2` with 05
    and 06 present are written (the item was sent back). Item 090: 06 still says FAIL (round rule (b))."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", ("01", "02", "03", "04", "05", "06"))
    (tmp_path / "work" / "999" / "06-verification.md").write_text("Verdict: FAIL (round 1)\nx\n", encoding="utf-8")
    for agent, fields in (("I1", "FIT | 1 files planned"), ("I2", "1 files changed | tests 1 passed in 0.01s"),
                          ("I3", "FAIL | sent to audit: no")):
        _log_line(tmp_path, "implementation", "999", agent, fields)
    assert _log(tmp_path, "I1", "999", "FIT | 1 files planned")[0] == 0
    assert _log(tmp_path, "I2", "999", "1 files changed | tests 1 passed in 0.01s")[0] == 0
    assert _written(tmp_path, "I1", "999") and _written(tmp_path, "I2", "999")


@pytest.mark.parametrize("team, agent, fields, steps, verdict", [
    ("research", "R3", "5 verified, 0 fixed, 0 removed | BLOCKED", ("01", "02", "03"),
     ("03", "Status: BLOCKED (x)\n")),                                                         # D4 (M6b)
    ("implementation", "I1", "NOT A FIT | 0 files planned", ("01", "02", "03", "04"),
     ("04", "Fit verdict: NOT A FIT\n")),                                                      # D5
])
def test_log_after_blocked_or_not_a_fit_is_written(tmp_path, team, agent, fields, steps, verdict):
    """086 D4, D5: after an R3 BLOCKED line (group 2 of R3's format) or an I1 NOT A FIT line, the R1
    re-log with later files present is written. Item 090: the sender's file still shows its send-back
    verdict (round rule (b))."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", steps)
    (tmp_path / "work" / "999" / STEP_NAMES[verdict[0]]).write_text(verdict[1] + "x\n", encoding="utf-8")
    _log_line(tmp_path, team, "999", agent, fields)
    code, err = _log(tmp_path, "R1", "999", "brief written | 0")
    assert code == 0, err


def test_log_after_a1_fail_is_written(tmp_path):
    """086 D6: 07 with `A1 result: FAIL` (069/070 shape): `--log I1` with 05/06 present is written."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", ("01", "02", "03", "04", "05", "06"))
    (tmp_path / "work" / "999" / "07-audit-task.md").write_text("x\nA1 result: FAIL (test)\n", encoding="utf-8")
    code, err = _log(tmp_path, "I1", "999", "FIT | 1 files planned")
    assert code == 0, err


def test_log_verdict_words_in_free_text_are_not_send_backs(tmp_path):
    """086 D7 (M7, RI-012): `READY (was BLOCKED)` and `PASS | sent to audit: yes (FAIL fixed)` are not
    send-backs (verdicts by fullmatch group), so `--log R1` with 02 present is refused."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", ("01", "02"))
    _log_line(tmp_path, "research", "999", "R3", "5 verified, 0 fixed, 0 removed | READY (was BLOCKED)")
    _log_line(tmp_path, "implementation", "999", "I3", "PASS | sent to audit: yes (FAIL fixed)")
    code, err = _log(tmp_path, "R1", "999", "brief written | 0")
    assert code == 2 and "already has 02-improvements.md after R1's step" in err, err


def test_log_07_never_counts_as_later(tmp_path):
    """086 D8: RESEARCH ONLY shape: 01, 03 and R3's 07 present; `--log R3` is written (07 never counts)."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", ("01", "03"))
    (tmp_path / "work" / "999" / "07-audit-task.md").write_text("x\n", encoding="utf-8")
    code, err = _log(tmp_path, "R3", "999", "1 verified, 0 fixed, 0 removed | READY")
    assert code == 0, err


def test_log_later_files_of_another_item_do_not_count(tmp_path):
    """086 D9: item 998 with 01-06 present does not refuse item 999's R1 (only 01 present)."""
    _request(tmp_path, "998")
    _steps(tmp_path, "998", ("01", "02", "03", "04", "05", "06"))
    _request(tmp_path, "999")
    _steps(tmp_path, "999", ("01",))
    code, err = _log(tmp_path, "R1", "999", "brief written | 0")
    assert code == 0, err


def test_log_format_refusal_runs_first(tmp_path):
    """086 D10: bad fields with later files present give the existing format refusal, unchanged."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", ("01", "02"))
    code, err = _log(tmp_path, "R1", "999", "see 01")
    assert code == 2 and err.startswith('--log refused: R1 | 999 | see 01 does not match "brief written | '), err
    assert "item 086" not in err and not (tmp_path / "logs").exists()


# Item 081 round 2 (RI-014): blame failure of a committed log; branches with no common history.
def _orphan(repo, name, files):
    """Push an orphan branch `name` holding `files` {path: text} (README.md when empty); back on main."""
    _git(repo, "checkout", "-q", "--orphan", name)
    _git(repo, "rm", "-rfq", ".")
    for path, text in (files or {"README.md": "x\n"}).items():
        _write(repo, path, text)
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "orphan")
    _git(repo, "push", "-q", "origin", name)
    _git(repo, "checkout", "-q", "-f", "main")


@NO_GIT
def test_blame_failure_of_committed_log_is_an_entry(tmp_path, monkeypatch, capsys):
    """R2-a: ls-tree succeeds and 1 of the 2 committed log files fails blame -> exactly 1 entry,
    LOG TIME names it, exit 1 (never `LOG TIME: none`)."""
    cp = _cp()
    repo, c = _history(tmp_path)
    monkeypatch.chdir(repo)
    assert cp.late_log_lines() == []                         # control: ls-tree and both blames work
    _patched_git(monkeypatch, cp, {("blame", "--line-porcelain", "--", "logs/implementation/2026-10-31.md"):
                                   ("", 128)})
    assert cp.late_log_lines() == ["logs/implementation/2026-10-31.md (git blame failed; item 081)"]
    code = cp.main(["--untracked-from", c, "--today", "2026-11-20"])
    out = capsys.readouterr().out
    assert "LOG TIME: logs/implementation/2026-10-31.md (git blame failed; item 081)" in out, out
    assert code == 1, out


@NO_GIT
def test_unrelated_branch_without_checked_paths_is_not_an_error(tmp_path, monkeypatch):
    """R2-b: I3's `nowork` repro. merge-base --all exit 1 is a real answer; 0 of 1 files on checked
    paths -> not-scanned line, no BRANCH ERROR, exit 0. Absent case: its ls-tree fails -> error."""
    import datetime as dt
    cp = _cp()
    repo = _repo_with_open_branch(tmp_path)
    _orphan(repo, "nowork", {})
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-02")
    assert code == 0, out
    assert any(l.startswith("  origin/nowork: no common history with HEAD; not scanned (item 081)")
               for l in out.splitlines()), out
    assert "BRANCH ERROR" not in out, out
    assert "  origin/fix: items 040; merges cleanly" in out, out
    assert "IN PR: 040" in out, out
    monkeypatch.chdir(repo)
    real = cp._git
    monkeypatch.setattr(cp, "_git", lambda *a: ("", 128) if a[:2] == ("ls-tree", "-r") and "origin/nowork" in a
                        else real(*a))
    nw = [b for b in cp.open_branches(dt.date(2026, 11, 2)) if b["ref"] == "origin/nowork"][0]
    assert nw["unrelated"] is True and nw["errors"] == ["git ls-tree failed (exit 128)"]


@NO_GIT
def test_unrelated_branch_with_work_is_branch_error(tmp_path):
    """R2-c: an orphan carrying work/150 (1 of 1 files on checked paths) cannot be scanned without a
    merge base: BRANCH ERROR, exit 1; --next-id still counts its ID (RI-009)."""
    repo = _repo_with_open_branch(tmp_path)
    _orphan(repo, "oldwork", {"work/150/request.md": "# Work item 150\nScope: FULL\nDate: 2026-10-31\n"})
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-02")
    assert code == 1, out
    assert ("BRANCH ERROR: origin/oldwork (no common history with HEAD; 1 file(s) on checked paths "
            "(first: work/150/request.md) not checked (item 081))") in out, out
    assert any(l.startswith("  origin/oldwork: no common history with HEAD; not scanned (item 081)")
               for l in out.splitlines()), out
    assert _run(repo, "check_pipeline.py", "--next-id") == (0, "151\n")


# Item 091 step 1 (081 F1, A1-A3): one orphan per isolable entry of the unrelated ref's ls-tree pathspec.
UNRELATED_GROUPS = {"w": "work/150/request.md", "ri": "logs/recurring-issues.md", "cl": ".claude/agents/x.md",
                    "tp": "templates/x.md", "cb": "ccbot/x.py", "cf": "config/x.json", "sc": "scripts/x.py",
                    "ts": "tests/test_x.py"}


@NO_GIT
def test_unrelated_branch_each_checked_group_is_branch_error(tmp_path):
    """Item 091 step 1: 8 orphans, each holding one file under a different pathspec entry (work/,
    RECURRING, RULE_PATHS .claude/ and templates/, RESEARCH_CODE_PATHS): one BRANCH ERROR line each, so
    dropping any group (or any one of these entries) from the ls-tree list loses a line. Exit 1."""
    repo = _repo_with_open_branch(tmp_path)
    for name, path in UNRELATED_GROUPS.items():
        _orphan(repo, name, {path: "x\n"})
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-02")
    assert code == 1, out
    for name, path in UNRELATED_GROUPS.items():
        assert (f"BRANCH ERROR: origin/{name} (no common history with HEAD; 1 file(s) on checked paths "
                f"(first: {path}) not checked (item 081))") in out.splitlines(), (name, out)
    assert subprocess.run(["git", "merge-base", "--all", "HEAD", "origin/w"], cwd=repo,
                          capture_output=True).returncode == 1


def test_rule_path_files_are_inside_research_code_dirs():
    """Item 091 step 1 premise: the two RULE_PATHS file entries (scripts/check_pipeline.py,
    scripts/check_handoff.py) also match the `scripts/` entry of RESEARCH_CODE_PATHS, so an orphan
    cannot isolate them, and dropping them from the unrelated-ref ls-tree is an equivalent mutant only
    while this holds. If a RULE_PATHS file leaves those dirs, this fails and the gap becomes real."""
    cp = _cp()
    assert all(any(f.startswith(d) for d in cp.RESEARCH_CODE_PATHS) for f in cp.RULE_PATHS if not f.endswith("/"))


# Item 091 step 2 (081 F1, A8, A9, A13): one patched git call per exit-code term, each with its control.
_BRANCH_LIST = ("branch", "-r", "--no-merged", "HEAD", "--format=%(refname:short)")


@NO_GIT
def test_branch_list_failure_exits_1(tmp_path, monkeypatch, capsys):
    """A8: `git branch -r` failing is the only change from an exit-0 control, so only the
    `isinstance(branches, str)` term can make the exit 1."""
    cp = _cp()
    repo = _repo_with_open_branch(tmp_path)
    monkeypatch.chdir(repo)
    args = ["--untracked-from", _root(repo), "--today", "2026-11-02"]
    assert cp.main(args) == 0, capsys.readouterr().out
    capsys.readouterr()
    _patched_git(monkeypatch, cp, {_BRANCH_LIST: ("", 128)})
    code = cp.main(args)
    out = capsys.readouterr().out
    assert code == 1, out
    assert "OPEN BRANCHES: git branch failed (exit 128) (item 081)" in out.splitlines(), out


@NO_GIT
def test_main_ref_lookup_failure_exits_1(tmp_path, monkeypatch, capsys):
    """A9a: the origin/main for-each-ref failing gives the MAIN AHEAD error and exit 1."""
    cp = _cp()
    repo = _repo_with_open_branch(tmp_path)
    monkeypatch.chdir(repo)
    args = ["--untracked-from", _root(repo), "--today", "2026-11-02"]
    assert cp.main(args) == 0, capsys.readouterr().out
    capsys.readouterr()
    _patched_git(monkeypatch, cp, {("for-each-ref", "--format=%(refname) %(objectname)",
                                    "refs/remotes/origin/main"): ("", 128)})
    code = cp.main(args)
    out = capsys.readouterr().out
    assert code == 1, out
    assert "MAIN AHEAD: git for-each-ref failed (exit 128) (item 081)" in out.splitlines(), out


@NO_GIT
def test_main_ahead_count_failure_exits_1(tmp_path, monkeypatch, capsys):
    """A9b: the HEAD..origin/main rev-list count failing gives the MAIN AHEAD error and exit 1."""
    cp = _cp()
    repo = _repo_with_open_branch(tmp_path)
    monkeypatch.chdir(repo)
    sha = subprocess.run(["git", "rev-parse", "origin/main"], cwd=repo, capture_output=True, text=True,
                         check=True).stdout.strip()
    args = ["--untracked-from", _root(repo), "--today", "2026-11-02"]
    assert cp.main(args) == 0, capsys.readouterr().out
    capsys.readouterr()
    _patched_git(monkeypatch, cp, {("rev-list", "--count", f"HEAD..{sha}"): ("", 128)})
    code = cp.main(args)
    out = capsys.readouterr().out
    assert code == 1, out
    assert "MAIN AHEAD: git rev-list failed (exit 128) (item 081)" in out.splitlines(), out


@NO_GIT
def test_next_id_branch_listing_failure_refuses(tmp_path, monkeypatch, capsys):
    """A13: a failed per-branch ls-tree is never read as an empty listing: --next-id refuses (exit 2,
    empty stdout) instead of printing HEAD's next ID."""
    cp = _cp()
    repo = _repo_with_open_branch(tmp_path)
    monkeypatch.chdir(repo)
    assert cp.main(["--next-id"]) == 0
    assert capsys.readouterr().out == "041\n"
    _patched_git(monkeypatch, cp, {("ls-tree", "-d", "--name-only", "origin/fix", "--", "work/"): ("", 128)})
    code = cp.main(["--next-id"])
    out, err = capsys.readouterr()
    assert code == 2, out
    assert out == "", out
    assert "--next-id refused: git ls-tree failed (exit 128)" in err, err


@NO_GIT
def test_merge_base_die_is_branch_error(tmp_path, monkeypatch, capsys):
    """R2-d: only merge-base exit 1 is the no-common-history answer; 128 is a BRANCH ERROR and the
    branch is still scanned (only the clash base is unknown)."""
    import datetime as dt
    cp = _cp()
    repo = _repo_with_open_branch(tmp_path)
    monkeypatch.chdir(repo)
    _patched_git(monkeypatch, cp, {("merge-base", "--all", "HEAD", "origin/fix"): ("", 128)})
    fix = [b for b in cp.open_branches(dt.date(2026, 11, 2)) if b["ref"] == "origin/fix"][0]
    assert fix["unrelated"] is False
    assert fix["errors"] == ["git merge-base failed (exit 128)"]
    assert "040" in fix["items"]
    code = cp.main(["--untracked-from", _root(repo), "--today", "2026-11-02"])
    out = capsys.readouterr().out
    assert code == 1, out
    assert "BRANCH ERROR: origin/fix (git merge-base failed (exit 128))" in out, out


def test_main_ahead_non_digit_count(monkeypatch):
    """R2-e: rev-list exits 0 with no count -> the error string, never None or 0."""
    cp = _cp()
    monkeypatch.setattr(cp, "_git", lambda *a: ("refs/remotes/origin/main " + "a" * 40 + "\n", 0)
                        if a[0] == "for-each-ref" else ("", 0))
    assert cp.main_ahead() == "git rev-list gave no count (item 081)"



# Item 082 (RI-006): from SUITE_FROM on, 05 has exactly one column-0 `Suite:` line equal to the tests
# field of the item's last I2 log line, compared as a whole string.
SUITE_DAY = "2026-11-11"
NO_SUITE = "05 has no 'Suite:' line (item 082)"


def _suite_item(root, suite05, i2=(FIELDS["I2"],), item="151"):
    """Item `item` with every step and log line (_item), then 05 replaced by `suite05` and its one I2
    log line replaced by the lines `i2`, in that order (an empty tuple: no I2 line)."""
    _item(root, item, ALL, date=SUITE_DAY)
    (root / "work" / item / "05-build-report.md").write_text(suite05, encoding="utf-8")
    log = root / "logs" / "implementation" / f"{SUITE_DAY}.md"
    text = log.read_text(encoding="utf-8")
    old = f"12:00 | I2 | {item} | {FIELDS['I2']}\n"
    assert old in text
    log.write_text(text.replace(old, "".join(f"12:00 | I2 | {item} | {f}\n" for f in i2)), encoding="utf-8")


def _inc(root):
    code, out = _run(root, "check_pipeline.py", "--today", SUITE_DAY)
    return code, _pick(out, "INCOMPLETE:")


def _mismatch(suite, field):
    return f"05 Suite line does not equal the last I2 log tests field (item 082): '{suite}' vs '{field}'"


SF = _cp().SUITE_FROM
S_FULL = "411 passed, 1 skipped in 1.00s"


def test_suite_line_absent_is_incomplete(tmp_path):
    """S0: 05 with no Suite line at all."""
    _suite_item(tmp_path, "x\n")
    code, inc = _inc(tmp_path)
    assert inc == f"INCOMPLETE: 151 ({NO_SUITE})" and code == 1


def test_suite_line_equal_to_field_passes(tmp_path):
    """S1: the boundary ID SF, Suite = the field as a whole line."""
    _suite_item(tmp_path, f"x\nSuite: {S_FULL}\n", i2=(f"1 files changed | tests {S_FULL}",), item=f"{SF:03d}")
    code, inc = _inc(tmp_path)
    assert inc == "INCOMPLETE: none" and code == 0


def test_suite_line_dropped_middle_is_incomplete(tmp_path):
    """S2 (probe target RI-006-082-suite): the field dropped `, 1 skipped`, at the boundary ID SF."""
    _suite_item(tmp_path, f"x\nSuite: {S_FULL}\n", i2=("1 files changed | tests 411 passed in 1.00s",),
                item=f"{SF:03d}")
    code, inc = _inc(tmp_path)
    assert inc == f"INCOMPLETE: {SF:03d} ({_mismatch(S_FULL, '411 passed in 1.00s')})" and code == 1


@pytest.mark.parametrize("field", ["411 passed, 1 skipped", S_FULL + " (note)"], ids=["S3-tail", "S4-note"])
def test_suite_line_part_of_field_is_incomplete(tmp_path, field):
    """S3: the field dropped the time (kills `field in suite`); S4: it added a note (kills `suite in field`).
    Item 090: on SF (below TIMED_FROM), where an untimed field is still well-formed."""
    _suite_item(tmp_path, f"x\nSuite: {S_FULL}\n", i2=(f"1 files changed | tests {field}",), item=f"{SF:03d}")
    _, inc = _inc(tmp_path)
    assert inc == f"INCOMPLETE: {SF:03d} ({_mismatch(S_FULL, field)})"


def test_suite_line_inside_fence_is_not_read(tmp_path):
    """S5: the only Suite line is inside a code fence."""
    _suite_item(tmp_path, "x\n```\nSuite: 1 passed\n```\n")
    _, inc = _inc(tmp_path)
    assert inc == f"INCOMPLETE: 151 ({NO_SUITE})"


def test_two_suite_lines_are_incomplete(tmp_path):
    """S6: two identical Suite lines, both equal to the field (kills first-wins and last-wins)."""
    _suite_item(tmp_path, "x\nSuite: 1 passed\nSuite: 1 passed\n")
    _, inc = _inc(tmp_path)
    assert inc == "INCOMPLETE: 151 (05 has 2 'Suite:' lines, needs exactly 1 (item 082))"


def test_unfilled_template_suite_line_is_incomplete(tmp_path):
    """S7: 05 is templates/build-report.md as shipped: its placeholder is not the field."""
    template = (REPO / "templates" / "build-report.md").read_text(encoding="utf-8")
    _suite_item(tmp_path, template)
    _, inc = _inc(tmp_path)
    holder = [l for l in template.splitlines() if l.startswith("Suite:")][0][len("Suite:"):].strip()
    assert inc == f"INCOMPLETE: 151 ({_mismatch(holder, '1 passed in 0.01s')})"


def test_suite_with_no_i2_line_adds_no_suite_entry(tmp_path):
    """S8: no I2 line: 043's entry only."""
    _suite_item(tmp_path, "x\n", i2=())
    _, inc = _inc(tmp_path)
    assert inc == "INCOMPLETE: 151 (no log line for I2)"


def test_suite_with_malformed_last_i2_line_never_falls_back(tmp_path):
    """S9: the last I2 line is malformed: 045's entry only, the earlier well-formed line is never used."""
    _suite_item(tmp_path, "x\nSuite: 411 passed\n",
                i2=("1 files changed | tests 410 passed in 0.01s", "1 files changed | tests 411/411"))
    _, inc = _inc(tmp_path)
    assert inc.startswith("INCOMPLETE: 151 (log line for I2 does not match its format (item 045)"), inc
    assert "Suite" not in inc, inc


def test_suite_below_cutoff_not_checked(tmp_path):
    """S10: ID SF - 1 with a mismatch: no Suite entry."""
    _suite_item(tmp_path, "x\nSuite: 2 passed\n", item=f"{SF - 1:03d}")
    _, inc = _inc(tmp_path)
    assert inc == "INCOMPLETE: none"


def test_suite_compared_with_last_i2_line(tmp_path):
    """S11: two I2 lines, the last equals Suite: no entry. S12: only the first does: mismatch."""
    _suite_item(tmp_path / "a", "x\nSuite: 2 passed in 0.02s\n",
                i2=("1 files changed | tests 1 passed in 0.01s", "1 files changed | tests 2 passed in 0.02s"))
    assert _inc(tmp_path / "a")[1] == "INCOMPLETE: none"
    _suite_item(tmp_path / "b", "x\nSuite: 1 passed in 0.01s\n",
                i2=("1 files changed | tests 1 passed in 0.01s", "1 files changed | tests 2 passed in 0.02s"))
    assert _inc(tmp_path / "b")[1] == f"INCOMPLETE: 151 ({_mismatch('1 passed in 0.01s', '2 passed in 0.02s')})"


def test_suite_inside_other_text_is_not_read(tmp_path):
    """S14: only the column-0 `Suite:` line is read. `Suite:` inline in backticks, in a list item and
    indented is not (kills `"Suite:" in line` and `line.lstrip().startswith("Suite:")`)."""
    _suite_item(tmp_path, "x\nSuite: 1 passed in 0.01s\n"
                          "the `Suite:` line above is copied as printed\n"
                          "- `Suite: 2 passed` was round 1\n"
                          "   Suite: 2 passed\n")
    code, inc = _inc(tmp_path)
    assert inc == "INCOMPLETE: none" and code == 0


@NO_GIT
@pytest.mark.parametrize("rules, seen", [
    ("TESTS_FORMAT_FROM = 76\nVERDICT_FROM = 71\n", False),
    ("TESTS_FORMAT_FROM = 76\nVERDICT_FROM = 71\nSUITE_FROM = 87\n", True),
], ids=["S13-not-seen", "S13b-seen"])
def test_suite_gate_follows_rule_file_of_05_commit(tmp_path, rules, seen):
    """S13: 05 (no Suite line) was added in a commit whose rule file has no SUITE_FROM: listed in RULE NOT
    SEEN, not INCOMPLETE (item 084 gate). S13b: the same with SUITE_FROM there: INCOMPLETE."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "scripts/check_pipeline.py", rules)
    _suite_item(repo, "x\n")
    root = _commit(repo, "151 built")
    _, out = _run(repo, "check_pipeline.py", "--untracked-from", root, "--today", SUITE_DAY)
    if seen:
        assert _pick(out, "INCOMPLETE:") == f"INCOMPLETE: 151 ({NO_SUITE})", out
        assert _pick(out, "RULE NOT SEEN:") == "RULE NOT SEEN: none", out
    else:
        assert "151 (" not in _pick(out, "INCOMPLETE:"), out
        assert _pick(out, "RULE NOT SEEN:") == (f"RULE NOT SEEN: 151 (05 added in {root[:7]} without SUITE_FROM "
                                                "(082): judged by no Suite check; item 084)"), out


@NO_GIT
def test_suite_gate_uncommitted_05_is_strict(tmp_path):
    """(u-s, item 088) S13b's rule file is committed but 151's 05 is not: no anchor, so the Suite check
    stays on (strict): INCOMPLETE, not listed (M-a)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "scripts/check_pipeline.py", "TESTS_FORMAT_FROM = 76\nVERDICT_FROM = 71\nSUITE_FROM = 87\n")
    root = _commit(repo, "root")
    _suite_item(repo, "x\n")
    _, out = _run(repo, "check_pipeline.py", "--untracked-from", root, "--today", SUITE_DAY)
    assert _pick(out, "INCOMPLETE:") == f"INCOMPLETE: 151 ({NO_SUITE})", out
    assert _pick(out, "RULE NOT SEEN:") == "RULE NOT SEEN: none", out


def test_suite_label_in_template_and_i2_text():
    """Item 082: the template has exactly one column-0 `Suite: <` line outside fences and comments, and
    i2-builder.md names the Suite line (text pin)."""
    cp = _cp()
    rows, _ = cp._md_lines((REPO / "templates" / "build-report.md").read_text(encoding="utf-8"))
    assert len([l for l, st in rows if st == "out" and l.startswith("Suite: <")]) == 1
    i2 = (REPO / ".claude" / "agents" / "i2-builder.md").read_text(encoding="utf-8")
    assert "05 has exactly one column-0 `Suite:` line" in i2 and "(item 082)" in i2


UNSHALLOW = ("If `git rev-parse --is-shallow-repository` prints true, run `git fetch --unshallow`, then test "
             "again. If it is still true, report UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD, LOG TIME, "
             "MAIN AHEAD, OPEN BRANCHES and RULE NOT SEEN as 'not checked', never 'none' (items 079, 084, 090).")


def test_unshallow_sentence_same_in_three_files():
    """Item 082 (RI-014): the unshallow sentences, byte for byte, once in each of the three files (text pin)."""
    for f in (".claude/commands/run-item.md", ".claude/commands/daily-audit.md", ".claude/agents/a1-auditor.md"):
        assert (REPO / f).read_text(encoding="utf-8").count(UNSHALLOW) == 1, f
    assert "RULE NOT SEEN" in UNSHALLOW                 # item 091 step 4: 084's not-checked form is named


def test_run_item_commit_subject_rule():
    """Item 082: run-item.md states the commit-subject rule for the orchestrator's step (5) and for I2
    (text pin only; no check reads commit text)."""
    text = (REPO / ".claude" / "commands" / "run-item.md").read_text(encoding="utf-8")
    assert text.count("(5) commit the step file and its log line. The commit that adds a step's log line has "
                      "the subject `Item <ID>: ` followed by the line `--log` printed for that step, copied "
                      "unchanged, never reworded (item 082); a commit made before that step's `--log` line "
                      "has no such subject rule.") == 1
    assert text.count("I2 commits each code change together with its 05 change. Its commit that adds the I2 "
                      "log line follows the same subject rule (item 082).") == 1


# Item 089 (RI-014): every repo read goes through _read; an unreadable file is listed on UNREADABLE and
# each consumer says not checked, never a traceback, a "" computation or a bare none.
LOG = "logs/implementation/2026-11-19.md"
BAD = b"\xff\xfe"
CLEAN_LOG = b"# Implementation log\n"


def _run3(root, *args):
    """(exit code, stdout decoded with replace, stderr bytes) of check_pipeline.py in `root` (item 089)."""
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "check_pipeline.py"), *args], cwd=root,
                       capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr


def _tree(root, log=CLEAN_LOG):
    """6a's tree: work/150/request.md only (FULL, opened 2026-11-21) and one implementation log file."""
    d = root / "work" / "150"
    d.mkdir(parents=True)
    (d / "request.md").write_text("# Work item 150\nScope: FULL\nDate: 2026-11-21\n", encoding="utf-8")
    f = root / LOG
    f.parent.mkdir(parents=True, exist_ok=True)
    if log is not None:
        f.write_bytes(log)
    return f


def _pick1(out, prefix):
    return [l for l in out.splitlines() if l.startswith(prefix)]


def test_read_contract(tmp_path, monkeypatch):
    """089 step 1: _read's results and the _UNREAD record (detail, never content)."""
    cp = _cp()
    monkeypatch.setattr(cp, "_UNREAD", {})
    ok = tmp_path / "ok.md"
    ok.write_text("x\ny\n", encoding="utf-8")
    assert cp._read(ok) == ("x\ny\n", None) and cp._UNREAD == {}
    bad = tmp_path / "bad.md"
    bad.write_bytes(BAD)
    assert cp._read(bad) == (None, f"{bad.as_posix()} unreadable")
    assert cp._UNREAD == {bad.as_posix(): "not UTF-8 at byte 0"}
    cp._UNREAD.clear()
    folder = tmp_path / "dir.md"
    folder.mkdir()
    assert cp._read(folder) == (None, f"{folder.as_posix()} unreadable")
    assert cp._UNREAD == {folder.as_posix(): "IsADirectoryError"}
    cp._UNREAD.clear()
    gone = tmp_path / "gone.md"
    assert cp._read(gone, missing_ok=True) == (None, None) and cp._UNREAD == {}
    assert cp._read(gone) == (None, f"{gone.as_posix()} unreadable")
    assert cp._UNREAD == {gone.as_posix(): "FileNotFoundError"}
    cr = tmp_path / "cr.md"
    cr.write_bytes(b"a\rb\r\nc")
    assert cp._read(cr) == ("a\nb\nc", None)


def test_read_census():
    """089 step 7: every file read in check_pipeline.py by (innermost function, call): only the reader
    and write_log's append. A raw read_text anywhere else fails here (M5)."""
    import ast
    import collections
    tree = ast.parse((REPO / "scripts" / "check_pipeline.py").read_text(encoding="utf-8"))
    seen = collections.Counter()

    def walk(node, fn):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, ast.Call):
                if isinstance(ch.func, ast.Attribute) and ch.func.attr in ("read_text", "read_bytes", "open"):
                    seen[(fn, ch.func.attr)] += 1
                elif isinstance(ch.func, ast.Name) and ch.func.id == "open":
                    seen[(fn, "open")] += 1
            walk(ch, ch.name if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn)

    walk(tree, None)
    census = {("_read", "read_bytes"): (1, "the reader (item 089)"),
              ("write_log", "open"): (1, "append write, item 045")}
    assert dict(seen) == {k: v[0] for k, v in census.items()}
    assert all(reason.strip() for _, reason in census.values())
    assert sum(seen.values()) == 2


def test_unreadable_log_exits_1_alone(tmp_path):
    """089 6a: a non-UTF-8 log file, no git: the clean twin exits 0, the bad twin exits 1 only because of
    UNREADABLE (M3), and ORPHAN LOG is never a bare none (M9). No traceback (M1)."""
    clean, bad = tmp_path / "clean", tmp_path / "bad"
    _tree(clean)
    _tree(bad, BAD)
    code, out, err = _run3(clean, "--today", "2026-11-21")
    assert b"Traceback" not in err, err
    assert code == 0, out
    assert "UNREADABLE: none" in out.splitlines() and "ORPHAN LOG: none" in out.splitlines(), out
    code, out, err = _run3(bad, "--today", "2026-11-21")
    assert b"Traceback" not in err, err
    assert code == 1, out
    lines = out.splitlines()
    assert f"UNREADABLE: {LOG} (not UTF-8 at byte 0)" in lines, out
    assert f"ORPHAN LOG: not checked ({LOG} unreadable; item 089)" in lines, out
    order = [l.split(":")[0] for l in lines]
    assert order.index("ORPHAN LOG") + 1 == order.index("UNREADABLE") == order.index("INBOX") - 1, out



# Item 092 (RI-014): check_handoff.py reads 01 and 03 through check_pipeline's _read; an unreadable file is a
# FAIL line and exit 1, never a traceback, a count from "" or LEGACY.
def _run3h(root, *args):
    """(exit code, stdout decoded with replace, stderr bytes) of check_handoff.py in `root` (item 092)."""
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "check_handoff.py"), *args], cwd=root,
                       capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr


def _h03(d, body=b""):
    """A clean 03 in folder d (one fact row, matching Totals line, Self-check), prefixed with `body`."""
    d.mkdir(parents=True, exist_ok=True)
    clean = ("# 03\n## Fact check\n| a | b |\n|---|---|\n| x | y |\n"
             "1 rows checked \u2192 1 VERIFIED as-is, 0 fixed, 0 removed\n## Self-check\nok\n")
    (d / "03-handoff.md").write_bytes(body + clean.encode("utf-8"))


def _ok3(code, out, err, want_code, lines):
    assert b"Traceback" not in err, err
    for line in lines:
        assert line in out.splitlines(), out
    assert code == want_code, out


def test_handoff_bad_01_no_03(tmp_path):
    """092 (a): a non-UTF-8 01 and no 03: not-computed sources line, FAIL line, exit 1 (M-a, M-c)."""
    bad, clean = tmp_path / "bad", tmp_path / "clean"
    (bad / "work" / "150").mkdir(parents=True)
    (bad / "work" / "150" / "01-research.md").write_bytes(BAD + b"see https://x.example/a\n")
    code, out, err = _run3h(bad, "150")
    _ok3(code, out, err, 1, [
        "sources count (unique URLs in 01-research.md): not computed "
        "(work/150/01-research.md unreadable (not UTF-8 at byte 0))",
        "FAIL: work/150/01-research.md unreadable (not UTF-8 at byte 0)",
        "no work/150/03-handoff.md; nothing else to check"])
    assert not any(re.fullmatch(r"sources count \(unique URLs in 01-research.md\): \d+", l)
                   for l in out.splitlines()), out
    (clean / "work" / "150").mkdir(parents=True)
    (clean / "work" / "150" / "01-research.md").write_bytes(b"see https://x.example/a\n")
    code, out, err = _run3h(clean, "150")
    _ok3(code, out, err, 0, ["sources count (unique URLs in 01-research.md): 1",
                             "no work/150/03-handoff.md; nothing else to check"])
    assert not any(l.startswith("FAIL:") for l in out.splitlines()), out


def test_handoff_bad_03(tmp_path):
    """092 (b): a non-UTF-8 03 next to a good 01: FAIL line, 1 problem(s), no table checks (M-b, M-d, M-g)."""
    bad, clean = tmp_path / "bad", tmp_path / "clean"
    for root, body in ((bad, BAD), (clean, b"")):
        d = root / "work" / "150"
        _h03(d, body)
        (d / "01-research.md").write_bytes(b"see https://x.example/a\n")
    code, out, err = _run3h(bad, "150")
    _ok3(code, out, err, 1, ["FAIL: work/150/03-handoff.md unreadable (not UTF-8 at byte 0)", "1 problem(s)"])
    assert not any(l.startswith("fact-check rows:") for l in out.splitlines()), out
    code, out, err = _run3h(clean, "150")
    _ok3(code, out, err, 0, ["sources count (unique URLs in 01-research.md): 1", "PASS"])


def test_handoff_all_one_bad_03(tmp_path):
    """092 (c): --all over three items, one 03 unreadable: that item is FAIL, the rest PASS (M-b, M-d).
    Every folder has a 03, so no git call is made. No 01: no sources count line."""
    bad, clean = tmp_path / "bad", tmp_path / "clean"
    for root in (bad, clean):
        for item in ("150", "151", "152"):
            _h03(root / "work" / item, BAD if root is bad and item == "151" else b"")
    code, out, err = _run3h(bad, "--all")
    _ok3(code, out, err, 1, ["150: PASS", "151: FAIL: work/151/03-handoff.md unreadable (not UTF-8 at byte 0)",
                             "152: PASS", "FAIL on 151"])
    code, out, err = _run3h(clean, "--all")
    _ok3(code, out, err, 0, ["150: PASS", "151: PASS", "152: PASS", "no new failures"])
    code, out, err = _run3h(clean, "150")
    _ok3(code, out, err, 0, ["PASS"])
    assert not any(l.startswith("sources count") for l in out.splitlines()), out


def test_handoff_03_is_directory(tmp_path):
    """092 (d): a 03 that is a directory is IsADirectoryError, exit 1 (M-b, M-d, M-g)."""
    bad, clean = tmp_path / "bad", tmp_path / "clean"
    (bad / "work" / "150" / "03-handoff.md").mkdir(parents=True)
    code, out, err = _run3h(bad, "150")
    _ok3(code, out, err, 1, ["FAIL: work/150/03-handoff.md unreadable (IsADirectoryError)", "1 problem(s)"])
    _h03(clean / "work" / "150")
    code, out, err = _run3h(clean, "150")
    _ok3(code, out, err, 0, ["PASS"])


def test_handoff_legacy_bad_03_is_fail(tmp_path):
    """092 (e): an unreadable 03 of a LEGACY ID is FAIL under --all, never LEGACY (M-b, M-d, M-f)."""
    bad, clean = tmp_path / "bad", tmp_path / "clean"
    _h03(bad / "work" / "003", BAD)
    code, out, err = _run3h(bad, "--all")
    _ok3(code, out, err, 1, ["003: FAIL: work/003/03-handoff.md unreadable (not UTF-8 at byte 0)", "FAIL on 003"])
    d = clean / "work" / "003"
    d.mkdir(parents=True)
    (d / "03-handoff.md").write_text("# 03\n## Fact check\n| a | b |\n|---|---|\n| x | y |\n", encoding="utf-8")
    code, out, err = _run3h(clean, "--all")
    _ok3(code, out, err, 0, ["no new failures"])
    assert any(l.startswith("003: LEGACY (") for l in out.splitlines()), out


def test_handoff_all_bad_01_good_03(tmp_path):
    """092 (f): under --all a bad 01 next to a good 03 is FAIL, though every 03 check passes (M-a, M-d)."""
    bad, clean = tmp_path / "bad", tmp_path / "clean"
    for root, body in ((bad, BAD), (clean, b"")):
        d = root / "work" / "151"
        _h03(d)
        (d / "01-research.md").write_bytes(body + b"see https://x.example/a\n")
    code, out, err = _run3h(bad, "--all")
    _ok3(code, out, err, 1, ["151: FAIL: work/151/01-research.md unreadable (not UTF-8 at byte 0)", "FAIL on 151"])
    code, out, err = _run3h(clean, "--all")
    _ok3(code, out, err, 0, ["151: PASS", "no new failures"])


def test_unreadable_problem_fullmatch_only():
    """092 step 4 (RI-012): only a whole unreadable-file problem skips LEGACY, never a substring."""
    sys.path.insert(0, str(REPO / "scripts"))
    import check_handoff
    rx = check_handoff.UNREADABLE_PROBLEM
    assert rx.fullmatch("work/003/03-handoff.md unreadable (not UTF-8 at byte 0)")
    assert rx.fullmatch("work/003/03-handoff.md unreadable (IsADirectoryError)")
    assert rx.fullmatch("no Totals line ('<n> rows checked -> ...')") is None
    assert rx.fullmatch("x unreadable (not UTF-8 at byte 0); y") is None


def test_handoff_read_census():
    """092 step 6: check_handoff.py has no raw read (read_text, read_bytes, open); main reads 01 and 03 by
    exactly 2 `_read` attribute calls (positive control, counted from the AST, RI-006)."""
    import ast
    import collections
    tree = ast.parse((REPO / "scripts" / "check_handoff.py").read_text(encoding="utf-8"))
    seen = collections.Counter()
    reads = collections.Counter()

    def walk(node, fn):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, ast.Call):
                if isinstance(ch.func, ast.Attribute) and ch.func.attr in ("read_text", "read_bytes", "open"):
                    seen[(fn, ch.func.attr)] += 1
                elif isinstance(ch.func, ast.Name) and ch.func.id == "open":
                    seen[(fn, "open")] += 1
                if isinstance(ch.func, ast.Attribute) and ch.func.attr == "_read":
                    reads[fn] += 1
            walk(ch, ch.name if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn)

    walk(tree, None)
    assert dict(seen) == {}
    assert sum(seen.values()) == 0
    assert dict(reads) == {"main": 2}


def test_r1_log_refuses_not_computed():
    """092 known gap 2: `--log R1` refuses a not-computed sources value, so the item stays INCOMPLETE."""
    cp = _cp()
    assert cp.log_fields_ok("R1", "092", "brief written | not computed (work/092/01-research.md unreadable "
                                         "(not UTF-8 at byte 0))") is False
    assert cp.log_fields_ok("R1", "092", "brief written | 7") is True


def test_unreadable_log_directory(tmp_path):
    """089 6b: a log path that is a directory is IsADirectoryError, exit 1 (M2)."""
    f = _tree(tmp_path, None)
    f.mkdir()
    code, out, err = _run3(tmp_path, "--today", "2026-11-21")
    assert b"Traceback" not in err, err
    assert code == 1, out
    assert f"UNREADABLE: {LOG} (IsADirectoryError)" in out.splitlines(), out


def test_unreadable_06(tmp_path):
    """089 6c: a non-UTF-8 06 is one INCOMPLETE entry in place of its checks; exit 1 (SKIPPED fires too).
    I2 addition (M14): a complete item 151 whose 06 is unreadable is `151: UNREADABLE`, never a status
    computed with verdict None."""
    _tree(tmp_path)
    (tmp_path / "work" / "150" / "06-verification.md").write_bytes(b"# 06\n\xff")
    _item(tmp_path, "151", ALL)
    (tmp_path / "work" / "151" / "06-verification.md").write_bytes(b"# 06\n\xff")
    code, out, err = _run3(tmp_path, "--today", "2026-11-21")
    assert b"Traceback" not in err, err
    assert code == 1, out
    lines = out.splitlines()
    assert ("UNREADABLE: work/150/06-verification.md (not UTF-8 at byte 5), "
            "work/151/06-verification.md (not UTF-8 at byte 5)") in lines, out
    inc = _pick1(out, "INCOMPLETE:")[0]
    assert ("150 (06 not checked (work/150/06-verification.md unreadable; item 089); no log line for I3; 06 round "
            "headings not checked (work/150/06-verification.md unreadable; item 091))") in inc, out   # 091: >= 92
    assert ("151 (06 not checked (work/151/06-verification.md unreadable; item 089); 06 round headings not checked "
            "(work/151/06-verification.md unreadable; item 091))") in inc, out
    assert "151: UNREADABLE (work/151/06-verification.md unreadable)" in lines, out


def test_unreadable_request(tmp_path):
    """089 6d: a non-UTF-8 request.md is `150: UNREADABLE`, exit 1 from UNREADABLE alone."""
    _tree(tmp_path)
    (tmp_path / "work" / "150" / "request.md").write_bytes(b"Scope: FULL\n\xff")
    code, out, err = _run3(tmp_path, "--today", "2026-11-21")
    assert b"Traceback" not in err, err
    assert code == 1, out
    lines = out.splitlines()
    assert "150: UNREADABLE (work/150/request.md unreadable)" in lines, out
    assert "UNREADABLE: work/150/request.md (not UTF-8 at byte 12)" in lines, out
    assert "INCOMPLETE: none" in lines, out


@NO_GIT
def test_unreadable_log_consumers_say_not_checked(tmp_path):
    """089 6e: with a bad log, UNCOMMITTED STEP and INCOMPLETE say not checked and never compute from ""
    (M10); 040 is below CHECKLIST_FROM and gets no entry."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _item(repo, "150", [], date="2026-11-21", logged=False)
    _item(repo, "040", ALL[:3], date="2026-10-30", logged=False)
    c = _commit(repo, "cutoff")
    _write(repo, "work/150/01-research.md")
    (repo / LOG).parent.mkdir(parents=True, exist_ok=True)
    (repo / LOG).write_bytes(BAD)
    code, out, err = _run3(repo, "--untracked-from", c, "--today", "2026-11-21")
    assert b"Traceback" not in err, err
    assert code == 1, out
    lines = out.splitlines()
    assert f"UNCOMMITTED STEP: not checked ({LOG} unreadable; item 089)" in lines, out
    inc = _pick1(out, "INCOMPLETE:")[0]
    assert inc == f"INCOMPLETE: 150 (log lines not checked ({LOG} unreadable; item 089))", out
    assert "no log line for" not in inc and "040 (" not in inc, out


def test_cr_only_07_reads_as_lines(tmp_path):
    """089 6h: a 07 with lone CR line ends reads as read_text did (universal newlines): complete (M11)."""
    _item(tmp_path, "150", ALL)
    (tmp_path / "work" / "150" / "07-audit-task.md").write_bytes(b"# 07\rA1 result: PASS\r")
    code, out, err = _run3(tmp_path, "--today", "2026-11-21")
    assert b"Traceback" not in err, err
    assert "150: complete (FULL)" in out.splitlines(), out


def test_unreadable_cleared_between_runs(tmp_path, monkeypatch, capsys):
    """089 6i: main twice in one process; after the log is fixed the second run is clean (M4)."""
    cp = _cp()
    f = _tree(tmp_path, BAD)
    monkeypatch.chdir(tmp_path)
    assert cp.main(["--today", "2026-11-21"]) == 1
    assert f"UNREADABLE: {LOG} (not UTF-8 at byte 0)" in capsys.readouterr().out.splitlines()
    f.write_bytes(CLEAN_LOG)
    assert cp.main(["--today", "2026-11-21"]) == 0
    assert "UNREADABLE: none" in capsys.readouterr().out.splitlines()


def test_unreadable_printed_before_inbox_early_return(tmp_path, monkeypatch, capsys):
    """089 6j: a failing INBOX returns early; UNREADABLE is printed before it (M6)."""
    cp = _cp()
    _tree(tmp_path, BAD)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cp, "inbox_section", lambda *a, **k: ("x", True))
    assert cp.main(["--today", "2026-11-21"]) == 1
    assert f"UNREADABLE: {LOG} (not UTF-8 at byte 0)" in capsys.readouterr().out.splitlines()


def test_orphan_log_with_unreadable_file(tmp_path):
    """089 6k: orphans from a readable file are listed, and the unreadable file is named (M9)."""
    _tree(tmp_path, BAD)
    (tmp_path / "logs" / "implementation" / "2026-11-18.md").write_text(
        "12:00 | I2 | 777 | 1 files changed | tests 1 passed\n", encoding="utf-8")
    code, out, err = _run3(tmp_path, "--today", "2026-11-21")
    assert b"Traceback" not in err, err
    assert (f"ORPHAN LOG: 777 (logs/implementation/2026-11-18.md); not checked: {LOG} unreadable (item 089)"
            in out.splitlines()), out


def test_unreadable_07(tmp_path):
    """089 6l: a non-UTF-8 07 is `150: UNREADABLE`, never awaiting A1 or complete (M14)."""
    _item(tmp_path, "150", ALL)
    (tmp_path / "work" / "150" / "07-audit-task.md").write_bytes(BAD)
    code, out, err = _run3(tmp_path, "--today", "2026-11-21")
    assert b"Traceback" not in err, err
    assert code == 1, out
    lines = out.splitlines()
    assert "150: UNREADABLE (work/150/07-audit-task.md unreadable)" in lines, out
    assert "UNREADABLE: work/150/07-audit-task.md (not UTF-8 at byte 0)" in lines, out


def test_unreadable_05_at_suite_check(tmp_path):
    """089 6m: a non-UTF-8 05 is `05 not checked` at the Suite check and not computable in LOG BATCH."""
    _item(tmp_path, "150", ALL)
    (tmp_path / "work" / "150" / "05-build-report.md").write_bytes(BAD)
    code, out, err = _run3(tmp_path, "--today", "2026-11-21")
    assert b"Traceback" not in err, err
    assert code == 1, out
    inc = _pick1(out, "INCOMPLETE:")[0]
    assert ("150 (05 not checked (work/150/05-build-report.md unreadable; item 089); 05 round headings not "
            "checked (work/150/05-build-report.md unreadable; item 091))") in inc, out   # 091: 150 >= 92
    assert "not computable: 150: work/150/05-build-report.md unreadable" in _pick1(out, "LOG BATCH:")[0], out


@NO_GIT
def test_shallow_file_unreadable_whatever_the_flag(tmp_path, monkeypatch):
    """089 T-sh: a shallow file that exists but can't be read is "unreadable" even when the flag is not a
    sure true (M7), and it is recorded (M8); a missing file or a failed --git-common-dir keeps 079's rule."""
    cp = _cp()
    monkeypatch.setattr(cp, "_UNREAD", {})
    repo, c = _history(tmp_path)
    monkeypatch.chdir(repo)
    shallow = repo / ".git" / "shallow"
    _patched_git(monkeypatch, cp, {("rev-parse", "--is-shallow-repository"): ("", 129)})
    shallow.write_bytes(b"\xff")
    assert cp._shallow_boundaries() == "unreadable"
    assert list(cp._UNREAD.values()) == ["not UTF-8 at byte 0"], cp._UNREAD
    cp._UNREAD.clear()
    shallow.unlink()
    shallow.mkdir()
    assert cp._shallow_boundaries() == "unreadable"
    assert list(cp._UNREAD.values()) == ["IsADirectoryError"], cp._UNREAD
    cp._UNREAD.clear()
    _patched_git(monkeypatch, cp, {("rev-parse", "--is-shallow-repository"): ("", 129),
                                   ("rev-parse", "--git-common-dir"): ("", 128)})
    assert cp._shallow_boundaries() == "full" and cp._UNREAD == {}
    _patched_git(monkeypatch, cp, {("rev-parse", "--is-shallow-repository"): ("true\n", 0),
                                   ("rev-parse", "--git-common-dir"): ("", 128)})
    assert cp._shallow_boundaries() == "unreadable" and cp._UNREAD == {}


def test_real_data_field_unreadable_request_and_05(tmp_path, monkeypatch):
    """089 T-rd: an unreadable request.md is not checked and the item is still judged as built (M15);
    an unreadable 05 is not checked, never a TOTAL-line verdict."""
    cp = _cp()
    monkeypatch.setattr(cp, "_UNREAD", {})
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cp, "_git", lambda *a: ("x", 0))
    monkeypatch.setattr(cp, "_item_triggers", lambda cutoff: ({"150": ("abc1234", ["ccbot/realtest.py"])}, None))
    d = tmp_path / "work" / "150"
    d.mkdir(parents=True)
    (d / "request.md").write_bytes(BAD)
    (d / "05-build-report.md").write_bytes(BAD)
    names, entries, failed = cp.real_data_field("c" * 40, walked=([], None, None))
    assert "150" in names, names
    assert entries["150"] == ["request.md not checked (work/150/request.md unreadable; item 089)",
                              "05 not checked (work/150/05-build-report.md unreadable; item 089)"], entries


def test_research_code_unreadable_request(tmp_path, monkeypatch):
    """089 T-rc: an unreadable request.md is flagged with its why, strict, never counted as built (M16)."""
    cp = _cp()
    monkeypatch.setattr(cp, "_UNREAD", {})
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cp, "_git", lambda *a: ("x", 0))
    d = tmp_path / "work" / "150"
    d.mkdir(parents=True)
    (d / "request.md").write_bytes(BAD)
    walked = ([("a" * 40, ["work/150/01-research.md", "ccbot/x.py"])], None, None)
    assert cp.research_code("c" * 40, walked) == (
        "150", {"150": ("aaaaaaa", "RESEARCH ONLY check: work/150/request.md unreadable (item 089)")})


@NO_GIT
def test_unreadable_request_still_clashes(tmp_path):
    """089 T-ob: main's 050/request.md unreadable: the clash compare is still made (listed, never dropped,
    M13), and the file is on UNREADABLE (exit 1)."""
    repo = _repo_with_open_branch(tmp_path)
    _branch_adds(repo, "pr5", "050", ["05-build-report.md"], "# Work item 050\nType: IDEA\nScope: FULL\nDate: 2026-10-31\n")
    _item(repo, "050", ALL)
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "main 050")
    (repo / "work" / "050" / "request.md").write_bytes(BAD)
    code, out, err = _run3(repo, "--untracked-from", _root(repo), "--today", "2026-11-03")
    assert b"Traceback" not in err, err
    assert code == 1, out
    lines = out.splitlines()
    assert "ID CLASH: 050 (origin/pr5)" in lines, out
    assert "050: UNREADABLE (work/050/request.md unreadable)" in lines, out
    assert "UNREADABLE: work/050/request.md (not UTF-8 at byte 0)" in lines, out


def test_inbox_unreadable_daily_report(tmp_path, monkeypatch):
    """089 T-is: an unreadable newest daily report is not checked, named (listed on UNREADABLE by main)."""
    cp = _cp()
    monkeypatch.setattr(cp, "_UNREAD", {})
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cp, "_inbox_gate", lambda path: None)
    (tmp_path / "logs" / "audit").mkdir(parents=True)
    (tmp_path / "logs" / "audit" / "2026-11-20.md").write_bytes(BAD)
    assert cp.inbox_section(Path("logs/audit")) == ("not checked (2026-11-20.md unreadable)", False)
    assert cp._UNREAD == {"logs/audit/2026-11-20.md": "not UTF-8 at byte 0"}


@NO_GIT
def test_inbox_unreadable_working_template(tmp_path):
    """089 T-ig: an uncommitted report whose working template can't be read is not checked, never judged
    by a template not read; the template is on UNREADABLE."""
    _daily(tmp_path, "2026-11-18.md", INBOX_OK.format(sha="a" * 7), template=None, commit=False)
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "daily-audit.md").write_bytes(BAD)
    code, out, err = _run3(tmp_path, "--today", "2026-11-18")
    assert b"Traceback" not in err, err
    lines = out.splitlines()
    assert ("INBOX: not checked (2026-11-18.md not committed; its templates/daily-audit.md unreadable)"
            in lines), out
    assert "UNREADABLE: templates/daily-audit.md (not UTF-8 at byte 0)" in lines, out
    assert code == 1, out


def test_sent_back_unreadable_log_is_no_send_back(tmp_path, monkeypatch):
    """089 T-sb2: _sent_back skips an unreadable log (the refusal side), no exception."""
    cp = _cp()
    monkeypatch.setattr(cp, "_UNREAD", {})
    monkeypatch.chdir(tmp_path)
    _tree(tmp_path, BAD)
    (tmp_path / "work" / "150" / "05-build-report.md").write_text("x\n", encoding="utf-8")
    assert cp._sent_back("150") is False


# Item 090 (RI-010, RI-014): timed I2 field from TIMED_FROM, LOG BATCH not computable as INCOMPLETE, the
# per-round I2 bound, the round rule for --log after a send-back, and the shallow-clone readers.
TIMED_HINT = "<n> files changed | tests <last line of python3 -m pytest -q, as printed, with its ` in <s>s` time>"


def test_log_i2_untimed_refused_from_090(tmp_path):
    """090 T1 (M1, M3): from TIMED_FROM the I2 field needs pytest's ` in <s>s` right after the stats; a time
    only inside the note does not count; below it the untimed form is still written."""
    for item in ("089", "990"):
        _request(tmp_path, item)
    code, err = _log(tmp_path, "I2", "990", "1 file changed | tests 5 passed")
    assert code == 2 and f'"{TIMED_HINT}"' in err, err
    assert _log(tmp_path, "I2", "990", "1 file changed | tests 5 passed (in 3.00s)")[0] == 2
    assert not (tmp_path / "logs").exists()
    for tail in ("in 3.21s", "in 61.68s (0:01:01)", "in 3.21 seconds", "in 3.21s (note)"):
        code, err = _log(tmp_path, "I2", "990", f"1 file changed | tests 5 passed {tail}")
        assert code == 0, (tail, err)
    assert _log(tmp_path, "I2", "089", "1 file changed | tests 5 passed")[0] == 0


def test_timed_hint_fits_timed_format():
    """090 T2: the timed hint's example fits I2_TIMED and is accepted for an ID >= TIMED_FROM; log_hint picks it
    from TIMED_FROM on only (M2 is killed by test_i2_tests_field_cutoff's untimed 076 line)."""
    import re
    cp = _cp()
    example = cp.LOG_HINT_TIMED["I2"][1]
    assert re.fullmatch(cp.I2_TIMED, example)
    assert cp.log_fields_ok("I2", f"{cp.TIMED_FROM:03d}", example)
    assert cp.log_hint("I2", f"{cp.TIMED_FROM:03d}") == TIMED_HINT == cp.LOG_HINT_TIMED["I2"][0]
    assert cp.log_hint("I2", f"{cp.TIMED_FROM - 1:03d}") == cp.LOG_HINT["I2"][0]
    assert cp.TIMED_FROM == 90


TIMED_RULES = "TESTS_FORMAT_FROM = 76\nVERDICT_FROM = 71\nSUITE_FROM = 87\n"
TIMED_05 = "x\nSuite: 1 passed\n## Test output\n1 passed in 0.01s\n"   # a time, so LOG BATCH is computable


def _timed_repo(tmp_path, rules, commit_05=True):
    """S13-style: RULE_FILE `rules`, item 990 with every step, 05 TIMED_05 and one untimed I2 line."""
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "scripts/check_pipeline.py", rules)
    root = _commit(repo, "root")
    _suite_item(repo, TIMED_05, i2=("1 files changed | tests 1 passed",), item="990")
    if commit_05:
        root = _commit(repo, "990 built")
    _, out = _run(repo, "check_pipeline.py", "--untracked-from", root, "--today", SUITE_DAY)
    return root, out


@NO_GIT
def test_timed_gate(tmp_path):
    """090 T3: an untimed 990 I2 line whose 05 was added under a rule file without TIMED_FROM is RULE NOT SEEN
    (`judged by untimed I2 form`), not INCOMPLETE; with TIMED_FROM there it is INCOMPLETE with the timed hint;
    an uncommitted 05 (no anchor) is strict."""
    sha, out = _timed_repo(tmp_path / "a", TIMED_RULES)
    assert _pick(out, "RULE NOT SEEN:") == (f"RULE NOT SEEN: 990 (05 added in {sha[:7]} without TIMED_FROM (090): "
                                            "judged by untimed I2 form; item 084)"), out
    assert _pick(out, "INCOMPLETE:") == "INCOMPLETE: none", out
    want = f'INCOMPLETE: 990 (log line for I2 does not match its format (item 045): I2 wants "{TIMED_HINT}")'
    _, out = _timed_repo(tmp_path / "b", TIMED_RULES + "TIMED_FROM = 90\n")
    assert _pick(out, "INCOMPLETE:") == want, out
    assert _pick(out, "RULE NOT SEEN:") == "RULE NOT SEEN: none", out
    _, out = _timed_repo(tmp_path / "c", TIMED_RULES, commit_05=False)
    assert _pick(out, "INCOMPLETE:") == want, out
    assert _pick(out, "RULE NOT SEEN:") == "RULE NOT SEEN: none", out


@NO_GIT
def test_timed_gate_not_seen_keeps_suite_check(tmp_path):
    """090: a RULE NOT SEEN TIMED_FROM item still gets its Suite check against its untimed field."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "scripts/check_pipeline.py", TIMED_RULES)
    _commit(repo, "root")
    _suite_item(repo, TIMED_05.replace("Suite: 1 passed", "Suite: 2 passed"), i2=("1 files changed | tests 1 passed",),
                item="990")
    root = _commit(repo, "990 built")
    _, out = _run(repo, "check_pipeline.py", "--untracked-from", root, "--today", SUITE_DAY)
    assert _pick(out, "INCOMPLETE:") == f"INCOMPLETE: 990 ({_mismatch('2 passed', '1 passed')})", out


@pytest.mark.parametrize("item, strict", [("990", True), ("089", False)])
def test_batch_not_computable_strict_from_090(tmp_path, item, strict):
    """090 T4 (M4): an 083-shaped timed item with one more line timed 25:00 is not computable; from TIMED_FROM
    that is also INCOMPLETE `LOG BATCH not computable: log line with no valid time (item 090)` (exit 1); on
    089 it stays LOG BATCH text only (exit 0)."""
    r, i = _six("10:15")
    _batch_item(tmp_path, item, r, i + [(BATCH_DAY, "25:00", "I3", "PASS | sent to audit: yes")],
                "344 passed, 1 skipped in 48.51s", "344 passed, 1 skipped in 47.57s", full=True)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-21")
    assert f"; not computable: {item}: log line with no valid time" in _pick(out, "LOG BATCH:"), out
    inc = _pick(out, "INCOMPLETE:")
    if strict:
        assert inc == "INCOMPLETE: 990 (LOG BATCH not computable: log line with no valid time (item 090))", out
        assert code == 1, out
    else:
        assert inc == "INCOMPLETE: none" and code == 0, out


@pytest.mark.parametrize("item, inc", [
    ("990", "INCOMPLETE: 990 (LOG BATCH not computable: no line before I2 (item 090))"),
    ("089", "INCOMPLETE: none")])
def test_batch_no_line_before_i2_strict_from_090(tmp_path, item, inc):
    """090 T5 variant: a timed item whose first line is I2 (no line before it): INCOMPLETE from TIMED_FROM,
    text only below it."""
    impl = [(BATCH_DAY, "10:00", "I2", "1 files changed | tests 1 passed in 0.01s"),
            (BATCH_DAY, "10:05", "I3", "PASS | sent to audit: yes")]
    _batch_item(tmp_path, item, impl=impl, t05="1 passed in 0.01s", t06="1 passed in 0.02s", full=True)
    for s in ("01", "02", "03", "04"):                        # no step files before 05: no R1-I1 log lines owed
        (tmp_path / "work" / item / STEP_NAMES[s]).unlink()
    (tmp_path / "work" / item / "request.md").write_text(
        f"# Work item {item}\nScope: FULL\nDate: 2026-11-20\nWaived: 01 02 03 04 (person, 2026-11-20: test)\n",
        encoding="utf-8")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-21")
    assert f"not computable: {item}: no line before I2" in _pick(out, "LOG BATCH:"), out
    assert _pick(out, "INCOMPLETE:") == inc, out


def _round_item(root, rows, t05=None, t06=None, full=False, item="999"):
    _batch_item(root, item, impl=rows, t05=t05, t06=t06, full=full)
    return _bl(root)


@pytest.mark.parametrize("t, flagged", [("60.00", False), ("60.01", True)])
def test_round_bound_delta0_boundary(tmp_path, t, flagged):
    """090 T6: Δ0 (I1 and I2 at 10:00), limit 60 s: 60.00 - 0.005 = 59.995 < 60 is not flagged, 60.01 -> 60.005
    is; the whole-item window (10:00 -> 10:30) is not flagged either way."""
    res = _round_item(tmp_path, [(BATCH_DAY, "10:00", "I1", "FIT | 1 files planned"),
                                 (BATCH_DAY, "10:00", "I2", f"1 files changed | tests 1 passed in {t}s"),
                                 (BATCH_DAY, "10:30", "I3", "PASS | sent to audit: yes")], t06="1 passed in 1.00s")
    want = ["999 I2 at 2026-11-20 10:00 (60.01 s pytest run after the I1 line at 10:00, limit 60 s; impossible under "
            "the run-item order, item 090)"] if flagged else []
    assert res["flagged"] == want and res["flagged_ids"] == (["999"] if flagged else []), res


ROUND2 = [(BATCH_DAY, "09:20", "I1", "FIT | 1 files planned"),
          (BATCH_DAY, "09:30", "I2", "1 files changed | tests 1 passed in 50.00s"),
          (BATCH_DAY, "09:50", "I3", "FAIL | sent to audit: no"),
          (BATCH_DAY, "10:05", "I1", "FIT | 1 files planned"),
          (BATCH_DAY, "10:05", "I2", "1 files changed | tests 1 passed in 80.00s"),
          (BATCH_DAY, "10:20", "I3", "PASS | sent to audit: yes")]
ROUND2_FLAG = ("999 I2 at 2026-11-20 10:05 (80.00 s pytest run after the I1 line at 10:05, limit 60 s; impossible "
               "under the run-item order, item 090)")


def test_round_bound_round2_batch(tmp_path):
    """090 T7 (M6): a round-2 I2 in the same minute as its I1 (80.00 s) is flagged; round 1 (50.00 s, Δ10) and the
    whole item (09:20 -> 10:20) are not. With prev = the item's first line it would be Δ65 (not flagged)."""
    _batch_item(tmp_path, "999", research=[(BATCH_DAY, "09:00", "R1", "brief written | 1")], impl=ROUND2)
    res = _bl(tmp_path)
    assert res["flagged"] == [ROUND2_FLAG] and res["flagged_ids"] == ["999"], res


def test_round_bound_delta1_limit_120(tmp_path):
    """090 T8 (M5): Δ1 (I1 10:00, I2 10:01): limit (1+1)*60 = 120 s, 86.00 s is not flagged."""
    res = _round_item(tmp_path, [(BATCH_DAY, "10:00", "I1", "FIT | 1 files planned"),
                                 (BATCH_DAY, "10:01", "I2", "1 files changed | tests 1 passed in 86.00s"),
                                 (BATCH_DAY, "10:30", "I3", "PASS | sent to audit: yes")])
    assert res["flagged"] == [], res


def test_round_bound_interleaved_items(tmp_path):
    """090 T9 (M7): three items, R1 and I1 at 23:27, I2 at 23:29 / 23:30 / 23:31 (70 s runs); each item's I3 is
    in the next item's I2 minute, above it. Per item, prev is the item's own I1 (Δ >= 2): none flagged; another
    item's I3 as prev would be Δ0."""
    impl = []
    for n, item in enumerate(("997", "998", "999")):
        _batch_item(tmp_path, item, [(BATCH_DAY, "23:27", "R1", "brief written | 1")],
                    [(BATCH_DAY, "23:27", "I1", "FIT | 1 files planned")])
    rows = [("23:29", "I2", "997"), ("23:30", "I3", "997"), ("23:30", "I2", "998"), ("23:31", "I3", "998"),
            ("23:31", "I2", "999"), ("23:32", "I3", "999")]
    with (tmp_path / "logs" / "implementation" / f"{BATCH_DAY}.md").open("a", encoding="utf-8") as fh:
        for hhmm, agent, item in rows:
            fields = "1 files changed | tests 1 passed in 70.00s" if agent == "I2" else "PASS | sent to audit: yes"
            fh.write(f"{hhmm} | {agent} | {item} | {fields}\n")
    res = _bl(tmp_path)
    assert res["flagged"] == [] and res["checked"] == 3, res


def test_round_bound_fast_prev_is_research(tmp_path):
    """090 T10: FAST shape: the R3 research line at the I2 minute is prev (Δ0): 70.00 s is flagged."""
    _batch_item(tmp_path, "999", [(BATCH_DAY, "10:15", "R3", "1 verified, 0 fixed, 0 removed | READY")],
                [(BATCH_DAY, "10:15", "I2", "1 files changed | tests 1 passed in 70.00s"),
                 (BATCH_DAY, "10:30", "I3", "PASS | sent to audit: yes")])
    assert _bl(tmp_path)["flagged"] == ["999 I2 at 2026-11-20 10:15 (70.00 s pytest run after the R3 line at 10:15, "
                                        "limit 60 s; impossible under the run-item order, item 090)"]


def test_round_bound_on_repo_data():
    """090 T11: on this repo's work/ and logs/ the per-round bound flags no I2 round (0 of 17 on 2026-11-21)."""
    res = _cp().batch_log_items(REPO / "work", REPO / "logs")
    assert not [f for f in res["flagged"] if f.endswith("item 090)")], res


def test_round_bound_end_to_end(tmp_path):
    """090 T12: T7's shape as a full item: `LOG BATCH: <the round entry>` and exit 1."""
    research = [(BATCH_DAY, "09:00", "R1", "brief written | 1"), (BATCH_DAY, "09:05", "R2", FIELDS["R2"]),
                (BATCH_DAY, "09:10", "R3", FIELDS["R3"])]
    _batch_item(tmp_path, "999", research=research, impl=ROUND2, t05="1 passed in 80.00s", t06="1 passed in 1.00s",
                full=True)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-21")
    assert _pick(out, "LOG BATCH:") == f"LOG BATCH: {ROUND2_FLAG}", out
    assert _pick(out, "INCOMPLETE:") == "INCOMPLETE: none", out
    assert code == 1, out


@pytest.mark.parametrize("team, sender, fields, steps, path, body, agent, want", [
    ("implementation", "I3", "FAIL | sent to audit: no", "010203040506", "06", "Verdict: PASS (round 2)\n", "I2",
     "work/999/06-verification.md no longer says FAIL (PASS); I3 ran again before this line"),
    ("research", "R3", "1 verified, 0 fixed, 0 removed | BLOCKED", "0102", "03", "Status: READY\n", "R1",
     "work/999/03-handoff.md no longer says BLOCKED (READY)"),
    ("implementation", "I1", "NOT A FIT | 0 files planned", "010203", "04", "Fit verdict: FIT\n", "R2",
     "work/999/04-build-plan.md no longer says NOT A FIT (FIT)"),
    ("implementation", "I1", "NOT A FIT | 0 files planned", "010203", "04",
     "Fit verdict: FIT | FIT WITH CHANGES | NOT A FIT\n", "R2", "(no readable Fit verdict: line)"),
    ("implementation", "I3", "FAIL | sent to audit: no", "010203040506", "06",
     "Verdict: PASS (round 2; earlier rounds: FAIL)\n", "I2", "no longer says FAIL (PASS)"),
    ("implementation", "I3", "FAIL | sent to audit: no", "010203040506", "06", b"\xff", "I2",
     "(work/999/06-verification.md unreadable)"),
    ("implementation", "I3", "FAIL | sent to audit: no", "0102030405", None, None, "I2", "(absent)"),
], ids=["06-pass", "03-ready", "04-fit", "04-unfilled", "06-earlier-fail", "06-unreadable", "06-absent"])
def test_round_content_refusal(tmp_path, team, sender, fields, steps, path, body, agent, want):
    """090 T14 (M9, M10, M17): in an open round, a step before the sender is refused when the sender's file
    no longer shows its send-back verdict (first verdict line, the unfilled template line reads as none, a
    later word in the line is not it), is unreadable or absent; exit 2, nothing written."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", [steps[k:k + 2] for k in range(0, len(steps), 2)])
    if path:
        f = tmp_path / "work" / "999" / STEP_NAMES[path]
        f.write_bytes(body) if isinstance(body, bytes) else f.write_text(body + "x\n", encoding="utf-8")
    _log_line(tmp_path, team, "999", sender, fields)
    code, err = _log(tmp_path, agent, "999", FIELDS[agent])
    assert code == 2 and want in err and "(item 090)" in err, err
    assert not _written(tmp_path, agent, "999")


def test_round_unreadable_07_keeps_rule_d(tmp_path):
    """090 (missing input 07): an unreadable 07 adds no send-back, so rule D refuses as today."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", ("01", "02", "03", "04", "05", "06"))
    (tmp_path / "work" / "999" / "07-audit-task.md").write_bytes(b"\xff")
    code, err = _log(tmp_path, "I1", "999", "FIT | 1 files planned")
    assert code == 2 and "(item 086)" in err, err


def test_round_open_refuses_later_step(tmp_path):
    """090 T15 (M15): I1 sent the item back (NOT A FIT) and has not logged again: `--log I2` is refused."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", ("01", "02", "03", "04"))
    (tmp_path / "work" / "999" / "04-build-plan.md").write_text("Fit verdict: NOT A FIT\n", encoding="utf-8")
    _log_line(tmp_path, "implementation", "999", "I1", "NOT A FIT | 0 files planned")
    code, err = _log(tmp_path, "I2", "999", FIELDS["I2"])
    assert code == 2, err
    assert ("--log refused: I1 sent work/999 back at 2000-01-01 10:00 and has not logged again; I1 runs before I2 "
            "(item 090)") in err, err


def _round_069(root, extra=()):
    """069's shape: 01-06, 06 PASS (round 2), lines I1, I2, I3 FAIL, I2, I3 PASS (+ extra), 07 A1 FAIL."""
    _request(root, "999")
    _steps(root, "999", ("01", "02", "03", "04", "05", "06"))
    (root / "work" / "999" / "06-verification.md").write_text("Verdict: PASS (round 2)\nx\n", encoding="utf-8")
    (root / "work" / "999" / "07-audit-task.md").write_text("x\nA1 result: FAIL (test)\n", encoding="utf-8")
    for agent, fields in (("I1", FIELDS["I1"]), ("I2", FIELDS["I2"]), ("I3", "FAIL | sent to audit: no"),
                          ("I2", FIELDS["I2"]), ("I3", "PASS | sent to audit: yes"), *extra):
        _log_line(root, "implementation", "999", agent, fields)


def test_round_069_shape(tmp_path):
    """090 T16 (M8, M16): after 069's A1 FAIL the round-3 I1, I2 and I3 log cleanly (the I3 FAIL round closed
    at I3 PASS, so 06's PASS is not read); with a round-3 I2 already logged, `--log I1` is refused (order)."""
    _round_069(tmp_path)
    assert _log(tmp_path, "I1", "999", FIELDS["I1"]) == (0, "")
    assert _log(tmp_path, "I2", "999", FIELDS["I2"]) == (0, "")
    assert _log(tmp_path, "I3", "999", "PASS | sent to audit: yes") == (0, "")
    twin = tmp_path / "twin"
    _round_069(twin, extra=(("I2", FIELDS["I2"]),))
    code, err = _log(twin, "I1", "999", FIELDS["I1"])
    assert code == 2, err
    assert "--log refused: I2 already logged at 10:00 after I3 10:00; log steps in order (item 090)" in err, err


def test_round_unreadable_log_refused(tmp_path):
    """090 T17: an unreadable log file with an I3 FAIL in another file: `--log I2` is refused, order not checked."""
    _request(tmp_path, "999")
    _steps(tmp_path, "999", ("01", "02", "03", "04", "05", "06"))
    (tmp_path / "work" / "999" / "06-verification.md").write_text("Verdict: FAIL (round 1)\nx\n", encoding="utf-8")
    _log_line(tmp_path, "implementation", "999", "I3", "FAIL | sent to audit: no")
    (tmp_path / "logs" / "implementation" / "2000-01-02.md").write_bytes(b"\xff\xfe")
    code, err = _log(tmp_path, "I2", "999", FIELDS["I2"])
    assert code == 2, err
    assert ("--log refused: logs/implementation/2000-01-02.md unreadable; order not checked (item 090)") in err, err


SHALLOW_LINE_TEXT = "not checked (shallow clone; run git fetch --unshallow)"


def _shallow_source(tmp_path, monkeypatch, late=True, branch="claude-x"):
    """origin (HEAD -> dev): main = c1 (work/150 + a log line `23:59` or `01:00` on 2026-11-20, committed
    2026-11-20 01:30) and c2 (2026-11-21 00:30); dev = main + c3 (HEAD's tip one commit ahead of main); an open
    branch off main with one .claude/x.md commit, or (branch=None) an orphan README-only branch `docs`."""
    origin, src = tmp_path / "origin.git", tmp_path / "src"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    _git(tmp_path, "clone", "-q", str(origin), str(src))
    _git(src, "checkout", "-q", "-b", "main")
    _item(src, "150", [], date="2026-11-20", logged=False)
    _write(src, "logs/implementation/2026-11-20.md",
           f"{'23:59' if late else '01:00'} | I3 | 150 | PASS | sent to audit: yes\n")
    monkeypatch.setenv("GIT_COMMITTER_DATE", "2026-11-20T01:30:00+00:00")
    _commit(src, "c1")
    monkeypatch.setenv("GIT_COMMITTER_DATE", "2026-11-21T00:30:00+00:00")
    _write(src, "notes/a.md")
    _commit(src, "c2")
    _git(src, "push", "-q", "origin", "main")
    if branch:
        _git(src, "checkout", "-q", "-b", branch)
        _write(src, ".claude/x.md")
        _commit(src, "rules")
        _git(src, "push", "-q", "origin", branch)
    else:
        _orphan(src, "docs", {})
    _git(src, "checkout", "-q", "-b", "dev", "main")
    _write(src, "notes/b.md")
    _commit(src, "c3")
    _git(src, "push", "-q", "origin", "dev")
    _git(origin, "symbolic-ref", "HEAD", "refs/heads/dev")
    monkeypatch.delenv("GIT_COMMITTER_DATE")
    return origin


def _clone(tmp_path, origin, name, *args):
    repo = tmp_path / name
    _git(tmp_path, "clone", "-q", *args, "--no-single-branch", f"file://{origin}", str(repo))
    flag = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=repo, capture_output=True, text=True)
    code, out = _run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-21")
    return flag.stdout.strip(), code, out


@NO_GIT
def test_shallow_three_readers_not_checked(tmp_path, monkeypatch):
    """090 T18 (M11): full-clone control: LOG TIME names the late line, no MAIN AHEAD line, the branch is
    scanned. Depth 1: LOG TIME, MAIN AHEAD and the unrelated branch say not checked, origin/main is not listed,
    and the branch's .claude/ file is a BRANCH ERROR (exit 1)."""
    origin = _shallow_source(tmp_path, monkeypatch)
    flag, code, out = _clone(tmp_path, origin, "full")
    lines = out.splitlines()
    assert flag == "false"
    assert _pick(out, "LOG TIME:") == "LOG TIME: 150 I3 (2026-11-20 23:59 after commit 2026-11-20 01:30 UTC)", out
    assert "MAIN AHEAD" not in out, out
    assert any(l.startswith("  origin/claude-x: items none; merges cleanly") for l in lines), out
    flag, code, out = _clone(tmp_path, origin, "d1", "--depth", "1")
    lines = out.splitlines()
    assert flag == "true"
    assert _pick(out, "LOG TIME:") == f"LOG TIME: {SHALLOW_LINE_TEXT}", out
    assert _pick(out, "MAIN AHEAD:") == f"MAIN AHEAD: {SHALLOW_LINE_TEXT}", out
    assert any(l.startswith(f"  origin/claude-x: {SHALLOW_LINE_TEXT}") for l in lines), out
    assert not any(l.startswith("  origin/main:") for l in lines), out
    assert _pick(out, "BRANCH ERROR:").startswith("BRANCH ERROR: origin/claude-x (shallow clone; "), out
    assert "run git fetch --unshallow (item 090))" in _pick(out, "BRANCH ERROR:"), out
    assert code == 1, out


@NO_GIT
def test_shallow_docs_only_orphan_exit_0(tmp_path, monkeypatch):
    """090 T19 (M11-M14): depth 1 with only an orphan README-only branch and no late line: the three not-checked
    lines and exit 0 (not-checked lines never change the exit; origin/main is not turned into a BRANCH ERROR)."""
    origin = _shallow_source(tmp_path, monkeypatch, late=False, branch=None)
    flag, code, out = _clone(tmp_path, origin, "d1", "--depth", "1")
    lines = out.splitlines()
    assert flag == "true"
    assert _pick(out, "LOG TIME:") == f"LOG TIME: {SHALLOW_LINE_TEXT}", out
    assert _pick(out, "MAIN AHEAD:") == f"MAIN AHEAD: {SHALLOW_LINE_TEXT}", out
    assert any(l.startswith(f"  origin/docs: {SHALLOW_LINE_TEXT}") for l in lines), out
    assert "BRANCH ERROR" not in out and not any(l.startswith("  origin/main:") for l in lines), out
    assert code == 0, out


def test_open_branches_default_computes_shallow(monkeypatch):
    """090 T20: open_branches() with no args (check_handoff's call) computes shallowness: origin/main is skipped
    and main_ahead is never called; _is_shallow reads "unreadable" and boundaries as shallow; main_ahead(True)
    with no ref is still 0 (no line)."""
    cp = _cp()
    branch = ("branch", "-r", "--no-merged", "HEAD", "--format=%(refname:short)")
    monkeypatch.setattr(cp, "_git", lambda *a: ("origin/main\n", 0) if a == branch else ("", 0))
    monkeypatch.setattr(cp, "main_ahead", lambda *a: (_ for _ in ()).throw(AssertionError("main_ahead called")))
    monkeypatch.setattr(cp, "_is_shallow", lambda: True)
    assert cp.open_branches() == []
    monkeypatch.undo()
    for value, want in (("unreadable", True), (["a" * 40], True), ([], False), ("full", False)):
        monkeypatch.setattr(cp, "_shallow_boundaries", lambda v=value: v)
        assert cp._is_shallow() is want, value
    monkeypatch.setattr(cp, "_git", lambda *a: ("", 0))
    assert cp.main_ahead(shallow=True) == 0


def test_i2_and_run_item_texts_name_item_090():
    """090: the i2-builder and run-item rule texts state the timed field and the round rule (text pins)."""
    i2 = (REPO / ".claude" / "agents" / "i2-builder.md").read_text(encoding="utf-8")
    assert ("From item 090 (TIMED_FROM) the field must keep pytest's ` in <s>s` time; `--log` refuses it without "
            "one.") in i2
    run = (REPO / ".claude" / "commands" / "run-item.md").read_text(encoding="utf-8")
    assert "it refuses a step after the sender until the sender logs again" in run and "(item 090)" in run
    assert "unless the item was sent back" not in run


# Item 091 step 5a/5b (086 F3, RI-010): round headings LOG BATCH does not read.
RH_TEMPLATE = {"templates/build-report.md": ("## Test output (round N, pasted)", "## Test output (round 2, pasted)"),
                  "templates/verification.md": ("## Tests re-run (round N)", "## Tests re-run (round 2)")}


def _rh_line(heading):
    return (f"Each later round's runs go under their own level-2 heading `{heading}`, never under a `###` heading "
            f"or a `Round N ...` heading (item 091).")


def test_round_heading_template_lines():
    """5a: each template states the round heading once; the heading parses with LOG BATCH's opener
    (RUN_HEADING, as batch_log_items passes it) and the line itself is never a stray heading."""
    cp = _cp()
    for (f, (heading, example)), step in zip(RH_TEMPLATE.items(), ("05", "06")):
        line = _rh_line(heading)
        assert (REPO / f).read_text(encoding="utf-8").count(line) == 1, f
        assert re.match(cp.RUN_HEADING[step], example), example
        assert cp.STRAY_RUN_HEADING.match(line) is None


RH_ID, RH_DAY = "150", "2026-11-21"
RH_USE = "is not read by LOG BATCH; use '## Test output (round N, pasted)' / '## Tests re-run (round N)' (item 091)"
RH_P1 = "## Round 2\n### Test output (round 2, pasted)\n```\n2 passed in 1.50s\n```\n"


def _rh_item(root, body05=None, body06=None, item=RH_ID):
    """A complete item (_item, every step and log line) with text appended to 05 and/or 06; 05 keeps
    its Suite line, so only the round-heading check can fire."""
    _item(root, item, ALL, date=RH_DAY)
    d = root / "work" / item
    for name, body in (("05-build-report.md", body05), ("06-verification.md", body06)):
        if body is not None:
            f = d / name
            f.write_text(f.read_text(encoding="utf-8") + body, encoding="utf-8")
    return d


def _rh_inc(root):
    code, out = _run(root, "check_pipeline.py", "--today", RH_DAY)
    return code, _pick(out, "INCOMPLETE:"), out


@pytest.mark.parametrize("step, body, heading", [
    ("05", RH_P1, "### Test output (round 2, pasted)"),
    ("05", "## Round 2 test output (pasted)\n2 passed in 1.50s\n", "## Round 2 test output (pasted)"),
    ("06", "## Round 1\n### Tests re-run (output)\n2 passed in 1.50s\n", "### Tests re-run (output)"),
], ids=["P1", "P2", "P3"])
def test_stray_round_heading_is_incomplete(tmp_path, step, body, heading):
    """RH_P1-P3: a run heading outside every read section is one INCOMPLETE entry naming it (no git: strict)."""
    d = _rh_item(tmp_path, **{f"body{step}": body})
    code, inc, out = _rh_inc(tmp_path)
    assert inc == f"INCOMPLETE: {RH_ID} ({step} heading '{heading}' {RH_USE})", out
    assert code == 1, out
    if step == "05":                                        # why: LOG BATCH reads no time under it
        cp = _cp()
        assert 1.5 not in cp._run_seconds(d / "05-build-report.md", cp.RUN_HEADING["05"])[0]


def test_stray_round_headings_one_entry_per_file(tmp_path):
    """Two stray headings in 05 are one entry, joined by ', '."""
    _rh_item(tmp_path, body05=RH_P1 + "## Round 3 test output\n")
    _, inc, out = _rh_inc(tmp_path)
    assert inc == (f"INCOMPLETE: {RH_ID} (05 heading '### Test output (round 2, pasted)', "
                   f"'## Round 3 test output' {RH_USE})"), out


@pytest.mark.parametrize("body05, item", [
    ("## Test output (pasted, not summarized)\n### Test output (detail)\n```\n2 passed in 1.50s\n```\n", RH_ID),
    ("## Notes on test output\nRound 2 runs go under ## Test output (round 2, pasted), never ### Test output.\n",
     RH_ID),
    (RH_P1, "091"),
    ("## Test output (round 2, pasted)\n```\n2 passed in 1.50s\n```\n", RH_ID),
], ids=["N1-inside-section", "N2-not-at-start", "N3-below-cutoff", "N4-round-opener"])
def test_read_or_unnamed_heading_is_not_stray(tmp_path, body05, item):
    """N1: a `###` run heading inside the `## Test output` section is read; N2: the name not at the line
    start (a heading or prose) is not a run heading (anchored .match, RI-012); N3: ID below
    ROUND_HEADING_FROM; N4: the round heading the template asks for."""
    d = _rh_item(tmp_path, body05=body05, item=item)
    code, inc, out = _rh_inc(tmp_path)
    assert inc == "INCOMPLETE: none" and code == 0, out
    if body05.startswith("## Test output (pasted"):         # N1: LOG BATCH reads its time
        cp = _cp()
        assert 1.5 in cp._run_seconds(d / "05-build-report.md", cp.RUN_HEADING["05"])[0]


def test_unreadable_05_round_headings_not_checked(tmp_path):
    """U: a non-UTF-8 05 is `not checked` with the reason (and on UNREADABLE), never a pass."""
    d = _rh_item(tmp_path)
    (d / "05-build-report.md").write_bytes(b"## Round 2\n\xff")
    code, inc, out = _rh_inc(tmp_path)
    path = f"work/{RH_ID}/05-build-report.md"
    assert f"05 round headings not checked ({path} unreadable; item 091)" in inc, out
    assert f"UNREADABLE: {path} (not UTF-8 at byte 11)" in out.splitlines(), out
    assert code == 1, out


@NO_GIT
@pytest.mark.parametrize("seen", [False, True], ids=["G-not-seen", "G-seen"])
def test_round_heading_gate_follows_rule_file_of_05_commit(tmp_path, seen):
    """G: RH_P1's 05 added in a commit whose rule file has no ROUND_HEADING_FROM: RULE NOT SEEN, no entry
    (item 084 gate). With the constant there: the INCOMPLETE entry and RULE NOT SEEN none."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    rules = "TESTS_FORMAT_FROM = 76\nVERDICT_FROM = 71\nSUITE_FROM = 87\nTIMED_FROM = 90\n"
    _write(repo, "scripts/check_pipeline.py", rules + ("ROUND_HEADING_FROM = 92\n" if seen else ""))
    _rh_item(repo, body05=RH_P1)
    root = _commit(repo, "150 built")
    _, out = _run(repo, "check_pipeline.py", "--untracked-from", root, "--today", RH_DAY)
    if seen:
        assert _pick(out, "INCOMPLETE:") == (f"INCOMPLETE: {RH_ID} (05 heading "
                                             f"'### Test output (round 2, pasted)' {RH_USE})"), out
        assert _pick(out, "RULE NOT SEEN:") == "RULE NOT SEEN: none", out
    else:
        assert _pick(out, "INCOMPLETE:") == "INCOMPLETE: none", out
        assert _pick(out, "RULE NOT SEEN:") == (f"RULE NOT SEEN: {RH_ID} (05 added in {root[:7]} without "
                                                "ROUND_HEADING_FROM (091): judged by no round-heading check; "
                                                "item 084)"), out


def test_section_flags_match_run_seconds_rule():
    """_section_flags: opener and closer rows are False; `###` neither opens nor closes."""
    cp = _cp()
    rows, _ = cp._md_lines("a\n## Test output (x)\nb\n### sub\nc\n## Next\nd\n")
    assert cp._section_flags(rows, cp.RUN_HEADING["05"]) == [False, False, True, True, True, False, False]


# Item 091 step 7 (RI-007): one scratch-dir sentence in four rule files (text only: no check sees a collision).
SCRATCH = ("Every agent works in its own new scratch dir, made with `python3 -c 'import tempfile; "
           "print(tempfile.mkdtemp(prefix=\"<agent>-<ID>-r<round>-\", dir=\"<absolute scratchpad path>\"))'`, and "
           "never reuses or writes into another agent's dir, even for the same item; agents with no shell (R1-R3, "
           "I1) get theirs from the orchestrator (item 091).")


def test_scratch_sentence_same_in_four_files():
    for f in (".claude/commands/run-item.md", ".claude/agents/i2-builder.md", ".claude/agents/i3-verifier.md",
              ".claude/agents/a1-auditor.md"):
        assert (REPO / f).read_text(encoding="utf-8").count(SCRATCH) == 1, f
