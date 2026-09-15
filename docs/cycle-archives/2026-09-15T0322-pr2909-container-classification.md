# PR #2909 container failure classification

Recorded at: 2026-09-15T03:22:40Z

Task: Prevent stale sessions blocking workflow (`c642d57a-5a24-48ca-8f85-57d31115eeb5`)

## Exact state

- Physical lane: `CI Fixup`; task state: `REVIEW`; session `5242ed7a-9492-4b63-93c5-b3fe09153b44` is waiting for input, with no running writer.
- Recovery checkout is clean and aligned with the fork and PR #2909 at `caee717b7c9d9c120e8dcbfcc77c7b08bfc9b697` against base `8acb32c8893d54089d11c7a43e0a61b97ba367bf`.
- The original checkout remains untouched at `b2dbf98a01b2bf6f20e21461d05c1f36627fd156` with its in-progress merge preserved.
- PR #2909 is open, draft, and mergeable.

## Leaf classification

E2E run `34888832549` failed all six container shards. Across approximately 134 tests, 22 failed: 20 shared `fetch failed` / `SocketError: other side closed` transport losses spanning unrelated Docker, SSH, Kubernetes, LSP, secrets, agent-config, popover, and concurrency paths, plus two 180-second docker-launch timeouts. Sibling tests passed in every shard, and the failures repeated on all three attempts.

The archive-cleanup wait is consequential after transport loss. The `docker-rollback-source-missing.git` message is the expected negative-path fixture for a passing rollback test. Same-test durations were 2–15 times slower than the upstream-main median, while an upstream-main run in the same window passed all six container shards. No E2E test or fixture changed across the relevant base ranges. All application checks and the ordinary web shards that ran were green.

Focused queue, messagequeue, and handler tests passed at the exact head. Docker is unavailable locally, so no meaningful local container replay exists. The evidence classifies the failure as external runner-side transport degradation; no branch-owned fix or retry commit is justified.

## Action and handoff

After confirming there was no exact-head duplicate, the task owner posted one request to rerun only the six container shard jobs: https://github.com/kdlbs/kandev/pull/2909#issuecomment-5673883109. No watcher, follow-up ping, empty commit, or source mutation was started.

Owner: repository Actions maintainer for the rerun; Coordinator for subsequent routing.

Health: blocked on external maintainer action while physically parked in CI Fixup.

Next action: on provider activity, maintainer reply, or the next bounded board recheck, inspect the exact run once. Green routes to fresh workflow-configured Review and then distinct QA. The same signature routes the preserved leaf evidence to the existing runner/CI capability owner after a live-board dedup search. A new task-owned failure returns to Work with exact evidence.

Deterministic resume trigger: a new attempt or terminal result for run `34888832549`, a maintainer reply, or a PR-head change.
