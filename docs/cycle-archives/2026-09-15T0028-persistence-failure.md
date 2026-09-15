# Coordinator cycle persistence degradation — 2026-09-15T00:28Z

The live board census contains 60 tasks: 24 Blocked, 36 non-Blocked, and 15 Done. The validated current-cycle ledger is archived in `2026-09-15T0022-current-cycle.md`; the append-only recovery delta is in `2026-09-15T0022-plan-delta.md`.

The live Coordinator task plan remained at 189,125 bytes with SHA-256 `ce32944602794c962f5177b250175f29678373299f2b7b97d91bdc53df43d624` and update time `2026-09-14T23:55:05.315677262Z`. One `update_task_plan` replacement, one compact append, and one `create_task_plan` replacement each stayed pending and were terminated after bounded waits. Authoritative readback after each attempt proved no write committed. No uncertain request was repeated.

The old live plan therefore retains 57 ledger IDs and 22 Blocked records. The archived current-cycle ledger contains all 60 unique live IDs and 24 complete Blocked records. Restore the task-plan write path, then publish the exact archived current-cycle ledger after confirming the live plan still has the recorded SHA.

Standalone ports `41001–41100` remain exhausted. No stale instance is conclusively reclaimable without an authenticated instance census. Run the supported authenticated instance census, correlate instance identity and generation with authoritative execution ownership, and tear down only a proven orphan through normal lifecycle deletion. If registered instances are fewer than 100 while allocation remains exhausted, use a coordinated `agentctl` restart to clear process-local unavailable slots. Do not delete guessed instances or free ports manually.
