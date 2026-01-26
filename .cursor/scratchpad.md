# Scratchpad

## Background and Motivation
This is our first time working on this project. The goal is to build a visual character file editor that can add/remove items from a character file by referencing item data from the exported content. We need a reliable item table to drive UI display and slot validation.
Planner note: focus this session on becoming familiar with the project structure, data sources, and current planning artifacts before implementation.
We will build a static, client-only web app (hosted on GitHub) that visually matches the in-game inventory UI and supports drag-and-drop item management.
Current request: read the `.cursor/` notes, then start the local webpage via Python (plan only in Planner mode; execution will follow once user switches to Executor mode).
Planner update: add a new context-menu action ("Dupe") for player inventory items to duplicate within the same section only, without spilling into other inventory sections.
Planner update: assess GitHub Pages readiness and required folders for static hosting.
Planner update: migrate web app into `docs/` for GitHub Pages Option B and update asset paths.
Planner update: user reports `ERR_EMPTY_RESPONSE` when hitting `http://localhost:8000/`; likely local dev server binding/firewall/port issue to confirm in Executor mode.
Planner update: requested review of `.cursor/` docs to identify any relevant info before further action.
Planner update: new homepage work will replace site `index.html` using `HomePage/ExampleIndex.html` as the starting point, with local copies of hosted images/assets where feasible.
Planner update: create a fidelity-focused rebuild plan for a hand-written HTML/CSS/JS version of the homepage.
Planner update: build a reusable Framer-based template page from `HomePage/ExamplePage.html`, applying the same localization and cleanup steps used for `docs/index.html`.

## Key Challenges and Analysis
- Inventory slot ranges differ by section and enforce item types.
- Empty slots are omitted from JSON and must remain omitted on save.
- `ItemData` is the only stable item identifier; `GUID` must be generated per instance.
- Item type constraints (runes/arrows/quest) must be derived from content data.
- Stackability and equip fields vary by item definition; we need a consistent model.
New constraint: duplication must target the next available slot in the same inventory section (bag/rune/ammo/quest/personal/loadout), and should no-op if that section is full.
New constraint: GitHub Pages serves only static files from repo root or `/docs`; asset paths must align to the publish root.
New constraint: `docs/` will become the working web root; all web assets and catalog must be contained there.
Additional analysis: documentation indicates content-driven item metadata and string tables under `Gameplay/Items/`, so item lookup and display naming will likely require a join step between item definition files and `ST_*.json` tables.
New constraints: item tabs map to inventory slot ranges (BagTab, RuneTab, AmmoTab, QuestTab), and PersonalInventory is a separate UI section that accepts BagTab items.
Observed in `DWE/Assets/`: each item is a paired `.json` + `.png` with a consistent schema (`ItemData`, `name`, `max_stack`, `icon`, `description`). Tabs are already organized into `BagTab/`, `RuneTab/`, `AmmoTab/`, and `QuestTab/` with deeper category folders for Bag/Ammo.
New constraint: `HomePage/ExampleIndex.html` is a Framer export with many remote assets (images, fonts, scripts) that need localization for self-hosting.
New constraint: large inline/minified CSS and JS blocks make manual editing risky; we should automate asset URL extraction and rewrites.
New constraint: third-party scripts (Cookiebot, GTM, Cloudflare, Framer analytics) may not be desired for the self-hosted site.
New constraint: hand-written rebuild must preserve visual fidelity across breakpoints and animations without Framer runtime.
New constraint: we should lock a reference viewport and compare before expanding to other breakpoints.
New constraint: `HomePage/ExamplePage.html` includes tracking scripts, external fonts, and remote Framer assets (icons/OG/preview images) that must be localized or removed.
New constraint: future pages should be created from a single template to reduce divergence; template should be documented and reusable.

## High-level Task Breakdown
1. Inspect character file structure and confirm slot rules.
2. Discover item definition schema under `Gameplay/Items/`.
3. Define item table schema and grouping strategy.
4. Prototype item table generation by `ItemFilterTags`.
5. Design visual editor UX (inventory grids, filters, search).
6. Implement editor with validation and save/export.
7. Add tests for parsing, validation, and serialization.
8. Validate item name resolution via string tables.
9. Map DWE `Assets/` tabs to inventory slot ranges and validate drag/drop rules.
10. Decide whether DWE `Assets/` becomes the primary item catalog source.
11. Add inventory-only "Dupe" context menu action with section-restricted slot targeting.
12. Define GitHub Pages publish root and required folders/files for hosting.
13. Move web app + DWE assets into `docs/` and rewrite paths to be relative.
14. Inventory homepage export assets and external dependencies.
15. Decide which third-party scripts/trackers to keep or remove.
16. Localize homepage images/fonts and update `index.html` references.
17. Validate homepage works in a static host environment.
18. Define fidelity targets and acceptance criteria for a hand-written rebuild.
19. Rebuild the homepage in static HTML/CSS/JS with progressive parity checks.
20. Inspect `HomePage/ExamplePage.html` for external dependencies and template structure.
21. Define a standard page template structure and asset path conventions for future pages.
22. Localize ExamplePage assets, scripts, and metadata into `docs/`.
23. Publish the first template-based page and document the workflow.

## Page Template Plan (Planner)
1. Inventory external URLs in `HomePage/ExamplePage.html` (scripts, fonts, images, search index).
2. Decide which scripts to strip (tracking/consent) and which Framer runtime modules to keep.
3. Mirror required images/icons/og assets into `docs/homepage/assets/` and rewrite references.
4. Mirror required fonts (Framer + Google) into `docs/homepage/assets/fonts/` and update CSS.
5. Define a template HTML file location in `docs/` for reuse (e.g., `docs/page-template.html`).
6. Parameterize page-specific metadata (title, description, og/twitter image) and content slots.
7. Document the template usage steps in `.cursor/DeveloperGuide.md` or a new doc.

## Web UI Build Plan (Planner)
1. Choose a static web stack (plain HTML/CSS/JS or minimal framework) and create base layout split: left ItemBrowser, right Inventory.
2. Add global background layers (`Landing_L1/L2/L3`) and top-center logo (`Logo_BG/Logo`) plus font setup (`SofiaSans`).
3. Implement Inventory panel shell on right using `Inventory_Background` and UI dividers; place action bar slots (8), tab row, 24-slot grid, and PersonalInventory grid.
4. Implement ItemBrowser shell on left with 32-slot grid and pagination dots.
5. Wire tab state so left and right panels switch in sync (Bag/Rune/Ammo/Quest) and swap tab images accordingly.
6. Load item catalog from `DWE/Assets/<Tab>/` and render into ItemBrowser pages (32 items per page).
7. Add file upload for character `.json`, parse inventory, and render items into right-side slots.
8. Enable drag/drop from ItemBrowser → Inventory with slot-range validation; show blocked state on invalid targets.
9. Add item removal and count editing with `max_stack` bounds.
10. Export updated character `.json`, omitting empty slots.

## Homepage Migration Plan (Planner)
1. Extract all external URLs from `HomePage/ExampleIndex.html` (images, fonts, scripts, CSS, preloads).
2. Categorize URLs: essential runtime vs. media assets vs. analytics/consent/telemetry.
3. Mirror media assets into a local folder (e.g., `docs/homepage/assets/`) and define a consistent path scheme.
4. Replace image/icon/og URLs with local paths; update `link rel="icon"` and social preview metadata.
5. Decide on fonts: download and self-host needed fonts or replace with existing local fonts.
6. Evaluate Framer runtime dependencies (modulepreloads, events script) and decide if we keep Framer output intact or rebuild a static layout.
7. Update canonical/og URLs to the new domain or relative site root.
8. Test locally and in the static hosting environment (GitHub Pages or equivalent).

## Homepage Rebuild Plan (Fidelity-First, Planner)
1. Baseline capture: lock a primary viewport (desktop 1440×900) and capture screenshots + element inventory (sections, headings, CTAs, cards, media, footers).
2. Asset inventory: catalog all images, videos, icons, and fonts currently used; map to local paths in `docs/homepage/assets/`.
3. Layout extraction: map the DOM into sections and components (hero, CTA rows, media blocks, feature grids, footer) with explicit spacing, typography, and colors.
4. CSS strategy: consolidate inline styles into structured CSS (variables for colors, spacing scale, typography scale).
5. HTML scaffold: rebuild semantic HTML for sections and components with minimal JS; ensure tab order and accessibility.
6. Typography parity: match font families, sizes, weights, line heights; validate against screenshots.
7. Interaction parity: re-implement hover/active states and simple transitions in CSS; only add JS where required.
8. Animation parity: reproduce key animations (fade-in, parallax, scroll-triggered) using lightweight JS/CSS; defer complex motion until layout matches.
9. Responsive parity: implement two additional breakpoints (tablet 1024, mobile 390); adjust spacing and type scale.
10. Visual diff checks: compare rebuild vs. Framer at each breakpoint and adjust until within tolerance.
11. Clean-up: remove unused assets, consolidate fonts, and document the new structure for future edits.

## Project Status Board
- [ ] Review `Beb.json` structure and required fields
- [ ] Catalog item definition file schemas
- [ ] Define item table schema and data sources
- [ ] Identify all `ItemFilterTags` values in item files
- [ ] Generate grouped item tables by `ItemFilterTags`
- [ ] Validate slot and item-type rules
- [x] Draft UX layout for editor
- [ ] Implement editor MVP
- [ ] Add tests for inventory parsing and output
- [ ] Validate DWE tab → slot range mapping
- [ ] Document DWE item schema and folder layout
- [x] Draft UI layout that mirrors in-game inventory
- [x] Build static UI scaffold (`web/`)
- [ ] Add inventory-only Dupe action and section-restricted duplication
- [ ] Plan GitHub Pages publish structure and required folders
- [ ] Plan migration to `docs/` as web root
- [x] Review `HomePage/ExampleIndex.html` for external dependencies
- [x] Decide on third-party scripts and tracking for homepage
- [ ] Localize homepage images/icons/fonts to repo
- [x] Replace `index.html` with localized homepage version
- [ ] Define fidelity targets and acceptance criteria for homepage rebuild
- [x] Capture reference screenshots + section inventory
- [ ] Build static HTML/CSS scaffold for homepage
- [ ] Re-implement hover/animation states
- [ ] Validate parity across desktop/tablet/mobile
- [ ] Review `HomePage/ExamplePage.html` external dependencies
- [ ] Define reusable page template and asset conventions
- [ ] Localize ExamplePage assets and metadata into `docs/`
- [ ] Document template page workflow

## Current Status / Progress Tracking
Planning phase: documentation initialized, slot rules documented, and item table approach drafted. Initial GUID format analysis completed. Item table plan pending. Familiarization pass started in Planner mode.
Planner note: new UI requirements and DWE asset tab mapping captured; awaiting deeper inspection of DWE assets and item tables.
Planner update: DWE assets use a simple item JSON schema and are already tab-grouped; UI draft next.
Executor update: static UI scaffold created in `web/` with background layers, logo, left ItemBrowser grid, right Inventory panel, and synced tab visuals.
Executor update: ItemBrowser now loads full DWE catalog, supports paging, and inventory supports file load, drag/drop, count editing, and export.
Executor update: local dev server started from `web/` via `python -m http.server` for manual UI testing.
Executor update: normalized catalog asset paths and fixed Rune tab normal image path to resolve missing UI icons.
Executor update: responsive layout uses CSS clamp variables and grid to scale panels with viewport size.
Executor update: increased panel and slot scaling to better fill available space while staying responsive.
Executor update: build script now captures BaseDurability, PowerLevel, and Weight when present.
Executor update: regenerated Table output from `Gameplay/Items` and `Gameplay/Character/Player/Equipment`.
Executor update: equipment items now include `VitalShield: 0` in generated table output.
Executor update: renamed Table assets by item name and updated icon references.
Executor update: patched missing item names to fall back to icon/filename in Table JSON.
Executor update: added sync script to replace `DWE/Assets` from `Table` by filename.
Executor update: sync script can now delete matched Table files to reveal unmatched items.
Executor update: ran sync with delete-matched; remaining Table files are unmatched items.
Executor update: rebuilt `web/data/catalog.full.json` from updated `DWE/Assets`.
Executor update: catalog build now includes durability, power level, weight, and vital shield fields.
Executor update: consolidated web catalog to `web/data/catalog.json` only and updated UI loader.
Executor update: asset path normalization no longer rewrites apostrophes to underscores.
Executor update: equipment items now include `Equipment` slot tags for Body/Cape/Head/Jewellery/Legs.
Executor update: added loadout row UI with equipment slot validation and overlays.
Executor update: loadout overlays hide when occupied; drag payload cached for loadout drops.
Executor update: inventory drag/drop now allowed across slots for inventory moves.
Executor update: clear drag highlight classes after drops and drag end.
Executor update: restored draggable flag on populated inventory/loadout slots.
Executor update: inventory drag/drop now swaps items when dropping onto occupied slots.
Executor update: moved panel badges to top center of item browser and inventory sections.
Executor update: added top badge labels and increased badge top padding.
Executor update: added header bar background and moved badges to top headers.
Executor update: added top page header bar and moved load/save actions into inventory header.
Executor update: moved logo into top header and resized header/load/save images.
Executor update: restored centered logo and doubled its size in the body.
Executor update: removed header logo from top bar.
Executor update: item browser supports double-click and context menu add actions with alert modal.
Executor update: removed action bar dividers and added tab background image.
Executor update: layered inventory background using InventoryBG images.
Executor update: adjusted inventory background layers to use contain sizing.
Executor update: scaled inventory background layers by 10 percent.
Executor update: inventory background now uses new top/bottom overlay images.
Executor update: swapped item browser/inventory card backgrounds and header layers.
Executor update: added equipment bar outline behind loadout row.
Executor update: added corner overlays for item browser and inventory cards.
Executor update: removed header back layer references after asset cleanup.
Executor update: added item browser scroller arrows with prev/next paging.
Executor update: added disabled arrow variants instead of hiding scroll buttons.
Executor update: added item browser search box with icon and filtering.
Executor update: moved status text under logo with loaded/unloaded visuals.
Executor update: moved status bar above the action bar in the inventory panel.
Executor update: centered status bar icon and text.
Executor update: added "Death's Wares" logo text with Crimson Pro font.
Executor update: vertically centered logo text within the logo layer.
Executor update: added tooltip UI for item hover details.
Executor update: tooltip now shows icon rows with power level overlay.
Executor update: power level icon moved to tooltip name row.
Executor update: adjusted tooltip icon sizes for power and durability.
Executor update: power level tooltip number switched to black.
Executor update: tooltip content left-aligned and power level number bolded.
Executor update: added left padding inside tooltip for alignment.
Executor update: added IMARU text to the top header.
Executor update: personal tab now uses background image behind label.
Executor update: added clear button for item browser search.
Executor update: hide search clear button when input is empty.
Executor update: clear tooltip datasets when re-rendering item browser slots.
Executor update: add Durability from BaseDurability on new items.
Executor update: inventory tooltip shows current/base durability and added Repair action.
Executor update: VitalShield injection now follows catalog vitalShield tag.
Executor update: documented character save output fields.
Executor update: layered header front overlay over header background.
Planner update: Dupe context-menu action requested for player inventory with section-limited duplication.
Executor update: added Dupe context-menu action with section-limited duplication.
Executor update: Dupe hidden for action bar and loadout slots.
Executor update: PersonalInventory MaxSlotIndex now set to highest used slot on save.
Executor update: count modal allows Enter to apply and does not cap at max.
Planner update: GitHub Pages hosting question raised; publish structure pending.
Planner update: user confirmed Option B and wants migration plan.
Executor update: moved web app and assets into docs/ and rewrote paths for Pages.
Executor update: restarted local Python server bound to IPv4 for localhost testing.
Executor update: generated `LootDropTable/DT_LootDropTable_EnemyNames.json` with internal enemy names for drop tables.
Executor update: generated `LootDropTable/DT_LootDropTable_ItemNames.json` with unique item IDs from loot tables.
Executor update: resolved item display names for all loot table items from `Gameplay/Items` and `Gameplay/Character`.
Executor update: added drop table page (`docs/drop-tables.html`) and script (`docs/drop-tables.js`) with autocomplete search and loot rendering.
Executor update: copied loot table data into `docs/data/` for web consumption.
Executor update: documented drop table update process in `.cursor/DropTableUpdate.md`.
Executor update: added `tools/update_drop_tables.py` to regenerate name lists and sync `docs/data/`.
Executor update: reviewed `.cursor` documentation (index, README, DeveloperGuide, scratchpad) to align with current project scope.
Planner update: reviewed `HomePage/ExampleIndex.html` and identified many external assets (Framer assets, Google fonts, analytics scripts) requiring localization decisions.
Executor update: replaced `docs/index.html` with the ExampleIndex homepage, removed analytics scripts, localized image assets to `docs/homepage/assets/`, and inserted placeholder URLs.
Executor update: restored Framer runtime markup/scripts in `docs/index.html` to fix missing hover/animation behavior while keeping analytics removed.
Executor update: localized non-Google fonts from `framerusercontent.com` into `docs/homepage/assets/fonts/` and rewrote font URLs in `docs/index.html`.
Executor update: captured baseline homepage screenshots at 1440x900 and stored them under `docs/homepage/baseline/`.
Executor update: section inventory (desktop): hero (logo/title, play button, Buy Now), Welcome to Ashenfall text block, image panels with heading copy (Runescape at its core, Survival through sorcery), and footer/social links.
Executor update: documented section inventory in `docs/homepage/baseline/section-inventory.md`.
Executor update: generated `docs/homepage/baseline/asset-inventory.md` with localized image/font lists and note about remaining remote video URL.
Executor update: created static rebuild scaffold in `docs/homepage/rebuild/` with `index.html`, `styles.css`, and `app.js` using localized assets.
Executor update: promoted rebuild to live homepage by replacing `docs/index.html` (backup saved as `docs/index.framer.html`).
Executor update: refined hero overlay/background, typography, and media frame styling for closer visual parity; added footer embers and synced rebuild HTML to `docs/index.html`.
Executor update: added responsive tuning for tablet/mobile breakpoints and hover transitions for hero CTA/play button.
Executor update: added styled social link placeholders and synced rebuild HTML to `docs/index.html`.
Executor update: replaced social placeholders with inline SVG icons and synced rebuild HTML to `docs/index.html`.
Executor update: added inline Steam-style icon to the hero Buy Now CTA and synced rebuild HTML to `docs/index.html`.
Executor update: tightened hero spacing, CTA icon sizing, and copy text width for closer alignment to baseline.
Executor update: refined hero spacing/CTA sizing and reduced social icon size for closer visual match.
Executor update: adjusted hero watch/play sizing and footer link density for closer parity.
Executor update: refined hero vertical alignment and footer spacing for closer baseline match.
Executor update: refined CTA sizing and spacing for closer hero parity.
Executor update: restored Framer homepage as live `docs/index.html` and added durable override system (`docs/homepage/overrides.js` + `overrides.json` + `overrides.md`).
Executor update: reviewed `.cursor` documentation (index, README, DeveloperGuide, scratchpad) to align with current project scope.
Executor update: replaced the remaining external hero video URL with a local image poster/source in the Framer module.
Executor update: removed homepage override files now that Framer is edited locally.
Executor update: documented the no-overrides Framer workflow in `.cursor/DeveloperGuide.md`.
Executor update: created `docs/page-template.html` from ExamplePage, localized assets/modules, and removed tracking scripts.
Executor update: swapped the Discord social icon background image(s) to `item_editor_icon.png` in `docs/index.html`.
Executor update: added a CSS override in `docs/index.html` to force the Discord icon image post-hydration.
Executor update: added a landing logo line with side text flanking the item editor logo on `docs/index.html`.
Executor update: hid another Framer container class (`framer-1glzj5b-container`) in `docs/shared-header.css`.
Executor update: removed missing ItemBrowser/Inventory background image refs from `docs/styles.css` to stop 404s.
Executor update: removed the remaining ItemBrowser background image ref to stop the last 404.
Executor update: added the editor logo line and tagline to `docs/item-editor.html`.
Executor update: converted the item editor tagline into a toggleable dropdown.

## Executor's Feedback or Assistance Requests
- Please confirm where the `.cursor/` documentation should live if not at the workspace root.
- GUIDs should be randomly generated for each injected item; generation method TBD.
- Confirm whether quest/rune/arrow types are explicitly marked in item JSON or inferred by folder.
 - Confirm the authoritative source for item table JSON (prebuilt vs generated from content).
 - Confirm whether DWE `Assets/` is the canonical catalog for items (recommended for UI browsing).
 - Confirm whether to remove or keep third-party scripts (Cookiebot, GTM, Cloudflare, Framer events) in the new homepage.
 - Confirm the intended public URL for canonical/og metadata updates.
 - Confirm target location for homepage assets (e.g., `docs/homepage/assets/` vs `docs/assets/`).

## Item Table Plan (Proposed)
- Source data: `Gameplay/Items/**/ITEM_*.json` with `Type: ItemData`.
- Key fields: `ItemData` (from `PersistenceID`), `display_name` (from `Name.SourceString`), `max_stack` (from `MaxStackSize`), `icon_path` (from `Icon.ObjectPath`).
- Grouping: one JSON file per unique `ItemFilterTags` value, stored in `Table/`.
- File naming: sanitize tag to filename, e.g. `ItemFilter.Material.BasicMaterial` → `Material.BasicMaterial.json`.
- Image handling: copy referenced icon `.png` into `Table/<group>/` to simplify UI lookup.
- Output schema per group:
  - `group_tag`
  - `items[]`: `{ item_data, display_name, max_stack, icon_source, icon_local }`

## UI Layout Draft (Planner)
- Primary layout mirrors in-game inventory:
  - Action bar row: 8 slots (slots `0-7`).
  - Tabbed grid: 24 slots (8 across × 3 down). Default shows BagTab slots `8-31`.
  - Switching tabs rebinds the same 24 visual slots to: Rune `32-55`, Ammo `56-79`, Quest `80-103`.
  - PersonalInventory always visible beneath: 20 slots arranged 8 across, 8 across, 4 across (slots `0-19` in `PersonalInventory` section).
- Tabs aligned to asset groups using `DWE/UI/*Tab*.png` for Bag/Rune/Ammo/Quest.
- Item browser panel (separate section) filtered by current tab; shows all items for that tab to support drag/drop into the 24-slot grid.
- Each inventory slot shows item icon with count overlay at bottom-right.
- Progressive feature targets: remove item, drag/drop from browser, change count (bounded by `max_stack`).
- File actions: upload character `.json`, display current items, export updated `.json` with empty slots omitted.

## UI Asset Integration Notes (Planner)
- Use `DWE/UI/Landing/Landing_L1.png`, `Landing_L2.png`, `Landing_L3.png` as layered page background.
- Layer `DWE/UI/Logo/Logo_BG.png` and `DWE/UI/Logo/Logo.png` at top-center of the page.
- Global font: `DWE/UI/SofiaSans.woff2` (also available via external link).
- Inventory panel sits on the right half of the screen, centered on `DWE/UI/Inventory/Inventory_Background.png`.
- Action bar area: top section framed by `Action_Bar_Outline.png` with 8 evenly spaced slots using `Item_BG.png`.
- Place `Action_Bar_Divider.png` below the action bar to separate the tabbed grid.
- Tabs order (left → right): Bag, Rune, Ammo, Quest.
  - Default tab is Bag; use `*_Selected.png` for the active tab and `*_Normal.png` for others.
- Place `Bottom_Divider.png` below the tabs.
- 24-slot grid (8×3) uses `Item_BG.png` per slot; add `Side_Divider.png` on left and right edges of this grid section.
- ItemBrowser (left side) is a simplified grid: 32 slots (8×4) using `Item_BG.png`.
- Use `DWE/UI/ItemBrowser/Current_Page_Dot.png` and `Non_Selected_Page_Dot.png` for ItemBrowser pagination only (no dots for player inventory).

## ItemBrowser Behavior (Planner)
- ItemBrowser sources its catalog from `DWE/Assets/<Tab>/` based on the active tab (Bag/Rune/Ammo/Quest).
- Default tab is Bag; both sides reflect the same active tab:
  - Right side (player inventory) shows current character items for that tab after a character `.json` is loaded; otherwise empty.
  - Left side (ItemBrowser) always shows all items from the active tab, enabling drag/drop into the player inventory.
 - Tabs stay in sync: switching the inventory tab switches the ItemBrowser tab to the same dataset to prevent misplacement.

## DWE Asset Paths (Planner)
- `DWE/Assets/BagTab/`
  - `Armour/` → `Capes/`, `General Armour/`, `Magic Armour/`, `Melee Armour/`, `Ranged Armour/`, `Shields/`, `Trinkets/`
  - `Consumables/` → `Buffs/`, `Burnt Food/`, `Cooked Food/`, `Drinks/`, `Potions/`, `Raw Food/`
  - `Materials/` → `Animal/`, `Bars/`, `Blocks/`, `Clay Components/`, `Cloth/`, `Crossbow Components/`, `Currency/`, `Dev Mats/`, `Fuel/`, `Gems/`, `Ground/`, `Herbs/`, `Leather/`, `Logs/`, `Loot Packs/`, `Magic/`, `Minerals/`, `Oils/`, `Planks/`, `Plants/`, `Seeds/`, `Shield Components/`, `Thread/`, `Tomes/`, `Vault/`
  - `Tools/` → `Axes/`, `Farming/`, `Pickaxes/`, `Tool Torch/`
  - `Weapons/` → `Dev Weapons/`, `Magic Weapons/`, `Melee Weapons/`, `Ranged Weapons/`
- `DWE/Assets/AmmoTab/` → `Arrows/`, `Bolts/`
- `DWE/Assets/QuestTab/`
  - `Dog Days/`, `Dragon Slayer/`, `Even More Restless Ghosts/`, `Goblin Diplomacy/`, `Granite Mauled/`, `Heartstrings/`,
  - `Highlighting the Problem/`, `Restless Ghosts/`, `The Wild Hunt/`, `Things That Go Boom In The Night/`, `Withering Heights/`
- `DWE/Assets/RuneTab/` → direct files (`Air Rune.json`, etc.)

## Lessons
- GUID values in `Beb.json` are 22 characters using base64url characters (`A-Z`, `a-z`, `0-9`, `-`, `_`). This suggests a 128-bit value encoded as base64url without padding (22 chars).
- Local UI testing: run `python -m http.server 8000` from `web/` and browse to `http://localhost:8000/`.
- DWE asset filenames replace apostrophes with underscores; normalize catalog image paths to match.
 - If localhost returns `ERR_EMPTY_RESPONSE`, restart `python -m http.server` with `--bind 127.0.0.1` and browse to `http://127.0.0.1:8000/`.