# 04 Build plan - 104
Fit verdict: FIT

Input: work/104/03-handoff.md (Status: READY, check_handoff PASS pasted 2026-11-24 23:56 UTC, commit e1b2b29). Branch daily-fixes/2026-11-24-b, read only. I1 has no shell, so every trace below was done by hand against tests/test_agent_tools.py as it stands (L1-L535, 109 tests). I2 confirms each one by running it.

Fit check:
- ~$3k account and strategy rules: no effect. This item changes only a repo-hygiene test (tests/test_agent_tools.py). No ccbot/ code, config, rule text in work/001 or order path changes. Nothing the person follows when trading changes, so no 001 rule text update is needed (001: no slack, tolerance or cap involved).
- Existing code: the only reader of `_frontmatter_error` is `agent_tools` in the same file (Grep over tests/ and scripts/, 2026-11-24: 3 hits, all in tests/test_agent_tools.py). No other test counts these tests. No conflict with 099-103 (they touch other files; I did not open them).
- Design: the 03 map fits the current loop. The new code goes after the column-0 (096) check and before the `prev_open` line (L222-L225), so every 080/087/096 error on a line still wins over a 104 error on the same line, and every existing fixture's earlier error is returned first. I re-traced p13, q23, d, y1, y4, p4, nk6, nk7, nk8, z, w, x, j2, s by hand: all keep their result.

## Extra research (with sources)
1. 1024 limit applies to block keys in YAML 1.2, not only 1.1. The libyaml wiki page on YAML 1.2 says: "The maximum key length of 1024 characters has been removed for flow mapping keys." and "libyaml implements the concept of "simple keys" from YAML 1.1." So in 1.2 the cap was dropped only for flow mapping keys. Block implicit keys, the only kind that KEY_RE reads at line start, keep it. This supports D5 as a fail-closed cap at any indent. It also confirms that keys inside `{...}` flow values need no cap: those values are skipped by `t[0] in "\"'[{"` and the cap never reaches them. Source: https://github.com/yaml/libyaml/wiki/YAML-1.2 (fetched 2026-11-24). The page does not quote the spec's exact wording. R3's row 26 still holds: I could not read the 1.2 spec text with "1024" either (https://yaml.org/spec/1.2-old/spec.html, the reader stopped at 5.7). Nothing is claimed about PyYAML's boundary. I2's D5 probe decides it.
2. Edge case R3 missed (information, no plan change): a continuation under a closed FLOW_KEYS line, for example `tools: Read, Write` then `  foo: bar`, now returns VALUE(3) from the continuation branch. Today it returns `_field`'s `unparsed tools: line 'foo: bar' (item 075)`. Both fail closed, and no existing fixture has this shape: y1 is `  , Bash` with no colon, and y5 is `  - Bash`, which becomes a structure line. The docstring's "`tools:`/`disallowedTools:` lines are left to `_field`" stays true, because it names the key line itself. No fixture is added. I2 notes this in 05 if the probe table shows it.
3. Correction to 03 Self-check 26 (number only, kill list unchanged): under M64, p13's `      hooks:` is frontmatter index 6, so the error is VALUE(8), not VALUE(7). The lines are name 2, description 3, tools 4, hooks 5, PreToolUse 6, matcher 7, hooks 8. M64 still kills only p13. 05 records whatever the run prints, and this is not a Deviation.
4. Typing note for I2: 03 map steps 1 and 4 escape `|` as `\|` inside Markdown table cells (03 L111). The code uses a plain `|`: `BLOCK_RE = re.compile(r"[|>](?:[1-9][-+]?|[-+][1-9]?)?(?:[ \t]+#.*)?[ \t]*")`, `ITEMS_RE = re.compile(r"(?:-(?:[ \t]+|$))*")`, `t[0] in "|>"`.

## Files to create/change
1. tests/test_agent_tools.py (the only code file)
   - Constants next to KEY_RE (03 step 1): BLOCK_RE, ITEMS_RE, COMMENT_CUT_RE, COLON_RE, KEY_MAX = 1024. Error texts next to NO_KEY, exactly as D7: VALUE, KEY_LONG, BLOCK.
   - Helpers (03 step 2): `_is_open(rest)`, `_plain_colon(text)`, `_node(line, n, check)` returning `(error, col, is_open, starts_block)`. Python 3.10 syntax only (RI-008): no walrus, no `match`.
   - `_frontmatter_error` (03 step 3): add `prev = None`, `block = None`; add the block-skip, continuation and structure-line branch between the column-0 check and the `prev_open` update; change the `prev_open` line to use `_is_open(line[k.end():])` (F-5). Docstring changes to "(items 080, 087, 096, 104)". Do not reuse `s`, `c` or the existing loop `t` before it is set.
   - CASES: v1-v22 as listed in 03 step 4 (ids may get a descriptive suffix, e.g. `v1_value_colon`). TREE: n13_value_colon.
   - Module docstring (03 step 6): add the "Item 104:" paragraph. In "Item 096", delete the clause at L47-L48 ("a column-0 item after an empty-valued key that carries a comment (`hooks: # c`);"). Leave the 080/087 false-error lists unchanged (D2).
2. work/104/05-build-report.md (I2's own step file: run output, mutation table, PyYAML probe table). Not counted as a planned code file.

## Tests and checks
- `python3 -m pytest tests/test_agent_tools.py -q` → 132 passed (109 + 22 parser + 1 tree).
- Base check (old `_frontmatter_error` with the new fixtures, scratch copy): exactly 13 failed, 119 passed. The 13 are v1, v2, v3, v6, v11, v12, v13, v15, v16, v18, v19, v21, n13.
- Full suite `python3 -m pytest -q`: same result as before plus 23 passed. Paste the pytest line as printed (RI-006).
- `python3.11 -m py_compile tests/test_agent_tools.py` where available (RI-008).
- Mutations M56-M68, one at a time, on a scratch copy (never in the repo, RI-009 lesson 034). Each must fail exactly the ids in 03 step 5. The 096 mutations M41-M55 must still fail every id in their 096/05 lists. Any new 104 ids they also fail are recorded and are not a Deviation.
- PyYAML probe (03 step 7) in a scratch venv, with the version printed, as information only (D6: no importorskip in the test). It covers v1-v22, `name: x` / `  - a`, `hooks:` / `    a: b` / `  c: d`, and the D5 boundary (1024 and 1025 as the first line, after `name: x`, and indented under `hooks:`). D8 applies if v2 or v11 loads. D5 applies if the boundary differs.
- Real tree: `test_no_shell_agents_leave_commands_to_orchestrator` passes with 21 of 21 frontmatter lines. I re-ran R3's Grep 2026-11-24: `^(name|description|tools):.*(:[ \t]|:$| #)` over .claude/agents → 0 hits.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 constants (BLOCK_RE, ITEMS_RE, COMMENT_CUT_RE, COLON_RE, KEY_MAX, VALUE/KEY_LONG/BLOCK) | Files 1, first bullet; plain `|` per Extra research 4 |
| Step 2 `_is_open`, `_plain_colon`, `_node` | Files 1, second bullet; pinned by v1-v22, mutations M56-M68 |
| Step 3 loop change (prev, block, continuation, structure line, F-5 `prev_open`) | Files 1, third bullet; 132 passed + base 13 failed |
| Step 4 fixtures v1-v22, n13 | Files 1, fourth bullet |
| Step 5 mutations M56-M68, M41-M55 still kill | Tests and checks, mutation line |
| Step 6 docstring paragraph + 096 clause removal | Files 1, fifth bullet; I3 reads the diff |
| Step 7 PyYAML probe, information only | Tests and checks, probe line |
| D1 continuation lines allowed, plain check on whole text | Step 3 continuation branch; v6 (error), v7 (pass); M58 |
| D2 block content skipped by 104 checks only | Step 3 block skip; v9, v10, v12; M62, M65 |
| D3 no sibling-indent stack | DROPPED: R3 decision, documented in the docstring as not checked |
| D4 `_field` unchanged | v21, v22 pin its texts; no edit to `_field` |
| D5 cap `colon index − key start > 1024`, any indent; I2 may lower it | v13-v17; M59, M60, M68; probe in step 7 |
| D6 no importorskip cross-check | Tests and checks, probe line (scratch venv only) |
| D7 error texts | Files 1, first bullet, verbatim |
| D8 `name: x:` and `> foo` fail closed | v2, v11; docstring update if the probe loads them |
| Missing inputs table (prev, prev_open, key, block, unreadable value) | Guardrail tests, Missing inputs |
| Removed claims 1-5 (no PyYAML facts) | 04 states none as fact; probe output only in 05/06 |
| Self-check 26 line number | Corrected in Extra research 3 (VALUE(8)); kill list unchanged |

## Guardrail tests
- Feasibility: plain value colon rule → 21 of 21 real frontmatter lines pass (7 files, R3 Grep 2026-11-24, I1 re-run 0 hits). Pinned by `test_no_shell_agents_leave_commands_to_orchestrator`. Existing fixtures: 107 of 107 keep their result (R3 trace; I1 spot-traced 14). Pinned by the full parametrized run.
- Feasibility: key cap 1024 → longest real key 11 (21 lines, 2026-11-24); pinned by the real-tree test; boundary pinned by v13/v14 (col 0), v15 (after a key), v16/v17 (indented); M60 and M68 kill the off-by-one and wrong-origin variants.
- Feasibility: block header rule → 0 real block headers, 1 fixture header in FLOW_KEYS (x_block_scalar, unchanged); v9, v10 (pass), v11 (BLOCK), v12 (block ends); M62, M65, M66, M67.
- Feasibility: continuation rule → 0 real indented lines; p13, q23, d, y1, y4 keep their result; v6/v7/v8; M58, M64.
- Missing inputs: no previous structure line (first line) → v1, v13 (the first line is a structure line, never a continuation).
- Missing inputs: `prev_open` with a column-0 item as the first line → nk11 unchanged (NO_KEY(2)).
- Missing inputs: no key on a structure line → v8 (`  plain text`, plain check, no cap) and d/y4.
- Missing inputs: no block header seen (`block = None`) → v1-v8 (no line treated as content); M65 pins the block end.
- Missing inputs: unreadable value / header / key → VALUE (v1, v2, v3, v6, v12, n13), BLOCK (v11), KEY_LONG (v13, v15, v16); never a tool set.

## Expected result
- tests/test_agent_tools.py: 132 passed; base check 13 failed, 119 passed; full suite +23 passed, no other change.
- Each F-1 to F-4 shape gives a named error: F-1 v1/v2 VALUE, F-2 v6 VALUE, F-3 v13 KEY_LONG, F-4 v3/v11/v16. F-5 (v18, v19) passes. The real agent files still pass.
- M56-M68 each fail the ids in 03 step 5 (M64 prints VALUE(8)); M41-M55 still fail their 096 ids.
- PyYAML probe table in 05 with version, information only.

Recurring issues checked (logs/recurring-issues.md, read first): RI-001 ESCALATED: every new filter has a dated count (21/21 real lines, 0 Grep hits, re-run 2026-11-24) and a pinning test. RI-010 ESCALATED: I write no log line; the orchestrator copies the last line via `--log`. RI-014 OPEN: does not apply (no git or clone path). GUARDED entries: RI-002 (this item's root cause; every unreadable shape is a named error, Missing inputs listed), RI-004/005 (re-traced the self-check, found the M64 line-number slip), RI-006 (no hand totals beyond the 03 counts; pytest line pasted as printed), RI-007 (Scope FULL, I1-I3 run, no code before 04), RI-008 (3.10 syntax, py_compile), RI-009 (mutations on a scratch copy only), RI-012 (in-text negatives v4, v5, v7, v8, v9, v10, v14, v17 kept). RI-003, RI-011 and RI-013 do not apply.

Log fields: FIT | 1 files planned
