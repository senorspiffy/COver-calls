# 03 Research hand-off - 111
Status: READY

Type BUG, Scope FULL, so R3 writes no 07-audit-task.md. The code change goes through I1-I3. Branch daily-fixes/2026-11-26, read only. R3 has no shell: it ran no test, regex, PyYAML call or git command. Every "R3 trace" was done by hand against tests/test_agent_tools.py as it stands (165 tests: 150 CASES + 13 TREE + 2 named, A1 run `165 passed`, logs/audit/2026-11-26-106.md L37). I2 confirms each trace by running it. The only PyYAML verdicts used as facts are measured ones: 106/05 L211-L245 (6.0.1 pure, 6.0.3 pure and libyaml), A1's 106 audit (L70, L79-L80; 6.0.3, both loaders) and 104/05 L101-L102. Every other verdict on a new fixture is a prediction, and step 2 measures it before the parser is changed (rule D-P).

Scope (orchestrator: "R-A plus what's needed for D3/er1"). This guards 0 of 21 real frontmatter lines, so the map keeps three rules and cuts the rest:
- Kept: R-A (F-1, both indent forms), R-B (er1), R-C (D3), the docstring fix (F-3) and the minimum state those rules need. That is 8 new fixtures and 7 mutants.
- Cut, with the reason:
  - R2 FOR 2 (`no_cont` flag, g5, g6, M89). The shapes it targets go under "Not checked" instead (step 4).
  - R2 FOR 3's k6 and M90. `last_open` is taken from `_node`'s `op`, so a block header sets it False by construction.
  - R2 AGAINST 3b's third "undecided" state and k7. Not needed (row 75).
  - R1's k1, k3 and k5. Each rule they pin is already pinned by another fixture (rows 39, 41, 43).
  - R1 OQ2's `in_flow` skip for R-B/R-C (row 45).
  - The b1-b12 re-run (row 82).
  - Two holes found by R3 (Decisions D6), left as "Not checked" lines and not fixed here.

Recurring issues checked (logs/recurring-issues.md, read first). Open or ESCALATED: RI-001 (ESCALATED) and RI-014 (OPEN). Also checked: GUARDED RI-002, RI-004, RI-005, RI-006, RI-007, RI-008, RI-010, RI-012 and RI-015.
- RI-001: each rule is a line filter, and its pass count is computed in the Feasibility column. On the real tree it is 21 of 21 lines pass and 0 selected (R3 Grep, 2026-11-26). On the existing fixtures it is 165 of 165 unchanged (Self-check 1). Nothing is asserted as "always".
- RI-014: does not apply. No git or clone-depth path is involved.
- RI-002 (this item's root cause, near miss, not counted): F-1, D3 and er1 now give a named error, not a tool set. The shapes still passed are listed by name under "Not checked" (step 4), so no undocumented pass is left.
- RI-004/005: every fixture, line number and mutant kill list was re-traced against the rule's own code (Self-check).
- RI-006: the totals are left to check_handoff.
- RI-007: Scope FULL, and R3 writes no code.
- RI-008: no 3.11+ syntax (no walrus, no `match`).
- RI-010: the orchestrator writes the log line, and the check_handoff line is left as in the template.
- RI-012: each new rule has a valid-looking negative fixture:
  - R-A: g3.
  - R-B: s6, measured to load, and k4.
  - R-C: s6, plus nk6 and v19 (measured to load).
  - Each negative is pinned by a named mutant (M82-M88).
- RI-015: mutants run with the bytecode guard (step 5).
- RI-003, RI-009, RI-011 and RI-013 do not apply: there is no calendar, branch, merge-base or realtest path.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 1. R1 L3: PyYAML is not a declared dependency | work/104/01-research.md L3; work/106/03-handoff.md row 1 (pyproject.toml L10) | VERIFIED | - |
| 2. R1: RI-002 L25 names this near miss ("scalar item + key at its content column, D3/er1 still return a tool set (existed before 106) → 111"), not counted | logs/recurring-issues.md L25 | VERIFIED | - |
| 3. R1 Question: F-1, F-2, F-3 as A1 wrote them | logs/audit/2026-11-26-106.md L78-L83 | VERIFIED | - |
| 4. R1 F1: continuation test is `prev and not prev[1] and ind > prev[0]`; otherwise a structure line | tests/test_agent_tools.py L335-L340 | VERIFIED | - |
| 5. R1 F2: `prev = (col, op)` (L352); `col` = lead spaces + the whole `- ` prefix (L255-L258, ITEMS_RE L101) | tests L101, L255-L258, L352 | VERIFIED | - |
| 6. R1 F3: form 1 returns ({Read}, None) today | R3 trace: `  b: c` ind 2, prev (2, closed), 2 > 2 false, lands on level 2; A1 measured (audit L79-L80) | VERIFIED | - |
| 7. R1 F4: form 2 passes today (`    b: c` ind 4, prev (4, closed), lands on 4) | R3 trace; audit L79-L80 | VERIFIED | - |
| 8. R1 F5: `- a` / ` b: c` gives INDENT today | R3 trace: pops 2, 0 ≠ 1 | VERIFIED | Under R-A it becomes VALUE(4) (1 > 0, continuation with `: `). It is not a fixture, and both results fail closed |
| 9. R1 F6: the structure branch tracks levels only; nk3 gives NO_KEY(3) | tests L343-L351, L573 | VERIFIED | - |
| 10. R1 F7: er1 gives {Read, Write}; SafeLoader "expected <block end>, but found '?'", CSafeLoader "did not find expected '-' indicator"; er1_tools gives the 075 text | work/106/05-build-report.md L158, L159, L244, L245 | VERIFIED | - |
| 11. R1 F8: A1 measured D3 and er1: tool set, both loaders raise ParserError; raw output not in repo | audit L70 | VERIFIED | - |
| 12. R1 F9: docstring says "6.0.1 and 6.0.4" (L73); 6.0.1/6.0.3 measured in 106/05 L211, 6.0.4 in 104/06 L72/L167, so "6.0.1, 6.0.3 and 6.0.4" is exact | tests L73; 106/05 L211; 104/06 L72, L167; audit L73-L75 | VERIFIED | - |
| 13. R1 F10: 7 agent files, `---` on L1 and L5, no frontmatter line starts with a space, tab or `-` (0 of 21) | R3 Grep `^(---\|[ \t-])` over .claude/agents/*.md, 2026-11-26: frontmatter hits are only L1/L5 `---` in all 7 files; every other hit is L11 or later | VERIFIED | - |
| 14. R1 F11: "Each node must be indented further than its parent node." / "All sibling nodes must use the exact same indentation level." (§6.1) | https://yaml.org/spec/1.2.2/ (R3 fetch) | VERIFIED | - |
| 15. R1 F12: "Normally, block sequences and mappings begin on the next line. In some cases, YAML also allows nested block collections to start in-line for a more compact notation." | https://yaml.org/spec/1.2-old/spec.html §3.2.3.1; https://spec.yaml.io/main/review/markdown.html "Node Styles"; also in https://yaml.org/spec/1.2.2/ §3.2.3.1 (R3 fetches) | VERIFIED | R1's reading (a plain scalar opens no collection) is backed by rows 17-20 and the measured s3 load (106/05 L233) |
| 16. R1 F13: the §8.2.1 / §7.3.3 productions (UNVERIFIED by R1) | R3 fetch of yaml.org/spec/1.2.2 also ends at 97,515 characters, before Chapter 8 | UNSUPPORTED | Removed. Nothing in the map rests on it. The PyYAML source plus the measured raises are the evidence (R1 OQ5) |
| 17. R1 F14: `scan_plain` sets `indent = self.indent+1` and stops on `not spaces or self.peek() == '#' or (not self.flow_level and self.column < indent)`; a chunk ends at `ch == ':' and self.peek(length+1) in '\0 \t\r\n…'` | https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/scanner.py (three R3 fetches) | VERIFIED | - |
| 18. R1 F15: `add_indent` raises the indent only `if self.indent < column`; `fetch_block_entry` opens a sequence only `if self.add_indent(self.column)`; a sequence at its parent key's column is indentless | scanner.py (R3 fetch); parser.py grammar (row 22) | VERIFIED | - |
| 19. R1 F16: `fetch_value` raises "mapping values are not allowed here" "when no simple key is possible" | scanner.py (R3 fetch) | WRONG (part) | Corrected: it raises only when no simple key is saved and `allow_simple_key` is False (block context). `required = not self.flow_level and self.indent == self.column` and the `key.line != self.line` drop are as R1 says |
| 20. R1 F17: both F-1 forms raise ScannerError because the deeper line continues the plain scalar | R3 trace of scanner.py: `scan_plain_spaces` sets `allow_simple_key = True` at the line break, `scan_plain` sets it False again on reading the chunk `b`, so at `: ` the flag is False and no key is saved → ScannerError; matches A1's measurement (audit L80) and c1-c5 (106/05 L238-L242) | VERIFIED | - |
| 21. R1 F18: `hooks:` / `- a` / `  b` loads as `['a b']` | none (a prediction); runoob shows the shape as one string but is a tutorial, not a run | UNSUPPORTED | Removed as a PyYAML fact. g3's expectation rests on the test's own rule; step 2 measures it |
| 22. R1 F19: `parse_block_sequence_entry` accepts only BLOCK-ENTRY/BLOCK-END, otherwise "while parsing a block collection" / "expected <block end>, but found %r"; `parse_block_mapping_key` "accepts KEY, VALUE or BLOCK-END"; `parse_indentless_sequence_entry` ends without error "on KEY/VALUE/BLOCK-END" | https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/parser.py (two R3 fetches) | WRONG (part) | Corrected. `parse_block_mapping_key` accepts only KEY or BLOCK-END at its start; the KEY/VALUE/BLOCK-END list is checked after a KEY is taken, to decide an empty key. Any other token (VALUE, BLOCK-ENTRY) raises "while parsing a block mapping". The indentless sequence ends without error on any token that is not BLOCK-ENTRY; the KEY/VALUE/BLOCK-END list only decides an empty entry. The D3 and column-0 conclusions stand |
| 23. R1 F20: er1 raises "expected <block end>, but found '?'" (a required simple key at column 2, no new mapping start); the column-0 form is valid; "v18, v19 and nk6 pass in PyYAML (104/05 L101-L102)" | scanner.py `if self.add_indent(key.column):` (R3 fetch); 104/05 L101-L102 | WRONG (part) | Corrected: only v18 and v19 are measured there. R3 Grep of work/*/05-06 found no PyYAML verdict for nk6. v19 (the same column-0 shape) is enough |
| 24. R1 F21: D3 gives BLOCK-ENTRY inside a block mapping → ParserError; after an empty-valued key (s6) it loads | R3 trace of scanner/parser; audit L70; 106/05 L236 (s6 loads, all three loaders) | VERIFIED | - |
| 25. R1 F22: CLoader/CSafeLoader "are versions of the above classes written in C using the LibYAML library", "available only if you build LibYAML bindings", "subtle (but not really significant) differences" | https://pyyaml.org/wiki/PyYAMLDocumentation (R3 fetch) | VERIFIED | - |
| 26. R1 Numbers: 165 tests; full suite 1069 passed, 1 skipped; last mutant M81 | audit L37-L38; 106/05 L100, L185 | VERIFIED | - |
| 27. R1 Numbers: 21 real lines, every rule selects 0 | row 13; Self-check 2 | VERIFIED | - |
| 28. R1 R-A: a closed non-block scalar item stores `prev = (last dash column, False)`; VALUE matches the error the test gives for c4 (measured ScannerError) | rows 17-20; 106/05 L241 | VERIFIED | Wording: this is YAML's reading only for a plain value not ended by ` #` (row 73). For quoted, flow or comment-ended items it is a fail-closed rule |
| 29. R1 g1, g2 → VALUE(4) | R3 trace (Self-check 3, 4) | VERIFIED | - |
| 30. R1 g3 → {Read, Write} | R3 trace (Self-check 5) | VERIFIED | - |
| 31. R1 g4 → VALUE(4) | R3 trace (Self-check 6) | VERIFIED | - |
| 32. R1: s7, y4, f1, c2, c5, d, nk6, v19, i2, q23 and the key items keep their results under R-A | R3 trace (Self-check 1, 12) | VERIFIED | - |
| 33. R1 M82 (R-A removed) → g1, g2, g4 fail | R3 trace (Self-check 15) | VERIFIED | - |
| 34. R1 R-B/R-C state: an item line pushes "the line's own indent" as `seq`; an open item's content column is "left undecided"; popped levels are deleted; never `setdefault` | R3 trace | WRONG (part) | Corrected (with R2 AGAINST 3a). A level keeps the kind it got when it was opened. A landing line never changes it (s6, v19 pin this). An open item's content column gets kind None, so no undecided state is needed. Every newly opened level is assigned fresh, so popped levels need no deletion. `setdefault` stays forbidden (k4, M87) |
| 35. R1 R-B: a key line on a `seq` level is an error | parser.py (row 22: a block sequence takes only BLOCK-ENTRY/BLOCK-END) | WRONG (part) | Corrected and simplified: any structure line that is not a `- ` item and lands on a `seq` level is an error (a key, a plain or a quoted line alike). Text: SEQ_LEVEL (D2) |
| 36. R1 R-C: a `- ` line on a `map` level whose last line at that level was a key with a value is an error | rows 22, 24 | VERIFIED | Text: MAP_ITEM (D2); `last_open` = `op` from `_node` (row 68) |
| 37. R1: R-B/R-C run after the INDENT check, so s1, s2, s4, s5 keep INDENT | R3 trace (Self-check 1) | VERIFIED | - |
| 38. R1: er1 → R-B(4); D3 → R-C(4) | R3 trace (Self-check 7, 8) | VERIFIED | - |
| 39. R1 k1 `hooks:` / `  - - a` / `  b: c` → R-B(4) | R3 trace: level 2 is a dash level (seq) | VERIFIED | Fixture cut (scope). er1 pins R-B, and M83 kills it |
| 40. R1 k2 → R-C(6) | R3 trace (Self-check 9) | VERIFIED | - |
| 41. R1 k3 `  a:` / `  - x` / `  - y` → pass | R3 trace | VERIFIED | Fixture cut (scope). nk6 and v19 already have two items under an open key, so they pin M86 |
| 42. R1 k4 `_fm("hooks:", "  - x", "name: y", "  a: b", TOOLS)` → pass (level 2 reopened as map) | R3 trace | WRONG | Corrected. `name: y` is closed, so `  a: b` (2 > 0) is a continuation, which gives VALUE(5) and not a pass. New k4 `_fm("hooks:", "  - x", "name:", "  a: b", "  c: d", TOOLS)` → {Read, Write}. Its line 6 lands on the reopened level, so a stale kind would show (M87) |
| 43. R1 k5 `hooks:` / `- x` / `a: v` → pass | R3 trace | VERIFIED | Fixture cut (scope). v18, v19, nk7 and nk12 have a column-0 key after a column-0 item and pin the same thing (M88) |
| 44. R1: p13, q23, s3, s7, d, y2, y7, v18, v19, nk6, nk7, nk12 unchanged; nk8 NO_KEY first | R3 trace (Self-check 1, 13) | VERIFIED | - |
| 45. R1: er1_tools would hit R-B before `_field`; R1 recommends skipping R-B/R-C under `in_flow` | R3 trace; R3 Grep of CASES: er1_tools is not a fixture (it exists only in the 106/05 probe) | VERIFIED | Decision D3: no skip. er1_tools would give SEQ_LEVEL(4) instead of the 075 text. Both fail closed, and both loaders raise (106/05 L245). No existing case changes (Self-check 1) |
| 46. R1 M83-M88 kill lists (M86 "item does not set last_open → k3"; M87 needs k4; M88 → k5, v19) | R3 trace (Self-check 16-21) | WRONG (part) | Corrected. M83 → er1. M84 → D3, k2. M85 (landing does not update `last_open`) → k2, nk6. M86 (a landing item sets `last_open = op`) → nk6, v19. With no update at all, k3 would still pass. M87 (`setdefault`) → k4. M88 (a landed level takes the line's kind) → g3, k2, nk7, nk12, s6, v18, v19 |
| 47. R1 projection: 176 tests; BASE 7 failed | R3 count | WRONG | Corrected: 165 + 8 = 173. BASE fails g1, g2, g4, er1, D3, k2 (6) and passes 167 (Self-check 14) |
| 48. R1 docstring plan (version list, remove the D3/er1 "Not checked", add "Item 111:", keep the runtime disclaimer) | tests L69-L86 | VERIFIED | Text in step 4, with the "Not checked" lines that the cuts need |
| 49. R1 Fit: test-only; no strategy rule, order or $3k limit is affected | item scope | VERIFIED | - |
| 50. R1 OQ4: `- \|` / ` x` may be a fail-closed false error; YAML allows content at dash + 1 | none (R1: UNVERIFIED, Chapter 8 not read) | UNSUPPORTED | Removed. It is out of scope, and block headers keep `block = col` |
| 51. R1 OQ6: near miss, not counted; no GUARDED condition changes | logs/recurring-issues.md L25; request L14 | VERIFIED | - |
| 52. R1/R2 PyYAML predictions for the unmeasured new shapes (g4, k1-k7 raise/load; g5, g6 ParserError) | none (readings of scanner.py/parser.py) | UNSUPPORTED | Removed as facts. Step 2 measures g3, g4, k2 and k4 before the parser change. Rule D-P says what a differing verdict changes |
| 53. R2 L3: full language search applies (outside YAML/PyYAML facts go into the docstring) | .claude/agents/r2-improver.md L16 | VERIFIED | - |
| 54. R2: A1 L70-L71 (D3/er1), L78-L83 (F-1-F-3), L63-L66 (b1-b12, no false INDENT) | audit | VERIFIED | - |
| 55. R2: 6.0.4 by I3 of 104, 6.0.3 and 6.0.1 by 106 | audit L73-L75 | VERIFIED | - |
| 56. R2: 106/02 L40-L43 called the stack "the same state model that 104's R2 declined" | work/106/02-improvements.md L40-L41 | VERIFIED | - |
| 57. R2: seventh patch on `_frontmatter_error` (075, 080, 087, 096, 104, 106, 111) | work/106/02-improvements.md L14 (six listed) + this item | VERIFIED | - |
| 58. R2: in 106's container CSafeLoader was absent and PyYAML was 6.0.1 | work/106/02-improvements.md L46 | VERIFIED | 106/05 L211 found 6.0.3 with libyaml in the user site, so step 2 records what it finds |
| 59. R2: the last full-search cycle (2026-11-25) used German, Russian, Italian (107, 110) and Korean, Portuguese, Dutch (106); French, Turkish, Hindi picked | logs/research/2026-11-25.md L10, L14, L17; logs/research/2026-11-26.md L4, L9 | VERIFIED | 112 (L8, 23:25) also used French and Turkish this cycle. The rule looks at the last cycle, so this is not a conflict |
| 60. R2 FOR 1: the threshold is "ind > last dash column" for both indent forms | rows 17, 18 | VERIFIED | - |
| 61. R2 Mandarin: `- newline` / `  newline2` with "字符串可以拆成多行，每一行会被转化成一个空格" | https://www.runoob.com/w3cnote/yaml-intro.html (R3 fetch: `    - newline` / `      newline2`, the same shape at dash 4) | VERIFIED | Translation right ("A string can be split over several lines; each line break becomes a space.") |
| 62. R2 FOR 1: nothing else reads `prev[0]` | tests L336 (only read) | VERIFIED | - |
| 63. R2 Japanese: `  - pymdownx.highlight # コードシンタックス` / `      linenums: true` → "expected <block end>, but found '<block mapping start>'"; "原因 : `:`がないから" | https://qiita.com/ponsuke0531/items/7dd4f81e061722d82af8 (R3 fetch; an MkDocs error) | VERIFIED | Translation right ("Cause: because there is no `:`") |
| 64. R2 FOR 2: a comment or a closed quote ends a scalar item; `- a # c` / `  b` and `- "a"` / `  b` pass today and under R-A | scanner.py `self.peek() == '#'` (row 17); R3 trace | VERIFIED | Listed under "Not checked" (step 4). The PyYAML verdicts are in row 52 |
| 65. R2 FOR 2 proposal (`no_cont` flag, g5, g6, M89) | R3 design review | VERIFIED | Cut for scope (orchestrator). The shapes are documented instead |
| 66. R2 FOR 3: §6.1; Red Hat: "it attempts to start a mapping block at an adjacent level to a sequence block" | https://yaml.org/spec/1.2.2/; https://www.redhat.com/es/blog/yaml-beginners (R3 fetch: English article text, Spanish site chrome) | VERIFIED | - |
| 67. R2 Spanish: "Los elementos de secuencia (-) cuentan como un nivel de indentación" | https://abacktools.com/es/blog/how-to-detect-and-fix-yaml-errors (R3 fetch) | VERIFIED | Translation right |
| 68. R2 FOR 3: `  a: \|` / `    t` / `  - x` passes unless a block header sets `last_open` False; use `last_open = op` | R3 trace: `_node` returns `op` False for a header (L275), `    t` is skipped (L325-L326), `  - x` lands on 2 | VERIFIED | Adopted as the formula (step 3). k6 and M90 cut |
| 69. R2 FOR 3: real-tree cost 0 | row 13 | VERIFIED | - |
| 70. R2 AGAINST 1: "The Symfony Yaml Component implements a selected subset of features defined in the YAML 1.2 version specification." | https://symfony.com/doc/7.0/reference/formats/yaml.html (R3 fetch) | VERIFIED | - |
| 71. R2 French: "Les messages d'erreur YAML varient fortement selon le parseur." / "PyYAML et js-yaml utilisent silencieusement la dernière occurrence, tandis que yaml.v3 de Go signale une erreur." / "Les éléments de séquence (-) comptent comme un niveau d'indentation" | https://abacktools.com/fr/blog/how-to-detect-and-fix-yaml-errors (R3 fetch) | VERIFIED | Translations right |
| 72. R2 AGAINST 1: about 179 tests and 9 mutants; drop R-C first if cutting | R3 count | WRONG | Corrected: 173 tests and 7 mutants. R-C is kept because D3 is in the request (F-2). The cuts are listed at the top |
| 73. R2 AGAINST 2: R-A's "continuation" reason is false for quoted, flow and comment-ended items; the docstring must say so | rows 17, 63 | VERIFIED | Adopted in the "Item 111:" text (step 4) |
| 74. R2 AGAINST 3a: a column-0 item must not turn level 0 into `seq`; "first opener keeps the kind until popped" | R3 trace (Self-check 21) | VERIFIED | Adopted (row 34) |
| 75. R2 AGAINST 3b: an open item needs a third state, and k7 is needed | R3 trace of k7 `  -` / `    a: b` / `    c: d`: `  -` opens 2 (seq) and 3 (None); `    a: b` opens 4 (map); `    c: d` lands on 4 → pass | WRONG (part) | Corrected: no third state is needed, so k7 is cut |
| 76. R2 AGAINST 3c: the measured pairs are only er1 (106/05) and D3, F-1 (A1) | 106/05 L244; audit L70, L80 | VERIFIED | - |
| 77. R2 English: "An array/list item is expected here. Any other entity is not allowed." | https://docs.apimatic.io/rulesets/yaml-semantic-validation/valid-block-sequence-item (R3 fetch) | VERIFIED | - |
| 78. R2 Mandarin: "同一层级的元素必须保持相同的缩进量"; the Discourse ?tl=zh page is a translated view of an English thread | runoob (R3 fetch: the clause is followed by "，通常建议使用 2 个空格作为缩进单位"); https://meta.discourse.org/t/did-not-find-expected-indicator-in-app-yml/83800?tl=zh (R3 fetch) | VERIFIED | Translation right |
| 79. R2 Spanish: "Una clave movida a un nivel de indentación distinto cambia su bloque padre." / "significa que un : apareció en un contexto donde el parser no estaba en un bloque de mapeo" | abacktools /es (R3 fetch) | VERIFIED | Translations right |
| 80. R2 Turkish: "Boşluk girintisi, yuvalamayı ve genel yapıyı belirtmek için kullanılır." / "Hiyerarşi çift boşluk karakterleri kullanılarak gösterilir." | https://www.aspose.info/tr/programming/yaml (R3 fetch) | VERIFIED | Translations right |
| 81. R2 Hindi: "हाइफ़न (-) का उपयोग प्रत्येक सदस्य के साथ एक अलग पंक्ति में सूची सदस्यों को इंगित करने के लिए किया जाता है।" / "पदानुक्रम को डबल स्पेस वर्णों का उपयोग करके दर्शाया जाता है। टैब वर्णों की अनुमति नहीं है" | https://www.aspose.info/hi/programming/yaml (R3 fetch) | VERIFIED | Translations right |
| 82. R2 Holes 5: re-run A1's b1-b12 plus the named existing cases | audit L63-L66 (b1-b12 live in A1's scratch, not in the repo) | WRONG (part) | Corrected: the required regression set is the 165 existing tests (Self-check 1). b1-b12 are optional for I3/A1 |
| 83. R2 Holes 7: record `yaml.__version__` and `yaml.__with_libyaml__`; "not measured" where CSafeLoader is absent; `n` is the test's own count | work/106/02-improvements.md L46-L47 | VERIFIED | Step 2 |
| 84. R2 Holes 8: remove the D3/er1 "Not checked" sentences only if R-B and R-C both land | tests L82-L86 | VERIFIED | Both land, so both sentences go |

**Totals:** 84 rows checked → **69 VERIFIED as-is**, **11 fixed**, **4 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

Rows counted as fixed (11): 19, 22, 23, 34, 35, 42, 46, 47, 72, 75, 82. Rows counted as removed (4): 16, 21, 50, 52. The other 69 rows are VERIFIED as-is. Where one of them has a Fix-cell note, the note adds context or records a scope cut and changes no claim.

## Removed claims
1. Row 16: the YAML 1.2.2 Chapter 7-8 productions. Not read by R1 or R3.
2. Row 21: g3 loads as `['a b']`. Not measured.
3. Row 50: `- |` / ` x` is a fail-closed false error. Not measured, and out of scope.
4. Row 52: every unmeasured PyYAML verdict on a new shape (g3, g4, k1-k7, g5, g6). Not measured.

None of these may appear in 04/05/06 as a YAML fact. Each may appear only next to a step 2 probe output, as information.

## Decisions
- D1 (R1 OQ1): R-A, applied to every closed scalar item (plain, quoted or flow; no key; not open; not a block header), because a quoted or flow item followed by a deeper `: ` line should also fail closed (g4). It is described as YAML's reading only for a plain value not ended by ` #` (row 73).
- D2, the error texts. `n` is the test's own count (`i + 2`), never PyYAML's mark.
  - `SEQ_LEVEL = "non-item line at a list's dash column on frontmatter line {} (item 111)"`
  - `MAP_ITEM = "list item at the indent of a key with a value on frontmatter line {} (item 111)"`
  - R-A reuses VALUE.
- D3 (R1 OQ2): R-B and R-C are not skipped under `in_flow` (row 45). This is one branch fewer and changes no expectation.
- D4, level state:
  - `kind[lv]` is set only when a level is opened. A dash column gets `"seq"`. The line's node column gets `"map"` if a key follows the dashes there, and `None` otherwise.
  - A landing line keeps the level's kind.
  - `last_open[lv]` is set to `op` when the level is opened. On landing it is set to `True` for an item and to `op` otherwise.
  - Both maps are read only for the landed level, and that level is always on the stack, so it was assigned when opened. Read them with `[]`, never `.get(…, default)` (Missing inputs).
- D-P, the probe rule (orchestrator): step 2 runs before the parser change. A fixture whose measured verdict differs from the predicted one changes its expected result, never the probe input, loader or version. The expected verdict in 05 and the docstring line follow the table in step 2. The CASES expectation of a measured-and-confirmed fixture (g1, g2, er1, D3) differing is a contradiction of a measurement: I2 stops and sends 03 back to R3.
- D6, out of scope. Holes R3 found while tracing are documented, not fixed. A1 may open a follow-up.
  - (a) `a:` / `  b` / `  c: d`. A key lands on the level of a plain line that sits under an empty-valued key. Today and after this item, the test returns a tool set. YAML (by the F17 mechanism, not measured) is expected to raise.
  - (b) `  a:` / `    b: c` / `  - x`. An item at a key's indent after that key's indented value passes (`last_open` is still True).
  - Both are listed under "Not checked" (step 4).

## Implementation map
Each `\|` inside a table cell is the Markdown table escape. The file has a plain `|`.
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | tests/test_agent_tools.py: add `SEQ_LEVEL` and `MAP_ITEM` (D2) next to INDENT, and 8 CASES (the ids may be renamed): g1 `_fm("hooks:", "- a", "  b: c", "tools: Read")` → VALUE(4); g2 `_fm("hooks:", "  - a", "    b: c", "tools: Read")` → VALUE(4); g3 `_fm("hooks:", "- a", "  b", TOOLS)` → {Read, Write}; g4 `_fm("hooks:", '- "a"', "  b: c", TOOLS)` → VALUE(4); er1 `_fm("hooks:", "  - x", "  a: v", TOOLS)` → SEQ_LEVEL(4); D3 `_fm("hooks:", "  a: v", "  - x", TOOLS)` → MAP_ITEM(4); k2 `_fm("hooks:", "  a:", "  - x", "  b: v", "  - y", TOOLS)` → MAP_ITEM(6); k4 `_fm("hooks:", "  - x", "name:", "  a: b", "  c: d", TOOLS)` → {Read, Write}. No parser change in this step. | - | 2 constants, 8 cases | BASE run (current parser + step 1): exactly g1, g2, g4, er1, D3, k2 fail → `6 failed, 167 passed`. 05 pastes the line and the ids | Fixtures: 6 expect an error (VALUE 3, SEQ_LEVEL 1, MAP_ITEM 2), 2 are negatives (g3, k4); 6 + 2 = 8 |
| 2 | PyYAML probe, before step 3 (information only; PyYAML is not a dependency). In a scratch venv, `python -I probe.py`. It loads each of the 8 fixtures' frontmatter lines (no `---`) with `yaml.load(text, Loader=yaml.SafeLoader)` (pure) and, if `yaml.__with_libyaml__`, `yaml.CSafeLoader`. It records `yaml.__version__`, `__with_libyaml__`, and per loader `loads <value>` or `<ExceptionClass> (<problem text>)`. Where CSafeLoader is absent, the column says "not measured (CSafeLoader absent, <version>)". Also probe, as information with no expectation, the 4 "Not checked" shapes of step 4 and D6. Rule D-P when a verdict differs from the prediction: g4 or k2 (predicted raise) loads → the expected verdict becomes "loads (<loader> <version>)", the CASES expectation stays (fail closed), and step 4 adds the shape to "Known fail-closed false errors". g3 or k4 (predicted load) raises → the expected verdict becomes "raises", the CASES expectation stays, step 4 adds the shape under "Not checked", and 05 names it as an RI-002 tool-set path for A1. g1, g2, er1, D3 (measured raise, rows 10, 11, 6) load → stop, send 03 back to R3 (D-P). The probe input is never edited to match a prediction. | scratch venv with PyYAML | probe table in 05 (fixture, test result, predicted, measured per loader) | I3 re-runs the probe and its table must match 05's. Predicted: g1, g2 ScannerError (both loaders, measured); g4 ParserError; er1, D3 ParserError (measured); k2 ParserError; g3, k4 load | – |
| 3 | `_frontmatter_error`: its docstring says "(items 080, 087, 096, 104, 106, 111)". Before the loop, `kind = {}` and `last_open = {}`. Replace the structure branch after `if error: return error` with the block "Step 3 code" below. The continuation branch, `_node`, `_field`, the 096 column-0 check and the tab/quote/flow checks are unchanged. | front lines | first error or None | `pytest tests/test_agent_tools.py` → `173 passed`. The 6 BASE failures pass, and the 165 existing tests keep their results (Self-check 1) | R-A: real tree 21 of 21 lines pass, 0 selected (0 `- ` lines in frontmatter, R3 Grep `^(---\|[ \t-])` over .claude/agents/*.md, 2026-11-26). Fixtures: 0 of 165 existing change; new: g1, g2, g4 selected. R-B: real tree 21 of 21 pass, 0 selected (no item, so no `seq` level exists); fixtures 0 of 165 change; new: er1 selected. R-C: real tree 21 of 21 pass, 0 selected (no item line); 0 of 165 change; new: D3, k2 selected. Empty result: no line selected → no error, and `test_no_shell_agents_leave_commands_to_orchestrator` still reports per file through tree_problems |
| 4 | Module docstring. (a) In "Item 106", change "measured on PyYAML 6.0.1 and 6.0.4" to "measured on PyYAML 6.0.1, 6.0.3 and 6.0.4". (b) Delete the paragraph's last sentence, from "Not checked (YAML's reading not checked): an indented `- ` item after a scalar-valued key" through "`_field` refuses it." (L82-L86). The paragraph then ends "…and a tab inside a quoted item of a flow collection." (c) Add the paragraph "Item 111" below. If step 2 measured a difference, add the D-P lines. | - | text | I1/I3 read the docstring diff against this cell. After step 3, 05 runs `agent_tools` on the 3 "Not checked" shapes and on D6 (a), and shows each returns {Read, Write} (Self-check 23) | – |
| 5 | Mutants, one at a time on a scratch copy, with PYTHONDONTWRITEBYTECODE=1 and a fresh PYTHONPYCACHEPREFIX (RI-015). The env-check line is pasted. M82: R-A removed (`prev = (col, op)` always) → g1, g2, g4. M83: the SEQ_LEVEL return removed → er1. M84: the MAP_ITEM return removed → D3, k2. M85: the landing update of `last_open` removed → k2, nk6. M86: on landing, `last_open[ind] = op` for items too → nk6, v19. M87: `kind[lv] = …` → `kind.setdefault(lv, …)` → k4. M88: the landed level also gets the line's kind (the `if not (landed and lv == ind)` guard applies to `last_open` only) → g3, k2, nk7, nk12, s6, v18, v19. M56-M81 and X1-X4 must still fail every id of their 106/06 lists. New ids there are recorded, not a Deviation. | code | failing ids per mutant | 05/06 list each mutant with its failing ids. Each list must equal this cell, or 05 states the difference as a Deviation with its run output | – |
| 6 | Full suite and real tree. | repo | pytest line | `pytest` → 1069 + 8 = 1077 passed, 1 skipped (if the base is unchanged). `test_no_shell_agents_leave_commands_to_orchestrator` passes | Real tree: 7 files, 21 lines, all pass (Self-check 2) |

Step 3 code (the structure branch after `if error: return error`; plain Python 3.10):
```python
                popped = False
                while stack and stack[-1] > ind:
                    stack.pop()
                    popped = True
                if popped and (not stack or stack[-1] != ind):
                    return INDENT.format(n)
                dash = [ind + j for j, ch in enumerate(line[ind:col]) if ch == "-"]
                is_key = bool(KEY_RE.match(line[col:]))
                landed = bool(stack) and stack[-1] == ind
                if landed and not dash and kind[ind] == "seq":
                    return SEQ_LEVEL.format(n)
                if landed and dash and kind[ind] == "map" and not last_open[ind]:
                    return MAP_ITEM.format(n)
                if landed:
                    stack.pop()
                    last_open[ind] = True if dash else op
                levels = sorted({ind, col} | set(dash))
                for lv in levels:
                    if not (landed and lv == ind):
                        kind[lv] = "seq" if lv in dash else ("map" if lv == col and is_key else None)
                        last_open[lv] = op
                stack.extend(levels)
                if dash and not op and not sb and not is_key:
                    prev = (dash[-1], False)
                else:
                    prev = (col, op)
                if sb:
                    block = col
```
`dash` is the same set as 106's inner-dash expression (L351), so the stack contents are unchanged. For a non-item line `dash` is empty and `col == ind`.

Step 4 "Item 111" paragraph (exact text; wrap to the docstring's width):
"Item 111: after a `- ` item whose value on its line is a closed scalar (plain, quoted or flow; no key, not empty, not a block header), a later line indented past the item's last dash is a continuation line and gets the item 104 check. For a plain value not ended by ` #` this is how YAML reads the line. After a quoted, flow or ` #`-ended value YAML starts no continuation, and a colon there is refused all the same. A structure line that lands on an open level first opened by a `- ` dash must be a `- ` item. A `- ` item that lands on an open level first opened by a key must follow an empty-valued key or another item at that level. This says nothing about what Claude Code does with such a file. Not checked (YAML's reading not checked): a line with no `: ` indented past the dash of a quoted, flow or ` #`-ended scalar item (`- "a"` / `  b`); a `- ` item at a key's indent after that key's indented value (`  a:` / `    b: c` / `  - x`); a key at the indent of a plain line under an empty-valued key (`a:` / `  b` / `  c: d`)."

Prevention guardrail (BUG), the one the request names:
- Each shape gives a named error: F-1 both forms (g1, g2) and the quoted form (g4) give VALUE, er1 gives SEQ_LEVEL, and D3 (plus its reset form k2) gives MAP_ITEM.
- Each new check fails a named fixture under its own mutant (M82, M83, M84), and the state rules are pinned by M85-M88.
- RI-012 negatives: g3, k4, s6, nk6 and v19.
- Every fixture is probed in both loaders where available (step 2, before the change).
- The real-tree test still runs over every agent file (step 6).
- Every remaining known pass of a shape YAML is expected to reject is named in the docstring, so none is undocumented (the F-1 failure mode).

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Previous structure line (`prev`, step 3) | the first meaningful line | `prev = None`, so the line is a structure line, never a continuation (unchanged) |
| Open levels (`stack`) at the first line, or after a dedent below every level | first line: nothing to pop, `landed` False | No R-B/R-C on an unlanded line. A dedent that empties the stack gives INDENT (s5, unchanged) |
| Level kind (`kind[ind]`) on landing | cannot be absent: every stack level is assigned when opened (D4). `None` = opened by a non-key, non-item node | Read with `kind[ind]`, never `.get(ind, default)`. A missing key raises KeyError and the test fails loudly. `None` → no R-B/R-C claim |
| `last_open[ind]` on landing | the same: assigned on open | `last_open[ind]`, never defaulted to True or False |
| Dash columns (`dash`) | the line is not a `- ` item | `[]`. R-A does not apply, and R-C does not apply |
| Last line of the frontmatter | no following line | R-A only sets `prev`, so nothing is assumed about a next line |
| PyYAML verdict on g3, g4, k2, k4 | not measured yet | Not claimed (Removed claims 2, 4). Measured in step 2, with rule D-P |
| CSafeLoader verdict | absent in the container | "not measured (CSafeLoader absent, <version>)" in 05 |
| Claude Code's YAML reader | not named (work/106/01-research.md F19) | No runtime claim. The docstring keeps the disclaimer |

## Self-check
R3 traces by hand (no shell). `n = i + 2`. prev = (column, open). S = the stack. K = kind, L = last_open. "lands on 2" means S[-1] = 2 = ind after any pops. The continuation threshold is `ind > prev[0]` with prev closed.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| 1. Existing 165 unchanged | R-A changes `prev` only after a closed scalar item; R-B/R-C fire only on a landed `seq` level (non-item) or a landed `map` level with L False (item) | R-A rows: d `  - Read` prev (2) → `  - Write` 2 > 2 false, lands on 2 (K seq, item) → pass. y4 `    Bash` 4 > 2 → continuation, `in_flow` → `_field` 075 (was: lands on 4). c5 6 > 0, f1 6 > 2, c2 6 > 2 → continuation (as before). s7 `    - b` 4 > 4 false → lands on 4 (K seq). q23 `  - github` lands on 2 (K seq), then end. nk6/v19 `- x` prev (0) → the next column-0 line 0 > 0 false. Landings on map with an item: nk6, nk7, nk12, v18, v19, v21, c5, nk9 → L[0] True (set by the open key `tools:`/`hooks:`/`hr: # …`/`rbi:`/`description:`). s6 `  - x` lands on 2 (K map, L True from `  a:`). Non-item landings: v18, v19, nk7, nk12 TOOLS/`rbi:` lands on 0 (K map). s3 `    c: d` on 4 (K map). p13 `      hooks:` on 6, `command:` on 10 (K map). s6 `  b: c` on 2 (K map). q23 `command`/`args` on 6 (K map). Errors that come first: s1, s2, s4, s5 INDENT; nk3, nk4, nk8, nk11 NO_KEY; v3 VALUE in `_node`; p3, w-cases, tb-cases tabs; TREE cases are column-0 lines | 165 of 165 keep their result |
| 2. Real tree | 21 lines, all column 0, none an item | L2 opens 0 (K map); L3 and L4 land on 0 with no dash → K map ≠ seq; no item → no R-C; no `- ` → R-A not used | 21 of 21 pass |
| 3. g1 | R-A then 104 check | `hooks:` opens 0 (K map, L True). `- a` lands on 0 (096: prev_open True); dash [0], col 2, closed, no key → prev (0, False). `  b: c` 2 > 0 → continuation; `in_flow` False; `_plain_colon("b: c")` True; i = 2 | VALUE(4) |
| 4. g2 | same | `  - a` opens 2 (seq), 4 (None); prev (2, False). `    b: c` 4 > 2 → continuation → `: `; i = 2 | VALUE(4) |
| 5. g3 | negative | `  b` 2 > 0 → continuation, no `: ` → none. TOOLS 0 > 0 false → pops 2, lands on 0, K map, non-item → no SEQ_LEVEL. `_field` → Read, Write | {Read, Write} |
| 6. g4 | quoted item | VALUE_START c = `"`, `_quote_end` = 5, `AFTER_CLOSE_RE` matches "". `_node` col 2, closed; `KEY_RE.match('"a"')` None → prev (0, False). `  b: c` 2 > 0 → `_plain_colon` True; i = 2 | VALUE(4) |
| 7. er1 | R-B | `  - x` opens 2 (seq), 4 (None); prev (2, False). `  a: v` 2 > 2 false → pops 4 (popped), 2 = 2 → no INDENT; landed, dash [], K[2] seq; i = 2 | SEQ_LEVEL(4) |
| 8. D3 | R-C | `  a: v` opens 2 (map, L = op False); prev (2, False). `  - x` 2 > 2 false; lands on 2, dash [2], K map, L False; i = 2 | MAP_ITEM(4) |
| 9. k2 | R-C after reset | `  a:` opens 2 (map, L True). `  - x` lands on 2 (K map, L True → ok), L ← True; opens 4 (None); prev (2, False). `  b: v` 2 > 2 false; pops 4, lands on 2 (K map, non-item → no SEQ_LEVEL); L ← op False. `  - y` lands on 2, K map, L False; i = 4 | MAP_ITEM(6) |
| 10. k4 | reopened level | `  - x` opens 2 (seq), 4. `name:` 0 > 2 false; pops 4, 2; lands on 0 (K map); L[0] ← True; prev (0, True). `  a: b` open prev → structure; opens 2 fresh: K map, L False; prev (2, False). `  c: d` 2 > 2 false; lands on 2, K map → no SEQ_LEVEL. TOOLS lands on 0 | {Read, Write} |
| 11. s6 negative (R-B and R-C) | measured load (106/05 L236) | `  a:` opens 2 (map, L True). `  - x` lands, L True → ok. `  b: c` pops 4, lands on 2, K map (not changed by the item) → ok | {Read, Write} |
| 12. Threshold values | `ind > prev[0]` | g1 2 > 0 T; g2 4 > 2 T; g3 2 > 0 T; g4 2 > 0 T; er1 2 > 2 F; D3 2 > 2 F; s7 4 > 4 F; d 2 > 2 F; y4 4 > 2 T; c5 6 > 0 T; f1 6 > 2 T; nk6 0 > 0 F | as used in rows 1-11 |
| 13. p13 / q23 / s3 kinds | K per open | p13: 0 map, 2 map, `    - matcher` 4 seq / 6 map, `        - type` 8 seq / 10 map; key items keep prev = (col, op). q23: 2 seq, 4 map, 6 map. s3: 2 seq, 4 map; `  - e: f` lands on 2 seq | pass ×3 |
| 14. Counts | 165 + new; BASE = new cases failing on today's parser | 165 + 8 = 173. Split VALUE 3 + SEQ_LEVEL 1 + MAP_ITEM 2 + pass 2 = 8. BASE today: g1 → {Read}, g2 → {Read}, g4/er1/D3/k2 → {Read, Write} (each lands on an existing level); g3 lands on 2 → pass; k4 → pass. 6 failed; 173 − 6 = 167 | `173 passed` / BASE `6 failed, 167 passed` |
| 15. M82 | prev = (col, op) | g1 `  b: c` 2 > 2 false → lands on 2 (K None) → pass; g2 4 > 4 false → lands on 4 (None) → pass; g4 the same. g3 lands on 2 (None) → pass (unchanged). y4 lands on 4 (None) → `_field` 075 (unchanged). er1/D3/k2/k4 do not use R-A | g1, g2, g4 |
| 16. M83 / M84 | return removed | M83: er1 → {Read, Write}. M84: D3 → {Read, Write}; k2 → {Read, Write} | er1 / D3, k2 |
| 17. M85 | no `last_open` update on landing | k2: L[2] stays True after `  b: v` → `  - y` ok → pass. nk6: `name: x` opens 0 with L False, `tools:` lands with no update → `- Read` MAP_ITEM(4). v19/nk7/nk12/v18: the open key is the first line (L True at open) → pass. s6: the item lands, L stays True → pass | k2, nk6 |
| 18. M86 | landing item sets L = op | nk6: `- Read` op False → `- Write` MAP_ITEM(5). v19: `- Mark McGwire` → `- Sammy Sosa` MAP_ITEM(4). k2 already expects MAP_ITEM(6); `- x` then `b: v` (a key) → same. s6: the item is followed by a key → pass | nk6, v19 |
| 19. M87 | `setdefault` | k4: 2 opened as seq, popped by `name:`, reopened by `  a: b` → stays seq → `  c: d` lands on seq → SEQ_LEVEL(6). q23: 4 reopened by `  - github` stays map, but nothing lands after it → pass. Other reopened levels get the same kind again (d 4 None; s3 4 map; s7 6 None; v19 2 None; k2 4 None) | k4 |
| 20. M88 | a landed level takes the line's kind | a landing column-0 or indented item makes the level seq, and a later non-item landing gives SEQ_LEVEL: g3 TOOLS (5), k2 `  b: v` (5), nk7 TOOLS (4), nk12 TOOLS (5), s6 `  b: c` (5), v18 TOOLS (4), v19 `rbi:` (6). nk6, c5, v21, nk9 end after their items → pass. D3's MAP_ITEM check comes before the assignment → unchanged | g3, k2, nk7, nk12, s6, v18, v19 |
| 21. Column-0 kind (R2 AGAINST 3a) | level 0 is opened by the first frontmatter line, a key (096 rejects an item first, nk11; INDENT an indented first line, s5) | K[0] = map, and landings never change it → R-B cannot fire at column 0. R-C at column 0: 096 lets an item through only after a column-0 open key or item, and both set L[0] True → R-C cannot fire there either | no change at column 0 |
| 22. Distinct kill lists | rows 15-20 | M82 {g1, g2, g4}; M83 {er1}; M84 {D3, k2}; M85 {k2, nk6}; M86 {nk6, v19}; M87 {k4}; M88 {g3, k2, nk7, nk12, s6, v18, v19}. No two are equal | each mutant distinguishable |
| 23. Docstring "Not checked" shapes pass | trace after step 3 | `- "a"` / `  b`: 2 > 0 → continuation, no `: ` → pass. `- a # c` / `  b`: the same. `  a:` / `    b: c` / `  - x`: `    b: c` opens 4 (map); `  - x` pops 4, lands on 2 (K map, L True from `  a:`) → pass. `a:` / `  b` / `  c: d`: `  b` opens 2 (K None, not a key); `  c: d` 2 > 2 false, lands on 2, K None → pass | each → {Read, Write}, so the docstring is true |
| 24. F5 shape | `- a` / ` b: c` | R-A prev (0, False); 1 > 0 → continuation → `: `; i = 2 | VALUE(4) (was INDENT(4); not a fixture) |

`check_handoff output (run by the orchestrator 2026-11-26 23:41 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 6
fact-check rows: 84
totals line: 84 rows -> 69 as-is, 11 fixed, 4 removed
PASS
```
