---
description: Run one work item through Research -> Implementation -> Audit
argument-hint: <work item ID>
---
Run work item $ARGUMENTS through the pipeline, one agent at a time, in this order:
r1-researcher -> r2-improver -> r3-fact-checker -> i1-reviewer -> i2-builder -> i3-verifier -> a1-auditor (per-item mode).

Before each step, confirm the previous step's file exists in work/$ARGUMENTS/. If a step returns BLOCKED, NOT A FIT, or FAIL, send the item back to the step named in that file and continue from there. Stop after 3 loops on the same step and report to the person.
