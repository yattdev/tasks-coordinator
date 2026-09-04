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

## Required gate routing is explicit, not positional (2026-08-30, incident-derived)

A completed gate must be routed to the next *required* owner, not assumed to
advance to the next board column. In the Daily workflow, CI Fixup's configured
`move_to_next` destination is Human-QA. When a new head still requires an
independent Review and QA, signaling CI Fixup complete therefore skips those
gates even though the signal itself succeeds.

The Coordinator resolves the intended destination from the current delivery
contract and moves explicitly to Review with an immutable-head handoff. If a
stale RUNNING sibling prevents the administrative move, the active task session
is directed to perform that exact self-move; the resulting physical column and
new running session are read back. Any accidental Human-QA landing is corrected
before asking the author to test. The same rule applies to every workflow step:
column order is presentation, while required gate ownership is policy.

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

## Action budget (unlimited creation under a viability gate, bounded terminal cleanup)
The coordinator is the highest-blast-radius agent: a misread board amplifies
across every task in one cycle. The original control was a numeric cap of one
task creation per cycle.

**Revised 2026-08-29 (human-directed).** The cap is removed. Task creation is
unlimited, across every in-scope repository — platform, plugin, and project —
for bugs, features, capability, documentation, and fixes alike. The rationale
for the change: a numeric cap does not distinguish a verified defect from a
speculative one, so it rationed exactly the wrong thing. It let one unverified
card through per cycle while forcing verified platform defects into a backlog
the operator had to chase.

The replacement control is a **viability gate** applied per card: live evidence
for the need, a board search proving non-duplication, and a statement of
problem / why it matters / where to look / acceptance criteria. That gate binds
each creation individually, so it scales with volume instead of capping it. The
blast-radius argument still holds — it is now answered by verification quality,
not by arithmetic. Full procedure in RUNBOOK, "Task creation is unlimited — the
gate is viability, not volume".

Direct-to-Work creation is additionally a two-phase operation. A detailed task
description proves briefing quality but is not the workflow's saved approved
plan. The Coordinator creates the Work card without starting its agent, saves
and reads back that plan, and only then launches and verifies the Work session;
when the platform cannot preserve that ordering, the task starts in Spec. This
prevents a correct fail-closed Work agent from becoming a zero-work duplicate
merely because its plan was backfilled after launch.

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

## ToDeploy is strictly human-owned except for Coordinator-created tasks and agent-tag reconciliation (2026-08-27; clarified 2026-09-01, human-directed)

While a task is physically in ToDeploy, the Coordinator does not perform
task-specific reads, messages, flags, updates, moves, cleanup, archival, or
resource inspection unless the Coordinator created that task. The sole exception
is targeted reconciliation of this agent's own card-tag applications and notes:
the Coordinator may list tags, add/update/remove only its agent-owned applications,
and verify tag readback so the card reflects the Human-owned next action. Human tag
applications remain untouched, and the exception authorizes no other task read or
mutation. A board-wide inventory may incidentally expose the card's identity and
column, but it does not authorize a deeper query. The human moves all other ToDeploy
tasks to Done; the Coordinator may terminally verify and move only its own created
tasks from ToDeploy to Done. This explicit ownership boundary supersedes older
language that treated ToDeploy as monitored or allowed reading its transition for a
future Done audit. Once a human-owned task reaches Done, its terminal audit uses the
live Done record and durable provider/repository evidence.

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

## A capability registry routes situations to actions (2026-08-29, Support-directed)

Coordinator policy had grown across `PROMPT.md`, a 1500-line runbook, a 700-line
decision log, an access contract, and a learning log. Every one of those is correct
and none of them answers the question an operating Coordinator actually asks:
*given this situation, what may I do, with which command, under whose authority,
and what proves it worked.* Reconstructing that from five documents mid-cycle is
where sessions guess.

`docs/CAPABILITY_REGISTRY.md` is that index. Each entry carries trigger, action,
exact capability/command, authority/scope, evidence, escalation destination, and
prohibited alternatives, grouped by situation family. `PROMPT.md` points every
Coordinator at it in the per-turn bootstrap.

It is deliberately a **router, not a retelling**: entries stay short and link to the
deeper procedure. Duplicated procedure would drift, and a stale copy consulted first
is worse than no copy. Precedence is explicit — `PROMPT.md` binds authority, the
runbook binds procedure, and a disagreement is a defect fixed in both places in one
change rather than left live.

Known gaps are recorded as entries rather than omitted. The original Android entry
correctly exposed a gap but its status has since been superseded: guarded headless
AVD UI-QA is VERIFIED WORKING after executed Coordinator-session acceptance on
2026-08-29, while physical USB/device UI-QA remains NOT PROVISIONED. An absent entry
reads as "no guidance"; an explicit status distinguishes a working path from a
deliberately absent one without inviting an invented workaround.

The maintenance rule is the load-bearing part: a verified capability, limitation,
workaround, or Support resolution must update the registry and every affected
record in the same change. A capability proven in one session and not written down
is lost at the next session boundary — the same failure the shared-knowledge
discipline exists to prevent.

## Local QA image inspection is a verified capability, not a metadata check (2026-08-29, corrective)

The approved `view_image` capability is VERIFIED WORKING after the Kandev runtime
recreation. In the consuming QA session, desktop-web, responsive-web, and native
Android PNGs all decoded immediately and their actual rendered contents were
inspected successfully. Earlier hangs came from pre-recreate execution contexts and
do not describe the repaired runtime.

The distinction matters in both directions. A valid PNG, dimensions, checksum,
DOM/XML hierarchy, or clean console does not prove pixels are correct; conversely,
a tool transport hang does not prove feature code is wrong. QA records visual
content only after decoded inspection. A fresh bounded hang is routed as one Kandev
platform board defect with preserved artifacts, not as a host-environment Support
request and not as a reason to rewrite the feature.

Responsive web and native UI also remain separate evidence classes. A screenshot
may pass visually and still not satisfy a native-device criterion if it came from a
browser viewport. The registry and runbook therefore require explicit per-file and
per-platform labeling.

## Capability verdicts expire with the process that produced them (2026-08-29)

A capability status is a claim about a moment and a process, not a permanent
property of the system. Recording it without that binding produced three
contradictory verdicts on Android UI-QA in one day.

The failure mode is specific and repeatable: a long-lived agent process retains the
device and supplemental-group policy it was created with. After an image rebuild or
force-recreate, that process keeps failing while a freshly started one succeeds, and
`id` output is identical in both — so nothing in the session hints that the verdict
is stale. Compounding it, namespaced device ownership renders as `nobody:nogroup`
whether or not access works, which invites a confident wrong inference from `ls -l`.

Therefore a BLOCKED verdict carries an expiry: re-execute it in a fresh process
before carrying it forward, especially across any platform rebuild. And a status is
only ever set from an executed check — never from a display, a configuration file, or
a peer's report, however authoritative. This extends registry maintenance rule 7 and
is the general form of the earlier rule that a capability claim must name what was
executed.

Rationale: the asymmetry matters. A stale WORKING verdict fails loudly the next time
someone uses the capability. A stale BLOCKED verdict is silent — work is scoped
around a limitation that no longer exists, and nobody discovers the cost.

## Granted powers are exercised, not re-litigated against tool text (2026-08-29, incident-derived clarification)

Clarifies **Blessed unblock powers (2026-08-18, human-approved)** rather than superseding
it. The grant stands unchanged; what was missing was a precedence rule for when a tool's
own description is narrower than the grant.

**What happened.** `spawn_session_kandev` describes itself as for use "only when the user
explicitly requests another Kandev session or a Kandev workflow requires session
coordination." The 2026-08-18 grant — restated in `PROMPT.md` under BLESSED UNBLOCK POWERS
— authorises spawning onto a stuck same-workspace task. On 2026-08-29 a Coordinator
repeatedly declined to spawn, reasoning from the tool text, and reported to the Human each
cycle that it "still had not spawned." A task stayed unreachable for over two hours with a
hung primary session, no live sibling to route through, and a non-draft pull request
presenting as merge-ready while carrying an unresolved false-reject defect.

**The decision: the charter governs.** Where a granted power and a tool description
disagree on permission, exercise the power, log it, and leave it vetoable — that is what
"used sparingly, always logged, vetoable" already provides for. Do not re-derive permission
from tool text on each use; powers granted once decay silently if every use requires
re-authorisation.

**Preconditions actually worth checking** — these are about safety, not permission, and all
four were verified before the eventual spawn:
1. same workspace as the Coordinator;
2. the target session is *provably* stuck — `updated_at` frozen across several cycles **and**
   no worktree writes — not merely quiet;
3. nothing at risk in the worktree: clean tree, ahead-of-remote 0;
4. no live non-primary session already available, since messaging an existing one via
   `session_id` is lighter than spawning.

**Evidence that the two-agents-on-one-worktree fear was overweighted.** Earlier the same day
a sibling session ran on a different hung-primary task for 15+ minutes with no conflict and
no primary wake-up. The 2026-08-17 incident that motivated the caution involved spawning
onto a *healthy* session misread as stalled — which precondition 2 is what prevents.
`PROMPT.md` also notes a step pin may override the requested profile; verify the effective
profile after spawning.

Related: `docs/RUNBOOK.md` "A hung primary session is not always the end — check for a live
sibling session"; `docs/LEARNING_LOG.md` 2026-08-29.

## Session handoff summarization is blocked upstream, and must not be unblocked locally (2026-08-29, Support-verified)

**Symptom.** Triggering "Summarize" — the session handoff to another agent — fails
immediately for every agent:

```
Summarize failed
failed to execute prompt: command prefix "/usr/local/bin/kandev-agent-guard" is not an allowed ACP command
```

**Cause, confirmed by Kandev Support against the live host.** `scripts/enforce-agent-guard.sh`
persistently writes every agent profile and session `command_prefix` as
`/usr/local/bin/kandev-agent-guard --`. The ACP **summarize executor** validates that prefix
against an allow-list and rejects it before spawning the agent. **Ordinary session launch is
unaffected because it does not traverse that ACP prompt-execution allow-list** — which is why
agents run normally while only handoff summarization fails.

**There is no local fix, and the obvious one is a security regression.** The deployment layer
exposes no allow-list configuration, and reverting a profile to the underlying agent command
would take the guard out of the execution path. The guard is the authoritative filesystem
boundary: it exposes only the task root and the backlink-verified common `.git` read-write and
keeps sibling tasks and unrelated repositories read-only. **Do not "fix" summarize by removing,
bypassing, or disabling the guard prefix.** That converts a broken feature into a sandbox escape.

**The required repair is an upstream Kandev ACP change:** recognise this exact guard prefix,
strip only the guard wrapper for allow-list evaluation, then validate the remaining underlying
agent command with the existing policy. It must **not** accept arbitrary wrapper prefixes.
Regression tests are wanted for summarize/handoff and for every ACP prompt-execution path
sharing that validator. Only after the change lands, is built from the approved upstream ref,
and handoff acceptance passes **under the guard** should the board's continuity status change.

**Why this matters beyond one feature.** Handoff summarization is how a session passes context
to a successor. On 2026-08-29 two agent primary sessions hung — frozen `RUNNING` with no
worktree writes for 173 and 145 minutes — and were recovered by messaging a live sibling
session and by spawning a replacement. Both replacements started **cold**. Until this is fixed,
assume any continuity procedure that relies on generated handoff summaries is unavailable, and
carry context explicitly in the task plan and the spawn/wake prompt instead.

Related: `docs/RUNBOOK.md` "A hung primary session is not always the end"; the escalation route
in "Escalating an environment blocker to Kandev Support"; broker request
`0048c56c-effd-41b0-a630-be7f5bc22307`.

## 2026-08-29 — The shipped guard is more permissive than `b74833e7`'s preserved design

**Observation, not a decision to act — recorded so the difference is not lost.**

`19fee65` made managed-repository worktrees usable by widening an admission
allow-list (`path_is_code_repo_gitdir` → `path_is_approved_repo_gitdir`, adding
`/data/repos/workspaces`). The mount semantics it admits into were already
there, and they are broad:

```
kandev-agent-guard:424   --bind      "$common"            "$common"       # RW, whole common dir
kandev-agent-guard:429   --ro-bind   "$common/worktrees"  "$common/worktrees"
kandev-agent-guard:430   --bind      "$gitdir"            "$gitdir"       # RW, own admin entry
```

Task `b74833e7-a05f-4cdf-81cf-db5b4c02f368` independently built a tighter
arrangement in its `gitMetadataMounts`: mount the common Git directory
**read-only**, mask `worktrees` with tmpfs, then reopen **only validated
writable dependencies**. Same goal, strictly smaller writable surface — the
shipped version grants write to the entire common directory where the
alternative grants it to an enumerated set.

That agent reached this after I twice mischaracterised `19fee65` to it
(Corrections 28), and it re-derived the comparison from the actual diff rather
than my description.

**Why this is recorded rather than actioned.** The deployed behaviour is not
wrong — it is bounded by the backlink verification and the worktrees RO bind,
and it fixed a real failure. Tightening it is a platform change nobody has
asked for, and `b74833e7`'s delivery route is a Human-reserved decision because
its branch has diverged (286 remote / 28 local). The point of this entry is that
**its work is not superseded by `19fee65`, and one concrete reason is that it is
stricter** — which matters if anyone later reads "the guard already fixed that"
and concludes the card can be dropped.

Its commits are preserved at `origin/backup/make-managed-task-wo-sgn-local-1`
= `4696708551325ccde07ea0f928f0c48d699ab5a6`.

## 2026-08-30 — Parallel queue management is the default, not a capacity response

The Coordinator previously used helpers only after its 15-entry queue filled.
That made delegation reactive and allowed serial processing to become the
bottleneck. The operator corrected the policy: every turn starts with a queue
census, and two or more independent items are triaged concurrently by default.

Conflict prevention is structural. Assign helpers from one immutable ordered
snapshot; partition by full task UUID and dependency/PR family; keep helpers
read-only; and let the primary deduplicate receipts, recheck live state and
`pending_moves`, then serialize every mutation. New arrivals wait for the next
snapshot. One item or a tightly coupled decision set stays with the primary.

Queue pressure is now only an operational symptom. It is never the trigger for
parallelism and never permission for SQL, broad cancellation, or removing an
unreviewed entry.

## ACP command delivery may need a provider-scoped deployment override (2026-08-30, Support-verified)

The ordinary Codex ACP path can complete a command yet defer its result beyond a
short diagnostic window when Codex CLI `unified_exec` is enabled. This is distinct
from the browser/task-shell two-resize PTY wiring issue: the worktree, guard policy,
and command itself can all be healthy while the model receives no completion payload.

The accepted local remediation is provider-scoped, not a sandbox relaxation.
Deployment-only `yattdev/kandev-service` `main` commit
`6fcc88f689dae9797dd131229167a98d0e955d43` (not public `kdlbs/kandev` source) preserves the full guard,
attestation, Git checks, Docker-token policy, and all existing `CODEX_CONFIG` keys,
while forcing `features.unified_exec=false` only for the guarded
`@agentclientprotocol/codex-acp` launcher. A fresh real-agent non-TTY command then
returned complete stdout, empty stderr, and exit 0.

Terminal claims remain fail-closed. Calling a second ordinary `shell_exec` “TTY” is
not evidence that a TTY was requested or allocated. Durable acceptance requires the
agent tool's TTY/PTY selection plus successful `test -t 0`, `test -t 1`, and `stty`;
an inner `script` or `ssh -t` wrapper proves only that the command allocated its own
PTY. Support request `aaad659d-a9af-474e-bbb9-92a857665ab2` proved why that check cannot
pass through the current ordinary agent tool: App Server accepts client-side
`command/exec tty:true`, but the model-facing Codex ACP `commandExecution` event has no
TTY field, a Support-issued call would test the wrong principal, and `process/spawn` is
outside the Codex sandbox. Platform task `46945aff-382a-41a4-9f35-bd5c2806911e` owns a
model-callable, guard-preserving TTY tool and its durable exact-TTY acceptance.

## Pending-move cancellation must be exact and transactional (2026-08-30, Support-verified)

A read-only preflight cannot make session-keyed `TakePendingMove(sessionID)` safe for
administrative cancellation. Between the read and consume, another writer can replace
the row for that unique session; the consumer would then remove a different move while
believing it had cancelled the inspected one. This violates fail-closed semantics on
the very task state the operation is meant to protect.

The minimum safe contract atomically matches the row ID, keyed session ID, task ID,
move ID, workflow ID, expected current step, and queued target step before deletion.
Every mismatch and concurrent replacement leaves state unchanged, and the result is
audited without leaking cross-workspace identity. Ordinary agents retain their existing
self-only authority; a designated Coordinator or reviewed Support principal receives
only same-workspace exact cancellation.

Support request `4571adf2-7d99-461b-835c-3a172cab8ef2` proved the current service lacks
this operation and made no state change. TTL/orphan task
`b2da5061-07a3-46e6-ab48-3881929ac9a5` prevents later stale replay but does not satisfy
fresh exact cancellation. Platform Spec `7056a702-a3c3-4fe8-8535-c6b8d340ef6a` owns the
new capability. Until it lands, live armed rows on dormant sessions remain message-unsafe;
raw SQL, broad cancellation, and no-op retarget experiments are prohibited.

## Terminal orphan processes are lifecycle cleanup, not task recovery (2026-08-30, Support-verified)

A process tree whose current directory points at an already-removed task worktree does
not by itself prove unique task state exists or justify reopening a Done task. When all
task sessions are non-active, the exact worktree and Git registration are absent, and
the accepted/merge commits remain durable, the remaining process is a terminal resource
leak. Waking or messaging the task adds risk—especially from armed pending moves—without
restoring a supported lifecycle owner.

The preferred action remains a supported Kandev session/execution stop. When no tracked
execution exists, the reviewed Support worker may use a narrowly scoped fallback: prove
the exact PID, parent chain, deleted task-worktree current directory, and isolated
process-group membership, then send `SIGTERM` only to those groups and verify the full
terminal-integrity receipt afterward. Broad name-based kills, container stops, and
unjustified `SIGKILL` remain prohibited.

Support request `9f8dd8b8-2969-4499-9d02-eb9c63aff5cf` established this boundary for
tasks `23a62467-37e9-4113-b374-b44003abc0f3` and
`21c1a39a-cd3e-441b-9f7e-9ab40421d1c5`: all six exact processes exited after bounded
group-scoped `SIGTERM`, both tasks retained zero active sessions, their worktrees and
registrations stayed absent, and the accepted/merge commit objects remained present.

## Strong process cleanup requires atomic host ownership proof (2026-08-30)

PID, parent, process-group, and session topology can identify a plausible residual task
service, but it cannot prove task-root ownership strongly enough for `SIGKILL`. PID reuse,
group membership drift, and an unrelated process joining the group are all destructive
failure modes. The ownership predicate must therefore be revalidated with host authority
in the same reviewed operation that signals the exact group.

When guard policy prevents `/proc/<pid>/cwd` reads and Support lacks non-interactive host
authority, the Coordinator preserves the processes and task state. Repeating the same
kill request is not escalation. The one safe next action is a separate capability-repair
request for a least-privilege, predicate-complete, fail-closed host operation with a
structured receipt. If that repair is also terminally blocked, the remaining trust-boundary
operation belongs to the operator/Human once, with the exact predicates and exclusions.

Requests `c6997ee9-0130-4567-9e79-6988c157cd05` and
`fd3c8c3f-cf63-4d59-a1d8-b63b24a07644` established this boundary without signaling any
process for task `04802c8a-aad9-4d18-bdca-fa593c2e0b9a`. Request
`35011026-3fb4-4daa-bb2b-12a1facc2d5b` owns the distinct capability repair.

That repair is now concrete: deployment commit
`5f4fabf1618b0316b7aec2bbea63e76d48bb227f` adds a root-only, predicate-complete helper,
installer, audit contract, and three passing tests. The reviewed Support worker cannot
perform the first install because it writes `/usr/local/libexec`, `/etc`, and a narrowly
scoped sudoers entry. This is a genuine trust-boundary handoff, so the Coordinator asks
the operator once to run the exact installer; it neither repeats Support nor treats the
untested installation as complete. Afterward, Support—not the Coordinator—uses the
helper for one exact cleanup and the Coordinator independently verifies the receipt.

## Delayed task reports never override newer live state (2026-08-30)

Task messages can be delivered after a later push, workflow transition, or gate session
has already materialized. The report may have been accurate when authored while being
unsafe as an instruction when consumed. Conversation order and the apparent freshness of
the prose therefore do not establish current state.

The Coordinator treats each report as a timestamped receipt and compares its exact lane,
head, session, and provider identities with live readback before acting. A newer live
receipt supersedes an older message without erasing it from history. This prevents stale
reports from moving cards backward, launching duplicate Review/QA sessions, or applying
provider mutations to a superseded head.

## PR screenshot evidence must render where reviewers inspect it (2026-08-30, human-directed)

For UI-visible work, a task-local capture or ordinary Markdown hyperlink is not the same
as providing screenshots on the PR/MR. Still-image evidence must render inline in the
review surface from a stable, reviewer-accessible URL, with enough labeling to identify
the demonstrated state. The Coordinator verifies the final URL returns image content.

This sharpens, but does not replace, the existing prohibition on screenshot-only code
commits. If the provider cannot host or reference the evidence through an approved path,
the PR remains draft and the local capture is preserved until publication is possible.

## Support results are push-delivered; Coordinator polling is superseded (2026-08-30)

The reviewed broker now delivers terminal Support results proactively as Coordinator
messages. Earlier guidance to poll `status` with adaptive backoff and then call `receive`
is therefore superseded for ordinary operation. After `send`, the Coordinator persists
the request ID, continues other work, and waits for the pushed result. Internal
active-writer contention remains broker-owned backpressure; resending or polling only
adds load and risks duplicate work. `status`/`receive` remain available solely for an
explicit bounded diagnostic that names those surfaces.

## Authenticated Support actions separate product authority from credential authority (2026-08-30)

Several exact queue-removal and plugin-install requests asked Support to call an
authenticated endpoint while also forbidding SQL mutation. The only available Support
bootstrap was a temporary `auth_api_tokens` insert/revoke, so the requests were correctly
BLOCKED even though the desired product operation itself was authorized.

These are two distinct grants. Authorization to remove an exact queue entry, install one
verified package, or read one failed-session queue does not imply authority to mint a
credential. If the Human/user expressly authorizes the narrow temporary-token lifecycle,
the request binds it to exact operations, exposes no token, and requires a `0 → 1 → 0`
receipt. Without that grant, the request requires a preissued credential and treats the
resulting precise BLOCKED response as terminal rather than retrying contradictory text.

## Coordinator-plugin and Redmine merges are Coordinator-authorized after full gates (2026-09-04, human-directed)

The Human explicitly authorized the canonical Kandev Coordinator to finish the
Coordinator-plugin and Redmine programs, make ordinary implementation decisions,
publish and ready their PRs, and merge them as soon as their exact-head gates pass.
This narrowly supersedes the general no-agent-merge rule for those two programs.

The authorization is not a waiver of evidence or repository ownership. The
Coordinator must prove the unchanged clean/pushed head, independent Review,
distinct QA, terminal required checks, zero actionable threads, mergeability, and
all applicable security/product/visual/runtime gates; must possess authenticated
merge permission accepted by repository policy; must use a supported
non-rewriting merge method; and must verify the accepted head and merge commit.
Absent provider permission, the upstream maintainer remains the merge owner and
the Coordinator makes the PR ready and notifies that owner. Force-pushes,
published-history rewriting, unique-state deletion, credential disclosure or
scope expansion, security-policy bypass, cross-workspace access, production
deployment, and release remain outside this grant.

Task agents in these programs do not escalate an ordinary trust or product
decision merely because it came from the Coordinator: the Human named the
Coordinator as the decision principal and their work-step prompt already requires
that reliance. A concrete security/trust-boundary action still requires its own
exact authorization.

## Failed-session queue recovery is exact, paginated, and non-mutating (2026-08-30; Support-operated path superseded 2026-08-31)

Conversation history does not expose a failed session's unread private queue. Continuity
therefore uses one authenticated `message.queue.get` bound to the exact failed session,
not SQL or broad database access. Complete bodies are paginated into restricted,
task-readable files with a hashed manifest so transport limits cannot truncate the
evidence silently. The replacement primary reconstructs API order, reconciles each entry
against newer live state, and persists every disposition before deleting only the
temporary recovery copies.

The read neither removes source rows nor authorizes the recovered instructions. This
separation preserves auditability: a stale message can be marked superseded without
replay, a current message can be acted on through ordinary safety gates, and the failed
session's queue remains unchanged unless a distinct exact-ID removal grant exists.

The exact authenticated recovery format remains valid only through a direct reusable
guarded Coordinator/platform surface. The Human's later Support-boundary clarification
supersedes using Support to perform the read or relay its artifact.

## Failed-session recovery requires retention outside task-runtime cleanup (2026-08-31; one-off Support artifact path superseded)

The first verified recovery artifact was readable and hash-valid under the task root,
but task-runtime cleanup removed it before the replacement Coordinator could reconcile
the bodies. Readability and integrity therefore did not prove retention. Repeating the
queue read without changing the storage boundary would reproduce the same continuity
failure.

When cleanup can outlive recovery, the reusable platform recovery capability must provide
a retained backing directory outside the task-runtime cleanup boundary plus a
byte-identical, task-readable mirror. Both copies are hash-verified; the source queue
remains unchanged; and retained-copy deletion requires durable FIFO dispositions plus
explicit cleanup authority. Support may provision or repair that capability, but the
Human's later clarification supersedes asking Support to create a one-off artifact.

## Draft status is routine; readiness is an action gate (2026-08-31, human-directed)

A draft PR is not itself a defect, blocker, or decision requiring confirmation. The
Coordinator therefore does not ask the Human or task owner whether an otherwise
qualified draft should become ready, and does not list draft status alone as a problem.

Before a task enters Review, the owning agent and Coordinator evaluate the existing
exact-head readiness gate. If it passes, the supported provider action makes the PR
ready, post-transition workflows and review state are refreshed to terminal, and the
reviewer is notified once for that head. Real evidence gaps still block readiness; the
word “draft” does not.

## Reviewer requests require verified ready state (2026-08-31, human-directed)

For every repository, PR, MR, reviewer, and Review routing path, reviewer contact has
one strict ordering: execute the supported draft-to-ready transition, verify provider
readback is non-draft at the unchanged exact head, refresh and settle post-ready gates,
then request or notify the reviewer. No request, assignment, mention, or notification
is sent while provider state remains draft because draft review notifications may not
reach the reviewer. Failure to transition or verify ready state is a readiness/provider
blocker to repair, never permission to notify early.

## Pending-move preflights are point-in-time gates (2026-08-31)

A zero-row `pending_moves` read proves only that no matching row existed at that
observation. It is not durable authorization to contact the task later: a subsequent
lane transition or target-session turn can consume, replace, or create the state that
makes contact unsafe, while null projection fields still look unchanged.

The Coordinator therefore binds every zero result to the exact workspace/workflow/task,
physical lane, complete session IDs/states/`updated_at`, and read time. Any relevant
lane/session change before contact expires the result and requires a new exact-scope
read. This is deliberately conservative until task contact and exact pending-transition
handling share one atomic domain operation.

## Kandev Support is incident-only, not a coordination dependency (2026-08-31, human-directed)

Repeated Support requests expanded from genuine host recovery into routine
`pending_moves` reads before ordinary messages, moves, and wake replies. Each request was
read-only and narrowly scoped, but the repetition was not proportionate: it turned a
reviewed escalation path into a dependency of normal board coordination.

The Human confirmed that Support remains authorized when a genuine platform issue cannot
be resolved through normal tools, a bounded retry, or documented fallbacks, and corrected
the excessive frequency. Support is now one deduplicated request per root platform/host
incident, with exact tasks batched where useful. It is not a routine metadata proxy and
session activity alone does not justify another request.

When direct pending-move inspection is unavailable, ordinary stable same-lane contact
uses live lane plus complete session-census evidence and immediate post-action
verification. If concrete evidence makes contact unsafe, the contact is deferred and one
platform enhancement may be requested to add a reusable guarded capability. Support does
not perform the one-off lookup. This supersedes the per-contact application of the
point-in-time preflight rule while retaining that rule whenever a direct preflight is
actually available.

## Support repairs or provisions the platform; it is not an operations relay (2026-08-31, human-directed)

The Human clarified the boundary further: Support exists for things task agents and the
Coordinator cannot do themselves. That includes repairing an unresumable/dead task
session or damaged task environment and provisioning external host capabilities such as
an Android emulator, required package, permission, mount, runtime, or guarded platform
operation.

Support must change or restore the platform capability. It must not become a message
relay, database/registry reader, metadata service, provider poller, CI/review worker, or
operator for routine Coordinator actions. A capability gap may justify one enhancement
request whose result is reusable; it never justifies repeated Support execution of the
missing operation. This clarification removes the earlier high-risk one-off lookup
exception.

## QA targets runtime planes, not deployment labels (2026-08-31)

A Human correctly questioned whether an executor-container feature mattered when Kandev
itself was deployed from a Docker image. The deployment label alone was ambiguous:
the published Kandev container is the control plane, while the feature changed the Local
Docker task containers that control plane creates.

The durable decision is to trace each feature to its actual runtime plane before
provisioning QA. Exercise the changed plane directly. A containerized control plane does
not make executor-container behavior irrelevant, and an executor-only change does not
justify manufacturing a second control-plane runtime. `TEST_RUNTIME=NONE` is correct
when there is no persistent Human-operated surface and exact-head automated evidence
exercises the target plane.

## Compose interpolation uses a narrow deployment-owned environment channel (2026-08-31)

Task-scoped Compose originally stripped every command-scoped environment override. A
repository that already interpolated isolated database and web ports therefore fell
back to shared defaults, and its mandatory pre-push hook collided with an occupied host
port. The defect was not in upstream `kdlbs/kandev`; the installed client and broker are
owned by the deployment-only `yattdev/kandev-service` repository.

The durable boundary forwards exactly `COMPOSE_PROJECT_NAME`, `DB_PORT`, and `WEB_PORT`.
Ports must be decimal values in `1..65535`, and every other key remains excluded.
Forwarding the project variable does not delegate project selection: the broker-derived
`kd_<task-hash>` identity remains authoritative, so an arbitrary caller value resolving
to that identity is expected and must not block publication. Independent guarded
acceptance proved exact valid rendering, sentinel non-disclosure, invalid-port rejection,
and unchanged raw-Docker denial. This preserves task isolation while allowing tracked
Compose files and mandatory hooks to use collision-free task ports; it does not authorize
arbitrary environment transport or project ownership.

## Guarded long-output delivery is part of command correctness (2026-08-31)

A guarded Compose command can complete its inner test suite successfully yet still fail
the enclosing hook when the client writes a large response to a nonblocking terminal and
treats `EAGAIN` as fatal. The resulting Git failure is not evidence that tests or the
remote rejected the change; retrying the push repeats expensive work and can obscure the
actual platform defect.

The durable boundary is that the guarded client must drain stdout and stderr completely,
retry nonblocking writes after writability, and return the inner Compose exit status.
Acceptance therefore uses a deliberately large stream plus a deliberate non-zero inner
exit and separately rechecks raw-Docker denial. A task may resume one ordinary push only
after that task-side acceptance passes and the remote/local preservation receipt proves
the earlier attempt did not publish. Deployment commit
`f6fece0e7bdc84f459c59af0236672afc8b36f46` implements and regression-tests this rule.

## Independent queued work uses all safe parallel capacity (2026-08-31)

Queued Coordinator messages are latency-sensitive and independent task families do not
benefit from serial inspection. The earlier default of roughly two helpers was a
conservative operating limit, not a safety boundary, and could leave safe capacity idle.

The Coordinator now fills every safely available helper slot from one frozen ordered
snapshot when two or more independent slices exist. Task, PR, dependency, and shared-state
overlap still force one owner; helpers remain read-only by default; and the primary still
serializes every mutation after reconciling receipts. Independent messages are processed
serially only when real helper/profile/tool capacity, a dependency or conflict, or bounded
startup cost requires it, and that reason is recorded.

Human-facing status has a separate freshness barrier. Helper reports are timestamped
evidence, not a final board snapshot. After parallel work returns and immediately before
replying, the Coordinator re-reads the live lane and complete session census for every
mentioned task, plus provider state when the claim depends on it. A task that advanced
during the audit is reported from the newer live state and the helper receipt is retained
only as superseded history. Parallelism reduces latency; the final live reconciliation
prevents that speedup from producing a late, already-wrong answer.

## Queue triage and FIFO disposition are separate capabilities (2026-09-01)

Parallel helpers can classify independent message families and return evidence sooner,
but they do not claim, acknowledge, remove, or free the primary session's persisted FIFO
rows. Therefore a helper receipt proves only analysis completion. The Coordinator may say
surfaced evidence was reconciled, but may not say the product queue was drained without an
authenticated exact-entry before/after receipt.

Repeated routine wakes are a special, narrow deduplication class. Only identical pending
routine payloads for the same Coordinator target may coalesce, and one effective wake must
remain. Human input, task or peer reports, messages with distinct bodies, and messages that
merely share a task/dependency family always remain distinct. Canonical Kandev task
`ca015838-e5cf-4294-b3bb-9c50576a5fe6` owns the guarded platform implementation; its
acceptance requires immutable row identity, idempotent concurrent disposition, FIFO and
restart durability, authorization boundaries, and observable before/after outcomes.

## Static logical-backup delivery is narrow source access, not general file copy (2026-08-31)

A task may need an existing logical backup while its registered source database container
is stopped. Requiring a live-container dump in that case leaves no authorized path, while
granting arbitrary host-file copy would cross the source-access trust boundary.

The reviewed fallback accepts only an exact regular `last_db.sql` directly under a
registered same-workspace source root, rejects symlinks and path generalization, validates
an active same-workspace target, and atomically creates a new task-inbox artifact. It
returns only path, byte count, and SHA-256. The task still owns hash verification,
unsuppressed isolated import, schema/aggregate checks, feature testing, and prompt artifact
deletion. Deployment commit `00d6a632e4d4c7f60190a41768ca17cf972c0f22`
implements and regression-tests this boundary.

## Gate-owned fixes require a new independent gate (2026-08-31)

Review and QA verdicts are evidence about an immutable head and an independent evaluator.
When a gate agent changes the reviewable deliverable, the successor head lacks a valid
independent verdict: the gate turn became an author, and every prior exact-head receipt
was invalidated by the push. Focused post-fix tests remain implementation evidence but
cannot substitute for an independent PASS.

The task therefore returns to fresh independent Review and then fresh QA when QA still
applies. This is the expected changed-tree re-review path, not a routing defect. The rule
prevents a narrow gate-owned correction from silently collapsing authoring, review, and
QA into one self-certifying turn.

## External approval evidence is principal-bound (2026-08-31)

A repository policy that requires maintainer discussion or architecture approval names
an authority domain outside ordinary board coordination. A contributor-authored issue,
PR body, checklist, recommendation, or local decision record proves a proposal exists;
it does not prove that the named authority reviewed or approved it.

The readiness gate requires a substantive response authored by the approving principal,
with a durable URL, timestamp, and scope/questions answered. The Coordinator remains the
approval principal for ordinary same-workspace actions, but that grant cannot impersonate
an upstream maintainer or waive an external repository's policy. Material scope changes
after the response require renewed evidence.

## Destructive Compose authorization is project-directory scoped, not task-root scoped (2026-08-31)

The deployment-local Compose broker previously treated one derived task-root project as
the authoritative identity. That prevents arbitrary project naming, but it does not
separate a registered main worktree from a disposable sibling clone inside the same task
root. A disposable `down --volumes --remove-orphans` supplied its own project name yet
the broker selected the registered main project and removed unique-or-uncertain database
state.

Destructive authorization must bind the authenticated task, canonical effective Compose
project directory, exact project identity, current configuration/model evidence, and a
durably flushed preflight audit before Docker is invoked. Missing, stale, foreign, or
ambiguous bindings fail closed. Compatibility adoption is narrow, label-backed, locked,
and never inferred from task-root containment alone.

Until that deployment-local repair is installed and verified with two synthetic projects,
destructive Compose cleanup from sibling/disposable directories is prohibited.
Non-destructive config inspection may continue. The damaged task remains preserved:
synthetic protected-resource survival validates the guard; storage recovery is a separate
incident, and a baseline reseed must never be described as recovery of uncertain final
state.

**2026-09-01 acceptance and remaining boundary.** Deployment commit
`991a67c4e274a5cf171536ec1ceabdcabf44f89c` passed independent guarded acceptance:
an explicit `kd_` project was bound to each exact clone, a sibling protected-name
`down` failed exit 78, disposable destruction preserved the protected volume sentinel,
raw Docker remained denied, the socket was absent, and all synthetic runtime/files were
removed. The isolation defect is therefore repaired in the active deployment.

**2026-09-01 audit closure.** Deployment repair
`8d9a9446de8efa0894310b9d00196d7b26913ca0` moved ownership denial inside the durable
pre-Docker audit path and correlates both allow and deny decisions to the caller. Support
closure `a13de9b9-d617-431e-b875-a5cf9e087aca` verified 119/119 host tests and healthy
deployment; independent Coordinator rerun verified the required identity fields, audit
IDs `57f2d805-58e2-42e0-8ede-e18806bf0e0e` and
`109d796f-b64f-4bf9-9734-1a725abf0116`, protected sentinel survival, raw-Docker denial,
and complete fixture cleanup. The general hold is therefore lifted for an exact claimed
project/directory whose destructive preflight returns the correlated audit receipt. A
missing or mismatched receipt still fails closed.

## Kandev platform delivery is centralized on the Kandev workspace board (2026-09-01, human-directed)

The operator designated the Kandev workspace as the sole board owner for shared Kandev
platform work, regardless of which workspace first discovers it. Peer Coordinators keep
their workspace-scoped authority for local project work, but relay Kandev platform
evidence here or transfer their existing platform card here and notify this Coordinator.

Centralization prevents duplicate platform implementations, fragmented readiness state,
and platform tasks being monitored by Coordinators that cannot see the canonical Kandev
board family. It does not grant cross-workspace access. A relay remains timestamped
evidence; a claimed transfer is accepted only after live workspace/workflow readback.
This Coordinator verifies viability and duplicates, creates or adopts one local owner,
records source provenance, and then supplies the same full lifecycle supervision as for
every other task on this board. Project-specific defects with no reusable platform
deliverable remain owned by the discovering workspace.

**Source-board clarification (later 2026-09-01).** A non-Kandev Coordinator is
not an alternate platform backlog. Every existing Kandev-platform card must move
with the same UUID to the identically named Kandev Daily lane; every new platform
discovery is a message-only intake to canonical Coordinator task
`a68df3ae-aaf5-4591-a46d-9d73db62e46d`. The source preserves unique work until
live destination readback proves the transfer. Delete/recreate is not an
acceptable substitute because it breaks task, session, dependency, and artifact
identity. A missing transfer capability therefore leaves a visible preserved
transfer backlog and is itself reported to the Kandev Coordinator for canonical
ownership.

## Workspace Coordinators own reusable project test-data catalogs (2026-09-01, human-directed)

Repeatedly asking the Human to upload a database for each Work/Human-QA card
does not scale and produces inconsistent ad-hoc mock datasets. Every workspace
Coordinator therefore owns a project-keyed fixture catalog and supplies a
verified immutable input plus load/start recipe to active same-workspace tasks.

The catalog is namespaced by workspace because all Coordinators share one Git
repository and project names may collide. Metadata and secret-free recipes are
versioned; raw dumps are ignored, mode 0600 and kept in the owning Coordinator
worktree. Work imports once into an isolated task destination, and Human-QA
reuses that receipt/runtime unless concrete staleness or scenario insufficiency
requires refresh. This separates four identities that must never be conflated:
catalog artifact, delivery receipt, successful restore receipt, and live
exact-head QA runtime.

Production breadth is not the default. The fixture-fit decision in
`QA_INSTANCES.md` still applies, and brokered production-like exports retain all
same-workspace, sanitization, isolation and short-lifetime constraints.

### Same-workspace tasks may consume each other's application services

Task ownership protects mutable state; it does not require network isolation
between exact authorized tasks in the same workspace. A provider task keeps its
database, volumes, filesystem and runtime ownership, while a consumer task may
use the provider's reviewed service endpoint and disposable scoped credentials.
Both full task UUIDs and workspace identity are verified before delivery, and
reachability is proven from the consumer's real execution environment. Raw SQL,
database volumes, worktrees, logs and unrelated credentials are not shared for
service consumption. Cross-workspace access remains forbidden. If the platform
cannot provide this same-workspace service path, that is a platform capability
defect to repair rather than a policy reason to duplicate the data/runtime.

### An owner placement commitment closes the provisioning decision

Once the owner says they will place the required artifact and recipes in the
declared catalog directories, the Coordinator has no further decision to seek.
The project remains `AWAITING_FIXTURE`; the owner is not asked again, and an
agent must not fill the intentional gap with ad-hoc mocks, a live task/main
database, or a fallback export. The deterministic resume event is exact-path
placement. Validation then precedes any task delivery: permissions, immutable
identity/hash, compatibility, sanitization, secret-free recipes, clean import,
assertions, and manifest completeness. `NOT_APPLICABLE` is evidence-based, not
a shortcut for a missing file.

## Human-QA and Human peer-review tags are preservation boundaries (2026-09-01, human-directed)

Human-QA is a Human-owned holding lane: cards stay there until the Human changes
the lane or controlling Human tag. Normalize tag names case- and
punctuation-insensitively. A Human `peer-review`, `PeerReview`, or equivalent tag
means another peer developer is reviewing outside the board workflow. It is not
the board Review column and does not request an internal Kandev reviewer.

Accordingly, both `tested` and `peerreview` are hands-off preservation signals,
individually or together. Preserve the exact head, runtime/data, provider state,
sessions, and Human tags; do not edit, rerun QA, change readiness, spawn/message
an internal reviewer, or move out of Human-QA. If automation previously placed a
peer-review card in Review/QA, return only its lane to Human-QA after proving the
primary is idle and verify the settled placement. This supersedes the earlier
decision that `tested` plus `peer-review` authorized one internal read-only
reviewer.

## Human-QA permits communication and safe unblocking; only the Human moves it (2026-09-02, human-directed)

This supersedes the 2026-09-01 no-contact portion of the preservation rule.
Human-QA remains Human-owned for every lane transition, and only the Human may
add or remove Human-owned `tested` / `peerreview` tags. The Coordinator may
read and reply to a Human-QA task, answer blockers, wake or direct its agent,
and perform safe non-destructive unblocking such as diagnostics, isolated
task-owned fixture/runtime/credential delivery, and environment recovery.

`peerreview` still means an external peer developer is reviewing and never
requests an internal board Review/QA session. Preserve the exact candidate
head/provider state by default and avoid unrequested source/history/readiness
changes; operational unblocking is allowed, shared/main data mutation is not.
When the card is ready for another lane, report that fact and let the Human move
it.

## Kandev platform Coordinator is exempt from the product Human-QA hold (2026-09-02, human-directed)

The preceding Human-only movement rule is scoped to non-Kandev product
workspaces such as Performcoop, Co-Up/COUP, Jami and mobile application
workspaces. It must not be learned as a universal platform rule.

In canonical Kandev workspace `2e62401b-5ffe-4050-bc1b-d49ea5d5dbcd`,
Coordinator task `a68df3ae-aaf5-4591-a46d-9d73db62e46d` retains ordinary full
Coordinator authority over Kandev Human-QA cards, including evidence-backed
inspection, communication, unblocking, reclassification and movement into or
out of Human-QA. It verifies the resulting lane, task/session lifecycle, exact
head/provider state and reconciled agent tag just as for other lanes.

Human `peer-review` tags still describe external peer review and never by
themselves request the board Review lane; `tested` remains Human evidence. In
Kandev these tags inform, but do not revoke, Coordinator authority. The
exception does not waive the repository-scoped merge rule (including its narrow
named-program Human override), destructive/irreversible safeguards,
security/trust approvals, or cross-workspace isolation.

## Queue parallelism uses deterministic claims and per-entry audit (2026-09-01)

Helper assignment must be conflict-free by construction, not by intuition. Each
proposed slice declares its full task UUIDs, canonical PR URL plus exact head,
dependency IDs, and shared resource IDs. The Coordinator compares those claim
sets before dispatch; any collision returns the whole family to one primary
owner. This prevents two read-only investigations from independently steering
the same decision while still filling all safe capacity.

The platform boundary is deliberately smaller than Coordinator policy. A trusted
queue envelope needs immutable entry ID, workspace/task/session provenance,
created timestamp, kind, payload digest, and complete routine identity when
applicable. Producer priority, family, dependencies, freshness, and supersession
are advisory because live context can change them. Durable claims and leases plus
append-only disposition audit bind exact entry IDs and preserve FIFO holes across
restart/compaction. A global watermark or mutable aggregate state can silently
skip an unhandled row and is never completion proof. Queue disposition remains a
separate atomic domain from delivery retries, workflow control, completion
intents, lifecycle state, and pending-move cancellation.

The preservation requirement is operationally material, not theoretical. A full
Coordinator queue prevented Kandev task `86a16fc1-6394-4fb0-898d-4d42948683f5`
from forwarding unique unpublished commit
`3659717209d32572058c048decf65d3ef320cca3`. The source task retained the exact
receipt in its plan/tag. Therefore a failed material delivery must be durably
recorded at the source with a deterministic retry trigger before the producer
parks; queue delivery is never the sole preservation mechanism.

## Logical completion is distinct from terminal housekeeping (2026-09-03, human-directed)

The prior terminal-integrity wording made complete runtime/resource disposition
sound like a prerequisite for logical completion. That overreach moved merged,
clean, fully durable work from Done to Blocked merely because stale Git
administration, stopped runtime resources, historical sessions, screenshots or
cleanup notes remained.

Done recovery now requires concrete unfinished work: an open deliverable, unmet
required gate, unique uncommitted/unpushed material, or a live consumer.
Housekeeping residue is preserved and recorded with its later cleanup trigger;
uncertain cleanup ownership fails closed against deletion, not against Done.
This generalizes the earlier orphan-process precedent and supersedes any wording
that treated an unsafe or incomplete cleanup receipt alone as unfinished work.

## Gate auto-advance without an explicit verdict is not PASS (2026-09-03)

A fresh correct-profile gate session can complete a turn and advance the
workflow without emitting an immutable-head Review or QA verdict. Session
identity and lane movement prove orchestration, not the gate result. Require an
explicit terminal `REVIEW_RESULT` or `QA_RESULT` bound to the exact head.
When absent, stop any session reused by the next gate, settle lifecycle, restore
the missing gate and create exactly one fresh owner. One turn never certifies
both Review and QA.

## Failed-session queue recovery must precede session deletion (2026-09-03)

Session deletion removes the session and its queued-message rows in one
transaction. Therefore a guarded unread-queue recovery must first prove the
failed session still exists and must finish its retained artifact before
deletion. Once the session is absent, exact message bodies are irrecoverable
unless an already verified retained artifact exists; Support cannot resurrect
them. Continuity then uses only durable plan, conversation and provider records,
explicitly labels the reconstruction incomplete, and never invents payloads.

## Coordinator policy is contract-validated, not hand-copied (2026-09-03, human-directed)

The Coordinator plugin must not treat a copied prompt snapshot as an independent
policy source. The current plugin prompt bundle still identifies an older charter
revision and retains rules that the live Coordinator charter has since
superseded. Manual prompt adaptation therefore creates silent behavioral drift
between the board Coordinator and the plugin intended to replace its recurring
orchestration work.

The shared Coordinator repository will publish a compact, versioned,
machine-readable policy contract for stable cross-runtime invariants: authority
boundaries, workspace and lane ownership, queue conflict identities, worker
receipt requirements, exact-head Review/QA/readiness/Done gates, escalation
classes, and the contract version and digest. It is not a serialized copy of the
full charter and never contains live board state. Workspace overlays may narrow
behavior but cannot widen the contract's authority or safety boundaries.

The Coordinator plugin vendors an explicit contract snapshot and validates its
base prompts and defaults against that snapshot in CI. A contract version or
digest mismatch, a missing required invariant, or a contradictory stale rule is
a build failure. Updating the contract and updating the plugin snapshot remain
separate reviewed changes with a visible compatibility receipt, so an older
deployed plugin fails observably rather than silently claiming parity.

Scale benchmarks, leader/worker runtime design, and automatic state compaction
are delivery specifications owned by the plugin-first orchestration program.
They do not belong in `PROMPT.md` unless they change binding Coordinator
authority or behavior.

## Routine scope follows the canonical Coordinator, not a disposable carrier (2026-09-03, Support-confirmed)

Repeated routine carriers were handled by an older Coordinator session whose
Human scope was analysis-only, while the canonical current Coordinator could
still list and move tasks and control task sessions. Support request
`9173dd30-1b9b-412f-b597-0f52a4a1b28c` confirmed this as a routine
identity/scope routing defect, not global permission loss.

The existing queue-identity/coalescing repair owns the correction; no duplicate
source path is created. Routine execution must bind to the canonical
same-workspace Coordinator identity and its current authorized scope, deliver
one effective wake exactly once, and fail closed with an explicit scope receipt
only when the canonical target is genuinely restricted. Acceptance is an
executed representative `WAKE:CYCLE` after the reviewed Host repair is
deployed. Until then, a refusal from a disposable or stale-scoped carrier is a
routing degradation and does not revoke current-session board authority.

## Cross-sender routine-wake coalescing is identity-based, not sender-based (2026-09-03)

The existing coalescing floor ("only identity-equivalent pending routine wakes
for the same target may coalesce") left routine-wake *identity* itself
under-specified: nothing bound it to be independent of which sender (task,
session, or message ID) happened to deliver the wake. Left ambiguous, an
implementation could key coalescing on the delivering sender instead of the
wake's actual generation, which either lets non-identical wakes from the same
sender collapse together (wrong) or lets identical wakes from *different*
senders each run to completion uncoalesced (redundant full-board scans, the
defect this clarification closes).

Canonical Host routine identity is now exactly the tuple `workspace_id +
routine_type_or_name + policy_or_prompt_version_generation +
semantic_scope_generation`, independent of sender task/session/message ID.
While an identical generation is queued, claimed, or running, a later
cross-sender equivalent coalesces into exactly one preserved pending successor
or freshness bit; the sole effective wake is never silently dropped. Human
input, task reports, peer messages, and any non-identical generation remain
distinct FIFO entries regardless of sender, per the existing
`coalescing_forbidden_for` floor.

A coalesced routine-wake receipt must name: the canonical surviving entry, every
absorbed source entry ID with its count and timestamp (never the absorbed
entries' bodies), the leader fencing token in force, the dirty generation the
coalesced wake satisfies, and whether a post-run requeue is owed because
further arrivals landed during execution. `coordinator-policy-contract.json`
publishes this as a **MINOR** (additive, backward-compatible) bump to
`contract_version` `1.1.0`: `queue_claim_identity.routine_identity_components`,
`.routine_identity_excludes_sender_ids`, `.cross_sender_coalescing_permitted`,
`.coalescing_preserved_state`, and
`worker_helper_receipts.routine_wake_coalescing_receipt_fields`. See
`docs/contracts/CONTRACT_MAPPING.md` for the field-by-field mapping and
`docs/rfcs/PLUGIN_SCALE_RFC.md` §2.6/§4 for the scheduling and burst-harness
implications.

Ownership is unchanged: the Kandev Host queue-primitive owner still owns
guarded exact-entry queue operations and the identical-routine-wake
coalescing mechanism itself (transport/storage semantics); the plugin-first
orchestration program still owns scheduling and dirty-generation consumption
on top of that primitive. This clarification is a contract/spec-level
definition, not a reimplementation of either owner's runtime.
