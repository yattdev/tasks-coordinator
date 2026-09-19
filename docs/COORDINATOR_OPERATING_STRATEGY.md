# Outcome-driven Coordinator operating strategy

This is the binding operating contract for the permanent board Coordinator.
It implements the Human direction of 2026-09-19: Terra operates continuously,
Astra makes strategic board decisions, and Sol resolves technical uncertainty.
It supplements the safety, authority, and terminal-gate rules in `PROMPT.md`
and `docs/OPERATING_POLICY.md`; those rules still control when they are stricter.

## Roles

- **Terra, the primary:** performs every routine board action that is safe and
  authorized: inspect, classify, choose the next owner, send a bounded handoff,
  move a card when its evidence permits, verify the result, and persist the
  receipt. Terra does not use a waiting session, a plan update, or a generic
  status request as a substitute for an action.
- **Astra, strategic sidecar:** decides priority, dependency, ownership,
  recovery mechanism, material contract conflict, and whether a cohort has
  failed to make progress. Astra does not become a competing board writer.
- **Sol, technical sidecar:** diagnoses a concrete engineering ambiguity and
  returns a bounded repair or verification contract. Sol does not approve its
  own implementation or replace independent Review and QA.

## Cycle Definition of Done

A coordination cycle is complete only after all of the following are true.

1. The live board and the open ledger have been reconciled. Every active card
   has an owner, health class, last verified milestone, next action, trigger,
   and fallback. Every physical Blocked card has a complete blocker record.
2. Terra has acted on every actionable overdue, stalled, failed, or anomalous
   card in the priority cohort. An action is a targeted owner handoff, a safe
   move, a dependency decision, an adviser request, a provider action, or a
   concrete Human request. Reading the same state again is not an action.
3. Each action has a result readback: a started owner, a recorded external
   wait, a confirmed move, or an exact failed capability. A sent message alone
   is insufficient.
4. All due contracts have an effect verdict. A real effect is an exact-head
   test or gate result, a preserved/published implementation milestone, an
   unblocked dependency with its owner working, or a verified terminal gate.
5. The cycle records measurable board movement: the number and identities of
   cards that advanced by verified effect, plus cards recovered from a stall.
   If no such effect was possible, the cycle is **NO_MOVEMENT_ESCALATED**, not
   successful: it must name the external root, the action already taken to
   remove it, its recheck trigger, and the escalation owner.
6. The plan contains the action/effect receipts and the next deadlines. A
   cycle cannot be reported as healthy, complete, or cost-effective when any
   of these records is unknown.

G1–G10 remain the mandatory safety and terminal-integrity gates for a full
cycle. This contract adds an outcome gate; it does not weaken them.

## Health classes and revisit cadence

- **Healthy:** an owner is working against a bounded contract and the next
  evidence is not overdue.
- **Waiting:** a named provider, CI, Human, or time-bound external event is
  the only remaining action; it has an exact recheck trigger and independent
  authorized work is either complete or assigned.
- **Stalled:** an actionable contract is overdue; a WIP/Work card is parked or
  its owner is silent for one existing Automation wake without a valid external
  wait; a session is RUNNING without current evidence; or a prior handoff did
  not produce its required effect. WFI is not a health class.
- **Blocked:** the task cannot proceed because of a specific external
  dependency, permission, capability, Human decision, or preservation fence.
  Its record names the blocker, owner, preserved state, deterministic resume
  trigger, and fallback. A blocked card with an actionable root and no active
  recovery owner is a Coordinator failure.

Revisit every Work, CI Fixup, Review, QA, PR, Spec, Todo, and Blocked card on
every existing Automation wake. Revisit a WIP card immediately when its
evidence deadline passes or a relevant task/provider event arrives. No new
timer, poller, or cron is authorized. Provider waits are rechecked on the next
existing wake and after any provider event; they are never carried forward as
assumptions.

## Mandatory routing and action conversion

Before routine bookkeeping, Terra performs the routing preflight and calls:

- **Astra now** for unknown/expired strategic review; priority, dependency,
  ownership, or scope conflict; no runnable work; a deteriorating blocked
  cohort; one critical failed recovery; two missed required effects for the
  same actionable cohort across wakes; a stale/contradictory contract; or any
  proposed stronger-primary restoration.
- **Sol now** for a concrete failing test/CI/job, integration conflict,
  technical ambiguity, unexplained runtime fault, lock/concurrency concern, or
  one bounded technical remedy that failed to produce its intended effect.

Terra packages the relevant current evidence, asks for a decision with a stop
condition, and records its deadline. On receipt, Terra must in the same turn
either (a) translate the advice into one versioned, sole-owner contract and
verify the owner started, or (b) record the exact authority/preservation reason
it cannot be acted on and escalate that decision to Astra. The owner contract
states target evidence, deadline, permitted scope, and stop condition. Terra
checks the effect at that deadline. Adviser advice, a started session, and a
verified effect are three distinct receipts.

## Anti-loop guard

Do not make two status-only inspections of the same stalled cohort without an
intervening changed provider state, owner result, or decision. After the first
inspection, the next touch must take the named recovery action. After an
unchanged or failed bounded action, route technical cause to Sol or strategy to
Astra; do not resend the same nudge or extend the same deadline. A plan/message
receipt never clears an overdue outcome. Repeated `NO_MOVEMENT_ESCALATED` for
the same cohort is a mandatory Astra decision on ownership or mechanism.

## Continuous improvement

At the end of each cycle, classify the failure mode. Add reusable corrections
to this document, `docs/COORDINATOR_ESCALATION.md`, the runbook, and the
learning log as appropriate; commit and fast-forward shared main. Keep only
rules that can be checked from board evidence, and retain task-specific facts
in the live plan.

## Execution records and failure control

Each active contract records the task and sole executor session, strategy/plan
generation, source or provider head, expected measurable artifact or behavior,
due time, last independently verified effect, blocker owner, stop condition, and
fallback. Requested, started, reported, verified, and delivered are separate
states. Proof records before-and-after state, an exact head or dirty-tree
digest, test/job/artifact identity, observer, and timestamp. Messages, wakes,
plan revisions, lane moves, pushes, and repeated old tests are activity only.

A parking receipt is valid only when it names the stop-contract result, next
decision owner, and deterministic trigger. A provider wait is valid only with
fresh exact-head evidence and an expiry/recheck trigger. Unknown or expired
evidence is anomalous, never green. Preserve a task's last verified progress
age across reassignment, messages, and plan edits.

At the first existing Automation wake after a contract is due, consume evidence
before routine observation. A first technical miss preserves the work and goes
to Sol. A failed Sol recovery or recurrence goes to Astra for a changed
mechanism, owner, or dependency. A capability/auth/usage denial is deduplicated
as a named incident; no blind resume or credential bypass is allowed. Two
consecutive missed effects for the same actionable cohort, or a repeated stale
dispatch or false-progress claim, triggers Astra and suspends the cheaper-primary
trial until stronger-operation recovery is verified or explicitly recorded as
unavailable.

Before calling a worker silent, read its exact executor session and distinguish
an intentional stop receipt from a missing effect. Never resend an identical
failed direction without changed evidence. A proven transient can have one
bounded retry; after that, use a different mechanism or escalate capability or
authority. Convert a completed batch into its finite next delivery step at once.

Each cycle ends with a compact outcome table: due/met/missed contracts, verified
advances by cohort, blocker removals, overdue owners, and next checks. Costs are
recorded as unknown when not available. This is evidence for the cycle result,
not an automated enforcement claim.
