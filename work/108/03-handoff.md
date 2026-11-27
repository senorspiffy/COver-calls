# 03 Research hand-off - 108
Status: READY
Recurring issues checked: RI-001 (ESCALATED), RI-014 (OPEN); also RI-002, RI-004, RI-005, RI-006, RI-012 (GUARDED, same failure shapes). See "Recurring issues" under the map.

All repo citations re-read on branch daily-fixes/2026-11-25 on 2026-11-25. External sources were opened 2026-11-25: docs.python.org functions.html (all), re.html (sub, fullmatch), docs.pytest.org/monkeypatch.html (setitem, undo). No non-English sources.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| R1 F1: A1 judged the constant "Enough" and listed the read-back as an optional EFFICIENCY follow-up | logs/audit/2026-11-24-101.md L43-47, L65-67 | VERIFIED | – |
| R1 F2: I3 noted that the precondition tests the constant `SE_FIELD`, not the read-back field | work/101/06-verification.md L25 | VERIFIED | – |
| R1 F3: 101's 03 step 2 hard-codes `"1 files changed \| tests 1 passed"` | work/101/03-handoff.md L73 | VERIFIED | – |
| R1 F4: `SE_FIELD` is defined at L5332 and read only at L5404 | tests/test_pipeline_check.py; grep `SE_FIELD` gives 2 hits (L5332, L5404) | VERIFIED | – |
| R1 F5: the precondition never reads the log file | tests/test_pipeline_check.py L5403-5404 | VERIFIED | – |
| R1 F6: `_se_timed05` hard-codes two edits (log and 05 Suite) | tests/test_pipeline_check.py L5349-5353 | VERIFIED | – |
| R1 F7: `_se_edit` asserts `old in text` | tests/test_pipeline_check.py L5335-5339 | VERIFIED | – |
| R1 F8: the I2 field comes from `FIELDS["I2"]` via `_field`; `_item` writes `12:00 \| I2 \| <item> \| <field>`; Suite = `split(' \| tests ', 1)[1]` | tests/test_pipeline_check.py L17-19, L30-32, L52-53, L60-66 | VERIFIED | – |
| R1 F9: `RH_ID, RH_DAY = "150", "2026-11-21"`; `_rh_item` calls `_item(root, item, ALL, date=RH_DAY)` | tests/test_pipeline_check.py L5150, L5155-5158 | VERIFIED | – |
| R1 F10: changing `FIELDS["I2"]` today fails at `_se_edit` L5351, so Done (a) also needs L5351-5352 derived | tests L5338, L5351-5352 (literal `tests 1 passed in 0.01s` disappears if the field changes); request.md L15 | VERIFIED | – |
| R1 F11: `LOG_LINE` regex; group 5 holds the fields | scripts/check_pipeline.py L576 | VERIFIED | – |
| R1 F12: the TIMED gate is `"I2" in bad` and `all(log_fields_ok(..., timed=False) for m in own_i2)` | scripts/check_pipeline.py L1060-1067 | VERIFIED | – (the gate also needs `int(ID) >= TIMED_FROM` and `not log_whys`, L1060/L1066; 150 clears both) |
| R1 F13: `_item_lines(logs)` returns `{ID: [...]}` | scripts/check_pipeline.py L1406-1430 | WRONG | It returns a tuple `({ID: [(stamp, agent, team, file idx, line idx, fields)]}, unreadable)` (L1407, L1430), so the dict is `[0]`. The map uses `LOG_LINE` over `_log_text`, not `_item_lines` (02 AGAINST 1) |
| R1 F14: the shallow TIMED branch is `elif unsure("05"):` at L1073-1076 (A1's "M L1062" at c771a21) | scripts/check_pipeline.py L1073-1076; logs/audit/2026-11-24-101.md L30 | VERIFIED | – |
| R1 F15: `timed=True` applies `I2_TIMED` from TIMED_FROM 90; `timed=False` applies `LOG_FORMAT["I2"]` (time optional) | scripts/check_pipeline.py L449, L476, L557, L815-827 | VERIFIED | – |
| R1 F16: in `I2_TIMED` the time `in \d+\.\d+(?:s\| seconds)` comes right after the stats | scripts/check_pipeline.py L476 | VERIFIED | – |
| R1 F17: `all()` is True for an empty iterable | https://docs.python.org/3/library/functions.html ("Return True if all elements of the iterable are true (or if the iterable is empty)") | VERIFIED | – |
| R1 F18: `re.sub` returns the string unchanged when the pattern is not found | https://docs.python.org/3/library/re.html ("If the pattern isn't found, string is returned unchanged.") | VERIFIED | – |
| R1 F19: `re.fullmatch` matches only the whole string; `log_fields_ok` uses it | https://docs.python.org/3/library/re.html; scripts/check_pipeline.py L823-827 | VERIFIED | – |
| R1 N1: the fixture writes 6 log lines for 150, exactly 1 of them I2 | tests L15 (AGENTS has 01-06), L91-92 (ALL = 01..07), L60-66 (07 has no agent) | VERIFIED | – |
| R1 N2: 3 coupling points to the literal (L5332, L5351, L5352) | tests/test_pipeline_check.py | VERIFIED | – |
| R1 N3: 2 mutants to re-run (`elif False` and step key `unsure("06")` at the TIMED branch) | logs/audit/2026-11-24-101.md L30, L35 | VERIFIED | – |
| R1 OQ4: the style nit is three blank lines at L5329-5331 and one blank line at L5412-5413 | tests/test_pipeline_check.py L5327-5331, L5411-5413 | WRONG | The three blank lines are L5328-5330 (L5331 is the `# Item 101` comment). The single blank line is L5412, before `def` at L5413. Find both by text, not by line number |
| R2: A1 called the constant "Enough", and 108 is a stricter pin, not a bug fix | logs/audit/2026-11-24-101.md L43-47 | VERIFIED | – |
| R2: the TIMED `elif unsure("05")` is now at L1073 | scripts/check_pipeline.py L1073 | VERIFIED | – |
| R2: RI-014 is the parent issue | logs/recurring-issues.md L152-158 | VERIFIED | – |
| R2: R2 lines for 099-103 are `languages: N/A` | logs/research/2026-11-24.md L29-34 | VERIFIED | – |
| R2 FOR 1: the strip `r" in \d+\.\d+(?:s\| seconds)"` with `count=1`, unanchored, follows I2_TIMED; the optional `(H:MM:SS)` / `(...)` tails come after the time | scripts/check_pipeline.py L476 | VERIFIED | – |
| R2 FOR 1: deriving 05's Suite edit with the same split keeps the 082 Suite check equal | scripts/check_pipeline.py L1108-1113 (Suite compared with the last I2 field's tests part, `timed=False`); tests L53 | VERIFIED | – |
| R2 FOR 2: `LOG_LINE` over `_log_text(...)[0]`, filtered on `m[3]=="I2" and m[4]==ID`, mirrors L1064-1065; non-empty `whys` skips the block (L1060) | scripts/check_pipeline.py L843-856, L1052-1067 | VERIFIED | – |
| R2 FOR 3: `_field` reads `FIELDS` at call time; `monkeypatch.setitem` patches a dict for one test and is undone afterwards | tests L30-32; https://docs.pytest.org/monkeypatch.html ("All modifications will be undone after the requesting test function or fixture has finished.") | VERIFIED | – |
| R2 AGAINST 1: `_item_lines` returns `(dict, unreadable)`, so R1's `[RH_ID]` index is wrong | scripts/check_pipeline.py L1406-1407, L1430 | VERIFIED | – |

**Totals:** 32 rows checked → **30 VERIFIED as-is**, **2 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
None. The two WRONG claims (R1 F13 and R1 OQ4's line numbers) are kept with corrections, so they count as fixed. R2 AGAINST 3's sentence about whether any future field's untimed form passes LOG_FORMAT is not a claim of fact. R2 marks it UNVERIFIED as not knowable, and step 2's precondition turns that case into a named test failure.

## Implementation map
Decisions on the open questions: (1) do both parts, read the field back and derive the edits, then delete `SE_FIELD`. (2) Use `cp.LOG_LINE` over `cp._log_text(...)[0]`. (3) Derive the Suite edit with the same split. (4) Fix the blank-line nit, since these lines are being edited anyway. This is a test-only change in one file. Find each place by name, not by line number.

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | tests/test_pipeline_check.py, `_se_timed05`: derive both edits from one value. `timed = _field("I2", RH_ID)`; `assert " \| tests " in timed`; `untimed = re.sub(r" in \d+\.\d+(?:s\| seconds)", "", timed, count=1)`; `assert untimed != timed`. Then `_se_edit(<impl log RH_DAY>, timed, untimed)` and `_se_edit(05, "Suite: " + timed.split(" \| tests ", 1)[1], "Suite: " + untimed.split(" \| tests ", 1)[1])`. `_se_edit`'s `old in text` stays | `FIELDS["I2"]` via `_field`, the fixture log, 05 | edited log I2 line and Suite line | For today's field the derived edits equal the old literals (Self-check rows 1-2), so `-k shallow_elif_branch` gives `14 passed` before step 3 | Today's FIELDS["I2"]: 1 of 1 fixture I2 lines is edited (1 I2 line out of 6 for 150, R1 N1); the strip removes 1 match. Computed by hand (Self-check 1); I2 measures it with the step 1 run |
| 2 | Same test, the timed05 precondition: replace the `SE_FIELD` assert with a read-back. `text, whys = cp._log_text(tmp_path / "logs")`; `assert whys == []`; `own_i2 = [m for m in (cp.LOG_LINE.match(l) for l in text.splitlines()) if m and m[3] == "I2" and m[4] == RH_ID]`; `assert len(own_i2) == 1`; `f = own_i2[0][5]`; `assert cp.log_fields_ok("I2", RH_ID, f, timed=False) and not cp.log_fields_ok("I2", RH_ID, f)`. Also assert `f == untimed`, either by returning it from setup or by recomputing it the same way. Delete `SE_FIELD` and its comment | fixture logs | assertion | grep `SE_FIELD` in tests/ gives 0 hits. Leaving ` in 0.01s` in the log (a one-off probe, recorded in 05) makes the precondition fail by name | 1 of 1 I2 line read back (Self-check 3). Empty-log case: `len(own_i2) == 1` fails by name, never a vacuous `all()` |
| 3 | Pin Done (a) with a permanent case `timed05alt` (step "05", setup `_se_timed05`, entry `I2_ENTRY`) in `SE_CASES`, giving ids `timed05alt-shallow` and `timed05alt-nogit`. The test takes `monkeypatch`. When `case == "timed05alt"`, it calls `monkeypatch.setitem(FIELDS, "I2", "2 files changed \| tests 3 passed in 0.02s")` before `setup(...)`. The precondition from step 2 runs for every case starting with `timed05`. The shared constant is never edited | FIELDS (patched for that test only) | 2 new ids | `-k shallow_elif_branch` → `16 passed`; full suite = base + 2 passed (I2 pastes both lines) | Alt field: 1 of 1 I2 line edited; its untimed form fullmatches LOG_FORMAT["I2"] and fails I2_TIMED (Self-check 4) |
| 4 | Mutants (I2 in 05, re-run by I3 in 06), one at a time on a scratch copy of scripts/check_pipeline.py, restored after each and compared with `cmp`. M-timed: `elif unsure("05"):` → `elif False:` at the TIMED gate (L1073 today; find it by the `# item 095: anchor not read` comment under `# item 090: TIMED gate`). K-timed: `unsure("05")` → `unsure("06")` at the same line | scratch copy | failing ids per mutant | Expected for each: exactly `timed05-shallow` and `timed05alt-shallow` fail, all other 14 ids pass (`2 failed, 14 passed`). Any other result is pasted and explained | 2 mutants, 2 expected failing ids each (Self-check 5) |
| 5 | Style: put 2 blank lines (PEP 8 top-level) before `# Item 101` (today 3, L5328-5330) and before `def test_round_build_missing_inputs` (today 1, L5412) | – | whitespace only | `git diff` shows only blank-line changes there | – |
| 6 | No change outside tests/test_pipeline_check.py (and work/108, logs) | branch base and head | empty diff | `git diff --stat <base> HEAD -- scripts/ templates/ .claude/ config/ ccbot/` is empty. The checker is unchanged, so full-clone `check_pipeline.py` output is unchanged except 108's own item lines | – |

Recurring issues (item 013):
- RI-001 (ESCALATED): there is no ticker, DTE or delta filter in this item. The only "rule" is the fixture precondition. Its count is computed: 1 I2 line out of 6 for item 150, and the strip removes 1 match from each of the 2 fields used (Self-check 1, 3, 4). I2's runs (14 passed, then 16 passed) are the measurement. No "always" claim is made.
- RI-014 (OPEN): parent issue. 108 changes only its test, and the shallow TIMED branch stays pinned by 2 mutants (step 4). Status unchanged.
- RI-002: `len(own_i2) == 1`, `whys == []`, `untimed != timed` and `" | tests " in timed` keep an empty or unchanged value from passing silently.
- RI-004/005: the worked values below are re-derived against the regexes they must match or fail.
- RI-006: the totals are counted by check_handoff (orchestrator), not by hand.
- RI-012: no text classification is added. The read-back uses the checker's own anchored `LOG_LINE` and `fullmatch`.

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Fixture log `logs/implementation/2026-11-21.md` (step 2, `_log_text`) | file absent or unreadable | `assert whys == []` fails with the why. An absent file gives `own_i2 == []`, so `assert len(own_i2) == 1` fails by name. Never a vacuous pass |
| The I2 line for 150 (step 2) | 0 or more than 1 lines | `assert len(own_i2) == 1` fails, showing the count |
| ` in <s>s` time in `FIELDS["I2"]` (step 1) | field has no time | `assert untimed != timed` fails (re.sub no-op, R1 F18) |
| ` \| tests ` separator in `FIELDS["I2"]` (step 1 Suite edit) | not present | `assert " \| tests " in timed` fails before the split |
| Edit target text (log line, 05 `Suite:`) (step 1) | not in file | `_se_edit`'s `assert old in text` fails, showing path and text |
| Screen tickers (`ccbot/screen.TESTS`, `MISSING_POLICY`) | n/a | No tickers are screened. This is a test-only change in the pipeline checker |

## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| 1. Strip on today's field | `re.sub(r" in \d+\.\d+(?:s\| seconds)", "", "1 files changed \| tests 1 passed in 0.01s", count=1)` | the match is ` in 0.01s` (9 chars), so 41 → 32 chars: `1 files changed \| tests 1 passed`. This equals the old `SE_FIELD` and the old L5351 replacement, and differs from timed | pass |
| 2. Suite edit from today's field | `"Suite: " + x.split(" \| tests ", 1)[1]` | timed → `Suite: 1 passed in 0.01s`, untimed → `Suite: 1 passed`, the same as the old L5352 literals. The 082 check (L1112-1113) compares untimed `1 passed` with Suite `1 passed`: equal, so no Suite entry | pass |
| 3. Precondition on the read-back (ID 150 ≥ TIMED_FROM 90) | `fullmatch(LOG_FORMAT["I2"], f) and not fullmatch(I2_TIMED, f)` | `1 files changed` matches `\d+ files? changed`; `1 passed` matches _STATS (`(?=[1-9])`, `_END` at `$`); _TAIL is optional, so LOG_FORMAT is True. I2_TIMED needs ` in \d+\.\d+` after the stats and none is there, so it is False. True and not False = True | pass |
| 4. Alt field (step 3) | rows 1-3 on `2 files changed \| tests 3 passed in 0.02s` | untimed `2 files changed \| tests 3 passed` (≠ timed); LOG_FORMAT True, I2_TIMED False; Suite `3 passed in 0.02s` → `3 passed` equals the untimed tests part. The log is edited only at the I2 line (the I1/I3 fields do not contain that text) | pass |
| 5. Mutant expectation | ids failing = shallow ids of the cases that reach L1073 | M-timed: shallow wants `got == []`, but with `elif False` the entry is not removed, so got = [I2_ENTRY]. That fails for timed05 and timed05alt (2 ids); nogit already takes the strict path (passes). K-timed: committed holds only 05, so `unsure("06")` is False and the result is the same as M (2 ids). Total ids after step 3: 7 + 1 cases × 2 modes = 16, so expect `2 failed, 14 passed` | pass |
| 6. Test-id counts | 7 cases × 2 modes; then 8 × 2 | 14 (as in 101) → 16 after step 3 | pass |
| 7. Fixture lines | AGENTS keys 01-06 over ALL 01-07 | 7 files, 6 with an agent → 6 lines, 1 I2 → `len(own_i2) == 1` | pass |

`check_handoff output (run by the orchestrator 2026-11-25 23:31 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 32
totals line: 32 rows -> 30 as-is, 2 fixed, 0 removed
PASS
```
