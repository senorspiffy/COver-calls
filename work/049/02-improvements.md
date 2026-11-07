# 02 Improvements - 049
## What past logs say
- RI-010 (ESCALATED, now 4): each earlier guardrail checked the lines but not the conditions they were written under. 045 added the check; 048 was built where the check didn't exist yet.
- RI-009 root cause: "new branches are built without the rules open PRs add". 034 fixed this only for branches that change the same file.
- LEGACY (021) and PRE_A1_LINE (033/035) show closed, named exception lists work and stay closed.

## 3 ways FOR
1. A `RULES BRANCH:` line printed by `check_pipeline.py` puts the warning in front of the builder at the start of run-item (which already runs the script after `git fetch origin`) and in A1's daily output, no hand check needed.
2. A named exception for 048's times is honest: the times can't be recovered; re-typing them would be another guess. The output still shows 048 and why.
3. Fixing the I1/I2 fields from 04/05 makes 048's log lines match its files, which is what A1 checks.

## 3 ways AGAINST
1. A closed exception list can grow. Reasoning: same "Never add a new item here" comment and a test that pins the list to {048}, as with LEGACY.
2. `RULES BRANCH` is information, not an exit code, so it can be ignored. Reasoning: making it exit 1 would turn every day with an open rules PR red, which is the normal state while the person reviews. The run-item rule makes it binding for builders; A1 lists it at the top.
3. CI is left out. Reasoning: CI would show a red main at merge, but it needs an outside service and a token that can push workflow files, and the person hasn't asked for one. The daily audit catches a red main within a day. Name CI in the PR as an option for the person.

## Findings by language
Languages: N/A (no new external claims). The fix is a check inside this repo's own scripts and agent text: no fee, rule or market fact changes.

## Holes to watch out for (summary)
- Editing 048's I1/I2 lines moves their blame to the new commit, so LOG TIME would stop flagging those two even without the exception. The exception must cover all six lines, and a test should show that a re-committed line is no longer checked (a known gap, written down, not fixed here).
- `RULES BRANCH` must ignore a branch already merged (open_branches only lists `--no-merged`).
- Answer to R1's open question: in-repo check now; CI as the person's choice.
