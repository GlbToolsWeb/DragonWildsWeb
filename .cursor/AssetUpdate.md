# Asset Update Pipeline

This document describes how to rebuild the `Table/` data from game content and
sync it into `DWE/Assets/` so the web UI stays up to date.

## Source of Truth
- `Gameplay/` contains the raw game export data.
- `Table/` is generated from `Gameplay/` and becomes the canonical dataset for
  the editor (JSON + PNG).
- `DWE/Assets/` is the web-facing asset folder; it should be updated by copying
  matching files from `Table/`.

## Command Order
1. Build table data from gameplay exports:
   - `python tools/build_item_tables.py --source Gameplay\Items Gameplay\Character\Player\Equipment --table Table --content-root .`
2. Rename table assets and normalize icon references:
   - `python tools/rename_dwe_assets.py --root Table`
3. Sync Table files into DWE assets (replace matching names):
   - `python tools/sync_table_to_assets.py --table Table --assets DWE\Assets`
   - Optional dry run: `python tools/sync_table_to_assets.py --table Table --assets DWE\Assets --dry-run`
   - Optional cleanup (delete matched Table files to reveal new items):
     `python tools/sync_table_to_assets.py --table Table --assets DWE\Assets --delete-matched`
4. Rebuild the web catalog (single file used by the UI):
   - `python tools/build_dwe_catalog.py`

## Notes
- The sync step matches files by exact filename (case-insensitive) and replaces
  any matches found in `DWE/Assets/`.
- If a file name exists in multiple asset locations, all matches are replaced
  and a warning is printed.
- Missing matches are reported so you can decide whether to copy or ignore them.
- The site loads `web/data/catalog.json` only (no `catalog.full.json`).
- If you pass `--delete-matched`, only unmatched Table files remain so you can
  identify items that need manual placement.
