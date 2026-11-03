# 02 Improvements - 027
## What past logs say
See `logs/audit/2026-10-31.md` and `logs/recurring-issues.md` (RI-008 occ 1).
## 3 ways FOR
1. The guardrail script works on every supported Python.
2. The test catches it on 3.12+ machines too.
3. Cheap: stdlib tokenize.
## 3 ways AGAINST
1. Relies on 3.12 tokenizer tokens (falls back to compile on older).
2. Other 3.12-only syntax (e.g. `type` statements) isn't covered.
3. Could instead raise requires-python, but the VPS version is unknown.
## Findings by language
Languages: N/A (no new external claims). This fix changes code, counts, wording or process inside this repo only, so no outside source in any language could confirm or contradict it.
## Holes to watch out for (summary)
See AGAINST list.
