# 04 Build plan - 091
Fit verdict: FIT WITH CHANGES

Method: I1 has no shell (item 072). I read work/091/request.md, 01-03, logs/recurring-issues.md, work/088/04, work/089/03, work/090/03 (089 and 090 have no 04 yet), and the cited code, all on daily-fixes/2026-11-21 (working tree, 2026-11-21). Nothing was run. 088 is already in the working tree: `_anchor_env` now returns `(env, failed)` (scripts/check_pipeline.py L628-649) and main's exit expression ends `or env_failed` (L1656-1658). So 03's line numbers have already moved by about 5-13 lines. **I2: re-read every line number at step 0, after 090 is committed. Find code by its text, not by any number in 03 or here.**

Fit: this is process and test hardening only. It has no trade, broker, account or strategy input, so the ~$3k account and the 001 rules are untouched, and no rule the person follows changes. RULE_PATHS are touched (.claude/, templates/, scripts/check_pipeline.py), so RULES BRANCH shows and **the person's OK is needed at PR review**. Changes to 03:
1. **One section reader (5b).** The stray-heading check and `_run_seconds` share one open/close function, so the two cannot drift apart. In 03 the check copies the rule instead.
2. **5b entry text has no `L<n>`.** `_md_lines` drops HTML comments before `splitlines()` (L451), so a multi-line comment shifts row numbers. The entry names the heading text.
3. **commit_step edge cases from extra research:** an absolute `GIT_INDEX_FILE`; `read-tree` as the first command on the empty mkstemp file; refusals for a named log path, a directory path, and a deletion.
4. **run-item sentence scope.** 03's "never with `git add logs/...`" would forbid A1's `logs/audit/` and `logs/recurring-issues.md` commits. It is narrowed to logs/research and logs/implementation files.
5. **5b unreadable text** follows 089's consumer form (`... not checked (<why>; item 091)`), not a new `unreadable (item 091)` text.
6. **Exit-term table (step 0).** 089 step 9 asks 091 to cover 089's `unreadable` term, and 088 asks it not to duplicate `env_failed`. Neither gets a new test. I2 names, for every term in the final exit expression, the test that kills its drop, so there is one table and no duplicate tests.
7. **The equivalent mutant in step 1 gets a reason test.** Dropping `scripts/check_pipeline.py` or `scripts/check_handoff.py` from the ls-tree list changes nothing while `scripts/` is in RESEARCH_CODE_PATHS. A small test pins that premise, so the residual cannot become a real gap without a failing test.

## Extra research (with sources)
- **Empty temp index file.** git commit db137fe (A. Julliard, 2009) fixed `GIT_INDEX_FILE=\`mktemp\` git read-tree master`, which failed with "fatal: index file smaller than expected". It added t1009 with the tests 'non-existent index file' and 'empty index file'. Both expect a non-merge `read-tree` into a zero-length file to succeed (https://timplab.syktsu.ru/admin/git/commit/db137fe91ea4afda7a2073364c610fe61dc769b8; https://code.googlesource.com/git/+/maint/t/t1009-read-tree-new-index.sh). So 03's mkstemp file works only if `read-tree HEAD` is the **first** git command run on it. The plan fixes that order, and test T1 pins it: if the order is wrong, T1 fails with that fatal error.
- **Relative GIT_INDEX_FILE.** A relative path is resolved against the work-tree top in one setup and against the cwd in another (detached work tree). The git thread says this makes it "impossible for any program that wants to use GIT_INDEX_FILE to use anything other than an absolute path" (https://public-inbox.org/git/xmqqtwho8spb.fsf@gitster.mtv.corp.google.com/T/). `git rev-parse --git-dir` prints `.git` (relative) at the top. So commit_step uses `--absolute-git-dir` (or `Path(...).resolve()`), and the mkstemp `dir` is absolute. This matches 03's 3.10/3.11 mkdtemp correction.
- **Comments shift rows.** `_md_lines` removes `<!--.*?-->` with re.S before splitting (scripts/check_pipeline.py L451). A comment that spans lines therefore removes rows. → change 2.
- **UTF-8 rule.** tests/test_safety.py `test_every_text_file_call_names_utf8` scans `scripts/*.py`, so commit_step.py falls under it. commit_step reads log files with `read_bytes()` and decodes explicitly, so the bytes are exact and the test holds. `test_fstrings_parse_on_python_310` also covers the new script and its test (RI-008).
- **Hooks.** Glob of .git/hooks: 14 `*.sample` files only. This agrees with 03, so `commit-tree` bypasses no live hook today. It is stated as a residual: if someone adds a hook, commit_step does not run it.
- **Considered and rejected:** one log file per item. It would remove the shared-file problem, but it changes every LOG_LINE reader (`_log_text`, `_item_lines`, `late_log_lines`, `_last_log_line`, the I3 loop, `orphan_log_lines`) and 089's reader table. That is much bigger than a helper.

## Files to create/change
12 files (plus I2's own work/091/05).

| # | File | Change |
|---|---|---|
| 1 | tests/test_pipeline_check.py | Steps 1, 2, 4, 5a and 5b tests, and 7's text pin |
| 2 | tests/test_probe_guardrails.py | Step 3 (two tests) |
| 3 | scripts/check_pipeline.py | Step 5b: `ROUND_HEADING_FROM = 92`, `STRAY_RUN_HEADING`, shared `_section_flags`, `stray_run_headings`, the `incomplete()` hook, a docstring line |
| 4 | scripts/commit_step.py (new) | Step 6 |
| 5 | tests/test_commit_step.py (new) | Step 6 tests |
| 6 | templates/build-report.md | Step 5a line |
| 7 | templates/verification.md | Step 5a line |
| 8 | .claude/commands/run-item.md | Step 4 UNSHALLOW, step 6 sentence, step 7 SCRATCH |
| 9 | .claude/commands/daily-audit.md | Step 4 UNSHALLOW |
| 10 | .claude/agents/a1-auditor.md | Step 4 UNSHALLOW, step 7 SCRATCH (new line) |
| 11 | .claude/agents/i2-builder.md | Step 6 pointer, step 7 SCRATCH |
| 12 | .claude/agents/i3-verifier.md | Step 6 pointer, step 7 SCRATCH |

Commit order (03, 02 AGAINST 3):
- (A) steps 1-3, tests only;
- (B) steps 4, 5a, 5b and 7;
- (C) step 6, the last commit, made with commit_step itself.

If step 6 fails I3 twice, I1/R3 may split it into its own item and keep (A) and (B).

### Step 0: base, no edit (05 "Base" block)
- Paste `git log --oneline -4` (it must show 088, 089 and 090) and the head sha.
- Re-read, by text:
  - `open_branches` (the unrelated block and its ls-tree list), `main_ahead`, `next_id`;
  - main's final exit expression;
  - `_run_seconds`, `batch_log_items`, `incomplete`, `_rule_seen`;
  - 089's `_read` and `_UNREAD`;
  - the GIT_CENSUS total assert and 089's `test_read_census` totals;
  - `UNSHALLOW` and its 3 copies.
- Paste the census total as read (88 keeps it at 47; 089 adds 0; 090 may change it). 091 adds 0 to both censuses.
- **Exit-term table:** one row per term of the final exit expression, each naming the existing test that fails when that term is dropped. Sources: 088/05 (`env_failed` → `test_anchor_env_failure_exits_1`), 089/05 (`unreadable` → 6a, M3), 090/05, plus step 2 here (`isinstance(branches, str)`, `isinstance(ahead, str)`). A term with no killing test is listed as `none found`, and A1 opens it as a follow-up. 091 does not add tests outside sub-ask 1.
- State whether 090 changed the UNSHALLOW list and whether it names RULE NOT SEEN.

### Step 1: sub-ask 1, A1-A3 (tests/test_pipeline_check.py)
- **New `test_unrelated_branch_each_checked_group_is_branch_error(tmp_path)`, `@NO_GIT`. R2-c is unchanged.**
  - Setup: `repo = _repo_with_open_branch(tmp_path)`, then 8 `_orphan` calls, one file each:

    | Branch | File |
    |---|---|
    | `w` | work/150/request.md |
    | `ri` | logs/recurring-issues.md |
    | `cl` | .claude/agents/x.md |
    | `tp` | templates/x.md |
    | `cb` | ccbot/x.py |
    | `cf` | config/x.json |
    | `sc` | scripts/x.py |
    | `ts` | tests/test_x.py |

  - Run once: `_run(repo, "check_pipeline.py", "--untracked-from", _root(repo), "--today", "2026-11-02")`.
  - Assert exit 1.
  - Assert each of the 8 exact lines `BRANCH ERROR: origin/<n> (no common history with HEAD; 1 file(s) on checked paths (first: <path>) not checked (item 081))`.
  - Assert `subprocess.run(["git","merge-base","--all","HEAD","origin/w"], cwd=repo).returncode == 1`.
  - The fixture is not shallow, so 090's shallow text does not apply. If 090 changed this text for the non-shallow case, I2 uses 090's text and says so in 05.
- **New `test_rule_path_files_are_inside_research_code_dirs()`** (change 7):
  - `assert all(any(f.startswith(d) for d in cp.RESEARCH_CODE_PATHS) for f in cp.RULE_PATHS if not f.endswith("/"))`.
  - Its docstring says why: the two file entries cannot be isolated by an orphan, and dropping them from the ls-tree is an equivalent mutant only while this holds.

### Step 2: sub-ask 1, A8, A9, A13 (in-process; `monkeypatch.chdir(repo)`; `_patched_git` on exactly one tuple)
Each test first runs its control unpatched, with the same args.
- `test_branch_list_failure_exits_1`:
  - control: `cp.main(["--untracked-from", root, "--today", "2026-11-02"]) == 0`;
  - patch `("branch","-r","--no-merged","HEAD","--format=%(refname:short)") → ("",128)` → `== 1`;
  - out has `OPEN BRANCHES: git branch failed (exit 128) (item 081)`.
- `test_main_ref_lookup_failure_exits_1`:
  - patch `("for-each-ref","--format=%(refname) %(objectname)","refs/remotes/origin/main") → ("",128)` → `== 1`;
  - out has `MAIN AHEAD: git for-each-ref failed (exit 128) (item 081)`.
- `test_main_ahead_count_failure_exits_1`:
  - patch `("rev-list","--count",f"HEAD..{sha}")`, with sha from `git rev-parse origin/main` → `("",128)` → `== 1`;
  - out has `MAIN AHEAD: git rev-list failed (exit 128) (item 081)`.
- `test_next_id_branch_listing_failure_refuses`:
  - control: `cp.main(["--next-id"]) == 0`, stdout `041\n`;
  - patch `("ls-tree","-d","--name-only","origin/fix","--","work/") → ("",128)` → `== 2`;
  - stdout empty;
  - stderr has `--next-id refused: git ls-tree failed (exit 128)`.
- If 090 gave `main_ahead`/`open_branches` an `env` argument, the patched tuples still apply, because the git args are unchanged. I2 re-checks them by text.

### Step 3: sub-ask 5a, M11 (tests/test_probe_guardrails.py)
- `test_recorded_with_trailing_text_is_unreadable`:
  - `_main(root, capsys, [_probe("z", recorded="2026-01-01: 1 failed, 1 passed x")])`;
  - `_line(out, "z")` contains `recorded 2026-01-01: 1 failed, 1 passed x (recorded unreadable)`;
  - exit 0.
- `test_recorded_trailing_newline_is_unreadable`:
  - `pg._recorded_marker({"recorded": "2026-01-01: 1 failed, 1 passed\n"}, {"t": "failed"}) == " (recorded unreadable)"`.
- Code is unchanged: it keeps `fullmatch` and never uses `prefixmatch` (3.15+, RI-008).

### Step 4: sub-ask 5b, UNSHALLOW
- Edit `UNSHALLOW` and its 3 copies in one change, so that the list of lines reported as 'not checked' also names `RULE NOT SEEN` and the item list gains 084. On today's text that gives: `... report UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD and RULE NOT SEEN as 'not checked', never 'none' (items 079, 084).`
- If 090 changed the list, add RULE NOT SEEN to 090's list. If 090 already names it, make no edit and say so in 05.
- INBOX stays out (`failed=False`). 088's unborn/verify forms and 089's UNREADABLE stay out too, because they are not shallow-clone results (see the Rule trace).
- Add `assert "RULE NOT SEEN" in UNSHALLOW` to `test_unshallow_sentence_same_in_three_files`.

### Step 5a: templates
- templates/build-report.md, the line under `## Test output (pasted, not summarized)`: `Each later round's runs go under their own level-2 heading \`## Test output (round N, pasted)\`, never under a \`###\` heading or a \`Round N ...\` heading (item 091).`
- templates/verification.md, the same under `## Tests re-run (output)`, with `## Tests re-run (round N)`.
- Test `test_round_heading_template_lines`:
  - `count(line) == 1` in each template;
  - `re.match(r"## Test output\b", "## Test output (round 2, pasted)")` and `re.match(r"## Tests re-run\b", "## Tests re-run (round 2)")`, using the opener strings `batch_log_items` passes, read by text at step 0;
  - `cp.STRAY_RUN_HEADING.match(<template line>) is None`, so the line itself is never stray.

### Step 5b: the check (scripts/check_pipeline.py)
- Constants: `ROUND_HEADING_FROM = 92` (item 091) and `STRAY_RUN_HEADING = re.compile(r"#{1,6} (?:round \d+ )?(?:test output|tests re-run)\b", re.I)`, used with `.match` (anchored, RI-012).
- **New `_section_flags(rows, heading)`.** It returns a list of bools (inside a read section) per `_md_lines` row, using `_run_seconds`'s exact rule as it stands after 090:
  - an "out" row matching `heading` opens the section (the opener row itself is False);
  - an "out" row matching `#{1,2} ` closes it.
- `_run_seconds` is refactored to use it, with no behaviour change (change 1).
- **New `stray_run_headings(path, opener) -> (headings, why)`:**
  - read with 089's `_read(path, missing_ok=True)`;
  - absent → `([], None)`; unreadable → `([], why)`;
  - otherwise, every "out" row with `STRAY_RUN_HEADING.match(line)`, `not re.match(opener, line)` and flag False.
- **In `incomplete()`,** for `int(ID) >= ROUND_HEADING_FROM`, for (05, `## Test output\b`) and (06, `## Tests re-run\b`). The openers are taken from where `batch_log_items` defines them, never retyped:
  - headings found → fired = `<05|06> heading '<heading>' is not read by LOG BATCH; use '## Test output (round N, pasted)' / '## Tests re-run (round N)' (item 091)`. There is one entry per file, and it lists all of that file's headings joined by `', '`.
  - why → `<05|06> round headings not checked (<why>; item 091)`. 089's UNREADABLE line also gets the file.
  - Gate, only when one fires, exactly as SUITE_FROM: `seen, sha7 = _rule_seen(item_dir, "05"|"06", "ROUND_HEADING_FROM", env)`. `False` gives a not_seen row `(ID, step, sha7, "ROUND_HEADING_FROM", "091", "no round-heading check")`. Otherwise `missing += [fired] + ([sha7] if seen is None and sha7 else [])`.
- This adds no `_git(` call and no raw read, so both censuses are unchanged.
- Module docstring: one line for item 091, plus the residuals (runs with no heading, e.g. 076/05 L29-59; headings indented 1-3 spaces; text-only templates).

### Step 6: sub-ask 3, scripts/commit_step.py (Python 3.10-safe)
- **Usage:** `python3 scripts/commit_step.py <ID> "<subject>" <path>...`, run from the repo top.
- **Imports:** `LOG_LINE` from check_pipeline, as check_handoff does (`sys.path.insert` of the script dir).
- **Layout:** `run(args, env=None, input=None) -> (stdout_bytes, code)` (patchable; `None` when git is missing); `filter_log(work: bytes, head: bytes | None, item) -> (bytes, own_added: list[str])` (raises `Refused`); `commit(item, subject, paths, run=run, old=None) -> int`; `main(argv)`.
- **(i) Refusals, exit 2, nothing written:**
  - no git, or cwd is not `--show-toplevel`;
  - unborn HEAD (`rev-parse --verify -q HEAD` exit 1);
  - a named path is missing (deletion not supported: residual), or is a directory;
  - a named path is under logs/research/ or logs/implementation/ (the helper finds those itself).
- **(ii) Build the log blobs.**
  - `old` = `rev-parse HEAD`.
  - For each `logs/{research,implementation}/????-??-??.md` in the working tree, take HEAD's bytes via `ls-tree HEAD -- <p>`. Exit 0 with empty output means absent; that is a real answer, with no HEAD lines. Otherwise read the blob with `cat-file blob <oid>`, keeping the mode from ls-tree.
  - `filter_log` splits both texts with `keepends=True` after a strict UTF-8 decode (an error → Refused `<file> unreadable`).
  - It walks the working lines with a pointer into HEAD's lines. A line equal to `head[ptr]` is kept and advances the pointer. Any other line is "added", and it is kept unless it is a LOG_LINE whose ID is not `<ID>`.
  - If the pointer has not reached the end, refuse with `<file>: committed lines changed; nothing committed (item 091)`.
  - Files whose result equals HEAD's bytes are not staged.
- **(iii) Temp index.**
  - `fd, idx = tempfile.mkstemp(dir=<absolute git dir>)`, closed at once, deleted in `finally`.
  - env = `{**os.environ, "GIT_INDEX_FILE": idx}`, absolute.
  - The first command is `read-tree HEAD` (t1009). Then `update-index --add -- <paths>`. Then, per blob, `hash-object -w --stdin --path <p>` and `update-index --add --cacheinfo <mode or 100644>,<sha>,<p>`. Then `write-tree`.
  - Any non-zero exit → `git <cmd> failed (exit n); nothing committed (item 091)`, exit 2.
- **(iv) Subject.**
  - 0 own lines added: any subject is accepted.
  - 1: the subject must equal `Item <ID>: ` + that line, with the newline stripped.
  - 2 or more: refused (a batch, item 045).
- **(v) Commit.** `commit-tree <tree> -p <old> -m <subject>`, then `update-ref -m "commit_step: <subject>" HEAD <new> <old>`. A non-zero exit gives `HEAD moved (<old7> -> <cur7>); re-run (item 091)`, exit 2, with HEAD unchanged.
- **(vi) Shared index.** `git reset -q -- <paths> <staged log files>`. If it fails: exit 1 with `commit <sha7> made; run git reset -q -- <paths> (item 091)`. On success: print `<sha7> <subject>`, exit 0.
- **run-item.md: one new sentence after (5) in L17.** The pinned 082 sentence stays byte-identical. The sentence: every commit that carries a logs/research or logs/implementation line, made by the orchestrator, I2, I3 or A1, is made with `python3 scripts/commit_step.py <ID> "<subject>" <paths>...`. It is never made with `git add` of a logs/research or logs/implementation file, `git add -A`, `git commit -a` or `git commit <log path>`. The helper does not split two items' edits inside one code file, so items that change the same file are built (I2-I3) one after another, never in parallel (item 091).
- **Pointers:** one line each in i2-builder.md and i3-verifier.md.
- **091's own last build commit** (C) is made with the helper, and its output is pasted in 05.

### Step 7: sub-ask 4, SCRATCH
- The same sentence in run-item.md, in i2-builder.md (by its scratch line), in i3-verifier.md (by its scratch line) and in a1-auditor.md (a new line; it has no scratch line today): `Every agent works in its own new scratch dir, made with \`python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="<agent>-<ID>-r<round>-", dir="<absolute scratchpad path>"))'\`, and never reuses or writes into another agent's dir, even for the same item; agents with no shell (R1-R3, I1) get theirs from the orchestrator (item 091).`
- `test_scratch_sentence_same_in_four_files`: `count(SCRATCH) == 1` in each.
- 05 states that this is text only: no check can see a real collision.

### Step 8: close
- Full suite.
- `python3.11 -m py_compile` on the 4 changed or new .py files (RI-008).
- `python3 scripts/check_pipeline.py`: 091 shows no INCOMPLETE or SKIPPED, and LOG TIME and LOG BATCH do not name it.
- Whole-output diff of check_pipeline.py before and after (B), same args (RI-013). Expected: no line changes, since 0 items are ≥ 92 and the `_run_seconds` refactor changes no LOG BATCH value.
- 090's TIMED_FROM applies to 091 (≥ 90): I2's log field must carry `in <s>s`, and 05 must hold a pytest time under a read heading (090 step 2 makes "not computable" an INCOMPLETE entry). Use the new round headings for round 2+.
- I3 re-runs every mutant below in its own mkdtemp dir.

## Tests and checks
| Test | Mutant (scratch copy only) | Must fail |
|---|---|---|
| step 1 orphans | A1 drop `*RESEARCH_CODE_PATHS`; A2 drop `*RULE_PATHS`; A3 drop `RECURRING`; drop `"templates/"` alone; drop `"scripts/"` alone; drop `"work/"` | each makes one or more of the 8 lines missing |
| step 1 premise | remove `"scripts/"` from RESEARCH_CODE_PATHS | `test_rule_path_files_are_inside_research_code_dirs` (and the `sc`/`cb`... lines) |
| step 2 A8 | drop `isinstance(branches, str)` from the exit | A8 test (exit 0) |
| step 2 A9 | drop `isinstance(ahead, str)` | A9a and A9b |
| step 2 A13 | `listing = ""` on ls-tree failure in next_id | A13 (`041` printed) |
| step 3 | M11 `.fullmatch` → `.match`; M11b `.match` + `$` added to RECORDED | (i); (ii) |
| step 4 | old sentence restored in one file; RULE NOT SEEN removed from all 4 | byte test; new assert |
| step 5a | template line deleted (each template) | count test |
| 5b P1 | 05 `## Round 2` + `### Test output (round 2, pasted)` + a summary line | entry; also `_run_seconds` returns no time for that line (pins why) |
| 5b P2 | 05 `## Round 2 test output (pasted)` + summary | entry |
| 5b P3 | 06 `## Round 1` + `### Tests re-run (output)` | entry |
| 5b N1 | `### Test output (detail)` inside `## Test output (pasted, not summarized)` | no entry; `_run_seconds` reads its time |
| 5b N2 | `## Notes on test output` | no entry |
| 5b N3 | ID 091 with P1's shape | no entry |
| 5b N4 | `## Test output (round 2, pasted)` | no entry |
| 5b U | 05 = b"## Round 2\n\xff" | `05 round headings not checked (work/150/05-build-report.md unreadable; item 091)` and the UNREADABLE line |
| 5b G | git repo: P1's 05 committed under a RULE_FILE without `ROUND_HEADING_FROM` | no entry; RULE NOT SEEN row `05 added in <sha7> without ROUND_HEADING_FROM (091): judged by no round-heading check` |
| 5b mutants | check removed → P1-P3 fail; `###` only → P2; inside-section exemption removed → N1; `.search` → N2; cutoff 0 → N3 and `test_repo_pipeline_has_no_skipped_items` (070-086); gate removed → G; `_section_flags` closer changed to `#{1,3} ` → N1 and an existing LOG BATCH test | named |
| 5b real tree | I2 runs `stray_run_headings` over work/*/05,06 with the cutoff ignored (REPL or a throwaway test, scratch) | exactly 10 headings in 7 items (070, 077, 079, 081, 082, 084, 086), matched to 03's list by file and text. If any differs, stop and report; never adjust the expectation |
| 6 T1 | HEAD log = title, blank, L_head; working + L151 then L150; `git add x.txt`; `commit_step 150 "Item 150: <L150>" work/150/05-build-report.md` | HEAD files = {05, log}; `HEAD:<log>` = H + L150; `diff --cached --name-only` = `x.txt`; working log bytes unchanged |
| 6 T2 | then `commit_step 151 "Item 151: <L151>" <151 file>` | `HEAD:<log>` == working bytes |
| 6 T3 refusals (exit 2; `rev-parse HEAD` and `.git/index` bytes unchanged) | HEAD line edited; non-UTF-8 log; wrong subject; two own lines; missing path; directory path; named log path; `old` ≠ HEAD (`commit(..., old=<parent>)`); ls-tree failure and cat-file failure (patched `run`); no git (tmp dir, no repo); unborn HEAD | each |
| 6 T4 | a log file not in HEAD | staged with its title + own line |
| 6 T5 | `git reset` failing (patched `run`) | exit 1, message names the new sha7, HEAD advanced |
| 6 mutants | shared index (no GIT_INDEX_FILE) → T1 `x.txt`; whole log staged → T1; append instead of order → T2; `update-ref` without `<old>` → T3 HEAD-moved; whole-file fallback → T3 edited line; subject check off → T3; `update-index` before `read-tree` → T1 (fatal: index file smaller than expected) | named |
| 6 text | run-item sentence, 2 pointers | count == 1 each |
| 7 | SCRATCH removed from any one file | count test |

The test_commit_step.py fixtures use real git (skipped without it) and the same identity env as test_pipeline_check's `_git` (GIT_CONFIG_GLOBAL=devnull, author/committer t).

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 0 base re-read after 088-090 | Step 0, plus the exit-term table (change 6) |
| Step 1 8 orphans, exact lines, merge-base exit 1 | Step 1 |
| Step 1 residual (2 RULE_PATHS files) | Step 1 premise test (change 7) |
| Fact-check 1.6 correction (10 entries, 8 isolable) | Step 1 |
| FOR 1a correction (`scripts/x.py` orphan) | Step 1 `sc` |
| Step 2 A8/A9a/A9b/A13 with controls; 1.9 correction (chdir, `--untracked-from`) | Step 2 |
| 089 step 9 (`unreadable` term) / 088 (no second `env_failed` test) | Step 0 exit-term table; no new test |
| Step 3 (i), (ii); 5.4 correction (`\n` case direct call); 5.5 (no prefixmatch) | Step 3 |
| Step 4 RULE NOT SEEN in UNSHALLOW; 5.8 correction (091 owns it) | Step 4 |
| 088's ask: name unborn/verify forms in the unshallow sentence | DROPPED: they are not shallow-clone results, and the sentence is about `--unshallow` only |
| Step 5a template lines + text pin | Step 5a |
| Step 5b constant, regex, gate, fixtures P1-P3/N1-N4, real-tree 10/7 | Step 5b, Tests rows 5b; entry without L<n> (change 2); shared walker (change 1) |
| FOR 3 correction (widened regex, 084/05 L205) | Step 5b regex; P2 |
| Option (b) level-aware reading | DROPPED: 03 defers it (changes past LOG BATCH results with no measurement) |
| Step 6 helper (i)-(vi), subject rule, run-item sentence, pointers, own commit | Step 6, with change 3 (absolute index, read-tree first, extra refusals) and change 4 (sentence scope) |
| 3.9 / FOR 2 corrections (x.txt, HEAD-moved, subject, T2 order) | Tests T1-T3 |
| Step 7 SCRATCH ×4, a1 new line, mkdtemp absolute dir | Step 7 |
| 4.4 removed (mktemp -d) | DROPPED: removed in 03 |
| Step 8 close | Step 8 |
| Commit order / split rule | Files: commit order (A)-(C) |
| Rule text the person follows (001 slack/tolerance/cap) | None changed; no request needed |

## Guardrail tests
- Feasibility: step 1, 8 of 10 pathspec entries isolable → 8 BRANCH ERROR lines in one run; 2 equivalent → premise test.
- Feasibility: step 2 A8 control exit 0 on the plain fixture (R2-b precedent; 040 < 41) → patched 1.
- Feasibility: step 5b, 10 stray headings / 7 items at cutoff 0 (R3 Grep, 2026-11-21) → I2's real-tree run must reproduce it; 0 items ≥ 92 → whole-output diff shows no change.
- Feasibility: step 6 T1, 4 of 5 lines kept (3 HEAD + 1 own), 1 dropped → T1 asserts; today's logs/implementation/2026-11-21.md has 18 LOG_LINE lines (03 Self-check). This is information only; no test reads the live log.
- Missing inputs: `branch -r` fails → A8 test; for-each-ref / rev-list fail → A9a / A9b; per-ref ls-tree in next_id fails → A13; merge-base exit 1 → step 1 direct assert (128 is R2-d, existing).
- Missing inputs: probe `recorded` with extra text / trailing newline → step 3 (i)/(ii); absent `recorded` → existing tests.
- Missing inputs: 05/06 absent → N4-style fixture with no 06 (no entry); unreadable → 5b U; anchor env set → 5b tests run with no git (strict); anchor git failed → existing 084 d1 rows (shared `_rule_seen`); RULE_FILE lacks the constant → 5b G.
- Missing inputs (commit_step): no git, unborn HEAD, missing / directory / log path, ls-tree or cat-file failure, non-UTF-8, non-subsequence, HEAD moved → T3 rows; HEAD log absent → T4; reset failure → T5.

## Expected result
- Suite green. Both censuses are unchanged by 091 (GIT_CENSUS stays at the post-090 total; 089's read census stays at its total).
- Every mutant in the table fails its named test. The A1-A3, A8, A9, A13 and M11 survivors from the 081/082 audits are now killed.
- `check_pipeline.py` on the real tree: the whole output is unchanged by (B), and 091 is clean.
- commit_step commits only the item's own log line; a staged foreign file stays staged and out of the commit; the working log is untouched.
- Residuals, stated in 05:
  - runs with no heading (076/05);
  - headings indented 1-3 spaces;
  - template lines and SCRATCH are text-only;
  - commit_step does not split one code file between items, does not run hooks, and does not commit deletions.

Recurring issues checked (item 013):
- RI-001 (ESCALATED): every filter has a dated count: 8/10 entries, 10 headings / 7 items, 0 items ≥ 92, 4 of 5 lines. Each has a test or a reproduce step; nothing says "always".
- RI-010 (ESCALATED): new duties get a check where one can exist (5b INCOMPLETE; commit_step refuses a wrong subject or a batch). 5a and 7 are text-only, and 05 says so. I1 typed no log line; the fields line below is for the orchestrator.
- RI-014 (OPEN): no new depth-dependent reader. 5b uses the 084 gate, which is strict when shallow. Step 4 names RULE NOT SEEN in the unshallow sentence.
- Also checked (GUARDED): RI-002 (every absent input has a not-checked or refusal, with no default); RI-004/005 (T1/T2 and the 10/7 count re-derived from 03's Self-check); RI-006 (12 files, counted from the table); RI-008 (no prefixmatch; absolute mkstemp/mkdtemp dir; py_compile 3.11); RI-009 (built on 090's head; re-read at step 0); RI-012 (anchored `.match` heading regex with negative N2; commit_step classifies by exit code only).

Log fields: FIT WITH CHANGES | 12 files planned
