#!/usr/bin/env python3
"""Tests for replay_reference.py -- the reference implementation of
docs/rfcs/STATE_COMPACTION_SPEC.md's mutation-log replay algorithm.

Stdlib-only (unittest). Run with:
    python3 -m unittest docs/rfcs/test_replay_reference.py -v
or, from this directory:
    python3 test_replay_reference.py
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import replay_reference as rr  # noqa: E402


def mk_side(body):
    """Build an inline `before`/`after` side for a given body dict."""
    return {"storage": "inline", "sha256": rr.canonical_hash(body), "body": body}


def mk_ref_side(ref, body):
    """Build a content_ref `before`/`after` side; caller must also register
    `body` under `ref` in a payload_store dict passed to replay/apply."""
    return {"storage": "content_ref", "sha256": rr.canonical_hash(body), "ref": ref}


class TestDeterministicReplayOrder(unittest.TestCase):
    def test_add_update_remove_sequence_reconstructs_expected_state(self):
        body_v1 = {"title": "follow up A", "status": "open"}
        body_v2 = {"title": "follow up A", "status": "resolved"}
        log = [
            {
                "mutation_id": 1, "workspace_id": "w1", "timestamp": "2026-09-03T00:00:01Z",
                "op": "add", "record_id": "f1", "record_kind": "follow_up",
                "before": None, "after": mk_side(body_v1),
                "compaction_id": None, "fencing_token": 1,
            },
            {
                "mutation_id": 2, "workspace_id": "w1", "timestamp": "2026-09-03T00:00:02Z",
                "op": "update", "record_id": "f1", "record_kind": "follow_up",
                "before": mk_side(body_v1), "after": mk_side(body_v2),
                "compaction_id": None, "fencing_token": 1,
            },
            {
                "mutation_id": 3, "workspace_id": "w1", "timestamp": "2026-09-03T00:00:03Z",
                "op": "remove", "record_id": "f1", "record_kind": "follow_up",
                "before": mk_side(body_v2), "after": None,
                "compaction_id": "c-1", "fencing_token": 1,
            },
        ]
        receipt = {"compaction_id": "c-1", "rolled_records": [{"record_id": "f1"}]}
        state = rr.replay({}, log, compaction_receipts=[receipt])
        self.assertEqual(state, {})

    def test_replay_is_order_independent_of_input_list_order(self):
        # Feeding the log in reverse (or any shuffled) order must produce
        # the same result, since replay sorts by mutation_id itself -- the
        # only "order" input the spec permits.
        body = {"lease_owner": "leader-1"}
        log_forward = [
            {
                "mutation_id": 5, "workspace_id": "w1", "timestamp": "t5",
                "op": "add", "record_id": "lease-1", "record_kind": "lease",
                "before": None, "after": mk_side(body),
                "compaction_id": None, "fencing_token": 2,
            },
        ]
        log_reversed = list(reversed(log_forward))  # trivial here, but proves sort-by-id
        state_a = rr.replay({}, log_forward)
        state_b = rr.replay({}, log_reversed)
        self.assertEqual(state_a, state_b)
        self.assertEqual(state_a, {"lease-1": body})

    def test_duplicate_mutation_id_is_rejected_as_ambiguous(self):
        body = {"x": 1}
        log = [
            {
                "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
                "op": "add", "record_id": "r1", "record_kind": "escalation",
                "before": None, "after": mk_side(body),
                "compaction_id": None, "fencing_token": 1,
            },
            {
                "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
                "op": "add", "record_id": "r2", "record_kind": "escalation",
                "before": None, "after": mk_side(body),
                "compaction_id": None, "fencing_token": 1,
            },
        ]
        with self.assertRaises(rr.ReplayError):
            rr.replay({}, log)

    def test_replay_to_arbitrary_target_mutation_id_stops_partway(self):
        body1 = {"n": 1}
        body2 = {"n": 2}
        log = [
            {
                "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
                "op": "add", "record_id": "r1", "record_kind": "dirty_task",
                "before": None, "after": mk_side(body1),
                "compaction_id": None, "fencing_token": 1,
            },
            {
                "mutation_id": 2, "workspace_id": "w1", "timestamp": "t2",
                "op": "update", "record_id": "r1", "record_kind": "dirty_task",
                "before": mk_side(body1), "after": mk_side(body2),
                "compaction_id": None, "fencing_token": 1,
            },
        ]
        # Replay to arbitrary T (here: mutation_id 1) reconstructs the
        # intermediate state, not just the final one.
        state_at_1 = rr.replay({}, log, target_mutation_id=1)
        self.assertEqual(state_at_1, {"r1": body1})
        state_at_2 = rr.replay({}, log, target_mutation_id=2)
        self.assertEqual(state_at_2, {"r1": body2})


class TestBodyReferenceHashVerification(unittest.TestCase):
    def test_inline_body_add_is_verified_and_applied(self):
        body = {"escalation": "destructive_or_irreversible"}
        mutation = {
            "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
            "op": "add", "record_id": "e1", "record_kind": "escalation",
            "before": None, "after": mk_side(body),
            "compaction_id": None, "fencing_token": 1,
        }
        state = rr.apply_mutation({}, mutation)
        self.assertEqual(state, {"e1": body})

    def test_content_ref_add_resolves_from_payload_store(self):
        body = {"escalation": "security_or_trust_boundary"}
        ref = f"sha256:{rr.canonical_hash(body)}"
        payload_store = {ref: body}
        mutation = {
            "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
            "op": "add", "record_id": "e2", "record_kind": "escalation",
            "before": None, "after": mk_ref_side(ref, body),
            "compaction_id": None, "fencing_token": 1,
        }
        state = rr.apply_mutation({}, mutation, payload_store)
        self.assertEqual(state, {"e2": body})

    def test_content_ref_unavailable_aborts_replay_as_corrupt(self):
        # Regression guard for the "before_sha256-only" defect this schema
        # closed: a content_ref that cannot be dereferenced must abort
        # replay, never silently skip the mutation or substitute an empty
        # body.
        body = {"escalation": "security_or_trust_boundary"}
        ref = f"sha256:{rr.canonical_hash(body)}"
        mutation = {
            "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
            "op": "add", "record_id": "e3", "record_kind": "escalation",
            "before": None, "after": mk_ref_side(ref, body),
            "compaction_id": None, "fencing_token": 1,
        }
        with self.assertRaises(rr.ReplayError):
            rr.apply_mutation({}, mutation, payload_store={})  # ref pruned/missing

    def test_tampered_inline_body_fails_hash_verification(self):
        body = {"n": 1}
        side = mk_side(body)
        side["body"] = {"n": 999}  # tamper after hashing
        mutation = {
            "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
            "op": "add", "record_id": "r1", "record_kind": "dirty_task",
            "before": None, "after": side,
            "compaction_id": None, "fencing_token": 1,
        }
        with self.assertRaises(rr.ReplayError):
            rr.apply_mutation({}, mutation)

    def test_content_ref_returning_substituted_body_fails_hash_verification(self):
        # A payload store returning stale/substituted content for a ref
        # must be caught by the sha256 check, not trusted blindly.
        real_body = {"n": 1}
        fake_body = {"n": 2}
        ref = f"sha256:{rr.canonical_hash(real_body)}"
        payload_store = {ref: fake_body}
        mutation = {
            "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
            "op": "add", "record_id": "r1", "record_kind": "dirty_task",
            "before": None, "after": mk_ref_side(ref, real_body),
            "compaction_id": None, "fencing_token": 1,
        }
        with self.assertRaises(rr.ReplayError):
            rr.apply_mutation({}, mutation, payload_store)

    def test_update_before_state_mismatch_is_rejected(self):
        wrong_prior = {"n": 999}
        new_body = {"n": 2}
        state = {"r1": {"n": 1}}
        mutation = {
            "mutation_id": 2, "workspace_id": "w1", "timestamp": "t2",
            "op": "update", "record_id": "r1", "record_kind": "dirty_task",
            "before": mk_side(wrong_prior), "after": mk_side(new_body),
            "compaction_id": None, "fencing_token": 1,
        }
        with self.assertRaises(rr.ReplayError):
            rr.apply_mutation(state, mutation)


class TestCompactionCorrelation(unittest.TestCase):
    def test_remove_without_compaction_id_is_rejected(self):
        body = {"n": 1}
        state = {"r1": body}
        mutation = {
            "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
            "op": "remove", "record_id": "r1", "record_kind": "dirty_task",
            "before": mk_side(body), "after": None,
            "compaction_id": None, "fencing_token": 1,
        }
        with self.assertRaises(rr.ReplayError):
            rr.apply_mutation(state, mutation)

    def test_add_or_update_with_nonnull_compaction_id_is_rejected(self):
        body = {"n": 1}
        add_mutation = {
            "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
            "op": "add", "record_id": "r1", "record_kind": "dirty_task",
            "before": None, "after": mk_side(body),
            "compaction_id": "c-1", "fencing_token": 1,
        }
        with self.assertRaises(rr.ReplayError):
            rr.apply_mutation({}, add_mutation)

    def test_receipt_rolled_records_matches_log_remove_entries(self):
        body = {"n": 1}
        log = [
            {
                "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
                "op": "remove", "record_id": "r1", "record_kind": "follow_up",
                "before": mk_side(body), "after": None,
                "compaction_id": "c-1", "fencing_token": 3,
            },
            {
                "mutation_id": 2, "workspace_id": "w1", "timestamp": "t2",
                "op": "remove", "record_id": "r2", "record_kind": "follow_up",
                "before": mk_side(body), "after": None,
                "compaction_id": "c-1", "fencing_token": 3,
            },
        ]
        receipt = {"compaction_id": "c-1", "rolled_records": [
            {"record_id": "r1"}, {"record_id": "r2"},
        ]}
        self.assertTrue(rr.check_compaction_correlation(receipt, log))

    def test_receipt_rolled_records_mismatch_is_rejected(self):
        body = {"n": 1}
        log = [
            {
                "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
                "op": "remove", "record_id": "r1", "record_kind": "follow_up",
                "before": mk_side(body), "after": None,
                "compaction_id": "c-1", "fencing_token": 3,
            },
        ]
        # Receipt claims r1 AND r2 were rolled, but the log only shows r1
        # under this compaction_id -- must be rejected (lost/double-claimed
        # record).
        receipt = {"compaction_id": "c-1", "rolled_records": [
            {"record_id": "r1"}, {"record_id": "r2"},
        ]}
        with self.assertRaises(rr.ReplayError):
            rr.check_compaction_correlation(receipt, log)


class TestReplayCompactionReceiptCorrelation(unittest.TestCase):
    """`replay()` must itself consume the relevant compaction receipt set
    and fail closed on any remove mutation whose compaction_id is absent,
    substituted, unknown, or mismatched -- correlation must not remain a
    detached optional helper the caller has to remember to invoke
    separately (see `check_compaction_correlation`, exercised on its own in
    `TestCompactionCorrelation` above; here it is exercised as part of the
    actual `replay()` call path)."""

    def _single_remove_log(self, compaction_id="c-1", record_id="r1"):
        body = {"n": 1}
        return [
            {
                "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
                "op": "remove", "record_id": record_id, "record_kind": "follow_up",
                "before": mk_side(body), "after": None,
                "compaction_id": compaction_id, "fencing_token": 1,
            },
        ], body

    def test_absent_receipt_set_is_rejected(self):
        # No compaction_receipts argument supplied at all (the default):
        # a remove mutation carrying a compaction_id has nothing to
        # correlate against, and must fail closed rather than silently
        # apply the removal.
        log, body = self._single_remove_log()
        with self.assertRaises(rr.ReplayError):
            rr.replay({"r1": body}, log)

    def test_empty_receipt_set_is_rejected(self):
        # An explicitly empty receipt set is the same failure mode as
        # omitting the argument -- both are "no matching receipt found".
        log, body = self._single_remove_log()
        with self.assertRaises(rr.ReplayError):
            rr.replay({"r1": body}, log, compaction_receipts=[])

    def test_nonexistent_compaction_id_is_rejected(self):
        # A receipt set is supplied, but none of its entries carry the
        # compaction_id this remove mutation actually references -- an
        # unknown/nonexistent id, not merely an absent set.
        log, body = self._single_remove_log(compaction_id="c-1")
        other_receipt = {"compaction_id": "c-999", "rolled_records": [{"record_id": "r1"}]}
        with self.assertRaises(rr.ReplayError):
            rr.replay({"r1": body}, log, compaction_receipts=[other_receipt])

    def test_substituted_mismatched_receipt_is_rejected(self):
        # The receipt carries the *correct* compaction_id, but its
        # rolled_records names a different record -- a substituted/
        # mismatched receipt, distinct from an unknown id.
        log, body = self._single_remove_log(compaction_id="c-1", record_id="r1")
        mismatched_receipt = {
            "compaction_id": "c-1",
            "rolled_records": [{"record_id": "some-other-record"}],
        }
        with self.assertRaises(rr.ReplayError):
            rr.replay({"r1": body}, log, compaction_receipts=[mismatched_receipt])

    def test_correlated_removal_succeeds_and_preserves_hash_and_order_checks(self):
        # Positive case: a correctly correlated receipt lets the remove
        # proceed, and the existing payload/ref hash verification and
        # deterministic (ascending mutation_id) ordering still apply
        # unchanged alongside the new correlation check.
        body_v1 = {"n": 1}
        body_v2 = {"n": 2}
        log = [
            {
                "mutation_id": 2, "workspace_id": "w1", "timestamp": "t2",
                "op": "update", "record_id": "r1", "record_kind": "follow_up",
                "before": mk_side(body_v1), "after": mk_side(body_v2),
                "compaction_id": None, "fencing_token": 1,
            },
            {
                "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
                "op": "remove", "record_id": "r2", "record_kind": "follow_up",
                "before": mk_side(body_v1), "after": None,
                "compaction_id": "c-1", "fencing_token": 1,
            },
        ]
        receipt = {"compaction_id": "c-1", "rolled_records": [{"record_id": "r2"}]}
        # log is fed out of mutation_id order (2 before 1) -- replay must
        # still apply mutation_id 1 (the remove) before mutation_id 2 (the
        # update), proving ordering is unaffected by the new check.
        state = rr.replay(
            {"r1": body_v1, "r2": body_v1}, log, compaction_receipts=[receipt],
        )
        self.assertEqual(state, {"r1": body_v2})

    def test_receipt_set_accepted_as_dict_keyed_by_compaction_id(self):
        # compaction_receipts may also be passed as a dict already keyed by
        # compaction_id, not just an iterable of receipt dicts.
        log, body = self._single_remove_log(compaction_id="c-1")
        receipts = {"c-1": {"compaction_id": "c-1", "rolled_records": [{"record_id": "r1"}]}}
        state = rr.replay({"r1": body}, log, compaction_receipts=receipts)
        self.assertEqual(state, {})

    def test_receipt_not_required_for_add_or_update_only_log(self):
        # Regression guard: the new correlation requirement is scoped to
        # remove mutations only -- a log with no remove entries must not
        # require compaction_receipts at all.
        body = {"n": 1}
        log = [
            {
                "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
                "op": "add", "record_id": "r1", "record_kind": "follow_up",
                "before": None, "after": mk_side(body),
                "compaction_id": None, "fencing_token": 1,
            },
        ]
        state = rr.replay({}, log)
        self.assertEqual(state, {"r1": body})


class TestRestoreAndSetEquality(unittest.TestCase):
    def test_full_replay_then_set_equality_matches_compaction_receipt(self):
        # End-to-end: build a small pre-rollup state, replay a rollup's
        # remove entries, and confirm §4's set-equality check accepts the
        # resulting pre/post/rolled sets.
        pre_state = {"r1": {"n": 1}, "r2": {"n": 2}, "r3": {"n": 3}}
        log = [
            {
                "mutation_id": 10, "workspace_id": "w1", "timestamp": "t10",
                "op": "remove", "record_id": "r1", "record_kind": "follow_up",
                "before": mk_side(pre_state["r1"]), "after": None,
                "compaction_id": "c-9", "fencing_token": 5,
            },
            {
                "mutation_id": 11, "workspace_id": "w1", "timestamp": "t11",
                "op": "remove", "record_id": "r2", "record_kind": "follow_up",
                "before": mk_side(pre_state["r2"]), "after": None,
                "compaction_id": "c-9", "fencing_token": 5,
            },
        ]
        post_state = rr.replay(
            pre_state, log,
            compaction_receipts=[{
                "compaction_id": "c-9",
                "rolled_records": [{"record_id": "r1"}, {"record_id": "r2"}],
            }],
        )
        self.assertEqual(post_state, {"r3": {"n": 3}})
        self.assertTrue(
            rr.verify_set_equality(
                pre_ids=pre_state.keys(),
                post_ids=post_state.keys(),
                rolled_ids=["r1", "r2"],
            )
        )

    def test_set_equality_rejects_lost_record(self):
        # r2 vanished from both post_ids and rolled_ids -- byte/count math
        # could still balance by coincidence, but the set check must catch
        # it.
        with self.assertRaises(rr.ReplayError):
            rr.verify_set_equality(
                pre_ids=["r1", "r2", "r3"],
                post_ids=["r3"],
                rolled_ids=["r1"],
            )

    def test_set_equality_rejects_double_counted_record(self):
        with self.assertRaises(rr.ReplayError):
            rr.verify_set_equality(
                pre_ids=["r1", "r2"],
                post_ids=["r1", "r2"],
                rolled_ids=["r2"],
            )

    def test_restore_to_arbitrary_timestamp_between_mutations(self):
        body_v1 = {"status": "open"}
        body_v2 = {"status": "resolved"}
        log = [
            {
                "mutation_id": 1, "workspace_id": "w1", "timestamp": "2026-09-03T00:00:01Z",
                "op": "add", "record_id": "f1", "record_kind": "follow_up",
                "before": None, "after": mk_side(body_v1),
                "compaction_id": None, "fencing_token": 1,
            },
            {
                "mutation_id": 2, "workspace_id": "w1", "timestamp": "2026-09-03T00:05:00Z",
                "op": "update", "record_id": "f1", "record_kind": "follow_up",
                "before": mk_side(body_v1), "after": mk_side(body_v2),
                "compaction_id": None, "fencing_token": 1,
            },
        ]
        # T strictly between mutation 1 and mutation 2 -- restore must
        # reconstruct the state as of mutation 1 only.
        state_at_t = rr.replay({}, log, target_timestamp="2026-09-03T00:02:00Z")
        self.assertEqual(state_at_t, {"f1": body_v1})


class TestRetention(unittest.TestCase):
    def test_prunable_snapshot_ids_keeps_newest_n(self):
        snapshots = [
            {"snapshot_id": f"s{i}", "timestamp": f"2026-09-{i:02d}T00:00:00Z"}
            for i in range(1, 13)
        ]
        prunable = rr.prunable_snapshot_ids(snapshots, keep_count=10)
        # Oldest two (s1, s2) fall outside the newest-10 window.
        self.assertEqual(set(prunable), {"s1", "s2"})

    def test_prunable_mutation_ids_respects_oldest_retained_watermark(self):
        retained_snapshots = [
            {"snapshot_id": "s1", "mutation_log_watermark": 5},
            {"snapshot_id": "s2", "mutation_log_watermark": 8},
        ]
        mutation_log = [{"mutation_id": i} for i in range(1, 10)]
        prunable = rr.prunable_mutation_ids(mutation_log, retained_snapshots)
        # Oldest retained snapshot's watermark is 5 -- only mutation_ids
        # <= 5 may be pruned; 6..9 are still needed for replay from s2.
        self.assertEqual(prunable, [1, 2, 3, 4, 5])

    def test_prunable_mutation_ids_empty_when_no_watermark(self):
        self.assertEqual(
            rr.prunable_mutation_ids([{"mutation_id": 1}], [{"snapshot_id": "s1", "mutation_log_watermark": None}]),
            [],
        )


class TestFencing(unittest.TestCase):
    def test_equal_or_higher_fencing_token_is_accepted(self):
        self.assertTrue(rr.check_fencing(incoming_token=5, current_token=5))
        self.assertTrue(rr.check_fencing(incoming_token=6, current_token=5))

    def test_stale_fencing_token_is_rejected(self):
        # A late write from a superseded leader (lower token) must be
        # rejected -- this is what prevents an old leader's in-flight
        # compaction from applying after a new leader has taken over (§6).
        with self.assertRaises(rr.ReplayError):
            rr.check_fencing(incoming_token=4, current_token=5)


class TestCrashRetryIdempotency(unittest.TestCase):
    def test_duplicate_reapplication_of_same_mutation_is_rejected(self):
        # §5's replay crash/retry guard: re-applying a mutation whose
        # before-state no longer matches (because it already applied once)
        # must be caught by the before-hash check, independent of any
        # external checkpoint bookkeeping.
        body_v1 = {"n": 1}
        body_v2 = {"n": 2}
        mutation = {
            "mutation_id": 2, "workspace_id": "w1", "timestamp": "t2",
            "op": "update", "record_id": "r1", "record_kind": "dirty_task",
            "before": mk_side(body_v1), "after": mk_side(body_v2),
            "compaction_id": None, "fencing_token": 1,
        }
        state = {"r1": body_v1}
        state_after_first = rr.apply_mutation(state, mutation)
        self.assertEqual(state_after_first, {"r1": body_v2})
        # Re-applying the same mutation against the already-updated state
        # must fail: state["r1"] is now body_v2, but the mutation's
        # `before` still declares body_v1.
        with self.assertRaises(rr.ReplayError):
            rr.apply_mutation(state_after_first, mutation)

    def test_resume_from_checkpoint_reapplies_only_remaining_mutations(self):
        # Simulates §5's "resume from k+1, never restart from base
        # snapshot" rule: replaying only mutation_id > k on top of the
        # state already reconstructed through k must equal replaying the
        # whole log from scratch.
        body1 = {"n": 1}
        body2 = {"n": 2}
        body3 = {"n": 3}
        log = [
            {
                "mutation_id": 1, "workspace_id": "w1", "timestamp": "t1",
                "op": "add", "record_id": "r1", "record_kind": "dirty_task",
                "before": None, "after": mk_side(body1),
                "compaction_id": None, "fencing_token": 1,
            },
            {
                "mutation_id": 2, "workspace_id": "w1", "timestamp": "t2",
                "op": "update", "record_id": "r1", "record_kind": "dirty_task",
                "before": mk_side(body1), "after": mk_side(body2),
                "compaction_id": None, "fencing_token": 1,
            },
            {
                "mutation_id": 3, "workspace_id": "w1", "timestamp": "t3",
                "op": "update", "record_id": "r1", "record_kind": "dirty_task",
                "before": mk_side(body2), "after": mk_side(body3),
                "compaction_id": None, "fencing_token": 1,
            },
        ]
        full_replay = rr.replay({}, log)
        checkpoint_k = 2
        state_at_checkpoint = rr.replay({}, log, target_mutation_id=checkpoint_k)
        remaining = [m for m in log if m["mutation_id"] > checkpoint_k]
        resumed = rr.replay(state_at_checkpoint, remaining)
        self.assertEqual(resumed, full_replay)


if __name__ == "__main__":
    unittest.main()
