# Coordinator learning-cycle log

## 2026-08-21 — semantic merge-result and mixed-CI triage

- Added semantic merge-result triage: a current-main test that contradicts an
  accepted feature invariant is an integration-phase reconciliation problem,
  not permission for Human-QA to regress production behavior or rewrite the
  branch.
- Required fresh testing of the actual merge result after the upstream fixture
  or expectation is corrected under integration authority.
- Added per-job CI classification: runner/artifact/setup breakage remains
  infrastructure, while a deterministic product failure in another shard of
  the same red workflow remains task-owned and actionable.
- Files: `docs/RUNBOOK.md`, `docs/DECISIONS.md`, and this log. `PROMPT.md` was
  unchanged, so no live task-description mirror is required.
- Policy commit: `cc0f3ad` (`docs(coordinator): classify merge-result
  failures`). Shared `main` fast-forwarded successfully with no conflicts or
  unresolved items; this receipt commit was fast-forwarded separately.

## 2026-08-21 — exact-head runtimes and credential-scoped PR recovery

- Made QA-instance validity explicitly exact-head: any push or integration
  commit withdraws readiness until the task-owned LAN container is rebuilt and
  revalidated; stale instances are excluded from current inventories.
- Added a bounded fallback for authorized mechanical PR-thread work when a
  task-local credential broker fails but the Coordinator has its own valid
  repository-scoped identity. The fallback requires canonical repo/head proof,
  concrete code/test evidence, per-thread reply URLs, and a final unresolved
  count; it never transfers credentials or expands into implementation/merge.
- Recorded that provider rate limits make follow-up evidence unavailable, not
  green, and that successful external PR actions during a wedged Kandev session
  do not substitute for a monitoring cycle or board persistence.
- Reinforced that repeated routine wakes cannot recover a wedged task-control
  transport: one bounded probe, terminate, replace the caller session, and do
  not emit a standup or completed-cycle receipt from partial evidence.
- Files: `docs/RUNBOOK.md`, `docs/DECISIONS.md`, and this log. `PROMPT.md` was
  unchanged, so no live task-description mirror is required.
- Policy commit: `305cd10` (`docs(coordinator): tighten recovery evidence
  boundaries`). Shared `main` fast-forwarded successfully with no conflicts or
  unresolved items; this receipt commit was fast-forwarded separately.

## 2026-08-21 — stale sessions and gate ownership

- Captured physical workflow-gate ownership: ad-hoc Work-stage review evidence
  does not skip Review/QA, while a physical exact-head Review PASS must not wait
  on downstream CI.
- Added stale `RUNNING` diagnosis and recovery: verify process/output/timestamp,
  stop repeated queue writes, respect parent-scoped stop authority, and replace
  only a wedged caller session when necessary.
- Recorded that database writes, credential extraction, and shared-backend
  restarts are not task-control recovery mechanisms.
- Added containment guidance for an unauthorized history rewrite and a fresh
  LAN-instance/credential inventory procedure.
- Files: `docs/RUNBOOK.md`, `docs/DECISIONS.md`, `README.md`, and this log.
- Policy commit: `4d98343` (`docs(coordinator): harden stale session recovery`).
- Merge result: shared `main` fast-forwarded successfully to the policy commit;
  no conflicts. The log/link commit was then fast-forwarded separately.
- `PROMPT.md` was unchanged, so no live task-description mirror was required.

## 2026-08-22 — Human-QA instance provisioning cycle

Lessons captured, all incident-derived from a single Human-QA provisioning cycle
across 18 tasks and 16 containers:

- Fixture fit: copying the live database into QA instances is the wrong default.
  It produced a copied `master.key` in a LAN-published container, an instance
  serving the whole board unauthenticated, and several wasted rebuilds — and it
  could not exercise the features anyway. Tasks that refused the instruction were
  right; their refusals contained the incident faster than review did.
- Order of operations: "load real data, then verify isolation" creates the
  exposure before checking it. Features that ACT get synthetic data.
- Evidence discipline: report the primary SESSION state, not the board column. A
  task sat idle and blocked for 90 minutes while being reported as implementing.
- Inherited vs owned failures: bisect before assigning. A launcher panic on a
  73-file PR touched zero launcher files; `upstream/main` itself failed to compile
  and cascaded ~10 red checks onto unrelated clean PRs.
- Shared repairs land once. Narrow cherry-picks only for tasks physically blocked
  from committing locally.
- Provenance: layered images report the BASE OCI revision; plugin binaries carry
  no VCS stamp (`(devel)` + zero pseudo-version); compare payload digests, never
  the outer tarball SHA; a build timestamp is not provenance.
- Green CI is not universal evidence — env-dependent defects pass on runners and
  fail deterministically in agent containers, and the reverse.
- Enumerate-then-fix beats one-item-per-CI-round discovery.
- A host redirect may be deliberate: scope it (`-i <lan-if>` / `! -s 172.16.0.0/12`),
  do not remove it. Verify from a throwaway bridge container.
- An honest "not testable here" beats a display-only fixture, which converts an
  infrastructure gap into a false bug report against the feature.

Files changed: PROMPT.md (version stamp, Human-QA gate extension, triage evidence
rule), docs/QA_INSTANCES.md (new, linked from PROMPT/RUNBOOK/README),
docs/RUNBOOK.md (six playbooks), docs/DECISIONS.md (four decisions), README.md.

Not carried into shared policy: instance ports, container names, credentials,
task IDs, and per-task status — all transient.

## 2026-08-22b — infra fixes, base-branch breakage, task-startup recoveries

Lessons captured since 518382a:

- Task startup: an untrusted worktree `mise.toml` fails sessions at ACP init;
  `mise trust` + respawn is the fix. A subtask stranded in Backlogs must be moved
  to Work before a respawn does anything.
- Broken BASE: `upstream/main` failed to compile and cascaded red CI onto every
  mergeable PR; N tasks independently reporting the same failing line is evidence
  of a broken base, and the fix is landing ONE repair PR, not N cherry-picks.
- Verify operator infra fixes with the defect's own acceptance test — a NAT-rule
  "fixed" report was re-probed from a bridge container and still failed; the
  definitive Docker-egress test is a full `apt-get update`, not just a fetch.
- Deliberate host rules are scoped (inbound iface / exclude container sources),
  never removed.
- rolldown/rollup optional-binding misses after fresh pnpm install are a known
  install artifact, not an environment block; confirm via other worktrees, remedy
  with `pnpm install --force`.
- Ask-channel reaffirmed by the operator: use it for blocked tasks, not just own
  escalations; prose is not surfacing.
- QA: identify which component a UI control belongs to before filing a defect
  (adjacent enhance-prompt-button vs notes-enhance-button phantom defect).

Files: PROMPT.md (ask-channel reaffirmation, verify-operator-fix, version stamp),
docs/RUNBOOK.md (5 playbooks), docs/DECISIONS.md (3 decisions), docs/QA_INSTANCES.md
(phantom-control), docs/LEARNING_LOG.md.

Not carried into shared policy: PR numbers, ports, container names, credentials,
task IDs, per-task status — all transient.

## 2026-08-22c — base-repair recovery, zero-diff disposition

Lessons since a011058:

- Zero-diff platform fix → Done directly (skip PR/CI-Fixup): dd4f90b0's host NAT
  remediation had an empty diff; its regression gate is the disposable-bridge apt
  probe, not code. Reconciled the ACTION BUDGET Done rule to cover this.
- Broken-base dispatch hold: hold when upstream/main does not compile; lift by
  compiling the base, not by tracking the escalated PR (repair landed via #2916,
  not the escalated #2842).
- After a base repair, feature-complete branches flip CONFLICTING — classify as
  integration-pending (branch-green, review-ready, conflict resolved post-Human-QA);
  do not merge main in Human-QA to "fix" it; expect a wave, do not ping each.
- Degenerate test assertion (`expect(``).toContain(...)`, empty template literal)
  reads red regardless of the code — check the test before blaming the feature.
- Cross-task delegation edges belong on the DEPENDENT pointing at the prerequisite,
  never the reverse; a prose-only delegation is not mechanically enforced.

Files: PROMPT.md (ACTION BUDGET zero-diff Done + dispatch-hold, version stamp),
docs/RUNBOOK.md (4 playbooks), docs/DECISIONS.md (2 decisions), docs/LEARNING_LOG.md.
Not carried: PR numbers as policy, ports, credentials, task-specific status.
