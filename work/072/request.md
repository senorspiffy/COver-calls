# Work item 072
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-18

## What we want
The rules match how the pipeline really runs: R1, R2, R3 and I1 have no shell (tools: Read, Write, Glob, Grep, Web), so they cannot run `check_pipeline.py --log` or `check_handoff.py` as run-item.md and their agent files say. Either the orchestrator's role is written into run-item.md (it runs `--log` and `check_handoff` right after the step's file exists and pastes the output), or those agents get Bash.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- Items 069 and 070 (2026-11-17/18): every R1-R3/I1 agent reported it could not run `--log` or `check_handoff`; the orchestrator ran them (logs/research/2026-11-17.md, logs/implementation/2026-11-18.md; `LOG TIME: none`).
- logs/audit/2026-11-18-069.md: "fits the rules' intent ... doesn't fit the wording, which says the agent itself runs them."
- .claude/commands/run-item.md: "each step's agent writes its log line with `check_pipeline.py --log`".

## Done looks like
One documented way, applied in run-item.md and the four agent files; no hand-typed lines; check stays `LOG TIME: none`.
