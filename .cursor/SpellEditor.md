# Spell Editor

## Goal
Build a spell editor at `docs/spell-editor.html` that displays and edits the
player's spellbooks. The UI mirrors the in-game radial wheel and lets users
assign spells, remove spells, and save updates to `Spellcasting.SelectedSpells`.

## Data Source
- Spell definitions live in `Content/Gameplay/**/USD_*.json`.
- Each spell provides `PersistenceID`, display name, requirements, icons, and
  optional cost items (runes/items).

## Catalog Build Step
Generate a UI-friendly catalog from `USD_*.json` and copy icons into
`docs/spells/icons/`.

Command (default paths):
`python tools/build_spell_catalog.py`

Useful options:
- `--spells Content/Gameplay` (source spell folder)
- `--items Content/Gameplay` (source item definitions)
- `--content-root Content` (icon resolution root)
- `--output docs/data/spells.json` (output catalog)
- `--icons-dir docs/spells/icons` (copied icon folder)

### Icon Fallback
- If `SpellIcon` is missing, the script falls back to
  `Content/Art/UI/Skills/Icons/Unlock/Placeholder/T_Skill_Placeholder_Active_Spells.png`
  (copied into `docs/spells/icons/`).

## Player Save Mapping
- Player JSON stores spell data under `Spellcasting.SelectedSpells`.
- There are **48 slots** total (4 spellbooks × 12 slots).
- Slot order is **clockwise**, starting at the top (slot 0 = top).
- Empty slots are stored as empty strings (`""`).

## UI Notes
- Spell browser (left) shows all spells from `docs/data/spells.json`.
- Radial wheel (right) shows the active spellbook (12 slots).
- Drag/drop from browser to wheel assigns a spell.
- Dragging a spell off the wheel clears the slot.
- Right‑click a slot for **Remove**.
- Save button overwrites `Spellcasting.SelectedSpells` and writes the file.

## Next Steps (when game updates)
1. Run the catalog build step to regenerate `docs/data/spells.json` and icons.
2. Verify new spells appear in the browser grid.
3. Validate a few spell tooltips (name, requirements, cooldown, costs).
4. Load/save a player file to confirm the `SelectedSpells` array updates.
