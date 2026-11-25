# 01 Research brief - 102
## Question
Part 1: how can a test prove that commit_step's `--trailer` refusals happen before any git call, so that A1's 098 mutant fails? In that mutant the `_trailer_ok` loop is moved to just before `commit-tree` (logs/audit/2026-11-24-098.md L45-46, N1 L50-53), and it currently survives with 40 passed.
Part 2: which of the 7 cutoffs (CHECKLIST_FROM, LOG_CHECK_FROM, TESTS_FORMAT_FROM, SUITE_FROM, TIMED_FROM, WHOLE_DIFF_FROM, VERDICT_FROM) already have a test that fails when the constant is shifted to FROM-1 or FROM+1? What fixture would pin the rest?
Part 3: whether i1's text gets the sentence "one mutant per refusal condition and per *_FROM boundary". **PENDING THE PERSON.** This is a RULE_PATHS edit (`.claude/` is in RULE_PATHS, scripts/check_pipeline.py L524), and the person has not given an OK. This brief does not research or propose wording for it. For the record: `.claude/agents/i1-reviewer.md` holds no "mutant", "_FROM" or "boundary" text today (Grep, 0 matches).

Recurring issues read: RI-010 (ESCALATED; the 098 entry names "commit_step trailer-refusal order untested -> 102" as a near miss) and RI-001 (a rule asserted but never measured: here, "before any git call" is asserted in commit_step.py L13 and L159 but no test measures it). No earlier log covers either part.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
### Part 1: trailer refusals before any git call
1.1 `commit()` runs `_trailer_ok` over the trailers first (L158-160). Its first git call is `run(["rev-parse", "--show-toplevel"])` at L161. Every later git call goes through the `run` parameter, directly or via `_git(run, ...)`: L161, L167, L189 (`_log_blobs(item, old, run)`), L195, L200-205, L212-215, L225. [scripts/commit_step.py L156-230]
1.2 T-b (`test_trailer_refusals_write_nothing`, tests/test_commit_step.py L295-309) runs the script as a child process (`_cli`, L63-66). It compares only `_state` = HEAD + `.git/index` bytes (L59-60). A recording `run` cannot reach a child process, and loose objects are not compared. That is why A1's moved-loop mutant passes (098 audit L45-46, L50-53). [tests/test_commit_step.py L59-66, L295-309; logs/audit/2026-11-24-098.md]
1.3 "Default parameter values are evaluated from left to right when the function definition is executed ... the same 'pre-computed' value is used for each call." So `commit(..., run=run, ...)` (L156) is bound to the module function at import time. Monkeypatching `cs.run` does NOT change what `main()` -> `commit()` uses. A recorder has to be passed as `run=` or patched one level lower, at `subprocess.run`. [https://docs.python.org/3/reference/compound_stmts.html]
1.4 The module `run` calls `subprocess.run(["git", *args], ...)` at call time (L61-67). `subprocess.run` "Run[s] the command described by args. Wait[s] for command to complete, then return[s] a CompletedProcess instance." So patching the `subprocess.run` that commit_step sees records every git call, including those made through main's default `run`. [scripts/commit_step.py L61-67; https://docs.python.org/3/library/subprocess.html]
1.5 The repo already passes a wrapper `run=lambda a, env=None, input=None: ...` that delegates to `cs.run` (T3 L178-186, T5 L225-233). A recording wrapper of the same shape fits the existing style. [tests/test_commit_step.py L178-186, L225-233]
1.6 pytest monkeypatch: "All modifications will be undone after the requesting test function or fixture has finished". `MonkeyPatch.context()` can "limit the patching to the block you want tested". This matters here: the test's own `_g` helper also calls `subprocess.run` (L29-32). If `subprocess.run` is patched, the recorder has to wrap only the `cs.main([...])` call, or it will also record the test's own `_state()` calls. [https://docs.pytest.org/en/stable/how-to/monkeypatch.html; tests/test_commit_step.py L29-32]
1.7 The "no-value" row (`--trailer` alone) is refused in `main` (L235-238) before `commit` is called. Only the main-level form (patched `subprocess.run` + `cs.main([...])`) covers all 6 T-b rows. A `cs.commit(..., run=rec, trailers=(bad,))` form covers the 5 `_trailer_ok` rows only. [scripts/commit_step.py L233-244]
1.8 What survives today and what the recorder shows: in A1's mutant the trailer loop runs after rev-parse, `_log_blobs`, the temp index, `hash-object -w` and `write-tree`. The recorder's first entry would be `rev-parse --show-toplevel`, so `calls == []` fails at any position after L160. This is inference from the code order and has not been run (UNVERIFIED until I2/I3 run the mutant).
1.9 The harm A1 named can also be measured directly. `git hash-object -w`: "Actually write the object into the object database". `git write-tree`: "Creates a tree object using the current index". In the fixture, the working log holds L150 (tests/test_commit_step.py L48), so `_log_blobs` yields a blob, and the moved-loop mutant would add loose objects under `.git/objects/` before refusing. A filesystem-only count of the files under `.git/objects/` before and after (no git call) would also fail under the mutant. That expectation is inference, not run (UNVERIFIED). [https://git-scm.com/docs/git-hash-object; https://git-scm.com/docs/git-write-tree; tests/test_commit_step.py L44-50]

### Part 2: FROM / FROM-1 pins for the 7 cutoffs
2.1 Values and gate sites:
- CHECKLIST_FROM 41: L433; gate L1032.
- LOG_CHECK_FROM 45: L437; gates L1049, L1385, L1507.
- TESTS_FORMAT_FROM 76: L438; gates L811, L824, L1066.
- SUITE_FROM 87: L441; gate L1097.
- TIMED_FROM 90: L444; gates L814, L827, L1055, L1087.
- WHOLE_DIFF_FROM 70: L498; gate L2017.
- VERDICT_FROM 71: L502; gate L1174.
[scripts/check_pipeline.py]
2.2 Key pattern: a test that takes its boundary ID from the constant (`SF = _cp().SUITE_FROM`, tests/test_pipeline_check.py L3680, used in S1-S4 L3691-3712; `f"{cp.TIMED_FROM:03d}"` L4402-4404) moves with a shifted constant, so it can never kill a shift. Only literal IDs (`"097"`/`"096"`, L5428) or a literal value assert (`assert cp.TIMED_FROM == 90`, L4405) can. [tests/test_pipeline_check.py L3680-3712, L4402-4405, L5428-5434]
2.3 Existing coverage, from reading the tests (Grep for the literal IDs 041/044/045/075/076/086/087/070/071). Not run, so each "survives" below is UNVERIFIED until I2/I3 run the mutant:
| Constant | FROM-1 shift killed by | FROM+1 shift killed by |
|---|---|---|
| CHECKLIST_FROM 41 | `test_incomplete_06_and_missing_log_line` (040 not listed, L428-433) | none found (041 appears only at L446/L783/L815 with no step files; 130/131 are far above) |
| LOG_CHECK_FROM 45 | `test_malformed_log_line_is_incomplete` (044, L502-511); `test_log_line_after_its_commit_is_flagged` (044 not in LOG TIME, L538) | none found (no literal 045 test; 150 is far above) |
| TESTS_FORMAT_FROM 76 | `test_i2_tests_field_cutoff` (075 old form accepted, L727-731, and 074/075/076/077 INCOMPLETE, L736-749); `test_old_i2_hint_fits_old_format` (L766-768) | the same two tests (076 refuses `9/9`, L732-733; log_hint 076, L768) |
| SUITE_FROM 87 | none found (no literal 086; S1-S4 use SF) | none found (S2 uses SF; item 151 tests kill only shifts above 151) |
| TIMED_FROM 90 | `test_log_i2_untimed_refused_from_090` (089 untimed accepted, L4392); `test_i2_summary_line_accepted` on 089 (L704-712) | only the literal value assert in `test_timed_hint_fits_timed_format` (L4405); no behavior pin at literal 090 (T1 uses 990, L4383-4391) |
| WHOLE_DIFF_FROM 70 | `test_t7_items_before_cutoff_are_not_checked` (069) | `test_t7b_cutoff_edge_item_070_is_checked`, `test_t7c_...`, `test_t7d_...` (literal `== 70`) |
| VERDICT_FROM 71 | none found (T3 uses 060/065 and 173, L2180-2193) | none found |
[tests/test_pipeline_check.py; tests/test_real_data_field.py L116-157]
2.4 Possible incidental kill (UNVERIFIED): in tests/test_real_data_field.py, item 070's 06 is `x\n` with no Verdict line (L129). A VERDICT_FROM=70 mutant may add a verdict entry there, but t7b checks with `startswith` and t7c with `in` (L132, L147), so it probably still passes. Only a run can say.
2.5 `_item` always writes a 05 `Suite:` line equal to the I2 field (L52-53) and a 06 with a Verdict (L54-58). So default fixtures never trip SUITE_FROM or VERDICT_FROM, which explains why shifts of those two survive. [tests/test_pipeline_check.py L35-66]
2.6 TESTS_FORMAT_FROM, SUITE_FROM, TIMED_FROM and VERDICT_FROM are also gated by `_rule_seen` when a check fires (L1057, L1067, L1115, L1183). The existing tests show that with no anchor `_rule_seen` returns `(None, "")` (L2976-2977, L3001-3002), and the existing non-git tmp fixtures (e.g. T3 L2180-2193, S2 L3698-3703) get the strict entry. So non-git fixtures pin the numeric boundary with no RULE_FILE setup. A git fixture would need the constant in its RULE_FILE at the adding commit, or the item lands in RULE NOT SEEN instead (098/03 row 02 FOR 2). [scripts/check_pipeline.py; tests/test_pipeline_check.py; work/098/03-handoff.md L62]
2.7 CHECKLIST_FROM and LOG_CHECK_FROM are purely numeric gates ("stay numeric", check_pipeline.py L383). [scripts/check_pipeline.py L381-383]
2.8 A shift mutant changes every gate site of a constant at once, so one FROM/FROM-1 pair per constant kills both shifts. An operator mutant at a single site (`>=` -> `>`) is a different mutant class. LOG_CHECK_FROM (3 sites), TESTS_FORMAT_FROM (3) and TIMED_FROM (4) would need one pin per site to kill those. The request asks only for shifts; per-site pins are an open question for R2/R3. (Inference from finding 2.1.)
2.9 The literal-ID parametrized pattern already exists for SCRATCH_FROM: `@pytest.mark.parametrize("item, entry", [("097", True), ("096", False)], ids=["FROM", "FROM-1"])` (L5428). pytest documents parametrize as letting you "define multiple sets of arguments and fixtures at the test function or class". [tests/test_pipeline_check.py L5428; https://docs.pytest.org/en/stable/how-to/parametrize.html]
2.10 Proposed literal fixtures for the four constants with a gap. Each comes from an existing helper. None has been run (UNVERIFIED):
- CHECKLIST_FROM: `_item(root, "041", ALL, logged=False)` gives `041 (no log line for R1 R2 R3 I1 I2 I3)`; `"040"` gives no entry (same shape as L424/L428/L431).
- LOG_CHECK_FROM: `_item(root, "045", ALL)` plus the appended line `12:00 | I2 | 045 | see 05 | tests 1/1` gives `045 (log line for I2 does not match its format (item 045)`; `044` gives none (shape of L502-511).
- SUITE_FROM: `_suite_item(root, "x\n", item="087")` gives `INCOMPLETE: 087 (05 has no 'Suite:' line (item 082))`; `item="086"` gives `INCOMPLETE: none` (shape of S0 L3684-3688). 086 is below TIMED_FROM, and the default I2 field (FIELDS L19) is well-formed there.
- VERDICT_FROM: `_item(root, "071", ALL, verdict=None)` gives `071 (06 has no readable 'Verdict: PASS' or 'Verdict: FAIL' line (item 071))`; `"070"` gives none (shape of T3 L2185-2192). With no git, 070's REAL-DATA check makes no INCOMPLETE entry (inference).
- TIMED_FROM (adds a behavior pin at literal 090): `_log(tmp, "I2", "090", "1 file changed | tests 5 passed")` gives exit 2 with the timed hint, and `"089"` gives exit 0 (shape of L4385-4392).
Each row also gets a literal `assert cp.<NAME> == <N>`, so the parametrized test names the constant it pins.

## Numbers used (show the math)
- 7 constants. 2 are already pinned both ways by behavior tests (TESTS_FORMAT_FROM, WHOLE_DIFF_FROM). 1 is pinned both ways, but the FROM side only by a literal value assert (TIMED_FROM). 2 are pinned on the FROM-1 side only (CHECKLIST_FROM, LOG_CHECK_FROM). 2 are not pinned on either side (SUITE_FROM, VERDICT_FROM). Check: 2 + 1 + 2 + 2 = 7.
- Shift mutants to run: 7 constants × 2 directions = 14. By the table in 2.3, 3 × 2 = 6 are expected killed today, plus 2 FROM-1 kills (CHECKLIST_FROM, LOG_CHECK_FROM) = 8. The other 6 are expected to survive: CHECKLIST_FROM+1, LOG_CHECK_FROM+1, SUITE_FROM±1, VERDICT_FROM±1 (6 = 14 − 8). These are inferences, not measured (RI-001: I2/I3 must run all 14).
- Boundary arithmetic, rule "checked iff int(ID) >= FROM":
  - 41: 041 checked (41 >= 41), 040 not (40 < 41).
  - 45: 045 checked, 044 not.
  - 87: 087 checked, 086 not.
  - 71: 071 checked, 070 not.
  - 90: 090 needs the time, 089 does not.
  - Shift to FROM+1: the FROM row fails (e.g. 87 >= 88 is false). Shift to FROM-1: the FROM-1 row fails (e.g. 86 >= 86 is true).
- Part 1: T-b has 6 rows (L296-301). 5 are `_trailer_ok` refusals and 1 is main's usage refusal. The main-level recorder covers 6 of 6. The `commit(run=rec)` form covers 5 of 6.

## Fit for a ~$3k account
Not applicable to trading. This is test-only pipeline work: no ticker, strike, premium, assignment, dividend, tax or commission is involved, so `ccbot/screen.TESTS` and `MISSING_POLICY` do not apply. As proposed, parts 1-2 change only tests/test_commit_step.py and tests/test_pipeline_check.py. `tests/` is in CODE_PATHS but not in RULE_PATHS (scripts/check_pipeline.py L524-526). Part 3 would edit `.claude/` (RULE_PATHS) and is pending the person.

## Open questions
1. Part 1 form: the main-level recorder (patched `subprocess.run`, scoped with `monkeypatch.context()`, covers 6 of 6 rows), or `commit(run=rec)` (5 rows)? Should the filesystem loose-object count (1.9) be added as a second assertion?
2. Part 2 scope: shifts only (14 mutants), or also per-site `>=` -> `>` operator mutants for the multi-site constants (2.8)?
3. Should TIMED_FROM's FROM side get a literal-090 behavior pin, even though `== 90` already kills the shift (2.3)?
4. Part 3 (the i1 sentence, RULE_PATHS): pending the person's OK. Not researched here.
5. Every "killed" and "survives" in 2.3 and 1.8 comes from reading the code. They are UNVERIFIED until the 14 shifts and the moved-loop mutant are run.
