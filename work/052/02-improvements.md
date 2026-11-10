# 02 Improvements - 052
## What past logs say
- 034, 037, 038 built OPEN BRANCHES, ID CLASH and BRANCH SKIPPED on `HEAD...ref` and one merge base; their fixtures have a single merge base.
- 049 added RULES BRANCH on the same diff and the "build on top of the open branch" rule. Following that rule (051 on PR #15, then PR #15 merged) is what made today's two merge bases.
- 051 (PR #16) also changes `open_branches()`; this item is built on top of it.

## 3 ways FOR
1. The merge-tree result is exactly what merging the branch would change, so items, the 036 note and RULES BRANCH can't pick up a merged PR's work, whatever the history shape.
2. `merge-tree` already runs for CONFLICTS; reusing its tree adds one `git diff` per branch and no new git call type.
3. ID CLASH checked against every merge base avoids a false clash when the request exists in one base but not the other.

## 3 ways AGAINST
1. A branch whose change is already on HEAD (same content) is no longer listed for that file. Reasoning: correct, merging changes nothing there.
2. git < 2.38 has no `--write-tree`. Reasoning: keep `HEAD...ref` as a fallback when merge-tree fails (the CONFLICTS line already shows unknown then).
3. Conflicted files in the merge tree carry markers and show as changed. Reasoning: correct, the branch does change them; CONFLICTS lists them too.

## Findings by language
Languages: N/A (no new external claims). Logic of a repo script and git behaviour from git's own docs.

## Holes to watch out for (summary)
- Fallback to `HEAD...ref` when merge-tree fails.
- Test must build a real criss-cross (two merge bases) and fail with the old diff.
- 051's MAIN AHEAD and next-id behaviour unchanged.
