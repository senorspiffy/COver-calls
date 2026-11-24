# 02 Improvements - 093
## What past logs say
- logs/audit/2026-11-22-090.md L90-101 (F1): A1 confirmed the gap as a BUG. Root cause: 090's claim that "no line before I2" is "impossible for every Scope" was never checked against the Waived path, and nobody counted the waiver shapes (RI-001 pattern). A1's proposed guardrail: excuse the reason only when every step before I2 is waived by `person`, keep it strict for any other waiver, flip [990], and add a non-person twin. "The per-round bound and the round rule keep running for waived items." It is a near miss and is not counted.
- logs/recurring-issues.md RI-010 (ESCALATED, 5 occurrences). The 2026-11-22 note lists "waiver gap → 093" as a near miss, not counted. The fix must not weaken LOG BATCH for any non-waived item, because RI-010 is still ESCALATED.
- RI-012 (GUARDED): never decide a kind from a substring of free text, and add negative tests where the pattern sits inside other text. This applies directly to the person check (see AGAINST 1).
- RI-002 (GUARDED): an uncomputable value must never turn into a silent pass. The excused item has to stay visible on the LOG BATCH line.
- RI-007: only the person may waive 03/06 (031). FAST must be `(person, <date>)` (042). 062's `_build_waived` already requires `who == "person"` plus a dated form.
- Precedent for reading request.md inside `batch_log_items`: the `excepted` branch already checks `(d / "request.md").exists()` (scripts/check_pipeline.py L1349-1351). So option (i) adds no new kind of dependency.
- Real `^Waived:` lines in work/ today (re-grepped 2026-11-24): 023 (A1), 024 (person), and 062/06 L49 (a quote, not in a request.md). None is numbered 090 or higher. R1's finding 16 holds.

## 3 ways FOR
1. **One shared, anchored person-waiver helper instead of a second hand-written check.** Add a helper such as `_person_waived(text, steps)` that returns True only when `who == "person"`, the text right after the step numbers `.match`es `\s*\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:`, and `steps <= waived`. Use it for 093, and optionally move `_build_waived` (L557-561) onto it.
   - Reasoning chain: `_build_waived` calls `WAIVE_BUILD_BY_PERSON.search(waived_line)` on the whole line. It is safe against the 062/06 L49 shape only because `who` comes from the first parenthesis.
   - It is not safe against `Waived: 01 02 03 04 (person: x "(person, 2026-11-19: ok)")`. There `who` = "person" (parse_request L550, `[^,:)]+` stops at `:`), and `.search` finds the quoted dated form. The undated waiver would then be excused.
   - An anchored `.match` on parse_request's group 2 closes this. Python docs: `search` "checks for a match anywhere in the string", while `match` checks "only at the beginning" (R1 finding 11).
   - Using one helper means 062 and 093 cannot drift apart.
2. **Put the excuse in `batch_log_items` as a distinct reason string (R1 option i), not in `incomplete()`.**
   - Reasoning: `incomplete()` tests `nc in BATCH_STRICT` by equality (L937, "never a substring"). A new reason such as `no line before I2 (steps before I2 waived by the person: <Waived line>)` is therefore not strict by construction. The item still appears on the LOG BATCH `not computable:` line, so the outcome is visible and not silent (RI-002).
   - `batch_log_items` already reads request.md for `excepted` (L1350), so this is not a new kind of read.
   - An unreadable request.md must give the existing strict reason, not the excused one. That keeps the fail-closed default, and classify already gives UNREADABLE (L662-664).
3. **Keep the per-round bound unchanged and do not build the optional I3-only bound now.**
   - Reasoning: the per-round loop (L1323-1341) runs before the `before` check and does not depend on the waiver. Every later I2 round has a prev line (the I3 line) and is already bounded. The first round has no prev under any rule, so the waiver neither adds nor removes a check there.
   - The I3-only bound rests on an order assumption that R1 marks UNVERIFIED (01 proposal 3). It would bound 0 real items today (finding 16).
   - Building it now would add an unverified rule for an empty set. That repeats RI-001: a rule asserted without measuring its candidates.
   - Record it as a documented gap instead (see AGAINST 3).

## 3 ways AGAINST
1. **A search-based person check would let an undated or non-person waiver through (RI-012).**
   - Two shapes would pass a bare `.search`. The 062/06 L49 shape `(I2, 2026-11-13: copied ... "(person, 2026-11-12: ok)")` passes if `who` is not checked. The shape `(person: x "(person, 2026-11-19: ok)")` passes even with the `who` check, because `who` = "person" and the quoted dated form satisfies `.search` (reasoning from L550 and L561).
   - Either one turns a waiver the request rules out (no date, or not the person) into a pass.
   - Cost: two more negative fixtures, R1 twin (c) and a new twin (e) with the undated person plus a quoted dated person. Each needs a mutation: `.match` → `.search` must fail (e).
2. **An excused item could hide a real batch, or report the same problem twice, if step files 01-04 exist.**
   - Reasoning: log lines are owed only for step files that exist (L904-907, R1 finding 3). Suppose a person-waived FULL item still has, say, 01-research.md but no R1 line. `unlogged` already makes it INCOMPLETE, and the excuse would add a second, contradictory "excused" note on the LOG BATCH line.
   - Suppose instead the item has 01-04 files and their lines, but they are ordered after I2. Then `before` is empty for a reason that has nothing to do with the waiver. That is a real ordering fault, and the excuse would wave it through.
   - Mitigation to weigh (R3): excuse only when, in addition, no `STEPS[s]` file exists for any waived step before 05. That matches 024's shape, where 01-04 are absent. A fixture with a waived step file present and lines after I2 must stay INCOMPLETE.
3. **The first I2 round of a waived item stays permanently unbounded, which is a quiet coverage hole.**
   - Reasoning: with no line before I2, the first round has no `prev` (L1331-1332, `continue`) and the whole-item bound is never computed (L1354-1356). After the fix, nothing in LOG BATCH can flag a batch-written waived item's first round (the 083 pattern, RI-010).
   - Today the "not computable ... INCOMPLETE" output at least forces a person to look. After the fix it is a plain listing.
   - Cost or risk: RI-010 is ESCALATED, and this narrows its check for one shape. Keep the reason text explicit, e.g. `first round not bounded`. Write it in the docstring (L174-175) and in gap list (j)/L251 so A1 can see it. LOG TIME (045) still checks every line against its commit.
   - Count: 0 real items today, so the cost is prospective only (finding 16).

## Findings by language
Random languages this cycle: none (N/A)
Languages: N/A (no new external claims). 093 is a BUG fix inside scripts/check_pipeline.py and its tests: waiver parsing, a reason string, and fixtures. It adds or changes no fee, market rule or statistic. The only outside fact used (Python `re.search` vs `match` semantics) is already sourced in 01 findings 11-13 from docs.python.org and is not a new claim.

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| All 7 | N/A (no new external claims) | - | - | - |

## Holes to watch out for (summary)
- **Anchored match, never search.** `Waived: 01 02 03 04 (person: x "(person, 2026-11-19: ok)")` has `who` = "person" and a dated `(person, ...:` that `.search` can find. Only an anchored `.match` at the first parenthesis rejects it. `_build_waived` (L561) has the same latent hole. I found it by reasoning from L550/L561 and did not run it; I3 should probe it. If confirmed for 062, it may need its own item.
- **Scope-aware subset.** Excuse needs `{s in REQUIRED[scope] if s < "05"} <= waived`: FULL {01, 02, 03, 04}, FAST {01, 03}. A FAST person-waived `01 03` item should pass. FULL `01 02 04` should not, because 03 exists and is logged, so `before` is not empty anyway. R1's twin (d) may not reach this branch; make sure each twin really produces "no line before I2".
- **Step files absent.** Consider also requiring that no waived pre-05 step file exists (AGAINST 2).
- **Unreadable request.md.** It must fall back to the strict reason, not the excused one.
- **Only the first `Waived:` line is read** (parse_request L549, `re.search`). A second line is ignored, which fails loud (stays INCOMPLETE). Document it in gap (j).
- **Other strict reasons.** `no pytest time ...` and `log line with no valid time` stay strict for waived items, and the TIMED_FROM `_rule_seen` gate (L938) must still run.
- **Docstrings.** Rewrite L174-175 ("no waiver excuses it") and the L1298-1299 per-round note, so they state the excuse and the unbounded first round.
- **Mutations to name.** (1) Excuse removed → flipped [990] fails. (2) `who` check dropped → twin (c) fails. (3) `.match` → `.search` → twin (e) fails. (4) Date check dropped → twin (b) fails. (5) Subset check dropped → a partial-waiver twin that really reaches the branch fails.

Log fields: 3 for / 3 against | languages: N/A
