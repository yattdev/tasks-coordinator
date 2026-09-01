# Test-data manifest: performcoop

- Status: `READY`
- Workspace ID: `d35ace87-2aae-4e9c-9114-f9899af7f64b`
- Repository: `28bb119f-3284-4feb-85bc-61c78c160587` (`/data/home/Code/performcoop`)
- Fixture ID/version: `performcoop-last-db-20260508-1fcb706c`
- Source class/time: owner-designated reusable test dump from
  `/data/home/Code/performcoop/last_db.sql`, mtime `2026-05-08 13:59:36Z`.
- Canonical private artifact:
  `/data/home/Code/coordinator/projects/performcoop/performcoop/artifacts/last_db.sql`
  (ignored, mode 0600)
- Bytes / SHA-256: `1614696474` /
  `1fcb706ca86f742f0144418f0ee8ff9d17f1ef425f20ab5ebdf796a45a52a6c6`
- Engine/format: MariaDB logical SQL dump, server `10.11.13`, database
  `performcoop`, UTF-8/utf8mb4. Destination is the task-owned Compose `db`
  service; use a compatible MariaDB client/server.
- Load/start recipes: `how-to-load.sh` and `how-to-start.sh`. The loader streams
  the dump to the task-owned DB container, equivalent to selecting the target
  database and running `source last_db.sql`; it never touches the shared/main
  instance.
- Sanitization: the owner identifies this as test data. An independent
  secret/PII audit has not been recorded, so keep it same-workspace, mode 0600,
  short-lived after delivery, and never publish or commit it.
- Required first restore assertions: clean destination, importer exit 0 with no
  suppressed stderr, schema present, representative domain counts, test login,
  task feature path, and exact-head web runtime. Record the resulting
  `TEST_DATA_RECEIPT`; that receipt, not the copy alone, proves acceptance.
- Refresh rule: replace only on an owner-supplied newer fixture or a proven
  schema/scenario incompatibility. Recompute size/hash and retain a new fixture
  ID; do not overwrite provenance silently.

Never add secrets or raw dump content to this manifest.
