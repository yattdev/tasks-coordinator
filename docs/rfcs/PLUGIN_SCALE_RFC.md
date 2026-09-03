# RFC: Coordinator plugin scale/load architecture and burst harness

Status: **proposed 2026-09-03**, implementation-ready. Owned by the plugin-first
orchestration program (parent task `1e46d457-6869-4750-bf97-4640a8df3b68`);
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
- **Injected faults**, run exactly once each per full harness pass, at these
  fixed positions in the `m1`..`m50` timeline (not "at least once" at an
  arbitrary point — a specific, reproducible position each run):
  - Kill a worker mid-claim: kill the worker holding the claim for `m12`
    (a task self-report) after it has read the entry but before it emits its
    read-only recommendation.
  - Kill the leader mid-mutation, sub-case A (before readback verify): kill
    the leader during the mutation triggered by `m25` (the last message of
    the first repetition), immediately after the write and before the
    readback-verify step.
  - Kill the leader mid-mutation, sub-case B (after readback verify): kill
    the leader during the mutation triggered by `m26` (the first message of
    the second repetition), immediately after the readback-verify step
    completes but before the claim is released.
  - Restart the whole process/session set from durable storage only: after
    `m38` has been fully disposed (durably actioned) and before `m39` is
    injected, halt every process/session and cold-restart from durable
    storage alone; resume injection at `m39`.
  - Delete a session that has an unread queued message: target the session
    holding `m45` (a Human message, per the slot-20/45 mapping in the
    schedule table above); delete it only after asserting, per the
    2026-09-03 decision, whether a recovery read of `m45` already completed
    or is provably impossible — the harness records which case occurred, it
    does not assume either.

### 4.3 Acceptance metrics (all must pass in the same run)

All metrics below are evaluated against the exact `t1`–`t70` / `m1`–`m50`
schedule and fault positions fixed in §4.2 — a run against a different or
re-randomized schedule is not a conforming harness run.

1. **Zero claim overlap** — no two simultaneously-held claims (worker or
   leader) ever have intersecting resource sets (§2.3). Hard invariant.
2. **Zero unreviewed/lost entries** across the crash/restart/session-deletion
   faults in §4.2 — every queue entry present before a fault is either
   already durably actioned or still present and claimable after recovery.
   Concretely: `m12`, `m25`, `m26`, `m39`, and `m45` (the exact entries live
   at each fault's injection point) must each individually resolve to
   exactly one of {already durably actioned, still present and claimable}
   after recovery — never neither, never both. Hard invariant.
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

- Host queue primitive owner `ca015838-e5cf-4294-b3bb-9c50576a5fe6` owns
  guarded exact-entry queue operations and identical-routine-wake
  coalescing at the **Kandev Host** layer. This RFC's durable queue (§2)
  *consumes* that primitive; it does not reimplement or duplicate it. Any
  gap found between what this RFC needs and what that Host primitive
  currently exposes belongs on that task, not as new queue code here or in
  the plugin.
- Parent program `1e46d457-6869-4750-bf97-4640a8df3b68` owns Host contracts,
  the plugin scheduler/reconciliation implementation, durable SQLite state,
  prompt composition, and rollout sequencing. This RFC is a design input to
  that program, not a replacement for its planning.
