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
