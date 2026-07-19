"""Proveedores de credenciales reutilizables (ADR-0008).

Política general de Runtime (ADR-0008):

    Runtime siempre aprovechará una autenticación existente antes de
    solicitar una nueva.

Un CredentialProvider resuelve "dame un token válido". El backend pide
un token sin importarle el origen; la resolución vive AQUÍ, en la
infra de auth, no en el backend (A2/A3 de ADR-0007 se preservan).

- ExistingCredentialProvider: reutiliza una sesión ya existente (HOY el
  token de spotify_player en ~/.cache/spotify-player/). NO guarda nada:
  solo LEE una sesión existente (cumple A2).
- RuntimeCredentialProvider: usa AuthManager (PKCE) cuando no hay
  credencial previa.

El resolver intenta Existing -> si None, Runtime.
"""
from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Credential:
    """Credencial genérica (ADR-0007 A1: Auth ≠ OAuth).

    Modela "una credencial válida" sin acoplarse al vocabulario OAuth.
    Hoy transporta un bearer token de Spotify; mañana podría llevar una
    API key, un certificado, etc.
    """

    def __init__(self, *, token: str, expires_at: float | None = None,
                 metadata: dict[str, Any] | None = None):
        self.token = token
        self.expires_at = expires_at
        self.metadata = metadata or {}

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() >= self.expires_at


class CredentialProvider(ABC):
    name: str = ""

    @abstractmethod
    def resolve(self) -> Credential | None:
        """Devuelve una credencial válida o None si no puede."""
        ...


class ExistingCredentialProvider(CredentialProvider):
    """Reutiliza la sesión ya existente de spotify_player (ADR-0008).

    Lee ~/.cache/spotify-player/user_client_token.json. Solo LEE; no
    guarda nada (cumple A2: la persistencia no se reparte en adapters).
    NO es un requisito permanente: es el primer ExistingCredentialProvider.
    En el futuro podría haber otros (p.ej. Horizon).
    """

    name = "existing-spotify-player"

    def __init__(self, cache_path: Path | None = None):
        self.cache_path = cache_path or (
            Path.home() / ".cache" / "spotify-player" / "user_client_token.json"
        )

    def resolve(self) -> Credential | None:
        if not self.cache_path.exists():
            return None
        try:
            data = json.loads(self.cache_path.read_text())
        except Exception:
            return None
        token = data.get("access_token") or data.get("token")
        if not token:
            return None
        expires_at = None
        if "expires_at" in data and data["expires_at"] is not None:
            try:
                # Puede venir como timestamp float o como ISO string.
                raw = data["expires_at"]
                if isinstance(raw, (int, float)):
                    expires_at = float(raw)
                else:
                    expires_at = time.mktime(
                        time.strptime(str(raw).replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
                    )
            except Exception:
                expires_at = None
        elif "expires_in" in data:
            expires_at = time.time() + float(data["expires_in"]) - 30
        # Si supiera que expiró, devolvería None y el resolver probaría
        # el siguiente proveedor. Sin info de expiración, confiamos.
        if expires_at is not None and expires_at <= time.time():
            return None
        return Credential(token=token, expires_at=expires_at,
                          metadata={"source": self.name})


class RuntimeCredentialProvider(CredentialProvider):
    """Usa la infra AuthManager (PKCE) cuando no hay credencial previa.

    Delega la resolución de token en AuthManager (que ya renueva solo).
    """

    name = "runtime-auth-manager"

    def __init__(self, manager, provider_name: str = "spotify"):
        self.manager = manager
        self.provider_name = provider_name

    def resolve(self) -> Credential | None:
        token = self.manager.get_token(self.provider_name)
        if not token:
            return None
        return Credential(token=token, metadata={"source": self.name})


def resolve_credential(*providers: CredentialProvider) -> Credential | None:
    """Intenta los proveedores en orden; devuelve la primera credencial.

    Política ADR-0008: reutilizar auth existente antes de pedir nueva.
    """
    for p in providers:
        try:
            cred = p.resolve()
        except Exception:
            cred = None
        if cred is not None:
            return cred
    return None
