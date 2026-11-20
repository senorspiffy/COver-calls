# 02 Improvements - 082
## What past logs say
- RI-006 (logs/recurring-issues.md L77-82) has been GUARDED since PR #3. 076 is "built (PR #33, A1 PASS)". The 2026-11-19 near miss was a dropped skip (`411/411` for 411 passed + 1 skipped), and 076 fixed it only halfway. work/076/02 AGAINST 1 had already said so: "B removes the arithmetic but not the omission. Only copying verbatim, or a cross-check (option C), closes that gap", and it asked for "a fixed label" in 05 "so that I3 and A1 can compare the two without RI-012-style text guessing". Point 1 is the cross-check 076's R2 asked for.
- RI-010 (L118-130) is ESCALATED today, with 5 occurrences. Its root cause is "step duties exist only in the agent text ... no script checks them". Points 1 and 3 replace text duties with checks. Points 4b and 5 only add pinned text, so they are the weak half (AGAINST 2).
- RI-012 (L139-142): whole-line matches only, no substrings. This governs point 1's compare (no `in`) and point 3's `recorded` parse.
- RI-014 (L152-158) is OPEN. 079's "unshallow line in daily-audit.md and run-item.md" is in both command files, verbatim and identical (repo grep 2026-11-20: daily-audit.md L4 and run-item.md L12 hold the same sentence, ending "never 'none' (item 079)."). a1-auditor.md has 0 hits.
- 084 (in parallel, work/084/02 FOR 1-3): R2 proposes that a format rule applies to item X only if the `scripts/check_pipeline.py` in the commit that added X's checked file defines the rule constant (`^NAME = `). This is used only above the numeric cutoff ("Never reach below the numeric cutoff", 084/02 holes). It adds a `RULE NOT SEEN:` line, and the self-test pins that line's set to exactly {083} on HEAD (084/02 FOR 3d). This bears directly on 01's open question 1 (FOR 1 below).
- 086 (in parallel, work/086/request.md L13) may read "a pytest time over 30 s" out of 05/06. A labelled `Suite:` line would give it one fixed place to read that from (FOR 1). 086's actual design is UNVERIFIED: there is no 086/02 yet.
- 081 (in parallel) changes shallow and git-failure handling, and may extend the 079 unshallow sentence. A verbatim-across-files pin (FOR 3) would force such a change into all three files at once.
- Precedent for languages: 077, 079, 084 and 085 (EFFICIENCY/BUG items inside the checker) logged `languages: N/A`. 076 did the full search because it built a rule on pytest's printed format, which was a new outside fact. 082 adds no new outside fact (see "Findings by language").

## 3 ways FOR
1. **Point 1: numeric floor `SUITE_FROM = 87`, plus 084's rule-seen gate. Compare the whole string, tail included, and only once an I2 line exists. Point the RI-006 probe at the new compare.** (Open questions 1 and 2.)
   - (a) Cutoff. Today `--next-id` is 087 (caller). 080, 081 and 084-086 are open on this branch, and their I2 may commit 05 before or after 082's code commit, so a cutoff of 82 depends on commit order. Under 084's design, items between 82 and 86 whose 05 was added before the `SUITE_FROM` constant would appear in `RULE NOT SEEN:`. That breaks 084's exact-set pin {083}. Without the gate they would be INCOMPLETE, the 083 failure again (01 F9).
   - (b) With a floor of 87, none of 080-086 reaches the rule. 084's gate "never reaches below" the floor, so the {083} pin is untouched. Items from 087 on get the gate automatically if 084's helper takes a list of `(constant, checked file)` pairs: register `("SUITE_FROM", "05-build-report.md")`. If 082 lands first, 084 adds that one pair. If 084 lands first, 082 adds it. Reasoning chain from 084/02 FOR 2-3d and 01 F9. 082's own 05 still carries a `Suite:` line voluntarily, and the fixtures (M1a/M1b) prove the rule.
   - (c) Compare. Take the `.strip()` value of the single column-0 `Suite: ` line from `_md_lines` "out" lines and the text after `" | tests "` in the last well-formed I2 line (01 F7/F8). They must be `==`, including the optional ` (note)` tail that `_TAIL` allows (check_pipeline.py L234). The Suite line is the field's single source, so a note goes in both or in neither. Partial or stripped-tail matching would bring back the substring logic that RI-012 forbids.
   - (d) Only when an I2 line exists. With no I2 line, `no log line for I2` already reports the state (01 Q2), and a second entry for the same state adds nothing (077/02 AGAINST 2 made the same "second report for one state" point). A round-2 05 updated before its I2 line is written gives a mismatch. That is correct and loud, and it lasts only until `--log` runs.
   - (e) Probe. Request point 1 says "add an RI-006 probe once *it* holds". "It" is the new compare. The 072 slip (a dropped part) is what the compare catches. 01 F10's m2 mutation (`<=` dropped) guards only I2_BEFORE, which applies to items below 76, and no new item can fall under it. So: a probe whose anchor is the `==` line of the Suite compare and whose replacement is `in` (or `True`), targeting the M1a fixture test. m2 can be a second entry if R3 wants it, which makes PROBES 9 -> 11 rather than 10. Bonus: 086 can read pytest's ` in <t>s` from the labelled line instead of guessing which pasted line is the full suite (01 F4/F6, RI-012).
2. **Point 3: `(live differs)` compares the failed count only (plus errors > 0). It is information only. Two fixtures kill two different mutations.** (Open questions 3 and 4.)
   - (a) Passed counts drift every time a test is added to the probed file. 01 F24 measured 90 -> 226 tests, a gap of 136, between 078 and 079. 081, 084 and 086 all add tests to tests/test_pipeline_check.py today. A full-count compare would therefore mark all 4 (+1) check_pipeline entries after most items. A1 would learn to ignore the marker, and then it carries no information.
   - (b) The failed count is what a probe is about: how many tests the mutation breaks. It changes only when tests that touch the mutated code are added or removed, which is worth seeing. `errors > 0` should also mark, because collection errors mean the run did not measure the probe.
   - (c) Parse `recorded` with the same regex the format assert uses (A1's `^\d{4}-\d{2}-\d{2}( \(\d{3}/05\))?: \d+ failed, \d+ passed$`, 01 F22), one source, never a substring (RI-012). Exit code unchanged, because the verdict stays exit code + junit (01 F24).
   - (d) Fixtures: probe X has recorded failed = 2 and live failed = 1, so it prints `(live differs)`. This kills "marker branch removed" (M3b). Probe Y has the same failed count and a different passed count, so it prints no marker. This kills a mutation to a full-string or failed+passed compare, which (a) shows is the likely wrong turn. M3a (`recorded` deleted from a shipped entry -> format assert fails) stays as 01 F26.
   - (e) Refreshing values. Copy them from 05's own `--ref HEAD` run output, never by hand (RI-006, 01 F25). With a failed-only compare, the refreshed values stay valid as tests are added.
3. **Points 2, 4 and 5: use the cheapest killer for each, pin the unshallow sentence verbatim in all three files, and take the commit subject from the `--log` line.**
   - (a) Point 2: T4 `longer-close` (```` ``` ```` closed by 5 backticks -> ("PASS", None)) and the P5a2 `XR1 | 151 |` line, as 01 F16/F18 propose. Both rest on CommonMark §4.5's "at least as many", already cited by 077 (01 F13).
   - (b) Point 4a: add both a `<40hex>x` line and a 41-hex line. One case kills `.match`. The other also kills a mutation to `.search` or a `{40,}` quantifier, at no extra cost (01 F30 math: 41 is neither 40 nor 64).
   - (c) Point 4b: one test that reads the sentence out of run-item.md L12 and asserts it appears byte for byte in daily-audit.md and a1-auditor.md. This is stronger than a substring pin on `fetch --unshallow`: deleting or rewording any one copy fails. It also makes 081, or any later edit, change all three at once (01 F33, Q5).
   - (d) Point 5: the subject is `Item <ID>: ` + the exact `--log` line just written. That text has already passed LOG_FORMAT (01 F37), and run-item step (4) already produces it, so the orchestrator has one source and nothing to reword. It also fits 086 if `--log` becomes order-checked. The check is a text pin on the new run-item.md sentence (01 F38a). There is no reader of commit text (062/RI-012).
   - (e) Drop 077 P1's second suggestion (I1 template: one mutation per docstring clause, 01 F19). It is outside request.md's text, and it would be a fourth RULE_PATHS file needing the person's OK. If wanted, it should be its own EFFICIENCY item.

## 3 ways AGAINST
1. **Three parallel items edit the same functions, so anchors and line numbers will move.**
   - 081, 084 and 086 all change scripts/check_pipeline.py today (01 Context).
   - 084/02 FOR 2 says `log_fields_ok`/`log_hint` "gain an optional 'rule seen' input". So 01 F10's anchor `return bool(m) and int(m[1]) <= int(m[2])`, and any anchor in the new compare, may change text or count after 084 lands. The probe would then print `ANCHOR MISSING (count N)`, which exits 1 and which A1 must treat as a finding (a1-auditor.md L36).
   - Mitigation (reasoning): whichever of 082/084 is built second re-greps the anchor (count must be 1) and re-runs `probe_guardrails.py --ref HEAD` in its 05. I1 finds every place by function name, not line number. I2 runs the whole suite after each of the 5 points (077/02 AGAINST 3 habit).
   - Cost: the 87 floor means no real item exercises the Suite rule until 087, so the only proof on this branch is the fixtures.
2. **Points 4b and 5 are text pins, the same "text duty with nothing to check it" shape that RI-010 is about.**
   - A pin proves the sentence exists, not that A1 runs `git fetch --unshallow` or that the orchestrator copies the subject (077 brief F5 limit, 01 F33).
   - Point 5's e813e1f evidence is UNVERIFIED by R1 (01 F34: no shell, .git/logs/HEAD has only today's entries). I could not read it either (no shell).
   - The only real check, comparing each commit subject with its log line, would read commit text, which 062/RI-012 rule out for classification (01 F38). So point 5 stays an honest partial guard, and 05 must say so in plain words. If R3 judges a pinned sentence with no check not worth a RULES change to run-item.md (which needs the person's OK, 01 F39), dropping point 5 is defensible.
   - The request's "Done looks like" asks for a fixture test and a mutation for each sub-point, and a text pin plus deletion satisfies that only in letter.
3. **The request's "once it holds on main" can be read as "not in this item", and the new marker is a new thing for A1 to misread.**
   - (a) Strictly, the probe guards a compare that is not on main until 082 merges. 01 F11's argument (the branch carries PR #33, so 082 cannot reach main without 076) covers code arriving with its probe. It does not change the literal wording. The alternative is a follow-up item after merge. That costs one more item, and it leaves RI-006's new guardrail unprobed for at least one daily run.
   - (b) `(live differs)` is the first info-only marker on a run line where every other non-HOLDS word is a finding (a1-auditor.md L36: "Every NOT HELD, ANCHOR MISSING or ERROR line is a finding"). Unless a1-auditor.md says in the same sentence that the marker is information and not a finding, A1 may open items for it, or later stop reading the line at all.
   - (c) Mitigation: one clause in a1-auditor.md L36, pinned by test. That adds another RULE_PATHS edit. R3 should choose: in this item with the sentence, or the marker deferred.

## Findings by language
Random languages this cycle: N/A
Languages: N/A (no new external claims). 082 is an EFFICIENCY item inside this repo's checker, probe script, tests, one template and two agent/command texts. It adds or changes no fee, market rule, statistic or trading behaviour. Every outside fact it rests on is already cited and in use: pytest's `-q` summary line (076, full 7-language search, work/076/02), CommonMark §4.5 fences (077), Python `re.fullmatch` and git commit titles (official English docs, 01 F27/F36). Point 1 compares two copies of one string inside the repo and adds no claim about pytest's format. This follows 077, 079, 084 and 085 (logged `languages: N/A`).

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | N/A (no new external claims) | | | |
| Mandarin Chinese | N/A | | | |
| Spanish | N/A | | | |
| Japanese | N/A | | | |
| N/A | N/A | | | |
| N/A | N/A | | | |
| N/A | N/A | | | |

## Holes to watch out for (summary)
- H1 (cutoff): not 82. With 084's gate, 084-086's 05s committed before the constant land in `RULE NOT SEEN:` and break the {083} pin. Without the gate they are INCOMPLETE. Use a floor of 87 and register `("SUITE_FROM", "05-build-report.md")` with 084's helper, whichever lands second.
- H2 (one line): exactly one column-0 `Suite: ` line outside fences and comments. In 05 prose, write the label inline in backticks, never at column 0, or it counts as a second line (loud, INCOMPLETE). Make the template placeholder a real line (not in `<!-- -->`), so an unfilled one fails the compare.
- H3 (tail): `_TAIL` allows ` (note)`. The compare is whole-string, so the note must be in both places or neither. The i2 text should say "copy the Suite line into the field unchanged".
- H4 (which I2 line): use the last well-formed I2 line by file date, then line order. A malformed last line is already 045's INCOMPLETE. Never fall back to an earlier line (01 F8).
- H5 (probe anchor): re-grep the count after 084/081 land. Pin the target test by name. PROBES length becomes 10 or 11, depending on R3's m2 choice, and `test_shipped_probes_well_formed`'s list must match.
- H6 (marker): failed count plus errors > 0, never passed. Parse `recorded` with the format-assert regex. Exit code unchanged. Say "information, not a finding" in a1-auditor.md, or defer the marker.
- H7 (recorded refresh): values come only from 05's `--ref HEAD` output (RI-006). Never typed.
- H8 (shallow case): add `c + "x"` and a 41-hex line. Both must be "unreadable" under `fullmatch`.
- H9 (unshallow pin): byte-equal across run-item.md, daily-audit.md and a1-auditor.md. If 081 rewrites the sentence first, copy 081's version.
- H10 (point 5): log-line subject plus a text pin. Never parse commit messages (RI-012/062). Say in 05 that it is a partial guard. The e813e1f wording is UNVERIFIED.
- H11 (scope): drop 077 P1's I1-template suggestion. Points 1, 4b and 5 (and H6's a1 clause) are RULE_PATHS edits that need the person's OK in PR review.
- H12 (UNVERIFIED): every mutation result in 01 comes from audit files. I2 must re-run each one on this branch's head.

Log fields: 3 for / 3 against | languages: N/A
