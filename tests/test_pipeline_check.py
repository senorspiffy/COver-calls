"""scripts/check_pipeline.py (items 026, 029; RI-007) and check_handoff.py --all (item 028)."""
import os
import shutil
import subprocess
import sys

import pytest

from conftest import REPO


AGENTS = {"01": "R1", "02": "R2", "03": "R3", "04": "I1", "05": "I2", "06": "I3"}
# One well-formed field set per agent (item 045, LOG_FORMAT).
FIELDS = {"R1": "brief written | 0", "R2": "3 for / 3 against | languages: N/A",
          "R3": "1 verified, 0 fixed, 0 removed | READY", "I1": "FIT | 1 files planned",
          "I2": "1 files changed | tests 1/1", "I3": "PASS | sent to audit: yes"}


def _item(root, item, files, scope="FULL", date="2026-10-31", waived=None, a1="A1 result: PASS (test)",
          logged=True):
    """A fixture item. Its 06 carries the step-0 line and each step gets its log line (item 043)."""
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
            body += "Recurring issues checked: RI-007\n"
        (d / f).write_text(body, encoding="utf-8")
        agent = AGENTS.get(f[:2])
        if agent and logged:
            log = root / "logs" / ("research" if agent[0] == "R" else "implementation") / f"{date}.md"
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("a", encoding="utf-8") as fh:
                fh.write(f"12:00 | {agent} | {item} | {FIELDS[agent]}\n")


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


def _branch_adds(repo, branch, item, files, request_text=None):
    """Push branch `branch` off main that adds work/<item> with `files` (item 037/038 tests)."""
    _git(repo, "checkout", "-q", "-b", branch, "main")
    d = repo / "work" / item
    d.mkdir(parents=True, exist_ok=True)
    (d / "request.md").write_text(request_text or f"# Work item {item}\nScope: FULL\nDate: 2026-10-31\n",
                                  encoding="utf-8")
    for f in files:
        (d / f).write_text("x\nA1 result: PASS (test)\n", encoding="utf-8")
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
    code, out = _run(repo, "check_pipeline.py", "--today", "2026-11-03")
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
    code, out = _run(repo, "check_pipeline.py", "--today", "2026-11-03")
    assert code == 0                               # a branch never fails main's check
    assert "BRANCH SKIPPED: 060 (origin/short: FULL: missing 01 02 03 04 before 05)" in out
    assert "BRANCH SKIPPED: 040" not in out        # origin/fix has 01-07 for 040
    assert "SKIPPED: none" in out


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_open_branch_line_shows_last_commit_age(tmp_path):
    """Item 039: a branch waiting for days stands out."""
    repo = _repo_with_open_branch(tmp_path)
    when = subprocess.run(["git", "log", "-1", "--format=%cs", "origin/fix"], cwd=repo,
                          capture_output=True, text=True).stdout.strip()
    import datetime as dt
    today = dt.date.fromisoformat(when) + dt.timedelta(days=3)
    out = _run(repo, "check_pipeline.py", "--today", today.isoformat())[1]
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
    (tmp_path / "work" / "131" / "06-verification.md").write_text("x\n", encoding="utf-8")
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
    code, out = _run(tmp_path, "check_pipeline.py", "--log", "I2", "150", "2 files changed | tests 9/9")
    after = dt.datetime.now(dt.timezone.utc)
    assert code == 0
    logs = list((tmp_path / "logs" / "implementation").glob("*.md"))
    assert len(logs) == 1 and not (tmp_path / "logs" / "research").exists()
    text = logs[0].read_text(encoding="utf-8")
    assert text.startswith("# Implementation log - ")
    line = text.splitlines()[-1]
    stamp = dt.datetime.fromisoformat(f"{logs[0].stem}T{line[:5]}+00:00")
    assert before <= stamp <= after
    assert line[5:] == " | I2 | 150 | 2 files changed | tests 9/9"


@pytest.mark.parametrize("agent, fields", [("I2", "see 05"), ("I1", "FIT | see 04"), ("R9", "x"),
                                           ("R1", "brief written | many")])
def test_log_refuses_bad_fields(tmp_path, agent, fields):
    """045: the 2026-11-04 placeholders are refused and nothing is written."""
    code, _ = _run(tmp_path, "check_pipeline.py", "--log", agent, "150", fields)
    assert code == 2 and not (tmp_path / "logs").exists()


def test_log_refuses_item_without_request(tmp_path):
    """047: a well-formed line for an ID with no work/<ID>/request.md is refused, nothing written."""
    (tmp_path / "work" / "999").mkdir(parents=True)   # folder alone is not enough
    code, _ = _run(tmp_path, "check_pipeline.py", "--log", "I2", "999", "1 file changed | tests 1/1")
    assert code == 2 and not (tmp_path / "logs").exists()


def test_orphan_log_line_is_reported(tmp_path):
    """047: a log line for an item with no work folder is ORPHAN LOG (exit 1); real items are not."""
    _item(tmp_path, "150", ALL)
    with (tmp_path / "logs" / "implementation" / "2026-10-31.md").open("a", encoding="utf-8") as fh:
        fh.write("12:05 | I2 | 999 | 1 file changed | tests 1/1\n")
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
    log.write_text("22:24 | I1 | 150 | FIT | 1 files planned\n23:10 | I2 | 150 | 1 files changed | tests 1/1\n"
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
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-05")
    line = [l for l in out.splitlines() if l.startswith("LOG TIME:")][0]
    assert code == 1
    assert "150 I2 (2026-11-04 23:10 after commit 2026-11-04 22:24 UTC)" in line
    assert "150 I3 (2026-11-05 09:00" in line
    assert "I1" not in line and "044" not in line and "R1" not in line


def test_log_time_not_checked_outside_git(tmp_path):
    _item(tmp_path, "150", ALL)
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-05")
    assert code == 0 and "LOG TIME: not checked (no git)" in out


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_rules_branch_is_reported(tmp_path):
    """049 (RI-010): 048 was built on main while PR #12 changed the logging rules. An open branch
    that changes .claude/, templates/ or the check scripts is named; one that changes only work/
    and logs/ is not."""
    repo = _repo_with_open_branch(tmp_path)
    code, out = _run(repo, "check_pipeline.py", "--today", "2026-11-02")
    assert "RULES BRANCH: none" in out
    _git(repo, "checkout", "-q", "-b", "rules")
    agent = repo / ".claude" / "agents" / "x.md"
    agent.parent.mkdir(parents=True)
    agent.write_text("new rule\n", encoding="utf-8")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "rules")
    _git(repo, "push", "-q", "origin", "rules")
    _git(repo, "checkout", "-q", "main")
    code, out = _run(repo, "check_pipeline.py", "--today", "2026-11-02")
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
            fh.write("".join(f"20:00 | {a} | {item} | {FIELDS[a]}\n" for a in ("I1", "I2")))
    _commit_all(tmp_path, "2026-11-07T20:20:51+00:00")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-08")
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
    _, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-08")
    assert "LOG TIME: 150 I2" in out
    log.write_text("20:40 | I2 | 150 | 1 files changed | tests 1/1\n", encoding="utf-8")
    _commit_all(tmp_path, "2026-11-07T22:00:00+00:00")
    _, out = _run(tmp_path, "check_pipeline.py", "--today", "2026-11-08")
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
            'I2 wants "<n> files changed | tests <pass>/<total>")') in out
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "check_pipeline.py"), "--log", "I2", "150", "see 05"],
                       cwd=tmp_path, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 2
    assert r.stderr.strip() == '--log refused: I2 | 150 | see 05 does not match "<n> files changed | tests <pass>/<total>"'


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
    out = _run(repo, "check_pipeline.py", "--today", "2026-11-09")[1]
    assert "MAIN AHEAD: origin/main has 1 commits not in HEAD; merge it before building (item 051)" in out
    assert "origin/main:" not in out and "origin/mirror:" not in out
    assert "(item 036)" not in out
    assert _run(repo, "check_pipeline.py", "--next-id")[1].strip() == "042"   # main's 041 still counts
    _git(repo, "checkout", "-q", "main")
    out = _run(repo, "check_pipeline.py", "--today", "2026-11-09")[1]
    assert "MAIN AHEAD" not in out
    assert "origin/fix: items 040" in out
