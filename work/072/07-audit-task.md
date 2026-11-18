# 07 Audit task - 072
I3 verdict: PASS (round 1), build commit bb5a32e. Type EFFICIENCY, Scope FULL, RULES BRANCH (.claude/, templates/): the person must approve the PR.

## What Audit should look at
1. **Does the rule text say one way?** Read the new run-item.md paragraph "Log lines and check_handoff (item 072)" and the four reworded lines: r1 (the "No shell" line), r2 (the "No shell" line), r3 (step 7 and the "The orchestrator then runs" line) and i1 (the "No shell" line). Check that:
   - no no-shell agent is still told to run a command;
   - the file → check_handoff → `--log` → commit order is clear;
   - D2 is stated: on a FAIL, no log line, no commit of 03, and one loop on R3;
   - D4 is stated: the orchestrator never writes to logs/ and never edits a refused line.
2. **Template and run-item agree.** The label `check_handoff output (run by the orchestrator <YYYY-MM-DD> <HH:MM> UTC, exit <n>; must say PASS):` is identical in both. Accepting it is I2 deviation 1. Check that check_handoff still finds `## Self-check` in a 03 built from the new template.
3. **Drift test strength (tests/test_agent_tools.py).** I3 probes:
   - x2: a line in a no-Bash file saying "you run `python3 scripts/...` (not the orchestrator)" passes the test, because the rule is a substring check.
   - x1: a YAML flow list `tools: [Read, ..., Bash]` is not parsed. Bash is missed, which fails loud.

   Decide whether either needs a follow-up item: for x2, a stricter rule such as requiring "the orchestrator runs" or "orchestrator copies"; for x1, flow-list support. Weigh both against RI-012, which I3 judged not applicable because this is not an error or reply classifier.
4. **Mutations.** Re-run m1-m5 (each must fail) and m6 (must pass) on a scratch worktree of the merged code. 06 has the exact commands' outputs. A good GUARDED probe for RI-010 is m1, which restores the old r1 line.
5. **LOG TIME for 071-074.** I3 checked all 17 lines up to 516c497, and none was late. Re-check the lines added after that (071 I2/I3, 073 I3, 074 I2/I3, 072 I3) once they are committed. 072's own I3 line is written by `--log` right after this file.
6. **I2 log field `tests 411/411`.** The suite reports 411 passed and 1 skipped (exchange_calendars). Check whether `<total>` should count skips, and how 069/070 counted.
7. **Counts in 05.** Base 404 passed, 1 skipped at bb5a32e~1, and 411 passed, 1 skipped at bb5a32e. I3 reproduced both. The full suite after 071, 073 and 074 land is a new base, so check that test_agent_tools still passes on the final branch head.
8. **README line** for check_handoff.py: does it match the run-item actor list (the orchestrator after R1 and R3; I3; A1)?
A1 result: PASS (2026-11-18, logs/audit/2026-11-18-072.md; suite 414 passed 1 skipped at e54a77e, m1-m5 fail/m6 passes; follow-ups P1 drift-test flow-list hole, P2 I2 log total)
