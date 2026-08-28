import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer
from proxmoxer import ProxmoxAPI

load_dotenv()

mcp = MCPServer("proxmox-mcp-server")

_REPO_ROOT = Path(__file__).resolve().parents[2]
_AUDIT_LOG = _REPO_ROOT / "docs" / "audit" / "actions.jsonl"

_VALID_RESOURCE_TYPES = ("qemu", "lxc")


def _read_client() -> ProxmoxAPI:
    return ProxmoxAPI(
        os.environ["PROXMOX_HOST"],
        user=os.environ["PROXMOX_USER"],
        token_name=os.environ["PROXMOX_TOKEN_NAME"],
        token_value=os.environ["PROXMOX_TOKEN_VALUE"],
        verify_ssl=os.environ.get("PROXMOX_VERIFY_SSL", "false").lower() == "true",
    )


def _write_client() -> ProxmoxAPI:
    return ProxmoxAPI(
        os.environ["PROXMOX_HOST"],
        user=os.environ["PROXMOX_USER"],
        token_name=os.environ["PROXMOX_WRITE_TOKEN_NAME"],
        token_value=os.environ["PROXMOX_WRITE_TOKEN_VALUE"],
        verify_ssl=os.environ.get("PROXMOX_VERIFY_SSL", "false").lower() == "true",
    )


def _audit(action: str, node: str, vmid: int, resource_type: str, result: str) -> None:
    _AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "node": node,
        "vmid": vmid,
        "resource_type": resource_type,
        "result": result,
    }
    with _AUDIT_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


@mcp.tool()
def list_nodes() -> list[dict[str, Any]]:
    """Lista los nodos del cluster Proxmox y su estado (cpu, memoria, uptime)."""
    return _read_client().nodes.get()


@mcp.tool()
def list_vms(node: str) -> list[dict[str, Any]]:
    """Lista las VMs (QEMU) de un nodo Proxmox."""
    return _read_client().nodes(node).qemu.get()


@mcp.tool()
def list_containers(node: str) -> list[dict[str, Any]]:
    """Lista los contenedores LXC de un nodo Proxmox."""
    return _read_client().nodes(node).lxc.get()


@mcp.tool()
def get_resource_status(node: str, vmid: int, resource_type: str) -> dict[str, Any]:
    """Obtiene el estado detallado de una VM o contenedor.

    resource_type debe ser 'qemu' o 'lxc'.
    """
    if resource_type not in _VALID_RESOURCE_TYPES:
        raise ValueError("resource_type debe ser 'qemu' o 'lxc'")
    return _read_client().nodes(node)(resource_type)(vmid).status.current.get()


def _power_action(action: str, node: str, vmid: int, resource_type: str) -> dict[str, Any]:
    if resource_type not in _VALID_RESOURCE_TYPES:
        raise ValueError("resource_type debe ser 'qemu' o 'lxc'")
    try:
        status = _write_client().nodes(node)(resource_type)(vmid).status
        upid = getattr(status, action).post()
    except Exception as exc:
        _audit(action, node, vmid, resource_type, f"error: {exc}")
        raise
    _audit(action, node, vmid, resource_type, "ok")
    return {"upid": upid}


@mcp.tool()
def start_resource(node: str, vmid: int, resource_type: str) -> dict[str, Any]:
    """Inicia una VM o contenedor detenido. resource_type debe ser 'qemu' o 'lxc'."""
    return _power_action("start", node, vmid, resource_type)


@mcp.tool()
def stop_resource(node: str, vmid: int, resource_type: str) -> dict[str, Any]:
    """Detiene (shutdown ordenado, no force) una VM o contenedor en ejecucion. resource_type debe ser 'qemu' o 'lxc'."""
    return _power_action("shutdown", node, vmid, resource_type)


@mcp.tool()
def restart_resource(node: str, vmid: int, resource_type: str) -> dict[str, Any]:
    """Reinicia (reboot) una VM o contenedor en ejecucion. resource_type debe ser 'qemu' o 'lxc'."""
    return _power_action("reboot", node, vmid, resource_type)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
