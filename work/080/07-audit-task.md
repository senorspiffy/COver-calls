# 07 Audit task - 080
A1, please check:
- check_handoff 080 → PASS, and check_pipeline → 080 awaiting A1.
- tests/test_agent_tools.py is the only code file changed (42b0378: +94 lines). `_field`, `tree_problems`, ENTRY_RE and the allow-list are untouched.
- Re-run your 075 probes a1-n1 (double- and single-quoted multi-line description) and a1-n2 (tab-indented block list) on main after merge. The real-tree test must fail with `unclosed quoted value on frontmatter line 3 (item 080)` / `tab in indentation on frontmatter line 5 (item 080)` (I3: each 1 failed, 58 passed; base 42 passed).
- Re-run a sample of M14-M24 (04 texts; I3's script is /tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3_080/mut.py). M14 must fail p4 (the 075 P2 gap). M15 must fail 11. Use `python3 -B` / `PYTHONDONTWRITEBYTECODE=1`: M22 is a same-size edit.
- D5 follow-up, not in 080: open `[`/`{` on other keys, and whether PyYAML or Claude Code accept `tools:\tRead` (p11 is kept positive; 04 research 3, UNVERIFIED). I3 checked that `tools: ["Read, Bash"]` and `tools: ["Read, Bash]` fail closed via the 075 path. The optional manual probe is `claude plugin validate .claude/agents` (04 research 4).
- Known fail-closed false errors are named in the docstring: a tab at the start of block-scalar content, and a whitespace-only line containing a tab. 0 occurrences today.
- Full suite at 42b0378 (I3, scratch worktree): `1 failed, 589 passed, 1 skipped`. The failure is the known 083 INCOMPLETE (fixed by 084).
