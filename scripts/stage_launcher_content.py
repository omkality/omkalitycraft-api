from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_manifest import build_manifest  # noqa: E402

LAUNCHER_MANAGED_ROOTS = [
    "assets/",
    "jre-x64-new/",
    "libraries/",
    "versions/",
    "launcher.py",
]

INSTANCE_MANAGED_ROOTS = [
    "asm/",
    "assets/",
    "astralsorcery/",
    "config/",
    "mods/",
    "mods-resourcepacks/",
    "mputils/",
    "patchouli_books/",
    "resourcepacks/",
    "resources/",
    "scripts/",
    "structures/",
    "TombManyGraves/",
    "vintagefix/",
    ".curseclient",
    "LICENSE",
    "manifest.json",
    "minecraftinstance.json",
    "modlist.html",
    "patchouli_data.json",
    "servers.dat",
]

INSTANCE_IGNORED_PREFIXES = [
    "crash-reports/",
    "dumps/",
    "journeymap/",
    "local/",
    "logs/",
    "saves/",
    "screenshots/",
    "BotaniaVars.dat",
    "crafttweaker.log",
    "knownkeys.txt",
    "options.txt",
    "roots.log",
    "usercache.json",
    "usernamecache.json",
]

INSTANCE_SOFT_MANAGED_PATHS = [
    "config/",
    "options.txt",
]


def copy_path(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_existing_paths(
    source_root: Path, destination_root: Path, relative_paths: list[str]
) -> None:
    for relative_path in relative_paths:
        normalized = relative_path.rstrip("/")
        source = source_root / normalized
        if not source.exists():
            print(f"Skip missing path: {source}")
            continue

        copy_path(source, destination_root / normalized)


def extract_classpath_from_run_bat(
    run_bat_path: Path, launcher_root: Path
) -> list[str]:
    content = run_bat_path.read_text(encoding="utf-8", errors="ignore")
    entries: list[str] = []

    for match in re.finditer(r'set "CP=!CP!;(?P<path>[^"]+)"', content):
        entry = match.group("path")
        entry = entry.replace("!LIBS!\\", "libraries\\")
        entry = entry.replace("!VERS!\\", "versions\\")
        normalized_entry = entry.replace("\\", "/")
        if not (launcher_root / normalized_entry).exists():
            print(f"Skip missing classpath entry: {normalized_entry}")
            continue
        entries.append(normalized_entry)

    return entries


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
        file.write("\n")


def write_manifest(
    source_root: Path,
    manifest_path: Path,
    content_id: str,
    kind: str,
    managed_roots: list[str],
    ignored_prefixes: list[str],
) -> None:
    manifest = build_manifest(
        source_root=source_root,
        ignored_prefixes=ignored_prefixes,
        managed_roots=managed_roots,
        content_id=content_id,
        kind=kind,
    )
    write_json(manifest_path, manifest)

    print(f"Manifest written to: {manifest_path}")
    print(f"Files: {len(manifest['files'])}")
    print(f"Total size: {manifest['total_size']} bytes")


def build_instance_config(instance_id: str) -> dict[str, Any]:
    return {
        "id": instance_id,
        "display_name": "Divine Journey 2",
        "description": "Divine Journey 2 modpack with OmkalityCore",
        "ignored_paths": INSTANCE_IGNORED_PREFIXES,
        "soft_managed_paths": INSTANCE_SOFT_MANAGED_PATHS,
        "delete_extra_files_in_managed_paths": True,
    }


def build_launch_profile(classpath: list[str]) -> dict[str, Any]:
    return {
        "java_path_relative": "jre-x64-new/bin/java.exe",
        "native_library_path_relative": "versions/divinejourney2/natives",
        "main_class": "net.minecraft.launchwrapper.Launch",
        "classpath": classpath,
        "jvm_args": [
            "-Xms8G",
            "-Xmx12G",
            "-XX:+UseG1GC",
            "-Dfml.ignoreInvalidMinecraftCertificates=true",
            "-Dfml.ignorePatchDiscrepancies=true",
        ],
        "game_args": [
            "--username",
            "{username}",
            "--version",
            "{instance_id}",
            "--gameDir",
            "{game_dir}",
            "--assetsDir",
            "{assets_dir}",
            "--assetIndex",
            "1.12",
            "--uuid",
            "{uuid}",
            "--accessToken",
            "0",
            "--userType",
            "mojang",
            "--versionType",
            "release",
            "--tweakClass",
            "net.minecraftforge.fml.common.launcher.FMLTweaker",
        ],
        "system_properties": {
            "omkality.password": "{password}",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--content-root", default="data/content")
    parser.add_argument("--instance-id", default="divinejourney2")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_root = Path(args.source_root).resolve()
    content_root = Path(args.content_root).resolve()
    instance_id = str(args.instance_id)

    launcher_files_root = content_root / "launcher" / "files"
    instance_root = content_root / "instances" / instance_id
    instance_files_root = instance_root / "files"
    client_launcher_path = (
        Path(__file__).resolve().parents[1] / "client" / "launcher.py"
    )

    if not source_root.exists():
        raise RuntimeError(f"Source launcher root not found: {source_root}")

    print(f"Source launcher root: {source_root}")
    print(f"Target content root: {content_root}")

    copy_existing_paths(source_root, launcher_files_root, LAUNCHER_MANAGED_ROOTS[:-1])
    copy_path(client_launcher_path, launcher_files_root / "launcher.py")

    copy_existing_paths(
        source_root / "instances" / instance_id,
        instance_files_root,
        INSTANCE_MANAGED_ROOTS,
    )

    classpath = extract_classpath_from_run_bat(source_root / "run.bat", source_root)
    if not classpath:
        raise RuntimeError("Classpath was not extracted from run.bat")

    write_json(
        instance_root / "instance_config.json", build_instance_config(instance_id)
    )
    write_json(instance_root / "launch_profile.json", build_launch_profile(classpath))

    write_manifest(
        source_root=launcher_files_root,
        manifest_path=content_root / "launcher" / "manifest.json",
        content_id="launcher-root",
        kind="launcher",
        managed_roots=LAUNCHER_MANAGED_ROOTS,
        ignored_prefixes=[],
    )
    write_manifest(
        source_root=instance_files_root,
        manifest_path=instance_root / "manifest.json",
        content_id=instance_id,
        kind="instance",
        managed_roots=INSTANCE_MANAGED_ROOTS,
        ignored_prefixes=INSTANCE_IGNORED_PREFIXES,
    )


if __name__ == "__main__":
    main()
