# Work item 112
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-26
## What we want
109's `*_FROM` census also checks each kill's `[param id]` against collected ids, and a behaviour test pins S7's documented FROM-1 equivalence.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-26-109.md follow-ups 1-3 (PR #39): census checks only the test function name, so a misspelled param id passes (all 33 real ids exist today); S7(b) equivalence is argued in 05/06 but not pinned; a cutoff used through a local alias or attribute would escape the census (none today).
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY). Proposal: resolve full ids via pytest collection or parametrize ids in the ast walk; one test showing S7 at FROM-1 gives identical output; census note or check for aliased use.
## Recurring issue link (RI-#, if any)
RI-001 (near miss in 109: `_defective` fixture shape not run before FIT), RI-010.
## Done looks like
A misspelled param id fails the census; S7 equivalence has a named test; alias case documented or checked.
