# 01 Research brief - 101
## Question
Item 095 added `elif unsure(step)` branches to `scripts/check_pipeline.py::incomplete`. Four of them have no test of their own: TIMED, LOG BATCH, Suite and round heading. What is the smallest test per branch that fails by name when that branch is replaced with `elif False`, with the full-clone output unchanged? (EFFICIENCY, RI-014.)

Prior work read first: logs/recurring-issues.md RI-014 (status line 2026-11-24: "Near miss, not counted: shallow elif branches untested → 101"), logs/audit/2026-11-24-095.md (TIMED probe `elif unsure("05")` → `elif False`: test_shallow_gated_entries_not_checked "1 passed"), work/095/06-verification.md L31 (I3 probe: 431 passed, 2 skipped with TIMED removed), work/095/07-audit-task.md point 4, logs/audit/2026-11-24.md L59, logs/efficiency/2026-11-24.md L4.

Tool limit for this run: R1 had no shell, so nothing below was executed. Every behaviour claim about the code comes from reading the source (file:line given). R3/I1 must confirm the claims by running the code.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- Git treats every commit listed in `$GIT_DIR/shallow` as a root commit: "lists commit object names and tells Git to pretend as if they are root commits". So in a shallow clone the anchor commit that `_rule_seen` needs may have no readable history. [https://git-scm.com/docs/shallow]
- `git clone --depth N` writes `$GIT_DIR/shallow`, and `git fetch --depth` updates it. [https://git-scm.com/docs/shallow]
- `@pytest.mark.parametrize` "enables parametrization of arguments for a test function". This gives one shallow / strict pair per branch, as P-e already does. [https://docs.pytest.org/parametrize.html]
- Repo (read, not run): `_rule_seen` returns `(None, "")` whenever `env` is set (scripts/check_pipeline.py L910-911). So with `env=cp.SHALLOW_TEXT` no git repo and no anchor are needed, and every gate reaches its `elif unsure(...)`.
- Repo (read): `_unsure` is True only when `env == SHALLOW_TEXT` and `work/<ID>/<step file>` is in `committed`, or `committed` is None (L977-985). `unsure()` also requires `unchecked is not None` (L1029-1030).
- Repo (read): these are the `elif unsure` branches in `incomplete` and their trigger conditions:
  - TIMED, L1062. ID >= TIMED_FROM (90, L444). I2 is in `bad`, and every own I2 line passes `log_fields_ok(..., timed=False)` (L1055-1056). This means a pytest-form I2 field with no ` in <s>s` time, e.g. `1 files changed | tests 1 passed` (LOG_FORMAT I2, L551; I2_TIMED, L471).
  - TESTS, L1076. Already covered by T-a / T-a3 (tests/test_pipeline_check.py L4886, L4923; the fixture I2 field `tests 9/9` fails LOG_FORMAT, so it takes the TESTS branch, not TIMED). This explains why the TIMED mutation stayed green.
  - LOG BATCH, L1091. `batch_nc[ID]` is one of BATCH_STRICT (L487) and ID >= 90. `batch_nc` is a parameter of `incomplete`, so a unit test can pass it directly.
  - Suite, L1118. ID >= SUITE_FROM (87), 05 exists, and the last I2 line passes the untimed form. The branch fires on: no `Suite:` line, more than one, or a mismatch (L1108-1113).
  - Round heading, L1135. ID >= ROUND_HEADING_FROM (92), and `stray_run_headings` finds a heading in 05 or 06. It is keyed on the loop's `step`, so 05 and 06 each have a path.
  - Round build, L1150 (098). Has its own shallow test, `test_round_build_shallow_goes_to_unchecked` (P-e, tests L5239-5252). That test is the model for this item.
  - Scratch dir, L1168 (097). A grep of tests/test_pipeline_check.py for `unchecked=` finds only L4970, L4973 and L5248. None of these is a Scratch case. It looks untested, but this is not in the request's four (see Open questions). UNVERIFIED by mutation.
  - VERDICT, L1186. Covered by T-a (NO_SENT_BACK in the INCOMPLETE NOT CHECKED line, L4893).
- Repo (read): the existing fixtures fire only the targeted check:
  - `_item(root, "150", ALL, date=...)` writes a clean item: timed I2 field `1 files changed | tests 1 passed in 0.01s` (tests L19), a matching `Suite:` line (L52-53), good `Scratch dir:` lines for IDs >= 97 (L24-27), and `Verdict: PASS` / `Sent back to: none`.
  - `_rh_item(root, body05=RH_P1)` fires only the round-heading check (L5080-5089, L5077).
  - A clean `_item` therefore fires only the check each test adds.
- Repo (read): under the `elif False` mutation, each branch's entry falls through to the strict path:
  - TIMED: I2 stays in `bad` → L1081-1083 appends the same text as `I2_ENTRY` (tests L4870).
  - LOG BATCH: L1094.
  - Suite: L1121.
  - Round heading: L1138.
  - `seen` is None and `sha7` is "", so no note is added. A test that asserts `(ID, entry) in unchecked and entry not in returned` therefore fails under the mutation. UNVERIFIED by running (no shell in this run).
- Repo (read): a test-only change does not touch scripts/check_pipeline.py, so the full-clone output cannot change. I2/I3 should still diff `check_pipeline.py` output before and after (RI-013 practice).

## Numbers used (show the math)
- Branches in the request: 4 (TIMED, LOG BATCH, Suite, round heading). Round heading has 2 steps (05, 06), so 5 shallow cases with 5 matching strict ("no git") controls = 10 parametrized cases, if one parametrized test per branch is used.
- `elif unsure` sites in `incomplete`: 8 (L1062, L1076, L1091, L1118, L1135, L1150, L1168, L1186), counted from the grep above. With a named shallow test: TESTS, round build, VERDICT = 3. Not covered: TIMED, LOG BATCH, Suite, round heading, Scratch = 5. The request covers 4 of these 5.
- Cutoffs the fixture ID must clear: TIMED_FROM 90, SUITE_FROM 87, ROUND_HEADING_FROM 92 (L441-447). RH_ID "150" clears all three.

## Proposed shape (for R3/I1; not a plan)
- Model each test on P-e (tests L5239-5252). The setup is `u = []` followed by this call:
  ```
  got = cp.incomplete(d, logs=root/"logs", env=cp.SHALLOW_TEXT | "no git", not_seen=[], unchecked=u, committed={f"work/150/{step file}"})
  ```
  - Shallow case: assert `(ID, entry) in u and entry not in got`.
  - "no git" case: assert `entry in got and (ID, entry) not in u`.
  - No `@NO_GIT` is needed (no git call is reached; L910).
- TIMED fixture: `_item` 150, I2 log field replaced with `1 files changed | tests 1 passed`, and the 05 `Suite:` line rewritten to `Suite: 1 passed`. Otherwise Suite also fires, and it lands in `u` too under shallow. Entry = `I2_ENTRY`.
- LOG BATCH fixture: clean `_item` 150, plus `batch_nc={"150": cp.BATCH_STRICT[0]}`. Entry = `f"LOG BATCH not computable: {cp.BATCH_STRICT[0]} (item 090)"`.
- Suite fixture: clean `_item` 150 with the `Suite:` line removed from 05. Entry = `"05 has no 'Suite:' line (item 082)"`.
- Round heading fixture: `_rh_item(body05=RH_P1)` and `_rh_item(body06=...)`, with `committed` holding that step's file. Entry text per L1129-1130 (`RH_USE`).
- Mutation check per branch: `elif unsure(...)` → `elif False` in a scratch copy. Exactly the matching shallow case should fail by name, and the other three should stay green.

## Fit for a ~$3k account
- No trading effect. This is test-only coverage of the pipeline checker. It costs no commissions or capital, and has no assignment, dividend or tax effect. Today the branches fail closed: removing one puts the entry back on INCOMPLETE, exit 1 (095/06 L31). So the account's process risk is a lost test signal, not a wrong pass.

## Open questions
- Scope: should the Scratch dir branch (L1168, item 097) get the same test here? It has the same shape and no shallow test was found by grep. The request names only four branches. R3 to decide; adding it would make 5 mutations.
- Should the TIMED case also pin that Suite moves to `u` when both fire (membership vs exact list)? Asserting exact `u` is stronger but couples two branches.
- R1 could not run `scripts/check_handoff.py 101` or `check_pipeline.py --log R1 101 ...` (no shell in this run). The sources count and the R1 log line are still owed, and must be produced by those scripts, never typed (item 045).
