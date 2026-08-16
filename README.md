# KanDev Coordinator

Long-lived task pinned to the board that supervises all active tasks
(spec → work → review → qa → pr → ci-fixup), resolves blockers with a
DECIDE / RECOMMEND / ESCALATE ladder, and posts a standup report every
day at 8:00 America/Montreal. Between standups it self-schedules
mid-interval monitoring cycles (30–60 min) whenever the pipeline has
active tasks — in-progress tasks often block silently, so cadence is
judged from board occupancy, not a fixed clock. Spec gets first-class
attention: the coordinator answers answerable questions itself and
moves plan-complete tasks forward to Todo. Replaces the human as first
responder; escalates only high-stakes forks.

## Components
- [PROMPT.md](PROMPT.md) — the Coordinator's workstep prompt (source of truth; paste into the KanDev task)
- [bin/kandev-coordinator-wake.sh](bin/kandev-coordinator-wake.sh) — cron-called wake script (MCP `message_task_kandev`)
- [config/coordinator.env.example](config/coordinator.env.example) — template for `~/.config/kandev/coordinator.env`
- [cron/crontab.example](cron/crontab.example) — the two cron entries (standup + cycle)
- [docs/DECISIONS.md](docs/DECISIONS.md) — why it's built this way
- [docs/RUNBOOK.md](docs/RUNBOOK.md) — ops and troubleshooting

## Bootstrap (once)
1. Create the Coordinator task on the board, pinned; paste PROMPT.md.
2. Copy `config/coordinator.env.example` → `~/.config/kandev/coordinator.env`,
   fill MCP_URL / TASK_ID / MCP_TOKEN, `chmod 600`.
3. Install `bin/kandev-coordinator-wake.sh` → `~/.local/bin/`, `chmod +x`.
4. Dry-run: `kandev-coordinator-wake.sh CYCLE` — coordinator should wake and log a cycle.
5. The coordinator provisions/heals its own crontab on every session start
   (see SELF-PROVISIONED WAKE-UP in PROMPT.md); `cron/crontab.example` is the reference.

## Wake protocol
`WAKE:STANDUP` → full cycle + daily report. `WAKE:CYCLE` → cycle only.
Anything else → treated as human/task communication.
