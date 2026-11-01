---
description: Run one work item through Research -> Implementation -> Audit
argument-hint: <work item ID>
---
Run work item $ARGUMENTS through the pipeline, one agent at a time, in this order:
r1-researcher -> r2-improver -> r3-fact-checker -> i1-reviewer -> i2-builder -> i3-verifier -> a1-auditor (per-item mode).

If `request.md` says `Scope: RESEARCH ONLY`, stop after r3-fact-checker: R3 writes `work/$ARGUMENTS/07-audit-task.md` (what A1 should check in 01-03), then run a1-auditor (per-item mode). Missing 04-06 files are expected for these items. If there is no Scope line, treat it as FULL.

If `request.md` says `Scope: FAST (person, <date>)` (the person asked to go faster), R2 and I1 may be skipped; R3's fact check and I3's verification never are. Nobody else may shorten the pipeline. A step that is waived after the fact is listed on a `Waived: <steps> (<who>, <date>: <why>)` line in request.md, which the person sees in review. Only the person may waive 03 or 06 (`<who>` = `person`); `scripts/check_pipeline.py` reports any other waiver of them as SKIPPED (item 031).

Before each step, confirm the previous step's file exists in work/$ARGUMENTS/. No file for the person (a summary, a screen, a code change) is written or merged before the step that checks it. At the end, run `python3 scripts/check_pipeline.py`: the item must not show SKIPPED. If a step returns BLOCKED, NOT A FIT, or FAIL, send the item back to the step named in that file and continue from there. Stop after 3 loops on the same step and report to the person.
