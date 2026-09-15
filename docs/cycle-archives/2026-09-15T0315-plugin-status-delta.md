# Redmine and Coordinator plugin status — 2026-09-15T03:15Z

Live identity: Coordinator task `a68df3ae-aaf5-4591-a46d-9d73db62e46d`, workspace `2e62401b-5ffe-4050-bc1b-d49ea5d5dbcd`, workflow `90f322ed-2159-424d-96e7-c2ad05668b8e`.

## Redmine plugin

- Direct remote ref read: `yattdev/kandev-plugin-redmine` main and annotated `v0.3.2` dereference to `b843ce5345e8a11ade7f0d4d33386c746465a049`; manifest version `0.3.2`, minimum Kandev `0.94.0`.
- Release chain includes merged PR #8 exact head `2192918e13fdeb8a0641eb240cc27f8286cb4da5` for malformed Redmine 6 `possible_values` handling. Derived custom-field fallback and release tasks are Done.
- Disposable first-version E2E task records `QA_RESULT=PASSED` for the published v0.3.2 artifact and Host v0.94.0 identity. Runtime was disposed. No Redmine delivery task has an active session or open blocker.
- Status: released and complete.

## Coordinator plugin

- Direct remote ref read: `yattdev/kandev-plugin-coordinator` main is `6fb1fdd63c1728258c40a67df037116c5ca9bbb8`, manifest version `0.1.0`; no release tags are published. Main contains the vendored v1.1 policy contract and SQLite durable-state foundation.
- Host AgentConversation port task `a091649a...` is Human-QA. PR #3672 is open/draft at `af509f8feae82074b22c902bd4d8e1021dd60537`; stored provider snapshot at 02:56Z shows checks success and zero unresolved threads. It awaits explicit Human-QA acceptance and later upstream merge.
- Capability approval task `23a05db4...` / PR #3238 is physically Blocked despite current head `d742006c2b215705a2897487cc7275c41a2e9624` being green, clean, non-draft, and thread-clean. Required fresh Review and distinct QA could not be started because the Kandev MCP task-control mutation path times out without committing.
- Host queue primitive `ca015838...` / PR #3377 remains open/draft/red at `c990b51cb8dc758f35a702ee6ee017dd1c593c26`. This blocks plugin fenced-runtime task `428d343e...`, which transitively blocks deterministic scale harness `0259d242...`.
- Isolated E2E task `afdb2ef3...` remains Blocked until PR #3672 merges and a compatible package can be installed in a fresh isolated runtime.
- Program owner `1e46d457...` remains Work with active GLM session `ba236402...`, contrary to the Human's Codex-only workflow change. The attempted supported stop was a task-control no-op; no duplicate Codex writer was started.
- Status: foundation exists, but the integrated Coordinator plugin is not release-ready or deployed. Current critical path is task-control recovery → fresh Review/QA for #3238 and Codex owner replacement → Human-QA/merge of #3672 → queue primitive #3377 → fenced runtime → scale harness → isolated E2E/release.

## Evidence limits and continuity

GitHub GraphQL is rate-limited for the configured account, so PR facts use the Kandev provider snapshots timestamped 02:53–02:56Z. Repository main/tag identities were refreshed directly with `git ls-remote`/`git fetch`. The live Coordinator plan remains unreadable/unwritable through MCP; this delta is committed to shared main as the executable handoff. No task, PR, release, or deployment mutation was performed.
