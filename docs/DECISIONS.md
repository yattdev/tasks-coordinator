# Design decisions

## Long-lived pinned task, not a daemon
Reuses KanDev primitives (session, tools, flags, comment trail) and dogfoods
the platform. A separate service only if event-driven triggers become necessary.

## Wake via External MCP `message_task_kandev`, not automation/webhooks
KanDev has no idle wake-up. The automation feature and webhook triggers create
a NEW task per fire — unusable for waking an existing task. The SPA deep link
does nothing without a browser (resume is done by frontend JS over WebSocket).
`message_task_kandev` on an idle task delivers immediately = wake; on a running
task it queues = harmless. Verified: [date, result of the idle-relaunch test].

## Cron → script → MCP, not protocol-in-crontab
MCP streamable HTTP needs a handshake; crontab stays one dumb line, all
protocol lives in the script, config in one env file.

## Action budget (1 task creation/cycle, no Done/backwards moves)
The coordinator is the highest-blast-radius agent: a misread board amplifies
across every task in one cycle. Budgets cap the damage; loosen only after
weeks of clean FYI/veto history.

## Escalation contract (3 reasons only)
High-stakes fork / irreconcilable cross-task conflict / systemic anomaly.
Everything else: decide-and-document as vetoable. Matches the trust model:
veto async from the board rather than pre-approve.

## DST
CRON_TZ=America/Toronto so 8:00 tracks Montreal wall clock across EST/EDT.
If the cron daemon ignores CRON_TZ, entries are in UTC with the assumed
offset noted in the marker comment (drifts 1h at DST changes).
