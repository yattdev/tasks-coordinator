# KanDev Coordinator

Long-lived board coordinator for Spec → Work → Review → QA → PR → CI Fixup,
with a mandatory terminal-integrity audit of Done.
It monitors active work, unblocks agents, escalates only decisions that need a
human, and produces a daily standup document.

## Components

- [PROMPT.md](PROMPT.md) — live Coordinator charter and source of truth
- [AGENTS.md](AGENTS.md) — model-neutral per-turn bootstrap into the charter
- [CLAUDE.md](CLAUDE.md) and [.github/copilot-instructions.md](.github/copilot-instructions.md) — thin compatibility loaders; policy remains in `PROMPT.md`
- [docs/DECISIONS.md](docs/DECISIONS.md) — design decisions
- [docs/RUNBOOK.md](docs/RUNBOOK.md) — operations and troubleshooting
- [docs/QA_INSTANCES.md](docs/QA_INSTANCES.md) — Human-QA test-instance provisioning: fixture-vs-copy, hard prohibitions, credential handoff
- [docs/LEARNING_LOG.md](docs/LEARNING_LOG.md) — shared learning-cycle receipts
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
