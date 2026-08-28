# proxmox-mcp-server

Servidor MCP (Model Context Protocol) para un cluster Proxmox VE. Expone el estado de nodos, VMs y contenedores LXC, y acciones de power management (start/stop/restart), como herramientas invocables por cualquier host compatible con MCP (Claude Code, Claude Desktop, agentes propios).

Fase 1-2 de un proyecto más grande: un agente DevOps con capacidades reales sobre infraestructura propia, con permisos explícitos y auditables. Ver `docs/bitacora/` para el registro de decisiones y aprendizaje, `docs/audit/` para el log de acciones de escritura.

## Seguridad: dos tokens separados

- **Lectura** (`PROXMOX_TOKEN_*`) — usuario `mcp-agent@pve`, rol `PVEAuditor` en `/`, sin privilege separation (hereda del usuario).
- **Escritura** (`PROXMOX_WRITE_TOKEN_*`) — mismo usuario, rol custom `MCPPowerOperator` (solo `VM.PowerMgmt`) asignado **al token**, no al usuario, con privilege separation activada. Así el token de lectura nunca hereda capacidad de escritura aunque el usuario gane más permisos a futuro.

## Docker dentro del LXC "docker-host" (via Portainer)

El LXC 101 corre Docker con Portainer, AdGuard Home y Tailscale. Portainer CE no tiene RBAC granular real (los roles "read-only"/"environment admin" no se aplican en la práctica, y no hay resource control para contenedores creados fuera de su UI) — el usuario dedicado `mcp-agent` en Portainer es administrador global (única forma de que vea los contenedores), pero **el límite de solo-lectura vive en este código, no en Portainer**: `docker_tools.py` solo expone tools de lectura, ninguna de escritura, sin importar que la cuenta técnicamente pueda más. Mismo patrón que el `hide_when_gated` de `devops-multiagent`.

## Setup

```bash
uv sync
cp .env.example .env  # completar con tus tokens de Proxmox y el API key de Portainer, ver docs/bitacora/
```

## Herramientas expuestas

Solo lectura (Proxmox):
- `list_nodes()` — nodos del cluster y su estado.
- `list_vms(node)` — VMs QEMU de un nodo.
- `list_containers(node)` — contenedores LXC de un nodo.
- `get_resource_status(node, vmid, resource_type)` — estado detallado de una VM o LXC.

Escritura (Proxmox, requieren `PROXMOX_WRITE_TOKEN_*`, quedan registradas en `docs/audit/actions.jsonl`):
- `start_resource(node, vmid, resource_type)`
- `stop_resource(node, vmid, resource_type)` — shutdown ordenado, no force.
- `restart_resource(node, vmid, resource_type)`

Solo lectura (Docker, via Portainer):
- `list_docker_containers()` — contenedores del LXC docker-host.
- `get_docker_container_status(name)` — inspect detallado de uno.

## Ejecutar

```bash
uv run proxmox-mcp-server
```

## Probar con MCP Inspector

```bash
uv run mcp dev src/proxmox_mcp_server/server.py
```
