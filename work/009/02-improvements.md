# 02 Improvements - 009
## What past logs say
See `logs/audit/2026-10-31.md` and `logs/recurring-issues.md` (none).
## 3 ways FOR
1. The reader sees the real cause.
2. One function decides both NaN and the text, so they can't drift.
3. Each cause has its own test.
## 3 ways AGAINST
1. One more key in the walk-forward result.
2. Old saved results lack it (report falls back to 'reason not recorded').
3. Text is longer when several causes hold.
## Findings by language
Languages: N/A (no new external claims). This fix changes code, counts, wording or process inside this repo only, so no outside source in any language could confirm or contradict it.
## Holes to watch out for (summary)
See AGAINST list.
