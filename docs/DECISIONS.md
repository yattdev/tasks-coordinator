# Design decisions

## Long-lived pinned task, not a daemon
Reuses KanDev primitives (session, tools, flags, comment trail) and dogfoods
the platform. A separate service only if event-driven triggers become necessary.

## Wake via External MCP `message_task_kandev`, not automation/webhooks
KanDev has no idle wake-up. The automation feature and webhook triggers create
a NEW task per fire — unusable for waking an existing task. The SPA deep link
does nothing without a browser (resume is done by frontend JS over WebSocket).
`message_task_kandev` on an idle task delivers immediately = wake; on a running
task it queues = harmless. Verified: [date, result of the idle-relaunch test].

## Cron → script → MCP, not protocol-in-crontab
MCP streamable HTTP needs a handshake; crontab stays one dumb line, all
protocol lives in the script, config in one env file.

## Action budget (1 task creation/cycle, no Done/backwards moves)
The coordinator is the highest-blast-radius agent: a misread board amplifies
across every task in one cycle. Budgets cap the damage; loosen only after
weeks of clean FYI/veto history.

## Escalation contract (3 reasons only)
High-stakes fork / irreconcilable cross-task conflict / systemic anomaly.
Everything else: decide-and-document as vetoable. Matches the trust model:
veto async from the board rather than pre-approve.

## Daily standup + adaptive cycle cadence (2026-08-16, human-directed)
The human works every day — weekday-only schedules were wrong. Standup fires
daily. Mid-interval monitoring (30–60 min) is judged from board occupancy:
active tasks anywhere Spec..CI Fixup → cycle wake-ups on (in-progress tasks
often block silently and don't report); empty pipeline → standup only.

## Spec is a first-class monitored step (2026-08-16, human-directed)
Spec tasks block quietly, wait on "human input" the coordinator can answer
(conventions, directory layout, scope interpretation), or sit with complete
plans. The coordinator answers what a lead would answer, and moves
plan-complete Spec tasks forward to Todo itself (vetoable, reported as FYI).

## Harness scheduler fallback (2026-08-16)
This executor image has no crontab binary. Wake-ups use the agent-harness
cron tools with the same markers in job prompts; jobs are session-scoped and
auto-expire (~7 days), so every wake-up re-verifies and recreates them.
Trade-off accepted: a full session restart drops the jobs until the next
manual message re-arms bootstrap — flagged in the setup report 2026-08-16.

## Flag substitution (2026-08-16, human-approved)
No flag_task tool exists in the MCP server. Interim: flag =
`[COORDINATOR FLAG]` comment + daily-report line; unflag =
`[COORDINATOR UNFLAG]`. Auto-reverts if a real flag tool appears.

## Platform bugs become board tasks (2026-08-17, human-directed)
The coordinator never fixes kandev platform code and never merely reports a
platform bug: it CREATES a task (evidence + where-to-look + acceptance criteria
incl. regression test) and monitors it like any other. First instance: stale
pending-move replay in workflow routing (task 6e0fc028).

## Knowledge sync across coordinator worktrees (2026-08-17, human-directed)
Each coordinator instance runs in its own worktree of the shared clone; main
(/data/home/Code/coordinator) is the source of truth. Rebase onto main before
editing; after every commit, fast-forward main from the main checkout
(`git -C /data/home/Code/coordinator merge --ff-only <branch>`). Conflicts are
hand-merged into a superseding version — never discard the other side's
learning (first occurrence: main's degraded-mode refinements × this branch's
daily-standup/adaptive-cadence changes → merged v2026-08-17). PROMPT.md changes
are mirrored into the kandev task description after every merge.

## DST
CRON_TZ=America/Toronto so 8:00 tracks Montreal wall clock across EST/EDT.
If the cron daemon ignores CRON_TZ, entries are in UTC with the assumed
offset noted in the marker comment (drifts 1h at DST changes).
