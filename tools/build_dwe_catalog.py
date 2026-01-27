import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_ASSETS_DIR = ROOT / "docs" / "DWE" / "Assets"
ASSETS_DIR = ROOT / "DWE" / "Assets"
OUTPUT_FILES = [
    ROOT / "web" / "data" / "catalog.json",
    ROOT / "docs" / "data" / "catalog.json",
]

TAB_LABELS = {
    "BagTab": "Bag Items",
    "RuneTab": "Rune Items",
    "AmmoTab": "Ammo Items",
    "QuestTab": "Quest Items",
}


def to_web_path(path: Path, base_root: Path) -> str:
    return path.relative_to(base_root).as_posix()


def build_catalog():
    assets_root = DOCS_ASSETS_DIR if DOCS_ASSETS_DIR.exists() else ASSETS_DIR
    base_root = ROOT / "docs" if assets_root == DOCS_ASSETS_DIR else ROOT
    catalog = {"tabs": {}}
    for tab_name in ["BagTab", "RuneTab", "AmmoTab", "QuestTab"]:
        tab_dir = assets_root / tab_name
        items = []
        for root, _, files in os.walk(tab_dir):
            for filename in files:
                if not filename.lower().endswith(".json"):
                    continue
                file_path = Path(root) / filename
                if file_path.name.lower() == "desktop.ini":
                    continue
                with file_path.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)

                icon_name = data.get("icon") or file_path.with_suffix(".png").name
                icon_path = file_path.parent / icon_name
                rel_dir = file_path.parent.relative_to(tab_dir)
                category = rel_dir.as_posix() if rel_dir.as_posix() != "." else tab_name

                item = {
                    "name": data.get("name", file_path.stem),
                    "itemData": data.get("ItemData"),
                    "maxStack": data.get("max_stack", 1),
                    "iconPath": to_web_path(icon_path, base_root),
                    "sourcePath": to_web_path(file_path, base_root),
                    "category": category,
                }
                if data.get("description") is not None:
                    item["description"] = data.get("description")
                if data.get("BaseDurability") is not None:
                    item["baseDurability"] = data.get("BaseDurability")
                if data.get("PowerLevel") is not None:
                    item["powerLevel"] = data.get("PowerLevel")
                if data.get("Weight") is not None:
                    item["weight"] = data.get("Weight")
                if data.get("VitalShield") is not None:
                    item["vitalShield"] = data.get("VitalShield")
                if data.get("Equipment") is not None:
                    item["equipment"] = data.get("Equipment")

                items.append(item)

        items.sort(key=lambda item: (item.get("category") or "", item.get("name") or ""))
        key = tab_name.replace("Tab", "").lower()
        catalog["tabs"][key] = {
            "label": TAB_LABELS.get(tab_name, tab_name),
            "items": items,
        }

    for output_file in OUTPUT_FILES:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", encoding="utf-8") as handle:
            json.dump(catalog, handle, indent=2)


if __name__ == "__main__":
    build_catalog()
