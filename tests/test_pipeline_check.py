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
    assert "RESEARCH CODE: none" in out                 # item 062


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


def _branch_adds(repo, branch, item, files, request_text=None, extra=()):
    """Push branch `branch` off main that adds work/<item> with `files` (item 037/038 tests),
    plus the paths in `extra` (item 062)."""
    _git(repo, "checkout", "-q", "-b", branch, "main")
    for path in extra:
        _write(repo, path)
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
            fh.write("".join(f"20:00 | {a} | {item} | {FIELDS[a]}\n" for a in ("I1", "I2")))
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
    log.write_text("20:40 | I2 | 150 | 1 files changed | tests 1/1\n", encoding="utf-8")
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
NO_GIT = pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
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
