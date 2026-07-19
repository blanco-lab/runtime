"""ProviderAdapter de Spotify (ADR-0007, ajustes 1 y 2 de Atlas).

- PKCE (supports_pkce=True): app instalada, SIN client_secret.
- Las llamadas HTTP viven AQUÍ, dentro del proveedor (backend), nunca en
  una Capability.
- El token se guarda por usuario vía AuthManager (no aquí).

Scopes: los mínimos para reproducir (incluye podcasts):
  user-read-playback-state, user-modify-playback-state,
  user-read-currently-playing
"""
from __future__ import annotations

import urllib.parse
import urllib.request
from typing import Any

from ..provider import ProviderAdapter

_SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
_SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# Scopes mínimos para control de reproducción (música y podcasts).
_SCOPES = "user-read-playback-state user-modify-playback-state user-read-currently-playing"


class SpotifyProvider(ProviderAdapter):
    name = "spotify"
    supports_pkce = True

    @property
    def scopes(self) -> str:
        return _SCOPES

    def token_url(self) -> str:
        return _SPOTIFY_TOKEN_URL

    def build_auth_url(self, *, client_id: str, redirect_uri: str,
                       state: str, code_challenge: str) -> str:
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "code_challenge_method": "S256",
            "code_challenge": code_challenge,
            "state": state,
            "scope": self.scopes,
        }
        return f"{_SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}"

    def _post(self, body: dict[str, str]) -> dict[str, Any]:
        data = urllib.parse.urlencode(body).encode()
        req = urllib.request.Request(
            self.token_url(),
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json_loads(resp.read())

    def exchange_code(self, *, client_id: str, redirect_uri: str,
                      code: str, code_verifier: str) -> dict[str, Any]:
        return self._post({
            "client_id": client_id,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
            # Sin client_secret: flujo PKCE para app instalada.
        })

    def refresh(self, *, client_id: str, refresh_token: str) -> dict[str, Any]:
        return self._post({
            "client_id": client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        })


def json_loads(b: bytes) -> dict[str, Any]:
    import json
    return json.loads(b)
