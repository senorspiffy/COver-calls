# 07 Audit task - 111
I3 result: PASS (round 1). Head: 7b11624 (I2), plus I3's 06/07 commit. Branch daily-fixes/2026-11-26, shared with 112/113.

What A1 should look at:
1. **Unpinned R-A sub-conditions (survivors I3b, I3c; 06 "Survivor shapes").**
   - In `_frontmatter_error`, R-A is `if dash and not op and not sb and not is_key:` followed by `prev = (dash[-1], False)`. Two mutants survive all 173 tests:
     - dropping `not sb`;
     - `dash[-1]` → `dash[0]`.
   - Both turn today's fail-closed result (INDENT or SEQ_LEVEL) into a tool set on files that both PyYAML loaders reject. This is the RI-002 direction.
   - Shapes: `hooks:` / `- |` / `  x` / ` b`, and `hooks:` / `- - a` / `  b`.
   - Decide whether this is a follow-up item. Two fixtures would pin them: `- |` / `  x` / ` b` → INDENT(5) and `- - a` / `  b` → SEQ_LEVEL(4).
   - Re-run both mutants with the RI-015 env guard.
2. **Missing negative (survivor I3e).**
   - The mutant changes `kind = "map" if lv == col and is_key` to drop `is_key`, and it survives.
   - Its distinguishing shapes load in both loaders: `a:` / `  b` / `  - x` folds into "b - x". The build passes them, which is correct; the mutant gives a fail-closed false MAP_ITEM.
   - Decide whether a negative fixture is wanted.
3. **Fifth tool-set path.**
   - The docstring still says "Not checked (YAML's reading not checked): the same no-colon line after a flow scalar item."
   - I3 measured `- [a]` / `  b`: both loaders raise (ParserError on PyYAML 6.0.1 pure and on 6.0.3 Safe and CSafe), and the build returns {Read, Write}.
   - It belongs with 04 C2's four "Known passes" (`- "a"` / `  b`, `- a # c` / `  b`, `  a:` / `    b: c` / `  - x`, `a:` / `  b` / `  c: d`). Together they are follow-up candidates (RI-002 near miss, not counted).
4. **Mutants not re-run by I3.** M56-M72, M76-M81 and X1-X4 rest only on I2's run (05 Tests 5), including M64's adapted form (`prev = (ind, op)` in R-A's `else:`). Spot-check at least M64 and X4. X4 has the new id q30.
5. **Exact text.** 06 shows that 03's "Step 3 code" block appears verbatim in the file, once, and that the docstring holds 03 step 4 plus 04 C2 word for word. Confirm on the merged head.
6. **Both PyYAML runs.** `-I` (6.0.1 pure, CSafeLoader not measured) and the user site (6.0.3, libyaml). I3's verdicts equal 04 Extra research 2 and 05's table. Check this once more on the head.
7. **Suite and pipeline on the branch after 112/113 land.** I3 measured 1081 passed, 1 skipped at 7b11624, the same as 05. Re-run on the final branch head, and check that `check_pipeline.py` shows 111 with no SKIPPED, INCOMPLETE, LOG TIME or LOG BATCH entry.
8. **RI-002 status for logs/recurring-issues.md (A1 copies it on main).** Near miss closed by 111: g1/g2/g4 → VALUE, er1 → SEQ_LEVEL, d3/k2 → MAP_ITEM, pinned by M82/M83/M84. The residuals are points 1 and 3.
