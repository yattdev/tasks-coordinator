# Test-data manifest: pc-mobile

- Status: `STALE`
- Workspace ID: `d35ace87-2aae-4e9c-9114-f9899af7f64b`
- Repository: `3cb0b634-8e42-41b5-bbfe-aca39b66246e` (`/data/home/Code/pc-mobile`)
- Mobile-owned database artifact/load recipe: `NOT_APPLICABLE`, verified from
  the project. `mockDebug` is no-network/offline, `GatewayServiceMock` uses
  tracked JSON, and DBFlow creates the mobile database from those inputs. Live
  backend testing uses an isolated Performcoop service, never a copied mobile
  SQL dump.
- Linked backend fixture: `performcoop-db-backups-20260302-d1a9b7a7`, canonical
  private artifact and restore receipt recorded in the Performcoop project slot.
  The dump restores substantial project/training/session/participant data and is
  compatible with the accepted Performcoop task head.
- Signature-scenario receipt: the raw restore had no exact signature-enabled
  signed/unsigned pair. An approved clearly synthetic, idempotent,
  destination-only overlay created project 123, training 5823, session 28322,
  signed participant 201874 and unsigned participant 201875 without mutating
  restored business rows. Internal browser/mobile authentication, permissions,
  project/training/signature APIs, state distinction and protected PNG access all
  passed.
- Why status is `STALE`: the preserved linked backend is healthy internally, but
  the guarded Compose broker has not produced a usable host/LAN mapping. The
  first repair restored stdin and the next repair fixed runtime-wrapper
  ownership, but replaying the real pre-repair saved model still publishes port
  0 after successful recreation. The first replay request returned only
  unfinished synthetic diagnosis; follow-up Support request
  `7a70141c-e7a2-48d0-84d8-68826afaeae8` owns completion. Do not send a
  backend URL or credentials, claim emulator reachability, or complete mobile QA
  until `compose port`, localhost HTTP and LAN/emulator HTTP all pass on the
  preserved exact runtime.
- Mobile setup after that trigger: deliver only the task-scoped backend URL,
  disposable credentials, exact scenario IDs and non-secret
  `TEST_DATA_RECEIPT`; select the networked development flavor; start the guarded
  Android AVD; verify API reachability/login and the signed-versus-unsigned pencil
  color path. Never point a mobile test at shared/main Performcoop.
- Refresh rule: rerun compatibility and exact feature assertions for any fixture,
  application head, recipe, scenario overlay, or runtime-publication change.

Never add secrets or raw dump content to this manifest.
