# Runbook

## Harness-scheduler mode (no `crontab` binary — current kandev worktree executor)
The coordinator schedules wake-ups with the agent-harness cron tools instead:
- Jobs carry the same markers (`# kandev-coordinator-standup`, `# kandev-coordinator-cycle`)
  inside the job prompt; standup fires DAILY (57 11 UTC = 7:57 Montreal EDT).
- Jobs are session-scoped: they auto-expire after ~7 days AND they vanish
  entirely the moment the session ends. A NEW coordinator session therefore
  starts with `CronList` empty — that is expected, not a bug, and re-provisioning
  both jobs is the first action of any restarted session (before any triage).
  If the agent session is fully restarted, any manual message to the coordinator
  task re-arms them.
- The cycle job exists only while the pipeline (Spec..CI Fixup) has tasks.

## Task failed to start: "Preparing worktree (checking out '…') fatal: '…' already exists"
Stale worktree dirs from a terminal session block fresh env prep (restore is
refused for terminal sessions; fresh-create collides with leftover dirs).
1. Verify the leftover worktrees are clean (`git status`) — branch refs live in
   the shared git dirs and survive removal.
2. Park (never rm) the dirs into /data/trash/, then `git worktree prune` in the
   shared repos.
3. Re-fire auto-start: same-step moves do NOT re-fire it and messages to
   terminal sessions error — bounce the task out to the inert Todo step and
   back to its target step (Todo only acts on turn START, so it's a safe hop).

## Task failed to start: "base branch does not exist: main"
The task's repository has no such branch — commonly an EMPTY repo (no initial
commit). Seed the repo (initial commit on the default branch) with the owning
task's credentials, then re-trigger the start (bounce, above).

## Step agent silently never launched (task idle in a step for hours)
Auto-start can fail without any message on the task. Check
/data/logs/backend-logs.log by task_id ("session entry created" missing after
the move = never launched). Re-fire with the Todo bounce; attach a hand-off
prompt on the move back. Note: move_task's prompt queues to the OLD primary
session when no live session exists — after relaunch, message the NEW session
explicitly (list_task_sessions → message_task with session_id).

## Task ping-pongs back to a previous step with an unchanged tree (pending-move replay)
Platform bug (kandev, confirmed 2026-08-17; fix task on board): a "pending move"
recorded while a session is mid-turn can re-apply after its first application,
yanking the task back (e.g. QA→Review) with an UNCHANGED tree and eating the
current step's step_complete signals. Triage: diff the tree between re-entries —
changed = by-design re-review (let it flow); unchanged = the replay bug.
Remedy: coordinator forward-move past the poisoned edge (trail must justify:
the affected steps already passed), then create/point to the platform bug task.

## A step posts its verdict then sits still (eaten step_complete signal)
A healthy turn logs `on_turn_complete consuming explicit signal` for the task id
in /data/logs/backend-logs.log. A step with `auto_advance_requires_signal: true`
that posts its result and then stops moving, with that line ABSENT for the turn,
did not get its signal through. Look just before it for a `pending move recorded`
/ `applying pending move` pair on a DIFFERENT session id, plus
`reusing existing session for profile` and `found resume token for session
resumption` — the step was re-entered on a resumed session rather than a fresh
one, even when the step declares `reset_agent_context` on_enter.
Triage: (a) replay path consumed the signal, or (b) the resumed agent never
emitted it because it never saw the on_enter contract. Both look identical on
the board. Remedy: nudge the step's own session to re-emit step_complete first
(cheap, usually works); only forward-move past the edge if it cannot.
Observed 2026-08-17 04:26–04:27 UTC on task 6e0fc028 — the pending-move fix task
reproducing the failure on itself; evidence posted on that task.

## No standup this morning
1. `crontab -l | grep kandev-coordinator` — entries present, exactly once each?
2. 2. `tail -50 ~/.local/state/kandev/coordinator-wake.log` — did cron fire? FATAL lines?
3. 3. Manual wake: `kandev-coordinator-wake.sh STANDUP` — watch the task in the UI.
4. 4. Script OK but task silent → check the task's session state in KanDev;
5.    test whether `message_task_kandev` relaunches idle sessions (see DECISIONS).
6. 
7. ## Wake script fails
8. - `FATAL: coordinator.env missing` → recreate from config/coordinator.env.example, chmod 600.
9. - `initialize failed HTTP ...` → MCP_URL/port wrong, endpoint down, or auth; try `tools/list` manually.
10. - `tools/call failed` / isError → check argument names (`task_id`, `message`) against `tools/list`.
11. 
12. ## Coordinator misbehaving (over-escalating / over-deciding / looping)
13. - Read its cycle logs on the task — decisions are one-line documented.
14. - Veto via comment; it calibrates from vetoes.
15. - Looping or runaway: flag the task with "STOP — wait for direction"; it must freeze.
16. 
17. ## Duplicate cron entries
18. Remove all marker-carrying entries, let the next session start re-provision
19. (idempotent check is on every session start).
20. 
21. ## Weekly hygiene
22. Cycle logs on the task grow; have the coordinator roll up old logs into a
23. weekly summary comment (or do it manually) to keep its context lean.
