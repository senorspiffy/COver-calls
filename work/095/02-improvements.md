# 02 Improvements - 095
## What past logs say
- RI-014 (logs/recurring-issues.md L152-158) is OPEN with 1 occurrence. The 2026-11-22 note lists this item as a near miss, not counted: "shallow 083 INCOMPLETE / merged-branch BRANCH ERROR → 095". The GUARDED condition is "merged and M11 fails on main". M11 (`shallow = False` in main) fails `test_shallow_three_readers_not_checked` (T18) and `test_shallow_docs_only_orphan_exit_0` (T19) (logs/audit/2026-11-22-090.md L55, L60). So 095 has to change T18, which is the test the GUARDED condition depends on.
- Source of the item: logs/audit/2026-11-22-090.md F3 (L121-128) and the real-clone probe (L64-87). A1 marked both as pre-existing (084/088) and not caused by 090. The 28-ref count comes from one probe on 2026-11-22 (L74-76) and was not re-run here (no shell).
- The rule text contradicts itself today. I read .claude/agents/a1-auditor.md L22-23 in this checkout:
  - L22 says that in a clone that stays shallow, A1 must "report ... OPEN BRANCHES and RULE NOT SEEN as 'not checked', never 'none'".
  - The same L22 says "Every SKIPPED or INCOMPLETE item ... is an error".
  - L23 says every `BRANCH ERROR:` line goes at the top of the report.
  - So the 083 entry, and each of the 28 refs, is "not checked" by one sentence and an error by the next.
- Code facts I checked (R1's line numbers hold on this branch):
  - `_rule_seen` returns `(None, "")` when env is set (scripts/check_pipeline.py L827-828).
  - It also returns `(None, "")` when the step file is not committed yet (L835-836, `if not sha: return None, ""`). The two cases look the same to the caller.
  - The shallow branch error text is built at L1449-1453.
  - Each error is printed as its own `BRANCH ERROR:` line (L2041-2043), and `branch_errors` makes the exit 1 (L2087).
- Precedent from 090 (work/090/02 AGAINST 1): pick the exit code on purpose and assert it in the fixture.
- Precedent for languages: 079, 084, 086 and 090 work on the same checker and the same topics, and all were logged `languages: N/A` (work/090/02 L16, L80).

## 3 ways FOR
1. **It fixes a contradiction in the rule text, and it does so with fewer lines, not more.**
   - Reasoning chain: a1-auditor.md L22 already calls OPEN BRANCHES and RULE NOT SEEN "not checked" in a clone that stays shallow. But the output those two cases cause (the gated INCOMPLETE entries, and one BRANCH ERROR per ref) is called an error by L22's next sentence and by L23 (see "What past logs say").
   - The fix makes the output match a rule that already exists:
     - (A) Gated entries carry a `not checked (shallow clone)` label.
     - (B) The no-merge-base refs fold into one line.
   - Measured on 2026-11-22 (A1's probe, 090 audit L74-76): 28 × 2 = 56 lines become 1 line. That is the 56 lines from 01 "Numbers": one OPEN BRANCHES sub-line and one BRANCH ERROR for each of the 28 refs.
   - Why this matters for A1: L23 asks for every BRANCH ERROR at the top of the report. With 28 of them, a real one is lost in the list. That is the "teaches A1 to ignore exit 1" cost from 01 "Fit".
2. **(A): use one helper keyed on `env`, not on `seen is None and sha7 == ""`. That gives a single mutation point and avoids a wrong label.**
   - Reasoning chain: `_rule_seen` gives `(None, "")` both when env is set (L827-828) and when the step file is not committed yet (L835-836).
   - If the label is keyed on the return value, an item being built in a full clone (05 or 06 written but not yet committed) gets "not checked (shallow clone)" in a repo that is not shallow. That is a wrong reason, the RI-014 / 089 "wrong UNTRACKED CHANGE reason" shape.
   - Fix: one function, for example `_gate_note(env)`, returns `f"rule seen not checked: {env}"` when env is set and `""` otherwise. All 7 gate sites (01 Numbers: L916, L922, L938, L963, L977 ×2, L994) append that note.
   - Mutation: make the helper return "" → the depth-1 fixture (a) fails at every site at once. This matches 090 FOR 3 ("one `env` value ... a single mutation point").
   - Keying on env also answers Open question 2 for free. "no git" and "unborn HEAD" get their own accurate label (`rule seen not checked: unborn HEAD`) and no extra code (01 A11).
3. **(B): fold only in main()'s printing, and build on 094's change to the same function.**
   - Reasoning chain: `scripts/check_handoff.py` L95-96 calls `open_branches()` and reads the per-ref dicts (01 B8). If the fold happens inside `open_branches`, that dict shape changes, and so do T19 and check_handoff's `_branch_with_handoff`.
   - Folding at L2017-2021 and L2041-2043 leaves the dicts as they are:
     - Collect the `unrelated and shallow` refs.
     - Print one `OPEN BRANCHES` sub-line with the count, then the names.
     - Print at most one summary BRANCH ERROR for the ones that hold checked paths.
   - Keep the names, not just a count (01 Open question 4). T18's `origin/claude-x` is an open branch in the full clone (test L4434: "items none; merges cleanly"). In depth 1 it looks exactly like the merged refs. The name is the only way A1 can see that an expected open branch is in the folded set.
   - 094 changes `open_branches` and the same rule sentence (work/094/01 #22-24, Open question 1). Its single-branch state may come back as a string, which main() already prints at L2011-2012. A fold that only touches the list branch of main() does not collide with that. I1 should still build on whichever of the two lands first (01 B9).

## 3 ways AGAINST
1. **Exit-code trap: the fold cannot tell merged refs from open ones, so making the folded line exit-neutral can hide a real open branch.**
   - Reasoning chain: in a shallow view, "no merge base" covers three cases: merged, open and branched before the boundary, or unrelated (01 G5, B6). T18's fixture shows it: an open branch (`origin/claude-x`) is a BRANCH ERROR in depth 1, just like the merged ones.
   - If the folded line follows T19's precedent ("not-checked lines never change the exit"), a shallow run where an open branch skips a step exits 0. The only remaining signal is one text line. That is the RI-002 shape (an unknown read as a pass).
   - The request's evidence complains that the run "exits 1 every time". Its Done line asks only for "one not-checked branch line" and does not mention the exit.
   - Suggested choice, for the person to confirm at PR review:
     - Keep exit 1 while at least one folded ref holds checked paths (as today, but from one summary `BRANCH ERROR` line).
     - Add to a1-auditor.md that in a clone that stays shallow this one line is "not checked", not an error.
     - Either way, T18 must still assert the exit code.
2. **(A) labels real failures as well as false ones, and in a depth-1 clone that means every gated entry.**
   - Reasoning chain: with env set, no gate can tell an item built before the rule (false entry, 01 A9) from one built after it (real failure).
   - In depth 1, every anchor would be the boundary commit (01 G8, derived, UNVERIFIED by probe). So every gated entry gets the label, including a real new failure in a recent item.
   - If labelled entries also stop setting the exit (01 Open question 1, option ii), a recent item's real Sent-back-line or Suite failure becomes exit 0 in a shallow clone. That is the same hole as AGAINST 1.
   - Option (i) avoids it: the entry stays in `INCOMPLETE:` with the label, and the exit stays 1. A1 L22 then says a labelled entry is "not checked; unshallow and re-run".
   - Option (i) does not meet "no false INCOMPLETE" literally, because the entry still sits on the INCOMPLETE line. I1 has to pick one and say so in 04.
   - A finer test would help: only label when the anchor commit is itself a shallow boundary (`_shallow_boundaries`, L1569). For a deeper shallow clone, recent items would then get exact answers. This is derived only: no git source says `--diff-filter=A` on a non-boundary commit equals the full-clone answer (UNVERIFIED). Leave it as a follow-up and do not build it here.
3. **Cost and guard risk: RULE_PATHS edits for a near miss, on the test that RI-014's GUARDED condition depends on, overlapping two other items built the same day.**
   - Reasoning chain:
     - RI-014 has 1 counted occurrence, and this is a near miss (recurring-issues L153).
     - The change touches scripts/check_pipeline.py, tests/test_pipeline_check.py and three rule files (a1-auditor.md L22, run-item.md L12, maybe daily-audit.md L4). All of them are RULE_PATHS, so the person's OK is needed (01 "Fit").
     - T18 is the M11 probe for RI-014 (090 audit L55-61). If T18 is edited and its new assertions no longer depend on `shallow`, M11 stops failing and the GUARDED evidence is lost without anyone noticing.
     - 094 (single-branch) and 092 (check_handoff shallow reads) change the same function, the same rule sentence and the same reader on the same day (01 B9). Three edits to a1-auditor.md L22 is the RI-010-style "each fix opens the next gap" pattern (work/090/02 "What past logs say").
   - Fix:
     - Re-run M11 after the change and record which tests fail in 05.
     - Add the two new fixtures with their own mutations (label off, fold off) as 01 "Numbers" says.
     - Write the rule sentence once, together with 094's single-branch sentence, rather than in two separate edits.

## Findings by language
Random languages this cycle: N/A
Languages: N/A (no new external claims). 095 is an EFFICIENCY change to this repo's own checker output and rule wording: a label on gated INCOMPLETE entries, one folded branch line, and rule-text sentences. It adds or changes no fee, market rule, statistic or trading behaviour. The only outside facts are git behaviours (shallow, clone, branch, merge-base, fetch) that R1 already cited to git-scm.com. Same precedent as 079, 084, 086 and 090.

## Holes to watch out for (summary)
- Key the (A) label on `env is not None`, never on `seen is None and sha7 == ""`. An uncommitted step file in a full clone also gives `(None, "")` (L835-836).
- Cover all 7 gate sites with one helper, and check them by grepping `_rule_seen(`.
  - The LOG BATCH site (L942-943) adds its note only `if sha7 not in missing`. The label must not be added twice for one item.
- Pin the exit code in both new fixtures and in the edited T18. After the change, M11 must still fail T18 (or its replacement) by name.
- The fold must keep the per-ref names. The full-clone output must be byte-for-byte unchanged (Done line). Use the existing full-clone control in T18 (L4429-4434).
- The fold must not touch the `isinstance(branches, str)` path (L2011-2012). 094 may use it for single-branch clones.
- check_handoff.py reads the per-ref dicts (L95-96). Fold only in main() printing.
- Entries not behind a gate (no log line, no RI line, unreadable files; 01 A8) must stay unlabelled errors in a shallow clone.
- The 28-ref and 083 facts come from one A1 probe on 2026-11-22. A fixture should use its own counts (for example 2 merged refs + 1 open ref → one line naming 3).
- Rule text: a1-auditor.md L22 and run-item.md L12 should name "INCOMPLETE entries labelled `rule seen not checked`" and "the folded shallow OPEN BRANCHES / BRANCH ERROR line". Say whether each one is an error or "not checked".
- Open for the person at PR review: should a run in a clone that stays shallow still exit 1 (AGAINST 1, 2)?

Log fields: 3 for / 3 against | languages: N/A
