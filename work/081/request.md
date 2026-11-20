# Work item 081
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-20

## What we want
Every check in scripts/check_pipeline.py treats a failed git command as "not checked (<why>)" or an error, never as "nothing found"; and git output that is not UTF-8 never crashes the script.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/audit/2026-11-19-079.md P1 (branch head 2977b96, malformed shallow file so every git command fails): `LOG TIME: none` with a late log line present; the OPEN BRANCHES line disappears; `--next-id` gives 080 instead of 100 (a new item would clash with an open branch). Code: `late_log_lines`, `open_branches`, `next_id` read a failed `_git` as empty.
- Same report P2 / work/079/07: one non-UTF-8 byte in `.git/shallow` → traceback from `_git` (strict decode). Base 7b09a8a crashes the same way.

## Root cause and prevention guardrail (BUG only)
Root cause: `_git` failures are handled per call site and three call sites fall through to the empty result (RI-002/RI-014 family: uncomputable turned into "none").
Guardrail: one helper that returns (out, ok) and a lint-style test that every `_git(` call site checks ok; fixture repo where git fails for all commands asserts no line says "none" and `--next-id` refuses; `errors="replace"` decode with a test.

## Recurring issue link (RI-#, if any)
RI-014 (checker result depends on git state). Found by A1 probe, never hit in a real run; not counted (precedent 069/070).

## Done looks like
All-git-fails fixture: LOG TIME / OPEN BRANCHES / --next-id say not checked or exit non-zero; non-UTF-8 fixture runs without a traceback; mutations fail named tests.
