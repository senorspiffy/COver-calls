# 03 Research hand-off - 071
Status: READY

All repo claims were checked by reading the files on daily-fixes/2026-11-18 (2026-11-18), with Read/Grep/Glob. I had no shell, so no code was run. Every count below comes from Grep/Glob output. I3 re-measures each one with the built code (RI-001). The one URL was fetched.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 F1: classify() reads 06 only to check it exists. Its only verdict reading is 07's `A1 result:` | scripts/check_pipeline.py L302, L315-323 | VERIFIED | - |
| 01 F2: with 01-06 present and no 07, classify returns `in progress (FULL: next 07)` | check_pipeline.py L324 | VERIFIED | - |
| 01 F3: A1 FAIL is anchored `^A1 result:\s*(\w+)` with re.M, and the last match decides | check_pipeline.py L317-323 | VERIFIED | - |
| 01 F4: main puts A1 FAIL in `failed`, prints `A1 FAIL:`, and failed gives exit 1 | check_pipeline.py L810-811, L841, L859 | VERIFIED | - |
| 01 F5: the docstring lists A1 FAIL (exit 1) and has no I3 entry | check_pipeline.py L20-33 | VERIFIED | - |
| 01 F6: with re.M, `^` matches at each line start. findall scans left to right, in the order found | https://docs.python.org/3/library/re.html (fetched 2026-11-18) | VERIFIED | - |
| 01 F7: the IN PR override applies only to STUCK, not started and in progress | check_pipeline.py L796-802 | VERIFIED | - |
| 01 F8: open_branches runs classify but keeps only SKIPPED | check_pipeline.py L486-488, L838-840 | VERIFIED | - |
| 01 F9: _open_at counts an item as open when 07 is absent, has no A1 line, or its last line is FAIL | check_pipeline.py L508-518 | VERIFIED | - |
| 01 F10: 069 round 1 pipeline line is `in progress (FULL: next 07)`, and the round was sent back to I2 with no 07 | work/069/06-verification.md L88, L90-91 | VERIFIED | - |
| 01 F11: 070 round 1 has the same line, "07 is not written because the verdict is FAIL", and "Sent to Audit: no" | work/070/06-verification.md L103-105, L107-115 | VERIFIED | - |
| 01 F12: 062 round 1 was sent back, not sent to Audit, and no 07 was written | work/062/06-verification.md L67-68 (L65: round 1 line was `next 06`, run before 06 existed) | VERIFIED | - |
| 01 F13: I3 log FAIL lines for 002 (x2), 062, 061, 069, 070. LOG_FORMAT["I3"] is at L213 | logs/implementation/2026-10-30.md L5, L8; 11-13.md L5; 11-14.md L5; 11-17.md L8; 11-18.md L3; check_pipeline.py L213 | VERIFIED | - |
| 01 F14: 67 06 files, all with a `^Verdict:` line, 73 lines in total. 002/069/070 have 3 each. No 06 for 001, 023, 057 | Glob work/*/06-verification.md (67); Grep `^Verdict:` | VERIFIED | - |
| 01 F15: the template verdict line and its "update this line first" comment | templates/verification.md L2-3 | VERIFIED | - |
| 01 F16: the first `Verdict:` line of all 67 files starts with PASS | Grep `^Verdict:` (every file at L2) | VERIFIED | R3 note: 070 L2 still says "round 2" although round 3 exists (L191-192), so line 2 is not always kept current (the first word is right) |
| 01 F17: 069/070 line 2 was rewritten and sits above a round-1 FAIL body | work/069/06 L2, L90-94; work/070/06 L2, L107-115 | VERIFIED | - |
| 01 F18: the last `Verdict:` line is PASS too (002 L237, 069 L162, 070 L192) | Grep `^Verdict:` | VERIFIED | - |
| 01 F19: round headers have no single format (H1/H2, "Re-verification", "Round n") | work/002/06 L162, L236; 061/06 L190; 062/06 L75; 069/06 L96, L161; 070/06 L117, L191 | VERIFIED | - |
| 01 F20: 061 and 062 round 2 have no `Verdict:` line of their own | 061/06 L190; 062/06 L111; Grep shows only L2 in both | VERIFIED | - |
| 01 F21: some verdict words are in bold `**FAIL**` / `**PASS**` | 002/06 L163, L237; 070/06 L192 | VERIFIED | - |
| 01 F22: PASS lines contain FAIL inside parentheses. RI-012 rule and i3 negative-test rule | 069/06 L2, L97, L162; logs/recurring-issues.md L138-141; .claude/agents/i3-verifier.md L14 | VERIFIED | - |
| 01 F23: the unfilled template line starts with PASS | templates/verification.md L2; 069/06 L93 | VERIFIED | - |
| 01 F24: I3 sends FAIL back to I1 or I2. run-item sends it back to the step named in the file | i3-verifier.md L15; .claude/commands/run-item.md L14 | VERIFIED | - |
| 01 F25: the send-back target is only in prose, and one FAIL can go to I1 and I2 | templates/verification.md L13; 069/06 L91; 070/06 L108; 062/06 L69, L71 | VERIFIED | - |
| 01 F26: i3 step 5 says "On PASS, write 06", but FAIL rounds wrote 06 | i3-verifier.md L16; 069/06 L88-94 | VERIFIED | - |
| 01 F27: the 069 and 070 histories mix I3 FAIL and A1 FAIL | 069/06 L2; 069/07 L22, L56; 070/06 L191-192; 070/07 L20, L31 | VERIFIED | - |
| 01 F28: with all 7 steps present, the A1 branch is reached first, so an I3 FAIL after an A1 FAIL would print A1 FAIL | check_pipeline.py L309-323 (code order) | VERIFIED | - |
| 01 F29: the fixture helper writes 06 as `x` + `Recurring issues checked: RI-007` with no Verdict line | tests/test_pipeline_check.py L19-34 | VERIFIED | - |
| 01 F30: the 042 tests to copy | tests/test_pipeline_check.py L325-335 | VERIFIED | - |
| 01 F31: the repo test was red during A1 FAIL and recorded as "not a 070 defect". Exit 1 for I3 FAIL would do the same | 070/06 L138-144, L189; check_pipeline.py L859 | VERIFIED | - |
| 01 Numbers: 67 files, 73 lines = 64 x 1 + 3 x 3 | Glob + Grep | VERIFIED | 64 + 9 = 73 |
| 01 Numbers: 0 of 67 would show I3 FAIL under either rule | Grep `^Verdict:` | VERIFIED | I3 re-measures with the built code |
| 01 Numbers: 6 FAIL rounds in 6 I3 log lines | logs/implementation Grep `\| I3 \|` | VERIFIED | - |
| 01 Fit for ~$3k: not trading. No ccbot/ or config/ change | request.md; this map | VERIFIED | - |
| 02: 011. 002/06 L2 once said FAIL while L237 said PASS, 235 lines down | logs/audit/2026-10-30.md L22, L53; logs/efficiency/2026-10-30.md L8; work/011/03-handoff.md L6, L14 | VERIFIED | 237 - 2 = 235 |
| 02: 042 is the model (anchored, last match, failed list, summary line, exit 1) | check_pipeline.py L317-323, L810-811, L841, L859 | VERIFIED | - |
| 02: 042's own 02 gives no design detail | work/042/02-improvements.md L1-15 | VERIFIED | - |
| 02: RI-010 fixes are structured fields with ID cutoffs (CHECKLIST_FROM=41, LOG_FORMAT, WHOLE_DIFF_FROM=70) | recurring-issues.md L118-124; check_pipeline.py L170, L180, L207-214 | VERIFIED | - |
| 02: RI-012 applies (PASS lines contain FAIL) | recurring-issues.md L138-141; i3-verifier.md L14 | VERIFIED | - |
| 02: RI-002, no silent defaults | recurring-issues.md L24-26 | VERIFIED | - |
| 02: I3 log lines per rounded item (002, 062, 061, 069, 070), last line PASS for all five | logs/implementation 10-30 L5, L8, L11; 11-13 L5, L7; 11-14 L5, L7; 11-17 L8, L11; 11-18 L3, L6, L9, L10 | VERIFIED | - |
| 02: a log cross-check would flag 0 items today | same Grep | VERIFIED | R3 count: 29 of 29 items 041-070 with a 06 (041-056, 058-070) have a PASS last I3 line and a PASS line 2. 0 disagree |
| 02: 069 and 070 went I3 FAIL, A1 FAIL, PASS. No RI occurrence counted | logs/audit/2026-11-17.md L51, L53 | VERIFIED | - |
| 02: no earlier attempt at this check (Grep "I3 FAIL") | Grep logs/ "I3 FAIL": 2026-11-17.md L51, L53; 2026-11-18-069.md L48; efficiency/2026-11-17.md L4; implementation/2026-10-30.md L6-7 | VERIFIED | - |
| 02: parallel work. 072/073 in R1. 074 must not edit check_pipeline.py | logs/research/2026-11-18.md L3-10; work/073/02-improvements.md L38, L94; work/073/01-research.md L54, L56 | WRONG (partly) | Fixed: R1 lines are L3-6 (074 is at L6), and all four items are past R2 (L7-10). No repo file holds the 074 restriction; it is an orchestrator note. 073 says it will not touch check_pipeline.py, but it does edit templates/verification.md L8 and i3-verifier.md L13. 071 edits L2-3 and L16 of the same files (see map, Overlap) |
| 02 FOR 1: reading line 2 works for 061/062, whose later rounds have no Verdict line | 061/06 L2, L190; 062/06 L2, L111 | VERIFIED | - |
| 02 FOR 1: regex `^Verdict:[ \t]*\**[ \t]*(PASS-or-FAIL)\b(?![ \t]*BAR)` (BAR = the pipe character) rejects the unfilled template | regex worked by hand; Python re doc (possessive quantifiers "Added in version 3.11") | WRONG | Fixed: the lookahead sits right after the word, so `Verdict: **PASS** BAR FAIL` passes (`**` comes before the bar), and `\**` allows any number of `*`. Replaced by VERDICT_LINE (map step 1), which skips spaces and `*` before a bar or slash. Possessive quantifiers can't be used: the project supports Python 3.10 (RI-008) |
| 02 FOR 1: cross-check from CHECKLIST_FROM, where 043 already needs an I3 log line | check_pipeline.py L170, L327-340 | VERIFIED | 29 of 29 agree (row above) |
| 02 FOR 1: I3 log lines are format-checked by --log from 045 | check_pipeline.py L174, L213, L341-346, L350-358 | VERIFIED | - |
| 02 FOR 2(a): a FAIL in 06 comes before A1's result, because Audit only follows an I3 PASS | run-item.md L14; i3-verifier.md L16 | VERIFIED | - |
| 02 FOR 2(b): plumbing copied from 042 (list, summary line, exit 1, docstring) | check_pipeline.py L20-33, L810-811, L841, L859 | VERIFIED | - |
| 02 FOR 2(c): add I3 FAIL to the IN PR tuple | check_pipeline.py L796 | VERIFIED | - |
| 02 FOR 2(d): LEGACY replaces only SKIPPED/in progress. 004-008 are PASS on L2 | check_pipeline.py L228-229, L792; Grep `^Verdict:` | VERIFIED | - |
| 02 FOR 3: put the target in a closed `Sent back to:` field under `## Sent back / sent to Audit` | 069/06 L90, L158, L269; 070/06 L107, L187, L237; Grep `^Sent back to:` = 0 lines | WRONG (placement) | Fixed: a multi-round 06 has one Sent back section per round (069 has 3, 070 has 3), so a first-match rule would read round 1. The field goes on line 3, under Verdict, and is updated with it (map step 6). The vocabulary and the regex idea are kept |
| 02 FOR 3: 069 round 2 used `<fill in>` placeholders | logs/audit/2026-11-18-069.md L48 | VERIFIED | - |
| 02 FOR 3: change i3 step 5 so 06 is written on FAIL too | i3-verifier.md L16 | VERIFIED | - |
| 02 AGAINST 1: the repo test asserts exit 0 on a HEAD worktree | tests/test_pipeline_check.py L155-161 | VERIFIED | - |
| 02 AGAINST 1: I3's round-2 step 2 pastes its own `I3 FAIL` line, because it runs before line 2 is rewritten | 069/06 L156, L267; 070/06 L184-185, L234-235 | WRONG | Fixed: I3 ran check_pipeline after writing 06 (and 07, and its log line) in every recorded round, so its own line shows the new round. I2's runs during the fix and other items' runs on the branch do see `I3 FAIL` |
| 02 AGAINST 1: the options are (i) exit 1 plus agent text, or (ii) exit 0 like AWAITING A1 | check_pipeline.py L808-809, L819; request.md L8, L18 | VERIFIED | Settled: (i), map steps 4, 7, 8 |
| 02 AGAINST 2: 042 uses `.upper()`, so copying it would accept `Verdict: pass` | check_pipeline.py L321 | VERIFIED | Settled: case-sensitive (Decisions D2) |
| 02 AGAINST 3: the script is about 865 lines and prints about 13 summary lines | check_pipeline.py L818-858, L864 | WRONG (count) | Fixed: 864 lines. With git it always prints 14 summary lines (STUCK, AWAITING A1, IN PR, RULES BRANCH, ID CLASH, A1 FAIL, INCOMPLETE, LOG TIME, UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD, ORPHAN LOG, INBOX, SKIPPED), plus MAIN AHEAD, OPEN BRANCHES and BRANCH SKIPPED when they apply |
| 02 AGAINST 3(b): items 041-044 have hand-typed I3 lines, and some items before 41 have none | logs/implementation/2026-11-04.md L5-14 (all `PASS \| sent to audit: yes`); no `\| I3 \| 040` line | VERIFIED | - |
| 02 AGAINST 3(c): a line after UTC midnight goes in the next day's file, so sort by file date and then line order | check_pipeline.py L362-364 (one `now` gives both file date and HH:MM) | VERIFIED | So the order is chronological. Not a hazard for this rule |
| 02 AGAINST 3: a RULES BRANCH edit needs the person's OK in PR review | work/070/02-improvements.md L18; check_pipeline.py L193 | VERIFIED | - |
| 02 Holes: open_branches reports only SKIPPED. Name the gap, as 042 did | check_pipeline.py L838-840 | VERIFIED | Settled: gap named (step 5) |
| 02 Holes: an INCOMPLETE cutoff of 071 keeps existing fixtures green | tests/test_pipeline_check.py L19-34, L342; tests/test_real_data_field.py L22-30 (fixture IDs 105-176 are all 71 or higher) | WRONG | Fixed: the cutoff does not protect fixtures, because their IDs are at or above 71. `_item`, `_rd_item` and test 131's 06 must write a Verdict line (map steps 9, 10) |
**Totals:** 67 rows checked → **61 VERIFIED as-is**, **6 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None.

## Implementation map
Scope FULL, EFFICIENCY. Files: scripts/check_pipeline.py, templates/verification.md, .claude/agents/i3-verifier.md, .claude/agents/i2-builder.md, tests/test_pipeline_check.py, tests/test_real_data_field.py. Nothing in ccbot/, config/, rule 001 or reports/ changes, and nothing places an order. templates/, .claude/ and scripts/check_pipeline.py are RULE_PATHS (L193), so the branch shows as RULES BRANCH and the person must OK it in PR review.

### Decisions (the open choices from 01/02)
- **D1, which line counts.** The first line outside ``` fences and HTML comments that starts at column 0 with `Verdict:` is the verdict line (the template's line 2). If VERDICT_LINE does not match that line, the verdict is unreadable. The reader never skips to a later `Verdict:` line, and there is no last-line rule (01 OQ1 a). A stale line 2 is caught by the log cross-check in D6.
- **D2, case.** Case-sensitive: only `PASS` and `FAIL`, optionally in `**` bold. 042's `.upper()` is not copied. `Verdict: pass` is unreadable: INCOMPLETE from 071, not checked below. Today there are 0 lowercase verdict lines (Grep -i `verdict:`: 73 uppercase lines at column 0; the only other hit, 061/06 L116, is indented prose).
- **D3, fences.** Lines inside ``` fences are skipped, so pasted output with another `Verdict:` is never read. Fences toggle on `line.lstrip().startswith("```")`, the same as `_field_gap` (L607, L616). HTML comments are removed first (as L604 does). Today 0 of 73 `Verdict:` lines are inside a fence: every one sits right after an H1/H2 heading or the title line (Grep line numbers vs headings).
- **D4, send-back target.** Read only from the first column-0 `Sent back to:` line outside fences/comments, with a full-line match against `I1`, `I2`, `I1 I2` or `none` (SENT_BACK_LINE). It is read only when the verdict is FAIL. `none` or an unreadable value with FAIL is "not stated", never I2 (RI-002). From 071 that also gives INCOMPLETE. The template puts the field on line 3 (fact-check row "FOR 3"). Today there are 0 such lines (Grep `^Sent back to:`). The prose "Sent back to I2 (" in 069/070 has no colon and does not match.
- **D5, exit code.** Exit 1, like A1 FAIL (request L8, L18). An `I3 FAIL:` summary line is printed. i2 and i3 get one sentence each: a red repo test whose only failing line is `I3 FAIL:` or `A1 FAIL:` is expected (steps 7, 8). Option (ii), exit 0, would contradict the request.
- **D6, log-line role (no fallback).** 06 is the only source of the status. The last I3 log line is a cross-check only, never a fallback. If 06's verdict is unreadable, the log is not used to fill it in (RI-002). From CHECKLIST_FROM (41), when 06's verdict is readable and the last `| I3 | <ID> |` line in logs/implementation/????-??-??.md (sorted by name, then line order) starts with PASS or FAIL, a difference is INCOMPLETE. With no I3 line, 043's "no log line for I3" already reports it. A malformed line is 045's format check (from 45). A log-only design (02 AGAINST 3) is rejected, because the request says "reads the verdict in 06".
- **D7, precedence.** The I3 check runs after the SKIPPED checks (L303-314) and before the all-steps/A1 branch (L315). So 06 FAIL beats an older 07 A1 FAIL (069/070 order) and beats `awaiting A1`. SKIPPED (gaps, results before 03, 062 flag, L794) still wins over it.
- **D8, branches and IN PR.** `I3 FAIL` is added to the IN PR tuple (L796). Open branches still report only SKIPPED, and the docstring names this gap, as 042 left A1 FAIL.
- **D9, cutoff.** VERDICT_FROM = 71. From 071, an unreadable verdict, and a FAIL with no stated target, are INCOMPLETE. Below 071 they are "not checked" (unreadable) or "sent back to: not stated" (FAIL, no target). A readable FAIL is shown for every item: 0 change today.

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | scripts/check_pipeline.py: after WHOLE_DIFF_FROM (L180) add `VERDICT_FROM = 71`, VERDICT_LINE, SENT_BACK_LINE (exact text below). After `_build_waived`, add `i3_verdict(path)`: returns `(verdict, target)`, where verdict is "PASS", "FAIL" or None and target is "I1", "I2", "I1 I2", "none" or None. It drops comments, skips fenced lines, and decides on the first `Verdict:` and the first `Sent back to:` line (D1-D4) | 06 text | (verdict, target) | T4 parametrized cases (step 9). Mutations m1-m5, m11 each fail at least 1 test (step 11) | VERDICT_LINE on the repo: 67 of 67 06 files readable, 67 PASS, 0 FAIL, 0 unreadable (Grep `^Verdict:` on work/*/06, daily-fixes/2026-11-18, 2026-11-18). I3 re-measures with the built code: `I3 FAIL: none` and `INCOMPLETE: none` |
| 2 | classify(): insert before L315: `if "06" in have:` call i3_verdict. On "FAIL", set `where = f"sent back to {target}" if target in ("I1", "I2", "I1 I2") else "sent back to: not stated"` and return `"I3 FAIL", f"{scope}; {where}, needs a later PASS round in 06 (item 071){extra}"` | item dir | status line `<ID>: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))` | T1, T2, T5, T6 | 0 of 67 items with a 06 change status today (0 FAIL). Fixtures T1, T5, T6 give 1 item each |
| 3 | incomplete(): after the existing entries (L333-346), add (a) for ID ≥ VERDICT_FROM with a 06: verdict None gives `06 has no readable 'Verdict: PASS' or 'Verdict: FAIL' line (item 071)`; (b) for ID ≥ VERDICT_FROM: FAIL and target not I1, I2 or I1 I2 gives `06 Verdict is FAIL but has no 'Sent back to: I1, I2 or I1 I2' line (item 071)`; (c) for ID ≥ CHECKLIST_FROM: verdict readable, and the last I3 log line's first word (PASS or FAIL, via LOG_LINE) differs, gives `06 Verdict says <v>, last I3 log line says <l> (item 071)` | 06, logs/implementation/????-??-??.md | INCOMPLETE entries | T3, T6, T7 | (a)/(b): 0 items of 71 or above have a 06 today (Glob work/07[1-4]/: no 06), so the empty result is `INCOMPLETE: none`. (c): 29 of 29 items 041-070 with a 06 agree, 0 disagree (Grep logs/implementation `\| I3 \|`, 2026-11-18) |
| 4 | main(): new list `i3_failed`. Add `"I3 FAIL"` to the IN PR tuple at L796. After L809 add `if status == "I3 FAIL": i3_failed.append(d.name)`. Before L841 print `I3 FAIL: <ids or none>`. Add `or i3_failed` to the L859 return | classify statuses | `I3 FAIL:` line; exit 1 | T1 (exit 1, `I3 FAIL: 171`), T2 (`I3 FAIL: none`, exit 0), T8 (IN PR), repo test asserts `I3 FAIL: none` | 0 items listed today, so the repo exit code is unchanged (0 of 67) |
| 5 | Docstring: after A1 FAIL (L31-32) add the I3 FAIL entry. After INCOMPLETE (L35-37) add the item-071 paragraph and gaps (w)-(z) (exact text below) | - | docstring | `grep -n "I3 FAIL" scripts/check_pipeline.py` shows the docstring entry at the status list; `grep -n "(w)" scripts/check_pipeline.py` shows the gap list | – |
| 6 | templates/verification.md: L2 is kept, a new L3 `Sent back to: <I1 \| I2 \| I1 I2 \| none>` is added, and the L3 comment (now L4) is replaced (exact text below) | - | template | T10: the shipped template's first Verdict line and first Sent back line are both unreadable (unfilled), and filled with `PASS (round 1)` / `none` they read ("PASS", "none") | – |
| 7 | .claude/agents/i3-verifier.md step 5 (L16): replace it with the exact text below (06 on PASS and FAIL, top two lines first, no 07 on FAIL, run step 2 after 06 and --log) | - | agent text | `grep -n "item 071" .claude/agents/i3-verifier.md` gives 1 hit. A1 reads it | – |
| 8 | .claude/agents/i2-builder.md step 3 (L20): append the exact sentence below | - | agent text | `grep -n "item 071" .claude/agents/i2-builder.md` gives 1 hit | – |
| 9 | tests/test_pipeline_check.py: `_item(..., verdict="PASS")`. The 06 body becomes `Verdict: <v> (round 1)\n` (no line when verdict=None), plus `Sent back to: I2\n` when FAIL, plus the old body. The I3 log field is `FAIL \| sent to audit: no` when FAIL. Test 131 (L342) writes `Verdict: PASS (round 1)\nx\n`. New tests T1-T8 and T10 (list below). The repo test (L156-163) also asserts `"I3 FAIL: none" in out` | fixtures | tests | `pytest -q tests/test_pipeline_check.py` passes, and every new test fails under its mutation (step 11) | T3 counts: 2 items below 71 (one single `Verdict: PASS`, one with no Verdict line) give 0 INCOMPLETE; 1 item of 71 or above with no Verdict line gives 1 INCOMPLETE |
| 10 | tests/test_real_data_field.py L29: the 06 body becomes `# 06\nVerdict: PASS (round 1)\nRecurring issues checked: RI-007\n{body06}` | - | test | `pytest -q tests/test_real_data_field.py` gives the same pass count as before (32 at 4789b44, 070/06 L210) | – |
| 11 | Verification: full suite; `python3 scripts/check_pipeline.py` on the real tree; mutations m1-m13, one at a time in a scratch copy (never in the repo, RI-009) | built tree | 05/06 pasted output | each mutation fails at least 1 named test; repo `I3 FAIL: none`, exit as before | – |

### Exact texts
Step 1 constants (Python 3.10 compatible, with no possessive quantifiers):
```
# Item 071: I3's verdict and send-back target in 06 (templates/verification.md L2-3). The first
# column-0 `Verdict:` / `Sent back to:` line outside code fences and HTML comments decides; never
# a later one, never a substring (RI-012). From VERDICT_FROM on an unreadable value is INCOMPLETE.
VERDICT_FROM = 71
VERDICT_LINE = re.compile(r"Verdict:[ \t]*(?:\*\*)?(PASS|FAIL)\b(?![ \t*]*[|/])")   # .match on the line
SENT_BACK_LINE = re.compile(r"Sent back to:[ \t]*(I1 I2|I1|I2|none)[ \t]*")         # .fullmatch on the line
```
i3_verdict: `text = re.sub(r"<!--.*?-->", "", text, flags=re.S)`. Then, for each line: a fence line toggles the fence and is skipped, and lines inside a fence are skipped. The first line with `line.startswith("Verdict:")` sets verdict to `VERDICT_LINE.match(line)[1]`, or None if it does not match; later Verdict lines are ignored. The first line with `line.startswith("Sent back to:")` sets target to `SENT_BACK_LINE.fullmatch(line)[1]`, or None. A missing file is never read: classify calls the function only when "06" is in `have`.

Step 5 docstring, after L32:
```
  I3 FAIL      06's verdict line (its first `Verdict:` line outside code fences; templates/verification.md
               L2) is FAIL (item 071): I3 sent the item back to the step on 06's first `Sent back to:`
               line (I1, I2 or I1 I2; else `sent back to: not stated`, never a default). Checked before
               A1's result: a FAIL in 06 means the current build has not passed I3. Not complete until a
               later round rewrites that line to PASS (exit 1).
```
After L37:
```
Item 071: from VERDICT_FROM on, a 06 whose verdict line is missing or unreadable (only `PASS` or
`FAIL`, case-sensitive, optionally **bold**; the unfilled `PASS | FAIL` is unreadable), or a FAIL with
no `Sent back to: I1|I2|I1 I2` line, is INCOMPLETE. From CHECKLIST_FROM on, a readable verdict that
differs from the first word of the item's last `| I3 |` log line (logs/implementation, by file date
then line order) is INCOMPLETE; the log never fills in a missing verdict. Known gaps: (w) a 06 FAIL
with a 07 whose last A1 line is PASS shows I3 FAIL, but _open_at (053) treats the item as closed (a
re-opened completed item is a new item, run-item.md); (x) open branches report only SKIPPED, so a
branch's I3 FAIL (like its A1 FAIL) is not listed; (y) below VERDICT_FROM an unreadable verdict is
not checked; (z) the line proves what I3 wrote, not that I3 ran (the log cross-check is the second
source).
```

Step 6 template, lines 2-4 after the edit:
```
Verdict: PASS | FAIL (round <n>; earlier rounds: <verdicts>)
Sent back to: <I1 | I2 | I1 I2 | none>
<!-- On every round, FAIL too, update these two lines first. Verdict: its first word is PASS or FAIL (bold allowed), then the latest round. Sent back to: I1, I2 or I1 I2 on FAIL, none on PASS. check_pipeline.py reads the first Verdict and Sent back line outside code fences (item 071). -->
```

Step 7, i3-verifier.md step 5, new text:
"5. Write `work/<ID>/06-verification.md` using `templates/verification.md` on PASS and on FAIL. On every round, first update the two top lines: `Verdict: PASS` or `Verdict: FAIL` with the round, and `Sent back to:` I1, I2 or I1 I2 (FAIL) or none (PASS). `check_pipeline.py` reads both (item 071). On FAIL write no 07; the item shows `I3 FAIL` (exit 1) until a later PASS round. On PASS, create the audit task `work/<ID>/07-audit-task.md` listing what Audit should look at. Run step 2's `check_pipeline.py` after this file and your `--log` line are written. In a FAIL round your own line is `<ID>: I3 FAIL (...)`, which is expected."

Step 8, i2-builder.md step 3, appended sentence:
"While an item is in I3 FAIL or A1 FAIL and its 06/07 is committed, `check_pipeline.py` exits 1 and `test_repo_pipeline_has_no_skipped_items` fails; if the only failing lines are `I3 FAIL:` / `A1 FAIL:` naming items sent back, record that in 05 as expected, not a defect of this build (item 071)."

### Tests (step 9) and mutations (step 11)
- T1 `test_i3_fail_shows_and_exits_1`: item 171 has 01-06, verdict FAIL, `Sent back to: I2`. Expect `171: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))`, `I3 FAIL: 171`, `A1 FAIL: none`, `INCOMPLETE: none`, exit 1.
- T2 `test_later_pass_round_clears_i3_fail`: items 172 (01-06) and 179 (01-07, 07 `A1 result: PASS`), both created with `logged=False` plus the test's own log lines. Each 06 has line 2 `Verdict: PASS (round 2; earlier rounds: FAIL round 1)`, and lower, under `# Round 1`, `Verdict: FAIL (round 1)` with `Sent back to: I2`. Each I3 log has FAIL in 2026-11-17.md at 23:50 and PASS in 2026-11-18.md at 00:00 (midnight order). Expect `172: in progress (FULL: next 07)`, `179: complete (FULL)`, `I3 FAIL: none`, `INCOMPLETE: none`, exit 0.
- T3 `test_old_06_without_round_headers_unchanged`: item 060 with 06 `Verdict: PASS` only, and item 065 with no Verdict line, both complete: no INCOMPLETE for either, exit 0. Item 173 with no Verdict line gives `173 (06 has no readable 'Verdict: PASS' or 'Verdict: FAIL' line (item 071))`, exit 1.
- T4 `test_i3_verdict_reader` (parametrized, calls `i3_verdict` on a tmp file).
  - Read as a verdict: `Verdict: PASS (round 3; earlier rounds: FAIL round 1)` gives PASS. `Verdict: **FAIL** (x)` gives FAIL. `Verdict: **PASS**. note` gives PASS.
  - Give None: the unfilled template line, `Verdict: **PASS**` + bar + `FAIL`, `Verdict: PASS/FAIL`, `Verdict: pass`, `Verdict: PASSED`, a file whose only verdict is mid-line (`see 05. Verdict: FAIL`), a file whose only verdict is indented (`  Verdict: FAIL`), and a file whose first Verdict line is the unfilled template with a later `Verdict: FAIL`.
  - Skipped text: a ``` fence holding `Verdict: FAIL` above `Verdict: PASS` gives PASS, and so does an HTML comment holding it.
  - Targets: `Sent back to: I1 I2` gives "I1 I2". `Sent back to: I2 (tests only)`, the unfilled placeholder, and mid-line `x Sent back to: I2` give None.
- T5 `test_i3_fail_beats_older_a1_fail`: item 174 with all 7 steps, 06 FAIL, and 07 ending `A1 result: FAIL`. Expect `174: I3 FAIL (`, `I3 FAIL: 174`, `A1 FAIL: none`.
- T6 `test_i3_fail_target_not_stated`:
  - Item 175, FAIL with no Sent back line, gives `175: I3 FAIL (FULL; sent back to: not stated, needs a later PASS round in 06 (item 071))` and INCOMPLETE `175 (06 Verdict is FAIL but has no 'Sent back to: I1, I2 or I1 I2' line (item 071))`.
  - Item 178, FAIL with `Sent back to: none`, gives the same two results.
  - Item 066, FAIL with no field, gives `sent back to: not stated`, and 066 is not in INCOMPLETE.
  - Assert `"sent back to I2" not in out`.
- T7 `test_06_verdict_disagrees_with_last_i3_log`: item 176 with 06 PASS and a last I3 log line FAIL gives `176 (06 Verdict says PASS, last I3 log line says FAIL (item 071))`. Item 040 (below 41), with the same disagreement, is not listed.
- T8 `test_i3_fail_with_more_steps_on_branch_is_in_pr` (git fixture, `_branch_adds`): main has 177 with 01-06 and 06 FAIL. The branch adds 07. Expect `177: IN PR (origin/... has ...; was I3 FAIL here)` and `I3 FAIL: none`.
- T10 `test_verification_template_lines_unfilled`: the shipped template gives (None, None), and the filled copy gives ("PASS", "none").
- Mutations, each in a scratch copy, each failing the named test:

  | Mutation | Fails |
  |---|---|
  | m1: `.search` instead of startswith/`.match` (anchor lost) | T4 mid-line and indented cases |
  | m2: lookahead removed | T4 unfilled template |
  | m3: lookahead back to R2's `(?![ \t]*BAR)` | T4 `**PASS**` + bar + FAIL |
  | m4: `re.I` or `.upper()` | T4 `pass` |
  | m5: fence/comment handling removed | T4 fence and comment cases |
  | m6: last Verdict line instead of the first | T2 |
  | m7: I3 check moved after the A1 branch | T5 |
  | m8: `or i3_failed` dropped | T1 (exit) |
  | m9: VERDICT_FROM check removed | T3 (065) |
  | m10: cross-check removed | T7 |
  | m11: `"FAIL" in line` | T4 first case, T2 |
  | m12: target defaults to "I2" | T6 |
  | m13: `"I3 FAIL"` removed from the IN PR tuple | T8 |

### Overlap with parallel items
073 edits templates/verification.md L8 and i3-verifier.md L13 (073/01 L54, L56). 071 edits verification.md L2-4 and i3-verifier.md L16, and 072 edits run-item.md L14 (so 071 leaves run-item.md alone). They are separate lines in the same files on one branch: I2 re-reads each file just before editing, and changes only its own lines. 073 does not touch check_pipeline.py (073/02 L38, L94). Items 072-074 whose 06 is written after this lands must fill `Sent back to:` on a FAIL, or they get INCOMPLETE (D9). That is intended.

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| 06 file (classify) | not read. The status comes from the existing rules (in progress / SKIPPED) | unchanged lines, e.g. `in progress (FULL: next 06)` |
| 06 verdict line, missing or unreadable (i3_verdict → None) | never PASS or FAIL. From 071: INCOMPLETE, exit 1. Below 071: not checked (gap y) | `06 has no readable 'Verdict: PASS' or 'Verdict: FAIL' line (item 071)` |
| `Sent back to:` line on a FAIL, missing, unreadable or `none` | never defaulted to I2. The status still shows I3 FAIL. From 071 it is also INCOMPLETE | status `sent back to: not stated`; INCOMPLETE `06 Verdict is FAIL but has no 'Sent back to: I1, I2 or I1 I2' line (item 071)` |
| `Sent back to:` on a PASS | not read | – |
| Last `\| I3 \| <ID> \|` log line (cross-check) | no cross-check. 043 already reports it (from 41) | `no log line for I3` (existing) |
| I3 log line whose first word is not PASS/FAIL | no cross-check. 045's format check reports it (from 45) | `log line for I3 does not match its format (item 045)` (existing) |
| logs/implementation folder | no I3 lines. Same as the row above | existing 043 text |
| Unclosed ``` fence before the verdict line | the lines after it are not read, so the verdict is unreadable | as for a missing verdict line (from 071) |
| 06 on an open branch (open_branches) | I3 FAIL is not reported there (gap x) | docstring gap (x) |

## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| VERDICT_FROM = 71 | first ID whose 06 is written under the new template = first ID after the last 06 written under the old one | last existing 06 = 070 (Glob); 071's own 06 comes after step 6; 070 + 1 = 71; items 071-074 with a 06 today = 0 | ✓ 71 |
| CHECKLIST_FROM (41) for the cross-check | items 041-070 with a 06 whose last I3 log first word = 06 line 2 first word | 041-056 = 16, 058-070 = 13, 16 + 13 = 29; agree 29, disagree 0 | ✓ 0 new INCOMPLETE |
| Repo count | lines = 64 x 1 + 3 x 3 | 64 + 9 = 73; files 21 (002-022) + 33 (024-056) + 13 (058-070) = 67 | ✓ |
| VERDICT_LINE on 069 L2 `Verdict: PASS (round 3; earlier rounds: FAIL ...)` | match `Verdict:`, spaces, optional `**`, word, `\b`; the lookahead fails only on spaces/`*` followed by a bar or slash | after "PASS": " (" → `[ \t*]*` takes " ", next "(" is not a bar or slash → match PASS | ✓ PASS (FAIL in parentheses ignored) |
| VERDICT_LINE on 070 L192 `Verdict: **PASS**. I2's fix` | same | `(?:\*\*)?` takes "**", PASS, then "**." → `[ \t*]*` takes "**", next "." → match | ✓ PASS |
| VERDICT_LINE on 002 L163 `Verdict: **FAIL** (1 new ...` | same | "**" then FAIL then "** (" → no bar → FAIL | ✓ FAIL (not 002's verdict line, which is L2 PASS) |
| VERDICT_LINE on the unfilled template line 2 | the lookahead must fail | after "PASS": space, bar → `[ \t*]*` takes the space, next is the bar → negative lookahead fails; no other start (the word must follow `Verdict:` + spaces) → no match | ✓ None (unreadable) |
| VERDICT_LINE on `Verdict: **PASS**` + space + bar + ` FAIL` (R2's regex passes this) | same | after "PASS": "** " then the bar → `[ \t*]*` takes "** ", then the bar → fails; the empty `(?:\*\*)?` branch would need the word at "*" → no match | ✓ None |
| SENT_BACK_LINE on the unfilled placeholder line 3 | fullmatch of one closed word after spaces | "<" is not I1/I2/none → no match | ✓ None |
| Worked example: 069 timeline under the new code (assuming round 1's line 2 read `Verdict: FAIL`; that text is no longer in the tree) | status per round = D7 order | r1 (652a320): 06 FAIL, no 07 → `069: I3 FAIL (FULL; sent back to: not stated, ...)` (069 is below 71, so not INCOMPLETE), exit 1; log FAIL 11-17 23:50 = 06 FAIL → agree. r2: 06 PASS, log PASS 23:58, 07 with no A1 line → `awaiting A1`. A1 FAIL (07 L22) → `A1 FAIL`. r3: 06 PASS, log PASS 11-18 00:25, 07 last line PASS (L56) → `complete` | ✓ matches request L8, L18 |
| Worked example T1 detail text | `where` = "sent back to " + target when target is I1/I2/I1 I2; detail = scope + "; " + where + ", needs a later PASS round in 06 (item 071)" | scope FULL, target "I2" → `171: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))`; target None → `sent back to: not stated` (no stray space) | ✓ contains "I3 FAIL" and "sent back to I2" (request L8) |
| Exit code today | 1 if skipped or failed or i3_failed or ... | i3_failed = 0 items (0 FAIL of 67) → term False → exit unchanged | ✓ |

Recurring issues checked: RI-001 (ESCALATED): every filter has a count (67/67 readable, 29/29 agree, 0 items at or above 71, 0 `Sent back to:` lines), and I3 re-measures each with the built code. RI-002: unreadable never becomes PASS, a target never defaults to I2, and the log never fills a verdict. RI-003: no calendar. RI-004/RI-005: the worked examples were checked against VERDICT_LINE's own rule (Self-check). RI-006: totals are taken from check_handoff output below. RI-007: SKIPPED still wins over I3 FAIL; the gap (w) with 053 is named. RI-008: no possessive quantifiers (3.11+). RI-009: mutations in scratch copies; the parallel-item overlap is named. RI-010: the status now comes from a field a script reads (this item). RI-011: no branch-diff change. RI-012: first-word anchored match plus negative tests with the pattern inside other text (T4, m1-m3, m11). RI-013: no realtest change.

check_handoff output (run by the orchestrator):
(run by the orchestrator 2026-11-18 23:38 UTC, exit 0)
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 67
totals line: 67 rows -> 61 as-is, 6 fixed, 0 removed
PASS
```
