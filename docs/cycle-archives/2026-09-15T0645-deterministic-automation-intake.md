# Deterministic no-model automation intake

Observed: 2026-09-15T06:45Z

The Human requested a reusable deterministic Automation action that can send an
exact fixed wake payload to the current PRIMARY Coordinator without creating an
intermediary task/session or invoking a model in the automation dispatcher.

Three parallel read-only audits found this feasible through the existing generic
Automation stack. Preserve `CronScheduler -> automation.Service.FireTrigger ->
automation.triggered -> AutomationRun history`. Branch by a new tagged action at
`apps/backend/internal/orchestrator/event_handlers_automation.go`, before the
current hidden-task creation and `StartTask` call. Existing rows and omitted API
fields must default to the current agent-backed behavior. The withdrawn legacy
`execution_mode` data remains inert.

The initial deterministic action sends an exact payload to a semantic current
PRIMARY Coordinator target. Target resolution and enqueue must share one
authoritative primary/current/generation/retirement fence. Retry identity must be
stable for the scheduled occurrence and independent of the resolved session, so
rotation or a lost response cannot cause duplicate delivery. Missing or ambiguous
PRIMARY state fails closed and remains visible in existing run history. The
automation dispatcher itself creates no task/session/provider/model request; the
already-running target Coordinator may process the delivered wake in its normal
session lifecycle.

Canonical implementation task:

- ID: `b94f9c54-b2fc-41f7-9c01-09ff2ef9d9c0`
- External ID: `automation-deterministic-no-model-actions-20260915-v1`
- Title: `Add deterministic no-model automation actions`
- Repository/base: `https://github.com/kdlbs/kandev`, `main`
- Saved approved plan: 8,576 bytes
- Workflow placement: Work; `start_when_unblocked=true`
- Current state: CREATED, zero sessions, dependency-gated

Required contracts:

- `ca015838-e5cf-4294-b3bb-9c50576a5fe6`: guarded queue delivery,
  occurrence/coalescing identity, and idempotent receipt.
- `b8fc206c-9e3f-4497-9ac3-3b62593da258`: authoritative dynamic PRIMARY
  selection, generation fencing, queue-preserving rotation, and retirement.

The task must not create a parallel scheduler, queue store, primary selector, or
heartbeat-only path. It owns the generic action registry, additive persistence and
API schema, conditional UI and history rendering, migration compatibility,
documentation, and the requested unit/integration/E2E coverage.
