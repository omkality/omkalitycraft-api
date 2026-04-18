from __future__ import annotations

from litestar import get
from litestar.response import Redirect

from ..core.config import settings
from ..core.project import get_project_info
from ..core.storage import content_root, instances_root


@get("/", sync_to_thread=True)
def docs_redirect() -> Redirect:
    return Redirect("/docs")


@get("/version", sync_to_thread=True)
def version() -> dict[str, str]:
    project_info = get_project_info()

    return {
        "name": project_info["name"],
        "version": project_info["version"],
        "description": project_info["description"],
    }


@get("/health", sync_to_thread=True)
def health() -> dict[str, object]:
    root = content_root()
    instances = instances_root()

    instances_count = 0
    if instances.exists():
        instances_count = len([p for p in instances.iterdir() if p.is_dir()])

    return {
        "status": "ok",
        "api_host": settings.api_host,
        "api_port": settings.api_port,
        "content_root": str(root),
        "instances_count": instances_count,
    }
