# 01 Research brief - 072

Type EFFICIENCY, Scope FULL, opened by A1, 2026-11-18. Branch daily-fixes/2026-11-18 (read only; R1 ran no git). R1 has no shell in this run either (tools: Read, Write, Glob, Grep, WebSearch, WebFetch), so every repo fact below comes from reading the files, cited as path:line. None of it is a measured run.

## Question
R1, R2, R3 and I1 have no shell, but run-item.md and their agent files tell them to run `scripts/check_pipeline.py --log` (all four) and `scripts/check_handoff.py` (R1, R3). Which one documented way should the pipeline use? (A) The orchestrator runs the commands right after the step file exists and pastes their output. (B) The four agents get Bash. The rule must keep "never type a log line by hand" (item 045) and `LOG TIME: none`.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### How the `tools:` frontmatter limits a subagent (official docs)
F1. The `tools` field lists the "Tools the subagent can use, as a comma-separated string such as `Read, Grep, Bash` or a YAML list". It "Inherits every tool available to subagents if omitted." [https://code.claude.com/docs/en/sub-agents]
F2. "To restrict tools, use the `tools` field as an allowlist or the `disallowedTools` field as a denylist. If both are set, `disallowedTools` is applied first, then `tools` is resolved against the remaining pool." [https://code.claude.com/docs/en/sub-agents]
F3. Bash is its own tool name in the `tools` list. The docs' examples include `tools: Read, Grep, Glob, Bash`. A subagent whose list leaves out Bash has no shell. [https://code.claude.com/docs/en/sub-agents]
F4. "A `disallowedTools` entry with a specifier, such as `Bash(git push *)`, still removes the whole tool from the subagent ... To keep Bash and block specific commands, add a Bash deny rule ... to `permissions.deny` in your settings. The rule applies to the main conversation and to subagents." [https://code.claude.com/docs/en/sub-agents]
F5. The frontmatter is not the way to limit Bash to a single command. Per-command control comes from permission rules in settings, which apply to the whole session as well as to subagents (F4). [https://code.claude.com/docs/en/sub-agents]
F6. Permission rules are "evaluated in order: deny, then ask, then allow". [https://code.claude.com/docs/en/permissions]
F7. "Bash permission patterns that try to constrain command arguments are fragile." [https://code.claude.com/docs/en/permissions]
F8. A Bash deny or ask rule "covers the invocation Claude usually produces and isn't a security boundary around the program." [https://code.claude.com/docs/en/permissions]
F9. Observation from this session: the tool set R1 was given is exactly the `tools:` line of .claude/agents/r1-researcher.md L4 (Read, Write, Glob, Grep, WebSearch, WebFetch, plus the hand-back tool), with no Bash. This matches F1/F3. It is one session's observation, not a doc claim.

### Each agent's `tools:` line compared with what its text tells it to run (repo)
F10. r1-researcher.md L4: `tools: Read, Write, Glob, Grep, WebSearch, WebFetch` (no Bash). L19 tells it to run `python3 scripts/check_pipeline.py --log R1 ...` and to take the sources count from `python3 scripts/check_handoff.py <ID>`. MISMATCH (2 commands).
F11. r2-improver.md L4: same list, no Bash. L22 tells it to run `check_pipeline.py --log R2 ...`. MISMATCH (1 command).
F12. r3-fact-checker.md L4: same list, no Bash. L20 (step 7) says "Run `python3 scripts/check_handoff.py <ID>` and paste its output into the Self-check section. It must say PASS before you set READY." L24 tells it to run `check_pipeline.py --log R3 ...`. MISMATCH (2 commands). Step 7 also gates READY on the output.
F13. i1-reviewer.md L4: same list, no Bash. L18 tells it to run `check_pipeline.py --log I1 ...`. MISMATCH (1 command).
F14. i2-builder.md L4: `tools: Read, Write, Edit, Glob, Grep, Bash`. L18/L20/L21/L25 tell it to run grep, tests, git status and `--log`. Match.
F15. i3-verifier.md L4: `tools: Read, Write, Glob, Grep, Bash`. L13 tells it to run check_handoff, check_pipeline and the tests; L18 `--log`. Match.
F16. a1-auditor.md L4: `tools: Read, Write, Glob, Grep, Bash`. L17/L21/L22/L29 tell it to run git, check_handoff --all, check_pipeline and --next-id. Match. A1 writes no `--log` line; its result goes in 07 (L12).
F17. Count: 7 agent files. 4 have no Bash (R1, R2, R3, I1) and their text names 6 commands per FULL item. 3 have Bash (I2, I3, A1) and their text matches their tools.

### run-item.md wording (repo)
F18. .claude/commands/run-item.md L14: "each step's agent writes its log line with `check_pipeline.py --log` as soon as its file exists, never in a batch at the end, item 045". Nothing in run-item.md names the orchestrator, or says who runs check_handoff for R1/R3.
F19. run-item.md L14 already gives the orchestrator a per-step duty: "Before each step, confirm the previous step's file exists in work/$ARGUMENTS/." That is the natural point to run the two commands.

### What actually happened in 069/070 (repo logs)
F20. logs/research/2026-11-17.md L3-L8: six R1/R2/R3 lines for 069 and 070, all in the `--log` format.
F21. logs/implementation/2026-11-18.md L5: `00:12 | I1 | 069 | FIT WITH CHANGES | 2 files planned`, in the I1 format.
F22. work/069/01-research.md L70 (R1's open question 6): "R1's tool set has no shell, so `python3 scripts/check_handoff.py 069` and `python3 scripts/check_pipeline.py --log R1 069 ...` could not be run ... the orchestrator must run the `--log` command."
F23. work/069/03-handoff.md L130 and work/070/03-handoff.md L159: check_handoff output pasted into the Self-check, labelled "(run by the orchestrator 2026-11-17, exit 0)". work/070/03-handoff.md L12: "The orchestrator's check_handoff run is the authority for the log line."
F24. logs/audit/2026-11-18-069.md L20-L24 (A1): every 069 line was written by `check_pipeline.py --log`, with `LOG TIME: none`, `INCOMPLETE: none`, and each line timed within a minute of its step commit (R1 23:21 vs commit 23:21:53; R3 23:32 vs 23:32:26). "Consistent with the rules' intent but not their wording." A1 proposes the run-item.md wording and a note in the step file.
F25. work/069/04-build-plan.md L223: the suggestion was DROPPED from 069 and left to the daily review, which opened it as this item.

### What `--log` does and does not check (repo)
F26. scripts/check_pipeline.py L350-L371 (`write_log`): it refuses (exit 2, writes nothing) if the agent, the ID or the fields don't match `LOG_FORMAT`, or if there is no `work/<ID>/request.md`. Otherwise it writes `HH:MM | agent | ID | fields` with the current UTC time. It does not record which process ran it, so an orchestrator-run line and an agent-run line look the same.
F27. scripts/check_pipeline.py L384-L408 (`late_log_lines`): `LOG TIME:` flags a line whose stated time is after the commit that added it (git blame, minute precision). It cannot tell who ran the command, only when. To keep `LOG TIME: none`, `--log` has to run before the commit that adds the line.
F28. scripts/check_handoff.py L11/L18/L43/L56: prints `sources count (unique URLs in 01-research.md): <n>` using `URL_RE`. That number is the R1 log field. R3's verified/fixed/removed counts come from the same script's totals output (r3-fact-checker.md L20).

### Option B risks (Bash for R1-R3/I1)
F29. R1-R3 and I1 read untrusted web pages (WebFetch/WebSearch, agent files L4). Giving those agents a shell lets fetched text reach a tool that can run commands. Per-command limits on Bash are "fragile" and "not a security boundary" (F7, F8). [https://code.claude.com/docs/en/permissions] The claim that this is a prompt-injection risk is R1's reasoning from F7/F8 and the tool lists. No outside source on injection was fetched in this item: UNVERIFIED as an external claim.
F30. Removing the `tools:` line to "fix" the gap would give the four agents every inherited tool, Bash included (F1). Option B has to be an explicit `tools:` edit adding Bash.

### Overlap with item 073 (parallel)
F31. work/073/request.md L8/L15: 073 adds a line to .claude/agents/i3-verifier.md (I3's head realtest run is its own) and to run-item.md "if needed". Under option A, 072 changes run-item.md L14 (the log/orchestrator sentence), r1, r2, r3 and i1. It needs no edit to i3-verifier.md, because I3 has Bash (F15). The two items share one file, run-item.md, in different paragraphs: 073's natural spot is the realtest paragraph L18, 072's is L14. Whichever item lands second should build on the other's branch (run-item.md L12, item 034 "a file you will change is on an OPEN BRANCH"). If 072 does touch i3-verifier.md, it overlaps 073 there too.

## Numbers used (show the math)
- Agent files: 7 (Glob of .claude/agents/*.md). Without Bash: r1, r2, r3, i1 = 4. With Bash: i2, i3, a1 = 3. 4 + 3 = 7.
- Commands the no-shell agents are told to run, per FULL item: R1 2 (check_handoff, --log) + R2 1 + R3 2 + I1 1 = 6. Per RESEARCH ONLY item (R1-R3): 2 + 1 + 2 = 5.
- Lines to reword under option A: run-item.md L14 (1), r1 L19, r2 L22, r3 L20 and L24, i1 L18 = 6 places in 5 files.
- 069 timing (from A1's audit, F24): R1 line 23:21 vs commit 23:21:53, so 0 minutes late. R3 line 23:32 vs commit 23:32:26, so 0 minutes late. Both are LOG TIME clean at minute precision (F27).

## Fit for a ~$3k account
This is a process item. It changes no strategy rule, trade, price, premium, dividend, tax or liquidity input, so the $3k limits don't apply. Option A adds no cost and no permissions. Option B widens what the research agents can do on the machine that runs the bot (F29), for no change in account outcome. Nothing here connects to a broker.

## Open questions
1. Recommendation for R2/R3 to test: option A. It is what already happens (F20-F24). It keeps least privilege (F7, F8, F29), and it needs only text changes.
   Proposed run-item.md L14 sentence: "R1, R2, R3 and I1 have no shell (`tools:` line). Right after such a step's file exists, and before its commit, the orchestrator runs `check_handoff.py <ID>` (after R1 and R3), then `check_pipeline.py --log <agent> <ID> "<fields>"`, taking every count from the script output. It pastes the check_handoff output into that step's file labelled `(run by the orchestrator <date>, exit <n>)`. I2, I3 and A1 run their own commands."
   Each of the four agent files would then say: "Your step has no shell: the orchestrator runs `--log` (and check_handoff) for you; write your fields in the file so it can copy them."
2. R3 step 7 ("must say PASS before you set READY", F12): under option A, R3 can't see the PASS. Choose one. (a) R3 writes READY, and if the orchestrator's check_handoff prints FAIL, the item goes back to R3 (counts as a loop under run-item L14). (b) R3 writes `READY (pending check_handoff)`, and the orchestrator confirms it. R2/R3 to decide. Is (b) parsed by any script? Not checked: UNVERIFIED.
3. Where R1's sources count lives: only in the log line, or also pasted into 01? The request says "pastes the output". Where it goes for R1 is not specified.
4. Optional guardrail against this drift coming back (RI-010 pattern: a duty that exists only in agent text). A test that each `.claude/agents/*.md` file whose text says `python3 scripts/` either lists Bash in `tools:` or names the orchestrator. It is cheap, and it would have caught this item. It is not requested, so I1 decides whether it is in scope.
5. "No hand-typed lines" also binds the orchestrator. It must use `--log`, never write to logs/ directly. Should run-item.md say that explicitly? It is implied by item 045.
6. 073 overlap (F31): agree the merge order with the orchestrator before I2.
7. Tooling note: R1 could not run `check_handoff.py 072` or `--log R1 072`. The orchestrator runs both (task instructions), which is option A applied to this item.
