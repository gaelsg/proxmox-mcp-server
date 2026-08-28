import os
from typing import Any

import requests
import urllib3

from proxmox_mcp_server.server import mcp

PORTAINER_HOST = os.environ["PORTAINER_HOST"].rstrip("/")
PORTAINER_API_KEY = os.environ["PORTAINER_API_KEY"]
PORTAINER_ENDPOINT_ID = os.environ.get("PORTAINER_ENDPOINT_ID", "3")
PORTAINER_VERIFY_SSL = os.environ.get("PORTAINER_VERIFY_SSL", "false").lower() == "true"

if not PORTAINER_VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_HEADERS = {"X-API-Key": PORTAINER_API_KEY}


def _docker_get(path: str, params: dict[str, str] | None = None) -> Any:
    url = f"{PORTAINER_HOST}/api/endpoints/{PORTAINER_ENDPOINT_ID}/docker/{path}"
    resp = requests.get(
        url, headers=_HEADERS, params=params, verify=PORTAINER_VERIFY_SSL, timeout=30
    )
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def list_docker_containers() -> list[dict[str, Any]]:
    """Lista los contenedores Docker dentro del LXC docker-host (via Portainer). Solo lectura."""
    containers = _docker_get("containers/json", params={"all": "true"})
    return [
        {
            "name": (c["Names"][0].lstrip("/") if c.get("Names") else c["Id"][:12]),
            "image": c["Image"],
            "state": c["State"],
            "status": c["Status"],
        }
        for c in containers
    ]


@mcp.tool()
def get_docker_container_status(name: str) -> dict[str, Any]:
    """Estado detallado (inspect) de un contenedor Docker por nombre. Solo lectura."""
    info = _docker_get(f"containers/{name}/json")
    state = info.get("State", {})
    health = state.get("Health") or {}
    return {
        "name": info.get("Name", "").lstrip("/"),
        "image": info.get("Config", {}).get("Image"),
        "status": state.get("Status"),
        "running": state.get("Running"),
        "started_at": state.get("StartedAt"),
        "restart_count": info.get("RestartCount"),
        "health": health.get("Status"),
    }
