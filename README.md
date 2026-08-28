# proxmox-mcp-server

Servidor MCP (Model Context Protocol) para un cluster Proxmox VE. Expone el estado de nodos, VMs y contenedores LXC, y acciones de power management (start/stop/restart), como herramientas invocables por cualquier host compatible con MCP (Claude Code, Claude Desktop, agentes propios).

Fase 1-2 de un proyecto más grande: un agente DevOps con capacidades reales sobre infraestructura propia, con permisos explícitos y auditables. Ver `docs/bitacora/` para el registro de decisiones y aprendizaje, `docs/audit/` para el log de acciones de escritura.

## Seguridad: dos tokens separados

- **Lectura** (`PROXMOX_TOKEN_*`) — usuario `mcp-agent@pve`, rol `PVEAuditor` en `/`, sin privilege separation (hereda del usuario).
- **Escritura** (`PROXMOX_WRITE_TOKEN_*`) — mismo usuario, rol custom `MCPPowerOperator` (solo `VM.PowerMgmt`) asignado **al token**, no al usuario, con privilege separation activada. Así el token de lectura nunca hereda capacidad de escritura aunque el usuario gane más permisos a futuro.

## Setup

```bash
uv sync
cp .env.example .env  # completar con tus tokens de Proxmox, ver docs/bitacora/
```

## Herramientas expuestas

Solo lectura:
- `list_nodes()` — nodos del cluster y su estado.
- `list_vms(node)` — VMs QEMU de un nodo.
- `list_containers(node)` — contenedores LXC de un nodo.
- `get_resource_status(node, vmid, resource_type)` — estado detallado de una VM o LXC.

Escritura (requieren `PROXMOX_WRITE_TOKEN_*`, quedan registradas en `docs/audit/actions.jsonl`):
- `start_resource(node, vmid, resource_type)`
- `stop_resource(node, vmid, resource_type)` — shutdown ordenado, no force.
- `restart_resource(node, vmid, resource_type)`

## Ejecutar

```bash
uv run proxmox-mcp-server
```

## Probar con MCP Inspector

```bash
uv run mcp dev src/proxmox_mcp_server/server.py
```
