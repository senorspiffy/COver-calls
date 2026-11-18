# 03 Research hand-off - 072
Status: READY (R3's own checks pass. check_handoff is run by the orchestrator and pasted at the end of Self-check. READY stands only if that output says PASS; on FAIL the item comes back to R3.)

Recurring issues checked (item 013), against this file:
- RI-001 (ESCALATED): the one selector in the map (step 8 drift test: "agent files with no Bash, lines holding `python3 scripts/`") has a count R3 computed from file reads: 7 agent files, 7 of 7 have a `tools:` line, 4 of 7 have no Bash, and those 4 hold 5 such lines. 0 of 5 contain "orchestrator" today, so the test fails on today's tree. After steps 2-5, 5 of 5 do. Nothing is called "always" or "every" without a count.
- RI-002 (GUARDED): nothing absent turns into a value. A missing check_handoff result, a missing `Log fields:` line, a `--log` refusal or a missing `tools:` line each block with a named result (Missing inputs). Nothing is defaulted.
- RI-010 (GUARDED; A1's 069 audit expects a 5th occurrence): this item is the RI-010 shape in reverse (a duty in the agent text that the agent cannot do). The fix is a text change plus a script check (step 8), so it is not text-only. The existing guardrails (`INCOMPLETE`, `LOG TIME:`) are unchanged.
- RI-006: every count in a log line comes from script output (check_handoff's `sources count` / `totals line`), copied by the orchestrator. The totals below were counted by R3 from this table. The orchestrator's check_handoff run is the authority.
- RI-004 / RI-005: every example log line in the map is checked against its LOG_FORMAT regex, and the LOG TIME ordering against `late_log_lines` (Self-check).
- RI-007 (GUARDED): Scope FULL. The item changes .claude/, templates/, README.md and tests/, so I1-I3 run. It is a RULES BRANCH (check_pipeline.py L193 RULE_PATHS) and needs the person's OK in PR review.
- RI-009 (GUARDED): overlap with 073 on run-item.md (different paragraphs, L14 vs L18). Merge order in step 9.
- Not applicable: RI-003 (no calendar), RI-008 (stdlib only, no new syntax), RI-011 (no branch diff), RI-012 (no error classification), RI-013 (no realtest change).

Sources:
- Repo on branch daily-fixes/2026-11-18. R3 opened every cited file:line. R3 has no shell: it ran no git command, no test, no script. Git-dependent facts (commit times) are written as checks for I3, not as results.
- Fetched 2026-11-18: https://code.claude.com/docs/en/sub-agents, https://code.claude.com/docs/en/permissions, https://genai.owasp.org/llm01/ (new, for F29).

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 F1: `tools` = "Tools the subagent can use, as a comma-separated string such as `Read, Grep, Bash` or a YAML list. Inherits every tool available to subagents if omitted." | https://code.claude.com/docs/en/sub-agents | VERIFIED | - |
| 01 F2: allowlist `tools` / denylist `disallowedTools`; disallowedTools applied first | https://code.claude.com/docs/en/sub-agents | VERIFIED | - |
| 01 F3: Bash is its own tool name; example `tools: Read, Grep, Glob, Bash`; no Bash in the list → no shell | https://code.claude.com/docs/en/sub-agents | VERIFIED | Example is the `safe-researcher` block. |
| 01 F4: a `disallowedTools` specifier removes the whole tool; Bash deny in `permissions.deny` "applies to the main conversation and to subagents" | https://code.claude.com/docs/en/sub-agents | VERIFIED | - |
| 01 F5: "The frontmatter is not the way to limit Bash to a single command"; per-command control is only from settings permission rules | https://code.claude.com/docs/en/sub-agents | Fixed | True for `tools`/`disallowedTools`. But the same page shows a frontmatter `hooks:` field with a `PreToolUse` hook, matcher `Bash`, whose script "exits with code 2 to block" (`db-reader` example). So per-command control is possible in the frontmatter through a hook (02 AGAINST 3). Option B with a hook is weighed and DROPPED in D1. |
| 01 F6: rules "evaluated in order: deny, then ask, then allow" | https://code.claude.com/docs/en/permissions | VERIFIED | Page L58. |
| 01 F7: "Bash permission patterns that try to constrain command arguments are fragile." | https://code.claude.com/docs/en/permissions | VERIFIED | - |
| 01 F8: a deny or ask rule "covers the invocation Claude usually produces and isn't a security boundary around the program" | https://code.claude.com/docs/en/permissions | VERIFIED | - |
| 01 F9: R1's session tool set = r1 L4 line plus the hand-back tool, no Bash | .claude/agents/r1-researcher.md L4 | VERIFIED | R3's own session shows the same for r3 L4 (Read, Write, Glob, Grep, WebSearch, WebFetch, plus hand-back). Session observation, not a doc claim. |
| 01 F10: r1 L4 no Bash; L19 names `--log R1` and `check_handoff.py <ID>` | .claude/agents/r1-researcher.md L4, L19 | VERIFIED | - |
| 01 F11: r2 L4 no Bash; L22 names `--log R2` | .claude/agents/r2-improver.md L4, L22 | VERIFIED | - |
| 01 F12: r3 L4 no Bash; L20 step 7 runs check_handoff and gates READY on PASS; L24 `--log R3` | .claude/agents/r3-fact-checker.md L4, L20, L24 | VERIFIED | - |
| 01 F13: i1 L4 no Bash; L18 `--log I1` | .claude/agents/i1-reviewer.md L4, L18 | VERIFIED | - |
| 01 F14: i2 L4 has Bash; L18/L20/L21/L25 grep, tests, git status, `--log` | .claude/agents/i2-builder.md L4, L18-L25 | VERIFIED | - |
| 01 F15: i3 L4 has Bash; L13 check_handoff, check_pipeline, tests; L18 `--log` | .claude/agents/i3-verifier.md L4, L13, L18 | VERIFIED | - |
| 01 F16: a1 L4 has Bash; L17/L21/L22/L29 git, check_handoff --all, check_pipeline, --next-id; no `--log` line; result in 07 (L12) | .claude/agents/a1-auditor.md L4, L12, L17, L21, L22, L29 | VERIFIED | - |
| 01 F17: 7 agent files, 4 without Bash, 3 with | Glob .claude/agents/*.md (7) | VERIFIED | - |
| 01 F18: run-item L14 "each step's agent writes its log line with `check_pipeline.py --log` ..."; run-item never names the orchestrator | .claude/commands/run-item.md L14; Grep "orchestrator" in .claude/ (0 hits) | VERIFIED | - |
| 01 F19: run-item L14 "Before each step, confirm the previous step's file exists" | .claude/commands/run-item.md L14 | VERIFIED | - |
| 01 F20: research/2026-11-17 L3-L8, six R1-R3 lines for 069/070, `--log` format | logs/research/2026-11-17.md L3-L8 | VERIFIED | - |
| 01 F21: implementation/2026-11-18 L5 I1 069 line | logs/implementation/2026-11-18.md L5 | VERIFIED | - |
| 01 F22: 069 R1 open question 6 (no shell; orchestrator must run `--log`) | work/069/01-research.md L70 | VERIFIED | - |
| 01 F23: 069/03 L130, 070/03 L159 "(run by the orchestrator 2026-11-17, exit 0)"; 070/03 L12 | work/069/03-handoff.md L130; work/070/03-handoff.md L12, L159 | VERIFIED | - |
| 01 F24: A1 on 069: all lines via `--log`, LOG TIME none, INCOMPLETE none, R1 23:21 vs 23:21:53, R3 23:32 vs 23:32:26; "consistent with the rules' intent but not their wording" | logs/audit/2026-11-18-069.md L20-L24 | VERIFIED | - |
| 01 F25: suggestion DROPPED from 069 | work/069/04-build-plan.md L223 | VERIFIED | - |
| 01 F26: write_log refuses (exit 2) on bad agent/ID/fields or no request.md; writes UTC `HH:MM`; does not record the caller | scripts/check_pipeline.py L350-L371 | VERIFIED | - |
| 01 F27: late_log_lines flags a line whose stated time is after its adding commit (minute precision); cannot tell who ran it | scripts/check_pipeline.py L384-L408 | VERIFIED | L403 drops seconds from the commit time; L404 `stated > commit`. |
| 01 F28: check_handoff prints `sources count (unique URLs in 01-research.md): <n>` (URL_RE); R3's counts from its totals | scripts/check_handoff.py L11, L18, L43, L56, L75; r3-fact-checker.md L20 | VERIFIED | - |
| 01 F29: Bash for R1-R3/I1 lets fetched web text reach a shell; prompt-injection risk UNVERIFIED as an external claim | https://code.claude.com/docs/en/permissions; agent files L4 | Fixed | New source https://genai.owasp.org/llm01/: "Indirect Prompt Injections occur when an LLM accepts input from external sources that can be controlled by an attacker", and "Follow the principle of least privilege by restricting the LLM to only the minimum level of access necessary". a1-auditor.md L15 already cites OWASP LLM01. |
| 01 F30: deleting the `tools:` line gives every inherited tool, Bash included | https://code.claude.com/docs/en/sub-agents (F1) | VERIFIED | The drift test (step 8) fails a file with no `tools:` line. |
| 01 F31: 073 changes i3-verifier.md and run-item.md "if needed"; 072 needs no i3 edit; run-item L12 item 034 build-on-branch rule; 073's spot near L18 | work/073/request.md L8, L15; run-item.md L12, L18 | VERIFIED | - |
| 01 Numbers: 7 agent files = 4 without Bash + 3 with | Glob; agent files L4 | VERIFIED | 4 + 3 = 7. |
| 01 Numbers: commands named for no-shell agents: FULL 2 + 1 + 2 + 1 = 6; RESEARCH ONLY 5 | r1 L19, r2 L22, r3 L20/L24, i1 L18 | VERIFIED | - |
| 01 Numbers: 6 places in 5 files to reword | Grep `check_handoff\|--log` outside work/ and logs/ | Fixed | Also README.md L37 says check_handoff is "run by R3, I3, A1", which would contradict the new rule, and templates/research-handoff.md L21 is where the "(run by the orchestrator ...)" label lives. Map: 8 places in 7 files (plus the test file in step 8). check_pipeline.py L52 ("Every step logs this way") names no actor and stays unchanged. |
| 01 Numbers: 069 timing 0 minutes late, LOG TIME clean | logs/audit/2026-11-18-069.md L21; check_pipeline.py L403-L404 | VERIFIED | 23:21 is not > 23:21 (commit 23:21:53 floored); 23:32 is not > 23:32. |
| 01 Fit: process item, no strategy, cost or broker effect | request.md; this map | VERIFIED | Research tooling, not financial advice. |
| 01 OQ2(b): is `READY (pending check_handoff)` parsed by any script? UNVERIFIED | Grep `READY\|pending` in scripts/ | Fixed | Only check_pipeline.py L210 (R3 regex `(READY\|BLOCKED)\b.*`, so it would be accepted) and L220 (hint). check_handoff does not read the Status line. No script gives "pending" a meaning, so no pending state is added (D2). |
| 02 Past logs: RI-010 root cause L120; `INCOMPLETE` (043) and `LOG TIME:` (045) cover the outcome whoever runs `--log` | logs/recurring-issues.md L120-L122 | VERIFIED | - |
| 02 Past logs: 045/049 occurrences were batches typed after the commit (23:10 vs 22:24; 20:40 vs 20:20) | logs/recurring-issues.md L128-L129 | VERIFIED | - |
| 02 Past logs: A1 checked the orchestrator pattern on 069; 069 later `Result: PASS` | logs/audit/2026-11-18-069.md L20-L24, L158 | VERIFIED | - |
| 02 Past logs: option A ran on 4 items (069, 070, 072, 073); LOG TIME for 070/072/073 UNVERIFIED | logs/research/2026-11-17.md L3-L8; logs/research/2026-11-18.md L3-L7; logs/audit/2026-11-18-070.md L56, L64 | Fixed | 6 items have R-lines that no-shell agents could not have written: 069, 070, 071, 072, 073, 074 (2026-11-18 L3-L6 add 071 and 074). 070 has `LOG TIME: none` per its A1 audit (L56). 071-074 are in progress; their LOG TIME is an I3 check (step 9). |
| 02 Past logs: attempt dropped in 069 | work/069/04-build-plan.md L223 | VERIFIED | - |
| 02 Past logs: 072 carried with 071, 073; 074 opened the same day | logs/efficiency/2026-11-18.md L3-L4 | VERIFIED | - |
| 02 Past logs: Grep logs/ for "Bash" → 0 occurrences in 0 files | Grep logs/ "Bash" | VERIFIED | - |
| 02 FOR 1: write option A at run-item L14's checkpoint, order file → check_handoff → `--log` → commit; keeps LOG TIME none | run-item.md L14; check_pipeline.py L384-L408 | VERIFIED | Adopted (step 1). |
| 02 FOR 2: `Log fields:` line in 02/04; LOG_FORMAT refuses a typo at `--log` (exit 2, nothing written) | check_pipeline.py L207-L214, L353-L358 | VERIFIED | Adopted for R2 and I1 only. R3's status is already on its Status line; R1 has no non-count field (D3). |
| 02 FOR 3: drift test; 7 files, 3 pass on Bash, 4 pass only after the rewording; frontmatter parser in tests/ UNVERIFIED | Glob .claude/agents/*.md; Grep tests/ for `frontmatter\|^tools:\|\.claude/agents` | Fixed | No frontmatter parser exists in tests/ (the only hit is a RULES BRANCH string, test_pipeline_check.py L479). The test parses the `---` block with stdlib line reads. Sharpened: each line of a no-Bash file that holds `python3 scripts/` must contain "orchestrator" (5 lines today, 0 pass), not just "the body names the orchestrator somewhere" (step 8). |
| 02 AGAINST 1: R3 loses its self-gate; FAIL must give no log line and no commit; a re-send is a loop; `READY (pending ...)` passes L210 but means nothing | r3-fact-checker.md L20; run-item.md L14; check_pipeline.py L210 | VERIFIED | Decided D2: option (a), the re-send counts as one loop on R3. |
| 02 AGAINST 2: the orchestrator has no agent file; 4 items run in parallel; LOG TIME cannot catch a line written late but before a late commit; 072 and 073 R1 lines both 23:22 | logs/efficiency/2026-11-18.md L3-L4; check_pipeline.py L404; logs/research/2026-11-18.md L3-L4 | VERIFIED | Commit times not checkable by R3 (no git). Mitigation adopted: "per step, never in a batch across steps or parallel items" (step 1). |
| 02 AGAINST 3: B with a PreToolUse hook (matcher Bash, exit 2 blocks) exists; settings rules apply to the whole session | https://code.claude.com/docs/en/sub-agents | VERIFIED | Recorded as considered and DROPPED (D1). |
| 02 Languages: N/A, no new external market claim | 01, 02 | VERIFIED | The outside sources are tool docs and OWASP. None is a market fact. |
| 02 Holes: do not "fix" by deleting the `tools:` line | https://code.claude.com/docs/en/sub-agents (F1) | VERIFIED | Pinned by step 8 (missing `tools:` line fails). |

**Totals:** 52 rows checked → **46 VERIFIED as-is**, **6 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None. The one partly wrong claim (F5) and the five UNVERIFIED or incomplete points (F29, Numbers places, OQ2(b), 02 "4 items", 02 parser) were corrected in place (see the Fix column).

## Decisions on R1/R2 open points (with reasons)
- **D1 Option A (the orchestrator runs the commands). Option B DROPPED, in both forms.** Plain B gives a shell to the four agents that read untrusted web text. OWASP LLM01 names that input path ("external sources that can be controlled by an attacker") and advises least privilege. B with a PreToolUse hook (F5 fix, 02 AGAINST 3) needs a hook script plus tests and a settings change. Command-pattern limits are "fragile" and "not a security boundary" (F7, F8), and settings rules are session-wide (F4). A is text only and has already run on 6 items (069-074). 070 has LOG TIME none (A1 audit), and 069 passed A1.
- **D2 R3's READY gate (01 OQ2): option (a).** R3 sets READY only if its own checks pass, and it leaves the template's check_handoff line for the orchestrator. If the orchestrator's check_handoff prints FAIL, there is no `--log` line and no commit of 03. The item goes back to R3 with the output, and that counts as one loop on R3 under run-item L14 (never silent). No "pending" state is added (OQ2(b) fix).
- **D3 Where fields live (01 OQ3, 02 FOR 2).** R1: sources count only in the log line, from check_handoff, with no paste into 01. 01 is committed, so A1 can re-run the count at any time. R2 and I1 end their file with `Log fields: <fields>`, and the orchestrator copies the line verbatim. R3's status comes from its Status line, and its counts come from check_handoff's `totals line`.
- **D4 The orchestrator never writes logs/ itself (01 OQ5)**, and it never edits a line `--log` refused. A refusal (exit 2) goes back to the step.
- **D5 Drift test (01 OQ4, 02 FOR 3): in the map as step 8.** It is the RI-010 lesson: a text-only duty needs a script check. It is not in the request, so I1 may DROP it with a reason. Without it the item is text only.
- **D6 073 overlap (01 OQ6, F31):** whichever item lands second builds on the other's branch (run-item L12, item 034). 072 does not touch i3-verifier.md.

## Implementation map
Files: .claude/commands/run-item.md, .claude/agents/{r1-researcher,r2-improver,r3-fact-checker,i1-reviewer}.md, templates/research-handoff.md, README.md, and tests/test_pipeline_check.py (step 8). That is 8 files, or 7 if I1 drops step 8. Nothing changes in ccbot/, config/, scripts/, data/ or reports/. Nothing connects to a brokerage. RULES BRANCH (.claude/, templates/), so the person must OK the PR.

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | **run-item.md L14**: in the end-of-run sentence, replace "(each step's agent writes its log line with `check_pipeline.py --log` as soon as its file exists, never in a batch at the end, item 045; ...)" with "(every log line is written with `check_pipeline.py --log` as soon as its step's file exists, never in a batch at the end, item 045; ...)". Add a new paragraph after L14: "Log lines and check_handoff (item 072). R1, R2, R3 and I1 have no shell (no Bash on their `tools:` line), so the orchestrator runs their commands; I2, I3 and A1 run their own. For each R1, R2, R3 and I1 step, in this order, one step at a time and never in a batch across steps or parallel items: (1) the step's file exists; (2) after R1 and R3, run `python3 scripts/check_handoff.py <ID>`; after R3, paste its output into 03 under the template's `check_handoff output (run by the orchestrator <YYYY-MM-DD>, exit <n>; must say PASS):` line; (3) if it printed FAIL, write no log line and do not commit 03: send the item back to R3 with the output (one loop on R3); (4) run `python3 scripts/check_pipeline.py --log <agent> <ID> "<fields>"`, copying R1's count from `sources count`, R3's from `totals line` (as-is → verified) with READY/BLOCKED from 03's Status line, and R2's and I1's fields from the `Log fields:` line at the end of 02/04; (5) commit the step file and its log line. The orchestrator never writes to logs/ itself and never edits a refused line: a `--log` refusal (exit 2) goes back to the step." | run-item.md L14 | run-item.md | grep: "the orchestrator runs their commands" 1 hit; "each step's agent writes its log line" 0 hits; "never writes to logs/" 1 hit | – |
| 2 | **r1-researcher.md L19** → "No shell (item 072): you run no command. Right after your file exists the orchestrator runs `python3 scripts/check_handoff.py <ID>` for the sources count (unique URLs in `01-research.md`) and `python3 scripts/check_pipeline.py --log R1 <ID> "brief written \| <sources count>"`, which appends `<UTC HH:MM> \| R1 \| <ID> \| brief written \| <sources count>` to `logs/research/<YYYY-MM-DD>.md`. Never type a log line or count sources by hand (item 045)." (one line) | r1 L19 | r1 | step 8 test; grep r1 for "Write it with" → 0 | – |
| 3 | **r2-improver.md L22** → "No shell (item 072): end 02 with `Log fields: 3 for / 3 against \| languages: <list>`. Right after your file exists the orchestrator copies it into `python3 scripts/check_pipeline.py --log R2 <ID> "<fields>"`, which appends `<UTC HH:MM> \| R2 \| <ID> \| <fields>` to `logs/research/<YYYY-MM-DD>.md` and refuses a line not in this format. Never type a log line by hand (item 045)." (one line) | r2 L22 | r2 | step 8 test; grep r2 "Log fields:" 1 hit | – |
| 4 | **r3-fact-checker.md L20** (step 7) → "7. No shell (item 072): set READY only if your own checks pass, and leave the template's check_handoff output line empty. The orchestrator runs `python3 scripts/check_handoff.py <ID>`, pastes its output there, and sends 03 back to you if it does not say PASS; READY stands only with PASS." **L24** → "The orchestrator then runs `python3 scripts/check_pipeline.py --log R3 <ID> "<n> verified, <n> fixed, <n> removed \| <READY/BLOCKED>"`, copying the counts from check_handoff's totals line and the status from your Status line; it appends `<UTC HH:MM> \| R3 \| <ID> \| ...` to `logs/research/<YYYY-MM-DD>.md`. Never type a log line or count by hand (item 045)." L22 (RESEARCH ONLY / 07) unchanged. | r3 L20, L24 | r3 | step 8 test; grep r3 "must say PASS before you set READY" → 0 | – |
| 5 | **i1-reviewer.md L18** → "No shell (item 072): end 04 with `Log fields: <verdict> \| <n> files planned`. Right after your file exists the orchestrator copies it into `python3 scripts/check_pipeline.py --log I1 <ID> "<fields>"`, which appends `<UTC HH:MM> \| I1 \| <ID> \| <fields>` to `logs/implementation/<YYYY-MM-DD>.md` and refuses a line not in this format. Never type a log line by hand (item 045)." (one line) | i1 L18 | i1 | step 8 test; grep i1 "Log fields:" 1 hit | – |
| 6 | **templates/research-handoff.md L21** → "`check_handoff output (run by the orchestrator <YYYY-MM-DD>, exit <n>; must say PASS):`" (same label as on 069/070's pastes). **README.md L37** "(run by R3, I3, A1)" → "(run by the orchestrator after R1 and R3, and by I3 and A1; item 072)". | template L21; README L37 | 2 lines | grep template "run by the orchestrator" 1 hit; grep README "run by R3, I3, A1" 0 hits. check_handoff still finds `## Self-check` (it reads only the heading, L81) | – |
| 7 | **Field formats**: no change to LOG_FORMAT or check_pipeline.py. The copied fields must fit the existing regexes (L208-L213). | check_pipeline.py L207-L214 | – | Self-check rows 4-7 (each example line vs its regex); existing tests `test_log_*` unchanged | – |
| 8 | **tests/test_pipeline_check.py**: new `test_no_shell_agents_leave_commands_to_orchestrator`. For each `.claude/agents/*.md` (sorted Glob, REPO-relative): the frontmatter is the lines between the first two `---`. No frontmatter or no `tools:` line → fail `"<file>: no tools: line (inherits every tool incl. Bash, item 072)"`. tools = `[t.strip() for t in value.split(",")]`. If "Bash" is not in tools: every body line that contains `python3 scripts/` must contain `orchestrator`, else fail naming file and line number. Also assert the set of no-Bash names == {"r1-researcher", "r2-improver", "r3-fact-checker", "i1-reviewer"} (a change is a RULES decision, item 072), and that run-item.md contains "the orchestrator runs their commands" and "never writes to logs/". Stdlib only. | 7 agent files, run-item.md | 1 test | `python3 -m pytest -q tests/test_pipeline_check.py` passes; full suite = base + 1 (pasted). **Mutations (scratch copy):** m1 restore old r1 L19 → fails (r1 line 19); m2 delete r2's `tools:` line → fails (no tools: line); m3 add Bash to i1's tools → set assert fails; m4 remove the run-item paragraph → fails. **Before-fix probe:** on today's tree the test fails with 5 lines named (r1 L19, r2 L22, r3 L20, r3 L24, i1 L18). | Agent files 7; with `tools:` line 7 of 7 (each L4); no Bash 4 of 7; lines with `python3 scripts/` in those 4: 5 (Grep, 2026-11-18). Containing "orchestrator" today: 0 of 5 (Grep "orchestrator" in .claude/: 0), so it would have caught this item. After steps 2-5: 5 of 5 (each new text is one line holding both strings). With Bash: 3 of 7, skipped by design. |
| 9 | **I3 checks on the branch**: `python3 scripts/check_pipeline.py`: 072 not INCOMPLETE; `LOG TIME:` names none of 071-074; `RULES BRANCH:` / OPEN BRANCHES lines pasted. `python3 scripts/check_handoff.py 072` PASS. If 073's branch is open and changes run-item.md, 072 is built on it or rebased after it (run-item L12, item 034); paste which. Check that 072's own R1-I1 lines were written by the orchestrator in step order: each log line's minute ≤ its adding commit's minute (git blame). | branch HEAD | pasted output | outputs pasted in 06 | – |

## Missing inputs
Step 3a (ticker screen vs `screen.TESTS` / `MISSING_POLICY`): not applicable, because no ticker is screened. The rows below cover this process's own inputs.
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| check_handoff output after R3 (step 1 (2)-(3)) | FAIL, or the script cannot run | No `--log` line, no commit of 03. Item back to R3 with the output (FAIL), or stop and report to the person (cannot run). Never a hand count, never READY without PASS. |
| check_handoff `sources count` after R1 (step 1 (4)) | no 01-research.md, or the script cannot run | No R1 log line. INCOMPLETE `no log line for R1` stays visible at the end-of-run check. Never a hand count. |
| `Log fields:` line in 02/04 (steps 3, 5) | missing or malformed | The orchestrator writes nothing and sends the step back. A malformed field is refused by `--log` (exit 2, nothing written, L353-L358). Never rebuilt from the chat report. |
| `--log` result (step 1 (4)) | exit 2 refusal | Nothing is written (L358/L361). The step goes back. The line is never edited into logs/ by hand. |
| 03 Status line for R3's field (step 1 (4)) | no READY/BLOCKED | The R3 regex refuses it (L210). Back to R3. |
| `tools:` line in an agent file (step 8) | no frontmatter or no `tools:` line | Test fails: `no tools: line (inherits every tool incl. Bash, item 072)`. Not treated as "no Bash" or as a pass. |
| Commit times for LOG TIME (step 9) | no git where checked | `LOG TIME:` is not checked (late_log_lines returns None, L387-L388). I3 runs it in the repo with git. R3 claims no result. |

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Agent split (F17, step 8) | no-Bash + Bash = files | 4 (r1, r2, r3, i1) + 3 (i2, i3, a1) = 7 = Glob count | OK |
| Lines the drift test reads (step 8) | lines with `python3 scripts/` in no-Bash files | r1 1 (L19) + r2 1 (L22) + r3 2 (L20, L24) + i1 1 (L18) = 5; with "orchestrator" today 0, so 5 fail; after steps 2-5, 1 + 1 + 2 + 1 = 5 pass | OK (fails today, passes after) |
| Files changed (map header) | listed files | run-item 1 + agent files 4 + template 1 + README 1 + test 1 = 8; without step 8: 7. Places: L14 + r1 L19 + r2 L22 + r3 L20 + r3 L24 + i1 L18 + template L21 + README L37 = 8 | OK |
| R1 field example | `brief written \| \d+` | 072's 01 has 2 unique URLs (`[https://...sub-agents]`, `[https://...permissions]`; URL_RE stops at `]`) → "brief written \| 2" = logs/research/2026-11-18.md L4 | match |
| R2 field example | `3 for / 3 against \| languages: \S.*` | "3 for / 3 against \| languages: N/A": "N" is non-space | match |
| R3 field example | `\d+ (verified\|as-is), \d+ fixed, \d+ removed \| (READY\|BLOCKED)\b.*` | totals "52 rows -> 46 as-is, 6 fixed, 0 removed" → "46 verified, 6 fixed, 0 removed \| READY" | match |
| I1 field example | `(FIT\|FIT WITH CHANGES\|NOT A FIT) \| \d+ files planned\b.*` | "FIT \| 8 files planned" | match |
| LOG TIME order (step 1 (4)-(5)) | flagged iff stated HH:MM > commit time with seconds dropped (L403-L404) | 069 R3: `--log` 23:32, commit 23:32:26 → 23:32 > 23:32 false → clean. Wrong order: commit 23:32:10 holding a line stamped 23:33 → 23:33 > 23:32 → flagged. So `--log` before the commit keeps it clean | OK |
| Fact-check totals | as-is + fixed + removed = rows | 46 + 6 + 0 = 52 = table rows (counted by R3; the script is the authority) | OK |

check_handoff output (run by the orchestrator):
(run by the orchestrator 2026-11-18 23:31 UTC, exit 0)
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 52
totals line: 52 rows -> 46 as-is, 6 fixed, 0 removed
PASS
```
