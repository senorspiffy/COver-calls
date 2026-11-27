# 04 Build plan - 111
Fit verdict: FIT WITH CHANGES

Input: work/111/03-handoff.md (Status: READY). I1 has no shell. Its one run was done by the orchestrator (2026-11-26, about 23:5x UTC, from /home/claude/fix, both commands exit 0, stderr empty, repo unchanged). The script and its outputs are in I1's scratch dir:
- `/tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i1-111-r1-b8p0b_aw/probe111.py`
- `out-isolated.txt` (system `python3 -I -B -X pycache_prefix=…`: PyYAML 6.0.1 pure)
- `out-usersite.txt` (`python3` with PYTHONDONTWRITEBYTECODE=1 and PYTHONPYCACHEPREFIX: PyYAML 6.0.3, `__with_libyaml__` True)

The script reads tests/test_agent_tools.py as text and execs it in memory: once as is (BASE), once with 03 step 3's block put in (NEW), and once per mutant on NEW. It runs all CASES, the 8 new fixtures and the 13 TREE cases, plus the real tree, then probes PyYAML. "Run" below means that run.

Fit check:
- ~$3k account and strategy rules: not touched. This is a test-only change to tests/test_agent_tools.py. It changes no order, cap, premium or 001 rule, so no rule text the person follows changes.
- Existing code: nothing outside tests/test_agent_tools.py calls `_frontmatter_error` or `agent_tools` (Grep over scripts/, tests/, ccbot/, .claude/, templates/).
- Parallel items: 112 and 113 edit tests/test_pipeline_check.py and scripts/check_pipeline.py, not this file (Grep of work/112, work/113 for test_agent_tools: no hits). So the only interaction is the full-suite total (Tests 6).

Why "WITH CHANGES": three changes to 03, none of which changes a CASES expectation.
- C1: the probe must run twice. 03 step 2 runs only `python -I`. `-I` drops the user site and every PYTHON* env var, and libyaml is only in the user site here (106/05 L211; run: `-I` gives 6.0.1, `__with_libyaml__` False). As written, CSafeLoader could never be measured.
- C2: the "Not checked (YAML's reading not checked)" docstring sentence is now false. The run measured all four of its shapes, and both loaders raise on each (table below). So the test still passes these four files although PyYAML rejects them. That is an RI-002 tool-set path, and the docstring must name it as such, not as unchecked. The request's "documented pass that matches YAML" does not hold for these four. They stay out of scope (orchestrator cut, 03 D6), so 05 names them for A1 as a follow-up.
- C3: fixture ids. 03 gives short ids, and the full ids are fixed in Files 1.

## Extra research (with sources)
1. **The plan was measured before FIT.** This guards against the RI-001/RI-010 near miss: 109's fixture was never run before FIT. Results:
   - BASE: `6 failed, 165 passed`, failing d3, er1, g1, g2, g4, k2. The 165 counts 158 CASES (150 + 8) and 13 TREE. It leaves out the 2 named tests, so pytest will show `6 failed, 167 passed` (03 Self-check 14).
   - NEW: `0 failed, 171 passed`. The real tree has 7 files, no problems, and `no_bash` = the 4 NO_SHELL agents.
   - Every mutant's kill list equals 03 step 5 exactly:
     - M82: g1, g2, g4.
     - M83: er1.
     - M84: d3, k2.
     - M85: k2, nk6.
     - M86: nk6, v19.
     - M87: k4.
     - M88: g3, k2, nk7, nk12, s6, v18, v19.
   - 106's structure mutants, put back on the new block, still kill their lists: M73 s1/s2/s4/s5; M74 (`levels = sorted({ind, col})`) s7; M75 s1/s2/s4.
   - No crash (KeyError) in any variant.
2. **PyYAML verdicts, measured. Every D-P prediction holds, so D-P adds no line.**

| shape | NEW test result | 6.0.1 SafeLoader | 6.0.3 SafeLoader | 6.0.3 CSafeLoader |
|---|---|---|---|---|
| g1 | VALUE(4) | ScannerError (mapping values are not allowed here) | same | ScannerError (… not allowed in this context) |
| g2 | VALUE(4) | ScannerError | ScannerError | ScannerError |
| g3 | {Read, Write} | loads `['a b']` | loads | loads |
| g4 | VALUE(4) | ParserError (… found '<block mapping start>') | same | ParserError (did not find expected key) |
| er1 | SEQ_LEVEL(4) | ParserError (… found '?') | same | ParserError (did not find expected '-' indicator) |
| d3 | MAP_ITEM(4) | ParserError (… found '-') | same | ParserError (did not find expected key) |
| k2 | MAP_ITEM(6) | ParserError (… found '-') | same | ParserError (did not find expected key) |
| k4 | {Read, Write} | loads | loads | loads |
| `- "a"` / `  b` | {Read, Write} | ParserError (… found '<scalar>') | same | ParserError |
| `- a # c` / `  b` | {Read, Write} | ParserError (… found '<scalar>') | same | ParserError |
| `  a:` / `    b: c` / `  - x` (D6 b) | {Read, Write} | ParserError | same | ParserError |
| `a:` / `  b` / `  c: d` (D6 a) | {Read, Write} | ScannerError | same | ScannerError |
| `- a` / ` b: c` (F5) | VALUE(4) (BASE: INDENT(4)) | ScannerError | same | ScannerError |
| er1_tools | SEQ_LEVEL(4) (BASE: 075 text) | ParserError | same | ParserError |
| s6, nk6, v19, s7 (controls) | {Read, Write} | load | load | load |

   This turns 03's removed claims 2 and 4 into measurements (information only; PyYAML is not a dependency). D3's no-skip decision changes er1_tools' message as predicted, and it still fails closed.
3. **`-I` and env vars.** "Run Python in isolated mode. This also implies -E, -P and -s options … ignores all PYTHON* environment variables" ([Python docs, command line](https://docs.python.org/3/using/cmdline.html)). So under `-I` the RI-015 env guard is ignored, and the probe needs `-B -X pycache_prefix=<scratch>`. The probe runs no mutant, so this only keeps .pyc out of the repo. I2's pytest mutant runs keep the env vars, without `-I`.
4. **Spec basis for the indentless sequence (R-C).** Production [201] `seq-spaces(n,c)`: "BlockOut uses n-1 (entries dedent by 1), BlockIn uses n", and mapping values use block-out ([rlsp-yaml-parser block.rs, citing YAML 1.2 productions](https://docs.rs/rlsp-yaml-parser/0.2.0/src/rlsp_yaml_parser/block.rs.html); secondary source). So a `- ` at a key's own indent is allowed only as that key's value, which is s6 (loads) against d3/k2 (raise). Chapter 8 of [yaml.org/spec/1.2.2](https://yaml.org/spec/1.2.2/) could still not be read: the page text is cut at 97,515 characters, and an offset fetch says so. This is background only, and the measured raises above are the evidence.

## Files to create/change
1. **tests/test_agent_tools.py** (only repo file).
   - a. Constants, next to INDENT, with the exact 03 D2 text:
     - `SEQ_LEVEL = "non-item line at a list's dash column on frontmatter line {} (item 111)"`
     - `MAP_ITEM = "list item at the indent of a key with a value on frontmatter line {} (item 111)"`
   - b. Add 8 CASES with 03 step 1's inputs and expectations, using these ids:
     - `g1_item_scalar_then_key` → VALUE(4)
     - `g2_indented_item_scalar_then_key` → VALUE(4)
     - `g3_item_scalar_continuation` → {Read, Write}
     - `g4_quoted_item_then_key` → VALUE(4)
     - `er1_key_at_item_dash` → SEQ_LEVEL(4)
     - `d3_item_after_scalar_key` → MAP_ITEM(4)
     - `k2_item_after_reset_key` → MAP_ITEM(6)
     - `k4_reopened_level_map` → {Read, Write}
     - The run found no id clash with existing CASES.
   - c. `_frontmatter_error`:
     - Docstring: "(items 080, 087, 096, 104, 106, 111)".
     - Add `kind = {}` and `last_open = {}` after `in_flow = False`.
     - Replace the structure branch after `if error: return error` (from `popped = False` to `block = col`) with 03's "Step 3 code" exactly. This is the text the run used. Nothing else changes: the continuation branch, `_node`, `_field`, the 096 check, and the tab, quote and flow checks.
   - d. Module docstring:
     - (a) In "Item 106", "6.0.1 and 6.0.4" → "6.0.1, 6.0.3 and 6.0.4".
     - (b) Delete Item 106's last sentence, from "Not checked (YAML's reading not checked): an indented `- ` item after a scalar-valued key" to "`_field` refuses it."
     - (c) Add the 03 step 4 "Item 111:" paragraph up to "…with such a file.", then end it with C2's text instead of 03's last sentence: "Known passes of files PyYAML rejects (both loaders raise, measured on PyYAML 6.0.1 and 6.0.3, item 111): a line with no `: ` indented past the dash of a quoted or ` #`-ended scalar item (`- "a"` / `  b`, `- a # c` / `  b`); a `- ` item at a key's indent after that key's indented value (`  a:` / `    b: c` / `  - x`); a key at the indent of a plain line under an empty-valued key (`a:` / `  b` / `  c: d`). Not checked (YAML's reading not checked): the same no-colon line after a flow scalar item."
   - Name functions, not line numbers. 112 and 113 do not touch this file, but lines may still move.
2. **Scratch only (not the repo).** I2's step 2 probe goes in its own scratch dir. It may copy I1's probe111.py, which needs only the anchor text to match. 05 pastes the table.

## Tests and checks
`RULES BRANCH:` lists only remote branches not merged into HEAD (`git branch -r --no-merged HEAD`), so on this branch's own checkout it normally reads `none` and does not name this branch's or its base branch's rule change; if it does name this branch, the remote has commits this checkout lacks (fetch and compare). To see the rule files this branch and its unmerged base change, run `git diff --stat origin/main...HEAD -- .claude templates scripts/check_pipeline.py scripts/check_handoff.py`; never switch this checkout to origin/main (item 113).

1. **BASE.** Add Files 1a-1b only, then run `pytest tests/test_agent_tools.py`. Expect `6 failed, 167 passed`, failing exactly the g1, g2, g4, er1, d3 and k2 ids (measured above). Paste the line and the ids in 05.
2. **PyYAML probe, before 1c (C1).** Run it twice from I2's scratch dir:
   - (i) `python3 -I -B -X pycache_prefix=<scratch>/pyc probe.py isolated`
   - (ii) `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<scratch>/pyc python3 probe.py usersite`
   - Record `yaml.__version__` and `__with_libyaml__` for each run. Where CSafeLoader is absent, write "not measured (CSafeLoader absent, <version>)".
   - The table must equal Extra research 2. If a verdict differs, apply 03 D-P: g1/g2/er1/d3 loading means stop and send back to R3. Any other difference changes only the docstring line and 05's table.
3. **Build.** Add Files 1c-1d, then run `pytest tests/test_agent_tools.py` → `173 passed`.
4. **After the build, run `agent_tools`** on the four "Known passes" shapes and on F5 and er1_tools. Expect {Read, Write} ×4, VALUE(4) and SEQ_LEVEL(4), as in Extra research 2. 05 names the four as RI-002 tool-set paths for A1 (C2).
5. **Mutants, one at a time, on a scratch copy.**
   - Run with PYTHONDONTWRITEBYTECODE=1 and a fresh PYTHONPYCACHEPREFIX, and paste the `True <pyc dir>` env-check line (RI-015).
   - Forms are as in probe111.py `MUTANTS`. Each must fail exactly:
     - M82 (R-A removed): g1, g2, g4.
     - M83 (SEQ_LEVEL return → `pass`): er1.
     - M84 (MAP_ITEM return → `pass`): d3, k2.
     - M85 (landing `last_open` update removed): k2, nk6_tools_col0_list.
     - M86 (landing `last_open[ind] = op`): nk6_tools_col0_list, v19_spec_two_comments.
     - M87 (`kind.setdefault`): k4.
     - M88 (kind assigned outside the landed guard): g3, k2, nk7, nk12, s6, v18, v19.
   - 106's M73 (INDENT `if False`), M74 (`levels = sorted({ind, col})`) and M75 (`if popped and not stack:`), put back on the new block, kill s1/s2/s4/s5, s7 and s1/s2/s4.
   - M56-M72 and M76-M81 and X1-X4 must still fail every id in their 106/05 L170-L207 lists. New ids are recorded, not a Deviation.
   - Any other difference is a 05 Deviation with its output.
6. **Full suite.** First run `pytest` before Files 1 (base B, which includes whatever 112/113 have landed). Then expect `B + 8 passed, 1 skipped`, which is 1077 only if B = 1069. `test_no_shell_agents_leave_commands_to_orchestrator` passes.
7. **Python 3.10 syntax.** Run `python3.11 -m py_compile tests/test_agent_tools.py` where available (RI-008). The block uses no walrus and no `match`.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1: SEQ_LEVEL/MAP_ITEM constants + 8 CASES; BASE 6 failed / 167 passed | Files 1a, 1b; Tests 1 (measured: same 6 ids) |
| Step 2: PyYAML probe before the parser change, both loaders, D-P | Tests 2, with C1 (two runs, `-I` flags); expected table = Extra research 2 |
| Step 3: `kind`/`last_open`, Step 3 code, R-A/R-B/R-C | Files 1c; Tests 3; measured NEW 0 failed |
| Step 4: docstring version list, delete D3/er1 "Not checked", add "Item 111" | Files 1d (a), (b), (c). The last sentence is changed by C2 because the shapes were measured to raise |
| Step 4: 05 runs agent_tools on the Not-checked shapes and D6 (a) | Tests 4 |
| Step 5: M82-M88 + 106 mutants, RI-015 guard | Tests 5 (lists measured equal) |
| Step 6: full suite + real tree | Tests 6 (base-relative because of 112/113); real tree measured no problems |
| D1: R-A on every closed scalar item (plain/quoted/flow) | Files 1c (`dash and not op and not sb and not is_key`); g4 pins quoted; M82 |
| D2: error texts; `n = i + 2` | Files 1a |
| D3: no `in_flow` skip for R-B/R-C | Files 1c; er1_tools measured SEQ_LEVEL(4), fails closed. No fixture added: both texts fail closed, and 03 cut it |
| D4: kind set only on open; landing keeps it; `last_open` on open/landing; `[]` reads | Files 1c; M85, M86, M87, M88 |
| D-P: probe rule | Tests 2. No differing verdict was measured, so no D-P line |
| D6: holes (a), (b) documented, not fixed | Files 1d (c) "Known passes" (C2: measured raise); 05 → A1 follow-up |
| Cuts: R2 FOR 2 (g5, g6, M89), k6/M90, k7, k1/k3/k5, in_flow skip, b1-b12 re-run | DROPPED: orchestrator scope cut (03 top). FOR 2's shapes are now measured to raise, so they are listed as Known passes (C2) |
| Prevention guardrail (named error per shape; mutant per check; negatives; probe; real tree; documented passes) | Files 1a-1d; Tests 2, 4, 5, 6 |
| Missing inputs table (prev, stack, kind, last_open, dash, last line, verdicts, CSafeLoader, Claude Code reader) | Guardrail tests: Missing inputs |
| 001 person rules (slack, tolerance, cap) | Not changed (test-only), so no rule text or request needed |

## Guardrail tests
- Feasibility: R-A selects 0 of 21 real frontmatter lines (real tree: 7 files, no problems, measured) and 3 fixtures (g1, g2, g4), pinned by M82 → those 3.
- Feasibility: R-B selects 0 real lines and 1 fixture (er1), pinned by M83 → er1.
- Feasibility: R-C selects 0 real lines and 2 fixtures (d3, k2), pinned by M84 → d3, k2.
- Feasibility: 0 of the 165 existing tests change (NEW 0 failed, measured).
- Missing inputs: no `prev` on the first line. The first line is a structure line, which s5_indented_first_line (INDENT) and nk11 (NO_KEY) pin. Unchanged and measured passing.
- Missing inputs: empty `stack` or no landing. R-B/R-C cannot fire, and INDENT does: s5, and M73/M75 kill s1/s2/s4(/s5).
- Missing inputs: `kind[ind]`/`last_open[ind]` are read only on a landed level, with `[]`, never `.get`. A missing key would raise. The run had no raise in 12 variants × 171 cases. M87 (k4) pins "assigned fresh on open". I3 greps the block for `.get(` and `setdefault`.
- Missing inputs: no dash (non-item line). R-A and R-C do not apply. er1 is the R-B pin, and k4's `  c: d` is the negative.
- Missing inputs: the item is the last line. Nothing is assumed: i2_block_single_quoted ends on a closed scalar item and passes.
- Missing inputs: CSafeLoader absent. Tests 2 writes "not measured (CSafeLoader absent, <version>)" (the `-I` run shows that case).
- Missing inputs: PyYAML absent. The probe prints "not importable" and the test suite does not depend on it.

## Expected result
- tests/test_agent_tools.py: 173 tests pass, and BASE before 1c gives `6 failed, 167 passed`.
- Each request shape gives a named error:
  - F-1 (both indent forms) and the quoted form give VALUE.
  - er1 gives SEQ_LEVEL.
  - D3 (and k2) gives MAP_ITEM.
- Each new check fails a named fixture under its own mutant, and M85-M88 pin the state rules.
- Negatives that both loaders load (g3, k4, s6, nk6, v19) still pass.
- The docstring has the corrected version list. Every shape the test still passes while both loaders raise is named under "Known passes of files PyYAML rejects", so none is undocumented, and 05 hands them to A1 as follow-ups.
- Full suite: base + 8 passed, 1 skipped. The real tree passes.

Recurring issues checked (logs/recurring-issues.md, read first):
- RI-001 (ESCALATED): every filter count above is measured, not asserted (real tree 0 of 21; fixtures 3/1/2; existing 0 of 165 change).
- RI-014 (OPEN): does not apply. There is no git or clone-depth path.
- RI-002 (GUARDED, this item's root cause, near miss): C2 names the four measured tool-set paths.
- RI-004/005: 03's traces and kill lists were checked against a run.
- RI-006: the counts come from the run lines.
- RI-007: Scope FULL, and I1 writes no code to the repo.
- RI-008: 3.10 syntax (Tests 7).
- RI-010: the log line is left to the orchestrator, and the plan was run before FIT (the 109 near miss).
- RI-012: negatives g3 and k4 are pinned by M88 and M87.
- RI-015: the env guard in Tests 5. `-I` needs flags (Extra research 3).
- RI-003, RI-009, RI-011 and RI-013 do not apply.

Log fields: FIT WITH CHANGES | 1 files planned
