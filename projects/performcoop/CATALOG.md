# Performcoop workspace project catalog

Workspace: `d35ace87-2aae-4e9c-9114-f9899af7f64b`

Project slots: `performcoop` (repository
`28bb119f-3284-4feb-85bc-61c78c160587`, `/data/home/Code/performcoop`) and
`pc-mobile` (repository `3cb0b634-8e42-41b5-bbfe-aca39b66246e`,
`/data/home/Code/pc-mobile`).

Reconciled: `2026-09-01` from live workspace repository inventory. These are
the only two registered application project slots; no duplicate alias was
created.

- `performcoop`: `READY`; private fixture
  `performcoop-last-db-20260508-1fcb706c` and reviewed load/start recipes are
  catalogued. The first clean isolated restore passed for schema/auth/runtime;
  the manifest records its sparse domain-data limitation.
- `pc-mobile`: `AWAITING_FIXTURE`; it owns no standalone SQL fixture. The linked
  backend was reachable from the emulator, but the current Performcoop fixture
  has no project/training-session/participant scenario, so the target feature
  path cannot be exercised. Resume only on owner placement of a replacement or
  new fixture version containing that scenario; never create a mobile DB/mock
  substitute.
