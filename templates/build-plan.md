# 04 Build plan - <ID>
Fit verdict: FIT | FIT WITH CHANGES | NOT A FIT
## Extra research (with sources)
## Files to create/change
## Tests and checks
`RULES BRANCH:` lists only remote branches not merged into HEAD (`git branch -r --no-merged HEAD`), so on this branch's own checkout it normally reads `none` and does not name this branch's or its base branch's rule change; if it does name this branch, the remote has commits this checkout lacks (fetch and compare). To see the rule files this branch and its unmerged base change, run `git diff --stat origin/main...HEAD -- .claude templates scripts/check_pipeline.py scripts/check_handoff.py`; never switch this checkout to origin/main (item 113).
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
## Guardrail tests
- Feasibility: <rule> → <test pinning its count>
- Missing inputs: <input> → <absent-case test>
## Expected result
