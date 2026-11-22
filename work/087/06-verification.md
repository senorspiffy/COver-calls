# 06 Verification - 087
Verdict: FAIL (round 1)
Sent back to: I1 I2

Head verified: fd73de1 (I2), base 0ad4d62. All runs below in my own worktrees of fd73de1 (/tmp/claude-0/scratch/i3-087/wt for the suite, /tmp/claude-0/scratch/i3-087/mut for mutations and probes), never in the main checkout. `git rev-parse --is-shallow-repository` → `false`.

## I1 audit (plan vs research)
- 04 follows 03's map step by step (VALUE_START_RE text, FLOW_KEYS, `_flow_end`, D5 order, the four 087 texts, p11 flip, q1-q26, n10/n11, M25-M37, 080 re-runs). The Rule trace table covers every 03 step, decision D1-D6 and correction row; the dropped corrections have a stated reason (wording only, no code effect).
- Unsourced additions: C1 (document markers, DOC_MARKER_RE, q27/q28, M38/M38b) is sourced (PyYAML docs quote on `---`/`...` and `load` returning the first document) and costed (0 real lines, Grep dated 2026-11-21). C2 is docstring only. Fixture names are cosmetic. No unsourced addition.
- Error in 04 (no code effect): Checks 2 says "25 parser + 2 tree + p11 = 28" fail on the base, 61 pass. The named list (q1-q5, q7-q20, q25, q27, q28) is 22 parser cases, so 25 tests fail and 64 pass. 05 Deviation 1 is right; my base run below gives the same 25.
- **Gap (finding F1, RI-012 / item 059):** 04 adds two new text-match classifiers with no negative fixture where the pattern sits inside other text: DOC_MARKER_RE (`---`/`...` matched at column 0) and the flow rule (`[`/`{` taken as a flow start only at the value start). 03/04 pinned anchoring only for the START rule (q21, q22, M26). See I2 audit for the surviving mutations.

## I2 audit (build vs plan)
`git diff 0ad4d62 fd73de1 --stat`: logs/implementation/2026-11-22.md, tests/test_agent_tools.py, work/087/05-build-report.md. Only the one planned code file.

Line by line against 04 Files 1-5:
- Files 1: VALUE_START_RE byte-identical to 04; DOC_MARKER_RE `(?:---|\.\.\.)(?:[ \t]|$)`; FLOW_KEYS tuple; AFTER_CLOSE_RE, ENTRY_RE unchanged. QUOTE_START_RE removed (no remaining use).
- Files 2: `_flow_end` matches 03 step 1 (closer stack, `_quote_end` skip, ` #`/`\t#` → None, mismatch → None, empty stack → `i + 1`, end → None), no annotation.
- Files 3: order DOC → leading tab (080 text) → TAB_BEFORE → START (`&!*?:`) → 080 quote logic with `s` → flow rule on non-FLOW_KEYS lines (FLOW_OPEN / FLOW_AFTER). Texts as module constants with 04's wording; docstring "(items 080, 087)". `_field`, `agent_tools`, `tree_problems`, NO_SHELL_ALLOWED untouched.
- Files 4: "Item 087" docstring paragraph has every 04 bullet, C2 and the kept "This says nothing about what Claude Code does" sentence.
- Files 5: p11 → `(None, TAB_BEFORE.format(2))`; q1-q28 and n10/n11 with 04's ids and texts (checked each row against the 04 table).
- Deviations 1-3 in 05 accepted (1 is 04's arithmetic, 2 is a shorthand constant, 3 keeps 080 f-strings as 04 says "unchanged").

Connectivity re-done: `_flow_end` is called only from `_frontmatter_error`; VALUE_START_RE, DOC_MARKER_RE, FLOW_KEYS used there; START/FLOW_OPEN/FLOW_AFTER/TAB_BEFORE/DOC returned and asserted by fixtures; every error goes `agent_tools` → `tree_problems` → real-tree assertion; `grep -rn QUOTE_START_RE --include=*.py` in the worktree: no output. No TODO, no new default.

Base-failure check, re-run (base 0ad4d62 parser above `def _fm(` + head fixtures):
```
FAILED ...[p11_tab_after_colon] [q10_comment_closer] [q11_wrong_closer] [q12_text_after_flow]
[q13_flow_next_line] [q14_anchor_alone] [q15_item_open_map] [q16_explicit_key] [q17_colon_start]
[q18_dash_tab] [q19_alias] [q1_anchor_dq] [q20_tag_on_tools] [q25_open_flow_last_line]
[q27_doc_end_marker] [q28_doc_start_marker] [q2_tag_dq] [q3_tag_sq] [q4_anchor_tag_dq]
[q5_item_anchor] [q7_open_seq] [q8_open_map] [q9_quoted_closer]
test_tree_problems[n10_anchor_description] test_tree_problems[n11_open_flow]
25 failed, 64 passed in 0.21s
```
Same set as 05. The guardrail catches the original error: every A1 shape from the request fails on the base parser (q1-q5, q7) and passes on head only as a named error.

Probes on the real .claude/agents/r1-researcher.md (scratch worktree, restored, `cmp` identical):
```
A1-1 | 1 failed | value starts with '&' on frontmatter line 3 (item 087)
A1-2 | 1 failed | value starts with '!' on frontmatter line 3 (item 087)
A1-3 | 1 failed | value starts with '!' on frontmatter line 3 (item 087)
A1-4 | 1 failed | value starts with '&' on frontmatter line 3 (item 087)
hooks | 1 failed | value starts with '&' on frontmatter line 6 (item 087)
flow | 1 failed | unclosed flow collection on frontmatter line 3 (item 087)
doc | 1 failed | document marker on frontmatter line 4 (item 087)
I3 mid-value ... (negative) | 1 passed | -   (description: Wait... then --- see [a and {b)
unchanged | 1 passed | -
```

Mutations re-run (my script /tmp/claude-0/scratch/i3-087/tools/mut.py, one at a time, each anchor asserted once, file restored, `git status --porcelain` empty after):
```
M25 &!* dropped | 9 failed, 80 passed | q14 q19 q1 q20 q2 q3 q4 q5 n10
M30 closer type not compared | 1 failed, 88 passed | q11_wrong_closer
M32 FLOW_KEYS exemption removed | 2 failed, 87 passed | j3_unclosed q26_disallowed_open
M33 key class back | 1 failed, 88 passed | q15_item_open_map
M35 TAB_BEFORE removed | 2 failed, 87 passed | p11_tab_after_colon q18_dash_tab
M37 flow rule removed | 10 failed, 79 passed | q10 q11 q12 q13 q15 q25 q7 q8 q9 n11
M38 doc rule removed | 2 failed, 87 passed | q27_doc_end_marker q28_doc_start_marker
I3-c START searched anywhere (&!*?) | 6 failed, 83 passed | e f q17 q21 q22 real-tree
I3-a DOC .match -> .search | 89 passed in 0.09s |
I3-b flow [/{ searched anywhere in the line | 89 passed in 0.06s |
I3-d DOC terminator (?:[ \t]|$) dropped | 89 passed in 0.07s |
```
I3-a: `if DOC_MARKER_RE.match(line):` → `.search(line)`. I3-b: `elif c in "[{" and ...` → `elif re.search(r"[\[{]", line) and ...` with `s` set to that match's start. I3-d: `DOC_MARKER_RE = re.compile(r"(?:---|\.\.\.)")`. These three leave all 89 tests green. The head code is right (the negative probe above passes), but nothing pins it. This is the RI-012 shape the rules name (item 059): a classifier that matches text (`...`, `--- `, `[`, `{`) with no negative test that has the pattern inside other text. Under the i3 rule, that FAILs the item.

## Tests re-run (output)
Full suite, worktree /tmp/claude-0/scratch/i3-087/wt at fd73de1, `python3 -B -m pytest -q -p no:cacheprovider -rs`:
```
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
728 passed, 1 skipped in 86.20s (0:01:26)
```
Same totals as 05 (728 passed, 1 skipped). `tests/test_agent_tools.py`: `89 passed in 0.07s`. `python3.11 -m py_compile tests/test_agent_tools.py` → ok. `tests/test_safety.py -k oldest` → `1 passed` (python3.11 on PATH, python3.10 not; the test ran, did not skip).

check_handoff (main checkout, 2026-11-22, exit 0):
```
sources count (unique URLs in 01-research.md): 5
fact-check rows: 84
totals line: 84 rows -> 64 as-is, 19 fixed, 1 removed
PASS
```

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 0ad4d62 fd73de1`: logs/implementation/2026-11-22.md, tests/test_agent_tools.py, work/087/05-build-report.md; no ccbot/, config/ or data/ file)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (ESCALATED: real-tree test passes at fd73de1, so 0 of 21 real frontmatter lines fire; each firing side pinned, except the mid-text negatives in F1), RI-010 (ESCALATED: this line written by `check_pipeline.py --log` right after this file; suite line copied as printed), RI-014 (OPEN: not touched, repo not shallow), RI-012 (GUARDED: FAIL here, F1: DOC and flow classifiers lack mid-text negative tests, mutations I3-a/b/d survive), RI-002 (GUARDED: base parser fails all 25 named fixtures; each unreadable start is a named error), RI-006 (totals copied from pytest), RI-008 (3.11 compile ok), RI-009/011 (own worktrees only; staged only my files)

## Pipeline line (step 2)
check_pipeline line: `087: I3 FAIL (FULL; sent back to I1 I2, needs a later PASS round in 06 (item 071))` (expected for a FAIL round; run after this file and the `--log` line; exit 1)

## Sent back / sent to Audit
FAIL, round 1. Not sent to Audit; no 07.

To I1 (plan) then I2 (build), problem F1:
1. Add a negative parser fixture for DOC_MARKER_RE with the marker inside other text, e.g. `q29_mid_value_markers`: `_fm("description: Wait... then --- more", TOOLS)` → {Read, Write}. Must fail under I3-a (`.match` → `.search`).
2. Add a negative fixture for the marker terminator, e.g. `q30_marker_prefix_text`: `_fm("name: x", "...x", "---x", TOOLS)` → {Read, Write}. Must fail under I3-d (`(?:[ \t]|$)` dropped).
3. Add a negative fixture for the flow rule with `[`/`{` mid-value, e.g. `q31_mid_value_bracket`: `_fm("description: see [a and {b", TOOLS)` → {Read, Write}. Must fail under I3-b (flow start searched anywhere).
4. 05 records I3-a, I3-b, I3-d as mutations with their failing ids; update the file counts (92 tests, suite +33) and fix 04 Checks 2's tally to 25 / 64.
Everything else in the build matches the plan and needs no change.
