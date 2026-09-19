# Proactive Coordinator escalation and verified progress

Human-directed policy, 2026-09-19. Applies primarily to this permanent board
Coordinator and also to its reusable plugin implementation. The Coordinator
selects helpers and initiates validated model handoffs without asking the Human
to operate the routing. Kandev Automation remains the sole periodic wake source.
Existing permissions, independent gates and single-primary requirements remain.
The routing rules below are binding operational policy; automated detection is
not claimed implemented until the pilot and real-board adapters pass their tests.

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
| Astra on apparent progress | At least two actionable tasks remain past their evidence deadlines on two consecutive complete wakes, even while cards move or other tasks advance. | Reassess the stalled cohort and its critical path rather than rewarding board activity. |
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
Astra, perform and record that strategic review directly; do not invoke a second
Astra solely to satisfy the tier name. A Sol primary still escalates board-wide
strategy to Astra. Model authority does not exempt any primary from outcome checks.

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
