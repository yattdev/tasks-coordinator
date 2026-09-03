#!/usr/bin/env python3
"""Standalone validator for the Coordinator policy contract.

Purpose
-------
This script has NO runtime dependency on the Coordinator knowledge-repository
checkout: it only needs the contract JSON (and, for the optional checks, a
plugin-snapshot or workspace-overlay JSON) passed in via explicit paths. The
Coordinator plugin repository may vendor this single file plus its vendored
copy of ``coordinator-policy-contract.json`` and run it in CI without cloning
this repository.

Stdlib only. No third-party dependencies. Python >= 3.8.

Usage
-----
    validate_contract.py contract --contract path/to/contract.json
    validate_contract.py plugin-snapshot --contract path/to/contract.json \
        --snapshot path/to/plugin-snapshot.json
    validate_contract.py overlay --contract path/to/contract.json \
        --overlay path/to/workspace-overlay.json

Exit code 0 on success, 1 on any validation failure. Failures are printed one
per line to stderr, prefixed with the failing check name, so CI logs stay
legible (see FILESYSTEM_DOCKER_CONTRACT.md's "denials fail closed and must be
legible" convention, applied here to contract validation).
"""

import argparse
import copy
import hashlib
import json
import sys

# Bump this only when this validator itself changes what it can recognize.
# The contract's own compatibility.max_known_contract_version is the field
# the validator checks the contract against; VALIDATOR_SCHEMA_VERSION is
# reported in --version output only.
VALIDATOR_SCHEMA_VERSION = "1.0.1"

# The highest contract_version this validator BUILD understands, hardcoded in
# code rather than read from the contract document. A contract's own
# compatibility.max_known_contract_version is self-declared: a future or
# malicious contract could set contract_version, min_supported_contract_version,
# and max_known_contract_version all to e.g. "2.0.0" in the same document, and
# the same-document check in validate_contract() (which only compares the
# contract against itself) would find it internally consistent and pass it.
# This constant is the independent, non-forgeable ceiling: it is what THIS
# validator source file was actually written to understand, so it cannot be
# smuggled past by anything inside the JSON body. Bump it only when this
# validator is upgraded to actually understand a newer contract_version.
VALIDATOR_MAX_SUPPORTED_CONTRACT_VERSION = "1.0.0"

# The exact, ordered readiness/notification sequence required by the
# contract (see CONTRACT_MAPPING.md: "Order is fixed; reordering is
# breaking"). Checked as a full sequence, not just first/last elements, so a
# contract that drops or reorders the middle `refreshed_post_ready_gates`
# step (the post-ready-gate refresh between provider-ready confirmation and
# reviewer notification) is rejected.
REQUIRED_READINESS_NOTIFICATION_ORDER = [
    "provider_confirmed_ready_nondraft",
    "refreshed_post_ready_gates",
    "reviewer_notification",
]

# Mandatory plugin-snapshot `defaults` keys. A snapshot with a missing or
# empty `defaults` object -- or missing any one of these keys -- declares no
# verifiable invariants at all and must fail closed rather than silently
# pass (an empty object trivially satisfies "no field contradicts the
# contract").
REQUIRED_PLUGIN_SNAPSHOT_DEFAULT_KEYS = [
    "human_reserved_classes",
    "exact_head_gates",
    "workers_never_mutate",
    "cross_workspace_authority",
]

DIGEST_EXCLUDED_FIELDS = ("digest",)

REQUIRED_TOP_LEVEL_FIELDS = [
    "contract_id",
    "contract_version",
    "source_charter_effective_version",
    "source_decision_anchor",
    "generated_at",
    "digest_algorithm",
    "digest",
    "compatibility",
    "required_fields",
    "authority_boundaries",
    "workspace_lane_ownership",
    "queue_claim_identity",
    "worker_helper_receipts",
    "gates",
    "readiness_notification_order",
    "escalation_classes",
    "done_integrity",
    "exclusions",
]

REQUIRED_GATE_KEYS = ["review", "qa", "readiness", "done_integrity"]

REQUIRED_HUMAN_RESERVED_CLASSES = {
    "destructive_or_irreversible",
    "security_or_trust_boundary",
}

FORBIDDEN_EXCLUSION_LEAKS = ["secret", "credential", "password", "token"]

# Bare category names are the expected, safe shape of an `exclusions` entry
# (see CONTRACT_MAPPING.md: "Category names only ... never example values").
# Anything else that matches a FORBIDDEN_EXCLUSION_LEAKS term is treated as
# an embedded secret-shaped value, not a category reference.
ALLOWED_BARE_EXCLUSION_CATEGORIES = {"secrets", "credentials"}


class ValidationError(Exception):
    """Raised with a list of (check_name, message) failures."""

    def __init__(self, failures):
        self.failures = failures
        super().__init__("; ".join(f"{c}: {m}" for c, m in failures))


def _load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def canonical_bytes(contract, exclude=DIGEST_EXCLUDED_FIELDS):
    """Deterministic canonical serialization used for the digest.

    Rules (documented in CONTRACT_MAPPING.md so plugin CI can reproduce this
    independently without importing this script):
      1. Start from the top-level object only (this contract format is not
         recursively digested field-by-field; the whole document minus the
         excluded fields is canonicalized).
      2. Drop the excluded top-level fields (currently just ``digest`` -- the
         digest cannot include itself).
      3. Serialize with ``sort_keys=True``, no extra whitespace, UTF-8.
    """
    working = copy.deepcopy(contract)
    for field in exclude:
        working.pop(field, None)
    return json.dumps(working, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compute_digest(contract, algorithm="sha256"):
    if algorithm != "sha256":
        raise ValidationError([("digest_algorithm", f"unsupported algorithm '{algorithm}'")])
    return hashlib.sha256(canonical_bytes(contract)).hexdigest()


def validate_contract(contract):
    """Validate a contract document. Returns list of (check, message) failures."""
    failures = []

    # 1. Required top-level fields present (schema/unknown-required-field check).
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in contract:
            failures.append(("required_fields", f"missing required top-level field '{field}'"))

    # An unrecognized *additional* required_fields entry this validator does
    # not know about means the document declares invariants this validator
    # cannot check -- fail closed rather than silently pass a newer/foreign
    # schema.
    declared_required = contract.get("required_fields", [])
    if isinstance(declared_required, list):
        unknown = [f for f in declared_required if f not in REQUIRED_TOP_LEVEL_FIELDS]
        if unknown:
            failures.append((
                "unknown_required_field",
                f"contract declares required field(s) unknown to this validator: {unknown}",
            ))
    else:
        failures.append(("required_fields", "'required_fields' must be a list"))

    if failures and not all(f in contract for f in ("digest", "digest_algorithm", "compatibility")):
        # Cannot safely continue version/digest checks without these fields.
        return failures

    # 2. Version support check.
    compat = contract.get("compatibility", {})
    max_known = compat.get("max_known_contract_version")
    min_supported = compat.get("min_supported_contract_version")
    version = contract.get("contract_version")
    if max_known and version and _version_tuple(version) > _version_tuple(max_known):
        failures.append((
            "stale_validator_or_future_contract",
            f"contract_version {version} exceeds this contract's own "
            f"declared max_known_contract_version {max_known}; treat as "
            "unsupported per compatibility.unsupported_version_behavior",
        ))
    if min_supported and version and _version_tuple(version) < _version_tuple(min_supported):
        failures.append((
            "stale_version",
            f"contract_version {version} is older than "
            f"min_supported_contract_version {min_supported}",
        ))
    # 2b. Independent, hardcoded ceiling (cannot be forged by the document
    # itself -- see VALIDATOR_MAX_SUPPORTED_CONTRACT_VERSION). A contract
    # that self-declares contract_version 2.0.0 alongside a matching
    # compatibility.max_known_contract_version of 2.0.0 passes check #2
    # above (it is internally consistent with itself) but must still be
    # rejected here, because this validator build was never actually written
    # to understand a 2.0.0 schema.
    if version and _version_tuple(version) > _version_tuple(VALIDATOR_MAX_SUPPORTED_CONTRACT_VERSION):
        failures.append((
            "stale_validator_or_future_contract",
            f"contract_version {version} exceeds "
            f"{VALIDATOR_MAX_SUPPORTED_CONTRACT_VERSION}, the maximum "
            "contract_version this validator build understands (hardcoded "
            "in validate_contract.py, independent of the contract's own "
            "self-declared compatibility fields); upgrade the validator "
            "before trusting a newer contract",
        ))

    # 3. Digest check.
    algorithm = contract.get("digest_algorithm", "sha256")
    declared_digest = contract.get("digest")
    try:
        recomputed = compute_digest(contract, algorithm)
    except ValidationError as exc:
        failures.extend(exc.failures)
        recomputed = None
    if recomputed is not None and declared_digest != recomputed:
        failures.append((
            "stale_digest",
            f"declared digest {declared_digest!r} does not match recomputed "
            f"digest {recomputed!r} over the canonical contract body",
        ))

    # 4. Required invariants: human-reserved escalation classes must be present
    #    and must not be narrowed (that would silently widen Coordinator
    #    authority into a Human-reserved class).
    authority = contract.get("authority_boundaries", {})
    reserved = set(authority.get("human_reserved_classes", []))
    missing_invariant = REQUIRED_HUMAN_RESERVED_CLASSES - reserved
    if missing_invariant:
        failures.append((
            "missing_required_invariant",
            f"authority_boundaries.human_reserved_classes is missing required "
            f"class(es): {sorted(missing_invariant)}",
        ))
    if authority.get("cross_workspace_authority", False) is not False:
        failures.append((
            "missing_required_invariant",
            "authority_boundaries.cross_workspace_authority must be false",
        ))

    # 5. Gates must all require exact-head evidence.
    gates = contract.get("gates", {})
    for gate_name in REQUIRED_GATE_KEYS:
        gate = gates.get(gate_name)
        if not isinstance(gate, dict):
            failures.append(("missing_required_invariant", f"gates.{gate_name} is missing"))
            continue
        if gate.get("exact_head_required") is not True:
            failures.append((
                "missing_required_invariant",
                f"gates.{gate_name}.exact_head_required must be true",
            ))

    # 6. Queue claim identity must be per-entry, never a global watermark.
    queue = contract.get("queue_claim_identity", {})
    if queue.get("audit_model") != "exact_entry_never_global_watermark":
        failures.append((
            "missing_required_invariant",
            "queue_claim_identity.audit_model must be "
            "'exact_entry_never_global_watermark'",
        ))
    if queue.get("identity_scope") != "per_entry":
        failures.append((
            "missing_required_invariant",
            "queue_claim_identity.identity_scope must be 'per_entry'",
        ))

    # 7. Worker/helper receipts: workers must never mutate.
    receipts = contract.get("worker_helper_receipts", {})
    if receipts.get("workers_never_mutate") is not True:
        failures.append((
            "missing_required_invariant",
            "worker_helper_receipts.workers_never_mutate must be true",
        ))

    # 8. Readiness/notification order must be the exact ordered sequence,
    # not merely start/end correctly. Checking only the first and last
    # elements would silently accept a contract that dropped or reordered
    # the required middle `refreshed_post_ready_gates` step (contradictory-
    # order check).
    order = contract.get("readiness_notification_order", [])
    if list(order) != REQUIRED_READINESS_NOTIFICATION_ORDER:
        failures.append((
            "contradictory_plugin_prompt_default",
            "readiness_notification_order must be the exact ordered "
            f"sequence {REQUIRED_READINESS_NOTIFICATION_ORDER}, got {order!r}",
        ))

    # 9. Exclusions must not themselves leak secret-shaped content. Check
    # each entry independently (never the whole list joined together, which
    # would mask a leaking entry among legitimate bare category names).
    exclusions = contract.get("exclusions", [])
    for entry in exclusions:
        normalized = str(entry).strip().lower()
        if normalized in ALLOWED_BARE_EXCLUSION_CATEGORIES:
            continue
        for leak_term in FORBIDDEN_EXCLUSION_LEAKS:
            if leak_term in normalized:
                failures.append((
                    "exclusion_leaks_secret",
                    f"exclusions entry {entry!r} looks like a secret-shaped "
                    f"value (matched {leak_term!r}); exclusions may only "
                    "name categories (e.g. 'secrets', 'credentials'), never "
                    "embed actual secret-shaped content",
                ))
                break

    return failures


def _version_tuple(version_str):
    parts = []
    for part in str(version_str).split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def validate_plugin_snapshot(contract, snapshot):
    """Validate a vendored plugin snapshot against the canonical contract.

    Expected snapshot shape:
        {
          "plugin_contract_version": "1.0.0",
          "vendored_digest": "<sha256>",
          "defaults": {
             "human_reserved_classes": [...],
             "exact_head_gates": true,
             "workers_never_mutate": true,
             "cross_workspace_authority": false
          }
        }
    """
    failures = []
    contract_version = contract.get("contract_version")
    plugin_version = snapshot.get("plugin_contract_version")
    if plugin_version != contract_version:
        failures.append((
            "stale_version",
            f"plugin_contract_version {plugin_version!r} does not match "
            f"contract_version {contract_version!r}",
        ))

    try:
        expected_digest = compute_digest(contract, contract.get("digest_algorithm", "sha256"))
    except ValidationError as exc:
        failures.extend(exc.failures)
        expected_digest = None
    vendored_digest = snapshot.get("vendored_digest")
    if expected_digest is not None and vendored_digest != expected_digest:
        failures.append((
            "stale_digest",
            f"snapshot vendored_digest {vendored_digest!r} does not match "
            f"contract digest {expected_digest!r}",
        ))

    defaults = snapshot.get("defaults")
    authority = contract.get("authority_boundaries", {})
    contract_reserved = set(authority.get("human_reserved_classes", []))

    if not isinstance(defaults, dict) or not defaults:
        failures.append((
            "missing_required_invariant",
            "plugin snapshot 'defaults' is missing or empty; a snapshot "
            "must explicitly declare all of "
            f"{REQUIRED_PLUGIN_SNAPSHOT_DEFAULT_KEYS} -- an absent or empty "
            "defaults object trivially satisfies 'no field contradicts the "
            "contract' and must not be treated as a valid snapshot",
        ))
        defaults = {}
    else:
        missing_default_keys = [
            key for key in REQUIRED_PLUGIN_SNAPSHOT_DEFAULT_KEYS if key not in defaults
        ]
        if missing_default_keys:
            failures.append((
                "missing_required_invariant",
                f"plugin snapshot 'defaults' is missing mandatory key(s): "
                f"{missing_default_keys}",
            ))

    snapshot_reserved = set(defaults.get("human_reserved_classes", []))
    if "human_reserved_classes" in defaults and not snapshot_reserved:
        failures.append((
            "missing_required_invariant",
            "plugin snapshot defaults.human_reserved_classes must not be "
            "empty; it must declare the full human-reserved floor",
        ))
    if contract_reserved - snapshot_reserved:
        failures.append((
            "contradictory_plugin_prompt_default",
            "plugin defaults.human_reserved_classes drops required class(es): "
            f"{sorted(contract_reserved - snapshot_reserved)}",
        ))
    if "exact_head_gates" in defaults and defaults["exact_head_gates"] is not True:
        failures.append((
            "contradictory_plugin_prompt_default",
            "plugin defaults.exact_head_gates contradicts contract "
            "(must be true)",
        ))
    if "workers_never_mutate" in defaults and defaults["workers_never_mutate"] is not True:
        failures.append((
            "contradictory_plugin_prompt_default",
            "plugin defaults.workers_never_mutate contradicts contract "
            "(must be true)",
        ))
    if "cross_workspace_authority" in defaults and defaults["cross_workspace_authority"] is not False:
        failures.append((
            "contradictory_plugin_prompt_default",
            "plugin defaults.cross_workspace_authority contradicts contract "
            "(must be false)",
        ))

    return failures


def validate_overlay(contract, overlay):
    """Validate a workspace overlay only narrows, never widens, the contract.

    Expected overlay shape:
        {
          "overlay_id": "workspace-x",
          "base_contract_version": "1.0.0",
          "narrows": {
             "human_reserved_classes": [...],   // may only be a superset
             "cross_workspace_authority": false, // may only stay false
             "coordinator_decidable_examples": [...] // may only be a subset
          }
        }
    """
    failures = []
    base_version = overlay.get("base_contract_version")
    contract_version = contract.get("contract_version")
    if base_version != contract_version:
        failures.append((
            "stale_version",
            f"overlay base_contract_version {base_version!r} does not match "
            f"contract_version {contract_version!r}",
        ))

    narrows = overlay.get("narrows", {})
    authority = contract.get("authority_boundaries", {})

    if "cross_workspace_authority" in narrows and narrows["cross_workspace_authority"] is not False:
        failures.append((
            "overlay_widens_authority",
            "overlay attempts to set cross_workspace_authority to true; "
            "overlays may never widen cross-workspace authority",
        ))

    if "human_reserved_classes" in narrows:
        base_reserved = set(authority.get("human_reserved_classes", []))
        overlay_reserved = set(narrows["human_reserved_classes"])
        removed = base_reserved - overlay_reserved
        if removed:
            failures.append((
                "overlay_widens_authority",
                "overlay removes required human_reserved_classes "
                f"{sorted(removed)}; an overlay may only add to, never "
                "remove from, human-reserved classes (removal widens "
                "Coordinator/plugin authority)",
            ))

    if "coordinator_decidable_examples" in narrows:
        base_decidable = set(authority.get("coordinator_decidable_examples", []))
        overlay_decidable = set(narrows["coordinator_decidable_examples"])
        added = overlay_decidable - base_decidable
        if added:
            failures.append((
                "overlay_widens_authority",
                "overlay adds coordinator_decidable_examples not present in "
                f"the base contract: {sorted(added)}; overlays may only "
                "narrow (subset), never add new decidable classes",
            ))

    return failures


def _print_failures(failures):
    for check, message in failures:
        print(f"FAIL [{check}] {message}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VALIDATOR_SCHEMA_VERSION)
    sub = parser.add_subparsers(dest="mode", required=True)

    p_contract = sub.add_parser("contract", help="Validate a contract document standalone.")
    p_contract.add_argument("--contract", required=True)

    p_snapshot = sub.add_parser("plugin-snapshot", help="Validate a vendored plugin snapshot.")
    p_snapshot.add_argument("--contract", required=True)
    p_snapshot.add_argument("--snapshot", required=True)

    p_overlay = sub.add_parser("overlay", help="Validate a workspace overlay.")
    p_overlay.add_argument("--contract", required=True)
    p_overlay.add_argument("--overlay", required=True)

    args = parser.parse_args(argv)

    contract = _load_json(args.contract)

    if args.mode == "contract":
        failures = validate_contract(contract)
    elif args.mode == "plugin-snapshot":
        failures = validate_contract(contract)
        snapshot = _load_json(args.snapshot)
        failures += validate_plugin_snapshot(contract, snapshot)
    elif args.mode == "overlay":
        failures = validate_contract(contract)
        overlay = _load_json(args.overlay)
        failures += validate_overlay(contract, overlay)
    else:  # pragma: no cover - argparse enforces choices
        parser.error(f"unknown mode {args.mode}")
        return 2

    if failures:
        _print_failures(failures)
        print(f"{len(failures)} check(s) failed.", file=sys.stderr)
        return 1

    print("OK: all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
