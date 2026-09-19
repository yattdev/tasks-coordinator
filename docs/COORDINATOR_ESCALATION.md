# Proactive Coordinator escalation and verified progress

Human-directed policy, 2026-09-19. Applies primarily to this permanent board
Coordinator and also to its reusable plugin implementation. The Coordinator
selects helpers and initiates validated model handoffs without asking the Human
to operate the routing. Kandev Automation remains the sole periodic wake source.
Existing permissions, independent gates and single-primary requirements remain.
The routing rules below are binding operational policy; automated detection is
not claimed implemented until the pilot and real-board adapters pass their tests.

The detailed cycle Definition of Done, health classifier, revisit cadence,
advice-to-action receipt, and anti-loop rule are binding in
[`COORDINATOR_OPERATING_STRATEGY.md`](COORDINATOR_OPERATING_STRATEGY.md).
Use that document to turn this routing policy into a measured operational cycle.

## Judge outcomes, not activity

Maintain three separate records per task and per dependency/recovery cohort:

- Activity: messages, card moves, session starts, plan edits, retries and commits.
- Verified progress: a previously failing required test passes at the relevant
  head; an independent review finding is resolved and verified; an accepted
  evidence-backed investigation milestone completes; a dependency is actually
  satisfied; a blocker is removed and its owner resumes useful work; or required
  delivery gates complete with remote preservation verified.
- Delivery: the task meets its contract and all applicable terminal gates.

A move, push, self-reported success, fresh heartbeat or green unrelated test
does not by itself advance the verified-progress timestamp. Record evidence
identity, head/plan version, verifier and which milestone or blocker it changes.
A head change invalidates affected gate receipts. Reopening the same issue is
a regression; it cannot manufacture another successful recovery. Distinguish
first evidence from eventual delivery, so legitimate long work can demonstrate
progress without pretending the task is complete.

Every active contract needs a next observable outcome, owner, evidence due time,
last verified progress, blocker root and next reassessment. Default first-evidence
deadline is two hours from execution start, tunable before execution for long
tests/builds. A later move/message/plan rewrite never resets elapsed age. Deadline
extensions require an evidence-backed reason recorded separately from progress;
repeated extensions are a strategic exception. Unknown evidence is unknown,
never green. Missing instrumentation cannot justify suppressing a review.

## Routing preflight

Before routine ledger maintenance on every wake, check the current runtime model,
last accepted Astra decision, overdue outcomes, unresolved strategic uncertainty
and failed advice effects. Persist this compact routing record at the front of
the live handoff: model evidence and timestamp; strategic decision ID/time;
cohort progress baseline; consecutive wakes missing required progress; next
outcome/owner/deadline; and pending adviser request/result/effect. Unknown model
or review time cannot justify the Astra-primary exemption or reset the watchdog.
Use fresh response/runtime metadata, not the configured profile or session name;
a model can change while those identities remain unchanged.
On an active board, an unknown last strategic review requires Astra now. A
missing routing receipt forbids a cycle-PASS claim or strategic plan change;
safe execution of existing valid contracts may continue. Use the canonical
G1–G10 gate meanings, not local substitutes for evidence or completion.

Dispatch triggered advice before another unchanged recheck or generic nudge.
Strategic uncertainty triggers Astra immediately. Two successive wakes without
the required progress on an actionable stalled cohort are a backstop, including
incomplete cycles; do not wait three hours or require two fully completed cycles.
The three-hour watchdog is an upper bound on active-board strategic review, not
a minimum delay. Existing equivalent in-flight advice is reconciled, not duplicated.

An implementation owner returning only another plan and becoming idle after an
execution handoff has not delivered its requested outcome. Route the unresolved
technical question to Sol; route priority, ownership, dependency or repeated
ineffectiveness to Astra. A positive claim of external waiting must name the
specific blocked action; continue independent authorized work. Do not turn a
publication or integration gate into a blanket stop on local proof.

Accept advice against current evidence, send the resulting executable action to
its sole owner, verify execution starts, and check the predicted effect at its
deadline. Start/response/decision/effect are separate receipts. A failed effect
returns to Astra without another unchanged cheap-model loop. No-duplicate-ping
rules suppress redundant messages, never escalation or due follow-through.
This is an operational obligation now; unfinished routing automation does not
excuse missed calls. Keep Terra as the normal operator and advisers bounded;
do not interpret the correction as permanent Astra operation.

## When to invoke which model

Evaluate on each incoming automation wake and meaningful event. Thresholds are
initial configurable defaults. Do not wait for the watchdog when a trigger fires.

| Route | Trigger | Why / required output |
| --- | --- | --- |
| Code / Terra | Next action is already specified, evidence is current and no exception exists. | Execute the contract, verify the effect, persist the receipt. |
| Sol immediately | Technical ambiguity, conflicting test evidence, unclear API/schema compatibility, reproducible unexplained failure, or a missed task evidence deadline without a proven external wait. | Diagnose within one task; give a testable next action, evidence to obtain, owner and deadline. No priority or cross-project strategy changes. |
| Sol after bounded operational failure | One attempted operational remediation did not resolve the same blocker, or the worker stops on an obstacle while independent authorized work remains. | Break the local technical loop; do not keep nudging the same worker with the same instructions. |
| Astra immediately | PLAN_INVALID; cross-task conflict; dependency cycle/change that affects execution; contradictory/stale strategy; significant scope/priority change; no runnable work despite unfinished actionable tasks; or a configured budget breach. | Decide priority, dependency order, ownership, scope and a versioned recovery plan. No need to exhaust cheaper models first. |
| Astra on deterioration | Two new actionable blocked tasks in a rolling hour; two critical-task failures without verified recovery; or two WIP/Blocked round trips for the same root since the last reviewed baseline. | Prevent accumulation and repeated rerouting. Unrelated completed tasks do not cancel this trigger. |
| Astra on apparent progress | An actionable stalled cohort misses required progress on two successive wakes, including incomplete cycles, even while cards move or other tasks advance. | Reassess the cohort and critical path; a single missed deadline or uncertainty may already require an earlier route. |
| Astra after ineffective advice | One completed Sol recovery attempt reaches its outcome deadline without verified improvement, or the same failure recurs. | Reconsider plan/owner/dependency assumptions. A technically valid answer without its predicted effect is not recovery. |
| Astra on visibility failure | Critical decision evidence is missing now, or board evidence remains incomplete across two wakes after an owned collection attempt. | Restore observability and choose safe action; never classify an unread board as healthy. |
| Astra watchdog | Three hours since the last successful strategic review on an active board, including an unchanged board. | Check priorities, aging, critical path, rising blocked cohorts and whether the last strategy produced its expected effects. |

Expected external waits are excluded from actionable-stall counts only with a
current source receipt, owner, expected condition/time and fallback. Missing or
expired proof makes the item unknown/actionable again. Unowned blocked work gets
an owner immediately; staffing attempts are activity until useful work resumes.
Idle-board watchdog skipping requires positive complete evidence of no actionable
work. Critical-path or cohort decline is never hidden by aggregate throughput.

When both technical and strategic triggers fire, Astra owns the strategy now.
Sol may gather a bounded technical fact in parallel only where that read-only
scope is independent; otherwise sequence it under Astra's question. Do not delay
a hard strategic trigger until Sol finishes. If the current primary is already
Astra according to fresh runtime evidence, perform and record that strategic
review directly; do not invoke a second Astra solely to satisfy the tier name.
A Sol primary still escalates board-wide
strategy to Astra. Model authority does not exempt any primary from outcome checks.
Direct review must record the same decision, owner, expected effect and deadline
as adviser output. Merely recording an Astra model or bootstrap is not a review.

## Compact call contract and failure handling

Each request carries a durable request ID, reason codes, incident/cohort identity,
strategy/plan versions, affected tasks, current outcome evidence, required decision,
bounded read scope, requested model, response deadline and stop condition. Helpers
receive explicit compact context, not inherited Coordinator history. Require an
actual-model/start receipt and a structured decision with expected observable
effect, owner and reassessment deadline. The Coordinator remains the sole actor.

Persist distinct states: requested, started, completed, decision accepted, effect
verified, failed and outcome unknown. A queued request, model error, malformed or
stale response never updates successful-review time or clears the escalation.
Successful strategic review and subsequent successful recovery have separate clocks.

Deduplicate by incident, evidence generation and strategy version; permit only one
in-flight equivalent helper. Reconcile a timeout/unknown outcome before retrying,
so the old helper cannot race a replacement. Allow at most one retry of a proven
transient failed call, using the next external wake or provider Retry-After. On
continued failure retain the pending obligation and route the verified runtime
defect to its existing repair owner. Do not silently substitute Sol for a required
Astra decision or repeatedly invoke an unavailable model. Human contact is only
for a real missing authority, credential or external action, not routine routing.
Safe previously authorized work may continue while the decision remains pending;
conflicting or stale-plan actions must stop.

Accept a decision only against fresh applicable state; stale advice needs a refreshed
request. At the outcome deadline verify the claimed effect at its source. Failure
reopens/escalates the recovery even if the advice was successfully delivered.
Event deduplication may suppress duplicate calls, never the obligation, deadline
or newly worsened evidence. Existing unresolved incidents are re-evaluated on every
wake without relying on fresh events.

## Proactive model transition

Human clarification, 2026-09-19: retain this primary session and use same-task
Sol/Astra adviser sessions for bounded requests. Verify each adviser's effective
model and provision both advisers before downgrading the primary, even while
the current primary is Astra. A one-time readiness bootstrap is not a strategic
review and does not reset its watchdog; keep the adviser idle afterward. Verify
model and non-primary identity; reuse a verified idle adviser with a fresh compact
contract rather than a full history. This overrides automatic disposal solely
because a useful adviser completed one request. Advisers remain idle between
requests, have no scheduler, and return evidence/decisions to the primary, which
serializes actions and owns durable state. Implementation stays with source tasks.
Use existing escalation triggers proactively; no Human intervention is required
per call. While the primary is Astra, it handles strategic triggers directly
unless an independent strategic assessment is specifically needed.

Same-task advisers do not require queue transfer or primary handoff. Prefer a
supported in-place change to a cheaper primary model, with actual-model readback,
while retaining session identity and automation targeting. That capability is
not yet verified. Spawning advisers alone leaves Astra-primary wake costs intact.
Keep guarded rotation as continuity recovery; it is not a dependency of advisers
and does not override the requested stable-primary layout.

The intended steady state is an inexpensive operational primary plus bounded Sol
and Astra assistance. Once rollout gates pass, the Coordinator performs the
supported model transition proactively. It does not wait for a Human to request
each switch or helper call. Verify actual model, sole primary, unread-message
continuity and future automation targeting before retiring the old owner.

Use helpers first for exceptions rather than changing primary for every incident.
If a weaker primary repeatedly misses strategic triggers, falsely records progress,
or fails to execute two consecutive accepted recovery plans by their outcome
deadlines, request an immediate Astra strategy audit and automatically roll back
to the last verified stronger configuration through the same guarded handoff.
The failing cohort determines this condition; unrelated wins do not mask it.
Do not downgrade again until the cause is repaired and a new trial passes. If a
required handoff capability is unavailable, retain the current owner and staff
capability repair; do not pretend that a sibling session is the new primary.

## Rollout evidence and regression cases

Measure task/cohort aging, new and recovered blockers, repeat blockers, missed
milestones, independent gate passes/reopens, completed delivery, strategic decisions
and verified effects per call, false health classifications, missed escalations,
latency, human interventions and real usage/cost. Report evidence coverage.
Cheap-model savings do not justify deteriorating recovery or false green status.

Required deterministic scenarios for the implementation owner:

1. Many card moves/messages/restarts with overdue outcomes still trigger Astra.
2. Unrelated completed tasks cannot hide a growing or aging blocked cohort.
3. Legitimate long work within its evidence deadline and proven external waits
   avoid false stall alarms; expired wait proof and repeated extensions escalate.
4. Sol resolution requires observed effect; failed effect or recurrence escalates.
5. Hard Astra triggers bypass Sol; simultaneous triggers choose strategy ownership.
6. Failed/unknown/wrong-model/stale helper results preserve escalation and review
   watermarks; bounded retry and in-flight deduplication survive restart.
7. No delta on an active board still runs the watchdog; periodic observations
   and plan rewrites cannot reset outcome age or the review clock.
8. A new critical regression breaks prior deduplication; replayed evidence never
   counts as new progress. Missing coverage cannot produce a healthy verdict.
9. A completed Astra review without later improvement remains unresolved and
   reaches recovery/rollback criteria; an Astra primary avoids duplicate helpers.
10. Profile selection without primary/queue/routine receipts fails the cutover
    gate; rollback preserves the same board identity and obligations.
