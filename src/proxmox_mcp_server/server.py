import os
from typing import Any

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer
from proxmoxer import ProxmoxAPI

load_dotenv()

mcp = MCPServer("proxmox-mcp-server")


def _client() -> ProxmoxAPI:
    return ProxmoxAPI(
        os.environ["PROXMOX_HOST"],
        user=os.environ["PROXMOX_USER"],
        token_name=os.environ["PROXMOX_TOKEN_NAME"],
        token_value=os.environ["PROXMOX_TOKEN_VALUE"],
        verify_ssl=os.environ.get("PROXMOX_VERIFY_SSL", "false").lower() == "true",
    )


@mcp.tool()
def list_nodes() -> list[dict[str, Any]]:
    """Lista los nodos del cluster Proxmox y su estado (cpu, memoria, uptime)."""
    return _client().nodes.get()


@mcp.tool()
def list_vms(node: str) -> list[dict[str, Any]]:
    """Lista las VMs (QEMU) de un nodo Proxmox."""
    return _client().nodes(node).qemu.get()


@mcp.tool()
def list_containers(node: str) -> list[dict[str, Any]]:
    """Lista los contenedores LXC de un nodo Proxmox."""
    return _client().nodes(node).lxc.get()


@mcp.tool()
def get_resource_status(node: str, vmid: int, resource_type: str) -> dict[str, Any]:
    """Obtiene el estado detallado de una VM o contenedor.

    resource_type debe ser 'qemu' o 'lxc'.
    """
    if resource_type not in ("qemu", "lxc"):
        raise ValueError("resource_type debe ser 'qemu' o 'lxc'")
    return _client().nodes(node)(resource_type)(vmid).status.current.get()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
