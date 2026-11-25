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

## Round 2 (2026-11-25, I1, after 06 FAIL round 1)
Input: work/104/06-verification.md (Verdict: FAIL (round 1), Sent back to: I1 I2; head fcf3cff). I1 re-read logs/recurring-issues.md and tests/test_agent_tools.py as built: COMMENT_CUT_RE L82, ITEMS_RE L81, `_is_open` L208, `_plain_colon` L214-L219, `_node` L222-L247 (`t[0] in "|>"` L241), `_frontmatter_error` L250-L306, CASES v1-v22 L535-L562. No shell, so every trace below is by hand; I2 runs them. Scratch dir (given by the orchestrator): /tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i1-104-r2-zms85tlk (not used; no files written there).

Fit verdict (round 2): FIT. Same single file, same scope. Round 2 adds 4 fixtures only. The parser code, the error texts and the docstring do not change: the "Item 104:" paragraph already states each rule these fixtures pin ("outside a ` #` comment", "A value starting with `|` or `>`", "indented past a scalar-valued parent's node column").

I3 findings (copied, 06 "Sent back" 1): RI-012 / item 059. Three text classifiers have no test with their pattern inside other text. X2 (`COMMENT_CUT_RE = r"#"`) and X3 (`if "|" in t or ">" in t:`) each leave all 132 tests green. X2 is fail-open: `name: a#b: c` would pass, but PyYAML raises on it (06 probe i3a). X4 (`ITEMS_RE = r"(?:-[ \t]*)*"`) also leaves all 132 green. I3 found no shape where X4 changes the verdict and left the pin to I1.

Research gap check: no R1/R3 re-run is needed. 03's rules are unchanged and no 03 row is wrong. The fixtures pin rules 03 already states, and the PyYAML verdicts for (a) and (b) are measured in 06 (PyYAML 6.0.4, both loaders).

### R2 extra research (with sources)
1. YAML plain scalar rules (rlsp-yaml-parser `lexer/plain.rs`, YAML 1.2 productions, fetched 2026-11-25): `ns_plain_char_block` is "Any `ns-plain-safe(c)` that is not `:` or `#`", with "`#` is allowed only when NOT preceded by whitespace" and "`:` is allowed only when followed by a safe plain char". So in `a#b: c` the `#` is text, not a comment, and the `: ` after it ends the scalar. That is the X2 shape (a). The same file's `ns_plain_first` says `?`, `:` and `-` may start a plain scalar "if ... the next character is a safe plain char". `|` and `>` are rejected only as a first character (`is_c_indicator`). The file has no rule against them later in the scalar. I read that from the code; the source does not say it in words. 06 probes i3b/i3c measure it: both loaders load `a > b` and `a | b`. So a header is recognised only from the value's first character, and that is the X3 shape (b). Source: https://docs.rs/crate/rlsp-yaml-parser/0.6.1/source/src/lexer/plain.rs. I could not reach the plain-style section of https://yaml.org/spec/1.2.2/ (the reader stopped at 6.6, "Comments must be separated from other tokens by white space characters.").
2. Edge case I3 missed: X4 does change a verdict. A column-0 key that starts with `-` and no space (`-a`) is a valid plain key per item 1. With the round 1 ITEMS_RE, `-a: b` has node column 0. Under X4 the `-` is eaten as an item prefix, so the node column becomes 1. A continuation at indent 1 (` c: d`) is then read as a new structure line (`ind 1 > 1` is False). `_node` sees key `c` with value `d` and no error. That is fail-open, the same shape as v6 (`name: x` / `  foo: bar` → VALUE(3)) one column over. Indent 2 does not show it (2 > 1 still makes it a continuation), so the fixture must use exactly one space. PyYAML's verdict on this shape is not measured. I expect "mapping values are not allowed here", as for v6, but I2 probes it and 05 must not claim it without the probe output. VALUE(3) is fail-closed either way, and it follows 03 D1.
3. Not pinned, by decision: a tab before `#` (`description: a\t# see: b`, 06 i3d). The pure-Python loader raises and libyaml loads it, so there is no single YAML answer to pin. The test passes the line. A mutant `COMMENT_CUT_RE = r"[ ]#"` would turn that pass into VALUE(2), which is fail-closed. This is the tab-before-`#` family the 096 docstring already lists. No fixture and no docstring change.
4. Real-tree count for the round 2 shapes (I1 Grep, 2026-11-25, over .claude/agents, 7 files): the pattern `^(name|description|tools):.*([^ \t]#|[|>])|^-[^ -]` (a `#` after a non-space or a `|`/`>` in a real value, or a column-0 `-` key other than `---`) → 0 hits. The first try without `-` in the last class counted the 14 `---` marker lines (2 per file), so the class excludes them.

### R2 files to change
Still 1 file: tests/test_agent_tools.py. Add these 4 entries to CASES after v22, with ids as given. No other line changes.

| id | text | expected |
|---|---|---|
| v23_hash_in_word_colon | `_fm("name: a#b: c", TOOLS)` | `None, VALUE.format(2)` |
| v24_gt_inside_value | `_fm("description: a > b", TOOLS)` | `{"Read", "Write"}, None` |
| v25_bar_inside_value | `_fm("description: a \| b", TOOLS)` (plain `|` in code; the `\|` is a table escape, see Extra research 4) | `{"Read", "Write"}, None` |
| v26_dash_key_continuation | `_fm("-a: b", " c: d", TOOLS)` (exactly one space before `c`) | `None, VALUE.format(3)` |

### R2 traces (by hand, round 1 code at fcf3cff)
- v23, line 2 `name: a#b: c`. DOC no, no lead tab. VALUE_START_RE: key `name`, c = `a` (not special). Column 0: KEY_RE matches `name:` → no NO_KEY. prev None → `_node`: ITEMS end 0, not open, KEY `name:`, rest ` a#b: c` not open, t = `a#b: c`, `t[0]` = `a`. `_plain_colon`: COMMENT_CUT_RE `[ \t]#` finds nothing (the `#` follows `a`), COLON_RE finds `: ` → VALUE(2). Under X2, the cut at index 1 leaves `a`, there is no colon, `_field` → {Read, Write}, so the test fails. Under M57 (no cut) the result is still VALUE(2), so M57 is unchanged.
- v24 `description: a > b` / v25 `description: a | b`. `_node`: t = `a > b` / `a | b`, `t[0]` = `a`, which is not in `"|>"`. `_plain_colon` finds no colon → no error → {Read, Write}. Under X3, `">" in t` / `"|" in t` is true and BLOCK_RE.fullmatch fails → BLOCK(2), so the test fails.
- v26, line 2 `-a: b`. VALUE_START_RE: `(?:-[ \t]+)*` takes nothing (no space after `-`). Key group first char `-` is allowed → key `-a`, c = `b`. Column 0: `_is_item` False (not `-` or `- `), KEY_RE matches (first `-(?=\S)`, body `a`, `:` then a space) → no NO_KEY. `_node`: ITEMS_RE (round 1) end 0, col 0, KEY `-a:`, t = `b`, no colon → prev = (0, False). `prev_open` False. Line 3 ` c: d`: lead is one space. VALUE_START_RE c = `d`. The column-0 check is skipped (starts with a space). block None. prev (0, False) is closed and ind 1 > 0 → continuation → `_plain_colon("c: d")` → VALUE(3). Under X4, line 2 has ITEMS end 1, so col = 1 and prev = (1, False). Line 3: ind 1 > 1 is False → `_node(" c: d")` → key `c`, t = `d` → no error. TOOLS → {Read, Write}, so the test fails.
- Existing fixtures: no change to code, so all 132 round 1 results stand (06 ran them: 132 passed).

### R2 tests and checks
1. `python3 -m pytest tests/test_agent_tools.py -q` → 136 passed (132 + 4).
2. Base check (pre-104 `_frontmatter_error`, scratch copy) → 15 failed, 121 passed: the round 1 13, plus v23 (old parser has no value check → tool set) and v26 (no continuation check → tool set). v24 and v25 pass on the old parser.
3. New mutants, each alone on a scratch worktree (RI-009; no stash). The failing ids must equal the list, or 05 states a Deviation with the run output:
   - X2 `COMMENT_CUT_RE = re.compile(r"#")` → v23
   - X3 `if t[0] in "|>":` → `if "|" in t or ">" in t:` → v24, v25
   - X4 `ITEMS_RE = re.compile(r"(?:-[ \t]*)*")` → v26
4. Updated round 1 lists (traced; all others unchanged):
   - M56 (`_plain_colon` → False) → its 6 plus v23, v26 = 8 failed.
   - M58 (no continuation branch) → v6, v26 (line 3 goes to `_node`: key `c`, value `d` → pass).
   - M57, M59-M68: unchanged. v23-v26 have no ` #` comment, so M57 is unchanged. Their keys are at most 11 characters (M59/M60/M68), there is no `# c` value (M61) and no block header (M62/M65/M66/M67). M63 is unchanged because their TOOLS line is the plain `tools: Read, Write`. M64 is unchanged because v26's node column is 0 either way: line indent 0 equals ITEMS end 0. Since M64 leaves v26 alone while X4 kills it, the two mutants stay distinguishable.
   - M41-M55 (096): re-run; any v23-v26 ids they also fail are recorded and are not a Deviation.
5. PyYAML probe (information only, D6), added to the 05 table: v23-v26 on SafeLoader and CSafeLoader with the version printed. 06 already has v23-v25 as i3a-i3c. v26 is new (R2 research 2).
6. Real tree passes (21 of 21). `python3.11 -m py_compile tests/test_agent_tools.py` where available (RI-008). Full suite `python3 -m pytest -q`: round 1 result plus 4 passed; paste the line as printed (RI-006).

### R2 rule trace
| Rule (source) | Plan line, or DROPPED: <reason> |
|---|---|
| 06 send-back 1(a): `name: a#b: c` → VALUE(2), killed by `COMMENT_CUT_RE = r"#"` | v23; X2 |
| 06 send-back 1(b): `description: a > b` / `a \| b` → {Read, Write}, killed by "header test anywhere" | v24, v25; X3 |
| 06 send-back 1, X4 decision (pin or docstring line) | Pinned: v26; X4 (R2 research 2). No docstring line needed |
| 06 send-back 2 (I2): counts 132 + new, BASE change | R2 Tests 1-2: 136 passed; BASE 15 failed, 121 passed |
| Filter count: real frontmatter lines with the round 2 shapes (I1 Grep 2026-11-25, pattern in R2 research 4) | 0 hits in 7 files; the real-tree test still pins 21 of 21 |
| Fixture count per pinned rule (non-zero, dated 2026-11-25 by hand trace) | comment cut: 1 positive (v4) + 1 in-text negative (v23); header first char: 3 headers (v9, v10, v11) + 2 in-text negatives (v24, v25); item prefix: 1 (v26) |
| Optional input: PyYAML verdict on v26 | Probed by I2 as information; not claimed (R2 research 2) |
| Tab before `#` (06 i3d) | DROPPED: loaders disagree; already in the docstring's not-checked list (R2 research 3) |
| Rule text the person follows | none changed (test-only) |

### R2 guardrail tests
- In-text negative, comment cut: `#` inside a word is value text → v23, pinned by X2. The positive v4 is still pinned by M57.
- In-text negative, block header: `>`/`|` after the first character is plain text → v24, v25, pinned by X3. Headers are still pinned by M62/M66/M67.
- Item prefix needs a space: a `-a` key keeps node column 0 → v26, pinned by X4. M64 is distinct from X4.
- Missing inputs: no new optional input. v26's line 2 is the first line (prev None) and is read as a structure line, not as a continuation, as in v1/v13.

### R2 expected result
tests/test_agent_tools.py: 136 passed. Base 15 failed, 121 passed. X2 fails v23 only, X3 fails v24 and v25, X4 fails v26. M56 fails 8, M58 fails v6 and v26, and the other M57-M68 lists are as in round 1. The real tree passes. No parser or docstring line changes.

Self-check (round 2): 132 + 4 = 136. Base 13 + 2 = 15, and 136 − 15 = 121. M56 6 + 2 = 8. Each of X2, X3 and X4 kills a non-empty set that is distinct from every M56-M68 list ({v23}, {v24, v25}, {v26}).

Recurring issues checked (round 2, logs/recurring-issues.md read first): RI-001 (ESCALATED): the new shapes have a dated real count (0 hits, Grep 2026-11-25) and a pinning test each; the 21 of 21 real-tree count is unchanged. RI-010 (ESCALATED): I typed no log line; this file ends with the Log fields line. RI-014 (OPEN): not applicable (no git or clone-depth path). GUARDED entries checked: RI-002 (X2 and X4 were fail-open; v23 and v26 now pin them), RI-004/005 (counts re-derived in the Self-check), RI-006 (I2 pastes pytest lines as printed), RI-007 (FULL, round goes back through I2/I3), RI-008 (no new syntax; fixtures only), RI-009 (mutants on a scratch worktree, no stash), RI-012 (this round's finding: in-text negatives v23, v24, v25 added, each with a named mutant). RI-003, RI-011 and RI-013 do not apply.

Sources (round 2): https://docs.rs/crate/rlsp-yaml-parser/0.6.1/source/src/lexer/plain.rs ; https://yaml.org/spec/1.2.2/

Log fields: FIT | 1 files planned
