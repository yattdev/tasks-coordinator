# Coordinator continuity contract

The Coordinator is a long-lived role, not a particular model process or chat
context. Sessions may stop, be compacted, switch models, or hit provider limits.
Continuity therefore uses durable, model-neutral storage.

## Storage layers

1. **Binding behavior — `PROMPT.md`.** Human operating rules and mandatory
   Coordinator behavior. It is mirrored completely into the live Coordinator
   task description so a replacement session can bootstrap even before reading
   repository history.
2. **Reusable capability — `docs/`.** Operational playbooks in `RUNBOOK.md`,
   rationale in `DECISIONS.md`, QA safety in `QA_INSTANCES.md`, and learning
   receipts in `LEARNING_LOG.md`. These files are committed and fast-forwarded
   to the shared main checkout so every Coordinator worktree can receive them.
3. **Live operational memory — task plan.** Current task snapshots, exact
   identifiers and heads, active flags, pending human asks, follow-up ledger,
   blockers, preserved work, degradations, completed actions, and next steps.
   This changes frequently and is read before every action.

Conversation history may help reconstruction, but it is not the sole or
authoritative store. Never persist passwords, access tokens, cookies, raw
credentials, or unnecessary sensitive data in any layer.

## Load protocol for every new, resumed, or switched session

1. Read the actual UTC time and discover the current tools.
2. Read `AGENTS.md` and all of `PROMPT.md`.
3. Resolve the live Coordinator task, workspace, and workflow identity; never
   inherit identity from a stale handoff.
4. Read the top/current portion of the Coordinator state plan, including every
   open follow-up entry and unresolved obligation.
5. Load only the relevant runbook/decision/reference sections.
6. Reconcile the handoff against live task/session/PR/worktree state before
   mutating anything. If they disagree, trust current source evidence and repair
   the plan.

Compatibility loaders (`AGENT.md`, `CLAUDE.md`, and Copilot instructions) point
different agent clients back to the same contract. The Kandev task description
contains the complete current `PROMPT.md` as a second bootstrap path.

## Save protocol at the end of every turn

Classify each material fact:

- **Transient:** raw logs, temporary observations, or task-specific noise that
  no later session needs. Do not persist it.
- **Live operational state:** unfinished work, exact task/session/PR/head,
  blocker, next action, follow-up time/trigger, fallback, preserved path, or
  current degradation. Update the task plan with an executable handoff.
- **Durable learning:** a reusable human correction, policy, capability,
  recovery procedure, safety rule, or recurring failure pattern. Update the
  smallest appropriate repository files and learning receipt.

For durable learning:

1. Rebase the current worktree onto shared main before editing.
2. Preserve and synthesize concurrent valid changes.
3. Validate with `git diff --check` and inspect the final diff.
4. Commit on the current branch, rebase again if main advanced, and
   fast-forward `/data/home/Code/coordinator` main without force.
5. If `PROMPT.md` changed, mirror its complete content into the live Coordinator
   task description.
6. Verify the worktree is clean and the branch and shared main point to the same
   commit.

For the live handoff, record at minimum: last completed action; all open
obligations; exact evidence identity; owner; next safe action; follow-up
trigger/time and attempt count; fallback; and whether partial work is preserved.

## Proactive primary-session rotation and helper cleanup

The Coordinator task is permanent; any one session is disposable. Use a
server-reported cumulative cached-input-token count rather than estimating from
conversation length. Begin the save protocol at 180,000,000 cached tokens and
complete a primary rotation no later than 200,000,000. Rotate sooner when turn
admission, tool transport, compaction, or responsiveness degrades repeatedly.

Rotation is complete only when all of these hold:

1. The old primary has persisted the current plan and every reusable policy or
   procedure change.
2. Its queue has been censused; unread entries remain preserved in original
   FIFO identity and are not disposed merely because a replacement exists.
3. Exactly one successor session on the same task/workspace has read the full
   bootstrap and plan, reconciled live state, and returned a start receipt.
4. Kandev atomically promotes that successor as the current primary and routine
   target, with authoritative readback and no interval containing two primaries.
5. Only after the new primary and queue continuity are verified may the old
   primary be closed, archived, or deleted.

Additional helper sessions should be retired immediately after their result is
consumed and durably preserved. Prefer deletion only when the helper is
non-primary, has no live execution or pending action, has no unread queue (or
the queue was safely transferred/dispositioned), and its transcript is not the
sole evidence copy. Otherwise archive it and hide archived/terminal helpers by
default. When the required token counter, atomic promotion, queue transfer, or
session-specific close/archive/delete operation is unavailable, record the
capability gap and do not emulate it with task deletion, database writes, or
broad cancellation.

## Interrupted-session recovery

If a session disappears before saving, the next session must not guess. Inspect
the live task conversation and all sessions, the persisted plan, repository
status and worktrees, remote/provider state, and backend logs when relevant.
Preserve incomplete work, reconstruct the missing handoff, and update the plan
before continuing unrelated coordination.

This contract preserves capabilities, conclusions, evidence, decisions, and
pending work. It does not—and should not claim to—preserve private hidden
chain-of-thought. The durable artifacts are the source of continuity.
