"""Item 070 (RI-010/RI-013): check_pipeline.py requires diff_reports' TOTAL line in the 05/06
Real-data effect section when an item's own commits change realtest's decision path."""
import ast
import json
import sys

import pytest

from conftest import REPO
from test_pipeline_check import _item, _git, _run, _history, _write, _commit, NO_GIT, ALL, _cp

HEAD = "## Real-data effect (diff_reports output, pasted)"
TOTAL = ("TOTAL: files 1, only-before 0, only-after 0, not compared 0, json changes 1, "
         "csv rows changed 0 added 0 removed 0, columns changed 0")
FILLED = f"{HEAD}\n```\n{TOTAL}\n```\n"
# the template's own comment, as I2/I3 would leave it unfilled
COMMENT = (f"{HEAD}\n<!-- Required when the item changes ccbot/realtest.py ... the whole output down to "
           "TOTAL. Otherwise: `not required (<git diff --stat file list>)`. -->\n")
DATE = "2026-11-11"                   # fixture log lines are timed before any real commit


def _rd_item(repo, item, body05=FILLED, body06=FILLED, files=ALL, scope="FULL"):
    """Every step file in `files` via _item, then the 05/06 bodies replaced (06 keeps its RI line)."""
    _item(repo, item, files, scope=scope, date=DATE)
    d = repo / "work" / item
    if "05-build-report.md" in files:
        (d / "05-build-report.md").write_text(f"# 05\n{body05}", encoding="utf-8")
    if "06-verification.md" in files:
        (d / "06-verification.md").write_text(f"# 06\nRecurring issues checked: RI-007\n{body06}",
                                              encoding="utf-8")


def _check(repo, cutoff):
    code, out = _run(repo, "check_pipeline.py", "--today", DATE, "--untracked-from", cutoff)
    line = lambda p: [l for l in out.splitlines() if l.startswith(p)][0]
    return code, out, line("REAL-DATA FIELD:"), line("INCOMPLETE:")


def _trigger_commit(tmp_path, item="160", path="ccbot/realtest.py", **kw):
    repo, cutoff = _history(tmp_path)
    _rd_item(repo, item, **kw)
    _write(repo, path)
    sha = _commit(repo, f"{item} + {path}")
    return repo, cutoff, sha


@NO_GIT
def test_t1_filled_field_passes(tmp_path):
    repo, cutoff, _ = _trigger_commit(tmp_path)
    code, out, real, inc = _check(repo, cutoff)
    assert real == "REAL-DATA FIELD: none", out
    assert "160 (" not in inc and inc == "INCOMPLETE: none", out
    assert code == 0, out


@NO_GIT
def test_t2_comment_only_field_is_incomplete(tmp_path):
    repo, cutoff, sha = _trigger_commit(tmp_path, body05=COMMENT, body06=COMMENT)
    code, out, real, inc = _check(repo, cutoff)
    assert inc.startswith("INCOMPLETE: 160 (05 Real-data effect has no diff_reports TOTAL line ("), out
    assert (f"06 Real-data effect has no diff_reports TOTAL line ({sha[:7]} changes ccbot/realtest.py; "
            "item 070)") in inc, out
    assert real == "REAL-DATA FIELD: 160", out
    assert code == 1


@NO_GIT
def test_t3_non_trigger_code_needs_no_field(tmp_path):
    repo, cutoff, _ = _trigger_commit(tmp_path, path="ccbot/x.py", body05="x\n", body06="x\n")
    code, out, real, inc = _check(repo, cutoff)
    assert real == "REAL-DATA FIELD: none" and inc == "INCOMPLETE: none", out
    assert code == 0, out


@NO_GIT
def test_t4_not_required_on_trigger_is_incomplete(tmp_path):
    body = f"{HEAD}\nnot required (ccbot/realtest.py)\n"
    repo, cutoff, _ = _trigger_commit(tmp_path, body05=body, body06=body)
    code, out, real, inc = _check(repo, cutoff)
    assert "160 (05 Real-data effect has no diff_reports TOTAL line" in inc, out
    assert real == "REAL-DATA FIELD: 160" and code == 1


@NO_GIT
def test_t5_total_outside_the_section_does_not_count(tmp_path):
    body = f"## Test output\n```\n{TOTAL}\n```\n{HEAD}\nsee above\n## Deviations from plan\n"
    repo, cutoff, _ = _trigger_commit(tmp_path, body05=body)
    code, out, real, inc = _check(repo, cutoff)
    assert "160 (05 Real-data effect has no diff_reports TOTAL line" in inc, out
    assert "06 Real-data effect" not in inc, out
    assert real == "REAL-DATA FIELD: 160" and code == 1


@NO_GIT
def test_t6_pr_merge_flags_only_the_item_whose_commit_triggers(tmp_path):
    """Two items in one PR merge: a first-parent unit would flag both; non-merge commits only 160."""
    repo, cutoff = _history(tmp_path)
    _git(repo, "checkout", "-q", "-b", "pr")
    _rd_item(repo, "160", body05="x\n", body06="x\n")
    _write(repo, "ccbot/realtest.py")
    a = _commit(repo, "A: 160 + realtest")
    _rd_item(repo, "161", body05="x\n", body06="x\n")
    _write(repo, "scripts/y.py")
    _commit(repo, "B: 161 + scripts/y.py")
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "--no-edit", "pr")
    code, out, real, inc = _check(repo, cutoff)
    assert real == "REAL-DATA FIELD: 160", out
    assert f"160 (05 has no '{HEAD}' section ({a[:7]} changes ccbot/realtest.py; item 070)" in inc, out
    assert "161 (" not in inc, out
    assert code == 1


@NO_GIT
def test_t7_items_before_cutoff_are_not_checked(tmp_path):
    repo, cutoff, _ = _trigger_commit(tmp_path, item="069", body05="x\n", body06="x\n")
    code, out, real, inc = _check(repo, cutoff)
    assert "069 (" not in inc, out
    assert real == "REAL-DATA FIELD: none", out



@NO_GIT
def test_t7b_cutoff_edge_item_070_is_checked(tmp_path):
    """Round 3 (A1 FAIL): the edge ID itself. Kills `<` -> `<=` and any WHOLE_DIFF_FROM > 70;
    T7 (069 not checked) kills any WHOLE_DIFF_FROM < 70."""
    repo, cutoff, sha = _trigger_commit(tmp_path, item="070", body05="x\n", body06="x\n")
    code, out, real, inc = _check(repo, cutoff)
    assert real == "REAL-DATA FIELD: 070", out
    assert inc.startswith(f"INCOMPLETE: 070 (05 has no '{HEAD}' section ({sha[:7]} changes "
                          "ccbot/realtest.py; item 070)"), out
    assert code == 1, out


@NO_GIT
def test_t7c_cutoff_edge_pair_in_one_repo(tmp_path):
    """069 and 070 each with their own trigger commit: only 070 is named."""
    repo, cutoff = _history(tmp_path)
    for item in ("069", "070"):
        _rd_item(repo, item, body05="x\n", body06="x\n")
        _write(repo, "ccbot/realtest.py", f"# {item}\n")
        _commit(repo, f"{item} + realtest")
    code, out, real, inc = _check(repo, cutoff)
    assert real == "REAL-DATA FIELD: 070", out
    assert "070 (" in inc and "069 (" not in inc, out
    assert code == 1, out


@pytest.mark.parametrize("tpl", ["templates/build-report.md", "templates/verification.md"])
def test_t7d_cutoff_constant_matches_template_comment(tpl):
    sys.path.insert(0, str(REPO / "scripts"))
    import check_pipeline
    assert check_pipeline.WHOLE_DIFF_FROM == 70
    assert f"from item {check_pipeline.WHOLE_DIFF_FROM:03d} check_pipeline.py requires" in \
        (REPO / tpl).read_text(encoding="utf-8")

def test_t8_no_git_is_not_checked(tmp_path):
    _rd_item(tmp_path, "160", body05="x\n", body06="x\n")
    code, out = _run(tmp_path, "check_pipeline.py", "--today", DATE)
    assert "REAL-DATA FIELD: not checked (no git)" in out, out
    assert "INCOMPLETE: none" in out
    assert code == 0, out


def _config_literals(tree):
    """`config/<n>` for every `... "config" / "<n>"` path in the module (C3)."""
    found = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
                and isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)):
            continue
        left = node.left
        if (isinstance(left, ast.Constant) and left.value == "config") or (
                isinstance(left, ast.BinOp) and isinstance(left.op, ast.Div)
                and isinstance(left.right, ast.Constant) and left.right.value == "config"):
            found.add(f"config/{node.right.value}")
    return found


def _imports(tree):
    """ccbot module names imported by a ccbot module (relative level 1 or absolute ccbot.*)."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level == 1:
                names |= {a.name for a in node.names} if node.module is None else {node.module.split(".")[0]}
            elif node.level == 0 and node.module and node.module.split(".")[0] == "ccbot":
                parts = node.module.split(".")
                names |= {parts[1]} if len(parts) > 1 else {a.name for a in node.names}
        elif isinstance(node, ast.Import):
            names |= {a.name.split(".")[1] for a in node.names if a.name.startswith("ccbot.")}
    return names


def test_t9_trigger_matches_realtest_imports_and_config_reads():
    cp = _cp()
    parse = lambda m: ast.parse((REPO / "ccbot" / f"{m}.py").read_text(encoding="utf-8"))
    todo = {"realtest"} | _imports(parse("__init__"))
    seen, files = set(), set()
    while todo:
        m = todo.pop()
        if m in seen:
            continue
        seen.add(m)
        tree = parse(m)
        files |= _config_literals(tree)
        todo |= _imports(tree) - seen
    derived = {f"ccbot/{m}.py" for m in seen} | files
    assert derived == set(cp.TRIGGER)
    assert "data/real" in {n.value for n in ast.walk(parse("realtest")) if isinstance(n, ast.Constant)}
    assert "data/real/" in cp.TRIGGER_DIRS
    assert all((REPO / p).is_file() for p in cp.TRIGGER)


@pytest.mark.parametrize("after", [{"a": 2}, {"a": 1}], ids=["change", "no-change"])
def test_t10_total_matcher_fits_diff_reports_output(tmp_path, after):
    sys.path.insert(0, str(REPO / "scripts"))
    import diff_reports
    b, a = tmp_path / "before", tmp_path / "after"
    for d, data in ((b, {"a": 1}), (a, after)):
        d.mkdir()
        (d / "summary.json").write_text(json.dumps(data), encoding="utf-8")
    lines, _ = diff_reports.diff_dirs(b, a)
    total = [l for l in lines if l.startswith("TOTAL:")]
    assert len(total) == 1
    assert _cp().TOTAL_LINE.fullmatch(total[0])


@NO_GIT
def test_t11_data_real_file_triggers(tmp_path):
    repo, cutoff, sha = _trigger_commit(tmp_path, path="data/real/prices/X.csv", body05="x\n", body06=FILLED)
    code, out, real, inc = _check(repo, cutoff)
    assert f"160 (05 has no '{HEAD}' section ({sha[:7]} changes data/real/prices/X.csv; item 070)" in inc, out
    assert real == "REAL-DATA FIELD: 160" and code == 1


@NO_GIT
@pytest.mark.parametrize("body05, want", [
    (f"{HEAD}\n```\n## x\n{TOTAL}\n```\n## Deviations from plan\n", None),
    ("## Test output\nok\n", f"05 has no '{HEAD}' section ("),
    (f"{HEAD}\n```\n{TOTAL}\n", "05 Real-data effect has an unclosed ``` fence ("),
], ids=["fenced-heading", "no-heading", "unclosed"])
def test_t12_fences_and_headings(tmp_path, body05, want):
    repo, cutoff, _ = _trigger_commit(tmp_path, body05=body05)
    code, out, real, inc = _check(repo, cutoff)
    if want is None:
        assert inc == "INCOMPLETE: none" and real == "REAL-DATA FIELD: none" and code == 0, out
    else:
        assert inc.startswith(f"INCOMPLETE: 160 ({want}"), out
        assert real == "REAL-DATA FIELD: 160" and code == 1


@NO_GIT
def test_t13_missing_06_is_not_checked_yet(tmp_path):
    repo, cutoff, _ = _trigger_commit(tmp_path, files=ALL[:5])
    code, out, real, inc = _check(repo, cutoff)
    assert "160: in progress (FULL: next 06)" in out
    assert inc == "INCOMPLETE: none" and real == "REAL-DATA FIELD: none", out
    assert code == 0, out


@NO_GIT
def test_t14_unusable_cutoff_is_not_checked(tmp_path):
    repo, _, _ = _trigger_commit(tmp_path, body05="x\n", body06="x\n")
    code, out, real, inc = _check(repo, "0" * 40)
    assert real == "REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)", out
    assert "160 (" not in inc, out


@NO_GIT
def test_t15_git_log_failure_fails(tmp_path, monkeypatch):
    repo, cutoff, _ = _trigger_commit(tmp_path)
    monkeypatch.chdir(repo)
    cp = _cp()
    real_git = cp._git
    monkeypatch.setattr(cp, "_git", lambda *a: ("", 128) if a[0] == "log" else real_git(*a))
    assert cp.real_data_field(cutoff, cp._walk(cutoff)) == ("git log failed (item 070)", {}, True)


@NO_GIT
def test_t16_triggered_id_without_request_is_named(tmp_path):
    repo, cutoff = _history(tmp_path)
    _write(repo, "work/162/01-research.md")
    _write(repo, "ccbot/realtest.py")
    _commit(repo, "162 R1 + realtest, no request.md")
    code, out, real, _ = _check(repo, cutoff)
    assert real == "REAL-DATA FIELD: 162 (no work/162/request.md here)", out
    assert code == 1


@NO_GIT
def test_t17_trigger_with_no_05_is_incomplete(tmp_path):
    repo, cutoff, sha = _trigger_commit(tmp_path, files=ALL[:4])
    code, out, real, inc = _check(repo, cutoff)
    assert inc == f"INCOMPLETE: 160 (no 05 for {sha[:7]} changes ccbot/realtest.py (item 070))", out
    assert real == "REAL-DATA FIELD: 160" and code == 1


@NO_GIT
def test_t18_research_only_item_is_062s(tmp_path):
    repo, cutoff, _ = _trigger_commit(tmp_path, item="163", scope="RESEARCH ONLY",
                                      files=["01-research.md"])
    code, out, real, inc = _check(repo, cutoff)
    assert real == "REAL-DATA FIELD: none", out
    assert "RESEARCH CODE: 163" in out, out


@NO_GIT
def test_t19_main_exits_1_when_git_log_fails(tmp_path, monkeypatch, capsys):
    """06 round 1, problem 1: T1's clean fixture, run through main in-process with 070's git log
    failing; REAL-DATA FIELD is the only failing line, so main's `real[2]` exit term is tested."""
    repo, cutoff, _ = _trigger_commit(tmp_path)
    monkeypatch.chdir(repo)
    cp = _cp()
    real_git = cp._git
    monkeypatch.setattr(cp, "_git", lambda *a: ("", 128) if a[:2] == ("log", "--no-merges") else real_git(*a))
    code = cp.main(["--today", DATE, "--untracked-from", cutoff])
    out = capsys.readouterr().out
    assert "REAL-DATA FIELD: git log failed (item 070)" in out, out
    for ok in ("INCOMPLETE: none", "SKIPPED: none", "UNTRACKED CHANGE: none", "RESEARCH CODE: none",
               "A1 FAIL: none", "LOG TIME: none", "ORPHAN LOG: none"):
        assert ok in out, out
    assert code == 1, out


@NO_GIT
def test_t20_main_exits_1_for_triggered_id_without_request(tmp_path):
    """06 round 1, problem 1: unlike T16, 062 and 053 stay quiet (FULL item 160 is open before the
    commit and its 05 is in it, 062 gap (g)), so REAL-DATA FIELD alone gives exit 1."""
    repo, cutoff = _history(tmp_path)
    _rd_item(repo, "160")
    audit = repo / "work" / "160" / "07-audit-task.md"
    a1 = audit.read_text(encoding="utf-8")
    audit.unlink()
    _commit(repo, "160 01-06 (open: no 07)")
    audit.write_text(a1, encoding="utf-8")
    report = repo / "work" / "160" / "05-build-report.md"
    report.write_text(report.read_text(encoding="utf-8") + "round 2\n", encoding="utf-8")
    _write(repo, "work/162/05-build-report.md")
    _write(repo, "ccbot/realtest.py")
    _commit(repo, "160 05 + 07, 162 05 + realtest; 162 has no request.md")
    code, out, real, inc = _check(repo, cutoff)
    assert real == "REAL-DATA FIELD: 162 (no work/162/request.md here)", out
    for ok in ("INCOMPLETE: none", "SKIPPED: none", "UNTRACKED CHANGE: none", "RESEARCH CODE: none",
               "A1 FAIL: none", "ORPHAN LOG: none"):
        assert ok in out, out
    assert code == 1, out


@NO_GIT
@pytest.mark.parametrize("prose", [
    f"see 05: {TOTAL} (copied)",
    f"TOTAL line below ({TOTAL})",
    "TOTAL line below",
    "the TOTAL: line is in the PR",
], ids=["quoted-total", "total-in-brackets", "word-total", "total-colon"])
def test_t21_total_inside_prose_is_incomplete(tmp_path, prose):
    """06 round 1, problem 2 (RI-012): TOTAL text inside other text, outside any comment, is not
    diff_reports' line; only a full-line match counts. Kills `"TOTAL" in line`, `"TOTAL:" in line`
    and `TOTAL_LINE.search(line)`."""
    body = f"{HEAD}\n{prose}\n"
    repo, cutoff, sha = _trigger_commit(tmp_path, body05=body, body06=FILLED)
    code, out, real, inc = _check(repo, cutoff)
    assert inc == ("INCOMPLETE: 160 (05 Real-data effect has no diff_reports TOTAL line "
                   f"({sha[:7]} changes ccbot/realtest.py; item 070))"), out
    assert real == "REAL-DATA FIELD: 160" and code == 1, out


@NO_GIT
def test_t22_total_line_inside_a_comment_does_not_count(tmp_path):
    """Round 2: the one-change "comments kept" mutation survived T2 (its comment holds no full TOTAL
    line). A whole TOTAL line inside an HTML comment, e.g. an example left in the template, is not
    a paste."""
    body = f"{HEAD}\n<!-- example:\n{TOTAL}\n-->\nnot pasted yet\n"
    repo, cutoff, sha = _trigger_commit(tmp_path, body05=body, body06=FILLED)
    code, out, real, inc = _check(repo, cutoff)
    assert inc == ("INCOMPLETE: 160 (05 Real-data effect has no diff_reports TOTAL line "
                   f"({sha[:7]} changes ccbot/realtest.py; item 070))"), out
    assert real == "REAL-DATA FIELD: 160" and code == 1, out
