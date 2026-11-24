#!/usr/bin/env python3
"""Check that every work item's step files match its Scope (items 026, 029, 034; RI-007, RI-009).

Usage: python3 scripts/check_pipeline.py [--today YYYY-MM-DD] [--untracked-from SHA]   (run from the repo root;
       --untracked-from is for tests only; the daily run uses the item-053 constant UNTRACKED_FROM)
       python3 scripts/check_pipeline.py --log <agent> <ID> "<fields>"   (item 045)
       python3 scripts/check_pipeline.py --next-id   (the ID to give a new work item, item 037)

Required step files by `Scope:` in request.md (no Scope line = FULL):
  FULL           01 02 03 04 05 06 07
  RESEARCH ONLY  01 02 03 07
  FAST           01 03 05 06 07   (the person asked to go faster: R2 and I1 may be skipped,
                                    never R3's fact check or I3's verification)
FAST counts only as `Scope: FAST (person, YYYY-MM-DD)`: the person asked for it. Any other
FAST line (no who, or another who) makes the item SKIPPED (item 042).
A `Waived: <steps> (<who>, <date>: <why>)` line in request.md excuses those steps; it is
printed every run so it stays visible. 03 (fact check) and 06 (verification) can be waived
only by the person: <who> must be `person`, otherwise the item is SKIPPED (item 031).

Each item is one of:
  SKIPPED      a later required step exists while an earlier one is missing, or another
               file (a result for the person, e.g. screen-summary.md) exists before
               the fact check 03 (exit 1)
  STUCK        only request.md, and its Date is at least 1 day before --today
  not started  only request.md, opened today
  in progress  the required steps present so far have no gap
  awaiting A1  every required step is present, but 07-audit-task.md has no `A1 result:` line
               (every item except the closed PRE_A1_LINE list; items 033, 035). Listed, not an error.
  IN PR        stuck, not started, in progress or I3 FAIL here, but an unmerged remote branch has more of
               its step files (item 034). Listed, not an error: it waits for the person's merge.
  A1 FAIL      every required step is present and the last `A1 result:` line is FAIL (item 042):
               the item went back to the team and is not complete until a later PASS line (exit 1)
  I3 FAIL      06's verdict line (its first `Verdict:` line outside code fences; templates/verification.md
               L2) is FAIL (item 071): I3 sent the item back to the step on 06's first `Sent back to:`
               line (I1, I2 or I1 I2; else `sent back to: not stated`, never a default). Checked before
               A1's result: a FAIL in 06 means the current build has not passed I3. Not complete until a
               later round rewrites that line to PASS (exit 1).
  complete     every required step is present and A1's last result is PASS
Items in LEGACY are older than this check and are reported as such.
INCOMPLETE (item 043, exit 1): for items from CHECKLIST_FROM on, a 06 with no
`Recurring issues checked:` line naming an RI-, or a step file whose agent wrote no
`| <agent> | <ID> |` line in logs/research or logs/implementation.
Item 071: from VERDICT_FROM on, a 06 whose verdict line is missing or unreadable (only `PASS` or
`FAIL`, case-sensitive, optionally **bold**; the unfilled `PASS | FAIL` is unreadable), or a FAIL
with no `Sent back to: I1|I2|I1 I2` line, or a PASS with no `Sent back to: none` line (a stale
field), is INCOMPLETE. From CHECKLIST_FROM on, a readable verdict that differs from the first word
of the item's last well-formed `| I3 |` log line (a malformed last line is 045's, never replaced by
an earlier one) (logs/implementation, by file date then line order) is INCOMPLETE; the log never
fills in a missing verdict. Known gaps: (w) a 06 FAIL with a 07 whose last A1 line is not FAIL is
I3 FAIL with that detail; _open_at (053) still treats the item as closed, so a code commit for it is
an UNTRACKED CHANGE. Both report an error (item 077). classify reads 07 alone: a PRE_A1_LINE or
LEGACY item with a 06 FAIL and no A1 PASS line keeps the old detail while _open_at calls it closed
(known gap, 0 items 2026-11-19); (y) below VERDICT_FROM an unreadable verdict is not checked; (z) the line proves what I3
wrote, not that I3 ran (the log cross-check is the second source).

When run inside a git repo, it also prints OPEN BRANCHES: every remote branch not merged into
HEAD, the work items it carries (what merging it into HEAD would change, from the
`git merge-tree` result, so a branch with two merge bases is not credited with work already in
HEAD; item 052), whether it merges cleanly into HEAD (`git merge-tree`), and
whether it edits logs/recurring-issues.md, which only A1's daily commit on main should (036),
and its last commit date and age (039). Three more lines come from the branches:
  ID CLASH        HEAD and an open branch each added work/<ID>/request.md since their merge
                  base, with different text: two items share one ID (item 037). Rename one.
  BRANCH SKIPPED  an item the open branch changes skips a step by the rules above, using the
                  branch's own files (item 038). An error for A1 (RI-007); exit code unchanged,
                  since the branch is not part of HEAD.
  BRANCH FAIL     an item the open branch changes is I3 FAIL or A1 FAIL by the rules above, using the
                  branch's own files (item 077). Listed for A1; exit code unchanged, since the branch
                  is not part of HEAD. An item that is BRANCH SKIPPED is not also listed here. A branch
                  file git cannot show is a BRANCH ERROR, and that item is not classified (item 081).
  BRANCH ERROR    (item 081, RI-014, exit 1) `<ref> (git <cmd> failed (exit <n>))`: a git read of an open
                  branch failed (its diff after the merge-tree fallback, ls-tree, merge-base --all, or a
                  show of a step file or request.md), so what that branch carries is not known. Each
                  distinct reason is listed once per branch. Without git the scan is skipped (no line);
                  a failing `git branch -r` prints `OPEN BRANCHES: git branch failed (exit <n>) (item
                  081)`, and IN PR, RULES BRANCH and ID CLASH say `not checked (see OPEN BRANCHES)`
                  (exit 1). A git repo with no open branch prints `OPEN BRANCHES: none`.
                  Item 094 (RI-014): a single-branch clone (`--single-branch`, plain `--depth 1`, or
                  either one after `--unshallow`) has no remote-tracking ref for other branches, so its
                  `none` would be false. When `remote.origin.fetch` has no `refs/heads/*:refs/remotes/
                  origin/*` line (one leading `+` allowed) or has a `^` line, it prints `OPEN BRANCHES:
                  not checked (SINGLE_TEXT)` and IN PR, RULES BRANCH and ID CLASH say `not checked (see
                  OPEN BRANCHES)`. The main exit is unchanged (as for a shallow clone, item 090);
                  --next-id refuses (exit 2) and check_handoff --all says not checked (exit 1). A failing
                  `git config` read is `OPEN BRANCHES: git config failed (exit <n>) (item 081)`, exit 1.
                  Known gaps: a full refspec that was never fetched still reports local refs only, and
                  remotes other than origin are not checked (item 094).
                  A branch with no common history with HEAD (`git merge-base --all` exit 1, a real
                  answer; item 081 round 2) is not scanned. OPEN BRANCHES shows `<ref>: no common
                  history with HEAD; not scanned (item 081)`, and the exit is unchanged when its tree
                  holds no file under work/, logs/recurring-issues.md, the rule paths or the code
                  paths (a docs or pages branch). If it holds any, it is the BRANCH ERROR `no common
                  history with HEAD; <n> file(s) on checked paths (first: <path>) not checked (item
                  081)`. Any other merge-base exit is `git merge-base failed (exit <n>)`. --next-id
                  still counts its work/ IDs. Known gap: check_handoff's `_branch_with_handoff` does
                  not read per-ref errors, so an item whose 03 exists only on an unreadable or
                  unrelated branch shows `no hand-off` there; this BRANCH ERROR is the loud signal.
                  Item 090 (RI-014): in a shallow clone origin/main is not listed (it is not merged in
                  the shallow view; MAIN AHEAD says not checked) and main_ahead is not called; an
                  unrelated ref is not scanned and, with checked paths, is a BRANCH ERROR (exit 1).
                  Item 095 (RI-014): all such refs fold into one sub-line `  shallow clone: <n> ref(s)
                  with no merge base not checked (<ref>, <ref>, ...); run git fetch --unshallow (item
                  095)` (refs in open_branches order, the per-ref age dropped) and, when k >= 1 of them
                  hold files on checked paths (the dict's `held` count, never error text), one BRANCH
                  ERROR `shallow clone; <k> of <n> ref(s) hold files on checked paths, not checked
                  (<refs with held > 0>); run git fetch --unshallow (item 095)`. A ref whose ls-tree
                  failed (`held` None) keeps its own `<ref> (<why>)` BRANCH ERROR. A full clone is
                  unchanged (081's per-ref unrelated line).
                  Known gaps: a branch with a shared shallow base is scanned as today and was not
                  checked by 090; refs already in main are listed (not merged in the shallow view), and
                  merged and open unrelated refs are not told apart in the fold (item 095).
--log <agent> <ID> "<fields>" (item 045) appends `HH:MM | <agent> | <ID> | <fields>` with the
current UTC time to logs/research or logs/implementation/<UTC date>.md, and refuses (exit 2)
fields that don't match the agent's format (LOG_FORMAT). Every step logs this way, right after
writing its file. From TESTS_FORMAT_FROM (item 076) the I2 tests field is the last line of
`python3 -m pytest -q` run from the repo root, as printed: its parts in pytest's KNOWN_TYPES order,
each at most once; `deselected` and unknown parts are refused. Before it (I2_BEFORE) the field is
`<pass>/<total>`, with total = passed + failed + skipped + errors + xfailed + xpassed (deselected
and warnings are not tests) and pass <= total. Known limit: a trailing ` (<note>)` is free text
and could hold e.g. `(1 failed)`; the stats part before the note is still checked in full, so no
failure can be dropped from it. Item 090: from TIMED_FROM on the field must keep pytest's ` in <s>s` time
right after the stats (I2_TIMED; a time only inside the note does not count); --log refuses it without
one. INCOMPLETE applies the same rule, gated by 084's _rule_seen on 05 (TIMED_FROM): an item whose 05 was
added under a rule file without it, and whose I2 lines all fit the untimed form, is listed in RULE NOT SEEN
as `judged by untimed I2 form`.
Item 082 (RI-006): from SUITE_FROM on, an item's 05 has exactly one column-0 `Suite:` line outside code
fences and HTML comments (_md_lines "out" rows), and its text after `Suite:` (stripped) equals the tests
field of the item's last I2 log line (by file date, then line order), compared as a whole string,
` (note)` included. No Suite line, more than one, or a different value is INCOMPLETE (exit 1). No I2
line or a malformed last one: no Suite entry (043/045 already report it; an earlier line is never
used). The check is gated by 084's _rule_seen on the commit that added 05 (SUITE_FROM): a 05 added
under a rule file without it is listed in RULE NOT SEEN as `judged by no Suite check`.
Item 086 (rule D, RI-010): --log also refuses (exit 2, nothing written) while a later step file 01-06
of the same item exists in work/<ID>/ (`--log refused: work/<ID>/ already has <files> after <agent>'s
step; ...`), so a batch of lines written after the build is refused at R1. 07 and other files never
count. It runs after the format and request.md refusals, whose texts and order are unchanged. For an
item that was sent back (SEND_BACK: an R3 line with BLOCKED, an I1 line with NOT A FIT or an I3 line with
FAIL, each read from its LOG_FORMAT fullmatch group, never a substring; or an `A1 result: FAIL` line in
07) a re-run step logs again while later files from the earlier round exist, so item 090's round rule
replaces it (_round_refusal, on the item's log lines by stamp, file, line):
  (a) while the latest send-back line's sender S has not logged again (the round is open), a step after
      S is refused: `<S> sent work/<ID> back at <date HH:MM> and has not logged again; ...`;
  (b) in that open round, a step before S is refused when S's file (03 `Status:`, 04 `Fit verdict:`, 06
      `Verdict:`; its first column-0 line outside fences and comments, the unfilled template line reads as
      none, VERDICT_OF) no longer says the send-back word, or is absent, unreadable or has no readable
      line: `work/<ID>/<file> no longer says <word> (...); <S> ran again before this line ...`;
  (c) from the latest send-back or terminal line (I3 PASS; R3 READY for RESEARCH ONLY), else the item's
      first line, a line with a later step than this one refuses it: `<agent> already logged at <HH:MM>
      after <start agent> <HH:MM>; log steps in order (item 090)`.
  An unreadable log file or request.md, or a line with no valid time, refuses with `order not checked
  (item 090)`. A round opened only by A1 FAIL gets (c) only.
From LOG_CHECK_FROM on, a log line not in its format is INCOMPLETE, and
  LOG TIME        a committed log line timed after the commit that added it (git blame): it was
                  not written when its step ran (exit 1; RI-010).
                  Items in LOG_TIME_EXCEPT are not checked and are named with their reason
                  (item 049). Known gap: blame gives a line's latest commit, so a line edited
                  in a later commit is checked against that later commit.
                  Item 090 (RI-014): in a shallow clone (_anchor_env gives SHALLOW_TEXT) blame gives the
                  boundary's later commit to older lines, so it prints `LOG TIME: not checked (shallow
                  clone; run git fetch --unshallow)`; exit unchanged.
                  Item 081: only log files listed by `git ls-tree -r HEAD` are blamed (an uncommitted
                  file is skipped); a failed ls-tree is the entry `git ls-tree HEAD failed (item 081)`,
                  and a failed blame of a committed file is the entry `<file> (git blame failed; item
                  081)`, never none (exit 1).
  LOG BATCH       (item 086, rule C, RI-010, exit 1) an item whose reported pytest runs could not
                  fit between its log lines: Σ - BATCH_ROUND·k >= (Δ+1)×60 s, over the whole item:
                  start = the item's latest log line before its first I2 line, end = its last I3
                  line, Δ = whole minutes between them (a line's stamp is its file date + HH:MM, so
                  lines Δ minutes apart are < (Δ+1)×60 s apart). Σ = t05 + t06: t05 the largest time
                  of the I2 log fields and of the pytest summary lines (SUMMARY_LINE, matched at the
                  start of the stripped line, so a summary inside a test ID is not a run) in every
                  `## Test output` section of 05; t06 the largest in every `## Tests re-run` section
                  of 06 after dropping any value equal to a t05 candidate (a copy). A section ends at
                  the next `# ` or `## ` heading outside code fences. k = the number of known values
                  (pytest prints .2f). Such an item is impossible under the run-item order on one
                  steady clock (run-item L14, L16): I2 runs the suite before its line, I3 re-runs it
                  after 05 exists and before its line. Items in LOG_BATCH_EXCEPT are counted, not
                  evaluated, and named with their reason. An item with no time (k = 0), no line before
                  its first I2, an unreadable 05/06/log file or a line with no valid time is listed
                  as `not computable: <ID>: <reason>` (entries joined by "; "), never flagged; an
                  item with no I3 line after its last I2 line is in progress and not evaluated.
                  No git, so the text and exit code are the same without it.
                  Item 090 (per-round bound): every timed I2 line is also checked against the item's
                  latest line before it (prev, same order rule): t - BATCH_ROUND >= (Δ+1)×60 s is
                  `<ID> I2 at <date HH:MM> (<t> s pytest run after the <agent> line at <HH:MM>, limit
                  <L> s; impossible under the run-item order, item 090)`, also for a round after a
                  send-back and before the in-progress skip. From TIMED_FROM on a not-computable
                  reason in BATCH_STRICT (no time, no line before I2, no valid time) is also an
                  INCOMPLETE entry `LOG BATCH not computable: <reason> (item 090)`, gated on 05 like
                  the timed I2 field. Item 093: a person-dated `Waived:` (first line only) covering
                  every pre-05 step of the Scope, with those step files absent (024's shape), is
                  excused: it is listed as `not computable: <ID>: no line before I2 (<steps> waived by
                  the person, first I2 round not bounded, item 093)` and is not INCOMPLETE. Any other
                  waiver stays strict. Known gaps: (w) runs pasted
                  outside the two sections are not read
                  (only lowers Σ); (x) the bound catches a round only when its run is longer than the
                  gap allows: with today's 74-93 s runs, same-minute (Δ0) batches; Δ >= 1 batches pass
                  it, and below TIMED_FROM untimed suites can't be flagged (D and the round rule cover
                  order); (y) I3's run is untimed, so an I3 batch is caught only by the round rule (b)
                  when 06 changed; an I3 that FAILs again leaves 06 at FAIL; A1 FAIL rounds get (c)
                  only; (z) pytest's time and the log stamp are both wall clock (time.time()), so a
                  clock step during a run can move both.
                  Item 091 (gap w, RI-010): from ROUND_HEADING_FROM on, a 05/06 heading outside code
                  fences that names a run (STRAY_RUN_HEADING: `#{1,6} [round N ]test output|tests re-run`,
                  case-insensitive, at the line start) but is neither that file's opener (RUN_HEADING) nor
                  inside a read section (_section_flags, the same open/close rule as _run_seconds) is the
                  INCOMPLETE entry `<05|06> heading '<heading>'[, '<heading>'] is not read by LOG BATCH;
                  use '## Test output (round N, pasted)' / '## Tests re-run (round N)' (item 091)`, gated
                  on that file like SUITE_FROM; an unreadable 05/06 is `<05|06> round headings not
                  checked (<why>; item 091)`. Known gaps: runs with no heading of their own (076/05 under
                  `## Round 2 build`), headings indented 1-3 spaces, and the template lines are text only.
  RULES BRANCH    an open branch that changes the rules (.claude/, templates/,
                  scripts/check_pipeline.py, scripts/check_handoff.py): build new items on top
                  of it, so its rules apply to them (item 049, RI-010). Listed, not an error.
  ORPHAN LOG      a log line whose item has no work/<ID>/ folder (exit 1; item 047). --log
                  refuses an ID without work/<ID>/request.md (exit 2), so a typo'd ID is caught
                  when it is written.
  MAIN AHEAD      HEAD is behind origin/main: merge main first. origin/main and branches whose
                  tip is already in it are then left out of OPEN BRANCHES (item 051); --next-id
                  still counts them. Item 081: origin/main is the exact ref refs/remotes/origin/main
                  (`git for-each-ref`; origin/main/x is not it); a failed lookup or count prints
                  `MAIN AHEAD: git <cmd> failed (exit <n>) (item 081)` (exit 1), never 0.
                  Item 090 (RI-014): in a shallow clone, with the ref present, the count can be false
                  (main's tip looks like a root), so it prints `MAIN AHEAD: not checked (shallow clone;
                  run git fetch --unshallow)`; exit unchanged; no ref is still 0 and no line. One source
                  (the shallow text) gives all three not-checked lines on purpose: a shallow 0 is exact,
                  but a uniform text was asked for, so do not "fix" it back to a count.
  UNTRACKED CHANGE  (item 053, exit 1; RI-007) a commit on HEAD's first-parent chain after the
                  cutoff UNTRACKED_FROM that changes CODE_PATHS (ccbot/, config/, scripts/, tests/,
                  .claude/, templates/) and changes no step file 01-06 of a work item that is open at
                  the commit's first parent (07 absent, no `A1 result:` line, or last line FAIL;
                  PRE_A1_LINE and LEGACY items are closed). Each commit is judged against its first
                  parent (`git diff-tree --no-renames`), so a merge is one unit. 07 never covers code.
                  A follow-up to a completed item is a new item. "not checked (no git)" without git;
                  "not checked (... shallow clone ...)" when the cutoff is missing from a shallow
                  clone (exit unchanged); a cutoff missing from a full clone is an error (exit 1).
                  Item 079 (RI-014): in a shallow clone (S = the lines of `<git rev-parse
                  --git-common-dir>/shallow`), a boundary in `cutoff..HEAD` gives `not checked (shallow
                  boundary <b7>; run git fetch --unshallow)`; a boundary that is an ancestor of the
                  cutoff keeps none but turns entries into `not checked (shallow boundary <b7> below the
                  cutoff; <n> unconfirmed entries; ...)`, exit unchanged; an unreadable shallow file
                  gives `not checked (shallow clone; ...)`. A diff-tree failure on a commit not in S
                  stays an entry (exit 1).
                  Known gaps: (a) one open item's 01-06 file covers unrelated code in the same unit;
                  (b) on a branch each direct commit is its own unit, so commit code together with
                  your 05; (c) PRs must land as merge commits (squash or rebase drops the cutoff ->
                  exit 1); (d) a merge's conflict edits are judged together with the whole merge
                  against its first parent; (e) paths outside CODE_PATHS (pyproject.toml, README.md,
                  data/) are not checked, and under work/ only .py files are code (WORK_CODE; other
                  script types there are not checked); (f) non-ASCII paths are quoted (no -z), under
                  work/ too.
                  Item 064: a .py file under work/<ID>/ (any depth, WORK_CODE) is code too, so a
                  diagnostic is committed together with an open item's step file. diff-tree lists
                  deleted paths too, so deleting or moving such a file is a code change as well.
  RESEARCH CODE   (item 062, RI-007) a RESEARCH ONLY item whose unit changes RESEARCH_CODE_PATHS
                  (ccbot/, config/, scripts/, tests/) with no I1-I3. A unit is one HEAD commit after
                  the cutoff (as 053, against its first parent) or one open branch as a whole. On
                  HEAD the item's line becomes `<ID>: SKIPPED (<sha7> RESEARCH ONLY: changes <files>
                  ...)` (exit 1) and the line lists the IDs, or none, "not checked (no git)", or
                  "not checked (see UNTRACKED CHANGE)" when the cutoff can't be used; a failed
                  diff-tree in the walk gives not checked (see UNTRACKED CHANGE), never none (079).
                  On a branch it is `BRANCH SKIPPED: <ID> (<ref>: RESEARCH ONLY: changes <files>
                  ...)`, joined to the item's classify detail when that is SKIPPED too (exit
                  unchanged). Scope and waiver
                  are read from request.md at the tip; a missing request.md is flagged, never passed.
                  Only `Waived: 04 05 06 (person, YYYY-MM-DD: <why>)` excuses it. Known gaps:
                  (g) a FULL/FAST item's 04 or 05 in the same unit covers the research item's code;
                  (h) .claude/ and templates/ edits are 053's only; (i) on a branch, code committed
                  without the research item's step file is caught by 053 on HEAD, not by 062;
                  (j) only the first `Waived:` line is read, so 04 05 06 go on the item's single
                  Waived line.
                  Item 064: a .py file under work/<ID>/ (WORK_CODE) is code here too. On a branch the
                  unit is the code and work/ .py files the branch changes plus the tip's step files
                  of the items it touches; a .py already at the tip and unchanged is not counted.
                  For (i): a work/ .py committed on a branch with no step file is 053's on HEAD.
                  (k) a diagnostic in a FULL/FAST item is covered by its step files; its logic is
                  checked only by I3's re-run. (l) a failed branch git diff is a BRANCH ERROR
                  (item 081).
  REAL-DATA FIELD (item 070, RI-010/RI-013) for items from WHOLE_DIFF_FROM on (earlier items are not
                  re-checked): when one of the item's own non-merge commits after the cutoff (a commit
                  holding one of its step files 01-06; one `git log --no-merges` call) changes a TRIGGER
                  path or a file under TRIGGER_DIRS (realtest's decision path), its 05, and its 06 once
                  that exists, must hold diff_reports' TOTAL line (TOTAL_LINE, a full-line match) in the
                  `## Real-data effect (diff_reports output, pasted)` section. HTML comments are dropped;
                  lines inside code fences (``` or ~~~, CommonMark 0.31.2 §4.5) are read, and a `## `
                  inside a fence does not end the section.
                  A missing section, no TOTAL line, an unclosed fence or a missing 05 is INCOMPLETE
                  (exit 1). The line lists the IDs with an entry, or none; "not checked (no git)";
                  "not checked (see UNTRACKED CHANGE)" when the cutoff can't be used; the 079
                  below-cutoff text replaces entries; "git log failed (item 070)" (exit 1); a
                  triggered ID with no request.md is named as `<ID> (no work/<ID>/request.md here)`
                  (exit 1). Known gaps: (m) conflict-only trigger edits in a
                  merge are not seen; (n) a committed-then-reverted change still triggers; (o) a TOTAL
                  line proves a paste, not that it is current, and does not prove 06's TOTAL equals 05's
                  (I3 still compares, templates/verification.md); (p) a data/real/ commit with no step
                  file is attributed to no item, and data/ is outside 053's CODE_PATHS (gap e); a --data
                  dir outside the repo is not seen; (q) one commit holding two items' step files triggers
                  both; (r) RESEARCH ONLY items are 062's and are skipped here; (s) uncommitted trigger
                  edits are not seen; (t) tests/test_real_data_field.py keeps TRIGGER in step with
                  realtest's imports and only literal `"config" / "<name>"` paths. Fences (item 077):
                  fences inside list items or blockquotes are read line by line; comments are dropped
                  before fences are tracked, so a `<!--` inside a fence with no `-->` on its line hides
                  text to the next `-->`.
  UNCOMMITTED STEP (item 077, RI-010, exit 1) a step file 01-06 in the working tree that is not in
                  `git ls-tree -r HEAD -- work/` and has no `| <agent> | <ID> |` log line, for every
                  item number: a step whose run was cut off before it logged or was committed. Finish or
                  redo that step. "not checked (no git)" without git; "git ls-tree HEAD failed (item
                  077)" when HEAD's tree can't be listed (exit 1, never none). This is the first check
                  of the working tree against HEAD's commit state. Known gaps: (a) a file and its log
                  line written but not committed is not listed; (b) a modified tracked step file (e.g.
                  a round-2 06) is not listed; (c) 07 and other files outside 01-06 are not checked.
  STASH           (item 097, RI-009, exit 1) `git stash list` in this checkout (refs/stash is shared by every
                  worktree of the repo). Exit 0 with empty output prints `STASH: none`; exit 0 with output
                  prints `STASH: <n> (first: <first line>); local to this checkout; only the person drops an
                  entry (item 097)` (exit 1). Decided by the exit code and empty stdout only, never by line text
                  (RI-012); <n> counts non-empty lines and is shown only (a log config that adds lines can raise
                  it, never turn entries into none). Without git `STASH: not checked (no git)`, exit unchanged;
                  any other failure `STASH: not checked (git stash failed (exit <n>)) (item 097)`, exit 1, and
                  stdout is not read. Known gap: it sees only entries left behind, not a push and drop in one run.
--next-id prints the next free ID over HEAD and every unmerged remote branch, so two threads
never pick the same number. Outside a git repo (or without git) the branch part is skipped.
Item 081: when `git branch -r` or a branch's `git ls-tree <ref> -- work/` fails, it prints
`--next-id refused: <why>; ...` to stderr, nothing on stdout, and exits 2 (never a guessed ID). A
branch with no work/ adds no ID. In a repo with no commit: --next-id refuses; make the first commit.
Item 094: in a single-branch clone (see OPEN BRANCHES) --next-id refuses with `--next-id refused:
<SINGLE_TEXT>; ...`, exit 2, nothing on stdout; a failing `git config` read refuses as above.
Known gap (item 081): when `--is-shallow-repository` and `--git-common-dir` both fail,
_shallow_boundaries returns "full", so _walk prints the squash/rebase text for UNTRACKED CHANGE:
the reason is wrong, but it still exits 1.
INBOX (item 069, RI-010): the daily audit's Inbox step (a1-auditor job B) is a text duty, so the
newest daily report logs/audit/<YYYY-MM-DD>.md must have a `## Inbox` section holding a
`project-inbox:` line (`nothing new`, `<n> new` or `UNREAD:`) and a `hub:` line (a 7-40 hex SHA or
`UNREAD:`), if it was written under the Inbox template (never a date, 069 round 2): the report is
checked only if INBOX_TEMPLATE at the commit that added it (`git log --diff-filter=A`) has `## Inbox`;
an uncommitted report is judged by the working-tree template. Otherwise, and with no git or in a
shallow clone, it prints `INBOX: not checked (...)`; a failing `git log` gives exit 1, and so does
`--is-shallow-repository` exiting 128 (git died, e.g. a bad shallow line; item 081). Other codes keep
the unknown-flag path. Only lines
between `## Inbox` and the next `## ` heading count. Per-item reports (<date>-<ID>.md) are ignored.
A report missing any part prints `INBOX: <file> (<what is missing>)` and gives exit 1; no daily
report prints `INBOX: not checked (no daily report)`. Known gaps: this proves the lines exist,
not that A1 read the channels; I3 and A1 spot-check that. (u) a report written but not committed
before a pull that brings the new template is judged by the new template: commit the daily report
before pulling. (v) removing `## Inbox` from the template later switches the check off for reports
added after that; this is intended, the rule follows the template.
RULE NOT SEEN (item 084, RI-010): an item is judged by the rule it was built under. When the I2
tests-field check (TESTS_FORMAT_FROM) or the 06 verdict-line checks (VERDICT_FROM) would fire, the
commit that added its 05 or 06 (`git log --no-renames --diff-filter=A -1`, default history
simplification, never --first-parent) is the anchor; if RULE_FILE in that commit's tree has no
`^<CONST> = ` line, the rule was not seen: the I2 lines are judged by I2_BEFORE (and stay INCOMPLETE
with its hint if they fail it), and the verdict checks are dropped (below VERDICT_FROM there are
none). Each such pair is printed after INCOMPLETE as `RULE NOT SEEN: <ID> (<step> added in <sha7>
without <CONST> (<rule item>): judged by <old rule>; item 084)`, or `none`; the exit code is
unchanged. No git or a shallow clone (079's _shallow_boundaries) prints `RULE NOT SEEN: not checked
(no git)` / `not checked (shallow clone; run git fetch --unshallow)` and keeps the numeric cutoffs.
Item 095 (RI-014): in a shallow clone the anchor can't be read, so an entry a gate (TIMED, TESTS when every
own I2 line passes I2_BEFORE, LOG BATCH not computable, Suite, round headings, verdict) would give for a step
file committed at HEAD is printed on `INCOMPLETE NOT CHECKED: <ID> (<entry>; <entry>), ...; rule seen not
checked (shallow clone; run git fetch --unshallow; item 095)` (or `INCOMPLETE NOT CHECKED: none`; the line
is printed only when shallow), not on INCOMPLETE; the exit is 1 for a non-empty list (fail closed). Only the
I2 part of a format entry moves; other agents stay on INCOMPLETE. A step file not in HEAD's tree (ls-tree
-r HEAD -- work/, read once and only when shallow) keeps its entries on INCOMPLETE, as a full clone does;
a failed HEAD tree read leaves them not checked (exit 1). Known gaps: no-git and unborn-HEAD entries are
not labelled; the finer test of which step files lie above the shallow boundary is not built; an exact
TESTS entry keeps the new-rule hint where the full clone shows the I2_BEFORE hint (both INCOMPLETE).
Item 088: an uncommitted 05/06 (any check run before its commit) keeps them with no entry; an unborn
HEAD prints `not checked (unborn HEAD)` and keeps them; a failed HEAD verify prints `not checked (git
rev-parse --verify HEAD failed (exit <n>))`, keeps them and gives exit 1. A failed git call (`<step>
anchor: git failed (item 084)`) or an anchor tree without RULE_FILE (`<step> anchor <sha7> has no
scripts/check_pipeline.py (item 084)`) keeps them and adds that entry (exit 1). Items below either
cutoff make no git call. Cost (item 088): HEAD is read once per run (+1 wrapper call); a full pair
is 3 wrapper calls (log, ls-tree, show) = 6 git processes (each _git also runs rev-parse
--show-toplevel); early exits make 0, 1 or 2; at most 3 pairs per item (05 TESTS, 05 SUITE, 06
VERDICT), 5 from ROUND_HEADING_FROM on (05 and 06 ROUND_HEADING, item 091; a pair runs only when a check fires). Before 088 a full pair was 4 calls = 8 processes. Known or decided gaps: WHOLE_DIFF_FROM (REAL-DATA FIELD) is not gated (0
items today); the 06 verdict vs last I3 line cross-check stays at CHECKLIST_FROM by decision;
CHECKLIST_FROM, LOG_CHECK_FROM and their checks stay numeric; --log (write_log) stays numeric, so a
new log line is never judged by an old rule. The constant counts only at the start of a line, so a
comment, a longer name (OLD_TESTS_FORMAT_FROM = 76) or a string is not it (RI-012, round 2 test);
a column-0 `<CONST> = ` line inside a triple-quoted string would still read as seen (strict: the
new rule is kept, never a false "not seen").
UNREADABLE (item 089, RI-014, exit 1): every repo file this script reads (work/, logs/, templates/daily-audit.md,
the shallow file) is read by one reader, _read: the bytes decoded as strict UTF-8, "\\r\\n" and "\\r" turned
into "\\n" (read_text's rule). A file that exists but can't be read (not UTF-8, a directory, no permission)
never raises: it is listed once on `UNREADABLE: <path> (<detail>)`, printed between ORPHAN LOG and INBOX
(`none` when every read worked), with the detail `not UTF-8 at byte <n>` or the exception class name (never
file content or error text), and the run exits 1. Each reader of it says what it did not check, never
computing from "" or printing a bare none: classify gives `<ID>: UNREADABLE (<path> unreadable)` for
request.md, 06 or 07; INCOMPLETE gets `06 not checked (...; item 089)`, `05 not checked (...)` at the Suite
check, and `log lines not checked (<files> unreadable; item 089)` for an item with any step file 01-06 (in
place of the log-line, format, Suite and I3-line checks); UNCOMMITTED STEP prints `not checked (<files>
unreadable; item 089)`; ORPHAN LOG prints `not checked (<files> unreadable; item 089)` or `<orphans>; not
checked: <files> unreadable (item 089)`; LOG BATCH lists the item as not computable (086); REAL-DATA FIELD
adds `request.md|05|06 not checked (...; item 089)` (an unreadable request.md counts as built, strict);
RESEARCH CODE flags `RESEARCH ONLY check: <path> unreadable (item 089)`; ID CLASH compares an unreadable
request.md as absent text, so the item is listed, never dropped; INBOX prints `not checked (<report>
unreadable)` or `not checked (<report> not committed; its templates/daily-audit.md unreadable)`. A shallow
file that exists but can't be read makes _shallow_boundaries "unreadable" even when the flag is not a sure
true (git died on it), so UNTRACKED CHANGE and RULE NOT SEEN say `not checked (shallow clone; ...)`, never
the squash/rebase text or none. scripts/check_handoff.py reads 01 and 03 through _read (item 092).
Known gaps: check_handoff --all never reads the 01 of an item with no 03 (092 01 F17), and
check_handoff ignores the why from open_branches' _read of request.md (092 01 F22).
"""
import datetime as dt
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

STEPS = {"01": "01-research.md", "02": "02-improvements.md", "03": "03-handoff.md",
         "04": "04-build-plan.md", "05": "05-build-report.md", "06": "06-verification.md",
         "07": "07-audit-task.md"}
REQUIRED = {"FULL": ["01", "02", "03", "04", "05", "06", "07"],
            "RESEARCH ONLY": ["01", "02", "03", "07"],
            "FAST": ["01", "03", "05", "06", "07"]}
# Only the person may waive these (run-item.md: R3 and I3 are never skipped; item 031).
PERSON_ONLY = ("03", "06")
# Items whose audit was recorded only in a daily report, before 07 carried an
# `A1 result:` line (item 033). Every other item needs the line (item 035: a date cutoff let
# items opened early but built later through). Never add a new item here.
PRE_A1_LINE = {"002", "003", "017", "018", "019", "020", "021", "022"}
RECURRING = "logs/recurring-issues.md"
# Item 043: the step-0 line in 06 and a log line per step are checked from this ID on.
# Earlier items are not re-checked (013-016 and 040 were found by A1 on 2026-11-04).
CHECKLIST_FROM = 41
AGENT = {"01": "R1", "02": "R2", "03": "R3", "04": "I1", "05": "I2", "06": "I3"}
# Item 045: from this ID on, each log line must match its agent's format, and a committed line
# may not be timed after the commit that added it. Lines are written with --log, never by hand.
LOG_CHECK_FROM = 45
TESTS_FORMAT_FROM = 76   # item 076: from this ID on the I2 tests field is pytest's summary line as printed
# Item 082: from this ID on 05 has exactly one column-0 `Suite:` line equal to the last I2 log tests field;
# numeric floor above every in-flight item (080-086).
SUITE_FROM = 87
# Item 090 (RI-010): from this ID on the I2 tests field keeps pytest's ` in <s>s` time (I2_TIMED); the 7th
# `*_FROM` cutoff, a numeric floor above the in-flight items 088/089.
TIMED_FROM = 90
# Item 091 (RI-010): from this ID on, a 05/06 run heading that LOG BATCH does not read is INCOMPLETE; the 8th
# `*_FROM` cutoff, a numeric floor above every item open on 2026-11-21 (work/ ends at 091).
ROUND_HEADING_FROM = 92
# Item 076: the parts of pytest's summary line, in KNOWN_TYPES order (pytest main/9.0.x terminal.py),
# each at most once. "deselected" left out on purpose: a full-suite run has none.
_N = r"[1-9]\d*"
_END = r"(?:, (?=[1-9])|(?=$| in | \())"          # a part is followed by ", <next part>" or the end of the stats
_STATS_PARTS = (rf"{_N} failed", rf"{_N} passed", rf"{_N} skipped", rf"{_N} xfailed", rf"{_N} xpassed",
                rf"(?:1 warning|(?!1 ){_N} warnings)", rf"(?:1 error|(?!1 ){_N} errors)",
                rf"{_N} subtests passed", rf"{_N} subtests failed", rf"{_N} subtests skipped")
_STATS = r"(?=[1-9])" + "".join(f"(?:{p}{_END})?" for p in _STATS_PARTS)
_TAIL = r"(?: in \d+\.\d+(?:s| seconds)(?: \(\d+:\d{2}:\d{2}\))?)?(?: \(.*\))?"
I2_BEFORE = r"\d+ files? changed \| tests (\d+)/(\d+)\b.*"    # items LOG_CHECK_FROM..TESTS_FORMAT_FROM-1
# Item 090: the I2 field from TIMED_FROM on: the time is mandatory and stands right after the stats, so a time
# only inside the ` (<note>)` does not count. The global _TAIL (LOG_FORMAT["I2"]) stays optional.
I2_TIMED = rf"\d+ files? changed \| tests {_STATS} in \d+\.\d+(?:s| seconds)(?: \(\d+:\d{{2}}:\d{{2}}\))?(?: \(.*\))?"
# Item 049: items whose log times can't be checked, with why. 048 was built on a branch cut
# before 045 merged; its six lines were typed by hand with a time after their commit, and the
# real times are lost. Never add a new item here.
LOG_TIME_EXCEPT = {"048": "built before 045's --log rule reached main; times typed by hand, not recoverable (item 049)"}
# Item 086 (rule C, RI-010): items whose pytest runs can't be checked against their log times, with why.
# 083's six lines were written in one batch after the build; the real times are lost. A separate
# dict from LOG_TIME_EXCEPT (083's lines are not after their commit). Never add a new item here.
LOG_BATCH_EXCEPT = {"083": "six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); "
                           "real times not recoverable (item 086)"}
BATCH_ROUND = 0.005   # item 086: pytest prints seconds with .2f, so the real time is >= printed - 0.005
# Item 086 (rule D): the send-back verdicts of a log line, as (LOG_FORMAT group, word); read by fullmatch,
# never a substring (RI-012). R3's verdict is group 2 (group 1 is verified/as-is).
SEND_BACK = {"R3": (2, "BLOCKED"), "I1": (1, "NOT A FIT"), "I3": (1, "FAIL")}
# Item 090 (RI-010): LOG BATCH not-computable reasons that are INCOMPLETE for an ID >= TIMED_FROM; compared by
# equality, never a substring (RI-012). "unreadable" reasons stay 089's (UNREADABLE, exit 1).
BATCH_STRICT = ("no pytest time in 05/06/I2 line", "no line before I2", "log line with no valid time")
# Item 086: a pytest summary line as printed, .match on the stripped line (anchored at its start, so a
# summary inside a test ID such as `FAILED t[1 failed in 58.86s]` is not a run); seconds in group 1.
# Item 091: the section openers LOG BATCH (rule C) reads, per step file; the one source for batch_log_items
# and the stray-heading check. STRAY_RUN_HEADING is used with .match (anchored at the line start, RI-012).
RUN_HEADING = {"05": r"## Test output\b", "06": r"## Tests re-run\b"}
STRAY_RUN_HEADING = re.compile(r"#{1,6} (?:round \d+ )?(?:test output|tests re-run)\b", re.I)
SUMMARY_LINE = re.compile(rf"(?:=+ )?(?={_N} )(?:{_STATS}) in (\d+\.\d+)(?:s| seconds)\b")
# Item 070: the Real-data effect field is checked from this ID on; earlier items are not re-checked.
WHOLE_DIFF_FROM = 70
# Item 071: I3's verdict and send-back target in 06 (templates/verification.md L2-3). The first
# column-0 `Verdict:` / `Sent back to:` line outside code fences and HTML comments decides; never
# a later one, never a substring (RI-012). From VERDICT_FROM on an unreadable value is INCOMPLETE.
VERDICT_FROM = 71
RULE_FILE = "scripts/check_pipeline.py"   # item 084: the file whose copy in an anchor commit's tree is read
VERDICT_LINE = re.compile(r"Verdict:[ \t]*(?:\*\*)?(PASS|FAIL)\b(?![ \t*]*[|/])")   # .match on the line
# Item 090 (rule D round check): the sender's step file and its verdict line (.match on the first column-0 line
# outside fences and comments that starts with the label, i.e. the pattern up to its first ":"). The lookahead
# makes the unfilled template lines (`FIT | FIT WITH CHANGES | NOT A FIT`, `READY | BLOCKED`) no verdict.
VERDICT_OF = {"R3": ("03", re.compile(r"Status:[ \t]*(?:\*\*)?(READY|BLOCKED)\b(?![ \t*]*[|/])")),
              "I1": ("04", re.compile(r"Fit verdict:[ \t]*(?:\*\*)?(NOT A FIT|FIT WITH CHANGES|FIT)\b(?![ \t*]*[|/])")),
              "I3": ("06", VERDICT_LINE)}
SENT_BACK_LINE = re.compile(r"Sent back to:[ \t]*(I1 I2|I1|I2|none)[ \t]*")         # .fullmatch on the line
# Item 070: realtest's decision path: ccbot/realtest.py, the ccbot modules it imports and the config
# files they read by literal path (tests/test_real_data_field.py keeps this list in step).
TRIGGER = ("ccbot/realtest.py", "ccbot/costs.py", "ccbot/expiries.py", "ccbot/config.py", "ccbot/pricing.py",
           "config/default.json", "config/tickers.json", "config/holidays.json")
# Item 070: realtest's default --data dir (realtest.py --data default); any file under it triggers.
TRIGGER_DIRS = ("data/real/",)
# Item 070: the 05/06 section heading (templates/build-report.md, templates/verification.md).
REAL_DATA_FIELD = "Real-data effect (diff_reports output, pasted)"
# Item 070: diff_reports.diff_dirs' fixed TOTAL line; a full-line match, never a substring (RI-012).
TOTAL_LINE = re.compile(r"TOTAL: files \d+, only-before \d+, only-after \d+, not compared \d+, json changes \d+, "
                        r"csv rows changed \d+ added \d+ removed \d+, columns changed \d+")
# Item 049: an open branch changing any of these changes the rules new items are built under.
RULE_PATHS = (".claude/", "templates/", "scripts/check_pipeline.py", "scripts/check_handoff.py")
# Item 053: a commit changing any of these must change a step file 01-06 of an open work item.
CODE_PATHS = ("ccbot/", "config/", "scripts/", "tests/", ".claude/", "templates/")
# item 053: HEAD of daily-fixes/2026-11-11 just before I2's first code commit; never move it forward
UNTRACKED_FROM = "694bf4d0038e25bb82bd111018fbd67a94bbc74d"
# Item 079 (RI-014): one line of the shallow file, a full SHA-1 (40) or SHA-256 (64) hex name.
SHALLOW_LINE = re.compile(r"[0-9a-f]{40}([0-9a-f]{24})?")
# Item 062: a RESEARCH ONLY item may not change these unless I1-I3 ran or the person waived them.
# .claude/ and templates/ are left to 053 (gap h).
RESEARCH_CODE_PATHS = ("ccbot/", "config/", "scripts/", "tests/")
# Item 064: a .py file under a work item's folder (any depth) is code for 053 and 062.
WORK_CODE = re.compile(r"work/\d{3}/.+\.py")
WAIVE_BUILD = {"04", "05", "06"}
WAIVE_BUILD_BY_PERSON = re.compile(r"\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:")
# Item 093: request.md's `Waived:` line (group 1 = step numbers, group 2 = the rest; parse_request reads
# the first one), and the person-with-date prefix written once (from WAIVE_BUILD_BY_PERSON). PERSON_DATED
# is used only with .match on WAIVED_LINE group 2, so a quoted person form later in the text never counts
# (RI-012); re.match, not prefixmatch (RI-008).
WAIVED_LINE = re.compile(r"^Waived:\s*([0-9 ,]+)(.*)$", re.M)
PERSON_DATED = re.compile(r"\s*" + WAIVE_BUILD_BY_PERSON.pattern)
STEP_FILE = re.compile(r"^work/(\d{3})/(01-research|02-improvements|03-handoff|04-build-plan|"
                       r"05-build-report|06-verification)\.md$")
LOG_FORMAT = {  # the fields after `HH:MM | <agent> | <ID> | ` (.claude/agents/*.md)
    "R1": r"brief written \| \d+",
    "R2": r"3 for / 3 against \| languages: \S.*",
    "R3": r"\d+ (verified|as-is), \d+ fixed, \d+ removed \| (READY|BLOCKED)\b.*",
    "I1": r"(FIT|FIT WITH CHANGES|NOT A FIT) \| \d+ files planned\b.*",
    "I2": rf"\d+ files? changed \| tests {_STATS}{_TAIL}",   # items >= TESTS_FORMAT_FROM; earlier: I2_BEFORE
    "I3": r"(PASS|FAIL) \| sent to audit: (yes|no)\b.*",
}
# Item 050: the same formats in plain words (as the agent files write them), with an example
# that fits each regex (tests check both), for INCOMPLETE and --log refusals.
LOG_HINT = {
    "R1": ("brief written | <sources count>", "brief written | 3"),
    "R2": ("3 for / 3 against | languages: <list or N/A>", "3 for / 3 against | languages: N/A"),
    "R3": ("<n> verified, <n> fixed, <n> removed | READY or BLOCKED", "5 verified, 1 fixed, 0 removed | READY"),
    "I1": ("FIT or FIT WITH CHANGES or NOT A FIT | <n> files planned", "FIT | 2 files planned"),
    "I2": ("<n> files changed | tests <last line of python3 -m pytest -q, as printed>",
           "2 files changed | tests 9 passed, 1 skipped in 3.21s"),
    "I3": ("PASS or FAIL | sent to audit: yes or no", "PASS | sent to audit: yes"),
}
# Item 076: the I2 hint for items before TESTS_FORMAT_FROM (read through log_hint).
LOG_HINT_BEFORE = {"I2": ("<n> files changed | tests <pass>/<total> (pass <= total)", "2 files changed | tests 9/9")}
# Item 090: the I2 hint from TIMED_FROM on (read through log_hint); its example fits I2_TIMED.
LOG_HINT_TIMED = {"I2": ("<n> files changed | tests <last line of python3 -m pytest -q, as printed, with its ` in <s>s` "
                         "time>", "2 files changed | tests 9 passed, 1 skipped in 3.21s")}
LOG_LINE = re.compile(r"^(\d{2}):(\d{2}) \| (R1|R2|R3|I1|I2|I3) \| (\d{3}) \| (.*)$")
FAST_BY_PERSON = re.compile(r"^Scope:\s*FAST\s*\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*\)", re.M)
# Older than the Scope/07 rules. Never add a new item here.
LEGACY = {"001": "RESEARCH ONLY before 07-audit-task existed (item 021)",
          **{i: "07 is combined in work/003/07-audit-task.md" for i in ("004", "005", "006", "007", "008")}}
INBOX_TEMPLATE = "templates/daily-audit.md"  # item 069 round 2: a daily report is checked only if written under this template with ## Inbox (never a date)
DAILY_REPORT = re.compile(r"\d{4}-\d{2}-\d{2}\.md")
INBOX_HEAD = re.compile(r"^## Inbox\b", re.M)
INBOX_PI = re.compile(r"^project-inbox:\s*(nothing new|\d+ new|UNREAD:)", re.M)
INBOX_HUB = re.compile(r"^hub:\s*([0-9a-f]{7,40}\b|UNREAD:)", re.M)


# Item 089 (RI-014): every file that _read could not read this run, {rendered path: detail}. Reasons only,
# never file text. main() clears it first (never rebinds it) and prints it on the UNREADABLE line.
_UNREAD = {}


def _shown(path):
    """Item 089: a path as printed (as_posix), with any surrogate-escaped byte of a non-UTF-8 file name
    shown as `\\udcXX` (backslashreplace), so printing it never raises. A UTF-8 name is unchanged."""
    return path.as_posix().encode("utf-8", "backslashreplace").decode("utf-8")


def _read(path, missing_ok=False):
    """Item 089 (RI-014): the one reader of repo files. (text, None) on success: the bytes decoded as
    UTF-8 (strict), with "\\r\\n" and then "\\r" turned into "\\n", the same rule as read_text's
    universal newlines and CPython subprocess's _translate_newlines (so text read here equals git's
    text-mode output). With missing_ok, a missing file is (None, None) and nothing is recorded. Any
    other OSError or UnicodeDecodeError is (None, "<path> unreadable") and records the path in _UNREAD
    with the detail `not UTF-8 at byte <n>` (decode error) or the exception class name (e.g.
    IsADirectoryError, PermissionError); never the error text or file content (RI-012)."""
    try:
        return path.read_bytes().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"), None
    except (OSError, UnicodeDecodeError) as err:
        if missing_ok and isinstance(err, FileNotFoundError):
            return None, None
        shown = _shown(path)
        _UNREAD[shown] = (f"not UTF-8 at byte {err.start}" if isinstance(err, UnicodeDecodeError)
                          else type(err).__name__)
        return None, f"{shown} unreadable"


def parse_request(text):
    """(scope, date, (waived steps, first Waived: line, who)) from request.md text."""
    scope = re.search(r"^Scope:\s*(FULL|RESEARCH ONLY|FAST)\b", text, re.M)
    date = re.search(r"^Date:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
    waived = WAIVED_LINE.search(text)
    who = re.match(r"\s*\(\s*([^,:)]+)", waived.group(2)) if waived else None
    return (scope.group(1) if scope else "FULL",
            dt.date.fromisoformat(date.group(1)) if date else None,
            (re.findall(r"\d\d", waived.group(1)), waived.group(0).strip(),
             who.group(1).strip().lower() if who else "") if waived else ([], "", ""))


def _build_waived(text):
    """Item 062: the item's first `Waived:` line excuses 04 05 06 and was written by the person
    with a date: `Waived: 04 05 06 (person, YYYY-MM-DD: <why>)`."""
    _, _, (steps, waived_line, who) = parse_request(text)
    return WAIVE_BUILD <= set(steps) and who == "person" and bool(WAIVE_BUILD_BY_PERSON.search(waived_line))


def _person_waived_before_i2(req_text, item_dir):
    """Item 093: the steps before 05 of the item's Scope, when the person waived all of them with a date
    and none of their files exists; else None (the strict "no line before I2" reason stays).
    Reads only the first `Waived:` line (parse_request's rule; a later person-dated line never counts,
    gap j). Its text after the step numbers must start with `(person, YYYY-MM-DD:` (PERSON_DATED.match,
    anchored; a person form quoted later in the text never counts). `person` is case-sensitive, so
    `(Person, ...)` stays strict (fails safe, same as FAST_BY_PERSON and WAIVE_BUILD_BY_PERSON); the date
    is not validated (2026-13-45 matches, the same known gap as those two patterns). No git."""
    scope, _, (waived, _, _) = parse_request(req_text)
    m = WAIVED_LINE.search(req_text)
    pre = [s for s in REQUIRED[scope] if s < "05"]
    if (m and PERSON_DATED.match(m.group(2)) and pre and set(pre) <= set(waived)
            and not any((item_dir / STEPS[s]).exists() for s in pre)):
        return pre
    return None


# Item 077: a CommonMark 0.31.2 §4.5 code fence opener (.fullmatch): 0-3 spaces, 3+ ` or ~, info string.
FENCE_OPEN = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")


def _md_lines(text):
    """Item 077: ([(line, state)], open_at_end) for a markdown text with HTML comments dropped first.
    state is "out", "mark" (an opening or closing fence line) or "in" (inside a fence). Fences are
    CommonMark 0.31.2 §4.5 code fences: an opener is 0-3 spaces then 3+ backticks or tildes (a
    backtick opener's info string may not hold a backtick); the closer is 0-3 spaces, the same
    char at least as many times, then only spaces or tabs. open_at_end: a fence is still open."""
    rows, char, n = [], None, 0
    for line in re.sub(r"<!--.*?-->", "", text, flags=re.S).splitlines():
        if char is None:
            m = FENCE_OPEN.fullmatch(line)
            if m and not (m[1][0] == "`" and "`" in m[2]):
                char, n = m[1][0], len(m[1])
                rows.append((line, "mark"))
            else:
                rows.append((line, "out"))
        elif re.fullmatch(rf" {{0,3}}{re.escape(char)}{{{n},}}[ \t]*", line):
            char = None
            rows.append((line, "mark"))
        else:
            rows.append((line, "in"))
    return rows, char is not None


def _a1_results(text):
    """Items 042, 053, 077: every `A1 result:` word in a 07 text, in order (one reader for classify
    and _open_at)."""
    return re.findall(r"^A1 result:\s*(\w+)", text, re.M)


def i3_verdict(path):
    """Item 071: (verdict, target) from the 06 file at `path` (_i3_verdict_text). Item 089: a file
    _read can't read gives (None, None) and is listed on the UNREADABLE line."""
    text, why = _read(path)
    return (None, None) if why else _i3_verdict_text(text)


def _i3_verdict_text(text):
    """Item 071: (verdict, target) from 06's text; the first column-0 line of each, outside code fences
    and HTML comments, decides, never a later one; None = unreadable. Fences are CommonMark 0.31.2 §4.5
    code fences (``` or ~~~, _md_lines; item 077)."""
    rows, _ = _md_lines(text)
    verdict = target = None
    seen_verdict = seen_target = False
    for line, state in rows:
        if state != "out":
            continue
        if not seen_verdict and line.startswith("Verdict:"):
            seen_verdict = True
            m = VERDICT_LINE.match(line)
            verdict = m[1] if m else None
        elif not seen_target and line.startswith("Sent back to:"):
            seen_target = True
            m = SENT_BACK_LINE.fullmatch(line)
            target = m[1] if m else None
        if seen_verdict and seen_target:
            break
    return verdict, target


def _is_code(f, paths):
    """Item 064: path `f` is code if it starts with one of `paths` or is a .py file under a work
    item's folder (WORK_CODE, whole path; never from commit text, RI-012)."""
    return f.startswith(paths) or WORK_CODE.fullmatch(f) is not None


def _research_code(files, request_text_of):
    """Item 062 (RI-007): [(ID, detail)] for the RESEARCH ONLY items in one unit (a HEAD commit
    or an open branch) whose `files` change RESEARCH_CODE_PATHS with no I1-I3 and no person's
    waiver. `request_text_of(ID)` is the item's request.md text at the tip, or None. Items come
    from the paths only, never from commit messages (RI-012)."""
    code = [f for f in files if _is_code(f, RESEARCH_CODE_PATHS)]
    if not code:
        return []
    items = sorted({m[1] for m in map(STEP_FILE.match, files) if m})
    texts = {i: request_text_of(i) for i in items}
    built = {i for i in items for s in ("04", "05") if f"work/{i}/{STEPS[s]}" in files}
    if any(texts[i] is not None and parse_request(texts[i])[0] in ("FULL", "FAST") for i in built):
        return []                                           # gap (g): a built item covers the unit
    flags = []
    for i in items:
        if i in LEGACY:
            continue
        if texts[i] is None:
            flags.append((i, "RESEARCH ONLY check: no request.md at the tip, item 062"))
        elif parse_request(texts[i])[0] == "RESEARCH ONLY" and not _build_waived(texts[i]):
            flags.append((i, f"RESEARCH ONLY: changes {' '.join(code)} with no 04-06; needs Scope FULL or "
                             '"Waived: 04 05 06 (person, <date>: <why>)" on the item\'s single Waived: line '
                             "(item 062)"))
    return flags


def classify(item_dir, today):
    """(status, detail) for one work item folder. Item 089: request.md, 06 or 07 that _read can't read
    gives ("UNREADABLE", "<path> unreadable"), never a status computed without it."""
    req_text, why = _read(item_dir / "request.md")
    if why:
        return "UNREADABLE", why
    scope, opened, (waived, waived_line, who) = parse_request(req_text)
    extra = f"; {waived_line}" if waived_line else ""
    if scope == "FAST" and not FAST_BY_PERSON.search(req_text):
        return "SKIPPED", f"FAST needs (person, <date>): only the person may shorten the pipeline (item 042){extra}"
    blocked = [s for s in waived if s in PERSON_ONLY and who != "person"]
    if blocked:
        return "SKIPPED", f"{scope}: {' '.join(blocked)} can be waived only by the person{extra}"
    need = [s for s in REQUIRED[scope] if s not in waived]
    have = [s for s in need if (item_dir / STEPS[s]).exists()]
    if not have and not any(f.name != "request.md" for f in item_dir.iterdir()):
        if opened is not None and (today - opened).days >= 1:
            return "STUCK", f"{scope}, opened {opened}, {(today - opened).days} day(s) with request.md only{extra}"
        return "not started", f"{scope}{extra}"
    last = max((need.index(s) for s in have), default=-1)
    gaps = [s for s in need[:last] if s not in have]
    if gaps:
        return "SKIPPED", f"{scope}: missing {' '.join(gaps)} before {need[last]}{extra}"
    results = sorted(f.name for f in item_dir.iterdir() if f.name != "request.md" and f.name not in STEPS.values())
    unchecked = [s for s in need[:need.index("03") + 1] if s not in have] if "03" in need else []
    if results and unchecked:
        return "SKIPPED", f"{scope}: {', '.join(results)} written before {' '.join(unchecked)}{extra}"
    if "06" in have:                                    # item 071: before A1's result (D7)
        ver_text, why = _read(item_dir / STEPS["06"])
        if why:
            return "UNREADABLE", why
        verdict, target = _i3_verdict_text(ver_text)
        if verdict == "FAIL":
            where = f"sent back to {target}" if target in ("I1", "I2", "I1 I2") else "sent back to: not stated"
            audit = item_dir / STEPS["07"]
            a1 = []
            if audit.exists():
                audit_text, why = _read(audit)
                if why:
                    return "UNREADABLE", why
                a1 = _a1_results(audit_text)
            if a1 and a1[-1].upper() != "FAIL":             # item 077: the item was completed
                return "I3 FAIL", (f"{scope}; {where}; 06 FAIL after A1 PASS in 07: a follow-up to a completed "
                                   f"item is a new item (run-item, items 053, 077){extra}")
            return "I3 FAIL", f"{scope}; {where}, needs a later PASS round in 06 (item 071){extra}"
    if len(have) == len(need):
        audit = item_dir / STEPS["07"]
        verdicts = []
        if audit.exists():
            audit_text, why = _read(audit)
            if why:
                return "UNREADABLE", why
            verdicts = _a1_results(audit_text)
        if item_dir.name not in PRE_A1_LINE and not verdicts:
            return "awaiting A1", f"{scope}{extra}"
        if verdicts and verdicts[-1].upper() == "FAIL":
            return "A1 FAIL", f"{scope}; sent back, needs a later A1 PASS line (item 042){extra}"
        return "complete", f"{scope}{extra}"
    return "in progress", f"{scope}: next {need[len(have)]}{extra}"


def log_fields_ok(agent, item, fields, new_rule=True, timed=True) -> bool:
    """Item 076: whether a log line's fields fit its agent's format for this item. I2 lines of items
    before TESTS_FORMAT_FROM use I2_BEFORE and need pass <= total; every other line LOG_FORMAT.
    Item 084: new_rule=False (the item's 05 was added under a rule file without TESTS_FORMAT_FROM)
    applies I2_BEFORE too; write_log never passes it. Item 090: an I2 line of an item from TIMED_FROM on
    must fullmatch I2_TIMED (the ` in <s>s` time is mandatory); timed=False (its 05 was added under a rule
    file without TIMED_FROM) applies LOG_FORMAT's optional time instead; write_log never passes it."""
    if agent == "I2" and (int(item) < TESTS_FORMAT_FROM or not new_rule):
        m = re.fullmatch(I2_BEFORE, fields.strip())
        return bool(m) and int(m[1]) <= int(m[2])
    if agent == "I2" and timed and int(item) >= TIMED_FROM:
        return bool(re.fullmatch(I2_TIMED, fields.strip()))
    return bool(re.fullmatch(LOG_FORMAT[agent], fields.strip()))


def log_hint(agent, item, new_rule=True, timed=True) -> str:
    """Item 076: the plain-words format that applies to this agent and item (LOG_HINT_BEFORE first).
    An ID that is not 3 digits (refused by write_log) gets the current form, never a traceback.
    Item 084: new_rule=False gives LOG_HINT_BEFORE, as in log_fields_ok. Item 090: from TIMED_FROM on
    (timed, the default) LOG_HINT_TIMED, as in log_fields_ok."""
    if agent in LOG_HINT_BEFORE and re.fullmatch(r"\d{3}", item) and (int(item) < TESTS_FORMAT_FROM
                                                                      or not new_rule):
        return LOG_HINT_BEFORE[agent][0]
    if agent in LOG_HINT_TIMED and timed and re.fullmatch(r"\d{3}", item) and int(item) >= TIMED_FROM:
        return LOG_HINT_TIMED[agent][0]
    return LOG_HINT[agent][0]


def _log_text(logs):
    """Items 043, 077: (text, whys): every research and implementation log file under `logs`, joined in
    file order ("" when the folders are absent). Item 089: a file _read can't read is left out of the
    text and its `<file> unreadable` is in whys, so a caller says not checked instead of computing from
    what is left."""
    texts, whys = [], []
    for sub in ("research", "implementation"):
        for f in (sorted((logs / sub).glob("*.md")) if (logs / sub).is_dir() else []):
            text, why = _read(f)
            if why:
                whys.append(why)
            else:
                texts.append(text)
    return "".join(texts), whys


def _logged(text, agent, item):
    """Items 043, 077: whether the log text holds a `| <agent> | <ID> |` line (its fields are not read)."""
    return re.search(rf"\|\s*{agent}\s*\|\s*{item}\s*\|", text) is not None


def uncommitted_steps(logs=Path("logs")):
    """Item 077 (RI-010): None without git, else (text after `UNCOMMITTED STEP: `, failed). A step file
    01-06 in the working tree that is not in `git ls-tree -r HEAD -- work/` and has no `| <agent> | <ID> |`
    log line is a cut-off run. Every item number is checked. A failing ls-tree is an error, never none.
    Item 089: an unreadable log file gives `not checked (<file> unreadable; item 089)`, never none."""
    if _git("rev-parse", "HEAD") is None:
        return None
    tree = _git("ls-tree", "-r", "--name-only", "HEAD", "--", "work/")
    if tree[1] != 0:
        return "git ls-tree HEAD failed (item 077)", True
    committed = set(tree[0].splitlines())
    text, whys = _log_text(logs)
    if whys:                                                # item 089: a lost log line could be any step's
        return f"not checked ({'; '.join(whys)}; item 089)", False
    entries = []
    for d in sorted(Path("work").glob("[0-9][0-9][0-9]")):
        if not d.is_dir():
            continue
        for s in sorted(AGENT):
            name = STEPS[s]
            if (d / name).exists() and f"work/{d.name}/{name}" not in committed \
                    and not _logged(text, AGENT[s], d.name):
                entries.append(f"{d.name} {name} (not in HEAD, no {AGENT[s]} log line; a cut-off run? item 077)")
    return "; ".join(entries) or "none", bool(entries)


def _anchor_env():
    """Items 084, 088 (RI-014): (env, failed). env is None when git can give the commit that added a
    step file; else the reason no anchor is read, and every item keeps the numeric cutoffs (strict):
    "no git"; "shallow clone; run git fetch --unshallow" when _shallow_boundaries (079) gives
    boundaries or "unreadable"; "unborn HEAD" when `rev-parse --verify -q HEAD` exits 1; any other
    exit gives "git rev-parse --verify HEAD failed (exit <n>)" with failed True (main exits 1). HEAD
    is read once per run here, not per pair in _rule_seen (item 088). Known gap: exit 1 means HEAD
    names no commit: unborn, or a ref git can't resolve; both are strict, and the second also fails
    UNCOMMITTED STEP's ls-tree HEAD (non-zero; 128 measured on a corrupt ref and a dangling symbolic
    HEAD, logs/audit/2026-11-21-088.md, item 091), so it is never a silent pass. Both print
    `not checked (unborn HEAD)`; the label is not accurate for the second (follow-up, not changed here)."""
    if _git("rev-parse", "--git-dir") is None:
        return "no git", False
    if _is_shallow():                                       # item 090: one source with open_branches
        return SHALLOW_TEXT, False
    head = _git("rev-parse", "--verify", "-q", "HEAD")
    if head is None:
        return "no git", False
    if head[1] == 0:
        return None, False
    if head[1] == 1:
        return "unborn HEAD", False
    return f"git rev-parse --verify HEAD failed (exit {head[1]})", True


def _rule_seen(item_dir, step, const, env):
    """Item 084 (RI-010): whether `const` (`^<const> = `) is in RULE_FILE in the tree of the commit
    that added work/<ID>/<step file> (default history simplification, no --first-parent).
    (True|False, sha7) when read; (None, "") with env set (_anchor_env: no git, shallow, unborn or a
    failed HEAD verify; HEAD is read once there, item 088) or an uncommitted file;
    (None, "<step> anchor: git failed (item 084)") on any failed git call and (None, "<step> anchor
    <sha7> has no RULE_FILE (item 084)") when the file is absent there. None keeps the strict rule."""
    if env is not None:
        return None, ""
    failed = f"{step} anchor: git failed (item 084)"
    sha, why = _git_ok("log", "--no-renames", "--diff-filter=A", "--format=%H", "-1", "--",
                       f"work/{item_dir.name}/{STEPS[step]}")
    if why:
        return None, failed
    sha = sha.strip()
    if not sha:
        return None, ""
    ls, why = _git_ok("ls-tree", "--name-only", sha, "--", RULE_FILE)
    if why:
        return None, failed
    if not ls.strip():
        return None, f"{step} anchor {sha[:7]} has no {RULE_FILE} (item 084)"
    text, why = _git_ok("show", f"{sha}:{RULE_FILE}")
    if why:
        return None, failed
    return re.search(rf"^{const} = ", text, re.M) is not None, sha[:7]


def _last_log_line(logs, agent, item):
    """Item 082: the item's last LOG_LINE match for `agent` in logs/implementation/????-??-??.md, by
    sorted file name then line order, or None. Item 089: a file _read can't read is skipped here; the
    caller (incomplete) runs this only when _log_text read every log file, so a skip is a race."""
    last = None
    impl = logs / "implementation"
    for f in (sorted(impl.glob("????-??-??.md")) if impl.is_dir() else []):
        text, why = _read(f)
        if why:
            continue
        for l in text.splitlines():
            m = LOG_LINE.match(l)
            if m and m[3] == agent and m[4] == item:
                last = m
    return last


def _suite_lines(text):
    """Item 082: the text after `Suite:` (stripped) of every column-0 `Suite:` line outside code fences
    and HTML comments (_md_lines "out" rows), in order."""
    return [line[len("Suite:"):].strip() for line, state in _md_lines(text)[0]
            if state == "out" and line.startswith("Suite:")]


def _unsure(item_dir, step, env, committed):
    """Item 095 (RI-014): True when a gated entry on `step` can't be judged: the clone is shallow
    (env == SHALLOW_TEXT, equality only; no git, unborn HEAD and a failed verify stay strict) and the
    step file is committed at HEAD (`committed`, from _head_work_files), or HEAD's tree could not be
    read (`committed` None: not checked, exit 1). An uncommitted step file gives False: a full clone
    keeps its entries too ((None, "") from _rule_seen, item 088), so a shallow clone keeps them (C1)."""
    if env != SHALLOW_TEXT:
        return False
    return committed is None or f"work/{item_dir.name}/{STEPS[step]}" in committed


def _head_work_files():
    """Item 095 (C1): the set of paths under work/ in HEAD's tree (never the index or the working tree),
    or None when the ls-tree fails (the caller then treats every gated entry as not checked)."""
    out, why = _git_ok("ls-tree", "-r", "--name-only", "HEAD", "--", "work/")
    return None if why else set(out.splitlines())


def incomplete(item_dir, logs=Path("logs"), env=None, not_seen=None, batch_nc=None, unchecked=None,
               committed=None):
    """Item 043: what is missing from a step's own checklist ([] = nothing). Item 084: a TESTS or
    VERDICT check that would fire is dropped only if the item's 05 / 06 was added under a rule file
    without that constant (_rule_seen False) and, for I2, every I2 line passes I2_BEFORE; each such
    pair is appended to `not_seen` as (ID, step, sha7, constant, rule item, old rule). Item 082: the
    Suite check (SUITE_FROM) is gated the same way, on 05. Item 089: an unreadable 06 is one entry
    `06 not checked (<why>; item 089)` in place of the RI-line, verdict-line and I3-line checks; an
    unreadable log file, for an item with any step file 01-06, is one entry `log lines not checked
    (<whys>; item 089)` in place of the unlogged, format, Suite and I3-line checks; an unreadable 05 at
    the Suite check is `05 not checked (<why>; item 089)`. Nothing is computed from what is left.
    Item 090: from TIMED_FROM on, an I2 line with no ` in <s>s` time is INCOMPLETE with the timed hint; when
    every I2 line of the item passes the untimed form it is gated on 05 by _rule_seen(TIMED_FROM): not seen
    gives the RULE NOT SEEN pair `judged by untimed I2 form` and no entry. Any other bad I2 line keeps the
    TESTS gate. batch_nc ({ID: reason}, from batch_log_items' not_computable): a BATCH_STRICT reason (by
    equality) of an ID from TIMED_FROM on is the entry `LOG BATCH not computable: <reason> (item 090)`, gated
    the same way (not seen: the pair `LOG BATCH not computable as text only`). Item 091: from ROUND_HEADING_FROM
    on, stray_run_headings of 05 and 06 is one entry per file, gated on that file by _rule_seen(ROUND_HEADING_FROM)
    (not seen: the pair `no round-heading check`); an unreadable file is `<step> round headings not checked`.
    Item 095 (RI-014): `unchecked` is a list of (ID, entry), like not_seen. Where a gate's anchor is not read
    and _unsure(item_dir, step, env, committed) is True (a shallow clone, the step file committed at HEAD or
    HEAD's tree unreadable), the entry goes to `unchecked` instead of the return value: the TIMED entry; the
    TESTS entry only when every own I2 line passes I2_BEFORE (else it is exact and stays); only I2 moves out
    of a format entry, other agents stay; LOG BATCH not computable; Suite; round headings (05 and 06); the
    verdict checks. With `unchecked` None (no caller collects it) nothing moves: strict, never dropped."""
    not_seen = [] if not_seen is None else not_seen

    def unsure(step):                                       # item 095: only when a caller collects them
        return unchecked is not None and _unsure(item_dir, step, env, committed)

    if not item_dir.name.isdigit() or int(item_dir.name) < CHECKLIST_FROM:
        return []
    missing = []
    ver = item_dir / STEPS["06"]
    ver_text, ver_why = _read(ver) if ver.exists() else (None, None)
    if ver_why:
        missing.append(f"06 not checked ({ver_why}; item 089)")
    elif ver_text is not None and not re.search(r"^.*Recurring issues checked:.*RI-\d", ver_text, re.M):
        missing.append("06 has no 'Recurring issues checked: RI-...' line")
    text, log_whys = _log_text(logs)
    if log_whys:
        if any((item_dir / STEPS[s]).exists() for s in AGENT):
            missing.append(f"log lines not checked ({'; '.join(log_whys)}; item 089)")
    unlogged = [AGENT[s] for s in sorted(AGENT) if (item_dir / STEPS[s]).exists()
                and not _logged(text, AGENT[s], item_dir.name)] if not log_whys else []
    if unlogged:
        missing.append(f"no log line for {' '.join(unlogged)}")
    if int(item_dir.name) >= LOG_CHECK_FROM and not log_whys:
        bad = sorted({m[3] for m in (LOG_LINE.match(l) for l in text.splitlines())
                      if m and m[4] == item_dir.name and not log_fields_ok(m[3], m[4], m[5])})
        new_rule, note = True, ""
        own_i2 = [m for m in (LOG_LINE.match(l) for l in text.splitlines())
                  if m and m[3] == "I2" and m[4] == item_dir.name]
        if "I2" in bad and int(item_dir.name) >= TIMED_FROM \
                and all(log_fields_ok("I2", m[4], m[5], timed=False) for m in own_i2):   # item 090: TIMED gate
            seen, sha7 = _rule_seen(item_dir, "05", "TIMED_FROM", env)
            note = sha7 if seen is None else ""             # a git-failed or no-file note; "" otherwise
            if seen is False:
                bad.remove("I2")
                not_seen.append((item_dir.name, "05", sha7, "TIMED_FROM", "090", "untimed I2 form"))
            elif unsure("05"):   # item 095: anchor not read in a shallow clone
                bad.remove("I2")
                unchecked.append((item_dir.name, f"log line for I2 does not match its format (item 045): "
                                                 f'I2 wants "{log_hint("I2", item_dir.name, new_rule)}"'))
        elif "I2" in bad and int(item_dir.name) >= TESTS_FORMAT_FROM:    # item 084: TESTS gate
            seen, sha7 = _rule_seen(item_dir, "05", "TESTS_FORMAT_FROM", env)
            note = sha7 if seen is None else ""             # a git-failed or no-file note; "" otherwise
            if seen is False:
                new_rule = False
                if all(log_fields_ok("I2", m[4], m[5], new_rule=False)
                       for m in (LOG_LINE.match(l) for l in text.splitlines())
                       if m and m[3] == "I2" and m[4] == item_dir.name):
                    bad.remove("I2")
                    not_seen.append((item_dir.name, "05", sha7, "TESTS_FORMAT_FROM", "076", "I2_BEFORE"))
            elif unsure("05") \
                    and all(log_fields_ok("I2", m[4], m[5], new_rule=False) for m in own_i2):   # item 095
                bad.remove("I2")
                unchecked.append((item_dir.name, f"log line for I2 does not match its format (item 045): "
                                                 f'I2 wants "{log_hint("I2", item_dir.name, new_rule)}"'))
        if bad:
            wants = "; ".join(f'{a} wants "{log_hint(a, item_dir.name, new_rule)}"' for a in bad)
            missing.append(f"log line for {' '.join(bad)} does not match its format (item 045): {wants}")
        if note:
            missing.append(note)
    nc = (batch_nc or {}).get(item_dir.name)
    if nc in BATCH_STRICT and int(item_dir.name) >= TIMED_FROM:   # item 090 step 2: equality, never a substring
        seen, sha7 = _rule_seen(item_dir, "05", "TIMED_FROM", env)
        if seen is False:
            not_seen.append((item_dir.name, "05", sha7, "TIMED_FROM", "090", "LOG BATCH not computable as text only"))
        elif unsure("05"):    # item 095
            unchecked.append((item_dir.name, f"LOG BATCH not computable: {nc} (item 090)"))
        else:
            missing += [f"LOG BATCH not computable: {nc} (item 090)"] + \
                ([sha7] if seen is None and sha7 and sha7 not in missing else [])   # the same 05 note once
    report = item_dir / STEPS["05"]
    if int(item_dir.name) >= SUITE_FROM and report.exists() and not log_whys:   # item 082: Suite = last I2 field
        last = _last_log_line(logs, "I2", item_dir.name)
        # else 043/045 report it; item 090: timed=False, so an untimed field still gets its Suite check (a
        # RULE NOT SEEN TIMED_FROM item has no format entry, and a seen one has both entries)
        if last is not None and log_fields_ok("I2", item_dir.name, last[5], timed=False):
            field = last[5].strip().split(" | tests ", 1)[1]
            body, why05 = _read(report)
            suites = _suite_lines(body) if why05 is None else []
            fired = None
            if why05:
                missing.append(f"05 not checked ({why05}; item 089)")
            elif not suites:
                fired = "05 has no 'Suite:' line (item 082)"
            elif len(suites) > 1:
                fired = f"05 has {len(suites)} 'Suite:' lines, needs exactly 1 (item 082)"
            elif suites[0] != field:
                fired = f"05 Suite line does not equal the last I2 log tests field (item 082): '{suites[0]}' vs '{field}'"
            if fired:                                       # item 084 gate, only when one fires
                seen, sha7 = _rule_seen(item_dir, "05", "SUITE_FROM", env)
                if seen is False:                           # below SUITE_FROM there is no Suite check
                    not_seen.append((item_dir.name, "05", sha7, "SUITE_FROM", "082", "no Suite check"))
                elif unsure("05"):    # item 095
                    unchecked.append((item_dir.name, fired))
                else:
                    missing += [fired] + ([sha7] if seen is None and sha7 else [])
    if int(item_dir.name) >= ROUND_HEADING_FROM:            # item 091: run headings LOG BATCH can't read
        for step in ("05", "06"):
            heads, why = stray_run_headings(item_dir / STEPS[step], RUN_HEADING[step])
            if why:
                missing.append(f"{step} round headings not checked ({why}; item 091)")
            elif heads:
                named = "', '".join(heads)
                fired = (f"{step} heading '{named}' is not read by LOG BATCH; use '## Test output (round N, "
                         f"pasted)' / '## Tests re-run (round N)' (item 091)")
                seen, sha7 = _rule_seen(item_dir, step, "ROUND_HEADING_FROM", env)   # item 084 gate
                if seen is False:                           # below ROUND_HEADING_FROM there is no such check
                    not_seen.append((item_dir.name, step, sha7, "ROUND_HEADING_FROM", "091",
                                     "no round-heading check"))
                elif unsure(step):    # item 095
                    unchecked.append((item_dir.name, fired))
                else:
                    missing += [fired] + ([sha7] if seen is None and sha7 else [])
    if ver_text is not None:                                # item 071 (a)-(d); item 089: 06 was read
        verdict, target = _i3_verdict_text(ver_text)
        if int(item_dir.name) >= VERDICT_FROM:
            fired = []
            if verdict is None:
                fired.append("06 has no readable 'Verdict: PASS' or 'Verdict: FAIL' line (item 071)")
            elif verdict == "FAIL" and target not in ("I1", "I2", "I1 I2"):
                fired.append("06 Verdict is FAIL but has no 'Sent back to: I1, I2 or I1 I2' line (item 071)")
            elif verdict == "PASS" and target != "none":
                fired.append("06 Verdict is PASS but has no 'Sent back to: none' line (item 071)")
            if fired:                                       # item 084: VERDICT gate, only when one fires
                seen, sha7 = _rule_seen(item_dir, "06", "VERDICT_FROM", env)
                if seen is False:                           # below VERDICT_FROM there is no verdict-line check
                    not_seen.append((item_dir.name, "06", sha7, "VERDICT_FROM", "071", "no Sent-back check"))
                elif unsure("06"):    # item 095
                    unchecked += [(item_dir.name, f) for f in fired]
                else:
                    missing += fired + ([sha7] if seen is None and sha7 else [])
        if verdict is not None and not log_whys:           # item 089: no I3-line check on a lost log
            last = None                                     # the item's last I3 line: by file date, then line order
            impl = logs / "implementation"
            for f in (sorted(impl.glob("????-??-??.md")) if impl.is_dir() else []):
                lines, why = _read(f)
                if why:                                     # only a race: _log_text read every file above
                    continue
                for l in lines.splitlines():
                    m = LOG_LINE.match(l)
                    if m and m[3] == "I3" and m[4] == item_dir.name:
                        last = m
            w = re.fullmatch(LOG_FORMAT["I3"], last[5].strip()) if last else None
            if w and w[1] != verdict:                       # malformed last line: 045's, no fallback (C2)
                missing.append(f"06 Verdict says {verdict}, last I3 log line says {w[1]} (item 071)")
    return missing


def _sent_back(item, logs=Path("logs")):
    """Item 086 (rule D): whether the item was ever sent back: a log line of R3, I1 or I3 whose fields
    fullmatch LOG_FORMAT with the SEND_BACK word in its group (never a substring, RI-012), or an
    `A1 result: FAIL` line in work/<ID>/07 (_a1_results, case-insensitive as in classify). An unreadable
    log file or 07 adds no send-back (the refusal side)."""
    for team in ("research", "implementation"):
        folder = logs / team
        for f in (sorted(folder.glob("????-??-??.md")) if folder.is_dir() else []):
            text, why = _read(f)
            if why:
                continue
            for m in map(LOG_LINE.match, text.splitlines()):
                if m and m[4] == item and m[3] in SEND_BACK:
                    group, word = SEND_BACK[m[3]]
                    v = re.fullmatch(LOG_FORMAT[m[3]], m[5].strip())
                    if v and v[group] == word:
                        return True
    audit = Path("work") / item / STEPS["07"]
    audit_text, why = _read(audit) if audit.exists() else ("", None)
    results = _a1_results(audit_text) if why is None else []
    return any(r.upper() == "FAIL" for r in results)


def _first_verdict(path, agent):
    """Item 090 (RI-012): (word, None) from the first column-0 line outside code fences and HTML comments
    (_md_lines "out") of `path` that starts with agent's label (VERDICT_OF), matched by its pattern; never a
    later line, never a substring. (None, "absent") with no file, (None, "<file> unreadable") when _read
    can't read it, (None, "no readable <label> line") when that line is missing or holds no verdict word
    (e.g. the unfilled template line)."""
    rx = VERDICT_OF[agent][1]
    label = rx.pattern[:rx.pattern.index(":") + 1]
    if not path.exists():
        return None, "absent"
    text, why = _read(path)
    if why:
        return None, why
    line = next((l for l, state in _md_lines(text)[0] if state == "out" and l.startswith(label)), None)
    m = rx.match(line) if line is not None else None
    return (m[1], None) if m else (None, f"no readable {label} line")


def _round_refusal(item, agent, logs=Path("logs")):
    """Item 090 (rule D after a send-back, RI-010): why `--log <agent> <item>` is refused for an item that
    was sent back (_sent_back), or None. The item's log lines (_item_lines, sorted by stamp, file, line):
    (a) L = the latest send-back line (SEND_BACK fullmatch), by S; while no later S line exists the round is
    open, and a step after S is refused (S must log again first). (b) In that open round a step before S
    is refused when S's file (VERDICT_OF, _first_verdict) no longer shows the send-back word, or is
    absent, unreadable or has no readable verdict line: S ran again before this line. (c) start = the latest
    send-back or terminal line (I3 PASS; R3 READY for RESEARCH ONLY, Scope from request.md), else the item's
    first line; a line after start with a later step than <agent> is refused (steps in order). An
    unreadable log file or request.md, or a line with no valid time, refuses (order not checked), never a
    pass."""
    lines, unreadable = _item_lines(logs)
    if unreadable:
        return f"{'; '.join(unreadable)}; order not checked (item 090)"
    if any(r[0] is None for r in lines.get(item, [])):
        return f"work/{item} has a log line with no valid time; order not checked (item 090)"
    rows = sorted(lines.get(item, []), key=lambda r: (r[0], r[3], r[4]))
    step = {a: s for s, a in AGENT.items()}

    def word(r, group):
        v = re.fullmatch(LOG_FORMAT[r[1]], r[5].strip())
        return v[group] if v else None

    sends = [k for k, r in enumerate(rows) if r[1] in SEND_BACK and word(r, SEND_BACK[r[1]][0]) == SEND_BACK[r[1]][1]]
    if sends:
        last = rows[sends[-1]]
        sender = last[1]
        if not any(r[1] == sender for r in rows[sends[-1] + 1:]):           # the round is open
            if step[agent] > step[sender]:                                  # (a)
                return (f"{sender} sent work/{item} back at {last[0]:%Y-%m-%d %H:%M} and has not logged again; "
                        f"{sender} runs before {agent} (item 090)")
            if step[agent] < step[sender]:                                  # (b)
                code, _ = VERDICT_OF[sender]
                found, why = _first_verdict(Path("work") / item / STEPS[code], sender)
                want = SEND_BACK[sender][1]
                if why or found != want:
                    return (f"work/{item}/{STEPS[code]} no longer says {want} ({found or why}); {sender} ran again "
                            f"before this line: log each step before the next one runs (item 090)")
    req_text, why = _read(Path("work") / item / "request.md")               # item 089's reader
    if why:                                                                 # Scope unknown: never a default
        return f"{why}; order not checked (item 090)"
    research_only = parse_request(req_text)[0] == "RESEARCH ONLY"
    terminal = ("R3", 2, "READY") if research_only else ("I3", 1, "PASS")
    marks = [k for k, r in enumerate(rows) if k in sends or (r[1] == terminal[0] and word(r, terminal[1]) == terminal[2])]
    start = marks[-1] if marks else 0
    after = [r for r in rows[start + 1:] if step[r[1]] > step[agent]]       # (c)
    if rows and after:
        first = rows[start]
        return (f"{after[0][1]} already logged at {after[0][0]:%H:%M} after {first[1]} {first[0]:%H:%M}; "
                f"log steps in order (item 090)")
    return None


def write_log(agent, item, fields, now=None):
    """Item 045: append `HH:MM | agent | ID | fields` (UTC) to today's research or implementation
    log. Exit code 2 and nothing written when the agent, ID or fields are not in the format.
    Item 086 (rule D): also refused while a later step file 01-06 of the item exists (07 and other
    files never count), unless the item was sent back (_sent_back). Item 090: a sent-back item is checked
    by _round_refusal instead (open round, sender's verdict, step order)."""
    if agent not in LOG_FORMAT or not re.fullmatch(r"\d{3}", item) \
            or not log_fields_ok(agent, item, fields):   # order matters: the ID check runs before int(item)
        print(f"--log refused: {agent} | {item} | {fields} does not match "
              f"{chr(34) + log_hint(agent, item) + chr(34) if agent in LOG_HINT else 'an agent R1 R2 R3 I1 I2 I3'}",
              file=sys.stderr)
        return 2
    if not (Path("work") / item / "request.md").exists():
        print(f"--log refused: no work/{item}/request.md (item 047)", file=sys.stderr)
        return 2
    step = next(s for s, a in AGENT.items() if a == agent)
    later = [STEPS[s] for s in sorted(AGENT) if s > step and (Path("work") / item / STEPS[s]).exists()]
    sent = _sent_back(item)
    if later and not sent:
        print(f"--log refused: work/{item}/ already has {' '.join(later)} after {agent}'s step; write this "
              f"line before the later steps run, then redo those steps (item 086)", file=sys.stderr)
        return 2
    elif sent:                                              # item 090: the round rule replaces "D off"
        why = _round_refusal(item, agent)
        if why:
            print(f"--log refused: {why}", file=sys.stderr)
            return 2
    now = now or dt.datetime.now(dt.timezone.utc)
    team = "research" if agent[0] == "R" else "implementation"
    log = Path("logs") / team / f"{now:%Y-%m-%d}.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    head = "" if log.exists() else f"# {team.capitalize()} log - {now:%Y-%m-%d}\n\n"
    line = f"{now:%H:%M} | {agent} | {item} | {fields.strip()}"
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"{head}{line}\n")
    print(line)
    return 0


def orphan_log_lines():
    """Item 047: (orphans, whys): `<ID> (<log file>)` for every agent log line whose work/<ID>/ folder is
    missing. Item 089: a log file _read can't read is not checked; its `<file> unreadable` is in whys."""
    orphans, whys = [], []
    for team in ("research", "implementation"):
        for f in sorted((Path("logs") / team).glob("????-??-??.md")):
            text, why = _read(f)
            if why:
                whys.append(why)
                continue
            ids = {m[4] for m in map(LOG_LINE.match, text.splitlines()) if m}
            orphans += [f"{i} ({f.as_posix()})" for i in sorted(ids) if not (Path("work") / i).is_dir()]
    return orphans, whys


def late_log_lines(shallow=False):
    """Item 045: committed log lines (items from LOG_CHECK_FROM on) timed after the commit that
    added them, by `git blame`. None when git is not available here. Item 081: a log file not in
    HEAD's tree (`git ls-tree`) is uncommitted and skipped; a failed ls-tree is the one entry
    `git ls-tree HEAD failed (item 081)`, and a failed blame of a committed file is an entry.
    Item 090 (RI-014): False (falsy, not None) in a shallow clone, where blame gives the boundary's
    commit to older lines: main prints `LOG TIME: not checked (SHALLOW_TEXT)`, exit unchanged."""
    if _git("rev-parse", "HEAD") is None:
        return None
    if shallow:
        return False
    tree, why = _git_ok("ls-tree", "-r", "--name-only", "HEAD", "--", "logs/research/", "logs/implementation/")
    if why:
        return ["git ls-tree HEAD failed (item 081)"]
    committed = set(tree.splitlines())
    late = []
    for team in ("research", "implementation"):
        for f in sorted((Path("logs") / team).glob("????-??-??.md")):
            if f.as_posix() not in committed:
                continue                                    # uncommitted: nothing to blame
            blame, why = _git_ok("blame", "--line-porcelain", "--", str(f))
            if why:
                late.append(f"{f.as_posix()} (git blame failed; item 081)")
                continue
            ctime = None
            for row in blame.splitlines():
                if row.startswith("committer-time "):
                    ctime = int(row.split()[1])
                elif row.startswith("\t"):
                    m = LOG_LINE.match(row[1:])
                    if m and ctime and int(m[4]) >= LOG_CHECK_FROM and m[4] not in LOG_TIME_EXCEPT:
                        stated = dt.datetime.fromisoformat(f"{f.stem}T{m[1]}:{m[2]}+00:00")
                        commit = dt.datetime.fromtimestamp(ctime, dt.timezone.utc).replace(second=0)
                        if stated > commit:
                            late.append(f"{m[4]} {m[3]} ({f.stem} {m[1]}:{m[2]} after commit "
                                        f"{commit:%Y-%m-%d %H:%M} UTC)")
                    ctime = None
    return late


def _item_lines(logs):
    """Item 086 (rule C): ({ID: [(stamp, agent, team, file index, line index, fields), ...]}, unreadable) over
    every LOG_LINE-shaped line in logs/research/????-??-??.md and logs/implementation/????-??-??.md,
    whatever its fields (a malformed line still marks when a step logged; 086 change 3). stamp is the
    file's date + HH:MM (UTC), or None when that is not a valid time. unreadable: `<file> unreadable`
    for a file that can't be read (OSError, non-UTF-8), never skipped silently."""
    lines, unreadable, index = {}, [], 0
    for team in ("research", "implementation"):
        folder = logs / team
        for f in (sorted(folder.glob("????-??-??.md")) if folder.is_dir() else []):
            index += 1
            text, why = _read(f)
            if why:
                unreadable.append(why)
                continue
            for n, row in enumerate(text.splitlines()):
                m = LOG_LINE.match(row)
                if not m:
                    continue
                try:
                    stamp = dt.datetime.fromisoformat(f"{f.stem}T{m[1]}:{m[2]}+00:00")
                except ValueError:
                    stamp = None
                lines.setdefault(m[4], []).append((stamp, m[3], team, index, n, m[5]))
    return lines, unreadable


def _run_seconds(path, heading):
    """Item 086 (rule C): (every SUMMARY_LINE time in seconds inside every section of `path` that starts
    with a line matching `heading` outside code fences, None). A section ends at the next `# ` or `## `
    heading outside fences; summary lines count outside or inside fences (pytest output is usually
    fenced); HTML comments are dropped (_md_lines). ([], None) when the file is absent, ([], "<file>
    unreadable") when it can't be read."""
    if not path.exists():
        return [], None
    text, why = _read(path)
    if why:
        return [], why
    rows, _ = _md_lines(text)
    found = []
    for (line, state), inside in zip(rows, _section_flags(rows, heading)):
        if inside and state in ("out", "in"):
            m = SUMMARY_LINE.match(line.strip())
            if m:
                found.append(float(m[1]))
    return found, None


def _section_flags(rows, heading):
    """Item 091: one bool per _md_lines row, True when the row is inside a section _run_seconds reads: an
    "out" row matching `heading` (re.match) opens it and is itself False; an "out" row matching `#{1,2} `
    closes it and is False. The one open/close rule shared by _run_seconds and stray_run_headings."""
    flags, inside = [], False
    for line, state in rows:
        if state == "out" and re.match(heading, line):
            flags.append(False)
            inside = True
        elif state == "out" and re.match(r"#{1,2} ", line):
            flags.append(False)
            inside = False
        else:
            flags.append(inside)
    return flags


def stray_run_headings(path, opener):
    """Item 091 (RI-010): (headings, None): every "out" row of `path` that matches STRAY_RUN_HEADING, is not
    `opener` (re.match) and is outside every section `opener` starts (_section_flags), so LOG BATCH never
    reads the runs under it. ([], None) when the file is absent; ([], "<file> unreadable") when _read fails."""
    text, why = _read(path, missing_ok=True)
    if why:
        return [], why
    if text is None:
        return [], None
    rows, _ = _md_lines(text)
    return [line for (line, state), inside in zip(rows, _section_flags(rows, opener))
            if state == "out" and not inside and STRAY_RUN_HEADING.match(line) and not re.match(opener, line)], None


def batch_log_items(work=Path("work"), logs=Path("logs"), excepted=None):
    """Item 086 (rule C, RI-010): items whose pytest runs could not fit between their log lines.
    For each ID >= LOG_CHECK_FROM with work/<ID>/: start = the item's latest log line before its first
    I2 line (research lines with a stamp <= that I2's count as before; implementation lines with the
    same stamp only if above it), end = its last I3 line, delta = whole minutes end - start. t05 = the
    largest time of the item's I2 log fields and of 05's `## Test output` sections; t06 = the largest
    of 06's `## Tests re-run` sections after dropping any value equal (to 0.01 s) to a t05 candidate
    (a copy); k = the number of known values. Flag when t05 + t06 - BATCH_ROUND*k >= (delta+1)*60.
    excepted (None = LOG_BATCH_EXCEPT) items are counted and listed with their reason, never evaluated.
    No I2 line: skipped. No I3 line after the last I2 line: in_progress (a round is open). No line
    before the first I2, no time at all (k = 0), an unreadable 05/06/log file or a line with no valid
    time: not_computable with the reason, never flagged and never read as 0 s.
    Item 090 (per-round bound): before the in-progress skip, every I2 line whose tests part is a
    SUMMARY_LINE with time t is checked against prev = the item's latest line before it (the same order
    rule as start), Δ = whole minutes prev -> I2: flagged when t - BATCH_ROUND >= (Δ+1)*60, since I2 runs
    the suite after prev's line and before its own. An I2 line with no prev is not evaluated (the whole-item
    rule's "no line before I2" covers it). It only catches rounds whose run is longer than the gap allows:
    with today's 74-93 s runs, same-minute (Δ0) batches; Δ >= 1 batches pass it.
    Item 093: with no line before the first I2, request.md is read (_read, missing_ok); if the person waived
    every pre-05 step of the Scope with a date on the first `Waived:` line and none of those files exists
    (_person_waived_before_i2), the reason is `no line before I2 (<steps> waived by the person, first I2
    round not bounded, item 093)`, which is not in BATCH_STRICT. The first I2 round of such an item has no
    prev, so nothing in LOG BATCH evaluates it (LOG TIME still applies). Only the first Waived line is read
    (gap j). A missing or unreadable request.md, or any other waiver, keeps "no line before I2".
    Returns {flagged, flagged_ids, excepted, not_computable, checked, in_progress}."""
    excepted = LOG_BATCH_EXCEPT if excepted is None else excepted
    order = lambda r: (r[0], r[3], r[4])                    # stamp, then file and line order
    lines, bad_logs = _item_lines(logs)
    out = {"flagged": [], "flagged_ids": [], "excepted": [], "not_computable": [], "checked": 0,
           "in_progress": []}
    for d in (sorted(work.glob("[0-9][0-9][0-9]")) if work.is_dir() else []):
        item = d.name
        if not d.is_dir() or int(item) < LOG_CHECK_FROM:
            continue
        rows = lines.get(item, [])
        i2 = [r for r in rows if r[1] == "I2"]
        if not i2 and not bad_logs:
            continue                                        # not built yet: nothing to check
        if bad_logs:                                        # a lost line could move start or end
            out["checked"] += 1
            out["not_computable"].append((item, "; ".join(bad_logs)))
            continue
        if any(r[0] is None for r in rows):
            out["checked"] += 1
            out["not_computable"].append((item, "log line with no valid time"))
            continue
        if item not in excepted:                            # item 090: per-round bound, before the in-progress skip
            for r in sorted(i2, key=order):
                m = re.match(r"\d+ files? changed \| tests (.*)", r[5].strip())
                s = SUMMARY_LINE.match(m[1]) if m else None
                if not s:
                    continue                                # no time: not evaluated (never read as 0 s)
                prev = [x for x in rows if x is not r
                        and (x[0] <= r[0] if x[2] == "research" else order(x) < order(r))]
                if not prev:
                    continue
                p = max(prev, key=order)
                t, gap = float(s[1]), int((r[0] - p[0]).total_seconds()) // 60
                limit = (gap + 1) * 60
                if round(t - BATCH_ROUND, 3) >= limit:
                    if item not in out["flagged_ids"]:
                        out["flagged_ids"].append(item)
                    out["flagged"].append(f"{item} I2 at {r[0]:%Y-%m-%d %H:%M} ({t:.2f} s pytest run after the "
                                          f"{p[1]} line at {p[0]:%H:%M}, limit {limit} s; impossible under the "
                                          f"run-item order, item 090)")
        first, last_i2 = min(i2, key=order), max(i2, key=order)
        i3 = [r for r in rows if r[1] == "I3"]
        end = max(i3, key=order) if i3 else None
        if end is None or order(end) < order(last_i2):
            out["in_progress"].append(item)                 # a round is open: its runs may lie after end
            continue
        out["checked"] += 1
        if item in excepted:
            if (d / "request.md").exists():
                out["excepted"].append((item, excepted[item]))
            continue
        before = [r for r in rows if (r[0] <= first[0] if r[2] == "research" else order(r) < order(first))]
        if not before:
            text, why = _read(d / "request.md", missing_ok=True)
            pre = _person_waived_before_i2(text, d) if why is None and text is not None else None
            out["not_computable"].append((item, f"no line before I2 ({' '.join(pre)} waived by the person, first "
                                                f"I2 round not bounded, item 093)" if pre else "no line before I2"))
            continue
        start = max(before, key=order)
        delta = int((end[0] - start[0]).total_seconds()) // 60
        t05, why05 = _run_seconds(d / STEPS["05"], RUN_HEADING["05"])
        t06, why06 = _run_seconds(d / STEPS["06"], RUN_HEADING["06"])
        why = "; ".join(w for w in (why05, why06) if w)
        if why:
            out["not_computable"].append((item, why))
            continue
        for r in i2:                                        # the I2 field's tests part, as printed (076)
            m = re.match(r"\d+ files? changed \| tests (.*)", r[5].strip())
            s = SUMMARY_LINE.match(m[1]) if m else None
            if s:
                t05.append(float(s[1]))
        kept06 = [v for v in t06 if all(round(v * 100) != round(c * 100) for c in t05)]
        known = ([max(t05)] if t05 else []) + ([max(kept06)] if kept06 else [])
        if not known:
            out["not_computable"].append((item, "no pytest time in 05/06/I2 line"))
            continue
        total, limit = sum(known), (delta + 1) * 60
        if round(total - BATCH_ROUND * len(known), 3) >= limit:   # values have 2 decimals: round off float noise
            if item not in out["flagged_ids"]:              # item 090: a round may have flagged it already
                out["flagged_ids"].append(item)
            out["flagged"].append(f"{item} ({total:.2f} s of pytest runs between {start[0]:%Y-%m-%d %H:%M} and "
                                  f"{end[0]:%H:%M} UTC, limit {limit} s; impossible under the run-item order, "
                                  f"item 086)")
    return out


def _git(*args):
    """stdout and exit code of a git command in the current directory, or None if git is
    missing or this directory is not the top of a git work tree. Output that is not UTF-8 is
    decoded with `replace`, never a traceback; the top-level path is compared as bytes decoded
    by os.fsdecode, as Path.cwd() is (item 081)."""
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True)
        if top.returncode != 0 or Path(os.fsdecode(top.stdout.strip())).resolve() != Path.cwd().resolve():
            return None
        r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
    except FileNotFoundError:
        return None
    return r.stdout, r.returncode


def _git_ok(*args):
    """Item 081 (RI-014): (stdout, None) when git exits 0; (None, "no git") when _git is None
    (git missing, or not the top of a work tree); (stdout, "git <args[0]> failed (exit <code>)")
    on any other exit. The reason never holds git's stderr. A caller treats any reason other than
    "no git" as an error, never as none, 0 or []."""
    out = _git(*args)
    if out is None:
        return None, "no git"
    if out[1] != 0:
        return out[0], f"git {args[0]} failed (exit {out[1]})"
    return out[0], None


def fetch_coverage():
    """Item 094 (RI-014): does origin's fetch refspec bring every branch into refs/remotes/origin/?
    Returns exactly one of "full", "no origin", "no git", SINGLE_TEXT or `git config failed (exit <n>)`.
    Reads `git config --get-all remote.origin.fetch` (all values, so a glob line before a named one still
    counts; `--includes` is on by default for reads, so an [include] line counts as git fetch sees it):
    exit 0 is "full" only if at least one value, with one leading `+` removed, equals _GLOB and no value
    starts with `^`; anything else (no value, named branches only, another dst, two `+`) is SINGLE_TEXT.
    A `^` line of any kind gives SINGLE_TEXT, even one that would hide no claude/* branch: this over-reports
    "not checked" and fails closed on purpose (C7). Exit 1 means the key is absent: git-config also uses
    exit 1 for an invalid section or key, but both keys here are fixed constants, so for us it means only
    absent; a later edit that builds a key from input must revisit this (C5). Then `git config --get
    remote.origin.url`: exit 1 is "no origin" (today's path), exit 0 is SINGLE_TEXT (a fetch line was
    removed), any other exit is the error string. Any other exit on the fetch read is the error string,
    never "full". A clone of a detached HEAD with --single-branch has no fetch line or a non-glob one, so
    it is SINGLE_TEXT too (C6). _git is called directly (not _git_ok) because exit 1 is an answer here.
    Known gaps: a full refspec never fetched still has only local refs (the rule files require `git fetch
    origin` first; ls-remote would need the network), and remotes other than origin are not checked
    (item 094)."""
    out = _git("config", "--get-all", "remote.origin.fetch")
    if out is None:
        return "no git"
    if out[1] == 0:
        values = [v for v in out[0].splitlines() if v]
        full = any((v[1:] if v.startswith("+") else v) == _GLOB for v in values)
        return "full" if full and not any(v.startswith("^") for v in values) else SINGLE_TEXT
    if out[1] != 1:
        return f"git config failed (exit {out[1]})"
    url = _git("config", "--get", "remote.origin.url")
    if url is None:
        return "no git"
    if url[1] == 1:
        return "no origin"
    if url[1] == 0:
        return SINGLE_TEXT
    return f"git config failed (exit {url[1]})"


def open_branches(today=None, shallow=None):
    """One dict per remote branch not merged into HEAD (items 034, 037, 038, 039): ref, items
    {item: set of step codes}, conflicts, recurring, clashes, skipped [(item, detail)],
    failed [(item, status, detail)] (item 077: I3 FAIL or A1 FAIL, never an item in skipped), last,
    errors [why] (item 081: a git read of this branch that failed; BRANCH ERROR), unrelated (item
    081 r2: True when merge-base --all exits 1; such a ref is not scanned, and its errors say whether
    it holds checked paths). None without git; the reason string when `git branch` itself fails
    (item 081), never []. Item 090 (RI-014): shallow (None = _is_shallow(), so check_handoff's call with
    no args computes it): main_ahead is not called (behind False), origin/main itself is skipped (its tip
    looks unreachable from a shallow HEAD), every dict has "shallow", and an unrelated ref with checked
    paths gets the shallow-clone error text. Item 095 (RI-014): an unrelated ref's dict also has "held", the
    number of files on checked paths in its tree, or None when that ls-tree failed (main folds shallow
    unrelated refs on it, never on error text). Item 094 (RI-014): after a successful branch read, fetch_coverage
    is read; SINGLE_TEXT or `git config failed (exit <n>)` is returned as the reason string (item 094)."""
    out, why = _git_ok("branch", "-r", "--no-merged", "HEAD", "--format=%(refname:short)")
    if why == "no git":
        return None
    if why:
        return why
    cov = fetch_coverage()                                  # item 094: after the branch read, before shallow
    if cov == SINGLE_TEXT or cov.startswith("git config failed"):
        return cov
    today = today or dt.datetime.now(dt.timezone.utc).date()
    shallow = _is_shallow() if shallow is None else shallow
    behind = not shallow and isinstance(a := main_ahead(), int) and a > 0
    found = []
    for ref in out.split():
        if ref.endswith("/HEAD") or "/" not in ref:
            continue
        if shallow and ref == MAIN:                         # item 090: MAIN AHEAD says not checked
            continue
        # HEAD is behind main: main and refs already in main are not open work (item 051)
        if behind and (ref == MAIN or _git("merge-base", "--is-ancestor", ref, MAIN)[1] == 0):
            continue
        when = _git("log", "-1", "--format=%cs", ref)
        last = dt.date.fromisoformat(when[0].strip()) if when and when[1] == 0 and when[0].strip() else None
        mb = _git("merge-base", "--all", "HEAD", ref)      # item 081 r2: exit 1 = no common ancestor (real answer)
        if mb is not None and mb[1] == 1:
            held, why = _git_ok("ls-tree", "-r", "--name-only", ref, "--", "work/", RECURRING,
                                *RULE_PATHS, *RESEARCH_CODE_PATHS)
            held = held.splitlines() if why is None else []
            count = len(held) if why is None else None      # item 095: None = not known, never 0
            errors = ([why] if why else
                      [f"shallow clone; {len(held)} file(s) on checked paths (first: {held[0]}) not checked; "
                       f"run git fetch --unshallow (item 090)" if shallow else
                       f"no common history with HEAD; {len(held)} file(s) on checked paths "
                       f"(first: {held[0]}) not checked (item 081)"] if held else [])
            found.append({"ref": ref, "items": {}, "conflicts": None, "recurring": False, "clashes": [],
                          "skipped": [], "failed": [], "last": last, "rules": [], "errors": errors,
                          "unrelated": True, "shallow": shallow, "held": count})
            continue
        merge = _git("merge-tree", "--write-tree", "--name-only", "--no-messages", "HEAD", ref)
        conflicts = None
        if merge is not None and merge[1] in (0, 1):
            conflicts = merge[0].splitlines()[1:] if merge[1] == 1 else []
        # what merging the branch would change: HEAD vs the merge result. `HEAD...ref` uses one
        # merge base, so with two (criss-cross) a PR already merged looks like this branch's (052)
        tree = merge[0].split()[0] if conflicts is not None and merge[0].strip() else None
        errors = []                                         # item 081: BRANCH ERROR

        def changed(*paths):
            if tree:
                diff, why = _git_ok("diff", "--name-only", "HEAD", tree, "--", *paths)
                if why is None:
                    return diff.split()
            diff, why = _git_ok("diff", "--name-only", f"HEAD...{ref}", "--", *paths)
            if why is not None:
                if why not in errors:
                    errors.append(why)
                return []
            return diff.split()

        # items the branch changes, with every step file it has for them
        touched = {n.split("/")[1] for n in changed("work/") if n.count("/") == 2}
        items = {i: set() for i in touched}
        files = {i: [] for i in touched}
        listing, why = _git_ok("ls-tree", "-r", "--name-only", ref, "--", "work/")
        if why is not None:
            errors.append(why)
        for name in (listing.splitlines() if why is None else []):
            parts = name.split("/")
            if len(parts) == 3 and parts[1] in items:
                files[parts[1]].append(parts[2])
                if parts[2] in STEPS.values():
                    items[parts[1]].add(parts[2][:2])
        recurring = bool(changed(RECURRING))
        rules = changed(*RULE_PATHS)
        if mb is None or mb[1] != 0:
            errors.append("git merge-base failed (no git)" if mb is None else f"git merge-base failed (exit {mb[1]})")
        bases = mb[0].split() if mb is not None and mb[1] == 0 else []
        clashes, skipped, failed, requests = [], [], [], {}
        for item in sorted(touched):
            req = f"work/{item}/request.md"
            theirs = None
            if "request.md" in files[item]:
                theirs, why = _git_ok("show", f"{ref}:{req}")
                if why is not None:
                    errors.append(why)
                    theirs = None
            requests[item] = theirs
            mine = Path(req)
            mine_text, _ = _read(mine) if mine.exists() else (None, None)   # item 089: None if unreadable
            if (bases and theirs is not None and mine.exists()
                    and all(_git("cat-file", "-e", f"{b}:{req}")[1] != 0 for b in bases)
                    and theirs != mine_text):                # unreadable mine: listed, never dropped
                clashes.append(item)
            if theirs is not None and item not in LEGACY:
                with tempfile.TemporaryDirectory() as tmp:
                    d = Path(tmp) / item
                    d.mkdir()
                    unread = False
                    for f in files[item]:
                        body, why = _git_ok("show", f"{ref}:work/{item}/{f}")
                        if why is not None:                 # item 081: not classified, BRANCH ERROR
                            errors.append(why)
                            unread = True
                            break
                        (d / f).write_text(body, encoding="utf-8")
                    if unread:
                        continue
                    status, detail = classify(d, today)
                if status == "SKIPPED":
                    skipped.append((item, detail))
                if status in ("I3 FAIL", "A1 FAIL"):         # item 077
                    failed.append((item, status, detail))
        # item 062: the branch is one unit; its RESEARCH ONLY items may not change code
        # item 064: plus the work/ .py files the branch changes; the tip's other files count
        # only as step files, so an unchanged .py at the tip is not the branch's code
        unit = (changed(*RESEARCH_CODE_PATHS) + [f for f in changed("work/") if WORK_CODE.fullmatch(f)]
                + [f"work/{i}/{f}" for i in sorted(touched) for f in files[i] if f in STEPS.values()])
        for item, detail in _research_code(unit, requests.get):
            have = [k for k, (i, _) in enumerate(skipped) if i == item]
            if have:
                skipped[have[0]] = (item, f"{skipped[have[0]][1]}; {detail}")
            else:
                skipped.append((item, detail))
        failed = [f for f in failed if f[0] not in {i for i, _ in skipped}]   # item 077: SKIPPED wins
        found.append({"ref": ref, "items": items, "conflicts": conflicts,
                      "recurring": recurring, "clashes": clashes,
                      "skipped": skipped, "failed": failed, "last": last, "rules": rules,
                      "errors": errors, "unrelated": False, "shallow": shallow})
    return found


def _open_at(parent, item):
    """Item 053: is work item `item` still going through the pipeline at commit `parent`?
    PRE_A1_LINE and LEGACY items are closed; otherwise open when its 07 is absent there, has no
    `A1 result:` line, or its last one is FAIL (as classify)."""
    if item in PRE_A1_LINE or item in LEGACY:
        return False
    audit = _git("show", f"{parent}:work/{item}/07-audit-task.md")
    if audit is None or audit[1] != 0:
        return True
    verdicts = _a1_results(audit[0])
    return not verdicts or verdicts[-1].upper() == "FAIL"


def _note(cutoff):
    """The cutoff note on UNTRACKED CHANGE lines when --untracked-from moved it (item 053)."""
    return f" (cutoff {cutoff[:7]} from --untracked-from)" if cutoff != UNTRACKED_FROM else ""


def _shallow_boundaries():
    """Item 079 (RI-014): "full", "unreadable", or the shallow boundaries S (file order, no
    duplicates; may be empty) from `<git rev-parse --git-common-dir>/shallow`, so a linked
    worktree reads its main repo's file. A flag git can't give and no file is "full"; a true flag
    with a missing, unreadable or malformed file (SHALLOW_LINE) is "unreadable", never skipped.
    Item 089: a shallow file that exists but _read can't read (not UTF-8, a directory, ...) is
    "unreadable" whatever the flag says, and is listed on the UNREADABLE line; only a missing file or a
    failed --git-common-dir keeps "full" when the flag is not a sure true."""
    r = _git("rev-parse", "--is-shallow-repository")
    if r is None or (r[1] == 0 and r[0].strip() == "false"):
        return "full"
    sure = r[1] == 0 and r[0].strip() == "true"
    d = _git("rev-parse", "--git-common-dir")
    if d is None or d[1] != 0:
        return "unreadable" if sure else "full"
    text, why = _read(Path.cwd() / d[0].strip() / "shallow", missing_ok=True)
    if why:
        return "unreadable"
    if text is None:
        return "unreadable" if sure else "full"
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if any(SHALLOW_LINE.fullmatch(line) is None for line in lines):
        return "unreadable"
    return list(dict.fromkeys(lines))


def _is_shallow():
    """Item 090 (RI-014): True when _shallow_boundaries (079) gives "unreadable" or a non-empty list of
    boundaries, so a shallow file git or _read can't read counts as shallow (strict); "full" and an empty
    file are False. The one test behind _anchor_env's SHALLOW_TEXT and open_branches' default."""
    s = _shallow_boundaries()
    return s == "unreadable" or (isinstance(s, list) and bool(s))


def _walk(cutoff):
    """Items 053/062/079: HEAD's first-parent commits after `cutoff`, each with the files it
    changes against its first parent: ([(sha, files or None if diff-tree failed)], None, below),
    or (None, (text, failed), None) when the cutoff can't be used or a shallow boundary is in
    `cutoff..HEAD` (item 079). `below` is a shallow boundary that is an ancestor of the cutoff
    (entries may then be extras), else None. Needs git."""
    note = _note(cutoff)
    known = _git("rev-parse", "--verify", "-q", f"{cutoff}^{{commit}}")
    if known[1] != 0 or _git("merge-base", "--is-ancestor", cutoff, "HEAD")[1] != 0:
        shallow = _git("rev-parse", "--is-shallow-repository")
        if shallow[1] == 0 and shallow[0].strip() == "true":
            return None, (f"not checked (cutoff {cutoff[:7]} not in this shallow clone; run git fetch --unshallow)"
                          + note, False), None
        if shallow[1] != 0 and _shallow_boundaries() == "unreadable":   # item 079: git died on a bad S line
            return None, ("not checked (shallow clone; run git fetch --unshallow)" + note, False), None
        return None, (f"cutoff {cutoff[:7]} not in HEAD's history (squash/rebase or wrong SHA)" + note, True), None
    shallow_s = _shallow_boundaries()                       # item 079 (RI-014)
    if shallow_s == "unreadable":
        return None, ("not checked (shallow clone; run git fetch --unshallow)" + note, False), None
    below = None
    if shallow_s and shallow_s != "full":
        all_ = _git("rev-list", f"{cutoff}..HEAD")
        if all_[1] != 0:
            return None, (f"cutoff {cutoff[:7]}: git rev-list failed" + note, True), None
        boundaries = set(shallow_s)
        inside = [c for c in all_[0].split() if c in boundaries]
        if inside:
            return None, (f"not checked (shallow boundary {inside[0][:7]}; run git fetch --unshallow)" + note,
                          False), None
        for b in shallow_s:
            m = _git("merge-base", "--is-ancestor", b, cutoff)
            if m[1] == 0:
                below = b
                break
            if m[1] != 1:
                return None, (f"cutoff {cutoff[:7]}: git merge-base failed" + note, True), None
    walk = _git("rev-list", "--first-parent", "--reverse", f"{cutoff}..HEAD")
    if walk[1] != 0:
        return None, (f"cutoff {cutoff[:7]}: git rev-list failed" + note, True), None
    units = []
    for c in walk[0].split():
        diff = _git("diff-tree", "-r", "--name-only", "--no-renames", f"{c}^1", c)
        units.append((c, diff[0].split("\n") if diff[1] == 0 else None))
    return units, None, below


def _parts(walked):
    """Item 079: (units, error, below) of a _walk result; a 2-tuple (older callers) has no below."""
    return walked[0], walked[1], (walked[2] if len(walked) > 2 else None)


def _below_text(below, n, cutoff):
    """Item 079: the text that replaces `n` entries when shallow boundary `below` is an ancestor of
    the cutoff, so the entries may be commits a full clone would not walk."""
    return (f"not checked (shallow boundary {below[:7]} below the cutoff; {n} unconfirmed entries; "
            "run git fetch --unshallow)" + _note(cutoff))


def untracked_changes(cutoff=UNTRACKED_FROM, walked=None):
    """Item 053 (RI-007): None without git, else (text after `UNTRACKED CHANGE: `, failed).
    `walked` is _walk(cutoff) when main() already has it."""
    if _git("rev-parse", "HEAD") is None:
        return None
    note = _note(cutoff)
    units, error, below = _parts(walked or _walk(cutoff))
    if error:
        return error
    entries = []
    for c, files in units:
        if files is None:
            entries.append(f"{c[:7]} (git diff-tree failed)")
            continue
        code = [f for f in files if _is_code(f, CODE_PATHS)]
        if not code:
            continue
        items = sorted({m[1] for m in map(STEP_FILE.match, files) if m})
        if not any(_open_at(f"{c}^1", i) for i in items):
            entries.append(f"{c[:7]} {' '.join(code)}")
    if not entries:
        return "none" + note, False
    if below:                                               # item 079: may be extras
        return _below_text(below, len(entries), cutoff), False
    return ("; ".join(entries) + " (item 053: code, config, tests or rules changed with no step file of an "
            "open work item; a follow-up to a completed item is a new item)" + note, True)


def research_code(cutoff=UNTRACKED_FROM, walked=None):
    """Item 062 (RI-007): None without git, else (text after `RESEARCH CODE: `, {ID: (sha7, detail)})
    for RESEARCH ONLY items whose HEAD commits after the cutoff change RESEARCH_CODE_PATHS. Scope
    and waiver are read from work/<ID>/request.md in the working tree. A cutoff problem is
    UNTRACKED CHANGE's (053) and is not reported twice; a diff-tree failure is 053's entry."""
    if _git("rev-parse", "HEAD") is None:
        return None
    units, error, below = _parts(walked or _walk(cutoff))
    if error:
        return "not checked (see UNTRACKED CHANGE)", {}
    if any(files is None for _, files in units):            # item 079: never "none" on a failed diff
        return "not checked (see UNTRACKED CHANGE)", {}

    unread = {}                                             # item 089: {ID: why} for an unreadable request.md

    def request_text_of(item):
        req = Path("work") / item / "request.md"
        if not req.is_file():
            return None
        text, why = _read(req)
        if why:
            unread[item] = why
        return text                                         # None when unreadable: strict, never built

    flagged = {}
    for c, files in units:
        for item, detail in _research_code(files, request_text_of):
            if item in unread:                              # its text is None: the only flag is "no request.md"
                detail = f"RESEARCH ONLY check: {unread[item]} (item 089)"
            if item in flagged:
                sha, old = flagged[item]
                flagged[item] = (sha, f"{old}; {c[:7]} {detail}")
            else:
                flagged[item] = (c[:7], detail)
    if flagged and below:                                   # item 079: no SKIPPED from 062
        return _below_text(below, len(flagged), cutoff), {}
    return ", ".join(sorted(flagged)) or "none", flagged


def _triggers(files):
    """Item 070: the sorted paths in `files` on realtest's decision path (TRIGGER, TRIGGER_DIRS)."""
    return sorted(f for f in files if f in TRIGGER or f.startswith(TRIGGER_DIRS))


def _field_gap(text):
    """Item 070: None when the Real-data effect section of a 05/06 text holds diff_reports' TOTAL
    line, else the reason. Comments are dropped; code fences (``` or ~~~, CommonMark 0.31.2 §4.5,
    _md_lines; item 077) are tracked from the top, lines inside them are read, and only a `## `
    outside a fence ends the section. A fence still open at the end of the file fails."""
    rows, open_at_end = _md_lines(text)
    start = next((k for k, (line, state) in enumerate(rows)
                  if state == "out" and line.rstrip() == f"## {REAL_DATA_FIELD}"), None)
    if start is None:
        return f"has no '## {REAL_DATA_FIELD}' section"
    section = []
    for line, state in rows[start + 1:]:
        if state == "out" and line.startswith("## "):
            break
        section.append(line)
    else:
        if open_at_end:
            return "Real-data effect has an unclosed ``` fence"
    if any(TOTAL_LINE.fullmatch(line.strip()) for line in section):
        return None
    return "Real-data effect has no diff_reports TOTAL line"


def _item_triggers(cutoff):
    """Item 070: ({ID: (sha7, files)}, None) for items from WHOLE_DIFF_FROM on whose own non-merge
    commits after `cutoff` (a commit holding one of the item's step files 01-06) change TRIGGER or
    TRIGGER_DIRS: the union of those files, and the sha7 of the newest such commit. One git log call;
    (None, error) when it fails."""
    out = _git("log", "--no-merges", "--no-renames", "--name-only", "--format=%x01%H", f"{cutoff}..HEAD")
    if out is None or out[1] != 0:
        return None, "git log failed (item 070)"
    found = {}
    for chunk in out[0].split("\x01")[1:]:
        rows = chunk.split("\n")
        sha, files = rows[0].strip(), [r for r in rows[1:] if r.strip()]
        hit = _triggers(files)
        if not hit:
            continue
        for item in sorted({m[1] for m in map(STEP_FILE.match, files) if m}):
            if int(item) < WHOLE_DIFF_FROM:
                continue
            sha7, old = found.get(item, (sha[:7], []))      # git log lists newest first
            found[item] = (sha7, sorted(set(old) | set(hit)))
    return found, None


def real_data_field(cutoff=UNTRACKED_FROM, walked=None):
    """Item 070 (RI-010/RI-013): None without git, else (text after `REAL-DATA FIELD: `,
    {ID: [INCOMPLETE entries]}, failed). `walked` is _walk(cutoff); a cutoff problem is UNTRACKED
    CHANGE's (053). 05 and 06 are read from the working tree; a missing 06 is not checked yet."""
    if _git("rev-parse", "HEAD") is None:
        return None
    if walked is None:
        walked = _walk(cutoff)
    if walked[1]:
        return "not checked (see UNTRACKED CHANGE)", {}, False
    below = _parts(walked)[2]
    found, error = _item_triggers(cutoff)
    if error:
        return error, {}, True
    names, entries, failed = [], {}, False
    for item, (sha7, files) in sorted(found.items()):
        req = Path("work") / item / "request.md"
        if not req.is_file():
            names.append(f"{item} (no work/{item}/request.md here)")
            failed = True
            continue
        req_text, req_why = _read(req)
        if req_why is None and parse_request(req_text)[0] == "RESEARCH ONLY":   # gap (r): 062's
            continue
        what = f"{sha7} changes {' '.join(files)}"
        gaps = [f"request.md not checked ({req_why}; item 089)"] if req_why else []   # scope unknown: built
        if not (req.parent / STEPS["05"]).is_file():
            gaps.append(f"no 05 for {what} (item 070)")
        for step in ("05", "06"):
            f = req.parent / STEPS[step]
            if f.is_file():
                body, why = _read(f)
                if why:                                     # item 089: never judged from a file not read
                    gaps.append(f"{step} not checked ({why}; item 089)")
                    continue
                gap = _field_gap(body)
                if gap:
                    gaps.append(f"{step} {gap} ({what}; item 070)")
        if gaps:
            names.append(item)
            entries[item] = gaps
    if names and below:                                     # item 079: no INCOMPLETE from 070
        return _below_text(below, len(names), cutoff), {}, False
    return ", ".join(names) or "none", entries, failed


MAIN = "origin/main"
# Item 090 (RI-014): the one text for every check that is not run in a shallow clone (_anchor_env's env; main
# compares by equality, so "no git", "unborn HEAD" or a verify failure never switch those checks off).
SHALLOW_TEXT = "shallow clone; run git fetch --unshallow"
# Item 094 (RI-014): the one text for a clone whose origin fetch refspec does not cover every branch; main,
# open_branches and next_id compare by equality only (RI-012).
SINGLE_TEXT = "single-branch clone; run git remote set-branches origin '*' && git fetch origin"
_GLOB = "refs/heads/*:refs/remotes/origin/*"


def main_ahead(shallow=False):
    """Commits on origin/main that HEAD lacks (item 051): an int, 0 when there is no
    refs/remotes/origin/main (exact refname, so origin/main/x is not it) or no git; or, item 081,
    the error string `<why> (item 081)` when the lookup or the count fails, never 0. Item 090
    (RI-014): None in a shallow clone when the ref exists (a shallow HEAD..main count can be false):
    main prints `MAIN AHEAD: not checked (SHALLOW_TEXT)`, exit unchanged."""
    refs, why = _git_ok("for-each-ref", "--format=%(refname) %(objectname)", f"refs/remotes/{MAIN}")
    if why == "no git":
        return 0
    if why:
        return f"{why} (item 081)"
    sha = next((p[1] for p in (ln.split() for ln in refs.splitlines())
                if len(p) == 2 and p[0] == f"refs/remotes/{MAIN}"), None)
    if sha is None:
        return 0
    if shallow:
        return None
    n, why = _git_ok("rev-list", "--count", f"HEAD..{sha}")
    if why == "no git":
        return 0
    if why or not n.strip().isdigit():
        return f"{why or 'git rev-list gave no count'} (item 081)"
    return int(n.strip())


def next_id():
    """The next free work item ID over HEAD and every unmerged remote branch (item 037):
    (id, None), or (None, why) when a git read fails (item 081), so no ID is guessed. Without git,
    HEAD's work/ only. A branch with no work/ adds no ID. Item 094 (RI-014): after a successful branch
    read, a single-branch clone or a failed config read (fetch_coverage) is (None, that reason) (item 094)."""
    ids = [int(p.name) for p in Path("work").iterdir() if p.name.isdigit()] if Path("work").is_dir() else []
    out, why = _git_ok("branch", "-r", "--no-merged", "HEAD", "--format=%(refname:short)")
    if why not in (None, "no git"):
        return None, why
    if why is None:
        cov = fetch_coverage()                              # item 094: hidden refs would give a clashing ID
        if cov == SINGLE_TEXT or cov.startswith("git config failed"):
            return None, cov
    for ref in (out.split() if why is None else []):
        listing, why = _git_ok("ls-tree", "-d", "--name-only", ref, "--", "work/")
        if why is not None:
            return None, why
        names = [Path(line).name for line in listing.splitlines()]
        ids += [int(n) for n in names if n.isdigit()]
    return f"{max(ids, default=0) + 1:03d}", None


def _inbox_gate(path: Path) -> "tuple[str, bool] | None":
    """Item 069 round 2 (RI-010): None if the daily report `path` was written under an
    INBOX_TEMPLATE with `## Inbox` (the template at the commit that added it; the working-tree
    template if it is not committed), else the (text, failed) INBOX result. No git or a shallow
    clone is `not checked`; a failing `git log` is a failure, never hidden."""
    shallow = _git("rev-parse", "--is-shallow-repository")
    if shallow is None:
        return "not checked (no git)", False
    if shallow[1] == 128:                                   # item 081: git died, e.g. a bad shallow line
        return f"{path.name} (git rev-parse failed (exit 128); item 081)", True
    if shallow[1] == 0 and shallow[0].strip() == "true":
        return "not checked (shallow clone; run git fetch --unshallow)", False
    sha = ""
    if _git("rev-parse", "--verify", "-q", "HEAD")[1] == 0:
        added = _git("log", "--no-renames", "--diff-filter=A", "--format=%H", "-1", "--", path.as_posix())
        if added[1] != 0:
            return f"{path.name} (git log failed)", True
        sha = added[0].strip()
    if sha:
        tpl = _git("show", f"{sha}:{INBOX_TEMPLATE}")
        ok = tpl[1] == 0 and INBOX_HEAD.search(tpl[0]) is not None
        where = f"added in {sha[:7]}"
    else:
        working = Path(INBOX_TEMPLATE)
        tpl_text, why = _read(working) if working.is_file() else (None, None)
        if why:                                             # item 089: not judged by a template not read
            return f"not checked ({path.name} not committed; its {INBOX_TEMPLATE} unreadable)", False
        ok = tpl_text is not None and INBOX_HEAD.search(tpl_text) is not None
        where = "not committed"
    return None if ok else (f"not checked ({path.name} {where}; its {INBOX_TEMPLATE} has no ## Inbox)", False)


def inbox_section(audit=Path("logs/audit")) -> tuple[str, bool]:
    """Item 069 (RI-010): (text after `INBOX: `, failed) for the newest daily report, if
    _inbox_gate says it was written under the Inbox template. A missing folder, no daily report,
    or a report the gate does not check is `not checked`, never `none`."""
    reports = sorted(p for p in audit.iterdir() if p.is_file() and DAILY_REPORT.fullmatch(p.name)
                     ) if audit.is_dir() else []
    if not reports:
        return "not checked (no daily report)", False
    newest = reports[-1]
    gate = _inbox_gate(newest)
    if gate:
        return gate
    text, why = _read(newest)
    if why:                                                 # item 089: listed on UNREADABLE, exit 1 there
        return f"not checked ({newest.name} unreadable)", False
    head = INBOX_HEAD.search(text)
    if head is None:
        return f"{newest.name} (no ## Inbox)", True
    rest = text[head.end():]
    nxt = re.search(r"^## ", rest, re.M)
    section = rest[:nxt.start()] if nxt else rest
    missing = [what for what, rx in (("no project-inbox: line", INBOX_PI),
                                     ("no hub: SHA or UNREAD line", INBOX_HUB)) if not rx.search(section)]
    return (f"{newest.name} ({'; '.join(missing)})", True) if missing else ("none", False)


def main(argv):
    _UNREAD.clear()                                         # item 089: one run's reads; never rebound
    today = dt.datetime.now(dt.timezone.utc).date()
    if argv[:1] == ["--next-id"]:
        nid, why = next_id()
        if why == SINGLE_TEXT:                              # item 094: single-branch clone
            print(f"--next-id refused: {SINGLE_TEXT}; not counting open branches would risk an ID clash "
                  f"(item 037). Re-run after that.", file=sys.stderr)
            return 2
        if why:                                             # item 081: never guess an ID
            print(f"--next-id refused: {why}; not counting open branches would risk an ID clash "
                  f"(item 037). Fix the clone (git fetch origin) and re-run.", file=sys.stderr)
            return 2
        print(nid)
        return 0
    if argv[:1] == ["--log"]:
        if len(argv) != 4:
            sys.exit(__doc__)
        return write_log(*argv[1:])
    cutoff, rest = UNTRACKED_FROM, list(argv)
    while rest:
        if len(rest) < 2 or rest[0] not in ("--today", "--untracked-from"):
            sys.exit(__doc__)
        if rest[0] == "--today":
            today = dt.date.fromisoformat(rest[1])
        else:
            cutoff = rest[1]
        rest = rest[2:]
    work = Path("work")
    skipped, stuck, awaiting, in_pr, failed, i3_failed, unfinished = [], [], [], [], [], [], []
    (env, env_failed), not_seen = _anchor_env(), []         # items 084, 088: computed once
    shallow = env == SHALLOW_TEXT                           # item 090: before open_branches; equality only
    unchecked = []                                          # item 095: (ID, entry) not checked when shallow
    committed = _head_work_files() if shallow else None     # item 095 (C1): read once, only when shallow
    branches = open_branches(today, shallow)
    blist = branches if isinstance(branches, list) else []  # item 081: None (no git) or a git error
    walked = _walk(cutoff) if _git("rev-parse", "HEAD") is not None else None
    untracked = untracked_changes(cutoff, walked)
    research = research_code(cutoff, walked)
    real = real_data_field(cutoff, walked)                  # item 070
    uncommitted = uncommitted_steps()                       # item 077
    flagged = research[1] if research else {}
    batch = batch_log_items()                               # item 086: no git, same text with or without it
    batch_nc = {i: r for i, r in batch["not_computable"]}   # item 090: read by INCOMPLETE (step 2)
    listed = sorted(p for p in work.iterdir() if (p / "request.md").exists())
    for d in listed:
        status, detail = classify(d, today)
        if d.name in LEGACY and status in ("SKIPPED", "in progress"):
            status, detail = "LEGACY", LEGACY[d.name]
        if d.name in flagged:                       # item 062: replaces the classify line
            status, detail = "SKIPPED", f"{flagged[d.name][0]} {flagged[d.name][1]}"
        if status in ("STUCK", "not started", "in progress", "I3 FAIL"):
            here = {s for s, f in STEPS.items() if (d / f).exists()}
            best = max(((len(items.get(d.name, set()) - here), ref, items.get(d.name, set()))
                        for ref, items in ((b["ref"], b["items"]) for b in blist)), default=(0, "", set()))
            if best[0] > 0:
                status, detail = "IN PR", f"{best[1]} has {' '.join(sorted(best[2]))}; was {status} here"
                in_pr.append(d.name)
        print(f"{d.name}: {status} ({detail})")
        if status == "SKIPPED":
            skipped.append(d.name)
        if status == "STUCK":
            stuck.append(d.name)
        if status == "awaiting A1":
            awaiting.append(d.name)
        if status == "A1 FAIL":
            failed.append(d.name)
        if status == "I3 FAIL":
            i3_failed.append(d.name)
        gaps = incomplete(d, env=env, not_seen=not_seen, batch_nc=batch_nc, unchecked=unchecked,
                          committed=committed) + (real[1].get(d.name, []) if real else [])
        if gaps:
            unfinished.append(f"{d.name} ({'; '.join(gaps)})")
    for item in sorted(set(flagged) - {d.name for d in listed}):   # item 062: no request.md here
        print(f"{item}: SKIPPED ({flagged[item][0]} {flagged[item][1]})")
        skipped.append(item)
    print(f"STUCK: {', '.join(stuck) or 'none'}")
    print(f"AWAITING A1: {', '.join(awaiting) or 'none'}")
    unread = "not checked (see OPEN BRANCHES)" if isinstance(branches, str) else None
    print(f"IN PR: {unread or ', '.join(in_pr) or 'none'}")
    ahead = main_ahead(shallow)
    if ahead is None:                                       # item 090: shallow clone, exit unchanged
        print(f"MAIN AHEAD: not checked ({SHALLOW_TEXT})")
    elif isinstance(ahead, str):                            # item 081: the lookup failed, exit 1
        print(f"MAIN AHEAD: {ahead}")
    elif ahead > 0:
        print(f"MAIN AHEAD: {MAIN} has {ahead} commits not in HEAD; merge it before building (item 051)")
    folded = []                                             # item 095: shallow unrelated refs
    if branches == SINGLE_TEXT:                             # item 094: single-branch clone, exit unchanged
        print(f"OPEN BRANCHES: not checked ({SINGLE_TEXT})")
    elif isinstance(branches, str):                         # item 081: git branch failed, exit 1
        print(f"OPEN BRANCHES: {branches} (item 081)")
    elif branches == []:
        print("OPEN BRANCHES: none")
    elif branches:
        print("OPEN BRANCHES (not merged into HEAD):")
        for b in branches:
            age = f"; last commit {b['last']} ({(today - b['last']).days} days)" if b["last"] else ""
            if b.get("unrelated") and b.get("shallow"):     # items 090, 095: no merge base in the shallow view
                folded.append(b)
                continue
            if b.get("unrelated"):                          # item 081 r2: not scanned
                print(f"  {b['ref']}: no common history with HEAD; not scanned (item 081){age}")
                continue
            conflicts = b["conflicts"]
            merge = ("merge not checked" if conflicts is None else
                     f"CONFLICTS: {', '.join(conflicts)}" if conflicts else "merges cleanly")
            note = f"; edits {RECURRING} (item 036)" if b["recurring"] else ""
            print(f"  {b['ref']}: items {', '.join(sorted(b['items'])) or 'none'}; {merge}{note}{age}")
        if folded:                                          # item 095: one line, names kept, age dropped
            print(f"  shallow clone: {len(folded)} ref(s) with no merge base not checked "
                  f"({', '.join(b['ref'] for b in folded)}); run git fetch --unshallow (item 095)")
    if _git("rev-parse", "HEAD") is not None:
        ruling = [f"{b['ref']} changes {', '.join(b['rules'])}" for b in blist if b["rules"]]
        print(f"RULES BRANCH: {unread or ('; '.join(ruling) + '; build new items on top of it (item 049)' if ruling else 'none')}")
    clashes = [f"{i} ({b['ref']})" for b in blist for i in b["clashes"]]
    print(f"ID CLASH: {unread or ', '.join(clashes) or 'none'}")
    for b in blist:
        for item, detail in b["skipped"]:
            print(f"BRANCH SKIPPED: {item} ({b['ref']}: {detail})")
    for b in blist:                                         # item 077: information, exit unchanged
        for item, status, detail in b["failed"]:
            print(f"BRANCH FAIL: {item} ({b['ref']}: {status}; {detail})")
    branch_errors = [f"{b['ref']} ({why})" for b in blist for why in b["errors"]
                     if not (any(b is f for f in folded) and isinstance(b.get("held"), int))]
    holding = [b["ref"] for b in folded if isinstance(b.get("held"), int) and b["held"] > 0]
    if holding:                                             # item 095: one summary; held None keeps its own
        branch_errors.append(f"shallow clone; {len(holding)} of {len(folded)} ref(s) hold files on checked paths, "
                             f"not checked ({', '.join(holding)}); run git fetch --unshallow (item 095)")
    for line in branch_errors:                              # item 081: exit 1
        print(f"BRANCH ERROR: {line}")
    print(f"I3 FAIL: {', '.join(i3_failed) or 'none'}")
    print(f"A1 FAIL: {', '.join(failed) or 'none'}")
    print(f"INCOMPLETE: {', '.join(unfinished) or 'none'}")
    if shallow:                                             # item 095: not checked, exit 1 (fail closed)
        by_unsure = {}
        for item, entry in unchecked:
            by_unsure.setdefault(item, []).append(entry)
        listed_nc = ", ".join(f"{i} ({'; '.join(e)})" for i, e in by_unsure.items())
        if listed_nc:
            listed_nc += f"; rule seen not checked ({SHALLOW_TEXT}; item 095)"
        print(f"INCOMPLETE NOT CHECKED: {listed_nc or 'none'}")
    by_id = {}                                              # item 084: information, exit unchanged
    for item, step, sha7, const, rule, old in not_seen:
        by_id.setdefault(item, []).append(f"{step} added in {sha7} without {const} ({rule}): judged by {old}")
    seen_text = ", ".join(f"{i} ({'; '.join(p)}; item 084)" for i, p in by_id.items())
    print(f"RULE NOT SEEN: {f'not checked ({env})' if env else seen_text or 'none'}")
    late = late_log_lines(shallow)
    excepted = "; ".join(f"{i}: {why}" for i, why in sorted(LOG_TIME_EXCEPT.items())
                         if (work / i / "request.md").exists())
    excepted = f" (not checked: {excepted})" if excepted and late is not None else ""
    if late is False:                                       # item 090: shallow clone, exit unchanged
        print(f"LOG TIME: not checked ({SHALLOW_TEXT})")
    else:
        print(f"LOG TIME: {'not checked (no git)' if late is None else (', '.join(late) or 'none') + excepted}")
    batch_text = "; ".join(batch["flagged"]) or "none"
    if batch["excepted"]:
        batch_text += f" (not checked: {'; '.join(f'{i}: {why}' for i, why in batch['excepted'])})"
    if batch["not_computable"]:
        batch_text += "; not computable: " + "; ".join(f"{i}: {why}" for i, why in batch["not_computable"])
    print(f"LOG BATCH: {batch_text}")
    print(f"UNTRACKED CHANGE: {'not checked (no git)' if untracked is None else untracked[0]}")
    print(f"RESEARCH CODE: {'not checked (no git)' if research is None else research[0]}")
    print(f"REAL-DATA FIELD: {'not checked (no git)' if real is None else real[0]}")
    print(f"UNCOMMITTED STEP: {'not checked (no git)' if uncommitted is None else uncommitted[0]}")
    stash_out, stash_why = _git_ok("stash", "list")         # item 097 (RI-009): decided by exit code only
    stash_bad = False
    if stash_why == "no git":                              # exit unchanged, never none
        print("STASH: not checked (no git)")
    elif stash_why:                                         # stdout is not read on a failed read
        print(f"STASH: not checked ({stash_why}) (item 097)")
        stash_bad = True
    elif stash_out.strip() == "":
        print("STASH: none")
    else:
        entries = [l for l in stash_out.splitlines() if l.strip()]   # n is shown only, never decides
        print(f"STASH: {len(entries)} (first: {entries[0]}); local to this checkout; only the person drops an "
              f"entry (item 097)")
        stash_bad = True
    orphans, orphan_whys = orphan_log_lines()
    if orphan_whys:                                         # item 089: never a bare none for a lost file
        lost = "; ".join(orphan_whys)
        print(f"ORPHAN LOG: {', '.join(orphans)}; not checked: {lost} (item 089)" if orphans
              else f"ORPHAN LOG: not checked ({lost}; item 089)")
    else:
        print(f"ORPHAN LOG: {', '.join(orphans) or 'none'}")
    inbox, inbox_bad = inbox_section()  # item 069
    print(f"UNREADABLE: {', '.join(f'{p} ({d})' for p, d in sorted(_UNREAD.items())) or 'none'}")   # item 089
    unreadable = bool(_UNREAD)
    print(f"INBOX: {inbox}")
    if inbox_bad:
        print(f"SKIPPED: {', '.join(skipped) or 'none'}")
        return 1
    print(f"SKIPPED: {', '.join(skipped) or 'none'}")
    return 1 if skipped or failed or i3_failed or unfinished or late or orphans or (untracked and untracked[1]) \
        or (real and real[2]) or (uncommitted and uncommitted[1]) \
        or (isinstance(branches, str) and branches != SINGLE_TEXT) \
        or branch_errors or isinstance(ahead, str) or batch["flagged"] or env_failed or unreadable \
        or unchecked or stash_bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
