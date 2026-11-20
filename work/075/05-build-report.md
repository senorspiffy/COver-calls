# 05 Build report - 075
Build base: f8981bd (branch daily-fixes/2026-11-19), changes uncommitted (the orchestrator commits code + 05 together).

## Changes made (file: what changed)
- tests/test_agent_tools.py (changed, the only file):
  - Module docstring: item 075 paragraph (any unreadable `tools:`/`disallowedTools:` line or entry is an error, never "not Bash"; the four no-shell agents may list only `NO_SHELL_ALLOWED`).
  - `import re`; `NO_SHELL_ALLOWED` (6 names); `ENTRY_RE = re.compile(r"[A-Za-z]+(\([^()]*\))?")`, used only with `.fullmatch`. `NO_SHELL` unchanged.
  - `_field(lines, key) -> (found, entries, error)` replaces 072's `_field`, with rules (a) key separator, (b) duplicate, tail scan (h) continuation line / (i) blank or comment inside a block list, (c) unclosed `[`, (d) depth-0 comma split + unbalanced parens, (e) one matching quote pair stripped, (f) `ENTRY_RE.fullmatch`, (g) no entries. Applied in the plan's order, first error returned. Small helper `_is_item(s)` (`-` or `- X`), used three times in the tail scan.
  - `agent_tools(text)`: tools error first, then 072's two texts unchanged, then the `disallowedTools` error; names are `e.split("(")[0]`.
  - `tree_problems(texts)`: 072's loop moved out, keyed by stem, label `.claude/agents/<stem>.md` (byte-identical to 072's `relative_to(REPO)` text); empty dict gives `(["no agent files under .claude/agents"], set())`; allow-list problem before the Bash skip, no continue; 072's body-line check unchanged.
  - Tests: CASES a-f unchanged + 27 new (g, h, i1, i2, j1-j3, k, l, m, q, r, s, t1, t2, u, v, w, x, y1-y7, z) with the plan's exact texts; `test_tree_problems` parametrized over n0-n5, n7; `test_tree_problems_no_files` (n6); real-tree test now calls `tree_problems`, with 072's two asserts and the run-item.md strings unchanged.

File counts (commands, item 012):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
1
$ git diff --stat
 tests/test_agent_tools.py | 248 ++++++++++++++++++++++++++++++++++++++--------
 1 file changed, 207 insertions(+), 41 deletions(-)
```
(`git status` also shows `?? work/077/04-build-plan.md`: another item's step file, not this build's.)

## Connectivity check
- [x] every new function/rule is used: `_is_item` and `ENTRY_RE` by `_field`; `_field` by `agent_tools` (twice); `agent_tools` by `tree_problems` and `test_agent_tools_parser`; `tree_problems` by `test_tree_problems`, `test_tree_problems_no_files` and the real-tree test; `NO_SHELL_ALLOWED` by `tree_problems`; `_fm`, `NO_TOOLS`, `SIX`, `BASE`, `R1`, `_allow` by the fixtures.
- [x] every input has a source, every output has a consumer: input is the frontmatter of `.claude/agents/*.md` (real tree) or the fixture texts; outputs are the error strings / problem list, each asserted exactly by a test.
- [x] every branch ends in a defined result: every `_field` path returns `(found, entries, error)`; not found → 072's no-tools text; empty → 072's empty text; each parse error → its named text, which `tree_problems` reports as a problem. Nothing is dropped or defaulted (RI-002).
- [x] no leftover TODOs or unused files (`grep -nE "TODO|FIXME" tests/test_agent_tools.py`: no output). The scratch worktree was removed (`git worktree remove`), and the scratch copy lives only under the scratchpad.

Missing-data policy grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 37 hits, none new or changed (`git diff --stat -- ccbot/` is empty; this build touches no ccbot/ file). No dataclass is added. The only `>`/`>=` tests in the changed file are `len(starts) > 1` and `len(x) >= 2`, on ints (no NaN possible).

Feasibility numbers (plan Guardrail tests, re-measured on today's tree):
- ENTRY_RE: `grep -n "^tools" .claude/agents/*.md` → 7 lines, all comma form (a1 5, i1 6, i2 6, i3 5, r1 6, r2 6, r3 6 = 40 entries); the real-tree test passes, so 40 of 40 entries fullmatch.
- Allow-list: 4 of 4 NO_SHELL files hold exactly `Read, Write, Glob, Grep, WebSearch, WebFetch` (same grep); real-tree test passes.
- Body-line rule: the real-tree test passes, so every no-shell `python3 scripts/` line names the orchestrator (count of 5 is I1's; m1 below shows the check still fires).

## Test output (pasted, not summarized)
```
$ python3 -m pytest -q tests/test_agent_tools.py
..........................................                               [100%]
42 passed in 0.04s

$ python3.11 -m py_compile tests/test_agent_tools.py && echo compile-ok
compile-ok

$ python3 -m pytest -q          (build, uncommitted on f8981bd)
488 passed, 1 skipped in 69.63s (0:01:09)

$ python3 -m pytest -q          (base f8981bd, scratch worktree)
453 passed, 1 skipped in 69.79s (0:01:09)
$ python3 -m pytest -q tests/test_agent_tools.py   (base)
7 passed in 0.01s
```
488 - 453 = 35 = 42 - 7, the added tests only (33 parser + 7 tree + 1 no-files + 1 real-tree = 42).

Probes and mutations (scratch copy `/tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/075-I2/copy`, driver `/tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/075-I2/probe.py`, each change restored before the next; command `python3 -m pytest -q tests/test_agent_tools.py`):

| Probe | pytest last line | failed tests | first assert |
|---|---|---|---|
| x4 r1 flow list +Bash | 1 failed, 41 passed in 0.04s | test_no_shell_agents_leave_commands_to_orchestrator | .claude/agents/r1-researcher.md: tools beyond the no-shell allow-list: Bash (RULES decision, item 075) |
| x5 r1 quoted Bash | 1 failed, 41 passed in 0.04s | test_no_shell_agents_leave_commands_to_orchestrator | .claude/agents/r1-researcher.md: tools beyond the no-shell allow-list: Bash (RULES decision, item 075) |
| x1 i2 flow list | 42 passed in 0.03s | - | - |
| m1 old r1 file | 1 failed, 41 passed in 0.04s | test_no_shell_agents_leave_commands_to_orchestrator | .claude/agents/r1-researcher.md:19: runs a script with no shell (item 072) |
| m2 r2 tools line deleted | 1 failed, 41 passed in 0.04s | test_no_shell_agents_leave_commands_to_orchestrator | .claude/agents/r2-improver.md: no tools: line (inherits every tool incl. Bash, item 072) |
| m3 i1 +Bash | 1 failed, 41 passed in 0.04s | test_no_shell_agents_leave_commands_to_orchestrator | .claude/agents/i1-reviewer.md: tools beyond the no-shell allow-list: Bash (RULES decision, item 075) |
| m4 run-item phrase removed | 1 failed, 41 passed in 0.04s | test_no_shell_agents_leave_commands_to_orchestrator | run-item.md lacks 'the orchestrator runs their commands' (item 072) |
| m5 i2 disallowedTools: Bash | 1 failed, 41 passed in 0.04s | test_no_shell_agents_leave_commands_to_orchestrator | .claude/agents/i2-builder.md:26: runs a script with no shell (item 072) |
| m6 i1 block list | 42 passed in 0.03s | - | - |
| M1 plain comma split | 8 failed, 34 passed in 0.09s | test_agent_tools_parser[g_flow_list_bash], test_agent_tools_parser[h_flow_list], test_agent_tools_parser[j3_unclosed], test_agent_tools_parser[k_paren_comma], test_agent_tools_parser[m_disallowed_flow], test_agent_tools_parser[t1_unbalanced], test_agent_tools_parser[v_empty_flow], test_tree_problems[n1_flow_list_bash] | - |
| M2 quote strip removed | 3 failed, 39 passed in 0.06s | test_agent_tools_parser[i1_double_quoted], test_agent_tools_parser[i2_block_single_quoted], test_tree_problems[n2_quoted_bash] | - |
| M3 ENTRY_RE check removed | 6 failed, 36 passed in 0.08s | test_agent_tools_parser[j1_stray_bracket], test_agent_tools_parser[j2_comment], test_agent_tools_parser[r_whole_quoted], test_agent_tools_parser[t2_two_parens], test_agent_tools_parser[u_empty_entry], test_agent_tools_parser[x_block_scalar] | - |
| M4 plain split (no depth) | 1 failed, 41 passed in 0.05s | test_agent_tools_parser[k_paren_comma] | - |
| M5 allow-list removed | 4 failed, 38 passed in 0.07s | test_tree_problems[n1_flow_list_bash], test_tree_problems[n2_quoted_bash], test_tree_problems[n3_monitor], test_tree_problems[n4_lower_bash] | assert [] == ['.claude/age...n, item 075)'] |
| M6 duplicate check removed | 1 failed, 41 passed in 0.05s | test_agent_tools_parser[l_duplicate] | assert None == 'duplicate tools: line (item 075)' |
| M7 key-separator check removed | 1 failed, 41 passed in 0.05s | test_agent_tools_parser[s_no_space] | assert None == 'tools: needs a space after the colon (item 075)' |
| M8 [^()]* -> .* | 1 failed, 41 passed in 0.05s | test_agent_tools_parser[t2_two_parens] | - |
| M9 rule (i) -> break | 3 failed, 39 passed in 0.06s | test_agent_tools_parser[y2_blank_in_list], test_agent_tools_parser[y3_comment_first], test_agent_tools_parser[y7_disallowed_blank] | assert None == 'blank or comment line inside tools: list (item 075)' |
| M10 rule (h) removed | 2 failed, 40 passed in 0.05s | test_agent_tools_parser[y1_continuation], test_agent_tools_parser[y5_inline_then_item] | - |
| M11 body-line check removed | 1 failed, 41 passed in 0.05s | test_tree_problems[n7_body_line] | assert [] == ['.claude/age...l (item 072)'] |
| M12 fullmatch -> match | 3 failed, 39 passed in 0.06s | test_agent_tools_parser[j1_stray_bracket], test_agent_tools_parser[j2_comment], test_agent_tools_parser[t2_two_parens] | - |
clean: 42 passed in 0.04s

("-" in the last column: the first `E` line was not an `AssertionError: <msg>` line, i.e. a plain `assert error == want` diff.) Every plan-named case fails under its mutation (M1 g, h, n1; M2 i1, i2, n2; M3 j1, j2, t2, x; M4 k; M5 n1-n4; M6 l; M7 s; M8 t2; M9 y2, y3, y7; M10 y1, y5; M11 n7; M12 t2, j1). No mutation left every test green. x4/x5 fail as the request asks; x1 now passes (correct parse, a change from 072's 06); m1-m5 still fail and m6 still passes. Note m3 now reports the allow-list problem first (the 072 set assert is not reached because `problems` is asserted first); it still fails.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: tests/test_agent_tools.py only; no ccbot/realtest.py or TRIGGER file)

## Deviations from plan
None in behaviour. Two small structure choices inside the plan's text: (1) a helper `_is_item(s)` for the `-` / `- X` test used three times in the tail scan; (2) n0-n5 and n7 are one parametrized `test_tree_problems`, and n6 is its own function `test_tree_problems_no_files` (plan allows "one parametrized test or 8 functions"; total 42 as planned).

## Recurring issues checked (item 013)
- RI-001 (ESCALATED): checked. Every filter's count is re-measured above (40/40 entries, 4/4 allow-list files, real-tree test), and each rule has a test that pins it (mutations M1-M12).
- RI-014 (OPEN): checked, not touched (no scripts/check_pipeline.py edit).
- RI-002 (GUARDED, near miss this item fixes): every unreadable line or entry is a named error; absent cases b, q, z, c, v, w, n5, n6 each asserted.
- RI-006: test counts copied from pytest's last lines above.
- RI-008: `python3.11 -m py_compile` passes; no `match` statement.
- RI-009/011: one file, no overlap with 076-079; probes in a scratch copy only.
- RI-012: classification by `fullmatch` on parsed tokens (M12 shows `.match` would fail tests).

RI-002: guardrail built (075); GUARDED when merged and the x4 probe (r1 `tools: [..., Bash]`) fails the real-tree test on main.
RI-001: ESCALATED, unchanged by this item.
RI-014: OPEN, unchanged by this item.
