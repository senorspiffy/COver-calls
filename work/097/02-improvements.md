# 02 Improvements - 097
## What past logs say
- RI-009 (logs/recurring-issues.md L108-116) is GUARDED. Its 2026-11-22 note logs this as a near miss that was not counted: "orchestrator scratch paths outside 091's mkdtemp rule; `git stash` in a scratch worktree shows in the main checkout -> 097". Its second occurrence (032/06, L115) is the harm this item guards against: an in-repo `git checkout` restore wiped another item's uncommitted edit. 01 C4 shows that `git stash push -- <file>` in the main checkout does the same thing.
- RI-010 (L118-130) is ESCALATED. Its root cause is "step duties exist only in the agent text; ... no script checks them". A new no-stash sentence and an orchestrator scratch duty are exactly that kind of duty. 091's own R2 said the same about the scratch rule (work/091/02 AGAINST 3: "The mkdtemp rule in particular cannot be checked after the fact"). That is why FOR 2 and AGAINST 2 below look for a real check.
- RI-014 (L152-158) and item 081: a failed git read must print "not checked", never "none". `_git_ok` (scripts/check_pipeline.py L1401-1411, 01 A6) is the reader to use.
- logs/audit/2026-11-22-091.md N3/N4 (01 B1, B4): the agents followed the rule and the orchestrator did not. A1's ruling was "the orchestrator changes, the rule stays".
- work/091/05 is not fully consistent on who made the paths. L534 reads "Scratch dir made with `mktemp -d /tmp/claude-0/scratch/i2-091r2-XXXX`" (I2 wrote it as if it made the dir itself). The audit (01 B1) says the orchestrator handed it out. Either way the path is outside the scratchpad and not in the rule's form. The same line reads "No `git stash` used." and "`git stash list | wc -l` gives 0". That matters for AGAINST 2's hole (a text grep for `git stash` would match a denial).
- Pinned text: `SCRATCH` constant plus `test_scratch_sentence_same_in_four_files` (tests/test_pipeline_check.py L4618-4628, read 2026-11-24). Grep for `stash` in .claude/, scripts/*.py and tests/*.py: no match (re-checked 2026-11-24).
- This run: the caller gave this R2 the dir `.../scratchpad/r2-097-r1-m3xi6a7n`, and gave R1 `.../r1-097-r1-m86381po` (01 B5). Both have the mkdtemp shape (FOR 2), so the orchestrator already follows option (i) of 01 open question 1. Whether `mkdtemp` actually made them is UNVERIFIED. This R2 has no shell and wrote nothing there.
- Neither R1 nor this R2 has a shell. Nothing was run.

## 3 ways FOR
1. **Settle open question 1 (orchestrator naming paths) with one rewritten SCRATCH sentence that binds the orchestrator by name, and fold the no-stash and `--detach` rules into the same pinned sentence.**
   - Proposed SCRATCH text, the same in all 4 files (run-item.md, i2, i3, a1), with the constant changed in the same commit (01 A2):
     > Every agent works in its own new scratch dir and never reuses or writes into another agent's dir, even for the same item. Agents with a shell (I2, I3, A1) make their own with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="<agent>-<ID>-r<round>-", dir="<absolute scratchpad path>"))'` and put any worktree inside it with `git worktree add --detach`. The orchestrator names no scratch path to them. For an agent with no shell (R1-R3, I1), the orchestrator runs that same command and passes on the path it printed, never a path it typed, a fixed path or `mktemp -d`. No one runs `git stash` in any checkout: refs/stash is shared by every worktree of the repo. Restore a probe file with `git checkout HEAD -- <file>` or from a copy (items 091, 097).
   - Why option (i) rather than (ii) "shell-less agents get no dir":
     - (i) matches what the caller does in this run (What past logs say).
     - (i) matches A1 N3's text (01 B4) and the "rule stays" ruling.
     - (i) keeps a place for shell-less agents that use Write for tool input.
   - R3 must record that this narrows the request's literal "orchestrator never names a scratch path" to "never one it did not get from the mkdtemp command". Only R3/the person can approve that wording change (01 open question 1).
   - Why one sentence and not two: one constant and one test keep the 4 files in step. A second no-stash sentence for only i2/i3/a1 would leave run-item.md (the orchestrator) unbound, and the request says "every agent and the orchestrator" (01 Numbers: 3 vs 4 files).
   - Why "any checkout" and not just "a scratch worktree" (01 open question 4): C4 shows that stash in the main checkout reverts other items' uncommitted edits, which is the RI-009 032/06 failure. C5 shows that drop or clear of the wrong entry cannot be undone.
   - Why `HEAD` in the restore (01 D2): plain `git checkout -- <file>` restores from the index, so a mutant that was `git add`ed would survive. 01 D1 shows that the path form moves no ref.
   - Why `--detach` (01 C8): without it, `git worktree add <path>` makes a shared branch named after the dir's basename. That is the same shared-`refs/` root cause, and it costs nothing to add here.
2. **Turn the orchestrator half into a check, not just text (RI-010): a shape check on the scratch paths named in 05/06.**
   - mkdtemp names are `prefix + 8 characters` from `abcdefghijklmnopqrstuvwxyz0123456789_` ([https://raw.githubusercontent.com/python/cpython/main/Lib/tempfile.py]: `_RandomNameSequence.characters = "abcdefghijklmnopqrstuvwxyz0123456789_"` and `k=8`, "Each string is eight characters long"). That is CPython main. That 3.10/3.11 use the same is UNVERIFIED, and I2 must pin it in the test with a real `tempfile.mkdtemp` call.
   - So a path that I2/I3/A1 name as their scratch dir in 05/06 must have, as its first segment below the scratchpad root, a segment matching `^(r1|r2|r3|i1|i2|i3|a1)-<ID>-r\d+-[a-z0-9_]{8}$`.
   - Checked against 01 B1, all 5 of 091's out-of-rule paths fail it:
     - `/tmp/claude-0/scratch/...` is not under the scratchpad;
     - `i3-091r2-UxQ8` and `i2-091r2-LpYi` have no `-r<round>-` part, contain uppercase, and have 4 characters;
     - `i3-091/wt`, `i2-091/` and `i2-091b/` have no suffix.
   - The agents' real dirs pass: `i3-091-r1-dpe6hf15`, `i3-091-r2-mz28r6tf`, `a1-091-r1-46dt4kc_` (underscore allowed).
   - Output: a `SCRATCH PATH:` line in check_pipeline (or an INCOMPLETE reason), only for items from 097 on, so that no past item turns red (the 048/049 lesson in RI-010 L119).
   - This is the only part of the scratch rule that can be checked after the fact, because caller messages are not logged.
   - How I2 finds "a path named as scratch" (a `Scratch dir:` field in templates/build-report.md and verification.md is the simple anchor) is a design choice for R3/I1. A free-text scan risks false positives (AGAINST 2 hole).
3. **Make the stash check exact by reading `git stash list` through `_git_ok`, which settles open question 3.**
   - git's source shows that `git stash list` returns 0 and prints nothing when no stash exists: in `list_stash`, `if (!refs_ref_exists(get_main_ref_store(the_repository), ref_stash)) return 0;`. Otherwise it returns the exit status of `git log --format=%gd: %gs -g --first-parent ... refs/stash --` [https://raw.githubusercontent.com/git/git/master/builtin/stash.c]. That is git master. That the installed git behaves the same is UNVERIFIED, and I2 pins it in the fixture with the exit code and output asserted directly (the 088/091 pattern).
   - That gives three cases, classified by exit code (RI-012), with stdout read only when exit is 0:
     - exit 0 and empty: `STASH: none`;
     - exit 0 and n lines: `STASH: n entries (first: stash@{0}: ...)`;
     - non-zero: `STASH: not checked (git stash list failed (exit n))`, never "none" (RI-014).
   - `rev-parse --verify -q` cannot tell "none" from "failed" (01 C7), so it is the worse choice.
   - Where it goes: check_pipeline main, which the orchestrator already runs at the end of every item (01 A5). run-item.md L15's end list gets "and `STASH:` must be `none`" next to LOG TIME / LOG BATCH.
   - Fixtures for "Done looks like":
     - (a) a repo with one stash entry: the line names it and the exit is 1;
     - (b) the same repo after `git stash drop`: `STASH: none`;
     - (c) `_git` patched to fail: `not checked`.
   - Mutations: drop the exit term (a must fail), and map a non-zero exit to none (c must fail).
   - This adds 1 `_git(` call, so the census test moves by +1 (as in 088/091).

## 3 ways AGAINST
1. **An exit-1 stash check can fail every run for a stash that is not the pipeline's, and it can falsely say "none" in another clone.**
   - refs/stash is a local ref and is never pushed. git stash is described as recording "the current state of the working directory and the index" in the local repository [https://git-scm.com/docs/git-stash]. A1 working in its own fresh clone therefore always sees `STASH: none`, whatever the orchestrator's checkout holds (reasoned from that and 01 C1. UNVERIFIED by probe).
   - In the other direction, a stash the person keeps on purpose in this checkout would turn every item's end check red. Whether the person keeps any is UNVERIFIED (01 open question 2). 091/06 L38 counted 0 afterwards.
   - Mitigations:
     - run-item.md says that only the person clears or drops a stash entry, and that an agent never drops an entry it did not make (01 C5);
     - the STASH line text says "local to this checkout";
     - A1 reports the orchestrator's checkout's STASH line, not its own clone's;
     - if the person wants their stashes kept, R3 can make the line print-only, with the exit-1 term for items from 097 on gated on new entries (a count at "Before starting" vs end). That gating is prose unless it is stored, so prefer exit 1 and let the person decide.
2. **The end-of-run stash check would not have caught the 091 incident, so it should not be sold as the guardrail for it.**
   - I2 (091) made 3 entries and dropped all 3 before its step ended. `git stash list` was empty again (work/091/05 L762, L534). A leftover-only check at the end of run passes that run.
   - The real harm happens at the moment of the `stash push`: in the main checkout it reverts other items' uncommitted edits (01 C4), and a wrong `drop` cannot be undone (01 C5). An end check cannot see either.
   - A text grep of 05/06 for `git stash` is no fix either. 091/05 L534 says "No `git stash` used." and L762 reports the incident honestly, so a grep matches both a denial and an admission.
   - Mitigations:
     - state in 05 and in the RI-009 status (via A1 on main) that the STASH line catches only entries left behind, and that the no-stash rule itself is text-only with the reason;
     - keep the restore method in the rule (FOR 1) so agents have a safe alternative;
     - whether git leaves any trace of a dropped stash that a check could read (for example, a HEAD reflog entry from the stash's reset) is UNVERIFIED. I2 may measure it on the fixture, but must not build on it unmeasured.
3. **Rule-file and shared-test churn while parallel items run in this checkout.**
   - The change edits run-item.md and three .claude/agents files, all in RULE_PATHS (scripts/check_pipeline.py L463: `".claude/"`). So the branch shows as a `RULES BRANCH:` that every parallel item must build on (run-item.md L12, item 049).
   - It also changes the shared tests/test_pipeline_check.py (SCRATCH constant, new fixtures, census +1) and check_pipeline.py. Under run-item.md L17 (item 091), items that change the same file are built one after another, never in parallel. RI-014's 2026-11-24 status says 092, 094 and 095 also run today, and at least 094/095 touch check_pipeline.py's git reads (RI-014 L153).
   - FOR 1 widens scope with `--detach` and "any checkout", and FOR 2 adds a new check plus template field. Each widens I3's surface under the 3-loop cap (run-item.md L15), the same risk 091's R2 flagged (work/091/02 AGAINST 3).
   - Mitigations:
     - build 097's I2-I3 only after any parallel item that touches check_pipeline.py or test_pipeline_check.py has finished its I3, and rebase before writing the census number;
     - order the commits: text plus pin first, then STASH plus fixtures, then the FOR 2 shape check;
     - if FOR 2 fails I3 twice, R3/I1 may split it into its own item.

## Findings by language
Random languages this cycle: N/A
Languages: N/A (no new external claims). 097 is a BUG item about this repo's own process: agent rule text, one check_pipeline line and test fixtures. It adds or changes no fee, market rule, statistic or trading behaviour. The only outside facts are git and Python tool behaviours, cited to their official docs and source (git-worktree, git-stash, git-checkout, git builtin/stash.c, CPython tempfile.py) and pinned by in-test asserts. This follows the precedent of 081-091 (all logged `languages: N/A`).

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | N/A (see above) | | | |
| Mandarin Chinese | N/A | | | |
| Spanish | N/A | | | |
| Japanese | N/A | | | |
| N/A | N/A | | | |
| N/A | N/A | | | |
| N/A | N/A | | | |

## Holes to watch out for (summary)
- Request vs N3 wording: "orchestrator never names a scratch path" against "orchestrator gives one to R1-R3/I1 via mkdtemp". FOR 1 picks the second. R3 must flag it as a narrowing, and only R3 or the person can approve it.
- `git checkout -- <file>` (N4's text) restores from the index, so a staged mutant survives. Use `git checkout HEAD -- <file>` (01 D2).
- `git worktree add <path>` without `--detach` creates a shared branch named after the dir (01 C8).
- `git stash list` empty-case behaviour is from git master source. Pin exit 0 and empty stdout on the installed git in the fixture. Read stdout only when exit is 0, and a non-zero exit gives "not checked", never "none" (RI-012, RI-014).
- refs/stash is per local repo. A1 in a separate clone gets a false "none", so report the orchestrator checkout's line.
- The STASH line catches only leftovers. 091's incident (3 made, 3 dropped) would have passed it, so do not claim it as the guardrail for that incident.
- A text grep for `git stash` in 05/06 matches denials ("No `git stash` used.", 091/05 L534).
- mkdtemp suffix shape (8 characters of `[a-z0-9_]`) is from CPython main. Pin it with a real mkdtemp call, and apply the shape check only to items from 097 on.
- SCRATCH is pinned byte-for-byte in 4 files. Change the constant in the same commit, or the test fails (01 A2).
- RULES BRANCH ripple and shared test file: build after the parallel items that touch check_pipeline.py or test_pipeline_check.py, and recount the census after rebasing.

Log fields: 3 for / 3 against | languages: N/A
