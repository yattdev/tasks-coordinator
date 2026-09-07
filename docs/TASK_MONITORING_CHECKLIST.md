# Coordinator task-monitoring checklist

This is the reviewable checklist for every Coordinator task touch. It applies
when a task is read, mentioned, monitored, moved, messaged, or included in a
status reply. A status request is an action sweep, not a read-only report.

`PROMPT.md` remains the authority source. `RUNBOOK.md` supplies detailed
procedures, and `CAPABILITY_REGISTRY.md` supplies capability routing. If this
checklist conflicts with either, stop and repair the contradiction.

## 1. Required checks on every task touch

- [ ] Present the task to the Human as
  `[Full task title — full UUID](<live-board-base>/t/<full-UUID>)`. Resolve the
  board base from the live environment. Do not shorten the UUID or leave a bare
  title/ID when the board URL is known.
- [ ] Re-read the live task row: physical lane, state, `updated_at`, pending
  task/session actions, and move-lifecycle state.
- [ ] Read the latest relevant conversation and saved plan; treat an older
  report as historical until live evidence confirms it.
- [ ] Read every nonterminal session, including session ID, state, update time,
  effective profile/model, and whether it is the current writer/gate owner.
- [ ] Read parent, child, sibling, blocker, and dependent relationships from
  both endpoints when a dependency matters.
- [ ] Read every attached repository/worktree: canonical repository, base,
  branch, local head, pushed/remote head, dirty/untracked state, and preserved
  unique work.
- [ ] If any PR/MR exists, run the complete PR/MR overlay in section 3.
- [ ] If any check is red or pending, run the complete CI overlay in section 4.
- [ ] Read the complete task tag set. Preserve correct agent-owned tags without
  churn; replace stale agent-owned tags/notes; never alter Human-owned tags.
- [ ] Classify the task exactly once as `healthy`, `stalled`, `blocked`,
  `failed`, `waiting`, `anomalous`, or `terminal`, with the evidence supporting
  that class.
- [ ] Name one current owner and one executable next action. `Wait`, `monitor`,
  `no session`, and a lane name are not executable next actions.
- [ ] Take every safe authorized action now. Delegate implementation, testing,
  review, and QA to the task agent; the Coordinator directs, moves, notifies,
  and verifies.
- [ ] After every action, re-read the lane, task state, sessions/model, pending
  lifecycle, tags, repository head, and provider state affected by the action.
- [ ] Persist owner, health, last action, next action, trigger, attempt count,
  evidence identity, preservation receipt, fallback, and verification result.

## 2. Lane-by-lane checklist

### Backlogs

- [ ] Determine who created the card. Human-created backlog cards remain
  Human-owned for promotion; record the concrete promotion decision needed.
- [ ] Coordinator/agent-created cards must not remain inert. If the scope is
  ready, save the approved plan, move to Work, and verify the Work owner starts;
  otherwise move to Spec and verify the Spec owner starts.
- [ ] Do not start an ordinary task Codex session while it remains in Backlogs.
  The permanent Coordinator task is the only exception.

### Todo

- [ ] Coordinator-created Todo with an approved plan: move Todo to Work now and
  verify a correct-model Work session starts.
- [ ] Human-created Todo: do not promote without the Human's decision; surface
  the exact decision only through the normal Human-action report/ask path.
- [ ] Do not leave a Coordinator-owned task in Todo with an empty next action.

### Spec — Codex `gpt-5.6-sol`

- [ ] Verify one fresh Spec owner is running on the required model.
- [ ] Answer lead-decidable questions directly and document the decision as
  vetoable; escalate only destructive/irreversible or security/trust-boundary
  choices.
- [ ] If the plan is complete and no question remains, signal/advance it. A
  known fix that needs edits is moved to Work; more discussion cannot unblock a
  read-only planning lane.
- [ ] Verify the approved plan exists before any direct Work launch.

### Work — Codex `gpt-5.6-terra`

- [ ] Verify exactly one active implementation owner, correct worktree, correct
  branch/base, clean preservation boundary, and correct model.
- [ ] If silent or stopped, diagnose before waking; resume the preserved owner
  or start one fresh correct-model owner without duplicating writers.
- [ ] Give exact review/CI/blocker findings, files, run/job/thread links, and
  expected receipt. Never implement the fix in the Coordinator worktree.
- [ ] Require applicable tests, clean commit, ordinary non-rewriting push, and
  exact local/remote head equality before advancing.

### Blocked — Coordinator-owned recovery queue

- [ ] Record the previous actionable lane.
- [ ] Re-prove the exact blocker/dependency and why work cannot continue.
- [ ] Name the blocker owner and follow dependencies to one root.
- [ ] Preserve branch, exact head, worktree, runtime, data, artifacts, and any
  unique uncommitted/unpushed work.
- [ ] Name the immediate removal action, expected evidence, deterministic
  resume trigger, attempt count, and fallback.
- [ ] Ensure the root is staffed by a verified running recovery owner, a visible
  unanswered Human-only ask, or a genuinely time-bound external event with a
  named fallback owner.
- [ ] Recheck every cycle even when unchanged. Suppress only duplicate pings,
  never inspection or action.
- [ ] When the trigger clears, atomically move to the narrowest actionable lane,
  send the preservation-bound handoff, verify the correct session starts, and
  reconcile the tag in the same cycle.
- [ ] Move terminal-safe obsolete/superseded carriers to Done only after the
  terminal gate; remove stale dependency edges and consolidate shared root
  failures instead of spawning duplicate repairs.

### Review — Codex `gpt-5.5`

- [ ] Bind review to the canonical PR/MR and exact current head.
- [ ] Stop/park authoring writers and verify a fresh independent Review session
  on the required model; lane movement alone is not a review.
- [ ] Require an explicit `REVIEW_RESULT=PASSED` or `FAILED` tied to that SHA.
- [ ] On findings, return to Work with exact thread/finding references; after a
  push, invalidate the old result and run a new independent Review.
- [ ] On pass, verify all actionable/hidden threads are resolved or replied,
  then advance to a distinct QA owner.

### QA — Codex `gpt-5.6-sol`

- [ ] Verify QA is a fresh independent session, not the author or reviewer
  reused by workflow automation, and bind it to the exact current head.
- [ ] Require an explicit `QA_RESULT=PASSED`, `FAILED`, or `INCOMPLETE` tied to
  that SHA and a statement of whether QA changed code.
- [ ] Exercise end-to-end behavior and regression/security boundaries. For
  visual/mobile/runtime work, apply the real UI/runtime evidence overlay.
- [ ] If QA changes code, return through fresh Review and QA; a prior gate does
  not cover a new head.
- [ ] On pass, advance to PR delivery work and refresh exact-head provider state.

### PR — Codex `gpt-5.4`

- [ ] Run the full PR/MR overlay below, including draft reason, readiness,
  conflicts, checks, threads, screenshots, reviewer state, and why still open.
- [ ] Draft is the creation default, not a Human-QA hold. If every readiness
  gate passes, make it ready immediately, refresh post-ready checks, then notify
  the correct reviewer once for that exact head.
- [ ] If not ready, route the missing evidence to the responsible task owner;
  do not leave a vague `draft` reason.
- [ ] Never interpret ready-for-review as merge permission.

### CI Fixup — Codex `gpt-5.6-luna`

- [ ] Bind failures to the canonical PR and latest exact head.
- [ ] Verify one Luna owner is running with exact failing run/job URLs, logs,
  symbols, and the expected fix or one narrow rerun.
- [ ] Classify every red/pending result using section 4; do not assign broken
  main, provider, or cascade failures to the feature branch.
- [ ] After a fix/push, invalidate older Review/QA/CI receipts as applicable and
  route back through the narrowest required gate.
- [ ] If exact-head CI is green and no fix remains, advance immediately; CI
  Fixup is not a holding lane.

### Human-QA — workspace-sensitive

- [ ] First resolve the workspace. In non-Kandev product workspaces, the Human
  owns lane movement; the Coordinator may still message, diagnose, provision a
  safe task-owned test instance, and remove ordinary blockers.
- [ ] In the canonical Kandev workspace, the Coordinator retains ordinary lane
  authority and must actively route Human-QA cards.
- [ ] State the exact manual/visual test still required, tester, exact head,
  runtime URL/credentials handoff location, scenarios, and pass/fail routing.
- [ ] A persistent runtime must pass the task-owned instance, safe data,
  `0.0.0.0`/LAN, login, feature, and start/stop receipt. Code-only work may use
  `TEST_RUNTIME=NONE` with a reason.
- [ ] Human-QA blocks draft readiness only when this exact change genuinely
  needs remaining Human/manual/visual evidence.

### ToDeploy — Human-owned boundary

- [ ] For non-Coordinator-created cards, inspect only incidental workflow-wide
  ID/title/lane data. Do not read task conversation, plan, sessions, relations,
  PR state, or resources; do not message, move, clean, archive, or deploy.
- [ ] The sole permitted touch is targeted reconciliation of this Coordinator's
  agent-owned task tag/note; never alter a Human-owned tag.
- [ ] For Coordinator-created cards only, apply the explicit terminal rules
  before any ToDeploy-to-Done movement.
- [ ] Report the Human-owned deployment action with a clickable task identity,
  canonical PR URL when known from prior lawful evidence, and consequence of
  delay; do not manufacture task-specific reads inside the lane.

### Done — terminal integrity, not an archive shortcut

- [ ] Enumerate every Done card each full cycle. Shallow-verify an unchanged
  card only when a complete persisted terminal receipt still matches live state.
- [ ] Deep-audit every new, changed, unreceipted, or suspicious card: all
  sessions, subtasks/dependencies, worktrees, branches/upstreams, dirty/untracked
  files, task-authored commits, remote containment, canonical merged PR and
  accepted head, runtime/resources, and remaining consumers.
- [ ] If unique or unpushed work, an open deliverable, an unmet required gate,
  or a live consumer exists, preserve it, move to the narrowest active lane, and
  start the correct recovery owner.
- [ ] Clean only exact verified redundant task-local resources under the
  terminal-cleanup grant; never remove uncertain or unique state.
- [ ] Persist the terminal receipt and allow normal archive timing only after it
  remains terminal-safe.

### Unknown or custom lane

- [ ] Ledger and classify it immediately.
- [ ] Treat it as monitored until policy identifies its ownership and execution
  semantics.
- [ ] Do not infer that a custom lane is inactive, Human-owned, or safe to skip.

## 3. PR/MR overlay — every open pull or merge request

- [ ] Canonical base repository, full URL, PR/MR number, base branch, head
  repository/branch, exact provider head SHA, and card association are correct.
- [ ] Local head, fork head, and provider head match; tree is clean and all task
  work is pushed.
- [ ] Title, body, scope, tests, compatibility/migration/rollback notes, and
  third-party template/contribution requirements match the current diff.
- [ ] Draft? State the exact missing readiness gate. If none remains, make it
  ready now; do not wait for Human-QA by default.
- [ ] Ready? Refresh checks, threads, and mergeability after the transition.
- [ ] Conflict/dirty? Delegate a normal non-rewriting integration fix in Work,
  verify the new head, then repeat Review/QA/CI as required. A conflict is work,
  not a Human decision.
- [ ] Enumerate required checks and every failed/pending/approval result at the
  exact head.
- [ ] Enumerate actionable, unresolved, and hidden review threads; direct fixes
  and require technical replies to each.
- [ ] For visual changes, verify sanitized reviewer-facing images are embedded
  on the provider and their URLs return image content.
- [ ] Verify reviewer request/notification identity and exact head. A ready
  `kdlbs/*` PR is notified to `@carlosflorencio` once per head, and again after
  a new push; notify other proven path owners only when justified.
- [ ] State why the PR remains open: active review, named current-head gate,
  merge owner, or exact external event. `Open` alone is not a status.
- [ ] If merged, verify accepted head and route through ToDeploy/Done semantics;
  if closed unmerged, prove abandonment/supersession before terminal routing.

## 4. CI overlay — every failed or pending check

- [ ] Refresh the exact-head check census and capture run/job URLs, status,
  conclusion, attempt, failing symbol/path, and relevant logs/artifacts.
- [ ] **Branch-owned defect:** give the CI Fixup owner the exact reproduction and
  expected fix; require push and fresh gates.
- [ ] **Stale base/conflict:** delegate additive integration with repaired
  current main; never rebase/squash published history without explicit authority.
- [ ] **Broken main:** reproduce on clean current main, staff one canonical base
  repair, and link dependents to its exact repair trigger.
- [ ] **Cascade:** identify the root job/failure; do not assign derivative red
  jobs as separate fixes.
- [ ] **Flaky:** require evidence it is nondeterministic, then authorize one
  narrow rerun with an owner and follow-up; repeated reruns are not a fix.
- [ ] **Provider/rate limit/approval:** re-test the exact capability each cycle,
  record reset/permission identity and one bounded retry/fallback.
- [ ] **Conclusive unrelated infrastructure/broken-base result:** it may remain
  under an active repair owner while review proceeds, but must be disclosed and
  must not be mislabeled branch-green without the classification.
- [ ] Never leave red CI with no running owner, and never count a posted comment
  as remediation.

## 5. Cross-cutting exception and failure cases

- [ ] **No live owner:** decide whether the lane expects execution. If yes,
  diagnose and wake/replace with the correct model; if no, name the Human,
  provider, dependency, or time-bound trigger and fallback.
- [ ] **Duplicate writers/gate owners:** freeze optional work, preserve both
  transcripts/worktrees, select one correct owner, park the stale owner, and
  verify the final complete session census.
- [ ] **Wrong model/profile:** do not resume it. Start a fresh correctly mapped
  session or route the configuration repair; verify runtime model metadata.
- [ ] **Failed/crashed session:** read its transcript and backend evidence,
  preserve unique work/queue, classify the cause, then restart only with the
  preservation-bound handoff.
- [ ] **Silent or stale:** after two unchanged checks or about two hours in an
  active lane, send one specific request. If still silent, classify and staff
  the blocker; do not spam generic status pings.
- [ ] **Pending move:** run a fresh exact-scope pending-move/session preflight
  before contact. An armed move makes messaging unsafe until atomically cleared.
- [ ] **Dependency:** verify edge direction from both endpoints. Distinguish a
  true implementation block from integration-only gating; safe stacked work may
  proceed on an exact prerequisite head while integration remains blocked.
- [ ] **Lead-decidable question:** decide/recommend and continue. Human escalation
  is reserved for destructive/irreversible, security/trust-boundary, physical,
  Human-only information/testing, or an explicit Human-owned lane action.
- [ ] **Human answer required:** create/verify the visible ask, include options,
  recommendation, exact action, and consequence of delay; keep the task's flag,
  tag, ledger, and ask synchronized.
- [ ] **Multiple repositories/PRs:** one task/subtask owner per repository or PR,
  with dedicated worktree, explicit handoff, and parent supervision.
- [ ] **Cross-workspace platform work:** transfer/relay evidence to the canonical
  Kandev workspace; never cross workspace credentials, worktrees, sessions, or
  data and never create a shadow implementation.
- [ ] **Provider data unavailable:** use documented read-only fallbacks, label
  evidence freshness, retry the exact capability once at the deterministic
  trigger, and never invent a clean/green/mergeable state.
- [ ] **Security/destructive action:** preserve state and ask the Human. Ordinary
  reversible task work remains Coordinator-approved.
- [ ] **Task appears complete:** do not use a lane or comment as proof. Apply the
  PR/merge, independent gates, durability, dependency, and Done integrity tests.

## 6. Required human-facing status shape

For every mentioned task, use this compact order:

1. `[Full task title — full UUID](<live-board-base>/t/<full-UUID>)`
2. What capability/deliverable it adds or repairs, in plain language.
3. Current verified state: lane, owner/session, PR URL and exact head if present.
4. Why it is not advancing now.
5. Action already taken by the Coordinator.
6. Next owner action and deterministic trigger/fallback.
7. Human action only when truly required, with recommendation and consequence.

Never output only a UUID, lane, PR number, `waiting`, `blocked`, `draft`, or
`pipeline issue`. Those are observations; the checklist requires ownership and
an action.
