from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from litestar.exceptions import HTTPException

from .config import settings


def content_root() -> Path:
    return Path(settings.content_root).resolve()


def launcher_root() -> Path:
    return content_root() / "launcher"


def launcher_files_root() -> Path:
    return launcher_root() / "files"


def launcher_manifest_path() -> Path:
    return launcher_root() / "manifest.json"


def instances_root() -> Path:
    return content_root() / "instances"


def instance_root(instance_id: str) -> Path:
    return instances_root() / instance_id


def instance_files_root(instance_id: str) -> Path:
    return instance_root(instance_id) / "files"


def instance_manifest_path(instance_id: str) -> Path:
    return instance_root(instance_id) / "manifest.json"


def instance_config_path(instance_id: str) -> Path:
    return instance_root(instance_id) / "instance_config.json"


def launch_profile_path(instance_id: str) -> Path:
    return instance_root(instance_id) / "launch_profile.json"


def ensure_exists(path: Path, message: str) -> Path:
    if not path.exists():
        raise HTTPException(status_code=404, detail=message)
    return path


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def safe_resolve(base: Path, relative_path: str) -> Path:
    base_resolved = base.resolve()
    normalized_relative_path = relative_path.lstrip("/\\")
    candidate = (base_resolved / normalized_relative_path).resolve()

    try:
        candidate.relative_to(base_resolved)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid path") from exc

    return candidate
