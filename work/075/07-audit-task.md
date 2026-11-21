# 07 Audit task - 075
Build commit: f47deb5 (tests/test_agent_tools.py only). I3: PASS round 1 (06).

What Audit should look at:
1. Re-run A1's own x4 and x5 probes on r1 (the request's "Done looks like") on a scratch worktree of the branch head: both must fail `test_no_shell_agents_leave_commands_to_orchestrator` with the allow-list problem naming `Bash`. On base f8981bd both pass (I3 re-ran this).
2. Try new shapes that might still read Bash on a no-shell agent as "not Bash" (the RI-002 near miss this item fixes): e.g. YAML anchors/aliases, `tools: !!str ...`, a tab-indented block list, a key in quotes (`"tools": ...`), an indented top-level mapping, Windows line endings. I3 reasons each fails closed (an error or the 072 no-tools text) but did not probe all of them.
3. M14 (I3's own mutation): making `_is_item` drop the bare `-` form leaves all 42 tests green. The outcome stays an error (only the message changes), but no fixture pins 03 D1(2)'s bare-`-` empty-entry text. Decide whether this needs a fixture (small EFFICIENCY item) or is fine as is.
4. The body-line rule (`"orchestrator" not in line`) is still a substring check, unchanged from 072 (03 D5 dropped the stricter wording rule as optional). Confirm that is acceptable or open an item.
5. RI-002 entry: 05 states the GUARDED condition "when merged and the x4 probe (r1 `tools: [..., Bash]`) fails the real-tree test on main". Carry it to logs/recurring-issues.md once PR is merged.
6. Later items 076, 077, 079 change scripts/check_pipeline.py on top of this commit; 075's only file is tests/test_agent_tools.py, so check no later build edits it.
7. Re-run the whole suite (I3: 488 passed, 1 skipped; skip = exchange_calendars not installed) and `python3.11 -m py_compile tests/test_agent_tools.py`.
A1 result: PASS (2026-11-20, logs/audit/2026-11-19-075.md; worktree f3521ff: 42 passed, suite 488 passed 1 skipped, x4/x5 fail on head and pass on base; follow-ups P1 quoted-scalar/tab frontmatter hole, P2 bare-dash fixture)
