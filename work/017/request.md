# Work item 017
Type: BUG
Opened by: A1
Date: 2026-10-30

## What we want
Make the account-size thresholds in `work/001/03-handoff.md` agree with the hand-off's own cash-buffer check.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `work/001/03-handoff.md` implementation map step 1, "How we check it": `(price × 100 × positions) ≤ cash − $200`.
- Same step, text: at $5,000–6,000 "it allows two positions ≤ $28 or one ≤ $55"; Outputs: "2 at ≥ $5.6k". Step 9(a): "single stocks only at ≥ $5.6k".
- Check with the step's own formula:
  - Two positions at $28: 2 × $28 × 100 = $5,600. Needs cash ≥ $5,600 + $200 = **$5,800**, not $5,600. At $5,600 the check fails (5,600 > 5,400).
  - One position at $55: $5,500. Needs cash ≥ **$5,700**. At $5,000 the check fails; at $5,600 the maximum single price is ($5,600 − $200) / 100 = **$54**.
  - At $5,000 two positions are allowed only at ≤ ($5,000 − $200) / 200 = **$24.00** each.
- The $3k case is correct: ($3,000 − $200) / 100 = $28.00. The worked example at $5,600 uses $27 shares (2 × $2,700 = $5,400 ≤ $5,400), so it passes; only the stated thresholds are wrong.

## Root cause and prevention guardrail (BUG only)
Root cause: R3 added the $200 buffer to the $3k rule but carried R1's no-buffer thresholds (N1: $6,000 / 2 = $30, $5,600 = 2 × $28 × 100) into the larger-account rules without re-deriving them from the new formula. Nothing in the R3 instructions or hand-off template asks for each threshold to be re-checked against the rule's own check formula.
Guardrail: add a required "Self-check" section to `templates/research-handoff.md` where R3 re-derives every numeric threshold in the implementation map from the step's "How we check it" formula and shows the arithmetic; add the same duty to `.claude/agents/r3-fact-checker.md`; I3/A1 verify the section exists.

## Recurring issue link (RI-#, if any)
RI-005 (occurrence 1)

## Done looks like
Step 1, step 9(a) and the worked example all use thresholds derived from `(price × 100 × positions) ≤ cash − $200` (two ≤ $28 needs $5,800; $5,600 allows two ≤ $27 or one ≤ $54), and the template + R3 instructions carry the self-check.
