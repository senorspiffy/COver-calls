# 02 Improvements - 072
R2 had no shell in this run (tools: Read, Write, Glob, Grep, WebSearch, WebFetch). Every repo fact below comes from reading files and is cited as path:line. None of it is a measured run. R2 did not run `--log`: the orchestrator writes R2's line, which is option A applied to this item.

## What past logs say
- RI-010 (logs/recurring-issues.md:120): root cause "some step duties ... exist only in the agent text; the template has no field for them and no script checks them". 072 is the reverse case. The duty is in the agent text, and the agent cannot do it. Any fix that only rewords text keeps the RI-010 shape unless a script covers it. Today two scripts already cover the outcome, whoever runs the command: `INCOMPLETE` for a missing or malformed line (043, items from 041 on) and `LOG TIME:` for a late line (045) (recurring-issues.md:121-122).
- Item 045 / RI-010 occurrences (recurring-issues.md:128-129): both failures were lines typed in one batch after the commit (041-044 at 23:10 vs commit 22:24; 048 at 20:40 vs commit 20:20). The rule that matters is "via `--log`, before the step's commit". Who runs it does not matter. `--log` does not record the caller (01 F26).
- logs/audit/2026-11-18-069.md:20-24: A1 checked the orchestrator-run pattern on 069. Every line came from `--log`, `LOG TIME: none`, `INCOMPLETE: none`, and each line was within a minute of its step commit. A1 called it "consistent with the rules' intent but not their wording" and suggested this item. 069 later got `Result: PASS` (L158) with that pattern unchanged.
- logs/research/2026-11-17.md:3-8 and logs/research/2026-11-18.md:3-4: all R1-R3 lines for 069, 070, 072 and 073 are in the `--log` format, and none was typed by hand (01 F20). So option A has now run on 4 items. A1 audited only 069 for LOG TIME. For 070, 072 and 073 a clean LOG TIME is not checked here (R2 has no shell): UNVERIFIED.
- work/069/04-build-plan.md:223 (01 F25): an earlier attempt to fix this inside 069 was DROPPED as out of scope. This item is the first real attempt.
- logs/efficiency/2026-11-18.md:4: 072 is carried in today's run with 071 and 073. 073 overlaps on .claude/commands/run-item.md (01 F31).
- No past log proposes giving R1-R3/I1 Bash. Grep of logs/ for "Bash" (case-sensitive) finds 0 occurrences in 0 files. Option B has never been tried or discussed in logs/.

## 3 ways FOR
1. **Choose option A and write it at the checkpoint run-item.md already has.** run-item.md:14 already makes the orchestrator act between steps ("Before each step, confirm the previous step's file exists"). Put the duty in that sentence, in a fixed order: (i) the step file exists; (ii) after R1 and R3, run `check_handoff.py <ID>`; (iii) run `check_pipeline.py --log <agent> <ID> "<fields>"`, with every count taken from the script output; (iv) then commit. Step (iv) last is what keeps `LOG TIME: none`, because `late_log_lines` compares the line's time with the commit that added it (01 F27). Reasons this fits:
   - It is what already ran on 069/070/072/073, and A1 passed 069 with it (past logs above).
   - It changes no permission and no `tools:` line. The four agents that read untrusted web pages keep no shell (01 F29).
   - It is text only, in 6 places in 5 files (01 Numbers).
   - It closes the "orchestrator must also never hand-type" gap (01 open question 5) in the same sentence: "the orchestrator uses `--log`, never writes to logs/ itself".
   - It keeps I2, I3 and A1 unchanged. They have Bash (01 F14-F16), so i3-verifier.md is not touched and the overlap with 073 stays at run-item.md only (01 F31).
2. **Have each no-shell agent write its non-count log fields in its step file, and leave every count to the script.** Today the orchestrator has to rebuild the fields from the agent's chat report (this task's own instruction: "Report back ... the exact fields for your log line"). A chat report is not in the repo, so nobody can re-check it later. Proposal: each of the four agent files says "Your step has no shell. End your file with `Log fields: <fields>`. The orchestrator runs `--log` with them." Then:
   - R2 writes `3 for / 3 against | languages: <list>`.
   - I1 writes `<verdict> | <n> files planned`.
   - R3 writes only `READY` or `BLOCKED`. Its three counts come from check_handoff's totals line (r3-fact-checker.md:20 "never count by hand", RI-006 recurring-issues.md:79-80).
   - R1 writes nothing. Its only field is the sources count from check_handoff (01 F28).
   This leaves an auditable trail in the step file, and A1 can compare it with the log line. It also keeps RI-006 intact: no hand count reaches a log line. LOG_FORMAT (scripts/check_pipeline.py:207-214) still refuses a malformed field, so a typo in `Log fields:` fails at `--log` (exit 2, nothing written; 01 F26), never silently.
3. **Add the cheap drift test from 01 open question 4, so a future agent file cannot reopen this gap.** The test: for each `.claude/agents/*.md` whose body contains `python3 scripts/`, either the `tools:` line lists `Bash`, or the body names the orchestrator (e.g. the literal "the orchestrator runs"). 7 files today. 3 pass on Bash (i2, i3, a1). The other 4 pass only after this item's rewording (01 F17). This is the RI-010 lesson applied: a text-only duty needs a script check, or it drifts. Here it drifted for at least two days (069, 070) before anyone wrote it down. Pin it with a mutation: put the old r1 L19 wording back, and the test must fail. It is not requested, so I1 decides scope. It is a pure repo read (one Glob, one frontmatter parse), with no git and no network, and it fits tests/test_pipeline_check.py style. Whether a frontmatter parser is already in tests/ is UNVERIFIED (not checked).

## 3 ways AGAINST
1. **R3 loses its self-gate, and a FAIL now costs a loop.** r3-fact-checker.md:20 says check_handoff "must say PASS before you set READY". Under option A, R3 cannot see the output, so READY is written blind. If the orchestrator's run prints FAIL, there are three consequences:
   - (a) The orchestrator must not run `--log ... READY`. A FAIL means no log line yet, and no commit of 03 yet. Otherwise LOG TIME or a wrong READY gets committed.
   - (b) The item goes back to R3 with the pasted output. That counts toward run-item.md:14's 3-loop stop, so a trivial count mismatch can now use up a loop where before R3 fixed it in-step.
   - (c) The R3 regex accepts `READY` followed by anything (`(READY|BLOCKED)\b.*`, scripts/check_pipeline.py:210), so the alternative `READY (pending check_handoff)` (01 open question 2b) would pass the log format. But no script gives "pending" any meaning, and A1 or I1 could read it as READY.
   Recommendation for R3: pick 2(a) from 01. R3 writes READY. The orchestrator runs check_handoff before `--log` and before any commit of 03. On FAIL, the orchestrator sends the item back to R3 with the output and writes no log line. Whether that re-send counts as a loop is R3/I1's call. R2 leans to "yes", so it is never silent.
2. **The duty moves to an actor with no agent file, and to a step that parallel runs make easy to batch.** The orchestrator is the main session following run-item.md. It has no `.claude/agents/` file and no log line of its own, so nothing records that it did the duty except the duty's result. Today 4 items (071-074) run in parallel (logs/efficiency/2026-11-18.md:3-4). That is exactly the setting where one would gather several agents' fields and run `--log` in a burst at the end. That is the 045 failure (recurring-issues.md:128), though done through `--log` and not by hand. LOG TIME only catches a line timed after its commit (01 F27), not a line written late but before a late commit. So "as soon as its file exists" stays text-only for the orchestrator, the RI-010 shape. Mitigation: run-item.md says "per step, not per batch: file, check_handoff, `--log`, commit, then the next step of any item". FOR 2's `Log fields:` line gives A1 something to compare. Also, the R1 line for 072 and the one for 073 both read 23:22 (logs/research/2026-11-18.md:3-4). That suggests the orchestrator already logs parallel items together. That is fine if each line came after its own file. R2 cannot check commit times without a shell: UNVERIFIED.
3. **Option B is the only way that makes the agents self-sufficient, and a scoped form exists. Option A gives that up.** Under A, every R1-R3/I1 step depends on an orchestrator that has a shell. Running an agent on its own (outside /run-item, or in a no-shell harness) leaves no log line until someone notices `INCOMPLETE` at the end. The sub-agents doc gives a narrower B than "full Bash": keep `tools: ... Bash` and add a `PreToolUse` hook on the subagent whose matcher is `Bash`. The hook reads the command and "exits with code 2 to block" anything not allowed, so it could allow only `python3 scripts/check_pipeline.py --log ...` and `python3 scripts/check_handoff.py <ID>`. [https://code.claude.com/docs/en/sub-agents] Costs of that route:
   - It adds a hook script and a settings change. Both are a RULES change, and the hook is new code that needs its own tests.
   - Command-pattern limits on Bash are "fragile" and "not a security boundary" (01 F7, F8, https://code.claude.com/docs/en/permissions).
   - It still hands a shell to the four agents that ingest untrusted web text (01 F29).
   - Settings-level allow/deny rules apply to the whole session, not only the subagent [https://code.claude.com/docs/en/sub-agents], so they cannot scope B to these four agents.
   Weighed against A's single text edit and the items already run under it, the hook route costs more and widens what can run, for no change in what gets logged. This point is against choosing A blindly, not a reason to switch. R3/I1 should record B-with-hook as considered and DROPPED, with these reasons, so the question is not reopened as new.

## Findings by language
Languages: N/A (no new external claims). This is an EFFICIENCY item that rewords this repo's own process files (run-item.md and four agent files), and optionally adds a repo-only test. The fix adds or changes no fee, market rule or statistic. The only outside references are Claude Code docs on subagent tools (R1's F1-F8, plus one hook quote in AGAINST 3). They are tool documentation, not market facts, and the recommended option A depends on none of them.

Random languages this cycle: N/A (last cycle with languages was 069: French, Italian, Dutch, logs/research/2026-11-17.md:6; the next full search should pick 3 others)

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | N/A (no market claim). Docs check only: hook-based Bash allowlist on a subagent, used in AGAINST 3 | https://code.claude.com/docs/en/sub-agents | "exits with code 2 to block write operations"; "A `disallowedTools` entry with a specifier, such as `Bash(git push *)`, still removes the whole tool from the subagent, not only the matching commands." | (English original) |
| Mandarin Chinese | N/A | | | |
| Spanish | N/A | | | |
| Japanese | N/A | | | |
| N/A | | | | |
| N/A | | | | |
| N/A | | | | |

## Holes to watch out for (summary)
- Order matters for `LOG TIME: none`. The sequence is file, then check_handoff (R1/R3), then `--log`, then commit. A commit of the step file before `--log` gives a LOG TIME hit (01 F27).
- R3 FAIL path: the orchestrator writes no READY log line and makes no commit of 03 until check_handoff prints PASS. It sends the item back to R3 with the output. Decide whether that counts as a loop under run-item.md:14 (AGAINST 1).
- Do not add a `READY (pending ...)` state. The log regex accepts it (check_pipeline.py:210), but no script reads "pending" (AGAINST 1c).
- The orchestrator also never writes to logs/ by hand. Say it explicitly in run-item.md (01 open question 5).
- Per step, not per batch, across parallel items. LOG TIME cannot catch a late line before a late commit (AGAINST 2).
- Do not "fix" it by deleting the `tools:` line. That gives all four agents every inherited tool, Bash included (01 F1, F30).
- R1's sources count lives in the log line only, from check_handoff. R3's 03 Self-check gets the pasted output labelled `(run by the orchestrator <date>, exit <n>)`, as on 069/070 (01 F23). Nothing new goes into 01.
- 073 overlap: both items edit run-item.md, 072 at L14 and 073 near L18. Whichever lands second builds on the other's branch (run-item.md:12, item 034). If 072 grows to touch i3-verifier.md, it overlaps 073 there too. It should not need to (01 F15, F31).
- The `.claude/` edits are a RULES change and need the person's OK in PR review. The branch will show as a `RULES BRANCH:` for later items (run-item.md:12, item 049).
- The drift test (FOR 3), if built, must accept both forms: Bash in `tools:`, or a body naming the orchestrator. A mutation restoring the old r1 L19 text must fail it.
