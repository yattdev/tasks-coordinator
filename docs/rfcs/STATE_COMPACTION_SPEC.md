# Specification: safe Coordinator state compaction

Status: **proposed 2026-09-03**, implementation-ready. Owned by the
plugin-first orchestration program (parent task
`1e46d457-6869-4750-bf97-4640a8df3b68`). This document specifies the target
design; it does **not** compact or rewrite the live Coordinator task plan.
No compaction described here has been executed against any live board state
by writing this document.

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
    "byte_count": <int>,
    "sha256": "<hex>",
    "record_count": <int>
  },
  "rolled_records": [
    {"record_id": "<id>", "kind": "<follow_up|lease|escalation|done_receipt>", "resolved_at": "<ts>"}
  ],
  "post_state": {
    "byte_count": <int>,
    "sha256": "<hex>",
    "record_count": <int>
  },
  "archive_append": {
    "archive_path": "<path>",
    "byte_count_appended": <int>,
    "sha256_of_appended_bytes": "<hex>"
  },
  "fencing_token": <int>
}
```

This mirrors the Done terminal-receipt convention (`PROMPT.md`: "audit time,
repository + PR URL, accepted/merged head, local head, remote containment
result, tree status, session/subtask state, and runtime/resource
disposition") — a compaction event is itself receipted the same way a Done
move is. The `fencing_token` field ties the compaction to the single-writer
mutation lane from `../rfcs/PLUGIN_SCALE_RFC.md` §2.1/§2.5 — a compaction is
a mutation like any other and must go through the fenced leader, never a
side-channel writer.

## 4. Required section-anchor / set-equality validation

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
2. **Set-equality validation**: the set of record IDs in
   `pre_state.record_count` must equal exactly `post_state.record_count +
   len(rolled_records)`, and every ID in `rolled_records` must be
   independently verifiable as present in the post-rollup archive append
   (not just claimed). This is the same "exact-entry, never a global
   watermark" discipline the contract requires of the queue
   (`queue_claim_identity.audit_model`), applied to compaction: a compaction
   that can only assert a smaller total count without naming which records
   moved is rejected, because that shape is indistinguishable from silent
   loss.
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
reference despite §4's checks):

1. Identify the target `compaction_id` (or "pre-compaction" state, i.e.
   before any rollup) from the append-only archive's own ordering — the
   archive is itself the durable history, so no separate backup mechanism is
   required.
2. Reconstruct the current-state surface **as of** that point by starting
   from the oldest retained full current-state snapshot at or before the
   target and replaying archive entries **backwards is not required** —
   restoration replays forward from a known-good full snapshot plus the
   ordered archive entries after it, because the archive stores what was
   *removed*, not a diff needed to reapply. In practice: the record that was
   archived is, by construction, still fully present in the archive; restore
   means copying the archived record(s) back into a working current-state
   view for read purposes. This is inherently non-destructive to the
   archive — restoration reads the archive, it never truncates or mutates
   it.
3. A restore for investigation purposes is read-only and does not require
   leader fencing. A restore that re-activates an archived record as a live
   obligation again (e.g. "actually this follow-up wasn't resolved") **is** a
   mutation of current state and must go through the fenced leader like any
   other compaction-adjacent write, with its own receipt.
4. Never restore by rewriting the live Coordinator plan directly from this
   specification or from this task; per this task's boundaries, the live
   plan is out of scope here. This spec constrains what the plugin-native
   implementation must do; execution against the actual live plan is the
   plugin-first program's responsibility once implemented and reviewed
   there.

## 8. What this spec explicitly does not change

- It does not touch the live Coordinator task plan (`43526f71-...`'s parent
  or any other live task's plan) — this is a specification document only.
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
