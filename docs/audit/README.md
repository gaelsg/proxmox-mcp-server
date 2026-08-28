# Audit log

`actions.jsonl` — registro append-only, generado automáticamente por el servidor (no a mano), de cada llamada a una tool de escritura (`start_resource`, `stop_resource`, `restart_resource`). Una línea JSON por acción: timestamp UTC, acción, nodo, vmid, tipo de recurso, resultado (`ok` o `error: ...`).

Este archivo es evidencia, no bitácora de aprendizaje — para el razonamiento detrás de una acción, ver `docs/bitacora/` del día correspondiente.
