# 04 Build plan - 072
Fit verdict: FIT WITH CHANGES

Fit check. This is a process item with no strategy, cost, broker or $3k-account effect: nothing in ccbot/, config/, scripts/, data/ or reports/ changes. It writes down the pattern already used on 069-074 (R3 F23/F24, 02 Past logs), and I1 is working that way on this item now: no shell, ending with a `Log fields:` line for the orchestrator. It is a RULES BRANCH (.claude/, templates/), so the person must approve the PR. It does not conflict with built code. `check_handoff.py`, `write_log` and `late_log_lines` stay unchanged (map step 7). No existing test reads the real agent files or run-item.md: the only `.claude` hits in tests/ are fixtures under tmp_path (test_pipeline_check.py, the RULES BRANCH and CODE_PATHS tests). Changes against 03:
1. C1, the drift test goes in a new file, `tests/test_agent_tools.py`, not tests/test_pipeline_check.py. 071 adds I3 FAIL fixture tests to test_pipeline_check.py (071/01 L48-L49, near the 042 tests) and is built first. A separate file means no shared test file and no merge conflict.
2. C2, the test parses both `tools:` forms the docs allow (comma string or YAML list). It also honours `disallowedTools`, and an entry's tool name is the text before any `(`. Fixture cases pin each form (Extra research 1).
3. C3, the run-item paragraph says the orchestrator runs both scripts from the repo root. It also says that after R1 only the `sources count` line is used and the exit code does not gate R1 (Extra research 2, 3).
4. C4, the `Log fields:` line is the plain last line of 02/04, with no backticks. The orchestrator passes the text after `Log fields: ` unchanged (Extra research 4).

## Extra research (with sources)
1. **Frontmatter forms R3's parser missed.** The sub-agents page (fetched 2026-11-18, https://code.claude.com/docs/en/sub-agents) says `tools` is a comma-separated string "such as `Read, Grep, Bash` or a YAML list". It says `disallowedTools` uses the "Same format as `tools`" and that "An entry with a specifier, such as `Bash(git push *)`, still removes the whole tool". R3's step 8 splits on commas only, which goes wrong in two ways:
   - A YAML list (`tools:` with an empty value, then `  - Read` lines) would parse as `[""]`. The file would count as "no Bash" because the parser broke, not because the file has no shell.
   - A `disallowedTools: Bash` line on i2/i3/a1 would leave Bash in the set, so the test would still treat the agent as shell-capable.
   Plan: parse both forms, take each tool name before any `(`, and count Bash as present only if it is in `tools` and not in `disallowedTools`. An empty `tools:` value with no list items is an error (fail), never "no tools". All of this is pinned by fixture cases.
2. **After R1, check_handoff's exit code is not R1's gate.** `scripts/check_handoff.py` `main()` prints `sources count` when 01 exists. It then returns 0 with "no 03 ...; nothing else to check" when 03 is absent, which is the normal first pass. But if an item is sent back to R1 (NOT A FIT, run-item "send the item back"), an old 03 is still there and may FAIL. The R1 count is still valid, so the orchestrator takes R1's field from the `sources count` line only. The exit code gates only the R3 step. If the `sources count` line is missing (no 01), no R1 line is written (03 Missing inputs row 2).
3. **cwd.** Both scripts use paths relative to the current directory: check_handoff `Path("work")`; write_log `Path("work") / item / "request.md"` and `Path("logs") / team`. Run from anywhere else, check_handoff prints `FAIL: no work item folder` and `--log` refuses with `no work/<ID>/request.md`. Both fail loud, but the cause would be misread as a content FAIL. The sub-agents page also says `cd` does not persist between Bash calls. So run-item says "from the repo root".
4. **Copying `Log fields:`.** `write_log` fullmatches `fields.strip()` against LOG_FORMAT (check_pipeline.py `write_log`). A line written as ``Log fields: `FIT | 8 files planned` `` would carry a backtick and be refused (exit 2). That is safe but wastes a loop. The agent texts therefore say "plain text, no backticks, last line of the file". The I1 regex `(FIT|FIT WITH CHANGES|NOT A FIT) \| \d+ files planned\b.*` accepts this file's own last line (checked below).
5. **Least privilege (D1) confirmed.** OWASP LLM01 (https://genai.owasp.org/llm01/, cited by R3 F29) advises restricting the LLM "to only the minimum level of access necessary". Keeping Bash off the four agents that read web text matches this. Nothing new changes D1.

## Files to create/change
Anchors are text, not line numbers: I2 builds 071 → 072 → 073 → 074 on this branch, so line numbers shift. Shared files are marked.

1. **.claude/commands/run-item.md** (SHARED with 073, which edits the realtest paragraph starting "When an item changes `ccbot/realtest.py`"; 072 does not touch that paragraph).
   - Anchor A: in the paragraph starting "Before each step, confirm the previous step's file exists", replace `(each step's agent writes its log line with \`check_pipeline.py --log\` as soon as its file exists, never in a batch at the end, item 045;` with `(every log line is written with \`check_pipeline.py --log\` as soon as its step's file exists, never in a batch at the end, item 045;`. The rest of that sentence is unchanged.
   - Anchor B: insert a new paragraph directly after that paragraph, before the one starting "A follow-up to a completed item". Text: map step 1's paragraph as written in 03, with three edits.
     - In (2), add "from the repo root (both scripts use paths relative to it)" after "run".
     - At the end of (2), add: "After R1, take only the `sources count` line; its exit code does not gate R1 (an old 03 from an earlier loop is R3's to fix)."
     - In (4), replace "R2's and I1's fields from the `Log fields:` line at the end of 02/04" with "R2's and I1's fields from the text after `Log fields: ` on the last line of 02/04, unchanged".
     - The fixed strings the test pins stay word-for-word: "the orchestrator runs their commands" and "never writes to logs/".
2. **.claude/agents/r1-researcher.md**: replace the whole line starting "Finish by appending one line to `logs/research/" with map step 2's text, as one line.
3. **.claude/agents/r2-improver.md**: replace the line starting "Append to `logs/research/<YYYY-MM-DD>.md`: `<UTC HH:MM> | R2" with map step 3's text, as one line. After "end 02 with", add "a last line, plain text, no backticks:".
4. **.claude/agents/r3-fact-checker.md**: replace the step-7 line starting "7. Run `python3 scripts/check_handoff.py <ID>`" with map step 4's first text. Replace the line starting "Append to `logs/research/<YYYY-MM-DD>.md`: `<UTC HH:MM> | R3" with map step 4's second text. Each is one line and contains "orchestrator". The RESEARCH ONLY / 07 paragraph is unchanged.
5. **.claude/agents/i1-reviewer.md**: replace the line starting "Append to `logs/implementation/<YYYY-MM-DD>.md`: `<UTC HH:MM> | I1" with map step 5's text, as one line, with the same "a last line, plain text, no backticks:" addition.
6. **templates/research-handoff.md**: replace the last line, "`python3 scripts/check_handoff.py <ID>` output (pasted, must say PASS):", with "`check_handoff output (run by the orchestrator <YYYY-MM-DD> <HH:MM> UTC, exit <n>; must say PASS):`". This adds the time, as 072/03's paste carries it. `## Self-check` stays, which is the only thing check_handoff reads besides the Fact check section.
7. **README.md** (possible neighbour: 071/074 may add or edit lines in the same scripts list). Anchor: in the line starting "- `scripts/check_handoff.py`", replace "(run by R3, I3, A1)" with "(run by the orchestrator after R1 and R3, and by I3 and A1; item 072)".
8. **tests/test_agent_tools.py** (NEW, replaces 03 step 8's location; stdlib + pytest; `from conftest import REPO`).
   - Helper `agent_tools(text) -> tuple[set[str], str | None]`. It returns the set of tool names with Bash removed if it is in `disallowedTools`, or an error string.
     - Frontmatter = the lines between line 1 `---` and the next `---`; if missing, error "no frontmatter".
     - For `tools:` and `disallowedTools:`, the value is the comma string, or, if empty, the following `- X` lines.
     - The name is `entry.split("(")[0].strip()`.
     - No `tools:` line gives `"no tools: line (inherits every tool incl. Bash, item 072)"`. An empty value with no items gives `"empty tools: (item 072)"`.
   - `test_agent_tools_parser[case]`, parametrized on in-memory strings, 6 cases:
     - (a) no frontmatter → error
     - (b) frontmatter without `tools:` → the no-tools error
     - (c) `tools:` empty, no items → empty error
     - (d) YAML list `- Read` / `- Write` → {"Read","Write"}, no Bash
     - (e) `tools: Read, Bash` plus `disallowedTools: Bash(git push *)` → no Bash
     - (f) `tools: Read, Bash(git *)` → Bash present
   - `test_no_shell_agents_leave_commands_to_orchestrator`:
     - for each sorted `REPO/.claude/agents/*.md`, an error from `agent_tools` fails, naming the file;
     - for each file without Bash, every body line holding `python3 scripts/` must hold `orchestrator`, otherwise it fails with `<file>:<line no>`;
     - the set of no-Bash stems must equal {"r1-researcher","r2-improver","r3-fact-checker","i1-reviewer"};
     - `REPO/.claude/commands/run-item.md` must contain "the orchestrator runs their commands" and "never writes to logs/".

Files planned: 8 (7 changed, 1 new). Not changed: scripts/check_pipeline.py, scripts/check_handoff.py, tests/test_pipeline_check.py, i2/i3/a1 agent files, templates/verification.md.

## Tests and checks
- `python3 -m pytest -q tests/test_agent_tools.py`: 7 passed (6 parser cases + 1 tree test).
- Full suite `python3 -m pytest -q`: base (I2 pastes the count after 071 is built) + 7, no new failures.
- Before-fix probe (I2, before editing the agent files): the tree test fails and names exactly 5 lines: r1 (the "Finish by appending" line), r2 (the "Append to" line), r3 (the step-7 line and the "Append to" line), and i1 (the "Append to" line). This matches 03's count of 5 (I1 re-grepped `python3 scripts/` in .claude/agents/ on 2026-11-18: r1 1, r2 1, r3 2, i1 1; i2/i3/a1 have Bash).
- Mutations, on a scratch copy only, never the repo tree (i3 rule); each must make the tree test fail:
  - m1: restore the old r1 line → fails naming r1.
  - m2: delete r2's `tools:` line → "no tools: line".
  - m3: add `, Bash` to i1's tools → set assert.
  - m4: remove the run-item paragraph → string assert.
  - m5: add `disallowedTools: Bash` to i2 → set assert. This shows disallowedTools is read.
  - m6: turn i1's tools into a YAML list without Bash → still passes. This shows the form does not matter.
- Greps (I3): "each step's agent writes its log line" 0 hits in .claude/; "the orchestrator runs their commands" 1 hit in run-item.md; "Log fields:" 1 hit each in r2 and i1; "run by R3, I3, A1" 0 hits in README.md; "must say PASS before you set READY" 0 hits in r3.
- `python3 scripts/check_handoff.py 072` PASS. `python3 scripts/check_pipeline.py`: 072 not SKIPPED/INCOMPLETE; `LOG TIME:` names none of 071-074; `UNTRACKED CHANGE:` none, because I2 commits the .claude/, templates/ and tests/ changes together with 05 (053); `RULES BRANCH:` / OPEN BRANCHES lines pasted (map step 9).
- I3: state which of 073's branch or this branch run-item.md is built on (run-item item 034). Here, all four items are on daily-fixes/2026-11-18 in order 071 → 074.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 run-item end-of-run sentence reworded | Files 1, anchor A |
| Step 1 new orchestrator paragraph (1)-(5) | Files 1, anchor B (plus C3 repo-root and R1-exit additions) |
| Step 2 r1 line | Files 2 |
| Step 3 r2 line + `Log fields:` | Files 3 (C4 plain-text wording) |
| Step 4 r3 step 7 + log line | Files 4 |
| Step 5 i1 line + `Log fields:` | Files 5 (C4); this file ends with it |
| Step 6 template label + README | Files 6, 7 |
| Step 7 no change to LOG_FORMAT/check_pipeline.py | Not changed (Files list); the existing `test_log_refuses_bad_fields`, `test_log_hints_match_formats` and `test_malformed_log_line_names_expected_format` stay green |
| Step 8 drift test | Files 8 (C1: new file tests/test_agent_tools.py instead of test_pipeline_check.py; C2 parser) |
| Step 9 I3 checks on the branch | Tests and checks, last two bullets |
| D1 option A, B dropped | Files 1-5 (A); no settings/hook change |
| D2 R3 READY gate (a), FAIL = no log, no commit, one loop | Files 1 anchor B (3), Files 4 |
| D3 where fields live | Files 1 anchor B (4), Files 2, 3, 5 |
| D4 orchestrator never writes logs/ or edits a refused line | Files 1 anchor B; pinned by the "never writes to logs/" string assert |
| D5 drift test kept | Files 8 (not dropped: the RI-010 lesson needs a script check) |
| D6 073 overlap | Files 1 note; build order 071 → 072 → 073 → 074 |
| Missing inputs rows 1-7 | Guardrail tests below |

No rule the person follows in 001 (slack, tolerance, cap) changes. No strategy text update is needed.

## Guardrail tests
- Feasibility: the step-8 selector "no-Bash agent files, lines holding `python3 scripts/`" has a dated count in 03 (2026-11-18): 4 of 7 files and 5 lines, 0 of 5 passing today. Pinned by the before-fix probe (exactly 5 named lines fail) and by the set assert (exactly the 4 no-Bash stems, so a 5th no-shell agent or a newly shell-enabled one is a visible RULES change).
- Missing inputs:
  - `tools:` line absent → `test_agent_tools_parser[b]` and mutation m2.
  - Frontmatter absent → `[a]`.
  - Empty `tools:` value → `[c]`. Never read as "no Bash".
  - `disallowedTools` present → `[e]` and m5.
  - check_handoff FAIL after R3, `sources count` missing after R1, `Log fields:` line missing, `--log` exit 2, no READY/BLOCKED on the Status line: these are orchestrator actions with no script of their own. The script side is already pinned. `--log` refuses a malformed or empty field with exit 2 and writes nothing (`test_log_refuses_bad_fields`, `test_malformed_log_line_names_expected_format`), so a missing or rebuilt-wrong field cannot enter logs/. A missing R1/R3 line shows as INCOMPLETE (043 tests). DROPPED as new tests: the orchestrator is the main session, not a script, and the outcome (no line, or a refused line) is already caught by INCOMPLETE and the `--log` tests.
  - Commit times absent (no git) → `test_log_time_not_checked_outside_git` (existing).

## Expected result
- run-item.md states one way: the orchestrator runs `check_handoff` and `--log` for R1, R2, R3 and I1, one step at a time from the repo root, in the order file → check_handoff → `--log` → commit. It never types or edits a line. I2, I3 and A1 run their own commands.
- The four no-shell agent files no longer tell the agent to run a command. Each `python3 scripts/` line names the orchestrator, and R2/I1 end their files with `Log fields:`.
- tests/test_agent_tools.py: 7 passed. It fails if an agent file without Bash tells its agent to run a script itself, if a `tools:` line goes missing, or if the set of no-shell agents changes.
- `check_pipeline.py`: `LOG TIME:` none for 071-074, 072 not INCOMPLETE. The PR is a RULES BRANCH, so the person must approve it.

Recurring issues checked (item 013), against this plan:
- RI-001 (ESCALATED): the one selector has a dated count (4 of 7 files, 5 lines; I1 re-grepped and got the same) and is pinned by the before-fix probe and the set assert.
- RI-002 (GUARDED): every absent input blocks with a named error. An empty or missing `tools:` is never read as "no Bash", and a missing field is never rebuilt.
- RI-007 (GUARDED): Scope FULL, I1-I3 run; I2 commits the code paths with 05.
- RI-009 (GUARDED): shared files named (run-item.md with 073; README.md possibly with 071/074); the test was moved out of test_pipeline_check.py to avoid 071.
- RI-010 (GUARDED): the text duty gets a script check (Files 8). INCOMPLETE and LOG TIME are unchanged.
- RI-004/RI-005: the I1 field below was checked against the I1 regex: "FIT WITH CHANGES | 8 files planned" matches `(FIT|FIT WITH CHANGES|NOT A FIT) \| \d+ files planned\b.*`.
- RI-006: the file count is listed (7 changed + 1 new = 8).
- Not applicable: RI-003, RI-008 (stdlib, no new syntax), RI-011, RI-012, RI-013.

Log fields: FIT WITH CHANGES | 8 files planned
