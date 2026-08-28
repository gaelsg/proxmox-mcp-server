# proxmox-mcp-server

Servidor MCP (Model Context Protocol) de solo lectura para un cluster Proxmox VE. Expone el estado de nodos, VMs y contenedores LXC como herramientas invocables por cualquier host compatible con MCP (Claude Code, Claude Desktop, agentes propios).

Fase 1 de un proyecto más grande: un agente DevOps con capacidades reales sobre infraestructura propia, con permisos explícitos y auditables. Ver `docs/bitacora/` para el registro de decisiones y aprendizaje.

## Setup

```bash
uv sync
cp .env.example .env  # completar con tu token de Proxmox, ver docs/bitacora/
```

## Herramientas expuestas

- `list_nodes()` — nodos del cluster y su estado.
- `list_vms(node)` — VMs QEMU de un nodo.
- `list_containers(node)` — contenedores LXC de un nodo.
- `get_resource_status(node, vmid, resource_type)` — estado detallado de una VM o LXC.

## Ejecutar

```bash
uv run proxmox-mcp-server
```

## Probar con MCP Inspector

```bash
uv run mcp dev src/proxmox_mcp_server/server.py
```
