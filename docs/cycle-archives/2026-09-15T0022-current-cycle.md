# Coordinator state & cycle logs

Current-first compact replacement candidate. No live plan, task, repository, provider, or host mutation was performed.

```json
{
  "schema": "coordinator-current-state-v3-candidate",
  "candidate_marker": "Full-cycle compact replacement candidate — 2026-09-15T00:11Z",
  "snapshot_at": "2026-09-15T00:21:56.572644741Z",
  "current_first": true,
  "identity": {
    "task_id": "a68df3ae-aaf5-4591-a46d-9d73db62e46d",
    "workspace_id": "2e62401b-5ffe-4050-bc1b-d49ea5d5dbcd",
    "workflow_id": "90f322ed-2159-424d-96e7-c2ad05668b8e",
    "primary_session": "da0761f2-cd4e-44d1-bccc-6f9c1119f534"
  },
  "policy": {
    "effective_version": "2026-09-14b",
    "workflow_profiles": "Human-maintained workflow/workstep configuration is authoritative; former fixed per-lane model gates are suspended.",
    "permanent_coordinator": "Never complete/move/delete the Coordinator task.",
    "to_deploy": "Human-owned; metadata-only Coordinator tracking.",
    "communication": "Routine board-task/provider communication authorized; avoid duplicate unchanged pings."
  },
  "census": {
    "live": 60,
    "blocked": 24,
    "nonblocked": 36,
    "done": 15,
    "lanes": {
      "Backlogs": 1,
      "Blocked": 24,
      "CI Fixup": 9,
      "Done": 15,
      "PR": 1,
      "Spec": 1,
      "ToDeploy": 2,
      "Work": 7
    }
  },
  "set_integrity": {
    "convention": "SHA-256 of sorted full UUIDs, each followed by LF",
    "open_ids_sha256": "30d6a14cf0f04ca113a7d236a79289863dc0d89b6504b5f0921e96165f929994",
    "blocked_ids_sha256": "93fe53b1b743ad6efd8751145db69b1d2ec836f835b94b4dc3f981d5bf0a4079",
    "open_count": 60,
    "blocked_count": 24,
    "source_counts": "36 non-Blocked current records + 24 Blocked current records"
  },
  "ledger": [
    {
      "task_id": "01432319-aa8b-4c7d-9841-addcc6ab8e76",
      "title": "Prepare maintained codex-acp fork fallback",
      "column": "ToDeploy",
      "state": "REVIEW",
      "owner": "Human",
      "health": "waiting",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "TEST_RUNTIME: `NONE`  STATE: `READY_FOR_HUMAN_TEST`  PR #1 remains open/draft and mergeable. HEAD is `3352b02c95627707ee1a71dc705cc19e80451f6d`; worktree is clean and all CI checks pass.  Review commands:  ```sh npm ci npm run typecheck npm test npm run build npm run bundle:all npm run package:all node scripts/verify-fork-policy.mjs ```  No server, databa...",
      "next_action": "Human performs deployment/acceptance; Coordinator tracks age and verifies deployment receipt.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 1,
          "COMPLETED": 1,
          "CANCELLED": 4
        },
        "active_ids": [],
        "latest": {
          "id": "377d039d-2e87-447c-aa47-60640790e294",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-06 06:11:58.64187625+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 1,
          "state": "merged",
          "draft": 0,
          "head": "3352b02c95627707ee1a71dc705cc19e80451f6d",
          "checks": "success",
          "passing": 8,
          "total": 8,
          "threads": 0
        }
      ],
      "blocker_or_gate": "ToDeploy; linked PR #1 is merged and checks green."
    },
    {
      "task_id": "01d6764d-b66d-46a0-a664-2caf4c3f4d98",
      "title": "Make terminal workflow routing atomic",
      "column": "Blocked",
      "state": "IN_PROGRESS",
      "owner": "Capacity task 8a182e40-d99c-42e9-b9be-1f8f78cf8388; Coordinator owns atomic R5 routing",
      "health": "blocked",
      "last_checked": "2026-09-15T00:11:12Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "After one verified free standalone allocation, fresh-check the unchanged green head, move Blocked→Review, start exactly one configured Review owner, and verify RUNNING; forbid the contaminated checkout.",
      "blocked_record": {
        "previous_workflow_step": "CI Fixup",
        "exact_blocker_or_dependency": "Provider gate cleared at unchanged PR #3166 head e30bd1f2e5008be93e11ede6b2d3827a74e68095; sole remaining blocker is standalone port capacity, which prevents atomic Blocked→Review handoff with a verified fresh owner.",
        "blocker_owner": "Capacity task 8a182e40-d99c-42e9-b9be-1f8f78cf8388; Coordinator owns atomic R5 routing",
        "preservation_receipt": "Provider head e30bd1f2e5008be93e11ede6b2d3827a74e68095. Contaminated checkout /data/tasks/make-terminal-workfl_8z3b2nzr/kandev-source, branch fix/atomic-terminal-routing, local fe21f495adf3c72fd3fc01de2fffc5541858e575, interrupted merge and roughly 2,200 staged paths preserved untouched; no retained runtime/data.",
        "owner_session_health": "active=0; pending_moves=0; latest owner f02f5828-691d-4cb5-bd8a-975920709659 WAITING_FOR_INPUT, CI Fixup profile 7c6be62e-6980-498a-a4fb-896947ff5402, gpt-5.6-luna",
        "next_action": "After one verified free standalone allocation, fresh-check the unchanged green head, move Blocked→Review, start exactly one configured Review owner, and verify RUNNING; forbid the contaminated checkout.",
        "deterministic_resume_trigger": "Verified free standalone allocation in 41001-41100; provider success already satisfied.",
        "fallback": "If exact-head status regresses, route by current failure ownership; preserve provider head and contaminated local checkout untouched.",
        "cleared": false,
        "last_checked": "2026-09-15T00:11:12Z",
        "provider_gate_cleared": true
      },
      "relations": "none",
      "pending_moves": []
    },
    {
      "task_id": "02159e6a-726a-43b2-8d9a-f74c5c01fe11",
      "title": "Recover atomic terminal routing in an isolated workspace",
      "column": "CI Fixup",
      "state": "FAILED",
      "owner": "Coordinator",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Exact-head CI Fixup is blocked pending current-head CI completion.  - Head verified: `e30bd1f2` - Current E2E run has no failed leaf jobs; 4 shards remain in progress. - Documentation failure is stale (`cd0be19f`); replacement run is queued on `e30bd1f2`. - No code changes, tests, commits, pushes, reruns, or review writes made. - GitHub API rate limit int...",
      "next_action": "After 8a repair, start one Luna CI owner and refresh only the replacement exact-head run; no duplicate rerun.",
      "session_health": {
        "counts": {
          "FAILED": 2,
          "WAITING_FOR_INPUT": 3,
          "COMPLETED": 13,
          "CANCELLED": 2
        },
        "active_ids": [],
        "latest": {
          "id": "4081e4fd-1269-4c27-a270-f2b18c05dc23",
          "state": "FAILED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 23:18:41.075141785+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [],
      "pr_gate": [],
      "blocker_or_gate": "Standalone capacity [41001,41100] is exhausted; configured session failed before inference. Exact e30bd1f2 CI receipt is preserved."
    },
    {
      "task_id": "0259d242-0a94-40ef-843e-385292796b64",
      "title": "Plugin deterministic scale harness",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "428d343e-c768-4bce-a5e7-efd3b10f363f, transitively ca015838-e5cf-4294-b3bb-9c50576a5fe6 and upstream deployment owner",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "After exact runtime delivery, move Blocked to Work and start one configured Work owner with the approved harness plan.",
      "blocked_record": {
        "previous_workflow_step": "Spec",
        "exact_blocker_or_dependency": "Required reviewed/deployed contract-v1.1.0 runtime from 428d343e-c768-4bce-a5e7-efd3b10f363f is absent; that task is itself Blocked on ca015838-e5cf-4294-b3bb-9c50576a5fe6 publication/deployment.",
        "blocker_owner": "428d343e-c768-4bce-a5e7-efd3b10f363f, transitively ca015838-e5cf-4294-b3bb-9c50576a5fe6 and upstream deployment owner",
        "preservation_receipt": "Approved harness plan; clean skeleton worktree /data/tasks/plugin-deterministic_mjefehl3/yattdev-kandev-plugin-coordinator, branch feature/plugin-deterministic-cyz, head 6fb1fdd63c1728258c40a67df037116c5ca9bbb8; no runtime/artifacts.",
        "owner_session_health": "active=0; pending_moves=0; 9699b6a1-f69c-432e-b626-b3eccaa56bf0 WAITING_FOR_INPUT, Worker/gpt-5.6-terra",
        "next_action": "After exact runtime delivery, move Blocked to Work and start one configured Work owner with the approved harness plan.",
        "deterministic_resume_trigger": "deployed callable Host contract v1.1.0 receipt from 428d343e",
        "fallback": "Keep plan and clean worktree dormant; do not substitute or duplicate Host runtime behavior.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": "blocked_by 428d343e; other blockers a08ef33c and be077c0f are Done",
      "pending_moves": []
    },
    {
      "task_id": "09325a7b-afb5-4f54-b2a7-ceae217a7bee",
      "title": "Fix repository provider eligibility refresh regression",
      "column": "Done",
      "state": "REVIEW",
      "owner": "Coordinator terminal tracking",
      "health": "terminal",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Current state verified:  - Worktree clean at `cb7b887e…`; no source changes made. - Fork remote is one test-only commit ahead at `b17dc78c…`; prior QA receipt no longer covers that tip. - Exact `gpt-5.4` remains unavailable. Available PR-owner profiles are `gpt-5.6-terra` and `sonnet`, and substitution is prohibited. - GitHub PR inspection was blocked by ...",
      "next_action": "Archive on normal Done retention; retain outgoing consumer edge only while cfcc still legitimately references it.",
      "session_health": {
        "counts": {
          "COMPLETED": 10,
          "WAITING_FOR_INPUT": 1,
          "FAILED": 1
        },
        "active_ids": [],
        "latest": {
          "id": "98950b18-2311-4e2b-9eb6-db874bf83e4c",
          "state": "COMPLETED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 02:56:10.918793054+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3498,
          "state": "merged",
          "draft": 0,
          "head": "b17dc78c56ded02e66d1f49a4eb37df6411e2ed0",
          "checks": "success",
          "passing": 44,
          "total": 44,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Merged #3498; b17dc78 content contained by main; no unique work.",
      "terminal_integrity": {
        "status": "terminal",
        "persisted_receipt": {
          "id": "09325a7b-afb5-4f54-b2a7-ceae217a7bee",
          "status": "terminal",
          "receipt": "Merged PR #3498; remote b17dc78c content contained by main 39e3ce2d52; no unique work."
        }
      }
    },
    {
      "task_id": "153cdbbe-beac-47b8-bc06-8dafdcc8ed80",
      "title": "Fix/Improve task panel close/open",
      "column": "Blocked",
      "state": "WAITING_FOR_INPUT",
      "owner": "Capacity task 8a182e40-d99c-42e9-b9be-1f8f78cf8388; Coordinator owns atomic R5 routing",
      "health": "blocked",
      "last_checked": "2026-09-15T00:11:12Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "After one verified free standalone allocation, fresh-check the unchanged green head, move Blocked→QA, start exactly one distinct configured QA owner, and verify RUNNING while retaining current-head Review evidence.",
      "blocked_record": {
        "previous_workflow_step": "CI Fixup",
        "exact_blocker_or_dependency": "Provider gate cleared at unchanged PR #2868 head b385a56071bfd6b35b8ecc911ba6592f2966cc3c; sole remaining blocker is standalone port capacity, which prevents atomic Blocked→QA handoff with a distinct verified fresh owner.",
        "blocker_owner": "Capacity task 8a182e40-d99c-42e9-b9be-1f8f78cf8388; Coordinator owns atomic R5 routing",
        "preservation_receipt": "Clean tracked worktree /data/tasks/fix-improve-task-pan_8xxomha3/kandev-source, branch integration-pr-2868-main, exact head b385a56071bfd6b35b8ecc911ba6592f2966cc3c; untracked qa-session-tab-close.png SHA-256 c46947d01febb9d6164e63a3d25578bb1400331590501f4620bda9279f149826; current-head Review PASS and corrected PR body receipt preserved.",
        "owner_session_health": "active=0; pending_moves=0; latest CI launch 721893bc-d067-4a7a-93de-12a110803c79 FAILED before inference on port exhaustion, CI Fixup/gpt-5.6-luna; current-head Review 54ea0234-f185-45f4-a392-3885242851f2 COMPLETED",
        "next_action": "After one verified free standalone allocation, fresh-check the unchanged green head, move Blocked→QA, start exactly one distinct configured QA owner, and verify RUNNING while retaining current-head Review evidence.",
        "deterministic_resume_trigger": "Verified free standalone allocation in 41001-41100; provider success already satisfied.",
        "fallback": "If exact-head status regresses, route by current failure ownership; preserve head and screenshot without duplicate contact.",
        "cleared": false,
        "last_checked": "2026-09-15T00:11:12Z",
        "provider_gate_cleared": true
      },
      "relations": "none",
      "pending_moves": []
    },
    {
      "task_id": "1d3d7383-8dba-41f8-a794-7e3d51809143",
      "title": "Repair Docker address-pool exhaustion",
      "column": "Work",
      "state": "FAILED",
      "owner": "Coordinator",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Resumed at `cfd6bdf65` with task-owned, uncommitted changes.  Completed: - Docker network SDK seam: filtered `ListNetworks` and per-ID `RemoveNetwork`; no global prune API. - Existing disabled-by-default network-maintenance settings preserved. - Updated the task plan with current progress.  Verified:  ```text cd apps/backend && go test ./internal/agent/do...",
      "next_action": "After 8a capacity repair, fresh-preflight Work and start one c06/Terra owner; preserve source/host boundaries and unknown networks.",
      "session_health": {
        "counts": {
          "FAILED": 1,
          "WAITING_FOR_INPUT": 3,
          "COMPLETED": 1
        },
        "active_ids": [],
        "latest": {
          "id": "8fc25db5-28c9-48a6-acd4-90d23d991648",
          "state": "FAILED",
          "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 23:40:51.162452397+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [],
      "pr_gate": [],
      "blocker_or_gate": "Standalone capacity [41001,41100] is exhausted; configured session failed before inference. Uncommitted Docker SDK/settings work is preserved."
    },
    {
      "task_id": "1e46d457-6869-4750-bf97-4640a8df3b68",
      "title": "Coordinate plugin-first board supervision delivery",
      "column": "Work",
      "state": "IN_PROGRESS",
      "owner": "task agent; active session ba236402-99ca-48ed-a812-ea0de6fdea3f RUNNING",
      "health": "healthy",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "The child completed the test reconciliation and pushed `0d4b730e`. Verifying the push receipt, independently confirming the regression is gone, and watching the CI wave at the new head:",
      "next_action": "Consume current owner receipt; route exact pushed head through current CI and remaining gates.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 4,
          "RUNNING": 1,
          "FAILED": 1
        },
        "active_ids": [
          "ba236402-99ca-48ed-a812-ea0de6fdea3f RUNNING"
        ],
        "latest": {
          "id": "c24d3d92-d745-4465-8252-f8a7a482e433",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 21:41:00.075683531+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [],
      "blocker_or_gate": "One RUNNING owner exists and child pushed 0d4b730e; CI verification is active."
    },
    {
      "task_id": "1f8d4dc8-83ac-44d6-9fbd-b34bd46e044e",
      "title": "Recover missing linked-worktree admin directories",
      "column": "Done",
      "state": "REVIEW",
      "owner": "Coordinator terminal tracking",
      "health": "anomalous",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Terminal integrity completed and recorded.  - PR #3137 merged as `21a639b7`. - Checkout remains preserved and clean at `32d10e8d6`. - No temporary artifacts or unique task resources remain. - Shared Kandev runtimes were left untouched due to ownership boundaries. - Workflow step completion signaled successfully.",
      "next_action": "Remove obsolete edge from safe task-owned context and verify blockers=[]; then archive normally.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 2,
          "COMPLETED": 21
        },
        "active_ids": [],
        "latest": {
          "id": "9049a4ed-c51b-4ab8-a023-cc2bfd709d9d",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 02:56:12.373146226+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3137,
          "state": "merged",
          "draft": 0,
          "head": "eb83bbe3d36e50abd04ecfaddbc21138c067e49b",
          "checks": "success",
          "passing": 51,
          "total": 51,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Merged #3137 and clean receipt, but Done still has a dependency edge to non-live b2a98e9e.",
      "terminal_integrity": {
        "status": "anomalous",
        "persisted_receipt": {
          "id": "1f8d4dc8-83ac-44d6-9fbd-b34bd46e044e",
          "status": "terminal",
          "receipt": "Merged PR #3137; delivery, preservation, and cleanup passed."
        }
      }
    },
    {
      "task_id": "212a68ce-7122-4cdb-ba68-764a5ebdb8c6",
      "title": "Finish Provider Usage plugin coverage",
      "column": "Blocked",
      "state": "FAILED",
      "owner": "Coordinator/platform native-sandbox and managed-worktree materialization owner",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "Provision a newly registered writable checkout, prove bounded Git index write/rollback, then move to Work and start one owner to restore the six files and complete tests/package/E2E.",
      "blocked_record": {
        "previous_workflow_step": "Todo",
        "exact_blocker_or_dependency": "Task checkout lacks valid writable Git administration/index. Formal blocker b74833e7-a05f-4cdf-81cf-db5b4c02f368 is Done after its rejected umbrella disposition, but did not deliver a writable checkout, so the real trigger remains unmet.",
        "blocker_owner": "Coordinator/platform native-sandbox and managed-worktree materialization owner",
        "preservation_receipt": "Recoverable six-file baseline commit a5c386b at /data/tasks/expose-provider-usag_kjfkfyxi/kdlbs-kandev-plugin-provider-usage-main; broken checkout /data/tasks/finish-provider-usag_8isp64fr/kdlbs-kandev-plugin-provider-usage has missing Git admin; no runtime/data/services.",
        "owner_session_health": "active=0; pending_moves=0; primary 501387d6-5c2c-4036-b768-2c568813d0f8 FAILED, Worker/gpt-5.6-terra",
        "next_action": "Provision a newly registered writable checkout, prove bounded Git index write/rollback, then move to Work and start one owner to restore the six files and complete tests/package/E2E.",
        "deterministic_resume_trigger": "successful task-owned Git write/rollback plus available standalone session capacity",
        "fallback": "Keep both paths immutable and do not retry the broken checkout or bypass guards.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": "blocked_by b74833e7 (Done but insufficient)",
      "pending_moves": []
    },
    {
      "task_id": "23a05db4-c7bf-4732-a390-08cb8f0a3a8d",
      "title": "H6: Add plugin capability approval and audit",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "Capacity task 8a182e40-d99c-42e9-b9be-1f8f78cf8388; Coordinator owns atomic post-clearance routing",
      "health": "blocked",
      "last_checked": "2026-09-15T00:18:30Z",
      "last_action": "Authoritative readback verified physical Blocked step 89985050-d740-4421-bbbe-4aa018d8c7ab, state REVIEW, pending moves 0, active sessions 0; agent at-risk tag records invalidated stale Review/QA and capacity gate.",
      "next_action": "After one verified free standalone slot, move Blocked→Review and start/verify one configured Codex reviewer; on Review pass start distinct QA, and only after QA pass return to Human-QA.",
      "blocked_record": {
        "previous_workflow_step": "Human-QA",
        "exact_blocker_or_dependency": "Substantive maintainer head d742006c2b215705a2897487cc7275c41a2e9624 invalidated the older Review/QA receipts. Current provider census is green (57 success, 19 skipped, 0 failed, 0 pending; unresolved threads 0), but standalone ports 41001-41100 are exhausted, preventing a fresh verified Review owner.",
        "blocker_owner": "Capacity task 8a182e40-d99c-42e9-b9be-1f8f78cf8388; Coordinator owns atomic Review routing",
        "preservation_receipt": "TEST_RUNTIME=NONE; PR #3238 open, non-draft, clean at d742006c2b215705a2897487cc7275c41a2e9624; provider 57 success/19 skipped/0 failed/0 pending; unresolved threads 0; no runtime retained.",
        "owner_session_health": "active=0; pending_moves=0; no current Review owner because standalone capacity is exhausted.",
        "next_action": "After one verified free standalone slot, move Blocked→Review and start/verify one configured Codex reviewer; on Review pass start distinct QA, and only after QA pass return to Human-QA.",
        "deterministic_resume_trigger": "One verified free standalone allocation in 41001-41100.",
        "fallback": "If a fresh exact-head census has any real failure, move to CI Fixup with that exact failure; preserve head and do not ask Human to test.",
        "cleared": false,
        "provider_gate_green": true,
        "last_checked": "2026-09-15T00:18:30Z"
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3238,
          "state": "open",
          "draft": false,
          "head": "d742006c2b215705a2897487cc7275c41a2e9624",
          "checks": "success",
          "passing": 57,
          "skipped": 19,
          "failed": 0,
          "pending": 0,
          "threads": 0
        }
      ],
      "tags": [
        "agent at-risk: substantive head invalidated stale Review/QA; standalone capacity prevents verified Review owner."
      ]
    },
    {
      "task_id": "27b493a3-65b6-4d4a-8b68-73f2ffcf9621",
      "title": "Fix workflow-sync GitHub polling starving API quota",
      "column": "Work",
      "state": "REVIEW",
      "owner": "Coordinator",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Restored state and reported it to the spawning session.  Current clean head: `9560bc2b5ce93855adabb3dc37692406cab907bf`.  The QA fixes are present and locally validated. `upstream/main` has moved, so prior CI, review, QA, and mergeability results are stale. Next gate: integrate and revalidate against the current base before a fresh exact-head CI census.",
      "next_action": "After port capacity returns, start one configured Work owner to integrate current main, push clean successor, and rerun exact-head CI.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 5,
          "COMPLETED": 25
        },
        "active_ids": [],
        "latest": {
          "id": "716ce6e7-d83d-4682-bd64-ec3383adc1ef",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 22:44:41.648633528+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3143,
          "state": "open",
          "draft": 1,
          "head": "9560bc2b5ce93855adabb3dc37692406cab907bf",
          "checks": "failure",
          "passing": 8,
          "total": 10,
          "threads": 0
        }
      ],
      "blocker_or_gate": "No active owner; clean 9560bc2 requires current-main integration and fresh gates."
    },
    {
      "task_id": "375dcc90-9ff3-4064-ba27-a7f20b33e80c",
      "title": "Expose Provider Usage through read-only MCP",
      "column": "Blocked",
      "state": "SCHEDULING",
      "owner": "Coordinator/platform native-sandbox and writable-worktree owner, then child 77353939-0ba8-40dd-b93c-57adc73a4011",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "Repair the child checkout through the supported native sandbox route, finish its two bounded coverage gaps, then independently gate the child and re-evaluate this parent for terminal delivery.",
      "blocked_record": {
        "previous_workflow_step": "Review",
        "exact_blocker_or_dependency": "Open child 77353939-0ba8-40dd-b93c-57adc73a4011 still cannot commit the remaining Provider Usage coverage because its Git-admin/writable-checkout recovery is unresolved; parent cannot close while that child remains open.",
        "blocker_owner": "Coordinator/platform native-sandbox and writable-worktree owner, then child 77353939-0ba8-40dd-b93c-57adc73a4011",
        "preservation_receipt": "Host worktree /data/tasks/expose-provider-usag_kjfkfyxi/kandev-source, branch feature/expose-provider-usag-960, clean head a4228a8080904a45b8218024a44ae6ce45b164d8; plugin baseline/package/E2E evidence at a5c386b retained; no live runtime.",
        "owner_session_health": "active=0; pending_moves=0; newest 5fe851f9-7518-4066-8c00-607be9263d35 FAILED, Worker/gpt-5.6-terra, unsafe workspace-reuse inventory mismatch",
        "next_action": "Repair the child checkout through the supported native sandbox route, finish its two bounded coverage gaps, then independently gate the child and re-evaluate this parent for terminal delivery.",
        "deterministic_resume_trigger": "child gains a writable registered checkout, successful owner start, and terminal delivery receipt",
        "fallback": "Preserve a4228a8/a5c386b/package/E2E evidence; never revive rejected umbrella C2-C6 paths or unsafe workspace reuse.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": "child 77353939 physical Blocked/SCHEDULING, active=0/pending=0",
      "pending_moves": []
    },
    {
      "task_id": "37eca47b-cf05-47ee-b143-39408edbeed1",
      "title": "Bound merged worktree branch accumulation",
      "column": "CI Fixup",
      "state": "REVIEW",
      "owner": "Coordinator",
      "health": "waiting",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "CI Fixup is blocked by GitHub API rate limiting:  - Exact head verified: `90e076db266cc601f599b244afc007e21116cb1e` - Current `origin/main`: `941e7950d1a94e8c028bf5cb98744415e053bf74` - Synthetic merge is conflict-free. - Current-base focused worktree suite passes. - `gh pr checks`, `gh run view 34895075268`, `scripts/pr-state`, and `scripts/pr-resolve` a...",
      "next_action": "On quota recovery, start one Luna CI owner for bounded exact-head checks/threads; route only from terminal evidence.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 6,
          "COMPLETED": 27,
          "CANCELLED": 1
        },
        "active_ids": [],
        "latest": {
          "id": "87287050-0065-4266-9081-79d66a3dfc84",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "c151363f-a48d-4955-b669-cab94470d04a",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 23:05:36.500340889+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3158,
          "state": "open",
          "draft": 0,
          "head": "90e076db266cc601f599b244afc007e21116cb1e",
          "checks": "failure",
          "passing": 52,
          "total": 56,
          "threads": 0
        }
      ],
      "blocker_or_gate": "No active owner; PR #3158 exact head 90e076db is blocked on GitHub quota/current check census."
    },
    {
      "task_id": "3f721d52-452b-4bc6-a61e-68d875baafbd",
      "title": "Recover Redmine preflight in a dedicated workspace",
      "column": "Done",
      "state": "COMPLETED",
      "owner": "Coordinator terminal tracking",
      "health": "anomalous",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Added and verified the dependency on `a3f02302-12fa-4129-8985-116efb8fed66`.  The task is blocked pending that repair; branch, head, workspace, sessions, and PR #4 remain unchanged.",
      "next_action": "After workspace inventory repair, remove exact edge and verify blockers=[]; keep unarchived.",
      "session_health": {
        "counts": {
          "FAILED": 2,
          "CREATED": 2,
          "WAITING_FOR_INPUT": 1
        },
        "active_ids": [],
        "latest": {
          "id": "e152181b-9375-4d7c-9d97-b02b8f985b26",
          "state": "FAILED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 20:20:59.56347876+00:00",
          "error_message": "workspace reuse is unsafe: canonical workspace repository inventory has no matching entry for repository \"***\" branch \"main\""
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 4,
          "state": "merged",
          "draft": 0,
          "head": "980dead49f3af23ab10c16c4a2c49ae5887ee7fa",
          "checks": "success",
          "passing": 4,
          "total": 4,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Merged #4/clean delivery, but obsolete dependency on a3f02302 remains.",
      "terminal_integrity": {
        "status": "anomalous",
        "persisted_receipt": {
          "id": "3f721d52-452b-4bc6-a61e-68d875baafbd",
          "status": "anomalous",
          "receipt": "Merged PR #4 and delivery/runtime integrity passed; state COMPLETED. Obsolete a3f02302-12fa-4129-8985-116efb8fed66 edge remains because workspace inventory prevents a task-owned cleanup session."
        }
      }
    },
    {
      "task_id": "428d343e-c768-4bce-a5e7-efd3b10f363f",
      "title": "Plugin fenced runtime and scheduler",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "ca015838-e5cf-4294-b3bb-9c50576a5fe6 credential-lease/publication owner, then upstream deployment owner",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "Repair ca015838's exact credential lease, publish/reconcile its preserved head, complete fresh gates and deploy; then move this task to Work with one owner.",
      "blocked_record": {
        "previous_workflow_step": "Spec",
        "exact_blocker_or_dependency": "Host queue contract v1.1.0 is not deployed. Owner ca015838-e5cf-4294-b3bb-9c50576a5fe6 remains Blocked: local unpublished 37ca515b cannot reach stale PR #3377, whose projection is open/draft/failure at c990b51cb8dc758f35a702ee6ee017dd1c593c26.",
        "blocker_owner": "ca015838-e5cf-4294-b3bb-9c50576a5fe6 credential-lease/publication owner, then upstream deployment owner",
        "preservation_receipt": "Clean /data/tasks/plugin-fenced-runtim_053sh4tb/yattdev-kandev-plugin-coordinator, branch feature/plugin-fenced-runtim-ck9, head 6fb1fdd63c1728258c40a67df037116c5ca9bbb8; approved plan, no runtime/artifacts.",
        "owner_session_health": "active=0; pending_moves=0; e77fc2f7-6574-4f96-b654-6426e1805b15 WAITING_FOR_INPUT, Worker/gpt-5.6-terra",
        "next_action": "Repair ca015838's exact credential lease, publish/reconcile its preserved head, complete fresh gates and deploy; then move this task to Work with one owner.",
        "deterministic_resume_trigger": "deployed callable exact Host queue contract v1.1.0",
        "fallback": "Retain clean plan/head and do not reimplement or guess Host behavior.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": "blocked_by ca015838; a08ef33c and be077c0f Done; blocks 0259d242",
      "pending_moves": []
    },
    {
      "task_id": "4640fd95-b7f9-4339-8836-cf03679eaf41",
      "title": "Publish Redmine patch release",
      "column": "Done",
      "state": "REVIEW",
      "owner": "Coordinator terminal tracking",
      "health": "terminal",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Done terminal-integrity audit passed and receipt persisted.  Verified:  - Immutable v0.3.1 tag and release commit - Successful workflow `34809511526` - PRs #4 and #5 merged in order - Published assets and checksums - Clean, pushed task work - v0.3.0 preservation - No live Redmine plugin runtime  The Done step was completed and the parent task notified.",
      "next_action": "Archive on normal Done retention.",
      "session_health": {
        "counts": {
          "COMPLETED": 4,
          "WAITING_FOR_INPUT": 3
        },
        "active_ids": [],
        "latest": {
          "id": "278f22a6-2c1a-48c3-9a70-ac0360eff22d",
          "state": "COMPLETED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 05:40:20.528257106+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 5,
          "state": "merged",
          "draft": 0,
          "head": "03b2754db637331caa585b5e4a7f9b397bd5c925",
          "checks": "success",
          "passing": 0,
          "total": 0,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Merged release delivery and immutable v0.3.1 assets/checksums verified; no live runtime.",
      "terminal_integrity": {
        "status": "terminal",
        "persisted_receipt": {
          "id": "4640fd95-b7f9-4339-8836-cf03679eaf41",
          "status": "terminal",
          "receipt": "Merged PR #5 and immutable Redmine release integrity passed."
        }
      }
    },
    {
      "task_id": "46945aff-382a-41a4-9f35-bd5c2806911e",
      "title": "Expose guarded TTY tool to ACP agents",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "Human release/deploy owner of 01432319-aa8b-4c7d-9841-addcc6ab8e76, then Coordinator for fresh QA",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "After supported runtime deployment, move to QA and start one fresh configured QA owner for live TTY cancel and ordinary non-TTY coexistence evidence.",
      "blocked_record": {
        "previous_workflow_step": "QA",
        "exact_blocker_or_dependency": "Final live integration still lacks an approved deployed maintained codex-acp runtime advertising guarded_tty_exec_kandev to an ordinary guarded task. Source owner 01432319-aa8b-4c7d-9841-addcc6ab8e76 is Human-owned ToDeploy; scoped fixture QA cannot replace live credentialed TTY/non-TTY acceptance.",
        "blocker_owner": "Human release/deploy owner of 01432319-aa8b-4c7d-9841-addcc6ab8e76, then Coordinator for fresh QA",
        "preservation_receipt": "Kandev worktree /data/tasks/expose-guarded-tty-t_dxnio2ff/kdlbs-kandev, branch feature/expose-guarded-tty-t-46l, clean PR #3497 head ae8fc93dfe7d84170921a2c074b9142876cc4b13 with checks success; immutable maintained fork f4df079f6f6a31e300772f537b14db54136a0ff6 and package checksums/artifacts retained; no live runtime/credentials.",
        "owner_session_health": "active=0; pending_moves=0; 3f3b00d7-8ba9-415c-a3f8-466f6fad716e WAITING_FOR_INPUT, Worker/gpt-5.6-terra; prior Review and scoped QA completed",
        "next_action": "After supported runtime deployment, move to QA and start one fresh configured QA owner for live TTY cancel and ordinary non-TTY coexistence evidence.",
        "deterministic_resume_trigger": "deployed approved maintained package advertises guarded_tty_exec_kandev to an ordinary guarded task",
        "fallback": "Retain artifacts and fail closed; no credential extraction, security weakening, or duplicate deployment ping.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": "no formal edge; source/release owner 01432319 is ToDeploy with merged fork PR #1",
      "pending_moves": []
    },
    {
      "task_id": "4b56a8b3-89fa-43ef-891d-c6b3a3b88e2a",
      "title": "Propagate CI cleanup errors on workspace deletion",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "9ee4be81-aa98-4e4d-bdd6-842fd918f00f and upstream maintainer; execution capacity root 8a182e40-d99c-42e9-b9be-1f8f78cf8388",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "Restore execution capacity, resume 9ee4be81 to finish and deliver the canonical store contract, then move this task to Work on landed main.",
      "blocked_record": {
        "previous_workflow_step": "Spec",
        "exact_blocker_or_dependency": "Required scoped-CI store contract is not in canonical main. Owner 9ee4be81-aa98-4e4d-bdd6-842fd918f00f remains CI Fixup/FAILED with no active session; PR #3165 is open/non-draft, checks success, mergeable blocked at a199dcd42a187572b52a428ed2fa158ebc1b06bd and still needs its PostgreSQL/current-main repair and delivery.",
        "blocker_owner": "9ee4be81-aa98-4e4d-bdd6-842fd918f00f and upstream maintainer; execution capacity root 8a182e40-d99c-42e9-b9be-1f8f78cf8388",
        "preservation_receipt": "Approved consumer plan; clean worktree /data/tasks/propagate-ci-cleanup_38s1stuy/kdlbs-kandev, branch feature/propagate-ci-cleanup-2jg, head 1ddce606edefe44c517f1f8829391f2e25b2cbee; no task implementation/runtime/data mutation.",
        "owner_session_health": "active=0; pending_moves=0; 339b7c88-b4ee-46fc-8b9f-bc3436bd08a3 WAITING_FOR_INPUT, Worker/gpt-5.6-terra",
        "next_action": "Restore execution capacity, resume 9ee4be81 to finish and deliver the canonical store contract, then move this task to Work on landed main.",
        "deterministic_resume_trigger": "PR #3165 merged or exact deleteCIRunWorkspaceData contract proved in canonical main",
        "fallback": "Preserve plan/clean skeleton and do not implement against the open carrier.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": "blocked_by 9ee4be81 (CI Fixup/FAILED, active=0/pending=0)",
      "pending_moves": []
    },
    {
      "task_id": "51c2875b-48ae-4097-b985-b8a9584ca8c2",
      "title": "Bug: Notes settings agent utility doesn't load agents profil",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "Human scope decision, then Host/Notes delivery owner; 9ee4be81 for scoped CI",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "Obtain the recorded Human scope choice; if adopting the maintainer contract, route to Spec/Work, reconcile exact Host head, then run fresh CI, Review, and QA before readiness.",
      "blocked_record": {
        "previous_workflow_step": "PR",
        "exact_blocker_or_dependency": "Material contract choice remains Human-owned: adopt maintainer-directed plugin-owned saved-profile dispatch with Utility Agents fallback or retain Host-selected contract. Meanwhile Host PR #2870 advanced to c24fc80361d014705b7ab156025b82792ba6168e and current projection is open/non-draft/blocked with checks pending; its prior QA head is stale. Formal scoped-CI dependency 9ee4be81 is also CI Fixup/FAILED.",
        "blocker_owner": "Human scope decision, then Host/Notes delivery owner; 9ee4be81 for scoped CI",
        "preservation_receipt": "Host local /data/tasks/bug-notes-settings-a_imzafc8h/kandev-source, branch feature/implement-host-agent-oav, clean 929c4c3cfeecc7a89eb960bd5474ddb731f019c7 and behind remote; provider PR #2870 at c24fc80361d014705b7ab156025b82792ba6168e. Notes clean branch feature/bug-notes-settings-a-0s3 and PR #7 at 19035c9e9989e2372d8e4eaca99772b58eb76a96, checks success. QA artifacts retained; no services.",
        "owner_session_health": "active=0; pending_moves=0; 418654e6-ec5d-43e0-9c28-f2702f4a86a6 WAITING_FOR_INPUT, DI small/DeepSeek V4 Flash",
        "next_action": "Obtain the recorded Human scope choice; if adopting the maintainer contract, route to Spec/Work, reconcile exact Host head, then run fresh CI, Review, and QA before readiness.",
        "deterministic_resume_trigger": "explicit Human contract decision plus terminal exact-head CI/capacity for the selected route",
        "fallback": "Preserve both PRs/artifacts and withhold readiness, reviewer contact, merge, and deployment.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": "blocked_by 9ee4be81; two implementation children are Done",
      "pending_moves": []
    },
    {
      "task_id": "531a41cd-57ef-495a-8dfa-614d2a4d0d52",
      "title": "Allow Coordinator dependency-edge mutation",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "fa3fba49-2018-460b-a600-adae23b24cc8 for #3048, 7056a702-a3c3-4fe8-8535-c6b8d340ef6a for #3155, then upstream maintainer",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "Finish the prerequisite principal-binding reconciliation and fresh exact-head gates; resume this task only after one canonical authority contract is reviewed and delivered.",
      "blocked_record": {
        "previous_workflow_step": "CI Fixup",
        "exact_blocker_or_dependency": "No single canonical Coordinator designation/authority model is integrated. PR #3048 is open/draft/pending at new head 56531c6e2d5dbea93682ab773fe5e0f55e86ee5d; PR #3155 is open/non-draft/blocked/pending at new head 2c2f9fd87397acedd90064d06333087034898ddb. Earlier head receipts are stale and neither contract is merged.",
        "blocker_owner": "fa3fba49-2018-460b-a600-adae23b24cc8 for #3048, 7056a702-a3c3-4fe8-8535-c6b8d340ef6a for #3155, then upstream maintainer",
        "preservation_receipt": "Clean /data/tasks/allow-coordinator-de_au1g7cb7/kandev-source, branch feature/allow-coordinator-de-gaj, zero-delta head cfd6bdf65ae6f631d7701c105791a099c0325cc3; no runtime/artifacts/live grant mutation.",
        "owner_session_health": "active=0; pending_moves=0; latest 5e0de349-8eaf-404f-9ae9-e5d102f70686 WAITING_FOR_INPUT, DI small/DeepSeek V4 Flash; dormant CI owner 72a7d5bd WAITING_FOR_INPUT",
        "next_action": "Finish the prerequisite principal-binding reconciliation and fresh exact-head gates; resume this task only after one canonical authority contract is reviewed and delivered.",
        "deterministic_resume_trigger": "one canonical designation model is merged/contained with competing authority models resolved",
        "fallback": "Preserve zero-delta carrier and stale-head evidence; do not enable live grants.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": "no formal edges; provider prerequisites #3048/#3155 tracked operationally",
      "pending_moves": []
    },
    {
      "task_id": "5c9f515d-e5f9-43c5-bf31-fb42276e5e15",
      "title": "Add guarded TTY bridge to codex-acp",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "agentclientprotocol/codex-acp maintainers",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "Watch for new upstream review/workflow/merge/release evidence; no duplicate maintainer ping. Close or reclassify only after the upstream disposition is terminal.",
      "blocked_record": {
        "previous_workflow_step": "Review",
        "exact_blocker_or_dependency": "Upstream PR #451 remains open/non-draft/unstable at exact 0bd0f8fb74a0dfec93eb3a8e586dc0d7c0e8488d and is watch-only pending maintainer workflow/review/merge/release. Downstream maintained-fork delivery is already merged and must not depend on this upstream decision.",
        "blocker_owner": "agentclientprotocol/codex-acp maintainers",
        "preservation_receipt": "Worktree /data/tasks/add-guarded-tty-brid_10966pzf/agentclientprotocol-codex-acp, branch feature/add-guarded-tty-brid-6q9, local/provider head 0bd0f8fb74a0dfec93eb3a8e586dc0d7c0e8488d; upstream request issuecomment-5577911822 already sent; maintained fork PR #1 merged at f4df079; no runtime.",
        "owner_session_health": "active=0; pending_moves=0; dormant CI Fixup sessions 70ecf6f1-9d03-4435-a50e-acce577ec6ec and 0e345274-f015-417f-986a-fe727c7f61a7 WAITING_FOR_INPUT, gpt-5.6-luna",
        "next_action": "Watch for new upstream review/workflow/merge/release evidence; no duplicate maintainer ping. Close or reclassify only after the upstream disposition is terminal.",
        "deterministic_resume_trigger": "new maintainer review, workflow approval/check result, merge, close, or release",
        "fallback": "Preserve PR/head as reference and continue downstream through the maintained fork.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": "none; explicitly not a blocker for downstream 46945aff",
      "pending_moves": []
    },
    {
      "task_id": "6a5a2f73-87e1-4c08-a983-64f2456c3633",
      "title": "Executor containers: allow unprivileged user namespaces",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "Support/platform runtime owner; Coordinator owns atomic resume",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "On a verified Support repair receipt, move to Human-QA and start one fresh configured owner for exactly one bounded acceptance probe with host/time/output.",
      "blocked_record": {
        "previous_workflow_step": "Human-QA",
        "exact_blocker_or_dependency": "PR #2937 is merged, but terminal acceptance still requires Support request 16b0c902-464c-40e6-80b1-fc69b8f63ce4 to provision reusable host user-namespace capability, followed by exactly one bounded task-owned unshare/bwrap probe. No verified Support receipt is visible in this workspace.",
        "blocker_owner": "Support/platform runtime owner; Coordinator owns atomic resume",
        "preservation_receipt": {
          "branch": "feature/executor-containers-nll",
          "extra": "origin/backup/executor-containers-nll-local-1 at same head; 5,649 staged/unmerged entries preserved untouched",
          "head": "d8af676da8852ea68dec1faedec8ed3baa8a236c",
          "runtime_data": "none running; prior probe receipt preserved",
          "worktree": "/data/tasks/executor-containers_7oiab541/kandev-source"
        },
        "owner_session_health": {
          "active_count": 0,
          "counts": {
            "COMPLETED": 3,
            "WAITING_FOR_INPUT": 6
          },
          "newest": [
            {
              "agent_profile_id": "5b1dc511-64f7-448a-aa2c-5bf72e81f9e9",
              "error_message": "",
              "id": "5392b5ee-1843-4436-bd3a-50c9be5b9429",
              "is_primary": 1,
              "name": "",
              "profile": {
                "model": "savoirfairelinux/DeepInfra/deepseek-ai%2FDeepSeek-V4-Flash-0731",
                "name": "DI small"
              },
              "started_at": "2026-09-14 03:10:46.113349559+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-14 03:13:21.629183558+00:00",
              "workspace_path": "/data/tasks/executor-containers_7oiab541/kandev-source"
            },
            {
              "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
              "error_message": "",
              "id": "bd0e2a4e-2357-42ea-8601-e5ea0a00a9d5",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-luna",
                "name": "CI Fixup"
              },
              "started_at": "2026-09-14 02:54:31.158430305+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-14 03:10:49.255456817+00:00",
              "workspace_path": "/data/tasks/executor-containers_7oiab541/kandev-source"
            },
            {
              "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
              "error_message": "",
              "id": "9551a5d6-41b7-43d1-b2ab-5bbf70769347",
              "is_primary": 0,
              "name": "fresh-terra-task-local-probe",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker"
              },
              "started_at": "2026-09-08 09:02:13.838153697+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-14 03:10:48.120992536+00:00",
              "workspace_path": "/data/tasks/executor-containers_7oiab541/kandev-source"
            },
            {
              "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
              "error_message": "",
              "id": "289224cc-e691-48c2-aee4-584633205b7e",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker"
              },
              "started_at": "2026-08-27 19:38:02.919801968+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-14 03:10:48.120992536+00:00",
              "workspace_path": "/data/tasks/executor-containers_7oiab541/kandev-source"
            },
            {
              "agent_profile_id": "06f0a558-84be-486e-a3ea-941b679dc87a",
              "error_message": "",
              "id": "894d80d3-60b4-44bf-9f26-41677572511c",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "sonnet",
                "name": "CI Fixup"
              },
              "started_at": "2026-08-18 20:37:02.670972589+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-14 03:10:48.120992536+00:00",
              "workspace_path": "/data/tasks/executor-containers_7oiab541/kandev-source"
            }
          ]
        },
        "next_action": "On a verified Support repair receipt, move to Human-QA and start one fresh configured owner for exactly one bounded acceptance probe with host/time/output.",
        "deterministic_resume_trigger": "Pushed Support repair receipt plus explicit task-owning bounded-probe handoff.",
        "fallback": "Preserve checkout and incident evidence; no raw Docker, sudo, source/security change, or repeat probe.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": {
        "blocked_by": [],
        "blocks": [],
        "parent_id": ""
      },
      "pending_moves": []
    },
    {
      "task_id": "6d03f4a9-bf89-4882-bf43-5a584f986185",
      "title": "Adopt exact profile assignment persistence",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "e0dd8d19, 7056a702/#3155, 9ee4be81/#3165 delivery owners; Coordinator",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "After the three contracts stabilize, move to Work and start one configured Codex owner to execute the saved semantic-adoption plan without copying superseded policy layers.",
      "blocked_record": {
        "previous_workflow_step": "Spec",
        "exact_blocker_or_dependency": "Implementation must semantically layer on the stable exact-model/start-policy contract from task e0dd8d19/PR #3473 and coordinate pending-move/store seams from #3155/#3165. Fixed model-lane gates are suspended, but these code contracts remain structural prerequisites; e0dd is Work/REVIEW with no active owner, #3155 is actively being repaired, and #3165 remains undelivered.",
        "blocker_owner": "e0dd8d19, 7056a702/#3155, 9ee4be81/#3165 delivery owners; Coordinator",
        "preservation_receipt": {
          "branch": "feature/platform-exact-profi-dbo (source carrier)",
          "extra": "preserved ref 2f753d219bfe96859d6f429b2272263dda0be52b; source carrier /data/tasks/platform-exact-profi_k2tb6qj7/kdlbs-kandev; canonical worktree clean",
          "head": "0c83f80fd90082aa4dc3b7baeb0b28cd6af77575",
          "runtime_data": "none",
          "worktree": "/data/tasks/adopt-exact-profile_aymu1kux/kandev-source"
        },
        "owner_session_health": {
          "active_count": 0,
          "counts": {
            "COMPLETED": 1,
            "WAITING_FOR_INPUT": 1
          },
          "newest": [
            {
              "agent_profile_id": "5b1dc511-64f7-448a-aa2c-5bf72e81f9e9",
              "error_message": "",
              "id": "74f1590e-9dad-4dca-8a2c-0e1652bdccdf",
              "is_primary": 1,
              "name": "",
              "profile": {
                "model": "savoirfairelinux/DeepInfra/deepseek-ai%2FDeepSeek-V4-Flash-0731",
                "name": "DI small"
              },
              "started_at": "2026-09-14 21:02:52.866930435+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-14 21:05:40.014752615+00:00",
              "workspace_path": "/data/tasks/adopt-exact-profile_aymu1kux/kandev-source"
            },
            {
              "agent_profile_id": "67ba38d7-89b5-40a8-a355-702e25d9e903",
              "error_message": "",
              "id": "b27451e9-66cd-46e1-b67e-2e674fedb794",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "savoirfairelinux/DeepInfra/moonshotai%2FKimi-K3",
                "name": "Kimi k3"
              },
              "started_at": "2026-09-14 20:44:58.818926127+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-14 21:02:53.548782821+00:00",
              "workspace_path": "/data/tasks/adopt-exact-profile_aymu1kux/kandev-source"
            }
          ]
        },
        "next_action": "After the three contracts stabilize, move to Work and start one configured Codex owner to execute the saved semantic-adoption plan without copying superseded policy layers.",
        "deterministic_resume_trigger": "PR #3473 exact contract and #3155/#3165 relevant seams are reviewed/delivered on a stable base.",
        "fallback": "Keep the source carrier immutable and re-plan changed seams; do not implement a competing model policy.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": {
        "blocked_by": [],
        "blocks": [],
        "parent_id": "a68df3ae-aaf5-4591-a46d-9d73db62e46d"
      },
      "pending_moves": []
    },
    {
      "task_id": "7056a702-a3c3-4fe8-8535-c6b8d340ef6a",
      "title": "Add exact pending-move cancellation",
      "column": "Work",
      "state": "IN_PROGRESS",
      "owner": "task agent; active session 0ba4a3ab-99ac-460d-95db-7f9800efd0db RUNNING",
      "health": "healthy",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "The E2E matrix is making steady progress: 26 passed, 24 pending, no failures.",
      "next_action": "Consume terminal matrix/repair receipt; branch-owned fix then fresh independent Review and QA.",
      "session_health": {
        "counts": {
          "RUNNING": 1,
          "COMPLETED": 24,
          "WAITING_FOR_INPUT": 3,
          "FAILED": 1,
          "CANCELLED": 24
        },
        "active_ids": [
          "0ba4a3ab-99ac-460d-95db-7f9800efd0db RUNNING"
        ],
        "latest": {
          "id": "0ba4a3ab-99ac-460d-95db-7f9800efd0db",
          "state": "RUNNING",
          "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 23:57:41.55916148+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3155,
          "state": "open",
          "draft": 0,
          "head": "2c2f9fd87397acedd90064d06333087034898ddb",
          "checks": "pending",
          "passing": 25,
          "total": 25,
          "threads": 0
        }
      ],
      "blocker_or_gate": "RUNNING Work owner; E2E matrix reported 26 passed/24 pending/0 failed."
    },
    {
      "task_id": "75d4c8af-dc90-4e68-bc74-3d86e99e52cb",
      "title": "Resolve C1 git-metadata projection disposition",
      "column": "Done",
      "state": "REVIEW",
      "owner": "Coordinator terminal tracking",
      "health": "terminal",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Done integrity verification completed and recorded in the task plan.  - Worktree clean; no unpublished work lost. - PR #3496 remains open/draft at `5504448a...`. - PR #3242 remains closed/unmerged at `9a6f2829...`. - Maintainer disposition preserved verbatim. - No source, PR, provider, implementation, or design mutation. - Provider mutation count: `0`.",
      "next_action": "Archive by retention while preserving the reference.",
      "session_health": {
        "counts": {
          "COMPLETED": 1,
          "WAITING_FOR_INPUT": 2
        },
        "active_ids": [],
        "latest": {
          "id": "1f585cd0-1733-4cb6-8407-3affceecc6eb",
          "state": "COMPLETED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 20:20:04.479004241+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [],
      "blocker_or_gate": "Maintainer disposition preserved; #3496 remains an intentional draft reference; no unique unpublished work.",
      "terminal_integrity": {
        "status": "terminal",
        "persisted_receipt": {
          "id": "75d4c8af-dc90-4e68-bc74-3d86e99e52cb",
          "status": "terminal",
          "receipt": "Maintainer disposition comment 5668637398 preserved; terminal read-only session completed; successor task owns sandbox design."
        }
      }
    },
    {
      "task_id": "76b4e3d4-ccb8-408c-a0de-5e5014c538be",
      "title": "Make visible Human questions durable",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "kdlbs/kandev Actions administrator plus current-base conflict repair owner",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "When a new exact-head run or substantive successor exists, route CI Fixup to classify it; green requires fresh Review and distinct QA.",
      "blocked_record": {
        "previous_workflow_step": "CI Fixup",
        "exact_blocker_or_dependency": "PR #3404 remains open/draft at 654a7cdca1d7af0eba20ac2acae63d4dcc04ab63 with the saved immutable-GHCR/shared-infrastructure failure and an admin-denied rerun; current branch also requires a substantive conflict/current-base resolution before fresh gates.",
        "blocker_owner": "kdlbs/kandev Actions administrator plus current-base conflict repair owner",
        "preservation_receipt": {
          "branch": "feature/make-visible-human-q-u2t",
          "extra": "local/fork/PR aligned and clean in saved receipt",
          "head": "654a7cdca1d7af0eba20ac2acae63d4dcc04ab63",
          "runtime_data": "no runtime or DB fixture",
          "worktree": "/data/tasks/make-visible-human-q_vhjkt1t6/kdlbs-kandev"
        },
        "owner_session_health": {
          "active_count": 0,
          "counts": {
            "CANCELLED": 1,
            "COMPLETED": 2,
            "WAITING_FOR_INPUT": 1
          },
          "newest": [
            {
              "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
              "error_message": "",
              "id": "d30978b2-e58e-4647-a687-0018172b1612",
              "is_primary": 1,
              "name": "",
              "profile": {
                "model": "gpt-5.6-luna",
                "name": "CI Fixup"
              },
              "started_at": "2026-09-05 09:24:42.084804551+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-09 04:11:53.006927506+00:00",
              "workspace_path": "/data/tasks/make-visible-human-q_vhjkt1t6/kdlbs-kandev"
            },
            {
              "agent_profile_id": "bd2c30cb-f2b6-4202-9a9b-0212632c15fe",
              "error_message": "",
              "id": "2c83cc7f-6d3b-4c1f-a9fc-c988485fd7cf",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-sol",
                "name": "Spec"
              },
              "started_at": "2026-09-05 06:55:30.492824221+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-05 09:24:42.490524709+00:00",
              "workspace_path": "/data/tasks/make-visible-human-q_vhjkt1t6/kdlbs-kandev"
            },
            {
              "agent_profile_id": "ce9f96f7-4434-4729-b23b-926b4b72f417",
              "error_message": "stopped by parent task via MCP",
              "id": "c031fc77-f998-4a93-95fe-c7248bcb63e0",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker-claude"
              },
              "started_at": "2026-09-01 05:17:33.484358291+00:00",
              "state": "CANCELLED",
              "updated_at": "2026-09-05 09:24:42.210904092+00:00",
              "workspace_path": "/data/tasks/make-visible-human-q_vhjkt1t6/kdlbs-kandev"
            },
            {
              "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
              "error_message": "",
              "id": "a3fcb767-ac94-4217-86fd-3a3529ea6552",
              "is_primary": 0,
              "name": "durable-human-question-owner",
              "profile": {
                "model": "gpt-5.6-luna",
                "name": "CI Fixup"
              },
              "started_at": "2026-09-01 03:38:02.454730211+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-05 09:24:42.210904092+00:00",
              "workspace_path": ""
            }
          ]
        },
        "next_action": "When a new exact-head run or substantive successor exists, route CI Fixup to classify it; green requires fresh Review and distinct QA.",
        "deterministic_resume_trigger": "Admin rerun/new scoped CI run, PR head change, or conflict-free successor.",
        "fallback": "No duplicate rerun/contact and no retry-only commit; preserve branch.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": {
        "blocked_by": [],
        "blocks": [],
        "parent_id": "a68df3ae-aaf5-4591-a46d-9d73db62e46d"
      },
      "pending_moves": []
    },
    {
      "task_id": "77353939-0ba8-40dd-b93c-57adc73a4011",
      "title": "Implement provider-usage MCP tool",
      "column": "Blocked",
      "state": "SCHEDULING",
      "owner": "Coordinator/platform workspace-materialization owner; successor executor-owned sandbox delivery",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "Replace the obsolete #3496 trigger with a fresh managed writable-checkout recovery owner under the approved executor-owned sandbox direction; then recover intent and start Work once.",
      "blocked_record": {
        "previous_workflow_step": "Review",
        "exact_blocker_or_dependency": "The child checkout still cannot start safely: Git admin/index materialization is missing or collides, and recent starts fail repository-inventory/worktree validation. Its tag and old trigger name PR #3496 writable-worktree delivery, but H1-H5 now keep #3496 draft/reference-only and plan to close it without merge, so the recorded trigger is superseded.",
        "blocker_owner": "Coordinator/platform workspace-materialization owner; successor executor-owned sandbox delivery",
        "preservation_receipt": {
          "branch": "UNKNOWN — managed Git admin unavailable",
          "extra": "attached read-only host at kdlbs-kandev-main and workspace symlink /data/tasks/implement-provider-u_k97qa5oa/kandev; no cleanup authorized",
          "head": "preserved Provider Usage baseline/intent; parent baseline a5c386b",
          "runtime_data": "none",
          "worktree": "/data/tasks/implement-provider-u_k97qa5oa"
        },
        "owner_session_health": {
          "active_count": 0,
          "counts": {
            "COMPLETED": 1,
            "FAILED": 3
          },
          "newest": [
            {
              "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
              "error_message": "workspace reuse is unsafe: canonical workspace repository inventory has no matching entry for repository \"***\" branch \"main\"",
              "id": "f44b042d-b4fb-4a4e-97d1-1b33f4e2c2ff",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker"
              },
              "started_at": "2026-09-07 13:43:29.284999596+00:00",
              "state": "FAILED",
              "updated_at": "2026-09-07 13:43:29.304606504+00:00",
              "workspace_path": ""
            },
            {
              "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
              "error_message": "environment preparation failed: git command failed: Preparing worktree (checking out '***')\nfatal: '***' already exists",
              "id": "f1ae0de9-7974-455c-a5ca-4005954b869d",
              "is_primary": 1,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker"
              },
              "started_at": "2026-08-27 21:57:46.857205791+00:00",
              "state": "FAILED",
              "updated_at": "2026-08-27 21:57:54.720880532+00:00",
              "workspace_path": ""
            },
            {
              "agent_profile_id": "5d7135f9-8b98-4168-856d-1b495e19b481",
              "error_message": "environment preparation failed: git command failed: Preparing worktree (checking out '***')\nfatal: '***' already exists",
              "id": "ec16aaa2-e194-48aa-b209-299ebde05122",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Terra 5.6"
              },
              "started_at": "2026-08-19 09:03:11.771727965+00:00",
              "state": "FAILED",
              "updated_at": "2026-08-27 21:57:46.859845428+00:00",
              "workspace_path": ""
            },
            {
              "agent_profile_id": "5d7135f9-8b98-4168-856d-1b495e19b481",
              "error_message": "",
              "id": "03a945b9-3602-40e9-947b-fad7ea22c80a",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Terra 5.6"
              },
              "started_at": "2026-08-19 08:02:53.654276984+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-08-27 21:57:46.866420632+00:00",
              "workspace_path": "/data/tasks/implement-provider-u_k97qa5oa"
            }
          ]
        },
        "next_action": "Replace the obsolete #3496 trigger with a fresh managed writable-checkout recovery owner under the approved executor-owned sandbox direction; then recover intent and start Work once.",
        "deterministic_resume_trigger": "Verified registered writable checkout plus successful bounded fresh session start under current execution capacity.",
        "fallback": "Keep baseline/artifact intent immutable; do not retry failed reuse or recreate old #3496 architecture.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": {
        "blocked_by": [],
        "blocks": [],
        "parent_id": "375dcc90-9ff3-4064-ba27-a7f20b33e80c"
      },
      "pending_moves": []
    },
    {
      "task_id": "7a0454aa-c089-4365-8966-ad99775a46f8",
      "title": "Fix Redmine derived custom-field fallback",
      "column": "Done",
      "state": "COMPLETED",
      "owner": "Coordinator terminal tracking",
      "health": "terminal",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Dependency edge removed successfully.  - Removed predecessor: `e8728906-86de-4a75-960f-9da585485823` - Current task: `7a0454aa-c089-4365-8966-ad99775a46f8` - Result: `blocked=false`, `depends_on=[]` - Verification: predecessor absent from related tasks - No code, files, plans, provider state, task lane/state, or other relations changed",
      "next_action": "Archive on normal Done retention.",
      "session_health": {
        "counts": {
          "COMPLETED": 3,
          "CANCELLED": 35
        },
        "active_ids": [],
        "latest": {
          "id": "ea654329-5c6f-4cff-96fb-34956e751bae",
          "state": "COMPLETED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 20:21:23.877177274+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3,
          "state": "merged",
          "draft": 0,
          "head": "caf0112739375dc5e4ecce5a09456096a8566110",
          "checks": "success",
          "passing": 4,
          "total": 4,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Merged #3; obsolete dependency removed and blockers=[] verified.",
      "terminal_integrity": {
        "status": "terminal",
        "persisted_receipt": {
          "id": "7a0454aa-c089-4365-8966-ad99775a46f8",
          "status": "terminal",
          "receipt": "Merged PR #3; obsolete e8728906-86de-4a75-960f-9da585485823 dependency removed; blockers=[] and state COMPLETED verified."
        }
      }
    },
    {
      "task_id": "7ca86e53-249b-4b31-a866-e807afd9a962",
      "title": "feat: Implement Redmine integration",
      "column": "Done",
      "state": "COMPLETED",
      "owner": "Coordinator terminal tracking",
      "health": "terminal-preserved",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Fresh read-only lane/session/provider/relations inspection completed; no mutation.",
      "next_action": "Closed-ledger retention; no cleanup without a separate safe preservation receipt.",
      "session_health": {
        "counts": {
          "FAILED": 4
        },
        "active_ids": [],
        "latest": {
          "id": "bc5890dd-9063-4351-8e9d-01c8176a507e",
          "state": "FAILED",
          "agent_profile_id": "2653283e-3df4-48d6-8242-774b24b54f38",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 22:43:42.899612704+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 2724,
          "state": "closed",
          "draft": 1,
          "head": "b0feb95dd74e1f48eb8b00bc38761b11fc5ea4ff",
          "checks": "success",
          "passing": 3,
          "total": 3,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Plugin #1 and Host #2872 are merged; canonical ecd v0.3.2 E2E is Done; historical checkout remains preserved.",
      "terminal_integrity": {
        "status": "terminal-preserved",
        "receipt": "Plugin #1 and Host #2872 merged; canonical v0.3.2 E2E task completed; historical PR #2724 is closed and the legacy checkout remains preservation-only. No cleanup without a separate safe receipt."
      }
    },
    {
      "task_id": "856898aa-d06a-43f7-9a87-f873665f19da",
      "title": "The tags plugin update should preserve the existings tags",
      "column": "Done",
      "state": "REVIEW",
      "owner": "Coordinator terminal tracking",
      "health": "terminal",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Terminal readback passed, and the task was routed to Done.  The merged implementation is present in `origin/main`; the worktree is clean, with only the preserved local QA-artifacts-only commit ahead of the feature remote. No PR, branch, readiness, or reviewer state was changed.",
      "next_action": "Archive on normal retention while preserving evidence assets.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 4,
          "COMPLETED": 15
        },
        "active_ids": [],
        "latest": {
          "id": "c294d548-739c-4527-bc6f-89cbaeee5f42",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 18:28:56.673397754+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 17,
          "state": "merged",
          "draft": 0,
          "head": "a630cb9c44e7a7b4467b531fbeb35a56e119c601",
          "checks": "success",
          "passing": 3,
          "total": 3,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Merged #17; local 9e6faf0 is QA-artifacts-only evidence; no QA-started runtime remains.",
      "terminal_integrity": {
        "status": "terminal",
        "persisted_receipt": {
          "id": "856898aa-d06a-43f7-9a87-f873665f19da",
          "status": "terminal",
          "receipt": "Merged PR #17; terminal receipt passed; remaining local commit is evidence-only."
        }
      }
    },
    {
      "task_id": "86a16fc1-6394-4fb0-898d-4d42948683f5",
      "title": "Bound plugin registry release latency",
      "column": "CI Fixup",
      "state": "FAILED",
      "owner": "Coordinator",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "CI fixup recheck complete:  - PR #3153 remains open/draft/mergeable at exact head `135a156acfaf24803e3938034acddada0f6b366a`. - All checks are terminal. - Backend Tests (2/2), job `104119967316`, remains failed. - Logs confirm an application test failure in `internal/agent/runtime/lifecycle`, matching the known base-owned flaky test. - No branch-owned def...",
      "next_action": "After capacity repair and legitimate rerun activity, start one Luna owner to classify job 104119967316; no duplicate request.",
      "session_health": {
        "counts": {
          "FAILED": 2,
          "WAITING_FOR_INPUT": 5,
          "COMPLETED": 6,
          "CANCELLED": 1
        },
        "active_ids": [],
        "latest": {
          "id": "c6632154-cf10-4fb0-9c8b-72d9b36df611",
          "state": "FAILED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 23:53:42.323399911+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3153,
          "state": "open",
          "draft": 1,
          "head": "135a156acfaf24803e3938034acddada0f6b366a",
          "checks": "failure",
          "passing": 53,
          "total": 55,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Standalone capacity [41001,41100] is exhausted; configured session failed before inference. Existing single maintainer rerun trigger remains."
    },
    {
      "task_id": "86c8b47e-e7a5-4693-8e11-dce08899a0bf",
      "title": "Preserve unread queue on session deletion",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "ca015838/#3377 delivery owner, then this task implementation owner and upstream maintainer",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "After #3377 is canonical, integrate current main, fix bounded retention/tombstone semantics, rerun fresh Review and distinct QA, and open the real upstream delivery PR.",
      "blocked_record": {
        "previous_workflow_step": "CI Fixup",
        "exact_blocker_or_dependency": "Queue-preserving cleanup implementation is stacked on ca015838/PR #3377, which is not canonically delivered. Temporary fork PR #15 at c4156e83b8379851f50ce6890a13b16720874df9 is review evidence only and retains a QA blocker: unbounded full-payload recovery snapshots lack audited bounded retention/redaction after disposition or hard deletion.",
        "blocker_owner": "ca015838/#3377 delivery owner, then this task implementation owner and upstream maintainer",
        "preservation_receipt": {
          "branch": "feature/preserve-unread-queu-s0c",
          "extra": "clean tracked tree; six untracked QA screenshots in apps/web/.qa-artifacts preserved",
          "head": "c4156e83b8379851f50ce6890a13b16720874df9",
          "runtime_data": "all temporary E2E runtimes stopped",
          "worktree": "/data/tasks/preserve-unread-queu_ofb2j8xg/kdlbs-kandev"
        },
        "owner_session_health": {
          "active_count": 0,
          "counts": {
            "COMPLETED": 1,
            "WAITING_FOR_INPUT": 2
          },
          "newest": [
            {
              "agent_profile_id": "ab57f00e-ed8d-4205-bada-8be63fc4cd7d",
              "error_message": "",
              "id": "02b48c70-3ad9-461d-a5ca-7fe3c01dfe50",
              "is_primary": 0,
              "name": "fresh-review-queue-retention-41922c84",
              "profile": {
                "model": "gpt-5.5",
                "name": "Review"
              },
              "started_at": "2026-09-06 08:07:43.596498386+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-06 08:11:23.115805113+00:00",
              "workspace_path": "/data/tasks/preserve-unread-queu_ofb2j8xg"
            },
            {
              "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
              "error_message": "",
              "id": "2376d3fe-6818-4486-a1fb-7dc99c3bf433",
              "is_primary": 1,
              "name": "",
              "profile": {
                "model": "gpt-5.6-luna",
                "name": "CI Fixup"
              },
              "started_at": "2026-09-06 06:37:19.510318271+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-06 08:46:10.548844609+00:00",
              "workspace_path": "/data/tasks/preserve-unread-queu_ofb2j8xg"
            },
            {
              "agent_profile_id": "bd2c30cb-f2b6-4202-9a9b-0212632c15fe",
              "error_message": "",
              "id": "fb3e5dd8-452b-4604-bd38-6c0ba9844d98",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-sol",
                "name": "Spec"
              },
              "started_at": "2026-09-05 04:58:22.910274115+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-06 06:37:20.412715914+00:00",
              "workspace_path": "/data/tasks/preserve-unread-queu_ofb2j8xg/kdlbs-kandev"
            }
          ]
        },
        "next_action": "After #3377 is canonical, integrate current main, fix bounded retention/tombstone semantics, rerun fresh Review and distinct QA, and open the real upstream delivery PR.",
        "deterministic_resume_trigger": "ca015838/#3377 reviewed, merged, and available on canonical base.",
        "fallback": "Preserve fork PR #15 as evidence only; do not repair/merge its fork preview or duplicate queue storage.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": {
        "blocked_by": [
          {
            "blocker_task_id": "ca015838-e5cf-4294-b3bb-9c50576a5fe6",
            "state": "REVIEW",
            "title": "Add guarded queue claim and routine wake coalescing",
            "workflow_step_id": "89985050-d740-4421-bbbe-4aa018d8c7ab"
          }
        ],
        "blocks": [
          {
            "state": "SCHEDULING",
            "task_id": "b8fc206c-9e3f-4497-9ac3-3b62593da258",
            "title": "Rotate Coordinator sessions before context exhaustion",
            "workflow_step_id": "89985050-d740-4421-bbbe-4aa018d8c7ab"
          }
        ],
        "parent_id": ""
      },
      "pending_moves": []
    },
    {
      "task_id": "8a182e40-d99c-42e9-b9be-1f8f78cf8388",
      "title": "Repair standalone execution port-pool exhaustion",
      "column": "Spec",
      "state": "FAILED",
      "owner": "Coordinator/platform runtime",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Fresh read-only lane/session/provider/relations inspection completed; no mutation.",
      "next_action": "On first verified free allocation, start this Spec owner first to diagnose and repair allocation/reclamation; then release dependent restarts.",
      "session_health": {
        "counts": {
          "FAILED": 1
        },
        "active_ids": [],
        "latest": {
          "id": "d0b7f9c7-7cab-4b88-baf0-e81b700b258c",
          "state": "FAILED",
          "agent_profile_id": "bd2c30cb-f2b6-4202-9a9b-0212632c15fe",
          "model": "gpt-5.6-sol",
          "updated_at": "2026-09-14 22:45:50.177897305+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [],
      "pr_gate": [],
      "blocker_or_gate": "Standalone capacity [41001,41100] is exhausted; configured session failed before inference."
    },
    {
      "task_id": "8f8a784d-92ea-421f-a368-154ef915fe4e",
      "title": "Register task runtimes with source broker",
      "column": "ToDeploy",
      "state": "REVIEW",
      "owner": "Human",
      "health": "waiting",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "STATE: READY_FOR_HUMAN_TEST  TEST_RUNTIME: NONE — deterministic tests and static checks fully cover the changed broker policy; no service or runtime is required.  Verified:  - HEAD and remote: `6e3595efb1a6053bb3543bf41fd7fd7eaa22ceb4` - Clean worktree - Broker and client tests passed - Compilation, `tabnanny`, and diff checks passed  Review focus:  - Run...",
      "next_action": "Human deploys runtime source-broker registration; Coordinator verifies rollout receipt.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 1,
          "COMPLETED": 1,
          "CANCELLED": 4
        },
        "active_ids": [],
        "latest": {
          "id": "39a616cd-7a6f-4a0c-9061-324cedd55fae",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-06 08:13:11.563570012+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 1,
          "state": "merged",
          "draft": 0,
          "head": "6e3595efb1a6053bb3543bf41fd7fd7eaa22ceb4",
          "checks": "success",
          "passing": 1,
          "total": 1,
          "threads": 0
        }
      ],
      "blocker_or_gate": "ToDeploy; linked PR #1 is merged and checks green."
    },
    {
      "task_id": "92535de6-7507-473c-b292-e69516d2434c",
      "title": "Design executor-owned native sandbox",
      "column": "Done",
      "state": "COMPLETED",
      "owner": "Coordinator terminal tracking",
      "health": "terminal",
      "last_checked": "2026-09-15T00:11:12Z",
      "last_action": "Authoritative late reconciliation verified Done/COMPLETED, clean worktree, complete preserved prototype streams, zero pending moves/active sessions; pre-final CLEANUP PENDING messages are stale and must not reopen the task.",
      "next_action": "Closed-ledger retention and normal Done archive timer; restore only from verified preservation manifests for a separately authorized implementation.",
      "session_health": {
        "counts": {
          "FAILED": 2,
          "COMPLETED": 2,
          "WAITING_FOR_INPUT": 1
        },
        "active_ids": [],
        "latest": {
          "id": "965ef214-2b76-4102-a049-ba86b13c48ff",
          "state": "FAILED",
          "agent_profile_id": "c151363f-a48d-4955-b669-cab94470d04a",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 23:26:05.717277323+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [],
      "pr_gate": [],
      "blocker_or_gate": "No open delivery or cleanup obligation; stale pre-final session messages are superseded.",
      "terminal_integrity": {
        "status": "terminal",
        "receipt": "Done/COMPLETED; task worktree clean; tracked patch and untracked archive preservation streams and reconstruction hashes verified; no PR, unique unpreserved work, pending move, active session, child, or cleanup obligation. Stale pre-final messages do not reopen."
      }
    },
    {
      "task_id": "9349b6e5-a167-4d88-af14-cb355015e3dd",
      "title": "Allow coordinator relation inspection",
      "column": "CI Fixup",
      "state": "REVIEW",
      "owner": "Coordinator",
      "health": "waiting",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "CI Fixup remains blocked.  - Exact head and clean worktree preserved: `b44ec6473`. - No maintainer rerun or head change occurred. - Provider recheck failed with GitHub GraphQL rate limit exhaustion. - No retry, source commit, duplicate contact, or stale evidence reuse was performed.  Next check is gated on the maintainer rerun, a head change, or new revie...",
      "next_action": "On provider reset/head or run change, start one Luna owner for exact CI census; no duplicate maintainer contact.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 6,
          "COMPLETED": 16
        },
        "active_ids": [],
        "latest": {
          "id": "364cc979-268f-4b42-a386-b3e5afdf984a",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 23:09:38.580838075+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 2841,
          "state": "open",
          "draft": 1,
          "head": "b44ec64734f4d6aab839b675eb2893b7eac38a04",
          "checks": "failure",
          "passing": 51,
          "total": 53,
          "threads": 0
        }
      ],
      "blocker_or_gate": "No active owner; exact head b44ec6473 awaits GitHub quota/rerun evidence."
    },
    {
      "task_id": "957da1cb-063b-4c2e-b406-6d04ad158fb9",
      "title": "Reuse workspace for additional task sessions",
      "column": "Done",
      "state": "REVIEW",
      "owner": "Coordinator terminal tracking",
      "health": "terminal",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Terminal integrity is complete.  - Worktree is clean and preserved at `97d980712`. - PR #3501 is merged as squash commit `796bf5853` on `upstream/main`. - Retained checkout regression is present in `upstream/main`. - Relevant `git diff --check` validations pass. - No code, tests, commits, or additional sessions were created. Obsolete model-only hold is cl...",
      "next_action": "Archive on normal Done retention.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 2,
          "COMPLETED": 13
        },
        "active_ids": [],
        "latest": {
          "id": "2c5243b6-e046-4fbc-b82b-1cbef6e8a835",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 02:56:03.815451206+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 2843,
          "state": "merged",
          "draft": null,
          "head": "",
          "checks": "success",
          "passing": 1,
          "total": 1,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Merged #2843; clean delivery and runtime cleanup passed.",
      "terminal_integrity": {
        "status": "terminal",
        "persisted_receipt": {
          "id": "957da1cb-063b-4c2e-b406-6d04ad158fb9",
          "status": "terminal",
          "receipt": "Merged PR #2843; delivery, clean/preservation, and runtime cleanup receipt passed."
        }
      }
    },
    {
      "task_id": "96e27238-8b7d-476a-8c70-b8da0abae935",
      "title": "Fix stale plugin-hook docs and template rename checklist",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "kdlbs/kandev-plugin-template maintainer with Actions approval authority",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "On maintainer approval/rerun or review activity, refresh exact-head results and route Review/QA or focused Work for a branch-owned failure.",
      "blocked_record": {
        "previous_workflow_step": "Work",
        "exact_blocker_or_dependency": "Template PR #4 at f616642516372091f1a0aa6239bb693d3eb2839d still lacks successful maintainer-approved CI/Build execution after the external-contributor gate; available account cannot approve/rerun.",
        "blocker_owner": "kdlbs/kandev-plugin-template maintainer with Actions approval authority",
        "preservation_receipt": {
          "branch": "feature/fix-stale-plugin-hoo-54w",
          "extra": "template fork branch fix/stale-plugin-hook-docs-and-release-id at f616642516372091f1a0aa6239bb693d3eb2839d",
          "head": "91e36603f33c0b004815e8ba6ec6c2163d7c3fd9",
          "runtime_data": "none",
          "worktree": "/data/tasks/fix-stale-plugin-hoo_wb6/kandev-source"
        },
        "owner_session_health": {
          "active_count": 0,
          "counts": {
            "COMPLETED": 4,
            "WAITING_FOR_INPUT": 1
          },
          "newest": [
            {
              "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
              "error_message": "",
              "id": "3990717f-3976-467b-8b30-a15065c1a1c1",
              "is_primary": 1,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker"
              },
              "started_at": "2026-08-27 19:38:02.728942705+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-08 04:10:26.568612141+00:00",
              "workspace_path": "/data/tasks/fix-stale-plugin-hoo_wb6/kandev-source"
            },
            {
              "agent_profile_id": "5d7135f9-8b98-4168-856d-1b495e19b481",
              "error_message": "",
              "id": "a462cd32-76ef-4df6-a2f8-8a080545791e",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Terra 5.6"
              },
              "started_at": "2026-08-18 02:06:41.260415133+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-08-27 19:38:02.740740032+00:00",
              "workspace_path": "/data/tasks/fix-stale-plugin-hoo_wb6/kandev-source"
            },
            {
              "agent_profile_id": "06f0a558-84be-486e-a3ea-941b679dc87a",
              "error_message": "",
              "id": "6a762d99-dcde-4bfb-b61d-bb274ebbba3d",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "sonnet",
                "name": "CI Fixup"
              },
              "started_at": "2026-08-05 22:07:43.530085972+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-08-27 19:38:02.731248765+00:00",
              "workspace_path": "/data/tasks/fix-stale-plugin-hoo_wb6/kandev-source"
            },
            {
              "agent_profile_id": "d05f88ca-4699-43c5-a558-70df3df45ec2",
              "error_message": "",
              "id": "21800fc1-67cb-4589-ba4f-a9fc0c44f0bf",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "opus[1m]",
                "name": "Review"
              },
              "started_at": "2026-08-05 21:19:22.284320151+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-08-27 19:38:02.731248765+00:00",
              "workspace_path": "/data/tasks/fix-stale-plugin-hoo_wb6/kandev-source"
            },
            {
              "agent_profile_id": "3e3c9eca-7dd9-4dbf-9cf9-82d97fc935d3",
              "error_message": "",
              "id": "66bfd2c7-cb9b-4c3d-8829-ae51340318fa",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "sonnet",
                "name": "Starter"
              },
              "started_at": "2026-08-05 21:19:17.902455589+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-08-27 19:38:02.731248765+00:00",
              "workspace_path": ""
            }
          ]
        },
        "next_action": "On maintainer approval/rerun or review activity, refresh exact-head results and route Review/QA or focused Work for a branch-owned failure.",
        "deterministic_resume_trigger": "New CI/Build attempt, review decision, or PR head change on template PR #4.",
        "fallback": "Do not duplicate approval request; deferred release.yml work remains separate/out of scope.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": {
        "blocked_by": [],
        "blocks": [],
        "parent_id": ""
      },
      "pending_moves": []
    },
    {
      "task_id": "9e67c426-1300-46ef-a00f-e5603791212d",
      "title": "Plan coordinator plugin architecture",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "replacement task 1e46d457 and Coordinator; #3155 capability owner for durable regression",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "When replacement delivery finishes, re-evaluate PR #2793 for formal supersession/closure and terminally disposition this source carrier; retain pending-row absence receipt.",
      "blocked_record": {
        "previous_workflow_step": "Work",
        "exact_blocker_or_dependency": "Monolithic architecture carrier is superseded by active replacement task 1e46d457-6869-4750-bf97-4640a8df3b68 and PR #2793 remains a conflicted draft baseline. Both historical pending-move rows are now proven absent in live DB, clearing that sub-blocker, but replacement delivery is still IN_PROGRESS with one RUNNING session, so terminal disposition is premature.",
        "blocker_owner": "replacement task 1e46d457 and Coordinator; #3155 capability owner for durable regression",
        "preservation_receipt": {
          "branch": "feature/create-a-plugin-that-kch",
          "extra": "origin/backup/create-a-plugin-that-kch-local-1 same head; 41 ahead/361 behind old remote; untracked tempartifacts/app paths untouched",
          "head": "ee41197009dd00331b74ab6a1b9c1a66292f2c20",
          "runtime_data": "none",
          "worktree": "/data/tasks/create-a-plugin-that_wtf60hhd/kandev-source"
        },
        "owner_session_health": {
          "active_count": 0,
          "counts": {
            "COMPLETED": 9,
            "FAILED": 5,
            "WAITING_FOR_INPUT": 5
          },
          "newest": [
            {
              "agent_profile_id": "5b1dc511-64f7-448a-aa2c-5bf72e81f9e9",
              "error_message": "",
              "id": "d770156a-416b-4134-9992-99b681782f37",
              "is_primary": 1,
              "name": "",
              "profile": {
                "model": "savoirfairelinux/DeepInfra/deepseek-ai%2FDeepSeek-V4-Flash-0731",
                "name": "DI small"
              },
              "started_at": "2026-09-14 04:11:48.804362411+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-14 04:13:00.067304194+00:00",
              "workspace_path": "/data/tasks/create-a-plugin-that_wtf60hhd/kandev-source"
            },
            {
              "agent_profile_id": "38b00822-c449-4f68-8e8a-034af450dbc1",
              "error_message": "",
              "id": "28e52f66-9f2c-44f8-8c7f-4eeaa05c8681",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "savoirfairelinux/DeepInfra/zai-org%2FGLM-5.3",
                "name": "GLM-5.3"
              },
              "started_at": "2026-09-14 03:09:30.355167868+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-14 04:11:59.638631371+00:00",
              "workspace_path": "/data/tasks/create-a-plugin-that_wtf60hhd/kandev-source"
            },
            {
              "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
              "error_message": "failed to resume session: validate launch workspace repository \"***\": required worktree is unavailable for reuse",
              "id": "6ce88dad-4143-40b8-a729-782d00354c99",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker"
              },
              "started_at": "2026-08-27 19:38:02.841420417+00:00",
              "state": "FAILED",
              "updated_at": "2026-09-14 04:11:53.97818013+00:00",
              "workspace_path": "/data/tasks/create-a-plugin-that_wtf60hhd/kandev-source"
            },
            {
              "agent_profile_id": "ab57f00e-ed8d-4205-bada-8be63fc4cd7d",
              "error_message": "failed to resume session: validate launch workspace repository \"***\": required worktree is unavailable for reuse",
              "id": "08558ba9-71d4-4f98-91d0-2418c583ebda",
              "is_primary": 0,
              "name": "human-qa-evidence",
              "profile": {
                "model": "gpt-5.5",
                "name": "Review"
              },
              "started_at": "2026-08-20 12:37:28.017270276+00:00",
              "state": "FAILED",
              "updated_at": "2026-09-14 04:11:53.97818013+00:00",
              "workspace_path": "/data/tasks/create-a-plugin-that_wtf60hhd/kandev-source"
            },
            {
              "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
              "error_message": "",
              "id": "c170ad39-5465-458c-8908-fd5b0787c1be",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-luna",
                "name": "CI Fixup"
              },
              "started_at": "2026-08-20 09:03:29.272095187+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-14 04:11:53.97818013+00:00",
              "workspace_path": "/data/tasks/create-a-plugin-that_wtf60hhd/kandev-source"
            }
          ]
        },
        "next_action": "When replacement delivery finishes, re-evaluate PR #2793 for formal supersession/closure and terminally disposition this source carrier; retain pending-row absence receipt.",
        "deterministic_resume_trigger": "Replacement task 1e46d457 reaches verified terminal delivery, or Coordinator proves all replacement obligations migrated and closes the obsolete carrier.",
        "fallback": "Do not contact stale sessions, touch PR #2793, move, clean, or rewrite history.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": {
        "blocked_by": [],
        "blocks": [],
        "parent_id": ""
      },
      "pending_moves": []
    },
    {
      "task_id": "9ee4be81-aa98-4e4d-bdd6-842fd918f00f",
      "title": "Allow scoped fresh CI dispatch",
      "column": "CI Fixup",
      "state": "FAILED",
      "owner": "Coordinator",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "I’m checking the durable plan, recent task messages, and the current repository/provider state first so I can classify the exact-head CI Fixup result without reusing stale evidence. I’ll preserve existing artifacts and only touch code if a reproducible task-owned defect is confirmed.",
      "next_action": "After capacity repair, start one Luna owner; reconcile five threads/current main and PostgreSQL constraint work before routing.",
      "session_health": {
        "counts": {
          "FAILED": 1,
          "WAITING_FOR_INPUT": 5,
          "CANCELLED": 39,
          "COMPLETED": 25
        },
        "active_ids": [],
        "latest": {
          "id": "d1d511e2-a754-44c8-afb6-6d9c0b8a412b",
          "state": "FAILED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 22:44:17.797698225+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3165,
          "state": "open",
          "draft": 0,
          "head": "a199dcd42a187572b52a428ed2fa158ebc1b06bd",
          "checks": "success",
          "passing": 57,
          "total": 57,
          "threads": 5
        }
      ],
      "blocker_or_gate": "Standalone capacity [41001,41100] is exhausted; configured session failed before inference. PR #3165 is green but has five unresolved threads in cached provider state."
    },
    {
      "task_id": "a091649a-79b0-40d6-a84d-84a3dc053e4a",
      "title": "Port AgentConversation Host contract to canonical main",
      "column": "CI Fixup",
      "state": "FAILED",
      "owner": "Coordinator",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Draft PR #3672 now includes the repair-test update at `0d4b730e0`.  - Pushed normally over SSH. - Focused race and repair regressions pass. - Full tagged service tests show only the established git-sandbox failures. - CI has not registered checks for the new head yet; CI Fixup will handle the terminal census.",
      "next_action": "After capacity repair, start one Luna CI owner; terminal green then fresh independent Review and distinct QA.",
      "session_health": {
        "counts": {
          "FAILED": 1,
          "WAITING_FOR_INPUT": 4,
          "COMPLETED": 2
        },
        "active_ids": [],
        "latest": {
          "id": "184a77c9-fe7e-4ae2-8c7f-558a6a9ac1b9",
          "state": "FAILED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 23:40:59.452837553+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3672,
          "state": "open",
          "draft": 1,
          "head": "0d4b730e0726302838c573455842649e17c72916",
          "checks": "pending",
          "passing": 7,
          "total": 7,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Standalone capacity [41001,41100] is exhausted; configured session failed before inference. Fresh PR #3672 head has pending CI."
    },
    {
      "task_id": "a3f02302-12fa-4129-8985-116efb8fed66",
      "title": "Recover workspace reuse inventory mismatches",
      "column": "CI Fixup",
      "state": "FAILED",
      "owner": "Coordinator",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Fresh exact-head CI Fixup completed.  - Head remains `db0118b47…`; worktree and remote are clean and synchronized. - Run `34810899170` is still attempt 1 and failed. - Direct failures are off-diff E2E flakes in Shards 2 and 10; aggregate failures are consequential. - No task-owned defect is reproducible, so no code changes, commit, or push were made. - Ma...",
      "next_action": "After capacity repair and provider activity, start one Luna owner to classify run 34810899170; no duplicate rerun.",
      "session_health": {
        "counts": {
          "FAILED": 2,
          "WAITING_FOR_INPUT": 5,
          "COMPLETED": 17,
          "CANCELLED": 20
        },
        "active_ids": [],
        "latest": {
          "id": "15a6ab88-5900-4ce5-b894-7b35f02fe369",
          "state": "FAILED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 22:44:18.751496205+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3310,
          "state": "open",
          "draft": 1,
          "head": "db0118b473d1ae3e31b1a63263ce625c7d22c5ae",
          "checks": "failure",
          "passing": 49,
          "total": 53,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Standalone capacity [41001,41100] is exhausted; configured session failed before inference. Existing off-diff E2E/admin rerun trigger remains."
    },
    {
      "task_id": "a68df3ae-aaf5-4591-a46d-9d73db62e46d",
      "title": "Coordinator: long-lived board orchestration",
      "column": "Backlogs",
      "state": "IN_PROGRESS",
      "owner": "Coordinator; active session da0761f2-cd4e-44d1-bccc-6f9c1119f534 RUNNING",
      "health": "waiting",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "I’m starting a full board action cycle. I’ll reconcile every live task against the durable ledger, split the inspection into disjoint read-only slices, then serialize any moves or fresh Codex session starts from the consolidated evidence.",
      "next_action": "Reinspect and route from current lane evidence.",
      "session_health": {
        "counts": {
          "RUNNING": 1
        },
        "active_ids": [
          "da0761f2-cd4e-44d1-bccc-6f9c1119f534 RUNNING"
        ],
        "latest": {
          "id": "da0761f2-cd4e-44d1-bccc-6f9c1119f534",
          "state": "RUNNING",
          "agent_profile_id": "ccd6113e-c1bd-4029-9d7d-f36f72272fa5",
          "model": "gpt-5.6-sol",
          "updated_at": "2026-09-14 23:57:12.429850086+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [],
      "blocker_or_gate": "Requires current evidence."
    },
    {
      "task_id": "ae8fc022-5562-4f58-95dc-3dab9d4c179f",
      "title": "Fix tag display and tags box UI",
      "column": "Blocked",
      "state": "FAILED",
      "owner": "Capacity task 8a182e40-d99c-42e9-b9be-1f8f78cf8388, then Coordinator cleanup/retention owner",
      "health": "blocked",
      "last_checked": "2026-09-15T00:21:56.572644741Z",
      "last_action": "Authoritative readback verified Done→Blocked at step 89985050-d740-4421-bbbe-4aa018d8c7ab, pending moves 0 and active sessions 0. Automatic Blocked owner 8cb37243 failed before useful work on standalone port exhaustion; residue was untouched.",
      "next_action": "After one verified free standalone slot, start one configured owner to prove zero live consumers; then record explicit retention/expiry or perform only separately authorized exact cleanup with a receipt.",
      "blocked_record": {
        "previous_workflow_step": "Done",
        "exact_blocker_or_dependency": "Unconsumed approximately 2.7GB kandev-qa-9683 residue has no proven live consumer, cleanup owner, retention decision, expiry, or removal receipt; standalone capacity exhaustion prevents a fresh verification owner.",
        "blocker_owner": "Capacity task 8a182e40-d99c-42e9-b9be-1f8f78cf8388, then Coordinator-designated cleanup/retention owner",
        "preservation_receipt": "Merged implementation delivery is contained and terminal; kandev-qa-9683 residue remains untouched and unarchived pending consumer/ownership proof. No cleanup mutation was performed.",
        "owner_session_health": "pending_moves=0; active=0; automatic Blocked session 8cb37243-044c-4c49-bb9c-fb6cc5fe9557, profile 8a033819-d149-4dfc-9ab1-0c2f2a3911b5, FAILED terminal before useful work: failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)",
        "next_action": "After one verified free standalone slot, start one configured owner to prove zero live consumers; then record explicit retention/expiry or perform only separately authorized exact cleanup with a receipt.",
        "deterministic_resume_trigger": "One verified free standalone allocation in 41001-41100.",
        "fallback": "Preserve the merged receipt and kandev-qa-9683 residue untouched and unarchived; do not infer zero consumers or delete without explicit authority.",
        "cleared": false,
        "last_checked": "2026-09-15T00:21:56.572644741Z"
      },
      "pending_moves": [],
      "tags": [
        "agent at-risk: Blocked: preserve unconsumed ~2.7GB kandev-qa-9683 residue. After capacity task 8a182e40 frees a slot, prove zero consumers, then assign explicit retention/expiry or authorized cleanup."
      ],
      "physical_step_id": "89985050-d740-4421-bbbe-4aa018d8c7ab",
      "active_sessions": 0
    },
    {
      "task_id": "af3d7a12-5fc2-408e-ab36-bb4bba6fed22",
      "title": "Manage task PR and MR links via MCP",
      "column": "Done",
      "state": "REVIEW",
      "owner": "Coordinator terminal tracking",
      "health": "terminal",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Done audit recorded in the task plan.  - PR #3506 merged; task link intact. - Worktree clean; no unpushed local commits. - No task-specific runtime or data artifacts remain. - Blocker: pushed commits `2ba884ba5` and `bd92d72aa` are task-owned but absent from merged commit `262ecdf2`; Coordinator disposition required.",
      "next_action": "Archive on normal Done retention.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 4,
          "COMPLETED": 10
        },
        "active_ids": [],
        "latest": {
          "id": "fe853dcd-0aaa-4fc5-be03-4c00a58b3585",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 18:21:09.946687802+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3506,
          "state": "merged",
          "draft": 0,
          "head": "bd92d72aa1c25eb875982c9d0c47bbc83f01d1bf",
          "checks": "success",
          "passing": 54,
          "total": 54,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Merged #3506; post-merge commits are content-contained by main and no unique work remains.",
      "terminal_integrity": {
        "status": "terminal",
        "persisted_receipt": {
          "id": "af3d7a12-5fc2-408e-ab36-bb4bba6fed22",
          "status": "terminal",
          "receipt": "Merged PR #3506; 2ba884ba5 and bd92d72aa content contained by main 262ecdf270; no unique work."
        }
      }
    },
    {
      "task_id": "afdb2ef3-06ca-4cd5-a074-c4e691679da9",
      "title": "Provision isolated Coordinator plugin end-to-end QA runtime",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "a091649a/#3672 delivery owner, standalone port-capacity repair, then canonical Host deployment",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "Restore standalone session capacity, staff a091 CI Fixup, deliver/deploy canonical Host contract, then move this card to QA for one fresh isolated package smoke/UI run.",
      "blocked_record": {
        "previous_workflow_step": "QA",
        "exact_blocker_or_dependency": "Canonical Host still lacks a deployed AgentConversation Host contract required by the immutable Coordinator plugin. Delivery task a091649a/PR #3672 is now CI Fixup FAILED with no active session because its launch hit standalone port exhaustion [41001,41100].",
        "blocker_owner": "a091649a/#3672 delivery owner, standalone port-capacity repair, then canonical Host deployment",
        "preservation_receipt": {
          "branch": "plugin source 5bfdbcf7d9608d1210453f95ebfc8f66c3179225",
          "extra": "package packages/kandev-plugin-coordinator-0.1.0-5bfdbcf7.tar.gz sha256 fc742be569bff2e27f967a0e11949a24f652c4f43809f32a240b04c062d76044; immutable receipt ca4f38ef...",
          "head": "5bfdbcf7d9608d1210453f95ebfc8f66c3179225",
          "runtime_data": "no live runtime; saved smoke/UI contract only",
          "worktree": "/data/repos/workspaces/2e62401b-5ffe-4050-bc1b-d49ea5d5dbcd/github/kdlbs/kandev"
        },
        "owner_session_health": {
          "active_count": 0,
          "counts": {
            "WAITING_FOR_INPUT": 1
          },
          "newest": [
            {
              "agent_profile_id": "bd2c30cb-f2b6-4202-9a9b-0212632c15fe",
              "error_message": "",
              "id": "c66159ec-9746-4485-9daf-8e757286b0ba",
              "is_primary": 1,
              "name": "",
              "profile": {
                "model": "gpt-5.6-sol",
                "name": "Spec"
              },
              "started_at": "2026-08-30 04:36:43.038107816+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-14 05:42:05.522735357+00:00",
              "workspace_path": "/data/repos/workspaces/2e62401b-5ffe-4050-bc1b-d49ea5d5dbcd/github/kdlbs/kandev"
            }
          ]
        },
        "next_action": "Restore standalone session capacity, staff a091 CI Fixup, deliver/deploy canonical Host contract, then move this card to QA for one fresh isolated package smoke/UI run.",
        "deterministic_resume_trigger": "Canonical Host build containing Ensure/Dispatch/Delete AgentConversation plus catalog refresher is deployed and task execution capacity is available.",
        "fallback": "Preserve immutable package and evidence; do not use #3377 or upstream #451 as false dependencies.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": {
        "blocked_by": [],
        "blocks": [],
        "parent_id": "a68df3ae-aaf5-4591-a46d-9d73db62e46d"
      },
      "pending_moves": []
    },
    {
      "task_id": "b007bb76-841e-4243-a251-c4f87a1ed1e4",
      "title": "Fix PR-watch amplification, task-status, and unbounded",
      "column": "CI Fixup",
      "state": "FAILED",
      "owner": "Coordinator",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "The conflict is confined to the PR-watch branch-resolution interface and related tests, plus the GitHub event-handler additions. I preserved the newer session-scoped `ResolveBranchForWatch` contract from `main`, retained this PR’s repository/multi-branch reconciliation helpers, and confirmed no conflict markers or staged whitespace errors remain. I’m now ...",
      "next_action": "After capacity repair, start one Luna owner only if pushed current head is proven; otherwise route preserved local repair to Work.",
      "session_health": {
        "counts": {
          "FAILED": 1,
          "WAITING_FOR_INPUT": 7,
          "COMPLETED": 20
        },
        "active_ids": [],
        "latest": {
          "id": "7ef06247-9891-4740-b3b9-a5d59dc43c03",
          "state": "FAILED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 22:44:19.760694269+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3319,
          "state": "open",
          "draft": 0,
          "head": "ddc0c266b64b32f5ae6d97eeac921a0784390e6f",
          "checks": "failure",
          "passing": 54,
          "total": 57,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Standalone capacity [41001,41100] is exhausted; configured session failed before inference. Latest Work turn began current-main conflict reconciliation."
    },
    {
      "task_id": "b74833e7-a05f-4cdf-81cf-db5b4c02f368",
      "title": "Make managed task worktrees Git-writable",
      "column": "Done",
      "state": "REVIEW",
      "owner": "Coordinator terminal tracking",
      "health": "anomalous",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Terminal integrity verification passed.  - Worktree is clean at `9f71cb006`; no staged, unstaged, or untracked task changes. - Umbrella PR [#3242](https://github.com/kdlbs/kandev/pull/3242) is closed and unmerged at `9a6f28293`. - C1 PR [#3496](https://github.com/kdlbs/kandev/pull/3496) remains open and draft at `5504448a57da825d279adcc57170a0a9b252b4da`....",
      "next_action": "Reconcile/remove obsolete dependency edge if 212a no longer requires this terminal carrier; preserve #3496 reference.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 5,
          "COMPLETED": 13
        },
        "active_ids": [],
        "latest": {
          "id": "3e1790eb-8f65-4226-8400-75b864971ca3",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 20:20:48.81510454+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3242,
          "state": "closed",
          "draft": 0,
          "head": "9a6f28293b4345dcb30bbdbc7eee4455e5b1902b",
          "checks": "pending",
          "passing": 35,
          "total": 35,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Umbrella is terminal/superseded, but a Done blocker edge still points to live blocked task 212a68ce.",
      "terminal_integrity": {
        "status": "anomalous",
        "persisted_receipt": {
          "id": "b74833e7-a05f-4cdf-81cf-db5b4c02f368",
          "status": "terminal",
          "receipt": "Closed PR #3242 at 9a6f28293b4345dcb30bbdbc7eee4455e5b1902b and draft reference #3496 at 5504448a57da825d279adcc57170a0a9b252b4da preserved; successor design task owns future work."
        }
      }
    },
    {
      "task_id": "b8fc206c-9e3f-4497-9ac3-3b62593da258",
      "title": "Rotate Coordinator sessions before context exhaustion",
      "column": "Blocked",
      "state": "SCHEDULING",
      "owner": "86c8b47e then ca015838 delivery owners; Coordinator",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "After 86c terminal delivery, move to Work before starting exactly one new configured implementation session using the exact dependency contract.",
      "blocked_record": {
        "previous_workflow_step": "newly created directly in Blocked",
        "exact_blocker_or_dependency": "Required dependency 86c8b47e has not delivered queue-preserving session cleanup; ca015838/#3377 beneath it is also undelivered. Current Host still lacks authoritative cached-token telemetry and atomic queue-preserving primary handoff.",
        "blocker_owner": "86c8b47e then ca015838 delivery owners; Coordinator",
        "preservation_receipt": {
          "branch": null,
          "extra": "approved plan plus deferred launch only; failed reuse sessions contain no implementation",
          "head": null,
          "runtime_data": "no branch, commit, PR, runtime, data, or artifact",
          "worktree": null
        },
        "owner_session_health": {
          "active_count": 0,
          "counts": {
            "FAILED": 2
          },
          "newest": [
            {
              "agent_profile_id": "ce9f96f7-4434-4729-b23b-926b4b72f417",
              "error_message": "workspace reuse is unsafe: canonical workspace repository inventory has no matching entry for repository \"***\" branch \"main\"",
              "id": "c0d09731-8fb6-4f7b-8cf9-92a1f1ebb561",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker-claude"
              },
              "started_at": "2026-09-06 08:06:22.247500687+00:00",
              "state": "FAILED",
              "updated_at": "2026-09-06 08:06:22.271955479+00:00",
              "workspace_path": ""
            },
            {
              "agent_profile_id": "ce9f96f7-4434-4729-b23b-926b4b72f417",
              "error_message": "workspace reuse is unsafe: canonical workspace repository inventory has no matching entry for repository \"***\" branch \"main\"",
              "id": "fcb1771c-de82-4975-9bb6-936de9c703bd",
              "is_primary": 1,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker-claude"
              },
              "started_at": "2026-09-06 00:35:10.742762952+00:00",
              "state": "FAILED",
              "updated_at": "2026-09-06 00:35:10.758553326+00:00",
              "workspace_path": ""
            }
          ]
        },
        "next_action": "After 86c terminal delivery, move to Work before starting exactly one new configured implementation session using the exact dependency contract.",
        "deterministic_resume_trigger": "86c8b47e reaches verified terminal delivery and its queue-preserving lifecycle is available on the base.",
        "fallback": "Keep deferred launch inert; never reuse failed sessions or implement duplicate queue storage.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": {
        "blocked_by": [
          {
            "blocker_task_id": "86c8b47e-e7a5-4693-8e11-dce08899a0bf",
            "state": "REVIEW",
            "title": "Preserve unread queue on session deletion",
            "workflow_step_id": "89985050-d740-4421-bbbe-4aa018d8c7ab"
          }
        ],
        "blocks": [],
        "parent_id": "a68df3ae-aaf5-4591-a46d-9d73db62e46d"
      },
      "pending_moves": []
    },
    {
      "task_id": "bdc56ccb-b1ea-4f22-a1e0-e81eac5fa06e",
      "title": "Fix plugin possible_values decode for Redmine 6.0",
      "column": "Done",
      "state": "COMPLETED",
      "owner": "Coordinator terminal tracking",
      "health": "terminal",
      "last_checked": "2026-09-15T00:11:12Z",
      "last_action": "CLOSE RESULT: COMPLETE  Verified:  - PR #8 merged at accepted head `2192918e13fdeb8a0641eb240cc27f8286cb4da5`. - Merge commit: `5f2d10ad76b6a135aee74bdaf2e6430b2d1403ed`. - Exact-head CI checks all passed. - Accepted head is preserved in `origin/main`. - All three task worktrees are clean. - No child tasks or uncommitted implementation remain. - All workt...",
      "next_action": "Archive on normal Done retention; preserve artifacts.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 4,
          "COMPLETED": 2
        },
        "active_ids": [],
        "latest": {
          "id": "66c51f62-dae8-4d97-ad2d-2009e756c032",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 22:15:07.11018398+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [],
      "blocker_or_gate": "Done/COMPLETED; PR #8 accepted 2192918e, merged 5f2d10ad, byte-identical in b843ce; all worktrees clean and no open obligation.",
      "terminal_integrity": {
        "status": "terminal",
        "receipt": "PR #8 accepted 2192918e13fdeb8a0641eb240cc27f8286cb4da5, merged as 5f2d10ad76b6a135aee74bdaf2e6430b2d1403ed and byte-identically contained in origin/main b843ce5345e8a11ade7f0d4d33386c746465a049; checks and three worktrees clean; no children, relations, unpushed delivery, active owner, or cleanup obligation; artifacts preserved."
      }
    },
    {
      "task_id": "c642d57a-5a24-48ca-8f85-57d31115eeb5",
      "title": "Prevent stale sessions blocking workflow",
      "column": "Work",
      "state": "REVIEW",
      "owner": "Coordinator",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Diagnosis complete. The standalone pool is host-wide, not related to Docker networking.  - Exact repair owner already exists: task `8a182e40-d99c-42e9-b9be-1f8f78cf8388`, “Repair standalone execution port-pool exhaustion.” - `92535de6` attempted instance `867c3eba…` at `22:44:05Z` and failed before ACP startup. Unrelated launches and resumes failed simult...",
      "next_action": "After 8a capacity repair, start one c06/Terra Work owner for exact current-head remediation/CI; do not wake stopped predecessors.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 15,
          "COMPLETED": 9,
          "CANCELLED": 1
        },
        "active_ids": [],
        "latest": {
          "id": "7fe710cf-79bd-44eb-aee9-2d9d5a67f538",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 22:48:31.092409079+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 2909,
          "state": "open",
          "draft": 1,
          "head": "caee717b7c9d9c120e8dcbfcc77c7b08bfc9b697",
          "checks": "failure",
          "passing": 31,
          "total": 53,
          "threads": 0
        }
      ],
      "blocker_or_gate": "No active owner; latest turn isolated host-wide standalone-port exhaustion and preserved PR #2909."
    },
    {
      "task_id": "ca015838-e5cf-4294-b3bb-9c50576a5fe6",
      "title": "Add guarded queue claim and routine wake coalescing",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "credential-lease provisioning/platform delivery owner, then upstream PR owner",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "When a matching lease and execution capacity exist, start fresh Work owner, normal-push local head, reconcile current main, and run fresh CI/Review/QA plus deployed census acceptance.",
      "blocked_record": {
        "previous_workflow_step": "Work",
        "exact_blocker_or_dependency": "Local successor 37ca515b0c8fd94cc98b38f898a9335765378ac2 (including fresh current/predecessor census callability coverage) cannot be delivered because the GitHub credential lease does not match the PR #3377 fork/ref. Provider head remains older c990b51cb8dc758f35a702ee6ee017dd1c593c26. Model-only #3473 gate is suspended and is not a blocker.",
        "blocker_owner": "credential-lease provisioning/platform delivery owner, then upstream PR owner",
        "preservation_receipt": {
          "branch": "feature/add-guarded-queue-cl-sls",
          "extra": "clean local worktree; provider PR #3377 remains on c990b51cb8dc758f35a702ee6ee017dd1c593c26",
          "head": "37ca515b0c8fd94cc98b38f898a9335765378ac2",
          "runtime_data": "none",
          "worktree": "/data/tasks/add-guarded-queue-cl_sf70tyvs/kdlbs-kandev"
        },
        "owner_session_health": {
          "active_count": 0,
          "counts": {
            "COMPLETED": 8,
            "WAITING_FOR_INPUT": 4
          },
          "newest": [
            {
              "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
              "error_message": "",
              "id": "fe0512a7-d4e6-405b-8741-d2d42f8ebae8",
              "is_primary": 0,
              "name": "semantic-incarnation-repair",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker"
              },
              "started_at": "2026-09-09 00:58:28.91834739+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-09 01:53:49.416099286+00:00",
              "workspace_path": "/data/tasks/add-guarded-queue-cl_sf70tyvs/kdlbs-kandev"
            },
            {
              "agent_profile_id": "ab57f00e-ed8d-4205-bada-8be63fc4cd7d",
              "error_message": "",
              "id": "9210c156-0f56-4eba-b119-881c40615aa7",
              "is_primary": 0,
              "name": "independent-review-c990b51c",
              "profile": {
                "model": "gpt-5.5",
                "name": "Review"
              },
              "started_at": "2026-09-09 00:25:27.749047664+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-09 00:30:49.052886729+00:00",
              "workspace_path": "/data/tasks/add-guarded-queue-cl_sf70tyvs/kdlbs-kandev"
            },
            {
              "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
              "error_message": "",
              "id": "260b4ddd-841f-40ec-9bd8-39535052dcc6",
              "is_primary": 1,
              "name": "complete-incarnation-adaptation",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker"
              },
              "started_at": "2026-09-09 00:11:15.832280632+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-14 18:32:31.685287357+00:00",
              "workspace_path": "/data/tasks/add-guarded-queue-cl_sf70tyvs/kdlbs-kandev"
            },
            {
              "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
              "error_message": "",
              "id": "77a3446f-1954-4c87-ac1d-5735d6db517d",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker"
              },
              "started_at": "2026-09-08 22:34:02.100163741+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-09 00:20:00.121686872+00:00",
              "workspace_path": "/data/tasks/add-guarded-queue-cl_sf70tyvs/kdlbs-kandev"
            },
            {
              "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
              "error_message": "",
              "id": "29501e9b-7ff9-47be-9f5e-69e0b4bb28d9",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-luna",
                "name": "CI Fixup"
              },
              "started_at": "2026-09-08 16:18:01.868960537+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-09 00:20:00.121686872+00:00",
              "workspace_path": "/data/tasks/add-guarded-queue-cl_sf70tyvs/kdlbs-kandev"
            }
          ]
        },
        "next_action": "When a matching lease and execution capacity exist, start fresh Work owner, normal-push local head, reconcile current main, and run fresh CI/Review/QA plus deployed census acceptance.",
        "deterministic_resume_trigger": "Verified yattdev/kandev credential lease for exact fork/ref and available standalone execution capacity.",
        "fallback": "No duplicate credential attempt, cross-workspace inspection, force-push, or provider contact.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": {
        "blocked_by": [],
        "blocks": [
          {
            "state": "REVIEW",
            "task_id": "428d343e-c768-4bce-a5e7-efd3b10f363f",
            "title": "Plugin fenced runtime and scheduler",
            "workflow_step_id": "89985050-d740-4421-bbbe-4aa018d8c7ab"
          },
          {
            "state": "REVIEW",
            "task_id": "86c8b47e-e7a5-4693-8e11-dce08899a0bf",
            "title": "Preserve unread queue on session deletion",
            "workflow_step_id": "89985050-d740-4421-bbbe-4aa018d8c7ab"
          }
        ],
        "parent_id": ""
      },
      "pending_moves": []
    },
    {
      "task_id": "cfccac4a-1c80-403f-b284-a673a26a321a",
      "title": "Fix shared task-switch E2E failure",
      "column": "PR",
      "state": "FAILED",
      "owner": "Coordinator",
      "health": "anomalous",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Merged current `origin/main` locally into the repair branch at `9ffc51d7`; the two-file E2E diff is unchanged and clean.  Fresh focused verification passed:  - Desktop Chromium: 1 passed, 14.9s - Mobile Chromium: 1 passed, 13.0s - ESLint and E2E sleep ratchet passed  Publishing is blocked because this environment lacks a credential lease for `yattdev/kand...",
      "next_action": "Reconcile/cancel or allow the exact armed move first; after port plus credential recovery start one c151 PR owner and publish the preserved successor without duplicate PR.",
      "session_health": {
        "counts": {
          "FAILED": 2,
          "WAITING_FOR_INPUT": 3,
          "COMPLETED": 2,
          "CANCELLED": 6
        },
        "active_ids": [],
        "latest": {
          "id": "23105cc8-3714-4244-b4e4-9498f6d01d70",
          "state": "FAILED",
          "agent_profile_id": "c151363f-a48d-4955-b669-cab94470d04a",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 22:44:05.421679463+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [
        {
          "id": "aeed2cd9-2de4-45db-bcc8-1fa5cc4e7613",
          "session_id": "c30dcee1-a037-45af-b1a3-d0bcca127694",
          "workflow_step_id": "347f3904-5972-44bf-92e8-a9a9a5efb96d",
          "queued_at": "2026-09-14 06:11:45.829548837+00:00",
          "actor": "agent",
          "sender_session_id": "da0761f2-cd4e-44d1-bccc-6f9c1119f534",
          "move_id": "ac438fa2-6352-4830-9156-48b25440c29a"
        }
      ],
      "pr_gate": [
        {
          "number": 3476,
          "state": "open",
          "draft": 1,
          "head": "6876ac7154b7eaa4fae6732da0ad19dc2f7f2ab7",
          "checks": "failure",
          "passing": 41,
          "total": 44,
          "threads": 0
        }
      ],
      "blocker_or_gate": "PR lane is FAILED with one armed pending move; local 9ffc51d7 is tested but push credential is absent."
    },
    {
      "task_id": "e0dd8d19-278c-4d38-aafa-c3e866d92cfb",
      "title": "Fix PR lane profile executing wrong model",
      "column": "Work",
      "state": "REVIEW",
      "owner": "Coordinator",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Current task state is established.  - Current profile: Codex **Worker** (`gpt-5.6-terra`), session `daee0378…`. - Workspace: clean detached `HEAD` at `0ce8992c1235c69035d3edfd08e0a184e539760c`, tracking `yattdev/kandev:feature/fix-pr-lane-profile-bt7`. - PR #3473: open, non-draft, mergeable, but blocked; base is `ba960f973205854733e0dcd9afa355bdda3dddf6`....",
      "next_action": "After capacity repair, start one Work owner to classify exact failures against current main and push only branch-owned remediation.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 4,
          "COMPLETED": 19,
          "CANCELLED": 42
        },
        "active_ids": [],
        "latest": {
          "id": "daee0378-a58f-4eed-ab6d-f5a46bd0351a",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 22:46:45.871016499+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3473,
          "state": "open",
          "draft": 0,
          "head": "0ce8992c1235c69035d3edfd08e0a184e539760c",
          "checks": "failure",
          "passing": 53,
          "total": 57,
          "threads": 0
        }
      ],
      "blocker_or_gate": "No active owner; PR #3473 non-draft but current provider projection has four failing checks."
    },
    {
      "task_id": "e8728906-86de-4a75-960f-9da585485823",
      "title": "Fix plugin task priority persistence",
      "column": "Blocked",
      "state": "REVIEW",
      "owner": "kdlbs/kandev Actions maintainer; scoped fresh-CI capability fallback",
      "health": "blocked",
      "last_checked": "2026-09-14T23:56:41Z",
      "last_action": "Fresh read-only Blocked audit completed; no duplicate contact or mutation.",
      "next_action": "When a new attempt appears, start one fresh configured CI Fixup owner for exact-head census; green then requires fresh Review and distinct QA.",
      "blocked_record": {
        "previous_workflow_step": "CI Fixup",
        "exact_blocker_or_dependency": "PR #3468 exact saved head 973a9d6d367b2c9a50c6ecd0557d70b23817d8b6 remains parked on shared SSH fixture SocketError in run 34197413540; one maintainer rerun request already exists and no new attempt is recorded in task state.",
        "blocker_owner": "kdlbs/kandev Actions maintainer; scoped fresh-CI capability fallback",
        "preservation_receipt": {
          "branch": "feature/fix-plugin-task-prio-w7w",
          "extra": "clean local/fork/PR head; focused race/package/vet/fixture checks passed",
          "head": "973a9d6d367b2c9a50c6ecd0557d70b23817d8b6",
          "runtime_data": "no services or ports",
          "worktree": "/data/tasks/fix-plugin-task-prio_rksfvx9c/kdlbs-kandev"
        },
        "owner_session_health": {
          "active_count": 0,
          "counts": {
            "CANCELLED": 5,
            "COMPLETED": 9,
            "WAITING_FOR_INPUT": 1
          },
          "newest": [
            {
              "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
              "error_message": "",
              "id": "c8df81fc-3ebe-439f-91d5-1a5646a2dc36",
              "is_primary": 1,
              "name": "",
              "profile": {
                "model": "gpt-5.6-luna",
                "name": "CI Fixup"
              },
              "started_at": "2026-09-08 15:48:39.572584425+00:00",
              "state": "WAITING_FOR_INPUT",
              "updated_at": "2026-09-08 22:41:34.452300385+00:00",
              "workspace_path": "/data/tasks/fix-plugin-task-prio_rksfvx9c/kdlbs-kandev"
            },
            {
              "agent_profile_id": "ab57f00e-ed8d-4205-bada-8be63fc4cd7d",
              "error_message": "",
              "id": "a56b4af9-6055-4fc1-ba75-8bd487b3669b",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.5",
                "name": "Review"
              },
              "started_at": "2026-09-08 15:40:25.826736169+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-08 15:48:40.078978195+00:00",
              "workspace_path": "/data/tasks/fix-plugin-task-prio_rksfvx9c/kdlbs-kandev"
            },
            {
              "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
              "error_message": "",
              "id": "40e9dc00-598b-486b-abe3-7d57f348b700",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-terra",
                "name": "Worker"
              },
              "started_at": "2026-09-08 15:22:47.390202895+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-08 15:48:39.723222659+00:00",
              "workspace_path": "/data/tasks/fix-plugin-task-prio_rksfvx9c/kdlbs-kandev"
            },
            {
              "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
              "error_message": "",
              "id": "9c4d2926-63e4-4035-8091-51201f93921a",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-luna",
                "name": "CI Fixup"
              },
              "started_at": "2026-09-08 10:26:12.604922428+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-08 15:48:39.723222659+00:00",
              "workspace_path": "/data/tasks/fix-plugin-task-prio_rksfvx9c/kdlbs-kandev"
            },
            {
              "agent_profile_id": "24eff7cc-14c2-4147-b635-5be3df285af3",
              "error_message": "",
              "id": "813570e7-c914-4772-ba28-8c5a20a08aab",
              "is_primary": 0,
              "name": "",
              "profile": {
                "model": "gpt-5.6-sol",
                "name": "QA"
              },
              "started_at": "2026-09-08 09:21:34.58214859+00:00",
              "state": "COMPLETED",
              "updated_at": "2026-09-08 15:48:39.723222659+00:00",
              "workspace_path": "/data/tasks/fix-plugin-task-prio_rksfvx9c/kdlbs-kandev"
            }
          ]
        },
        "next_action": "When a new attempt appears, start one fresh configured CI Fixup owner for exact-head census; green then requires fresh Review and distinct QA.",
        "deterministic_resume_trigger": "Run 34197413540 gains a new attempt/status, PR head changes, or deployed scoped rerun capability creates a new run.",
        "fallback": "Do not duplicate issuecomment-5584377539 or push a retry-only commit.",
        "cleared": false,
        "last_checked": "2026-09-14T23:56:41Z"
      },
      "relations": {
        "blocked_by": [],
        "blocks": [],
        "parent_id": "a68df3ae-aaf5-4591-a46d-9d73db62e46d"
      },
      "pending_moves": []
    },
    {
      "task_id": "ecd8b857-42a6-417f-a7e4-084f50fc6956",
      "title": "Run isolated Redmine first-version E2E",
      "column": "Done",
      "state": "REVIEW",
      "owner": "Task 7056a702-a3c3-4fe8-8535-c6b8d340ef6a owns safe exact cancellation; Coordinator terminal tracking",
      "health": "anomalous",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Completed the Done step.  `QA_RESULT=PASSED` is recorded in [QA-RESULT.md](/data/tasks/run-isolated-redmine_dfcy6fbj/e2e-v032/runtime/evidence/QA-RESULT.md). The disposable runtime and all synthetic data, credentials, ports, containers, network, and volume were removed. No PR was created because this task has no source diff and v0.3.2 is already released ...",
      "next_action": "After 7056 exact cancellation capability is reviewed/deployed, cancel pending row 3d1006bf-ff64-46a0-bff1-9cee8047b410 with predicates and verify Done remains stable with pending_moves=0.",
      "session_health": {
        "counts": {
          "COMPLETED": 3,
          "WAITING_FOR_INPUT": 5
        },
        "active_ids": [],
        "latest": {
          "id": "8c36e143-8cc4-48d8-ba7d-6d663002da23",
          "state": "COMPLETED",
          "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 21:50:14.960392119+00:00"
        }
      },
      "pending_moves": [
        {
          "id": "3d1006bf-ff64-46a0-bff1-9cee8047b410",
          "session_id": "1f88f830-91c1-4371-894b-cfaaa16a347c",
          "workflow_step_id": "485f61e8-33e7-4cc6-a170-6d1411cc5ebb",
          "queued_at": "2026-09-14 21:02:18.19025106+00:00",
          "actor": "agent",
          "sender_session_id": "da0761f2-cd4e-44d1-bccc-6f9c1119f534",
          "move_id": "7dd95377-7a02-4276-836a-f991c832e0cb"
        }
      ],
      "pr_gate": [],
      "blocker_or_gate": "Pending move is unsafe to touch until 7056 repair delivers ID-preserving rollback/re-arm fence.",
      "terminal_integrity": {
        "status": "anomalous",
        "receipt": "v0.3.2 disposable Redmine 6 E2E passed with immutable QA_RESULT and full runtime/data/credential/port/container/network/volume teardown; no source diff or PR. Stale Done→QA pending move remains."
      }
    },
    {
      "task_id": "f169e54f-610b-4f35-bcdc-cf3dfe3baaab",
      "title": "Enable audited cross-workspace task transfer",
      "column": "CI Fixup",
      "state": "FAILED",
      "owner": "Coordinator",
      "health": "stalled",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "CI Fixup completed the authorized conflict repair:  - Classified the prior E2E failure as base-owned; aggregates were derivative. - Merged current `origin/main`, preserving both service registrations. - Commit: `5309703fb18972bc14b7360c5e6d6f27e2ab654a` - Hooks, transfer tests, full Go build, and exact E2E reproduction with `--retries=0` passed. - Pushed ...",
      "next_action": "After capacity repair, start one Luna owner for exact current-head/base/threads; green routes Review then QA.",
      "session_health": {
        "counts": {
          "FAILED": 1,
          "WAITING_FOR_INPUT": 3,
          "COMPLETED": 17,
          "CANCELLED": 7
        },
        "active_ids": [],
        "latest": {
          "id": "e68c2c45-4fe2-4b49-8b4d-a7f5c40d7b00",
          "state": "FAILED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 22:44:20.037912634+00:00",
          "error_message": "failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500)"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3243,
          "state": "open",
          "draft": 1,
          "head": "5309703fb18972bc14b7360c5e6d6f27e2ab654a",
          "checks": "success",
          "passing": 53,
          "total": 53,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Standalone capacity [41001,41100] is exhausted; configured session failed before inference. PR #3243 cached CI is green at pushed successor."
    },
    {
      "task_id": "f2078d51-4dd4-435f-812a-f632328ccfb2",
      "title": "Harden env-read guard against aliased os imports",
      "column": "Done",
      "state": "REVIEW",
      "owner": "Coordinator terminal tracking",
      "health": "terminal",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Done audit passed and receipt persisted.  - PR #3505 merged at `4fde4f7c` - Task linkage verified - Merged files confirmed - Worktree clean, no unpushed task commits - No retained task runtime detected - Completion signal accepted",
      "next_action": "Archive on normal Done retention.",
      "session_health": {
        "counts": {
          "COMPLETED": 11,
          "WAITING_FOR_INPUT": 4
        },
        "active_ids": [],
        "latest": {
          "id": "009e4854-03a6-48d2-8b52-85c410743e1a",
          "state": "COMPLETED",
          "agent_profile_id": "7c6be62e-6980-498a-a4fb-896947ff5402",
          "model": "gpt-5.6-luna",
          "updated_at": "2026-09-14 18:20:41.558490586+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3505,
          "state": "merged",
          "draft": 0,
          "head": "7be6b34cb6c89db1149c8db869a585ce0e7dbde3",
          "checks": "success",
          "passing": 52,
          "total": 52,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Merged #3505; remote 7be6b34 content contained by squash delivery; clean/no runtime.",
      "terminal_integrity": {
        "status": "terminal",
        "persisted_receipt": {
          "id": "f2078d51-4dd4-435f-812a-f632328ccfb2",
          "status": "terminal",
          "receipt": "Merged PR #3505; remote 7be6b34 content contained by squash delivery 4fde4f7cb4; no unique work."
        }
      }
    },
    {
      "task_id": "fa3fba49-2018-460b-a600-adae23b24cc8",
      "title": "Add coordinator grant management surfaces",
      "column": "Work",
      "state": "REVIEW",
      "owner": "Coordinator",
      "health": "waiting",
      "last_checked": "2026-09-14T23:58:11.312865Z",
      "last_action": "Recovered and pushed the branch additively.  - Head: `56531c6e2d5dbea93682ab773fe5e0f55e86ee5d` - Remote and PR #3048 head match; worktree is clean. - PR is open, draft, and mergeable against `main` at `941e7950…`. - CI is still active: 2 success, 18 skipped, 10 queued, 1 in progress. - Focused backend and integrated-runtime tests passed.  The next gate i...",
      "next_action": "At next natural CI completion, run one exact-head census; green routes fresh Review, red routes exact branch-owned finding.",
      "session_health": {
        "counts": {
          "WAITING_FOR_INPUT": 4,
          "COMPLETED": 15
        },
        "active_ids": [],
        "latest": {
          "id": "d57acfc4-dc99-43b1-9241-05a6e3dbfff4",
          "state": "WAITING_FOR_INPUT",
          "agent_profile_id": "c06ad00e-0da1-429a-8174-54f97164a289",
          "model": "gpt-5.6-terra",
          "updated_at": "2026-09-14 22:48:06.618066372+00:00"
        }
      },
      "pending_moves": [],
      "pr_gate": [
        {
          "number": 3048,
          "state": "open",
          "draft": 1,
          "head": "56531c6e2d5dbea93682ab773fe5e0f55e86ee5d",
          "checks": "pending",
          "passing": 39,
          "total": 39,
          "threads": 0
        }
      ],
      "blocker_or_gate": "Fresh head 56531c6 is pushed/clean; PR #3048 CI remains nonterminal."
    }
  ],
  "human_asks": [
    {
      "task_id": "51c2875b-48ae-4097-b985-b8a9584ca8c2",
      "ask": "Choose maintainer-recommended plugin-owned saved-profile dispatch with Utility Agents fallback, or retain the preserved Host-selected contract.",
      "recommendation": "Adopt maintainer redirection.",
      "consequence": "Both clean PR heads remain withheld from notification/merge/deploy until decided."
    },
    {
      "task_id": "8f8a784d-92ea-421f-a368-154ef915fe4e",
      "ask": "Deploy the merged task-runtime source-broker registration through the Human release boundary.",
      "recommendation": "Deploy when the normal window is available.",
      "consequence": "Runtime provenance consumers remain unable to use the delivered service change."
    },
    {
      "task_id": "01432319-aa8b-4c7d-9841-addcc6ab8e76",
      "ask": "Publish/deploy the maintained codex-acp guarded-TTY distribution.",
      "recommendation": "Publish through the normal release boundary.",
      "consequence": "46945aff-382a-41a4-9f35-bd5c2806911e remains blocked on npm E404."
    },
    {
      "task_id": "8a182e40-d99c-42e9-b9be-1f8f78cf8388",
      "ask": "Run the supported authenticated read-only standalone-instance census and correlate ownership/generation; authorize normal teardown of exactly one conclusively terminal unowned orphan, or coordinate an agentctl maintenance restart if allocator-unavailable slots are the deficit.",
      "recommendation": "Census first; reclaim one proven orphan through normal lifecycle, then re-census and capacity-probe before any further action.",
      "consequence": "Fresh owners, including ae8 consumer verification and three cleared-gate R5 transitions, cannot start while all 100 allocator slots remain unavailable."
    }
  ],
  "durable_decisions": [
    "Human-maintained workflow step profile is authoritative; fixed lane-model gates remain suspended.",
    "Permanent Coordinator stays Backlogs and is never completed/moved/deleted.",
    "ToDeploy is Human-owned and Coordinator metadata-only.",
    "No duplicate unchanged provider/Human pings; stopped predecessors are never messaged or resumed.",
    "Sandbox H1-H5: Docker Sandboxes v1 fail-closed; microsandbox deferred; layered policy may only tighten absent authorized audited override; deny-all network default; PR #3496 reference-only then close after migration gates.",
    "Canonical adoption without exact transfer is evidence-backed adoption, not identity-preserving transfer; source carrier remains halted until unique-work recovery is confirmed."
  ],
  "source_carriers": [
    {
      "source_task_id": "3061ba9c-d9c8-472c-9ccb-e0400ccbc754",
      "workspace_id": "d35ace87-2aae-4e9c-9114-f9899af7f64b",
      "title": "Docker address pools exhausted",
      "disposition": "Adopted by canonical task 1d3d7383-8dba-41f8-a794-7e3d51809143; source remains halted immutable evidence carrier.",
      "overlaps": [
        "afdb2ef3-06ca-4cd5-a074-c4e691679da9 consumer",
        "8f8a784d-92ea-421f-a368-154ef915fe4e runtime registration only",
        "4b56a8b3-89fa-43ef-891d-c6b3a3b88e2a DB cleanup only",
        "92535de6-7507-473c-b292-e69516d2434c future sandbox only"
      ],
      "preservation": {
        "worktree": "/data/tasks/docker-address-pool_y55bu4s9/coordinator",
        "branch": "feature/docker-address-pool-2kn",
        "head": "425b1a4b1f2cca429d0c8af3ecd848db5cffa694",
        "state": "clean; zero commits ahead; no implementation",
        "source_session": "ebf71c87-d5c1-4afb-a530-7014011af720 WAITING_FOR_INPUT"
      },
      "next_action": "Canonical Work resumes after standalone capacity recovery; source carrier stays untouched; operator-only Docker remediation remains separately authorized."
    },
    {
      "source_task_id": "2348f10c-a220-40f9-9cc5-514aa95dae19",
      "workspace_id": "d35ace87-2aae-4e9c-9114-f9899af7f64b",
      "title": "Persist exact task-profile assignment and launch generation",
      "disposition": "Adopted by canonical task 6d03f4a9-bf89-4882-bf43-5a584f986185; source remains halted immutable evidence carrier.",
      "overlaps": [
        "e0dd8d19-278c-4d38-aafa-c3e866d92cfb configured-model enforcement after profile resolution",
        "7056a702-a3c3-4fe8-8535-c6b8d340ef6a pending-move generation/cancellation",
        "c642d57a-5a24-48ca-8f85-57d31115eeb5 workflow/session convergence"
      ],
      "preservation": {
        "worktree": "/data/tasks/platform-exact-profi_k2tb6qj7/kdlbs-kandev",
        "branch": "feature/platform-exact-profi-dbo",
        "head": "0c83f80fd90082aa4dc3b7baeb0b28cd6af77575",
        "preservation_ref": "2f753d219bfe96859d6f429b2272263dda0be52b",
        "tree": "3833932ed2516ed498d1d2f09ff81df11ae97f48",
        "uncommitted": "apps/backend/internal/orchestrator/session_launch.go; 36 insertions/10 deletions; diff-check clean",
        "source_session": "675deade-3a62-4ad5-ab58-cd01e575aecd WAITING_FOR_INPUT"
      },
      "next_action": "After e0dd8d19/#3473, 7056/#3155, and 9ee4/#3165 seams stabilize, atomically resume canonical task; source carrier stays untouched."
    }
  ],
  "degradations": [
    {
      "id": "standalone_port_capacity",
      "impact": "All 100 allocator slots in 41001-41100 are allocated or unavailable; session starts fail before inference. No stale instance ID is proven reclaimable.",
      "evidence": "/tmp/standalone-port-capacity-diagnostic-20260915.md SHA256 2a2d465b83d2c3fe33632cd887a1fa1a5c5213d091999210b0ce7dc51198ff0e",
      "next_action": "Operator/backend runs authenticated read-only ControlClient.ListInstances census; correlate ownership/generation; teardown exactly one proven orphan through normal lifecycle, then re-census/probe. If count<100 while exhausted, coordinate agentctl restart/product repair."
    },
    {
      "id": "cross_task_dependency_remove_self_scoped",
      "impact": "3f721d52 retains obsolete a3f edge; 1f8 retains non-live b2a edge; b748→212a requires disposition.",
      "next_action": "Use task-owned safe cancellation/removal only after workspace inventory and 7056 repair permit exact predicate verification; no DB bypass."
    },
    {
      "id": "cross_workspace_transfer_unavailable",
      "impact": "Canonical tasks adopted Performcoop evidence, but exact identity-preserving transfer is unavailable.",
      "next_action": "Keep source carriers halted and immutable until canonical owners confirm semantic recovery; f169e54f/PR #3243 remains deduplicated transfer capability owner."
    }
  ],
  "active_obligations": [
    {
      "priority": 1,
      "owner": "platform operator + 8a182e40-d99c-42e9-b9be-1f8f78cf8388",
      "action": "Restore and verify one standalone allocation using supported census/normal teardown; start capacity Spec first."
    },
    {
      "priority": 2,
      "owner": "Coordinator",
      "action": "Complete atomic R5 for 01d→Review and 153→QA only after capacity allows each new owner to be verified RUNNING."
    },
    {
      "priority": 3,
      "owner": "7056a702-a3c3-4fe8-8535-c6b8d340ef6a",
      "action": "Deliver safe exact cancellation, then remove ecd stale Done→QA pending row and resolve cfcc armed row without replay."
    },
    {
      "priority": 4,
      "owner": "Coordinator after capacity repair",
      "action": "For 23a, atomically route Blocked→Review with a verified configured Codex reviewer; require distinct QA before Human-QA; fresh red routes CI Fixup."
    },
    {
      "priority": 5,
      "owner": "Coordinator terminal tracking after capacity recovery",
      "action": "For ae8, prove zero consumers then record retention/expiry or authorized exact cleanup; resolve remaining Done relation anomalies while preserving receipts."
    },
    {
      "priority": 6,
      "owner": "Human",
      "action": "Execute ToDeploy asks for 8f8 and 014 through normal release boundaries; decide 51c scope redirection."
    }
  ],
  "action_verification": [
    {
      "task_id": "92535de6-7507-473c-b292-e69516d2434c",
      "action": "late terminal reconciliation",
      "result": "Done/COMPLETED, clean, preservation streams verified; stale pre-final messages superseded; do not reopen."
    },
    {
      "task_id": "86a16fc1-6394-4fb0-898d-4d42948683f5",
      "action": "PR #3153 configured CI restart",
      "result": "Session c6632154-cf10-4fb0-9c8b-72d9b36df611 used profile 7c6be62e-6980-498a-a4fb-896947ff5402/gpt-5.6-luna and failed before inference on port exhaustion; no source/provider mutation or retry."
    },
    {
      "task_id": "01d6764d-b66d-46a0-a664-2caf4c3f4d98",
      "action": "provider clearance recheck",
      "result": "Provider gate green; remained Blocked because capacity prevents verified atomic Review owner. No half-move."
    },
    {
      "task_id": "153cdbbe-beac-47b8-bc06-8dafdcc8ed80",
      "action": "provider clearance recheck",
      "result": "Provider gate green; remained Blocked because capacity prevents verified atomic distinct QA owner. No half-move."
    },
    {
      "task_id": "ecd8b857-42a6-417f-a7e4-084f50fc6956",
      "action": "terminal readback",
      "result": "E2E/runtime cleanup complete; stale pending move preserved because cancellation is unsafe before 7056 repair."
    },
    {
      "task_id": "8a182e40-d99c-42e9-b9be-1f8f78cf8388",
      "action": "capacity diagnostic",
      "result": "Supported backend diagnostic bundle failed to materialize after bounded attempts; no stale ID was proven. Human/operator must run authenticated read-only ControlClient.ListInstances census, correlate ownership/generation, and use normal lifecycle teardown only for one proven orphan; otherwise coordinate agentctl restart/product repair."
    },
    {
      "task_id": "bdc56ccb-b1ea-4f22-a1e0-e81eac5fa06e",
      "action": "Done integrity readback",
      "result": "Accepted head/merge/main containment, clean checks/worktrees, no delivery/cleanup obligations."
    },
    {
      "task_id": "23a05db4-c7bf-4732-a390-08cb8f0a3a8d",
      "action": "authoritative Human-QA→Blocked reconciliation",
      "result": "Physical Blocked step 89985050-d740-4421-bbbe-4aa018d8c7ab, REVIEW, updated 2026-09-15T00:18:30Z, pending0/active0; provider green at d742006c; R5 deferred solely for standalone capacity."
    },
    {
      "task_id": "ae8fc022-5562-4f58-95dc-3dab9d4c179f",
      "action": "authoritative Done→Blocked reconciliation",
      "result": "Physical Blocked step 89985050-d740-4421-bbbe-4aa018d8c7ab, FAILED, updated 2026-09-15T00:21:56.572644741Z, pending0/active0; automatic session 8cb37243/profile 8a033819 failed before useful work on failed to create execution: failed to create standalone instance: failed to create instance: failed to create instance: failed to allocate port: no available ports in range [41001, 41100] (status 500); at-risk note read back exactly; residue untouched."
    }
  ],
  "closed_ledger": [
    {
      "task_id": "00ceb41b-97fe-42d1-be99-10bbe9d1b676",
      "title": "Complete Redmine plugin implementation",
      "resolution": "Absent from live board after previously verified Done placement; archived from open ledger during reconciliation.",
      "closed_at": "2026-09-14T05:00:00Z"
    }
  ],
  "archive": {
    "path": "docs/archive/coordinator-state-plan-preimage-2026-09-14T202607Z.md",
    "bytes": 260867,
    "sha256": "4ba79d3c2a94e713d4844cf42b871d2695235c1bb9215a20cb5410cfeec45d8c",
    "commit": "cb6b69ade4ed3aeae8aa7b8d9cc6932515df0c19",
    "shared_main_fast_forwarded": true
  },
  "latest_cycle_gate_receipt": {
    "cycle": "2026-09-14T23:56:41Z snapshot; candidate built 2026-09-15T00:11:12Z",
    "G1": "PASS candidate: exactly 60 unique live IDs represented once (24 Blocked + 36 non-Blocked).",
    "G2": "PASS candidate: every ledger record has owner, health, last action, concrete next action.",
    "G3": "PASS candidate: 24 Blocked records contain all R4 fields and current checked timestamps; 01d/153/23a/ae8 capacity-gated resumes retained.",
    "G4": "PASS for this no-mutation candidate: cleared provider gates were not half-moved; R5 is executable only after verified capacity.",
    "G5": "PASS candidate: all cited actions have explicit results.",
    "G6": "PASS candidate: permanent Coordinator is sole Backlogs item; no Coordinator-owned Todo remains.",
    "G7": "NOT APPLICABLE to candidate: no live plan write authorized; candidate path/hash/readback validated locally."
  },
  "executable_handoff": [
    "Read PROMPT.md and this current-first snapshot; re-census before mutation.",
    "Capacity first: supported authenticated read-only instance census, ownership/generation proof, then exactly one normal teardown if conclusively stale; never kill or speculate.",
    "After verified capacity, execute 01d and 153 R5 atomically with physical move, precise handoff, and RUNNING owner verification.",
    "Process remaining ledger next_action fields; do not message stopped predecessors or duplicate unchanged provider contacts.",
    "Preserve Performcoop carriers and all Done artifacts until named cleanup/recovery receipts exist."
  ]
}
```

## Closed history note

Superseded detailed history remains in the verified archive referenced by `archive`; the compact `closed_ledger`, decisions, source carriers, receipts, and executable obligations above are authoritative for continuation.
