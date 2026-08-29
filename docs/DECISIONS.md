# Design decisions

## Coordinator continuity is storage-backed, not session-backed (2026-08-24, human-directed)

The long-lived Coordinator role must survive session termination, compaction,
model changes, and provider limits. Its continuity is deliberately split across
versioned binding policy (`PROMPT.md`), versioned reusable procedures and
learning (`docs/`), and frequently updated live operational state (the Kandev
task plan). Model-specific conversation memory is never the only copy.

Every session loads these layers before acting and performs a save checkpoint
before yielding. Repository compatibility loaders and the mirrored live task
description make the bootstrap visible to different agent clients. If a hard
interruption prevents saving, the successor reconstructs from task/session,
repository, provider, and log evidence and repairs the handoff. We preserve
decisions and evidence, not hidden chain-of-thought.

## Reply-bearing delegation requires proactive follow-up (2026-08-24, human-directed)

Every outbound task/session request that expects a reply is tracked in a
persisted follow-up ledger until the requested evidence or explicit response is
observed. Transport acknowledgement and `WAITING_FOR_INPUT` do not prove the
handoff completed: sessions can be interrupted, terminated, or rate-limited
without reporting back.

The Coordinator rechecks due entries during routine cycles, avoids duplicate
pings while work is active, waits until a known provider reset before one
retry, and then executes a recorded fallback or escalation. Urgent work may be
routed to the primary or another authorized helper immediately, while partial
work and transcripts remain preserved. This gives proactive recovery without
adding a hidden scheduler or multiplying sessions.

An unanswered request is a state-diagnosis event, not a reason to repeat the
message. The Coordinator inspects every session, conversation, pending queue,
workspace startup, and backend error. It then chooses exactly one corresponding
action: leave an actively working session alone, start one replacement session
when the prior session is terminal and the workspace is healthy, or route a
workspace-start failure to its existing repair owner and retry only after the
repair trigger clears.

## WAKE:CYCLE is an explicit action contract (2026-08-24, human-directed)

The routine may deliver either the short `WAKE:CYCLE` marker or the expanded
canonical checklist in `PROMPT.md`; both require the same complete action cycle.
The expanded prompt makes durable the operating lessons that are easy to omit
under queue pressure: bootstrap from live identity and persisted state, inspect
all sessions and Done receipts, delegate only bounded read-only evidence slices,
diagnose failures from transcripts/logs, preserve incomplete work, enforce
exact-head draft readiness, distinguish branch defects from base/provider
failures, use valid Human-QA fixtures, surface human-only blockers through the
visible ask channel, reconcile every mutation, and persist the result. The
routine schedule remains operator-owned and is not changed by a cycle.

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

## External credentials are action-scoped, not session-scoped (2026-08-21)

A worker's failed GitHub credential lease does not make an authorized,
mechanical PR action impossible when the Coordinator independently holds a
valid repository-scoped identity. The Coordinator may reply to and resolve
already-addressed review threads after verifying canonical repository, exact
head, code/test evidence, and current unresolved state. It records discussion
URLs and the resulting state, never transfers credentials, and does not expand
this exception to implementation, history changes, merge, or release.

Provider rate limits are evidence gates: successful mutations remain valid, but
unavailable follow-up queries are reported as unavailable rather than inferred
green. Likewise, external PR work completed during a Kandev transport outage
does not constitute a monitoring cycle and must not advance board state without
task-control reconciliation.

## Repository-qualified, current-head PR evidence (2026-08-20)

PR/MR readiness evidence is keyed by canonical URL and exact head SHA. Bare
numbers are ambiguous across forks, and superseded-head checks or reviews cannot
prove the current head. Every push or base change invalidates the prior readiness
snapshot until checks, threads, reviews, and mergeability are refreshed.

Human-QA preserves the integration boundary. A conflicted PR may lack ordinary
`pull_request` workflows because the provider cannot create a merge ref; this is
an integration gate, not permission to rebase or merge main during Human-QA.

## Draft readiness belongs to the task agent; the Coordinator owns the gate (2026-08-24, human-directed)

When no acceptance criterion genuinely requires remaining human testing, the
owning task agent makes its PR/MR ready after it has committed and pushed a clean
exact head, run applicable tests with high confidence, obtained terminal-green
required CI, addressed and replied to every actionable review thread, supplied
sanitized screenshots/recordings for visual changes, and refreshed an accurate
reviewer-facing title/body/scope and mergeability snapshot.

The Coordinator directs and verifies this work as the board lead; it does not
implement the task's missing fixes, tests, or visual evidence. A credentialed
Coordinator fallback may perform only the mechanical draft→ready provider action
after the task agent explicitly reports readiness and the primary independently
verifies the complete gate. Human-only testing, external access, or approval keeps
the PR draft and is surfaced through the visible ask channel. Ready-for-review is
not merge, deploy, or permission to skip workflow gates, and every later head/base
change invalidates the readiness snapshot.

A bounded read-only helper (`/root/pr_readiness_policy_audit`) audited this rule's
placement against the existing exact-head, credential-fallback, human-testing,
and delegation policies. The primary independently reviewed its receipt and
adopted the monitoring-cycle enforcement hook; the helper made no changes.

## Merge-result failures are classified by semantics and job boundary (2026-08-21)

A failing merge-result test is not automatically a branch regression. If a
current-main test encodes an assumption that contradicts the task's accepted
invariant, the integration phase owns reconciliation of the test fixture and
the merge result; Human-QA does not weaken production behavior or bring main
into the branch. Fresh merge-result CI is required after that authorized work.

CI classification is per job and failure boundary, not per workflow aggregate.
Runner/artifact/setup failures before product execution are infrastructure,
while a deterministic product test that reaches the application remains
task-owned even if an unrelated shard is broken. Both classifications coexist
and receive separate remediation/evidence.

## Long-lived pinned task, not a daemon
Reuses KanDev primitives (session, tools, flags, comment trail) and dogfoods
the platform. A separate service only if event-driven triggers become necessary.

## Temporary helpers accelerate triage; authority stays primary (2026-08-24, human-directed)

The active Coordinator may use bounded temporary sessions/agents to triage an
inbound message burst or gather evidence for disjoint task slices. Helpers are
read-only by default, receive only the task IDs and context needed for their
slice, and report evidence/classification/recommendation back to the primary
session. They are not additional coordinators and do not independently move,
message, flag, create, archive, delete, edit, push, escalate, clean resources, or
declare gates complete.

The primary Coordinator retains decision and reporting responsibility. It
independently verifies workspace and task/PR identity, current head/state,
authority, and any explicitly delegated mutation, then reconciles live state and
records helper provenance. Prefer temporary sessions on the Coordinator task for
an auditable shared trail, normally at most two concurrently with disjoint
assignments. Delegation never creates a scheduler or persistent board task and
ends at the active turn's stated stop condition.

First pilot receipt: temporary session `a2a3eccc-0bd3-4364-8eef-2f782635166e`
triaged three named message-linked tasks read-only, detected one superseded
instruction, one healthy exact-head CI wait, and one duplicate-session risk from
a pinned rate-limited profile. The primary independently re-queried both PRs and
all three session inventories before accepting the report. The helper's relation
reads were forbidden, but the bounded fallback evidence was sufficient; no
helper mutation was required.

## KanDev routines are the sole wake source (2026-08-19, human-directed)
The self-managed cron/heartbeat design failed to keep the Coordinator awake and
created unverifiable scheduler state across sessions. It is removed. An
operator-owned KanDev routine now targets the existing Coordinator task every
15–30 minutes, with a separate daily 07:00 America/Montreal standup routine.
The Coordinator consumes these pings and never creates or repairs a scheduler.

## Disposable wake sessions are reminder carriers, not reminder state (2026-08-28, human-directed)

Each `WAKE:CYCLE` may create a new automation session that is removed after a
retention window. Therefore a wake session cannot be the sole durable home of a
GitHub rate-limit reminder. The Coordinator stores one reset record per GitHub
resource in its plan, using `Retry-After` or `X-RateLimit-Reset` plus a 15–30
second buffer, and the first routine at or after that deadline performs one
bounded retry. A repeated limit updates the same dedupe entry; `401` is handled
as a separate credential blocker.

A live wake session may accelerate delivery only through a native, verified
future-delivery operation whose receipt includes the dedupe key and timestamp
and whose retention covers the deadline. Immediate/queued task messaging is not
scheduling. This preserves the operator-owned routine boundary, prevents sleep
or polling loops, and makes session deletion harmless. The Coordinator plugin
should expose the native schedule-at accelerator while retaining the plan
ledger as authoritative state.

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

## Done is a monitored terminal-integrity lane (2026-08-24, human-directed)

The Coordinator enumerates Done on every full cycle. It deep-audits newly
entered, changed, unreceipted, or suspicious tasks and shallow-verifies stable
tasks against a persisted terminal receipt. A merged PR is necessary evidence
for normal code work but is not sufficient: the local task head may contain a
later Human-QA commit that was never pushed or included in the merge.

The receipt binds task ID, qualified PR/MR and accepted head, local head, remote
containment, tree state, session/subtask state, and resource disposition. Unique
local or untracked work halts cleanup and authorizes a move to the narrowest safe
active recovery step. Work is never discarded on a claim of supersession without
ancestry or scenario-level equivalence evidence. This recovery is a safety action,
not a claim that the operator's Done move was generally wrong.

## Physical Blocked owns stopped active work (2026-08-29, human-directed)

Backlogs and ToDeploy are Human-managed holding columns; Human-QA waits for
Human review/testing. Every other column is Coordinator-supervised. When a task
there is expected to progress but cannot, the Coordinator moves it to
physical Blocked in the same cycle, marks it HIGH PRIORITY, records preservation
and a concrete removal action, and rechecks it every cycle. Blocked is an active
recovery queue, never an optional label or parking place; clearing the trigger
requires an atomic return to the recorded actionable step plus verified session
startup.

This supersedes older scope language that left unrelated Todo or stopped active
cards Human-owned, or allowed a task to remain stopped outside physical Blocked.
It does not override a task-specific Human hands-off directive, the strict
ToDeploy boundary, Human-QA ownership, or the Done terminal-integrity gate. A
hands-off conflict is recorded with its exact denial and Human authorization
trigger, never bypassed.

## Done is destructive cleanup, not "closed" or merely complete (2026-08-27, human-directed)

The workflow columns represent distinct lifecycle states. Active delivery lanes
retain tasks whose canonical PR/MR is open or whose review, testing, CI,
integration, or merge is unfinished. `ToDeploy` is post-acceptance and
post-merge: required Human validation has passed when applicable, the canonical
deliverable is merged, and the task remains available while deployment,
dependencies, subtasks, sessions, or post-merge coordination still need it.

`Done` is terminal and cleanup-capable. Its agent may remove task worktrees,
local branches, runtimes, and artifacts after verification, so placing an open
PR, merely green branch, closed-unmerged PR, or still-needed task there creates
a data-loss risk. Normal code work reaches Done only after the canonical
deliverable is merged, acceptance is satisfied, no task/session/runtime or
dependency still needs it, all work is durable, and cleanup is safe. The
abandoned/obsolete/superseded exception still requires no open PR/MR or subtask
and an explicit terminal reason.

Incident receipt: task `65af61f6-792d-497c-a313-a0436f6fe627` was recovered
from Done to Review while canonical `kdlbs/kandev#3052` remained open. The Done
agent correctly refused cleanup because the Kanban implementation/test content
was not preserved in the main checkout; nothing was deleted. This establishes
an explicit pre-move gate: verify merged identity, accepted head, no open
replacement, no remaining dependency/session need, durable local work, and safe
resource disposition before exposing a task to Done cleanup.

## ToDeploy is strictly human-owned except for Coordinator-created tasks (2026-08-27, human-directed)

While a task is physically in ToDeploy, the Coordinator does not perform
task-specific reads, messages, flags, updates, moves, cleanup, archival, or
resource inspection unless the Coordinator created that task. A board-wide
inventory may incidentally expose the card's identity and column, but it does
not authorize a deeper query. The human moves all other ToDeploy tasks to Done;
the Coordinator may terminally verify and move only its own created tasks from
ToDeploy to Done. This explicit ownership boundary supersedes older language
that treated ToDeploy as monitored or allowed reading its transition for a
future Done audit. Once a human-owned task reaches Done, its terminal audit uses
the live Done record and durable provider/repository evidence.

## One canonical charter with model-specific loaders (2026-08-24)

`PROMPT.md` remains the only full Coordinator policy. Root `AGENTS.md`, root
`CLAUDE.md`, and `.github/copilot-instructions.md` are thin boot loaders that
require a complete charter and live-plan read at the start of every turn. This
is more reliable than a skill alone: skills are selected by task trigger and are
not guaranteed to load for every routine wake or across agent vendors. The live
Kandev task description remains the runtime launch copy and is mirrored after
each charter change.

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

## Task PR/MR links follow the current deliverable (2026-08-27, human-directed)
Provider-linked PR/MR cards are operational identity, not immutable history.
When a recovery, superseding implementation, or follow-up PR/MR becomes the
task's current deliverable, the Coordinator verifies its canonical repository
identity, removes the obsolete association, and links the replacement. Old URLs
remain in the task trail and terminal receipt for auditability. A merged link is
not removed when it is still the canonical completed deliverable. If Kandev
lacks safe link mutation, the Coordinator creates one platform capability task,
persists the pending replacement set, and waits for deployment rather than
editing storage directly or leaving future Coordinators to rediscover the gap.

## Knowledge sync across coordinator worktrees (2026-08-17, human-directed)
Each coordinator instance runs in its own worktree of the shared clone; main
(/data/home/Code/coordinator) is the source of truth. Rebase onto main before
editing; after every commit, fast-forward main from the main checkout
(`git -C /data/home/Code/coordinator merge --ff-only <branch>`). Conflicts are
hand-merged into a superseding version — never discard the other side's
learning (first occurrence: main's degraded-mode refinements × this branch's
daily-standup/adaptive-cadence changes → merged v2026-08-17). PROMPT.md changes
are mirrored into the kandev task description after every merge.

## Standing workspace source-broker authority (2026-08-27, human-directed)
Broker-validated Coordinators may autonomously use `docker kandev source` list,
curated inspect, bounded logs, and logical database dumps, including
production-like data requested by active same-workspace tasks. Case-by-case
human approval is unnecessary; broker enforcement is authoritative for target
activity and workspace membership. Source access identity always comes from the
Coordinator's materialized task worktree, while the shared main checkout remains
the Git synchronization point for durable Coordinator knowledge.

## Database dump delivery is not restore acceptance (2026-08-28)
Broker authorization and artifact integrity prove that the correct bytes reached
the correct same-workspace task; they do not prove that the destination database
accepted every statement. A restore can leave a plausible partial schema even
when the dump contains the missing table definition and the client appears
silent. Therefore the handoff has three independent gates: delivery hash/size,
unsuppressed client exit and first-error evidence into a known-clean task-owned
database, then schema/data plus feature-level verification. Overlaying a retry
onto a partial restore obscures causality, so retries start from a recreated
task-owned destination and use a fresh short-lived artifact when necessary.

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

## Coordinator is the full board approval principal (2026-08-27, human-directed)

The Human clarified that the Coordinator has full approval authority on every
task in its live workspace, regardless of task creator. A Coordinator approval
is sufficient; agents do not wait for or request a second Human approval. The
Coordinator proactively decides, resumes, and verifies the work.

Only two approval classes remain Human-reserved: destructive/practically
irreversible actions and security/trust-boundary actions. Normal task edits,
tests, commits, non-rewriting pushes with configured credentials, PR/MR work,
draft readiness, additive reconciliation, reversible board actions, CI/review
remediation, and bounded provider operations are Coordinator-approved work.
Production, protected-branch, cost, or external-communication labels do not by
themselves create a separate approval gate; the concrete operation is classified
by destructiveness and security impact.

Each approval names the task, repository/remote, branch/head where relevant,
preservation constraints, expected receipt, and fallback; the Coordinator then
verifies the outcome and logs the decision as vetoable. A task guard that still
requires a direct Human message is a platform capability defect and belongs to
the grant-management task, not a reason to make the Human a reminder service.

Human escalation remains mandatory for deletion or task-resource removal that
may remove unique or still-needed state, reset/clean/discard, force-push,
rebase/squash/amend of published history, secret or credential
disclosure/scope expansion, authorization weakening, security policy bypass, or
cross-workspace/trust-boundary access. Existing explicit Human operating
constraints remain binding; notably, non-Coordinator-created ToDeploy tasks stay
outside Coordinator access unless the Human changes that boundary.

Human clarification (2026-08-28): exact task-local worktree and local-feature-
branch cleanup is Coordinator-approved when the full Done gate proves the
canonical deliverable is merged, every task change is durable in the accepted
result, the tree has no uncommitted/untracked deliverable or unpushed commit, and
no session/runtime/subtask/dependency still needs the resource. The approval is
bound to exact paths/refs, excludes remotes/shared checkouts/unrelated resources,
and requires post-delete verification. Active process cwd use, uncertain
ownership, or any unique state fails this exception and keeps cleanup preserved.

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

## QA fixtures default to purpose-built, not to a production copy (2026-08-22)

Seeding Human-QA instances from the live application database is permitted only
when broad real-world breadth is the thing under test AND the feature has no live
write path. Otherwise build a synthetic fixture.

Rationale: a blanket "copy production" instruction issued mid-cycle produced, in
one afternoon, a copied `master.key` inside a LAN-published container, an instance
serving the operator's entire board with authentication disabled, and several
wasted rebuilds. It also failed on the merits — production could not contain the
states the features needed (an available plugin upgrade, monitored workflow steps,
a resolvable in-container workspace path). Tasks that refused the instruction were
right, and the refusals contained it faster than review did.

Corollary: order matters. "Load real data, then verify isolation" creates the
exposure before checking it. Never put data in reach that the feature could act on.

## A shared repair lands once, not per PR (2026-08-22)

When a broken base blocks multiple branches, the repair commit is landed once via
its owning PR. Narrow cherry-picks are authorized only for a task physically
unable to commit locally, and must be declared in the PR description as an
imported repair that will dedupe when the owning PR lands.

Rationale: N copies of the same commit across N PRs collide on merge and obscure
which branch actually owns the fix.

## An honest "not testable here" beats a fixture that looks ready (2026-08-22)

When the QA image cannot exercise a feature's success path — missing binary,
missing agent-profile family, feature flag off, session-scoped tool unreachable —
classify the task as ready for review WITHOUT a runtime instance and hand over
named automated coverage instead. Do not stage files that make a broken path look
demonstrable.

Rationale: a display-only fixture converts an infrastructure gap into a false bug
report against the feature, wasting the reviewer's time and impugning correct work.
Three tasks hit distinct image limits in one cycle; each was more useful having
said so plainly.

## Report session state, not board column (2026-08-22)

Any statement that a task is working, implementing, or progressing must be derived
from its primary session state, not from the step it occupies.

Rationale: the Coordinator reported a task as "implementing" while it had been
idle and blocked for ninety minutes. The operator noticed before the Coordinator
did. A column cannot distinguish blocked from busy.

## The ask-channel is for blocked tasks too, and must be used (reaffirmed 2026-08-22)

Any blocker requiring operator decision, permission, credential, or a fix only the
operator can apply — whether it originates in the Coordinator's own work or in a
supervised task/subtask — is surfaced through ask_user_question_kandev, not left in
a cycle report. The operator reaffirmed they will not notice prose escalations.

Rationale: the operator directly corrected a reading that the ask tool should be
used sparingly — "use the ask tool, otherwise I'll not notice anything," extended
to "blocked tasks that need my clarification should also use it." A report is a
summary; the ask channel is the notification.

## Verify operator infra fixes before closing (2026-08-22)

When the operator says a host/network/infra issue is fixed, re-run the defect's
acceptance test and report concrete evidence before marking it resolved. This is
loop-closing, not distrust, and it has caught a fix that was reported but not
actually applied (a NAT rule still redirecting because a broad rule was left in
place / the wrong ruleset engine was edited).

## Deliberate host rules are scoped, not removed (2026-08-22)

A host redirect/NAT/proxy rule that serves an operator convenience (e.g. port-80
browsing) is corrected by constraining it (inbound interface, or excluding
container source ranges), never by deleting it. Establish what a rule is FOR
before recommending its removal; the acceptance test is run from the exact path
the failure used (a bridge container for Docker egress).

## Zero-diff verified platform fixes go straight to Done (2026-08-22)

A task whose deliverable is a host/platform remediation with an empty diff — the
fix lives in operator-applied host config, not code — is routed directly to Done
once its own acceptance gate is independently verified, skipping PR and CI Fixup.
Marching an empty diff through those steps produces a guaranteed no-op or failure.

Rationale: dd4f90b0 (Docker-bridge port-80 NAT redirect) fixed a host-config fault
with zero repository change; its regression test is the disposable-bridge apt
probe, not an in-repo artifact. Recorded as a resolution with evidence, not a claim
that a code PR passed review; the acceptance criterion that lived in a sibling
feature task was reassigned there rather than closed. Logged vetoable.

## A broken base pauses dispatch; the compile check lifts it (2026-08-22)

When upstream/main does not compile, hold routine task dispatch — every branch is
red on the same inherited line and pushing work forward adds nothing. Escalate the
single high-leverage ask (merge the repair / fix the base). Lift the hold when the
base compiles again, verified by building it directly, because the repair may land
via a different PR than the one escalated (broken base escalated as #2842, repaired
by #2916). Knowledge, standup, and learning work continue through the hold.

## Preserve a platform fix's reproduction over a safe one-off workaround (2026-08-24)

When a FAILED task is the live reproduction case for an in-flight platform-bug fix,
the Coordinator does NOT apply an otherwise-safe operational workaround to unblock
it — the failed state is preserved until the fix lands, then the task resumes on
the repaired logic.

Rationale: 375dcc90 (stale-worktree collision) had a verified-safe `git worktree
remove` available, but c0db9627's platform fix cited 375dcc90's worktree as its
reproduction. Clearing it would have destroyed the repro the fix is validated
against — a worse outcome than a preserved FAILED task. "Safe to do" is not
"correct to do" when a durable fix depends on the broken state.

## Coordinator is a workspace plugin principal, not a worker-task role (2026-08-28, human-directed)

The long-lived Coordinator task is a useful bootstrap and compatibility model,
but it is not the target architecture. An ordinary task inherits task-scoped
relationships, session lifecycle, workflow transitions, and parent-only action
limits. Making it supervise unrelated board tasks therefore requires fragile
special cases, duplicates policy/state across workspaces, and leaves board
orchestration vulnerable to an ordinary task session becoming stale or blocked.

The target is a first-class, workspace-scoped Coordinator plugin principal. It
owns isolated durable orchestration state, board/event history, monitoring and
escalation policy, and explicit audited capabilities for task inspection,
messaging, movement, dependency management, session control, PR/MR links, and
automation. Parent-equivalent or cross-task operations are mediated platform
operations: validate the workspace, exact target, preservation preconditions,
and permitted action, perform only that bounded operation, and return an audit
receipt. The plugin is not granted an unrestricted cross-task filesystem or
container shell.

Versioned plugin policy can distribute improvements consistently across
workspaces while each workspace keeps separate authority and state. Destructive
unique-state operations and security/trust-boundary changes remain Human-gated;
the existing verified-redundant cleanup exception and full same-workspace
approval policy still apply. Until the plugin is deployed, the task-based
Coordinator remains the operational fallback and must obey its current scope.

## Host environment blockers route through the dedicated Support thread (2026-08-29, human-directed)

Missing tools or dependencies, permission and access failures, unavailable host
capabilities, Android emulator or device support, and other host/container limits
route to `Kandev Support — Codex`, thread
`01a043b4-fe52-7020-94bb-de94e72f8a07`. Missing Kandev platform features remain
board work and do not route through this support path.

Agent containers cannot directly resume the host thread. A bounded validation
using the documented resume command returned `thread/resume failed: no rollout
found for thread id ... (code -32600)`; it did not deliver a request and did not
create a queue. Until a reviewed support broker exists, the owning board/task
trail must carry a complete paste-ready request containing the Coordinator task
and session, affected task and session when applicable, worktree, exact evidence,
expected outcome, and destructive/production-sensitivity classification. A
host-side operator or Support agent runs the resume command. Coordinators must
not target the thread with Kandev task messaging, claim direct delivery, expose
host `~/.codex`, or retry unsupported workarounds.

Rationale: this preserves host isolation while giving environment blockers a
single named owner and a reproducible handoff instead of leaving workflow tasks
stalled or cycling through ineffective retries.

Two Coordinators reproduced the `-32600` failure independently, from different
worktrees and sessions, on 2026-08-29. The CLI is installed and authenticated, so
the call genuinely reaches the RPC layer; only the host thread's rollout state is
absent. The finding is therefore recorded as SETTLED — later cycles escalate
through the trail rather than re-probing it and burning turns.

Corollary on capability discovery: a guarded broker may under-report itself.
`docker kandev --help` announces `docker compose` support only, while
`docker kandev source list` succeeds and returns the workspace inventory.
Establish capability by running the specific documented operation, not by reading
top-level help — otherwise a working authorized path is mistaken for a missing
one, producing exactly the needless escalation this decision exists to prevent.

## Kandev Support is contacted autonomously through the broker (2026-08-29, supersedes the board-trail relay)

**Supersedes** the 2026-08-29 decision above stating that agent containers cannot
deliver to the Support thread and must leave a paste-ready request in the board
trail for a human to run. That conclusion was drawn from testing only
`codex exec resume`, which fails from a container with `no rollout found for
thread id ... (-32600)` because host Codex rollout state is deliberately not
mounted. It generalised one blocked route into "no route exists".

A reviewed broker route does exist: `docker kandev support send|status|receive`.
An acceptance test on 2026-08-29 confirmed the transport end to end — `send`
returned a request ID and `queued`, `status` reached `complete` in ~10-15s, and
`receive` returned the genuine host-side stdout/stderr of the resume attempt. The
broker runs the resume host-side, which is exactly why host Codex state can stay
unmounted. Coordinators therefore contact Support themselves and must not ask the
Human to relay routine requests.

The board-trail handoff remains the correct fallback only when the broker itself
is unavailable — not as the default.

Two failure modes must not be conflated, because they have opposite remedies:
`no rollout found` means the wrong route was used (switch to the broker), while
`thread-store conflict: ... already has an active writer` means the broker worked,
reached the host, and found another writer holding the thread — an operator-side
release, and a genuine escalation once it persists across spaced retries.

Rationale: a capability wrongly recorded as impossible is more costly than one
merely undocumented — it teaches every future session to route around a working
path and to spend the Human's attention on requests an agent could file itself.
The general lesson is that "cannot" claims must name the exact route tested, and a
guarded broker's advertised surface (`docker kandev` no-args omits `support`
entirely) is not evidence of what it can do.

## Active Support writers are broker backpressure, not terminal failure (2026-08-29, supersession)

**Supersedes** the earlier same-day conclusion that a persistent
`thread-store conflict: ... already has an active writer` required operator
release and could legitimately complete with return code 1. The corrected worker
keeps such requests queued and retries them automatically with capped exponential
backoff. It reports `complete` only after Codex processes the request.

Independent end-to-end validations from guarded Coordinator sessions proved the
state contract: `send` exited 0 and returned one queued request ID; adaptive
status checks remained queued with exit 0 for roughly twelve to sixteen minutes;
status then became complete with return code 0; and `receive` exited 0 with a
genuine Support response carrying the Coordinator and broker request identities,
rather than the former conflict transcript. The same test confirmed fail-closed
behavior for unknown IDs, outside-task-root files, and incomplete request JSON.

Therefore Coordinators record and poll the same request ID, check previously
requeued requests before sending replacements, and never infer failure or create
a duplicate from a long queued interval. Requests that failed under the former
worker were requeued during deployment, so an old request ID is checked before a
replacement is sent. Only a terminal non-zero broker result or a state-contract
violation is an escalation.

Operationally, a long `queued` means success in progress: poll adaptively with
capped backoff, continue unrelated board work, and report "queued, still
retrying" rather than "complete" or "stalled". This avoids human escalation
for contention the broker resolves itself.
