"""Run each recurring-issue mutation probe in PROBES on a scratch worktree of --ref (item 074).

A probe replaces one exact anchor in one committed file, runs one test file, and HOLDS only if
its named target test fails. Every other result (NOT HELD, ANCHOR MISSING, ERROR) exits 1.
Setup errors (no git, bad ref, scratch inside the repo, worktree add failed) exit 2.

The repo's working files are never opened for writing: all edits happen in a detached
worktree inside a TemporaryDirectory outside the repo, removed in `finally` (RI-009).
Results come from pytest's exit code and junit XML only, never from its text output (RI-012).

    python3 scripts/probe_guardrails.py [--ref HEAD] [--repo <root>] [--timeout 600]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

# Strings copied byte for byte from 074/03 step 1 and 078/03 step 5. `recorded` is printed only.
# An entry with no `module` names in `no_module_reason` how its test reaches the file (078).
_CP_REASON = ("tests/test_pipeline_check.py runs scripts/check_pipeline.py as"
              " REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after"
              " sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py")

PROBES = [
    {"id": "RI-002-063-leading-edge", "ri": "RI-002", "file": "ccbot/realtest.py",
     "anchor": 'if i == 0:\n        return "before_first"',
     "replacement": 'if i == 0:\n        return "known"',
     "test_file": "tests/test_realtest.py",
     "target": "tests/test_realtest.py::test_leading_edge_100_days_blocks",
     "module": "ccbot.realtest", "recorded": "2026-11-18: 9 failed, 41 passed"},
    {"id": "RI-002-065-interior-gap", "ri": "RI-002", "file": "ccbot/realtest.py",
     "anchor": 'if _is_gap(td.earnings[i - 1], td.earnings[i]):\n        return "interior_gap"',
     "replacement": 'if False:\n        return "interior_gap"',
     "test_file": "tests/test_realtest.py",
     "target": "tests/test_realtest.py::test_interior_gap_180_blocks",
     "module": "ccbot.realtest", "recorded": "2026-11-18: 4 failed, 46 passed"},
    {"id": "RI-013-067-1b", "ri": "RI-013", "file": "scripts/diff_reports.py",
     "anchor": "                out.extend(diff_json(a[k], b[k], p))\n        return out",
     "replacement": "                out.extend(diff_json(a[k], b[k], p) if not path or type(a[k]) is not dict"
                    " else [])\n        return out",
     "test_file": "tests/test_diff_reports.py",
     "target": "tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict",
     "no_module_reason": "tests/test_diff_reports.py runs scripts/diff_reports.py as"
                         " REPO/scripts/diff_reports.py (SCRIPT), REPO from tests/conftest.py",
     "recorded": "2026-11-18: 1 failed, 16 passed"},
    {"id": "RI-002-046-tickers-key", "ri": "RI-002", "file": "config/tickers.json",
     "anchor": '"F": {\n    "asset_type": "stock",',
     "replacement": '"F": {\n    "foo_date": null,\n    "asset_type": "stock",',
     "test_file": "tests/test_missing_inputs.py",
     "target": "tests/test_missing_inputs.py::test_ticker_fields_cover_file_and_code",
     "no_module_reason": "config/tickers.json is data: tests/test_missing_inputs.py"
                         " test_ticker_fields_cover_file_and_code reads tickers.json from"
                         " Path(__file__).resolve().parents[1]",
     "recorded": "2026-11-20 (078/05): 1 failed, 22 passed"},
    {"id": "RI-007-064-work-py", "ri": "RI-007", "file": "scripts/check_pipeline.py",
     "anchor": "    return f.startswith(paths) or WORK_CODE.fullmatch(f) is not None",
     "replacement": "    return f.startswith(paths)",
     "test_file": "tests/test_pipeline_check.py",
     "target": "tests/test_pipeline_check.py::test_research_only_work_py_is_research_code",
     "no_module_reason": _CP_REASON, "recorded": "2026-11-20 (078/05): 8 failed, 82 passed"},
    {"id": "RI-009-037-clash-line", "ri": "RI-009", "file": "scripts/check_pipeline.py",
     "anchor": "                clashes.append(item)",
     "replacement": "                pass",
     "test_file": "tests/test_pipeline_check.py",
     "target": "tests/test_pipeline_check.py::test_same_id_on_main_and_open_branch_is_a_clash",
     "no_module_reason": _CP_REASON, "recorded": "2026-11-20 (078/05): 1 failed, 89 passed"},
    {"id": "RI-010-049-rules-line", "ri": "RI-010", "file": "scripts/check_pipeline.py",
     "anchor": "        rules = changed(*RULE_PATHS)",
     "replacement": "        rules = []",
     "test_file": "tests/test_pipeline_check.py",
     "target": "tests/test_pipeline_check.py::test_rules_branch_is_reported",
     "no_module_reason": _CP_REASON, "recorded": "2026-11-20 (078/05): 1 failed, 89 passed"},
    {"id": "RI-011-052-merge-tree", "ri": "RI-011", "file": "scripts/check_pipeline.py",
     "anchor": "        tree = merge[0].split()[0] if conflicts is not None and merge[0].strip() else None",
     "replacement": "        tree = None",
     "test_file": "tests/test_pipeline_check.py",
     "target": "tests/test_pipeline_check.py::test_criss_cross_branch_lists_only_its_own_changes",
     "no_module_reason": _CP_REASON, "recorded": "2026-11-20 (078/05): 1 failed, 89 passed"},
    {"id": "RI-012-059-bare-429", "ri": "RI-012", "file": "ccbot/broker/webull_sandbox.py",
     "anchor": '    return bool(_HTTP_429.search(low)) or "too many requests" in low'
               ' or "too_many_requests" in low',
     "replacement": '    return "429" in low or "too many requests" in low or "too_many_requests" in low',
     "test_file": "tests/test_webull_sandbox.py",
     "target": "tests/test_webull_sandbox.py::test_429_inside_other_text_is_not_retried",
     "module": "ccbot.broker.webull_sandbox", "recorded": "2026-11-20 (078/05): 1 failed, 17 passed"},
]

REQUIRED = ("id", "ri", "file", "anchor", "replacement", "test_file", "target")


class JunitError(Exception):
    """The junit file is missing or cannot be parsed."""


def junit_key(nodeid):
    """(classname, name) as pytest's junitxml writes them (mangle_test_address)."""
    path, bracket, params = nodeid.partition("[")
    names = path.split("::")
    names[0] = re.sub(r"\.py$", "", names[0].replace("/", "."))
    names[-1] += bracket + params
    return ".".join(names[:-1]), names[-1]


_RANK = {"passed": 0, "skipped": 1, "failed": 2, "error": 3}


def read_junit(path):
    """{(classname, name): "passed"|"failed"|"error"|"skipped"} from the <testcase> elements."""
    try:
        root = ET.fromstring(Path(path).read_bytes())
    except (OSError, ET.ParseError) as e:
        raise JunitError(str(e)) from e
    out = {}
    for tc in root.iter("testcase"):
        tags = {child.tag for child in tc}
        status = ("error" if "error" in tags else "failed" if "failure" in tags
                  else "skipped" if "skipped" in tags else "passed")
        key = (tc.get("classname", ""), tc.get("name", ""))
        if key not in out or _RANK[status] > _RANK[out[key]]:
            out[key] = status
    return out


def classify(returncode, junit_path, target, timed_out):
    """(verdict, results) from the exit code and junit only. `timed_out` is the timeout in
    seconds when the run timed out, else None. results is None when no junit was read."""
    if timed_out:
        return f"ERROR (timeout {timed_out} s)", None
    if returncode not in (0, 1):
        return f"ERROR (pytest exit {returncode})", None
    try:
        results = read_junit(junit_path)
    except JunitError:
        return "ERROR (no junit result)", None
    errors = sum(1 for s in results.values() if s == "error")
    if errors > 0:
        return f"ERROR ({errors} errors)", results
    key = junit_key(target)
    if key not in results:
        return "ERROR (target not run)", results
    if results[key] == "failed":
        return "HOLDS", results
    return "NOT HELD", results


def _child_env():
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_pytest(wt, test_file, junit, timeout):
    """(returncode or None, timed out: bool, seconds) for one pytest run of test_file in wt."""
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rfE",
           f"--rootdir={wt}", f"--junit-xml={junit}", test_file]
    t0 = time.monotonic()
    try:
        r = subprocess.run(cmd, cwd=wt, env=_child_env(), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, True, time.monotonic() - t0
    return r.returncode, False, time.monotonic() - t0


def module_file(wt, module, timeout):
    """(True, resolved __file__) when `module` imports in wt, else (False, error text)."""
    code = "import importlib, sys\nprint(importlib.import_module(sys.argv[1]).__file__)\n"
    try:
        r = subprocess.run([sys.executable, "-c", code, module], cwd=wt, env=_child_env(),
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"import timeout {timeout} s"
    lines = r.stdout.strip().splitlines()
    if r.returncode != 0 or not lines:
        err = r.stderr.strip().splitlines()
        return False, err[-1] if err else f"import exit {r.returncode}"
    return True, str(Path(lines[-1]).resolve())


def worktree_clean(wt):
    """True only if git reports no change to a tracked file in wt."""
    r = subprocess.run(["git", "-C", str(wt), "status", "--porcelain", "--untracked-files=no"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode == 0 and r.stdout.strip() == ""


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def _counts(results):
    if results is None:
        return "counts n/a"
    n = {s: sum(1 for v in results.values() if v == s) for s in _RANK}
    return f"{n['failed']} failed, {n['passed']} passed, {n['error']} errors, {n['skipped']} skipped"


def _bad_lines(results):
    return [f"    {'FAILED' if s == 'failed' else 'ERROR'} {c}::{n}"
            for (c, n), s in sorted((results or {}).items()) if s in ("failed", "error")]


def _baseline(wt, scratch, n, test_file, timeout):
    """(results or None, problem text or None) for the unmutated test file; prints its line."""
    junit = scratch / f"base-{n}.xml"
    rc, timed_out, secs = run_pytest(wt, test_file, junit, timeout)
    results, problem = None, None
    if timed_out:
        problem = f"timeout {timeout} s"
    elif rc not in (0, 1):
        problem = f"pytest exit {rc}"
    else:
        try:
            results = read_junit(junit)
        except JunitError:
            problem = "no junit result"
    if results is not None:
        bad = sum(1 for s in results.values() if s in ("failed", "error"))
        if rc != 0 or bad:
            problem = f"exit {rc}, {_counts(results)}"
    shown = _counts(results) if results is not None else f"n/a ({problem})"
    print(f"baseline {test_file}: {shown}; {secs:.1f} s", flush=True)
    for line in _bad_lines(results):
        print(line, flush=True)
    return results, problem


def _run_probe(p, wt, scratch, sha, n, timeout, baselines, modules):
    """(verdict, results, extra) for one probe. extra holds the code-check text."""
    if p.get("module"):
        code = f"code check: {p['module']} not checked"
    else:
        code = f"code check: n/a ({p['no_module_reason']})"
    path = wt / p["file"]
    if not path.is_file():
        return f"ANCHOR MISSING (file not in {sha})", None, code, False
    original = path.read_bytes()
    text = original.decode("utf-8")
    count = text.count(p["anchor"])
    if count != 1:
        return f"ANCHOR MISSING (count {count})", None, code, False
    mutated = text.replace(p["anchor"], p["replacement"], 1)
    if mutated == text:
        return "ERROR (mutation does not change the file)", None, code, False
    if p["file"].endswith(".py"):
        try:
            compile(mutated, str(path), "exec")
        except SyntaxError as e:
            return f"ERROR (mutation does not compile: {e.msg}, line {e.lineno})", None, code, False
    if p["file"].endswith(".json"):
        try:
            json.loads(mutated)
        except ValueError as e:
            msg, line = getattr(e, "msg", str(e)), getattr(e, "lineno", "?")
            return f"ERROR (mutation is not valid JSON: {msg}, line {line})", None, code, False
    if p.get("module"):
        mkey = (p["module"], p["file"])
        if mkey not in modules:
            modules[mkey] = module_file(wt, p["module"], timeout)
        ok, where = modules[mkey]
        if not ok or Path(where) != path.resolve():
            return f"ERROR (code under test is {where})", None, code, False
        code = f"code check: {p['module']} is {p['file']} in the worktree"
    tf = p["test_file"]
    if tf not in baselines:
        baselines[tf] = _baseline(wt, scratch, len(baselines), tf, timeout)
    base, problem = baselines[tf]
    if problem is None:
        status = base.get(junit_key(p["target"]))
        if status is None:
            problem = "target not found"
        elif status != "passed":
            problem = f"target {status}"
    if problem is not None:
        return f"ERROR (baseline: {problem})", None, code, False
    junit = scratch / f"probe-{n}.xml"
    try:
        path.write_bytes(mutated.encode("utf-8"))
        rc, timed_out, _ = run_pytest(wt, tf, junit, timeout)
    finally:
        path.write_bytes(original)
    verdict, results = classify(rc, junit, p["target"], timeout if timed_out else None)
    return verdict, results, code, True


def main(argv=None, probes=PROBES):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    t_start = time.monotonic()

    if shutil.which("git") is None:
        print("SETUP: git not found", flush=True)
        return 2
    _git(repo, "worktree", "prune")
    rev = _git(repo, "rev-parse", "--verify", "-q", args.ref + "^{commit}")
    if rev.returncode != 0 or not rev.stdout.strip():
        print(f"SETUP: ref {args.ref} not found", flush=True)
        return 2
    sha = rev.stdout.strip()

    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp).resolve()
        if scratch == repo or repo in scratch.parents:
            print(f"SCRATCH INSIDE REPO: {scratch}", flush=True)
            return 2
        wt = scratch / "wt"
        add = _git(repo, "worktree", "add", "--detach", "-q", str(wt), sha)
        if add.returncode != 0:
            print(f"SETUP: worktree add failed: {add.stderr.strip()}", flush=True)
            _git(repo, "worktree", "prune")
            return 2
        try:
            return _probe_all(probes, args, wt, scratch, sha, t_start)
        finally:
            _git(repo, "worktree", "remove", "--force", str(wt))
            _git(repo, "worktree", "prune")


def _probe_all(probes, args, wt, scratch, sha, t_start):
    print(f"ref {args.ref} = {sha}", flush=True)
    if "PYTEST_ADDOPTS" in os.environ:
        print(f"PYTEST_ADDOPTS ignored: {os.environ['PYTEST_ADDOPTS']!r}", flush=True)
    tally = {"hold": 0, "not held": 0, "anchor missing": 0, "error": 0}
    baselines, modules = {}, {}
    reported, stopped = 0, False
    for n, p in enumerate(probes):
        missing = [k for k in REQUIRED if not p.get(k)]
        t0 = time.monotonic()
        if missing:
            verdict, results, code, wrote = f"ERROR (probe entry lacks {', '.join(missing)})", None, "", False
        elif not p.get("module") and not p.get("no_module_reason"):
            verdict, results, code, wrote = ("ERROR (probe entry lacks module or no_module_reason)",
                                             None, "", False)
        else:
            verdict, results, code, wrote = _run_probe(p, wt, scratch, sha, n, args.timeout,
                                                       baselines, modules)
        if wrote and not worktree_clean(wt):
            verdict, stopped = "ERROR (worktree not restored)", True
        secs = time.monotonic() - t0
        key = ("hold" if verdict == "HOLDS" else "not held" if verdict == "NOT HELD"
               else "anchor missing" if verdict.startswith("ANCHOR MISSING") else "error")
        tally[key] += 1
        reported += 1
        if results is None and not wrote:
            counts = "pytest not run"
        else:
            counts = _counts(results)
        target = p.get("target", "?")
        if results is not None:
            hit = "yes" if results.get(junit_key(target)) == "failed" else "no"
        else:
            hit = "n/a"
        rec = f"recorded {p['recorded']}" if p.get("recorded") else "recorded: none"
        parts = [counts, f"target {target} failed: {hit}", verdict, rec]
        if code:
            parts.append(code)
        parts.append(f"{secs:.1f} s")
        print(f"{p.get('id', '?')} ({p.get('ri', '?')}): " + "; ".join(parts), flush=True)
        for line in _bad_lines(results):
            print(line, flush=True)
        if stopped:
            break
    if stopped:
        print(f"STOPPED: {len(probes) - reported} probes not run (worktree not restored)", flush=True)
    total = time.monotonic() - t_start
    print(f"TOTAL: {reported} probes, {tally['hold']} hold, {tally['not held']} not held, "
          f"{tally['anchor missing']} anchor missing, {tally['error']} error; {total:.1f} s", flush=True)
    return 0 if probes and not stopped and tally["hold"] == len(probes) else 1


if __name__ == "__main__":
    sys.exit(main())
