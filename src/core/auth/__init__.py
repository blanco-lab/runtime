"""Infraestructura de autenticación de Runtime (ADR-0007).

Runtime distingue dos niveles (VISION-horizon.md):
- La lógica de autenticación PERTENECE a Horizon (estado persistente del
  usuario). El MECANISMO de almacenar/renovar credenciales vive en Runtime
  como infraestructura reutilizable por cualquier backend.

Este paquete es esa infraestructura. Es GENÉRICO desde el inicio
(ajuste 2 de Atlas): no hay "SpotifyAuth", sino AuthManager + Provider
Adapter. Hoy solo existe el proveedor Spotify; los demás (google, github,
telegram...) se añadirán sin desmontar nada.

Principios:
- Auth sin client_secret cuando el proveedor lo permita (PKCE para apps
  nativas/instaladas). Ajuste 1 de Atlas.
- El token se guarda por usuario en ~/.config/runtime/auth/<prov>.json.
- Nada de esto pertenece a ninguna Capability: es infra de Runtime.
"""
from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .provider import ProviderAdapter

DEFAULT_AUTH_DIR = Path.home() / ".config" / "runtime" / "auth"


class AuthManager:
    """Registro y ciclo de vida de credenciales por proveedor (ADR-0007).

    - Mantiene los adapters registrados.
    - Guarda/lee tokens en ~/.config/runtime/auth/<prov>.json.
    - Renueva tokens expirados bajo demanda.

    NO conoce HTTP ni detalles de proveedor: delega en el ProviderAdapter.
    """

    def __init__(self, auth_dir: Path | None = None):
        self.auth_dir = auth_dir or DEFAULT_AUTH_DIR
        self._providers: dict[str, ProviderAdapter] = {}

    def register(self, adapter: ProviderAdapter) -> None:
        self._providers[adapter.name] = adapter

    def provider(self, name: str) -> ProviderAdapter:
        try:
            return self._providers[name]
        except KeyError:
            raise KeyError(
                f"Proveedor '{name}' no registrado. "
                f"Disponibles: {sorted(self._providers)}"
            )

    def available(self) -> list[str]:
        return sorted(self._providers)

    # --- persistencia (por usuario) ---

    def _path(self, name: str) -> Path:
        return self.auth_dir / f"{name}.json"

    def _load(self, name: str) -> dict[str, Any] | None:
        p = self._path(name)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text())
        except Exception:
            return None

    def _save(self, name: str, data: dict[str, Any]) -> None:
        self.auth_dir.mkdir(parents=True, exist_ok=True)
        self._path(name).write_text(json.dumps(data, indent=2))

    def is_authenticated(self, name: str) -> bool:
        d = self._load(name)
        return bool(d and d.get("access_token"))

    def get_token(self, name: str) -> str | None:
        """Devuelve un access token válido, renovándolo si hizo falta.

        Devuelve None si no hay credenciales.
        """
        d = self._load(name)
        if not d:
            return None
        if d.get("expires_at") and time.time() >= d["expires_at"] and d.get("refresh_token"):
            adapter = self.provider(name)
            fresh = adapter.refresh(
                client_id=d.get("client_id", ""),
                refresh_token=d["refresh_token"],
            )
            d = self._merge_tokens(d, fresh)
            self._save(name, d)
        return d.get("access_token")

    def store_tokens(self, name: str, client_id: str, tokens: dict[str, Any]) -> None:
        """Guarda tokens tras un intercambio exitoso."""
        data = {
            "client_id": client_id,
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "expires_at": self._expiry(tokens),
        }
        self._save(name, data)

    @staticmethod
    def _expiry(tokens: dict[str, Any]) -> float | None:
        secs = tokens.get("expires_in")
        if isinstance(secs, (int, float)):
            return time.time() + float(secs) - 30
        return None

    @staticmethod
    def _merge_tokens(old: dict[str, Any], fresh: dict[str, Any]) -> dict[str, Any]:
        merged = dict(old)
        merged["access_token"] = fresh.get("access_token", old.get("access_token"))
        if fresh.get("refresh_token"):
            merged["refresh_token"] = fresh["refresh_token"]
        exp = AuthManager._expiry(fresh)
        if exp:
            merged["expires_at"] = exp
        return merged
