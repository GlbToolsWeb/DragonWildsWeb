import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Optional, Tuple


def sanitize_tag(tag: str) -> str:
    tag = tag.replace("ItemFilter.", "")
    tag = tag.split(".")[-1]
    return re.sub(r"[^A-Za-z0-9._-]+", "_", tag)


def resolve_icon_path(object_path: str, content_root: Path) -> Tuple[str, Optional[Path]]:
    if not object_path:
        return "", None
    cleaned = object_path.replace("RSDragonwilds/Content/", "")
    cleaned = cleaned.rstrip(".0")
    rel_path = Path(cleaned + ".png")
    abs_path = content_root / rel_path
    return cleaned, abs_path if abs_path.exists() else None


def load_item_data(file_path: Path) -> dict | None:
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[WARN] JSON parse failed: {file_path} ({exc})")
        return None
    if not data or not isinstance(data, list):
        print(f"[WARN] Unexpected JSON root: {file_path}")
        return None
    for entry in data:
        props = entry.get("Properties", {})
        if isinstance(props, dict) and props.get("PersistenceID"):
            return entry
    return data[0] if data else None


def extract_item(
    entry: dict,
    source_file: Path,
    content_root: Path,
    requires_vital_shield: bool,
    equipment_slot: str | None,
) -> Optional[Tuple[str, dict, Optional[Path], str]]:
    props = entry.get("Properties", {})
    tags = props.get("ItemFilterTags") or []
    item_filter_tags = [t for t in tags if t.startswith("ItemFilter.")]
    if item_filter_tags:
        if len(item_filter_tags) > 1:
            print(f"[WARN] Multiple ItemFilterTags, using last: {source_file} -> {item_filter_tags}")
        tag = item_filter_tags[-1]
    else:
        category_tag = props.get("Category", {}).get("TagName") or ""
        tag = category_tag if category_tag else "Misc"

    name = props.get("Name", {}).get("SourceString") or ""
    description = props.get("Description", {}).get("SourceString") or ""
    if not description:
        description = props.get("FlavourText", {}).get("SourceString") or ""
    if not description:
        buff_datas = props.get("BuffDatas") or []
        if isinstance(buff_datas, list) and buff_datas:
            buff_desc = buff_datas[0].get("Description", {}).get("SourceString") or ""
            description = buff_desc
    persistence_id = props.get("PersistenceID") or ""
    internal_name = props.get("InternalName") or ""
    max_stack = props.get("MaxStackSize")
    if max_stack is None:
        max_stack = 1
    icon_obj = props.get("Icon", {}).get("ObjectPath") or ""
    base_durability = props.get("BaseDurability")
    power_level = props.get("PowerLevel")
    weight = props.get("Weight")

    _icon_source, icon_abs = resolve_icon_path(icon_obj, content_root)

    item = {
        "ItemData": persistence_id,
        "name": name,
        "max_stack": max_stack,
        "icon": "",
        "description": description,
    }
    if not item["name"]:
        item["name"] = internal_name or source_file.stem
    if equipment_slot:
        item["Equipment"] = equipment_slot
    if requires_vital_shield:
        item["VitalShield"] = 0
    if base_durability is not None:
        item["BaseDurability"] = base_durability
    if power_level is not None:
        item["PowerLevel"] = power_level
    if weight is not None:
        item["Weight"] = weight
    return tag, item, icon_abs, icon_obj, internal_name


def normalize_plan_name(name: str) -> str:
    trimmed = name.strip()
    if not trimmed:
        return trimmed
    return re.sub(r"^PLAN\s*[:_-]\s*", "", trimmed, flags=re.IGNORECASE)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build item tables grouped by ItemFilterTags.")
    parser.add_argument(
        "--source",
        required=True,
        nargs="+",
        help="Source directory (or directories) with ITEM_*.json files.",
    )
    parser.add_argument("--table", required=True, help="Output table directory.")
    parser.add_argument("--content-root", default=".", help="Workspace content root.")
    args = parser.parse_args()

    source_dirs = [Path(source) for source in args.source]
    table_dir = Path(args.table)
    content_root = Path(args.content_root)

    for source_dir in source_dirs:
        if not source_dir.exists():
            print(f"[ERROR] Source directory not found: {source_dir}")
            return 1

    table_dir.mkdir(parents=True, exist_ok=True)

    groups: dict[str, dict] = {}
    icon_copy_count = 0
    missing_icon_count = 0
    placeholder_icon_count = 0
    total_items = 0
    item_json_count = 0
    placeholder_icon = Path("docs") / "DWE" / "Assets" / "Placeholders" / "placeholder_icon.png"

    def add_item_from_file(
        file_path: Path,
        requires_vital_shield: bool = False,
        equipment_slot: str | None = None,
        group_override: str | None = None,
    ) -> None:
        nonlocal icon_copy_count, missing_icon_count, placeholder_icon_count
        nonlocal total_items, item_json_count
        if "_MeshData" in file_path.name:
            return
        entry = load_item_data(file_path)
        if not entry:
            return
        extracted = extract_item(
            entry,
            file_path,
            content_root,
            requires_vital_shield,
            equipment_slot,
        )
        if not extracted:
            return
        tag, item, icon_abs, icon_obj, internal_name = extracted
        group_key = group_override or sanitize_tag(tag)

        if group_key == "Plans" and item.get("name"):
            item["name"] = normalize_plan_name(item["name"])

        if icon_abs and internal_name:
            item["icon"] = f"{internal_name}{icon_abs.suffix}"
        elif icon_abs:
            item["icon"] = icon_abs.name

        if group_key not in groups:
            groups[group_key] = {"items": []}
        groups[group_key]["items"].append(item)
        total_items += 1

        dest_dir = table_dir / group_key
        dest_dir.mkdir(parents=True, exist_ok=True)

        if icon_abs:
            icon_name = item["icon"] if item["icon"] else icon_abs.name
            shutil.copy2(icon_abs, dest_dir / icon_name)
            icon_copy_count += 1
            if internal_name:
                json_name = f"{internal_name}.json"
            else:
                json_name = Path(icon_name).with_suffix(".json").name
        else:
            missing_icon_count += 1
            print(f"[WARN] Icon not found: {file_path} -> {icon_obj}")
            if not item["icon"]:
                icon_name = f"{internal_name}.png" if internal_name else f"{item['ItemData']}.png"
                item["icon"] = icon_name
            if internal_name:
                json_name = f"{internal_name}.json"
            else:
                json_name = f"{item['ItemData']}.json"
            if placeholder_icon.exists():
                shutil.copy2(placeholder_icon, dest_dir / item["icon"])
                placeholder_icon_count += 1
            else:
                print(f"[WARN] Placeholder icon missing: {placeholder_icon}")

        json_path = dest_dir / json_name
        json_path.write_text(json.dumps(item, indent=2, ensure_ascii=True), encoding="utf-8")
        item_json_count += 1

    for source_dir in source_dirs:
        for file_path in sorted(source_dir.rglob("ITEM_*.json")):
            requires_vital_shield = "Gameplay" in file_path.parts and "Equipment" in file_path.parts
            equipment_slot = None
            if requires_vital_shield:
                equipment_root = Path("Gameplay") / "Character" / "Player" / "Equipment"
                for slot in ("Body", "Cape", "Head", "Jewellery", "Legs"):
                    if equipment_root / slot in file_path.parents:
                        equipment_slot = slot
                        break
            add_item_from_file(
                file_path,
                requires_vital_shield=requires_vital_shield,
                equipment_slot=equipment_slot,
            )

    plans_root = content_root / "Gameplay" / "Items" / "Consumables" / "Plans"
    vestiges_root = content_root / "Gameplay" / "Items" / "Consumables" / "Vestiges"
    if plans_root.exists():
        for file_path in sorted(plans_root.rglob("DA_Consumable_*.json")):
            add_item_from_file(file_path, group_override="Plans")
    else:
        print(f"[WARN] Plans folder not found: {plans_root}")
    if vestiges_root.exists():
        for file_path in sorted(vestiges_root.rglob("DA_Consumable_*.json")):
            add_item_from_file(file_path, group_override="Vestiges")
    else:
        print(f"[WARN] Vestiges folder not found: {vestiges_root}")

    print("[INFO] Sources:")
    for source_dir in source_dirs:
        print(f"[INFO] - {source_dir}")
    print(f"[INFO] Groups: {len(groups)}")
    print(f"[INFO] Items processed: {total_items}")
    print(f"[INFO] Item JSON written: {item_json_count}")
    print(f"[INFO] Icons copied: {icon_copy_count}")
    print(f"[INFO] Icons missing: {missing_icon_count}")
    print(f"[INFO] Placeholder icons copied: {placeholder_icon_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
