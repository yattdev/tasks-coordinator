# Human-QA monitoring state

Rolling snapshot of the Human-QA column so a monitoring cycle does not re-ping tasks that are
already acting on the same issue. Update the **Last cycle** block each run; keep one cycle of
history. See [QA_INSTANCES.md](QA_INSTANCES.md) for the instance contract and
[RUNBOOK.md](RUNBOOK.md) for the playbooks.

## Instance registry (LAN test URLs)

All published `0.0.0.0:<port>->38429`, `--restart unless-stopped`, verified `200` +
`<title>Kandev</title>` from `192.168.50.131`. Redmine dep on `:13080`.

| Task | Title | LAN URL | Kind |
|---|---|---|---|
| `7ca86e53` | Redmine integration | http://192.168.50.131:38447 (+ redmine :13080) | UI+runtime |
| `9e67c426` | Coordinator plugin architecture | http://192.168.50.131:38439 | UI |
| `52892e8e` | Build coordinator plugin | http://192.168.50.131:38445 | runtime |
| `153cdbbe` | Task panel close/open | http://192.168.50.131:38443 | UI |
| `51c2875b` | Notes utility-agent dropdown | http://192.168.50.131:38448 | UI |
| `9349b6e5` | MCP relation inspection | http://192.168.50.131:38446 | backend (instance optional) |
| `9ebf7cdc` | Session revival fix | http://192.168.50.131:38441 | backend (instance optional) |
| `f4136a59` | Expand task fields | http://192.168.50.131:38444 | backend (instance optional) |

`kandev-qa-9683` (:—, exited) is an unmapped orphan — leave stopped. `kandev-test-lan`
(rich-hover, `d30ca136`) moved to ToDeploy — leave stopped.

## Last cycle — 2026-08-24 (triggered by peer task 76cc1eea)

18 tasks in Human-QA inspected. GitHub core rate limit healthy (5000/5000). All 8 UI/runtime
instances LAN-reachable + restart-policied. Nine tasks pinged (all were idle
`WAITING_FOR_INPUT`, none mid-fix):

| Task | PR | Issue pinged | Expecting back |
|---|---|---|---|
| `16803c08` | #2940 | FAIL Backend Tests (MERGEABLE) — **linchpin** fix | green CI + fix SHA |
| `f4136a59` | #2872 | FAIL Static Checks + Backend Tests (MERGEABLE) | green CI + fix SHA |
| `6a5a2f73` | #2937 | PENDING CI + userns-dropped-on-model-switch bug + aria-label | green CI + regression test + thread replies |
| `c642d57a` | #2909 | CONFLICT + 8 unresolved (Major atomicity/attestation/identity) | rebase + per-comment disposition |
| `9ebf7cdc` | #2766 | CONFLICT + FAIL backend | rebase + green CI |
| `b74833e7` | #2845 | CONFLICT + FAIL E2E shards (follow-up; blocks 212a68ce) | rebase + E2E green/evidenced |
| `5d27f4a2` | #2870 | CONFLICT (green CI) — Notes host half | rebase + mergeable |
| `153cdbbe` | #2868 | DRAFT + CONFLICT | rebase + un-draft |
| `9e67c426` | #12 | FAIL deploy-only checks (fork PR) | determination + PR comment |

Rebase authorization: operator standing directive — "notify others that still have CI-issue to
rebase onto upstream:main, fix any conflict and address/reply comments." Rebase-to-reviewable
only; no branch→main merge, no acceptance trigger (Human-QA boundary).

**Ready for MR/PR review without a test instance (green + clean + no comments):** `725d47ae`
(#2792, hermetic github tests — no instance needed), `55d2d589` (#2800, E2E runner), `9349b6e5`
(#2841, MCP relation), `dacee5a8` (#2910, dev DB path), `52892e8e` (plugin-coordinator #1),
`00ceb41b` (plugin-redmine #1), `dfb3f5c7` (plugin-tags #9; #8 already merged).

**Do NOT re-ping next cycle** unless a task is stalled past a reasonable window or newly
regresses — the nine above have live, precise instructions. Recheck their CI/PR state and only
follow up on stalls or false readiness claims.
