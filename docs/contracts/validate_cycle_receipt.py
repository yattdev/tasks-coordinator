#!/usr/bin/env python3
"""Fail-closed validator for Coordinator cycle/status gate receipts.

The validator checks executable evidence, not narrative confidence. It is
stdlib-only so a Coordinator, plugin, or CI job can run it without this repo as
a Python package.
"""

import argparse
import json
import sys
from datetime import datetime


SCHEMA_VERSION = "1.0.0"
HEALTH_CLASSES = {
    "healthy", "stalled", "blocked", "failed", "waiting", "anomalous", "terminal"
}
DELIVERY_STATUSES = {"none", "delivered", "deployable", "to_deploy_ready", "terminal"}
TERMINAL_PROVIDER_STATES = {"merged", "released", "published", "deployed"}
GENERIC_ACTIONS = {"", "wait", "waiting", "monitor", "monitoring", "unknown", "none", "n/a"}
BLOCKED_FIELDS = {
    "previous_step", "blocker_proof", "falsification_query",
    "falsification_result", "blocker_owner", "preservation_receipt",
    "removal_action", "expected_evidence", "trigger", "attempt_count", "fallback",
}
PRE_TRANSITION_FIELDS = {
    "source_lane", "target_lane", "authority", "evidence_generation",
    "pending_move_checked_at", "expected_owner", "expected_model",
    "required_verdicts", "invalidation_conditions",
}
POST_TRANSITION_FIELDS = {
    "lane", "state", "lifecycle_settled", "session_id", "profile_id",
    "runtime_model", "head", "tag_aligned", "pending_move_clear",
    "execution_expected", "execution_state", "verified",
}
REQUIRED_TRANSITION_VERDICTS = {
    "review": {"AUTHOR_TESTS=PASSED", "HEAD_PUSHED=CLEAN"},
    "qa": {"REVIEW_RESULT=PASSED"},
    "todeploy": {"PROVIDER_DELIVERY=MERGED_OR_RELEASED"},
    "done": {"DONE_INTEGRITY=PASSED"},
}


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _iso(value):
    if not _nonempty(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _timestamp(value):
    if not _iso(value):
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _ids(value, path, failures):
    if not isinstance(value, list) or any(not _nonempty(v) for v in value):
        failures.append((path, "must be a list of non-empty task IDs"))
        return []
    if len(value) != len(set(value)):
        failures.append((path, "contains duplicate task IDs"))
    return value


def _index(records, path, failures):
    if not isinstance(records, list):
        failures.append((path, "must be a list"))
        return {}
    out = {}
    for idx, record in enumerate(records):
        if not isinstance(record, dict) or not _nonempty(record.get("task_id")):
            failures.append((f"{path}[{idx}]", "must contain non-empty task_id"))
            continue
        task_id = record["task_id"]
        if task_id in out:
            failures.append((path, f"duplicate record for task {task_id}"))
        out[task_id] = record
    return out


def validate(receipt):
    failures = []
    if receipt.get("schema_version") != SCHEMA_VERSION:
        failures.append(("schema_version", f"must be {SCHEMA_VERSION!r}"))
    scope = receipt.get("scope")
    if scope not in {"cycle", "status"}:
        failures.append(("scope", "must be 'cycle' or 'status'"))
    cycle_id = receipt.get("cycle_id")
    if not _nonempty(cycle_id):
        failures.append(("cycle_id", "must be non-empty"))
    if not _iso(receipt.get("observed_at")):
        failures.append(("observed_at", "must be ISO-8601"))

    if scope == "cycle":
        live_ids = _ids(receipt.get("live_task_ids"), "live_task_ids", failures)
        expected_ids = set(live_ids)
    else:
        scoped_ids = _ids(receipt.get("scope_task_ids"), "scope_task_ids", failures)
        expected_ids = set(scoped_ids)
    ledger_ids = _ids(receipt.get("open_ledger_task_ids"), "open_ledger_task_ids", failures)
    if expected_ids != set(ledger_ids):
        failures.append(("G1", f"scope/live IDs and open ledger IDs differ: missing={sorted(expected_ids-set(ledger_ids))}, extra={sorted(set(ledger_ids)-expected_ids)}"))

    ledger = _index(receipt.get("ledger_entries"), "ledger_entries", failures)
    if set(ledger) != set(ledger_ids):
        failures.append(("G2", "ledger entry task IDs must exactly equal open_ledger_task_ids"))
    required_entry = {
        "owner", "health", "last_action", "next_action", "trigger", "fallback",
        "evidence_generation", "lane", "last_checked_cycle_id",
        "anomalous", "mutated", "transitioned", "delivery_status",
    }
    for task_id, entry in ledger.items():
        missing = sorted(k for k in required_entry if k not in entry)
        if missing:
            failures.append(("G2", f"{task_id} missing fields {missing}"))
            continue
        for key in ("owner", "last_action", "trigger", "fallback", "evidence_generation", "lane"):
            if not _nonempty(entry.get(key)):
                failures.append(("G2", f"{task_id}.{key} must be non-empty"))
        if entry.get("health") not in HEALTH_CLASSES:
            failures.append(("G2", f"{task_id}.health is invalid"))
        action = str(entry.get("next_action", "")).strip().lower().rstrip(".")
        if action in GENERIC_ACTIONS:
            failures.append(("G2", f"{task_id}.next_action is not executable"))
        if entry.get("last_checked_cycle_id") != cycle_id:
            failures.append(("G2", f"{task_id} was not checked in this receipt's cycle"))
        if not isinstance(entry.get("anomalous"), bool) or not isinstance(entry.get("mutated"), bool) or not isinstance(entry.get("transitioned"), bool):
            failures.append(("G2", f"{task_id} anomaly/mutation/transition flags must be boolean"))
        if entry.get("delivery_status") not in DELIVERY_STATUSES:
            failures.append(("G2", f"{task_id}.delivery_status is invalid"))

    blocked_ids = set(_ids(receipt.get("blocked_task_ids", []), "blocked_task_ids", failures))
    blocked = _index(receipt.get("blocked_records", []), "blocked_records", failures)
    expected_blocked = {task_id for task_id, entry in ledger.items() if str(entry.get("lane", "")).lower() == "blocked"}
    if blocked_ids != expected_blocked or set(blocked) != blocked_ids:
        failures.append(("G3", "physical Blocked IDs, ledger Blocked lanes, and blocked records must match exactly"))
    for task_id, record in blocked.items():
        missing = sorted(k for k in BLOCKED_FIELDS if k not in record)
        if missing:
            failures.append(("G3", f"{task_id} blocked record missing {missing}"))
        for key in BLOCKED_FIELDS - {"attempt_count"}:
            if not _nonempty(record.get(key)):
                failures.append(("G3", f"{task_id}.{key} must be non-empty"))
        if not isinstance(record.get("attempt_count"), int) or record.get("attempt_count", -1) < 0:
            failures.append(("G3", f"{task_id}.attempt_count must be a non-negative integer"))
        if record.get("last_checked_cycle_id") != cycle_id:
            failures.append(("G3", f"{task_id} blocker was not checked this cycle"))

    anomalies = _index(receipt.get("anomalies", []), "anomalies", failures)
    expected_anomalies = {task_id for task_id, entry in ledger.items() if entry.get("anomalous")}
    if set(anomalies) != expected_anomalies:
        failures.append(("G4", "anomaly records must exactly match ledger anomalous flags"))
    for task_id, record in anomalies.items():
        if record.get("owner_contact") not in {"obtained", "unsafe", "unavailable"}:
            failures.append(("G4", f"{task_id}.owner_contact is invalid"))
        if record.get("owner_contact") == "obtained" and not _nonempty(record.get("owner_account")):
            failures.append(("G4", f"{task_id} obtained owner contact but has no owner account"))
        surfaces = record.get("independent_surfaces")
        if not isinstance(surfaces, list) or not surfaces or any(not _nonempty(v) for v in surfaces):
            failures.append(("G4", f"{task_id} needs independently verified named surfaces"))
        if not _nonempty(record.get("verification_result")):
            failures.append(("G4", f"{task_id} missing independent verification result"))

    deliveries = _index(receipt.get("delivery_claims", []), "delivery_claims", failures)
    expected_deliveries = {task_id for task_id, entry in ledger.items() if entry.get("delivery_status") != "none"}
    if set(deliveries) != expected_deliveries:
        failures.append(("G5", "delivery claims must exactly match non-'none' ledger delivery statuses"))
    for task_id, record in deliveries.items():
        for key in ("claim", "task_head", "remote_ref", "canonical_delivery", "provider_state", "observed_at"):
            if not _nonempty(record.get(key)):
                failures.append(("G5", f"{task_id}.{key} must be non-empty"))
        if not _iso(record.get("observed_at")):
            failures.append(("G5", f"{task_id}.observed_at must be ISO-8601"))
        if record.get("remote_reachable") is not True or record.get("contained") is not True:
            failures.append(("G5", f"{task_id} lacks positive remote/provider containment"))
        if ledger.get(task_id, {}).get("delivery_status") in {"delivered", "deployable", "to_deploy_ready", "terminal"}:
            provider_state = str(record.get("provider_state", "")).strip().lower()
            if provider_state not in TERMINAL_PROVIDER_STATES:
                failures.append(("G5", f"{task_id} delivery claim is not in a terminal provider state"))

    transitions = _index(receipt.get("transitions", []), "transitions", failures)
    expected_transitions = {task_id for task_id, entry in ledger.items() if entry.get("transitioned")}
    if set(transitions) != expected_transitions:
        failures.append(("G6", "transition records must exactly match ledger transitioned flags"))
    for task_id, record in transitions.items():
        if not _nonempty(record.get("transition_id")):
            failures.append(("G6", f"{task_id}.transition_id must be non-empty"))
        pre, post = record.get("pre", {}), record.get("post", {})
        missing_pre = sorted(k for k in PRE_TRANSITION_FIELDS if k not in pre)
        missing_post = sorted(k for k in POST_TRANSITION_FIELDS if k not in post)
        if missing_pre:
            failures.append(("G6", f"{task_id} pre-transition missing {missing_pre}"))
        if missing_post:
            failures.append(("G7", f"{task_id} post-transition missing {missing_post}"))
        if pre.get("target_lane") != post.get("lane"):
            failures.append(("G7", f"{task_id} target lane does not match post lane"))
        if pre.get("evidence_generation") != ledger.get(task_id, {}).get("evidence_generation"):
            failures.append(("G6", f"{task_id} transition used a stale evidence generation"))
        target_lane = "".join(ch for ch in str(pre.get("target_lane", "")).lower() if ch.isalnum())
        verdicts = pre.get("required_verdicts")
        if not isinstance(verdicts, list) or any(not _nonempty(v) for v in verdicts):
            failures.append(("G6", f"{task_id} required_verdicts must be a list of non-empty receipts"))
            verdicts = []
        required = REQUIRED_TRANSITION_VERDICTS.get(target_lane, set())
        if not required.issubset(set(verdicts)):
            failures.append(("G6", f"{task_id} transition to {pre.get('target_lane')!r} lacks predecessor verdicts {sorted(required-set(verdicts))}"))
        if target_lane == "pr" and not (
            "QA_RESULT=PASSED" in verdicts
            or any(v.startswith("QA_NOT_APPLICABLE:") and v.split(":", 1)[1].strip() for v in verdicts)
        ):
            failures.append(("G6", f"{task_id} transition to PR lacks QA_RESULT=PASSED or a reasoned QA_NOT_APPLICABLE receipt"))
        if post.get("lifecycle_settled") is not True or post.get("verified") is not True:
            failures.append(("G7", f"{task_id} transition is not settled and verified"))
        if post.get("tag_aligned") is not True or post.get("pending_move_clear") is not True:
            failures.append(("G7", f"{task_id} transition tag/pending-move readback failed"))
        if post.get("execution_expected") is True and post.get("execution_state") not in {"RUNNING", "STARTING"}:
            failures.append(("G7", f"{task_id} expected execution did not start"))

    mutations = receipt.get("mutations", [])
    if not isinstance(mutations, list):
        failures.append(("G8", "mutations must be a list"))
        mutations = []
    mutated_ids = set()
    for idx, mutation in enumerate(mutations):
        task_id = mutation.get("task_id") if isinstance(mutation, dict) else None
        if not _nonempty(task_id):
            failures.append(("G8", f"mutation {idx} missing task_id"))
            continue
        mutated_ids.add(task_id)
        for key in ("kind", "target", "result", "readback"):
            if not _nonempty(mutation.get(key)):
                failures.append(("G8", f"mutation {idx}.{key} must be non-empty"))
        if mutation.get("verified") is not True:
            failures.append(("G8", f"mutation {idx} is not verified"))
    expected_mutated = {task_id for task_id, entry in ledger.items() if entry.get("mutated")}
    if mutated_ids != expected_mutated:
        failures.append(("G8", "mutation task IDs must exactly match ledger mutated flags"))

    continuity = receipt.get("continuity", {})
    plan_bytes = continuity.get("plan_bytes")
    if not isinstance(plan_bytes, int) or plan_bytes < 0:
        failures.append(("G9", "continuity.plan_bytes must be a non-negative integer"))
        plan_bytes = 10**9
    if continuity.get("soft_limit_bytes") != 200000 or continuity.get("hard_limit_bytes") != 240000:
        failures.append(("G9", "continuity size limits must be 200000/240000"))
    if plan_bytes >= 240000:
        failures.append(("G9", "live plan is at or above hard stop"))
    elif plan_bytes >= 200000:
        failures.append(("G9", "completed receipt must leave the live plan below the compaction threshold"))
    for key in ("write_readback_verified", "current_snapshot_first", "open_record_sets_preserved"):
        if continuity.get(key) is not True:
            failures.append(("G9", f"continuity.{key} must be true"))
    if continuity.get("compaction_performed") is True:
        for key in ("archive_path", "archive_sha256", "pre_open_ids_hash", "post_open_ids_hash"):
            if not _nonempty(continuity.get(key)):
                failures.append(("G9", f"compaction requires continuity.{key}"))
        if continuity.get("pre_open_ids_hash") != continuity.get("post_open_ids_hash"):
            failures.append(("G9", "pre/post open ID hashes differ"))

    report = receipt.get("report", {})
    mentioned = set(_ids(report.get("mentioned_task_ids", []), "report.mentioned_task_ids", failures))
    if not mentioned.issubset(expected_ids):
        failures.append(("G10", "report mentions tasks outside receipt scope"))
    if not _iso(report.get("barrier_at")) or report.get("fresh") is not True:
        failures.append(("G10", "report barrier is missing, invalid, or stale"))
    receipt_time = _timestamp(receipt.get("observed_at"))
    report_time = _timestamp(report.get("barrier_at"))
    if receipt_time and report_time and report_time < receipt_time:
        failures.append(("G10", "report barrier predates receipt observation"))
    barriers = _index(report.get("task_barriers", []), "report.task_barriers", failures)
    if set(barriers) != mentioned:
        failures.append(("G10", "every mentioned task needs exactly one freshness barrier"))
    for task_id, barrier in barriers.items():
        lane_time = _timestamp(barrier.get("lane_session_observed_at"))
        if lane_time is None:
            failures.append(("G10", f"{task_id} lane/session barrier is invalid"))
        elif receipt_time and lane_time < receipt_time:
            failures.append(("G10", f"{task_id} lane/session barrier predates receipt observation"))
        elif report_time and lane_time > report_time:
            failures.append(("G10", f"{task_id} lane/session barrier is later than the report barrier"))
        if barrier.get("provider_required") is True:
            provider_time = _timestamp(barrier.get("provider_observed_at"))
            if provider_time is None:
                failures.append(("G10", f"{task_id} provider barrier is required but invalid"))
            elif receipt_time and provider_time < receipt_time:
                failures.append(("G10", f"{task_id} provider barrier predates receipt observation"))
            elif report_time and provider_time > report_time:
                failures.append(("G10", f"{task_id} provider barrier is later than the report barrier"))

    declared = receipt.get("gate_results")
    if not isinstance(declared, dict) or set(declared) != {f"G{i}" for i in range(1, 11)}:
        failures.append(("gate_results", "must contain exactly G1 through G10"))
    elif any(value != "pass" for value in declared.values()):
        failures.append(("gate_results", "all declared gate results must be 'pass'"))

    return failures


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt")
    args = parser.parse_args(argv)
    try:
        with open(args.receipt, encoding="utf-8") as handle:
            receipt = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"input: {exc}", file=sys.stderr)
        return 1
    failures = validate(receipt)
    for gate, message in failures:
        print(f"{gate}: {message}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
