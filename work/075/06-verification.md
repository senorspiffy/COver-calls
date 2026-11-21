# 06 Verification - 075
Verdict: PASS (round 1)
Sent back to: none

Build commit checked: f47deb5 (branch daily-fixes/2026-11-19; base f8981bd). HEAD is now dcfdd47 (077 I1 plan: work/077/04-build-plan.md + 1 log line only; `git diff f47deb5 HEAD --stat` touches no code). Scratch worktrees: `/tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/075-I3/head` (f47deb5) and `.../075-I3/base` (f8981bd), driver `.../075-I3/drive.py`, output `.../075-I3/head-probes.txt`.

## I1 audit (plan vs research)
- 03 map steps 1-5, D1-D7 and the 7 Missing inputs rows are each traced in 04's Rule trace table; I checked each row against 03 text. Step 1 rules (a)-(g), error texts, ENTRY_RE (with `fullmatch`, so the `^...$` anchors of 03 are equivalent), NO_SHELL_ALLOWED (6 names), allow-list placed before the Bash skip with 072's checks kept, `tree_problems(texts)` refactor, fixtures g-x and n0-n4 with the exact texts, probes x1/x4/x5, m1-m6 and M1-M8: all carried over unchanged.
- D5 (wording regex) DROPPED with 03's own reason. Correct.
- Additions beyond 03, all sourced or fail-closed by construction: rule (h) continuation line (YAML 1.2.2 §2.3/§6.5 quote), rule (i) blank/comment inside a block list (YAML 1.2.2 Example 2.9; 04 says honestly the blank-line case rests on the separation rules, not a quote; it is an error either way, so it cannot open a hole), fixture z (key with space before colon, fail closed, no source needed), n5/n6 (03's own Missing inputs rows that had no fixture), n7 (body-line check pin), M9-M12. No unsourced addition that changes behaviour toward "allowed".
- Fit check: one file, tests only; no 001 rule text, ccbot/ or config change. Confirmed by `git show --stat f47deb5` (tests/test_agent_tools.py, work/075/05, 1 log line).

## I2 audit (build vs plan)
Line by line against 04 "Files to create/change", reading f47deb5's tests/test_agent_tools.py and `git diff f8981bd f47deb5`:
- Docstring paragraph (item 075): present, as planned.
- `import re`, `ENTRY_RE = re.compile(r"[A-Za-z]+(\([^()]*\))?")` used only with `.fullmatch` (and nowhere else), `NO_SHELL_ALLOWED` = the 6 names, `NO_SHELL` unchanged: yes.
- `_field`: (a) checked on every key line before (b); (b) duplicate; none → `(False, [], None)`; tail scan stops at the first non-blank, non-comment, column-0 line that is not `-`/`- X`; (h) with an inline value any non-blank/non-comment tail line is an error, and any indented non-item line is the (h) text; (i) a blank or comment line followed by an item (before the first item too) is an error; (c) unclosed `[`; `[]`/blank inner → no entries; (d) depth-0 split and both unbalanced cases; (e) one matching quote pair if len >= 2; (f) fullmatch; (g) `(True, [], None)`. Order and texts match the plan. The helper `_is_item` is a structure choice declared in 05 Deviations; behaviour unchanged.
- `agent_tools`: tools error first, then 072's two texts byte-identical, then the disallowedTools error; names `e.split("(")[0]` (072's `.strip()` dropped, which is safe because fullmatch forbids spaces before `(`).
- `tree_problems`: label `.claude/agents/<stem>.md` (same bytes as 072's `relative_to(REPO)`), empty-dict text, parse error + continue, allow-list problem with no continue, Bash skip, 072's body-line loop byte-identical. Real-tree test keeps 072's two asserts and run-item.md strings.
- Fixtures: all 27 planned parser cases (g ... x, y1-y7, z) with the plan's exact expected values; TREE n0-n5, n7 plus `test_tree_problems_no_files` (n6), as the plan allows. 6 + 27 = 33 parser tests + 7 + 1 + 1 = 42.
- Connectivity re-done: every new name is used (`_is_item` 3x in `_field`; `_field` 2x in `agent_tools`; `agent_tools` by `tree_problems` and the parser test; `tree_problems` by 3 tests; `NO_SHELL_ALLOWED` by `tree_problems`; `_fm`, `NO_TOOLS`, `SIX`, `BASE`, `R1`, `_allow` by fixtures). Every `_field` path returns a 3-tuple; every error reaches a problem line or a parser assert. `grep -nE "TODO|FIXME" tests/test_agent_tools.py`: none. No other file imports it.
- 05's missing-data grep: this build touches no ccbot/ file (`git diff --stat f8981bd f47deb5 -- ccbot/` empty), so its 37 hits are unchanged; the grep reasons hold.
- Deviations in 05 (helper, n6 as its own function): both inside the plan's text. Accepted.

## Tests re-run (output)
```
$ python3 -m pytest -q tests/test_agent_tools.py          (worktree f47deb5)
42 passed in 0.04s
$ python3 -m pytest -q tests/test_agent_tools.py          (worktree f8981bd, base)
7 passed in 0.03s
$ python3 -m pytest -q                                    (repo, HEAD dcfdd47 = f47deb5 code)
488 passed, 1 skipped in 64.91s (0:01:04)
$ python3 -m pytest -q -rs | grep -i skip
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
$ python3 -m pytest -q tests/test_safety.py -k oldest
1 passed, 8 deselected in 0.12s
$ python3.11 -m py_compile tests/test_agent_tools.py && echo compile-ok
compile-ok
$ python3 scripts/check_handoff.py 075
sources count (unique URLs in 01-research.md): 3
fact-check rows: 62
totals line: 62 rows -> 55 as-is, 6 fixed, 1 removed
PASS
```
Counts match 05 (42; 488 passed, 1 skipped; 488 - 453 = 35 = 42 - 7). The oldest-Python compile test ran (python3.11 on PATH, python3.10 not), it did not skip.

Probes and mutations (my own driver, scratch worktree only, `git checkout -- .` before each and after the last; final `git status --short` empty). Head f47deb5:
```
== clean                                  42 passed
== x4 r1 flow list +Bash                  1 failed, 41 passed  E .claude/agents/r1-researcher.md: tools beyond the no-shell allow-list: Bash (RULES decision, item 075)
== x5 r1 quoted Bash                      1 failed, 41 passed  E (same allow-list text naming Bash)
== x1 i2 flow list                        42 passed  (correct parse, a change from 072's 06)
== m1 r1 L19 without orchestrator         1 failed  E .claude/agents/r1-researcher.md:19: runs a script with no shell (item 072)
== m2 r2 tools line deleted               1 failed  E .claude/agents/r2-improver.md: no tools: line (inherits every tool incl. Bash, item 072)
== m3 i1 +Bash                            1 failed  E .claude/agents/i1-reviewer.md: tools beyond the no-shell allow-list: Bash (RULES decision, item 075)
== m4 run-item phrase removed             1 failed
== m5 i2 disallowedTools: Bash            1 failed  E .claude/agents/i2-builder.md:26: runs a script with no shell (item 072)
== m6 i1 block list                       42 passed
== x6 r1 continuation `  , Bash` (I3)     1 failed  E .claude/agents/r1-researcher.md: unparsed tools: line ', Bash' (item 075)
== x7 r1 block list blank then Bash (I3)  1 failed  E .claude/agents/r1-researcher.md: blank or comment line inside tools: list (item 075)
== x8 r1 `tools:Read,...` no space (I3)   1 failed  E .claude/agents/r1-researcher.md: tools: needs a space after the colon (item 075)
== M1 plain comma split      8 failed, 34 passed: g, h, j3, k, m, t1, v, n1
== M2 quote strip removed    3 failed, 39 passed: i1, i2, n2
== M3 ENTRY_RE check removed 6 failed, 36 passed: j1, j2, r, t2, u, x
== M4 plain split (no depth) 1 failed, 41 passed: k
== M5 allow-list removed     4 failed, 38 passed: n1, n2, n3, n4
== M6 duplicate removed      1 failed, 41 passed: l
== M7 key-separator removed  1 failed, 41 passed: s
== M8 [^()]* -> .*           1 failed, 41 passed: t2
== M9 rule (i) -> break      3 failed, 39 passed: y2, y3, y7
== M10 rule (h) removed      2 failed, 40 passed: y1, y5
== M11 body-line removed     1 failed, 41 passed: n7
== M12 fullmatch -> match    3 failed, 39 passed: j1, j2, t2
== M13 key match `(key+":") in line` instead of startswith (I3, RI-012)  1 failed, 41 passed: w
== M14 `_is_item` drops bare `-` (I3)   42 passed (see note)
```
Every plan-named case fails under its mutation; results are identical to 05's table for x1/x4/x5, m1-m6 and M1-M12. M14 note: the only extra mutation left green. It changes the error text, not the outcome: `tools:` / `  -` then gives `unparsed tools: line '-'` instead of `unparsed tools: entry ''`, still an error, and a column-0 bare `-` ends the list (072's empty/absent texts). No path becomes "allowed", so it is not a hole, but no fixture pins the bare-`-` text that 03 D1(2) names. Listed for Audit (07), not a FAIL.

Same driver on base f8981bd (the original error): x4, x5, x6, x7, x8 all give `7 passed` (Bash on r1 undetected); on the head each is red with a named problem. This shows the guardrail catches the original error and the two forms I1 added.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat f8981bd f47deb5`: logs/implementation/2026-11-19.md, tests/test_agent_tools.py, work/075/05-build-report.md; none is in TRIGGER or TRIGGER_DIRS)

## BUG checks (step 3)
- Fix in place: inline `[...]` lists and quotes are parsed (g, h, i1, i2, n1, n2). Guardrail in place: every unreadable line or entry is a named error (j1-j3, r, s, t1, t2, u, x, y1-y5, y7), and the four no-shell agents are held to an allow-list by exact name (n1-n4). Would have caught the original: x4 is green on base, red on head (above).
- RI-002 restore in scratch: M3 puts back the removed default (an unrecognised token is kept as a plain name, i.e. "not Bash") → 6 failed; restored, 42 passed.
- RI-001 feasibility re-run: `grep -n "^tools" .claude/agents/*.md` → 7 lines, comma form, 5+6+6+5+6+6+6 = 40 entries, 0 `disallowedTools:`; real-tree test passes, so 40 of 40 fullmatch and 4 of 4 NO_SHELL sets are the 6 allowed names, as 03/04/05 cite. Body-line count 5 is I1's; m1 shows the check fires on r1 L19.
- Data-window edges: not a data-hole check (no time series). The analogous edges are covered: before the first block item (y3), between items (y2, y7), after the last item / at the list end (y6, d, c), and continuation after an inline value (y1, y5).
- 001 rule text: no rule the person follows changes.
- RI-012 text classification: tokens are classified by `fullmatch` and keys by `startswith`, never a substring. Negative test with the pattern inside other text: w (`tools:` inside `disallowedtools:`) fails under M13; j2 (`Bash` inside `Write # Bash`) and n4 (`bash`) are errors, not matches. The body-line check (`"orchestrator" not in line`) is 072 code, byte-unchanged, and its tightening was dropped as out of scope (03 D5).
- Simulator/replay (062): not applicable.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (feasibility counts 40/40, 4/4 re-measured and pinned by the real-tree test), RI-002 (this item's near miss; M3 default restored → 6 failed; base vs head on x4-x8), RI-006 (all counts copied from pytest's last lines), RI-008 (python3.11 py_compile ok; oldest-Python test passed, not skipped), RI-009/RI-011 (single file, no overlap with 076-079; HEAD moved to dcfdd47 with no code change), RI-012 (M13 negative test w fails), RI-013 (no realtest change; Real-data not required), RI-014 (OPEN: check_pipeline.py not touched; this clone's run shows `UNTRACKED CHANGE: none`), RI-007/RI-010 (FULL scope, steps 01-05 present, log line via --log). RI-003, RI-004, RI-005: GUARDED, not touched (no calendar or worked-example change; every new fixture traced in 04).

## Pipeline line (step 2)
check_pipeline line: `075: awaiting A1 (FULL)` (run after 06, 07 and the --log line were written; INCOMPLETE none, LOG TIME none, UNTRACKED CHANGE none)

## Sent back / sent to Audit
Sent to Audit: yes (work/075/07-audit-task.md). Nothing sent back.
