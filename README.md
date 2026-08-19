# KanDev Coordinator

Long-lived board coordinator for Spec → Work → Review → QA → PR → CI Fixup.
It monitors active work, unblocks agents, escalates only decisions that need a
human, and produces a daily standup document.

## Components

- [PROMPT.md](PROMPT.md) — live Coordinator charter and source of truth
- [docs/DECISIONS.md](docs/DECISIONS.md) — design decisions
- [docs/RUNBOOK.md](docs/RUNBOOK.md) — operations and troubleshooting
- [standups/](standups/) — date-stamped standup reports; newest five retained

## Bootstrap

1. Create and pin the Coordinator task; mirror [PROMPT.md](PROMPT.md) into its
   description.
2. In KanDev routines, target that existing task with a monitoring ping every
   15–30 minutes, around the clock.
3. Add a separate daily routine at 07:00 America/Montreal for the standup.

The Coordinator does not install or maintain cron jobs, heartbeat scripts,
credentials, or scheduler state. KanDev routines are the sole wake source.

## Routine protocol

- `WAKE:CYCLE` — run one monitoring cycle and persist the cycle log.
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
