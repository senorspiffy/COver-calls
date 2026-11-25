# 02 Improvements - 101
## What past logs say
- logs/audit/2026-11-24-095.md L47: the probe `TIMED elif unsure("05") -> elif False` left `test_shallow_gated_entries_not_checked` at "1 passed". L63-66: the TIMED, LOG BATCH, Suite and round-heading branches "have no test of their own"; removing one "fails closed (entry back on INCOMPLETE, exit 1 either way), so no wrong pass is possible". It was flagged as a small EFFICIENCY follow-up. That follow-up is this item.
- logs/recurring-issues.md L153 (RI-014, OPEN): "Near miss, not counted: shallow elif branches untested → 101". The RI stays OPEN until 079/081/088-095 merge. 101 adds no guardrail to RI-014 and changes no status. It only closes a test gap inside 095's code.
- The model test is P-e, `test_round_build_shallow_goes_to_unchecked` (tests/test_pipeline_check.py L5239-5252). It is a parametrized shallow / "no git" pair that calls `cp.incomplete` directly, and it uses `committed` holding only the gated step file.
- I re-read scripts/check_pipeline.py L903-1189 and confirmed R1's source claims by reading:
  - `_rule_seen` returns `(None, "")` whenever `env` is set (L910-911).
  - `_unsure` uses equality on SHALLOW_TEXT plus `committed` membership (L983-985).
  - `unsure()` needs `unchecked is not None` (L1029-1030).
  - The four target branches are at L1062, L1091, L1118 and L1135.
  - The fall-through strict paths are at L1081-1083, L1094, L1121 and L1138.
  - Nothing was run: this R2 has no shell.
- RI-001 (one rule, unmeasured reach) has a small echo here. Scratch dir (L1168) is a fifth branch with no shallow test, and it sits outside the request's four (01 open question 1).
- Precedent for languages N/A: 081-098 EFFICIENCY items that touch only the repo's checker (for example 098/02 L75-76).

## 3 ways FOR
1. **Key each case's `committed` to exactly the gated step file. This kills wrong-step mutants as well as `elif False`.**
   - `unsure(step)` looks up `work/<ID>/<STEPS[step]>` in `committed` (L985).
   - TIMED, LOG BATCH and Suite gate on "05" (L1062, L1091, L1118). Round heading gates on the loop `step` (L1135).
   - With `committed={"work/150/05-build-report.md"}` only, a mutant `unsure("06")` in any 05 branch makes `_unsure` False. The entry then stays in `got`, so the shallow assert fails.
   - Round heading needs both a 05 case and a 06 case, each with only its own file in `committed`. A mutant `unsure("05")` in place of `unsure(step)` at L1135 is killed only by the 06 case.
   - So the 5 shallow cases (R1's count: 4 branches, round heading x2) are not padding. Each one pins a distinct key.
   - I3 should run the step-key mutants (`unsure("06")` at L1062/L1091/L1118 and `unsure("05")` at L1135) next to the four `elif False` mutants. Reasoning from the source; UNVERIFIED until run.

2. **Assert the exact lists, not just membership. The fixtures are clean, so this is cheap, and a case then fails by name for leaks as well as for a lost move.**
   - `_item` writes a clean item: timed I2, matching Suite, good Scratch lines, PASS / none verdict (01 findings, tests L19-53). `_rh_item` "keeps its Suite line, so only the round-heading check can fire" (tests L5081-5082).
   - So in each shallow case `got == []` and `u == [(ID, entry)]` hold. In each "no git" case `got == [entry]` and `u == []` hold. All of this is reasoned from the source and is UNVERIFIED until run.
   - Membership alone (P-e's form) misses two kinds of mutant:
     - a mutant that appends to `u` and also leaves the entry in `missing`, for example dropping `bad.remove("I2")` at L1063. Under this mutant `fired not in got` does fail, so membership catches it.
     - a mutant that adds a second, different entry. Membership does not catch this one. Exact lists do.
   - For TIMED this settles 01 open question 2. Rewrite the 05 `Suite:` line to `Suite: 1 passed`, so Suite does not fire and `u` holds only the I2 entry. Do not pin both branches in one case.
   - Fixture detail: the Suite field is split from the LAST I2 log line (L1098-1102). So replace the `_item` I2 field rather than append a second I2 line, or the Suite value must match whichever line is last. Both forms keep `all(... timed=False)` True (L1056), but replacing is simpler.

3. **Unit-level, test-only, one parametrized test with 10 ids. This is the smallest change that meets "fails by name" and leaves full-clone output unchanged by construction.**
   - No change to scripts/check_pipeline.py means `main()` output cannot change (01 finding, last bullet). I2/I3 should still diff the `check_pipeline.py` output before and after, as RI-013 practice.
   - `env` set means `_rule_seen` makes no git call (L910-911). So no fixture repo, no `@NO_GIT`, and no `_commit` are needed. The test is fast, and `test_git_call_census` (088) is untouched.
   - Use one `@pytest.mark.parametrize` over (branch, step, fixture-builder, entry) x (shallow, no-git), with ids like `timed-shallow`, `rh06-nogit`. pytest prints the id of a failing case [https://docs.pytest.org/en/stable/how-to/parametrize.html], so the mutant run names the branch.
   - Five separate functions would also work. One table keeps the 1:1 branch-to-case mapping visible. Either form is fine; I1 should pick and give the reason in one line.

## 3 ways AGAINST
1. **Scope gap: Scratch dir (L1168, item 097) has the same shape and also has no shallow test. Covering 4 of 5 leaves a known hole.**
   - R1's grep of `unchecked=` found only L4970, L4973 and L5248, and none of these is a Scratch case (01 Numbers). After 101, `elif unsure` coverage would be 7 of 8 sites (3 already covered + 4 new).
   - Leaving one out repeats the pattern this item fixes: a branch noticed but untested (095 audit L63).
   - Adding it costs 2 more cases (05, 06). The Scratch branch uses `+=` over a list (L1169), so its entries are per problem.
   - Fixture: remove the `Scratch dir:` line from 05, giving entry `"05 has no Scratch dir: line (item 097)"` (L965).
   - Recommendation for R3: include Scratch as a fifth branch, or else name it explicitly in 05 as deferred, with a follow-up ID. Do not leave it silent.

2. **Calling `incomplete()` directly does not test how `main()` prints `unchecked` (INCOMPLETE NOT CHECKED), and it does not test how `committed` is built.**
   - In `main()`, `committed` comes from `_head_work_files` (L988-992) and `env` from `_anchor_env`. These tests pass both in by hand.
   - The direct call is right for "smallest test per branch". But it means a branch could pass its unit case while the line wiring regresses.
   - That wiring is already covered by 095's M5 / M11 end-to-end tests (095 audit L41, L45: both "1 failed" under their mutations). So this is a limit to state, not a gap to fill.
   - Hole: do not claim in 05 that these tests cover the printed line.

3. **Same file as parallel items, and nothing here has been run yet.**
   - tests/test_pipeline_check.py is the shared test file. Items 099, 100 and 102-104 are open in this checkout, and R1 cites line numbers (L4886, L5239 and others) that will move.
   - Mitigations:
     - append the new test after P-e or at the end of the file;
     - find helpers by name (`_item`, `_rh_item`, `RH_USE`, `I2_ENTRY`), not by line;
     - rebase before I2 if a sibling merges first.
   - R1 and R2 both had no shell. Every "fails under mutation" claim is reasoned from the source and is UNVERIFIED.
   - The TIMED case in particular rests on the claim that `1 files changed | tests 1 passed` passes `log_fields_ok(..., timed=False)` and fails timed (L1055-1056, LOG_FORMAT L551, I2_TIMED L471).
   - If that is wrong, the case lands on the TESTS branch (L1066) and silently retests it. That is exactly the 095 failure mode (T-a's `tests 9/9` took TESTS, not TIMED, 01 finding).
   - Guard: inside the TIMED case, assert the precondition `cp.log_fields_ok("I2", "150", field, timed=False) and not cp.log_fields_ok("I2", "150", field)`. A wrong fixture then fails by name and cannot pass via the wrong branch.

## Findings by language
Random languages this cycle: N/A
Languages: N/A (no new external claims). 101 is an EFFICIENCY item that adds only unit tests for existing branches of this repo's checker. It adds or changes no fee, market rule, statistic or trading behaviour. The only outside facts are git's shallow file and pytest parametrize, both cited by R1 to official docs.

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
- `committed` must hold only the gated step file: 05 for TIMED, LOG BATCH and Suite; 05 or 06 per round-heading case. Otherwise the step-key mutants survive (FOR 1).
- Round heading needs both a 05 case and a 06 case. A single `elif False` kills both, but only the 06 case kills `unsure("05")`.
- TIMED fixture:
  - replace the I2 field with `1 files changed | tests 1 passed` and rewrite `Suite:` to `Suite: 1 passed`;
  - assert the untimed-pass / timed-fail precondition in the test, so it cannot quietly take the TESTS branch (AGAINST 3).
- LOG BATCH: pass `batch_nc={"150": cp.BATCH_STRICT[0]}`. The check uses equality (L1087), so pass the constant, never a substring.
- Assert exact `got` / `u` lists in both shallow and no-git cases (FOR 2). Do not pin two branches in one case.
- Scratch dir (L1168): include it as a fifth branch, or name it as deferred in 05 (AGAINST 1).
- Do not claim these tests cover the printed INCOMPLETE NOT CHECKED line. That is covered by 095 M5/M11 (AGAINST 2).
- Mutant run (I3), one at a time in a scratch copy:
  - 4 (or 5) `elif False` mutants, plus the step-key mutants;
  - each should fail only its named ids;
  - diff full-clone `check_pipeline.py` output before and after (expected empty).
- Find helpers by name, not line. Rebase if 099/100/102-104 touch the test file first.
- Owed by scripts, never typed (item 045): R1's and R2's log lines via `check_pipeline.py --log`. This R2 had no shell.

Log fields: 3 for / 3 against | languages: N/A
