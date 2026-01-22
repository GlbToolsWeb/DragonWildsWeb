# Drop Table Update Guide

This document describes how to update the Drop Tables data used by the website.

## Source Files
- `LootDropTable/DT_LootDropTable.json` - Raw loot drop table export.
- `LootDropTable/DT_LootDropTable_EnemyNames.json` - Internal enemy names mapped to display names.
- `LootDropTable/DT_LootDropTable_ItemNames.json` - Loot item IDs mapped to display names.

## Web Data Files
These are the copies consumed by the website:
- `docs/data/loot_drop_table.json`
- `docs/data/loot_drop_table_enemy_names.json`
- `docs/data/loot_drop_table_item_names.json`

## Update Steps
1. **Replace the raw loot table export**
   - Update `LootDropTable/DT_LootDropTable.json` with the latest game export.

2. **Update enemy display names**
   - Edit `LootDropTable/DT_LootDropTable_EnemyNames.json` so each internal key has the correct display name.
   - The UI search uses these display names.

3. **Regenerate names and sync web data**
   - Run the helper script:
     - `python tools/update_drop_tables.py`
   - This refreshes the enemy/item name lists from the loot table, preserving any
     existing display names you already filled in.
   - It also copies the three source files into `docs/data/` using the web filenames above.
   - The Drop Tables page reads only from `docs/data/`.

## Notes
- Run the script after you update `LootDropTable/DT_LootDropTable.json` so the
  extracted item/enemy lists stay in sync.
- The Drop Tables page matches items by display name against `docs/data/catalog.json`.
  If the catalog is missing an item or name changes, update the catalog using
  the asset pipeline in `AssetUpdate.md`.
- If new loot items appear and you do not have matching icons/names, update
  the catalog first to avoid missing images.
