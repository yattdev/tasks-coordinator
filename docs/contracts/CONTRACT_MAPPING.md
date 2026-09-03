# Contract field mapping, evolution rules, and validator conventions

Status: **agreed 2026-09-03**, implementing `docs/DECISIONS.md#coordinator-policy-is-contract-validated-not-hand-copied-2026-09-03-human-directed`.

This document is the canonical reference for `coordinator-policy-contract.json`.
It exists so a reviewer (or the plugin repository's CI) can answer, for any
field: *where does this come from, and what changes are compatible versus
breaking?* It is deliberately separate from the contract file itself, which
stays compact and machine-readable.

## 1. What the contract is, and is not

- The contract is a **compact, versioned, machine-readable extract** of stable
  cross-runtime invariants — not a serialized copy of `PROMPT.md`, and it never
  contains live board state (task/session IDs, board rows, in-flight queue
  entries).
- It captures **authority boundaries, ownership shape, identity/receipt
  requirements, gate requirements, notification ordering, and escalation
  classes** — the parts of the charter that the plugin's scheduler/prompt
  bundle must not silently drift from.
- It excludes secrets, credentials, and anything transient (`exclusions`
  field). If a future field would require a secret or a transient ID to be
  meaningful, it does not belong in this contract.
- Scale/load architecture, the burst-harness spec, and state-compaction
  mechanics are **delivery specifications**, not contract invariants (see the
  2026-09-03 decision's final paragraph). They live in `docs/rfcs/` and are
  referenced from the contract's mapping table below only where a contract
  field constrains them (e.g. `worker_helper_receipts.workers_never_mutate` is
  an invariant the scale RFC's read-only worker pool must satisfy).

## 2. Field-by-field source mapping

| Contract field | Canonical source | Notes |
| --- | --- | --- |
| `source_charter_effective_version` | `PROMPT.md` line 2 (`<!-- effective-version: ... -->`) | Bump whenever `PROMPT.md`'s effective-version header changes in a way that touches any mapped field below. |
| `source_decision_anchor` | `docs/DECISIONS.md#coordinator-policy-is-contract-validated-not-hand-copied-2026-09-03-human-directed` | The decision that authorizes this contract's existence. |
| `authority_boundaries.approval_principal`, `.scope`, `.cross_workspace_authority` | `PROMPT.md` "FULL COORDINATOR APPROVAL AUTHORITY" section (same-workspace approval principal); `docs/FILESYSTEM_DOCKER_CONTRACT.md` §3 (workspace-scoped authority, peers have no standing over each other) | Cross-workspace authority is always `false`; no evolution may set it `true`. |
| `authority_boundaries.coordinator_decidable_examples` | `PROMPT.md` "Everything else is Coordinator-decidable" paragraph | Additive (new examples) is a **minor** change; removing an example without a corresponding Human-reserved reclassification is **breaking**. |
| `authority_boundaries.human_reserved_classes` | `PROMPT.md` "The only approval classes reserved for the Human are (1)... (2)..." | These two classes (`destructive_or_irreversible`, `security_or_trust_boundary`) are the floor. A contract or overlay may only add to this set, never remove from it — enforced by the validator's `missing_required_invariant` / `overlay_widens_authority` checks. |
| `workspace_lane_ownership.*` | `PROMPT.md` "Monitor every task in spec, work, review, qa, pr, ci-fixup, AND Done"; `docs/FILESYSTEM_DOCKER_CONTRACT.md` §3 (peer workspaces) | `done_is_terminal_integrity_lane` must stay `true` — Done is never an ignored archive. |
| `queue_claim_identity.*` | `PROMPT.md` "Queue identity and disposition are per-entry..." paragraph (queue helpers/coalescing section) | `audit_model` must stay `exact_entry_never_global_watermark`; this is the specific defect class the 2026-09-01j decision closed. |
| `worker_helper_receipts.*` | `PROMPT.md` "helpers never mutate the board, provider, task worktrees..." paragraph; "A helper receipt never proves that its source queue row was claimed..." | `workers_never_mutate` is a floor invariant shared with the scale RFC's read-only worker pool design. |
| `gates.review`, `gates.qa`, `gates.readiness`, `gates.done_integrity` | `PROMPT.md` "exact-head Review/QA/CI readiness" (multiple sections); "DONE TERMINAL-INTEGRITY GATE" | All four must keep `exact_head_required: true`. This is the single most load-bearing invariant in the contract — it is what stops a stale-head approval. |
| `readiness_notification_order` | `PROMPT.md` "universal reviewer-request ordering is strict: provider-confirmed ready/non-draft first, then refreshed post-ready gates, then and only then reviewer notification" | Order is fixed; reordering is **breaking**. |
| `escalation_classes.human_reserved[].includes` | `PROMPT.md` "Destructive includes deletion, reset/clean/discard..." / "Security includes secret/credential disclosure..." | Additive is **minor**; removing an item from `includes` without also removing it from the `PROMPT.md` prose is **breaking** (and would itself require a Human-directed decision, per the escalation-classes rule). |
| `escalation_classes.label_alone_does_not_escalate` | `PROMPT.md` "Labels such as production, protected/release branch, cost, or external communication do not by themselves create a second approval principal" | Advisory list; additive-only. |
| `done_integrity.required_proof`, `.receipt_fields` | `PROMPT.md` "Before any move to Done, explicitly prove..." and the terminal-receipt paragraph | Mirrors `docs/FILESYSTEM_DOCKER_CONTRACT.md`'s audit-trail convention (name the exact fields, never an aggregate claim). |
| `exclusions` | `docs/DECISIONS.md#coordinator-policy-is-contract-validated-not-hand-copied-2026-09-03-human-directed` (second paragraph) | Category names only (e.g. `"secrets"`), never example values. |

## 3. Compatible vs. breaking evolution

The contract uses a `MAJOR.MINOR.PATCH` `contract_version`, checked by the
validator against `compatibility.min_supported_contract_version` and
`compatibility.max_known_contract_version`.

- **PATCH** — wording/clarification only; no field added, removed, or
  semantically changed. Digest still changes (any byte change moves the
  digest), but no invariant check result can change. Example: fixing a typo in
  an `includes` string.
- **MINOR** — backward-compatible addition: a new optional field, a new
  `coordinator_decidable_examples` entry, a new `human_reserved_classes` entry,
  a new `includes` item under an existing escalation class. A plugin vendored
  at the previous minor version remains valid (it simply doesn't yet know
  about the addition); a plugin vendored at the new version must reflect it.
- **MAJOR** — anything that changes what was previously required or allowed:
  removing a `required_fields` entry, weakening any `gates.*.exact_head_required`
  or `worker_helper_receipts.workers_never_mutate` or
  `queue_claim_identity.audit_model` invariant, removing a
  `human_reserved_classes` entry, reordering `readiness_notification_order`,
  or widening `cross_workspace_authority`. A **major** bump must cite the
  `PROMPT.md` effective-version change and, if it changes binding authority,
  a corresponding `docs/DECISIONS.md` entry — never a silent contract-only
  change to authority.

Bumping `contract_version` always requires recomputing `digest` (see §5) and
updating `source_charter_effective_version` if the underlying charter section
moved.

## 4. Plugin vendoring

1. The plugin repository vendors an **exact copy** of
   `coordinator-policy-contract.json` (or the fields it actually consumes,
   still under the same `contract_version`/`digest`) plus a copy of
   `validate_contract.py`. Neither file has a runtime dependency on this
   checkout — that's why the validator only takes explicit `--contract`/
   `--snapshot`/`--overlay` paths.
2. Plugin CI runs a **plugin snapshot** through
   `validate_contract.py plugin-snapshot --contract <vendored contract>
   --snapshot <plugin's own defaults dump>` (see `validate_plugin_snapshot()`
   in the validator, and `fixtures/valid_plugin_snapshot.json` /
   `fixtures/contradictory_plugin_snapshot.json` for the expected snapshot
   shape). This is the CI gate the 2026-09-03 decision requires: a version or
   digest mismatch, missing invariant, or a contradictory default
   **must fail the plugin build**.
3. Updating the contract (this repository) and updating the plugin's vendored
   snapshot (the plugin repository) are **separate reviewed changes**. Do not
   bump both in the same PR across repositories — the whole point is that an
   older deployed plugin fails observably (wrong `vendored_digest` /
   `plugin_contract_version`) instead of silently claiming parity.
4. Unsupported version behavior: if the plugin's `plugin_contract_version` is
   older than this contract's `compatibility.min_supported_contract_version`,
   or newer than `compatibility.max_known_contract_version`, the build **must
   fail closed** (`compatibility.unsupported_version_behavior`), never
   silently downgrade to "best effort".

## 5. Workspace-overlay narrowing

A workspace overlay (`fixtures/narrowing_overlay.json` shows a valid shape)
may only ever **narrow** behavior relative to its `base_contract_version`:

- `cross_workspace_authority` may stay `false`; it may never be set `true`.
- `human_reserved_classes` may only **grow** (a workspace can decide more
  classes need Human sign-off than the floor requires; it can never shrink
  the floor).
- `coordinator_decidable_examples` may only **shrink** (a workspace can
  decide fewer things are Coordinator-decidable; it can never add a new
  decidable example the base contract didn't already list).

`validate_overlay()` enforces exactly these three checks and reports
`overlay_widens_authority` for any violation. An overlay is validated against
the same `--contract` path as everything else; it is never self-certifying.

## 6. Digest computation (reproducible without importing the validator)

`digest` is `sha256` over the contract's own JSON body, minus the `digest`
field itself, serialized with `json.dumps(doc, sort_keys=True,
separators=(",", ":"))` (compact, UTF-8, sorted keys — no field ordering or
whitespace dependency). Any tool in any language can reproduce this by:

1. Parsing the contract JSON.
2. Deleting the top-level `digest` key.
3. Re-serializing with keys sorted and no insignificant whitespace.
4. Hashing the UTF-8 bytes with SHA-256.

This is implemented once in `validate_contract.py:compute_digest` — the
canonical, tested implementation — but the algorithm above is intentionally
simple enough to reimplement in the plugin's own language/toolchain if
preferred, as long as it is round-trip tested against this contract's
published `digest` before being trusted.

## 7. Failure behavior for unsupported contract versions

- A contract whose `contract_version` is below its own
  `compatibility.min_supported_contract_version`, or a `required_fields` list
  containing an entry this validator's `REQUIRED_TOP_LEVEL_FIELDS` doesn't
  recognize, is invalid — **fail closed**, never "pass with a warning".
- A plugin build that cannot resolve a contract file at all (missing vendor
  copy, path not passed) must treat that the same as a failing validation run
  — it must not fall back to trusting its own hardcoded prompt defaults.
- See `docs/rfcs/PLUGIN_SCALE_RFC.md` and `docs/rfcs/STATE_COMPACTION_SPEC.md`
  for how this contract's invariants (`workers_never_mutate`, exact-head
  gates, single-writer mutation lane, exact-entry queue identity) are
  satisfied by the scale/compaction designs; those documents do not
  reintroduce or relax any invariant defined here.

## 8. Related documents

- [`coordinator-policy-contract.json`](coordinator-policy-contract.json) — the contract itself.
- [`validate_contract.py`](validate_contract.py) — the standalone validator.
- [`test_validate_contract.py`](test_validate_contract.py) — the test suite (`python3 -m unittest docs/contracts/test_validate_contract.py -v`).
- [`fixtures/`](fixtures/) — one fixture per required validator scenario (valid contract, stale version, stale digest, missing invariant, unknown required field, contradictory plugin snapshot, widening overlay, plus positive controls).
- [`../rfcs/PLUGIN_SCALE_RFC.md`](../rfcs/PLUGIN_SCALE_RFC.md) — scale/load architecture and the 70-task/50-message burst harness.
- [`../rfcs/STATE_COMPACTION_SPEC.md`](../rfcs/STATE_COMPACTION_SPEC.md) — safe state compaction.
