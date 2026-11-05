# 01 Research brief - 043
## Question
Can a template field and a script check make I3's step-0 list and every step's log line hard to skip?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- 040's 06 names no RI entry and no check_pipeline line [work/040/06-verification.md]
- 013–016's 06 name no RI entry [grep -ci 'recurring|RI-' work/01[3-6]/06-verification.md → 0]
- i3 step 0 and step 2 require them [.claude/agents/i3-verifier.md]
- 040's R1/R3/I3 have no log line [grep -rn 040 logs/ → only I2]
- templates/verification.md has no field for either [templates/verification.md]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (RI-002, RI-007, RI-009, RI-010).
## Numbers used (show the math)
Log line form `HH:MM | <agent> | <ID> |`; agents by step: 01 R1, 02 R2, 03 R3, 04 I1, 05 I2, 06 I3. Items checked: 041 and later (first after the rule is enforced).
## Fit for a ~$3k account
Process only; no trading, no cost.
## Open questions
None.
