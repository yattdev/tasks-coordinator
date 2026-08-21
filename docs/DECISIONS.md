# Design decisions

## One active Coordinator per workspace (2026-08-20, incident-derived)
Coordinator ownership is scoped by `workspace_id`, not by repository directory,
shared memory, task title, or routine name. Every session resolves its own task,
workspace, and workflow before board action. Coordinators for different
workspaces remain active peers; standby and takeover rules apply only to
same-workspace contention. This prevents a shared-memory identity from causing
cross-board moves, plan overwrites, false routine-target alarms, or an entire
unrelated board being stood down.

## Workflow column plus session must reconcile (2026-08-20)
The workflow step is authoritative. Messaging an idle session may make it
RUNNING without correcting a stale column, profile, or pending move. Every action
cycle therefore re-lists touched tasks and verifies physical step, task state,
primary session, effective profile, and pending move. Coordinator-owned approved
Todo tasks are moved Todo→Work before messaging so on-entry owns the new session.

Independent gates additionally require a fresh session and immutable-head
receipt. A Review or QA column containing the still-running authoring session is
a settling transition, not proof that independent review began.

## Gate evidence follows physical ownership (2026-08-21)

Ad-hoc review evidence gathered during Work does not imply the task already
traversed Review or QA. The physical workflow step remains authoritative and
configured gate entry must still occur. After an exact-head independent Review
PASS exists in the physical Review step, however, missing or incomplete CI is
not a reason to hold Review: PR and CI Fixup own CI evidence. This keeps each
stage accountable for its own contract and prevents both skipped gates and
Review becoming a catch-all waiting room.

## Stale RUNNING recovery is session-scoped, never database-scoped (2026-08-21)

A RUNNING row without a live process, output, or advancing timestamp is stale
even if it accepts queued messages. Repeated messages can wedge the caller's MCP
transport and must stop after a bounded probe. Parent-scoped stop remains the
only task-agent stop authority; unrelated top-level sessions require operator
UI action. If the caller stays wedged after the stale target is stopped, replace
only the caller session. Health/database/process reads may establish the
diagnosis, but direct database mutation, credential extraction, and shared
backend restarts are not recovery mechanisms.

## Repository-qualified, current-head PR evidence (2026-08-20)

PR/MR readiness evidence is keyed by canonical URL and exact head SHA. Bare
numbers are ambiguous across forks, and superseded-head checks or reviews cannot
prove the current head. Every push or base change invalidates the prior readiness
snapshot until checks, threads, reviews, and mergeability are refreshed.

Human-QA preserves the integration boundary. A conflicted PR may lack ordinary
`pull_request` workflows because the provider cannot create a merge ref; this is
an integration gate, not permission to rebase or merge main during Human-QA.

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

## Human-QA requires a LAN Docker clone of main data (2026-08-20, human-directed)

For tasks that need a persistent runtime, Human-QA readiness now requires one
exact-head task-owned Docker instance, the previous task instance stopped, a
verified LAN URL, and a private writable clone of a sanitized immutable snapshot
of the main container's application data. The main instance and data remain
strictly read-only. This is an acceptance gate, not a best-effort convenience:
wrong-head, empty, unseeded, shared-main, credential-bearing, non-Docker,
localhost-only, or feature-broken instances are rejected. Runtime-free tasks may
declare `TEST_RUNTIME=NONE` with a reason.

Rationale: realistic data is required for meaningful human testing, while
sharing the live database makes a test destructive. Exact-head isolation and
destination-only credentials/fixtures make the result reproducible and keep
main safe. The first enforcement cycle also found stale external-content FTS
rows that passed SQLite integrity checks but broke the next task insert, so the
handoff additionally requires disposable-write proof rather than integrity
checks alone.
