# RFC: Coordinator plugin scale/load architecture and burst harness

Status: **proposed 2026-09-03**, implementation-ready. Owned by the plugin-first
orchestration program (the parent program tracked on the Kandev board under
that role; per this repository's exclusion convention — see `exclusions` in
[`../contracts/coordinator-policy-contract.json`](../contracts/coordinator-policy-contract.json)
— this document identifies owners by stable role, not by an embedded transient
board task ID, since a task ID does not survive board reorganization the way
the role/ownership relationship does);
this document specifies the target design and acceptance bar but does not
implement it — implementation lives in the Coordinator plugin repository, not
here (see `docs/DECISIONS.md#coordinator-policy-is-contract-validated-not-hand-copied-2026-09-03-human-directed`,
final paragraph: scale/load design is a delivery specification, not a
`PROMPT.md` rule).

This RFC assumes and must not weaken any invariant in
[`../contracts/coordinator-policy-contract.json`](../contracts/coordinator-policy-contract.json)
(exact-head gates, workers-never-mutate, per-entry queue identity, escalation
classes). Where this document uses a contract term, it means exactly the
contract's definition — see
[`../contracts/CONTRACT_MAPPING.md`](../contracts/CONTRACT_MAPPING.md).

## 1. Problem statement

The current Coordinator runs as a single long-lived agent session per
workspace, driven by external routine pings (`WAKE:CYCLE`/`WAKE:STANDUP`) and
ordinary task/Human messages, with delegation to short-lived helper
sub-agents during a single turn (see `PROMPT.md` "Parallel-safe queue
handling"). This works at today's board size, but has no defined behavior
under sustained high message/task volume: no fenced single-writer guarantee,
no formal conflict-claim model beyond "helpers never mutate, primary
serializes", no bounded lease/receipt contract, and no compaction strategy for
the plan/ledger state that keeps every open follow-up entry inline.

This RFC specifies a plugin-native architecture that keeps every existing
policy invariant (exact-head gates, single approval principal per workspace,
per-entry queue identity, Done terminal integrity) while making the
concurrency and scale model explicit and testable.

## 2. Architecture overview

```
                       ┌─────────────────────────┐
   inbound events ───► │   Ingress / Dedupe       │
 (routine, Human,      │  (per-entry envelope,    │
  task, peer messages) │   payload digest)        │
                       └───────────┬─────────────┘
                                   │ enqueue (append-only)
                                   ▼
                       ┌─────────────────────────┐
                       │   Durable Queue          │
                       │ (exact-entry, FIFO holes │
                       │  preserved across        │
                       │  restart/compaction)     │
                       └───────────┬─────────────┘
                    claim (lease)  │  ▲ readback verify
                                   ▼  │
        ┌───────────────┐   ┌───────────────┐    ┌───────────────┐
        │ Read-only      │  │ Read-only      │    │ Read-only      │
        │ Worker #1      │  │ Worker #2      │ …  │ Worker #N      │
        │ (investigate,  │  │ (investigate,  │    │ (investigate,  │
        │  never mutate) │  │  never mutate) │    │  never mutate) │
        └───────┬───────┘   └───────┬───────┘    └───────┬───────┘
                │ receipt (claim id, findings, no board write)
                └────────────────────┬────────────────────┘
                                     ▼
                       ┌─────────────────────────┐
                       │   Fenced Leader          │
                       │ (exactly one active per  │
                       │  workspace; single-writer│
                       │  mutation lane)          │
                       └───────────┬─────────────┘
                                   │ effect + readback verify
                                   ▼
                       ┌─────────────────────────┐
                       │  Board / Provider /      │
                       │  Coordinator plan        │
                       └─────────────────────────┘
```

### 2.1 Fenced leader

- Exactly one **leader** per workspace holds the mutation lane at a time,
  identified by a monotonically increasing **fencing token** (e.g. an
  epoch/lease counter persisted with the leader record).
- Every mutation the leader performs is tagged with its current fencing
  token. The board/provider/plan writer rejects a mutation whose token is
  behind the last-accepted token for that workspace — this is what makes a
  stale or duplicate leader (e.g. after a crash/restart race) unable to
  clobber a newer leader's effect, satisfying the contract's
  `worker_helper_receipts` single-writer-lane invariant even under leader
  failover.
- Leadership is a **lease**, not a permanent role: it has a bounded TTL and
  must be renewed before expiry. A leader that cannot renew (crash, network
  partition) loses leadership at TTL expiry; a new leader fences it out with
  a higher token. No two fencing tokens are ever treated as concurrently
  valid.
- Leader election itself does not require a new external primitive: it can
  be implemented as a single row with `(workspace_id, token, holder_id,
  expires_at)` under optimistic concurrency (compare-and-swap on `token`),
  consistent with the plan's existing "per-entry, never a global watermark"
  convention for the queue.

### 2.2 Read-only worker pool

- Workers **investigate only**: they read board/provider/session state, run
  diagnostics, and produce a **receipt** — they never write to the board,
  provider, task worktrees, the shared Coordinator repository, the queue, or
  the live plan. This is the existing `PROMPT.md` parallel-triage rule,
  formalized as a structural guarantee (workers hold no mutation credential
  at all, rather than merely being instructed not to use one) and is the
  literal meaning of `worker_helper_receipts.workers_never_mutate` in the
  contract.
- A worker's receipt binds: `claim_id`, `entry_id` (from the durable queue),
  `fencing_token` the leader was on when the claim was issued, `outcome`,
  `evidence` (readback-verifiable pointers, not copied secret data), and
  `timestamp`. A receipt is evidence for the leader to act on, never itself a
  disposition of the queue entry (mirrors `PROMPT.md`: "A helper receipt
  never proves that its source queue row was claimed, acknowledged, removed,
  or that capacity was released").
- Workers are stateless between claims: a crashed worker loses no committed
  state, because it never held any — only its lease on the claimed entry
  needs to be reclaimed (see §2.4).

### 2.3 Deterministic pairwise conflict claims

- Two entries **conflict** if they would touch the same task, PR, dependency,
  branch, or other shared resource. Conflict is computed **deterministically
  and pairwise** from each entry's declared resource set (task ID, PR URL,
  branch ref, dependency edge) — never inferred from timing, ordering, or a
  global lock.
- A claim on entry A is granted only if no currently-held claim's resource
  set intersects A's resource set. This is a direct implementation of the
  contract's `queue_claim_identity.claim_collision_check:
  deterministic_claim_set`.
- Conflicting entries are **not** dropped or merged silently: per
  `queue_claim_identity.coalescing_forbidden_for`, only identity-equivalent
  routine wakes may coalesce. Two independent, resource-conflicting reports
  are serialized (one waits for the other's claim to release) and, when the
  leader acts, merged into one primary action with one receipt per
  `PROMPT.md`'s parallel-triage rule — never two competing mutations.

### 2.4 Bounded leases and receipts

- Every claim (queue-entry claim, leader lease) has an explicit, bounded
  **lease duration**. A lease that is not renewed or explicitly released
  before expiry is automatically reclaimable — this is what bounds the
  "stuck worker" and "stuck leader" failure modes without a human timeout
  decision.
- A claim's receipt must be durable (append-only, keyed by `entry_id` +
  `claim_id`) before the claim is considered actionable by the leader. An
  in-memory-only receipt that a crash can erase does not count.
- Recommended default bounds (tunable per workspace, never per the
  contract's authority boundaries — a lease-duration tuning change is
  Coordinator-decidable, not an escalation class):
  - Human-message claim lease: 30s (must be reclaimed well inside the p95
    claim target in §5).
  - Task/peer-report claim lease: 60s.
  - Leader lease TTL: 20s, renewed at 2/3 of TTL (≈13s).

### 2.5 Single-writer mutation lane

- All board/provider/plan mutations funnel through the **one active leader**
  for the workspace. Workers and any number of concurrent investigative
  helpers never hold this lane.
- The leader serializes effects **and verifies readback** before considering
  an effect committed: after a mutation (board move, tag update, message
  send, plan write), the leader re-reads the affected resource and confirms
  the observed state matches the intended effect before releasing the
  associated claim. This is the plugin-native form of `PROMPT.md`'s
  "freshness barrier before every human-facing reply" and the move-then-tag
  reconciliation rule ("The move is incomplete until both lane and tag
  agree").
- If readback does not match (e.g. a human or peer Coordinator raced the
  same resource), the leader treats its own claimed state as stale, re-reads,
  and either re-applies idempotently or reports a conflict — it never
  double-applies blindly.

### 2.6 Event-driven dirty-task scheduling

- The leader does not poll the whole board on a fixed timer beyond the
  externally delivered routine wake. Within a wake/session, task state
  changes (board webhook/event, provider webhook, queue entry arrival) mark
  the affected task **dirty**; the leader's work loop drains the dirty set
  plus the routine's own checklist, rather than re-scanning everything
  unconditionally on every internal tick.
- This does not relax the routine's "include the complete Done column"
  requirement (`PROMPT.md`) — Done enumeration remains a mandatory full pass
  every cycle; dirty-tracking is an optimization for how the leader
  *prioritizes and batches* work *inside* a cycle, not a replacement for the
  full monitored-lane sweep the contract's
  `workspace_lane_ownership.monitored_lanes` requires each cycle.
- Dirty-task scheduling must not become a hidden scheduler
  (`PROMPT.md`/README "KanDev routines are the SOLE wake source"): it only
  reorders work already triggered by a live wake or a live inbound event; it
  never invents a new wake source or timer of its own.

### 2.6.1 Cross-sender routine-wake identity (contract_version 1.1.0)

- The contract's `queue_claim_identity.routine_identity_components`
  (`coordinator-policy-contract.json`, see
  [`../contracts/CONTRACT_MAPPING.md`](../contracts/CONTRACT_MAPPING.md))
  fixes canonical Host routine identity as the tuple `workspace_id +
  routine_type_or_name + policy_or_prompt_version_generation +
  semantic_scope_generation` — deliberately **independent of which sender**
  (task ID, session ID, or message ID) delivered the wake. Two routine wakes
  with an identical value across all four components are the *same pending
  generation*, whether they arrived from the same session or two entirely
  different ones (e.g. two independent automation deliveries, or a
  same-session redelivery after a transient disconnect).
- While an identical generation is queued, claimed, or actively running, a
  later cross-sender equivalent **coalesces** into exactly one preserved
  pending successor or freshness bit
  (`queue_claim_identity.coalescing_preserved_state`) — it is never silently
  dropped with no trace, and it is never allowed to spawn a second,
  redundant full monitored-lane scan. This is what
  `cross_sender_coalescing_permitted: true` requires: coalescing must work
  *across* senders, not only when the exact same sender happens to redeliver.
- Human input, task reports, peer-Coordinator reports, and any
  **non-identical** generation (a different `policy_or_prompt_version_generation`
  or `semantic_scope_generation`, even from the same workspace and routine
  type) remain distinct FIFO entries regardless of sender — the existing
  `coalescing_forbidden_for` floor is unchanged by this clarification; it is
  the routine-wake identity itself that is now fully specified, not the set
  of things that must never coalesce.
- A coalesced routine-wake receipt (`worker_helper_receipts.routine_wake_coalescing_receipt_fields`)
  binds: `canonical_entry_id` (the one surviving entry the leader actually
  acted on), `absorbed_source_entry_ids` plus their
  `absorbed_source_entry_count` and `absorbed_source_entry_timestamps_without_bodies`
  (proof of exactly what was absorbed, deliberately never the absorbed
  entries' payload bodies — coalescing is a dedup decision, not a summary of
  content), the `leader_fencing_token` in force when the coalescing decision
  was made, the `dirty_generation` the canonical entry satisfies (§2.6), and
  `post_run_requeue_required`: `true` when a further arrival of the same or a
  newer generation lands *after* the canonical entry's run has already
  started — the leader must schedule one follow-up dirty pass for that newer
  arrival rather than treat the in-flight run as having already covered it.
- Ownership is unchanged from §5: the Kandev Host queue-primitive owner
  implements the actual coalescing/dedup mechanism at the transport/storage
  layer (it is the authority that decides two entries share one routine
  identity and enforces the single-surviving-entry guarantee); this RFC's
  leader only **consumes** the resulting canonical entry and its dirty
  generation (§2.6) to decide *what to schedule*, and does not reimplement
  Host-side identity comparison or coalescing storage.

### 2.7 Compact snapshots

- See [`STATE_COMPACTION_SPEC.md`](STATE_COMPACTION_SPEC.md) for the full
  specification. In architectural terms: the leader's working state is a
  **materialized current-state snapshot** (open follow-ups, active leases,
  dirty set) plus an **append-only audit/archive** of everything rolled out
  of the snapshot. The leader never treats a snapshot as authoritative
  without its paired audit trail being consistent (hash/count verified, see
  the compaction spec).

### 2.8 Metrics / SLOs

Emit at minimum (all per-workspace, per-cycle, and cumulative):

| Metric | Definition | Target |
| --- | --- | --- |
| `claim_latency_human_ms` | time from entry arrival to first successful claim, Human-authored entries | p95 < 10,000 ms |
| `claim_latency_task_report_ms` | time from entry arrival to first successful claim, task/peer report entries | p95 < 30,000 ms |
| `claim_overlap_count` | count of any two simultaneously-held claims whose resource sets intersect | 0 (hard invariant, not just an SLO) |
| `queue_entries_lost_total` | entries present pre-crash/restart/session-deletion not recoverable post-event | 0 (hard invariant) |
| `coalesced_wakes_total` / `coalesced_wakes_incorrect_total` | routine wakes coalesced / any coalesce that was not exactly-identical | incorrect = 0 (hard invariant) |
| `suppressed_duplicate_full_board_scan_total` | count of routine-wake claims suppressed by cross-sender coalescing (§2.6.1) that would otherwise have triggered a redundant full monitored-lane scan | tracked; must equal `coalesced_wakes_total` exactly (every correct coalesce suppresses exactly one redundant scan, never zero and never more than one) |
| `leader_fencing_rejections_total` | mutations rejected due to a stale fencing token | tracked, non-zero is expected under failover and is not itself a defect |
| `readback_mismatch_total` | leader mutations whose post-write readback did not match intent | tracked; sustained non-zero indicates a race or bug |
| `snapshot_compaction_duration_ms`, `snapshot_bytes_before/after` | see compaction spec | tracked |

SLO breaches feed the existing escalation model: a **sustained** breach (not
one blip) is a platform defect, filed as a board task per `PROMPT.md`'s
existing capability-gap-is-a-board-task rule — never a silent retry loop.

### 2.9 Failure recovery

| Failure | Recovery |
| --- | --- |
| Worker crash mid-claim | Claim lease expires (§2.4); entry becomes reclaimable; no state is lost because workers hold no durable state of their own. |
| Leader crash | Leader lease expires; a new leader is elected with a strictly higher fencing token; in-flight mutations from the old leader are rejected by the fencing check (§2.1) if they arrive late; the new leader resumes from the last durable snapshot + audit trail (§2.7). |
| Full process/session restart | Durable queue and snapshot/audit trail survive (external storage, not in-process memory); on restart, the new leader/worker set re-derives the dirty set from queue state, never from memory. |
| Session deletion (Kandev-level) | Per `docs/DECISIONS.md#failed-session-queue-recovery-must-precede-session-deletion-2026-09-03`, any queue-recovery read must complete *before* a failed session is deleted. This RFC's durable queue is deliberately external to any single session's lifetime for exactly this reason — session deletion never implies queue-entry deletion. |
| Split-brain (two leaders believe they hold the lease) | Fencing token compare-and-swap (§2.1) makes this detectable and safe: at most one leader's mutations are ever accepted; the loser observes rejected mutations and steps down. |

### 2.10 Shadow migration

The plugin-native leader/worker model must not cut over in one step from the
current single-session Coordinator:

1. **Shadow phase**: run the plugin leader/worker pool in read-only shadow
   mode alongside the existing Coordinator session. The shadow leader
   computes what it *would* do (claims, proposed mutations) and records them,
   but only the existing Coordinator session actually mutates. Compare
   shadow decisions against real Coordinator actions; diffs are logged, not
   escalated, during this phase.
2. **Gated cutover**: once shadow-phase diffs are at an acceptable rate (0
   `claim_overlap_count` and 0 `queue_entries_lost_total` sustained across at
   least one full burst-harness run, §4), enable the plugin leader as the
   real mutation path for one workspace, with the existing Coordinator
   session demoted to a hot-standby leader candidate (so a plugin leader
   failure still fences correctly into a working fallback).
3. **Rollback**: the shadow/cutover switch is a single per-workspace flag; a
   regression rolls back to the prior single-session Coordinator without
   losing queue state, because the durable queue and snapshot format are
   shared across both phases.

## 3. Explicit non-goals

- This RFC does not change any contract invariant. If a proposed
  optimization would require weakening `workers_never_mutate`, exact-head
  gates, or per-entry queue identity, it is out of scope here and must go
  through a contract **major** version change with its own decision record
  (see `../contracts/CONTRACT_MAPPING.md` §3).
- This RFC does not implement multi-workspace coordination. Workspaces
  remain peers with no standing over each other's resources
  (`docs/FILESYSTEM_DOCKER_CONTRACT.md` §3); the leader/worker model is
  strictly per-workspace.
- This RFC does not replace KanDev routines as the wake source (§2.6).

## 4. Burst harness

### 4.1 Purpose

A reproducible load test that exercises the architecture in §2 against
realistic-scale board activity, so acceptance metrics are measured against a
fixed, repeatable scenario rather than ad hoc production observation.

### 4.2 Scenario shape

The scenario is **fully deterministic**: every task, message, and fault
position below is fixed by explicit enumeration or formula, not left to
"a representative mix" chosen at run time. Two independent harness
implementations that both follow this section must produce byte-identical
task/message schedules. Any residual non-schedule randomness the
implementation needs (e.g. synthetic payload filler text, timing jitter
within a fault's injection window) **must** be seeded with the fixed value
`HARNESS_RANDOM_SEED = 20260903` so a full run is bit-for-bit reproducible;
the schedule itself does not depend on this seed.

- **70 tasks**, numbered `t1`..`t70` in ascending creation order, distributed
  across the monitored lanes (`workspace_lane_ownership.monitored_lanes`) in
  exactly this fixed order and count (no "e.g." — this is the canonical
  distribution, not an example):
  - `t1`–`t10` → Spec (10)
  - `t11`–`t25` → Work (15)
  - `t26`–`t35` → Review (10)
  - `t36`–`t45` → QA (10)
  - `t46`–`t55` → PR (10)
  - `t56`–`t60` → CI Fixup (5)
  - `t61`–`t70` → Done (10), split `t61`–`t66` clean terminal receipts and
    `t67`–`t70` deliberately suspicious (missing/mismatched terminal-receipt
    field) to exercise the terminal-integrity gate.
- **50 messages**, indexed `m1`..`m50` in injection order, drawn from a
  fixed 25-slot base pattern repeated twice (`m1`–`m25` then `m26`–`m50`,
  each repetition assigning fresh distinct `entry_id`s so no message content
  repeats across the two halves except the intentional duplicate-wake pairs
  called out below). The base pattern's per-slot type assignment:

  | Slot (mod 25, 1-indexed) | Type |
  | --- | --- |
  | 1, 7, 13, 20, 25 | Human message |
  | 2, 3, 6, 9, 12, 14, 17, 19, 22, 24 | Task self-report |
  | 4, 10, 16, 23 | Peer-Coordinator report |
  | 5, 8 | Routine wake, identical `WAKE:CYCLE` duplicate pair "A" |
  | 15, 18 | Routine wake, identical `WAKE:CYCLE` duplicate pair "B" |
  | 11 | Routine wake, near-duplicate (non-identical) variant 1 |
  | 21 | Routine wake, near-duplicate (non-identical) variant 2 |

  Applied twice (`m1`–`m25`, `m26`–`m50`), this yields exact totals: **10
  Human messages, 20 task self-reports, 8 peer-Coordinator reports, 8
  identical-duplicate routine-wake markers forming 4 coalescing-eligible
  pairs** (pair A repetition 1 = `m5`/`m8`, pair B repetition 1 =
  `m15`/`m18`, pair A repetition 2 = `m30`/`m33`, pair B repetition 2 =
  `m40`/`m43`), **and 4 near-duplicate non-identical routine-wake markers**
  (`m11`, `m21`, `m36`, `m46`) that must never coalesce with each other or
  with anything else. `10 + 20 + 8 + 8 + 4 = 50`.
- **Cross-sender assignment (contract_version 1.1.0 addendum, §2.6.1)**: each
  coalescing-eligible pair's two markers are, by fixed design, delivered by
  two **distinct senders** — the first member of every pair (`m5`, `m15`,
  `m30`, `m40`) carries `sender_session_id = harness-session-A`, and the
  second member (`m8`, `m18`, `m33`, `m43`) carries
  `sender_session_id = harness-session-B` (two fixed, distinct synthetic
  session identifiers, never the harness's own driver session). Both members
  of a pair still share an identical `entry_id`-independent routine-identity
  4-tuple (`workspace_id`, `routine_type_or_name`,
  `policy_or_prompt_version_generation`, `semantic_scope_generation`) —
  this is what makes the pair coalescing-eligible in the first place. This
  fixed cross-sender assignment is what proves coalescing is keyed on
  routine identity, not on sender identity: a harness that only ever
  redelivered duplicates from the *same* sender would not exercise
  `cross_sender_coalescing_permitted`. The 4 near-duplicate markers
  (`m11`, `m21`, `m36`, `m46`) each carry their own third fixed sender
  (`harness-session-C`) and a deliberately different
  `semantic_scope_generation` value, so they must never coalesce with
  either pair member regardless of shared sender or target.
- **Injected faults**, run exactly once each per full harness pass, at these
  fixed positions in the `m1`..`m50` timeline (not "at least once" at an
  arbitrary point — a specific, reproducible position each run):
  - Kill a worker mid-claim: kill the worker holding the claim for `m12`
    (a task self-report) after it has read the entry but before it emits its
    read-only recommendation.
  - Kill the leader mid-coalescing-decision (contract_version 1.1.0
    addendum): kill the leader while processing `m8` (pair A repetition 1's
    cross-sender duplicate of `m5`, arriving at 7830ms inside `m5`'s
    7800–7850ms claim window per §4.2.1's override table) immediately after
    the leader recognizes `m8`'s routine identity matches `m5`'s
    already-claimed entry — so `m8` must be absorbed, never separately
    claimed — but **before** the coalescing receipt
    (`canonical_entry_id`/`absorbed_source_entry_ids`/`leader_fencing_token`/
    `dirty_generation`) is durably written. Recovery must resolve to exactly
    one of {the receipt is already durably written and `m8` is recorded
    absorbed} or {the receipt was never written and `m8` is still present,
    re-derivable as a pending absorption target from the durable queue
    alone} — never both `m5` and `m8` ending up separately claimed/disposed,
    and never `m8` vanishing with no absorption record either way.
  - Kill the leader mid-mutation, sub-case A (before readback verify): kill
    the leader during the mutation triggered by `m25` (the last message of
    the first repetition), immediately after the write and before the
    readback-verify step.
  - Kill the leader mid-mutation, sub-case B (after readback verify): kill
    the leader during the mutation triggered by `m26` (the first message of
    the second repetition), immediately after the readback-verify step
    completes but before the claim is released.
  - Restart the whole process/session set from durable storage only: `m38`
    arrives at 14,400ms and, carrying its own uncontended `task:t18` claim
    key (§4.2.4), is claimed immediately, so its earliest possible
    disposal (Human-message receipt, §4.2.3's 500ms duration) is
    14,400ms + 500ms = **14,900ms**. `m39` arrives earlier still, at
    14,600ms, on its own uncontended `task:t19` key — under the ordinary
    immediate-claim rule of §4.2.2 it would already be claimed at
    14,600ms and fully disposed by 14,800ms (its 200ms task-self-report
    duration), i.e. *before* `m38`'s own disposal and before this fault
    could ever be exercised. This restart fault is therefore the
    harness's second explicit, designed exception to the immediate-claim
    rule (the first being `m12`'s mid-claim kill, §4.2.2): `m39`'s claim
    is deliberately withheld past its 14,600ms arrival, so that it
    remains durably enqueued but unclaimed through the restart. The
    fixed, deterministic restart boundary is **14,900ms** — strictly
    after both `m38`'s 14,900ms disposal and `m39`'s 14,600ms arrival (an
    explicit, nonnegative 300ms window in which `m39` sits
    durable-but-unread): at that offset, halt every process/session and
    cold-restart from durable storage alone. `m39` is the harness's
    designed unread durable queue entry that crosses the cold restart —
    recovery must re-derive it from durable state and grant its claim
    only after the restart, exercising true zero-loss recovery rather
    than merely re-observing already-disposed state. Resume normal
    injection (per the uniform §4.2.1 cadence, unaffected by this fault)
    with `m40` once the restarted process/session set is live, and grant
    `m39`'s deferred claim as part of the same post-restart recovery
    pass. Because `m40` (pair B repetition 2's first member) is injected
    immediately after this restart, the restarted leader/worker set must
    also re-derive `m40`'s pending coalescing-eligible state purely from
    durable storage, with no in-memory carryover of pre-restart pairing
    state from repetition 1.
  - Delete a session that has an unread queued message: target the session
    holding `m45` (a Human message, per the slot-20/45 mapping in the
    schedule table above); delete it only after asserting, per the
    2026-09-03 decision, whether a recovery read of `m45` already completed
    or is provably impossible — the harness records which case occurred, it
    does not assume either.
  - Delete the non-canonical sender's session mid-pair (contract_version
    1.1.0 addendum): after `m43` (pair B repetition 2's cross-sender
    duplicate of `m40`, `sender_session_id = harness-session-B`) has been
    absorbed and its coalescing receipt durably written, delete
    `harness-session-B` itself. The coalescing receipt's
    `absorbed_source_entry_ids`/count/timestamps must remain fully readable
    from the durable queue/receipt store afterward — proving absorption
    evidence never depends on the absorbed message's *sender session*
    surviving, only on the durable receipt already written before deletion
    (mirrors `docs/DECISIONS.md#failed-session-queue-recovery-must-precede-session-deletion-2026-09-03`
    applied to a coalesced, not just a plain unread, entry).

### 4.2.1 Arrival-time schedule

All offsets are milliseconds elapsed since harness start (`T0 = 0`). Two
independent implementations of this schedule must compute byte-identical
offsets from the formulas below (no rounding/timezone/clock-source
ambiguity — this is simulated logical time, not wall-clock time).

- **Task arrival**: task `t_i` (`i` = 1..70) arrives at offset
  `(i-1) * 100` ms. This single formula reproduces the lane batches already
  fixed above as contiguous 100ms-spaced blocks with no gaps:

  | Lane batch | Tasks | Offset range (ms) |
  | --- | --- | --- |
  | Spec | `t1`–`t10` | 0–900 |
  | Work | `t11`–`t25` | 1000–2400 |
  | Review | `t26`–`t35` | 2500–3400 |
  | QA | `t36`–`t45` | 3500–4400 |
  | PR | `t46`–`t55` | 4500–5400 |
  | CI Fixup | `t56`–`t60` | 5500–5900 |
  | Done | `t61`–`t70` | 6000–6900 |

- **Message injection**: begins only after every task has arrived, at fixed
  offset `T_msg0 = 7000` ms (100ms after `t70`). Message `m_i` (`i` = 1..50)
  arrives at offset `T_msg0 + (i-1) * 200` ms — i.e. `m1`@7000ms ..
  `m50`@16800ms — **except** the five messages listed in the override table
  below, whose offsets are deliberately pulled earlier than the uniform
  200ms cadence would place them, to force genuine concurrent claim
  contention on a shared resource key rather than sequential
  non-overlapping claims (see §4.2.4):

  | Message | Uniform-cadence offset (ms) | Overridden offset (ms) | Why |
  | --- | --- | --- | --- |
  | `m3` | 7400 | 7250 | Forces `m3` to arrive 50ms after `m2` while `m2`'s 200ms self-report claim window (7200–7400ms, see §4.2.3) is still open — the deliberate non-wake overlap/rejection case (§4.2.4). |
  | `m8` | 8400 | 7830 | Forces `m8` to arrive 30ms after `m5` (paired identical wake, pair A rep. 1) while `m5`'s 50ms claim window (7800–7850ms) is still open. |
  | `m18` | 10400 | 9830 | Forces `m18` to arrive 30ms after `m15` (pair B rep. 1) while `m15`'s 50ms claim window (9800–9850ms) is still open. |
  | `m33` | 13400 | 12830 | Forces `m33` to arrive 30ms after `m30` (pair A rep. 2) while `m30`'s 50ms claim window (12800–12850ms) is still open. |
  | `m43` | 15400 | 14830 | Forces `m43` to arrive 30ms after `m40` (pair B rep. 2) while `m40`'s 50ms claim window (14800–14850ms) is still open. |

  All other messages use the uniform-cadence formula unmodified. The five
  overrides above are the harness's only intentionally-tightened arrivals;
  every other pairing in the schedule is spaced far enough apart (relative
  to the fixed processing durations in §4.2.3) that claims never contend by
  accident — contention only ever occurs where this table says it must.

### 4.2.2 Worker pool and concurrency schedule

- The worker pool size is fixed at **`W = 8`** read-only workers for the
  entire run; the harness never autoscales the pool up or down.
- All 8 workers are idle and claimable starting at `T0`.
- Concurrency is deterministic: each worker claims exactly one unclaimed
  queue entry (a message, or a task dirty-signal per §2.6) at a time, taken
  in strict FIFO arrival order among entries not already claimed, and
  releases its claim (emits its read-only receipt) exactly
  `processing_duration(entry_type)` ms after the claim is taken (§4.2.3). A
  second claim attempt against a resource key that is still held is
  deferred/rejected until the holder releases — it is never granted
  concurrently (this is the mechanism the §4.3 "zero claim overlap" metric
  verifies). With `W = 8` and one entry claimed per worker, at most 8
  entries are ever concurrently claimed system-wide; this is the entire
  concurrency schedule, and it requires no additional random limiting.
- The one designed exception is the faulted claim on `m12` (§4.2's fault
  list): that worker is killed after reading but before emitting its
  receipt, so `m12`'s claim is released for re-claim by the same FIFO order
  during recovery rather than by its own normal processing-duration timer.

### 4.2.3 Deterministic processing durations

Fixed, not random, worker-side read-only processing time from claim to
receipt emission, by entry type:

| Entry type | Processing duration |
| --- | --- |
| Human message | 500 ms |
| Task self-report | 200 ms |
| Peer-Coordinator report | 150 ms |
| Routine wake (identical or near-duplicate) | 50 ms |
| Task dirty-signal (background scheduling item, §2.6) | 300 ms |

A conforming harness must use exactly these durations — they are what makes
the §4.3 p95 metrics computable from the fixed schedule itself, rather than
measured against arbitrary/unspecified production timing. The only
permitted randomness anywhere in the run is the `HARNESS_RANDOM_SEED`
jitter named in §4.2's opening paragraph, and it never applies to these
processing durations.

### 4.2.4 Claim sets: message-to-resource mapping and overlap/rejection cases

Every message claims a resource key of the form `task:<task_id>` — the
pairwise-conflict claim target from §2.3. The mapping is fixed by formula
plus a small set of explicit overrides that create the intentional overlap
cases:

- **Default formula**: for message `m_i` not listed in the override table
  below, `task_id = t_{11 + ((i-1) mod 15)}` (cycles across the 15 Work-lane
  tasks `t11`–`t25`).
- **Overrides** (the deliberate overlap/rejection cases):

  | Message(s) | Resource key | Intended outcome |
  | --- | --- | --- |
  | `m2`, `m3` | `task:t12` | Distinct-payload task self-reports on the same resource key, with `m3` injected inside `m2`'s still-open claim window (§4.2.1). `m3`'s claim attempt must be deferred/rejected until `m2` releases at 7400ms; `m3`'s *effective* claim time is therefore 7400ms, not its 7250ms arrival time. Neither message is ever merged or dropped — this is the deliberate **non-wake** overlap/rejection case, distinct from the routine-wake coalescing cases below. |
  | `m5`, `m8`, `m11` (rep. 1); `m30`, `m33`, `m36` (rep. 2) | `task:t14` | `m5`/`m8` (and, in rep. 2, `m30`/`m33`) are the identical-payload `WAKE:CYCLE` pair on this target and must coalesce to exactly one effective wake (§4.3 metric 3). `m11` (rep. 2: `m36`) is the near-duplicate, non-identical payload on the **same** resource key: it must never coalesce with the pair, and must be served as its own distinct, serialized claim (deferred until the pair's single surviving claim releases if still open) — proving that same-target-but-different-payload is a genuine overlap/rejection case, not a coalescing one. |
  | `m15`, `m18`, `m21` (rep. 1); `m40`, `m43`, `m46` (rep. 2) | `task:t22` | Same structure as the `task:t14` group above, for coalescing pair B and its near-duplicate. |

  All other tasks referenced by the default formula (`t11`, `t13`,
  `t15`–`t21`, `t23`–`t25`) receive at most one concurrently-open claim at
  any point in the schedule under the arrival offsets in §4.2.1 and
  durations in §4.2.3 — i.e. the formula-mapped messages are the harness's
  designed **non-overlap** control cases, contrasted with the explicit
  overlap/rejection cases in the override table.

### 4.2.5 Deriving the §4.3 metrics from the fixed inputs above

Because §4.2.1–§4.2.4 fix every arrival offset, claim target, and
processing duration, the §4.3 acceptance metrics are computed directly from
harness output against these known inputs rather than estimated:

- **Zero claim overlap** (§4.3 metric 1) is checked against every resource
  key in §4.2.4, including the five deliberately-tightened arrivals in
  §4.2.1 — a conforming run must show the deferred/rejected second claim in
  each override row, never two simultaneously-held claims on the same key.
- **Human-message claim p95 < 10s** (§4.3 metric 7) is measured over the
  claim latency (`claim_time - arrival_time`) of the 10 fixed Human-message
  arrivals in §4.2.1 (`m1`, `m7`, `m13`, `m20`, `m25`, `m26`, `m32`, `m38`,
  `m45`, `m50`); under normal (non-faulted) operation each should claim
  near-immediately (well under the 10s bar) since Human messages are never
  coalescing-deferred and only `m45` carries a fault (session deletion).
- **Task-report claim p95 < 30s** (§4.3 metric 8) is measured the same way
  over the 20 fixed task self-report arrivals, including the deliberately
  deferred `m3` (§4.2.4), whose effective claim time (7400ms, not its
  7250ms arrival) is part of the sample the p95 is computed over — a
  harness that instead measured from `m3`'s *arrival* offset without
  accounting for the deferral would understate the true claim latency.
  `m39`'s claim is likewise deliberately withheld (§4.2's restart fault)
  until after the 14,900ms cold restart rather than its 14,600ms arrival;
  its effective claim time (post-restart, not its raw arrival offset) is
  part of this same sample for the identical reason.

### 4.3 Acceptance metrics (all must pass in the same run)

All metrics below are evaluated against the exact `t1`–`t70` / `m1`–`m50`
schedule and fault positions fixed in §4.2 — a run against a different or
re-randomized schedule is not a conforming harness run.

1. **Zero claim overlap** — no two simultaneously-held claims (worker or
   leader) ever have intersecting resource sets (§2.3). Hard invariant.
2. **Zero unreviewed/lost entries** across the crash/restart/session-deletion
   faults in §4.2 — every queue entry present before a fault is either
   already durably actioned or still present and claimable after recovery.
   Concretely: `m8`, `m12`, `m25`, `m26`, `m39`, `m43`, and `m45` (the exact
   entries live at each fault's injection point, including the two
   contract_version 1.1.0 cross-sender faults: `m8`'s mid-coalescing-decision
   leader kill and `m43`'s post-absorption sender-session deletion) must
   each individually resolve to exactly one of {already durably actioned,
   still present and claimable} after recovery — never neither, never both.
   Hard invariant.
3. **Coalescing correctness** — of the 4 identical-duplicate routine-wake
   pairs (`m5`/`m8`, `m15`/`m18`, `m30`/`m33`, `m40`/`m43`), exactly one
   effective wake survives per pair (4 survivors from 8 markers); the 4
   near-duplicate markers (`m11`, `m21`, `m36`, `m46`) and every Human/task/
   peer message remain individually uncoalesced
   (`coalesced_wakes_incorrect_total == 0`).
4. **Message distinctness** — all 50 injected messages (`m1`–`m50`) remain
   individually traceable to a distinct `entry_id` through to disposition;
   no two distinct messages share a disposition record.
5. **Workers never mutate** — zero board/provider/plan writes attributable
   to a worker principal across the entire run (structurally enforced per
   §2.2, verified by audit log inspection).
6. **Single serializing leader with verified readback** — at every point in
   the run, at most one leader fencing token is accepted; every leader
   mutation has a matching readback-verify record before its claim is
   released (including across the `m25`/`m26` leader-kill sub-cases).
7. **Human-message claim p95 < 10s** — measured over the 10 Human messages
   (`m1`, `m7`, `m13`, `m20`, `m25`, `m26`, `m32`, `m38`, `m45`, `m50`).
8. **Task-report claim p95 < 30s** — measured over the 20 task self-report
   messages in §4.2's schedule.
9. **Cross-sender coalescing correctness** (contract_version 1.1.0) — for
   each of the 4 coalescing-eligible pairs, the two markers' distinct fixed
   `sender_session_id`s (`harness-session-A` / `harness-session-B`, §4.2)
   are confirmed distinct in the run's ingress log, and the pair still
   produces exactly one canonical entry with a coalescing receipt naming
   `canonical_entry_id`, `absorbed_source_entry_ids` (matching the
   non-canonical member's `entry_id`), `leader_fencing_token`, and
   `dirty_generation`; `suppressed_duplicate_full_board_scan_total` equals
   `coalesced_wakes_total` for the run. Hard invariant — a coalesce that
   only ever worked for same-sender redelivery would pass metric 3 but fail
   this one.

A harness run that fails any single metric is a release blocker for cutover
past the shadow phase (§2.10 step 2); it is not averaged away by the other
metrics passing.

### 4.4 Harness implementation ownership

The harness itself (fixture generator, fault injector, metrics collector) is
implemented in the Coordinator **plugin** repository, since it must exercise
the plugin's actual leader/worker runtime — this repository only specifies
the scenario shape and acceptance bar above. The plugin's harness run report
should cite this document's §4.3 metric numbering directly so a reviewer can
check the report against this spec without re-deriving it.

## 5. Relationship to existing owners

Both owners below are identified by their stable board role, not by an
embedded task ID — consistent with the exclusion of transient board state
from this repository's shared artifacts (`exclusions` in
[`../contracts/coordinator-policy-contract.json`](../contracts/coordinator-policy-contract.json);
see the header of this document for why). A reader needing the current live
task for either role should resolve it through the Kandev board itself, not
through a copy of the ID pinned in this document.

- **Kandev Host queue primitive owner** — owns guarded exact-entry queue
  operations and identical-routine-wake coalescing at the **Kandev Host**
  layer, including cross-sender routine-identity comparison and the
  coalescing receipt's durable storage (§2.6.1). This RFC's durable queue
  (§2) *consumes* that primitive; it does not reimplement or duplicate it.
  Any gap found between what this RFC needs and what that Host primitive
  currently exposes belongs on that owner's task, not as new queue code
  here or in the plugin.
- **Plugin-first orchestration parent program** — owns Host contracts, the
  plugin scheduler/reconciliation implementation (including consuming the
  Host's coalesced canonical entry and dirty generation to decide what the
  leader schedules next, §2.6/§2.6.1), durable SQLite state, prompt
  composition, and rollout sequencing. This RFC is a design input to that
  program, not a replacement for its planning.
