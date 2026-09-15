# Issue #3176, Redmine marketplace, and quota handoff — 2026-09-15T04:55Z

## GitHub issue discussion

- Issue: `https://github.com/kdlbs/kandev/issues/3176`, “Architecture discussion: GitHub rate coordination and Workflow Sync recovery”.
- Canonical Kandev owner: task `27b493a3-65b6-4d4a-8b68-73f2ffcf9621`, “Fix workflow-sync GitHub polling starving API quota”, physical Work.
- Canonical delivery: draft PR `https://github.com/kdlbs/kandev/pull/3143`, “fix(github): coordinate rate limits and workflow sync recovery”.
- One deduplicated discussion notification was posted to the issue for `@carlosflorencio`, `@jcfs`, and `@nova28`: `https://github.com/kdlbs/kandev/issues/3176#issuecomment-5674557550`.
- `gh issue comment` failed through GraphQL with a rate-limit error. The equivalent single REST create-comment request succeeded. Do not duplicate the notification.

## Redmine marketplace registration obligation

- Human requirement: the released Redmine plugin must be registered in Kandev’s canonical plugin marketplace/manager so it appears in Browse and can be installed.
- Required direct child title: `Register Redmine plugin in marketplace`.
- Idempotency key: `register-redmine-plugin-marketplace-20260915`.
- Required repository/base: `https://github.com/kdlbs/kandev`, `main`.
- Intended scope: validate Redmine v0.3.2 release assets/checksums and Kandev v0.94.0 compatibility; add the canonical registry entry; validate registry behavior; open a draft PR; route through fresh Review and distinct QA. Closed PR #3682 and branch `feature/register-redmine-marketplace-v032` are evidence only and must not be blindly reopened or reused.
- Bounded `create_task_kandev` call timed out after 60 seconds. Read-only DB readback found no task with the external ID. No task exists yet; never report otherwise and never substitute local/native implementation.
- Next action: Coordinator retries creation only after the Kandev task-control surface returns a verified successful create plus readback, then saves the approved plan, moves Todo→Work, and verifies a workflow-configured Codex Work session starts.

## GitHub quota task recovery

- Existing task `27b493a3-65b6-4d4a-8b68-73f2ffcf9621` already owns the durable optimization: principal-keyed request coordination, interactive priority, a background reserve, resource-aware primary/secondary classification, equal-jitter backoff and suspension, and a provider-free task-bound local snapshot.
- Live provider behavior reproduced the issue: `gh issue comment` failed through GraphQL as rate-limited while an immediate REST `gh api rate_limit` reported full core, GraphQL, and search primary quotas; the direct REST issue-comment mutation succeeded. Treat resource/transport observations independently and avoid redundant GraphQL reads.
- Human requested fresh workflow-configured Codex sessions because stopped/hung sessions cannot answer. Bounded stop/spawn task-control calls timed out. DB readback showed no new session; stale GLM row `cc2afa78-ca2d-4999-ad01-e2a2102451c4` remains RUNNING, and existing Codex Work sessions are terminal or waiting. Do not message or rely on the stopped sessions.
- Next action: after task control recovers, stop the stale live session, start exactly one fresh Work session with the workflow’s Codex profile, and verify it is RUNNING. The handoff must reconcile local/fork/PR/current-main refs, retain the Retry-After and Search-resource QA fixes, integrate current main additively, and refresh exact-head CI → Review → distinct QA without duplicate provider polling.

## Continuity result

Task-plan mutation is part of the same unavailable task-control surface, so this archive is the durable fallback. No implementation, source branch, or PR content was changed by the Coordinator.
