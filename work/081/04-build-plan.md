# 04 Build plan - 081
Fit verdict: FIT WITH CHANGES

I1 had no shell in this run, so I ran no git command, no pytest and no `check_pipeline.py`. The code facts below come from reading `scripts/check_pipeline.py`, `scripts/check_handoff.py`, `scripts/probe_guardrails.py` and `tests/test_pipeline_check.py` on daily-fixes/2026-11-20. 081 builds first today, so the line numbers in 03 still match this tree. I re-read L480-1151 and L1-203. Functions are named below as well, so 084 and 086 can follow the plan after line drift. The I1 log line has to be written by the orchestrator: `python3 scripts/check_pipeline.py --log I1 081 "FIT WITH CHANGES | 4 files planned"`.

Recurring issues checked (item 013), open or ESCALATED entries:
- **RI-001** (ESCALATED). No ticker, DTE or delta filter here. Each disambiguation rule has a computed fixture count: (d1) 0 of 1 log files listed, so it is skipped; (d2) max(040, 099)+1 = 100 (fixture IDs); (d3) 0 refs match, so no line; step 8 code == 128. Each count is pinned by a named test below. Nothing says "always".
- **RI-010** (ESCALATED). The I1 line goes through `--log` (orchestrator). Nothing is typed by hand. 081 adds no log rule.
- **RI-014** (OPEN, this item). The guardrail is the census test, fixtures (a)-(d3) and mutations m1-m9. The 05/06 status line is step 13.
- Also checked: RI-002 (GUARDED, family). No failed git read becomes `none`, `0`, `[]` or an ID; see Rule trace "Missing inputs". RI-009 (GUARDED). `--next-id` refuses and never guesses. RI-008. `os.fsdecode` and `errors=` exist on 3.10; I3 runs `py_compile` under python3.11. RI-011. The `merge-tree` diff path and its anchor line are unchanged.

## Fit check
- **~$3k account.** Tooling only. No trade, price, option, broker or ticker input changes, and nothing connects to a brokerage. No 001 rule (slack, tolerance, cap) changes. The one rule text that changes is in a1-auditor.md, which the auditor follows (step 12). It is planned here and needs the person's OK in PR review.
- **Existing code.** The plan fits the 077/069/070 precedents: a failed git read is an error with exit 1, and a known benign state (no git, a shallow clone) is `not checked` with exit 0. It conflicts with nothing built. `_git`'s contract stays `(stdout, code)` / None, so the 5 monkeypatch lambdas and `_patched_git` keep working. The 3 probe anchor lines stay byte-identical.
- **Ordering (081 → 084 → 086).** 084/04 L15 and L42 expect "every git call goes through 081's helper" and "081's call-site lint test". The interface section below fixes that contract, so 084 and 086 can add their calls without re-reading this build.
- **Changes to 03 (why "WITH CHANGES"):**
  1. **LOG TIME error shape.** `late_log_lines` returns a one-entry list `["git ls-tree HEAD failed (item 081)"]` instead of a bare string. `main` already prints `', '.join(late)` and exits 1 when `late` is truthy, so no new type branch is needed. A bare string would print joined character by character unless main special-cased it. The printed text is the same as 03's.
  2. **(d2) needs an orphan branch.** A branch cut from `main` inherits main's `work/`, so `_branch_adds` cannot make "a branch with no work/". The fixture uses `git checkout --orphan nowork` with one README commit, pushed (see Extra research 2).
  3. **A failed `show` of a branch step file skips classify for that item.** 03 step 4 records the error but would still classify a temp dir holding an empty file. That empty file could print a false BRANCH SKIPPED or BRANCH FAIL beside the BRANCH ERROR. With the change, only the error is printed for that item.
  4. **`changed()` errors are de-duplicated per ref.** `changed()` runs 5 times per ref (L664, L674, L675, L703 twice). The first diff (against the merge-tree result) falling back is not an error. Only the fallback `HEAD...ref` failing is one. Each distinct `why` is recorded once.
  5. **check_handoff `_branch_with_handoff` returns `(ref, why)`.** `check_all` prints `<ID>: not checked (open branches: <why>)` and counts it in `failed`.
  6. **a1-auditor.md L23 also names `BRANCH ERROR:`.** These lines go at the top of the report with the other branch lines. This is the same file as step 12, so no extra file.
  7. **(d3) uses `refs/remotes/origin/main/x` alone.** It cannot coexist with `origin/main` (Extra research 3).

## Interface for 084 and 086 (keep stable)
```python
def _git(*args) -> "tuple[str, int] | None"      # unchanged contract; stdout decoded utf-8 errors="replace"
def _git_ok(*args) -> "tuple[str | None, str | None]"
    # (stdout, None)                       git exited 0
    # (None, "no git")                     _git returned None (git missing / cwd not the work-tree top)
    # (stdout, f"git {args[0]} failed (exit {code})")   any non-zero exit; stdout as git gave it (usually "")
    # The reason never holds git's stderr (PEP 538, 03 row 7).
```
- New git calls use `_git_ok` and branch on `why is not None`. `why == "no git"` is the benign case. Any other `why` is an error, never `none`, 0 or `[]`.
- Use raw `_git` only where a non-zero code is a real answer (`merge-base --is-ancestor` 1, `merge-tree` 1, `cat-file -e`). Each such call needs a census reason.
- Census: `tests/test_pipeline_check.py::GIT_CENSUS = {(function, callee): (count, reason)}`, where callee is `"_git"` or `"_git_ok"`. A new call adds or bumps one entry with a non-empty reason. 084 adds `("_rule_seen", "_git_ok")` and, if it calls git, `("_anchor_env", ...)`. 086 does the same for its function.
- Test helper `_patched_git(monkeypatch, cp, table)` is unchanged. Because `_git_ok` looks `_git` up as a module global, patching `cp._git` also drives `_git_ok`.

## Extra research (with sources)
1. **The step 1 compare is exact.** `os.fsdecode`: "Decode the path-like filename from the filesystem encoding and error handler". The os docs say "undecodable bytes are replaced by a Unicode character U+DCxx on decoding" [https://docs.python.org/3/library/os.html]. `Path.cwd()` is built from `os.getcwd()`, which uses the same filesystem decoding. That last part is not in the fetched text, so it is UNVERIFIED by doc and pinned by fixture (c2). If (c2) shows a mismatch, I2 records it in 05 and sends it back to I1.
2. **"Branch with no work/" needs `--orphan`.** git-checkout `--orphan`: "Create a new unborn branch ... The first commit made on this new branch will have no parents" [https://git-scm.com/docs/git-checkout]. A normal branch from main carries main's `work/040`, so `ls-tree <ref> -- work/` would list it and (d2) would not test the empty case. `--no-merged HEAD` lists an unrelated orphan tip, because it is not reachable from HEAD.
3. **`origin/main` and `origin/main/x` cannot both exist.** git stores refs as a hierarchy, so a ref name that is a prefix directory of another conflicts. This is my knowledge of git's ref store, UNVERIFIED by a fetched doc here. So 03 Self-check row 7's "2 lines → filter → 1" case cannot be built. (d3) builds the one real case: only `refs/remotes/origin/main/x` (via `git update-ref`), which must give no MAIN AHEAD line. Mutation m4b (drop the exact-name filter) then counts `HEAD..<main/x sha>` and prints a line. The fixture's tip of main/x is one commit ahead of HEAD, so the count is 1 and visible.
4. **Unborn HEAD (an edge 03 does not name).** In a repo with no commit, `branch -r --no-merged HEAD` cannot resolve HEAD. After 081 that gives an OPEN BRANCHES error and a `--next-id` refusal. Today 077's `ls-tree HEAD` already exits 1 in that state (`uncommitted_steps`), so main's exit is unchanged. For `--next-id` it is the safe side (RI-009). Docstring gap text: "a repo with no commit: --next-id refuses; make the first commit". No fixture: no repo this project runs from is unborn.
5. **Edge in `_branch_with_handoff`.** Today, without git, `open_branches()` returns `[]` and the loop runs zero times. After 081 it returns None, and `for b in None` would raise TypeError on every `check_handoff.py --all` run without git (03 row 47). Change 5 covers it, and test (h2) pins it.

## Files to create/change
4 files (plus I2's own work/081/05).

1. `scripts/check_pipeline.py`
   - `import os`.
   - `_git` (L619-630):
     - The `--show-toplevel` run goes to bytes (`capture_output=True`, no text). It compares `Path(os.fsdecode(top.stdout.strip())).resolve() != Path.cwd().resolve()`.
     - The main run adds `errors="replace"` (keeping `text=True, encoding="utf-8"`).
     - The return contract and the docstring's contract are unchanged. One docstring sentence is added: decode `replace` (item 081).
   - New `_git_ok(*args)` directly after `_git`, as in the interface above.
   - `late_log_lines` (L592-616):
     - Keep the L595 `is None` probe.
     - Add `tree, why = _git_ok("ls-tree", "-r", "--name-only", "HEAD", "--", "logs/research/", "logs/implementation/")`. A `why` returns `[f"git ls-tree HEAD failed (item 081)"]`.
     - `committed = set(tree.splitlines())`. In the loop, `f.as_posix() not in committed` means `continue` (uncommitted; the only skip).
     - Blame goes through `_git_ok`. Its failure appends `f"{f.as_posix()} (git blame failed; item 081)"` and continues.
   - `open_branches` (L633-717):
     - `out, why = _git_ok("branch", ...)`. `why == "no git"` returns None. Another `why` returns `why` (str).
     - Add `errors = []` per ref.
     - `changed()` uses `_git_ok` for both diffs. When the fallback fails it appends the `why` once (`if why not in errors`) and returns `[]`.
     - `ls-tree` L667, `merge-base --all` L676 and `show` request L681 use `_git_ok`. L681 is shown only when `"request.md" in files[item]`, else `requests[item] = None` as today. Their failures append to `errors`.
     - `show` body L693 uses `_git_ok`. A failure appends to errors, and that item is not classified (change 3).
     - `log -1` L712, `merge-base --is-ancestor` L647, `merge-tree` L649 and `cat-file -e` L685 keep `_git` (census reasons).
     - `behind = isinstance(a := main_ahead(), int) and a > 0`. The walrus is fine on 3.10.
     - The dict gains `"errors": errors`.
     - The three anchor lines `                clashes.append(item)`, `        rules = changed(*RULE_PATHS)` and `        tree = merge[0].split()[0] if conflicts is not None and merge[0].strip() else None` stay byte-identical.
   - `main_ahead` (L971-977):
     - `_git_ok("for-each-ref", "--format=%(refname) %(objectname)", "refs/remotes/origin/main")`. Keep only the line whose first field == `refs/remotes/origin/main`. None found gives 0.
     - Else `_git_ok("rev-list", "--count", f"HEAD..{sha}")`.
     - Any non-"no git" `why`, or a count that is not a digit string, returns the string `f"{why} (item 081)"`. "no git" gives 0.
     - Docstring: int, or the error string.
   - `next_id` (L980-987) returns `(id, None)` or `(None, why)`:
     - `branch -r` goes through `_git_ok`. "no git" gives the HEAD-only count, as today.
     - Per ref: `_git_ok("ls-tree", "-d", "--name-only", ref, "--", "work/")`, `Path(line).name` of each line, digits only.
     - Any other `why` returns `(None, why)`.
   - `_inbox_gate` (L995): after the `is None` test, `if shallow[1] == 128: return (f"{path.name} (git rev-parse failed (exit 128); item 081)", True)`. Exit 129 and the others keep today's path.
   - `main`:
     - `--next-id`: on `why`, print `--next-id refused: {why}; not counting open branches would risk an ID clash (item 037). Fix the clone (git fetch origin) and re-run.` to stderr, nothing on stdout, return 2.
     - `blist = branches if isinstance(branches, list) else []` is used for the IN PR scan, clashes, BRANCH SKIPPED and BRANCH FAIL.
     - `ahead = main_ahead()`. A str prints `MAIN AHEAD: {ahead}`. An int > 0 prints today's line.
     - OPEN BRANCHES:
       - None prints no line (test L201).
       - A str prints `OPEN BRANCHES: {branches} (item 081)`.
       - `[]` prints `OPEN BRANCHES: none`.
       - A list prints today's block.
     - When `branches` is a str, IN PR, RULES BRANCH and ID CLASH each print `not checked (see OPEN BRANCHES)`.
     - After BRANCH FAIL, print `BRANCH ERROR: {ref} ({why})` for each error.
     - Exit 1 also when `isinstance(branches, str)`, any `b["errors"]`, or `isinstance(ahead, str)`.
   - Docstring:
     - BRANCH FAIL's last sentence (L69-70) becomes: "a branch file git cannot show is a BRANCH ERROR, and that item is not classified (item 081)".
     - New `BRANCH ERROR` entry (exit 1).
     - LOG TIME (L82-86): the ls-tree list, the uncommitted skip, and blame failure as an entry.
     - MAIN AHEAD (L93-95): the error line, and an exact refname match.
     - Gap (l) (L145-147) is replaced by: "a failed branch git diff is a BRANCH ERROR (item 081)".
     - `--next-id` (L181-182): the refusal (exit 2, empty stdout), and the unborn-HEAD note.
     - OPEN BRANCHES: none vs absent (no git).
     - A known-gap note: `_shallow_boundaries` returns "full" when the flag and `--git-common-dir` both fail. `_walk` then prints the squash/rebase text (wrong reason, but still exit 1; 03 Missing inputs last row).
   - Scope lock: no change to `_walk`, `_shallow_boundaries`, `untracked_changes`, `research_code`, `real_data_field`, `_item_triggers`, `_open_at`, `uncommitted_steps`, the strict `read_text` sites (F10, a separate item), constants, or LOG_FORMAT.
2. `scripts/check_handoff.py`, `_branch_with_handoff` (L90-98) and `check_all`:
   - `found = open_branches()`. None returns `(None, None)`. A str returns `(None, found)`. Otherwise the first ref with 03 is returned as `(ref, None)`.
   - `check_all` prints `<ID>: not checked (open branches: <why>)` and appends it to `failed`.
3. `tests/test_pipeline_check.py`: the new tests listed below. `test_branch_diff_failure_hides_code_gap_l` is renamed `test_branch_diff_failure_is_branch_error` and changed on purpose. The docstring says so, as its own text requires (L1741).
4. `.claude/agents/a1-auditor.md`:
   - L29: append "If `--next-id` refuses, fix the clone and re-run; never pick an ID by hand (item 081)."
   - L23: in the list of branch lines that go at the top of the report, add "every `BRANCH ERROR:` line (git could not read that branch; item 081)".
   - Additions only. A RULES change, so it needs the person's OK in PR review.

## Tests and checks
New and changed tests in `tests/test_pipeline_check.py` (`@NO_GIT` unless noted):
- `test_git_ok_contract` (no git needed): with `cp._git` patched:
  - `("x", 0)` gives `("x", None)`;
  - None gives `(None, "no git")`;
  - `("", 128)` for `("log", "-1")` gives `("", "git log failed (exit 128)")`.
- `test_git_call_census` (no git needed). It uses `ast.parse` on `REPO/scripts/check_pipeline.py`. Each `ast.Call` whose `func` is `Name` `_git` / `_git_ok` maps to its innermost enclosing `FunctionDef` (generator expressions are not functions). The `Counter` must equal `{k: v[0] for k, v in GIT_CENSUS.items()}`, and every reason must be non-empty. Expected after 081 (my count from the plan above; I2 recounts on the built file and pins what it prints):

  | function | `_git` | `_git_ok` | reason |
  |---|---|---|---|
  | uncommitted_steps | 2 | 0 | `is None` no-git probe; ls-tree failure is 077's error |
  | late_log_lines | 1 | 2 | no-git probe; ls-tree and blame failures are entries |
  | _git_ok | 1 | 0 | the helper |
  | open_branches | 4 | 5 | is-ancestor 128 lists the ref (more); merge-tree 0/1 are answers, else "merge not checked"; cat-file non-zero = absent at base (a die gives a clash, loud); log -1 is age only (cosmetic) |
  | changed | 0 | 2 | fallback failure → BRANCH ERROR |
  | _open_at | 1 | 0 | an absent 07 must read open; the same walk's diff-tree just succeeded (F8) |
  | _shallow_boundaries | 2 | 0 | 079: failure → "full" → `_walk` L775 loud (exit 1) |
  | _walk | 7 | 0 | 079: each failure is a not-checked or error tuple |
  | untracked_changes, research_code, real_data_field | 1 each | 0 | no-git probe |
  | _item_triggers | 1 | 0 | 070: "git log failed", exit 1 |
  | main_ahead | 0 | 2 | error string → MAIN AHEAD line, exit 1 |
  | next_id | 0 | 2 | refusal, exit 2 |
  | _inbox_gate | 4 | 0 | flag 128 loud (081); log failure loud (069); show failure → not checked |
  | main | 2 | 0 | no-git probes |

  Totals: `_git` 2+1+1+4+1+2+7+1+1+1+1+4+2 = 28; `_git_ok` 2+5+2+2+2 = 13; 28 + 13 = 41 = 03's 39 + 1 (the new ls-tree) + 1 (the `_git` inside `_git_ok`).
- (a) `test_all_git_fails_no_line_says_none`:
  - Setup: tmp_path with work/150 (request only), `logs/audit/2026-11-20.md`, and `templates/daily-audit.md` with `## Inbox`. `monkeypatch.chdir` there and `monkeypatch.setattr(cp, "_git", lambda *a: ("", 128))`. Run `cp.main(["--today", "2026-11-20"])` with capsys.
  - Each of these lines exists and does not end in `: none`: LOG TIME, OPEN BRANCHES, IN PR, RULES BRANCH, ID CLASH, MAIN AHEAD, UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD, UNCOMMITTED STEP, INBOX.
  - The return is 1.
  - Then `cp.main(["--next-id"])` returns 2, captured stdout is `""`, and stderr holds `--next-id refused: git branch failed (exit 128)`.
- (b) `test_malformed_shallow_real_git_nothing_none`:
  - Setup: `_repo_with_open_branch`, then `_branch_adds(repo, "scratch-x", "099", ...)`. Commit a log line for 150 timed 23:59 (late). Write `.git/shallow` = `<HEAD sha>\nzz\n`. Run via `_run`.
  - Same line asserts as (a), and exit 1.
  - `_run(repo, "check_pipeline.py", "--next-id")` gives `(2, "")`, never `"080"`-style output.
  - I2 pastes the printed lines in 05.
- (c) `test_non_utf8_shallow_line_no_traceback`: `.git/shallow` = bytes `<40hex>\n\xff\n`. A `subprocess.run` with `capture_output=True` (bytes) gives exit 1, `b"Traceback" not in stderr`, and no git line ending in `: none`. 05 records the UNTRACKED CHANGE text.
- (c2) `test_non_utf8_repo_path_is_still_git`:
  - Setup: a repo in `tmp_path / os.fsdecode(b"r\xff")`. Skip with a reason if `mkdir` raises.
  - The run has no `not checked (no git)` line, `UNTRACKED CHANGE: none`, and no traceback.
- (d1) `test_uncommitted_log_file_is_skipped`: a git repo with a committed log, plus an uncommitted `logs/implementation/2026-11-20.md` holding a late-looking line. Expect `LOG TIME: none` and exit 0. The existing late-line tests stay unchanged.
- (d2) `test_next_id_orphan_branch_without_work`: `_repo_with_open_branch`, plus orphan branch `nowork` (README only, pushed), plus `_branch_adds(repo, "b099", "099", [])`. `--next-id` gives `100`, exit 0. Without b099, `--next-id` gives `041` (orphan counts 0).
- (d3) `test_main_ahead_exact_ref_only`: a repo with no origin/main and `refs/remotes/origin/main/x`, one commit ahead, created by `git update-ref`. There is no `MAIN AHEAD` line. The existing `test_branch_behind_main_says_main_ahead` (L744) still passes unchanged.
- (e) `test_branch_diff_failure_is_branch_error` (renamed from gap l): the same setup, which expects `"git diff failed (exit 1)" in res[0]["errors"]`. Via `main`, the output holds `BRANCH ERROR: origin/res (git diff failed (exit 1))` and exit 1.
- (f) `test_branch_show_failure_skips_classify`: patch `("show", "origin/short:work/060/05-build-report.md")` to `("", 128)` on the `_branch_adds(..., "short", "060", ["05-build-report.md"])` fixture. The output has `BRANCH ERROR: origin/short (git show failed (exit 128))` and no `BRANCH SKIPPED: 060`.
- (g) `test_inbox_flag_die_is_loud`: `_patched_git` `("rev-parse", "--is-shallow-repository"): ("", 128)` with a daily report gives `inbox_section()[1] is True` and the text has `git rev-parse failed (exit 128)`. `test_shallow_flag_unknown_no_file_is_full` (129) stays unchanged.
- (h1) `test_open_branches_none_line`: a git repo with no remote branches gives `OPEN BRANCHES: none`.
- (h2) `test_check_handoff_open_branches_states` (no git needed): patch `check_pipeline.open_branches` in `sys.modules`. A str makes `check_all` print `<ID>: not checked (open branches: git branch failed (exit 128))` and return 1. None gives `<ID>: no hand-off` and return 0. `test_all_names_branch_with_handoff` stays unchanged.
- Kept unchanged and must pass: L201 (`"OPEN BRANCHES" not in out` without git), `test_next_id_counts_open_branches` (041 / 058), `test_same_id_on_main_and_open_branch_is_a_clash`, `test_rules_branch_is_reported`, `test_criss_cross_branch_lists_only_its_own_changes`, `test_malformed_shallow_line_real_git_not_checked`, and the test_real_data_field.py patches.

**Mutations** (I2 runs them, I3 re-runs them on a scratch copy; each must fail the named test):
- m1: `continue` back at the blame failure in `late_log_lines` fails (a), (b).
- m1b: the ls-tree `why` ignored (treated as empty) fails (a).
- m2: `return []` back for a `branch -r` failure fails (a), (b), (h1 control stays green).
- m3: `next_id` back to treating a failure as `[]` fails (a), (b).
- m4: `main_ahead` returning 0 on failure fails (a). m4b: the exact-refname filter dropped fails (d3).
- m5: `errors="replace"` dropped on the main run fails (c) (traceback).
- m6: the top-level run back to `text=True, encoding="utf-8"` fails (c2).
- m7: `changed()` returning `[]` without recording the error fails (e).
- m8: the step 8 `128` branch removed fails (a) INBOX and (g).
- m9: a `_git("rev-parse", "HEAD")` line added in `main_ahead` fails `test_git_call_census`.
- m10: classify kept after a body failure fails (f).

**Checks:**
- `python3 -m pytest -q` passes, with the count as printed (today's plus about 13 new tests).
- `python3.11 -m py_compile scripts/check_pipeline.py scripts/check_handoff.py`, if python3.11 is present (RI-008).
- `python3 scripts/probe_guardrails.py --ref HEAD` after commit: 0 ANCHOR MISSING, and the RI-009/010/011 probes hold.
- `python3 scripts/check_pipeline.py` on this branch prints `OPEN BRANCHES:` and no `BRANCH ERROR:` (full clone). Exit is unchanged apart from today's in-progress items.
- `git diff .claude/agents/a1-auditor.md` shows additions only.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Scope note: 12 sites change code, 14 reviewed | Files 1 (`late_log_lines` 1, `open_branches` branch + 5 per-ref, `next_id` 2, `main_ahead` 2, `_inbox_gate` 1 = 12); census reasons for `log -1` and `_open_at` (14) |
| Step 1 `_git` decode (bytes + `os.fsdecode` top; `errors="replace"` main) | Files 1 `_git`; (c), (c2); m5, m6 |
| Step 2 `_git_ok` | Interface; Files 1; `test_git_ok_contract` |
| Step 3 LOG TIME (ls-tree list, uncommitted skip, blame failure entry) | Files 1 `late_log_lines` (list entry, change 1); (a), (b), (d1); m1, m1b |
| Step 4 `open_branches` None / str / list, per-ref errors, main lines, docstring, gap-(l) test changed | Files 1 `open_branches`, `main`, docstring; (a), (b), (e), (f), (h1), L201; m2, m7, m10; changes 3, 4 |
| Step 5 check_handoff | Files 2; (h2); change 5 |
| Step 6 `next_id` refusal, `ls-tree <ref> -- work/` | Files 1 `next_id`, `main`; (a), (b), (d2) with orphan (change 2); m3 |
| Step 7 `main_ahead` for-each-ref exact match | Files 1 `main_ahead`, `behind`; (a), (d3) (change 7); m4, m4b |
| Step 8 `_inbox_gate` 128 loud | Files 1 `_inbox_gate`; (a), (g); m8 |
| Step 9 census `{function: (count, reason)}` | `test_git_call_census`, keyed `(function, callee)` (Interface); m9 |
| Step 10 fixtures (a)-(d3) | Tests (a)-(d3) |
| Step 11 mutations m1-m8 | m1-m8 plus m1b, m4b, m9, m10 |
| Step 12 a1-auditor.md L29 sentence (RULES, person's OK) | Files 4 (plus L23 `BRANCH ERROR:`, change 6) |
| Step 13 RI-014 status line for 05/06 | Expected result, last bullet |
| Fact check row 7 / Removed: no git stderr in messages | `_git_ok` reason = argv[0] + code only (Interface) |
| Fact check row 18 correction: L681 request show | Files 1 `open_branches` (`"request.md" in files[item]`) |
| Fact check row 22: no `rev-parse HEAD` health probe | DROPPED: as decided in 03 (it does not fire in A1's repro); every site checks its own code |
| Fact check row 23 correction: L995 exit 128 | Step 8 row |
| Fact check row 25/40 correction: L624 bytes + fsdecode | Step 1 row; Extra research 1 |
| Fact check row 26: F10 strict `read_text` (11 sites incl. L686) | DROPPED: out of scope by request (git output only); A1 opens a separate item if wanted |
| Fact check row 46 correction: prefix match filter | Step 7 row; (d3) |
| Fact check row 47 correction: check_handoff + gap-(l) test + help text | Files 2, Files 1 docstring, test (e) |
| Fact check row 52 removed (concurrent fetch example) | DROPPED: removed by R3, no source |
| Removed: `surrogateescape` on L627 | DROPPED: as decided in 03 (crash moves to L694 `write_text`) |
| Missing input: git binary / not top-level | unchanged; L201, `test_work_code_without_git`; (h2) None case |
| Missing input: non-UTF-8 `--show-toplevel` | (c2) |
| Missing input: non-UTF-8 stdout/stderr | (c) |
| Missing input: HEAD tree list for logs fails | (a); m1b |
| Missing input: log file not in HEAD | (d1) |
| Missing input: blame of committed log fails | (b) (real die); m1 |
| Missing input: `branch -r` fails | (a), (b); `--next-id` exit 2 |
| Missing input: per-ref diff / ls-tree / merge-base / show fails | (e), (f); (a) covers all at once |
| Missing input: request.md absent on a ref | `test_open_branch_item_that_skips_steps_is_reported` unchanged (absent request path), plus 03's `"request.md" in files` test in (f)'s fixture control |
| Missing input: `log -1` fails | census reason (cosmetic) |
| Missing input: no origin/main | (d3), and the existing no-remote fixtures print no MAIN AHEAD |
| Missing input: origin/main lookup or count fails | (a); m4 |
| Missing input: `--is-shallow-repository` exit 128 | (g), (a) |
| Missing input: `_shallow_boundaries` both calls fail | DROPPED: known gap, docstring note; still exit 1 (wrong reason), 079's text out of scope |
| Self-check row 1 (39 calls, 15 functions) | Census table recount: 41 after the build; I2 pins the printed count |
| Self-check rows 3-8 | (a) line list, (d2) 100, step 8 128-vs-129, (d3), probe anchors check |

## Guardrail tests
- Feasibility: LOG TIME uncommitted skip, 0 of 1 log files listed → (d1). `--next-id` disambiguation, orphan branch 0 IDs plus b099 → 100, or 041 without b099 → (d2). MAIN AHEAD exact ref, 0 of 1 refs match → no line → (d3). INBOX loud iff code == 128 (A1 repro 128 → loud; 079 test 129 → unchanged) → (g) and `test_shallow_flag_unknown_no_file_is_full`. Census 41 calls → `test_git_call_census`.
- Missing inputs: each row of 03's Missing inputs maps to an absent-case test in the Rule trace above. Two have no new test, by reason: `log -1` (cosmetic, census) and the `_shallow_boundaries` both-fail gap (docstring).

## Expected result
- 4 files changed (plus 05).
- On this branch, in a full clone, `check_pipeline.py` prints `OPEN BRANCHES: none` or the branch block, `MAIN AHEAD` only when behind, and no `BRANCH ERROR:`. The exit status matches today's apart from items still in progress.
- In A1's malformed-shallow repro, no git-reading line says `none`, the exit is 1, and `--next-id` exits 2 with empty stdout (not `080`).
- A `\xff` shallow line gives no traceback.
- The full suite passes, with the count as printed by pytest. m1-m10 each fail a named test. `probe_guardrails.py --ref HEAD` shows 0 ANCHOR MISSING.
- 05/06 status line (step 13): "RI-014: guardrail extended (081); GUARDED when 079 and 081 are merged and m2 fails fixture (b) on main."
