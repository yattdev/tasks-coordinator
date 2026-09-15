# Primary Coordinator rotation handoff — 2026-09-15T04:33Z

## Identity and authority

- Permanent Coordinator task: `a68df3ae-aaf5-4591-a46d-9d73db62e46d`; never move, complete, archive, or delete this task.
- Workspace: `2e62401b-5ffe-4050-bc1b-d49ea5d5dbcd` (`Kandev`). Workflow: `90f322ed-2159-424d-96e7-c2ad05668b8e` (`Daily workflow`).
- Old primary/current session at checkpoint: `da0761f2-cd4e-44d1-bccc-6f9c1119f534`, profile `ccd6113e-c1bd-4029-9d7d-f36f72272fa5`, state RUNNING.
- The Human explicitly requested a compacted handoff to one fresh session that should become the main Coordinator. The successor must obey `AGENTS.md`, all of `PROMPT.md`, `docs/CONTINUITY.md`, the live Coordinator plan, and this receipt before mutation.
- Coordinator delegates implementation only through persistent Kandev board tasks. It does not code, test, push, publish, or create PRs itself.
- Workflow-configured Codex/Copilot profiles are authoritative. Do not recreate the retired fixed model map.

## Durable state

- Coordinator branch and shared `/data/home/Code/coordinator` main both pointed to `9cae45a86f6c29ee302bec231bc1ce28fa379dd5` and were clean before this handoff file was added.
- The live plan was read at 190,450 UTF-8 characters. Its current-first structure and all open blocked records remain authoritative. It is close to the 200 KiB compaction threshold; measure again before the next large append and compact only with an exact archive preserving every open task ID and blocked record.
- Latest exhaustive cycle artifacts: `docs/cycle-archives/2026-09-15T0415-cycle-receipt-blocked.json` and `docs/cycle-archives/2026-09-15T0415-control-plane-blocked-cycle.md`. That census had 60 tasks before the two Redmine registration children were created, so the successor must perform a fresh full-board reconciliation rather than reuse the count.

## Queue and rotation safety

- At this checkpoint `get_message_queue_census_kandev({})` failed with backend `UNKNOWN_ACTION: mcp.get_message_queue_census`. No queue entry was read, acknowledged, disposed, replayed, or transferred.
- `list_task_sessions_kandev` showed exactly one session: old session `da0761f2-cd4e-44d1-bccc-6f9c1119f534`, `is_primary=true`, `is_current=true`, RUNNING.
- No task-runtime tool currently exposes atomic queue-preserving primary/routine-target promotion or exact-session retirement. Do not emulate this with raw HTTP, WebSocket, SQL, task deletion, or filesystem mutation. A spawned successor is not authoritative until a native atomic promotion and primary/current/routine-target plus queue readback succeeds. If that capability remains unavailable, the old session remains authoritative even while the successor bootstraps.
- Existing platform owners: queue capability `ca015838-e5cf-4294-b3bb-9c50576a5fe6` / PR #3377; exact session rotation `b8fc206c-9e3f-4497-9ac3-3b62593da258`; safe session cleanup `86c8b47e-e7a5-4693-8e11-dce08899a0bf`.

## Immediate delivery obligations

1. Redmine marketplace registration is delegated to the sole recovery task `b7cb6fe6-3766-4b81-a7ee-f5e9c16627cf` (`register-redmine-plugin-marketplace-20260915-recovery-v1`) in Work. It uses `workspace_mode=new_workspace`, repository `https://github.com/kdlbs/kandev`, base `main`. Session `e731d488-4804-4c59-afd4-b1144f2cda3d`, profile `c06ad00e-0da1-429a-8174-54f97164a289` (Codex gpt-5.6-terra), was verified RUNNING. Monitor it; do not implement or publish from the Coordinator. Its failed empty carrier `3d456f24-73e7-4c0b-8821-ee49a3fa0f31` is terminally superseded in Done and must never restart.
2. GitHub issue #3176 maps to task `27b493a3-65b6-4d4a-8b68-73f2ffcf9621` and PR https://github.com/kdlbs/kandev/pull/3143. Discussion notification is already posted at https://github.com/kdlbs/kandev/issues/3176#issuecomment-5674557550 mentioning Carlos and relevant maintainers. Do not duplicate it without new evidence.
3. H6 task `23a05db4-c7bf-4732-a390-08cb8f0a3a8d` had a cleared capacity blocker but remained physical Blocked when task control failed. After fresh pending-move/session/lane preflight, atomically route to Review with exactly one workflow-configured Review owner and verify it starts; otherwise preserve its full R4 record.
4. The Human stopped stalled/hung board sessions and switched workflows to Codex-family profiles. Work/Review tasks that still rely only on stopped or stale pre-switch owners must be relaunched through their current workflow-configured profile, one active owner per expected execution step, after exact pending-move preflight. Never resume stopped sessions or assume they will answer.
5. Preserve exact pending-move safety. Never touch row `aeed2cd9-2de4-45db-bcc8-1fa5cc4e7613` or session `c30dcee1-a037-45af-b1a3-d0bcca127694`; task `7056a702-a3c3-4fe8-8535-c6b8d340ef6a` owns the repair. Another known pending move is `ecd8b857-42a6-417f-a7e4-084f50fc6956` targeting QA with row `3d1006bf-...`; identify its full immutable row and preflight before any contact.
6. GitHub API quota is a recurrent degradation. Use one shared resource-keyed quota snapshot, REST before GraphQL when sufficient, event-driven wakeups, bounded polling with backoff, cached exact-head evidence, and no duplicate PR/thread/check censuses. Task `27b493a3-65b6-4d4a-8b68-73f2ffcf9621` / PR #3143 owns the workflow-sync quota fix.
7. Reconcile the complete board, including every physical Blocked task and every Done task, against the open/closed ledger. Each live entry needs owner, health, last action, next action, and current-cycle checked timestamp; every physical Blocked record needs previous step, exact blocker, owner, preservation, next action, and deterministic trigger.

## Successor first actions

1. Read the required policy/state files completely and resolve live identity, workflow steps, plan, tasks, sessions, pending-move capability, queue capability, and provider quota state.
2. Return a start receipt to old session `da0761f2-cd4e-44d1-bccc-6f9c1119f534` using `message_task_kandev` on this same task with the explicit `session_id`. Name the files read, effective profile/model, live task/session counts, reconciled obligations, queue result, and any mismatch.
3. Do not dispose queue entries or mutate the board until bootstrap/reconciliation is complete.
4. If a native atomic promotion operation is exposed, use it exactly once and verify successor `is_primary=true`, `is_current=true`, routine target, generation fence, and preserved queue identity before asking the old session to retire. If absent, report the capability gap; do not claim the successor is the main session.
