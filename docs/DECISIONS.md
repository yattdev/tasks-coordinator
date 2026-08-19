# Design decisions

## Long-lived pinned task, not a daemon
Reuses KanDev primitives (session, tools, flags, comment trail) and dogfoods
the platform. A separate service only if event-driven triggers become necessary.

## KanDev routines are the sole wake source (2026-08-19, human-directed)
The self-managed cron/heartbeat design failed to keep the Coordinator awake and
created unverifiable scheduler state across sessions. It is removed. An
operator-owned KanDev routine now targets the existing Coordinator task every
15–30 minutes, with a separate daily 07:00 America/Montreal standup routine.
The Coordinator consumes these pings and never creates or repairs a scheduler.

## Action budget (1 task creation/cycle, bounded terminal cleanup)
The coordinator is the highest-blast-radius agent: a misread board amplifies
across every task in one cycle. Budgets cap the damage; loosen only after
weeks of clean FYI/veto history.

Human-directed exception (2026-08-19): the Coordinator may move a task to Done
when its trail proves it is abandoned, obsolete, or superseded, no further
implementation is authorized, and it has no open PR or subtask. The resolution
must preserve partial work/history and must not imply that acceptance criteria
passed. Prefer this terminal disposition over deletion; deletion remains
separately human-authorized and destructive.

## Escalation contract (3 reasons only)
High-stakes fork / irreconcilable cross-task conflict / systemic anomaly.
Everything else: decide-and-document as vetoable. Matches the trust model:
veto async from the board rather than pre-approve.

## Daily standup files + five-day rotation (2026-08-19, human-directed)
The standup runs every day at 07:00 America/Montreal. Its full body is written
to `standups/standup-YYYY-MM-DD.md`, not posted in chat; chat contains only the
document name. The five newest dated reports are retained.

## Spec is a first-class monitored step (2026-08-16, human-directed)
Spec tasks block quietly, wait on "human input" the coordinator can answer
(conventions, directory layout, scope interpretation), or sit with complete
plans. The coordinator answers what a lead would answer, and moves
plan-complete Spec tasks forward to Todo itself (vetoable, reported as FYI).

## Task creator owns Todo → Work (2026-08-17, human-directed)
Todo intentionally does not auto-start an agent. When the Coordinator creates a
child, that child completes Spec, and its approved plan lands in Todo, the
Coordinator must move it promptly to Work and verify the Work session started.
This exception is ownership-scoped: unrelated/manual Todo tasks remain human-owned.

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

## 24/7 monitoring + visible ask-channel (updated 2026-08-19, human-directed)
The coordinator is not human and must not mimic human working hours: routine
cycles run every 15–30 minutes around the clock whenever anything is in a
creator-owned Todo handoff, or parked on a decision. Quiet cycles reduce depth,
never frequency. Separately: every human-facing question/blocker goes through
ask_user_question_kandev (visible input icon on the task) — the editing-blocker
decision sat unanswered a full day because it lived only in prose reports.
Text reports summarize; the ask tool escalates.

## Blessed unblock powers (2026-08-18, human-approved)
Standing powers, used sparingly, always logged vetoable: (1) spawn_session onto
a stuck same-workspace task; (2) forward moves past confirmed platform defects;
(3) gh pushes for mechanical repo operations (seeds, authorized PR closures).
Granted after all three proved out on 2026-08-17 (scheduler-fix session, loop
bypass, template seed).

## Editing blocker resolution: pin now, container-fix later (2026-08-18, human decision)
Human chose BOTH: pin Claude profiles to Work/Review/CI-Fixup immediately
(human clicks; coordinator verifies via list_workflow_steps and resumes the
gated tasks), and a platform task (6a5a2f73) designs a configurable
userns-permitting seccomp profile for executor containers as the durable fix —
after which the pinning can be reverted.

## Time zone
The standup routine uses America/Montreal so 07:00 follows local wall time
across EST/EDT. The report filename uses that same local calendar date.
