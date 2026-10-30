# 02 Improvements - 006
## What past logs say
- RI-002 occurrence 4. I3 noted it in 002/06 "Notes for later"; I2 judged it "not NaN-to-number" and skipped it. So the standing rule's wording ("NaN") was read too narrowly. It must say "cannot be computed → n/a", whatever the type.
- 001 step 9c: "No margin". The benchmark borrows $600 and breaks the account's own rule.

## 3 ways FOR
1. **`lots = floor(...)`; if 0 → B&H n/a with the reason. Same change in `report.py` L168.** This is the simplest fix that closes the bug: two lines, and the report prints `Excess vs B&H: n/a (100 shares cost more than cash − buffer)`. Reasoning: A1's case (s0 = $36 → floor 0 → `max(1, 0)` = 1 lot → cash −$600).
2. **An account-invariant test for every simulated path (R1): cash ≥ 0 and shares a multiple of 100, for the strategy and each benchmark.** This is the best systemic guardrail in 005/006. It tests the outcome, so it catches the next defaulted benchmark whatever the code looks like (`max(1,`, `or 1`, a hard-coded lot). It is the same kind of check as the 002 tests that the mutation check proved.
3. **It also feeds 005's enumerated policy table (`bh_benchmark: n/a`).** One list of "what happens when X can't be formed" covers both bugs.

## 3 ways AGAINST
1. **A B&H that is "n/a" removes the comparison the report exists to make.** At $3k, any underlying above $28 gives n/a (006/01). The person then sees no benchmark at all. R1's second benchmark, "B&H from the strategy's first buy", fixes this, but it shares the strategy's entry timing. So it must be labelled, and it is not the same comparison. The person has to choose (006/01 open question). Recommend showing n/a plus the labelled first-buy benchmark, because n/a alone hides a useful comparison.
2. **Fractional-share B&H is an option that is not in R1's brief.** It is always feasible and keeps the same start date. But it is not the account the person can hold in 100-share lots for covered calls, so it flatters B&H (no lot drag). Reasoning only; reject unless labelled.
3. **The `max(1,`/`min(1,` grep alone would not have caught this in review.** I2 saw it and still judged it acceptable. Only the behaviour test (FOR 2) and the wider rule wording stop a reviewer from making the same call again.

## Findings by language
See `work/003/02-improvements.md` § Findings by language (random: Arabic, Hindi, Turkish). Little here is specific to 006. Hindi (max loss = share price − premium) supports comparing against an unlevered holding. Turkish confirms the 100-share unit.

## Holes to watch out for (summary)
- V0's "+5.12% excess" is already in a generated report. Regenerate the report after the fix, or mark the old one superseded.
- `metrics` must handle a B&H series of None/n/a without raising, and without turning it into 0.
- The invariant test needs one input where 100 sh > cash − buffer (SYNTH_A × 1.5) and one where it fits, so the test proves both branches.
