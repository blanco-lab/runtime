"""ProviderAdapter: contrato de un proveedor de autenticación (ADR-0007).

Base genérica. Cada proveedor (Spotify hoy; Google/GitHub/Telegram en el
futuro) implementa una subclase. Runtime solo conoce esta interfaz;
no sabe detalles de ningún proveedor.

Adapte 1 de Atlas: si el proveedor soporta OAuth para aplicaciones
nativas/instaladas, declara supports_pkce=True y el flujo va sin
client_secret (usa code_challenge/code_verifier).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProviderAdapter(ABC):
    name: str = ""  # p.ej. "spotify"
    supports_pkce: bool = False  # True para apps instaladas (sin client_secret)

    @abstractmethod
    def build_auth_url(self, *, client_id: str, redirect_uri: str,
                       state: str, code_challenge: str) -> str:
        """URL que el usuario abre para autorizar la app."""
        ...

    @abstractmethod
    def exchange_code(self, *, client_id: str, redirect_uri: str,
                      code: str, code_verifier: str) -> dict[str, Any]:
        """Cambia authorization code por tokens. Devuelve dict crudo."""
        ...

    @abstractmethod
    def refresh(self, *, client_id: str, refresh_token: str) -> dict[str, Any]:
        """Renueva el access token. Devuelve dict crudo."""
        ...

    @property
    @abstractmethod
    def scopes(self) -> str:
        ...

    @abstractmethod
    def token_url(self) -> str:
        ...
