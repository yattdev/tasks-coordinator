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
Before calling it a replay, apply the transcript check in the next section — log
shape alone is not enough.

## A step posts its verdict then sits still (no forward move)
A healthy turn logs `on_turn_complete consuming explicit signal` for the task id
in /data/logs/backend-logs.log. A step with `auto_advance_requires_signal: true`
that posts its result and then stops moving, with that line ABSENT for the turn,
never emitted the signal. It was NOT eaten in transit — but do not conclude the
agent was merely careless either. ROOT CAUSE FOUND 2026-08-17 (kandev commit
8dee5c978, `fix: inject completion context after workflow reset`): the
completion-signal contract was injected into the step prompt only when the
session state was `Created`. A step re-entered on a REUSED session is
`WAITING_FOR_INPUT`, so on re-entry the agent was never told to call
step_complete_kandev — even when the step declares both `reset_agent_context`
and `auto_advance_requires_signal`. The agent could not have known. The fix
extends the condition to steps declaring `reset_agent_context` on_enter.
Remedy while that fix is unmerged, and for any residual case: nudge the step's
own session with an explicit trigger/action/fallback naming step_complete_kandev.
It costs one message and moves the task immediately, because the agent's work is
genuinely finished — only the instruction was missing.
Only after a nudge produces a signal that IS logged as consumed and the task
still does not move should you suspect the routing layer.
Do not read a resumed session as evidence of a replay: `reusing existing session
for profile` + `found resume token for session resumption` is ordinary re-entry,
and the same `session_id` appearing on two `applying pending move` lines usually
means one session was resumed twice, not that one move applied twice. To claim a
replay you need two applications of ONE recorded move — check for a matching
`pending move recorded` line before each application, and read the recording
session's transcript to see whether it deliberately issued the second move.
(Learned the hard way 2026-08-17 on task 6e0fc028: the coordinator called a
replay from log shape alone and had to retract it — the QA agent had plainly
called move_task_kandev the second time. Read the transcript before the verdict.)

## Step re-enters on an ALREADY-COMPLETED session and loops
Symptom: A→B→A→B with no new commits, each step insisting it is already done.
Mechanism (observed 2026-08-17, task 6e0fc028, Review<->QA): a step that already
finished is re-entered on its old session; the resumed agent sees the board
sitting in its own step, reasonably concludes "my earlier completion signal must
have been canceled", re-routes to the neighbouring step and re-signals — which
returns `already_signaled` — and the neighbour then advances back into it. Both
agents behave correctly; the cycle is structural and the task cannot exit it.
Remedy: coordinator forward-moves PAST BOTH looping steps (here Review/QA -> PR)
with a hand-off prompt that states which gates already passed, at which commit,
and instructs the receiving agent not to re-run them or self-route. Trail must
justify it: both gates genuinely passed on the same commit.

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
