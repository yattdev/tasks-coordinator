# Runbook

## Local ignores in a LINKED WORKTREE go in the common dir
Task worktrees on this board are linked worktrees: `.git` is a FILE, not a
directory. Two consequences that cost real time on 2026-08-19 (`3c2a0d34`):
- `.git/info/exclude` fails outright with "Not a directory".
- Writing to `$(git rev-parse --git-dir)/info/exclude` SILENTLY DOES NOTHING —
  that resolves to `…/.git/worktrees/<name>/`, which git does not read ignores
  from. No error; the file just stays untracked.
Git reads `info/exclude` from **`$(git rev-parse --git-common-dir)`**. Verified:
in a coordinator worktree `--git-dir` gives `…/.git/worktrees/coordinator2` while
`--git-common-dir` gives `…/.git`. Always confirm the write took with
`git check-ignore -v <path>` — a correct exclusion names the common-dir file and
line, e.g. `/data/home/Code/performcoop/.git/info/exclude:22`.
RELATED JUDGEMENT worth copying: to keep files out of a push, use the LOCAL
exclude, never the tracked `.gitignore`. Editing the tracked ignore file to avoid
pushing something is itself a pushed change — self-defeating, and easy to miss.

## A task push can take down SHARED containers (compose project-name collision)
Happened for real on 2026-08-19: pushing from task `89812cba`'s worktree took the
main dev database down for a couple of minutes.
Mechanism, and it is armed on every worktree of a repo that does this:
1. `git config core.hooksPath .githooks`, and `.githooks/pre-push` execs
   `qualitycheck.sh`, which runs `docker compose` UNSCOPED (`qualitycheck.sh:15`).
2. Docker Compose derives its project name from the DIRECTORY BASENAME when
   `COMPOSE_PROJECT_NAME` is unset. Every task worktree for this repo is called
   `…/<task-slug>/performcoop` — basename `performcoop`, identical to the main
   checkout at `/data/home/Code/performcoop`.
3. So the hook operates on the MAIN checkout's containers. It recreated the live
   `performcoop-db-1` using the task's `DB_PORT`, which then failed to start on a
   port collision with the task's own DB.
The only protection is `COMPOSE_PROJECT_NAME=<task>` in the worktree's `.env` —
and an agent rewriting `.env` during a QA/Review pass can silently drop that
line, disarming it without any error. That is exactly how it happened.
SWEEP, run it before any task reaches PR rather than after an outage:
    for d in /data/tasks/*/<repo> /data/home/Code/<repo>; do
      printf '%-56s %s\n' "$d" "$(grep -h '^COMPOSE_PROJECT_NAME' "$d/.env" 2>/dev/null || echo MISSING)"
    done
On 2026-08-19 that returned MISSING for 9 of 10 worktrees. Most were dormant
(Done/Backlog tasks never push), so triage by whether the task is ACTIVE — the
risk is a live task reaching PR, not a stale directory.
Durable fixes are repo-level and belong to the human: scope the hook's compose
invocation with `-p`/`--project-name`, or stop naming worktree subdirectories
after the repo. A per-worktree `.env` line is a patch, not a fix, because the
next `.env` rewrite removes it again.

## Re-check a dirty working tree before flagging it
A `git status` snapshot taken while an agent's turn is running is a photograph of
a moving target. Build steps and test runs dirty the tree transiently, and the
agent commits or reverts moments later. Twice on 2026-08-19 a coordinator
snapshot would have produced a false flag on `89812cba`:
- 20:42 showed `M forms/training.py` uncommitted entering Review; the agent
  committed it at 20:43. The message and the commit crossed.
- 21:42 showed four modified `stashed/locales/**/django.po` files; seconds later
  the tree was clean. Transient artifacts of the QA build.
RULE: before sending a message about uncommitted or untracked work, re-run
`git status --short` and confirm the finding still holds. If it cleared, say
nothing — the agent handled it. Costs one command; the alternative is
interrupting a productive agent to report its own already-finished housekeeping,
which trains it to treat coordinator messages as noise.
The rule cuts both ways — it is a filter, not an excuse for silence. Same task,
same day at 22:12: 36 `.po` files under `stashed/locales/**` were modified and
STILL modified 30 seconds later. Persisted, so flagged. The diff was
auto-injected translation-consistency comments (HTML inside `#.` comments), i.e.
a `makemessages`-style build side effect writing into an archived tree — the kind
of churn that gets swept into a feature MR by a broad `git add -A` at PR time,
leaving a reviewer to guess whether 36 unrelated translation files were
intentional. Re-check, then flag what survives.
This does NOT apply to a persistently exposed artifact: `?? DIAGNOSTIC_REPORT_ANALYSIS.md`
sat untracked across many cycles and was real. The distinction is duration —
re-check, and flag what survives the re-check.

## Audit where the DELIVERABLE lives, not just where the notes live
Every cycle, for each active task, ask one question the task itself rarely asks:
**where does its primary output physically live, and does it survive the
worktree?** Agents reason carefully about the durability of their notes,
criteria and plans while the actual deliverable sits untracked, because the
deliverable feels solid — they have been editing it all day.
Observed 2026-08-19 on `3c2a0d34`: `DIAGNOSTIC_REPORT_ANALYSIS.md`, the 208-line
client-facing deliverable under active human review and carrying the estimate,
sat untracked at repo root across four sessions of work.
ACCURACY CORRECTION, because the first version of this entry was unfair to that
agent: it HAD noticed and raised the exposure to the human in the message
immediately before the coordinator's — independently and at the same moment. The
lesson is therefore NOT "agents fail to notice their deliverable is exposed".
The lesson is that **noticing is not securing**: the document remained untracked
for as long after it was surfaced as before, because surfacing it created a
pending human decision rather than a durable artifact. Run the check yourself
each cycle regardless of whether the task has raised it, and treat "flagged to
the human" as an open exposure, not a closed one.
Cheap check, run it per task: `git status --short` in the task's worktree, and
read the `??` lines as "dies when this worktree is cleaned up". Do not accept
"it's in the plan" as cover — a plan holding source material is not the same as
the document built from it.
Legitimate answer: the deliverable lives outside the repo and is delivered by
another channel. Then have them NAME the channel. The only thing to rule out is
"one worktree's disk".
When a task is already waiting on a human for one decision, BUNDLE the commit
ask into it rather than sending a second and third. One decision, several things
unblocked.

## A large task plan is append-only BY HAND, not by tool
`update_task_plan_kandev` and `create_task_plan_kandev` take FULL CONTENT — every
write regenerates the whole document through token output, with no byte-fidelity
guarantee. That is harmless for a plan you authored and can re-derive. It is
dangerous once a plan holds material that cannot be regenerated: verbatim source
comments, transcribed requirements, exact quotes, anything whose value is that it
is a faithful copy.
Observed 2026-08-19 on `3c2a0d34`: a 692-line plan held the only verbatim
transcription of 39 source comments. Appending one acceptance criterion would
have meant regenerating all 39 through the model. The agent refused; a previous
session on the same task had refused for the same reason. Upheld — trading an
irreplaceable requirements artifact to record a criterion about not losing
artifacts is exactly backwards.
Before rewriting any plan, ask what in it cannot be regenerated. If the answer is
"nothing", rewrite freely. If it holds copied source material, treat it as
append-only by hand and put new material somewhere else.
**Somewhere else does NOT mean an untracked file.** The same agent first parked
the criterion in an untracked `SPEC_ADDENDUM_INTERNAL.md` at repo root — a worse
failure mode than the one it avoided: it dies with the worktree, is invisible to
anyone without that checkout, and never reaches the Review or QA agent. An
acceptance criterion nobody downstream can see does not exist. Two resting places
that actually work, and they compose:
1. A TRACKED repo file, placed BESIDE THE CODE IT CONSTRAINS — survives the
   worktree, travels with the branch, appears in the diff the reviewer reads.
   **VERIFY THE DESTINATION IS ACTUALLY TRACKABLE FIRST: `git check-ignore -v
   <path>`.** Do not assume a `docs/` convention exists. In the Performcoop repo
   `28bb119f`, `/docs` is gitignored (`.gitignore:19`), there is no `docs/`
   directory on disk, and tracked markdown is four files. A coordinator told a
   task to move an acceptance criterion into `docs/` there on 2026-08-19; it
   would have landed in a gitignored directory, reproducing the invisibility it
   was meant to fix, while looking deliberate enough that nobody would question
   it. The agent checked and refused. Check before you direct.
   Corollary hazard on that repo: because `/docs` is ignored, documentation
   written there exists on one worktree's disk and is invisible to git and to
   every other checkout. Task `bcb507ce`'s handoff cites `docs/regenerate-entity-titles.md`
   as pre-existing; if it exists at all it is untracked and dies with its
   worktree. Treat any cited doc under an ignored path as non-existent until
   `git ls-files` proves otherwise.
2. The TASK CONVERSATION — an agent's own messages already are durable board
   state, retrievable via `get_task_conversation_kandev`. Note there is NO append
   primitive for a task's own conversation: `update_task_kandev` is
   full-description replacement, carrying the same fidelity risk as a plan
   rewrite. Never direct a task to overwrite its description to record something.
STAGED IS NOT COMMITTED. A staged file lives in the worktree index and dies with
the worktree exactly as an untracked one does. If a task's instructions forbid
committing without a human ask, the criterion is not durable until that ask
lands — say so rather than letting a staged file pass for a saved one.

## Never message a task parked in Todo — it bounces BACKWARDS
Some workflows give Todo an `on_turn_start` rule that moves the task to another
step the instant anything starts a turn there. A task that has just completed
Spec and auto-advanced into Todo can therefore be shoved straight back into Spec
by ANY inbound message — including a coordinator's congratulations. It then
re-runs a finished spec, and the completed plan is at risk of being re-litigated.
RULE: when a task is sitting in Todo, do not message it. Move it forward FIRST
(Todo has no auto-start, so it will never leave on its own), and put whatever you
wanted to say in the move's hand-off `prompt` — that reaches the receiving agent
at the new step without triggering the bounce.
This is the same mechanism as the deliberate "Todo bounce" used to re-fire a dead
auto-start; check each board's Todo `on_turn_start` target before relying on
either behaviour, because the destination differs per workflow.

## Coordinator-created child reaches Todo after Spec
Todo is deliberately inert: it does not auto-start an implementation agent.
If the Coordinator created/owns the child, verify that its saved plan is complete
and approved, move it Todo→Work with a concise implementation handoff, then list
its sessions and confirm a Work-profile session is RUNNING. If the move conflicts
because an obsolete Spec execution still appears live, stop only that direct
child's stale execution, retry the move, and record the recovery. Never apply this
rule to unrelated/manual Todo tasks.

## A resumed session is running but the task is still in the wrong column
`message_task_kandev` can successfully resume an idle session without changing
the task's workflow step. This creates a convincing false healthy signal: the
agent is RUNNING, but the authoritative board still says Todo, Review, or another
stale step, so the next lifecycle transition and profile selection are wrong.
After every resume, move, or recovery, re-list the task and its sessions. Verify
the physical `workflow_step_id`, task state, primary session, effective profile,
and pending move together. For a Coordinator-owned approved Todo task, perform
Todo→Work with the implementation handoff first and verify the Work on-entry
session starts; do not treat a resumed Spec/old session as equivalent.

## Task files are writable but Git cannot create `index.lock`
A managed task worktree may allow normal source edits and tests while its `.git`
file points to a linked-worktree administration directory outside the writable
task root. `git status` and `git diff` still work, but `git add`, `git restore`,
or `git commit` fails with read-only `.../.git/worktrees/<name>/index.lock`.
This is a Git-metadata authorization defect, not the same bug as duplicate
workspace materialization or canonical-workspace reuse.

Capture `git rev-parse --git-dir`, `git rev-parse --git-common-dir`, the exact
failed command, and the index-lock error. Do not broaden permissions to the
entire common `.git`, symlink around the sandbox, or expose sibling worktree
administration. Preserve the worktree and its diff. File a platform task whose
acceptance covers task-scoped linked gitdir/common-dir projection, primary and
later-attached repositories, real add/commit, normal concurrent lock conflicts,
and sibling isolation. If a separately authorized writable checkout is used to
recover work, verify every transferred file by checksum/diff and keep the
original checkout untouched for evidence.

## Abandoned, obsolete, or superseded task remains in an active column
Do not leave dead work parked indefinitely in Spec–CI Fixup. First verify from
the task trail that no implementation remains authorized, and check that it has
no open PR or open subtask. Post the terminal reason, preserve partial commits
and incident history, then move the task to Done. State explicitly that this is
a terminal resolution, not evidence that the original acceptance criteria
passed. Prefer this recoverable, auditable disposition over deletion. Deletion
still requires separate explicit human authorization.

## Wake delivery through KanDev routines
The Coordinator never installs or maintains cron, heartbeat scripts, local
credentials, or session-bound scheduler jobs. An operator-owned KanDev routine
targets the existing Coordinator task every 15–30 minutes with `WAKE:CYCLE`.
A second routine sends `WAKE:STANDUP` every day at 07:00 America/Montreal.

If routine delivery appears late, process the current message and compare its
timestamp with the last recorded routine ping. Record the gap as a degradation
and raise one visible human ask so the operator can inspect the routine. Do not
construct a fallback scheduler.

For a standup ping, run the full cycle, write
`standups/standup-YYYY-MM-DD.md` using the Montreal date, retain the five newest
dated reports, and reply in chat with only today's document name.

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
CAUTION — the signature is NECESSARY, NOT SUFFICIENT. `WAITING_FOR_INPUT`
seconds after a step agent starts also matches an agent that is simply between
polls, or one whose session was interrupted mid-poll and later resumes on its
own. Observed 2026-08-19 on `89812cba`: the coordinator read a 2-second
start-to-`WAITING_FOR_INPUT` gap in CI Fixup as a lost completion contract; the
agent was in fact mid-poll on a 15-minute CI pipeline, resumed, found it green,
and advanced itself. Same signature, different cause.
Therefore PHRASE THE NUDGE AS A QUESTION, never an assertion: "signal if you are
done, or reply with one line saying what you are waiting on." A question costs
nothing when the diagnosis is wrong and still unblocks when it is right.
Asserting "your session never received the contract" would have been confidently
incorrect and would have taught the agent to discount the next message.
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
DO NOT conflate this with the agent-context reset skip. Investigated on the
source 2026-08-17 (task d5e71c58) and confirmed INDEPENDENT: retained
agent-visible context cannot recreate or cancel a completion signal, because
completion is orchestrator-side state and `already_signaled` is only the MCP
dedupe result. The loop is also already treated separately in-tree —
`handleAgentBootReady` must not call `processOnTurnCompleteViaEngine`, asserted
by `event_handlers_github_review_test.go`. The confirming check: in the observed
loop the resumed agent derived "my signal must have been canceled" from the
VISIBLE BOARD STATE, not from stale memory, so a properly context-reset agent
would have reasoned identically. Fixing the reset does not fix the loop.
For reference, the reset skip itself (a different bug): on_enter reset runs
BEFORE lazy resume, `resetAgentContext` finds no live execution id, returns
success WITHOUT clearing `executors_running.resume_token`, and the later lazy
resume copies that stale token into `req.ACPSessionID` — so the first resumed
turn carries old context and the reset silently reported success.

## Agent cannot edit existing files (bwrap / userns)
Symptom, from a codex-profile session: `apply_patch verification failed: Failed
to read file to update ... fs sandbox helper failed ... bwrap: No permissions to
create a new namespace`. Creating NEW files succeeds; only existing-file patches
fail. Never the agent's fault, never fixed by retrying.
MEASURE IT, do not assume (2026-08-17 12:33 UTC):
  cat /proc/sys/kernel/unprivileged_userns_clone   -> 1        (kernel ALLOWS)
  cat /proc/sys/user/max_user_namespaces           -> 236497   (kernel ALLOWS)
  unshare --user --pid echo ok                     -> Operation not permitted
  grep ^Seccomp: /proc/self/status                 -> Seccomp: 2
  cat /proc/self/attr/current                      -> docker-default (enforce)
So the kernel permits user namespaces and the CONTAINER RUNTIME denies the
syscall. The fix is at container-run level (`--security-opt seccomp=unconfined`,
`--security-opt apparmor=unconfined`, or a profile permitting
`clone(CLONE_NEWUSER)`) — which may be deliberate hardening, so it is a human
decision, not something to route around.
Do NOT ask the agent to use direct-write workarounds: codex sessions carry a
patch-only constraint and are right to refuse.
DEAD WORKAROUND — do not promise it: spawning an editing-capable Claude session
onto the stuck task with `spawn_session_kandev` now returns
`FORBIDDEN: cannot spawn a session on a task in another workspace`. The
coordinator can only add sessions to tasks sharing its OWN materialized
workspace. Verify the tool call BEFORE telling a task help is coming (2026-08-17:
announced it to 9e67c426, then had to retract).
Every step in the Daily workflow pins a codex profile, and the Claude profiles on
this board (all `bypassPermissions`, which edit via native tools and never invoke
bwrap) are reachable only as a task's own assignee profile — which the step pin
overrides. So there is no coordinator-level fix.
What to do instead: (1) get the task to land everything achievable as NEW files
(spec/ADR docs, new modules) so the stop is partial, not total; (2) ask it for a
concrete blocked-list of deliverables plus the exact existing-file paths — that
list is the escalation's payload; (3) escalate to the human with options: pin
Claude profiles to the editing steps, fix the container sandbox policy, or
rebuild the task environment. Before choosing, check whether a task with a FRESH
workspace on the same repo can edit — if it can, the variable is environment age
and rebuilding the stuck task's environment is the narrow fix.
Before declaring the failure host-wide, compare a sibling task using the SAME
step profile and repository. A sibling that can edit is decisive evidence that
the variable is workspace/session preparation, not the global host policy; send
that comparison to the blocked task and require exact differentiating evidence.

## More than one coordinator is alive
**FIRST, AND MOST IMPORTANT: there is one Coordinator PER WORKSPACE, and they are
peers, not rivals.** Two coordinator tasks existing does NOT mean one must stand
down. Before concluding anything about ownership, resolve which WORKSPACE each
coordinator serves — `list_related_tasks_kandev` on your own task id returns your
`workspace_id`. A coordinator only has standing on its own workspace's board, and
has none on anyone else's. Known live pairs: `a68df3ae` serves workspace
`2e62401b` (Kandev); `f2949187` serves `d35ace87` (Performcoop).
Several coordinator TASKS share this repo, each in its own worktree. The shared
project memory under
`/data/home/.claude/projects/-data-home-Code-coordinator/memory/` is keyed to the
DIRECTORY, not to a task, so a fresh session will read it and may adopt another
task's identity wholesale. Confirm your own `Kandev Task ID` AND workspace from
your session context before you post, move, flag, or write a task plan.
WHAT THIS COST ON 2026-08-17..19: a session in `coordinator-long-liv_hnr95fk5`
(task f2949187, Performcoop) read the memory, concluded it was a68df3ae, and for
two days supervised the KANDEV board — nudging, forward-moving and creating tasks
it had no standing over, and overwriting a68df3ae's plan four times. On noticing
the clash it then negotiated a "single-owner standby" with a68df3ae and stood its
OWN board down, which is how a Spec task on Performcoop got told to take its
question to a coordinator in another workspace that could not even see it. Both
errors came from the same missing question: WHICH BOARD IS MINE?
The standby doctrine below applies ONLY to two coordinators contending for the
SAME workspace. If your workspaces differ, you are both active, you owe each
other nothing but courtesy, and standing down is itself the failure.
Wake ownership is SINGLE-OWNER WITHIN ONE WORKSPACE (irrelevant across
workspaces — each board's coordinator gets its own routines): exactly one
coordinator per board is the target of that board's routines and owns its watch — the one the human directs, whose
description carries the charter mirror. Every other instance is STANDBY: it is
not a routine target and makes no nudges, moves, or comments on board tasks. A
standby takes over only after the routine target is changed by the operator and
the takeover is announced on the formerly active task. Two active targets will
double-nudge every stuck task and create duplicate standups.
Handover needs no negotiation: all durable state lives in this repo and in the
active task's plan, so a standby can take over cold.
If a routine ping reaches a standby, do NOT run the cycle. Tell the active
coordinator and ask the operator to remove that standby from the routine target.
A WAKE:STANDUP reaching a standby is the dangerous one: the standup is a FILE
(`standups/standup-YYYY-MM-DD.md`) in this shared clone with a five-day
rotation, so two coordinators running it write the same path and both
fast-forward main — one silently clobbers the other, or the rotation deletes
files while the other is mid-write. Chat duplication is embarrassing; this
corrupts the durable record. Decline it and say so; never write that path unless
you are the routine target.
DECIDING WHETHER YOU ARE ACTUALLY STANDBY: first prove both coordinators belong
to the same workspace. Only then use liveness evidence: "received that
workspace's routine ping AND produced a turn", not "its session state reads
alive". Check the backend log for deliveries keyed by task and workspace over
the last interval and for turn boundaries. Never infer duplicate targeting from
two different workspace coordinators receiving similarly named routines.

## The visible ask channel can fail closed
The charter makes `ask_user_question_kandev` binding for every human-facing
blocker, but it requires a human attached to the calling session. From a
standby, headless, or routine-driven session it returns
`backend error [INTERNAL_ERROR]: Clarification request timed out or was
cancelled`. Such a session CANNOT comply with the rule as written: its
escalation dead-ends, and if it does not check the return value the blocker
disappears silently. This is the 2026-08-17 prose-only failure arriving from the
opposite direction — the mechanism meant to guarantee visibility failing closed.
Workaround: route the ask through a coordinator session that HAS a human
attached (normally the active coordinator), state plainly that you are relaying
rather than originating, and give the decision as named options so a one-word
answer resolves it. Always read the tool's return value; never assume an ask is
pending because you called the tool.
VERIFYING A PEER'S STANDBY — do it behaviourally, not declaratively. One
coordinator cannot inspect another's routine configuration. The check that works:
sweep /data/logs/backend-logs.log over the window and attribute every board
event — moves, messages, pending-move recordings — to a session id. All actions
on monitored tasks should trace to the ACTIVE coordinator's session; anything
unattributed is the signal to investigate. Run it each cycle. This corroborates
standby from the board trail rather than from either party's self-report, and it
also catches a standby that is misbehaving without having admitted it.

## Created a task and it never starts (Work step, no agent activity)
A task placed directly in the Work step can sit idle indefinitely because its
Work agent refuses to start without a SAVED APPROVED PLAN — creating the task
with a detailed description is not enough. Symptom: task shows in Work, no agent
messages, no session activity, worktree at the base commit with a clean status.
Fix: save a plan on it (`create_task_plan_kandev`, content can be derived
verbatim from the task description) and nudge it. Cost when missed: task
d5e71c58 was created 05:05 on 2026-08-17 and sat idle over seven hours.
If you create a task at Work, verify within one cycle that it actually produced
an agent message — do not assume creation means running.

## Two coordinators escalating the same issue: name actions, not letters
When more than one coordinator writes to the human about the same decision, do
NOT label options A/B/C — the instances will number them differently and the
human's "do A" becomes ambiguous. On 2026-08-17 two coordinators sent mirrored
recommendations for the editing blocker with A and B swapped; the substance
agreed, the letters did not. Name the action in the sentence ("pin Claude
profiles to the editing steps" / "relax the container seccomp+AppArmor policy")
so a one-word reply cannot select the wrong one.

## No standup this morning
1. Check that the daily routine is enabled, targets the active Coordinator task,
   uses `WAKE:STANDUP`, and is scheduled for 07:00 America/Montreal.
2. Check the task's sessions and routine execution history for delivery errors.
3. Send one manual `WAKE:STANDUP` to recover today's report; do not add cron or
   another heartbeat.

## Coordinator misbehaving (over-escalating / over-deciding / looping)
- Read its cycle logs on the task — decisions are one-line documented.
- Veto via comment; it calibrates from vetoes.
- Looping or runaway: flag the task with "STOP — wait for direction"; it must freeze.

## Weekly hygiene
Cycle logs on the task grow; have the coordinator roll up old logs into a
weekly summary comment (or do it manually) to keep its context lean.
