# 04 Build plan - 075
Fit verdict: FIT WITH CHANGES

Fit check: this is process tooling only. It does not touch the bot, quotes, the ~$3k account rules or 001, so no rule text the person follows changes. One file changes: tests/test_agent_tools.py (072's drift test on PR #32). No other code imports it (Grep `test_agent_tools|agent_tools` in scripts/, tests/ and work/076-079: only the file itself and two "no overlap" notes in 076/04 and 077/03). scripts/probe_guardrails.py (078) does not mention agents. 075 builds first, so nothing upstream is changed under it. Stdlib `re` only, as 03 D1 says.

The changes (from the extra research below): two YAML forms in 03's map still leave a line the parser does not read, which is the RI-002 shape this item fixes. (1) A plain value continued on an indented next line (`tools: Read, Write` then `  , Bash`). Today the parser reads only the key line. (2) A blank or comment line inside a block list (`- Read`, blank, `- Bash`). Today the loop stops at the blank line and drops `Bash`. Both become named errors (step 1 rules (h) and (i) below). I also add the missing absent-case fixtures (n5 file missing, n6 no files), one body-line fixture (n7), and the exact problem text.

Recurring issues checked (item 013), against this plan:
- RI-001 (ESCALATED): every filter has a dated, non-zero count from 03 and a test that pins it (Guardrail tests). ENTRY_RE: 40 of 40 entries on the 7 L4 lines (re-read by I1 2026-11-19 with Grep `^(tools|disallowedTools|Tools):` in .claude/agents: 7 hits, all comma form, 0 `disallowedTools:`). Allow-list: 4 of 4 NO_SHELL files hold exactly the 6 names. Body-line rule: 5 of 5 no-shell `python3 scripts/` lines name the orchestrator (r1 L19, r2 L22, r3 L20, r3 L24, i1 L18, Grep). No "always" without a count.
- RI-014 (OPEN): not touched. Only tests/test_agent_tools.py changes, and check_pipeline.py `_walk` is not read or changed.
- RI-002 (GUARDED, 075 is its near miss): this is the fix. Every line or entry the parser cannot read is a named error, including the two forms added here. Nothing is defaulted, and each Missing inputs row has an absent-case fixture.
- RI-012: classification is by full match (`re.fullmatch`) on a parsed token, never a substring. The wording lint stays unchanged (D5).
- RI-008: no `match`, no syntax newer than 3.10. `dict[str, str]` hints are 3.9+. I3 runs `python3.11 -m py_compile`.
- RI-006: I2/I3 copy test counts from pytest's last line, not by hand.
- RI-004/005: every new fixture below is traced through its rule (Rule trace and Tests).
- RI-009/011: no file overlap with 076-079 (Grep above).
- Not applicable: RI-003, RI-007 (FULL scope, I1-I3 run; no `.claude/` or `templates/` edit), RI-010 (no new agent-text duty), RI-013 (no realtest change).

## Extra research (with sources)
1. **Plain scalars can continue on the next line.** YAML 1.2.2 §2.3: "All flow scalars can span multiple lines; line breaks are always folded." §6.5: "all line breaks are folded without exception." (https://yaml.org/spec/1.2.2/, fetched 2026-11-19; R3's row #12 has the same quote.) A plain value is a flow scalar, so `tools: Read, Write` followed by an indented `  , Bash` is one value, `Read, Write , Bash`. 03's map reads only the key line (`{Read, Write}`), so a no-shell agent could get Bash unseen. The empty-entry rule catches `tools: Read,` + `  Bash`, but not this case. New rule (h): after a key line with an inline value, any later indented line that is not blank and not a comment is an error. Fail closed: it does not matter how the runtime folds the line.
2. **Comments between block entries.** YAML 1.2.2 §2.2, Example 2.9 (same fetch): `hr: # 1998 hitters` then `  - Mark McGwire`, and `rbi:` then `  # 1998 rbi leaders` then `  - Sammy Sosa`. A comment line inside a block sequence is valid YAML. The spec text I could fetch was cut off before §6.7/§8.2.1, so the blank-line case rests on the same separation rules, not on a quote. Today's loop (L27-L34) stops at the first line that is not `- X`. With `tools:` / `  - Read` / blank / `  - Bash`, it returns `{Read}`, and r1 would pass with Bash. New rule (i): a blank or comment line followed by another `- X` item in the same list is an error. I chose an error, not a skip, because a skip would be unsafe for `disallowedTools` (it would read more denials than the runtime might, so fewer tools). An error is safe both ways and does not depend on the unquoted section. `hr: # 1998 hitters` (a comment after the key) already fails as entry `# 1998 hitters` under 03 rule (f).
3. **Key with a space before the colon** (`tools : Read, Bash`). In YAML this is still the key `tools`. The parser does not see a `tools:` line, so it gives 072's no-tools error. That fails closed. I pin it with fixture z so a later "tolerant" key match must keep it an error. No source is needed, because the result does not depend on how the runtime reads it.
4. Checked and not needed: the runtime's behaviour for any of these forms (03 #11, #19 unknowns). Each new rule is an error whatever the runtime does.

## Files to create/change
1 file: **tests/test_agent_tools.py** (change). Nothing else. No `.claude/`, `templates/`, `scripts/` or `ccbot/` edit.

- Module docstring: add a paragraph saying that any `tools:`/`disallowedTools:` line or entry the parser cannot read (flow list, quotes, parens, continuation, blank or comment inside a list, separator, duplicate) is an error, never "not Bash", and that the four no-shell agents may list only `NO_SHELL_ALLOWED` (item 075).
- Constants: `import re`. `ENTRY_RE = re.compile(r"[A-Za-z]+(\([^()]*\))?")`, always used with `.fullmatch`. `NO_SHELL_ALLOWED = {"Read", "Write", "Glob", "Grep", "WebSearch", "WebFetch"}`. Keep `NO_SHELL` unchanged.
- `_field(lines, key) -> (found: bool, entries: list[str], error: str | None)`. It replaces 072's `_field`. Rules, applied in this order, returning the first error:
  - (a) Key lines are `line == key + ":"`, `line.startswith(key + ": ")` or `line.startswith(key + ":\t")`. Any other line that starts with `key + ":"` → `f"{key}: needs a space after the colon (item 075)"`.
  - (b) A second key line → `f"duplicate {key}: line (item 075)"`. None → `(False, [], None)`.
  - Tail scan of the lines after the key line, until the first line that is not blank, not a comment (`strip()` starts with `#`) and not indented (`line[0] not in " \t"`), except that a `- X` / `-` line at column 0 still counts as an item:
    - (h) If the inline value is non-empty, any tail line that is not blank or a comment → `f"unparsed {key}: line '{s}' (item 075)"`, where `s = line.strip()`.
    - (i) If the inline value is empty: `- X` gives item `X`, and a bare `-` gives item `""`. A blank or comment line seen after an item, then followed by another item → `f"blank or comment line inside {key}: list (item 075)"`. A comment or blank line before the first item that is followed by an item gets the same error (Example 2.9's `rbi:` shape). Any other indented line → the (h) message.
  - (c) An inline value that starts with `[` must end with `]`, else `f"unclosed [ in {key}: (item 075)"`. Strip the pair. `[]` (or blank inner text) → no entries.
  - (d) Split on commas at paren depth 0. A `)` at depth 0, or depth > 0 at the end → `f"unbalanced ( ) in {key}: (item 075)"`.
  - (e) Each entry (comma, flow or block): `strip()`, then strip one matching pair of `"` or `'` around the whole entry if the entry is at least 2 characters long.
  - (f) Each entry must `ENTRY_RE.fullmatch`, else `f"unparsed {key}: entry '{x}' (item 075)"`, where x is the entry after (e).
  - (g) No entries → `(True, [], None)`.
- `agent_tools(text)`: frontmatter handling is unchanged. Then `_field(front, "tools")`. Its error is returned first, then 072's "no tools: line ..." and "empty tools: (item 072)" texts, unchanged. Then `_field(front, "disallowedTools")`: its error is returned, and empty or absent removes nothing. Names are `e.split("(")[0]`.
- `tree_problems(texts: dict[str, str]) -> (list[str], set[str])`. It is 072's loop moved out, keyed by stem, with `label = f".claude/agents/{stem}.md"` so 072's messages are byte-identical. Empty dict → `(["no agent files under .claude/agents"], set())`. Per stem, sorted:
  1. Parse error → `f"{label}: {error}"`, then continue.
  2. If the stem is in NO_SHELL and `tools - NO_SHELL_ALLOWED` is not empty → `f"{label}: tools beyond the no-shell allow-list: {', '.join(sorted(extras))} (RULES decision, item 075)"`. No continue.
  3. If `"Bash" in tools`, continue.
  4. Add the stem to no_bash. Run 072's body-line check unchanged: `f"{label}:{n}: runs a script with no shell (item 072)"`.
- `test_no_shell_agents_leave_commands_to_orchestrator`: keep `assert files`, build `{p.stem: p.read_text() for p in files}`, call `tree_problems`, and keep 072's two asserts (problems, `no_bash == NO_SHELL`) and the run-item.md strings unchanged.

## Tests and checks
Parser `CASES` (072's a-f unchanged). Each case asserts the exact error, or the exact set with error None:

| Case | Text (frontmatter) | Expected |
|---|---|---|
| g | `tools: [Read, Write, Bash]` | {Read, Write, Bash} |
| h | `tools: [Read, Write]` | {Read, Write} |
| i1 | `tools: Read, "Bash"` | {Read, Bash} |
| i2 | `tools:` / `  - 'Bash'` | {Bash} |
| j1 | `tools: Read, Bash]` | `unparsed tools: entry 'Bash]' (item 075)` |
| j2 | `tools: Read, Write # Bash` | `unparsed tools: entry 'Write # Bash' (item 075)` |
| j3 | `tools: [Read, Bash` | `unclosed [ in tools: (item 075)` |
| k | `tools: Agent(worker, researcher), Read` | {Agent, Read} |
| l | `tools: Read` / `tools: Bash` | `duplicate tools: line (item 075)` |
| m | `tools: Read, Bash` / `disallowedTools: [Bash]` | {Read} |
| q | `Tools: Read` | 072 no-tools-line error |
| r | `tools: 'Read, Bash'` | `unparsed tools: entry ''Read' (item 075)` |
| s | `tools:Read` | `tools: needs a space after the colon (item 075)` |
| t1 | `tools: Bash) (x` | `unbalanced ( ) in tools: (item 075)` |
| t2 | `tools: Bash(a)(b)` | `unparsed tools: entry 'Bash(a)(b)' (item 075)` |
| u | `tools: Read,,Write` | `unparsed tools: entry '' (item 075)` |
| v | `tools: []` | `empty tools: (item 072)` |
| w | `tools: Read, Bash` / `disallowedtools: Bash` | {Read, Bash} |
| x | `tools: >` | `unparsed tools: entry '>' (item 075)` |
| y1 (new) | `tools: Read, Write` / `  , Bash` | `unparsed tools: line ', Bash' (item 075)` |
| y2 (new) | `tools:` / `  - Read` / (blank) / `  - Bash` | `blank or comment line inside tools: list (item 075)` |
| y3 (new) | `tools:` / `  # leaders` / `  - Read` (spec Ex. 2.9 shape) | `blank or comment line inside tools: list (item 075)` |
| y4 (new) | `tools:` / `  - Read` / `    Bash` | `unparsed tools: line 'Bash' (item 075)` |
| y5 (new) | `tools: Read` / `  - Bash` | `unparsed tools: line '- Bash' (item 075)` |
| y6 (new, no false alarm) | `tools: Read, Write` / (blank) / `# c` / `name: x` | {Read, Write} |
| y7 (new) | `tools: Read, Bash` / `disallowedTools:` / `  - Read` / (blank) / `  - Bash` | `blank or comment line inside disallowedTools: list (item 075)` |
| z (new) | `tools : Read, Bash` | 072 no-tools-line error |

Traces for the new cases: y1: inline value non-empty, tail line `  , Bash` is indented and not blank or a comment → (h). y2: item `Read`, then a blank line, then item `Bash` → (i). y3: a comment line, then an item → (i). y4: indented `Bash` is not `- X` → (h) text. y5: inline value non-empty, so the tail `- Bash` → (h). y6: blank and comment lines are skipped, and `name: x` is at column 0, so the tail ends there → no error, entries `Read`, `Write`. y7: `tools` parses, then `disallowedTools` hits (i) → its error is returned. z: no line starts with `tools:` → not found → 072 text.

Tree fixtures via `tree_problems`. Baseline: the 4 NO_SHELL stems with `"---\ntools: Read, Write, Glob, Grep, WebSearch, WebFetch\n---\n"`, and the 3 shell stems (a1-auditor, i2-builder, i3-verifier) with `"---\ntools: Read, Bash\n---\n"`. Each case asserts the exact problems list and no_bash:
- n0 baseline → `[]`, no_bash == NO_SHELL.
- n1 r1 = x4 line `tools: [Read, Write, Glob, Grep, WebSearch, WebFetch, Bash]` → `[".claude/agents/r1-researcher.md: tools beyond the no-shell allow-list: Bash (RULES decision, item 075)"]`, r1 not in no_bash.
- n2 r1 = x5 line `..., WebFetch, "Bash"` → the same problem naming `Bash`.
- n3 r1 `tools: Read, Monitor` → the problem naming `Monitor`. r1 is in no_bash (no Bash).
- n4 r1 `tools: Read, bash` → the problem naming `bash`.
- n5 (new, file missing) r1 key removed from the dict → `[]`, no_bash == NO_SHELL − {"r1-researcher"} (≠ NO_SHELL).
- n6 (new, no files) `tree_problems({})` → `(["no agent files under .claude/agents"], set())`.
- n7 (new, body line) r1 text = baseline + `"run python3 scripts/x.py\n"` → `[".claude/agents/r1-researcher.md:4: runs a script with no shell (item 072)"]` (line 4 = first body line).

Real tree: `test_no_shell_agents_leave_commands_to_orchestrator` passes on today's 7 files.

Probes and mutations (I2 in 05, I3 in 06, scratch copy under the scratchpad only): 03 step 4's probes (x4 and x5 on r1 → fail; x1 on i2 → now passes; 072 m1-m5 still fail, m6 passes) and M1-M8 with their named cases. Added:
- M9: rule (i) replaced by 072's `break` → y2, y3, y7 fail.
- M10: rule (h) removed (tail lines ignored when the value is inline) → y1, y5 fail.
- M11: the body-line check removed from `tree_problems` → n7 fails.
- M12: `ENTRY_RE.fullmatch` replaced by `.match` → t2 fails (`Bash(a)` matches the prefix of `Bash(a)(b)`), and j1 fails.

A mutation that leaves every test green is a finding.

Whole suite: `python3 -m pytest -q`, with totals copied from the last line (RI-006). Also `python3.11 -m py_compile tests/test_agent_tools.py` (RI-008).

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 (a) key separator | `_field` (a); fixture s; M7 |
| Step 1 (b) duplicate key | `_field` (b); fixture l; M6 |
| Step 1 (c) unclosed `[` | `_field` (c); fixtures j3, g, h, v |
| Step 1 (d) depth-0 split, unbalanced | `_field` (d); fixtures k, t1; M4 |
| Step 1 (e) quote strip | `_field` (e); fixtures i1, i2, r; M2 |
| Step 1 (f) ENTRY_RE full match | `_field` (f) with `fullmatch`; fixtures j1, j2, t2, u, x; M3, M8, M12 |
| Step 1 (g) empty → 072 texts; error order; names before `(` | `_field` (g) and `agent_tools`; fixtures c, v, m, y7 |
| Step 1 docstring | Files: module docstring |
| Step 2 allow-list, before the Bash skip, 072 checks kept | `tree_problems` steps 2-4; fixtures n0-n4; M5 |
| Step 2 `tree_problems(texts)` refactor | `tree_problems` with byte-identical 072 labels; real-tree test; n6, n7 |
| Step 3 fixtures g-x, n0-n4 | Tests table (all kept, with exact texts) |
| Step 4 probes and M1-M8 | Tests: probes and mutations (plus M9-M12) |
| Step 5 whole suite + 3.11 compile | Tests: whole suite |
| D1 (1)-(3) | `_field` (a), (f) empty entry, (d) |
| D2 allow-list on top of 072 | `tree_problems` step 2; 072 asserts kept |
| D3 no MCP form | ENTRY_RE as written (letters only); an `mcp__` entry fails (f) |
| D4 fixtures | Tests table |
| D5 wording regex | DROPPED: out of scope, as 03 D5 decides (request marks it optional; A1: "not on its own worth an item"); body rule unchanged |
| D6 duplicate keys error | `_field` (b) |
| D7 multi-line flow list, block scalar error | (c) unclosed `[` (j3); (f) on `>` (x); plus new (h) for any continuation line |
| Missing inputs rows (7) | Guardrail tests: Missing inputs |
| I1 addition: continuation lines (h) | `_field` (h); y1, y4, y5; M10 |
| I1 addition: blank or comment inside a list (i) | `_field` (i); y2, y3, y7; M9 |

No rule the person follows (001) changes. No rule text update is needed.

## Guardrail tests
- Feasibility: ENTRY_RE on today's tree, 40 of 40 entries in 7 of 7 files (Grep 2026-11-19) → `test_no_shell_agents_leave_commands_to_orchestrator` (any parse error is a problem) + n0.
- Feasibility: allow-list, 4 of 4 NO_SHELL files ⊆ NO_SHELL_ALLOWED (2026-11-19) → the real-tree test + n0; n1-n4 pin that it fires.
- Feasibility: body-line rule, 5 of 5 lines name the orchestrator (2026-11-19) → the real-tree test + n7.
- Missing inputs: frontmatter → case a. `tools:` key absent or mis-cased → b, q, z. `tools:` value empty → c, v. A single entry empty or unreadable → u, j1, j2, r, x, t2. `disallowedTools:` absent or misspelled → w (and g, h, k without it). NO_SHELL file missing → n5. No agent files → n6.

## Expected result
- `pytest tests/test_agent_tools.py`: 072's 6 cases + 27 new parser cases (19 from 03: g, h, i1, i2, j1, j2, j3, k, l, m, q, r, s, t1, t2, u, v, w, x; 8 from I1: y1-y7, z) = 33 parametrized parser tests, + 8 tree fixtures (n0-n7, as one parametrized test or 8 functions), + the real-tree test = 42 tests in the file, all passing. I2 reports the exact count from pytest.
- The whole suite stays green. Its only change is these added tests.
- A1's x4/x5 probes on r1 fail the real-tree test with the allow-list problem naming Bash. M1-M12 each fail at least their named cases.
- The 7 shipped agent files are unchanged and pass.

Log fields: FIT WITH CHANGES | 1 files planned
