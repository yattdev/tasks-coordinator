# Human-QA test instances

Companion to the HUMAN-QA TEST INSTANCE GATE in PROMPT.md. Read both before
telling the human an instance is ready.

## Fit the fixture to the feature — do not default to copying production

Copying the live application database into a QA instance is the EXPENSIVE option
and is frequently the WRONG one. Decide per feature:

- **Purpose-built synthetic fixture** — the default. Choose it when the feature
  needs specific state that production does not contain (e.g. "an installed
  plugin whose marketplace catalog advertises a HIGHER version than installed"),
  or when the feature ACTS on data: dispatching runs, writing back to an external
  system, attaching to workspaces/worktrees.
- **Sanitized production snapshot** — only when broad real-world breadth is
  genuinely the thing under test (rich relationship graphs, long session
  histories) AND the feature has no live write path.

A task that refuses a copy instruction on these grounds is usually right. Two
independent findings from 2026-08-22 make the point concrete:

1. A copied board's workspace paths point at the operator's real worktrees.
   Inside a container those paths are ABSENT, so an attach fails closed. That
   proves isolation, but it also proves copied production data can never
   exercise a positive attach/reuse path — it only ever produces the negative case.
2. Production data cannot contain a not-yet-published upgrade, a monitored-step
   policy that does not exist upstream, or any state the feature was built to
   introduce.

## Hard prohibitions

- **Never import the operator's `master.key`.** It encrypts their production
  secrets; inside a LAN-published container it is a worse exposure than the row
  data. A key the instance GENERATES for itself is expected and required — do not
  delete that one. (These are different objects; be explicit which you mean.)
- **Never disable authentication** on an instance that holds copied real data.
  An instance was stopped mid-cycle for serving the operator's whole board
  unauthenticated on the LAN. Auth-disabled is acceptable ONLY for wholly
  synthetic fixtures.
- **Never open the source database read-write.** The proven-safe method is
  `sqlite3 -readonly <src> ".backup <tmp>"` (or a `?mode=ro` URI), snapshot to
  temp, then move only the snapshot into the STOPPED target container.
- **Never mutate the source**, including "harmless" repairs. Integrity warnings
  found in the source are findings to report, not defects to fix in passing.

## Credentials must be in the handoff

Every seeded instance requires a login, and a healthy instance nobody can enter
is useless. State the login as the FIRST line of the handoff, and say which case
applies:

- **Copy-seeded, ownership untouched** → the operator signs in with their OWN
  normal credentials. The copied user table contains their account and Argon2id
  hashes are self-contained (they do not need `master.key`). This is the
  preferred shape.
- **Ownership reassigned to a QA account** → their own credentials will NOT show
  the workspace. Say so explicitly or they will conclude the instance is broken.
- **Synthetic fixture** → their credentials cannot work; give the disposable
  account.

Create disposable accounts with the codebase's own password hashing, as a NEW
account only. Never reset an existing user's password, even in a copy.

**Verify the published credentials actually work** before reporting ready:
`POST /api/v1/auth/login` and check for 200. Handoffs have shipped with untested
passwords.

## Restored fixtures carry live CONFIGURATION, not just data

Auditing rows is not enough. A restored Redmine fixture was found with
`auto_status_writeback: true` from a previous run — moving a task during testing
would have written to the external system unprompted. Before handing over, audit
integration toggles, write-back switches, configured endpoints and credentials,
and disable anything pointing at a real system. State what you disabled.

## When the image cannot exercise the feature, say so

QA images routinely lack runtime capabilities: no `git` binary, no configured
agent-profile family, feature flags off, session-scoped MCP tools unreachable
from an HTTP client. When the success path cannot run:

- **Do NOT build a display-only fixture that looks ready.** Files staged to look
  like a working scenario convert an infrastructure gap into a FALSE BUG REPORT
  against the feature. This is worse than having no instance.
- Classify the task **ready for review without a runtime instance**, and hand the
  reviewer NAMED automated coverage — specific test functions and packages per
  claimed behaviour — plus a change summary and the verification command.
- Determine the limit from the code, not by assumption. One "no git therefore
  attach fails" diagnosis was wrong: attach was a pure filesystem/DB operation
  and the real blocker was agent-profile resolution, proven by one real launch
  attempt.

## Acceptance, verbatim

```
curl -s -o /dev/null -m 8 -w '%{http_code}\n' http://<LAN_IP>:<port>/     # 200
curl -s -m 8 http://<LAN_IP>:<port>/ | grep -o '<title>[^<]*</title>'
docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' <container>        # unless-stopped
docker inspect -f '{{range $p,$b := .HostConfig.PortBindings}}{{$p}} {{$b}}{{end}}' <container>
```

`--restart unless-stopped` is mandatory: a whole QA fleet was lost to a host
restart because no container carried a restart policy. Host-local curls to the
LAN IP prove the BIND, not the firewall — ask the operator to confirm one URL
from another machine and keep that caveat until they do.

## Identify which component a control belongs to before filing a defect

A "disabled control" report is not a defect until you confirm WHICH control it is.
A Notes task nearly filed a host/plugin regression over a disabled
`enhance-prompt-button` — which is the adjacent CORE task-chat control and
correctly depends on the user's default utility-agent setting. The feature's own
control (`notes-enhance-button` / `toolbar-item-enhance`) was enabled and correct.
Two similarly-named controls, different ownership, different correct behaviour.
Match the test-id/component to the feature under test before routing anything to
implementation; a phantom defect wastes a turn and impugns correct work.
