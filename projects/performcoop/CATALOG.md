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
  catalogued. The first clean isolated restore receipt remains required.
- `pc-mobile`: `READY_LINKED_BACKEND`; it owns no standalone SQL fixture. A
  mobile integration task consumes a verified task-owned Performcoop backend
  created from the catalogued fixture, then points its networked development
  flavor at that isolated URL.
