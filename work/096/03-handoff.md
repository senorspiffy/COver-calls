# 03 Research hand-off - 096
Status: READY

Type BUG, Scope FULL, so no 07-audit-task.md is due from R3. The code change goes through I1-I3. Branch daily-fixes/2026-11-24, read only. R3 has no shell and ran no test, regex, PyYAML call or git command. Every "R3 trace" below was done by hand against tests/test_agent_tools.py as it stands (92 tests). I2 confirms each one by running it.

Recurring issues checked (logs/recurring-issues.md, read first): RI-001 (ESCALATED), RI-010 (ESCALATED), RI-014 (OPEN), and the GUARDED entries RI-002, RI-003, RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-011, RI-012, RI-013. How each was applied:
- RI-001: the new allow-list is a filter rule. Its pass count is computed below: 21 of 21 real frontmatter lines pass, and 0 of 90 existing fixtures change result (Feasibility column, Self-check rows 1-2). Nothing is asserted as "always".
- RI-002 (this item's root cause, near miss, not counted): a line the test cannot read becomes NO_KEY. It never becomes a tool set. When there is no previous line, `prev_open` starts False (Missing inputs).
- RI-004/005: every fixture and mutation was traced against the rule's own regex and state (Self-check).
- RI-006: totals are left to check_handoff.
- RI-007: Scope FULL. I1-I3 run, and no code is in R1-R3.
- RI-008: PyYAML is not used in the test. The reason is that it is not a declared dependency (pyproject.toml L10, 080 D7). RI-008 itself does not rule it out (fact row 36). No 3.11+ syntax is used: the step 2 code uses no walrus and no `re.prefixmatch`.
- RI-010: log lines are written by the orchestrator. The check_handoff line is left empty.
- RI-012: KEY_RE is anchored with `.match`. The in-text negatives are the q30 swap (`...x: y` / `---x: z`, the marker as a key prefix) and nk10 (an inner colon).
- RI-014, RI-003, RI-009, RI-011, RI-013 do not apply: no git, calendar, branch, merge-base or realtest path is involved.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 1. R1 F1: check order in `_frontmatter_error` is DOC, lead tab, TAB_BEFORE, START, quote, flow (FLOW_KEYS skipped); no column-0 key check | tests/test_agent_tools.py L170-L198 | VERIFIED | - |
| 2. R1 F2: VALUE_START_RE text; the key group is optional | tests/test_agent_tools.py L45 | VERIFIED | - |
| 3. R1 F3: `_field` breaks on a column-0 non-item; `_is_item` | tests/test_agent_tools.py L79-L80, L51-L52 | VERIFIED | - |
| 4. R1 F4: `name: x`/`foo`/TOOLS → {Read, Write}; I3 base probe | work/087/06-verification.md L17; logs/audit/2026-11-22-087.md L82-L84 | VERIFIED | - |
| 5. R1 F5: trailing `foo` → {Read, Write}; PyYAML ScannerError | R3 trace; audit L83 | VERIFIED | - |
| 6. R1 F6: `name: x`/`- a`/`tools: Read` → {Read}; PyYAML ParserError | R3 trace; audit L83-L84 | VERIFIED | - |
| 7. R1 F7: q30 text at L404; PyYAML ScannerError; 04 calls it valid at L236-L243; q30 is the only fixture M41 kills | tests L404; 087/06 L14, L56; 087/04 | VERIFIED (citation fixed) | The "valid" wording is at 087/04 L229 ("why these lines are valid"). L236/L243 hold the q30 row and its trace. |
| 8. R1 F8: `...x: y`/`---x: z` loads in PyYAML; head returns {Read, Write}; M41 kills it | 087/06 L17; audit L79-L80 | VERIFIED | - |
| 9. R1 F9: 7 files, 14 `^---$` hits, 21 `^(name\|description\|tools): ` lines | R3 Grep over .claude/agents, 2026-11-24 (14 hits; count 3 per file, 21 total) | VERIFIED | - |
| 10. R1 F10: 33 + 15 + 31 = 79 parser cases; 11 tree cases; 92 tests | R3 count of CASES/TREE, tests L272-L458; 087/06 L10 | VERIFIED | - |
| 11. R1 F11: no other 09x item changes test_agent_tools.py | R3 Grep over work/09*/*.md: 096 files and 090/06 L5 only | VERIFIED | - |
| 12. R1 F12: 22 fixtures have a column-0 non-key line after an earlier error line | R3 trace (p1, p2, p5, p6, p14; q1-q10; q12-q15; n8, n10, n11). q11 has no closer line and is rightly left out | VERIFIED | - |
| 13. R1 F13: q16, q17, p15, q27, q28, s_no_space have the shape on their error line | R3 trace | VERIFIED | - |
| 14. R1 F14: `tools : Read, Bash` is a key under an L45-shaped key test | R3 trace of KEY_RE (step 1): `t`, `ools `, `:`, space | VERIFIED | - |
| 15. R1 F15 / Numbers: "20 empty-valued-key fixtures" incl. q14 | R3 scan of CASES | WRONG | Corrected: 17 parser fixtures (c, d, i2, p3, p4, p13, p14, q5, q6, q13, q15, q18, q23, y2, y3, y4, y7) plus tree n9 = 18. q14 is `description: &d`, which has a value. 8 of the 17 are on non-FLOW_KEYS keys (p13, p14, q5, q6, q13, q15, q18, q23). These are the ones M45 kills (Self-check 14). |
| 16. R1 F16: y6 has a column-0 `# c` and a blank line | tests L315 | VERIFIED | - |
| 17. R1 F17: no existing fixture has a column-0 `- X` line | R3 scan of CASES/TREE | VERIFIED | - |
| 18. R1 F18: "Each node must be indented further than its parent node." / "All sibling nodes must use the exact same indentation level." | https://spec.yaml.io/main/review/markdown.html (YAML 1.2.2, 2021-10-01) | VERIFIED | - |
| 19. R1 F19: "Implicit keys are restricted to a single line." | spec.yaml.io | VERIFIED | - |
| 20. R1 F20: `-`, `?`, `:` "are perceived by people to be part of the indentation." | spec.yaml.io | VERIFIED | - |
| 21. R1 F21: spec example "Mapping Scalars to Sequences" puts `- ` items at the key's column, so `tools:`/`- Read` is valid YAML | spec.yaml.io; https://redocly.com/docs/yaml/sequences ("The indentation isn't required when mapping scalars to sequences.", example `citrus:` / `- orange`) | VERIFIED | Basis for D1 (option b). |
| 22. R1 F21: whether PyYAML 6.0.3 loads `tools:`/`- Read` as a list | none (R1 marks UNVERIFIED) | UNSUPPORTED | Removed. Not claimed. D1 rests on the spec example (row 21). |
| 23. R1 F22: A1 measured a ParserError for `name: x`/`- a`; the spec production was not read | audit L83-L84 | VERIFIED | The spec part stays unread and is not used. |
| 24. R1 F23: `---` separates directives from content; `...` ends a document | spec.yaml.io | VERIFIED | - |
| 25. R1 F24: indicator list `- ? : , [ ] { } # & * ! \| > ' " % @` and the grave accent | spec.yaml.io | VERIFIED | Used for KEY_RE's first-character class (step 1). |
| 26. R1 F25: "YAML that doesn't parse: Claude Code reads no fields from the file, skips it, and writes the parse error to the debug log." The parser is not named | https://code.claude.com/docs/en/sub-agents | VERIFIED | No runtime claim is made. |
| 27. R1 F26: `tools` is a comma-separated string or a YAML list, and inherits every tool if omitted | code.claude.com sub-agents | VERIFIED | - |
| 28. R1 F27: `claude plugin validate` quote; cited as "087 D8 (work/087/03-handoff.md L147)" | code.claude.com sub-agents (quote right; page adds "Requires Claude Code v2.1.233 or later") | VERIFIED (citation fixed) | 087/03 L147 is its Missing-inputs row ("No claim is made ... (080 D8)"). The decision is 080 D8. Not needed for 096. |
| 29. R1 Numbers: 79/92 tests; 21 real lines, 0 hit; 22 / 6 / 1 / 0 fixture counts | rows 10, 9, 12, 13, 14, 17 | VERIFIED | The 20 is covered in row 15. |
| 30. R1 projection 98 or 99 tests | R3 map below | WRONG (superseded) | Corrected: the map adds 10 parser cases (nk1-nk10) and 1 tree case (n12), and q30 is replaced in place. 89 + 12 + 1 + 1 = 103 (Self-check 3). |
| 31. R1 mutations M42-M46 (M44 fails only fixture 3; M45 fails "every empty-valued-key fixture") | R3 trace (Self-check 11-19) | WRONG (part) | Corrected: M44 (items always allowed) fails nk3, nk4, nk8. M45 fails 12 fixtures (p13, p14, q5, q6, q13, q15, q18, q23, nk6-nk9), not the FLOW_KEYS-only fixtures, because those lines are exempt. M42, M43 and M46 hold as R1 predicted (M42 now 8 named). M47-M50 added. |
| 32. R1 OQ1: "087 chose fail closed throughout (work/087/03-handoff.md D4)" | 087/03 L127 | WRONG (citation) | D4 is 087's tab decision. 087's general fail-closed posture is in its D-list and 080 D8. 096 picks option (b) (D1) because the fail-closed alternative would reject a spec-valid `tools` list (rows 21, 27). |
| 33. R2: N1 source and A1's draft rule | logs/audit/2026-11-22-087.md L77-L102 (draft L99) | VERIFIED | - |
| 34. R2: 087's R2 suggested an allow-list | work/087/02-improvements.md L44 | VERIFIED | - |
| 35. R2: 087 AGAINST 3 precedence warning | work/087/02-improvements.md L46-L51 | VERIFIED | - |
| 36. R2: "RI-008 (L101): adding PyYAML to the test is still off the table" | logs/recurring-issues.md L101-L106 (RI-008 is the Python 3.10 floor); pyproject.toml L10 `dependencies = ["numpy", "pandas"]`; 087/03 #77 | WRONG | Corrected (same fix as 087 #77): PyYAML is not used because it is not a declared dependency (080 D7). RI-008 does not rule it out by itself. |
| 37. R2: frontmatter lines come from `text.splitlines()` | tests L203 | VERIFIED | - |
| 38. R2: 0 real frontmatter lines contain a second `: ` | R3 Grep `^(name\|description\|tools): .*: ` over .claude/agents: 0 | VERIFIED | - |
| 39. R2: 087 used French/Russian/Dutch; 093 N/A | logs/research/2026-11-21.md L12; logs/research/2026-11-24.md L9 | VERIFIED | - |
| 40. R2 FOR 1 Japanese: KYAML is "標準YAMLの厳格なサブセット(もしくは「方言」)" / "YAMLが多くの選択肢を与えてくれる" | https://kubernetes.io/ja/blog/2026/08/11/how-to-pretty-print-kubernetes-yaml-as-kyaml/ | VERIFIED | Translation correct. The second sentence is "それはYAMLが多くの選択肢を与えてくれるということです". |
| 41. R2 FOR 1 Chinese: "冒号后面必须有一个空格或换行" | https://support.huaweicloud.com/intl/zh-cn/devg-cci/cci_05_1001.html | VERIFIED | Translation correct. |
| 42. R2 FOR 1 Turkish: "İki nokta'dan ":" sonra bir boşluk varsa bu bir dictionaryi temsil eder." | https://dev.to/enesgerem/yaml-1men | VERIFIED | Translation correct. |
| 43. R2 FOR 1: a tab after the colon is already caught by TAB_BEFORE, so `[ \t]` in the key test changes nothing | R3 trace of L45, L182 | WRONG (part) | Corrected: true when a value follows (p11). For `key:\t` with nothing after it, VALUE_START_RE's key group fails, so there is no TAB_BEFORE, and KEY_RE accepts the line. That is a key with an empty value, so this is not a false pass of a non-key. |
| 44. R2 FOR 1: put the new check last in the line; 0 real lines | R3 trace (Self-check 1, 18) | VERIFIED | M46 pins it. |
| 45. R2 FOR 2: reusing the L45 key group as-is lets `- a: b` and `%x: y` count as keys | R3 trace (L45 class `[^\s"'#&!*\[{?:]` admits `-`, `%`) | VERIFIED | - |
| 46. R2 FOR 2 German/Spanish: "er stieß auf ein - Listenelement, wo er einen Schlüssel erwartete" / "se topó con un elemento de lista - donde esperaba una clave" | https://abacktools.com/de/blog/how-to-detect-and-fix-yaml-errors ; https://abacktools.com/es/blog/how-to-detect-and-fix-yaml-errors | VERIFIED | Translations correct. One site, one source. |
| 47. R2 FOR 2: the key's first char must not be an indicator, except `-` before a non-space | spec.yaml.io indicator list (row 25); https://blogs.perl.org/users/tinita/2018/03/strings-in-yaml---to-quote-or-not-to-quote.html (`-<space>` "Block sequence entry", `@`/backtick "Reserved characters") | VERIFIED | Adopted as KEY_RE (step 1). |
| 48. R2 FOR 2: one mutation (L45 key group reused) fails both `- a: b` and `%x: y` | R3 trace | WRONG (part) | Corrected: in the map, the item branch runs before KEY_RE, so `- a: b` is caught as an item after a scalar (killed by M44). M47 (L45 class) fails only nk5 `%x: y`. |
| 49. R2 FOR 3: Redocly "The indentation isn't required when mapping scalars to sequences." | https://redocly.com/docs/yaml/sequences | VERIFIED | - |
| 50. R2 FOR 3: state = "was the previous non-blank, non-comment column-0 line an empty-valued key or an item?" | R3 trace | WRONG (part) | Corrected: taken over the previous non-blank, non-comment line of any column. Otherwise `hooks:` / `  a: b` / `- c` passes: `hooks:` is the last column-0 line, but its value is already a nested mapping. Pinned by nk8 and M48. |
| 51. R2 FOR 3: `_field` already reads column-0 items | tests L79, L51-L52 | VERIFIED | - |
| 52. R2 AGAINST 1: `a:b: c` is a valid plain key, from the Turkish rule on colons in values | dev.to/enesgerem (re-fetched: the sentence is about a colon in the value part) | WRONG (source) | Fixed with a new source: perl.org (tinita) "A colon is allowed, but only if it's not followed by whitespace." So `a:b` is a valid plain scalar. Listed as a known false error and pinned by nk10. |
| 53. R2 AGAINST 1: "Python treats ASCII record separator ('\x1e') as a newline" | https://mail.python.org/pipermail/python-bugs-list/2018-August/375874.html | VERIFIED | - |
| 54. R2 Holes 5: splitlines also splits on \x0b, \x0c, \x1c-\x1e, \x85, U+2028, U+2029 (marked UNVERIFIED) | https://mail.python.org/pipermail/python-checkins/2015-April/135329.html (table: \n, \r, \r\n, \v/\x0b, \f/\x0c, \x1c, \x1d, \x1e, \x85,  ,  ) | VERIFIED (new source) | Fixed: the full list is now sourced. |
| 55. R2 AGAINST 1: YAML 1.2 treats only CR and LF as line breaks | none (R2/R1 could not read that chapter) | UNSUPPORTED | Removed. The docstring says only that the test splits there, and makes no YAML claim. |
| 56. R2 AGAINST 2 Educative: `key1: value1:`, "an unnecessary colon after `value1`" | https://www.educative.io/answers/unable-to-parse-yaml-mapping-values-are-not-allowed-here | VERIFIED | Follow-up F-1. |
| 57. R2 AGAINST 2: `name: x: y` and `name: x`/`  foo: bar` pass the new rule | R3 trace (KEY_RE matches `name: `; indented lines are skipped) | VERIFIED | Out of scope (follow-ups F-1, F-2). |
| 58. R2 AGAINST 2: "A simple key is restricted to only one line. - A simple key must not be longer than 1024 characters." | https://fuchsia.googlesource.com/third_party/pyyaml/+/refs/tags/5.2/tests/data/spec-10-08.error | VERIFIED | Follow-up F-3. |
| 59. R2 AGAINST 3 de/es: the error line can come after its cause | abacktools de/es | VERIFIED | Translations correct. |
| 60. R2 AGAINST 3: `n = i + 2` is the test's own count | tests L173 | VERIFIED | The error text does not claim to be PyYAML's mark. |
| 61. R2 Italian: "Le coppie chiave-valore seguono la struttura chiave: valore ..." / "Un trattino all'inizio della riga indica un elemento di lista." | https://www.datacamp.com/it/blog/what-is-yaml | VERIFIED | Translation correct. Background only. |
| 62. R2 Hole 9: abacktools was also used in 087 (es, ru), so it is one source | work/087/02-improvements.md L27, L75 | VERIFIED | - |
| 63. R2: this is the fourth item on this parser (075, 080, 087, 096) | tests L9-L34 docstring | VERIFIED | - |
| 64. R2: PyYAML results for `- a: b`, `%x: y` and the nk8 shape (marked UNVERIFIED) | none | UNSUPPORTED | Removed as claims. The fixtures pin the test's own rule. I2 may probe them in scratch as information only. 04/05 must not call them "YAML-invalid" without that probe output. |

**Totals:** 64 rows checked → **49 VERIFIED as-is**, **12 fixed**, **3 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
1. Row 22: PyYAML loads column-0 `tools:` / `- Read` as a list. This was not measured. D1 rests on the YAML spec example instead.
2. Row 55: YAML 1.2 treats only CR/LF as line breaks. Not read. The docstring makes no YAML claim about the splitlines characters.
3. Row 64: PyYAML verdicts for `- a: b`, `%x: y` and `hooks:` / `  a: b` / `- c`. Not measured. They may be recorded only from an I2/I3 probe, and only as information.

## Decisions
- D1 (R1 OQ1, R2 FOR 3): option (b). A column-0 `- ` item is allowed only when the previous non-blank, non-comment line (of any column) is a column-0 empty-valued key or a column-0 item. Blank and comment lines do not reset the state. `_field` still gives its own gap error for `tools:` (nk9).
- D2 (R1 OQ2, R2 FOR 2): key = KEY_RE (step 1). The first character is not whitespace or a YAML indicator, or it is `-` followed by a non-space. After that come any non-colon characters, then `:` followed by a space, a tab or the end of the line. Quoted keys never reach it: p15-style lines get AFTER earlier.
- D3 (R1 OQ3): the new check is the last check in each line. `tools:`/`disallowedTools:` lines are left to `_field` (FLOW_KEYS). M46 and M50 pin this.
- D4 (R1 OQ4): 096's 04 and 05 each carry one sentence: "087's q30 (`...x` / `---x`) was not valid YAML (PyYAML 6.0.3 ScannerError, work/087/06-verification.md L14); 087/04 L229 called it valid." 087's files are not edited.
- D5 Error text: `no key on frontmatter line {n} (item 096)`. `n` is the test's own line count (L173). It is not PyYAML's mark.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | tests/test_agent_tools.py: after DOC_MARKER_RE add ``KEY_RE = re.compile(r"""(?:[^\s"'#&!*\[\]{},\|>%@`?:-]\|-(?=\S))[^:]*:(?=[ \t]\|$)""")`` (the `\|` in this cell is the table escape; the file has a plain `|`). Next to DOC/TAB_BEFORE add `NO_KEY = "no key on frontmatter line {} (item 096)"`. | - | constants | Unit by fixtures (step 4). Self-check 4-10 trace each shape through KEY_RE | - |
| 2 | `_frontmatter_error`: set `prev_open = False` before the loop. At the end of each line's body (after the existing `if m:` block, so last in the line, D3): if `line[:1] not in ("", " ", "\t", "#") and not line.startswith(FLOW_KEYS)`, then if `_is_item(line)` and not `prev_open`, return `NO_KEY.format(n)`; elif not `_is_item(line)` and not `KEY_RE.match(line)`, return `NO_KEY.format(n)`. Then, if `line.strip()` is non-empty and does not start with `#`: `k = KEY_RE.match(line)`; `prev_open = line[0] != " " and (_is_item(line) or bool(k and not line[k.end():].strip()))`. No walrus. Do not reuse the name `s` (it is the value index in the `if m:` block). Docstring: "(items 080, 087, 096)". | front lines | first error or None | All 90 existing cases keep their result (q30 is rewritten in step 4). Fixtures nk1-nk10 and n12 as in step 4 | Real tree: 21 of 21 frontmatter lines pass (7 files; each line is `name: `, `description: ` or `tools: ` at column 0). R3 Grep 2026-11-24, `^(name\|description\|tools): ` = 21 and `^---$` = 14. Run as `test_no_shell_agents_leave_commands_to_orchestrator`. Existing fixtures: 90 of 90 keep their result (R3 trace, Self-check 1). Empty result: none. The rule selects nothing. A failing line gives the named NO_KEY error, which is reported per file by tree_problems |
| 3 | Module docstring: add an "Item 096:" paragraph. A column-0 frontmatter line must be blank, a `#` comment, a `key:` (followed by a space, a tab or the end of the line; the key does not start with a YAML indicator, except `-` followed by a non-space), or a `- ` item directly after a column-0 empty-valued key or another column-0 item (blank and comment lines skipped). `tools:` and `disallowedTools:` lines are left to `_field`. Anything else is an error. Keep "This says nothing about what Claude Code does with such a file." Known fail-closed false errors: a key with an inner colon not followed by a space (`a:b: c`). Also rejected (YAML's reading not checked): a column-0 item after an empty-valued key that carries a comment (`hooks: # c`); a column-0 item after the indented content of an earlier column-0 item; text split by `str.splitlines()` at \x0b, \x0c, \x1c, \x1d, \x1e, \x85, U+2028 or U+2029. | - | text | I1/I3 read the docstring diff against this cell | - |
| 4 | CASES: replace q30 with `"q30_marker_prefix_text": (_fm("name: x", "...x: y", "---x: z", TOOLS), {"Read", "Write"}, None)`. Add nk1 `_fm("name: x", "foo", TOOLS)` → NO_KEY(3); nk2 `_fm("name: x", TOOLS, "foo")` → NO_KEY(4); nk3 `_fm("name: x", "- a", "tools: Read")` → NO_KEY(3); nk4 `_fm("name: x", "- a: b", TOOLS)` → NO_KEY(3); nk5 `_fm("name: x", "%x: y", TOOLS)` → NO_KEY(3); nk6 `_fm("name: x", "tools:", "- Read", "- Write")` → {Read, Write}; nk7 `_fm("description:", "- a", TOOLS)` → {Read, Write}; nk8 `_fm("hooks:", "  a: b", "- c", TOOLS)` → NO_KEY(4); nk9 `_fm("tools:", "", "- Read")` → `"blank or comment line inside tools: list (item 075)"`; nk10 `_fm("a:b: c", TOOLS)` → NO_KEY(2). Error cases use `(text, None, NO_KEY.format(n))`. TREE: `"n12_no_key_line": ({"r1-researcher": f"---\nfoo\ntools: {SIX}\n---\n"}, None, [f"{R1}: {NO_KEY.format(2)}"], NO_SHELL - {"r1-researcher"})`. Ids are free to rename. | - | 10 parser cases + 1 tree case; q30 rewritten | `pytest tests/test_agent_tools.py` → 103 passed. Base-failure check (base parser + head fixtures): exactly nk1, nk2, nk3, nk4, nk5, nk8, nk10, n12 fail, so 8 failed, 95 passed | Fixtures: 7 parser + 1 tree expect NO_KEY; 3 positives (nk6, nk7, q30); 1 gap error (nk9) |
| 5 | Mutations (I2 runs one at a time on a scratch copy; I3 re-runs). M41 (existing, DOC terminator dropped) → q30. M42 new check removed → nk1, nk2, nk3, nk4, nk5, nk8, nk10, n12. M43 new check skips the last front line → nk2. M44 item branch always allowed (no `prev_open`) → nk3, nk4, nk8. M45 KEY_RE lookahead `(?=[ \t])` (no end of line) → p13, p14, q5, q6, q13, q15, q18, q23, nk6, nk7, nk8, nk9. M46 new check moved before the DOC check → p15, q16, q17, q27, q28. M47 KEY_RE first-character class replaced by L45's `[^\s"'#&!*\[{?:]` (no `-` alternative) → nk5. M48 `prev_open` updated only on column-0 lines → nk8. M49 a blank/comment line sets `prev_open = False` → nk9. M50 FLOW_KEYS exemption dropped from the new check → s_no_space. | code | named failing ids per mutation | 05/06 list each mutation with its failing ids. Each must equal this cell, or 05 states the difference as a Deviation with its run output | - |
| 6 | 04 and 05: D4 sentence on 087's q30. 05 records the real-tree run and the suite line as printed. | - | text | I3 checks that the sentence is present and that the PyYAML cite matches 087/06 L14 | - |

Prevention guardrail (BUG): steps 2, 4 and 5. Column-0 lines are checked against an allow-list, so an unlisted shape fails with a named error instead of each bad shape having to be named. Each branch of the rule is pinned by a fixture that a named mutation kills (M42-M50), and the real-tree test still runs over every agent file. This is the request's guardrail plus three additions: the indicator-based key class (M47), the any-column state (M48) and the blank/comment non-reset (M49).

Follow-ups for A1 (same root cause, outside 096's request, each 0 real lines; per 053 these are new items, not 096 scope):
- F-1: a second `: ` inside a value (`name: x: y`) passes. Educative's "mapping values are not allowed here" example.
- F-2: an indented `  foo: bar` under a scalar-valued key passes (PyYAML result not measured).
- F-3: a column-0 key longer than 1024 characters passes (PyYAML spec-10-08 test data).
- F-4: an allow-list for indented lines as well (087/02 L44). This would close F-1 and F-2 together.
- F-5 (false error, documented in step 3): `hooks: # c` followed by a column-0 item. Allowing a trailing comment needs its own fixture.

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Frontmatter block (`agent_tools`, L204-L209) | no opening/closing `---` | `no frontmatter` (unchanged) |
| Previous non-blank, non-comment line (step 2 `prev_open`) | the column-0 item is the first meaningful line | `prev_open` starts False, so the item gives `no key on frontmatter line <n> (item 096)`. It is never assumed open |
| A column-0 line's key (step 2 KEY_RE) | no `key:` shape, or the first character is an indicator | `no key on frontmatter line <n> (item 096)`. It never becomes a tool set |
| `tools:` line (`_field`) | missing | `no tools: line (inherits every tool incl. Bash, item 072)` (unchanged) |
| PyYAML's verdict on new shapes (nk4, nk5, nk8) | not measured | not claimed (Removed claim 3). The fixtures pin the test's rule only |
| Claude Code's YAML reader | not named in the docs (row 26) | no runtime claim. The docstring keeps "This says nothing about what Claude Code does" |

## Self-check
R3 traces by hand (no shell). `n = i + 2` (L173). `prev_open` = P.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| 1. Existing fixtures unchanged | every column-0 line of the 79 + 11 cases either errors earlier, is FLOW_KEYS, or matches KEY_RE | non-FLOW_KEYS column-0 lines that reach the new check are `name: x`, `name: db-reader`, `name: browser-tester`, `description: ...` (p9, p10, p12, p13, q21-q24, q29, q31), `Tools: Read` (q), `disallowedtools: Bash` (w), `tools : Read, Bash` (z), `hooks:` (p13), `mcpServers:` (q23). Each first char is a letter, then `[^:]*`, then `:` + space or end of line. Closer lines (`end"`, `]`, `}`, ...) come after an earlier error (row 12). Same-line shapes (row 13) error earlier or are FLOW_KEYS | 90 of 90 keep their result; q30 is rewritten (step 4) |
| 2. Real tree | 21 lines `name: `/`description: `/`tools: ` | `n`/`d` first, KEY_RE matches; `tools:` exempt | 21 of 21 pass |
| 3. Test count | 79 + 10 parser, 11 + 1 tree, + 2 | 89 + 12 + 2 = 103; base fails 8 → 103 − 8 = 95 | 103 passed / base 8 failed, 95 passed |
| 4. nk1 | `foo`, i = 1 | not an item; KEY_RE: `f`, `oo`, then needs `:`, end → no match | NO_KEY(1 + 2 = 3) |
| 5. nk2 | `foo`, i = 2 (last) | as nk1; TOOLS at i = 1 is exempt | NO_KEY(4) |
| 6. nk3 / nk4 | `- a` / `- a: b`, i = 1; P from `name: x` | KEY_RE matches `name:`, rest `x` non-empty → P = False; `_is_item` True and not P | NO_KEY(3) both. Old checks: `- ` prefix, then c = `a`, or key `a:` + c = `b`: no earlier error |
| 7. nk5 | `%x: y`, i = 1 | L45 key group admits `%` → c = `y`, no earlier error; KEY_RE: `%` is excluded and is not `-` → no match | NO_KEY(3) |
| 8. nk6 / nk7 | `tools:` / `description:` sets P | KEY_RE: `t`/`d`, `[^:]*`, `:` then end → match; rest "" → P = True; `- Read`/`- a` is an item and P → allowed; the item keeps P = True; `_field`: column-0 `- ` lines are items (L79) | {Read, Write} both |
| 9. nk8 | `hooks:` P = True; `  a: b` | indented line: skipped by the check; meaningful, `line[0] == " "` → P = False; `- c` at i = 2 is an item and not P | NO_KEY(4) |
| 10. nk9 / nk10 | `tools:` P = True; `""` skipped (P kept); `- Read` allowed / `a:b: c` | `_field`: blank → gap, then item → gap error / KEY_RE: `a`, `[^:]*` = "", `:` then lookahead sees `b` → fail; L45 group also fails (`b` is not a space) → c = `a`, no earlier error | `blank or comment line inside tools: list (item 075)` / NO_KEY(2) |
| 11. q30 new | `...x: y`, `---x: z` | DOC needs space/tab/end after 3 chars, gets `x` → no; KEY_RE: `.` is not an indicator → `..x`, `:` + space; `---x: z`: not an item (`---` does not start with `- `), alt 2: `-` before `-` (non-space), `--x`, `:` + space | {Read, Write}. Under M41, `...x: y` matches `\.\.\.` → DOC(3) → fails |
| 12. n12 | front `[foo, tools: SIX]`, `foo` at i = 0 | NO_KEY(2); tree_problems appends `.claude/agents/r1-researcher.md: no key on frontmatter line 2 (item 096)`, r1 not in no_bash | problems = [that], no_bash = NO_SHELL − {r1} |
| 13. M43 | skip i = len(front) − 1 | lone column-0 non-keys at the last index: only nk2 (`foo` i = 2 of 3). nk9's `- Read` is last but allowed anyway | nk2 only |
| 14. M45 | `(?=[ \t])` only | empty-valued non-FLOW_KEYS keys with no earlier error before them: p13 `hooks:` (n5), p14, q5, q6, q15, q18 `hooks:` (n2), q13 `description:` (n2), q23 `mcpServers:` (n5), nk7, nk8 → NO_KEY at that line; nk6, nk9: `tools:` fails KEY_RE → P = False → item NO_KEY(4) | 12 fail |
| 15. M46 | new check before DOC | p15 `"`, q16 `?`, q17 `:` → excluded first char; q27 `...`, q28 `--- # c` → no `:` → NO_KEY instead of AFTER/START/DOC | 5 fail |
| 16. M44 / M47 | no P / L45 class | nk3 → {Read}, nk4 and nk8 → {Read, Write} / only `%x: y` changes (the L45 class admits `%`; `-` lines go to the item branch first; the class is only looser, so no positive flips) | nk3, nk4, nk8 / nk5 |
| 17. M48 / M49 | P set only from column-0 lines / blank resets | nk8: `hooks:` stays the last column-0 line → P = True → `- c` allowed → {Read, Write} / nk9: P = False at `- Read` → NO_KEY(4) | nk8 / nk9 |
| 18. M50 | FLOW_KEYS not exempt | `tools:Read`: `:` then `R` → KEY_RE fails → NO_KEY(2). Every other `tools:`/`disallowedTools:` line has a space or end of line after the colon; p11's tab gives TAB_BEFORE earlier | s_no_space only |
| 19. M42 | check removed (= base) | each NO_KEY fixture falls through: nk1/nk2/nk4/nk5/nk8/nk10 → {Read, Write}; nk3 → {Read}; n12 → no problem | 8 fail: nk1-nk5, nk8, nk10, n12 |

`check_handoff output (run by the orchestrator 2026-11-24 18:26 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 64
totals line: 64 rows -> 49 as-is, 12 fixed, 3 removed
PASS
```
