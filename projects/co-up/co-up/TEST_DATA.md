# Test-data manifest: co-up

- Status: `READY`
- Workspace ID: `25f53734-5aea-490e-b7ba-d5da6fe821dd`
- Repositories: `abe336e4-0af1-4b6b-91e9-17124e2e9bda` (`/data/home/Code/co-up`) and `0c390752-fe23-4ba0-a55b-179ac6f1dff7` (`/data/home/Code/inno-prod/projects/co-up`)
- Fixture ID/version: `co-up-db-backup-20260408-80e51f42`
- Source class/time: owner-designated reusable test dump from
  `/data/home/Code/co-up/db_backup.sql`, mtime `2026-04-08 15:30:01Z`.
- Canonical private artifact:
  `/data/home/Code/coordinator/projects/co-up/co-up/artifacts/db_backup.sql`
  (ignored, mode 0600)
- Bytes / SHA-256: `66386677` /
  `80e51f42c81f1204f8f7a5633db3f5c3b433313625b1efdc1b5d4748c548278e`
- Engine/format: MariaDB logical SQL dump, server `10.11.15`, database
  `socodevi`, UTF-8/utf8mb4. Destination is an empty task-owned MariaDB 10.11
  `db` service.
- Load recipe: `how-to-load.sh`; stream only into the task's isolated DB
  container, then apply task-branch migrations if required.
- Sanitization: the owner identifies this as test data. Independent secret/PII
  audit is not recorded; keep same-workspace, private and short-lived after
  task delivery. Never commit, publish or attach it to a PR/MR.
- Required first restore assertions: clean destination; importer exit 0 and
  unsuppressed stderr; schema/domain counts; disposable login; feature path;
  exact-head application runtime; then record `TEST_DATA_RECEIPT`.
- Refresh rule: only a newer owner fixture or proven incompatibility; create a
  new fixture ID/hash rather than silently replacing provenance.
- Alternate live source: guarded broker container `coup-db`, image
  `mariadb:10.11`, in Compose project `co-up`. Do not redump it merely because
  it is available; the immutable owner-supplied fixture above is canonical.
- Repository overlay: `database/seeders/TestBaselineSeeder.php` may add one
  reviewed user/member/link graph after the base restore when the task scenario
  needs it. It requires an existing `Seed Coop A` row and never replaces the
  representative base fixture.

Never add secrets or raw dump content to this manifest.
