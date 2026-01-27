# Recipe Unlocker

## Goal
Build a new tool page at `docs/recipe-unlocker.html` that lists every recipe in
the game and highlights which recipes are unlocked for a loaded character via
the `RecipesUnlocked` array in the player `.json`.

## Data Source
- Recipe files appear to use the `RECIPE_*.json` naming convention under
  `Content/Gameplay`.
- We need a consolidated recipe catalog folder to drive the UI list and
  lookup-by-id behavior.

## Catalog Build Step
Use the new script to copy every `RECIPE_*.json` into `Recipes/`.

Command (default scan path):
`python tools/build_recipe_catalog.py`

Useful options:
- `--source Content/Gameplay` (override source root)
- `--output Recipes` (override output folder)
- `--no-flat` (preserve subfolders under `Recipes/`)
- `--dry-run` (print actions only)

## Catalog Index Step
Build a UI-friendly recipe index and copy required icons from gameplay content.
This step enriches each recipe with output/input item icons, display names, and
IDs for tooltip rendering and unlock matching.

Command (default paths):
`python tools/build_recipe_index.py`

Useful options:
- `--recipes Recipes` (source recipe folder)
- `--items Content/Gameplay` (source item definitions)
- `--content-root Content` (icon resolution root)
- `--output docs/data/recipes.json` (output catalog)
- `--icons-dir docs/recipes/icons` (copied icon folder)

### Filtering and Placeholders
- Recipes with no valid output item (`ItemsCreated` empty/null/Count 0) are
  skipped from the catalog.
- The script now indexes both `ITEM_*.json` and `DA_*.json` items.
- Missing icons fall back to `docs/DWE/Assets/Placeholders/recipe_icon.png`
  (copied into `docs/recipes/icons/`).

## Verified Mappings
- `RecipesUnlocked` in the player JSON stores **recipe PersistenceID values**
  (example in `Beb.json`).
- The recipe catalog now uses `persistence_id` for unlock matching and keeps
  `name` / `display_name` for UI labels.

## Next Steps
1. Build the `docs/recipe-unlocker.html` UI using `docs/data/recipes.json`.
2. Add player file loader and overlay unlocked state using `persistence_id`.
3. Add tooltips for `items_consumed` using the icon + count data.
