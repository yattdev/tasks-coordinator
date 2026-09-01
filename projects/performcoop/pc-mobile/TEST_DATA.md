# Test-data manifest: pc-mobile

- Status: `AWAITING_FIXTURE`
- Workspace ID: `d35ace87-2aae-4e9c-9114-f9899af7f64b`
- Repository: `3cb0b634-8e42-41b5-bbfe-aca39b66246e` (`/data/home/Code/pc-mobile`)
- Mobile-owned database artifact/load recipe: `NOT_APPLICABLE`, verified from
  the project rather than inferred from absence. `mockDebug` is documented as
  no-network/offline; `GatewayServiceMock` loads tracked JSON from
  `app/src/mock/assets/mock/`; and the app creates its DBFlow database from
  those inputs. No standalone reusable `db.sql` or `how-to-load.sh` is needed
  for this project slot. Live-backend testing uses the separately catalogued
  Performcoop service rather than a copied mobile SQL dump.
- Expected reviewed secret-free recipe:
  `projects/performcoop/pc-mobile/how-to-start.sh`
- The recipe must name the supported mock/local variant, guarded emulator/ADB
  procedure, required non-secret inputs and exact smoke/UI assertions. No
  credentials or environment values may be embedded.
- Provisioning decision: the owner will place the start recipe. Do not ask
  again, invent alternate mock data, copy a live task/main database, or create a
  substitute recipe.
- Resume trigger: owner placement of
  `projects/performcoop/pc-mobile/how-to-start.sh`. Then review it for secrets,
  portability and correct mock/local variant; execute it in a clean isolated
  task runtime; verify the declared guarded emulator/ADB smoke/UI assertions;
  and complete this manifest before serving a task.

Never add secrets or raw dump content to this manifest.
