# Runbook

## Human-QA runtime provisioning is an acceptance gate

Fixture-vs-copy decision, hard prohibitions, credential handoff and image
capability limits live in [QA_INSTANCES.md](QA_INSTANCES.md).

For every Human-QA task that needs an application runtime, create a separate
Docker instance from the exact tested head and stop that task's older test
instance first. Publish and verify a `0.0.0.0` binding through the machine's
actual LAN address; `127.0.0.1` is diagnostic evidence, not a human handoff.

Seed the instance from a task-private writable clone of a sanitized, immutable
snapshot of the main container's application data. Treat the main container and
its volumes as read-only. Destination-only operations include migrations,
database/index repairs, test-user creation, and feature fixtures. Never copy
provider credentials, auth sessions/tokens, managed-Git secrets, agent homes,
repositories/worktrees, caches, builds, or logs. Preserve representative
non-secret rows and required attachments so the human tests realistic state.

Before publishing `TEST_INSTANCE_READY`, prove and record:

- task ID, exact source commit, image and container IDs;
- `0.0.0.0` port binding, canonical LAN URL, HTTP health, and test login;
- seed manifest/hash, private clone path, database integrity, and one disposable
  destination-only write/delete;
- representative data counts and task-specific feature checks;
- the previous task instance is stopped, the main instance remains healthy and
  unchanged, and exact start/stop commands are available.

SQLite integrity checks do not prove external-content FTS consistency. When a
cloned `tasks_fts` contains stale/orphan row IDs, repair only the private clone
in an exclusive transaction by deleting the FTS rows and reinserting canonical
`tasks` rows with matching `rowid`; then verify exact counts, zero orphans,
`quick_check`, `integrity_check`, and a disposable task lifecycle. The generic
FTS `rebuild` control command is not valid for the schema that exposed this
failure.

Reject wrong-head, empty, unseeded, shared-main, credential-bearing,
non-Docker, localhost-only, or feature-broken handoffs. A compliant instance
that reveals a product defect sends the task back to implementation. A task may
use `TEST_RUNTIME=NONE` only when its deliverable genuinely has no persistent
runtime (for example docs, a code-only library, or test-runner infrastructure).

Any push, merge, rebase, or conflict-resolution commit immediately withdraws a
published instance's readiness until it is rebuilt and revalidated at the new
exact head. The old container may remain available briefly for diagnosis, but
label it stale and do not include it in a current human-testing inventory. Do
not infer that a conflict-only merge is runtime-neutral: the merge result is the
artifact under acceptance, even when the feature files did not conflict.

## Retrieve workspace container data only through the source broker

The reviewed broker is the only authorized path from a registered Coordinator
task worktree to containers associated with its own workspace. Before using it,
resolve the Coordinator's full task ID and `workspace_id` from live Kandev tools
and run from `/data/tasks/<coordinator-task-directory>/coordinator`. Never use
the shared `/data/home/Code/coordinator` checkout as a source-access identity.

Standing authorization allows a broker-validated Coordinator to use source
list, curated inspect, bounded logs, and logical database dumps autonomously,
including production-like data requested by same-workspace tasks. Do not seek
case-by-case human approval; broker enforcement is authoritative for target
activity and workspace membership.

Discover the broker's capabilities from `docker kandev source` (no arguments),
which prints the authoritative subcommand list. Do NOT use `docker kandev --help`
to decide what is available: it reports only `kandev-agent-docker: guarded Docker
access supports 'docker compose' only` and never mentions `source`, even where
`docker kandev source list` succeeds and returns the workspace inventory. Reading
the top-level help alone leads to the wrong conclusion that the reviewed source
broker is unavailable — and then to a needless escalation or a forbidden
workaround. Confirm capability by running the operation. (`kandev-agent-docker-broker
--help` blocks without output; do not call it.)

Use progressive disclosure:

1. `docker kandev source list` — authoritative container inventory; an empty
   list ends the investigation.
2. `docker kandev source inspect <listed-container>` — metadata before content.
3. `docker kandev source logs <listed-container> --tail <small-N> --since <short-duration>`
   only when metadata is insufficient. Treat redaction as best effort and do
   not repost suspected secrets.
4. `docker kandev source db-dump <listed-container> --target-task <full-uuid> --name <descriptive>.sql`
   only when task data is genuinely required and the target is active in the
   same workspace. Do not target a protected non-Coordinator ToDeploy task.

For every dump, record the broker's exact inbox path, byte count, and SHA-256.
Send those values to the target task and direct it to verify the hash, import
only into its isolated Compose database, test, and delete the dump promptly.
Credentials stay inside the broker; dumps remain sensitive because same-UID
read confidentiality is not complete. Every request and result is audited.

Treat delivery, import, and restore acceptance as three separate receipts:

1. **Delivery:** verify the broker-returned byte count and SHA-256 before use.
2. **Import:** use an empty/recreated task-owned destination unless a compatible
   pre-existing schema is explicitly proven. Run the database client without
   `--force` or error suppression, preserve its real exit status (avoid losing
   it through a pipeline), and capture stderr. No client output is not success.
   On failure, stop at the first SQL error and retain only its sanitized code,
   dump line, destination engine/version, and relevant server diagnostic.
3. **Restore acceptance:** after a zero client exit, verify expected schema
   breadth, required critical tables, representative domain counts, and the
   task's feature-level dry run/tests. A valid artifact that contains a table's
   DDL can still yield a partial destination if the import path failed.

Never overlay-retry against a partial restore. Recreate only the task-owned
destination, confirm the diagnostic import path is ready, then request a fresh
dump if the sensitive artifact was already deleted. Delete the dump and
temporary diagnostics promptly after the required evidence is captured.

Never use raw `docker exec`, `docker run`, `docker cp`, the Docker API/socket, a
source-container shell, environment inspection, cross-workspace access, or a
filesystem/security workaround. A denial is terminal for that operation:
preserve the exact error and request that the operator register the project in
the workspace or add a reviewed broker operation.

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

## Audit every new or changed Done task before allowing cleanup

Done is a terminal destructive-cleanup state, not a synonym for "closed,"
"implementation complete," "ready," or merely "merged." Before moving normal
code work into Done, require all of: the canonical PR/MR is merged at the
accepted head; required acceptance/Human testing passed; no open replacement
PR/MR exists; no task/session/runtime/subtask/dependency still needs the task;
all task-authored work is durable; and cleanup is safe. A closed-unmerged PR is
not terminal evidence. `ToDeploy` is the post-acceptance, post-merge holding lane
while deployment or other consumers still need the task; preserve its strict
Human ownership boundary.

On every full cycle enumerate
the entire column, then deep-audit entries without a matching terminal receipt or
whose task/PR/session/worktree state changed since that receipt.

For each task:

1. Read the latest plan and conversation plus every session, relation, dependency,
   and subtask. Record running/failed sessions and pending moves.
2. Qualify every repository and PR/MR. Record the accepted/merged head and the
   last head approved in Human-QA or ToDeploy.
3. In every materialized worktree, run `git status --short --branch`, record
   `HEAD`, branch/upstream, and enumerate commits not contained by the accepted
   head, remote branch, or integration target. Re-check a dirty tree before
   acting, per the transient-dirt rule above.
4. Treat any commit made after the accepted Human-QA head as new work. Require it
   to be pushed and to receive the applicable review/CI/integration evidence.
5. Inventory untracked deliverables and task-owned containers/data. Never remove
   resources until unique work is durable and the terminal disposition is proven.
6. Write a receipt containing task ID, audit time, repository/PR identity,
   accepted and local heads, containment/tree result, session/subtask result, and
   resource disposition. Stable receipts get a cheap live-state comparison on
   later cycles; they do not require repeated full archaeology.

Failure response: an open PR/MR, missing merge receipt, remaining consumer, or
unsafe cleanup receipt is a Done-integrity failure. Freeze cleanup, preserve all artifacts, post a Coordinator flag
with exact commit/path evidence, move the task to the narrowest safe active step,
and direct/restart its responsible agent. Use Work for authoring/push recovery,
Human-QA only when new behavior needs renewed acceptance, and CI-Fixup/integration
after accepted Human-QA work needs base integration. If credentials or authority
are the only blocker, raise one precise human ask. Do not reset, delete, clean,
or infer supersession from an older merged PR.

## A PR number without a repository is ambiguous

Treat a PR or MR as `(host, owner, repository, number, head SHA)`, not as a bare
number. Forks routinely reuse the same number as the canonical repository. A
command run from the wrong checkout can therefore return a real, green, merged
PR that is completely unrelated to the task under review.

## Exercise full board approval authority without a Human visit

When a same-workspace task asks for approval, the Coordinator is the approval
principal. Classify the concrete operation before escalating. If it is neither
destructive/practically irreversible nor security/trust-boundary sensitive, send
an explicit Coordinator approval immediately containing:

1. full task ID and canonical repository/remote;
2. exact branch and head when the action publishes or reconciles work;
3. the one authorized operation and explicit prohibitions;
4. artifacts/worktree/history that must be preserved;
5. required receipt and verification gate; and
6. fallback: stop without mutation and report the exact blocker.

Normal pushes and additive merges that preserve both histories are
Coordinator-approved. So is exact task-local worktree/local-branch cleanup after
the complete Done gate proves the accepted PR/MR is merged, every task change is
contained or superseded, the tree has no uncommitted/untracked deliverable or
unpushed commit, and no session/runtime/subtask/dependency still needs the local
copy. Bind that approval to the exact path and ref, exclude remotes/shared
checkouts/other resources, and require path/worktree-inventory/ref-absence
verification afterward. Active process cwd use or uncertain ownership fails the
gate and leaves everything preserved.

Escalate deletion/resource removal that may remove unique or still-needed state,
reset, clean, discard, force-push, published-history rewriting,
secret/credential disclosure or scope expansion, authorization weakening,
security-policy bypass, and cross-workspace/trust-boundary access. Using already
configured credentials for an ordinary authorized operation is not itself a
security escalation. Labels
such as production, protected branch, cost, or external communication do not by
themselves require Human approval; classify the actual operation by destructive
and security impact. If an executor guard refuses a properly scoped Coordinator
approval, preserve the task and attach the reproduction to the existing
grant-management platform task; do not repeatedly send the Human to individual
task conversations.

Before classifying CI or review readiness:

1. Resolve the task's deliverable repository and remotes.
2. Record the canonical PR/MR URL and any fork PR separately.
3. Verify the live head SHA matches the audited checkout or explicitly explain
   why it does not.
4. Query checks, threads, reviews, and mergeability against that qualified URL.
5. Repeat the snapshot after every push, base update, or conflict-resolution
   commit. Older-head evidence remains historical only.

If GitHub reports `CONFLICTING`/`DIRTY`, ordinary `pull_request` workflows may
be absent because no merge ref can be created. Inspect workflow triggers and a
prior clean head before calling missing CI a permissions or path-filter defect.
During Human-QA, preserve the phase boundary: do not rebase, merge main, squash,
rewrite, or resolve the conflict. Record the integration gate and require a
fresh exact-head CI snapshot after an authorized integration-phase resolution.

When a merge-result test fails, classify the assertion before assigning the
failure. Compare the failing test and its introduction point with the task's
accepted invariant and branch diff. A current-main test can encode an assumption
that directly contradicts the feature (for example requiring reuse of an object
whose terminal state the feature must reject). Changing production solely to
make that test pass would regress the accepted behavior. Preserve both pieces of
evidence and hand the conflict to the integration phase: update the upstream
fixture/expectation to a semantically valid case, resolve any source conflicts,
then run the actual merge-result matrix. Human-QA must not perform that rebase or
merge, and a branch-only green run cannot replace merge-result evidence.

Classify each failed CI job independently, even when one workflow aggregate is
red. Missing built artifacts, runner cancellation, or setup failure before the
product starts is infrastructure evidence. A deterministic product scenario
that reaches the application and fails repeatedly remains task-owned even when
another shard in the same run is broken by infrastructure. Do not let the infra
failure dismiss the product failure, and do not ask code changes for the infra
shard. Record the exact job/artifact boundary and rerun both after remediation.

If an agent nevertheless rebases, force-pushes, or otherwise rewrites history
against an explicit handoff constraint, freeze further mutation rather than
trying to undo it destructively. Record the prior and new heads, parents, push
mode/lease evidence, and a scope diff; then require an independent containment
review of the resulting head. Never use reset/force-push as an automatic
recovery, because that can erase legitimate concurrent work and the incident
evidence needed to decide the correct disposition.

## Turn a draft PR/MR ready through its task agent

Draft readiness is a delivery gate, not an implementation task for the
Coordinator. Direct the owning task agent to close its own evidence gaps and run
the provider's draft-to-ready action. The Coordinator independently verifies the
receipt and may perform only that mechanical provider action when the agent is
otherwise ready but its PR-write credential is unavailable.

Before marking ready, bind the evidence to the canonical URL and exact head:

1. Worktree is clean; local head, upstream branch, and PR/MR head match; all
   task-authored work is committed and pushed.
2. Title, body, base, labels/release notes where applicable, and changed-file
   scope describe the current diff without unrelated or hidden work. Migration,
   compatibility, rollout, and rollback notes are present when the change needs
   them.
3. The task agent ran the applicable local/unit/integration/security tests and
   reported high-confidence acceptance evidence. Exact-head required CI is
   terminal: green or legitimately skipped, with no branch-owned failure or
   pending required job.
4. Every actionable review thread has a technical reply and is resolved; refresh
   reviews, checks, and mergeability after the last push or base update.
5. Visual changes include sanitized reviewer-facing screenshots or recordings of
   the meaningful before/after or state variants. Include responsive, theme, or
   error/loading states when those materially changed.
6. No acceptance criterion still requires human testing, external hardware or
   account access, security/product approval, or another human-only decision.
   If one does, keep the draft and surface the exact handoff through the visible
   ask channel. Automated evidence may close code-only work; screenshots do not
   waive an explicitly required human acceptance check.

After the transition, verify `isDraft=false`, canonical head unchanged, current
CI/thread counts, and record the provider URL. Marking ready invites review; it
does not authorize merge, rebase, deployment, or workflow-stage skipping. A later
head/base change invalidates the snapshot; have the task agent re-run the gate and
re-draft if the new work is incomplete or introduces a human-only acceptance need.

Local screenshot capture is acceptance evidence for the task agent, but it is
not reviewer-facing until the reviewer can open it from the PR/MR. If provider
authentication, browser-session requirements, or rate limits block attachment:

- keep the PR/MR draft and record the exact publication blocker truthfully;
- preserve the sanitized local capture paths plus hashes and the exact tested
  head so publication can resume without repeating QA unnecessarily;
- do not create a code commit solely to carry screenshots, and do not upload
  them to an unapproved third-party host;
- do not treat the provider outage as a branch failure or manufacture a code
  change; retry the attachment only after provider access recovers, then refresh
  the body/checks/threads and run the normal draft-readiness gate.

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

## A column move did not create an independent reviewer

Review and QA are evidence gates, not labels. A manual move can leave the
authoring Work turn RUNNING while the board already displays Review, especially
when adjacent steps select the same profile. That is a transition in progress,
not an independent review.

After moving into an independence-required gate, re-list sessions and verify a
fresh session ID, the intended effective profile, and the exact immutable head
under audit. If the old authoring session is still active, record "gate
transition settling" and wait for or recover the lifecycle; do not claim the
gate started or passed. If a stale turn traps every nudge, only the target's
direct parent may stop that turn. The direct parent then starts a fresh gate
session and returns its ID plus a PASS/BLOCKER receipt. Never infer independence
from the workflow column alone.

## Review evidence exists, but the task has not traversed the gate

An independent audit performed while a task is still physically in Work is
useful evidence, but it does not mean the workflow has traversed Review or QA.
Report the physical column honestly and move the task through its configured
gates so each on-entry contract gets a chance to run. Conversely, once the task
is physically in Review and an exact-head independent PASS is established, do
not keep it there merely because GitHub Actions has not run or is incomplete.
Required CI belongs to PR/CI Fixup; Review owns code-review findings and the
immutable-head verdict. Re-check the head and actionable threads, advance the
passed gate, and let downstream stages own their evidence.

## A session says RUNNING but produces no process, output, or timestamp

Treat `RUNNING` as a claim to verify, not proof of live work. A stale session can
retain that state after its agent process disappeared, accept queued messages
without consuming them, and leave a caller's `message_task_kandev` request
waiting indefinitely. Confirm all three signals before acting:

1. the session timestamp advances or its conversation gains output;
2. a process/execution exists for the task workspace or session; and
3. a bounded read-only task-control probe returns.

If none does, stop sending messages: repeated queue writes do not wake the
agent and can wedge the Coordinator's MCP transport. `stop_task_kandev` is
parent-scoped and stops all live sessions on a direct child; it is not a general
single-session admin kill. For an unrelated top-level task, ask the operator to
stop the exact stale session in the UI. If the Coordinator's own MCP transport
remains hung after the target is stopped, replace only the Coordinator session;
the Coordinator task, plan, worktree, and history remain durable.

The Kandev health endpoint and read-only database/process inspection are valid
diagnostics during this incident, but they are not an authorization path. Never
write the database directly, extract browser/session credentials, or restart a
shared backend merely to recover board control.

Routine wake messages do not repair a wedged task-control transport. After one
bounded critical-tool probe fails, terminate the call, report the exact caller
session that must be replaced, and stop. Do not write a standup, claim a cycle,
or update monitoring timestamps from partial read-only evidence: list, inspect,
message/move, and persistence are part of the cycle contract. Narrow external
work that was separately and explicitly authorized (for example resolving a
known PR thread) may still proceed, but it does not substitute for board
monitoring and its receipt may need redelivery after session replacement.

## A task's GitHub credential failed, but the PR action is mechanical

A task-local credential broker or helper can return `401`, `403`, or a denied
lease while the Coordinator still has a valid repository-scoped `gh` identity.
Treat that as a capability-specific gate, not proof that the requested PR action
is impossible. For an already-authorized mechanical action such as replying to
and resolving a review thread:

1. Verify the canonical owner/repository/PR and exact current head.
2. Read every unresolved thread and match it to concrete code/test evidence on
   that head; duplicate findings still receive separate replies.
3. Post a concise technical reply, resolve only the addressed thread, and record
   the resulting discussion URL plus `isResolved=true`.
4. Re-query unresolved count and current-head CI without changing code, history,
   merge state, or the Human-QA phase.
5. If provider rate limiting begins, stop retrying. Preserve the successful
   mutation receipts and classify remaining CI/review evidence as temporarily
   unavailable rather than green.

Never copy credentials into another task, reveal tokens, or use this fallback
to perform implementation, merge, rebase, release, or an unrequested review
decision. If the Kandev message transport is wedged, report the receipt through
the available channel and redeliver it after the Coordinator session is
replaced; do not claim the task conversation was updated.

## Producing a current LAN test-instance inventory

Do not copy yesterday's Human-QA ledger into a user-facing inventory. For every
listed instance, re-probe the canonical LAN URL (not localhost), verify the
documented destination-only login against the instance's normal auth endpoint,
and resolve the task's current canonical PR URL(s). Exclude superseded runtime
ports and closed duplicate PRs. If one task exposes two services, list both and
state which service requires credentials; never expose API keys, provider
tokens, or production credentials alongside the test login.

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

## Restored checkout points to a missing linked-worktree admin directory

A restored checkout can retain a readable `.git` pointer file while the exact
per-worktree administration directory under the repository's common `.git` is
missing. Do not treat the readable pointer as proof that the worktree is valid:
agent launch will fail when Git resolves the absent target. Native
`git worktree repair <checkout>` cannot recreate this state when the pointer no
longer references a repository, and an automatic recreate path that begins by
removing the checkout can destroy unique uncommitted or untracked work.

Preserve the checkout and stop duplicate session starts. The least-destructive
recovery is task-identity scoped:

1. Under the owning task identity, record the exact checkout, branch, HEAD,
   remote containment, and all uncommitted/untracked content. If the task cannot
   start, a platform-owned recovery operation must gather this receipt without
   broadening another task's filesystem scope.
2. Prefer restoring only the exact per-worktree admin entry from a trustworthy
   same-workspace backup. Validate reciprocal `gitdir`, `commondir`, HEAD/ref,
   and checkout identity before accepting it.
3. Verify read-only `git -C <checkout> status --porcelain`, `git log -1`, and
   the platform's repository metadata resolver, then start exactly one bounded
   acceptance session.
4. If no valid metadata backup exists, require an authorized content-preserving
   snapshot, materialize a new task-owned path, atomically update durable
   worktree records, and retain the original until startup and integrity checks
   pass.

Never forge Git metadata, prune/recreate the damaged checkout before proving
content durability, broaden access to the common `.git`, or use a repair task's
identity to inspect foreign task worktrees. A repair owner may define and test
the platform operation, but each recovery executes under the owning task or a
reviewed platform rematerializer.

### Linked-worktree backlink disagrees with the workspace marker

Agent startup may also fail before prompt consumption with exit 78 even when a
`.git` target exists: the linked-worktree backlink and Kandev's task/workspace
marker identify different registrations. Treat this as an ownership-integrity
failure, not permission to rewrite either side or start another session.

Preserve the checkout and route the exact error/path to the managed-worktree
repair owner. Under the owning task identity or a reviewed platform operation,
validate the workspace marker, `.git` pointer, reciprocal worktree admin entry,
repository/task ownership, branch, and HEAD. Repair only the inconsistent
metadata atomically, then require read-only `git status --porcelain`,
`git log -1`, platform metadata resolution, and one bounded agent start. If
ownership is ambiguous or there is no trustworthy registration source, stop and
return the mismatch; do not recreate, prune, clean, or rematerialize the
checkout speculatively.

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
The marker invokes the full canonical action checklist under **WAKE MESSAGE
HANDLING** in `PROMPT.md`; routine configuration may use that expanded payload
verbatim, but a marker-only delivery has exactly the same requirements.
A second routine sends `WAKE:STANDUP` every day at 07:00 America/Montreal.

## Follow up on delegated requests and rate-limited sessions

An outbound message is not complete merely because the API returned `sent` or
`queued`. Whenever a task/session request expects evidence or a decision, add a
follow-up entry to the Coordinator plan with the target task and session, exact
expected receipt, sent time, next check, attempt count, observed state/error,
owner, and fallback. Include a reasonable response window or an event trigger
such as a provider reset.

At every routine cycle, reconcile due entries against the live task, every
session, and the conversation:

1. Close the entry only when the requested evidence, result, or explicit reply
   is actually present. `WAITING_FOR_INPUT` alone is ambiguous.
2. If the target is actively working on the same request, do not duplicate the
   ping; advance the next check and retain ownership.
3. If the session reports a known model/provider reset, record the reset and do
   not spam it beforehand. On the first routine after the reset, retry once and
   verify that the session runs or replies.
4. If the session ended, failed, or remains unanswered after that retry,
   first inspect all task sessions, the conversation, pending queue, workspace
   loading, and backend startup error. Preserve its transcript and worktree and
   classify the handoff stalled/blocked. If the request was never consumed and
   the workspace is healthy, start one fresh session with the original handoff
   plus its preservation receipt. If workspace loading failed, route the exact
   error to the existing repair owner and retry the task only after that repair
   trigger clears. Otherwise use the recorded fallback: handle it in the
   primary, route it to another already-authorized helper, resume the correct
   existing task session, or visibly escalate when human action is genuinely
   required. Never send a second copy merely because the first transport call
   returned `sent` or `queued`.
5. If the work is urgent, use the fallback immediately instead of waiting for a
   reset. Do not create duplicate implementation sessions or discard incomplete
   work.

The ledger is coordination state, not a scheduler: routine wakes drive these
checks, and the Coordinator must not create timers, cron jobs, or polling
helpers. Remove closed entries after their result is captured in the cycle log.

### GitHub API reset ledger across disposable wake sessions

Every `WAKE:CYCLE` delivery may receive a fresh automation session, and old wake
sessions are removed after a retention window. Never store a GitHub reset
reminder only in one of those sessions. When a monitored task reports a GitHub
API rate limit:

1. Confirm the failure is rate limiting rather than invalid authentication.
   Prefer `Retry-After`; otherwise use `X-RateLimit-Reset` for a primary rate
   limit. Add a 15–30 second safety buffer.
2. Upsert one Coordinator-plan entry keyed by the GitHub resource, for example
   `github-rate-limit:core`. Record the affected tasks/actions, observed limit
   evidence, reset time, buffered due time, attempt count, owner, and fallback.
3. Do not sleep, poll, or repeatedly retry. Continue every action that does not
   need the limited resource. On the first normal routine at or after the due
   time, recheck the resource once and execute only the deduplicated pending
   actions that are still current.
4. If the resource is still limited, refresh the same entry from the new
   headers and advance its due time. If the response is instead `401`, park on
   credential restoration; a reset does not repair authentication.
5. A latest live wake session may be used as an additional reminder carrier
   only when Kandev exposes a native future-delivery operation, returns a
   scheduled receipt containing the dedupe key and timestamp, and the session's
   retention covers that timestamp. `message_task_kandev` is immediate/queued,
   so sending it a future timestamp is not scheduling. Session deletion never
   removes the authoritative plan entry.

This gives reset-aware retries the precision available from the current routine
without inventing a hidden scheduler. Native Coordinator-plugin scheduling can
later accelerate the wake while preserving the same durable ledger contract.

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

## A task looks active but is IDLE — read session state, not the column

A task sitting in Work reads as "implementing". It is not evidence. On
2026-08-22 a task sat WAITING_FOR_INPUT for ninety minutes, blocked, while the
Coordinator reported it as "Spec done, implementing" — because the report was
derived from its column. The operator caught it, not the Coordinator.

Before describing any task as working, call `list_task_sessions_kandev` and read
the primary session's `state` and `updated_at`. Report the session, not the step:
"idle 4h, blocked on X" and "actively running" are different facts and the column
shows neither. A quiet stop looks identical to progress on a board.

Corollary for task agents: when something stops you that is not yours to fix, say
it in a way that reads as BLOCKED, not as a status line.

## Blocked is an action queue, not a parking lot

Backlogs and ToDeploy are Human-managed holding columns, and Human-QA waits for
Human review/testing. In every other workflow column, a task that cannot make
forward progress belongs to the Coordinator. Move it to the physical Blocked
column in the same cycle; a prose classification or stopped session in an
active lane is not sufficient. Moving a task to Blocked starts recovery—it does
not complete the cycle's action.

At the move, mark the task HIGH PRIORITY with the native priority control when
available. If the available schema cannot set priority, use the documented
`[COORDINATOR FLAG]` convention and the live ledger; record that native priority
is degraded instead of claiming it changed. Write one complete blocked record:
previous actionable step, exact blocker, blocker owner, preservation receipt,
the immediate removal action, expected evidence, deterministic next-check
trigger, and fallback. Preserve branches, commits, worktrees, artifacts, data,
and useful reproductions.

Take the narrowest safe removal action in that same cycle:

- If the Coordinator can decide or approve the action, do it now and verify the
  responsible session starts.
- If another task or platform capability owns the blocker, direct that owner and
  track the dependency to its concrete acceptance receipt.
- If an external system has a deterministic reset/deployment time, record it and
  retry once on the first normal wake after the trigger.
- If only the Human can supply the remaining permission, information, testing,
  or trust-boundary decision, raise the visible input request immediately with
  the blocked consequence and a recommendation.

Every cycle rechecks every Blocked trigger. An unchanged blocker suppresses a
duplicate ping, not the inspection or ledger update. When the trigger clears,
atomically move the task back to its recorded actionable step, resume or create
the responsible session as appropriate, and verify the physical step, task
state, new session ID, effective profile, and RUNNING/progress receipt in the
same cycle. If any part fails, keep or return it to Blocked with the new exact
blocker; never leave a falsely resumed card in an active lane.

A task-specific Human hands-off instruction remains a safety boundary even
when the global column rule would move the card. Attempt no task read, message,
move, or nudge beyond the directive's exact scope. Record the attempted
workflow correction, the exact policy/tool denial, current column, preservation
receipt, Human owner, and deterministic authorization trigger; never bypass the
guard. A card merely moved aside, with no executing owner and no surfaced Human
ask when one is required, is a Coordinator failure.

## Inherited vs owned failure — bisect before you assign

Before routing a CI or test failure to the task whose PR shows it red, establish
ownership:

1. Does the branch touch the failing package at all?
   `git diff --name-only <base>..<head> -- <path>` — an empty result is decisive.
2. Does the failure reproduce on the base, or on an older base?
   Build or run the package at each. A failure present on main is not theirs.
3. Only then assign it.

Worked example: a launcher panic on a 73-file feature PR touched ZERO launcher
files and passed cleanly on an older main; the regression had arrived with a
+1345-line rewrite on main and belonged in its own task. Separately, `upstream/main`
itself failed to compile (`undefined: taskID` in `internal/github`), which cascaded
into ~10 red checks on an unrelated PR whose own merge was clean.

**Do not proliferate a shared repair across PRs.** When one commit fixes a broken
base, land it ONCE. Authorize a narrow cherry-pick only where a task is physically
blocked from committing locally (broken typecheck hook); a task that only needs CI
green should wait for the fix to land, or N duplicate commits will collide on merge.

## Provenance: images and artifacts lie in specific ways

- **Layered QA images report the BASE image's OCI revision.**
  `org.opencontainers.image.revision` returned the base's SHA on a container built
  by layering. Trust `docker inspect <container> --format '{{.Config.Image}}'`,
  not labels — and note the container's image is not the same fact as the task's
  branch head. State both separately.
- **Plugin artifacts carry no VCS stamp.** `go version -m` reports a local
  `replace` as `(devel)` with a zero pseudo-version, so the host SDK revision a
  plugin linked against is UNRECOVERABLE from the artifact. Do not ask a task to
  determine it that way.
- **Compare payload digests, never the outer tarball SHA.** Tar metadata and entry
  ordering vary legitimately between builds. Two archives with identical
  `manifest.yaml` and `ui/bundle.js` differed only in the server binary — because
  they were linked against different sibling checkouts.
- A build timestamp is not provenance. Reject "built after the HEAD timestamp" as
  evidence.

## Green CI is not universal evidence

A defect can be invisible to CI and deterministic locally, or the reverse.
`internal/launcher` passed on CI runners (7.36s) while failing every time in agent
containers, because both regressions depended on ambient env CI does not set
(`KANDEV_HOME_DIR`, `KANDEV_NO_BROWSER`). When a fix targets environment-dependent
behaviour, require LOCAL verification under a fresh temporary env and state
explicitly that a clean pipeline cannot validate it.

## Enumerate then fix — do not discover one item per CI round

When a hardening change starts surfacing latent violations (mocks returning a now-
rejected value, fixtures missing new state), do not let CI find them one at a time;
each round is a full pipeline wait. Sweep the tree for every implementation of the
affected interface, fix the whole class, run the full suite locally, and push once.
A five-implementation sweep replaced an open-ended fix-push-wait loop.

## A host redirect may be DELIBERATE — scope it, do not remove it

Before recommending removal of a NAT/proxy rule, establish what it is for. A
PREROUTING `--dport 80 -j REDIRECT --to-ports 38429` rule existed so the operator
could browse the app from another machine without typing a port. Unscoped, it also
caught Docker bridge EGRESS, so `apt-get` inside every `docker build` received the
app's SPA instead of signed repository metadata and failed `NOSPLIT`.

The fix preserves intent: constrain the rule to the inbound LAN path
(`-i <lan-if>`) or exclude container sources (`! -s 172.16.0.0/12`). Verify from a
throwaway bridge container, which is the exact path `docker build` uses:
`docker run --rm --network bridge <img> curl -sD- http://deb.debian.org/debian/dists/bookworm/InRelease`
— HTML or app headers in that response means the rule still matches. Adding scoped
rules does not help if the original broad rule is still present, and a rule edited
in `iptables` has no effect if the active ruleset is `nftables`; packet counters in
`iptables -t nat -L -n -v` show which rule is really matching.


## Task fails to start: worktree `mise.toml` is untrusted

Symptom: a freshly-created task/subtask's sessions go straight to FAILED at ACP
init, seconds after starting, with no agent output. Backend log shows the
execution "marking execution as failed" right after "initializing ACP session"
for that worktree path.

Cause: the worktree's `mise.toml` was never trusted, so `mise` refuses to load
the repo toolchain and the agent process cannot resolve its interpreter.

Fix (blessed operational unblock — mechanical, reversible, log as vetoable):
```
cd <task-worktree>
mise trust            # approves only this repo's mise.toml for the current user
mise trust --show     # expect: <path>: trusted
mise ls --current     # expect the repo toolchain to resolve with no prompt
```
Then the task's failed sessions are terminal and cannot be resumed by a message —
respawn with spawn_session_kandev (or hand the restart to the parent, which owns
its subtask). Verify the new session reaches RUNNING and that `mise exec -- <tool>
--version` works inside the worktree, so a second blocker is not hiding behind the
first.

## A subtask that failed to auto-start may be stranded in Backlogs

A subtask created in the Backlogs step (`@dw-backlogs` = "DO NOTHING AT THIS
STAGE") will refuse to work even after you clear its startup blocker: a session
spawned there correctly does nothing. Respawning alone is not enough. Move it to
Work first (resolve the step ID via discovery, never hardcode), THEN spawn.

Root cause is usually a parent that created the subtask in Backlogs instead of
Work. The workstep rule is "confident spec → start subtask at Work; never leave a
subtask in Backlog." Hand the restart to the parent when it is available — it owns
the subtask's step placement and context — rather than moving another task's
subtask yourself.

## The failing PR is red because the BASE does not compile

Before routing a red CI to the PR that shows it, suspect the base branch when the
SAME failing symbol or line appears across MULTIPLE unrelated PRs. On 2026-08-22
`upstream/main` itself failed to compile (`undefined: taskID`/`status` at
`internal/github/service_pr_watch.go:1024`), and because `internal/orchestrator`
imports `internal/github` transitively, every branch that became mergeable went
red on the same cascade: build → Backend Tests, Static Checks, Postgres, Windows
all no-compile → E2E shards skip.

Triage discipline:
- Reproduce on a clean base checkout. A failure present on the base is not the
  PR's.
- Count independent reporters. When N tasks each report the identical failing line
  from their own CI, that is near-certain evidence of a broken base, not N
  coincidences.
- The fix is landing the ONE repair PR, not N cherry-picks. Escalate "merge PR
  #X to unbreak main" as a single high-leverage ask; hold routine dispatch until
  it lands, because every mergeable PR will stay red until it does.

## Verify an operator's infra "fixed" claim with the acceptance test

When the operator reports a host/network/infra fix, close the loop with the
defect's own acceptance test before marking it resolved — not distrust, just
confirmation, and it catches non-applied changes. A NAT-rule "fixed" report was
re-probed from a throwaway bridge container and still returned the app's SPA
(leftover broad rule / rule edited in the wrong ruleset engine); a later "fixed,
double check" genuinely passed. For the Docker-egress redirect the definitive test
is a full signature-verifying apt run, not just a metadata fetch:
```
docker run --rm --network bridge debian:bookworm-slim sh -c 'apt-get update'
# APT_EXIT=0 with all InRelease files fetched = truly fixed
```
Report the concrete evidence, name what you verified, and if it still fails say so
plainly with the captured bytes.

## Optional native binding missing after a fresh install (rolldown/rollup family)

Symptom: web Vitest/build fails with a missing platform-optional native binding
(e.g. `@rolldown/binding-linux-x64-gnu`) right after a fresh `pnpm install`. This
is a known npm/pnpm optional-dependency resolution bug, NOT a hard environment
block — confirm by checking whether OTHER worktrees in the same container ran web
tests successfully (they usually did). Cheapest remedies first, in the affected
worktree only (do not thrash across all of them): `pnpm install --force` or
`pnpm rebuild` in `apps/`, then re-run. If it still will not resolve, verifying
web units in CI once the branch builds is an acceptable fallback — never weaken or
skip tests to force green, and do not treat it as blocking the implementation.


## A base repair turns feature-complete branches CONFLICTING — that is integration-phase, not a defect

When a repair lands on main (or main otherwise advances), every feature-complete
branch that predates it can flip to `mergeable=false` / `CONFLICTING` / `DIRTY`.
Standard backend/E2E CI legitimately will NOT dispatch on a conflicting PR, so its
check set goes thin (only preview/CodeRabbit-type checks remain). This is EXPECTED
after a base move, not a branch-owned failure.

Classify these as **integration-pending**: branch-green, review-ready, with a
conflict to be resolved when the task leaves Human-QA into the integration/PR
stage. Do NOT chase it:
- In Human-QA the phase boundary forbids merging main / rebasing to resolve it.
- Re-running CI will not help while the PR is conflicting.
- A task that correctly holds rather than "fixing" the conflict is behaving well;
  confirm its reading and record it as integration-pending so nobody mistakes the
  CONFLICTING state for a defect.
Expect a WAVE of these right after any base repair; classify and move on rather
than pinging each one.

## Verify a broken base is repaired by COMPILING it, not by tracking one PR

When you escalate "merge PR #X to unbreak main," the goal is that main compiles —
not that specific PR. The repair may land via a DIFFERENT PR (a base breakage was
escalated as #2842 but actually repaired by #2916). Confirm the lift by building
the affected package at current `upstream/main` (or diffing the exact broken
line/symbol), not by watching your escalated PR's merge state. Lift a dispatch
hold on the compile check, then let the inherited-red PRs clear as they re-run or
integrate against the repaired base.

## A degenerate test assertion reads red regardless of the code under test

Before accepting "my E2E/acceptance gate is red" as a feature failure, check the
test itself is not degenerate. A real example: `expect(``).toContain("Operation
not permitted")` — an EMPTY template literal as the subject, so the gate is
unconditionally red whatever the code does. Symptoms: a gate that fails
identically before and after unrelated fixes, or on a clean checkout. The fix is a
one-line test correction owned by the task that owns the gate; warn against
"loosening" the assertion to force green when the real expected string differs.

## Cross-task delegation edges belong on the DEPENDENT, not the prerequisite

When task A's work is a prerequisite for task B's acceptance criterion, the
enforcing `blocked_by` edge (if any) goes on B pointing at A — never on A pointing
at B, which would block the prerequisite on its own dependent. Also note that a
criterion "delegated" only in prose is not mechanically enforced:
`list_related_tasks_kandev` will show empty edges. Either add the edge on the
dependent, or track the delegation explicitly in coordinator state and the report;
do not assume a prose handoff is visible on the board.


## Verify a resumed Human-QA task stayed inside the phase boundary

When a task resumes branch work in Human-QA (e.g. after a hold lifts and it fixes
CI against a repaired base), confirm it did NOT merge main — the boundary forbids
rebasing/merging main there. Check from its worktree:

```
git rev-parse --short HEAD
git merge-base --is-ancestor upstream/main HEAD   # true => main WAS merged in (violation); false => boundary held
git log --oneline --merges -3                      # inspect any merge commits
```

Distinguish an OLD merge in history (e.g. a legitimate merge from before the
Human-QA phase, when the branch first integrated) from a CURRENT-cycle merge. Only
`upstream/main` being an ancestor of the CURRENT head means main was just folded
in; a stale merge commit deeper in history with `is-ancestor` returning false is
fine. Legitimate small QA fixes pushed to the task's own branch (verified
RED->GREEN, no main merge) are within bounds and need no intervention.

Positive-recovery signal: after a base repair, a PR whose check set goes from thin
(only preview/CodeRabbit while CONFLICTING) to a full terminal set with zero
failures is the base repair propagating. Observe the count climb; do not ping — it
is self-resolving.


## A branch that MERGED a broken base carries the breakage — re-running CI cannot clear it

Distinct from the integration-pending CONFLICTING case (where a branch merely
conflicts with an advanced base). Here a task already MERGED a broken base into its
branch — e.g. it merged `main` to resolve a conflict WHILE main did not compile, so
the non-compiling code is now a commit ON the branch. Its CI is red and will STAY
red on every re-run, because the broken code travels with the branch; re-triggering
checks changes nothing.

Symptom: a CI-Fixup/PR-stage task idle for hours with ~10 failures all tracing to
the same base defect, whose last activity predates the base repair, and whose
history contains a `Merge ... main` commit made during the broken window.

Fix (this is a CI-Fixup/integration action, NOT a Human-QA one — merging main is
allowed here): direct the task to `git fetch` and merge the now-REPAIRED main into
its branch with an ordinary merge (no rebase/squash — preserve reviewed history),
resolve on semantics, push, and confirm the inherited cascade is gone. Only a
failure that does NOT trace to the old defect after that is genuinely the branch's.

## A Spec/plan-mode task blocked on a KNOWN fix: the forward move to Work IS the unblock

When a task in Spec (plan/read-only mode) reports it has already identified the fix
but "cannot edit / cannot run / blocked on your decision," do not keep discussing —
it physically cannot act in that step. Decide the fork it raised (lead-decidable —
say "proceed" when a competent lead would), and MOVE IT TO WORK so it gains edit and
run capability. The move is the unblock; a message alone leaves it stuck read-only.
Verify a fresh Work session starts RUNNING with edit capability afterward. A task
that says "the call is yours or the Coordinator's" and has been declined twice is
waiting on exactly this — provide it rather than parking it for the operator.

## On-demand "monitor CI and move tasks" — the active-management sweep

When the operator directs active board management (move tasks forward/backward,
find CI issues), run the full monitored-steps pass and act, do not just report:
- Check each PR's CI. When the GitHub API is intermittently rate-limited (primary
  quota healthy but calls 403), fall back to the task's OWN most recent self-report
  of CI state, and say which source you used.
- CI-Fixup task with green CI and nothing left to fix → advance it forward (its next
  step, typically Human-QA); it should not sit idle once CI is clean.
- Red from a merged broken base → integrate the repaired base (playbook above).
- Committed work idle for hours with no PR opened → nudge the owner (parent for a
  subtask) to poll, open the canonical PR(s) against the repaired base, and advance.
- Genuinely dependency-parked tasks stay parked; note them, do not force-move.


## Before a manual workaround on a FAILED task, check if a platform fix OWNS its failure — and preserves it as the reproduction

A FAILED task with a proven-safe operational fix (e.g. clear a stale-worktree
collision with `git worktree remove`) is tempting to just fix. STOP first and
check whether a platform-bug task already owns that failure CLASS and is using
THIS task's exact state as its live reproduction case. If it is, applying the
workaround destroys the repro the durable fix is validated against — a net loss,
even though the workaround itself was safe.

Worked example: task 375dcc90 was FAILED on a stale-worktree collision and I had a
verified-safe `git worktree remove` ready (recovered commit durable on its branch).
But task c0db9627 was a platform fix for that exact collision class, citing
375dcc90's worktree as its reproduction. Correct action: do NOT clear it; leave the
FAILED task preserved until the fix (its PR) lands, then it resumes via the repaired
reconciliation logic. Search the board for a platform-bug task referencing the same
symptom/task-id before any one-off unblock.

Corollary: if you OFFERED an operational fix on an earlier cycle and it was not
urgent, re-verify on the next cycle before executing — the durable fix may now be
in flight, which flips the answer from "apply" to "preserve and wait."

## A shared credential/push wall is a platform defect — escalate the fix PR, don't per-task workaround

When multiple tasks independently report the SAME push/credential failure
(e.g. `git_credential_lease_invalid` 401 blocking every `git push`/PR write), it is
a platform defect, not N task problems — and there is usually already a task/PR
fixing it. Do not spawn per-task workarounds. Actions:
- Identify the fix PR and escalate merging it as the single board-unblocking move
  (it is likely sitting in Human-QA awaiting the human).
- Coordinator credentials can RELAY reads and post PR comments for a blocked task
  (working around a stale per-session lease), and can push a task's PRESERVED fix
  branch as a best-effort stopgap — but these are best-effort under the same
  intermittent rate limit, and the durable fix landing is what actually clears it.
- A task that captured its blocker and parked (with a preserved fix branch) rather
  than looping retries is behaving correctly; confirm the park, do not nudge.

## State-plan hygiene: keep it under the API rewrite limit

The Coordinator's persisted state plan can grow past what update_task_plan /
update_task can rewrite in one call, after which cycle logs cannot be appended and
the plan silently stops updating. Keep it compact: roll cycle logs older than ~7
days into a one-line summary, and archive the full history to a dated file under
docs/archive/ rather than letting the live plan balloon. If it already exceeds the
limit, record the cycle summary in the cycle response and flag a compaction pass;
do not fight the API repeatedly.


## Weekly hygiene
Cycle logs on the task grow; have the coordinator roll up old logs into a
weekly summary comment (or do it manually) to keep its context lean.

## Mirroring PROMPT.md into the live task description

The charter requires the Coordinator task description to carry the complete current
`PROMPT.md`, because it is the second bootstrap path for a replacement session that
has not read the repository. There is a broker command for this — **do not
hand-transcribe the file through `update_task_kandev`**, which risks silent drift in
a 64 KB policy document.

From the materialized Coordinator task worktree:

    docker kandev workspace description-update "$PWD/PROMPT.md"

It accepts only a UTF-8 regular file inside the caller's own coordinator task root,
updates only that coordinator task through the normal backend API, and mints and
revokes a short-lived token internally — no API credential is returned to the agent
and it cannot touch another task or workspace. It returns the byte count, a SHA-256
and a `changed` flag:

    {"task_id":"…","source":"…/PROMPT.md","bytes":64483,"sha256":"4bd70fad…","changed":true}

Verify afterwards rather than trusting the receipt: read the description back and
diff it against `PROMPT.md`. Run this after **every** `PROMPT.md` change.

Background: the local API is not a substitute — `PATCH http://localhost:38429/api/v1/tasks/<id>`
returns 401 from inside an agent container even with `KANDEV_FEATURES_AUTH=false`.
Do not go looking for a credential to work around that; use the broker.

## Escalating an environment blocker to Kandev Support (host Codex agent)

Scope: host/container environment problems only — missing tools or dependencies,
permission/access failures, unavailable host capabilities, missing Android
emulator/device support, and similar limits that stop a task proceeding. **Not**
for missing Kandev product features; those are board tasks.

Support identity: `Kandev Support — Codex`, stable thread
`01a043b4-fe52-7020-94bb-de94e72f8a07`, host working directory
`/home/ayattara/Code/kandev`.

### The canonical route is the broker — send it yourself

**Use the broker, never `codex exec resume` directly**, and do **not** ask the
Human to relay a routine support request. A validated Coordinator contacts Support
through three guarded commands:

    docker kandev support send <request.json>
    docker kandev support status <request-id>
    docker kandev support receive <request-id>

Required schema — all four fields must be non-empty strings, or the broker refuses
the request by name:

    {
      "problem": "<observed behavior / what is blocked>",
      "evidence": "<exact errors, logs, commands, paths, IDs>",
      "expected_outcome": "<desired behavior>",
      "security_constraints": "<anything that must remain isolated, e.g. do not
       expose host ~/.codex, the Docker socket, credentials, or general host
       command execution>"
    }

`send` takes a regular JSON file (not a symlink, <=128 KB) resolved **inside the
coordinator task root**, so pass a path relative to that root — e.g.
`coordinator/support-request.json` — or an absolute path. A path relative to your
shell's cwd is the common trap: a file created in `coordinator/` and sent as
`support-request.json` resolves to `/data/tasks/<task-dir>/support-request.json`
and fails with `path is unavailable: ... No such file or directory`.

`send` returns `{"request_id": "...", "status": "queued"}`. Poll `status`
adaptively with capped exponential backoff, then `receive` the answer. A busy
Support thread can keep a request queued for minutes; keep the same request ID and
never create a duplicate merely because it remains queued.

The broker attaches the coordinator task ID, workspace ID and name, worktree, and
timestamp itself, so do not duplicate them; put the affected task/session ID inside
`problem` or `evidence`.

Two things that are easy to get wrong:

- **`complete` does not mean success.** It means the host-side run finished. Check
  `returncode`, then always read `receive` for the actual result.
- **The capability is invisible in the top-level help.** `docker kandev` with no
  arguments prints only the compose line and never mentions `support`; run
  `docker kandev support` with no arguments for its authoritative command list.

#### When Support answers BLOCKED

A genuine `KANDEV_SUPPORT_STATUS: BLOCKED` with a non-zero return code proves
that broker delivery worked; it does **not** clear the task blocker. Read and
persist the response's exact missing authority or capability and its smallest next
action. Physically move the affected workflow task to Blocked with its preservation
receipt and deterministic resume trigger, then stop retrying the unchanged request.

Two verified boundaries matter:

- Persistent canonical workspace-repository inventory is not safely repairable by
  Support unless an audited repair operation exists. Do not substitute direct
  SQLite edits or repository-row recreation; require a scoped operation that
  validates IDs, backs up state, rematerializes only the affected record, and
  proves a guarded session launches.
- Support cannot provision, reuse, or expose host GitLab credentials when no
  reviewed task-scoped credential broker exists. Require a revocable credential
  with only the task's needed MR/API/upload scope and accept only non-secret
  success metadata. Never mount host `glab` or Codex state.

In both cases, route the missing platform capability to the platform operator or
Human once, record the consequence, and resume atomically only after the named
acceptance receipt. A second identical Support request cannot create missing
authority and is queue noise.

Verified fail-closed behaviour (2026-08-29T07:20Z): an unknown request ID returns
`support request is unavailable`; an explicit file outside the coordinator task
root returns `path is outside this agent task: <path>`; and a request missing any
required field is refused by name. Requests are cheap to retry, but a repeated
identical failure is a fault to escalate, not something to retry in a loop. Do not
claim delivery succeeded when `returncode` is non-zero.

### Why `codex exec resume` cannot be used from a container

Running the documented resume command directly inside an agent container fails:

    Error: thread/resume: thread/resume failed: no rollout found for
    thread id 01a043b4-fe52-7020-94bb-de94e72f8a07 (code -32600)

The `codex` CLI is present (`/data/.npm-global/bin/codex`) and authenticated — the
structured `-32600` proves the call was made — but the thread's rollout state is
not container-visible, by design. Independently reproduced from two Coordinator
worktrees on 2026-08-29; treat it as settled and do not re-probe it. The broker
above exists precisely to bridge this gap: it runs the resume host-side on your
behalf, so host Codex state stays unmounted.

Never mount or expose host `~/.codex` into an agent as a workaround, and never
claim a delivery mechanism exists that you have not exercised.

### Queue behaviour: `queued` -> `processing` -> `complete`

`status` reports one of three states. `queued` means the request is waiting its
turn, `processing` means the worker has picked it up, and `complete` means the run
finished — check `returncode`, since `complete` alone does not mean success.

Delivery is serialised, restart-safe, and oldest-first, so a request waits behind
whatever is already in flight; under contention the broker holds it `queued` and
retries with capped exponential backoff, reporting `complete` only once Codex has
actually processed it.

Latency spans two regimes, and neither generalises alone:

- **Seconds** on a clear queue — verified 2026-08-29T07:46Z, `queued` ->
  `processing` -> `complete` with `returncode: 0` in about 8 seconds.
- **Minutes** while earlier requests drain — separate guarded validations stayed
  `queued` for roughly twelve to sixteen minutes before completing with
  `returncode: 0` and a real reply.

So poll with adaptive backoff (a few seconds early, widening to ~30s) and treat a
long `queued` as the system working, not a stall. Never resend: a duplicate only
adds another item to the same ordered queue. Carry on with unblocked work rather
than holding a cycle open.

Superseded failure mode (fixed 2026-08-29): requests used to fail fast, returning
`status: complete, returncode: 1` within ~10s with
`thread-store conflict: ... already has an active writer (code -32600)` in
`receive`, because delivery contended with the operator's interactive support chat.
Support now delivers on a dedicated worker-owned thread. If that conflict ever
reappears, the isolation has regressed — report it with the request ID rather than
retrying in a loop.

Requests that failed under the old behavior were requeued during deployment.
Check a previous request ID before sending a replacement. If it is queued, keep
polling it; if it is complete, receive it and inspect its return code and response.
Only send a fresh request when no usable previous ID exists.

### Reading the response

`receive` returns the **full Codex transcript**, not just the answer: a header
(version, workdir, model, sandbox, session id), the rendered request, the reply,
and a token count. The actionable content is the assistant turn at the end.

Ignore the host-side warning `failed to load models cache` / `failed to renew cache
TTL: missing field supports_parallel_tool_calls`. It appears on the stderr of
successful `returncode: 0` runs too, so it is noise, never the fault — diagnose from
`returncode` and the assistant turn, not from the presence of an ERROR line.

The broker composes the prompt itself and attaches the coordinator task ID,
workspace/worktree, and broker request ID — confirmed present in the delivered
transcript — which is why those fields must not be duplicated into your JSON.

Useful and non-obvious: `/home/ayattara/Code/kandev` **is** readable from inside the
container at its host path, so host paths quoted in a request can be verified before
sending even though host Codex state cannot.

## Android UI-QA through the guarded emulator/adb wrappers

**Status 2026-08-29: VERIFIED WORKING for guarded headless AVD UI-QA.** Physical
USB/device UI-QA is separately **NOT PROVISIONED**; USB/ADB host passthrough remains
intentionally absent.

The surface exists and looks healthy, which is why this needs writing down:

- Guarded `emulator` and `adb` wrappers on `PATH` at `/usr/local/bin`.
- A read-only host Android SDK; `emulator -list-avds` returns a populated catalogue.
- `adb` starts an agent-local daemon on port **5038**.

A guarded task session invoking the wrappers directly is the intended path — there
is no Coordinator-only guard entrypoint and no workspace-scoped KVM/ADB broker.
Use the inventory rather than assuming an AVD name, and do not write to the host
SDK or catalogue:

    emulator -list-avds
    python3 -c "import os; fd=os.open('/dev/kvm', os.O_RDWR); os.close(fd)"
    emulator -accel-check
    emulator -avd <listed-avd> -no-window -no-audio -no-boot-anim \
      -gpu swiftshader_indirect -no-snapshot-load -no-snapshot-save

Keep the emulator command running in its own bounded session. Poll `adb devices -l`
and `adb -s <serial> shell getprop sys.boot_completed` with capped backoff until the
property is `1` or the task's time budget expires. Then collect the criterion's real
evidence, including at minimum:

    adb -s <serial> shell getprop ro.build.version.sdk
    adb -s <serial> shell getprop ro.product.model

For visual evidence, `adb -s <serial> exec-out screencap -p` may be redirected to a
task-owned or temporary PNG. Shut down with `adb -s <serial> emu kill`; if console
authentication prevents that command from terminating the wrapper-launched process,
use `adb -s <serial> shell reboot -p`, wait for the emulator command to exit, then
run `adb kill-server`. Confirm no `emulator`, `qemu-system`, or `adb` process remains.

**Independent acceptance receipt (2026-08-29).** In the resumed Coordinator
session, `/dev/kvm` opened O_RDWR and `emulator -accel-check` reported KVM version 12
usable. `Pixel_3_API_29` booted as `emulator-5554`, reached
`sys.boot_completed=1`, reported API 29/model `Android SDK built for x86`, and
produced a valid 1080x1920 screenshot. `adb shell reboot -p` ended the emulator;
final process checks were empty. The SDK and AVD catalogue were mounted `ro`, the
protected Code parent was non-writable, and no `codex-linux-sandbox` process wrapped
tool commands.

The earlier VERIFIED BLOCKED receipt was produced by a stale pre-recreate process.
Two persistent defects were repaired on 2026-08-29: stored session
`runtime_config.mode` could override the enforced full-access guard profile and
re-enable the provider inner sandbox; and the `agentctl` user transition dropped the
host KVM supplemental GID because the image lacked a matching group. The runtime
mode fields are now migrated and protected by triggers, and the rebuilt image
creates/reuses the host KVM group and adds `kandev`. A namespaced `/dev/kvm` may
still display `nobody:nogroup`; successful open and acceleration are authoritative.

Do **not** substitute code-only evidence for an on-device acceptance criterion.
Genuinely code-only mobile work still uses the ordinary `TEST_RUNTIME=NONE` path;
that is not a stand-in for UI-QA that a criterion actually requires.

Registry entry: [E1](CAPABILITY_REGISTRY.md#e1-a-task-needs-an-android-emulator-or-on-device-ui-qa).

**Verifying the shutdown — do not let the receipt lie.** `pgrep -c -f qemu-system`
counts the invoking shell's own command line, so it reports stray processes that do
not exist and can also mask a real one. Confirm with a pattern that cannot match the
checker, e.g. `ps -eo pid,comm | grep -i qemu` or `pgrep -c -x qemu-system-x86_64`.
A cleanup receipt built on a self-matching pattern is not evidence.
## Inspecting QA screenshots with `view_image`

**Status 2026-08-29: VERIFIED WORKING after the Kandev runtime recreation.** Use the
approved image-inspection capability for screenshots already present in a task
workspace or `/tmp`; filesystem metadata is only a preflight, not visual evidence.

1. Confirm the exact artifact belongs to the task and preserve it until the QA/PR
   handoff is durable. `file`, dimensions, and a hash may establish integrity but do
   not establish what is rendered.
2. Call `view_image` with the absolute path and `detail=original` for every decisive
   screenshot. Inspect the actual criterion: content, state, clipping, overlap,
   error artifacts, and any required platform-specific UI.
3. Record a per-file PASS/FAIL receipt. Label responsive-web images as responsive
   web; they never substitute for native-device evidence.
4. If a call remains RUNNING without output, terminate it at a bounded interval and
   preserve the path, timestamp, duration, and termination result. After a known
   runtime/process recreation, perform exactly one fresh consuming-session retry.
5. If the fresh retry still hangs, treat it as a Kandev product/tool defect, create
   or update one platform board task, and physically Block the dependent task with a
   preservation receipt and deterministic resume trigger. Do not route a missing
   Kandev platform feature to Kandev Support and do not modify feature code merely
   to compensate for an inspection failure.

Recovery receipt: after the 2026-08-29 runtime recreation, three previously blocked
valid PNGs (desktop web, responsive web, and native Android) decoded immediately in
the owning QA session. Their visual contents passed and the task advanced. This
supersedes pre-recreate hang evidence for the current capability status; the bounded
failure procedure remains the correct regression path.

Registry entry: [K1](CAPABILITY_REGISTRY.md#k1-a-task-has-local-png-screenshots-that-require-visual-acceptance).

## The dated standup file is shared across workspaces

`standups/standup-YYYY-MM-DD.md` has no workspace qualifier, but Coordinators are
workspace-scoped peers that each run their own standup routine into the same shared
clone. So a file already existing for today does **not** mean you re-ran your own
standup — it may be another workspace's report.

The existing rule anticipated only same-workspace duplicates ("two coordinators
running it write the same path"). Cross-workspace peers were explicitly declared
independent, and nobody noticed they still collide on this one filename. Writing
your report over it destroys a peer's durable record, and the five-file rotation can
then delete the evidence.

Procedure: read the file first. If its content is yours, update in place with a
`revised at HH:MM` note. If it is not yours, append a section headed
`## Workspace: <name> (<workspace_id>)` and leave every other section byte-identical.
Add the same heading above the existing content if it does not already carry one, so
the file is self-describing. Never replace a section you did not write.

Retention still keeps the five newest `standup-YYYY-MM-DD.md` files, deleted by
explicit filename — the count is per file, not per workspace section.
## Board mechanics: cards advance themselves, and a move call only queues

Two behaviours to check before you attribute a card's position to anyone's decision.

### Which lanes advance a card when its agent completes a turn

For workflow `90f322ed`, from `workflow_steps.events`:

- **Advance on turn completion:** Spec, Work, Review, QA, PR, CI Fixup
- **Hold still:** Backlogs, Todo, **Blocked**, Human-QA, ToDeploy, Done

All six advancing lanes also auto-start an agent on entry, so a card with a live session
walks forward through the whole chain unattended. **This is not agent mis-routing — do
not record it as one.** The chain stops at Human-QA (auto-starts, does not advance), so
a card cannot drift to Done; it drifts into a Human-owned column instead and falsely
reads as ready for testing.

Re-derive the map for any workflow rather than trusting the table above, and match on
the event *trigger*, not the verb — advancement is expressed as **both** `move_to_next`
and `move_to_step`, and grepping for only the first will tell you a lane is stable when
it is not:

```sh
sqlite3 -noheader -separator ' | ' "file:/data/data/kandev.db?mode=ro" \
  "SELECT position, name,
          CASE WHEN events LIKE '%on_turn_complete%' THEN 'ADVANCES' ELSE 'stable' END,
          CASE WHEN events LIKE '%auto_start_agent%' THEN 'auto-start' ELSE '-' END
   FROM workflow_steps WHERE workflow_id='<workflow-uuid>' ORDER BY position;"
```

**To park a card that must wait** (CI in flight, an external dependency): use
**Blocked**. It is the only lane that keeps the agent attached without moving the card,
and it is what the column-ownership policy already requires for a task that cannot
progress. Tell the agent explicitly to idle and not signal completion, and say what you
will do when the wait ends — otherwise a parked card reads as an accusation.

### Confirm a move from the database, never from the tool response

`move_task_kandev` returns 200 and echoes the **requested** `workflow_step_id` even when
the move has only been queued. A move requested while the target's session is mid-turn
is deferred to the turn boundary. Confirm it landed:

```sh
sqlite3 -noheader -separator ' | ' "file:/data/data/kandev.db?mode=ro" \
  "SELECT ws.name, t.updated_at FROM tasks t
   JOIN workflow_steps ws ON ws.id=t.workflow_step_id WHERE t.id='<task-uuid>';"

# if the lane disagrees, the move is queued rather than failed:
sqlite3 -noheader -separator ' | ' "file:/data/data/kandev.db?mode=ro" \
  "SELECT * FROM pending_moves WHERE task_id='<task-uuid>';"
```

**The row's presence means the move is still queued** — there is no `applied` column,
and the row is deleted once the move lands. `session_id` is `UNIQUE`, so a second move
request **supersedes** the first rather than stacking; correcting a queued move is safe.
Issue the corrected move and verify exactly one pending row survives, naming the
destination you want. Do not conclude a move failed, and do not re-issue it repeatedly,
until you have checked `pending_moves`.

Columns are `id, session_id, task_id, workflow_id, workflow_step_id, step_position,
queued_at, actor, sender_session_id, move_id` — note `step_position`, which is easy to
misread as an applied/status flag when scanning a row positionally.

Note the schema: there are no `sessions` or `messages` tables in this database; session
and conversation state live elsewhere. Use `list_task_sessions_kandev` and
`get_task_conversation_kandev` for those.
