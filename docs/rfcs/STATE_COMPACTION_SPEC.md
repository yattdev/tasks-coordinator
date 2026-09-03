# Specification: safe Coordinator state compaction

Status: **proposed 2026-09-03**, implementation-ready. Owned by the
plugin-first orchestration program (identified here by stable board role,
not by an embedded transient task ID — consistent with the `exclusions` in
[`../contracts/coordinator-policy-contract.json`](../contracts/coordinator-policy-contract.json)
and with §8 below, which makes the same "no transient task ID" commitment
for the rest of this document; a reader needing the current live parent
task should resolve it through the Kandev board, not through a copy of an
ID pinned here). This document specifies the target design; it does
**not** compact or rewrite the live Coordinator task plan. No compaction
described here has been executed against any live board state by writing
this document.

This spec assumes and must not weaken any invariant in
[`../contracts/coordinator-policy-contract.json`](../contracts/coordinator-policy-contract.json).
It exists because the live Coordinator plan and the follow-up ledger
(`PROMPT.md`'s "Follow up on delegated requests" section, `docs/RUNBOOK.md`'s
ledger conventions) grow unboundedly if every open item is kept inline
forever, and because ad hoc trimming of that plan is exactly the failure mode
`docs/DECISIONS.md`'s continuity rules exist to prevent (silently losing a
durable obligation is worse than a large file).

## 1. Model: materialized current state + append-only audit/archive

Compaction never deletes information; it **moves** information from a
frequently-read "current state" surface into an append-only archive, leaving
behind only what is still live plus a pointer to where the rest went.

- **Materialized current state** — the minimal set of records an agent needs
  to act *right now*: open follow-up entries, active leases/claims, the dirty
  task set, unresolved escalations, and the most recent terminal receipts for
  Done tasks that changed since the last audit. This is what stays inline in
  the live plan (or the plugin's equivalent durable state store).
- **Append-only audit/archive** — every record that rolls out of current
  state is appended, never overwritten or deleted, to an archive log (this
  repository's existing convention: `docs/archive/`, `standups/` retaining
  only the newest five with older ones presumably archived, and
  `docs/LEARNING_LOG.md`'s append-only shape are the prior art this spec
  generalizes).
- A record only *moves* from current to archive when it is **resolved**:
  closed follow-up (evidence captured), released lease, task reached a
  settled Done terminal receipt with no open dependency, or a superseded
  duplicate. An unresolved record is never rolled out merely because the
  file is large — size pressure is handled by archiving *resolved* history
  more aggressively, never by dropping unresolved obligations.

### 1.1 Full-snapshot schema

A **full snapshot** is a complete, self-contained copy of the entire
current-state surface at one instant — not just its hash/count (§3 already
records those, but a hash alone is not restorable; the snapshot must carry
the actual content it hashes):

```
{
  "snapshot_id": "<uuid>",
  "workspace_id": "<workspace>",
  "timestamp": "<UTC ISO-8601>",
  "trigger": "<pre_rollup|scheduled_cadence|manual_pre_restore>",
  "content": {
    "follow_up_entries": [ { "record_id": "<id>", "...": "full record body" } ],
    "active_leases": [ { "record_id": "<id>", "...": "full record body" } ],
    "dirty_task_set": [ { "record_id": "<id>", "...": "full record body" } ],
    "unresolved_escalations": [ { "record_id": "<id>", "...": "full record body" } ],
    "done_terminal_receipts": [ { "record_id": "<id>", "...": "full record body" } ]
  },
  "byte_count": <int>,
  "sha256": "<hex, over the canonical serialization of `content`>",
  "record_count": <int>,
  "record_id_set_sha256": "<hex, see §3>",
  "mutation_log_watermark": "<mutation_id of the last mutation-log entry already reflected in this snapshot's content, or null if none yet>",
  "fencing_token": <int>
}
```

Every field in `content` is a full record body, not a diff or reference —
a snapshot is restorable on its own, with zero dependency on any other
snapshot. `mutation_log_watermark` is the join key to §1.3's mutation log:
it names the exact last mutation already baked into `content`, so replay
(§7) knows precisely which mutation-log entries still need to be applied
on top of this snapshot to reach any later point in time.

### 1.2 Snapshot cadence and retention

- A full snapshot is captured automatically at two triggers:
  1. **`pre_rollup`** — immediately before every rollup (§2), capturing
     exactly the state that becomes `pre_state` in §3's compaction receipt.
     This snapshot is retained at least until every record it lists is
     independently confirmed reachable through either current state or the
     archive (i.e. at least until the rollup that consumed it has itself
     passed §4's set-equality validation).
  2. **`scheduled_cadence`** — every 20 full monitoring cycles, independent
     of whether any rollup threshold has fired, so the maximum replay
     distance (§7) is bounded even during long stretches with nothing to
     roll up. `20` is chosen to keep worst-case replay under one
     rollup-threshold cycle window (§2's default N = 3) times a small
     constant factor, not an arbitrary round number.
  3. A `manual_pre_restore` snapshot may additionally be taken immediately
     before a restore-driven mutation (§7 step 4), purely so that restore
     operation is itself replayable/undoable the same way a rollup is; it
     never replaces the two automatic triggers above.
- **Retention**: the most recent **10** full snapshots (across all trigger
  types combined, ordered by `timestamp`) are retained unconditionally.
  Snapshots older than the 10 most recent may be pruned **only** if every
  mutation-log entry (§1.3) between that snapshot and the next-newer
  retained snapshot has itself already been superseded by (i.e. is already
  reflected in the `content` of) a newer retained snapshot — in other words,
  pruning a snapshot never creates a gap that later replay cannot bridge
  using the next-older retained snapshot plus the mutation log. Pruning
  itself is a mutation of the archive's retained-snapshot index and is
  receipted the same way as a rollup (§3's shape, with `kind:
  "snapshot_prune"` and `rolled_records` naming the pruned `snapshot_id`s,
  never actual state records).

### 1.3 Append-only mutation log for adds/updates/removals

§2's rollup only captures records *leaving* current state (resolved →
archived). That alone is insufficient for deterministic replay: a record
that is **added** to current state, or **updated in place** while still
unresolved, between two snapshots leaves no trace anywhere else, so replay
from an older snapshot could not reconstruct it. The mutation log closes
this gap by recording **every** current-state mutation, not only rollups:

```
{
  "mutation_id": "<monotonic-per-workspace integer or ULID>",
  "workspace_id": "<workspace>",
  "timestamp": "<UTC ISO-8601>",
  "op": "<add|update|remove>",
  "record_id": "<id>",
  "record_kind": "<follow_up|lease|dirty_task|escalation|done_receipt>",
  "before_sha256": "<hex of prior record body, or null if op == add>",
  "after_sha256": "<hex of new record body, or null if op == remove>",
  "fencing_token": <int>
}
```

- Every add/update/remove against the materialized current-state surface —
  whether or not it is rollup-related — appends exactly one mutation-log
  entry, through the single-writer lane (§6), **before** the in-memory/
  on-disk current-state surface itself is considered changed (append-log-
  then-apply, the same ordering §5 already uses for rollup's archive
  append).
- A `remove` mutation-log entry is exactly what a rollup produces per
  rolled record (§2/§3's `rolled_records` are a `record_id`-keyed view over
  a contiguous run of `remove`-op mutation-log entries); the mutation log
  and the archive are two views of the same underlying rollup event, not
  two independent things that could disagree — `rolled_records` in a
  compaction receipt (§3) must be exactly the `remove`-op mutation-log
  entries with the matching `compaction_id` correlation, so the two logs
  can be cross-checked against each other.
- `before_sha256`/`after_sha256` let replay (§7) verify each step against
  the record content it is applying, rather than trusting the `op` field
  alone: replaying an `update` must confirm the current in-memory record's
  hash matches `before_sha256` before applying, and must confirm the result
  hashes to `after_sha256` afterward; a mismatch aborts replay as corrupt
  input rather than silently producing a divergent reconstruction.
- Retention of the mutation log mirrors snapshot retention (§1.2): log
  entries older than the oldest **retained** snapshot's
  `mutation_log_watermark` may be pruned, since no retained snapshot needs
  them for replay; entries newer than that watermark are never pruned until
  superseded by a newer snapshot the same way.

## 2. Automatic rollup thresholds

Rollup runs automatically (no human trigger required) when **either**:

1. **Size threshold**: current-state surface exceeds a configured byte budget
   (default: 80% of the smaller of (a) the host's practical single-file
   comfortable-read size, i.e. use the same ~20KB-per-view-call order of
   magnitude this environment already treats as "large", scaled up for a
   plan file that is expected to be read in sections rather than at once —
   default budget 200KB) — expressed as a percentage so it is tunable without
   being a magic number.
2. **Age/count threshold**: a resolved record has remained inline past N
   cycles after resolution (default N = 3 full monitoring cycles) — giving a
   human reviewer a bounded window to see recently-resolved items inline
   before they roll to archive, without holding them inline indefinitely.

Whichever threshold fires first triggers rollup; both are re-checked every
cycle, not just at startup.

## 3. Exact pre/post byte counts and hashes

Every rollup operation must record, before mutating anything:

```
{
  "compaction_id": "<uuid>",
  "workspace_id": "<workspace>",
  "timestamp": "<UTC ISO-8601>",
  "pre_state": {
    "snapshot_id": "<the §1.1 full-snapshot id captured pre_rollup>",
    "byte_count": <int>,
    "sha256": "<hex>",
    "record_count": <int>,
    "record_id_set_sha256": "<hex, see §4>"
  },
  "rolled_records": [
    {"record_id": "<id>", "kind": "<follow_up|lease|escalation|done_receipt>", "resolved_at": "<ts>", "mutation_id": "<the §1.3 remove-op mutation-log entry for this record>"}
  ],
  "post_state": {
    "snapshot_id": "<the §1.1 full-snapshot id captured immediately after rollup, if one is taken; otherwise null and post_state is reconstructible as pre_state's snapshot replayed forward through exactly the rolled_records mutation-log entries>",
    "byte_count": <int>,
    "sha256": "<hex>",
    "record_count": <int>,
    "record_id_set_sha256": "<hex, see §4>"
  },
  "archive_append": {
    "archive_path": "<path>",
    "byte_count_appended": <int>,
    "sha256_of_appended_bytes": "<hex>",
    "rolled_record_id_set_sha256": "<hex, see §4>"
  },
  "fencing_token": <int>
}
```

`pre_state` and `post_state` are never *only* a hash/count pair in
isolation — each names the full-snapshot (§1.1) or, for `post_state` when no
new snapshot was taken for this specific rollup, the exact mutation-log
range (§1.3) that reconstructs it from `pre_state`'s snapshot. This is what
makes "preserve exact pre/post snapshots per compaction" concretely true:
either an actual full snapshot exists for each side, or the side is a
deterministic, hash-verified function of one that does.

This mirrors the Done terminal-receipt convention (`PROMPT.md`: "audit time,
repository + PR URL, accepted/merged head, local head, remote containment
result, tree status, session/subtask state, and runtime/resource
disposition") — a compaction event is itself receipted the same way a Done
move is. The `fencing_token` field ties the compaction to the single-writer
mutation lane from `../rfcs/PLUGIN_SCALE_RFC.md` §2.1/§2.5 — a compaction is
a mutation like any other and must go through the fenced leader, never a
side-channel writer.

Each `record_id_set_sha256` is computed identically to the contract's own
digest convention (`../contracts/CONTRACT_MAPPING.md` §6): sort the record
IDs in the set, join with `\n`, hash the UTF-8 bytes with SHA-256. This lets
§4's set-equality check compare hashes of record-ID **sets**, not just
integer counts, so two rollups that happen to move the same *number* of
records but different *identities* produce different, detectably-mismatched
hashes.

## 4. Required section-anchor / hash-anchored set-equality and disjointness validation

Before a rollup is considered committed:

1. **Section-anchor validation**: every markdown/anchor reference into the
   current-state surface that existed before rollup (e.g. a cross-task
   pointer like "`see live plan §Follow-up ledger, entry X`") must still
   resolve after rollup — either because the anchor is still present (record
   stayed inline) or because the archive preserves the same anchor text at
   its new location and the current-state surface leaves a forwarding
   pointer (`"see docs/archive/<file>#<anchor>"`). A rollup that breaks an
   existing external reference without leaving a forwarding pointer is
   rejected before commit.
2. **Hash-anchored set-equality validation**: a bare count equation
   (`pre_state.record_count == post_state.record_count +
   len(rolled_records)`) is necessary but **not sufficient** — it cannot
   distinguish "the right records moved" from "some other record silently
   vanished while an unrelated one was double-counted." The validation must
   instead assert, over the actual record-ID **sets** (not just their
   sizes):
   - `pre_state`'s record-ID set equals exactly the **disjoint union** of
     `post_state`'s record-ID set and the `rolled_records` ID set:
     `pre_ids == post_ids ∪ rolled_ids` **and** `post_ids ∩ rolled_ids == ∅`.
     A rollup where a record ID appears in both `post_state` and
     `rolled_records` (counted twice) or in neither (lost) is rejected even
     if the byte-count arithmetic happens to balance.
   - This is checked via the hashes in §3: recompute
     `record_id_set_sha256` over `post_ids ∪ rolled_ids` (after asserting
     the union is disjoint, i.e. `|post_ids| + |rolled_ids| ==
     |post_ids ∪ rolled_ids|`) and require it to equal the recorded
     `pre_state.record_id_set_sha256`. A hash match without the prior
     disjointness assertion is not accepted as proof — two different sets
     can collide in principle, but a set that fails disjointness is already
     known-wrong regardless of what any hash says.
   - Every ID in `rolled_records` must additionally be independently
     verifiable as present in the post-rollup archive append (not just
     claimed) — the `archive_append.rolled_record_id_set_sha256` field in
     §3 must match a hash recomputed directly from the bytes actually
     appended, not copied from the pre-computed `rolled_records` list.
   - This is the same "exact-entry, never a global watermark" discipline the
     contract requires of the queue (`queue_claim_identity.audit_model`),
     applied to compaction: a compaction that can only assert a smaller
     total count, or a matching sum, without naming and hash-verifying which
     exact records moved is rejected, because that shape is indistinguishable
     from silent loss or duplication.
3. Both validations run **before** the pre-rollup current-state file is
   truncated/rewritten. If either fails, the rollup aborts with no mutation
   applied (the archive append and the rewritten current-state file are
   prepared and validated, then swapped in atomically only after both checks
   pass — see §5 for the atomicity mechanism).

## 5. Crash/retry behavior

- Compaction is structured as: (a) compute the new archive-append content and
  the new current-state content in full, in memory/temp storage; (b)
  validate per §4; (c) append to the archive log (append-only, so a partial
  append is detectable — the append includes its own byte count and hash,
  checked on next read); (d) atomically replace the current-state file
  (write-temp-then-rename, or the durable store's native atomic-write
  primitive) only after (c) is durably confirmed.
- A crash between (c) and (d) leaves the archive with a valid appended record
  and the current-state file still in its pre-rollup form — this is safe:
  on restart, the leader detects that the archive already contains the
  intended append (by `compaction_id`) but the current-state file was not
  yet updated, and it **replays step (d) only**, never re-appending to the
  archive (which would duplicate the archived records). This is why every
  compaction event carries an explicit `compaction_id`: retries are
  idempotent keyed on that ID.
- A crash before (c) simply means the compaction never started durably;
  retry begins fresh from (a) with a new `compaction_id`.
- No compaction step is ever retried past (c) with a *different* set of
  `rolled_records` under the same `compaction_id` — the ID and its record set
  are bound together at creation, matching the queue's exact-entry identity
  convention.
- **Replay crash/retry (§7)**: forward replay from a snapshot through a
  range of mutation-log entries is itself checkpointed after each
  successfully-applied `mutation_id` (a monotonic counter, so "successfully
  applied up to `mutation_id = k`" is a single comparable value, not a set).
  A crash mid-replay resumes by re-reading that checkpoint and continuing
  from `k+1` — it never restarts from the base snapshot, and it never
  re-applies `mutation_id <= k` (each mutation's `before_sha256`/
  `after_sha256` check, per §1.3, would itself detect and reject a
  duplicate re-application, since the "before" state would no longer match
  after the first successful apply — this is a second, independent guard
  on top of the checkpoint).

## 6. Single-writer fencing

- Compaction is a mutation of the live plan/current-state surface and
  therefore runs exclusively through the fenced leader
  (`../rfcs/PLUGIN_SCALE_RFC.md` §2.1/§2.5), carrying the leader's current
  fencing token in the compaction receipt (§3).
- A compaction proposal computed by a read-only worker (e.g. "this workspace
  is over the size threshold, here is a proposed rollup set") is only ever a
  **recommendation** with no mutation authority — consistent with
  `worker_helper_receipts.workers_never_mutate`. Only the leader may execute
  steps (c)/(d) of §5.
- If leadership changes mid-compaction (old leader's lease expires between
  steps), the new leader's higher fencing token causes any late-arriving
  write from the old leader to be rejected (per the scale RFC's fencing
  model), and the new leader resumes from whatever the archive/current-state
  pair durably shows per the crash/retry rules in §5 — it does not assume
  the old leader's in-flight compaction succeeded or failed without checking
  the archive for the `compaction_id`.

## 7. Restore procedure

To restore a specific historical state (e.g. to investigate a regression, or
to recover from a rollup that is later found to have broken an external
reference despite §4's checks), or to reconstruct current state as of any
point in time `T`:

1. **Identify the target point.** Either a specific `compaction_id` (restore
   to immediately before or after that rollup), or an arbitrary timestamp
   `T`, resolved against the append-only archive's own ordering — the
   archive plus the mutation log (§1.3) is itself the durable history, so no
   separate backup mechanism is required.
2. **Select the base snapshot.** Choose the newest retained full snapshot
   (§1.1) whose `timestamp <= T` (for a `compaction_id` target, its
   `pre_state.snapshot_id`, per §3, is always such a snapshot and may be
   used directly without search). Call its `mutation_log_watermark` value
   `k0`.
3. **Deterministic forward replay.** Starting from the chosen snapshot's
   `content` (§1.1) as the working state, fetch every mutation-log entry
   (§1.3) with `mutation_id > k0` up to and including the last entry with
   `timestamp <= T`, in ascending `mutation_id` order, and apply each in
   turn:
   - `add`: insert a new record with the given `record_id`; verify the
     resulting record's hash equals `after_sha256`.
   - `update`: verify the working state's current record for `record_id`
     hashes to `before_sha256` (abort as corrupt input if not — see §5's
     replay crash/retry guard), replace its content, and verify the result
     hashes to `after_sha256`.
   - `remove`: verify the working state's current record hashes to
     `before_sha256`, then delete it from the working state (its content
     remains permanently available in the archive append that the matching
     `compaction_id`/`rolled_records` entry named, per §3 — restore never
     needs to "undelete" from anywhere else).
   This process is a pure function of `(snapshot.content, ordered
   mutation-log subsequence)`: two independent implementations given the
   same snapshot and mutation range must produce byte-identical
   reconstructed state, which is what "deterministic" means here — there is
   no other input (no wall-clock behavior, no implementation-specific
   ordering choice beyond ascending `mutation_id`).
4. **Verify the reconstruction.** Compute `record_id_set_sha256` (§3) over
   the reconstructed working state and confirm it matches the value that
   would be expected from chaining the intervening compaction receipts'
   `post_state.record_id_set_sha256` values (or, if `T` lands strictly
   between two compactions, the appropriate intermediate hash derivable from
   the mutation log alone per §1.3's disjointness guarantee). A mismatch
   means the archive/mutation-log/snapshot chain is itself corrupt between
   the snapshot and `T` — restore must fail closed and report exactly which
   `mutation_id` broke the chain, never silently return a best-effort
   reconstruction.
5. **Read-only vs. mutating restore.** A restore performed purely to inspect
   historical state (steps 1–4 above) is read-only and requires no leader
   fencing — it never writes to the archive, the mutation log, or current
   state. A restore that **re-activates** a reconstructed record as a live
   obligation again (e.g. "actually this follow-up wasn't resolved") *is* a
   mutation of current state: it must go through the fenced leader like any
   other write, append its own `add`-op mutation-log entry (§1.3) for the
   reactivated record, and carry its own receipt in the same shape as §3
   (with `kind: "restore_reactivation"` and `rolled_records` replaced by a
   `reactivated_records` list of the same shape). This mutation is subject
   to the same crash/retry idempotency as any other (§5): it carries an
   explicit `restore_id`, and a crash after the mutation-log append but
   before current-state is updated resumes by replaying only the
   current-state write, never re-appending the mutation-log entry.
6. Never restore by rewriting the live Coordinator plan directly from this
   specification or from this task; per this task's boundaries, the live
   plan is out of scope here. This spec constrains what the plugin-native
   implementation must do; execution against the actual live plan is the
   plugin-first program's responsibility once implemented and reviewed
   there.

## 8. What this spec explicitly does not change

- It does not touch the live Coordinator task plan (the parent program's
  plan or any other live task's plan) — this is a specification document
  only, and per the exclusions in
  [`../contracts/coordinator-policy-contract.json`](../contracts/coordinator-policy-contract.json)
  (`transient_task_ids`), this spec deliberately does not name any specific
  transient task ID.
- It does not relax the Done terminal-integrity gate; a compacted Done
  terminal receipt remains subject to the same shallow-verify-if-unchanged /
  deep-audit-if-new-or-suspicious rule in `PROMPT.md` — compaction only
  changes *where* the receipt is stored (current-state vs. archive), never
  whether it is trusted without re-verification when the underlying task
  changes again.
- It does not introduce a new wake source, timer, or scheduler; rollup
  triggers are evaluated during an already-live cycle (§2), never on an
  independent timer (consistent with `PROMPT.md`/README: "KanDev routines
  are the SOLE wake source").
