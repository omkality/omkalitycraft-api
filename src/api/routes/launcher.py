from __future__ import annotations

from litestar import get

from ..core.storage import ensure_exists, launcher_manifest_path, read_json


@get("/launcher/manifest", sync_to_thread=True)
def get_launcher_manifest() -> dict:
    path = ensure_exists(
        launcher_manifest_path(),
        "Launcher manifest not found",
    )
    return read_json(path)
