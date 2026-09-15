# Coordinator cycle blocked by task-control service

Cycle: `wake-cycle-2026-09-15T03:24:09Z`

## Reconciliation

- Live board and ledger both contain 60 tasks; sorted-ID SHA-256 is `30d6a14cf0f04ca113a7d236a79289863dc0d89b6504b5f0921e96165f929994`.
- Lanes: 24 Blocked, 16 Done, 7 CI Fixup, 5 Work, 2 Review, 2 Human-QA, and one each in Spec, ToDeploy, and Backlogs.
- All 24 Blocked tasks were freshly audited. Every record has the previous step, exact blocker, owner, preservation receipt, next action, deterministic trigger, and fallback. All have zero active sessions and zero pending moves.
- All 16 Done tasks were audited. Eleven are terminal-clean; PR #2868 is intentionally abandoned and terminal-preserved; four retain exact relation or pending-move cleanup obligations.
- The only pending move on the board remains the protected Redmine E2E row owned by the exact-cancellation repair. It was not touched.

## Findings and actions

- Safe bind probes found 8–13 free ports in the standalone range. Immediate bind capacity has recovered, though allocator inventory is still unverified.
- PR #3238 at `d742006c2b215705a2897487cc7275c41a2e9624` is green and has no provider blocker. Task `23a05db4-c7bf-4732-a390-08cb8f0a3a8d` is ready for atomic Blocked→Review routing.
- Five stale GLM sessions still appear RUNNING for tasks `1d3d7383`, `1e46d457`, `27b493a3`, `e0dd8d19`, and `fa3fba49`, but no matching live processes exist. The Human requires fresh Codex sessions and explicitly states the stopped sessions will not respond.
- One serialized attempt to spawn fresh Codex Work sessions timed out; readback showed no new sessions. Direct-child stop attempts for `1d3d7383` and `e0dd8d19` also timed out and made no state change.
- One standalone-capacity Spec start for `8a182e40-d99c-42e9-b9be-1f8f78cf8388` timed out; readback proved no session was created.
- Because these independent task-control operations all timed out and committed nothing, no further blind mutation attempts were made.
- `9ee4be81-aa98-4e4d-bdd6-842fd918f00f` is anomalously in Human-QA with five unresolved threads. `a091649a-79b0-40d6-a84d-84a3dc053e4a` is in Human-QA while PR #3672 remains draft. Both require corrected routing after task-control recovers.
- `7056a702-a3c3-4fe8-8535-c6b8d340ef6a` has a current blocking Review finding and needs Work. `37eca47b-cf05-47ee-b143-39408edbeed1` needs a fresh Codex Work owner for its preserved push. `b007bb76-841e-4243-a251-c4f87a1ed1e4` needs one exact-head failed-leaf classification. These actions were not half-applied.
- Existing exact-head maintainer rerun requests for PRs #2909, #3153, #3310, and #2841 remain deduplicated and event-driven.

## Required recovery

Operator owner: Kandev task-control/action service owner.

Repair or restart the task-control action path, then verify one session creation commits and reads back. After that:

1. Stop the five stale GLM sessions at safe boundaries and start one fresh workflow-configured Codex session for each affected task.
2. Start the `8a182e40` Spec owner and distinguish allocator inventory from bind availability.
3. Execute atomic R5 for `23a05db4`: Blocked→Review, exact-head preservation handoff, and verified fresh Review session.
4. Correct the two premature Human-QA routes and start the needed Work/Review owners listed above.

Deterministic resume trigger: a supported task-control mutation returns successfully and independent readback shows the intended new session or lane state.

## Exit gates

- G1 pass: 60 live task IDs equal 60 ledger IDs.
- G2 pass: every entry has owner, health, and executable next action.
- G3 pass: every Blocked task has a complete record checked this cycle.
- G4 fail: the cleared PR #3238 blocker could not be atomically moved and started because task-control mutations timed out/no-op.
- G5 pass: every attempted action has an independent no-op readback.
- G6 pass: Coordinator-owned Backlog/Todo disposition is complete; the permanent Coordinator remains in Backlogs by policy.
- G7 pass in the Git continuity archive; live plan writes remain unavailable.

The cycle is not signaled complete. It is durably parked on the task-control recovery trigger.
