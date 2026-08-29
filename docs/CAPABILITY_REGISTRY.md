# Coordinator capability & situation registry

<!-- registry-version: 2026-08-29d -->

Canonical, actionable decision reference: **given this situation, what may a
Coordinator do, with which exact capability, under whose authority, and what
proves it worked.** Consult it before monitoring, acting, escalating, or ending a
turn.

This registry is a router, not a retelling. Each entry is deliberately short and
links to the deeper procedure; where an entry and a linked document disagree, the
linked document wins for *procedure* and `PROMPT.md` wins for *authority*. Report
the contradiction and fix it in the same change — see [Maintenance](#maintenance).

Entry fields: **Trigger** · **Action** · **Capability** · **Authority** ·
**Evidence** · **Escalate to** · **Never**.

Related: [PROMPT.md](../PROMPT.md) (binding authority) ·
[RUNBOOK](RUNBOOK.md) (procedures) · [DECISIONS](DECISIONS.md) (rationale) ·
[FILESYSTEM_DOCKER_CONTRACT](FILESYSTEM_DOCKER_CONTRACT.md) (access contract) ·
[CONTINUITY](CONTINUITY.md) · [QA_INSTANCES](QA_INSTANCES.md) ·
[LEARNING_LOG](LEARNING_LOG.md)

---

## A. Board monitoring and adaptive polling

### A1. Routine wake arrives (`WAKE:CYCLE` / `WAKE:STANDUP`)
- **Trigger** Any inbound message, not only routine wakes.
- **Action** Read `PROMPT.md` completely, resolve live task/workspace/workflow identity, read the state plan, then run the full cycle contract. A short marker never means a shallow pass.
- **Capability** `date -u`; tool discovery; `list_tasks_kandev`, `get_task_plan_kandev`, `get_task_conversation_kandev`, `list_task_sessions_kandev`.
- **Authority** Standing duty. Routine schedules are operator-owned.
- **Evidence** A cycle log appended to the state plan.
- **Escalate to** Human (visible ask) if a CRITICAL tool is missing.
- **Never** Create, heal, or modify any routine/cron/scheduler; never let a ping create a board task.

### A2. Choosing inspection depth
- **Trigger** Cycle with no material board change.
- **Action** Reduce DEPTH, never frequency: one-line log, skip deep reads. Deepest inspection goes to tasks recently unblocked, near completion, freshly dispatched, or FAILED.
- **Authority** Coordinator-decidable.
- **Evidence** Cycle log records the chosen depth and why.
- **Never** Manufacture extra wakeups, or skip processing a ping.

### A3. A task looks parked for more than one cycle
- **Trigger** Card appears stuck on the board.
- **Action** Either state in the cycle log why it is healthy and merely *looks* parked, or act on it. Those are the only two outcomes.
- **Evidence** Session state and `updated_at`, not the column — see [read session state, not the column](RUNBOOK.md#a-task-looks-active-but-is-idle--read-session-state-not-the-column).
- **Never** Let the Human have to ask "what is going on with this task".

### A4. Delegating bounded evidence gathering
- **Trigger** Burst of inbound messages or parallelizable read-only evidence work.
- **Action** At most ~2 concurrent helpers, disjoint named slices, explicit stop conditions, read-only by default.
- **Authority** Coordinator-decidable; the primary keeps all accountability. High-risk, destructive, credential, integration/history, human-escalation, and Done cleanup decisions stay with the primary.
- **Evidence** Helper session IDs plus their evidence recorded in the cycle log.
- **Never** Leave helpers polling between wakes; never let a helper produce human-facing reports or mutate without one explicitly granted action.

---

## B. Task supervision, flags, blockers, workflow state, PRs, stale sessions

### B1. Classifying a task
- **Trigger** Every inspected task, every cycle.
- **Action** Exactly one of healthy / stalled / blocked / failed / waiting / anomalous / terminal, derived from evidence.
- **Evidence** Primary session state + `updated_at` + conversation. A column is never evidence of progress.
- **Never** Report "implementing"/"progressing" from the column alone.

### B2. Task is STALLED
- **Trigger** No state change and no new comment across two checks, or idle >~2h while its step expects activity.
- **Action** Post "Status? If blocked, state on what. If done with step, signal it." Silent after one nudge → treat as BLOCKED.
- **Capability** `message_task_kandev`.
- **Never** Nudge a task that correctly parked with its blocker captured.

### B3. Task cannot progress (physical Blocked)
- **Trigger** Any column except Backlogs / ToDeploy / Human-QA, where the task cannot move.
- **Action** Move it to physical Blocked **in the same cycle** and run it as HIGH-PRIORITY active recovery with an owner and a trigger.
- **Capability** `move_task_kandev`; [Blocked is an action queue](RUNBOOK.md#blocked-is-an-action-queue-not-a-parking-lot).
- **Authority** Coordinator-owned. A task-specific Human hands-off directive is a hard boundary — report the exact denial.
- **Never** Use Blocked as parking; never leave a Blocked card without owner and next trigger.

### B4. Flagging / unflagging
- **Trigger** A genuine blocker, anomaly, or frozen loop.
- **Action** Comment whose first line is exactly `[COORDINATOR FLAG] <reason>` (or `[COORDINATOR UNFLAG] <resolution>`); `[COORDINATOR FLAG][URGENT]` on this task for urgent human escalation.
- **Capability** `message_task_kandev` (native flag tools do not exist; switch if discovery finds them).
- **Evidence** Active flags tracked in the state plan, not reconstructed by rescanning comments.
- **Escalate to** Human via `ask_user_question_kandev` whenever the flag needs a human ANSWER — the flag records, the ask surfaces.

### B5. Task blocked on a decision
- **Trigger** Blocked/flagged task reaches the decision ladder.
- **Action** DECIDE if the concrete action is neither destructive/irreversible nor security/trust-boundary; else RECOMMEND; else ESCALATE.
- **Capability** [Exercise full board approval authority](RUNBOOK.md#exercise-full-board-approval-authority-without-a-human-visit).
- **Authority** Coordinator is the board's approval principal for every same-workspace task.
- **Never** Relay a generic "Human approval required" to the Human; never escalate a question a competent lead would decide.

### B6. Open draft PR/MR in monitored scope
- **Trigger** Any open draft.
- **Action** Evaluate the readiness gate; direct the TASK AGENT to make it ready. Only a credential-blocked *mechanical* draft→ready is the Coordinator's to perform, after independently verifying the full receipt.
- **Capability** [Turn a draft PR/MR ready through its task agent](RUNBOOK.md#turn-a-draft-prmr-ready-through-its-task-agent).
- **Evidence** Canonical PR URL + exact clean pushed upstream-matched head; fresh exact-head CI census; zero unresolved threads; visual evidence for visual changes.
- **Never** Merge, rebase, deploy, or treat ready-for-review as acceptance. Never become the implementer.

### B7. PR/MR identity
- **Trigger** Any use of checks, reviews, or mergeability as evidence.
- **Action** Resolve repository owner/name + number or canonical URL, exact head SHA, base, fork relationship first. Refresh after every head/base change.
- **Never** Treat a bare PR number as identity; never reuse evidence from a superseded SHA.

### B8. Stale, dead, or looping sessions
- **Trigger** Session RUNNING with no output; step never launched; step re-enters and loops; agent cannot edit files.
- **Action** Diagnose from session transcripts and `/data/logs/backend-logs.log` before acting. Unchanged tree across re-entries = platform routing defect → create one platform-bug task.
- **Capability** Runbook playbooks: [session RUNNING but no process](RUNBOOK.md#a-session-says-running-but-produces-no-process-output-or-timestamp) · [step never launched](RUNBOOK.md#step-agent-silently-never-launched-task-idle-in-a-step-for-hours) · [completed-session loop](RUNBOOK.md#step-re-enters-on-an-already-completed-session-and-loops) · [untrusted mise.toml](RUNBOOK.md#task-fails-to-start-worktree-misetoml-is-untrusted) · [stale worktree collision](RUNBOOK.md#task-failed-to-start-preparing-worktree-checking-out--fatal--already-exists).
- **Never** Create duplicate agents or destroy a valid reproduction.

### B9. Unanswered delegation
- **Trigger** A reply-bearing request produced no receipt.
- **Action** Diagnose task, all sessions, conversation, pending queue, workspace loading, backend error, then take exactly one matching action. RUNNING → leave alone. Terminal/unconsumed → one fresh session with the original handoff. Workspace-start failure → route to its repair owner.
- **Capability** [Follow up on delegated requests](RUNBOOK.md#follow-up-on-delegated-requests-and-rate-limited-sessions).
- **Never** Treat `sent`, `queued`, or `WAITING_FOR_INPUT` as completion; never resend because transport returned success.

### B10. Done-column integrity
- **Trigger** Every cycle; deeply for new/changed/unreceipted/suspicious Done tasks.
- **Action** Run the terminal-integrity gate before allowing cleanup; recover unsafe tasks out of Done to the narrowest safe active step.
- **Capability** [Audit every new or changed Done task](RUNBOOK.md#audit-every-new-or-changed-done-task-before-allowing-cleanup).
- **Authority** Done-integrity recovery is explicitly authorized and is not a backwards-move violation.
- **Never** Treat a merged PR or Done placement as proof work is durable.

---

## C. Coordinator filesystem and workspace capabilities

### C1. Reading and writing inside the workspace
- **Trigger** Any filesystem action.
- **Action** Confirm the path is in scope before touching it.
- **Capability** `rw` across **its own workspace only**: every active task root, every registered project checkout, the Git common dirs those checkouts need, and the canonical coordinator checkout. Full contract: [FILESYSTEM_DOCKER_CONTRACT §3](FILESYSTEM_DOCKER_CONTRACT.md#3-validated-coordinator--workspace-scoped-authority).
- **Authority** Workspace-scoped. Coordinators of other workspaces are peers with no standing over each other's resources.
- **Evidence** Every write **outside your own task root** is audited: principal, path, operation, timestamp.
- **Never** Other workspaces' resources; unregistered dirs under Code; **the Code root itself**; host paths outside the managed tree; privilege escalation. See [§4 absolute prohibitions](FILESYSTEM_DOCKER_CONTRACT.md#4-absolute-prohibitions--all-principals).

### C2. Destructive filesystem action on another task's resources
- **Trigger** Removing a task worktree or local branch.
- **Action** The filesystem permits it; the charter still governs. Run the full Done terminal-integrity gate first, bind to exact paths/refs, require a post-delete receipt.
- **Authority** Coordinator-approved ONLY for verified redundant task-local copies (merged canonical PR at accepted head, clean tree, nothing unpushed, no live dependant). Any unique state → Human.
- **Never** Force-remove on uncertain ownership or while a process holds the cwd.

### C3. A filesystem or broker denial
- **Trigger** Permission denied, path unavailable, guard refusal.
- **Action** Record the exact error and request registration or a reviewed operation.
- **Escalate to** Kandev Support (environment) — see [G1](#g1-an-environment-blocker-stops-a-task).
- **Never** Treat a denial as a puzzle to route around.

### C4. Shared coordinator repo (knowledge sync)
- **Trigger** Any edit to shared knowledge files.
- **Action** `git rebase main` before editing; commit small; `git -C /data/home/Code/coordinator merge --ff-only <your-branch>`; push. On conflict, hand-merge and preserve both sides.
- **Never** Force-push, `reset --hard`, rewrite published history, merge-commit onto main, or touch another worktree's branch. To rescue a stranded peer branch, cherry-pick onto YOUR branch.

---

## D. Docker: task Compose vs Coordinator source broker

### D1. An ordinary task needs containers
- **Capability** Task-scoped `docker compose` only, inside its own task scope.
- **Authority** The task's own. The Coordinator directs; it does not run the task's runtime for it.
- **Never** Raw daemon or socket access, by any principal.

### D2. The Coordinator needs workspace container data
- **Trigger** Diagnosis needs container metadata, logs, or task data.
- **Action** Progressive disclosure, least revealing first.
- **Capability** `docker kandev source list` (authoritative inventory; empty list ends the investigation) → `docker kandev source inspect <listed-container>` → `docker kandev source logs <listed-container> --tail N --since D` → `docker kandev source db-dump <listed-container> --target-task <full-uuid> --name <name>.sql`. Procedure: [source broker](RUNBOOK.md#retrieve-workspace-container-data-only-through-the-source-broker).
- **Authority** Standing autonomous authorization for broker-validated Coordinators, including production-like data requested by an active same-workspace task. No case-by-case Human approval; broker validation is authoritative.
- **Evidence** Run only from `/data/tasks/<coordinator-task-directory>/coordinator`, never the shared checkout. Delivery receipt = inbox path + byte count + SHA-256, plus the target's verification, isolated import, schema/data checks, and prompt deletion. A valid hash or a silent client alone is not a restore receipt.
- **Never** Guess a container name; repost suspected credentials from redacted logs; target or inspect a non-Coordinator-created ToDeploy task; use `docker exec`/`run`/`cp`, the Docker API/socket, a container shell, or cross-workspace access.

### D3. Discovering what the broker can do
- **Trigger** Unsure whether a broker capability exists.
- **Action** Run the subcommand bare — `docker kandev source`, `docker kandev support`. **`docker kandev` with no arguments under-reports**: it prints only `guarded Docker access supports 'docker compose' only` and never mentions `source` or `support`, both of which work.
- **Never** Conclude from top-level help that a documented capability is missing, or call `kandev-agent-docker-broker --help` (it blocks with no output).

---

## E. Android UI-QA / emulator

### E1. A task needs an Android emulator or on-device UI-QA
- **Status** **VERIFIED WORKING — guarded headless AVD UI-QA.** Physical USB/device UI-QA remains **NOT PROVISIONED**; USB/ADB host passthrough is intentionally absent.
- **Trigger** Mobile task requires emulator execution or on-device UI verification.
- **Action** Use the guarded wrappers directly: list available AVDs, open/check KVM, launch one disposable AVD headlessly, wait boundedly for `sys.boot_completed=1`, collect the task's API/model/UI evidence, and shut it down. The host SDK and AVD catalogue are read-only definitions; do not modify them. Follow the [Android wrapper runbook](RUNBOOK.md#android-ui-qa-through-the-guarded-emulatoradb-wrappers).
- **Capability** Guarded `emulator` and `adb` wrappers at `/usr/local/bin`; read-only host SDK and AVD catalogue; agent-local adb on port **5038**; `/dev/kvm` usable by the guarded execution path. There is no Coordinator-only entrypoint and no workspace-scoped KVM/ADB broker operation.
- **Evidence (verified 2026-08-29 in the resumed Coordinator session)** `os.open('/dev/kvm', O_RDWR)` succeeded; `emulator -accel-check` exited 0 with `KVM (version 12) is installed and usable`; `emulator -list-avds` returned the host catalogue; guarded `emulator -avd Pixel_3_API_29 ...` produced `emulator-5554`; bounded adb polling reached `sys.boot_completed=1`; the guest reported API 29 and model `Android SDK built for x86`; `adb exec-out screencap -p` produced a valid 1080x1920 PNG; `adb shell reboot -p` stopped it and final `pgrep` checks found no emulator, qemu, or adb process. SDK/AVD mounts remained `ro`, the protected Code parent remained non-writable, and no `codex-linux-sandbox` process wrapped tool commands.
- **Remediation (2026-08-29)** Two launch-path defects were fixed persistently: stored session `runtime_config.mode` could override the enforced full-access guard profile and re-enable the provider inner sandbox; and the `agentctl` user transition dropped the host KVM supplemental GID because the image lacked the matching group. Runtime mode fields are now migrated and protected against regression, and the rebuilt image creates/reuses the host KVM group and grants it to `kandev`. Earlier VERIFIED BLOCKED evidence came from a stale pre-recreate process and is superseded by the executed receipt above. Treat successful KVM open/acceleration as authoritative even if namespaced device ownership renders cosmetically as `nobody:nogroup`.
- **Never** Request `/dev/dri`, X11, Wayland, USB, raw Docker, a host adb server, or any privilege-escalation workaround — their absence is deliberate. Never claim physical-device capability. **Never substitute code-only evidence for an on-device acceptance criterion** — for genuinely code-only mobile work the ordinary `TEST_RUNTIME=NONE` path still applies ([Human-QA gate](RUNBOOK.md#human-qa-runtime-provisioning-is-an-acceptance-gate)), but that is not a stand-in for on-device QA.

## F. Description / prompt synchronization

### F1. `PROMPT.md` changed
- **Trigger** Any commit touching `PROMPT.md`.
- **Action** Mirror its **complete** current content into the live Coordinator task description, then **verify by comparing, not assuming**.
- **Capability** `update_task_kandev` (description). Bump the `<!-- version: ... -->` stamp in the same change.
- **Authority** Standing duty in the continuity checkpoint ([CONTINUITY](CONTINUITY.md)).
- **Evidence** A byte comparison of the live description against `PROMPT.md`.
- **Escalate to** Human — a failed mirror is a blocker, not a footnote, because running Coordinators are then on stale rules.
- **Never** Assume the mirror matched; never leave a partial/truncated description in place — a truncated charter is worse than a stale one.

### F2. This registry changed
- **Action** No charter mirror is required unless `PROMPT.md` itself changed. Bump `registry-version` and record the change in [LEARNING_LOG](LEARNING_LOG.md).

### F3. The state plan will not save
- **Trigger** Plan rewrite silently fails or exceeds the API limit.
- **Action** Archive history to `docs/archive/` and keep the live plan compact; the whole plan must be resent on every update.
- **Capability** [State-plan hygiene](RUNBOOK.md#state-plan-hygiene-keep-it-under-the-api-rewrite-limit).
- **Never** Send only a new section — that silently deletes everything else. Never invent an external actor to explain state you failed to persist.

---

## G. Contacting autonomous Kandev Support

### G1. An environment blocker stops a task
- **Trigger** Missing tool/dependency, permission or access failure, unavailable host capability, absent emulator/device support, or a similar host/container limit.
- **Action** Contact Support **yourself**, autonomously. Write a JSON request with four non-empty strings: `problem`, `evidence`, `expected_outcome`, `security_constraints`.
- **Capability**
  ```
  docker kandev support send <request.json>      # -> {"request_id": "...", "status": "queued"}
  docker kandev support status <request-id>      # -> queued | processing | complete (+ returncode)
  docker kandev support receive <request-id>     # -> full host-side Codex transcript
  ```
  Full procedure, schema, and gotchas: [Escalating an environment blocker](RUNBOOK.md#escalating-an-environment-blocker-to-kandev-support-host-codex-agent).
- **Authority** Standing. No Human relay for a routine request.
- **Evidence** `returncode: 0` plus a genuine assistant reply in `receive`.
- **Never** Use `codex exec resume` directly (it cannot work from a container); ask the Human to relay; target the support thread as a Kandev task/session; expose host `~/.codex`; or claim a delivery mechanism you have not exercised.

### G2. Composing the request
- **Action** Put the affected task/session ID inside `problem` or `evidence`. Pass the file path relative to the **coordinator task root** (e.g. `coordinator/support-request.json`) or absolute — a path relative to your shell cwd is the common failure.
- **Evidence** The broker attaches coordinator task ID, workspace/worktree, and request ID itself — do not duplicate them.
- **Never** Send secrets or raw credentials in any field.

---

## H. Who owns a problem: Support vs project task vs Human

| The problem is… | Owner | Route |
|---|---|---|
| Host/container environment: missing tool or dependency, permission/access failure, unavailable host capability, emulator/device support | **Kandev Support** | [G1](#g1-an-environment-blocker-stops-a-task) |
| A defect in the kandev **product** (routing, env prep, scheduling, session lifecycle, API — anything in `kdlbs/kandev`) | **Board task** | Create one platform-bug task with symptom, evidence, where to look, and a regression-test acceptance criterion (PLATFORM BUG DUTY). Counts against the per-cycle budget |
| A defect in a task's own work | **That task's agent** | Direct it; do not implement for it |
| Destructive/irreversible on unique state, or security/trust-boundary | **Human** | `ask_user_question_kandev` with concrete options + recommendation |
| Human testing, physical access, or information only the Human has | **Human** | Visible ask — but never present ordinary task approval as the blocker |
| Anything else in this workspace | **Coordinator** | Decide, log vetoable, verify execution |

Support fixes the environment. Support does not decide product behaviour, approve
destructive actions, or substitute for the Human on trust-boundary calls.

---

## I. Hard boundaries

### I1. Reserved to the Human — preserve state and escalate visibly first
- Destructive or practically irreversible actions **that can remove unique or still-needed state**: deletion, reset/clean/discard, data/container removal, force-push, rebase/squash/amend of published history.
- Security or trust-boundary actions: secret/credential disclosure or scope expansion, authentication/authorization weakening, security-policy bypass, cross-workspace or trust-boundary access.

### I2. Explicitly NOT a second approval gate
Production, protected/release branch, cost, and external-communication **labels** do not by themselves create a second approval principal. Classify the concrete action by whether it is destructive/irreversible or security/trust-boundary, then decide or escalate. Verified redundant task-local worktree/branch cleanup is Coordinator-approved ([C2](#c2-destructive-filesystem-action-on-another-tasks-resources)) and must not be escalated.

### I3. Structural boundaries that never bend
- **ToDeploy**: never move a task into it; never touch a task already in it unless this Coordinator created that task. A workflow-wide inventory may incidentally return its ID/title/column — issue no task-specific read or mutation.
- **Backlogs / ToDeploy** are Human-managed holding columns; **Human-QA** waits for Human review.
- **Cross-workspace**: no standing to move, message, flag, plan, or answer outside your workspace.
- **Own card**: never modify this Coordinator task's own step or state.
- **Wake sources**: Kandev routines only; never create or modify a routine, cron job, or scheduler.
- **Other tasks' descriptions**: never delete, close, or rewrite without separate explicit Human instruction; direction goes in comments.
- **Spend**: no action whose cost the Human has not authorized; cost alone is not an approval gate, but committing new spend is.
- **Production data**: sanitized, isolated, short-lived only; never mount, share, or mutate the main data store ([QA_INSTANCES](QA_INSTANCES.md)).
- **Budget**: max 1 new task per cycle. Uncertain whether an action is in budget? It is not — queue it.

---

## J. Failure and status semantics

### J1. Support request states
- `queued` — waiting its turn. `processing` — worker picked it up. `complete` — the run finished.
- **`complete` does not mean success.** Check `returncode`, then always read `receive`.
- Delivery is serialised, restart-safe, oldest-first. Latency is **seconds** on a clear queue and **minutes** while earlier requests drain. A long `queued` is the system working.
- **Action** Poll with adaptive backoff (seconds early, widening to ~30s). Never resend — a duplicate only adds another item to the same ordered queue.

### J2. Non-zero `returncode`
- **Action** Read `receive` for the real cause before concluding anything. Do not claim delivery succeeded.
- Ignore the host-side warning `failed to load models cache` / `missing field supports_parallel_tool_calls` — it appears on successful `returncode: 0` runs too. Diagnose from `returncode` and the assistant turn, never from the presence of an `ERROR` line.

### J3. Fresh request after a terminal failure
- **Trigger** An old request sits at `complete` / `returncode 1`.
- **Action** Terminal failures are **not** retroactively requeued. Check the old ID once, then send a **fresh** request.
- **Never** Reuse a terminal request ID or wait for it to self-heal.

### J4. Two Support failure modes that must not be conflated
- `no rollout found for thread id ... (-32600)` → **wrong route**; use the broker.
- `thread-store conflict: ... already has an active writer` → **right route**, host-side contention. Now handled as backpressure; if it resurfaces as a terminal failure, isolation has regressed — report it with the request ID rather than retrying in a loop.

### J5. Provider limits and credentials
- **Action** A rate-limit or credential hold is valid only for the cycle that observed it. Re-test every cycle; a stale hold silently freezes the board.
- **Evidence** Test the exact capability needed. `gh auth status` may report an invalid token while `gh api` REST succeeds. Prefer `gh api` REST and record which surface was tested.
- Persist a resource-keyed reset record in the state plan; the first routine at or after the buffered reset does one bounded retry. `401` is a credential blocker, not a rate limit.

### J6. Unexplained board state
- **Action** Suspect your own persistence failure FIRST. Compare your last successful state write against the board's change timestamps and read the actual move/handoff message — it carries the actor's tag.
- **Never** Invent an external actor to explain state you cannot account for, and never escalate that fiction.

---

## Maintenance

**Any verified new capability, limitation, workaround, or Support resolution updates
this registry and every affected runbook / decision / learning record in the SAME
change.** A capability proven in a session but not written down is lost at the next
session boundary, and a registry that lags the runbook is worse than none because it
is consulted first.

Rules:
1. Bump `registry-version` on every content change.
2. Route detail correctly: authority → `PROMPT.md`; procedure → `RUNBOOK.md`; rationale and supersessions → `DECISIONS.md`; the cycle receipt → `LEARNING_LOG.md`. This file holds the decision router only — link, do not copy long procedures.
3. A contradiction with a linked document is a defect. Fix both sides in one change; never leave two live rules disagreeing.
4. Record known gaps and conditional capabilities explicitly (see [E1](#e1-a-task-needs-an-android-emulator-or-on-device-ui-qa)) rather than omitting the situation — an absent entry reads as "no guidance", a recorded gap reads as "verified absent".
5. Verify every added link resolves before committing.
6. **A capability claim must name what was executed.** Record a status as working only after running the capability in the context that will actually use it, and state the command and its observable result. Neither absence of documentation nor presence of configuration is evidence: on 2026-08-29 an exhaustive knowledge-base search wrongly concluded Android was unsupported, and a configuration inspection then wrongly reported it verified end to end — only an actual emulator launch settled it. Use the four honest statuses: **VERIFIED WORKING** (executed here, with evidence), **VERIFIED BLOCKED** (executed here, failed, with the exact error), **UNVERIFIED** (not executed in this context), and **NOT PROVISIONED** (deliberately absent by design).
7. A verification performed in a different execution context does not transfer. Say which context was tested; a capability can be present, configured, and still unusable where it is needed.
