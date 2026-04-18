from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_path(path: Path) -> str:
    return path.as_posix()


def should_ignore(relative_path: str, ignored_prefixes: list[str]) -> bool:
    return any(relative_path.startswith(prefix) for prefix in ignored_prefixes)


def build_manifest(
    source_root: Path,
    ignored_prefixes: list[str],
    managed_roots: list[str],
    content_id: str,
    kind: str,
) -> dict:
    files: dict[str, dict] = {}
    total_size = 0

    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue

        relative_path = normalize_path(path.relative_to(source_root))

        if relative_path == "manifest.json":
            continue

        if should_ignore(relative_path, ignored_prefixes):
            continue

        file_size = path.stat().st_size
        total_size += file_size

        files[relative_path] = {
            "sha256": sha256_of_file(path),
            "size": file_size,
        }

    return {
        "content_id": content_id,
        "kind": kind,
        "generated_at": datetime.now(UTC).isoformat(),
        "managed_roots": managed_roots,
        "total_size": total_size,
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--manifest-path", required=True)
    parser.add_argument("--content-id", required=True)
    parser.add_argument("--kind", choices=["launcher", "instance"], required=True)
    parser.add_argument("--managed-root", action="append", default=[])
    parser.add_argument("--ignore-prefix", action="append", default=[])

    args = parser.parse_args()

    source_root = Path(args.source_root).resolve()
    manifest_path = Path(args.manifest_path).resolve()

    manifest = build_manifest(
        source_root=source_root,
        ignored_prefixes=args.ignore_prefix,
        managed_roots=args.managed_root,
        content_id=args.content_id,
        kind=args.kind,
    )

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)

    print(f"Manifest written to: {manifest_path}")
    print(f"Files: {len(manifest['files'])}")
    print(f"Total size: {manifest['total_size']} bytes")


if __name__ == "__main__":
    main()
