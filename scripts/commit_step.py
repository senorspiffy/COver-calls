"""Commit one item's step files with only that item's own log lines (item 091, 086 F4, RI-010).

Usage, from the repo top:
  python3 scripts/commit_step.py <ID> "<subject>" <path>...

The shared daily log files (logs/research/YYYY-MM-DD.md, logs/implementation/YYYY-MM-DD.md) hold lines
of several items at once. `git add` of such a file would commit another item's uncommitted line too
(91ade51 carried 081's I3 line). This helper builds the commit in a temporary index, never touching
the shared one until the commit is made:
  (i)   refuses (exit 2, nothing written) when git is missing, the cwd is not the repo top, HEAD is
        unborn, the ID is not 3 digits, a named path is missing (deletions are not supported) or a
        directory, or a named path is a log file under logs/research/ or logs/implementation/ (the
        helper finds those itself);
  (ii)  for each log file in the working tree, keeps HEAD's lines and every added line except a LOG_LINE
        (check_pipeline) of another item, in working-tree order. HEAD's lines must be an in-order
        subsequence of the working lines, and both texts strict UTF-8; else refused, never a whole-file
        fallback. A file equal to HEAD after filtering is not staged; a file not in HEAD is staged only
        if it gains one of this item's lines;
  (iii) in a temp index (mkstemp in the absolute git dir, deleted in `finally`; `read-tree` of the
        parent is the first command on the empty file, git t1009): stages the named paths, then each
        filtered log blob (`hash-object -w --stdin --path`, `update-index --cacheinfo`), `write-tree`;
  (iv)  subject: with 0 own log lines added, any subject; with 1, it must equal `Item <ID>: ` + that line
        (run-item's item-082 rule); with 2 or more, refused (a batch, item 045);
  (v)   `commit-tree <tree> -p <old>`, then `update-ref HEAD <new> <old>`: if HEAD moved since it was
        read, refused (exit 2) and HEAD is unchanged;
  (vi)  `git reset -q -- <paths> <staged log files>` on the shared index, so other staged files stay
        staged and the log files show only the other items' lines as changed. If that fails: exit 1,
        the commit is made, and the message names the command to run.
Prints `<sha7> <subject>` and exits 0 on success. Known gaps: one code file holding two items' edits is
committed whole (build such items one after another, run-item.md); hooks are not run (.git/hooks held
only *.sample files on 2026-11-21); deletions are not committed; a HEAD log file with no final newline
that later gains lines reads as changed and is refused (strict).
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_pipeline import LOG_LINE  # noqa: E402  (as check_handoff does)

LOG_DIRS = ("logs/research", "logs/implementation")
LOG_NAME = re.compile(r"\d{4}-\d{2}-\d{2}\.md")


class Refused(Exception):
    """A reason to commit nothing (exit 2)."""


def run(args, env=None, input=None):
    """(stdout bytes, exit code) of `git <args>` in the cwd, or None when git is missing."""
    try:
        r = subprocess.run(["git", *args], capture_output=True, env=env, input=input)
    except FileNotFoundError:
        return None
    return r.stdout, r.returncode


def filter_log(work, head, item, name="log file"):
    """(bytes to commit, own LOG_LINE lines added) for one log file: HEAD's lines (head None = not in
    HEAD) are kept and must appear in order in `work`; of the other lines, a LOG_LINE of another item
    is dropped and every other line kept, in working-tree order. Raises Refused on non-UTF-8 text or
    when HEAD's lines are not an in-order subsequence of the working lines."""
    try:
        wl = work.decode("utf-8").splitlines(keepends=True)
        hl = head.decode("utf-8").splitlines(keepends=True) if head is not None else []
    except UnicodeDecodeError:
        raise Refused(f"{name} unreadable (item 091)") from None
    out, own, ptr = [], [], 0
    for line in wl:
        if ptr < len(hl) and line == hl[ptr]:
            out.append(line)
            ptr += 1
            continue
        m = LOG_LINE.match(line.rstrip("\r\n"))
        if m and m[4] != item:
            continue
        out.append(line)
        if m:
            own.append(line.rstrip("\r\n"))
    if ptr < len(hl):
        raise Refused(f"{name}: committed lines changed; nothing committed (item 091)")
    return "".join(out).encode("utf-8"), own


def _git(run, args, env=None, input=None):
    """stdout bytes of a git command that must succeed, else Refused with the command and code."""
    r = run(args, env=env, input=input)
    if r is None:
        raise Refused("no git (item 091)")
    if r[1] != 0:
        raise Refused(f"git {args[0]} failed (exit {r[1]}); nothing committed (item 091)")
    return r[0]


def _log_blobs(item, old, run):
    """[(path, mode, bytes)] to stage and the item's own added LOG_LINE lines, over every log file."""
    blobs, own = [], []
    for d in LOG_DIRS:
        for f in (sorted(Path(d).iterdir()) if Path(d).is_dir() else []):
            if not (f.is_file() and LOG_NAME.fullmatch(f.name)):
                continue
            p = f.as_posix()
            ls = _git(run, ["ls-tree", old, "--", p]).decode("utf-8", "replace").strip()
            mode, head = "100644", None
            if ls:                                          # exit 0 + empty = not in HEAD (a real answer)
                meta = ls.split("\t", 1)[0].split()
                mode = meta[0]
                head = _git(run, ["cat-file", "blob", meta[2]])
            try:
                work = f.read_bytes()
            except OSError:
                raise Refused(f"{p} unreadable (item 091)") from None
            new, mine = filter_log(work, head, item, p)
            own += mine
            if (head is not None and new != head) or (head is None and mine):
                blobs.append((p, mode, new))
    return blobs, own


def commit(item, subject, paths, run=run, old=None):
    """Make the commit (see the module text). Returns the exit code; messages go to stdout/stderr."""
    try:
        top = run(["rev-parse", "--show-toplevel"])
        if top is None:
            raise Refused("no git (item 091)")
        if top[1] != 0 or Path(os.fsdecode(top[0].strip())).resolve() != Path.cwd().resolve():
            raise Refused("not the top of a git work tree; run from the repo top (item 091)")
        head = run(["rev-parse", "--verify", "-q", "HEAD"])
        if head is None:
            raise Refused("no git (item 091)")
        if head[1] == 1:
            raise Refused("no HEAD commit (item 091)")
        if head[1] != 0:
            raise Refused(f"git rev-parse failed (exit {head[1]}); nothing committed (item 091)")
        old = old or head[0].decode("utf-8").strip()
        if not re.fullmatch(r"\d{3}", item):
            raise Refused(f"ID {item!r} is not 3 digits (item 091)")
        if not paths:
            raise Refused("no path named (item 091)")
        named = []
        for p in paths:
            n = Path(os.path.normpath(p)).as_posix()
            if any(n == d or n.startswith(d + "/") for d in LOG_DIRS):
                raise Refused(f"{p}: log files are found by the helper; do not name them (item 091)")
            if not os.path.lexists(n):
                raise Refused(f"{p} not found; deletions are not supported (item 091)")
            if os.path.isdir(n):
                raise Refused(f"{p} is a directory; name files (item 091)")
            named.append(n)
        blobs, own = _log_blobs(item, old, run)
        if len(own) > 1:
            raise Refused(f"{len(own)} log lines of {item} in one commit: a batch (item 045); commit each step "
                          f"with its own line (item 091)")
        if own and subject != f"Item {item}: {own[0]}":
            raise Refused(f"subject must be 'Item {item}: {own[0]}' (item 082); nothing committed (item 091)")
        gitdir = _git(run, ["rev-parse", "--absolute-git-dir"]).decode("utf-8").strip()
        fd, idx = tempfile.mkstemp(prefix="commit_step-", suffix=".index", dir=gitdir)
        os.close(fd)
        try:
            env = {**os.environ, "GIT_INDEX_FILE": idx}
            _git(run, ["read-tree", old], env)              # first command on the empty file (t1009)
            _git(run, ["update-index", "--add", "--", *named], env)
            for p, mode, data in blobs:
                sha = _git(run, ["hash-object", "-w", "--stdin", "--path", p], env, data).decode("utf-8").strip()
                _git(run, ["update-index", "--add", "--cacheinfo", f"{mode},{sha},{p}"], env)
            tree = _git(run, ["write-tree"], env).decode("utf-8").strip()
        finally:
            try:
                os.unlink(idx)
            except FileNotFoundError:
                pass
        new = _git(run, ["commit-tree", tree, "-p", old, "-m", subject]).decode("utf-8").strip()
        moved = run(["update-ref", "-m", f"commit_step: {subject}", "HEAD", new, old])
        if moved is None or moved[1] != 0:
            cur = run(["rev-parse", "--verify", "-q", "HEAD"])
            cur = cur[0].decode("utf-8").strip() if cur and cur[1] == 0 else "?"
            if cur != old:
                raise Refused(f"HEAD moved ({old[:7]} -> {cur[:7]}); re-run (item 091)")
            raise Refused(f"git update-ref failed (exit {moved[1] if moved else 'no git'}); nothing committed "
                          f"(item 091)")
    except Refused as why:
        print(f"commit_step refused: {why}", file=sys.stderr)
        return 2
    staged = [*named, *(p for p, _, _ in blobs)]
    reset = run(["reset", "-q", "--", *staged])
    if reset is None or reset[1] != 0:
        print(f"commit {new[:7]} made; run git reset -q -- {' '.join(staged)} (item 091)", file=sys.stderr)
        return 1
    print(f"{new[:7]} {subject}")
    return 0


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    return commit(argv[0], argv[1], argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
