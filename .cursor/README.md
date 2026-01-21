# RSDragonwilds Character Editor

## Overview
This workspace contains exported game content and a sample character file. The goal is to build a visual character editor that can add/remove items in a character file by referencing item definitions from the content data.

## Key Paths
- `Beb.json`: Example character file with `Inventory` and `PersonalInventory` sections.
- `Gameplay/Items/`: Item definitions, recipes, vendors, and related data.
- `Gameplay/Items/ST_*.json`: String tables for item names, descriptions, and info.
- `Art/UI/`: UI assets that may be useful for the editor visuals.
- `DWE/Assets/`: Curated item catalogs for Bag/Rune/Ammo/Quest tabs.
- `DWE/UI/`: UI assets for the web interface (inventory, logo, landing).
- `web/`: Static web UI scaffold (HTML/CSS/JS).

## Character File Notes
- Empty slots are omitted from JSON; only occupied slots are stored.
- `ItemData` is the UID used to identify the item.
- `GUID` is a per-instance identifier that must be generated for injected items.
- `Count` appears on stackable items.
- `VitalShield` appears on equippable items (currently observed as 0).

## Inventory Slot Ranges
- Inventory: `0-7` action bar, `8-31` main, `32-55` runes, `56-79` arrows, `80-103` quest items
- PersonalInventory: `0-19` personal items
