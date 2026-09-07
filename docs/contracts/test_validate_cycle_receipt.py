import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

import validate_cycle_receipt as validator


def valid_receipt():
    cycle_id = "cycle-2026-09-07T15:00:00Z"
    task_id = "task-1"
    return {
        "schema_version": "1.0.0",
        "scope": "cycle",
        "cycle_id": cycle_id,
        "observed_at": "2026-09-07T15:00:00Z",
        "live_task_ids": [task_id],
        "open_ledger_task_ids": [task_id],
        "ledger_entries": [{
            "task_id": task_id,
            "owner": "Coordinator",
            "health": "healthy",
            "last_checked_cycle_id": cycle_id,
            "last_action": "verified live session",
            "next_action": "recheck exact session at the next routine cycle",
            "trigger": "next routine cycle",
            "fallback": "start a fresh correct-profile owner if session stops",
            "evidence_generation": "lane:work/session:s1@1/head:h1",
            "lane": "Work",
            "anomalous": False,
            "mutated": False,
            "transitioned": False,
            "delivery_status": "none",
        }],
        "blocked_task_ids": [],
        "blocked_records": [],
        "anomalies": [],
        "delivery_claims": [],
        "transitions": [],
        "mutations": [],
        "continuity": {
            "plan_bytes": 100000,
            "soft_limit_bytes": 200000,
            "hard_limit_bytes": 240000,
            "compaction_performed": False,
            "write_readback_verified": True,
            "current_snapshot_first": True,
            "open_record_sets_preserved": True,
        },
        "report": {
            "mentioned_task_ids": [task_id],
            "barrier_at": "2026-09-07T15:00:00Z",
            "fresh": True,
            "task_barriers": [{
                "task_id": task_id,
                "lane_session_observed_at": "2026-09-07T15:00:00Z",
                "provider_required": False,
            }],
        },
        "gate_results": {f"G{i}": "pass" for i in range(1, 11)},
    }


class CycleReceiptTests(unittest.TestCase):
    def checks(self, receipt):
        return {check for check, _ in validator.validate(receipt)}

    def test_valid_receipt(self):
        self.assertEqual(validator.validate(valid_receipt()), [])

    def test_documented_valid_fixture(self):
        fixture = Path(__file__).parent / "fixtures" / "valid_cycle_receipt.json"
        self.assertEqual(validator.validate(json.loads(fixture.read_text())), [])

    def test_inventory_mismatch_fails(self):
        receipt = valid_receipt()
        receipt["open_ledger_task_ids"] = []
        self.assertIn("G1", self.checks(receipt))

    def test_generic_next_action_fails(self):
        receipt = valid_receipt()
        receipt["ledger_entries"][0]["next_action"] = "monitor"
        self.assertIn("G2", self.checks(receipt))

    def test_blocked_requires_positive_and_falsification_proof(self):
        receipt = valid_receipt()
        entry = receipt["ledger_entries"][0]
        entry["lane"] = "Blocked"
        entry["health"] = "blocked"
        receipt["blocked_task_ids"] = ["task-1"]
        receipt["blocked_records"] = [{
            "task_id": "task-1",
            "previous_step": "Work",
            "blocker_proof": "",
            "falsification_query": "query canonical dependency",
            "falsification_result": "dependency remains open",
            "blocker_owner": "dependency owner",
            "preservation_receipt": "head h1 is pushed",
            "removal_action": "finish dependency",
            "expected_evidence": "merged dependency receipt",
            "trigger": "dependency merge",
            "attempt_count": 1,
            "fallback": "staff replacement owner",
            "last_checked_cycle_id": receipt["cycle_id"],
        }]
        self.assertIn("G3", self.checks(receipt))

    def test_anomaly_requires_owner_and_independent_surfaces(self):
        receipt = valid_receipt()
        receipt["ledger_entries"][0]["anomalous"] = True
        receipt["anomalies"] = [{
            "task_id": "task-1",
            "owner_contact": "obtained",
            "owner_account": "",
            "independent_surfaces": [],
            "verification_result": "",
        }]
        self.assertIn("G4", self.checks(receipt))

    def test_delivery_claim_requires_remote_containment(self):
        receipt = valid_receipt()
        receipt["ledger_entries"][0]["delivery_status"] = "deployable"
        receipt["delivery_claims"] = [{
            "task_id": "task-1",
            "claim": "deployable",
            "task_head": "h1",
            "remote_ref": "origin/feature",
            "remote_reachable": False,
            "canonical_delivery": "https://example.test/pull/1",
            "provider_state": "open",
            "contained": False,
            "observed_at": "2026-09-07T15:00:00Z",
        }]
        self.assertIn("G5", self.checks(receipt))

    def test_open_provider_state_cannot_be_called_delivered(self):
        receipt = valid_receipt()
        receipt["ledger_entries"][0]["delivery_status"] = "delivered"
        receipt["delivery_claims"] = [{
            "task_id": "task-1",
            "claim": "delivered",
            "task_head": "h1",
            "remote_ref": "origin/feature",
            "remote_reachable": True,
            "canonical_delivery": "https://example.test/pull/1",
            "provider_state": "open",
            "contained": True,
            "observed_at": "2026-09-07T15:00:00Z",
        }]
        self.assertIn("G5", self.checks(receipt))

    def test_todeploy_lane_cannot_bypass_delivery_claim(self):
        receipt = valid_receipt()
        receipt["ledger_entries"][0]["lane"] = "ToDeploy"
        self.assertIn("G5", self.checks(receipt))

    def test_todeploy_lane_accepts_exact_containment_claim(self):
        receipt = valid_receipt()
        entry = receipt["ledger_entries"][0]
        entry["lane"] = "ToDeploy"
        entry["delivery_status"] = "to_deploy_ready"
        receipt["delivery_claims"] = [{
            "task_id": "task-1",
            "claim": "to_deploy_ready",
            "task_head": "h1",
            "remote_ref": "origin/feature",
            "remote_reachable": True,
            "canonical_delivery": "https://example.test/pull/1",
            "provider_state": "merged",
            "contained": True,
            "observed_at": "2026-09-07T15:00:00Z",
        }]
        self.assertEqual(validator.validate(receipt), [])

    def test_delivery_claim_must_match_ledger_status(self):
        receipt = valid_receipt()
        receipt["ledger_entries"][0]["delivery_status"] = "deployable"
        receipt["delivery_claims"] = [{
            "task_id": "task-1",
            "claim": "delivered",
            "task_head": "h1",
            "remote_ref": "origin/feature",
            "remote_reachable": True,
            "canonical_delivery": "https://example.test/pull/1",
            "provider_state": "merged",
            "contained": True,
            "observed_at": "2026-09-07T15:00:00Z",
        }]
        self.assertIn("G5", self.checks(receipt))

    def test_unsettled_transition_fails(self):
        receipt = valid_receipt()
        entry = receipt["ledger_entries"][0]
        entry["transitioned"] = True
        receipt["transitions"] = [{
            "task_id": "task-1",
            "transition_id": "move-1",
            "pre": {
                "source_lane": "Spec",
                "target_lane": "Work",
                "authority": "Coordinator",
                "evidence_generation": entry["evidence_generation"],
                "pending_move_checked_at": "2026-09-07T15:00:00Z",
                "expected_owner": "Work owner",
                "expected_model": "gpt-5.6-terra",
                "required_verdicts": [],
                "invalidation_conditions": ["head change"],
            },
            "post": {
                "lane": "Work",
                "state": "REVIEW",
                "lifecycle_settled": False,
                "session_id": "s1",
                "profile_id": "p1",
                "runtime_model": "gpt-5.6-terra",
                "head": "h1",
                "tag_aligned": True,
                "pending_move_clear": True,
                "execution_expected": True,
                "execution_state": "WAITING_FOR_INPUT",
                "verified": False,
            },
        }]
        checks = self.checks(receipt)
        self.assertIn("G7", checks)

    def test_mutation_without_readback_fails(self):
        receipt = valid_receipt()
        receipt["ledger_entries"][0]["mutated"] = True
        receipt["mutations"] = [{
            "task_id": "task-1",
            "kind": "move",
            "target": "Work",
            "result": "success",
            "readback": "",
            "verified": False,
        }]
        self.assertIn("G8", self.checks(receipt))

    def test_qa_transition_requires_passed_review_receipt(self):
        receipt = valid_receipt()
        entry = receipt["ledger_entries"][0]
        entry["transitioned"] = True
        receipt["transitions"] = [{
            "task_id": "task-1",
            "transition_id": "move-qa-1",
            "pre": {
                "source_lane": "Review",
                "target_lane": "QA",
                "authority": "Coordinator",
                "evidence_generation": entry["evidence_generation"],
                "pending_move_checked_at": "2026-09-07T15:00:00Z",
                "expected_owner": "QA owner",
                "expected_model": "gpt-5.6-luna",
                "required_verdicts": [],
                "invalidation_conditions": ["head change"],
            },
            "post": {
                "lane": "QA",
                "state": "RUNNING",
                "lifecycle_settled": True,
                "session_id": "s2",
                "profile_id": "p2",
                "runtime_model": "gpt-5.6-luna",
                "head": "h1",
                "tag_aligned": True,
                "pending_move_clear": True,
                "execution_expected": True,
                "execution_state": "RUNNING",
                "verified": True,
            },
        }]
        self.assertIn("G6", self.checks(receipt))

    def test_plan_hard_stop_fails(self):
        receipt = valid_receipt()
        receipt["continuity"]["plan_bytes"] = 240000
        receipt["continuity"]["compaction_performed"] = True
        receipt["continuity"].update({
            "archive_path": "docs/archive/state.md",
            "archive_sha256": "abc",
            "pre_open_ids_hash": "same",
            "post_open_ids_hash": "same",
        })
        self.assertIn("G9", self.checks(receipt))

    def test_completed_compaction_must_finish_below_soft_limit(self):
        receipt = valid_receipt()
        receipt["continuity"]["plan_bytes"] = 210000
        receipt["continuity"]["compaction_performed"] = True
        receipt["continuity"].update({
            "archive_path": "docs/archive/state.md",
            "archive_sha256": "abc",
            "pre_open_ids_hash": "same",
            "post_open_ids_hash": "same",
        })
        self.assertIn("G9", self.checks(receipt))

    def test_stale_report_fails(self):
        receipt = valid_receipt()
        receipt["report"]["fresh"] = False
        self.assertIn("G10", self.checks(receipt))

    def test_wall_clock_stale_report_fails_when_age_gate_enabled(self):
        receipt = valid_receipt()
        failures = validator.validate(
            receipt,
            now=datetime(2026, 9, 7, 15, 10, tzinfo=timezone.utc),
            max_age_seconds=300,
        )
        self.assertIn("G10", {check for check, _ in failures})

    def test_wall_clock_fresh_report_passes_when_age_gate_enabled(self):
        receipt = valid_receipt()
        failures = validator.validate(
            receipt,
            now=datetime(2026, 9, 7, 15, 4, tzinfo=timezone.utc),
            max_age_seconds=300,
        )
        self.assertEqual(failures, [])

    def test_report_barrier_cannot_predate_receipt(self):
        receipt = valid_receipt()
        receipt["report"]["barrier_at"] = "2026-09-07T14:59:59Z"
        self.assertIn("G10", self.checks(receipt))

    def test_status_scope_is_bounded(self):
        receipt = valid_receipt()
        receipt["scope"] = "status"
        receipt.pop("live_task_ids")
        receipt["scope_task_ids"] = ["task-1"]
        self.assertEqual(validator.validate(receipt), [])


if __name__ == "__main__":
    unittest.main()
