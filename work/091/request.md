# Work item 091
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-21
## What we want
Small test and process hardening from today's per-item audits (080, 081, 084, 086), in one item:
1. 081 F1: mutations A1-A3 (drop RESEARCH_CODE_PATHS / RULE_PATHS / RECURRING from the unrelated-branch ls-tree list), A8/A9 (drop `isinstance(branches, str)` / `isinstance(ahead, str)` from the exit code), A13 (`next_id` treats a failed per-branch ls-tree as empty) survive all tests: R2-c per checked-path group, a patched-git test per exit-code term, a `--next-id` refusal test.
2. 086 F3: rule C ignores runs under `### Test output (round 2 ...)` headings; template rule for round headings or read them.
3. 086 F4: the orchestrator commits the shared daily log file whole, so one item's commit can carry another item's line (91ade51 carried 081's I3 line → transient INCOMPLETE). Stage only the item's own lines (run-item.md sentence + a helper).
5. 082 A1 F1: `RECORDED.fullmatch` → `.match` in `_recorded_marker` survives tests/test_probe_guardrails.py; fixture `"2026-01-01: 1 failed, 1 passed x"` → `(recorded unreadable)`. The unshallow sentence (3 copies) doesn't name 084's RULE NOT SEEN not-checked form.
4. Shared scratchpad: two agents overwrote each other's mutation scripts (work/081/06 round 1). run-item.md: every agent uses a uniquely named scratch dir.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-21-081.md F1; logs/audit/2026-11-21-086.md findings 3-4; logs/audit/2026-11-21-082.md findings 1-2; work/081/06-verification.md round 1 "Process issue".
## Recurring issue link (RI-#, if any)
RI-009/RI-014 (1), RI-010 (2, 3), RI-007 (4).
## Done looks like
Each sub-point has a fixture or a pinned rule line, and a mutation that fails it.
