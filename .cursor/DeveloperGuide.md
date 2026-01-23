# Developer Guide

## Data Model Conventions
- Character inventory data omits empty slots; only occupied slots exist in JSON.
- `ItemData` is the stable item UID used to map to item definitions.
- `GUID` is a per-instance unique identifier; generation method is TBD.
- `Count` indicates stack size for stackable items.
- `VitalShield` appears on equippable items (observed value is 0).

## Inventory Slot Mapping
Use these ranges for validation and UI placement:
- Inventory `0-7`: Action bar
- Inventory `8-31`: Main
- Inventory `32-55`: Runes only
- Inventory `56-79`: Arrows only
- Inventory `80-103`: Quest items only
- PersonalInventory `0-19`: Personal items

## Item Tables (Planned)
We will build one or more item tables to drive the editor:
- Parse item definitions from `Gameplay/Items/**.json`.
- Join with string tables in `Gameplay/Items/ST_*.json` for display names and descriptions.
- Include derived fields (type, stackable, category) to support slot validation.

### Proposed Table Fields
- `item_uid` (from `ItemData`)
- `display_name` (from string tables)
- `description` (from string tables)
- `category` / `item_type` (derived from definition file)
- `stackable` / `max_stack`
- `equip_slot` (if applicable)

## Implementation Patterns
### Item UID Resolution
Prefer building a lookup table keyed by `ItemData` UID:
1. Scan `Gameplay/Items/` for item JSON definitions.
2. Extract each item's UID and metadata.
3. Merge string table values for display.

### Slot Validation
When adding items:
- Enforce slot range by inventory section.
- Enforce item type (runes/arrows/quest) for restricted slots.
- Keep empty slots omitted from the JSON output.

## Homepage Framer Workflow
- Edit Framer output locally (e.g., `docs/index.html` and `docs/homepage/framer-modules/`).
- Do not use runtime override scripts; keep changes in the generated Framer files.

## Page Template Workflow
- Use `docs/page-template.html` as the base for new static pages.
- Copy the template into `docs/` with a new filename and update title/description/OG/Twitter metadata.
- Keep page assets under `docs/homepage/assets/` and page modules under `docs/homepage/framer-modules/`.
- Avoid runtime overrides; edit the HTML and Framer module files directly.