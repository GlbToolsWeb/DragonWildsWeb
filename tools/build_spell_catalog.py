import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ITEM_ID_PATTERN = re.compile(r"(ITEM_[A-Za-z0-9_]+|DA_[A-Za-z0-9_]+)")


def load_json(path: Path) -> list[dict[str, Any]] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[WARN] JSON parse failed: {path} ({exc})")
        return None
    if not isinstance(data, list) or not data:
        print(f"[WARN] Unexpected JSON root: {path}")
        return None
    return data


def resolve_object_path(object_path: str) -> Path | None:
    if not object_path:
        return None
    cleaned = object_path.replace("RSDragonwilds/Content/", "")
    cleaned = cleaned.rstrip(".0")
    return Path(cleaned + ".png")


def file_hash(path: Path) -> str:
    hasher = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def copy_icon(icon_abs: Path, icons_dir: Path) -> str:
    icons_dir.mkdir(parents=True, exist_ok=True)
    dest = icons_dir / icon_abs.name
    if dest.exists():
        if file_hash(dest) == file_hash(icon_abs):
            return dest.name
        base = icon_abs.stem
        suffix = file_hash(icon_abs)[:8]
        dest = icons_dir / f"{base}_{suffix}{icon_abs.suffix}"
    dest.write_bytes(icon_abs.read_bytes())
    return dest.name


def extract_item_id(item_data: dict[str, Any]) -> str:
    object_name = item_data.get("ObjectName", "")
    object_path = item_data.get("ObjectPath", "")
    match = ITEM_ID_PATTERN.search(str(object_name))
    if match:
        return match.group(1)
    if object_path:
        return Path(object_path).stem
    return ""


def build_item_lookup(
    source_dir: Path, content_root: Path, icons_dir: Path
) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    icon_missing = 0
    item_count = 0

    for file_path in sorted(source_dir.rglob("ITEM_*.json")):
        data = load_json(file_path)
        if not data:
            continue
        entry = next((row for row in data if row.get("Properties")), data[0])
        props = entry.get("Properties", {})
        item_id = entry.get("Name") or file_path.stem
        display_name = (
            props.get("Name", {}).get("SourceString")
            or props.get("Name", {}).get("LocalizedString")
            or props.get("InternalName")
            or item_id
        )
        icon_obj = props.get("Icon", {}).get("ObjectPath") or ""
        icon_rel = resolve_object_path(icon_obj)
        icon_file = ""
        if icon_rel:
            icon_abs = content_root / icon_rel
            if icon_abs.exists():
                icon_file = copy_icon(icon_abs, icons_dir)
            else:
                icon_missing += 1
                print(f"[WARN] Icon not found: {file_path} -> {icon_obj}")
        else:
            icon_missing += 1
            print(f"[WARN] Icon missing: {file_path}")

        lookup[item_id] = {
            "item_id": item_id,
            "display_name": display_name,
            "icon": icon_file,
        }
        item_count += 1

    print(f"[INFO] Items indexed: {item_count}")
    print(f"[INFO] Missing item icons: {icon_missing}")
    return lookup


def extract_spell_entry(data: list[dict[str, Any]]) -> dict[str, Any] | None:
    for entry in data:
        props = entry.get("Properties", {})
        if props.get("SpellDisplayName") and props.get("PersistenceID"):
            return entry
    return None


def extract_cost_modules(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    modules = []
    for entry in data:
        entry_type = str(entry.get("Type", ""))
        entry_class = str(entry.get("Class", ""))
        if "SpellModule_CostItems" in entry_type or "SpellModule_CostItems" in entry_class:
            modules.append(entry)
    return modules


def build_spell_catalog(
    spells_dir: Path,
    item_lookup: dict[str, dict[str, Any]],
    content_root: Path,
    icons_dir: Path,
) -> list[dict[str, Any]]:
    spells: list[dict[str, Any]] = []
    spell_count = 0
    icon_missing = 0
    placeholder_icon = ""
    placeholder_path = (
        content_root
        / "Art"
        / "UI"
        / "Skills"
        / "Icons"
        / "Unlock"
        / "Placeholder"
        / "T_Skill_Placeholder_Active_Spells.png"
    )
    if placeholder_path.exists():
        placeholder_icon = copy_icon(placeholder_path, icons_dir)
    else:
        print(f"[WARN] Placeholder spell icon missing: {placeholder_path}")

    for file_path in sorted(spells_dir.rglob("USD_*.json")):
        data = load_json(file_path)
        if not data:
            continue
        spell_entry = extract_spell_entry(data)
        if not spell_entry:
            print(f"[WARN] Spell data missing: {file_path}")
            continue
        props = spell_entry.get("Properties", {})

        display_name = (
            props.get("SpellDisplayName", {}).get("SourceString")
            or props.get("SpellDisplayName", {}).get("LocalizedString")
            or spell_entry.get("Name")
            or file_path.stem
        )
        requirements = (
            props.get("SpecialRequirementsText", {}).get("SourceString")
            or props.get("SpecialRequirementsText", {}).get("LocalizedString")
            or ""
        )

        spell_icon_obj = props.get("SpellIcon", {}).get("ObjectPath") or ""
        spell_tag_obj = props.get("SpellTagIcon", {}).get("ObjectPath") or ""
        spell_icon = ""
        spell_tag_icon = ""

        spell_icon_rel = resolve_object_path(spell_icon_obj)
        if spell_icon_rel:
            spell_icon_abs = content_root / spell_icon_rel
            if spell_icon_abs.exists():
                spell_icon = copy_icon(spell_icon_abs, icons_dir)
            else:
                icon_missing += 1
                print(f"[WARN] Spell icon not found: {file_path} -> {spell_icon_obj}")
        elif spell_icon_obj:
            icon_missing += 1
        if not spell_icon and placeholder_icon:
            spell_icon = placeholder_icon

        spell_tag_rel = resolve_object_path(spell_tag_obj)
        if spell_tag_rel:
            spell_tag_abs = content_root / spell_tag_rel
            if spell_tag_abs.exists():
                spell_tag_icon = copy_icon(spell_tag_abs, icons_dir)
            else:
                icon_missing += 1
                print(f"[WARN] Tag icon not found: {file_path} -> {spell_tag_obj}")
        elif spell_tag_obj:
            icon_missing += 1

        costs = []
        for module in extract_cost_modules(data):
            module_props = module.get("Properties", {})
            for cost in module_props.get("ItemsCostInfo", []) or []:
                item_data = cost.get("ItemData", {}) or {}
                item_id = extract_item_id(item_data)
                count = cost.get("Count", 1)
                lookup = item_lookup.get(item_id, {})
                costs.append(
                    {
                        "item_id": item_id,
                        "count": count,
                        "display_name": lookup.get("display_name", item_id),
                        "icon": lookup.get("icon", ""),
                    }
                )

        spells.append(
            {
                "persistence_id": props.get("PersistenceID", ""),
                "display_name": display_name,
                "requirements": requirements,
                "cooldown": props.get("CooldownDuration"),
                "spell_icon": spell_icon,
                "spell_tag_icon": spell_tag_icon,
                "costs": costs,
                "internal_name": props.get("InternalName", ""),
            }
        )
        spell_count += 1

    print(f"[INFO] Spells indexed: {spell_count}")
    print(f"[INFO] Missing spell icons: {icon_missing}")
    return spells


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a UI-friendly spell catalog from USD_*.json files."
    )
    parser.add_argument(
        "--spells",
        default="Content/Gameplay",
        help="Directory containing USD_*.json spell files.",
    )
    parser.add_argument(
        "--items",
        default="Content/Gameplay",
        help="Directory containing ITEM_*.json files.",
    )
    parser.add_argument(
        "--content-root",
        default="Content",
        help="Content root used to resolve icon ObjectPath values.",
    )
    parser.add_argument(
        "--output",
        default="docs/data/spells.json",
        help="Output JSON path for the spell catalog.",
    )
    parser.add_argument(
        "--icons-dir",
        default="docs/spells/icons",
        help="Directory to copy spell/item icons into.",
    )
    args = parser.parse_args()

    spells_dir = Path(args.spells)
    items_dir = Path(args.items)
    content_root = Path(args.content_root)
    output_path = Path(args.output)
    icons_dir = Path(args.icons_dir)

    if not spells_dir.exists():
        print(f"[ERROR] Spells directory not found: {spells_dir}")
        return 1
    if not items_dir.exists():
        print(f"[ERROR] Items directory not found: {items_dir}")
        return 1

    item_lookup = build_item_lookup(items_dir, content_root, icons_dir)
    spells = build_spell_catalog(spells_dir, item_lookup, content_root, icons_dir)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(spells, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(f"[INFO] Wrote spell catalog: {output_path}")
    print(f"[INFO] Icons output: {icons_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
