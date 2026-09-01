# Test-data manifest: co-up

- Status: `AWAITING_OWNER_FIXTURE`
- Workspace ID: `25f53734-5aea-490e-b7ba-d5da6fe821dd`
- Repositories: `abe336e4-0af1-4b6b-91e9-17124e2e9bda` (`/data/home/Code/co-up`) and `0c390752-fe23-4ba0-a55b-179ac6f1dff7` (`/data/home/Code/inno-prod/projects/co-up`)
- Artifact: `artifacts/db.sql` (ignored, mode 0600)
- Load/start recipes: awaiting owner-provided reviewed scripts
- Fixture ID, source, timestamp, bytes, SHA-256, engine/format, sanitization, assertions, refresh rule and limitations: awaiting validation
- Verified candidate source (2026-09-01 04:24 UTC): guarded broker container
  `coup-db`, image `mariadb:10.11`, running in Compose project `co-up`.
  Export is not authorized as a reusable fixture until a sanitization and load
  recipe is reviewed; broker availability alone does not prove data safety.
- Repository fallback assessment: existing `*.sql` files are unvalidated and
  must not be copied into the catalog. `database/seeders/TestBaselineSeeder.php`
  is a safe, test-only idempotent overlay for one user/member/link graph, but it
  requires an existing `Seed Coop A` row and therefore cannot bootstrap a full
  representative database.

Never add secrets or raw dump content to this manifest.
