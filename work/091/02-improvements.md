# 02 Improvements - 091
## What past logs say
- logs/audit/2026-11-21-081.md F1 (via 01 findings 1.3, 1.8, 1.11): A1-A3, A8, A9 and A13 survive because each guarded term or path group has no fixture where it is the only thing that changes the result. 088 has the same pattern (logs/audit/2026-11-21-084.md finding 1, work/088/02 FOR 1-2): "only some unknown paths are held strict". The fix that worked there was one fixture per branch, with the git behaviour pinned inside the test.
- RI-014 (logs/recurring-issues.md L152-158) is OPEN. Its 2026-11-21 status already names 090 for depth-1 LOG TIME / MAIN AHEAD / unrelated-branch and 089 for non-UTF-8 reads. 091's sub-asks 1 and 5 sit in the same code (open_branches, main's exit terms, the unshallow sentence).
- RI-010 (L118-131) is ESCALATED. Its root cause is "step duties exist only in the agent text; ... no script checks them". Sub-asks 2(a), 3 (rule sentence) and 4 are new duties of that kind, so each one needs a check, not just a sentence (AGAINST 3).
- RI-007 (L84-99): 091 links sub-ask 4 to it. The evidence is work/081/06 round 1 L7: the scratch dir was overwritten by another agent, and I3 re-ran every mutation in a uniquely named dir. The caller for this run already gives each agent its own dir (/tmp/claude-0/scratch/r1-091/, /tmp/claude-0/scratch/r2-091/), so the convention works when someone hands out the dir.
- Parallel work today: 088, 089, 090 and 091 are open on the same branch and checkout (logs/research/2026-11-21.md L3-7 interleave R1/R2 lines for 088-091). 089 adds a shared reader plus a read census over every `read_text` in check_pipeline.py (work/089/01 F17, F31; `_run_seconds` L914 is one of its sites). 090 changes rule C/D in `batch_log_items` and the not-checked lines for shallow clones (work/090/request.md L7, L13). 088 changes `_rule_seen` / `_anchor_env` and the census (work/088/02 FOR 3).
- Neither R1 nor this R2 has a shell. Code facts below come from reading the files on daily-fixes/2026-11-21 (scripts/check_pipeline.py L905-1004; tests/test_pipeline_check.py L229-248, L1600-1603, L2432, L3228-3264, L3456-3464; .claude/commands/run-item.md L12, L15-19). Nothing was run.

## 3 ways FOR
1. **Sub-asks 1 and 5: kill the six mutants and M11 with tests only, and use fewer subprocess runs than R1's plan.**
   - (1a) Instead of 7 parametrised R2-c cases (each builds `_repo_with_open_branch` and runs the CLI in a subprocess, L3255-3257), build one repo with one orphan per pathspec entry, using `_orphan(repo, name, {path: text})`: `w` → `work/150/request.md`, `ri` → `logs/recurring-issues.md`, `cl` → `.claude/agents/x.md`, `tp` → `templates/x.md`, `cb` → `ccbot/x.py`, `cf` → `config/x.json`, `ts` → `tests/test_x.py`. Make one CLI run and assert all 7 exact `BRANCH ERROR: origin/<name> (... 1 file(s) on checked paths (first: <path>) not checked (item 081))` lines plus exit 1.
   - Why one run is enough: the error is per ref, so each orphan's line depends only on its own file's group. Dropping RECURRING, RULE_PATHS or RESEARCH_CODE_PATHS (A1-A3), or any single entry such as `"templates/"`, removes exactly the matching line(s). This is reasoned from L1063-1068 and not run, so it is UNVERIFIED until I3 mutates.
   - Keep R1's 1.5 rule: no sample file under `scripts/`, because `scripts/check_pipeline.py` matches both RULE_PATHS and `scripts/`. Keep the existing R2-c test as it is, since it carries the `--next-id == 151` assert.
   - Add a direct pin of the undocumented git behaviour (01 finding 1.13, open question 6): `subprocess.run(["git","merge-base","--all","HEAD","origin/w"], cwd=repo).returncode == 1`. If a git upgrade changes that exit code, the test then names the cause instead of failing on a changed BRANCH ERROR string. This is the same pattern 088 used (work/088/02 FOR 1).
   - (1b) A8 / A9 / A13 as R1 designed them (01 findings 1.9-1.12). Each test patches exactly one call with `_patched_git` (L1600-1603) on `_repo_with_open_branch`, with an unpatched control at exit 0 (A8/A9) or `041` (A13). The A13 ref is `origin/fix`; the fixture pushes branch `fix` (L241-246). In-process calls need `monkeypatch.chdir(repo)`, as R2-b does at L3243. Otherwise `_git` reads as "no git" and the test passes for the wrong reason (work/088/02 Holes).
   - (5) Add R1's two M11 fixtures, trailing ` x` and trailing `\n`, to tests/test_probe_guardrails.py (01 finding 5.4).
   - None of this adds a `_git(` call to the script, so the census stays 47 (L2432) for these parts.
2. **Sub-ask 3: one helper that builds the whole step commit in a private index, instead of a prose rule plus a staging helper.**
   - The problem with R1's design: it stages the filtered log blob into the shared index (01 finding 3.5) and then needs a plain `git commit` (01 finding 3.3). But a plain `git commit` records the whole shared index, so it also carries anything another parallel agent has staged in the same checkout.
   - The `--only`/pathspec form does not help either. It takes "the updated working tree contents of the paths specified ... disregarding any contents that have been staged for other paths" [https://git-scm.com/docs/git-commit], so it would re-read the unfiltered log file from disk.
   - Better: `check_pipeline.py --commit-step <ID> <subject> <path>...` does the following:
     - (i) sets `GIT_INDEX_FILE` to a temp file and runs `read-tree HEAD`;
     - (ii) runs `update-index --add` for each named path, plus the filtered blob from R1's 3.6 rule for the day's log file(s), via `hash-object -w --stdin --path` and `update-index --cacheinfo`;
     - (iii) runs `write-tree`, then `commit-tree -p HEAD -m <subject>`;
     - (iv) runs `git update-ref HEAD <new> <old>`, which "updates ... only if its current value is <old-oid>" [https://git-scm.com/docs/git-update-ref], so a commit that raced in from another agent makes it refuse (exit 2) rather than drop that commit;
     - (v) runs `git reset -q -- <paths>` so that the shared index matches the new HEAD for those paths only.
   - The shared index is never written except by (v), so nothing another agent staged goes into this commit.
   - The subject comes from item 082's rule ("Item <ID>: " + the `--log` line, run-item.md L17), so the helper can also refuse a subject that is not the line `--log` just printed. That turns an RI-010 prose rule into a check.
   - That `GIT_INDEX_FILE` redirects plumbing commands to another index is UNVERIFIED here: the official git(1) environment section could not be fetched. I2 must pin it in the fixture.
   - Fixture, extending R1's 3.9 (two uncommitted log lines for 150 and 151): also `git add` an unrelated file `x.txt` before calling `--commit-step 150`. Assert that `git show --stat HEAD` lists only 150's paths, that `git diff --cached --name-only` still lists `x.txt`, and that 151's line is still unstaged.
   - Mutations:
     - shared index used: `x.txt` gets committed, so the test fails;
     - whole log file staged: 151's line is in HEAD;
     - `update-ref` without `<old>`: a pre-moved HEAD fixture loses a commit.
3. **Split the overlap with 090/089 by ownership, and do the cheap text parts in their checkable form.**
   - Sub-ask 2: 091 does option (a) only, the template line (01 finding 2.6), in templates/build-report.md and templates/verification.md, with a text pin. Option (b), reading `###` round headings level-aware (01 finding 2.7), goes to 090 or a follow-up item opened after 090 merges. 090 already owns `batch_log_items` / rule C (work/090/request.md L13), and 089 rewrites the read at L914 through its shared reader. A third parallel edit of L905-1004 would conflict twice.
   - Make (a) checkable in a way that does not change current LOG BATCH results. 091 adds an INCOMPLETE reason (from a cutoff ≥ 092, so no current item changes) for a 05/06 that has a `### Test output` / `### Tests re-run` heading outside any read section. That is the exact shape counted in 01 finding 2.3 (9 headings in 7 items, all below 092). The rule is then enforced, not only written.
   - Unshallow sentence: 090 owns it. 090 must already edit `UNSHALLOW` and its three copies for LOG TIME / MAIN AHEAD / unrelated-branch (01 finding 5.8), so it adds `RULE NOT SEEN` (item 084) in the same edit, and the byte-for-byte test (L3461-3464) covers all forms at once. 091's 05 names this hand-off, and 091's I3 checks that 090's 03 includes RULE NOT SEEN. If 090 is dropped, the sentence edit comes back to 091.
   - Sub-ask 4: put the `tempfile.mkdtemp(prefix="<agent>-<ID>-r<round>-", dir=<scratchpad>)` rule (01 finding 4.6) in run-item.md and in the i2/i3/a1 "scratch copy" lines. Name the orchestrator as the one who makes the dir for shell-less agents (R1-R3, I1). This run's caller already does that.

## 3 ways AGAINST
1. **Sub-ask 3 fixes log lines, but parallel items in one checkout also share code files, and staging by file cannot split those.**
   - 088, 089, 090 and 091 all edit scripts/check_pipeline.py and tests/test_pipeline_check.py on one branch and one working tree (What past logs say). When one item's I2 commits check_pipeline.py with its 05 (run-item.md L19), the commit carries whatever hunks the other items have on disk in that file. Neither R1's helper nor FOR 2 can separate hunks inside one code file without a patch, and `git add -p` is interactive only (01 finding 3.4).
   - So a log-only helper could give false confidence: the 91ade51 failure mode (one item's commit carries another's work) stays open for code. This is reasoning from the shared checkout, with no run (UNVERIFIED by probe).
   - Linked worktrees fix the index side: each one shares the repo "sharing everything except per-worktree files such as `HEAD`, `index`" [https://git-scm.com/docs/git-worktree]. But git refuses to check out a branch already checked out in another worktree unless `--force` is used [same page]. Separate branches per item would then append to the same daily log file, which risks a merge conflict at the end of the file (reasoned, UNVERIFIED).
   - Mitigation: add a run-item sentence that items which change the same file are built (I2-I3) one after another, never in parallel, and keep FOR 2's helper for the shared log files. State in 05 that the helper does not make parallel code builds safe.
2. **Reading `###` round headings (sub-ask 2 option b) inside 091 changes past results without measurement, and collides with two parallel items.**
   - New t05 values can raise max(t05). A value equal to a t06 value also drops that t06 value as a copy (L994). So past items' LOG BATCH results can change in both directions (01 finding 2.8). Only 086's window has been computed. The other 6 items in 01 finding 2.3 have not (UNVERIFIED).
   - A new flag on a merged item turns main's check red: the 048/049 history in RI-010 (L119) shows how costly that is.
   - The same lines are being rewritten by 089 (L914 read) and 090 (rule C), so a third branch on L905-1004 means at least one rebase with census changes on top (088's ±1, 089's read census).
   - Mitigation: FOR 3, option (a) only in 091. Option (b) goes to 090 or a later item that pastes a measured before/after LOG BATCH line over the real tree (I2 step 0).
3. **The bundle adds more prose-only duties to an ESCALATED root cause and raises the cost of one send-back.**
   - Sub-asks 2(a), 3 and 4 as R1 wrote them are sentences in run-item.md and the templates, pinned by a "sentence exists" text test (01 findings 2.6, 4.6). RI-010's root cause is exactly that kind of duty with nothing to check whether it was done (logs/recurring-issues.md L120). A text pin proves the sentence is present, not that an agent followed it. The mkdtemp rule in particular cannot be checked after the fact (01 finding 4.6: names in 05/06 check text, not collisions).
   - The five sub-asks also share one I3 verdict. A FAIL on the hardest part (sub-ask 3: new git plumbing, census +3 or more, a RULE_PATH change so RULES BRANCH shows) sends back the easy, finished parts too, under the 3-loop cap (run-item.md L15).
   - Mitigations:
     - give each prose duty a check where one is possible: FOR 2 (the helper refuses a wrong subject), FOR 3 (an INCOMPLETE reason for stray `###` run headings);
     - say plainly in 05 that sub-ask 4 is text-only, with the reason;
     - order the build so that tests-only parts (1, 5) are committed first. If sub-ask 3 fails twice, R3/I1 may split it into its own item rather than hold 1, 2(a), 4 and 5.

## Findings by language
Random languages this cycle: N/A
Languages: N/A (no new external claims). 091 is an EFFICIENCY item inside this repo's pipeline checker and agent rules: test fixtures, a template line, a staging/commit helper and a scratch-dir rule. It adds or changes no fee, market rule, statistic or trading behaviour. The only outside facts are git and Python tool behaviours, cited to their official docs (git-commit, git-update-ref, git-worktree, Python re/tempfile) and pinned by in-test asserts. This matches the precedent of 081-088 (all logged `languages: N/A`).

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
- Sub-ask 1:
  - No orphan sample under `scripts/`: it matches RULE_PATHS and RESEARCH_CODE_PATHS at once, so A2 survives.
  - Assert each exact BRANCH ERROR line, not only exit 1. The unrelated-branch lines are per ref, so the exit code alone cannot tell which group was dropped.
  - Pin `merge-base --all` exit 1 directly. It is undocumented (01 finding 1.13).
- A8 test: call `main` without `--next-id`, because `next_id` makes the same `branch -r` call (01 finding 1.10). Every in-process test needs `monkeypatch.chdir(repo)`, or `_git` reads as "no git".
- A13: patch exactly `("ls-tree","-d","--name-only","origin/fix","--","work/")`. Assert exit 2, empty stdout, and the refusal text on stderr.
- M11: add the trailing-newline case as well as ` x`, because a `$`-anchored `match` would pass the first but not the second (01 finding 5.4). Keep `fullmatch` and do not use `prefixmatch` (Python ≥ 3.10, RI-008).
- Sub-ask 3:
  - A plain `git commit` records the whole shared index, and a pathspec commit re-reads the unfiltered file from disk [https://git-scm.com/docs/git-commit]. Neither is safe alone. Use a private index plus `update-ref HEAD <new> <old>` [https://git-scm.com/docs/git-update-ref].
  - Refuse (exit 2, nothing written) if HEAD's log lines are not an in-order subsequence of the working file, or if the file is unreadable. Read it through 089's shared reader once that lands.
  - Count every new `_git(` call in GIT_CENSUS, after re-reading the total, since 088/089 may have moved it from 47.
  - The helper does not make parallel builds of the same code file safe (AGAINST 1). Say so in 05 and in run-item.md.
- Sub-ask 2:
  - (a) only in 091, plus the stray-`###` INCOMPLETE reason from cutoff 092. (b) goes to 090 or later, with a measured before/after LOG BATCH line.
  - Do not end sections at `#{1,3} `: that cuts the `###` subsections inside today's `## Test output` sections (01 finding 2.7).
- Unshallow sentence: one owner (090) for one edit of `UNSHALLOW` and its 3 copies, adding RULE NOT SEEN (item 084). If 090 is dropped, 091 takes it back. Whether INBOX belongs in the sentence is still open (01 open question 5). Recommendation: leave it out, because INBOX's not-checked line has `failed=False` and does not gate the exit (01 finding 5.7).
- Sub-ask 4: `mkdtemp` returns a fresh absolute dir that its user must delete [https://docs.python.org/3/library/tempfile.html]. Shell-less agents get their dir from the orchestrator. Never reuse another agent's dir, even within the same item.
- Build order: commit tests-only parts (1, 5) first, then 2(a) and 4, then 3. Rebase on whichever of 088/089/090 merges first, and re-read line numbers and the census total before writing fixtures.

Log fields: 3 for / 3 against | languages: N/A
