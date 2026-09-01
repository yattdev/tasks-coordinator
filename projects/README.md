# Workspace project test-data catalogs

Each permanent Coordinator owns only its workspace namespace. The durable
private artifact root is the shared Coordinator checkout at
`/data/home/Code/coordinator/projects/`; this survives replacement of a
Coordinator task worktree. Coordinator worktrees consume the tracked manifest
and recipe from their checkout, but resolve raw artifacts from that canonical
private root before copying an immutable task-scoped delivery.

```text
projects/<workspace-slug>/<project-key>/
├── TEST_DATA.md          # versioned manifest; never secrets
├── how-to-load.sh        # optional reviewed, secret-free loader
├── how-to-start.sh       # optional reviewed, secret-free runtime launcher
└── artifacts/            # ignored raw dumps, mode 0600
```

Use `TEST_DATA.md` as the authoritative fixture registry. Raw artifacts are
never committed. A task receives an immutable copy plus hash and imports it into
a clean task-owned destination; the task returns the receipt defined in
`docs/RUNBOOK.md`. Project aliases that identify the same application belong in
one manifest.

Current namespaces correspond to the live permanent Coordinators:

- `kandev` — workspace `2e62401b-5ffe-4050-bc1b-d49ea5d5dbcd`
- `performcoop` — workspace `d35ace87-2aae-4e9c-9114-f9899af7f64b`
- `co-up` — workspace `25f53734-5aea-490e-b7ba-d5da6fe821dd`
- `jami` — workspace `d918c5e2-903e-47ce-b372-8e62f9dbad9c`

Start from [`_template/TEST_DATA.md`](_template/TEST_DATA.md). The Coordinator
updates availability and hashes after the owner supplies a fixture/recipe or a
brokered source is independently accepted.
