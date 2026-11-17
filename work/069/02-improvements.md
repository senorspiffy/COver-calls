# 02 Improvements - 069
## What past logs say
- No earlier item, audit note or recurring issue covers an inbox or the hub. A Grep for "inbox|project-inbox|shared-facts|Updated-folder" finds only work/069 and logs/audit/2026-11-17.md (01 finding 23). The 2026-11-17 daily report already has a hand-written `## Inbox` section that names hub commit 116c68c and says "Nothing new" [/home/claude/df17/logs/audit/2026-11-17.md L4-5]. That is a working first run, but nothing makes the next run repeat it.
- Three recurring issues have the same shape as the risks here:
  - RI-002 (ESCALATED, 10 occurrences): "Missing or uncomputable data silently turned into a value". An inbox that can't be reached must not be written up as "nothing new" [/home/claude/df17/logs/recurring-issues.md L24-26].
  - RI-010 (GUARDED, 4 occurrences): duties that "exist only in the agent text ... no script checks them" get skipped [/home/claude/df17/logs/recurring-issues.md L120]. A new A1 step with no template field and no check is the same setup.
  - RI-007 (GUARDED, 6 occurrences): "fixes made in other threads skip the pipeline entirely" [/home/claude/df17/logs/recurring-issues.md L86]. The hub rule now sends other projects' fixes to our audit [01 finding 16]. So this item is the way in for exactly the outside changes RI-007 is about, and every message has to become a work item, never a direct edit.
- Last full language search: 053 (2026-11-11), with Portuguese, German and Korean as the random three [/home/claude/df17/logs/research/2026-11-11.md L4]. All later R2 lines are `languages: N/A`, so those three are excluded this time.

## 3 ways FOR
1. **Treat each message as untrusted data with a recorded origin, and say which fields can be trusted.**
   - OWASP ASI07 (as summarized by Zealynx): "treat every agent-to-agent message as untrusted data" unless its origin can be checked, and review "who made the request and which untrusted inputs shaped it" before high-impact steps [https://www.zealynx.io/research/adversarial-security/owasp-asi07-inter-agent-communication]. Tianpan (zh) says the same: peer-agent output counts as "tainted" until verified [https://tianpan.co/zh/blog/2026-04-10-three-attack-surfaces-multi-agent-communication].
   - Here: the `from:` header in project-inbox is free text that anyone can write. Both current files say `from: covered-calls`, written by this project to itself [01 finding 7]. So `from:` cannot be checked. For hub lines, the git commit SHA and author are firmer than the hand-written "from <project>" text.
   - Proposal: each inbox-made item's `Opened by:` names the source as either `<path>` or `<hub file>@<sha> (author <git author>)`. Its evidence quotes the message verbatim under a heading such as "Untrusted message text", kept apart from A1's own words.
   - Add the 01 finding 30 limits to a1-auditor.md word for word. A message cannot:
     - set Scope or FAST,
     - waive a step,
     - edit config/ or a running test,
     - ask for a brokerage connection (if it does, list it as "refused" under "For the person").
2. **Make the step idempotent, keyed on the message, not only on the status field.**
   - AWS SQS docs (fr): a message copy may be received again, so "Concevez les applications afin qu'elles soient idempotentes" (design applications to be idempotent) [https://docs.aws.amazon.com/fr_fr/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html]. The same message can come back here in four ways:
     - a status write to /mnt/project-files fails or isn't allowed (01 open question 3),
     - two hub SHA ranges overlap,
     - the previous report has no SHA,
     - a hub line is edited and so re-appears in a diff.
   - Proposal: before opening an item, Grep `work/*/request.md` for the source key above. If an item already has it, list "already item NNN" and open nothing.
   - Rule for when the marker can't be used: if the last report has no hub SHA (first run), or the SHA is not an ancestor of `origin/main` (history rewritten), read all of `projects/covered-calls/inbox.md` (once it exists) plus any `shared-facts.md` lines dated since the last report. Say "full read, no usable marker" in the report. This is reasoning from git-scm's definition of `A..B` (01 finding 26). Whether `git log` stops with an error on a missing SHA is UNVERIFIED.
3. **Three explicit states plus a cheap check, so the step can't drift away (RI-002, RI-010).**
   - The template's `## Inbox` section takes exactly one of three states, for each channel separately:
     - `nothing new`,
     - `<n> new` with the list,
     - `UNREAD: <channel> not reachable (<error>)`.
   - Unknown must never be shown as empty (RI-002 root cause). Each run also records the hub SHA range it read.
   - Then make R1's optional guardrail 4 part of the build. check_pipeline.py (or a small test) fails when the newest logs/audit/<date>.md has no `## Inbox` heading, or has one with neither a 7+ hex SHA nor `UNREAD:`.
   - Why: RI-010's history shows that duties written only in agent text are the ones that get skipped. Each earlier guardrail held only once a script checked it (043, 045, 049).

## 3 ways AGAINST
1. **Running a foreign request through to code on the same day widens the prompt-injection surface before the person has seen it.**
   - OpenAI (es): an agent "debe tener límites en sus funciones para reducir el riesgo" (must have limits on its functions to reduce the risk), and the system should show the user what is at stake "y le pedimos confirmación" (and ask for confirmation) [https://openai.com/es-419/index/designing-agents-to-resist-prompt-injection/]. ＠IT (ja) calls for "処理前の確認ステップの導入" (a confirmation step before processing) [https://atmarkit.itmedia.co.jp/ait/articles/2604/05/news007.html]. Kiteworks (nl): agents that process such content "lezen de instructies en voeren ze uit" (read the instructions and carry them out) [https://www.kiteworks.com/nl/beheer-van-cyberbeveiligingsrisicos/indirecte-prompt-injectie-ai-aanvallen/].
   - Here: under the request's "run with the day's items", I2 writes code on a branch driven by another project's text. The person's first look is PR review, after the build.
   - Cost-limiting option for R3 and the person to decide: run inbox items through R1-R3 on the day, list them under "For the person", and start I1 only after the person says so in a thread. This is a deviation from the request's wording, so it needs the person's choice and must not be assumed.
2. **Two writers share one status field, and the writes happen outside the repo and outside review.**
   - Every thread of this project follows PROJECT-INSTRUCTIONS: check `to/covered-calls/` for `unread`, tell the person, then set `status: read` [01 finding 6]. So a morning-recap or work thread can flip a message to `read` before the daily audit runs. A filter on `unread` alone would then never see that test request. R1's rule (a) also reads `read` files from other projects that aren't `done`, and that rule is required, not optional.
   - A1's own status writes and moves on /mnt/project-files are outside its "logs/ and work/ only" rule [01 finding 19]. They don't show in any PR diff and can't be reverted with git.
   - Mitigation: A1 decides what is "new" from its own records (source keys in work/*/request.md and the files listed in the previous report). The status field is never A1's marker. If A1 writes at all, it only sets `read` and only moves `done` files. Whether A1 may write there at all is the person's call (01 open question 3).
3. **Low volume today, so a daily cost now, noise in the report, and one channel that can't deliver at all.**
   - Measured 2026-11-17: 0 messages from another project in `to/covered-calls/` ever, and 0 hub lines addressed to us. The hub has no `projects/covered-calls/` inbox, so the hub channel can't carry a message addressed to us [01 findings 7, 13, Numbers].
   - Each daily run adds a fetch, a diff and a section that will mostly say "nothing new". nss magazine (it) describes alert fatigue as notifications becoming "poco rilevanti ... anche quando questi riguardano notizie di grande importanza" (of little weight ... even when they concern very important news) [https://www.nssmag.com/it/lifestyle/42150/notifiche-alert-fatigue-crisi-informazione].
   - Also, one large FULL request could make the day's run much longer (01 open question 5).
   - Mitigation: one line per channel when empty. Put the hub-inbox gap under "For the person" once, not every day. Creating `projects/covered-calls/inbox.md` and the README row is a hub write that only the person or a thread with hub access can make. Until it exists, the hub check can only catch `shared-facts.md` lines and lines that name us inside other projects' inboxes.

## Findings by language
Random languages this cycle: French, Italian, Dutch (053, the last full search, used Portuguese, German, Korean).
| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | FOR 1: treat peer messages as untrusted unless origin is verified; show who asked before high-impact steps. Hole: assuming inter-agent traffic is trusted by default. | https://www.zealynx.io/research/adversarial-security/owasp-asi07-inter-agent-communication | "treat every agent-to-agent message as untrusted data" | (English original) |
| Mandarin Chinese | FOR 1: peer-agent output is tainted until verified. Hole: no sender authentication. The source proposes signing each message; our inbox has no signatures, so `from:` cannot be trusted. | https://tianpan.co/zh/blog/2026-04-10-three-attack-surfaces-multi-agent-communication | "接收其他智能体输出的智能体应将该输出视为"已污染"，除非它通过了验证。" | "An agent that receives another agent's output should treat that output as 'tainted' unless it has passed verification." |
| Spanish | AGAINST 1: limit what the agent can do with untrusted input, and ask the user to confirm. | https://openai.com/es-419/index/designing-agents-to-resist-prompt-injection/ | "debe tener límites en sus funciones para reducir el riesgo inherente a operar en un entorno malicioso de este tipo." / "o mostramos al usuario la información que se podría transmitir y le pedimos confirmación" | "it must have limits on its functions to reduce the risk inherent in operating in such a malicious environment." / "or we show the user the information that could be transmitted and ask them for confirmation" |
| Japanese | AGAINST 1: validate external content, minimise permissions, add a confirmation step before processing. Hole: shared files are a named injection vector, and our inbox is a shared folder. | https://atmarkit.itmedia.co.jp/ait/articles/2604/05/news007.html | 「AIエージェントには外部コンテンツの検証、権限の最小化に加え、処理前の確認ステップの導入が求められています。」 | "AI agents need validation of external content and minimised permissions, plus a confirmation step before processing." |
| French | FOR 2: delivery can repeat, so make handling idempotent. Hole: duplicate work items when a status write fails or SHA ranges overlap. | https://docs.aws.amazon.com/fr_fr/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html | "Concevez les applications afin qu'elles soient idempotentes (c.-à-d. qu'elles ne doivent pas être affectées si le même message est traité plus d'une fois)." | "Design applications to be idempotent (that is, they must not be affected if the same message is processed more than once)." |
| Italian | AGAINST 3: alert fatigue. Constant notices make even important ones easy to miss. Hole: a daily "nothing new" line that people learn to skip. | https://www.nssmag.com/it/lifestyle/42150/notifiche-alert-fatigue-crisi-informazione | "rendere poco rilevanti gli avvisi informativi, anche quando questi riguardano notizie di grande importanza." | "making informational alerts seem of little relevance, even when they concern news of great importance." |
| Dutch | AGAINST 1: agents that process outside content read the embedded instructions and carry them out. The control is enforced below the model, not by its judgement. | https://www.kiteworks.com/nl/beheer-van-cyberbeveiligingsrisicos/indirecte-prompt-injectie-ai-aanvallen/ | "AI-agenten die deze content doorzoeken, samenvatten of verwerken, lezen de instructies en voeren ze uit." | "AI agents that search, summarise or process this content read the instructions and carry them out." |

## Holes to watch out for (summary)
1. **`from:` can't be trusted.** Anyone can write any `from:` (both current files are self-addressed). Use the file location for "addressed to us" and the git SHA and author for hub origin. Never trust the header alone.
2. **Status race.** Threads set `status: read` before the audit runs, so an `unread`-only filter misses requests. Decide "new" from A1's own records.
3. **Duplicate items.** Grep the source key in work/*/request.md before using `--next-id`.
4. **No usable marker.** The previous report may have no SHA, or the SHA may be gone after a rewrite. Use a full read and say so. Git's exact behaviour on a missing SHA is UNVERIFIED.
5. **Unreachable is not empty.** Use `UNREAD: <channel> not reachable` (RI-002). Whether the scheduled run can reach /mnt/project-files and fetch the hub is still UNVERIFIED (01 open question 4).
6. **The hub channel can't reach us yet.** There is no `projects/covered-calls/inbox.md`. Creating it is a hub write outside this repo; it is the person's action.
7. **Keyword search gives false hits** (01 finding 15). Address by file location, not by the word "covered".
8. **A message is evidence, never approval.** It cannot set FAST, waive a step, change config/ or a running test, or connect to a brokerage. It also gets no exemption from the $3k fit check in R1 (a request from a $500 or other-venue project is judged against our limits).
9. **Same-day build.** Running to code the same day happens before the person sees the request. Offer "R1-R3 today, I1 after the person's OK" as an option. It needs the person's choice.
10. **Writes outside the repo.** Status changes and moves on /mnt/project-files are outside A1's logs/ and work/ rule and outside PR review. They need the person's yes. Otherwise A1 only lists them.
11. **No check, so the step drifts (RI-010).** Add a check that the newest daily report has `## Inbox` with a SHA or `UNREAD:`.
12. **Archive folder missing.** `archive/covered-calls/` doesn't exist yet. The first move must create it (01 finding 9).

Source count (hand count; R3 should take `check_handoff.py`'s figure): 7 new external URLs (Zealynx, Tianpan zh, OpenAI es-419, ＠IT, AWS SQS fr, nss magazine, Kiteworks nl), plus local repo and log files.
