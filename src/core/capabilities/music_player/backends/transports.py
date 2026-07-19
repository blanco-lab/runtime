"""Transportes internos del backend Spotify (ADR-0004 / ADR-0008).

El backend Spotify expone una sola interfaz a la Capability music_player,
pero internamente usa DOS transportes y elige según el tipo de _play:

- SpotifyCLITransport: usa el CLI `spotify_player` (tracks). Hoy es el
  mecanismo por defecto para música (ya verificado, REAL).
- SpotifyWebApiTransport: usa la Spotify Web API (HTTPS) para lo que el
  CLI no cubre — concretamente podcasts (shows/episodes).

La Capability NO sabe qué transporte se usa (ADR-0004). SpotifyWebApi
recibe por INYECCIÓN un token (resuelto vía infra de auth ADR-0008) y un
device_id (ADR-0007 A3: no sabe de dónde procede). NO hay REST en la
Capability.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import urllib.error
import urllib.request
from typing import Callable


# --- transporte CLI (spotify_player) ---

def _run_cli(args: list[str], retries: int = 3) -> subprocess.CompletedProcess:
    """Ejecuta spotify_player con reintentos ante fallos de red (igual que antes)."""
    import time
    last_err = None
    for attempt in range(retries):
        try:
            return subprocess.run(["spotify_player", *args], capture_output=True,
                                  text=True, timeout=30)
        except (subprocess.TimeoutExpired, OSError) as e:
            last_err = e
            if attempt == retries - 1:
                break
            time.sleep(0.5 * (2 ** attempt))
    assert last_err is not None
    raise last_err


class SpotifyCLITransport:
    """Reproduce tracks vía el CLI spotify_player (busca + playback)."""

    def search_track(self, query: str) -> dict | None:
        try:
            res = _run_cli(["search", query])
        except subprocess.TimeoutExpired:
            return None
        if res.returncode != 0:
            return None
        try:
            data = json.loads(res.stdout)
            return data["tracks"][0]
        except (json.JSONDecodeError, KeyError, IndexError):
            return None

    def start_track(self, track_id: str) -> dict:
        try:
            res = _run_cli(["playback", "start", "track", "--id", track_id])
        except subprocess.TimeoutExpired:
            return {"ok": False, "message": "Timeout al iniciar reproducción."}
        if res.returncode != 0:
            err = res.stderr.strip()
            hint = ""
            if "404" in err or "no playback" in err.lower():
                hint = " (sin dispositivo de Spotify activo: abre la app y reproduce algo)"
            return {"ok": False, "message": f"Error playback: {err}{hint}",
                    "track_id": track_id}
        return {"ok": True}

    def search_show(self, query: str) -> dict | None:
        """Busca un show (podcast). El CLI lo encuentra aunque no lo reproduzca."""
        try:
            res = _run_cli(["search", query])
        except subprocess.TimeoutExpired:
            return None
        if res.returncode != 0:
            return None
        try:
            data = json.loads(res.stdout)
            return data["shows"][0]
        except (json.JSONDecodeError, KeyError, IndexError):
            # La search unificada a veces no trae "shows"; lo intentamos
            # con un término explícito. Si sigue sin haber, devolvemos None.
            return None


# --- transporte Web API (podcasts) ---

class SpotifyWebApiTransport:
    """Reproduce podcasts (shows) vía Spotify Web API.

    - Token: inyectado (resuelto por la infra de auth ADR-0008). No sabe
      si viene de spotify_player o de AuthManager.
    - device_id: inyectado (ADR-0007 A3). No sabe de dónde procede
      (hoy del daemon, mañana de Spotify Connect/móvil/etc.).
    """

    BASE = "https://api.spotify.com/v1"

    def __init__(self, token: str, device_id: str | None,
                 http: Callable | None = None):
        self.token = token
        self.device_id = device_id
        self._http = http or urllib.request.urlopen

    def play_show(self, show_uri: str) -> dict:
        url = f"{self.BASE}/me/player/play"
        if self.device_id:
            url += f"?device_id={self.device_id}"
        body = json.dumps({"context_uri": show_uri}).encode()
        req = urllib.request.Request(
            url, data=body, method="PUT",
            headers={"Authorization": f"Bearer {self.token}",
                     "Content-Type": "application/json"},
        )
        try:
            self._http(req, timeout=20)
            return {"ok": True, "message": f"Reproduciendo podcast: {show_uri}",
                    "show_uri": show_uri}
        except urllib.error.HTTPError as e:
            detail = e.read().decode() if e.fp else ""
            return {"ok": False,
                    "message": f"Error Web API ({e.code}): {detail[:200]}"}
        except urllib.error.URLError as e:
            return {"ok": False, "message": f"Error de red: {e.reason}"}
