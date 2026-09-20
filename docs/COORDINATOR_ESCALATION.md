# Proactive Coordinator escalation and verified progress

Human-directed policy, revised 2026-09-20. Applies primarily to this permanent board
Coordinator and also to its reusable plugin implementation. The Coordinator
selects bounded helpers while Astra remains PRIMARY; generic continuity handoffs
retain their guarded requirements. Kandev Automation remains the sole periodic wake source.
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
deadline is 30 minutes for a small first-evidence item, tunable before execution
with an evidence-backed reason for long tests/builds. Do not alter an existing
deadline automatically. A later move/message/plan rewrite never resets elapsed age. Deadline
extensions require an evidence-backed reason recorded separately from progress;
repeated extensions are a strategic exception. Unknown evidence is unknown,
never green. Missing instrumentation cannot justify suppressing a review.

## Routing preflight

Before routine ledger maintenance on every wake, Astra PRIMARY checks the current runtime model,
last accepted Astra decision, overdue outcomes, unresolved strategic uncertainty
and failed advice effects. Persist this compact routing record at the front of
the live handoff: model evidence and timestamp; strategic decision ID/time;
cohort progress baseline; consecutive wakes missing required progress; next
outcome/owner/deadline; and pending adviser request/result/effect. Unknown model
or review time cannot justify the Astra-primary exemption or reset the watchdog.
Use fresh response/runtime metadata, not the configured profile or session name;
a model can change while those identities remain unchanged.
On an active board, an unknown last strategic review requires Astra's direct
review now. A
missing routing receipt forbids a cycle-PASS claim or strategic plan change;
safe execution of existing valid contracts may continue. Use the canonical
G1–G10 gate meanings, not local substitutes for evidence or completion.

Dispatch a required bounded contract before another unchanged recheck or generic
nudge. Strategic uncertainty and ambiguous health/error go directly to Astra
with exact evidence; Sol is optional, never a required hop. Two successive wakes without
the required progress on an actionable stalled cohort are a backstop, including
incomplete cycles; do not wait three hours or require two fully completed cycles.
The three-hour watchdog is an upper bound on active-board strategic review, not
a minimum delay. Existing equivalent in-flight advice is reconciled, not duplicated.

An implementation owner returning only another plan and becoming idle after an
execution handoff has not delivered its requested outcome. Route the unresolved
technical question to Astra, which may elect Sol for an independent complex
investigation; route priority, ownership, dependency or repeated ineffectiveness
to Astra. A positive claim of external waiting must name the
specific blocked action; continue independent authorized work. Do not turn a
publication or integration gate into a blanket stop on local proof.

Accept advice against current evidence, send the resulting executable action to
its sole owner, verify execution starts, and check the predicted effect at its
deadline. Start/response/decision/effect are separate receipts. A failed effect
returns to Astra without another unchanged cheap-model loop. No-duplicate-ping
rules suppress redundant messages, never escalation or due follow-through.
This is an operational obligation now; unfinished routing automation does not
excuse missed calls. Astra remains stable PRIMARY; Terra, Luna, and Sol are
bounded sidecars.

## When to invoke which model

Evaluate on each incoming automation wake and meaningful event. Thresholds are
initial configurable defaults. Do not wait for the watchdog when a trigger fires.

| Route | Trigger | Why / required output |
| --- | --- | --- |
| Deterministic tools / Luna | Exact supported collection or mechanical recipe is current and allowlisted. | Produce the requested readback; do not make board writes outside a current authorized batch. |
| Terra | Astra has issued a bounded coordination/execution contract with current preconditions. | Execute only its allowlisted recipe, return source readback, and stop on stale state. |
| Sol optional | A complex independent technical investigation can usefully run in parallel with Astra's direct reasoning. | Diagnose one task; return evidence and a testable next action. No priority, scope, or gate decision. |
| Astra directly | PLAN_INVALID; ambiguous health/error; cross-task conflict; dependency change; stale strategy; missed effect; no runnable work; or budget breach. | Decide priority, dependency order, ownership, scope and a versioned recovery plan. |
| Astra on deterioration | Two new actionable blocked tasks in a rolling hour; two critical-task failures without verified recovery; or two WIP/Blocked round trips for the same root since the last reviewed baseline. | Prevent accumulation and repeated rerouting. Unrelated completed tasks do not cancel this trigger. |
| Astra on apparent progress | An actionable stalled cohort misses required progress on two successive wakes, including incomplete cycles, even while cards move or other tasks advance. | Reassess the cohort and critical path; a single missed deadline or uncertainty may already require an earlier route. |
| Astra after ineffective advice | One completed optional Sol recovery attempt reaches its outcome deadline without verified improvement, or the same failure recurs. | Reconsider plan/owner/dependency assumptions. A technically valid answer without its predicted effect is not recovery. |
| Astra on visibility failure | Critical decision evidence is missing now, or board evidence remains incomplete across two wakes after an owned collection attempt. | Restore observability and choose safe action; never classify an unread board as healthy. |
| Astra watchdog | Three hours since the last successful strategic review on an active board, including an unchanged board. | Check priorities, aging, critical path, rising blocked cohorts and whether the last strategy produced its expected effects. |

Expected external waits are excluded from actionable-stall counts only with a
current source receipt, owner, expected condition/time and fallback. Missing or
expired proof makes the item unknown/actionable again. Unowned blocked work gets
an owner immediately; staffing attempts are activity until useful work resumes.
Idle-board watchdog skipping requires positive complete evidence of no actionable
work. Critical-path or cohort decline is never hidden by aggregate throughput.

When technical and strategic triggers fire, Astra owns the decision now. Sol may
gather an independent bounded fact in parallel only when that offload beats direct
reasoning; do not delay Astra. Direct review records decision, owner, expected
effect and deadline. Recording a model or bootstrap is not a review.

## Compact call contract and failure handling

Each sidecar request carries `action_id`, strategy revision, exact task/session/
lane/head preconditions, an allowlisted action or conditional recipe, measurable
outcome, deadline/expiry, preservation and forbidden actions, stop/fallback, and
required readback. Helpers read `PROMPT.md` once per turn, their designated
strategy sections, that compact context, current target rows and only necessary
policy sections; never the giant whole-board plan or primary history. Startup
verifies caller task, workspace and tool authority before board writes; wrong or
unknown identity returns a read-only result. The primary is the sole strategy
and effect-acceptance actor.

Persist distinct states: requested, started, completed, decision accepted, effect
verified, failed and outcome unknown. A queued request, model error, malformed or
stale response never updates successful-review time or clears the escalation.
Successful strategic review and subsequent successful recovery have separate clocks.

Deduplicate by incident, evidence generation and strategy version; permit one
mutation-batch executor globally at a time. Parallel disjoint read collection is
allowed. This lease is a logical contract, not a platform-atomic claim. Reconcile a timeout/unknown outcome before retrying,
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

## Stable primary and future handoff

Astra is the stable PRIMARY. There is no automatic cheap-primary downgrade and
no mandatory Astra or Sol adviser. Reuse relevant idle designated sidecars; do
not give them timers, infinite loops, or daisy-chained/nested delegation absent
exact authorization. Default to one executor plus an independent read-only
helper only when useful. Native helpers may execute authorized coordination or
documentation batches; implementation of other board tasks remains task-bound
to its sole writer.

A future primary handoff remains subject to the generic guarded requirements:
fresh effective-model evidence, exactly one primary, unread FIFO preservation,
generation fencing, successor bootstrap, and authoritative routine-target and
rollback readback. A failed batch narrows or upgrades that exact batch; it does
not replace the PRIMARY.

## Rollout evidence and regression cases

For the next three complete cycles, measure task/cohort aging, new and recovered
blockers, repeat blockers, accepted milestones per whole-team cost (including
Astra, Review, and retries), deadline misses, unowned actionable work and
coverage, duplicate/unsafe moves (target zero), Human rescues, latency, and
real usage/cost. Report evidence coverage; unknown cost stays unknown. This
pilot does not establish savings.

Required deterministic scenarios for the implementation owner:

1. Many card moves/messages/restarts with overdue outcomes still trigger Astra.
2. Unrelated completed tasks cannot hide a growing or aging blocked cohort.
3. Legitimate long work within its evidence deadline and proven external waits
   avoid false stall alarms; expired wait proof and repeated extensions escalate.
4. An optional Sol resolution requires observed effect; failed effect or recurrence escalates.
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
