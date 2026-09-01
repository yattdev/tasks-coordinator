# Test-data manifest: pc-mobile

- Status: `READY_LINKED_BACKEND`
- Workspace ID: `d35ace87-2aae-4e9c-9114-f9899af7f64b`
- Repository: `3cb0b634-8e42-41b5-bbfe-aca39b66246e` (`/data/home/Code/pc-mobile`)
- Mobile-owned database artifact/load recipe: `NOT_APPLICABLE`, verified from
  the project rather than inferred from absence. `mockDebug` is documented as
  no-network/offline; `GatewayServiceMock` loads tracked JSON from
  `app/src/mock/assets/mock/`; and the app creates its DBFlow database from
  those inputs. No standalone reusable `db.sql` or `how-to-load.sh` is needed
  for this project slot. Live-backend testing uses the separately catalogued
  Performcoop service rather than a copied mobile SQL dump.
- Linked backend fixture: use
  `performcoop-last-db-20260508-1fcb706c` from the `performcoop` project slot.
  The Coordinator provisions a task-owned Performcoop web/DB instance first,
  verifies its `TEST_DATA_RECEIPT`, and gives the mobile task only that
  task-owned backend URL plus disposable test credentials.
- Mobile setup remains project/task-specific: select the networked development
  flavor, point it at the isolated backend URL, start the guarded Android AVD,
  and verify API reachability, login and the task feature path. Never point a
  mobile test at the shared/main Performcoop service.
- Refresh rule: reuse the linked backend receipt while its fixture hash,
  engine, exact backend head and scenario remain valid. A mobile workflow-step
  change alone does not justify another dump/import.

Never add secrets or raw dump content to this manifest.
