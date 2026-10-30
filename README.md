# Covered-call agent teams

Three teams of Claude Code agents that research, build, and audit your covered-call strategy and tools, with every hand-off written to a file so nothing is lost or made up.

## The flow

```
 You or A1 open a work item (work/<ID>/request.md)
        |
 RESEARCH   R1 Researcher -> R2 Improver -> R3 Fact Checker
        |                                  (writes the implementation map)
 IMPLEMENT  I1 Reviewer -> I2 Builder -> I3 Verifier
        |                                  (audits I1 + I2, sends audit task)
 AUDIT      A1 Auditor: per-item review + daily review of all logs
        |
        +--> bugs/errors       -> new BUG item + prevention guardrail -> back to R1
        |                         and logged in logs/recurring-issues.md
        +--> small improvements -> new EFFICIENCY item -> back to R1
```

| Agent | Job | Writes |
|---|---|---|
| R1 Researcher | Sourced research on the topic | `01-research.md` |
| R2 Improver | Past logs + 3 for, 3 against, pitfalls, searching English, Mandarin, Spanish, Japanese + 3 rotating spoken languages | `02-improvements.md` |
| R3 Fact Checker | Checks every claim and number, removes anything unsupported, maps the build | `03-handoff.md` |
| I1 Reviewer | Fit check for a ~$3k account, a bit more research, build plan | `04-build-plan.md` |
| I2 Builder | Builds it; checks every path leads somewhere | `05-build-report.md` |
| I3 Verifier | Audits I1 and I2, re-runs tests, sends audit task | `06-verification.md`, `07-audit-task.md` |
| A1 Auditor | Per-item audit; daily log review; sends bugs and efficiency ideas to Research | `logs/audit/`, `logs/efficiency/` |

## Layout

- `.claude/agents/` - the seven agent definitions
- `.claude/commands/run-item.md` - `/run-item <ID>` runs one item through all seven steps
- `.claude/commands/daily-audit.md` - `/daily-audit` runs the daily review
- `templates/` - the hand-off format for each step
- `work/<ID>/` - every file for one item, numbered 01 to 07
- `logs/<team>/<date>.md` - one line per agent action, read by R2 and A1

## Safety rules built in

- No made-up facts: unsourced claims are marked UNVERIFIED and R3 strips them before build.
- No live trading: I2 uses sample or paper data only unless you say otherwise.
- Every error found goes back with a guardrail so it can't reappear. Repeats are tracked in `logs/recurring-issues.md`, and anything seen 3+ times is escalated to you.
- Loops stop after 3 send-backs on the same step and come to you.

## How to use

1. Put this folder in a GitHub repo and open it in Claude Code.
2. Create `work/001/request.md` from `templates/request.md`, e.g. "Build a strike picker for 30-45 day calls around 0.30 delta on stocks under $30".
3. Run `/run-item 001`.
4. Run `/daily-audit` once a day, or schedule it.
