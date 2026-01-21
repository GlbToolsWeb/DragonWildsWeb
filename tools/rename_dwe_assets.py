import argparse
import json
import re
from pathlib import Path


INVALID_CHARS = re.compile(r'[\\/:*?"<>|]')


def sanitize_filename(name: str) -> str:
    name = INVALID_CHARS.sub("_", name)
    name = name.replace("\t", " ").replace("\n", " ").replace("\r", " ")
    name = re.sub(r"\s+", " ", name).strip()
    name = name.rstrip(" .")
    return name or "item"


def unique_base_name(base: str, used: set[str]) -> str:
    if base not in used:
        used.add(base)
        return base
    idx = 2
    while True:
        candidate = f"{base} ({idx})"
        if candidate not in used:
            used.add(candidate)
            return candidate
        idx += 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rename Table assets by item name (JSON + icon)."
    )
    parser.add_argument(
        "--root",
        default="Table",
        help="Root directory containing asset folders (default: Table).",
    )
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"[ERROR] Root not found: {root}")
        return 1

    json_files = sorted(root.rglob("*.json"))
    if not json_files:
        print(f"[WARN] No json files found under: {root}")
        return 0

    # Group JSON files by their parent folder to keep names unique per folder.
    folder_map: dict[Path, list[Path]] = {}
    for json_path in json_files:
        if json_path.name.lower() == "desktop.ini":
            continue
        folder_map.setdefault(json_path.parent, []).append(json_path)

    total = 0
    renamed_json = 0
    renamed_img = 0
    warnings = 0

    for folder, files in folder_map.items():
        used_names = {
            p.stem
            for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in {".json", ".png"}
        }

        for json_path in sorted(files):
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                print(f"[WARN] JSON parse failed: {json_path} ({exc})")
                warnings += 1
                continue

            if not isinstance(data, dict):
                print(f"[WARN] Unexpected JSON shape: {json_path}")
                warnings += 1
                continue

            name = data.get("name", "").strip()
            if not name:
                icon_fallback = Path(data.get("icon", "")).stem
                name = icon_fallback or json_path.stem
                data["name"] = name
                warnings += 1
                print(f"[WARN] Missing name patched: {json_path} -> {name}")

            base = sanitize_filename(name)
            base = unique_base_name(base, used_names)

            icon_name = data.get("icon", "").strip()
            icon_path = folder / icon_name if icon_name else None
            icon_ext = Path(icon_name).suffix if icon_name else ".png"
            new_icon_name = f"{base}{icon_ext}"
            new_icon_path = folder / new_icon_name

            # Rename image if it exists.
            if icon_path and icon_path.exists():
                if icon_path.name != new_icon_name:
                    icon_path.rename(new_icon_path)
                    renamed_img += 1
                data["icon"] = new_icon_name
            else:
                # Keep placeholder if missing.
                data["icon"] = data.get("icon", "")

            new_json_name = f"{base}.json"
            new_json_path = folder / new_json_name

            if json_path.name != new_json_name:
                json_path.rename(new_json_path)
                renamed_json += 1

            new_json_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=True), encoding="utf-8"
            )
            total += 1

    print(f"[INFO] Root: {root}")
    print(f"[INFO] Items processed: {total}")
    print(f"[INFO] JSON renamed: {renamed_json}")
    print(f"[INFO] Images renamed: {renamed_img}")
    print(f"[INFO] Warnings: {warnings}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
