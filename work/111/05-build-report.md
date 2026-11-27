# 05 Build report - 111
Scratch dir: /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-111-r1-82en7wtf

Base: 3794ef2 (daily-fixes/2026-11-26, after 113's I2 commit and 112's I1 commit). Everything below is inside the scratch dir above:
- `probe.py`: a copy of I1's probe111.py, unchanged. Its outputs are `out-isolated.txt` and `out-usersite.txt`.
- `tools/mut.py`: the mutant runner. `tools/shapes.py`: the Tests 4 run.
- `build.py`: a copy of the build file. mut.py restores it.
- `pyc-pr08izqa`: the pyc dir for the probe runs. `pyc-rcdkdih3`: the pyc dir for the mutant runs and shapes.py. Both were made with the mkdtemp command, prefix `pyc-`, inside the scratch dir.
- `wt`: a `git worktree add --detach` worktree at 3794ef2. Every mutant ran only there.

When the mutants were done, `wt`'s file was put back with `git checkout HEAD -- tests/test_agent_tools.py` and the worktree was removed with `git worktree remove`. In the main checkout I ran only the unmutated test file (BASE and build states) and the full suite. No `git stash` was used.

## Changes made (file: what changed)
- `tests/test_agent_tools.py` is the only file, as in 04 Files 1.
  - 1a: `SEQ_LEVEL` and `MAP_ITEM` added right after `INDENT`, with the exact 04 Files 1a text.
  - 1b: 8 CASES added at the end of CASES, with the 04 Files 1b ids, the 03 step 1 inputs and their expectations:
    - `g1_item_scalar_then_key`, `g2_indented_item_scalar_then_key`, `g3_item_scalar_continuation`, `g4_quoted_item_then_key`
    - `er1_key_at_item_dash`, `d3_item_after_scalar_key`, `k2_item_after_reset_key`, `k4_reopened_level_map`
  - 1c, `_frontmatter_error`:
    - The docstring now says "(items 080, 087, 096, 104, 106, 111)".
    - `kind = {}` and `last_open = {}` are set after `in_flow = False`.
    - The structure branch after `if error: return error` is replaced by 03's "Step 3 code".
    - I made the replacement with the same anchor strings as probe111.py (`OLD_INIT`/`OLD_BLOCK` → `NEW_INIT`/`NEW_BLOCK`, each found exactly once). So the repo text is the text the I1 run measured.
    - Nothing else in the function, `_node` or `_field` changed.
  - 1d, module docstring:
    - (a) "6.0.1 and 6.0.4" became "6.0.1, 6.0.3 and 6.0.4". The words after it were re-wrapped onto the next line.
    - (b) Item 106's last sentence was deleted, from "Not checked (YAML's reading not checked): an indented `- ` item" to "`_field` refuses it.". The paragraph now ends "…and a tab inside a quoted item of a flow collection."
    - (c) A new "Item 111:" paragraph: the 03 step 4 text up to "…with such a file.", then the 04 C2 "Known passes of files PyYAML rejects …" sentence and "Not checked … flow scalar item." word for word. It is wrapped at 76 columns, and no backtick span is split.
- No change to ccbot/, config/ or scripts/. `git diff --stat` lists only `tests/test_agent_tools.py | 66 +++++++++++++++++++++++++++++++++++++++--------`.

File counts (from commands, before commit):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
1
```
That is 1 file changed, which matches 04's "1 files planned".

## Connectivity check
- [x] every new function/rule is used:
  - `SEQ_LEVEL` and `MAP_ITEM` are returned by `_frontmatter_error` and used in the er1/d3/k2 expectations.
  - `kind`, `last_open`, `dash`, `is_key`, `landed` and `levels` are each read in the same structure branch that sets them.
  - The 8 cases are read by `test_agent_tools_parser`, which is parametrized over CASES.
- [x] every input has a source, every output has a consumer:
  - The input is the frontmatter lines, which come from `agent_tools`.
  - The output is an error string or a tool set. `tree_problems` reads it for the real tree (`test_no_shell_agents_leave_commands_to_orchestrator` passes), and so does the parser test.
- [x] every branch ends in a defined result:
  - A landed seq level with a non-item line → SEQ_LEVEL(n).
  - A landed map level whose last line had a value, followed by an item → MAP_ITEM(n).
  - A closed scalar item → `prev` at its last dash, so the next deeper line goes to the 104 continuation check (VALUE(n) or pass).
  - Otherwise the result is as before: INDENT, `_field`, or the tool set.
  - `kind[ind]` and `last_open[ind]` are read only when `landed` is true, and with `[]`. A missing key would raise. There were no raises in the 173 tests or in any mutant run.
- [x] no leftover TODOs or unused files: `grep -n TODO tests/test_agent_tools.py` gives nothing, and no file was added.
- Missing-data grep:
  - `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` → `38`. All 38 are pre-existing, and `git diff --stat -- ccbot/` is empty.
  - The same pattern plus `\.get\(|setdefault` on the added lines of `git diff tests/test_agent_tools.py` → no hit (grep exit 1).
  - The change has no dataclass field and no numeric default.
  - Every `>` test compares ints (`stack[-1] > ind`, `ind > prev[0]`), so none can be NaN.
  - `last_open[ind] = True if dash else op` is no default: an item at the level counts as an open slot, by the D4 rule. M85 and M86 pin it.
- Feasibility numbers (04 Guardrail tests), measured:
  - Real tree: 7 files, `problems none`, no_bash = the 4 NO_SHELL agents (probe NEW line below).
  - R-A selects g1, g2 and g4 (M82). R-B selects er1 (M83). R-C selects d3 and k2 (M84).
  - 0 of the 165 existing tests change: the build gives 173 passed.

## Test output (pasted, not summarized)
Suite: 1081 passed, 1 skipped in 148.27s (0:02:28)

Tests 6, base B (main checkout at 3794ef2, before any edit): `python3 -m pytest -q`, last line:
```
1073 passed, 1 skipped in 138.32s (0:02:18)
```
B = 1073, not 1069, because 113 has landed. Expected is B + 8 = 1081 passed, 1 skipped.

Tests 1, BASE (main checkout, Files 1a-1b only, old parser): `python3 -m pytest -q tests/test_agent_tools.py`, FAILED lines and last line:
```
FAILED tests/test_agent_tools.py::test_agent_tools_parser[d3_item_after_scalar_key]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[er1_key_at_item_dash]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[g1_item_scalar_then_key]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[g2_indented_item_scalar_then_key]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[g4_quoted_item_then_key]
FAILED tests/test_agent_tools.py::test_agent_tools_parser[k2_item_after_reset_key]
6 failed, 167 passed in 0.20s
```
These are exactly the 6 planned ids (g1, g2, g4, er1, d3, k2).

Tests 2, PyYAML probe (before 1c). It ran from the scratch dir and read the repo file with 1a-1b in place. Env check:
```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-111-r1-82en7wtf/pyc-pr08izqa python3 -c 'import sys; print(sys.dont_write_bytecode, sys.pycache_prefix)'
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-111-r1-82en7wtf/pyc-pr08izqa
```
The two runs:
- (i) `python3 -I -B -X pycache_prefix=<pyc-pr08izqa>/iso probe.py isolated` → exit 0, stderr 0 bytes.
- (ii) `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<pyc-pr08izqa> python3 probe.py usersite` → exit 0, stderr 0 bytes.

The repo file now holds the 8 cases under their full ids, and the probe adds its own short-id copies. So the probe's BASE/NEW counts include each new case twice: 166 CASES + 13 TREE = 179, and BASE has 12 failures = 6 ids × 2. I left the probe unchanged on purpose, so that it matches I1's script.

Run (ii) `out-usersite.txt`, whole:
```
python 3.13.18 | /usr/local/bin/python3 | label usersite
BASE: 12 failed, 167 passed (CASES+new 166, TREE 13) | failed: d3, d3_item_after_scalar_key, er1, er1_key_at_item_dash, g1, g1_item_scalar_then_key, g2, g2_indented_item_scalar_then_key, g4, g4_quoted_item_then_key, k2, k2_item_after_reset_key
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']
NEW: 0 failed, 179 passed (CASES+new 166, TREE 13) | failed: -
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']
  NEW d3: (set(), 'list item at the indent of a key with a value on frontmatter line 4 (item 111)')
  NEW er1: (set(), "non-item line at a list's dash column on frontmatter line 4 (item 111)")
  NEW g1: (set(), 'colon in unquoted value on frontmatter line 4 (item 104; quote the value)')
  NEW g2: (set(), 'colon in unquoted value on frontmatter line 4 (item 104; quote the value)')
  NEW g3: ({'Write', 'Read'}, None)
  NEW g4: (set(), 'colon in unquoted value on frontmatter line 4 (item 104; quote the value)')
  NEW k2: (set(), 'list item at the indent of a key with a value on frontmatter line 6 (item 111)')
  NEW k4: ({'Write', 'Read'}, None)
  NEW info nc1_quoted_item_plain: ({'Write', 'Read'}, None)
  NEW info nc2_comment_item_plain: ({'Write', 'Read'}, None)
  NEW info d6a_key_on_plain_level: ({'Write', 'Read'}, None)
  NEW info d6b_item_after_indented_value: ({'Write', 'Read'}, None)
  NEW info f5_key_between_dash_and_content: (set(), 'colon in unquoted value on frontmatter line 4 (item 104; quote the value)')
  NEW info er1_tools: (set(), "non-item line at a list's dash column on frontmatter line 4 (item 111)")
  BASE info nc1_quoted_item_plain: ({'Write', 'Read'}, None)
  BASE info nc2_comment_item_plain: ({'Write', 'Read'}, None)
  BASE info d6a_key_on_plain_level: ({'Write', 'Read'}, None)
  BASE info d6b_item_after_indented_value: ({'Write', 'Read'}, None)
  BASE info f5_key_between_dash_and_content: (set(), 'indent matches no open level on frontmatter line 4 (item 106)')
  BASE info er1_tools: (set(), "unparsed tools: line 'Bash: x' (item 075)")
M82: 6 failed, 173 passed (CASES+new 166, TREE 13) | failed: g1, g1_item_scalar_then_key, g2, g2_indented_item_scalar_then_key, g4, g4_quoted_item_then_key
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']
M83: 2 failed, 177 passed (CASES+new 166, TREE 13) | failed: er1, er1_key_at_item_dash
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']
M84: 4 failed, 175 passed (CASES+new 166, TREE 13) | failed: d3, d3_item_after_scalar_key, k2, k2_item_after_reset_key
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']
M85: 3 failed, 176 passed (CASES+new 166, TREE 13) | failed: k2, k2_item_after_reset_key, nk6_tools_col0_list
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']
M86: 2 failed, 177 passed (CASES+new 166, TREE 13) | failed: nk6_tools_col0_list, v19_spec_two_comments
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']
M87: 2 failed, 177 passed (CASES+new 166, TREE 13) | failed: k4, k4_reopened_level_map
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']
M88: 9 failed, 170 passed (CASES+new 166, TREE 13) | failed: g3, g3_item_scalar_continuation, k2, k2_item_after_reset_key, nk12_indented_comment_then_item, nk7_item_after_empty_key, s6_list_at_key_indent, v18_comment_key_then_item, v19_spec_two_comments
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']
M73: 4 failed, 175 passed (CASES+new 166, TREE 13) | failed: s1_map_dedent_between, s2_tools_list_dedent, s4_dedent_off_level, s5_indented_first_line
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']
M74: 1 failed, 178 passed (CASES+new 166, TREE 13) | failed: s7_nested_dash_levels
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']
M75: 3 failed, 176 passed (CASES+new 166, TREE 13) | failed: s1_map_dedent_between, s2_tools_list_dedent, s4_dedent_off_level
  real tree: 7 files, problems none, no_bash ['i1-reviewer', 'r1-researcher', 'r2-improver', 'r3-fact-checker']

PyYAML 6.0.3 | __with_libyaml__ True | /root/.local/lib/python3.13/site-packages/yaml/__init__.py
  yaml g1: SafeLoader ScannerError (mapping values are not allowed here) | CSafeLoader ScannerError (mapping values are not allowed in this context)
  yaml g2: SafeLoader ScannerError (mapping values are not allowed here) | CSafeLoader ScannerError (mapping values are not allowed in this context)
  yaml g3: SafeLoader loads {'hooks': ['a b'], 'tools': 'Read, Write'} | CSafeLoader loads {'hooks': ['a b'], 'tools': 'Read, Write'}
  yaml g4: SafeLoader ParserError (expected <block end>, but found '<block mapping start>') | CSafeLoader ParserError (did not find expected key)
  yaml er1: SafeLoader ParserError (expected <block end>, but found '?') | CSafeLoader ParserError (did not find expected '-' indicator)
  yaml d3: SafeLoader ParserError (expected <block end>, but found '-') | CSafeLoader ParserError (did not find expected key)
  yaml k2: SafeLoader ParserError (expected <block end>, but found '-') | CSafeLoader ParserError (did not find expected key)
  yaml k4: SafeLoader loads {'hooks': ['x'], 'name': {'a': 'b', 'c': 'd'}, 'tools': 'Read, Write'} | CSafeLoader loads {'hooks': ['x'], 'name': {'a': 'b', 'c': 'd'}, 'tools': 'Read, Write'}
  yaml nc1_quoted_item_plain: SafeLoader ParserError (expected <block end>, but found '<scalar>') | CSafeLoader ParserError (did not find expected key)
  yaml nc2_comment_item_plain: SafeLoader ParserError (expected <block end>, but found '<scalar>') | CSafeLoader ParserError (did not find expected key)
  yaml d6a_key_on_plain_level: SafeLoader ScannerError (mapping values are not allowed here) | CSafeLoader ScannerError (mapping values are not allowed in this context)
  yaml d6b_item_after_indented_value: SafeLoader ParserError (expected <block end>, but found '-') | CSafeLoader ParserError (did not find expected key)
  yaml f5_key_between_dash_and_content: SafeLoader ScannerError (mapping values are not allowed here) | CSafeLoader ScannerError (mapping values are not allowed in this context)
  yaml er1_tools: SafeLoader ParserError (expected <block end>, but found '?') | CSafeLoader ParserError (did not find expected '-' indicator)
  yaml ctl_s6_list_at_key_indent: SafeLoader loads {'hooks': {'a': ['x'], 'b': 'c'}, 'tools': 'Read, Write'} | CSafeLoader loads {'hooks': {'a': ['x'], 'b': 'c'}, 'tools': 'Read, Write'}
  yaml ctl_nk6_tools_col0_list: SafeLoader loads {'name': 'x', 'tools': ['Read', 'Write']} | CSafeLoader loads {'name': 'x', 'tools': ['Read', 'Write']}
  yaml ctl_v19_spec_two_comments: SafeLoader loads {'hr': ['Mark McGwire', 'Sammy Sosa'], 'rbi': ['Sammy Sosa', 'Ken Griffey'], 'tools': 'Read, Write'} | CSafeLoader loads {'hr': ['Mark McGwire', 'Sammy Sosa'], 'rbi': ['Sammy Sosa', 'Ken Griffey'], 'tools': 'Read, Write'}
  yaml ctl_s7_nested_dash_levels: SafeLoader loads {'hooks': [['a', 'b']], 'tools': 'Read, Write'} | CSafeLoader loads {'hooks': [['a', 'b']], 'tools': 'Read, Write'}
```
Run (i) `out-isolated.txt`:
- Its BASE/NEW/mutant lines equal run (ii)'s, except for set print order (`{'Read', 'Write'}`), checked with `diff`.
- Its PyYAML section:
```
PyYAML 6.0.1 | __with_libyaml__ False | /usr/lib/python3/dist-packages/yaml/__init__.py
CSafeLoader: not measured (CSafeLoader absent, 6.0.1)
  yaml g1: SafeLoader ScannerError (mapping values are not allowed here)
  yaml g2: SafeLoader ScannerError (mapping values are not allowed here)
  yaml g3: SafeLoader loads {'hooks': ['a b'], 'tools': 'Read, Write'}
  yaml g4: SafeLoader ParserError (expected <block end>, but found '<block mapping start>')
  yaml er1: SafeLoader ParserError (expected <block end>, but found '?')
  yaml d3: SafeLoader ParserError (expected <block end>, but found '-')
  yaml k2: SafeLoader ParserError (expected <block end>, but found '-')
  yaml k4: SafeLoader loads {'hooks': ['x'], 'name': {'a': 'b', 'c': 'd'}, 'tools': 'Read, Write'}
  yaml nc1_quoted_item_plain: SafeLoader ParserError (expected <block end>, but found '<scalar>')
  yaml nc2_comment_item_plain: SafeLoader ParserError (expected <block end>, but found '<scalar>')
  yaml d6a_key_on_plain_level: SafeLoader ScannerError (mapping values are not allowed here)
  yaml d6b_item_after_indented_value: SafeLoader ParserError (expected <block end>, but found '-')
  yaml f5_key_between_dash_and_content: SafeLoader ScannerError (mapping values are not allowed here)
  yaml er1_tools: SafeLoader ParserError (expected <block end>, but found '?')
  yaml ctl_s6_list_at_key_indent: SafeLoader loads {'hooks': {'a': ['x'], 'b': 'c'}, 'tools': 'Read, Write'}
  yaml ctl_nk6_tools_col0_list: SafeLoader loads {'name': 'x', 'tools': ['Read', 'Write']}
  yaml ctl_v19_spec_two_comments: SafeLoader loads {'hr': ['Mark McGwire', 'Sammy Sosa'], 'rbi': ['Sammy Sosa', 'Ken Griffey'], 'tools': 'Read, Write'}
  yaml ctl_s7_nested_dash_levels: SafeLoader loads {'hooks': [['a', 'b']], 'tools': 'Read, Write'}
```
Both runs' PyYAML lines equal I1's `out-isolated.txt` / `out-usersite.txt` line for line, checked with `diff` (no output).

| shape | test (build) | 6.0.1 SafeLoader | 6.0.3 SafeLoader | 6.0.3 CSafeLoader |
|---|---|---|---|---|
| g1 | VALUE(4) | ScannerError (mapping values are not allowed here) | same | ScannerError (… not allowed in this context) |
| g2 | VALUE(4) | ScannerError | same | ScannerError |
| g3 | {Read, Write} | loads `['a b']` | loads | loads |
| g4 | VALUE(4) | ParserError (… found '<block mapping start>') | same | ParserError (did not find expected key) |
| er1 | SEQ_LEVEL(4) | ParserError (… found '?') | same | ParserError (did not find expected '-' indicator) |
| d3 | MAP_ITEM(4) | ParserError (… found '-') | same | ParserError (did not find expected key) |
| k2 | MAP_ITEM(6) | ParserError (… found '-') | same | ParserError (did not find expected key) |
| k4 | {Read, Write} | loads | loads | loads |
| `- "a"` / `  b` | {Read, Write} | ParserError (… found '<scalar>') | same | ParserError (did not find expected key) |
| `- a # c` / `  b` | {Read, Write} | ParserError (… found '<scalar>') | same | ParserError (did not find expected key) |
| `  a:` / `    b: c` / `  - x` (D6 b) | {Read, Write} | ParserError (… found '-') | same | ParserError (did not find expected key) |
| `a:` / `  b` / `  c: d` (D6 a) | {Read, Write} | ScannerError | same | ScannerError |
| `- a` / ` b: c` (F5) | VALUE(4) (BASE: INDENT(4)) | ScannerError | same | ScannerError |
| er1_tools | SEQ_LEVEL(4) (BASE: 075 text) | ParserError (… found '?') | same | ParserError (did not find expected '-' indicator) |
| s6, nk6, v19, s7 (controls) | {Read, Write} | load | load | load |

The table equals 04 Extra research 2. Every D-P prediction holds, so no D-P line is needed and there is no send-back.

Tests 3, build (main checkout, Files 1a-1d): `python3 -m pytest -q tests/test_agent_tools.py`, last line:
```
173 passed in 0.15s
```

Tests 4, after the build. `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<pyc-rcdkdih3> python3 tools/shapes.py /home/claude/fix` imports the built repo module:
```
module: /home/claude/fix/tests/test_agent_tools.py
nc1 `- "a"` / `  b`: tools ['Read', 'Write'] err None
nc2 `- a # c` / `  b`: tools ['Read', 'Write'] err None
d6b `  a:` / `    b: c` / `  - x`: tools ['Read', 'Write'] err None
d6a `a:` / `  b` / `  c: d`: tools ['Read', 'Write'] err None
f5 `- a` / ` b: c`: tools [] err 'colon in unquoted value on frontmatter line 4 (item 104; quote the value)'
er1_tools `tools:` / `  - Read` / `  Bash: x`: tools [] err "non-item line at a list's dash column on frontmatter line 4 (item 111)"
flow item `- [a]` / `  b` (Not checked): tools ['Read', 'Write'] err None
```
The result is {Read, Write} ×4, VALUE(4) and SEQ_LEVEL(4), as 04 expects. The last line is extra information on the docstring's "Not checked" flow-item shape. The probe did not cover it, so no YAML verdict is claimed.

For A1 (04 C2): the test still returns a tool set for 4 files that both PyYAML loaders reject. These are RI-002 tool-set paths, and each is documented under "Known passes of files PyYAML rejects". They are follow-ups, out of scope here (orchestrator cut, 03 D6):
1. `- "a"` / `  b`
2. `- a # c` / `  b`
3. `  a:` / `    b: c` / `  - x`
4. `a:` / `  b` / `  c: d`

Tests 5, mutants. They ran in the `wt` worktree only, one at a time, starting from `build.py`. mut.py asserts both env vars and restores the build file at the end. Env check, as printed:
```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-111-r1-82en7wtf/pyc-rcdkdih3 python3 -c 'import sys; print(sys.dont_write_bytecode, sys.pycache_prefix)'
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-111-r1-82en7wtf/pyc-rcdkdih3
```
Output of `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<pyc-rcdkdih3> python3 tools/mut.py <scratch>`. It runs `python3 -m pytest -q -p no:cacheprovider tests/test_agent_tools.py` in `wt`. "exact" means the list must equal 04. "superset" means it must contain every id of the 106/05 L170-L207 list.
```
BUILD: 173 passed in 0.13s | failed: -
M82: 3 failed, 170 passed in 0.15s | failed: g1_item_scalar_then_key, g2_indented_item_scalar_then_key, g4_quoted_item_then_key | exact: EQUAL
M83: 1 failed, 172 passed in 0.14s | failed: er1_key_at_item_dash | exact: EQUAL
M84: 2 failed, 171 passed in 0.19s | failed: d3_item_after_scalar_key, k2_item_after_reset_key | exact: EQUAL
M85: 2 failed, 171 passed in 0.17s | failed: k2_item_after_reset_key, nk6_tools_col0_list | exact: EQUAL
M86: 2 failed, 171 passed in 0.15s | failed: nk6_tools_col0_list, v19_spec_two_comments | exact: EQUAL
M87: 1 failed, 172 passed in 0.14s | failed: k4_reopened_level_map | exact: EQUAL
M88: 7 failed, 166 passed in 0.23s | failed: g3_item_scalar_continuation, k2_item_after_reset_key, nk12_indented_comment_then_item, nk7_item_after_empty_key, s6_list_at_key_indent, v18_comment_key_then_item, v19_spec_two_comments | exact: EQUAL
M73: 4 failed, 169 passed in 0.17s | failed: s1_map_dedent_between, s2_tools_list_dedent, s4_dedent_off_level, s5_indented_first_line | exact: EQUAL
M74: 1 failed, 172 passed in 0.14s | failed: s7_nested_dash_levels | exact: EQUAL
M75: 3 failed, 170 passed in 0.18s | failed: s1_map_dedent_between, s2_tools_list_dedent, s4_dedent_off_level | exact: EQUAL
M69: 12 failed, 161 passed in 0.26s | failed: tb1_tools_comma_tab, tb2_tools_trailing_tab, tb3_tools_flow_tab, w10_tab_in_empty_key, w13_tab_in_flow_after_quoted_hash, w1_tab_before_hash_colon, w2_tab_before_hash, w3_tab_in_plain, w4_tab_in_continuation, w5_tab_in_item, w6_tab_in_block_header, w9_tab_after_bare_hash | superset: ALL KILLED
M70: 1 failed, 172 passed in 0.18s | failed: w8_tab_in_comment | superset: ALL KILLED
M71: 1 failed, 172 passed in 0.13s | failed: w7_tab_in_quote | superset: ALL KILLED
M72: 1 failed, 172 passed in 0.15s | failed: w9_tab_after_bare_hash | superset: ALL KILLED
M76: 4 failed, 169 passed in 0.17s | failed: c1_tools_continuation_key, c2_tools_item_continuation_key, c3_disallowed_continuation_key, c5_tools_col0_item_continuation | superset: ALL KILLED
M77: 1 failed, 172 passed in 0.14s | failed: c4_flag_cleared_by_key | superset: ALL KILLED
M78: 4 failed, 169 passed in 0.18s | failed: c5_tools_col0_item_continuation, nk6_tools_col0_list, nk9_tools_blank_then_item, v21_tools_comment_then_item | superset: ALL KILLED
M79: 1 failed, 172 passed in 0.14s | failed: f1_tools_item_indents | superset: ALL KILLED
M80: 2 failed, 171 passed in 0.23s | failed: w11_tab_in_block_content, w12_tab_in_comment_line | superset: ALL KILLED
M81: 1 failed, 172 passed in 0.17s | failed: w13_tab_in_flow_after_quoted_hash | superset: ALL KILLED
M56: 12 failed, 161 passed in 0.27s | failed: c4_flag_cleared_by_key, g1_item_scalar_then_key, g2_indented_item_scalar_then_key, g4_quoted_item_then_key, n13_value_colon, v12_block_ends, v1_value_colon, v23_hash_in_word_colon, v26_dash_key_continuation, v2_value_colon_end, v3_nested_value_colon, v6_continuation_colon | superset: ALL KILLED (+ new ['g1_item_scalar_then_key', 'g2_indented_item_scalar_then_key', 'g4_quoted_item_then_key'])
M57: 1 failed, 172 passed in 0.16s | failed: v4_colon_in_comment | superset: ALL KILLED
M58: 6 failed, 167 passed in 0.20s | failed: c4_flag_cleared_by_key, g1_item_scalar_then_key, g2_indented_item_scalar_then_key, g4_quoted_item_then_key, v26_dash_key_continuation, v6_continuation_colon | superset: ALL KILLED (+ new ['g1_item_scalar_then_key', 'g2_indented_item_scalar_then_key', 'g4_quoted_item_then_key'])
M59: 3 failed, 170 passed in 0.17s | failed: v13_key_1025, v15_key_1025_after_key, v16_key_1025_indented | superset: ALL KILLED
M60: 2 failed, 171 passed in 0.16s | failed: v14_key_1024, v17_key_1024_indented | superset: ALL KILLED
M61: 4 failed, 169 passed in 0.18s | failed: v18_comment_key_then_item, v19_spec_two_comments, v20_comment_key_then_map, v21_tools_comment_then_item | superset: ALL KILLED
M62: 4 failed, 169 passed in 0.27s | failed: v10_block_folded_indicators, v12_block_ends, v9_block_literal, w11_tab_in_block_content | superset: ALL KILLED
M63: 1 failed, 172 passed in 0.15s | failed: v22_tools_entry_colon | superset: ALL KILLED
M64: 2 failed, 171 passed in 0.15s | failed: p13_doc_hooks_example, s3_compact_map_in_list | superset: ALL KILLED
M65: 1 failed, 172 passed in 0.19s | failed: v12_block_ends | superset: ALL KILLED
M66: 1 failed, 172 passed in 0.14s | failed: v11_block_header_text | superset: ALL KILLED
M67: 1 failed, 172 passed in 0.15s | failed: v10_block_folded_indicators | superset: ALL KILLED
M68: 1 failed, 172 passed in 0.14s | failed: v17_key_1024_indented | superset: ALL KILLED
X1: 10 failed, 163 passed in 0.24s | failed: n13_value_colon, v11_block_header_text, v12_block_ends, v13_key_1025, v15_key_1025_after_key, v16_key_1025_indented, v1_value_colon, v23_hash_in_word_colon, v2_value_colon_end, v3_nested_value_colon | superset: ALL KILLED
X2: 1 failed, 172 passed in 0.15s | failed: v23_hash_in_word_colon | superset: ALL KILLED
X3: 2 failed, 171 passed in 0.16s | failed: v24_gt_inside_value, v25_bar_inside_value | superset: ALL KILLED
X4: 2 failed, 171 passed in 0.15s | failed: q30_marker_prefix_text, v26_dash_key_continuation | superset: ALL KILLED (+ new ['q30_marker_prefix_text'])
restored build file; mutants not matching: 0
```
After the run:
- `cmp build.py wt/tests/test_agent_tools.py` printed "wt file = build file".
- `cmp build.py /home/claude/fix/tests/test_agent_tools.py` printed "repo file = build file".
- `find wt -name "*.pyc" | wc -l` gave `0`.

Results:
- M82-M88 and M73-M75 each fail exactly their 04 lists.
- M56-M72, M76-M81 and X1-X4 each still fail every id of their 106/05 lists.
- New ids, recorded and not a Deviation (04 Tests 5):
  - M56 and M58 add g1, g2 and g4. These are the new VALUE fixtures, which go through `_plain_colon` and the continuation test.
  - X4 adds q30. Under X4, `ITEMS_RE` reads `---x: z` as three dashes. In-memory check: `X4 q30: (set(), 'list item at the indent of a key with a value on frontmatter line 4 (item 111)')`.

Mutant forms:
- M82-M88 and M73-M75 are the probe111.py `MUTANTS` strings.
- M69-M81 follow 106/03 step 5.
- M56-M68 follow 104/05 L74, and X1-X4 follow 106/05 L207 / 104/04.
- M64 is a forced adaptation. The old block had one `prev = (col, op)`, and the new block has it only in R-A's `else:` branch. M64 changes that `else` line to `prev = (ind, op)`.

Tests 7, Python syntax:
- `python3.11 -m py_compile tests/test_agent_tools.py` (with PYTHONPYCACHEPREFIX in scratch) → exit 0.
- `python3.10` is not installed (`which python3.10` exit 1).
- `grep -nE ":=|^\s*match " tests/test_agent_tools.py` → no hit.

Tests 6, full suite (main checkout, build). `python3 -m pytest -q`, last line as printed:
```
1081 passed, 1 skipped in 148.27s (0:02:28)
```
1081 = B (1073) + 8, which is as expected. `python3 -m pytest -q tests/test_agent_tools.py -k no_shell` gives `1 passed, 172 deselected in 0.02s`, so the real-tree test passes. That check is extra; the `Suite:` line above is the full run.

`python3 scripts/check_pipeline.py` before writing 05 (main checkout): exit 0. Lines read: `111: in progress (FULL: next 05)`, `RULES BRANCH: none`, `I3 FAIL: none`, `A1 FAIL: none`, `INCOMPLETE: none`, `UNTRACKED CHANGE: none`, `STASH: none`, `SKIPPED: none`.

`git diff --stat origin/main...HEAD -- .claude templates scripts/check_pipeline.py scripts/check_handoff.py`: 7 files changed, 55 insertions(+), 22 deletions(-). This is the rule change already on this branch and its unmerged base (PR #39). This item adds no rule change.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: tests/test_agent_tools.py only; no ccbot/realtest.py or TRIGGER file)

## Deviations from plan
None. Every count matched 04:
- BASE: 6 failed, 167 passed, with the 6 named ids.
- Probe table: equal to Extra research 2.
- Build: 173 passed.
- Tests 4: as expected.
- M82-M88 and M73-M75: exact lists. The other mutants still kill every listed id. The new ids are recorded above.
- Full suite: B + 8 = 1081 passed, 1 skipped.

Notes, not deviations:
- Tests 6's base is 1073, not 1069, because 113 landed. 04 states the expectation relative to B.
- M64's form is adapted as described under Tests 5.
- To keep lines at their width, the docstring 1d (a) edit moved "line" to the next line.

Recurring issues checked (logs/recurring-issues.md, read first):
- RI-001: ESCALATED, unchanged. Every filter count was measured: real tree 7 files / no problems; R-A 3, R-B 1, R-C 2 fixtures; 0 of the 165 existing tests changed (173 passed).
- RI-002: GUARDED, unchanged. Near miss closed (D3/er1, from 106): g1/g2/g4 → VALUE, er1 → SEQ_LEVEL, d3/k2 → MAP_ITEM, each pinned by M82/M83/M84. These 4 tool-set paths remain and are documented for A1 as follow-ups: `- "a"` / `  b`; `- a # c` / `  b`; `  a:` / `    b: c` / `  - x`; `a:` / `  b` / `  c: d`.
- RI-004 / RI-005: GUARDED, unchanged. 03/04's kill lists and traces were checked against my own run, and all are equal.
- RI-006: GUARDED, unchanged. Counts come from command output, and the `Suite:` line is copied as printed.
- RI-007: GUARDED, unchanged. Scope FULL; 01-04 exist before this 05.
- RI-008: GUARDED, unchanged. python3.11 py_compile exit 0; no walrus or `match`.
- RI-009: GUARDED, unchanged. Mutants ran only in my own scratch worktree; no `git stash`; 113's files were not touched.
- RI-010: GUARDED, unchanged. The log line is written by `--log` right after this file.
- RI-012: GUARDED, unchanged. Negatives g3 and k4 are pinned by M88 and M87; s6/nk6/v19 are controls.
- RI-014: OPEN, does not apply (no git or clone-depth path).
- RI-015: GUARDED, unchanged. Every probe/mutant command set PYTHONDONTWRITEBYTECODE=1 and a fresh PYTHONPYCACHEPREFIX, and the `True <pyc dir>` lines are pasted above.
- RI-003, RI-011 and RI-013 do not apply.
