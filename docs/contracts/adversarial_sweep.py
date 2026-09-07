#!/usr/bin/env python3
"""Reproducible complete adversarial sweep for the Coordinator policy contract.

Purpose
-------
Enumerates every mandatory invariant this validator (`validate_contract.py`)
enforces and, for each, applies every weakening/removal mutation that is
semantically distinct for that field (a scalar-equality invariant gets a
"weaken to a wrong-but-plausible value" mutation; a presence-sensitive
boolean invariant additionally gets a "remove the key entirely" mutation; a
list-superset invariant gets a "remove one required member" mutation; an
exact-order list gets a "drop/reorder the required middle element"
mutation). Every mutated contract has its digest **recomputed and set
correctly** before validation, so a mutation can only be caught by the
specific invariant check it targets -- never masked by (or credited to) an
unrelated `stale_digest` failure.

This is the standalone, reproducible artifact that proves the validator
fails closed for every mutation in MUTATIONS, not just the illustrative
subset that has a standing fixtures/*.json file. Run directly:

    python3 adversarial_sweep.py

Exit code 0 iff every mutation in MUTATIONS is rejected (at least one
failure reported) and none of those failures is `stale_digest`. Prints one
line per mutation plus a final "N/N mutations correctly rejected" summary.

Stdlib only, no third-party dependencies, importable from
test_validate_contract.py for CI wiring.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import validate_contract as vc  # noqa: E402

CANONICAL = os.path.join(HERE, "coordinator-policy-contract.json")


def load_canonical():
    with open(CANONICAL, encoding="utf-8") as fh:
        return json.load(fh)


def _get_parent(contract, path):
    node = contract
    for key in path[:-1]:
        node = node[key]
    return node


def weaken(path, value):
    """Set contract[path...] = value (path is a tuple of dict keys)."""
    def _mutate(contract):
        _get_parent(contract, path)[path[-1]] = value
        return contract
    return _mutate


def remove(path):
    """Delete contract[path...] entirely."""
    def _mutate(contract):
        del _get_parent(contract, path)[path[-1]]
        return contract
    return _mutate


def remove_list_item(path, item):
    """Remove one member from a required-superset list at contract[path...]."""
    def _mutate(contract):
        lst = _get_parent(contract, path)[path[-1]]
        _get_parent(contract, path)[path[-1]] = [v for v in lst if v != item]
        return contract
    return _mutate


def drop_middle(path):
    """Drop the second element of an exact-order list at contract[path...]."""
    def _mutate(contract):
        lst = _get_parent(contract, path)[path[-1]]
        _get_parent(contract, path)[path[-1]] = [lst[0], lst[-1]]
        return contract
    return _mutate


def insert_leak(path):
    def _mutate(contract):
        lst = _get_parent(contract, path)[path[-1]]
        _get_parent(contract, path)[path[-1]] = list(lst) + ["sk-example-secret-token"]
        return contract
    return _mutate


def remove_all_list_items(path):
    def _mutate(contract):
        _get_parent(contract, path)[path[-1]] = []
        return contract
    return _mutate


def swap_full_order(path):
    def _mutate(contract):
        lst = _get_parent(contract, path)[path[-1]]
        _get_parent(contract, path)[path[-1]] = list(reversed(lst))
        return contract
    return _mutate


def set_non_list(path, value):
    def _mutate(contract):
        _get_parent(contract, path)[path[-1]] = value
        return contract
    return _mutate


def append_unknown(path, value):
    def _mutate(contract):
        lst = _get_parent(contract, path)[path[-1]]
        _get_parent(contract, path)[path[-1]] = list(lst) + [value]
        return contract
    return _mutate


# Each entry: (name, mutate_fn, expected_check[, skip_digest_recompute]).
# expected_check is either a single check name or a tuple of acceptable
# check names (some structural mutations may legitimately trip more than
# one specific check name). skip_digest_recompute defaults to False; it is
# set True only for the one mutation (digest_algorithm itself) where a
# valid digest cannot be recomputed under the mutated algorithm -- the
# validator's own digest check degrades gracefully in that case (see
# validate_contract: recomputed stays None, so no spurious stale_digest
# false-positive is raised either).
MUTATIONS = [
    # -- authority_boundaries --------------------------------------------
    ("authority.human_reserved_classes.remove_destructive",
     remove_list_item(("authority_boundaries", "human_reserved_classes"), "destructive_or_irreversible"),
     "missing_required_invariant"),
    ("authority.human_reserved_classes.remove_security",
     remove_list_item(("authority_boundaries", "human_reserved_classes"), "security_or_trust_boundary"),
     "missing_required_invariant"),
    ("authority.human_reserved_classes.remove_all",
     remove_all_list_items(("authority_boundaries", "human_reserved_classes")),
     "missing_required_invariant"),
    ("authority.cross_workspace_authority.weaken_true",
     weaken(("authority_boundaries", "cross_workspace_authority"), True),
     "missing_required_invariant"),
    ("authority.cross_workspace_authority.remove",
     remove(("authority_boundaries", "cross_workspace_authority")),
     "missing_required_invariant"),
    ("authority.scope.weaken",
     weaken(("authority_boundaries", "scope"), "cross_workspace_allowed"),
     "missing_required_invariant"),
    ("authority.scope.remove",
     remove(("authority_boundaries", "scope")),
     "missing_required_invariant"),
    ("authority.approval_principal.weaken_none",
     weaken(("authority_boundaries", "approval_principal"), "none"),
     "missing_required_invariant"),
    ("authority.approval_principal.remove",
     remove(("authority_boundaries", "approval_principal")),
     "missing_required_invariant"),

    # -- gates: exact_head_required (all four gates) -----------------------
    ("gates.review.exact_head_required.weaken",
     weaken(("gates", "review", "exact_head_required"), False),
     "missing_required_invariant"),
    ("gates.qa.exact_head_required.weaken",
     weaken(("gates", "qa", "exact_head_required"), False),
     "missing_required_invariant"),
    ("gates.readiness.exact_head_required.weaken",
     weaken(("gates", "readiness", "exact_head_required"), False),
     "missing_required_invariant"),
    ("gates.done_integrity.exact_head_required.weaken",
     weaken(("gates", "done_integrity", "exact_head_required"), False),
     "missing_required_invariant"),

    # -- gates: independent_session_required (review/qa) -------------------
    ("gates.review.independent_session_required.weaken",
     weaken(("gates", "review", "independent_session_required"), False),
     "missing_required_invariant"),
    ("gates.review.independent_session_required.remove",
     remove(("gates", "review", "independent_session_required")),
     "missing_required_invariant"),
    ("gates.qa.independent_session_required.weaken",
     weaken(("gates", "qa", "independent_session_required"), False),
     "missing_required_invariant"),
    ("gates.qa.independent_session_required.remove",
     remove(("gates", "qa", "independent_session_required")),
     "missing_required_invariant"),

    # -- gates: readiness recheck / done_integrity terminal receipt --------
    ("gates.readiness.recheck_after_draft_to_ready_transition.weaken",
     weaken(("gates", "readiness", "recheck_after_draft_to_ready_transition"), False),
     "missing_required_invariant"),
    ("gates.done_integrity.terminal_receipt_required.weaken",
     weaken(("gates", "done_integrity", "terminal_receipt_required"), False),
     "missing_required_invariant"),

    # -- gates: entire gate object removed ---------------------------------
    ("gates.review.remove", remove(("gates", "review")), "missing_required_invariant"),
    ("gates.qa.remove", remove(("gates", "qa")), "missing_required_invariant"),
    ("gates.readiness.remove", remove(("gates", "readiness")), "missing_required_invariant"),
    ("gates.done_integrity.remove", remove(("gates", "done_integrity")), "missing_required_invariant"),

    # -- task evidence / delivery containment gates (contract 1.2.0) ------
    ("evidence.fresh_status_barrier.weaken",
     weaken(("task_evidence_gates", "status_claims_require_fresh_live_barrier"), False),
     "missing_required_invariant"),
    ("evidence.owner_account.weaken",
     weaken(("task_evidence_gates", "owner_account_required_for_anomaly_when_contact_safe"), False),
     "missing_required_invariant"),
    ("evidence.named_surfaces.weaken",
     weaken(("task_evidence_gates", "absence_requires_all_named_surfaces_checked"), False),
     "missing_required_invariant"),
    ("evidence.blocker_falsification.weaken",
     weaken(("task_evidence_gates", "blocker_falsification_required_each_cycle"), False),
     "missing_required_invariant"),
    ("evidence.blocked_current_cycle.weaken",
     weaken(("task_evidence_gates", "blocked_last_checked_current_cycle"), False),
     "missing_required_invariant"),
    ("evidence.delivery_containment.weaken",
     weaken(("task_evidence_gates", "delivery_containment_required_before_deployable_or_terminal"), False),
     "missing_required_invariant"),
    ("evidence.delivery_proof.remove_remote",
     remove_list_item(("task_evidence_gates", "delivery_containment_proof"), "named_remote_branch_reachability"),
     "missing_required_invariant"),
    ("evidence.delivery_proof.remove_provider_state",
     remove_list_item(("task_evidence_gates", "delivery_containment_proof"), "provider_proven_merge_or_release_state"),
     "missing_required_invariant"),
    ("evidence.lane_alone_not_proof.weaken",
     weaken(("task_evidence_gates", "lane_or_receipt_alone_is_not_proof"), False),
     "missing_required_invariant"),

    # -- workflow transition gates (contract 1.2.0) -----------------------
    ("transition.pre_receipt.weaken",
     weaken(("workflow_transition_gates", "pre_transition_receipt_required"), False),
     "missing_required_invariant"),
    ("transition.post_readback.weaken",
     weaken(("workflow_transition_gates", "post_transition_readback_required"), False),
     "missing_required_invariant"),
    ("transition.head_invalidation.weaken",
     weaken(("workflow_transition_gates", "head_change_invalidates_gate_receipts"), False),
     "missing_required_invariant"),
    ("transition.review_verdict.weaken",
     weaken(("workflow_transition_gates", "review_requires_explicit_verdict"), False),
     "missing_required_invariant"),
    ("transition.qa_verdict.weaken",
     weaken(("workflow_transition_gates", "qa_requires_explicit_verdict"), False),
     "missing_required_invariant"),
    ("transition.to_deploy_containment.weaken",
     weaken(("workflow_transition_gates", "to_deploy_requires_provider_merged_or_released"), False),
     "missing_required_invariant"),
    ("transition.failure_counts_as_advance.weaken",
     weaken(("workflow_transition_gates", "transition_failure_is_not_advancement"), False),
     "missing_required_invariant"),

    # -- cycle exit / continuity gates (contract 1.2.0) -------------------
    ("cycle.inventory_equality.weaken",
     weaken(("cycle_exit_gates", "live_task_ids_equal_open_ledger_ids"), False),
     "missing_required_invariant"),
    ("cycle.entry_fields.remove_owner",
     remove_list_item(("cycle_exit_gates", "every_open_entry_requires"), "owner"),
     "missing_required_invariant"),
    ("cycle.entry_fields.remove_trigger",
     remove_list_item(("cycle_exit_gates", "every_open_entry_requires"), "trigger"),
     "missing_required_invariant"),
    ("cycle.blocked_current_record.weaken",
     weaken(("cycle_exit_gates", "blocked_entries_require_complete_current_cycle_record"), False),
     "missing_required_invariant"),
    ("cycle.mutation_readback.weaken",
     weaken(("cycle_exit_gates", "mutations_require_post_action_readback"), False),
     "missing_required_invariant"),
    ("cycle.persistence_readback.weaken",
     weaken(("cycle_exit_gates", "persisted_state_write_and_readback_required"), False),
     "missing_required_invariant"),
    ("cycle.failed_gate_blocks_completion.weaken",
     weaken(("cycle_exit_gates", "unresolved_gate_failure_blocks_cycle_completion"), False),
     "missing_required_invariant"),
    ("continuity.soft_limit.weaken",
     weaken(("continuity_state", "live_plan_soft_limit_bytes"), 250000),
     "missing_required_invariant"),
    ("continuity.hard_stop.weaken",
     weaken(("continuity_state", "live_plan_hard_stop_bytes"), 262144),
     "missing_required_invariant"),
    ("continuity.unresolved_inline.weaken",
     weaken(("continuity_state", "unresolved_records_remain_inline"), False),
     "missing_required_invariant"),
    ("continuity.archive_hash.weaken",
     weaken(("continuity_state", "pre_compaction_archive_sha256_required"), False),
     "missing_required_invariant"),
    ("continuity.set_equality.weaken",
     weaken(("continuity_state", "pre_post_open_record_set_equality_required"), False),
     "missing_required_invariant"),
    ("continuity.readback.weaken",
     weaken(("continuity_state", "post_write_readback_required"), False),
     "missing_required_invariant"),
    ("continuity.current_first.weaken",
     weaken(("continuity_state", "current_snapshot_first"), False),
     "missing_required_invariant"),

    # -- workspace_lane_ownership -------------------------------------------
    ("lane.done_is_terminal_integrity_lane.weaken",
     weaken(("workspace_lane_ownership", "done_is_terminal_integrity_lane"), False),
     "missing_required_invariant"),
    ("lane.done_is_terminal_integrity_lane.remove",
     remove(("workspace_lane_ownership", "done_is_terminal_integrity_lane")),
     "missing_required_invariant"),
    ("lane.monitored_lanes.remove_done",
     remove_list_item(("workspace_lane_ownership", "monitored_lanes"), "done"),
     "missing_required_invariant"),
    ("lane.unit.weaken", weaken(("workspace_lane_ownership", "unit"), "task"), "missing_required_invariant"),
    ("lane.unit.remove", remove(("workspace_lane_ownership", "unit")), "missing_required_invariant"),
    ("lane.peer_model.weaken",
     weaken(("workspace_lane_ownership", "peer_model"), False),
     "missing_required_invariant"),
    ("lane.peer_model.remove",
     remove(("workspace_lane_ownership", "peer_model")),
     "missing_required_invariant"),
    ("lane.cross_workspace_standing.weaken",
     weaken(("workspace_lane_ownership", "cross_workspace_standing"), True),
     "missing_required_invariant"),
    ("lane.cross_workspace_standing.remove",
     remove(("workspace_lane_ownership", "cross_workspace_standing")),
     "missing_required_invariant"),
    ("lane.auto_start_lane_move_requires_settled_lifecycle.weaken",
     weaken(("workspace_lane_ownership", "auto_start_lane_move_requires_settled_lifecycle"), False),
     "missing_required_invariant"),
    ("lane.auto_start_lane_move_requires_settled_lifecycle.remove",
     remove(("workspace_lane_ownership", "auto_start_lane_move_requires_settled_lifecycle")),
     "missing_required_invariant"),

    # -- queue_claim_identity -------------------------------------------------
    ("queue.audit_model.weaken",
     weaken(("queue_claim_identity", "audit_model"), "global_watermark"),
     "missing_required_invariant"),
    ("queue.audit_model.remove",
     remove(("queue_claim_identity", "audit_model")),
     "missing_required_invariant"),
    ("queue.identity_scope.weaken",
     weaken(("queue_claim_identity", "identity_scope"), "global"),
     "missing_required_invariant"),
    ("queue.identity_scope.remove",
     remove(("queue_claim_identity", "identity_scope")),
     "missing_required_invariant"),
    ("queue.coalescing_rule.weaken",
     weaken(("queue_claim_identity", "coalescing_rule"), "all_messages"),
     "missing_required_invariant"),
    ("queue.coalescing_rule.remove",
     remove(("queue_claim_identity", "coalescing_rule")),
     "missing_required_invariant"),
    ("queue.minimum_trusted_envelope.remove_entry_id",
     remove_list_item(("queue_claim_identity", "minimum_trusted_envelope"), "entry_id"),
     "missing_required_invariant"),
    ("queue.minimum_trusted_envelope.remove_workspace_id",
     remove_list_item(("queue_claim_identity", "minimum_trusted_envelope"), "workspace_id"),
     "missing_required_invariant"),
    ("queue.coalescing_forbidden_for.remove_human_input",
     remove_list_item(("queue_claim_identity", "coalescing_forbidden_for"), "human_input"),
     "missing_required_invariant"),
    ("queue.claim_collision_check.weaken",
     weaken(("queue_claim_identity", "claim_collision_check"), "none"),
     "missing_required_invariant"),
    ("queue.claim_collision_check.remove",
     remove(("queue_claim_identity", "claim_collision_check")),
     "missing_required_invariant"),
    ("queue.routine_identity_components.remove_semantic_scope_generation",
     remove_list_item(("queue_claim_identity", "routine_identity_components"), "semantic_scope_generation"),
     "missing_required_invariant"),
    ("queue.routine_identity_excludes_sender_ids.weaken",
     weaken(("queue_claim_identity", "routine_identity_excludes_sender_ids"), False),
     "missing_required_invariant"),
    ("queue.routine_identity_excludes_sender_ids.remove",
     remove(("queue_claim_identity", "routine_identity_excludes_sender_ids")),
     "missing_required_invariant"),
    ("queue.cross_sender_coalescing_permitted.weaken",
     weaken(("queue_claim_identity", "cross_sender_coalescing_permitted"), False),
     "missing_required_invariant"),
    ("queue.cross_sender_coalescing_permitted.remove",
     remove(("queue_claim_identity", "cross_sender_coalescing_permitted")),
     "missing_required_invariant"),
    ("queue.coalescing_preserved_state.weaken",
     weaken(("queue_claim_identity", "coalescing_preserved_state"), "dropped"),
     "missing_required_invariant"),
    ("queue.coalescing_preserved_state.remove",
     remove(("queue_claim_identity", "coalescing_preserved_state")),
     "missing_required_invariant"),

    # -- worker_helper_receipts ------------------------------------------------
    ("receipts.workers_never_mutate.weaken",
     weaken(("worker_helper_receipts", "workers_never_mutate"), False),
     "missing_required_invariant"),
    ("receipts.workers_never_mutate.remove",
     remove(("worker_helper_receipts", "workers_never_mutate")),
     "missing_required_invariant"),
    ("receipts.mutation_serialized_by.weaken",
     weaken(("worker_helper_receipts", "mutation_serialized_by"), "none"),
     "missing_required_invariant"),
    ("receipts.mutation_serialized_by.remove",
     remove(("worker_helper_receipts", "mutation_serialized_by")),
     "missing_required_invariant"),
    ("receipts.receipt_is_not_proof_of.remove_one",
     remove_list_item(("worker_helper_receipts", "receipt_is_not_proof_of"), "capacity_released"),
     "missing_required_invariant"),
    ("receipts.receipt_is_not_proof_of.remove_all",
     remove(("worker_helper_receipts", "receipt_is_not_proof_of")),
     "missing_required_invariant"),
    ("receipts.receipt_required_fields.remove_claim_or_lease_id",
     remove_list_item(("worker_helper_receipts", "receipt_required_fields"), "claim_or_lease_id"),
     "missing_required_invariant"),
    ("receipts.freshness_barrier_required_before_reporting.weaken",
     weaken(("worker_helper_receipts", "freshness_barrier_required_before_reporting"), False),
     "missing_required_invariant"),
    ("receipts.freshness_barrier_required_before_reporting.remove",
     remove(("worker_helper_receipts", "freshness_barrier_required_before_reporting")),
     "missing_required_invariant"),
    ("receipts.routine_wake_coalescing_receipt_fields.remove_leader_fencing_token",
     remove_list_item(
         ("worker_helper_receipts", "routine_wake_coalescing_receipt_fields"), "leader_fencing_token"
     ),
     "missing_required_invariant"),

    # -- done_integrity --------------------------------------------------------
    ("done.merged_pr_or_done_placement_alone_is_not_proof.weaken",
     weaken(("done_integrity", "merged_pr_or_done_placement_alone_is_not_proof"), False),
     "missing_required_invariant"),
    ("done.merged_pr_or_done_placement_alone_is_not_proof.remove",
     remove(("done_integrity", "merged_pr_or_done_placement_alone_is_not_proof")),
     "missing_required_invariant"),
    ("done.required_proof.remove_no_unique_local",
     remove_list_item(("done_integrity", "required_proof"), "no_unique_local_or_untracked_work"),
     "missing_required_invariant"),
    ("done.required_proof.remove_canonical_merged_identity",
     remove_list_item(("done_integrity", "required_proof"), "canonical_merged_identity_and_accepted_head"),
     "missing_required_invariant"),
    ("done.receipt_fields.remove_local_head",
     remove_list_item(("done_integrity", "receipt_fields"), "local_head"),
     "missing_required_invariant"),

    # -- readiness_notification_order (exact ordered sequence) ----------------
    ("readiness_notification_order.drop_middle",
     drop_middle(("readiness_notification_order",)),
     "contradictory_plugin_prompt_default"),

    # -- compatibility ----------------------------------------------------------
    ("compatibility.unsupported_version_behavior.weaken",
     weaken(("compatibility", "unsupported_version_behavior"), "best_effort"),
     "missing_required_invariant"),
    ("compatibility.unsupported_version_behavior.remove",
     remove(("compatibility", "unsupported_version_behavior")),
     "missing_required_invariant"),

    # -- exclusions (secret-shaped leak) ------------------------------------
    ("exclusions.insert_leak", insert_leak(("exclusions",)), "exclusion_leaks_secret"),

    # -- required_fields self-declaration -------------------------------------
    ("required_fields.omit_done_integrity",
     remove_list_item(("required_fields",), "done_integrity"),
     "required_fields"),
    ("required_fields.add_unknown_field",
     append_unknown(("required_fields",), "not_a_real_field"),
     "unknown_required_field"),
    ("required_fields.not_a_list",
     set_non_list(("required_fields",), "done_integrity"),
     "required_fields"),

    # -- worker_helper_receipts: whole receipt_required_fields dropped ---------
    ("receipts.receipt_required_fields.remove_all",
     remove(("worker_helper_receipts", "receipt_required_fields")),
     "missing_required_invariant"),

    # -- readiness_notification_order: full reorder, not just a middle drop --
    ("readiness_notification_order.full_reorder",
     swap_full_order(("readiness_notification_order",)),
     "contradictory_plugin_prompt_default"),

    # -- contract_version below min_supported_contract_version -----------------
    ("contract_version.stale",
     weaken(("contract_version",), "0.9.0"),
     "stale_version"),

    # -- digest_algorithm: unsupported algorithm named ---------------------------
    ("digest_algorithm.unsupported",
     weaken(("digest_algorithm",), "md5"),
     "digest_algorithm",
     True),  # skip_digest_recompute: sha256 recompute is impossible once the
             # algorithm itself is mutated to something unsupported.
]


def run_sweep(verbose=False):
    """Run every mutation in MUTATIONS. Returns (results, all_passed).

    results is a list of (name, failures, ok) tuples where ok is True iff
    the mutation was rejected (non-empty failures) without a stale_digest
    false-positive masking the real check.
    """
    canonical = load_canonical()
    baseline_failures = vc.validate_contract(canonical)
    if baseline_failures:
        raise AssertionError(f"canonical contract must itself be valid, got: {baseline_failures}")

    results = []
    for entry in MUTATIONS:
        name, mutate_fn, expected_check = entry[0], entry[1], entry[2]
        skip_digest_recompute = entry[3] if len(entry) > 3 else False
        contract = copy.deepcopy(canonical)
        contract = mutate_fn(contract)
        if not skip_digest_recompute:
            # Recompute a *valid* digest for every mutation so each is
            # judged solely on its own targeted invariant, never on an
            # incidental stale_digest failure.
            contract["digest"] = vc.compute_digest(contract)
        failures = vc.validate_contract(contract)
        checks = [c for c, _ in failures]
        expected = (expected_check,) if isinstance(expected_check, str) else tuple(expected_check)
        ok = bool(checks) and "stale_digest" not in checks and any(c in expected for c in checks)
        results.append((name, failures, ok))
        if verbose:
            status = "PASS" if ok else "FAIL"
            print(f"[{status}] {name}: {checks}")

    all_passed = all(ok for _, _, ok in results)
    return results, all_passed


def main():
    results, all_passed = run_sweep(verbose=True)
    total = len(results)
    passed = sum(1 for _, _, ok in results if ok)
    print(f"\n{passed}/{total} mutations correctly rejected")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
