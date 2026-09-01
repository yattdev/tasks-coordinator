# Test-data manifest: performcoop

- Status: `AWAITING_FIXTURE`
- Workspace ID: `d35ace87-2aae-4e9c-9114-f9899af7f64b`
- Repository: `28bb119f-3284-4feb-85bc-61c78c160587` (`/data/home/Code/performcoop`)
- Expected artifact: `projects/performcoop/performcoop/artifacts/db.sql`
  (ignored, required mode 0600)
- Expected reviewed secret-free recipes:
  `projects/performcoop/performcoop/how-to-load.sh` and
  `projects/performcoop/performcoop/how-to-start.sh`
- Provisioning decision: the owner will place all three declared files. Do not
  ask again, invent mock data, copy a live task/main database, or substitute a
  broker export, repository fixture, or seeder.
- Compatibility target: project Compose MariaDB service. Engine/version, dump
  format, sanitization, fixture ID/version, capture time, bytes, SHA-256,
  clean-import recipe and schema/domain/login/feature assertions remain to be
  supplied and independently verified.
- Resume trigger: owner placement of all three files at the exact paths above.
  Then verify the SQL file is regular and mode 0600; record bytes and SHA-256;
  validate MariaDB engine/version/format compatibility and sanitization; review
  both recipes for secrets and portability; run a clean isolated import plus
  schema/domain/login/feature assertions; and complete this manifest before
  serving a task.

Never add secrets or raw dump content to this manifest.
