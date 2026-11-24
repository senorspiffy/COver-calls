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
