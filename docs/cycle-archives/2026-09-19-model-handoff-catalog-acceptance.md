# Model handoff: deployment receipt versus caller acceptance

Support result `b08ae611-5d33-4a84-8ea2-731334a9548a` reports a temporary
deployment overlay implementing exact profile selection and guarded primary
handoff. Reported source references are backend `50d95d2ae` and agentctl
`7283d9f1a`; deployment provenance is `de967a8` plus `338a878` in
`yattdev/kandev-service`. This is Support-reported provenance, not independent
source or deployment verification by the Coordinator.

Coordinator-side verification at 2026-09-19 05:29 UTC found:

- Profile discovery works and identifies enabled generic Terra, Luna, Sol and
  Astra profiles. Session readback now includes queue incarnation IDs.
- The existing Coordinator's callable catalog lacks
  `assign_exact_task_profile_kandev`, `handoff_coordinator_primary_kandev` and
  `list_repositories_kandev`. No tool-search or refresh control is exposed.
- `get_message_queue_census_kandev({})` still returns
  `UNKNOWN_ACTION: mcp.get_message_queue_census`.
- The original Astra remains the sole primary. No model assignment, successor
  probe, handoff, queue disposal or rollback was attempted.

Therefore live handoff acceptance is incomplete. Support follow-up
`743d0eee-30ad-412d-8373-8de7abbabcec` owns the existing-session catalog/action
gap. Verify the actual caller after its pushed result; a fresh standalone
bootstrap or passing backend suite alone does not prove that a long-lived
client can invoke a newly registered tool. Do not reset an active primary to
obtain the controls needed to preserve that primary's unread queue.

The permanent source successor is
`65142b9f-e392-4538-bb9d-1e9152008e2a`, replacing the unlaunchable preserved
owner `b8fc206c-9e3f-4497-9ac3-3b62593da258` for this implementation. Its
approved plan requires reconciling existing exact-profile PR #3688, isolated
source work, independent gates and a post-merge/release Support callback.
Overlay cleanup must wait for an image containing every still-required fix;
Support owns safe deployment and rollback. The source worker must not remove
the overlay or operate the live Coordinator.

Reusable rule: distinguish deployment, tool visibility, successful invocation,
actual model verification, and complete handoff verification. None implies the
next. Missing caller controls remain an owned repair, not a successful switch
or measured cost saving.
