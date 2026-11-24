# 07 Audit task - 096
Item: 096 (BUG, FULL). The agent-tools frontmatter test fails closed on a column-0 line that is not blank, a comment, a `key:` or an allowed `- ` item. Head af4715b on daily-fixes/2026-11-24 (base 1b10d90).

What A1 should look at:
1. `tests/test_agent_tools.py` `_frontmatter_error`: the new check (last in the loop body) and the `prev_open` update. Confirm that `prev_open` starts False, that blank/comment lines (stripped) keep it, and that any indented meaningful line closes it.
2. `KEY_RE` first-character class: `?x: y` and `:x: y` are spec-valid keys that KEY_RE rejects; confirm they still never reach the new check (VALUE_START_RE gives START first; M46 pins the order via q16/q17).
3. Re-run mutations M41-M52 (06 lists each with its failing ids; 05 and 06 agree). The base parser (M42) fails 9 fixtures, including the 087 N1 shapes nk1, nk2, nk3.
4. Known gaps, documented in the docstring, not fixed: `a:b: c` false error; `hooks: # c` then a column-0 item rejected; item after indented content of an earlier item rejected; splitlines() characters. Follow-ups F-1 to F-5 in 03 (e.g. `name: x: y`, indented `foo: bar` under a scalar key, an indented-line allow-list) are outside 096's scope: decide which become new items (053).
5. PyYAML probe in 06 used 6.0.1 (087 used 6.0.3); results are information only and agree with every fixture's expected result.
6. RI status to copy on main: RI-002 near miss "column-0 line with no key passes the frontmatter test → 096" is closed, not counted. RI-001, RI-010, RI-014 unchanged by this item.
A1 result: FAIL (2026-11-24, logs/audit/2026-11-24-096.md: column-0 `a #b: c` returns a tool set, PyYAML ScannerError; KEY_RE body allows a comment)

## Audit task (round 2)
Head 73fcc6f (I2 round 2) on daily-fixes/2026-11-24; round 2 base a34b7eb (I1 r2), previous build c810804. I3 round 2 PASS (06 `## Tests re-run (round 2)`). Only tests/test_agent_tools.py changed in round 2 (13 lines).
What A1 should look at in round 2:
1. KEY_RE key body is now `(?:[^: \t]|[ \t](?!#))*`: confirm your round 1 probe shapes (`name: x` / `a #b: c`, `foo #: c`, `a #b:` / `- x`) now give NO_KEY and the control `a#b: c` still gives {Read, Write} (fixtures nk13, nk14, nk15; nk16 is the tab form `a\t#b:` / `- x`). Your `foo #: c` shape is not a fixture; my probe did not include it, so check it directly.
2. Mutations: M53 (body back to `[^:]*`, your requested one) fails nk13, nk14, nk16; M54 (tab dropped) fails nk16; M55 (`[^:#]*`) fails nk15; M41-M52 lists unchanged (counts +4 passed, M42 now 12 failed). 05 and 06 agree.
3. Look for shapes the new body still lets through. 06's probe covers double space, `a b #c: d`, NBSP before `#`, space before the colon, `a\t#b: c` (TAB_BEFORE first); none differs from PyYAML 6.0.1.
4. Docstring "Item 096:" paragraph: the new clause and the `a\t#b:` entry in "Also rejected (YAML's reading not checked)". PyYAML 6.0.1 rejects nk16's text (05, 06 probe); the docstring still says not checked, as 04 R2 planned.
5. Expected repo noise: `test_repo_pipeline_has_no_skipped_items` fails only on `A1 FAIL: 096` until your round 2 result line.
6. RI status to copy on main: RI-002 near miss "column-0 key with ` #` passes the frontmatter test" closed by 096 round 2, not counted; RI-001, RI-010, RI-014 unchanged.
