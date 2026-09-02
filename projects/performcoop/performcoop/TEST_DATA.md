# Test-data manifest: performcoop

- Status: `READY`
- Workspace ID: `d35ace87-2aae-4e9c-9114-f9899af7f64b`
- Repository: `28bb119f-3284-4feb-85bc-61c78c160587` (`/data/home/Code/performcoop`)
- Fixture ID/version: `performcoop-db-backups-20260302-d1a9b7a7`
- Source class/time: owner-designated reusable test dump from
  `/data/home/Code/performcoop/drafts/db_backups.sql`, mtime
  `2026-03-02 15:22:18.824506948Z`.
- Canonical private artifact:
  `/data/home/Code/coordinator/projects/performcoop/performcoop/artifacts/db_backups.sql`
  (ignored, regular non-symlink, one link, mode 0600).
- Bytes / SHA-256: `1545258208` /
  `d1a9b7a7b0b9cceaf0f352e62f076366244110379a1a1640f6078ff730bb86fe`
- Format: logical MariaDB/MySQL SQL dump with 133 `CREATE TABLE` and 1,588
  `INSERT` markers. Accepted destination was MariaDB 12.3.3; use the task-owned
  Compose `db` service and validate compatibility again for a different head or
  engine.
- Load/start recipes: `how-to-load.sh` and `how-to-start.sh`, SHA-256
  `d8a0fd92d86d948fe116370302f3b543c1e2214d1a13e67972c3362e8d8f5cf8` and
  `d8305c0a4a038fa8fb5598ec6d6e201074e5804b4a63cd80528ae0d3fff50443`.
  Guarded redirected stdin was repaired by deployment-local commit
  `ab8174cea69f0e503439d06340abed5d19716e5a` and exact binary/empty-input
  task acceptance passed. Continue to verify importer exit, schema and counts;
  an exit code alone is never an import receipt.
- Sanitization: the owner identifies this as test data. An independent
  secret/PII audit has not been recorded, so keep it same-workspace, mode 0600,
  immutable after delivery, short-lived in task inboxes, and never publish or
  commit it.
- First clean restore receipt (2026-09-02): exact task
  `1f434680-0901-4a0c-abaf-1c48d050f7d4`, project `kd_1f4346800901`.
  The real import populated 133 InnoDB tables and approximately 17.4 million
  rows; all tables passed `mariadb-check`; 12 supported migrations brought the
  schema to 291 applied/zero pending; Django checks passed. Final representative
  counts: 1,000 organizations, 112 projects, 1,654 users, 190,233 persons,
  447,579 questionnaires, 5,185 trainings, 26,005 sessions, and 501,981
  participation rows.
- Exact mobile-signature scenario: the restored dump had no signature-enabled
  project or signed attendance row. The accepted task receipt therefore adds a
  clearly synthetic, idempotent destination-only overlay without changing any
  restored business row: project 123, training 5823, session 28322, signed
  participant 201874, unsigned participant 201875, plus a seven-day task-only
  test account. Browser login, mobile auth/permissions, project/training/signature
  APIs and protected signature media passed internally.
- Current runtime limitation: the preserved acceptance runtime is internally
  healthy, but the guarded broker suppresses its declared host/LAN ports.
  Do not hand out its URL until task-side `compose port` plus localhost/LAN HTTP
  probes pass after the Support repair. The fixture itself is accepted and may
  be delivered to another isolated same-workspace task under the normal catalog
  procedure.
- Refresh rule: replace only on an owner-supplied newer fixture or a proven
  schema/scenario incompatibility. Recompute size/hash and retain a new fixture
  ID; do not overwrite provenance silently.

Never add secrets or raw dump content to this manifest.
