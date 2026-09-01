# Test-data manifest: performcoop

- Status: `AWAITING_SANITIZED_FIXTURE_AND_RECIPES`
- Workspace ID: `d35ace87-2aae-4e9c-9114-f9899af7f64b`
- Repository: `28bb119f-3284-4feb-85bc-61c78c160587` (`/data/home/Code/performcoop`)
- Expected artifact: `projects/performcoop/performcoop/artifacts/db.sql`
  (ignored, required mode 0600)
- Expected reviewed secret-free recipes:
  `projects/performcoop/performcoop/how-to-load.sh` and
  `projects/performcoop/performcoop/how-to-start.sh`
- Repository candidates found: Django seed fixtures under `django/bpa/fixtures/`
  and `django/core/fixtures/`. They are suitable only when their exact scenario
  assertions are sufficient; they are not a broad database substitute.
- Guarded broker candidate: registered same-workspace sources may be used via
  `docker kandev source` for an exact active task. The existing
  `/data/home/Code/performcoop/last_db.sql` was inspected only as metadata:
  regular file, 1,614,696,474 bytes, mode 0664, outside this catalog. It was not
  read, copied, moved, hashed, or accepted as a catalog fixture.
- Compatibility target: project Compose MariaDB service. Engine/version, dump
  format, sanitization, fixture ID/version, capture time, bytes, SHA-256,
  clean-import recipe and schema/domain/login/feature assertions remain to be
  supplied and independently verified.
- Resume trigger: the owner supplies the sanitized artifact and reviewed
  recipes, or a concrete task scenario is proven safely satisfiable by the
  guarded broker or repository fixtures; then record the immutable fixture and
  accepted restore receipt here.

Never add secrets or raw dump content to this manifest.
