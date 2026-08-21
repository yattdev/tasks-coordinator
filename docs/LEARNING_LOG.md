# Coordinator learning-cycle log

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
