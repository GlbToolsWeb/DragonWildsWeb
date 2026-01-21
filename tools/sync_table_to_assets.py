import argparse
import shutil
from pathlib import Path


def build_asset_index(assets_root: Path) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    for path in assets_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.lower() == "desktop.ini":
            continue
        if path.suffix.lower() not in {".json", ".png"}:
            continue
        key = path.name.lower()
        index.setdefault(key, []).append(path)
    return index


def sync_table_to_assets(
    table_root: Path,
    assets_root: Path,
    dry_run: bool,
    delete_matched: bool,
) -> int:
    if not table_root.exists():
        print(f"[ERROR] Table not found: {table_root}")
        return 1
    if not assets_root.exists():
        print(f"[ERROR] Assets not found: {assets_root}")
        return 1

    asset_index = build_asset_index(assets_root)
    table_files = [
        path
        for path in sorted(table_root.rglob("*"))
        if path.is_file()
        and path.name.lower() != "desktop.ini"
        and path.suffix.lower() in {".json", ".png"}
    ]

    replaced = 0
    deleted = 0
    missing = 0
    multi_match = 0

    for table_file in table_files:
        targets = asset_index.get(table_file.name.lower(), [])
        if not targets:
            missing += 1
            print(f"[WARN] No asset match for: {table_file}")
            continue
        if len(targets) > 1:
            multi_match += 1
            print(f"[WARN] Multiple asset matches for: {table_file.name}")
        for target in targets:
            if dry_run:
                print(f"[DRYRUN] {table_file} -> {target}")
            else:
                shutil.copy2(table_file, target)
            replaced += 1
        if delete_matched:
            if dry_run:
                print(f"[DRYRUN] delete {table_file}")
            else:
                table_file.unlink()
            deleted += 1

    print(f"[INFO] Table root: {table_root}")
    print(f"[INFO] Assets root: {assets_root}")
    print(f"[INFO] Table files scanned: {len(table_files)}")
    print(f"[INFO] Files replaced: {replaced}")
    if delete_matched:
        print(f"[INFO] Table files deleted: {deleted}")
    print(f"[INFO] Missing matches: {missing}")
    print(f"[INFO] Multiple matches: {multi_match}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace DWE/Assets files with matching names from Table."
    )
    parser.add_argument(
        "--table",
        default="Table",
        help="Table root containing grouped JSON/PNG (default: Table).",
    )
    parser.add_argument(
        "--assets",
        default="DWE/Assets",
        help="Assets root to replace files in (default: DWE/Assets).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without copying files.",
    )
    parser.add_argument(
        "--delete-matched",
        action="store_true",
        help="Delete Table files after they successfully replace assets.",
    )
    args = parser.parse_args()

    return sync_table_to_assets(
        Path(args.table),
        Path(args.assets),
        args.dry_run,
        args.delete_matched,
    )


if __name__ == "__main__":
    raise SystemExit(main())
