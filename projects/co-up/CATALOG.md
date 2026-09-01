# Co-Up workspace project catalog

Workspace: `25f53734-5aea-490e-b7ba-d5da6fe821dd`

Project slots: `co-up` (repository aliases
`abe336e4-0af1-4b6b-91e9-17124e2e9bda` and
`0c390752-fe23-4ba0-a55b-179ac6f1dff7`), `co-up-rbac02-env`, and
`coup-mobile`. The two Co-Up repository registrations share one application
fixture manifest; record both source paths there rather than duplicating data.

Live reconciliation at 2026-09-01 04:24 UTC also found the registered
development MariaDB source `coup-db` (`mariadb:10.11`) through the guarded
source broker. It is an alternate refresh source, not a reason to redump while
the owner-supplied immutable fixture remains compatible. The repository's
`TestBaselineSeeder`/rollback pair is a scenario overlay that requires a
pre-existing cooperative named `Seed Coop A`.

Owner fixture/recipe status: `co-up-db-backup-20260408-80e51f42` is now the
private reusable backend fixture with a reviewed secret-free loader. Its first
clean isolated restore receipt remains required before a task may claim the
runtime ready. Mobile has no standalone database; integration scenarios consume
this Co-Up backend fixture through a task-owned backend URL.
