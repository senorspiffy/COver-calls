# 01 Research brief - 047
## Question
How should `scripts/check_pipeline.py` catch a research/implementation log line whose item ID has no work item, both when `--log` writes it and when the daily check reads the logs?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- No external facts needed: the change is inside this repo's own scripts. Sources are repo files and commands.
- `write_log()` (scripts/check_pipeline.py, item 045) checks the agent, a 3-digit ID and the fields, but never looks at `work/` [repo: scripts/check_pipeline.py `def write_log`].
- A1 probe 2026-11-06 on PR #12's code: `--log I2 999 "1 file changed | tests 1/1"` → exit 0, line written; `check_pipeline.py` then prints no line naming 999 and exits 0 [work/047/request.md, Evidence].
- `LOG_LINE` (`^HH:MM | R1..I3 | <3 digits> | ...`) already parses every agent line; it is the parser `incomplete()` and `late_log_lines()` use [repo: scripts/check_pipeline.py].
- Every agent log line on main today has a `work/<ID>/` folder (A1 loop over logs/research/*.md and logs/implementation/*.md, 2026-11-06: no orphan). So a new `ORPHAN LOG` check starts at `none` and needs no LEGACY list.
- The agents run `--log` "right after writing your step file" (r1-researcher.md … i3-verifier.md), and `request.md` is written before R1 runs (run-item.md). So refusing `--log` when `work/<ID>/request.md` is missing never blocks a correct step.
- A1's daily job B asks "Is every log line backed by a file in `work/`?" by hand [repo: .claude/agents/a1-auditor.md].

## Numbers used (show the math)
- Agent log lines on main: every ID found in logs/ has a folder → 0 orphans (start value of the new line).

## Fit for a ~$3k account
Process only; no trading rule or number changes.

## Open questions
- Read the logs from the working tree (any line, committed or not) or only committed ones? The working tree is simpler and catches a typo before commit; R2/R3 to weigh.
