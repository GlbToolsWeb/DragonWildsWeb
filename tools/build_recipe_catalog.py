import argparse
import hashlib
import shutil
from pathlib import Path


def file_hash(path: Path) -> str:
    hasher = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def sanitize_suffix(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value)
    cleaned = "_".join(filter(None, cleaned.split("_")))
    return cleaned or "root"


def resolve_destination(
    source_file: Path,
    source_root: Path,
    output_dir: Path,
    flat: bool,
    overwrite: bool,
) -> tuple[Path, str]:
    if not flat:
        relative_path = source_file.relative_to(source_root)
        return output_dir / relative_path, "preserve-path"

    dest_path = output_dir / source_file.name
    if not dest_path.exists():
        return dest_path, "flat"

    if file_hash(dest_path) == file_hash(source_file):
        return dest_path, "duplicate-skip"

    if overwrite:
        return dest_path, "overwrite"

    suffix = sanitize_suffix(str(source_file.relative_to(source_root).parent))
    candidate = output_dir / f"{source_file.stem}__{suffix}{source_file.suffix}"
    if not candidate.exists():
        return candidate, "rename"

    index = 2
    while True:
        candidate = output_dir / f"{source_file.stem}__{suffix}_{index}{source_file.suffix}"
        if not candidate.exists():
            return candidate, "rename"
        index += 1


def copy_recipes(
    source_dirs: list[Path],
    output_dir: Path,
    flat: bool,
    overwrite: bool,
    dry_run: bool,
) -> int:
    total_found = 0
    total_copied = 0
    total_skipped = 0
    total_renamed = 0
    total_overwritten = 0

    output_dir.mkdir(parents=True, exist_ok=True)

    for source_dir in source_dirs:
        if not source_dir.exists():
            print(f"[ERROR] Source directory not found: {source_dir}")
            return 1

    for source_dir in source_dirs:
        recipe_files = sorted(source_dir.rglob("RECIPE_*.json"))
        print(f"[INFO] Scanning: {source_dir} ({len(recipe_files)} matches)")
        for recipe_path in recipe_files:
            total_found += 1
            dest_path, mode = resolve_destination(
                recipe_path, source_dir, output_dir, flat, overwrite
            )

            if mode == "duplicate-skip":
                total_skipped += 1
                print(f"[INFO] Skip duplicate: {recipe_path}")
                continue

            if mode == "overwrite":
                total_overwritten += 1
                action = "Overwrite"
            elif mode == "rename":
                total_renamed += 1
                action = "Copy (renamed)"
            else:
                action = "Copy"

            if not dry_run:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(recipe_path, dest_path)
            total_copied += 1
            print(f"[INFO] {action}: {recipe_path} -> {dest_path}")

    print("[INFO] Summary")
    print(f"[INFO] - Files found: {total_found}")
    print(f"[INFO] - Files copied: {total_copied}")
    print(f"[INFO] - Files skipped (duplicates): {total_skipped}")
    print(f"[INFO] - Files renamed: {total_renamed}")
    print(f"[INFO] - Files overwritten: {total_overwritten}")
    if dry_run:
        print("[INFO] Dry run only: no files were written.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy RECIPE_*.json files into a consolidated Recipes folder."
    )
    parser.add_argument(
        "--source",
        nargs="+",
        default=["Content/Gameplay"],
        help="Source directory (or directories) to scan.",
    )
    parser.add_argument(
        "--output",
        default="Recipes",
        help="Output directory for collected recipe JSON files.",
    )
    parser.add_argument(
        "--flat",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Copy all recipes into a single folder (default: true).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite name collisions instead of renaming.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without copying files.",
    )
    args = parser.parse_args()

    source_dirs = [Path(source) for source in args.source]
    output_dir = Path(args.output)

    return copy_recipes(
        source_dirs=source_dirs,
        output_dir=output_dir,
        flat=args.flat,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
