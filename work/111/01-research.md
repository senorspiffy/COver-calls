# 01 Research brief - 111

Type BUG, Scope FULL, opened by A1, 2026-11-26. Branch daily-fixes/2026-11-26 (built on PR #39, daily-fixes/2026-11-25), read only. R1 has no shell: it ran no test, regex, PyYAML call or git command. Repo facts are cited as path:line from reading files. Anything R1 worked out by hand is labelled "R1 trace (not run)". A PyYAML verdict is "measured" only where an earlier 05/06 or A1 audit pasted the result for that exact shape. Every other verdict is a prediction for I2/I3 to probe, as information only (PyYAML is not a declared dependency, work/104/01-research.md L3).

Recurring issues read first (logs/recurring-issues.md):
- RI-002 is this item's root cause: a file YAML cannot read must give a named error, never a tool set. Near miss, not counted (L25: "scalar item + key at its content column, D3/er1 still return a tool set (existed before 106) → 111").
- RI-001: each new rule gets a count on the real tree (Numbers).
- RI-012: the new rules classify lines by shape, so each one needs a negative fixture that looks like the bad shape but is valid YAML.
- RI-008: no 3.11+ syntax is proposed.
- RI-015: mutants run with the bytecode guard (I2/I3 duty).
- RI-010: the orchestrator writes the log line.
- RI-003, 009, 011, 013 and 014 do not apply: there is no calendar, branch, merge-base, realtest or clone path.

## Question
A1's audit of 106 (logs/audit/2026-11-26-106.md L78-L83) found three things:
- F-1: `hooks:` / `- a` / `  b: c` / `tools: Read` and `hooks:` / `  - a` / `    b: c` / `tools: Read` return ({Read}, None). SafeLoader and CSafeLoader both raise ScannerError. The shape is not in the docstring's "Not checked" list.
- F-2: D3 (`  a: v` / `  - x`) and er1 (`  - x` / `  a: v`) are documented as "Not checked", but they return a tool set while both loaders raise.
- F-3: the docstring version list should read "6.0.1, 6.0.3 and 6.0.4".

For each shape: what rule gives a named error (or a documented pass that matches YAML)? The rule must keep the 7 real agent files passing, and each new check needs a fixture that a named mutant kills.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### The code as it stands (repo, read only)
F1. Continuation test (tests/test_agent_tools.py L335-L338): `ind = lead spaces`. If `prev` is closed and `ind > prev[0]`, the line is a continuation and gets only `_plain_colon` (VALUE, unless `in_flow`). Otherwise it is a structure line (L340-L354).
F2. `prev = (col, op)` (L352). `col` is `_node`'s node column: lead spaces plus the whole `- ` prefix (L255-L258, `ITEMS_RE` L101). So for a scalar item, `prev[0]` is the column of the scalar's first character, not the dash column.
F3. R1 trace (not run), F-1 form 1. `hooks:` gives stack [0], prev (0, open). `- a` is col 0, so 096's check passes it because prev_open is True (L317-L320). It is a structure line: `_node` returns col 2, closed, and the stack becomes [0, 2] (L351). `  b: c` has ind 2, which is not > 2, so it is a structure line. `_node` reads key `b`, value `c`, and finds no colon, so there is no error. The stack lands on 2 (L349-L351), and nothing errors. `_field("tools")` then reads `tools: Read` → ({Read}, None). This matches A1's measured result (logs/audit/2026-11-26-106.md L79-L80).
F4. R1 trace (not run), F-1 form 2. `  - a` is ind 2, dash 2, col 4, and the stack is [0, 2, 4]. `    b: c` has ind 4, which is not > 4, so it lands on 4 → pass. The same gap.
F5. R1 trace (not run): with `- a` / ` b: c` (ind 1, between the dash and the content column), the stack pops 2, and top 0 ≠ 1 → INDENT. That already fails closed. The hole is exactly ind == content column after a scalar item.
F6. The structure branch tracks only levels (a sorted list of ints, L343-L351), not what kind of node opened each level. A key landing on a level opened by an indented `- ` (er1) and a `- ` landing on a level opened by a scalar-valued key (D3) both pass. R1 trace (not run). The column-0 analogue of D3 is already refused by item 096's prev_open rule (nk3, L573: `name: x` / `- a` → NO_KEY(3)). There is no indented equivalent.
F7. Measured: er1 `hooks:` / `  - x` / `  a: v` gives {Read, Write} on the build. SafeLoader raises ParserError "expected <block end>, but found '?'" and CSafeLoader raises ParserError "did not find expected '-' indicator" (work/106/05-build-report.md L158, L244). er1_tools (`tools:` / `  - Read` / `  Bash: x`) fails closed in `_field` with the 075 text (L159, L245).
F8. Measured by A1: D3 and er1 "both pass with a tool set, and both loaders raise (ParserError/ParserError, d1/d2)" (logs/audit/2026-11-26-106.md L70). The raw output is in A1's scratch probe-out.txt and is not in the repo. R1 cannot re-read it.
F9. The docstring (L69-L86) lists both shapes under "Not checked" (L83-L86). It says "measured on PyYAML 6.0.1 and 6.0.4" (L73). 6.0.1 (pure) and 6.0.3 (libyaml) were measured in 106/05 (L211), and 6.0.4 in work/104/06-verification.md (logs/audit/2026-11-26-106.md L73-L75). So F-3's "6.0.1, 6.0.3 and 6.0.4" is exact.
F10. Real tree (R1 Grep, 2026-11-26, `^(---|[ \t-])` over .claude/agents/*.md): 7 files. In each file `---` is on L1 and L5, and no frontmatter line (L2-L4) starts with a space, a tab or `-`. Every indented hit is at L11 or later, in the body. So 0 of 21 real frontmatter lines are items or indented, and none of the rules below can select a real line.

### YAML: what the spec says (primary)
F11. YAML 1.2.2 §6.1: "Each node must be indented further than its parent node." "All sibling nodes must use the exact same indentation level." [https://yaml.org/spec/1.2.2/] (re-read 2026-11-26).
F12. YAML spec, "Node Styles": "Normally, block sequences and mappings begin on the next line. In some cases, YAML also allows nested block collections to start in-line for a more compact notation." [https://yaml.org/spec/1.2-old/spec.html] (1.2.0, §3.2.3.1). The 1.2.2 review text has the same sentences [https://spec.yaml.io/main/review/markdown.html]. Only a collection that starts on the dash line (a compact mapping `- a: b` or sequence `- - a`) puts sibling nodes at the content column. A plain scalar `a` starts no collection.
F13. The §8.2.1 block sequence productions (l+block-sequence, c-l-block-seq-entry, s-l+block-indented, seq-spaces, compact sequence/mapping) and the §7.3.3 plain scalar productions (ns-plain-char, multi-line plain): UNVERIFIED from the spec. Each fetch of yaml.org/spec/1.2.2, yaml.org/spec/1.2-old and spec.yaml.io ended in §5.7-§6.6, so R1 did not read Chapters 7-8. The loader source below is the primary evidence for how the shapes are read.

### PyYAML: how the pure loader reads these shapes (primary, official library source)
F14. `scan_plain` sets `indent = self.indent+1` and ends a multi-line plain scalar `if not spaces or self.peek() == '#' or (not self.flow_level and self.column < indent)`. A plain scalar also stops at `ch == ':' and self.peek(length+1) in '\0 \t\r\n\x85  '` [https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/scanner.py]. So in block context, a later line at column ≥ (current collection indent + 1) continues the scalar.
F15. `add_indent(column)` raises the indent only `if self.indent < column`. `fetch_block_entry` opens a BLOCK-SEQUENCE-START only `if self.add_indent(self.column)` [https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/scanner.py]. So a sequence at a column deeper than its parent sets `indent` to the dash column. A sequence at its parent key's column (`hooks:` / `- a`) leaves `indent` at the key's column and is parsed as an indentless sequence.
F16. `fetch_value` in block context raises `"mapping values are not allowed here"` when no simple key is possible. A simple key whose line differs from the current line is dropped (`if key.line != self.line ...`), and if it was `required` it raises "could not find expected ':'". `required = not self.flow_level and self.indent == self.column` [https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/scanner.py].
F17. R1 reading of F14-F16 (not run), F-1 form 1. The sequence is indentless, so `indent` = 0 and the scalar's continuation threshold is column ≥ 1. `  b: c` (column 2) continues the scalar `a`. The `: ` comes after a line break inside that scalar, so the simple key saved on line 3 cannot cover it, and the error is "mapping values are not allowed here" (ScannerError). Form 2: `indent` = 2, the threshold is ≥ 3, and `    b: c` (column 4) continues → the same ScannerError. This matches the measured ScannerError in both loaders (logs/audit/2026-11-26-106.md L80; request.md L9). In YAML's reading the line is a continuation of the scalar, not a sibling key. So the parser's threshold for a scalar item should be the dash column, not the content column.
F18. R1 reading (not run): the same rule makes `hooks:` / `- a` / `  b` (no colon) the plain scalar `a b`, which loads. Prediction, I2 probe.
F19. `parse_block_sequence_entry` accepts only BLOCK-ENTRY or BLOCK-END. For any other token it raises ParserError "while parsing a block collection" / "expected <block end>, but found %r". `parse_block_mapping_key` accepts KEY, VALUE or BLOCK-END, otherwise it raises "while parsing a block mapping". `parse_indentless_sequence_entry` ends the sequence without an error on KEY/VALUE/BLOCK-END. The grammar: `indentless_sequence ::= (BLOCK-ENTRY block_node?)+` [https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/parser.py].
F20. R1 reading of F15/F19 (not run), er1. The sequence at column 2 has `indent` 2. `  a: v` at column 2: `add_indent(2)` is False, so no BLOCK-MAPPING-START is emitted. A KEY token ('?') arrives inside the block sequence → "expected <block end>, but found '?'". That is exactly the measured text (F7). At column 0 (`hooks:` / `- x` / `a: v`) the sequence is indentless and ends on KEY without an error (F19), so the key belongs to the parent mapping. That form is valid, which is why v18, v19 and nk6 pass in PyYAML (work/104/05-build-report.md L101-L102).
F21. R1 reading (not run), D3. `  a: v` opens a mapping at `indent` 2. `  - x` at column 2: `add_indent(2)` is False, so no sequence start is emitted. A BLOCK-ENTRY arrives in a block mapping, after a value, where KEY/VALUE/BLOCK-END is expected → ParserError. That matches A1's "ParserError" (F8). After an empty-valued key (`  a:` / `  - x`, s6) the entry becomes the value as an indentless sequence, which loads (measured, 106/05 L236).
F22. PyYAML docs: CLoader/CSafeLoader are "versions of the above classes written in C using the LibYAML library", "available only if you build LibYAML bindings". There are "some subtle (but not really significant) differences between pure Python and LibYAML based parsers" [https://pyyaml.org/wiki/PyYAMLDocumentation]. For the shapes in this item, both loaders raise (F7, F8, F17). Each probe should still record both loaders (the request's guardrail).

## Numbers used (show the math)
- File today: 165 tests in tests/test_agent_tools.py (106/05 L100; A1 re-run L37). Full suite: 1069 passed, 1 skipped (A1 L38). The last mutant name is M81 (106/05 L185), so new mutants start at M82.
- Real tree: 7 files × 3 frontmatter lines = 21 lines, and 0 of them are indented or items (F10). Every rule below selects 0 of 21. RI-001 feasibility: there is no cost on the real tree, and each rule fails the fixtures named below.

### Proposal R-A (F-1): continuation threshold for a scalar item is the last dash column
- Rule: when a structure line's node is a closed, non-block scalar after a `- ` prefix (no key follows the dashes: a plain, quoted or flow value), store `prev = (last dash column, False)` instead of `(col, False)`. A later line with `ind >` that column is a continuation, and the existing 104 check gives VALUE when it holds `: ` (or `_field` handles it, inside `in_flow`). Basis: F14-F17. This is YAML's own reading, and VALUE is the error the test already gives for the same ScannerError shape on a key (v6, c4; c4 measured ScannerError "mapping values are not allowed here", 106/05 L241).
- Block headers (`- |`) keep `block = col` unchanged (out of scope; see OQ4).
- Traces (R1, not run):
  - g1 `_fm("hooks:", "- a", "  b: c", "tools: Read")`: line 4, ind 2 > dash 0 → continuation, `in_flow` False (cleared by `hooks:`, L333-L334), `_plain_colon("b: c")` → VALUE(4).
  - g2 `_fm("hooks:", "  - a", "    b: c", "tools: Read")`: 4 > 2 → VALUE(4).
  - g3 (RI-012 negative) `_fm("hooks:", "- a", "  b", TOOLS)` → continuation with no colon → {Read, Write} (PyYAML predicted to load `['a b']`, F18, UNVERIFIED).
  - g4 `_fm("hooks:", '- "a"', "  b: c", TOOLS)` → VALUE(4) (quoted scalar item. YAML is predicted to raise, UNVERIFIED).
- Unchanged fixtures (R1 trace, not run):
  - s7 `  - - a` / `    - b`: last dash 4, and 4 is not > 4, so the line is a structure line and lands on dash level 4 → pass.
  - y4 `  - Read` / `    Bash`: now a continuation under `in_flow` → `_field` 075 text, the same as today.
  - f1, c2, c5: already continuations.
  - d, nk6, v19, i2, q23: siblings at the dash column, or nothing follows.
  - Key items (`- a: b`, s3, s4, p13, q23) are not scalar items, so their `prev` is unchanged.
- Mutant M82: R-A removed (prev uses `col` again) → g1, g2 and g4 fail (they return a tool set).

### Proposal R-B / R-C (F-2): remember which kind of node opened each level
- State: next to `stack`, a mapping `kind[level]` set when a level is pushed: `seq` for a level opened by a `- ` (the line's own indent if the line is an item, plus every further dash column), and `map` for a level opened by a key (the line's indent, or the column after the dashes for a key item). For an open item (`- ` with nothing after it), the content column is left undecided, so the next line there decides it. Also `last_open[level]`: True after an empty-valued key or an item at that level, False after a scalar-valued key. Popped levels are deleted. A new level is always assigned, never `setdefault`.
- R-B (er1): a key line that lands on an existing level whose kind is `seq` → named error. Text is R3's call, e.g. `"key at a list's dash column on frontmatter line {} (item 111)"`. Basis F19/F20.
- R-C (D3): a `- ` line that lands on an existing `map` level whose `last_open` is False → named error. R3's call: a new text such as `"list item after a scalar-valued key on frontmatter line {} (item 111)"`, or NO_KEY, since 096 gives NO_KEY for the column-0 form (nk3). Basis F21.
- Run both after the existing INDENT check (L347-L348), so s1, s2, s4 and s5 keep INDENT.
- Traces (R1, not run):
  - er1 `_fm("hooks:", "  - x", "  a: v", TOOLS)`: level 2 is `seq` → R-B(4). PyYAML raises in both loaders (measured, F7).
  - D3 `_fm("hooks:", "  a: v", "  - x", TOOLS)`: level 2 is `map`, last_open False → R-C(4). Both loaders raise (measured by A1, F8).
  - k1 `_fm("hooks:", "  - - a", "  b: c", TOOLS)`: level 2 is `seq` → R-B(4). Today it passes (the stack lands on 2). PyYAML is predicted to raise, ParserError "expected <block end>, but found '?'" (F14/F19 reading, UNVERIFIED).
  - k2 `_fm("hooks:", "  a:", "  - x", "  b: v", "  - y", TOOLS)` → R-C(6), because `b: v` reset last_open. Predicted to raise (F21, UNVERIFIED).
  - Negatives (RI-012), expected {Read, Write}:
    - s6 (measured: loads).
    - k3 `_fm("hooks:", "  a:", "  - x", "  - y", TOOLS)` (predicted to load).
    - k4 `_fm("hooks:", "  - x", "name: y", "  a: b", TOOLS)`: level 2 is popped by `name:` and reopened as `map` (predicted to load).
    - k5 `_fm("hooks:", "- x", "a: v", TOOLS)`: column 0, an indentless sequence, valid (F20; predicted to load).
- Unchanged (R1 trace, not run):
  - p13: 0 map, 2 map, 4 seq/6 map, 6 key, 8 seq/10 map, 10 key → pass.
  - q23: 2 seq, 4 map, 6 map, `  - github` lands on 2 seq → pass.
  - s3: `    c: d` lands on 4 map, `  - e: f` lands on 2 seq → pass.
  - s7: `    - b` lands on 4 seq → pass.
  - d, y2, y7: items on a seq level.
  - v18, v19, nk6, nk7, nk12: column 0, map level with last_open True, and 096 runs first.
  - nk8: NO_KEY first.
- `tools:`/`disallowedTools:` fields: er1_tools (`tools:` / `  - Read` / `  Bash: x`) would hit R-B before `_field` and change from the 075 text to the R-B text. Both fail closed. R1 recommends skipping R-B/R-C while `in_flow` is set, as 106 did for continuations (L337), so er1_tools keeps its measured 075 text (see OQ2).
- Mutants:
  - M83: R-B removed → er1 and k1 fail.
  - M84: R-C removed → D3 and k2 fail.
  - M85: `last_open` not reset by a scalar-valued key → k2 fails.
  - M86: an item does not set `last_open` → k3 fails.
  - M87: `kind` kept for popped levels, or `setdefault` → k4 fails.
  - M88: R-B also applied at a level that is both a key level and an indentless-sequence level → k5 and v19 fail.
- Projection: 165 + g1-g4 (4) + er1, D3, k1-k5 (7) = 176 tests in the file, with no existing expectation changed (if OQ2 is "skip under `in_flow`"). This is a projection, not a run. BASE (today's parser with the new fixtures) is predicted to fail g1, g2, g4, er1, D3, k1 and k2 = 7. R1 trace only; I2 runs it.

### Docstring (F-3 and the "Not checked" list)
- In the Item 106 paragraph, change "measured on PyYAML 6.0.1 and 6.0.4" (L73) to "6.0.1, 6.0.3 and 6.0.4" (F9).
- Remove the two D3/er1 sentences from "Not checked" (L83-L86).
- Add an "Item 111:" paragraph. It covers R-A (a line indented past a scalar item's dash is a continuation of that scalar), R-B, R-C and their known false errors (none predicted, see OQ3), and keeps "This says nothing about what Claude Code does with such a file."

## Fit for a ~$3k account
This is a test-only item, in tests/test_agent_tools.py. It changes no strategy rule, order, premium, dividend, tax or liquidity input, so the $3k limits (100 shares under ~$30, assignment, commissions, spreads) do not apply. It makes the agent-tools drift test fail with a named error on frontmatter shapes that both PyYAML loaders reject, so no tool set is read from a file YAML cannot load (RI-002). It makes no claim about which parser Claude Code uses (work/106/01-research.md F19). Nothing connects to a broker. This is research, not financial advice.

## Open questions
1. R-A versus a separate named error for F-1. R-A gives VALUE, which matches YAML's reading (F17) and lets the valid `- a` / `  b` pass (g3). The alternative is a new error for any structure line at a scalar item's content column, which would also refuse g3 (a fail-closed false error). R1 recommends R-A.
2. Should R-B/R-C be skipped inside a `tools:`/`disallowedTools:` field (`in_flow`)? If yes, er1_tools keeps the measured 075 text and no existing expectation changes. If no, the message changes and an expectation must be added. Either way it fails closed.
3. False errors: R1 found no valid YAML that R-A, R-B or R-C refuses (F12, F19-F21), but this is a reading, not a run. I2 should probe g3, k3, k4, k5, s3, s6, s7, p13 and q23 in both loaders (pure 6.0.1 and libyaml 6.0.3/6.0.4), and add a "Known fail-closed false errors" line for any that loads but is refused.
4. Out of scope, noted: the block-scalar header in an item (`- |`) still uses `block = col`. YAML allows content at dash + 1 (UNVERIFIED, Chapter 8 not read, F13), so `- |` / ` x` may be a fail-closed false error today. Not a tool-set hole.
5. YAML 1.2.2 Chapters 7-8 could not be read through the fetch tool (F13). R3 may want to verify F12's reading against §8.2.1 another way, or accept the PyYAML source plus the measured raises as the evidence.
6. RI-002: a near miss, not counted (request L14). No GUARDED condition changes. The GUARDED probe is M82-M84 failing their named fixtures on main once merged.
