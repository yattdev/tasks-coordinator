#!/usr/bin/env python3
"""Portable reference implementation of the mutation-log replay algorithm
specified in ``docs/rfcs/STATE_COMPACTION_SPEC.md`` §1.3 and §7.

Purpose
-------
This module has NO runtime dependency on the Coordinator knowledge-repository
checkout, the Kandev board, or any live task state — it operates purely on
in-memory snapshot/mutation-log/payload-store data structures passed in by
the caller. It exists so the spec's claim that mutation entries are
"replay sufficient" (add/update/remove can be verified and replayed at
arbitrary T) is independently, testably true, not merely descriptive —
mirroring the "portable validator with tests" convention
``docs/contracts/validate_contract.py`` established for the policy contract.

It is a *reference/conformance* implementation, not the plugin-first
program's actual Kandev-native compaction/replay engine — that implementation
lives in the plugin repository once built, and may differ in storage
backend, language, or performance characteristics as long as it satisfies
the same observable contract this module checks.

Stdlib only. No third-party dependencies. Python >= 3.8.
"""

import hashlib
import json


class ReplayError(Exception):
    """Raised when replay/verification detects corrupt or inconsistent input."""


def canonical_hash(body):
    """sha256 over a canonical JSON serialization of a record body.

    Same convention as ``docs/contracts/validate_contract.py:compute_digest``
    and ``CONTRACT_MAPPING.md`` §6: ``sort_keys=True``, no extra whitespace,
    UTF-8 -- reproducible in any language.
    """
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def record_id_set_sha256(record_ids):
    """§3/§4's record_id_set_sha256: sort the IDs, join with '\\n', sha256
    the UTF-8 bytes.
    """
    joined = "\n".join(sorted(record_ids))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def resolve_payload(side, payload_store):
    """Resolve a mutation-log entry's ``before``/``after`` side to its body.

    ``side`` is ``None`` (§1.3: ``before`` is null iff op == add, ``after``
    is null iff op == remove) or a dict of shape
    ``{"storage": "inline", "sha256": "<hex>", "body": {...}}`` or
    ``{"storage": "content_ref", "sha256": "<hex>", "ref": "<locator>"}``.

    Returns the resolved body (a dict), verified against the declared
    ``sha256``. Raises ``ReplayError`` if a ``content_ref`` cannot be
    resolved (unavailable/pruned/missing -- §1.3's fail-closed availability
    rule) or if the resolved body's hash does not match the declared
    ``sha256`` (corrupt or substituted content).
    """
    if side is None:
        return None
    storage = side.get("storage")
    declared_hash = side.get("sha256")
    if storage == "inline":
        body = side.get("body")
    elif storage == "content_ref":
        ref = side.get("ref")
        if payload_store is None or ref not in payload_store:
            raise ReplayError(
                f"content_ref {ref!r} is not available (pruned, missing, or "
                "no payload store supplied); replay must abort as corrupt "
                "input, never silently skip the mutation"
            )
        body = payload_store[ref]
    else:
        raise ReplayError(f"unknown storage kind {storage!r}")
    recomputed = canonical_hash(body)
    if recomputed != declared_hash:
        raise ReplayError(
            f"resolved body hash {recomputed!r} does not match declared "
            f"sha256 {declared_hash!r} (storage={storage!r})"
        )
    return body


def apply_mutation(state, mutation, payload_store=None):
    """Apply one mutation-log entry to ``state`` (a dict of
    ``record_id -> body``), verifying before/after hashes per §1.3/§7.

    Returns a *new* state dict; does not mutate the input in place,
    mirroring the spec's "prepare in full, validate, swap" discipline
    (§5).
    """
    op = mutation["op"]
    record_id = mutation["record_id"]
    new_state = dict(state)

    if op == "add":
        if record_id in state:
            raise ReplayError(f"add for already-present record_id {record_id!r}")
        if mutation.get("compaction_id") is not None:
            raise ReplayError(
                f"add mutation for {record_id!r} must carry compaction_id: "
                "null (add is never rollup-driven)"
            )
        after_body = resolve_payload(mutation.get("after"), payload_store)
        if after_body is None:
            raise ReplayError(f"add mutation for {record_id!r} is missing 'after'")
        new_state[record_id] = after_body

    elif op == "update":
        if record_id not in state:
            raise ReplayError(f"update for missing record_id {record_id!r}")
        if mutation.get("compaction_id") is not None:
            raise ReplayError(
                f"update mutation for {record_id!r} must carry "
                "compaction_id: null (update is never rollup-driven)"
            )
        before_body = resolve_payload(mutation.get("before"), payload_store)
        if before_body is None or canonical_hash(state[record_id]) != canonical_hash(before_body):
            raise ReplayError(
                f"update before-state mismatch for {record_id!r}: working "
                "state does not match the mutation's declared before body "
                "(possible duplicate replay or corrupt input)"
            )
        after_body = resolve_payload(mutation.get("after"), payload_store)
        if after_body is None:
            raise ReplayError(f"update mutation for {record_id!r} is missing 'after'")
        new_state[record_id] = after_body

    elif op == "remove":
        if record_id not in state:
            raise ReplayError(f"remove for missing record_id {record_id!r}")
        if mutation.get("compaction_id") is None:
            raise ReplayError(
                f"remove mutation for {record_id!r} is missing the required "
                "compaction_id correlation (§1.3: every remove entry MUST "
                "carry the compaction_id of the rollup that produced it)"
            )
        before_body = resolve_payload(mutation.get("before"), payload_store)
        if before_body is None or canonical_hash(state[record_id]) != canonical_hash(before_body):
            raise ReplayError(
                f"remove before-state mismatch for {record_id!r}: working "
                "state does not match the mutation's declared before body"
            )
        del new_state[record_id]

    else:
        raise ReplayError(f"unknown op {op!r}")

    return new_state


def _index_compaction_receipts(compaction_receipts):
    """Normalize a ``compaction_receipts`` argument into a
    ``compaction_id -> receipt`` dict.

    Accepts ``None`` (no receipts supplied at all), a dict already keyed by
    ``compaction_id``, or an iterable of receipt dicts each carrying its own
    ``compaction_id`` field (the same shape ``check_compaction_correlation``
    already expects for its ``compaction_receipt`` argument).
    """
    if compaction_receipts is None:
        return {}
    if isinstance(compaction_receipts, dict):
        return dict(compaction_receipts)
    return {receipt["compaction_id"]: receipt for receipt in compaction_receipts}


def replay(snapshot_content, mutation_log, payload_store=None,
           target_mutation_id=None, target_timestamp=None,
           compaction_receipts=None):
    """Deterministically replay ``mutation_log`` on top of
    ``snapshot_content`` up to and including ``target_mutation_id`` and/or
    ``target_timestamp`` (§7 step 3), in ascending ``mutation_id`` order.

    ``snapshot_content`` is a dict of ``record_id -> body`` (the working
    state). ``compaction_receipts`` is the relevant compaction receipt set
    (``None``, a ``compaction_id -> receipt`` dict, or an iterable of
    receipt dicts) that every ``remove`` mutation actually replayed must
    correlate against, per §1.3/§7 step 3's cross-check: "a `remove` entry
    with a `compaction_id` that does not correlate to any known compaction
    receipt is corrupt input, not a silently-accepted orphan removal." This
    correlation is enforced here, inside ``replay()`` itself -- it is not a
    detached optional helper the caller might forget to invoke. Returns the
    reconstructed state; raises ``ReplayError`` on any corrupt/inconsistent
    input (an absent receipt set, an unknown/nonexistent `compaction_id`, or
    a substituted/mismatched receipt, exactly as much as a hash mismatch or
    duplicate `mutation_id` would) rather than returning a best-effort
    partial result (§7 step 4's fail-closed rule).
    """
    ids = [m["mutation_id"] for m in mutation_log]
    if len(ids) != len(set(ids)):
        raise ReplayError(
            "duplicate mutation_id in mutation log; replay order is "
            "ambiguous and cannot be deterministic"
        )
    # Ascending mutation_id order is the *only* ordering input (§1.3/§7):
    # sorting here rather than trusting input order is what makes replay a
    # pure function of the (snapshot, log) pair regardless of how the log
    # was fetched/paginated.
    ordered = sorted(mutation_log, key=lambda m: m["mutation_id"])

    # Determine the subsequence that will actually be applied under the
    # target_mutation_id/target_timestamp cutoffs before doing any
    # correlation work, so a receipt is only required for compaction_ids
    # this call will actually replay through.
    applied = []
    for mutation in ordered:
        if target_mutation_id is not None and mutation["mutation_id"] > target_mutation_id:
            break
        if target_timestamp is not None and mutation["timestamp"] > target_timestamp:
            break
        applied.append(mutation)

    receipts_by_id = _index_compaction_receipts(compaction_receipts)
    remove_compaction_ids = {
        m["compaction_id"] for m in applied
        if m["op"] == "remove" and m.get("compaction_id") is not None
    }
    for compaction_id in remove_compaction_ids:
        receipt = receipts_by_id.get(compaction_id)
        if receipt is None:
            raise ReplayError(
                f"a remove mutation being replayed references compaction_id "
                f"{compaction_id!r}, but no matching receipt was found in "
                "the supplied compaction_receipts set (absent receipt set, "
                "or an unknown/nonexistent compaction_id); a remove cannot "
                "be replayed without correlating it against its rollup "
                "receipt"
            )
        # Full cross-check, not just "a receipt with this id exists": the
        # receipt's rolled_records must be exactly the remove-op entries
        # carrying this compaction_id in the full mutation_log (§1.3), so a
        # substituted or mismatched receipt (wrong rolled_records for a
        # correctly-named compaction_id) is caught the same way an unknown
        # id is.
        check_compaction_correlation(receipt, mutation_log)

    state = dict(snapshot_content)
    for mutation in applied:
        state = apply_mutation(state, mutation, payload_store)
    return state


def verify_set_equality(pre_ids, post_ids, rolled_ids):
    """§4's hash-anchored set-equality + disjointness validation:
    ``pre_ids == post_ids ∪ rolled_ids`` and ``post_ids ∩ rolled_ids == ∅``.

    Returns True on success; raises ``ReplayError`` describing exactly
    which condition failed.
    """
    post_set, rolled_set, pre_set = set(post_ids), set(rolled_ids), set(pre_ids)
    if len(post_set) + len(rolled_set) != len(post_set | rolled_set):
        raise ReplayError(
            "post_ids and rolled_ids are not disjoint: a record_id appears "
            "in both (double-counted) or the inputs contain duplicates"
        )
    union = post_set | rolled_set
    if pre_set != union:
        missing = union - pre_set
        extra = pre_set - union
        raise ReplayError(
            "pre_ids does not equal post_ids ∪ rolled_ids "
            f"(unexpected in union: {sorted(missing)}, "
            f"missing from union: {sorted(extra)})"
        )
    return True


def check_fencing(incoming_token, current_token):
    """§6's fencing rule: a write's fencing_token must be >= the leader's
    current fencing token. A late-arriving write carrying a lower
    (superseded) token is rejected.
    """
    if incoming_token < current_token:
        raise ReplayError(
            f"stale fencing_token {incoming_token} < current leader fencing "
            f"token {current_token}; write rejected (superseded leader)"
        )
    return True


def check_compaction_correlation(compaction_receipt, mutation_log):
    """§1.3's cross-check: a compaction receipt's ``rolled_records`` must be
    exactly the ``remove``-op mutation-log entries carrying the matching
    ``compaction_id`` -- the mutation log and the archive/receipt are two
    views of the same rollup event, not two independent things that could
    disagree.
    """
    compaction_id = compaction_receipt["compaction_id"]
    log_removed_ids = {
        m["record_id"] for m in mutation_log
        if m["op"] == "remove" and m.get("compaction_id") == compaction_id
    }
    receipt_ids = {r["record_id"] for r in compaction_receipt["rolled_records"]}
    if log_removed_ids != receipt_ids:
        raise ReplayError(
            "compaction receipt rolled_records does not match mutation-log "
            f"remove entries for compaction_id {compaction_id!r}: "
            f"receipt={sorted(receipt_ids)!r} log={sorted(log_removed_ids)!r}"
        )
    return True


def prunable_snapshot_ids(snapshots, keep_count=10):
    """§1.2 retention: the newest ``keep_count`` full snapshots (across all
    trigger types, ordered by ``timestamp``) are retained unconditionally.
    Returns the ``snapshot_id``s of snapshots outside that window that MAY
    be considered for pruning -- the caller must still separately confirm
    the mutation-log-bridging condition in the prose (every mutation-log
    entry between a candidate and the next-newer retained snapshot is
    already reflected in a newer retained snapshot) before actually pruning
    any given one; this helper only applies the count-based floor.
    """
    ordered = sorted(snapshots, key=lambda s: s["timestamp"], reverse=True)
    return [s["snapshot_id"] for s in ordered[keep_count:]]


def prunable_mutation_ids(mutation_log, retained_snapshots):
    """§1.3 retention: mutation-log entries older than the oldest retained
    snapshot's ``mutation_log_watermark`` may be pruned, since no retained
    snapshot needs them for replay.
    """
    watermarks = [
        s["mutation_log_watermark"] for s in retained_snapshots
        if s.get("mutation_log_watermark") is not None
    ]
    if not watermarks:
        return []
    watermark = min(watermarks)
    return [m["mutation_id"] for m in mutation_log if m["mutation_id"] <= watermark]
