# 07 Audit task - 106
Item: agent-tools frontmatter test fails closed on 104's three open shapes (tab before `#`, sibling indent, continuation under `tools:`). Test-only change in tests/test_agent_tools.py (build de08401). I3 PASS round 1.

What Audit should look at:
1. The tab check `"\t" in line[:keep] + line[cut:].split(" #", 1)[0]`. Can a tab outside the quote, flow span or ` #` comment still reach a tool set? Try shapes on FLOW_KEYS lines, `- ` items with quoted values, and a second quoted span later in a plain value. I3's x1-x8 probes found none (06).
2. The indent stack. Check the equal-level replace (my mutant E3 survives and I3 calls it equivalent: duplicate `ind` only), and the dash-level push for `- - a` (s7, M74). Find a valid YAML shape that now gives a false INDENT, other than the documented ones.
3. `_ends_field` is now shared by `_field` and `in_flow`. Check that a column-0 `- ` item after a non-tools key (v18/nk7 shapes) cannot leave `in_flow` set across a later key's continuation.
4. Docstring "Not checked": D3 (`  a: v` / `  - x`) and 04 Extra research 1 (`  - x` / `  a: v`). Both pass the test, and PyYAML raises on the second (05 er1). Decide whether a follow-up item is needed. On `tools:`, `_field` refuses both.
5. Re-run a sample of M69-M81 on a scratch worktree of main once merged (GUARDED probe for RI-002's near miss).
6. The docstring says "measured on PyYAML 6.0.1 and 6.0.4". 05 and 06 measured 6.0.1 (pure) and 6.0.3 (libyaml). 6.0.4 comes from 104/06. Confirm that the wording is acceptable.
