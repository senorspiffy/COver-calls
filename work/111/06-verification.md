# 06 Verification - 111
Verdict: PASS (round 1; earlier rounds: none)
Sent back to: none
Scratch dir: /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-111-r1-3rfqodn9

Inside my scratch dir, made by me for this round (mkdtemp, prefix `i3-111-r1-`):
- `pyc-74ckelcx`: the pyc dir (mkdtemp, prefix `pyc-`). Every suite, probe and mutant command set both env vars on itself.
- `wt`: `git worktree add --detach` at 7b11624 (I2's commit). Every run below was made there, never in the main checkout.
- `tools/yprobe.py` (my own PyYAML probe; it imports the built module and does not reuse I1's or I2's script), `tools/mut.py` (my mutant runner), `tools/surv.py` (survivor shapes).
- Outputs: `full-suite.txt`, `y-usersite.txt`, `y-isolated.txt`, `mut-out.txt`, `surv-out.txt`.

The main checkout ran only `check_handoff.py` and `check_pipeline.py`, which are read-only except for `--log`. No `git stash`. After the mutants, `git -C wt status --porcelain` gave 0 lines, and `find wt -name '*.pyc'` gave 0.

## I1 audit (plan vs research)
- 04 follows 03 (Status READY, check_handoff PASS, re-run below). The 04 Rule trace has a row for each 03 map step 1-6, for D1-D4, D-P, D6, the cuts and the prevention guardrail. I checked every row against 03.
- 04 makes three changes to 03, and each one has a source:
  - C1 (run the probe twice, `-I` and user-site): sourced by the Python docs quote (Extra research 3) and by 106/05 (libyaml is only in the user site). I measured it: `-I` gives PyYAML 6.0.1 with `__with_libyaml__` False, and the user site gives 6.0.3 with True.
  - C2 (03's last "Not checked" sentence becomes "Known passes of files PyYAML rejects"): sourced by I1's measured probe table. My probe gives the same verdicts on all four shapes (both loaders raise; table below). The flow shape stays "Not checked", which is what 03 said.
  - C3 (full fixture ids): a naming change only. 03 step 1 says "the ids may be renamed".
- No unsourced addition. The expected suite total is base-relative (B + 8) because 112/113 share the checkout. 03 step 6 itself says "if the base is unchanged".
- 001 rule text: not affected. The change is to tests/ only and changes no person rule, so no rule-text change or request is needed.
- Simulator/replay rule (item 062): not applicable. There is no picker and no replay.

## I2 audit (build vs plan)
I compared the build with 04, line by line, in my worktree at 7b11624 (`git diff 3794ef2 7b11624`). The only code file is `tests/test_agent_tools.py`, 66 lines (+55/-11). The other files in the commit are 05 and its log line.
- 1a: `SEQ_LEVEL` and `MAP_ITEM` sit right after `INDENT`. The text equals 04 Files 1a character for character.
- 1b: the 8 CASES have the 04 ids, and their inputs and expectations equal 03 step 1, checked one by one in the diff.
- 1c: the function docstring says "(… 106, 111)", and `kind = {}` / `last_open = {}` follow `in_flow = False`. I cut 03's "Step 3 code" block out of 03 and looked for it in the file: `step3 code found verbatim in file: True 1`. The continuation branch, `_node`, `_field`, the 096 check and the tab/quote/flow checks are not in the diff.
- 1d: checked on the flattened module docstring.
  - (a) `6.0.1, 6.0.3 and 6.0.4` is present.
  - (b) The old "an indented `- ` item after a scalar-valued …" sentence is gone.
  - (c) 03's step 4 text up to "…with such a file." is present, followed by 04's C2 sentence word for word (both `True`).
  - No line of the docstring has an odd number of backticks, so no backtick span is split across lines.
- Connectivity, re-done:
  - The two constants are returned by `_frontmatter_error`, and the er1/d3/k2 CASES expect them.
  - The 8 CASES run through `test_agent_tools_parser`, which is parametrized over CASES (173 = 165 + 8).
  - The real tree goes through `tree_problems` (`test_no_shell_agents_leave_commands_to_orchestrator` passes in the full suite).
  - `kind[ind]` and `last_open[ind]` are read only when `landed` is true, with `[]`. My 15 mutant/BASE runs and 21 probe shapes raised nothing.
- 05's grep reasons, re-run:
  - The missing-data grep over ccbot/ gives `38`, and `git diff --stat 3794ef2 7b11624 -- ccbot/ config/ scripts/` is empty, so all 38 are pre-existing.
  - The added lines have no `.get(` or `setdefault` (grep exit 1) and no TODO (grep exit 1).
- Edges of the input (the data-hole rule, applied to frontmatter lines):
  - First line: no `prev`. Pinned by s5/nk11, which are unchanged and pass.
  - Item on the last frontmatter line (`tools: Read, Write` / `hooks:` / `- a`): the build gives tools, and both loaders load.
  - First item at column 0 after a key (`a:` / `- x`): the build gives tools, and both loaders load.
- RI-012 (text-matching classifier): the change classifies no error or reply by matching text. The new checks compare columns and the `kind` value. The negatives g3 and k4 (pinned by M88/M87) and the controls s6, nk6 and v19 are fixtures that contain the shape without the fault.
- 05's mutant forms for M82-M88 and M73-M75 equal 04/03 step 5. I re-ran them myself (below). M56-M72, M76-M81 and X1-X4 I did not re-run, so 05's run is the only evidence for them.

## Tests re-run (output)
All runs were made in `wt` at 7b11624. Env check, as printed:
```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-111-r1-3rfqodn9/pyc-74ckelcx python3 -c 'import sys; print(sys.dont_write_bytecode, sys.pycache_prefix)'
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-111-r1-3rfqodn9/pyc-74ckelcx
```
Full suite: `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<pyc-74ckelcx> python3 -m pytest -q -p no:cacheprovider`, last line:
```
1081 passed, 1 skipped in 213.41s (0:03:33)
```
This equals 05 (1081 passed, 1 skipped; B 1073 + 8). The 1 skip was also in 05's base run.

Python ≥ 3.10:
- `tests/test_safety.py::test_every_py_compiles_on_oldest_python` → `1 passed`. It ran and was not skipped: python3.11 is on PATH, python3.10 is not.
- `python3.11 -m py_compile tests/test_agent_tools.py` → exit 0.
- The grep for walrus/`match` gives no hit.

check_handoff (`python3 scripts/check_handoff.py 111`, main checkout, exit 0):
```
sources count (unique URLs in 01-research.md): 6
fact-check rows: 84
totals line: 84 rows -> 69 as-is, 11 fixed, 4 removed
PASS
```

Mutants and BASE (`tools/mut.py`; `pytest -q -p no:cacheprovider tests/test_agent_tools.py`; the build file was restored at the end). The runner asserts both env vars before it starts.
```
BUILD: 173 passed in 0.17s
BASE(old parser, 1a-1b kept): 6 failed, 167 passed in 0.22s | failed: d3_item_after_scalar_key, er1_key_at_item_dash, g1_item_scalar_then_key, g2_indented_item_scalar_then_key, g4_quoted_item_then_key, k2_item_after_reset_key | exact: EQUAL
M82: 3 failed, 170 passed in 0.21s | failed: g1_item_scalar_then_key, g2_indented_item_scalar_then_key, g4_quoted_item_then_key | exact: EQUAL
M83: 1 failed, 172 passed in 0.14s | failed: er1_key_at_item_dash | exact: EQUAL
M84: 2 failed, 171 passed in 0.15s | failed: d3_item_after_scalar_key, k2_item_after_reset_key | exact: EQUAL
M85: 2 failed, 171 passed in 0.16s | failed: k2_item_after_reset_key, nk6_tools_col0_list | exact: EQUAL
M86: 2 failed, 171 passed in 0.19s | failed: nk6_tools_col0_list, v19_spec_two_comments | exact: EQUAL
M87: 1 failed, 172 passed in 0.17s | failed: k4_reopened_level_map | exact: EQUAL
M88: 7 failed, 166 passed in 0.22s | failed: g3_item_scalar_continuation, k2_item_after_reset_key, nk12_indented_comment_then_item, nk7_item_after_empty_key, s6_list_at_key_indent, v18_comment_key_then_item, v19_spec_two_comments | exact: EQUAL
M73: 4 failed, 169 passed in 0.19s | failed: s1_map_dedent_between, s2_tools_list_dedent, s4_dedent_off_level, s5_indented_first_line | exact: EQUAL
M74: 1 failed, 172 passed in 0.13s | failed: s7_nested_dash_levels | exact: EQUAL
M75: 3 failed, 170 passed in 0.16s | failed: s1_map_dedent_between, s2_tools_list_dedent, s4_dedent_off_level | exact: EQUAL
I3a R-A drops `not is_key`: 2 failed, 171 passed in 0.16s | failed: p13_doc_hooks_example, s3_compact_map_in_list | killed
I3b R-A drops `not sb`: 173 passed in 0.12s | failed: - | SURVIVED
I3c R-A uses dash[0]: 173 passed in 0.13s | failed: - | SURVIVED
I3d R-C drops `not last_open`: 13 failed, 160 passed in 0.28s | failed: c5_tools_col0_item_continuation, g1_item_scalar_then_key, g3_item_scalar_continuation, g4_quoted_item_then_key, k2_item_after_reset_key, nk12_indented_comment_then_item, nk6_tools_col0_list, nk7_item_after_empty_key, nk9_tools_blank_then_item, s6_list_at_key_indent, v18_comment_key_then_item, v19_spec_two_comments, v21_tools_comment_then_item | killed
I3e kind map ignores is_key: 173 passed in 0.15s | failed: - | SURVIVED
restored; not matching: 3
```
- BASE and every planned mutant (M82-M88, M73-M75) fail exactly the 04 list.
- I3a-I3e are my own extra mutants. They have no planned list. The 3 counted as "not matching" are the survivors I3b, I3c and I3e, analysed below.

Survivor shapes (`tools/surv.py`: the build, the mutant, and PyYAML 6.0.3 SafeLoader/CSafeLoader on the same frontmatter):
```
I3b 'hooks:' / '- |' / '  x' / ' b': build err indent matches no open level on frontmat | mutant tools | Safe ParserError, CSafe ParserError
I3b 'hooks:' / '- |' / '  x' / ' b: c': build err indent matches no open level on frontmat | mutant err colon in unquoted value on frontmatter l | Safe ParserError, CSafe ParserError
I3b 'hooks:' / '  - |' / '    x' / '   b': build err indent matches no open level on frontmat | mutant tools | Safe ParserError, CSafe ParserError
I3c 'hooks:' / '- - a' / '  b': build err non-item line at a list's dash column on | mutant tools | Safe ScannerError, CSafe ScannerError
I3c 'hooks:' / '- - a' / ' b': build err indent matches no open level on frontmat | mutant tools | Safe ParserError, CSafe ParserError
I3c 'hooks:' / '- - a' / '  b: c': build err non-item line at a list's dash column on | mutant err colon in unquoted value on frontmatter l | Safe ParserError, CSafe ParserError
I3c 'hooks:' / '- - a' / '   b': build tools | mutant tools | Safe loads, CSafe loads
I3e 'a:' / '  b' / '  - x': build tools | mutant err list item at the indent of a key with a  | Safe loads, CSafe loads
I3e 'hooks:' / '- a' / '- b': build tools | mutant tools | Safe loads, CSafe loads
I3e 'hooks:' / '  b' / '  - x': build tools | mutant err list item at the indent of a key with a  | Safe loads, CSafe loads
I3e 'a:' / '  - x' / '  b' / '  - y': build err non-item line at a list's dash column on | mutant err non-item line at a list's dash column on | Safe ScannerError, CSafe ScannerError
```
(An earlier run of surv.py cut the frontmatter at the last line instead of at the closing `---`, so its ComposerError cells were not real. I fixed the cut and ran it again. The run above is the corrected one.)
- **I3b and I3c survive, and the build is right on their shapes.** The build fails closed (INDENT or SEQ_LEVEL) on files both loaders reject. Each mutant turns that into a tool set, which is the RI-002 direction. No fixture pins R-A's `not sb` or its `dash[-1]` choice.
  - This does not fail this round: 03/04 planned one mutant per new check (M82-M84), and each kills its named fixtures.
  - Sent to A1 as a follow-up candidate (07 point 1). Two fixtures would pin them: `- |` / `  x` / ` b` → INDENT(5), and `- - a` / `  b` → SEQ_LEVEL(4).
- **I3e survives in the other direction.** Its shapes load: `  - x` after the plain `  b` folds into the scalar "b - x". The build passes them, which is correct. The mutant would add fail-closed false errors. This is a missing negative, not a tool-set path (07 point 2).

PyYAML probe (`tools/yprobe.py`, my own script). It imports the built module from `wt` and runs each new fixture, the controls, 04's info shapes and 3 edge shapes I added.
- (ii) `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<pyc-74ckelcx> python3 tools/yprobe.py <wt> usersite`, exit 0:
```
python 3.13.18 | label usersite | module /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-111-r1-3rfqodn9/wt/tests/test_agent_tools.py
PyYAML 6.0.3 | __with_libyaml__ True | /root/.local/lib/python3.13/site-packages/yaml/__init__.py
g1_item_scalar_then_key: test -> err colon in unquoted value on frontmatter line 4 (item 104; quote the value) | Safe ScannerError | CSafe ScannerError
g2_indented_item_scalar_then_key: test -> err colon in unquoted value on frontmatter line 4 (item 104; quote the value) | Safe ScannerError | CSafe ScannerError
g3_item_scalar_continuation: test -> tools Read,Write | Safe loads | CSafe loads
g4_quoted_item_then_key: test -> err colon in unquoted value on frontmatter line 4 (item 104; quote the value) | Safe ParserError | CSafe ParserError
er1_key_at_item_dash: test -> err non-item line at a list's dash column on frontmatter line 4 (item 111) | Safe ParserError | CSafe ParserError
d3_item_after_scalar_key: test -> err list item at the indent of a key with a value on frontmatter line 4 (item 111) | Safe ParserError | CSafe ParserError
k2_item_after_reset_key: test -> err list item at the indent of a key with a value on frontmatter line 6 (item 111) | Safe ParserError | CSafe ParserError
k4_reopened_level_map: test -> tools Read,Write | Safe loads | CSafe loads
s6_list_at_key_indent: test -> tools Read,Write | Safe loads | CSafe loads
nk6_tools_col0_list: test -> tools Read,Write | Safe loads | CSafe loads
v19_spec_two_comments: test -> tools Read,Write | Safe loads | CSafe loads
s7_nested_dash_levels: test -> tools Read,Write | Safe loads | CSafe loads
nc1 `- "a"`/`  b`: test -> tools Read,Write | Safe ParserError | CSafe ParserError
nc2 `- a # c`/`  b`: test -> tools Read,Write | Safe ParserError | CSafe ParserError
d6b `  a:`/`    b: c`/`  - x`: test -> tools Read,Write | Safe ParserError | CSafe ParserError
d6a `a:`/`  b`/`  c: d`: test -> tools Read,Write | Safe ScannerError | CSafe ScannerError
f5 `- a`/` b: c`: test -> err colon in unquoted value on frontmatter line 4 (item 104; quote the value) | Safe ScannerError | CSafe ScannerError
er1_tools: test -> err non-item line at a list's dash column on frontmatter line 4 (item 111) | Safe ParserError | CSafe ParserError
flow `- [a]`/`  b`: test -> tools Read,Write | Safe ParserError | CSafe ParserError
edge: item last line `hooks:`/`- a`: test -> tools Read,Write | Safe loads | CSafe loads
edge: R-C first item after key `a:`/`- x`: test -> tools Read,Write | Safe loads | CSafe loads
```
- (i) `python3 -I -B -X pycache_prefix=<pyc-74ckelcx>/iso tools/yprobe.py <wt> isolated`, exit 0:
  - It prints `PyYAML 6.0.1 | __with_libyaml__ False | /usr/lib/python3/dist-packages/yaml/__init__.py` and `CSafeLoader: not measured (CSafeLoader absent, 6.0.1)`.
  - Every "test ->" result and every SafeLoader verdict equals run (ii), line for line.
- The build result and the loader verdicts equal 05's table and 04 Extra research 2 on every shared shape. There is no D-P case.
- Extra fact for A1: the docstring's remaining "Not checked (YAML's reading not checked)" shape, a no-colon line after a flow scalar item (`- [a]` / `  b`), is also rejected by both loaders, and the build passes it. This is a fifth tool-set path of the same class as 04's C2 four, and it is outside this item's scope (07 point 3).

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 3794ef2 7b11624`: logs/implementation/2026-11-27.md, tests/test_agent_tools.py, work/111/05-build-report.md; no TRIGGER file, nothing under data/real/)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-014, RI-002, RI-012, RI-015, RI-008, RI-006, RI-009, RI-010
- RI-001 (ESCALATED): I re-ran every feasibility number and each matches 03/04's cited number.
  - Real tree: 7 files, 21 frontmatter lines, 0 item lines and 0 indented lines (awk/grep), so R-A/R-B/R-C select 0 real lines.
  - Fixtures: R-A 3 (M82), R-B 1 (M83), R-C 2 (M84).
  - Existing tests: 0 of 165 change (BASE 6 failed = only the 6 new ids; BUILD 173 passed).
- RI-014 (OPEN): does not apply. The change has no git or clone-depth path. `git rev-parse --is-shallow-repository` → false.
- RI-002 (GUARDED, this item's root cause, near miss): the fix and its guardrail are both in place.
  - Would the guardrail have caught the original error? Yes: with the old parser put back (BASE), g1/g2/g4/er1/d3/k2 fail.
  - RI-002 probe: this item removes no default, so the probe is the old block put back, in the scratch worktree only. 6 tests fail, then the file was restored.
  - Residual tool-set paths, all documented or sent to A1:
    - 04 C2's four, in the docstring.
    - The flow shape, also measured rejected (07 point 3).
    - The survivors I3b and I3c, which are fail-closed today but not pinned (07 point 1).
- RI-012 (GUARDED): no text-matching classifier was added. The negatives are present (g3, k4, s6, nk6, v19) and pinned by M87/M88.
- RI-015 (GUARDED): every probe, mutant and suite command set PYTHONDONTWRITEBYTECODE=1 and PYTHONPYCACHEPREFIX=`pyc-74ckelcx`. The `True <pyc dir>` line is pasted above, `wt` has 0 `.pyc` files, and the mutant runner asserts both vars.
- RI-008 (GUARDED): python3.11 compile passes and the oldest-Python test passed. python3.10 is not on PATH.
- RI-006 (GUARDED): every count is copied from command output.
- RI-009 (GUARDED): my own mkdtemp dir and detached worktree. No stash. I touched only 111's files.
- RI-010 (GUARDED): the log line is written with `--log` right after this file.
- RI-003, RI-004/005 (03 traces confirmed by run), RI-007 (Scope FULL, 01-05 present), RI-011 and RI-013: do not apply, or unchanged.

## Pipeline line (step 2)
check_pipeline line: `111: awaiting A1 (FULL)` (run after 06, 07 and the `--log` line `00:10 | I3 | 111 | PASS | sent to audit: yes` were written; exit 0, STASH none, UNTRACKED CHANGE none, SKIPPED none, INCOMPLETE none)

## Sent back / sent to Audit
Sent to Audit: yes. The audit task is in work/111/07-audit-task.md.
