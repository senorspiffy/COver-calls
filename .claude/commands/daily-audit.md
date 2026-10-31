---
description: Daily audit of all logs by the Audit & Efficiency team
---
Use the a1-auditor agent in daily-review mode for today's date. It runs `python3 scripts/check_pipeline.py` and `python3 scripts/check_handoff.py --all`, and puts the STUCK items (request.md only, 1+ day old) at the top of the report with a question to the person: which to run. Then list any new BUG and EFFICIENCY work items it opened, and run each through /run-item.
