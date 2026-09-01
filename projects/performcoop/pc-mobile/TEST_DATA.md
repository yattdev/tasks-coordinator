# Test-data manifest: pc-mobile

- Status: `DATABASE_NOT_APPLICABLE_RECIPE_PENDING`
- Workspace ID: `d35ace87-2aae-4e9c-9114-f9899af7f64b`
- Repository: `3cb0b634-8e42-41b5-bbfe-aca39b66246e` (`/data/home/Code/pc-mobile`)
- Mobile-owned database artifact/load recipe: `NOT_APPLICABLE`. The Android
  offline `mock` flavor uses repository JSON assets and needs no reusable SQL
  dump. Local integration must consume a compatible task-owned Performcoop
  backend fixture/receipt; it must not duplicate that database here.
- Expected reviewed secret-free recipe:
  `projects/performcoop/pc-mobile/how-to-start.sh`
- The recipe must name the supported mock/local variant, guarded emulator/ADB
  procedure, required non-secret inputs and exact smoke/UI assertions. No
  credentials or environment values may be embedded.
- Resume trigger: the owner supplies/reviews the start recipe, or a concrete
  task records a verified equivalent command and exact-head emulator receipt;
  then version the recipe and its accepted assertions here.

Never add secrets or raw dump content to this manifest.
