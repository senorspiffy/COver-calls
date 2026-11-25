# 04 Build plan - 069
Fit verdict: FIT WITH CHANGES

Fit check. No strategy number, ticker, premium, cap or broker path is touched, so the ~$3k account and 001's rules are unaffected. No rule the person follows in 001 changes (no slack, tolerance or cap), so no 001 text update is needed. The change is process only: two agent/command texts, one template, one report line in check_pipeline.py, and tests. It does not conflict with built code: `parse_request` already anchors `^Scope:` / `^Waived:` (check_pipeline.py L191-193, L179), so "> " quoting works with no code change (test viii pins it). Nothing checks `Opened by:` or `Type:` (Grep: 0 hits), so `Opened by: A1 (inbox: <key>)` and Type IDEA need no code. The changes below fix the merge with 070, a crash in the fixtures, and section bounds:

- **C1 (merge with 070).** 070's map step 5 adds a print after `RESEARCH CODE:` (L650) and adds a term to the `return 1 if ...` line (L654). git's content merge "looks for overlapping diff hunks", so edits on adjacent lines conflict (source 1). 069 must therefore leave L650 and L654 alone. It inserts its block only between `print(f"ORPHAN LOG: ...")` (L652) and `print(f"SKIPPED: ...")` (L653). An unchanged line separates it from each of 070's hunks. Its new constant goes after `LEGACY` (after L183), not next to CHECKLIST_FROM/LOG_CHECK_FROM (L136-140), where 070 adds WHOLE_DIFF_FROM. Its function goes after `next_id()` (after L562), and its docstring entry goes after the `--next-id` paragraph (after L112). 070's docstring entry goes after RESEARCH CODE (L110).
- **C2 (missing folder).** Every existing fixture runs in a tmp root that has no logs/audit/. `inbox_section()` must return "not checked (no daily report from 2026-11-18)" when the folder is missing. It must not raise. Added test (ix).
- **C3 (section bounds).** The `project-inbox:` / `hub:` lines count only between `^## Inbox` and the next `^## ` heading (anchored line regexes, RI-012). Added test (x): a well-formed `hub:` line under another heading does not satisfy the check.
- **C4 (wording).** The L20 sentence is amended to: "A1's daily commits change only logs/ and work/ markdown; the Inbox step's status lines and moves are on /mnt/project-files, outside the repo, and are listed in the report (item 069)." The status writes are not commits, so "except" would misdescribe them.
- **C5 (no clone).** A missing hub clone gives `hub: UNREAD: not reachable (no clone at <path>)`, as in Missing inputs row 2. A1 does not clone. This keeps 2b's "clone fails" wording from implying a clone step that nothing else in the map describes.

## Extra research (with sources)
1. Why the placement in C1 matters. Jeff King on git@vger, 2015-04-29: "The content-level merge in git looks for overlapping diff hunks." Edits on neighbouring lines are reported as a conflict even when they don't collide logically. https://lore.kernel.org/all/20150429023509.GB438@peff.net/T/ . So both items merge cleanly only if at least one unchanged line separates every 069 hunk from every 070 hunk.
2. Exit code without touching L654. Python `return` inside the inserted block, after printing the SKIPPED line, gives exit 1 without changing the shared return expression. The block (step 4 below) prints SKIPPED itself and then returns 1. The normal path prints it at L653 as before. Same output either way. (Python language reference, `return` statement: standard behaviour, no new dependency.)
3. Edge case R3 missed (C2). Existing fixtures have no logs/audit/. `Path.iterdir()` on a missing folder raises FileNotFoundError (Python pathlib docs, standard behaviour), so without the guard every no-git fixture test would crash.

## Files to create/change
1. `.claude/commands/daily-audit.md`: map step 1 as written in 03 (Inbox first; "IDEA" added to the run list: "new BUG, EFFICIENCY and IDEA (inbox) work items").
2. `.claude/agents/a1-auditor.md` job B: a new first bullet "Inbox (item 069), before the log review" with 2a-2d as in 03. The bullet includes C5 (no clone → UNREAD), decisions 3-5 (marker = A1's own records, never `status:`; own notes are listed and never moved, hub L21/L59 link them; only projects/covered-calls/inbox.md and shared-facts.md are read), and the 2c limits verbatim. L20 is amended per C4.
3. `templates/daily-audit.md`: map step 3. The new section goes first, after the title and before `## ESCALATED`. Heading `## Inbox (other projects asking us to test or try something; item 069)`. Lines `project-inbox: ...` and `hub: ...`. Sub-lists: New items (ID → key), FYI, Refused, Status writes.
4. `scripts/check_pipeline.py` (self-contained per C1):
   - After LEGACY: `INBOX_FROM = "2026-11-18"  # item 069: first daily report under the Inbox template`, plus `DAILY_REPORT = re.compile(r"\d{4}-\d{2}-\d{2}\.md")`, `INBOX_HEAD = re.compile(r"^## Inbox\b", re.M)`, `INBOX_PI = re.compile(r"^project-inbox:\s*(nothing new|\d+ new|UNREAD:)", re.M)`, `INBOX_HUB = re.compile(r"^hub:\s*([0-9a-f]{7,40}\b|UNREAD:)", re.M)`.
   - After `next_id()`: `def inbox_section(audit=Path("logs/audit")) -> tuple[str, bool]`. If the folder is missing, or no file name fullmatches DAILY_REPORT with a stem ≥ INBOX_FROM, it returns `("not checked (no daily report from 2026-11-18)", False)`. Otherwise it takes the newest such file by name and cuts the section from INBOX_HEAD to the next `^## `. It returns `("none", False)` or `("<file> (<missing parts joined by '; '>)", True)`. The missing parts are "no ## Inbox", "no project-inbox: line" and "no hub: SHA or UNREAD line". The annotation is `tuple[str, bool]`, which is valid on 3.10 (RI-008).
   - In main, between L652 and L653 only:
     ```
     inbox, inbox_bad = inbox_section()            # item 069
     print(f"INBOX: {inbox}")
     if inbox_bad:
         print(f"SKIPPED: {', '.join(skipped) or 'none'}")
         return 1
     ```
   - Docstring: an `INBOX (item 069, RI-010)` entry after the `--next-id` paragraph. It covers the rule, the cutoff, per-item reports being ignored, exit 1, and the known gap that the check proves the lines exist, not that A1 read the channels (I3/A1 spot-check).
5. `tests/test_pipeline_check.py`: the 11 tests in the next section. A helper `_daily(root, name, body)` writes `logs/audit/<name>`, and the runs use the existing `_run`. None of the tests needs git. Test (viii) calls `parse_request` on a fixture text (import via REPO/scripts, as other tests do, or by running the script on a fixture item).

5 files planned.

## Tests and checks
| # | Fixture | Expected |
|---|---|---|
| i | `2026-11-18.md`: `## Inbox (...)`, `project-inbox: nothing new (2 seen before)`, `hub: 116c68c, nothing new` | `INBOX: none`, exit 0 |
| i-b | same with the 40-char SHA `116c68c533cbd9d13bf3e81c1d833ab408102f84` | `INBOX: none` (7 and 40 both pass) |
| ii | `project-inbox: UNREAD: not reachable (x)`, `hub: UNREAD: not reachable (y)` | `INBOX: none`, exit 0 |
| iii | `2026-11-18.md` with no `## Inbox` | `INBOX: 2026-11-18.md (no ## Inbox...`, exit 1 |
| iv | `hub: nothing new` (no SHA, no UNREAD) | names "no hub:", exit 1 |
| v | project-inbox line missing | names "no project-inbox:", exit 1 |
| vi | valid `2026-11-18.md` + `2026-11-18-070.md` (no section) | `INBOX: none` (per-item file ignored) |
| vii | only `2026-11-17.md`, no section | `INBOX: not checked (no daily report from 2026-11-18)`, exit 0 |
| viii | request.md: `Scope: FULL` at L3; under `## Evidence`: `> Scope: FAST (person, 2026-11-18)`, `> Waived: 03 06 (person, 2026-11-18: x)` | `parse_request` → scope FULL, waived [] (pins R3-b) |
| ix | tmp root with no logs/audit/ (C2) | `INBOX: not checked (...)`, no traceback, exit unchanged |
| x | `## Inbox` with only `project-inbox:`; `hub: 116c68c` under `## Items reviewed` (C3) | names "no hub:", exit 1 |

Mutations (I3, scratch copy): `inbox_section` always returns ("none", False) → iii, iv, v, x fail. INBOX_FROM set to "2026-11-17" → vii fails. DAILY_REPORT changed to `.match` (prefix) → vi fails. Section bounds removed (whole-file search) → x fails. "> " quoting removed from the viii fixture → viii fails (proves the pin).
Suite: `python3 -m pytest -q tests/test_pipeline_check.py` passes, with base + 11 tests (I2 pastes before and after). `test_repo_pipeline_has_no_skipped_items` still passes: today there are 0 daily reports ≥ 2026-11-18, so the result is not checked. Merge probe (I2/I3, scratch copy): once 070 has built, `git merge-tree` of the 069 and 070 branches over check_pipeline.py shows no conflict. If 070 is not built yet, it is checked at A1.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 daily-audit.md | File 1 |
| Map 2 a1 bullet + L20 | File 2; L20 wording per C4 |
| Map 2a project-inbox key/new/UNREAD | File 2 (2a verbatim); worked examples in 03 Self-check; I3 reads |
| Map 2b hub range, is-ancestor, full-read fallback, missing inbox line | File 2 (2b verbatim + C5) |
| Map 2c classify by body, IDEA item, "> " evidence, dup-key check, limits, refused | File 2 (2c verbatim); test viii |
| Map 2d status writes, archive/ creation, own-note exception, never hub | File 2 (2d verbatim) |
| Map 3 template section | File 3 |
| Map 4 INBOX_FROM, inbox_section, output line, docstring, exit | File 4 (placement per C1, missing folder per C2, bounds per C3) |
| Map 5 tests i-viii | File 5 i-viii, plus i-b, ix, x |
| Decision 1 same-day FULL | File 1 (run list includes IDEA) |
| Decision 2 narrow status writes | File 2 (2d) + C4 |
| Decision 3 "new" by A1 records, not status | File 2 (2a) |
| Decision 4 own notes listed, not moved | File 2 (2d) |
| Decision 5 hub addressing by file | File 2 (2b) |
| Decision 6 UNREAD per channel | File 2, template, regexes accept `UNREAD:`; test ii |
| Decision 7 urgent first, same day | File 2 (2c: "urgent listed first") |
| Decision 8 build guardrail | Files 4, 5 |
| Correction R1-15 / R1-N2 (6 content-only hits) | File 2 (no keyword search; the "6 of 12" reason is noted in the bullet) |
| Correction R2-9 (is-ancestor exit codes) | File 2 (2b: any non-zero exit → full read) |
| Correction R2-5, R2-16 (quote/overstatement fixes) | DROPPED: research text only, nothing to build |
| Removed R1-27 (`--since`) | DROPPED: removed in 03; the plan uses a SHA range only |
| R3-a hub links to own-note path | File 2 (2d own-note exception) |
| R3-b line-anchored Scope/Waived | Test viii |
| R3-c/R3-d per-item reports; one old `## Inbox` | DAILY_REPORT fullmatch (test vi); INBOX_FROM cutoff (test vii) |

## Guardrail tests
- Feasibility: daily-report name filter (`\d{4}-\d{2}-\d{2}\.md`, 8 of 15 files 2026-11-1*, 03 Self-check) → test vi.
- Feasibility: INBOX_FROM cutoff (0 daily reports ≥ 2026-11-18 today; 2026-11-17.md would fail iv/v) → test vii + the real-repo test (`not checked`, exit 0).
- Feasibility: hub SHA regex 7..40 hex (116c68c = 7, full = 40) → tests i, i-b.
- Feasibility: project-inbox channel (2 files, 0 foreign, 2026-11-17) and hub range (0 new lines, 116c68c..116c68c) are A1 text rules, not code. They are pinned by 03's worked examples and by I3 reading them against the bullet. The first daily run (2026-11-18) must show `project-inbox: 2 new` (first run) or name both files.
- Missing inputs: logs/audit/ absent → test ix. No daily report ≥ cutoff → test vii. Channel unreachable → test ii (UNREAD accepted, never read as "nothing new"). Hub SHA absent → test iv. The A1-side absences (no previous report, missing `from:`/`priority:`, failed status write, no covered-calls hub inbox) are text rules in File 2, copied from 03's Missing inputs table, and I3 checks each row is present.

## Expected result
On the branch, `python3 scripts/check_pipeline.py` prints `INBOX: not checked (no daily report from 2026-11-18)` and the exit code is unchanged. From the 2026-11-18 daily report on, a report with no Inbox section, or one missing either channel line, gives exit 1. The daily audit reads the inbox before the log review. It opens an IDEA item (evidence quoted with "> ") for each test/try request, lists FYI and refused messages, and writes status only on /mnt/project-files. check_pipeline.py merges cleanly with 070.

Recurring issues checked (item 013): RI-001 (every code filter has a dated count and a pinning test: vi, vii, i/i-b), RI-002 ESCALATED (UNREAD is never shown as empty; missing folder → "not checked", never "none"; test ix), RI-004/RI-005 (03's worked examples re-checked against the regexes: 116c68c passes INBOX_HUB, and 2026-11-17.md's "Hub (116c68c)" does not), RI-006 (n/a, no hand totals), RI-007 (each message becomes an item; viii closes the quoted-waiver path), RI-008 (annotation valid on 3.10; no 3.12 syntax), RI-009 (`--next-id` in 2c; 070 merge per C1), RI-010 (the INBOX check is the script check for a text duty), RI-011 (n/a), RI-012 (anchored regexes, section-bounded, test x), RI-013 OPEN (n/a, no realtest output change). RI-003: n/a.

## Round 2 (after A1 FAIL)
Fit verdict: FIT WITH CHANGES. Input: logs/audit/2026-11-18-069.md "Sent back" 1-2 and probes P1/P2. The earlier sections above are kept as the round-1 record. Where they conflict with this section (INBOX_FROM, tests vii/ix wording, "None of the tests needs git", the Expected result line), this section replaces them.

### Fit check (round 2)
- A1 is right. A calendar cutoff picked on the branch judges reports written on main under main's old template. The merge date is not known when the cutoff is chosen, so no fixed date is safe. This is RI-010's 048 pattern.
- The fix stays inside 069's own code: the `INBOX_FROM` constant (L224), the `inbox_section()` body (L706-723), its docstring paragraph (L133-140), and 069's test block (tests/test_pipeline_check.py L1172-1310 plus new tests appended right after it).
- `main()` is not edited. The INBOX block at L816-820 and its return-1 stay as built, so the early-return path is unchanged.
- 070's code is not touched: TRIGGER/REAL_DATA_FIELD/TOTAL_LINE (L173-185), `real_data_field`, main L750/L775/L813/L822-823, and tests/test_real_data_field.py. 070's I2 is working in the same tree at the same time. I2 must therefore re-read check_pipeline.py and the test file just before each edit, and edit only the lines named here (RI-009).
- Not a strategy or 001 change; no rule the person follows changes.

### Decision: the check follows the template, not a date or a SHA
Rule. Take the newest daily report `logs/audit/<YYYY-MM-DD>.md` (DAILY_REPORT fullmatch, any date). Check it only if it was written under a template that has the Inbox section:
- **Committed report.** Find the commit that last added it: `git log --no-renames --diff-filter=A --format=%H -1 -- logs/audit/<name>`. The report is checked only if `templates/daily-audit.md` at that commit (`git show <sha>:templates/daily-audit.md`) matches `INBOX_HEAD`. Otherwise the result is `not checked (<name> added in <sha7>; its templates/daily-audit.md has no ## Inbox)`, exit 0.
- **Uncommitted report** (log output empty, or HEAD has no commit yet). Judge it by the working-tree `templates/daily-audit.md`, the template the writer has in front of them. If that has no `## Inbox`, or the file is missing: `not checked (<name> not committed; its templates/daily-audit.md has no ## Inbox)`, exit 0.

Why this rule cannot break main, whatever the merge date:
- Every report written on main before the merge was added by a main commit, and main's template at that commit has no `## Inbox`. So P1 gives `not checked`, exit 0, on any date. The same holds if the old report is later edited (A1 appends a note), because the adding commit stays the same. Test xiv-b pins this.
- Every report written after the template reaches a branch is added by a commit whose template has `## Inbox`. So it is checked from its first day, with no hand edit at merge time (A1's option (b) problem).
- It needs no recorded SHA. A1's ancestry option would record the template commit (8dc2c2d) and test `merge-base --is-ancestor`. That is sound under run-item's merge-commit rule, but the SHA is stale after any squash or rebase. UNTRACKED_FROM already has that failure mode ("squash/rebase or wrong SHA", L526). The template content at the adding commit survives a squash: a squash commit carries the new template, and reports added on main before it keep their old adding commit.
- It is the same idea as CHECKLIST_FROM, LOG_CHECK_FROM and WHOLE_DIFF_FROM (the rule applies from where it exists), keyed to the file that defines the rule.

How git finds the adding commit (research):
- `--diff-filter=A` selects "files that are Added (A)" (git-diff docs, https://git-scm.com/docs/git-diff).
- Default history simplification: "If the commit was a merge, and it was TREESAME to one parent, follow only that parent" (git-log docs, History Simplification, https://git-scm.com/docs/git-log). So after main is merged into a branch, or the branch into main, the log follows the side that already had the report and returns main's original adding commit, not the merge.
- `--no-renames` makes a renamed report count as added at its new path. With a single pathspec the old path is outside the diff, so this mostly restates the default. It is kept so the result does not depend on `diff.renames`. No test is planned for it.

Missing inputs. Each case returns `not checked`, never `none` (RI-002), except a real git error:

| Case | INBOX line | exit | Test |
|---|---|---|---|
| no logs/audit/ or no daily report | `not checked (no daily report)` | 0 | ix (wording updated), xvii-b |
| no git / cwd not the work-tree top (`_git` → None) | `not checked (no git)` | 0 | xvii |
| shallow clone (`rev-parse --is-shallow-repository` = true) | `not checked (shallow clone; run git fetch --unshallow)`, as in `_walk` L522-525 | 0 | xviii |
| `git log` exits non-zero in a repo with a HEAD | `<name> (git log failed)` (same as 070's convention) | 1 | xix |
| template absent at the adding commit | `not checked (<name> added in <sha7>; its templates/daily-audit.md has no ## Inbox)` | 0 | xx |
| uncommitted report, working template without Inbox (or missing) | `not checked (<name> not committed; ...)` | 0 | xv-c |
| repo with no commits, uncommitted report, working template with Inbox | checked by content | per content | xxi |

The shallow case matters: in a depth-1 clone every file looks "added" in the boundary commit, whose template has Inbox. Old reports would then be checked and fail, which is the P1 failure again. So the shallow case returns `not checked`.

### R2-1 Changes to scripts/check_pipeline.py (069's lines only)
1. L224: delete `INBOX_FROM = "2026-11-18" ...`. Add `INBOX_TEMPLATE = "templates/daily-audit.md"  # item 069 round 2: a daily report is checked only if written under this template with ## Inbox (never a date)`. DAILY_REPORT, INBOX_HEAD, INBOX_PI and INBOX_HUB are unchanged.
2. New helper `_inbox_gate(path: Path) -> tuple[str, bool] | None`, placed directly above `inbox_section`. It returns None when the report is checked, else the `(text, failed)` from the table above. `X | None` is a runtime annotation and is valid on 3.10 (PEP 604; RI-008). If I2 prefers, use `Optional[...]` or no annotation. Order of steps:
   1. `_git("rev-parse", "--is-shallow-repository")`. If this is None → `("not checked (no git)", False)`. If it is `true` → the shallow tuple.
   2. `head = _git("rev-parse", "--verify", "-q", "HEAD")`. If its exit is 0, run the `git log` above; a non-zero log exit → `(f"{path.name} (git log failed)", True)`; `sha = out.strip()`. If HEAD does not verify, `sha = ""`.
   3. If `sha` is set: `tpl = _git("show", f"{sha}:{INBOX_TEMPLATE}")`; `ok = tpl[1] == 0 and INBOX_HEAD.search(tpl[0])`; `where = f"added in {sha[:7]}"`.
   4. Otherwise, read the working-tree `Path(INBOX_TEMPLATE)` if it is a file; `where = "not committed"`.
   5. Return None if `ok`, else `(f"not checked ({path.name} {where}; its {INBOX_TEMPLATE} has no ## Inbox)", False)`.
   The path given to git is `path.as_posix()`, relative to the cwd. `_git` already returns None unless the cwd is the work-tree top.
3. `inbox_section`:
   - Drop the `p.stem >= INBOX_FROM` term. No report → `("not checked (no daily report)", False)`.
   - After picking `newest`, `gate = _inbox_gate(newest)`; `if gate: return gate`. The content checks below it are unchanged.
   - Update its docstring: newest daily report, gate, never `none` when unchecked.
4. Module docstring L133-140: replace "dated on or after INBOX_FROM (the first report under the Inbox template)" with the template rule (adding commit's `templates/daily-audit.md`; uncommitted → working tree; no git / shallow → not checked; git log failure → exit 1). Add known gaps:
   - (u) a report written but not committed before a pull that brings the new template is judged by the new template. Commit the daily report before pulling.
   - (v) removing `## Inbox` from the template later switches the check off for reports added after that. This is intended: the rule follows the template.

### R2-2 Changes to tests/test_pipeline_check.py (069 block only)
Helper changes, so the existing tests i-vi and x-xiii now run in a git fixture:
- `_daily(root, name, body, template=INBOX_TPL, commit=True, git=True)`.
  - With `git=True`, the first call runs `git init -q -b main` (test `_git`, which isolates config). xvii passes `git=False`.
  - It writes `templates/daily-audit.md` = `template` if given; INBOX_TPL is `"# Daily audit\n## Inbox (x)\nproject-inbox: <fill in>\nhub: <fill in>\n"`.
  - It writes the report and, if `git and commit`, runs `_commit(root)`.
- `_inbox(root)` passes `--untracked-from <HEAD sha>` (via `_commit_sha`) when the root is a repo with a commit, so the walk is empty and UNTRACKED CHANGE / RESEARCH CODE / REAL-DATA FIELD stay `none`. A templates/ commit after the cutoff would otherwise be an UNTRACKED CHANGE (CODE_PATHS includes templates/).
- All git tests get `@pytest.mark.skipif(shutil.which("git") is None, ...)`. viii, ix and xvii need no git. Every new test name contains `inbox`, so `-k inbox` selects it.
- I2 confirms that i, ii and vi still give exit 0 in the git fixture, with the whole output pasted.

Updated tests:
| # | Fixture | Expected |
|---|---|---|
| vii (rewritten) | c1: template without `## Inbox` + `2026-11-17.md` (its real shape: `## Inbox` prose, "Hub (116c68c)") | `INBOX: not checked (2026-11-17.md added in <sha7>; its templates/daily-audit.md has no ## Inbox)`, exit 0 |
| ix (wording) | no logs/audit/ | `INBOX: not checked (no daily report)`, exit 0 |

New tests:
| # | Fixture | Expected | Pins |
|---|---|---|---|
| xiv (P1, A1 send-back 1) | c1 old template (no `## Inbox`); c2 adds `2026-11-25.md` = old-format text (copy of the 2026-11-17 shape; dated a week after 11-18 to show the date is irrelevant); c3 changes the template to INBOX_TPL (the merge) | `INBOX: not checked (2026-11-25.md added in <c2 sha7>; ...)`, exit 0 | gate uses the adding commit, not HEAD |
| xiv-b | xiv plus c4, which edits 2026-11-25.md (appends a line) | still `not checked (... added in <c2 sha7> ...)`, exit 0 | `--diff-filter=A` (an old report edited after the merge stays unchecked) |
| xiv-c | xiv's history via a real merge: old-format report committed on branch `main`, template change on branch `t`, then `git merge --no-ff` of each into the other (both orders) | `not checked (... added in <report commit sha7> ...)`, exit 0 | history simplification through merges (git-log doc quote) |
| xv (A1 send-back 1, second test) | xiv history, then c4 adds `2026-11-26.md` in the new format with no `hub:` line | `INBOX: 2026-11-26.md (no hub: SHA or UNREAD line)`, exit 1 | new-format reports are still checked |
| xv-b | as xv but `2026-11-26.md` left uncommitted; the working template has Inbox | same failure, exit 1 | uncommitted → working template |
| xv-c | uncommitted `2026-11-26.md` with a working template without `## Inbox` | `not checked (2026-11-26.md not committed; ...)`, exit 0 | uncommitted absent case |
| xvi (P2, A1 send-back 2) | parametrized `hub:` values `116c68, nothing new` (6 hex), `2026-11-18, nothing new` (a date), and a 41-hex string (`116c68c533cbd9d13bf3e81c1d833ab408102f84a`) | each `INBOX: 2026-11-18.md (no hub: SHA or UNREAD line)`, exit 1 | `{7,40}` lower bound (m10 `{1,40}` → the 6-hex and date cases pass → test fails) and upper bound (`{7,}` → the 41-hex case fails the test) |
| xvii | tmp root with no git (`_daily(..., git=False)`), well-formed report | `INBOX: not checked (no git)`, exit 0 | no-git absent case |
| xvii-b | git repo with logs/audit/ holding only per-item reports | `INBOX: not checked (no daily report)`, exit 0 | |
| xviii | xiv history, then `git clone -q --depth 1 file://<repo> <clone>`; run in the clone | `INBOX: not checked (shallow clone; run git fetch --unshallow)`, exit 0 | shallow guard (without it, the boundary commit carries the new template and the old report fails) |
| xix | unit: `monkeypatch.chdir(repo)`, `cp._git` patched to return `("", 128)` for `log` | `cp.inbox_section()` == `("2026-11-18.md (git log failed)", True)` | git error is not hidden |
| xx | c1 adds `2026-11-18.md` (old format) with no templates/ at all; c2 adds INBOX_TPL | `not checked (2026-11-18.md added in <c1 sha7>; ...)`, exit 0 | template absent at the adding commit |
| xxi | unit (`monkeypatch.chdir`, `cp.inbox_section()`): `git init` with no commit; working INBOX_TPL; uncommitted new-format report with both lines. Unit level because with no HEAD the item-053 walk reports its cutoff missing, which is not this test's concern | `("none", False)` | no-HEAD path does not crash and is checked |

Test count: base 14 inbox cases (with i-b) + xiv, xiv-b, xiv-c (2 params), xv, xv-b, xv-c, xvi (3 params), xvii, xvii-b, xviii, xix, xx, xxi = 14 + 16 = 30 `-k inbox` cases. I2 pastes before and after counts and the whole suite.

### Mutations (I3, each in its own scratch copy; `-k inbox`)
| Mutation | Must fail |
|---|---|
| m10 hub `{7,40}` → `{1,40}` (A1's) | xvi[6-hex], xvi[date] |
| hub `{7,40}` → `{7,}` | xvi[41-hex] |
| `_inbox_gate` always returns None (every report checked, no date) | vii, xiv, xiv-b, xiv-c, xv-c, xvii, xviii, xx |
| `_inbox_gate` always returns not checked | i, i-b, ii, iii, iv, v, vi, x, xi, xii, xiii, xv, xv-b, xvi, xxi |
| gate reads `HEAD:templates/daily-audit.md` instead of `<sha>:` | xiv, xiv-b, xiv-c, xx |
| `--diff-filter=A` removed (last commit touching the report) | xiv-b |
| shallow guard removed | xviii |
| git-log failure returned as `(..., False)` or as not checked | xix |
| P1 replay at the round-1 code (dc162cf's `inbox_section`) | xiv (shows the new test catches A1's FAIL) |

### Probes (I2 in 05, re-run by I3 in 06; scratch clones only, never the real tree)
1. Real repo on the branch: paste `git log --no-renames --diff-filter=A --format='%h %cI' -1 -- logs/audit/2026-11-17.md` and `git log --format='%h %cI' -- templates/daily-audit.md`. Expected: 2026-11-17.md was added before 8dc2c2d (R1 read it before 1fb7f6a), so `python3 scripts/check_pipeline.py` prints `INBOX: not checked (2026-11-17.md added in <sha7>; its templates/daily-audit.md has no ## Inbox)` and the exit code is unchanged. Dated count for the gate (RI-001): of the 8 daily reports 2026-11-10 to 2026-11-17, 0 were added under an Inbox template. I2 confirms this with the same log command for each.
2. A1's P1, replayed as a real merge. In a scratch clone, check out origin/main and commit `logs/audit/2026-11-18.md` = a copy of 2026-11-17.md. Then:
   - `git merge --no-ff <branch tip>`, run check_pipeline → `INBOX: not checked (2026-11-18.md added in ...)`, exit 0. Round-1 code gave exit=1 here.
   - Repeat with `git merge --squash` + commit → same.
   - Then add an unfilled `2026-11-19.md` from the merged template → exit 1.
3. Merge with 070. Once 070's rework commits, run `git diff` over check_pipeline.py and confirm that no 070 line changed in 069's commit (`git diff -U0 <before> <069 commit> -- scripts/check_pipeline.py` touches only L133-140, L224 and the inbox_section region).

### Expected result (round 2)
- On the branch: `INBOX: not checked (2026-11-17.md added in <sha7>; its templates/daily-audit.md has no ## Inbox)`, exit 0.
- After the merge, on any date: every report written on main before the merge stays `not checked`. The first daily report added under the new template is checked, and a missing or unfilled line gives exit 1.
- No date or SHA needs editing at merge time.
- 07's expected INBOX line (L5) changes to the line above. I3/A1 update it in their round.
- 2 files planned: scripts/check_pipeline.py, tests/test_pipeline_check.py. No agent, command or template text changes. a1-auditor.md and daily-audit.md never named the date (Grep `2026-11-18|cutoff` over .claude/: only run-item.md L16, unrelated).

### Rule trace (round 2)
| Round-2 rule | Plan line, or DROPPED: <reason> |
|---|---|
| A1 send-back 1: cutoff follows the template, not the calendar | R2-1 items 1-4; tests vii, xiv, xiv-b, xiv-c, xx; probe 2 |
| A1 send-back 1: old-format report dated after the cutoff date, written before the template → not checked, exit 0 | test xiv (2026-11-25.md), probe 2 |
| A1 send-back 1: a new-format report still fails when a line is missing | tests xv, xv-b |
| A1 send-back 2: pin the SHA lower bound; m10 fails | test xvi; mutation m10 |
| Missing-data policy for each new optional input (git, history depth, adding commit, template at that commit, working template) | Missing inputs table; tests xv-c, xvii, xvii-b, xviii, xix, xx, xxi |
| A1 EFFICIENCY suggestion (orchestrator-run `--log`) | DROPPED: A1 left it to the daily review; not part of 069 |
| A1 RI-010 occurrence record | DROPPED: the daily review records it in logs/recurring-issues.md (fix branches don't edit it, item 036) |

Recurring issues checked (item 013, round 2):
- RI-010 GUARDED, likely ESCALATED after the daily review. This round is the fix: the check is keyed to the rule's own file at the report's adding commit, so work done on main under the old rules is never judged by the new rule. Pinned by xiv, xiv-b and xiv-c and by probe 2.
- RI-001 ESCALATED. The gate is a filter. It has a dated count (0 of 8 daily reports from 11-10 to 11-17 added under an Inbox template; probe 1) and pinning tests (xiv, xv). The SHA bound has negative tests on both sides (xvi).
- RI-002 ESCALATED. No git, a shallow clone, or no report gives `not checked`, never `none`. A git error gives exit 1 (xix). An uncommitted report is never silently skipped (xv-b).
- RI-008: no syntax beyond 3.10. I3 runs py_compile on 3.11.
- RI-009: 070's rework runs in the same tree. The edits are limited to named lines, with a re-read before each edit (probe 3).
- RI-011: no merge-base is used. Path-limited log through merges is pinned by xiv-c.
- RI-012: INBOX_HEAD (anchored) is reused on the template text, so a mid-line "## Inbox" in a template doesn't count.
- RI-007: no step is skipped (back to I2 then I3).
- RI-013 OPEN, RI-003/004/005/006: n/a (no realtest output, no example numbers or hand totals change).
