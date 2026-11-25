# 02 Improvements - 108
## What past logs say
- A1's audit of 101 judged the constant `SE_FIELD` precondition "Enough" and listed the read-back as an optional EFFICIENCY follow-up, not a finding. The same note covers the three-blank-line style nit [logs/audit/2026-11-24-101.md L43-47, L65-67]. So 108 is a stricter pin, not a bug fix. No result changes today.
- A1's mutant table for 101: `elif False` at the TIMED `elif unsure("05")` (then L1062) and the step-key mutant `unsure("06")` each failed only `timed05-shallow` [logs/audit/2026-11-24-101.md L30, L35]. Those are the 2 mutants 108 must re-run. I re-read the branch: the line is now L1073 [scripts/check_pipeline.py L1073], as R1 says.
- RI-014 (checker result depends on clone depth) is the parent issue [logs/recurring-issues.md L152-155]. 108 touches only its test, not the checker.
- RI-002 (a missing value silently treated as a pass) is the hole that R1 findings 17-18 guard against: an empty `own_i2` makes `all()` vacuously true, and a no-op `re.sub` gives the same field back. Past occurrences are in logs/audit/2026-10-30.md L7 onward. R1 is right to ask for both guards.
- The R2 log lines for 101, 099-103 and most EFFICIENCY items are `languages: N/A` [logs/research/2026-11-24.md L29-34]. That is consistent with this item.
- I checked R1's repo citations on the branch. All hold (tests L17-19, L30-32, L52-53, L60-66, L5332-5353, L5403-5404; check_pipeline L476, L1060-1076), with one exception, given below in AGAINST 1.

## 3 ways FOR
1. **Do both parts: read the field back and derive the two edits. Then delete `SE_FIELD`.** This answers R1's open question 1. Changing only L5404 would not meet Done (a): if `FIELDS["I2"]` changes, `_se_edit` at L5351 fails by name, because the literal `"tests 1 passed in 0.01s"` would no longer be in the log [tests/test_pipeline_check.py L5338, L5351; R1 finding 10]. So build both parts from one value:
   - `timed = _field("I2", RH_ID)`
   - `untimed = re.sub(r" in \d+\.\d+(?:s| seconds)", "", timed, count=1)`, which follows I2_TIMED's time shape [scripts/check_pipeline.py L476]
   - `assert untimed != timed` (R1 finding 18)
   - edit the log line `timed` to `untimed`
   - edit 05's `Suite: <timed tests part>` to `Suite: <untimed tests part>`, using the same `split(' | tests ', 1)[1]` as `_item` L53 (this answers open question 3: the 082 Suite check then still sees equal parts)

   Leave the strip pattern unanchored. I2_TIMED allows optional `(H:MM:SS)` and `(...)` tails after the time, and an end-anchored strip would miss a field that has one [L476]. Once the edits are derived, nothing reads `SE_FIELD`, so delete it. Its only reader is L5404 [R1 finding 4].
2. **The precondition should read the log the same way `incomplete` does.** This answers open question 2. Run `cp.LOG_LINE` over `cp._log_text(tmp_path / "logs")[0]`, filter on `m[3] == "I2" and m[4] == RH_ID`, and `assert len(own_i2) == 1`. Then assert `log_fields_ok("I2", RH_ID, own_i2[0][5], timed=False) and not log_fields_ok("I2", RH_ID, own_i2[0][5])`. This is the same expression as the gate at scripts/check_pipeline.py L1064-1067, so the precondition tests what the gate tests. The count of 1 comes from the fixture writing one I2 line for 150 [R1 "Numbers used"]. It closes the vacuous-`all()` hole [https://docs.python.org/3/library/functions.html, R1 finding 17]. Also assert `whys == []` from `_log_text`. That way an unreadable log fails here and does not take the `log_whys` path, which skips the whole block [L1060].
3. **The Done (a) probe is cheap and touches no other test.** `_field` reads `FIELDS` when it is called, not at import [tests/test_pipeline_check.py L30-32]. So `monkeypatch.setitem(FIELDS, "I2", "2 files changed | tests 3 passed in 0.02s")` before `setup(...)` changes only that test's fixture, and pytest undoes it afterwards. That avoids the shared-constant problem in R1's open question 3. The probe can be a one-off I2 run recorded in 05. Better, it can be a permanent extra param (`timed05alt`), so (a) stays pinned and is not a single manual check. I suggest the permanent param. The cost is 2 more test ids.

## 3 ways AGAINST
1. **R1 open question 2 has a wrong call shape.** `cp._item_lines(tmp_path / "logs")[RH_ID]` would raise or give the wrong object. `_item_lines` returns a tuple, `({ID: [...]}, unreadable)` [scripts/check_pipeline.py L1406-1407], so the dict is `[0]`. Whoever picks that reader must index `[0][RH_ID]`, check `unreadable` is empty, and filter on agent `"I2"` (tuple slot 1). This is another reason to prefer the `LOG_LINE` + `_log_text` form in FOR 2, which mirrors L1064-1065 directly.
2. **It is extra work for no change in result, and it couples the test to more private names.** A1 called the constant "Enough": `elif False` at the gate already fails only timed05, which shows the fixture reaches the TIMED branch [logs/audit/2026-11-24-101.md L44-46]. The read-back adds `cp.LOG_LINE` and `cp._log_text`. A rename of either would break this test, though by name, not silently. The test file already uses private names such as `cp._rule_seen` [R1 open question 2], so the added risk is small. The gain is (a), and it is real: today any change to `FIELDS["I2"]` breaks timed05 with a confusing `old in text` error.
3. **A derived edit can hide a fixture that no longer exercises the gate.** Suppose a later `FIELDS["I2"]` is valid timed but its untimed form fails `LOG_FORMAT["I2"]`, for example a stats form that only I2_TIMED accepts. The read-back precondition then fails. That is the correct outcome, but it would look like a 108 regression. Two more cases: the strip removes nothing (guarded by `untimed != timed`), or it removes too much. The edit-site guards stay: `_se_edit`'s `old in text` [L5338] and `count=1`. The 2 mutants from A1 L30 and L35 must be re-run after the change. Each must still fail `timed05-shallow` only (Done (b)), and also the new `timed05alt-shallow` if that param is added. Whether the untimed form of any future field passes LOG_FORMAT is UNVERIFIED. It is not knowable now.

Out of scope: A1's blank-line nit (L5329-5331, L5412-5413; R1 open question 4). Fix it only if I1 is already editing those exact lines; it is cosmetic. I recommend it, because the 101 block is the area being edited and a one-line diff costs nothing. Either way, record it in 05.

## Findings by language
Languages: N/A (no new external claims). This is a test-only change inside this repo (deriving a fixture string and reading back a log line). It adds no fee, rule or market fact. The only outside references are R1's existing Python docs citations for `all()` and `re`.
Random languages this cycle: N/A
| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | N/A | | | |
| Mandarin Chinese | N/A | | | |
| Spanish | N/A | | | |
| Japanese | N/A | | | |
| N/A | N/A | | | |
| N/A | N/A | | | |
| N/A | N/A | | | |
## Holes to watch out for (summary)
- `_item_lines` returns `(dict, unreadable)`, not a dict. R1's suggested `[RH_ID]` index is wrong (AGAINST 1).
- Vacuous `all()` on an empty I2 list: assert `len(own_i2) == 1`, and assert `whys == []` from `_log_text` (FOR 2).
- `re.sub` no-op: assert the derived untimed field differs from the timed one. Do not anchor the strip at the end (FOR 1).
- Done (a) needs the two `_se_timed05` edit strings derived too, not only L5404. Probe it with `monkeypatch.setitem(FIELDS, "I2", ...)`, never by editing the shared constant (FOR 3).
- Re-run both A1 mutants (`elif False` at L1073 and the step-key `unsure("06")`). Each must fail `timed05-shallow`, and no `-nogit` id may fail (AGAINST 3).

Log fields: 3 for / 3 against | languages: N/A
