# Filesystem & Docker access contract

Status: **agreed 2026-08-29** between the operator, the host Codex consultation, and the
workspace Coordinator. Supersedes ad-hoc per-path fixes.

Design goal: **permissive enough that no agent is ever blocked doing legitimate work, strict
enough that nothing can destroy what it does not own.** Where those conflict, prefer granting
access and detecting misuse over withholding access and stalling the board.

## 0. Enforcement model

- `kandev-agent-guard` is the single enforcement point. Every provider runs its full-access /
  prompt-bypass mode **inside** the guard.
- "Bypass" means the *provider's own* permission prompting is disabled. **The guard's
  restrictions are never bypassable by the provider.** Any future mode that weakens the guard
  itself is outside this contract.
- **Each agent has a private mount namespace.** An agent sees its own overrides and no others.
  Absence of a mount in one namespace is not evidence about another.
- Denials fail closed and must be legible: name the exact path, the rule that refused, and the
  principal. Today's guard errors already do this; keep it.

## 1. Principals

| Principal | Resolution |
| --- | --- |
| Ordinary task agent | Its own Kandev task/session |
| Validated Coordinator | Registered coordinator repository **plus** platform-attested task/session metadata |
| Operator / human | Out of scope here; unrestricted by design |

**Coordinator validation must be attested, never self-asserted.** The guard resolves it from
the platform's authoritative session record. If any value the agent process can influence is
sufficient to claim coordinator identity, the model collapses — an ordinary task could claim
workspace-wide write access.

**Revocation:** if validation fails or cannot be re-established mid-session, rights drop
immediately to ordinary-task scope. Elevated rights never survive a state transition that can
no longer prove them. (Sessions here resume and fail repeatedly; this is not hypothetical.)

## 2. Ordinary task agent — read/write

Granted `rw`:
- its own task root (`/data/tasks/<its-task>/…`);
- the Git metadata it needs to commit: **its own per-worktree admin directory**
  (`<common>/.git/worktrees/<its-worktree>`) plus the shared object/ref writes a normal
  `add`/`commit`/`fetch` requires.

Granted `ro`: registered project checkouts it must read to build.

**Amendment adopted:** rw is scoped to the task's *own* admin subdirectory, **not** the whole
common `.git`. Granting the entire common directory exposes
`.git/worktrees/<every other task>` to any task — a cross-task blast radius through a path
nobody thinks of as shared, and the same surface as the missing/mismatched worktree-admin
defect. Where object/ref writes cannot be separated at the filesystem layer, they are shared;
the per-worktree admin entries are not.

Denied: other task roots, other workspaces, the Code root, host paths.

## 3. Validated Coordinator — workspace-scoped authority

Granted `rw` across **its own workspace only**:
- every active task root in that workspace;
- every registered project checkout in that workspace;
- the Git common directories those checkouts require;
- the canonical coordinator checkout.

Rationale: the Coordinator performs Done terminal-integrity verification and cleanup across
task worktrees. Read-only access allows it to *detect* unpushed or unique work but not to
*complete* terminal cleanup, which leaves resources to accumulate and forces escalation for
routine disposal.

**Conditions:**
1. **Audit every Coordinator write outside its own task root** — principal, path, operation,
   timestamp. This grant makes a buggy or mistaken Coordinator capable of destroying every
   task's uncommitted work in its workspace. Policy should not rest solely on agent good
   behaviour; logging makes misuse detectable at negligible cost.
2. Destructive operations on another task's resources still require the Done terminal-integrity
   gate: merged canonical PR, clean tree, no unpushed task commits, no live dependant. The
   filesystem permits it; the charter still governs when it is allowed.
3. Coordinator authority is **workspace-scoped**. Coordinators of different workspaces are
   peers with no standing over each other's resources.

## 4. Absolute prohibitions — all principals

- Other workspaces' task roots, checkouts, and resources.
- Unregistered directories under Code.
- **The Code root itself** — specific *registered checkouts* are writable per §2/§3; the root
  is never writable and no principal may create new directories at it.
- Host paths outside the managed tree.
- Raw Docker socket or daemon access.
- Privilege escalation; any destructive host access.

A denial here is a policy boundary, never a puzzle to route around. Record the exact error and
request registration or a reviewed operation.

## 5. Docker

- **Ordinary task:** task-scoped Compose only.
- **Validated Coordinator:** workspace-mapped containers through the audited workspace broker.
  Least privilege in order — `inspect`, then bounded `logs --tail N --since D`, then `db-dump`
  only when task data is genuinely required. Dumps are sensitive, audited, short-lived.
- **No principal:** cross-workspace access, raw daemon, or socket.

## 6. Mount-health verification — rule plus mechanism

**Mount health is tested inside the target agent's namespace, never inferred from another.**

This rule requires a mechanism, or it removes the only available detection method and
guarantees the next operator or Coordinator guesses again. **The guard must expose a per-task
writability probe** the Coordinator can invoke for a target task, returning at minimum: task
root writable, git-dir writable, `git add -A --dry-run` result.

Until that exists, the only valid check is to ask the owning agent to run:

```
git -C <its-worktree> add -A --dry-run
```

and report. A Coordinator-side `findmnt`, `/proc/mounts`, or `touch` probe against another
agent's path says only that *the Coordinator* lacks access — which may be a correct scope
boundary — and says nothing about the owning task.

Incident that produced this rule: on 2026-08-29 the Coordinator probed sibling worktrees from
its own namespace, saw `ro`, and escalated a board-wide read-only regression that did not
exist. It imposed a dispatch hold, withheld an approved UX direction, and declined to start a
requested task — all on invalid evidence.

## 7. Implementation status — validated 2026-08-29T05:0xZ

Independently revalidated with reversible write probes from coordinator session
`2b3b715c-8dff-43b6-af81-5d0f1f94f246`. See `docs/LEARNING_LOG.md` 2026-08-29c for evidence.

1. Per-task writability probe (§6) — **DONE.** `docker kandev workspace probe <task-uuid>`.
2. Attested Coordinator validation (§1) — **DONE.** Exported task/session pair matched against
   `kandev.db`; workspace derived, never accepted from the agent. Partial or mismatched IDs fail
   closed to ordinary scope. Rechecked every 15s; revocation emits `scope_revoked`.
3. Audit log for Coordinator writes outside its own task root (§3 condition 1) — **PARTIAL.**
   `/data/logs/coordinator-workspace-audit.jsonl` records scope *grants* (principal, session,
   workspace, cwd, full rw scope, timestamp). It does **not** record individual writes, so the
   control §3 relies on to make a mistaken Coordinator detectable is not yet in place.
4. Per-worktree admin scoping for ordinary tasks (§2) — **DONE.** Verified against a live
   ordinary task's guard argv: common `.git` bound rw, `worktrees` registry bound ro, only that
   task's own admin entry rebound rw.
5. Coordinator workspace-wide rw (§3) — **DONE.** 118 granted paths (110 task roots + 8
   registered checkouts), all write-probed. Parents `/data/home/Code`, `/data/home`,
   `/data/tasks` remain ro; other workspaces' task roots and managed repo roots are denied.

### Open defects

- **The coordinator repo grant shadows the §2 sibling-admin overlay.** `--bind
  /data/home/Code/<repo>` is applied after `--ro-bind <repo>/.git/worktrees`, so for a validated
  Coordinator the overlay is inert and every sibling worktree admin directory is writable. Fix
  by ordering the coordinator repo binds before the worktree overlay, or by implementing item 3.
- **`/data/home/go` is absent from the support-path allowlist**, so default `GOMODCACHE` is
  read-only while every other language cache is writable (degradation D9).
- **Broker tokens are passed in argv** and are readable from `/proc/<pid>/cmdline` by any
  same-UID process, including tokens belonging to other workspaces' agents. Token plus matching
  cwd is the whole authorization.
- **`/data/data/kandev.db` is readable by every agent**, exposing cross-workspace metadata
  outside the broker. Read-only, but outside §4's intent.
