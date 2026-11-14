# 02 Improvements - 051
## What past logs say
- 034, 037, 039 built OPEN BRANCHES for unmerged fix branches; none of them considered a fix branch that main has moved past (their fixtures run on main).
- 047, 050 (EFFICIENCY): small output changes to check_pipeline.py merged without trouble.

## 3 ways FOR
1. Removes a false item-036 warning that shows on every fix branch after each daily audit commit.
2. `MAIN AHEAD` names the right next step (merge main), which run-item's build-on-top rule does not cover.
3. Mirror branches (thread branches sitting on a main commit) stop cluttering the list.

## 3 ways AGAINST
1. A branch already in main could still carry items HEAD lacks, and IN PR would miss them. Reasoning: such items are in main; MAIN AHEAD tells the fixer to merge main, after which they show normally.
2. Dropping main from `--next-id` would let a branch reuse an ID main just took (today's 051 is on main only). Reasoning: answer to R1's question: leave `next_id()` unchanged.
3. Repos without `origin/main` (tests, forks). Reasoning: if `origin/main` does not resolve, behave as today.

## Findings by language
Languages: N/A (no new external claims). Wording and logic of a repo script only.

## Holes to watch out for (summary)
- Keep `--next-id` counting main.
- No `origin/main` → unchanged output.
- On main itself (main merged into HEAD) nothing changes.
