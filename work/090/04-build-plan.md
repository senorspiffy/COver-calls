# 04 Build plan - 090
Fit verdict: FIT WITH CHANGES

Method: I1 has no shell (item 072). I read .claude/agents/i1-reviewer.md, work/090/request.md, 01-03, logs/recurring-issues.md, work/088/04-build-plan.md, work/089/03-handoff.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, scripts/check_handoff.py L90-104, .claude/commands/run-item.md L10-17, .claude/agents/i2-builder.md L25, and templates L2. Branch: daily-fixes/2026-11-21, working tree, 2026-11-21. Nothing was run.

**Build order and line numbers.** Build 090 on top of 088 and 089, then 091 builds on 090. In this working tree 088's code is already present: `_anchor_env` returns `(env, failed)` at L628-649, and main unpacks it at L1548. 089 is not built yet: there are still 21 `read_text` sites and no `_read`. **I2 must re-read every line number below after 089 lands, finding each line by its text.** The table is a starting point only:

| Name | Line(s) today |
|---|---|
| `_TAIL`, `I2_BEFORE` | L329, L330 |
| `BATCH_ROUND`, `SEND_BACK` | L340, L343 |
| `LOG_FORMAT["I2"]`, `LOG_HINT`, `LOG_HINT_BEFORE` | L389, L394-402, L404 |
| `log_fields_ok`, `log_hint` | L572, L583 |
| `_anchor_env` (shallow text L641) | L628 |
| `incomplete` (TESTS gate L722-736) | L700 |
| `_sent_back`, `write_log` (rule D L826-831) | L786, L812 |
| `late_log_lines`, `_item_lines`, `batch_log_items` | L854, L890, L945 |
| `open_branches` (`behind` L1064, unrelated L1074-1085) | L1050 |
| `main_ahead` | L1429 |
| `main` (open_branches L1545, env L1548, item loop L1555-1581, MAIN AHEAD L1589-1593, unrelated print L1602-1604, LOG TIME L1632-1636, batch L1637, exit L1656-1658) | L1520 |
| docstring: rule D L105-111, LOG BATCH gaps (x)/(y) L139-143, MAIN AHEAD L150-154 | — |
| tests: FIELDS L15-17, `test_log_hints_match_formats` L603, L464, NEW_I2_WANT L2611, GIT_CENSUS L2369 (total 47), (b) L2455, (c) L2475, 086 C tests L2918-3176, D tests L3197-3290, UNSHALLOW L3565 | — |

**Fit.** The change is process-only. Nothing in ccbot/, config/ or data/ changes, and no broker, price or account input is touched, so the ~$3k account and the 001 strategy rules are unaffected. No rule the person follows (001 slack, tolerance or cap) changes. The scripts/check_pipeline.py and .claude/ edits are RULE_PATHS, so the person's OK is needed at PR review. I made these changes to 03's map:
1. **Fixture blast radius (missed by R3).** `FIELDS["I2"]` (tests L17) is `"1 files changed | tests 1 passed"`, with no time. `_item` writes it for every fixture item, and most of those items are ≥ 90 (150, 151, 999). With `TIMED_FROM = 90`, every main-running fixture with an I2 line becomes INCOMPLETE. The plan therefore changes `FIELDS["I2"]` to a timed field and lists the literal sites (Tests B0).
2. **Shallow `origin/main` in OPEN BRANCHES (missed by R3).** `git branch -r --no-merged HEAD` lists the "branches whose tips are not reachable from" HEAD (git-branch docs). In a depth-1 clone, origin/main's tip, an ancestor of HEAD in the full clone, is not reachable. With 03's `behind = False`, origin/main would then be listed, called unrelated, and turned into a BRANCH ERROR, because its tree holds checked paths. That would make every shallow run exit 1. In a full clone origin/main is never listed: either it is merged, or `behind > 0` skips it (L1070). So in a shallow clone the plan skips `ref == MAIN`, and the MAIN AHEAD not-checked line covers it.
3. **Exit-0 shallow fixture must use an orphan branch.** A branch that shares history carries the whole tree (work/, .claude/), so in a shallow clone it always holds checked paths. 03's "exit 0 with a docs-only branch" is only possible with an orphan README-only branch (`_orphan`, tests L3294).
4. **Unfilled template lines.** `Fit verdict: FIT | FIT WITH CHANGES | NOT A FIT` and `Status: READY | BLOCKED (<reason>)` (templates L2) must read as no verdict. The 03/04 patterns get VERDICT_LINE's `(?![ \t*]*[|/])` lookahead.
5. **Env equality, and env computed first.** 088's `_anchor_env` can also give "unborn HEAD", "no git" or a verify failure. Only the shallow text may switch the three readers to not checked, so the test is equality with one constant `SHALLOW_TEXT`, and env is computed before `open_branches` (today it is L1548, after L1545). `check_handoff._branch_with_handoff` calls `open_branches()` with no args, so `shallow=None` makes the function compute it itself.
6. **Rule text.** run-item.md L17 ("unless the item was sent back") and i2-builder.md L25 state the old rules, so both are updated in this plan. The UNSHALLOW sentence (3 files + test constant) is also updated.

## Extra research (with sources)
- git-branch: `--no-merged`: "Only list branches whose tips are not reachable from *<commit>*" (https://git-scm.com/docs/git-branch, opened 2026-11-21). With B2 (shallow view only removes parent edges, https://git-scm.com/docs/shallow), "merged" is exact in a shallow clone and "not merged" is uncertain. So the branch list over-includes and never hides a branch (the safe direction). Fit change 2 rests on this. Known gap for the docstring: in a shallow clone, refs already in main are listed (and are loud, as in A1's 628-file probe).
- Code reading, not in 03: `check_handoff.py` L95-96 imports `open_branches`. The new keyword defaults to computing shallowness, so check_handoff needs no edit.
- Code reading: test L464 (`--log I2 999 "1 file changed | tests 1 passed"`, which expects exit 2 for "no request.md", item 047) would still pass after step 1, but for the wrong reason (format). Its field becomes timed, and it gains an `"item 047" in err` assert.
- Code reading: test (b) L2455 and (c) L2475 assert exit 1 in a malformed or non-UTF-8 shallow clone. Today LOG TIME is one of their exit-1 terms (ls-tree dies, giving an entry). After step 5 LOG TIME says not checked. Exit 1 must still come from OPEN BRANCHES / MAIN AHEAD failing (git 128), and from 089's UNREADABLE in (c). Both tests stay unedited and pin this.
- pytest `-q` always prints ` in <s>s` (03 #6, https://pytest.org/latest/_modules/_pytest/terminal.html). The timed form costs a correct I2 nothing. I found no better source.

## Files to create/change
6 files planned (plus I2's own work/090/05).

**1. `scripts/check_pipeline.py`**
- Constants:
  - `TIMED_FROM = 90` (comment: item 090, the 7th `*_FROM`, numeric floor above 088/089).
  - `I2_TIMED = rf"\d+ files? changed \| tests {_STATS} in \d+\.\d+(?:s| seconds)(?: \(\d+:\d{{2}}:\d{{2}}\))?(?: \(.*\))?"`. The global `_TAIL` and `LOG_FORMAT["I2"]` are unchanged.
  - `LOG_HINT_TIMED = {"I2": ("<n> files changed | tests <last line of python3 -m pytest -q, as printed, with its ` in <s>s` time>", "2 files changed | tests 9 passed, 1 skipped in 3.21s")}`.
  - `SHALLOW_TEXT = "shallow clone; run git fetch --unshallow"`.
  - `VERDICT_OF = {"R3": ("03", re.compile(r"Status:[ \t]*(?:\*\*)?(READY|BLOCKED)\b(?![ \t*]*[|/])")), "I1": ("04", re.compile(r"Fit verdict:[ \t]*(?:\*\*)?(NOT A FIT|FIT WITH CHANGES|FIT)\b(?![ \t*]*[|/])")), "I3": ("06", VERDICT_LINE)}`.
  - `BATCH_STRICT = ("no pytest time in 05/06/I2 line", "no line before I2", "log line with no valid time")`, compared by equality, never a substring (RI-012).
- `log_fields_ok(agent, item, fields, new_rule=True, timed=True)`: after the I2_BEFORE branch, `if agent == "I2" and timed and int(item) >= TIMED_FROM: return bool(re.fullmatch(I2_TIMED, fields.strip()))`. `log_hint(..., timed=True)` returns `LOG_HINT_TIMED` under the same condition. `write_log` passes neither argument, so it stays numeric and strict.
- `incomplete(item_dir, logs, env, not_seen, batch_nc=None)`:
  - If `"I2" in bad`, the ID ≥ TIMED_FROM, and every I2 line of the item passes `log_fields_ok(..., timed=False)`: call `_rule_seen(item_dir, "05", "TIMED_FROM", env)`.
    - False: drop I2 from `bad` and append `(ID, "05", sha7, "TIMED_FROM", "090", "untimed I2 form")` to `not_seen`.
    - None with a note: strict, and the note is added.
    - True: strict with the timed hint.
  - Otherwise use today's TESTS gate unchanged.
  - Step 2: for an ID ≥ TIMED_FROM whose `batch_nc` reason is in BATCH_STRICT, use the same `_rule_seen(..., "TIMED_FROM", env)`. False adds the not_seen pair `"LOG BATCH not computable as text only"`. Otherwise add the entry `LOG BATCH not computable: <reason> (item 090)` (plus the note if any).
- `batch_log_items`: per-round I2 bound.
  - Placement: after the `r[0] is None` check and before `first, last_i2`. Skip `item in excepted`.
  - For each I2 row r whose tests part matches SUMMARY_LINE, find prev = the latest row before r by 086's rule: research rows with `stamp <= r.stamp`, implementation rows with `order(x) < order(r)`. With no prev, skip the round.
  - Δ = whole minutes from prev to r. Flag when `round(t - BATCH_ROUND, 3) >= (Δ+1)*60`.
  - Entry: `<ID> I2 at <YYYY-MM-DD HH:MM> (<t:.2f> s pytest run after the <agent> line at <HH:MM>, limit <L> s; impossible under the run-item order, item 090)`. It goes into `flagged`. `flagged_ids` is appended only if the ID is not already there. `checked` is not changed.
  - Docstring: the bound only catches rounds where the run is longer than the gap allows; with today's 74-93 s runs that means same-minute (Δ0) batches.
- New `_first_verdict(path, agent) -> (word | None, why | None)`:
  - Reads through 089's `_read`. Takes the first column-0 line outside fences and comments (`_md_lines` "out") that starts with the label, and matches `VERDICT_OF[agent][1]`.
  - Results: `(None, "<file> unreadable")` when the file can't be read; `(None, "absent")` when there is no file; `(None, "no readable <label> line")` when there is no such line.
- New `_round_refusal(item, agent, logs=Path("logs")) -> str | None`, called by `write_log` in place of the bare `not _sent_back(item)` skip. The new code is `if later and not sent: refuse as today (D); elif sent: why = _round_refusal(...)`. It refuses (exit 2, nothing written) with the texts below:
  - Inputs:
    - `_item_lines(logs)`. Unreadable → `--log refused: <whys>; order not checked (item 090)`. A None stamp → `... log line with no valid time; order not checked (item 090)`.
    - Rows are sorted by (stamp, file index, line index).
    - Send-backs are found by SEND_BACK fullmatch.
  - (a): L = the latest send-back row, by S. The round is open while no row after L has agent S. While it is open, `step(X) > step(S)` → `<S> sent work/<ID> back at <date HH:MM> and has not logged again; <S> runs before <X> (item 090)`.
  - (b): while the round is open, `step(X) < step(S)` → call `_first_verdict(work/<ID>/<file>, S)`. If the word is not the SEND_BACK word, or `why` is set: `work/<ID>/<file> no longer says <word> (<found word or why>); <S> ran again before this line: log each step before the next one runs (item 090)`.
  - (c): start = the latest row that is a send-back or a terminal line (I3 PASS for FULL/FAST; R3 READY for RESEARCH ONLY; Scope from request.md via 089's reader). With no such row, the start is the item's first row. If any row after the start has `step > step(X)`: `<agent> already logged at <HH:MM> after <start agent> <HH:MM>; log steps in order (item 090)`.
- `_is_shallow()`: True when `_shallow_boundaries()` is "unreadable" or a non-empty list. `_anchor_env` uses it and `SHALLOW_TEXT`, so there is one source.
- `late_log_lines(shallow=False)`: after the no-git probe, `if shallow: return False`. False is falsy and not None, so exit and "no git" are unchanged.
- `main_ahead(shallow=False)`: after the for-each-ref lookup (errors and "no ref → 0" unchanged), `if shallow: return None`.
- `open_branches(today=None, shallow=None)`:
  - `shallow = _is_shallow() if shallow is None else shallow`.
  - When shallow: `behind = False` (main_ahead is not called), `ref == MAIN` is skipped, and the dict gains `"shallow": True`.
  - A `merge-base --all` exit 1 when shallow: the errors text with checked paths is `shallow clone; <n> file(s) on checked paths (first: <p>) not checked; run git fetch --unshallow (item 090)`. An ls-tree failure stays its own error.
- `main`:
  - `(env, env_failed)` moves above `open_branches`, and `shallow = env == SHALLOW_TEXT`.
  - The new calls are `open_branches(today, shallow)`, `main_ahead(shallow)` and `late_log_lines(shallow)`.
  - `batch = batch_log_items()` moves above the item loop. The loop passes `batch_nc={i: r for i, r in batch["not_computable"]}`.
  - Prints:
    - `ahead is None` → `MAIN AHEAD: not checked (SHALLOW_TEXT)`.
    - `late is False` → `LOG TIME: not checked (SHALLOW_TEXT)`.
    - unrelated + shallow → `  <ref>: not checked (SHALLOW_TEXT)<age>`.
  - The exit expression is unchanged: `late` False, `ahead` None.
- Docstring:
  - Rule D paragraph L105-111 → the 090 round rule (a)-(c).
  - LOG BATCH gaps (x)/(y) rewritten. New known gaps:
    - I3's run is untimed, so an I3 batch is caught only by (b) when 06 changed;
    - an I3 that FAILs again leaves 06 at FAIL;
    - A1 FAIL rounds get (c) only;
    - batches with Δ ≥ 1 pass the bound;
    - in a shallow clone, a branch with a shared shallow base is scanned as today and was not checked by 090, and refs already in main are listed;
    - a single-branch clone hides branches (sent to A1).
  - MAIN AHEAD, LOG TIME and OPEN BRANCHES each gain their shallow sentence (item 090, RI-014). The exit is unchanged except for the unrelated BRANCH ERROR, which stays exit 1.

**2. `tests/test_pipeline_check.py`**: see Tests and checks.

**3-5. `.claude/commands/run-item.md` L12, `.claude/commands/daily-audit.md`, `.claude/agents/a1-auditor.md`**: the UNSHALLOW sentence becomes "... report UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD, LOG TIME, MAIN AHEAD and OPEN BRANCHES as 'not checked', never 'none' (items 079, 090)." It is identical in all three files, and the test constant L3565 matches it.

**3 (also). run-item.md L17**: the last sentence becomes: "`--log` also refuses while a later step file (01-06) of the same item exists (item 086). After a send-back (R3 BLOCKED, I1 NOT A FIT, I3 FAIL, or `A1 result: FAIL`) it refuses a step after the sender until the sender logs again, a step before the sender once the sender's file no longer shows its send-back verdict, and any line after a later step of the same round (item 090): log each step before the next one runs."

**6. `.claude/agents/i2-builder.md` L25**: add "From item 090 (TIMED_FROM) the field must keep pytest's ` in <s>s` time; `--log` refuses it without one." I2 checks whether a test pins this text and adds a one-line text pin like L3555.

Not changed: `_TAIL`, `LOG_FORMAT`, LOG_TIME_EXCEPT, LOG_BATCH_EXCEPT, SUITE_FROM, `_rule_seen`, GIT_CENSUS (no new `_git`/`_git_ok` call site, so the total stays 47; I2 confirms), and 089's read census (the new readers use `_read`).

## Tests and checks
**B0. Fixture sweep (first, before any code edit).**
- `FIELDS["I2"]` → `"1 files changed | tests 1 passed in 0.01s"`. `_item`'s Suite line follows it through `_field`.
- `_impl` default, `_suite_item` default i2, L464, L472, L502, L597, L2461, L3102, L3223, L3226, L3498, L3501: timed where the item is ≥ 90 and the time is incidental. Untimed only where the test is about untimed.
- `NEW_I2_WANT` → the LOG_HINT_TIMED words.
- I2 runs the suite after the code change and lists in 05 every test edited for the timed field, with its count. No assertion's meaning may change.

**Step 1 (`--log` and INCOMPLETE):**
1. `test_log_i2_untimed_refused_from_090`:
   - `--log I2 990 "1 file changed | tests 5 passed"` → 2, and the error names the LOG_HINT_TIMED words.
   - `"... tests 5 passed (in 3.00s)"` → 2.
   - `"... in 3.21s"`, `"... in 61.68s (0:01:01)"`, `"... in 3.21 seconds"` and `"... in 3.21s (note)"` → 0.
   - `--log I2 089 "1 file changed | tests 5 passed"` → 0.
   - Kills M1 and M3.
2. `test_log_hints_match_formats` extended: the LOG_HINT_TIMED example fullmatches I2_TIMED. L712 (`--log I2 076 ... tests 9 passed` → 0) stays and kills M2 (global `_TAIL` made mandatory).
3. `test_timed_gate` (NO_GIT, S13-style repo):
   - 990 with an untimed I2 line and 05 committed. With RULE_FILE `TESTS_FORMAT_FROM = 76\nVERDICT_FROM = 71\nSUITE_FROM = 87\n`, expect `RULE NOT SEEN: 990 (05 added in <sha7> without TIMED_FROM (090): judged by untimed I2 form; item 084)` and no I2 format entry.
   - Twin with `TIMED_FROM = 90\n` added: expect the INCOMPLETE format entry with the timed hint.
   - Absent case: 05 uncommitted → strict, `RULE NOT SEEN: none`.

**Step 2:**
4. `test_batch_not_computable_strict_from_090`: two `_batch_item(full=True)` twins with timed fields plus an extra `25:00` I3 line.
   - 990 → INCOMPLETE contains `LOG BATCH not computable: log line with no valid time (item 090)`, exit 1.
   - 089 → only the LOG BATCH text, exit 0.
   - Kills M4.
5. N5 (L3057) is rewritten on ID 089 (text only, exit 0). A 990 untimed twin gives both the format entry and `LOG BATCH not computable: no pytest time in 05/06/I2 line (item 090)`.

**Step 3 (`_bl`):**
6. `test_round_bound_delta0_boundary` (parametrize 60.00 → none, 60.01 → flagged): I1 10:00, I2 10:00, I3 10:30, t06 1.00 s. Expected text: `999 I2 at 2026-11-20 10:00 (60.01 s pytest run after the I1 line at 10:00, limit 60 s; impossible under the run-item order, item 090)`.
7. `test_round_bound_round2_batch`: R1 09:00, I1 09:20, I2 09:30 (50.00 s), I3 FAIL 09:50, I1 10:05, I2 10:05 (80.00 s), I3 10:20. Exactly that one entry is flagged (whole-item C is not). Kills M6 (prev = first line gives Δ65).
8. `test_round_bound_delta1_limit_120`: I1 10:00, I2 10:01, 86.00 s → none. Kills M5.
9. `test_round_bound_interleaved_items`: three items, R1 at 23:27, and each item's I2 a different minute after its own I1, 70 s runs; lines interleaved with other items in the same minute → none. Kills M7.
10. `test_round_bound_fast_prev_is_research`: R3 10:15 (research), I2 10:15 (70.00 s) → flagged, `after the R3 line at 10:15`.
11. `test_round_bound_on_repo_data` (NO_GIT not needed): `batch_log_items(REPO/"work", REPO/"logs")` has no entry containing `item 090)` (pins 0 of 17).
12. End-to-end: test 7's shape with `full=True` → `LOG BATCH: 999 I2 at ...` and exit 1. All existing 086 C tests stay unedited (checked by reading: none has a timed I2 run ≥ its round limit).

**Step 4 (`--log`):**
13. D3/D4/D5 fixtures gain their verdict line: 06 `Verdict: FAIL (round 1)`, 03 `Status: BLOCKED (x)`, 04 `Fit verdict: NOT A FIT`. The assertions are unchanged.
14. `test_round_content_refusal` (parametrize):
    - I3 FAIL + 06 PASS + `--log I2` → 2, and `no longer says FAIL`.
    - R3 BLOCKED + 03 READY + `--log R1` → 2.
    - I1 NOT A FIT + 04 `Fit verdict: FIT` + `--log R2` → 2.
    - 04 = the unfilled template line → 2 (`no readable`). Kills M17.
    - 06 `Verdict: PASS (round 2; earlier rounds: FAIL)` → 2. Kills M9.
    - 06 = b"\xff" → 2 (`unreadable`). Kills M10.
    - 06 absent → 2.
15. `test_round_open_refuses_later_step`: I1 NOT A FIT, then `--log I2` → 2. Kills M15.
16. `test_round_069_shape`: 01-06, 06 `Verdict: PASS (round 2)`, lines I1, I2, I3 FAIL, I2, I3 PASS, 07 `A1 result: FAIL`.
    - `--log I1`, `--log I2` and `--log I3 "PASS | sent to audit: yes"` → 0 each. Kills M8.
    - A twin with a round-3 I2 already logged: `--log I1` → 2 (`already logged`). Kills M16.
17. `test_round_unreadable_log_refused`: a log file b"\xff\xfe" with an I3 FAIL in another file, then `--log I2` → 2 and `order not checked`.

**Step 5 (shallow, NO_GIT):**
18. `test_shallow_three_readers_not_checked`.
    - Source repo:
      - log `2026-11-20.md` with `23:59 | I3 | 150 | PASS | sent to audit: yes` committed with `GIT_COMMITTER_DATE=2026-11-20T01:30:00Z` (monkeypatch.setenv, precedent L784), then a later commit at `2026-11-21T00:30:00Z`;
      - origin/main pushed one commit behind HEAD's tip;
      - a branch off main with one `.claude/x.md` commit, pushed.
    - Full clone control (`git clone -q --no-single-branch file://...`):
      - `LOG TIME: 150 I3 (2026-11-20 23:59 after commit 2026-11-20 01:30 UTC)`;
      - no `MAIN AHEAD:` line;
      - the branch scanned (`items none; merges cleanly`).
    - Depth 1 (`--depth 1 --no-single-branch`), with `--is-shallow-repository` == true asserted:
      - `LOG TIME: not checked (shallow clone; run git fetch --unshallow)`;
      - `MAIN AHEAD: not checked (shallow clone; run git fetch --unshallow)`;
      - `  origin/<b>: not checked (shallow clone; run git fetch --unshallow)` (age suffix allowed);
      - no line starting `  origin/main:`;
      - `BRANCH ERROR: origin/<b> (shallow clone; ...)`, exit 1.
19. `test_shallow_docs_only_orphan_exit_0`: the same depth-1 setup but with the only open branch an `_orphan` README-only branch and no late line → the three not-checked lines and exit 0.
    - Kills M11 (env forced None: the lines revert), M12 (`main_ahead` returns the hint str: exit 1), M13 (`late_log_lines` returns `[hint]`: exit 1) and M14 (MAIN skip removed: origin/main listed, BRANCH ERROR, exit 1).
20. `test_open_branches_default_computes_shallow` (unit, `_patched_git` / monkeypatch `cp._is_shallow` → True): `open_branches()` with no args skips MAIN. This pins the check_handoff path.
21. Existing (b), (c), P5f (L947), L1053 and L2078 stay unedited. They must pass, and (b)/(c) must still exit 1 (Extra research).
22. UNSHALLOW constant updated. `test_unshallow_sentence_same_in_three_files` passes.

**Mutations:** run on a scratch copy only (`/tmp/claude-0/scratch/i2-090/`). I2 lists each with its failing test and the failed/passed counts. I3 re-runs them.

| ID | Mutation | Must fail |
|---|---|---|
| M1 | write_log: no TIMED_FROM test | 1 |
| M2 | `_TAIL` made mandatory | L712 test |
| M3 | I2_TIMED accepts the time inside the note | 1 (`(in 3.00s)`) |
| M4 | step 2 ID test dropped | 4 (089 twin) |
| M5 | `+1` dropped in the bound | 8 |
| M6 | prev = the item's first line | 7 |
| M7 | per-item filter removed | 9 |
| M8 | no round close in (b) | 16 |
| M9 | substring verdict | 14 |
| M10 | unreadable → still sent back | 14 |
| M11 | `shallow` forced False | 18, 19 |
| M12 | `main_ahead` returns the hint str | 19 |
| M13 | `late_log_lines` returns `[hint]` | 19 |
| M14 | shallow MAIN skip removed | 19 |
| M15 | (a) dropped | 15 |
| M16 | (c) dropped | 16 |
| M17 | lookahead dropped from VERDICT_OF 04 | 14 |

**Done check:**
- Full suite green.
- `python3.11 -m py_compile scripts/check_pipeline.py` if present (RI-008).
- Whole-output diff of `python3 scripts/check_pipeline.py`, before and after on the post-089 tree in a full clone. Expected: 0 changed lines, because no real item is ≥ 90 with an I2 line, there are 0 per-round flags, and the full clone is unchanged (RI-013). If I2's worktree is shallow, it runs `git fetch --unshallow` first, or records the three expected not-checked lines.

**Re-derivations (I2 pastes the commands in 05):**
- 03's 17-round table (0 flagged; 077 r2 91.97/300).
- The 30-line replay of (c) (0 refused).
- (b) for the 4 named lines, plus the 10 git-replayed lines (`git show <line's commit>:work/<ID>/06-verification.md`).
- The 27/27 template-line counts.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 TIMED_FROM, timed I2 form, `_TAIL` stays optional, write_log numeric, incomplete gated, RULE NOT SEEN pair, LOG_HINT | Files 1 (constants, log_fields_ok, incomplete); Tests 1-3 |
| Step 2 not computable → INCOMPLETE for ID ≥ 90, same gate, unreadable stays 089's, batch before INCOMPLETE | Files 1 (BATCH_STRICT, incomplete batch_nc, main order); Tests 4-5 |
| Step 3 per-round bound, prev by 086's order, before the in-progress skip, docstring limit | Files 1 (batch_log_items); Tests 6-12 |
| Step 4 (a) open round | `_round_refusal` (a); Test 15 |
| Step 4 (b) content, first verdict line, refusal on absent/unreadable | `_first_verdict`, (b); Tests 13-14, 17 |
| Step 4 (c) order from send-back/terminal line | (c); Tests 16-17 |
| Step 4 readers via 089's reader | `_first_verdict` and the Scope read use `_read`; 089 read census |
| Step 4 existing exemption fixtures updated | Test 13 |
| Step 5 env before open_branches; three not-checked lines; uniform text; exit pins; UNSHALLOW sentence | Files 1 (`_is_shallow`, readers, main), 3-5; Tests 18-22. Changed: MAIN skipped in shallow (fit change 2) |
| Step 5 "exit 0 with a docs-only branch" | Changed: orphan README-only branch (fit change 3), Test 19 |
| Step 6 docstring gaps | Files 1 docstring bullets |
| Step 7 05 RI lines and re-derivations | Done check / Re-derivations; I2 writes `RI-010:` and `RI-014:` lines in 05 |
| #10 correction (bound catches Δ0 only) | Docstring wording; Test 8 pins Δ1 passes |
| #13/#43 correction (round closes at the next S line; 069/070) | (b) open-round condition; Test 16 |
| #20, #21, #26 removed claims | DROPPED: removed in 03; nothing in the plan depends on them (whole-line not checked; shared-base gap documented) |
| #22 (`--count` documented), #25 (merge-base exit 1 sourced) | No code change; the census reason at L2374-2378 already cites merge-base.c |
| #33 (17 of 18), #48, #49, #51 (7th constant), #41 (run-item L17) | Wording only; L17 edit in Files 3 |
| #46 exact shallow 0 declined | Kept declined: one source (`shallow`) for all lines. Docstring says why so a later item does not "fix" it back |
| #53 (089 census future) | 089 is built first; its census pins the reads |
| #56 (no line before I2 impossible for every scope) | BATCH_STRICT includes it |
| Missing inputs rows 1-9 | Guardrail tests below |
| Rule text the person follows (001 slack/tolerance/cap) | None changed. Agent rule text changed in the same plan: run-item L12/L17, daily-audit, a1-auditor, i2-builder L25 |
| Open Q5 single-branch clone | DROPPED: out of scope (request). I2 names it in 05 for A1 as a possible new item (RI-009) |
| Open Q3 I3 run time in its field | DROPPED: LOG_FORMAT change not requested; known gap in the docstring |

## Guardrail tests
- Feasibility: TIMED_FROM (0 of 0 items ≥ 90 with an I2 line; 17/18 timed) → Test 1 (990 refused, 089 accepted) + done-check diff 0 lines.
- Feasibility: step 2 (0 of 7 not-computable items ≥ 90) → Test 4 (089 twin exit 0) + done-check diff.
- Feasibility: per-round bound (17/17 real rounds, 0 flagged) → Test 11 on repo data; Tests 6/8 pin the 60 s / 120 s limits.
- Feasibility: (c) order (30/30 lines, 0 refused) and (b) (4/4 + 10 replayed) → I2's replay in 05; Tests 16 (069 shape passes) and 14 (refusals).
- Feasibility: shallow fixture counts (A1: full 1 late line vs depth-1 none; MAIN AHEAD 1 vs 0; 1 shared branch) → Test 18 full-clone control vs depth-1.
- Missing inputs: I2 time absent → Tests 1, 3, 5.
- Missing inputs: no line before I2 → Test 5 variant (`no line before I2`, 990 vs 089 twin) and existing N12.
- Missing inputs: 05 anchor absent/uncommitted → Test 3 absent case.
- Missing inputs: 03/04/06 verdict line absent/unreadable/unfilled → Test 14.
- Missing inputs: log file unreadable at `--log` → Test 17.
- Missing inputs: 07 unreadable → existing `_sent_back` refusal side; I2 adds a one-row case to Test 14 (07 b"\xff", no send-back line: D refuses as today).
- Missing inputs: request.md absent → existing L464 (made timed, asserts `item 047`).
- Missing inputs: shallow file unreadable → existing (b)/(c) plus `_is_shallow` returns True for "unreadable" (Test 20 unit row).
- Missing inputs: refs/remotes/origin/main absent → P5f-style default single-branch clone with origin/main present; I2 adds a unit row where `main_ahead(shallow=True)` with no ref → 0, no line.

## Expected result
- `--log I2` for ID ≥ 90 without ` in <s>s` exits 2. A committed untimed ≥ 90 line is INCOMPLETE, or RULE NOT SEEN when 05 predates TIMED_FROM.
- An untimed or invalid-time ≥ 90 item is INCOMPLETE through LOG BATCH not computable. Below 90 nothing changes.
- A same-minute I2 round (Δ0, run ≥ 60.005 s) is flagged in LOG BATCH (exit 1), including after a send-back. The 17 real rounds give 0 flags.
- After a send-back, `--log` refuses an out-of-round line by (a), (b) or (c). The 069/070 histories log cleanly.
- In a depth-1 clone LOG TIME, MAIN AHEAD and the unrelated line say `not checked (shallow clone; run git fetch --unshallow)` and origin/main is not listed. Exit: 0 with an orphan docs-only branch; 1 when a branch holds checked paths.
- Every mutation M1-M17 fails a named test. The suite is green. The real-tree whole-output diff has 0 lines in a full clone.

Conflicts with today's other items:
- **089** must be merged first. `_first_verdict`, the Scope read and `_item_lines` go through `_read`. BATCH_STRICT excludes `unreadable` by equality.
- **091** adds no exit term for 090 (090 adds none: the per-round flags join `batch["flagged"]`, step 2 joins INCOMPLETE). 091's unshallow wording builds on 090's new sentence.
- GIT_CENSUS total stays 47.

Recurring issues checked:
- RI-001 (ESCALATED): every filter, window and refusal rule has a dated count from 03 and a test that pins it (Guardrail tests); none says "always".
- RI-010 (ESCALATED): this item. Gap (y) is closed for Δ0 I rounds and for out-of-order or verdict-changed rounds. The docstring lists what stays open (I3 untimed, a repeat FAIL, A1 FAIL rounds, Δ ≥ 1).
- RI-014 (OPEN): this item. Uniform not-checked text from one `shallow` value, exit pinned in two fixtures, full-clone control, and (b)/(c) kept at exit 1.
- Also checked, GUARDED:
  - RI-002: no absent verdict, time, prev line or shallow state becomes a pass, 0 s or none.
  - RI-012: verdict words are matched in their group with a lookahead, BATCH_STRICT by equality.
  - RI-008: py_compile on 3.11.
  - RI-009: build order and check_handoff's `open_branches` caller.
  - RI-013: whole-output diff.
  - RI-004/005: fixture numbers re-derived (60.01 − 0.005 = 60.005 ≥ 60; 60.00 → 59.995 < 60; 80.00 → 79.995 ≥ 60 at Δ0; 86.00 → 85.995 < 120 at Δ1; Test 7 round 1: 50.00 − 0.005 < (10+1)×60 = 660, so only round 2 flags).
  - RI-006: the file count of 6 is counted from Files 1-6.

Log fields: FIT WITH CHANGES | 6 files planned
