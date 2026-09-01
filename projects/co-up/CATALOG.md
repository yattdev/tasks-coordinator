# Co-Up workspace project catalog

Workspace: `25f53734-5aea-490e-b7ba-d5da6fe821dd`

Project slots: `co-up` (repository aliases
`abe336e4-0af1-4b6b-91e9-17124e2e9bda` and
`0c390752-fe23-4ba0-a55b-179ac6f1dff7`), `co-up-rbac02-env`, and
`coup-mobile`. The two Co-Up repository registrations share one application
fixture manifest; record both source paths there rather than duplicating data.

Live reconciliation at 2026-09-01 04:24 UTC found the registered development
MariaDB source `coup-db` (`mariadb:10.11`) available through the guarded source
broker. The repository also contains several unvalidated SQL files and a
`TestBaselineSeeder`/rollback pair. None is yet a reusable full fixture: the SQL
files have no sanitization or provenance receipt, and the seeder is only a
small overlay that requires a pre-existing cooperative named `Seed Coop A`.

Owner fixture/recipe status: one sanitized immutable Co-Up fixture plus a
reviewed load recipe is still required. Mobile has no standalone database; its
integration scenarios consume the Co-Up backend fixture. Raw or unvalidated
repository dumps are not catalog inputs.
