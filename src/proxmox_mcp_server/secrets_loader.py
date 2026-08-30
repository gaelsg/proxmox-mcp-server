from __future__ import annotations

import os

import requests


def load_secrets_from_vault() -> None:
    """Trae los secretos reales de Vault via AppRole y los inyecta en
    os.environ, para que el resto del codigo siga leyendo variables de
    entorno normales sin cambios.

    Falla rapido (lanza excepcion) si Vault esta configurado pero no
    responde - arrancar con credenciales a medias es peor que negarse a
    arrancar. Si Vault no esta configurado (no hay VAULT_ROLE_ID en el
    entorno), no hace nada - permite correr contra lo que ya haya en el
    entorno (ej. desarrollo local sin Vault).
    """
    role_id = os.environ.get("VAULT_ROLE_ID")
    secret_id = os.environ.get("VAULT_SECRET_ID")
    if not role_id or not secret_id:
        return

    addr = os.environ["VAULT_ADDR"]
    cacert = os.environ.get("VAULT_CACERT")
    verify: bool | str = cacert if cacert else True

    login = requests.post(
        f"{addr}/v1/auth/approle/login",
        json={"role_id": role_id, "secret_id": secret_id},
        verify=verify,
        timeout=10,
    )
    login.raise_for_status()
    token = login.json()["auth"]["client_token"]

    resp = requests.get(
        f"{addr}/v1/secret/data/proxmox-mcp-server",
        headers={"X-Vault-Token": token},
        verify=verify,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()["data"]["data"]

    for key, value in data.items():
        os.environ[key] = value
