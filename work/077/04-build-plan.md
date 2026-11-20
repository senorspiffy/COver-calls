# 04 Build plan - 077
Fit verdict: FIT WITH CHANGES

Fit check: this is process tooling only. Nothing in ccbot/, config/, data/ or reports/ changes, nothing connects to a brokerage, and the ~$3k account rules in 001 are unchanged. It fits the existing checker: every change extends a function that is already there (`open_branches`, `classify`, `_open_at`, `i3_verdict`, `_field_gap`, `incomplete`, `main`) or adds a small helper next to it. It does not call or change `_walk` (079's).

Build order (brief): 075 -> 076 -> **077** -> 078 -> 079. Build on 076's commit. 076 changes `LOG_FORMAT["I2"]`, adds `log_fields_ok`/`log_hint`, and rewrites the `bad = ...` and `wants = ...` lines of `incomplete()`. It also adds `_field(agent, item)` to tests/test_pipeline_check.py and uses it inside `_item`. This plan names functions and anchors, not line numbers. I2 re-reads every anchor on 076's tree. Step 5 factors out only the log-text join and the `unlogged` regex of `incomplete()`, and keeps 076's `log_fields_ok`/`log_hint` lines exactly as 076 left them (076 note: "any new reader of I2 log lines must call `log_fields_ok`". Step 5 reads only whether a `| <agent> | <ID> |` line exists, never its fields, so this does not apply).

Changes against 03 (why "WITH CHANGES"):
1. **A1 is never told to read the two new lines (RI-010).** `.claude/agents/a1-auditor.md` (job B, the check_pipeline bullet and the open-PR bullet) lists by name every line A1 must report (SKIPPED, INCOMPLETE, LOG TIME, ID CLASH, BRANCH SKIPPED, RULES BRANCH, UNTRACKED CHANGE). It names neither `BRANCH FAIL:` nor `UNCOMMITTED STEP:`. Without them, 077 prints lines that no duty reads. That is RI-010's shape in reverse. Plan: one clause added in each bullet (Files 4), pinned by a text test. This adds a 4th file to 03's map. `.claude/` is in RULE_PATHS, so the edit needs the person's OK in PR review, as check_pipeline.py already does. 078 later edits a different paragraph of the same file (the probe_guardrails runtime), so the two do not overlap.
2. **Step 3: a mutation survives.** T5 asserts only `174: I3 FAIL (`. With the new check weakened to `if a1:` (last line not tested), T5 (a1 = [FAIL]) gets the new detail and still passes. With `a1[0]` instead of `a1[-1]`, no planned fixture fails either. Fix: T5 asserts the full old detail. T-P3 adds item 185 whose 07 has `FAIL` then `PASS` (want: new detail).
3. **Step 3: the PRE_A1_LINE/LEGACY sentence conflicts with 03's formula.** 03's docstring text says "PRE_A1_LINE and LEGACY items keep the old detail", but its formula reads 07's A1 lines only, with no exclusion. The plan keeps the formula: classify reads 07 alone, the same rule for every item. The docstring states the remaining difference as a known gap: a PRE_A1_LINE or LEGACY item with a 06 FAIL and no A1 PASS line in 07 keeps the old detail, while `_open_at` calls it closed. There are 0 such items (03 F18). It is pinned by test T-P3b (017 with no A1 line).
4. **Step 4: four spec cases with no test.** These are: a closer indented 4+ spaces (inside a fence it is content, not a closer); a backtick opener whose info string holds a backtick (not an opener); a tilde opener whose info string holds a backtick (an opener); and a backtick line inside a tilde fence (not a closer). The planned mutations "closer uses `lstrip()`", "backtick-info rule dropped", "backtick-info rule applied to `~`" and "closer accepts either char" all survive 03's ids. Four T4 ids are added.
5. **Step 4: 03's grep misses one closer shape.** 03 counted `^\s*```\S` (0). A line "``` note" (backticks, spaces, then text) is a valid opener but not a closer under the new rule, and that pattern was not counted. I2 also greps `^\s*(```|~~~)[ \t]+\S` over work/*/0[56]-*.md. Beyond the whole-output diff, I2 runs a scratch-only comparison of old vs new `i3_verdict` on every 06 and old vs new `_field_gap` on every 05/06, and pastes the counts in 05.
6. **Step 5: three test-design fixes.**
   - (a) P5f must assert `git rev-parse --is-shallow-repository` == `true`, so it cannot quietly test a full clone (precedent: `test_cutoff_missing_in_shallow_clone_not_checked`). The uncommitted files are made in the clone after cloning, because untracked files are not cloned.
   - (b) 03's Missing-inputs row "ls-tree fails -> failed, exit 1" has no test. P5h adds one (unborn HEAD).
   - (c) The "no logs/ folder" row is pinned by building P5b on a repo with no logs/ folder.
7. **Docstrings.** The module docstring says "Two more lines come from the branches" (ID CLASH, BRANCH SKIPPED). With BRANCH FAIL that becomes "Three more lines". The `open_branches` docstring lists the dict keys and gains `failed`.

## Extra research (with sources)
- **Shallow clones of a local repo (P5f).** git-clone: a plain path "implies `--local`". For a URL ("`file:///path/to/repo.git/`") "this flag is ignored (and we never use the local optimizations)". `--depth` creates "a *shallow* clone with a history truncated to the specified number of commits" (https://git-scm.com/docs/git-clone, fetched 2026-11-19). So P5f must clone from `file://...`, as the existing shallow test does, and must assert shallowness rather than assume it. The page does not say whether `ls-tree HEAD` sees the whole tip tree in a shallow clone. That stays UNVERIFIED until P5f runs, as 03 F39 says.
- **Unborn HEAD (P5h).** In a repo with no commit, `_git("rev-parse", "HEAD")` is not None: `_git` returns None only when the cwd is not the top of a work tree (`_git` docstring). So `uncommitted_steps` goes on to `ls-tree HEAD`, which cannot resolve HEAD. 03's rule turns this into `git ls-tree HEAD failed (item 077)` with exit 1. That is the right result (never `none`, RI-002). The exact git exit code is UNVERIFIED by a run; P5h checks only the line text. The other checks already run without commits (`test_inbox_repo_without_commits_checks_content`).
- **Fence edge cases (CommonMark 0.31.2 §4.5, fetched by 03).** The closing fence "may be preceded by up to three spaces of indentation". It must be the same character and "at least as long as the opening fence". A backtick fence's info string "may not contain any backtick characters". This gives the four added T4 ids in change 4.
- **No better method found.** The two other options are a CommonMark library (e.g. markdown-it-py) or one `git status --porcelain -uall` call instead of `ls-tree`. The library would add a dependency for one line helper, and it handles containers, which 03 records as gap F29 with 0 cases. git status adds C-quoting and "modified" states that 03 gap (b) keeps out of scope (03 F34-F36). Neither is simpler, so 03's choices stand.

## Files to create/change
4 files.

1. **scripts/check_pipeline.py** (RULE_PATHS: needs the person's OK)
   - **Step 2 `open_branches`.** In the per-item loop, right after `status, detail = classify(d, today)`, also collect `(item, status, detail)` into `failed` when status is `"I3 FAIL"` or `"A1 FAIL"`. After the item-062 `_research_code` merge loop, set `failed = [f for f in failed if f[0] not in {i for i, _ in skipped}]`. Add `"failed": failed` to the dict appended to `found`, and add `failed [(item, status, detail)]` to the docstring.
   - **Step 2 `main`.** After the `BRANCH SKIPPED:` loop, add `for item, status, detail in b["failed"]: print(f"BRANCH FAIL: {item} ({b['ref']}: {status}; {detail})")` for each branch. The exit expression is unchanged by step 2.
   - **Step 2 module docstring.** Change "Two more lines" to "Three more lines". Add a `BRANCH FAIL` entry after `BRANCH SKIPPED` with 03's text: "an item the open branch changes is I3 FAIL or A1 FAIL by the rules above, using the branch's own files (item 077). Listed for A1; exit code unchanged, since the branch is not part of HEAD. An item that is BRANCH SKIPPED is not also listed here. A branch file git cannot show is read as empty, so its I3 FAIL is not listed." Remove known gap (x) from the item-071 paragraph and keep (w) (rewritten, below), (y) and (z).
   - **Step 3.** Add `def _a1_results(text): return re.findall(r"^A1 result:\s*(\w+)", text, re.M)` next to `i3_verdict`. Use it in `classify` (the `verdicts = ...` line in the `len(have) == len(need)` block) and in `_open_at` (`verdicts = ...`). In `classify`'s `if verdict == "FAIL":` branch, before the existing return:
     - read `a1 = _a1_results(audit_text)` when `item_dir / STEPS["07"]` exists, else `[]`;
     - if `a1 and a1[-1].upper() != "FAIL"`, return `"I3 FAIL", f"{scope}; {where}; 06 FAIL after A1 PASS in 07: a follow-up to a completed item is a new item (run-item, items 053, 077){extra}"`;
     - otherwise return the existing detail unchanged.
     The docstring replaces gap (w) with: "a 06 FAIL with a 07 whose last A1 line is not FAIL is I3 FAIL with that detail; _open_at (053) still treats the item as closed, so a code commit for it is an UNTRACKED CHANGE. Both report an error (item 077). classify reads 07 alone: a PRE_A1_LINE or LEGACY item with a 06 FAIL and no A1 PASS line keeps the old detail while _open_at calls it closed (known gap, 0 items 2026-11-19)."
   - **Step 4.** Add `FENCE_OPEN = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")` (used with `.fullmatch`) and `def _md_lines(text)` returning `(rows, open_at_end)`, exactly as in 03 "Exact rules". Strip comments first (`re.sub(r"<!--.*?-->", "", text, flags=re.S)`). The closer is `re.fullmatch(rf" {{0,3}}{re.escape(c)}{{{n},}}[ \t]*", line)`. A backtick opener whose group 2 contains a backtick is not an opener. Python 3.10 syntax only.
     - `i3_verdict(path)`: loop over `rows` and read only `state == "out"` lines. The first-line logic is unchanged. Docstring: "Fences are CommonMark 0.31.2 §4.5 code fences (``` or ~~~, _md_lines)". Drop "(~~~ is not tracked, 0 in 06 files 2026-11-18)".
     - `_field_gap(text)`: find the heading on an `out` row. The section takes every following row (any state) until an `out` row starting with `## `. In the for-else, return `"Real-data effect has an unclosed ``` fence"` only when `open_at_end` is True. The message text is unchanged (the t12 `unclosed` id pins it). Docstring updated the same way.
     - Module docstring, REAL-DATA FIELD entry: "lines inside ``` fences are read" becomes "lines inside code fences (``` or ~~~, CommonMark 0.31.2 §4.5) are read". Add known gaps: "fences inside list items or blockquotes are read line by line; comments are dropped before fences are tracked, so a `<!--` inside a fence with no `-->` on its line hides text to the next `-->`".
   - **Step 5.** Factor out of `incomplete()`:
     - `def _log_text(logs)`: the existing join over `("research", "implementation")` and `sorted((logs / sub).glob("*.md"))`.
     - `def _logged(text, agent, item)`: `re.search(rf"\|\s*{agent}\s*\|\s*{item}\s*\|", text) is not None`.
     `incomplete()` calls both. Its output is unchanged, and 076's `log_fields_ok`/`log_hint` lines are untouched.
     Add `def uncommitted_steps(logs=Path("logs"))` exactly as in 03 "Exact rules": None when `_git("rev-parse", "HEAD") is None`; one `_git("ls-tree", "-r", "--name-only", "HEAD", "--", "work/")` call (no `--full-tree`, 03 FOR 3b fix); a non-zero exit returns `("git ls-tree HEAD failed (item 077)", True)`; it walks `sorted(Path("work").glob("[0-9][0-9][0-9]"))` dirs and steps `sorted(AGENT)`; each entry reads `<ID> <name> (not in HEAD, no <agent> log line; a cut-off run? item 077)`; it returns `("; ".join(entries) or "none", bool(entries))`. It never calls `_walk`.
   - **Step 5 `main`.** Set `uncommitted = uncommitted_steps()`. After the `REAL-DATA FIELD:` print, print `UNCOMMITTED STEP: {'not checked (no git)' if uncommitted is None else uncommitted[0]}`. In the final return expression, add `or (uncommitted and uncommitted[1])`.
   - **Step 5 module docstring.** Add an `UNCOMMITTED STEP` entry (item 077, RI-010, exit 1). It gives the rule (a step file 01-06 in the working tree that is not in `git ls-tree -r HEAD -- work/` and has no `| <agent> | <ID> |` log line, for all item numbers) and the no-git and ls-tree-failure texts. It lists the gaps: (a) a file and its log line written but not committed; (b) a modified tracked step file (e.g. a round-2 06); (c) 07 and other files outside 01-06.
2. **tests/test_pipeline_check.py.** Tests are listed below. Helper change: `_branch_adds(repo, branch, item, files, request_text=None, extra=(), bodies=None)` writes `(bodies or {}).get(f, "x\nA1 result: PASS (test)\n")`. The default is as today.
3. **tests/test_real_data_field.py.** In `test_t23_own_head_run_text`, the i3 `must` list gains `"never use the head run made for 05, whoever made it (I2 or the orchestrator), even if the same-inputs check passes;"` and the run-item list gains `"never give I3 the head run made for 05, even when the same-inputs check passes,"`. Existing strings are kept and there are no new ids. Add 4 ids to `test_t12_fences_and_headings`.
4. **.claude/agents/a1-auditor.md** (RULE_PATHS: needs the person's OK), job B:
   - In the check_pipeline bullet, after "every `LOG TIME:` entry (a log line timed after its commit)", insert ", and every `UNCOMMITTED STEP:` entry (a step file neither committed nor logged: a cut-off run; finish or redo that step, item 077)". "is an error" then covers it.
   - In the open-PR bullet, after the `BRANCH SKIPPED:` clause, insert "and every `BRANCH FAIL:` line (an open-branch item at I3 FAIL or A1 FAIL, item 077; information, not an error: the branch's team is still working, so note it with the branch's age)".

## Tests and checks
New and changed tests (tests/test_pipeline_check.py unless named):
- **Step 1.** The t23 strings above. Mutations, each run on a scratch copy:
  - i3 `even if the same-inputs check passes` -> `unless the same-inputs check passes` fails t23[i3];
  - `never use` -> `you may use` fails t23[i3];
  - run-item `even when` -> `unless` fails t23[run-item];
  - `never give` -> `you may give` fails t23[run-item].
  The count stays 3 passed.
- **Step 2.**
  - BF1 `test_branch_i3_fail_is_listed`: branch `i3fail`, item 181, ALL[:6], `bodies={"06-verification.md": "Verdict: FAIL (round 1)\nSent back to: I2\nx\n"}`. Want `BRANCH FAIL: 181 (origin/i3fail: I3 FAIL; FULL; sent back to I2, needs a later PASS round in 06 (item 071))` and `code == 0`.
  - BF2 `test_branch_a1_fail_is_listed`: branch `a1fail`, item 182, ALL, 07 body `x\nA1 result: FAIL (test)\n`. Want `BRANCH FAIL: 182 (origin/a1fail: A1 FAIL; FULL; sent back, needs a later A1 PASS line (item 042))` and exit 0. The branch's 06 has no `Verdict:` line, so this also pins "06 verdict unreadable on a branch: no I3 FAIL".
  - BF3 `test_branch_skipped_wins_over_branch_fail`: item 183, request `# Work item 183\nScope: RESEARCH ONLY\nDate: 2026-10-31\n`, files 01 02 03 07 (07 `x\nA1 result: FAIL (test)\n`), `extra=("ccbot/x.py",)`. Want `BRANCH SKIPPED: 183 (` and `BRANCH FAIL: 183` not in out.
  - The existing `test_open_branch_item_that_skips_steps_is_reported` gains `"BRANCH FAIL: 060" not in out` and `"BRANCH FAIL: 040" not in out`.
  - T8 `test_i3_fail_with_more_steps_on_branch_is_in_pr` keeps every assertion and adds `"BRANCH FAIL: 177 (origin/fix: I3 FAIL; " in out`.
  - Mutations: keep only SKIPPED fails BF1 and BF2. A BRANCH FAIL term in the exit expression fails BF1/BF2 (`code == 0`). Dropping the `skipped` filter fails BF3.
- **Step 3.**
  - T-P3 `test_i3_fail_after_a1_pass_is_a_new_item`: `_item(tmp, "180", ALL, verdict="FAIL")` (default 07 `A1 result: PASS (test)`) and `_item(tmp, "185", ALL, verdict="FAIL", a1="A1 result: FAIL (r1)\nA1 result: PASS (r2)")`. Want `180: I3 FAIL (FULL; sent back to I2; 06 FAIL after A1 PASS in 07: a follow-up to a completed item is a new item (run-item, items 053, 077))` and the same detail for 185, `I3 FAIL: 180, 185`, exit 1, and `needs a later PASS round` not on either line.
  - T-P3b `test_i3_fail_with_no_a1_line_keeps_old_detail`: `_item(tmp, "184", ALL, verdict="FAIL", a1=None)` and `_item(tmp, "017", ALL, verdict="FAIL", a1=None)`. Both want `<ID>: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))`.
  - T5 `test_i3_fail_beats_older_a1_fail` adds `"174: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))" in out` (change 2).
  - T6 is unchanged (no 07, old detail). The 053 `_open_at` tests stay green.
  - Mutations: drop the new branch fails T-P3. `if a1:` fails T5. `a1[0]` fails T-P3 (185). `_open_at` keeping its own regex is a refactor-only change. I2 checks it with a Grep for the regex text `A1 result:\s*(\w+)`: exactly 1 hit, inside `_a1_results`. Docstring mentions of "A1 result:" do not count. The hit is pasted in 05.
- **Step 4.**
  - `test_i3_verdict_reader` (T4) new ids, with the old ids unchanged:
    - `tilde` `~~~\nVerdict: FAIL (pasted)\n~~~\nVerdict: PASS (round 1)\n` -> ("PASS", None);
    - `longer` "````\n```\nVerdict: FAIL (pasted)\n````\nVerdict: PASS (round 1)\n" -> ("PASS", None);
    - `4-space` `    ```\nVerdict: PASS (round 1)\n    ```\n` -> ("PASS", None);
    - `tab` `\t```\nVerdict: PASS (round 1)\n` -> ("PASS", None);
    - `info` "```\n```py\nVerdict: FAIL (pasted)\n```\nVerdict: PASS (round 1)\n" -> ("PASS", None);
    - `4-space-close` "```\nVerdict: FAIL (pasted)\n    ```\nVerdict: FAIL (inside)\n```\nVerdict: PASS (round 1)\n" -> ("PASS", None);
    - `backtick-info` "```x`y\nVerdict: PASS (round 1)\n" -> ("PASS", None);
    - `tilde-info` "~~~x`y\nVerdict: FAIL (pasted)\n~~~\nVerdict: PASS (round 1)\n" -> ("PASS", None);
    - `mixed` "~~~\nVerdict: FAIL (pasted)\n```\nVerdict: FAIL (inside)\n~~~\nVerdict: PASS (round 1)\n" -> ("PASS", None).
  - `test_t12_fences_and_headings` new ids (tests/test_real_data_field.py), as traced in 03 Self-check rows 9-12:
    - `tilde` and `longer` -> None;
    - `4-space` -> `05 Real-data effect has no diff_reports TOTAL line (`;
    - `info` -> None.
  - Mutations, each failing the named ids:
    - any-length closer: T4/t12 `longer`;
    - `~` dropped: T4/t12 `tilde`, T4 `mixed`;
    - `lstrip()` for the opener: T4 `4-space`, `tab`, t12 `4-space`;
    - `\s{0,3}`: T4 `tab`;
    - closer allows trailing text: T4/t12 `info`;
    - closer uses `lstrip()`: T4 `4-space-close`;
    - backtick-info rule dropped: T4 `backtick-info`;
    - backtick-info rule applied to `~`: T4 `tilde-info`;
    - closer accepts either char: T4 `mixed`;
    - `i3_verdict` keeps its old loop: the new T4 ids;
    - `_field_gap` keeps its old loop: the new t12 ids.
    The FOR 3a rule (unclosed only when the section runs to EOF) is kept by the existing `fenced-heading` and `unclosed` ids (03 Self-check row 13).
  - Real tree: I2 pastes the full `check_pipeline.py` output before and after step 4 in 05. They must be identical. The grep from change 5 and the scratch old-vs-new comparison must give 75 of 75 files with the same result.
- **Step 5.** All on a git fixture (`_history` unless named), `--untracked-from <cutoff>`, `--today 2026-11-11`:
  - P5a `_item(repo, "151", ["01-research.md"], logged=False)`: `UNCOMMITTED STEP: 151 01-research.md (not in HEAD, no R1 log line; a cut-off run? item 077)`, exit 1.
  - P5b uses a plain repo with no logs/ folder (`git init -b main`, `config/x.json`, commit = cutoff). `_item(repo, "040", ["01-research.md"], logged=False)`: listed, `INCOMPLETE: none`, exit 1. This kills both the exit-term mutation and a CHECKLIST_FROM cutoff, and pins "no logs folder -> listed".
  - P5c uncommitted `_item(repo, "152", ALL[:6])` (logged): `UNCOMMITTED STEP: none`, `INCOMPLETE: none`, exit 0.
  - P5d `_item(repo, "153", ["01-research.md"], logged=False)` then `_commit`: `INCOMPLETE: 153 (no log line for R1)` and `UNCOMMITTED STEP: none`.
  - P5e like P5a, then `git add work/151/01-research.md` (not committed): still listed.
  - P5f `_history` plus a commit, then `git clone -q --depth 1 file://<repo> clone`, asserting `--is-shallow-repository` == `true`. In the clone: `_item(clone, "152", ALL[:6])` gives `UNCOMMITTED STEP: none` and exit 0 (cutoff not in the shallow clone gives UNTRACKED CHANGE "not checked", exit unchanged, as the existing shallow test). Then `_item(clone, "151", ["01-research.md"], logged=False)` gives the P5a line.
  - P5g non-git tmp dir: `UNCOMMITTED STEP: not checked (no git)`.
  - P5h `git init -q -b main` with no commit and `_item(repo, "154", ["01-research.md"])`: `UNCOMMITTED STEP: git ls-tree HEAD failed (item 077)`, exit 1.
  - `test_head_run_ignores_uncommitted_item` adds: the tree run has `UNCOMMITTED STEP: 151 01-research.md (` and the head run has `UNCOMMITTED STEP: none`.
  - `test_repo_pipeline_has_no_skipped_items` adds `"UNCOMMITTED STEP: none" in out`.
  - Mutations, each failing the named test:
    - no HEAD test: P5d;
    - no log test: P5c;
    - CHECKLIST_FROM cutoff: P5b;
    - porcelain `??` only, or HEAD replaced by the index (`ls-files`): P5e;
    - no `or uncommitted` in exit: P5b;
    - ls-tree failure read as an empty set or as `none`: P5h.
- **Step 6 (A1 text).** `test_a1_text_names_077_lines`: a1-auditor.md contains "`UNCOMMITTED STEP:` entry" and "`BRANCH FAIL:` line". Mutation: either clause removed fails it.
- **Full suite** after each of steps 1-5, and the mutations one at a time in a scratch worktree under /tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/077-I2/ (never in the repo, RI-009). Existing git tests that write step files outside `_item` and leave them uncommitted with no log line would now print an UNCOMMITTED STEP entry. I2 reports any such new failure in 05 and fixes the fixture (commit or log it), never the check.
- **Real tree:** `python3 scripts/check_pipeline.py` before and after the whole build. The output may differ only by the new `UNCOMMITTED STEP:` line (expected `none`) and any `BRANCH FAIL:` lines (I2 pastes their count). The exit code must match.
- **Python 3.10:** `python3.11 -m py_compile scripts/check_pipeline.py` where available (RI-008). There are no possessive quantifiers or 3.12 f-strings.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| D1 / step 1: one contiguous clause per file in t23 | Files 3; Tests step 1 (4 mutations) |
| D2 / step 2: BRANCH FAIL for I3 FAIL / A1 FAIL, exit unchanged, SKIPPED wins | Files 1 step 2; BF1-BF3, T8, L293 test |
| D2 docstring entry, gap (x) removed | Files 1 step 2 docstring; "Three more lines" (change 7) |
| D3 / step 3: option B detail, `_a1_results` shared | Files 1 step 3; T-P3, T-P3b, T5 (change 2) |
| D3 docstring gap (w) replaced | Files 1 step 3 docstring, with the PRE_A1_LINE wording corrected (change 3) |
| D4 / step 4: `_md_lines`, FENCE_OPEN, both callers, docstrings, known gaps | Files 1 step 4; T4 9 ids, t12 4 ids (change 4) |
| D4 message "unclosed ``` fence" unchanged | Files 1 step 4; t12 `unclosed` |
| D5 / step 5: `uncommitted_steps`, `_log_text`, `_logged`, exit 1, no-git text | Files 1 step 5; P5a-P5h |
| Step 6: suite per step, scratch mutations, real-tree before/after | Tests: Full suite, Real tree |
| Exact rules: `_md_lines` | Files 1 step 4 (as written) |
| Exact rules: `uncommitted_steps` | Files 1 step 5 (as written) |
| Overlap: 076 LOG_FORMAT, 079 `_walk`, 075 test file | Build-order paragraph; no `_walk` call |
| Correction F11 (T8 gets the D3 detail) | T8 adds `BRANCH FAIL: 177 (origin/fix: I3 FAIL; ` |
| Correction F28 / Numbers (0 at line start, 16 inline) | Change 5 grep plus scratch comparison |
| Correction F39 (shallow is a required test) | P5f with the shallow assert (change 6a) |
| Correction RI-010 wording (point 5 is the first commit-state check) | Docstring entry only; no code depends on it |
| Correction FOR 3a (unclosed only in the for-else) | Files 1 step 4 `_field_gap`; t12 `fenced-heading`, `unclosed` |
| Correction FOR 3b / H5 (no `--full-tree`) | Files 1 step 5 |
| Correction AGAINST 1 (literal ` {0,3}`, tab not a fence, §2.2) | FENCE_OPEN; T4 `tab` |
| Correction H2 (062 merge can add an A1 FAIL item to `skipped`) | Files 1 step 2 filter; BF3 |
| Missing input: no git (steps 2, 5) | P5g; existing no-git tests (`OPEN BRANCHES` absent) |
| Missing input: ls-tree fails | P5h (change 6b) |
| Missing input: logs folder absent | P5b (change 6c) |
| Missing input: 07 absent (step 3) | T6 (ALL[:6]) |
| Missing input: 07 without `A1 result:` | T-P3b item 184 |
| Missing input: branch `git show` fails | DROPPED test: the existing behaviour (empty file) is unchanged by 077 and making `git show` fail on a listed path needs a corrupted object store; written as a docstring gap |
| Missing input: branch 06 verdict unreadable | BF2 (06 with no `Verdict:` line, no I3 FAIL) |
| Missing input: fence never closed | T4 existing unclosed id; t12 `unclosed` |
| Missing input: PRE_A1_LINE/LEGACY with 06 FAIL | T-P3b item 017; docstring gap (change 3) |
| A1 duty for the new lines (not in 03) | Files 4; `test_a1_text_names_077_lines` (change 1) |
| Rule the person follows (001 slack, tolerance, cap) | None changed. The process texts (a1-auditor.md, check_pipeline docstring) go to the person in PR review |

## Guardrail tests
- Feasibility: these are error detectors, not candidate filters. The healthy real count is 0, and each rule's non-zero count comes from dated fixtures.
  - Fence rule: 548 fence lines in 75 work/*/05 and 06 files (03, Grep 2026-11-19), all of which must read the same. Pinned by the before/after whole-output diff and the scratch 75-file old-vs-new comparison (change 5). In fixtures: T4 +9 ids, t12 +4 ids.
  - Step 3 rule: 0 real items today (03 F18). Fixtures: T-P3 (2 items), T-P3b (2).
  - BRANCH FAIL: the real count is measured by I2 on the real tree. Fixtures: BF1, BF2, T8 (1 line each).
  - UNCOMMITTED STEP: 0 expected on the real tree (pasted by I2). Fixtures: P5a, P5b, P5e, P5f, P5h.
  - t23 clauses: 1 of 1 hit each (Grep 2026-11-19, i3-verifier.md and run-item.md).
- Missing inputs:
  - no git -> P5g;
  - ls-tree fails -> P5h;
  - no logs folder -> P5b;
  - 07 absent -> T6;
  - 07 with no A1 line -> T-P3b (184);
  - branch 06 unreadable -> BF2;
  - unclosed fence -> T4/t12 existing ids;
  - PRE_A1_LINE item -> T-P3b (017);
  - branch `git show` failure -> DROPPED (see Rule trace).

## Expected result
- t23 fails if either person's-choice clause is weakened. It stays at 3 ids.
- `check_pipeline.py` prints `BRANCH FAIL: <ID> (<ref>: I3 FAIL|A1 FAIL; <detail>)` for open-branch items in those states, never for a BRANCH SKIPPED item. The exit code is unchanged.
- A 06 FAIL whose 07 ends in A1 PASS is I3 FAIL with the "follow-up to a completed item is a new item" detail. classify and `_open_at` share one A1 reader.
- `i3_verdict` and `_field_gap` share `_md_lines` (CommonMark §4.5 fences, ``` and ~~~). The real tree's output is unchanged by it.
- `UNCOMMITTED STEP:` lists step files that are neither committed nor logged (exit 1), says `not checked (no git)` without git, and never says `none` when ls-tree fails.
- a1-auditor.md names both new lines.
- The full suite is green, each mutation fails its named test, and the real-tree check exit code is the same as before.

Notes for later items:
- 078 edits a different paragraph of a1-auditor.md (probe_guardrails runtime). Re-read it after 077's clauses.
- 079 changes `_walk` and main's walk handling. `uncommitted_steps` is independent of it. 079's shallow fixture may now also print `UNCOMMITTED STEP:`, which must be `none` there if its files are committed.

Recurring issues checked:
- RI-001 (ESCALATED and GUARDED wording; listed by 03 as ESCALATED): no trading filter or window. Every count is dated (2 clause hits, 548/75 fence lines, 0 06-FAIL+A1-PASS items), and the error-detector rules get non-zero fixture counts (Guardrail tests).
- RI-014 (OPEN): nothing calls or changes `_walk`. P5f asserts shallowness rather than assuming it, and reads only the UNCOMMITTED STEP line and an exit code already shown stable in shallow fixtures.
- Also checked: RI-002 (ls-tree failure and missing logs are never `none`; P5h, P5b); RI-004/RI-005 (each test id traced, and two surviving mutations found, changes 2 and 4); RI-007 (SKIPPED wins; 053's new-item rule kept); RI-008 (3.10 syntax, py_compile); RI-009 (scratch worktrees only); RI-010 (A1 duty for the new lines, change 1); RI-012 (fullmatch fences, one shared A1 reader and log regex); RI-013 (whole-output diff plus a 75-file comparison for step 4).

Log fields: FIT WITH CHANGES | 4 files planned
