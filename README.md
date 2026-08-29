# KanDev Coordinator

Long-lived board coordinator for Spec → Work → Review → QA → PR → CI Fixup,
with a mandatory terminal-integrity audit of Done.
It monitors active work, unblocks agents, escalates only decisions that need a
human, and produces a daily standup document.

## Components

- [PROMPT.md](PROMPT.md) — live Coordinator charter and source of truth
- [AGENTS.md](AGENTS.md) — model-neutral per-turn bootstrap into the charter
- [CLAUDE.md](CLAUDE.md) and [.github/copilot-instructions.md](.github/copilot-instructions.md) — thin compatibility loaders; policy remains in `PROMPT.md`
- [docs/CAPABILITY_REGISTRY.md](docs/CAPABILITY_REGISTRY.md) — canonical situation-to-action registry: what a Coordinator may do in each situation, with which capability, authority, evidence, and escalation route
- [docs/DECISIONS.md](docs/DECISIONS.md) — design decisions
- [docs/RUNBOOK.md](docs/RUNBOOK.md) — operations and troubleshooting
- [docs/QA_INSTANCES.md](docs/QA_INSTANCES.md) — Human-QA test-instance provisioning: fixture-vs-copy, hard prohibitions, credential handoff
- [docs/LEARNING_LOG.md](docs/LEARNING_LOG.md) — shared learning-cycle receipts
- [docs/CONTINUITY.md](docs/CONTINUITY.md) — model-independent load/save contract for session replacement
- [standups/](standups/) — date-stamped standup reports; newest five retained

## Bootstrap

1. Create and pin one Coordinator task per workspace; verify its live task ID,
   `workspace_id`, and `workflow_id`, then mirror [PROMPT.md](PROMPT.md) into its
   description. Coordinators for different workspaces are active peers, not
   primary/standby duplicates.
2. In KanDev routines, target that existing task with a monitoring ping every
   15–30 minutes, around the clock.
3. Add a separate daily routine at 07:00 America/Montreal for the standup.

The Coordinator does not install or maintain cron jobs, heartbeat scripts,
credentials, or scheduler state. KanDev routines are the sole wake source.

Every new or resumed session loads the charter and live plan through the
model-neutral repository boot files and mirrored task description. Every turn
ends with a continuity checkpoint: reusable learning goes to versioned shared
main, while current obligations and exact handoff state go to the live task
plan. Conversation memory is never the only copy.

## Workspace source broker

A Coordinator may autonomously use the reviewed `docker kandev source` broker
for source list, curated inspection, bounded logs, and logical database dumps,
including production-like data requested by an active same-workspace task. The
broker's workspace/target validation is authoritative; no case-by-case approval
is required. Source requests run only from the Coordinator's materialized task
worktree, never the shared main checkout. See
[docs/RUNBOOK.md](docs/RUNBOOK.md#retrieve-workspace-container-data-only-through-the-source-broker).

## Environment blockers

Host/container limits — missing tools or dependencies, permission failures,
unavailable host capabilities, absent Android emulator/device support — go to
`Kandev Support — Codex`. Missing kandev *product* features remain ordinary board
tasks. Coordinators contact Support **autonomously** through the reviewed broker
(`docker kandev support send|status|receive`) rather than asking the human to
relay, and never via `codex exec resume`, which cannot work from a container. See
[docs/RUNBOOK.md](docs/RUNBOOK.md#escalating-an-environment-blocker-to-kandev-support-host-codex-agent)
for the request schema, the three commands, and the known host-side faults.

## Routine protocol

- `WAKE:CYCLE` — run the complete action-oriented monitoring contract in `PROMPT.md`, including exact-head PR readiness and Done terminal-integrity checks, then persist the cycle log.
- `WAKE:STANDUP` — run one monitoring cycle, then write
  `standups/standup-YYYY-MM-DD.md` using the Montreal calendar date.

Queued duplicate markers are coalesced. A normal human message remains a normal
request, but also triggers a monitoring cycle when the board has not been
checked recently.

## Terminal cleanup

When a task is conclusively abandoned, obsolete, or superseded and has no open
PR or subtask, the Coordinator records that resolution and moves it to Done.
This preserves partial work and history without claiming the original work
passed. Deletion remains a separate, explicitly human-authorized action.

Done is monitored, not ignored. Newly entered or changed Done tasks receive a
terminal-integrity audit proving that local commits and untracked deliverables
are durable, the accepted PR head matches the final task head, sessions and
subtasks are terminal, and disposable resources have a safe disposition. An
unsafe Done task is preserved and returned to the narrowest active recovery step.
