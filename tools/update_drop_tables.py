import json
import re
import shutil
from pathlib import Path


LOOT_TABLE_PATH = Path("LootDropTable/DT_LootDropTable.json")
ENEMY_NAMES_PATH = Path("LootDropTable/DT_LootDropTable_EnemyNames.json")
ITEM_NAMES_PATH = Path("LootDropTable/DT_LootDropTable_ItemNames.json")

WEB_TARGETS = {
    LOOT_TABLE_PATH: Path("docs/data/loot_drop_table.json"),
    ENEMY_NAMES_PATH: Path("docs/data/loot_drop_table_enemy_names.json"),
    ITEM_NAMES_PATH: Path("docs/data/loot_drop_table_item_names.json"),
}

ITEM_ID_PATTERN = re.compile(r"(ITEM_[A-Za-z0-9_]+|DA_[A-Za-z0-9_]+)")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )


def extract_rows(loot_table: object) -> dict:
    if isinstance(loot_table, list) and loot_table:
        first = loot_table[0]
        if isinstance(first, dict):
            return first.get("Rows", {}) or {}
    if isinstance(loot_table, dict):
        return loot_table.get("Rows", {}) or {}
    return {}


def update_enemy_names(rows: dict) -> dict:
    existing = {}
    if ENEMY_NAMES_PATH.exists():
        existing = load_json(ENEMY_NAMES_PATH)
    updated = {}
    for internal_name in sorted(rows.keys()):
        current = ""
        if isinstance(existing, dict):
            current = existing.get(internal_name, "")
        updated[internal_name] = current
    write_json(ENEMY_NAMES_PATH, updated)
    return updated


def update_item_names(rows: dict) -> dict:
    existing = {}
    if ITEM_NAMES_PATH.exists():
        existing = load_json(ITEM_NAMES_PATH)
    found_ids = set()
    for row in rows.values():
        for resource in row.get("Resources", []):
            object_name = resource.get("SpawnedItemData", {}).get("ObjectName", "")
            for match in ITEM_ID_PATTERN.findall(str(object_name)):
                found_ids.add(match)
    updated = {}
    for item_id in sorted(found_ids):
        current = ""
        if isinstance(existing, dict):
            current = existing.get(item_id, "")
        updated[item_id] = current
    write_json(ITEM_NAMES_PATH, updated)
    return updated


def main() -> None:
    loot_table = load_json(LOOT_TABLE_PATH)
    rows = extract_rows(loot_table)

    update_enemy_names(rows)
    update_item_names(rows)

    for src_path, dst_path in WEB_TARGETS.items():
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src_path, dst_path)
        print(f"Copied {src_path} -> {dst_path}")


if __name__ == "__main__":
    main()
