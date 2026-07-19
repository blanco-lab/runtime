"""Transportes internos del backend Spotify (ADR-0004 / ADR-0008).

El backend Spotify expone una sola interfaz a la Capability music_player,
pero internamente usa DOS transportes y elige según el tipo de _play:

- SpotifyCLITransport: usa el CLI `spotify_player` (tracks). Hoy es el
  mecanismo por defecto para música (ya verificado, REAL).
- SpotifyWebApiTransport: usa la Spotify Web API (HTTPS) para lo que el
  CLI no cubre — podcasts (shows/episodes) y listados.

PRINCIPIO (ajuste de Atlas, revisión podcasts): el backend NO interpreta
lenguaje natural ni decide play/list. Expone primitivas TÉCNICAS puras:
play_show, play_episode, search_episode, list_episodes. Quién invoca qué
es decisión del Intent (y mañana Horizon), no del backend.

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
import urllib.parse
import urllib.request
from typing import Callable


# --- transporte CLI (spotify_player) ---

def _run_cli(args: list[str], retries: int = 3) -> subprocess.CompletedProcess:
    """Ejecuta spotify_player con reintentos ante fallos de red."""
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

    @staticmethod
    def search_show(query: str) -> dict | None:
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
            return None


# --- transporte Web API (podcasts) ---

class SpotifyWebApiTransport:
    """Primitivas de podcast vía Spotify Web API.

    - Token: inyectado (resuelto por la infra de auth ADR-0008). No sabe
      si viene de spotify_player o de AuthManager.
    - device_id: inyectado (ADR-0007 A3). No sabe de dónde procede.
    - El backend llama a estas primitivas; NO decide por lenguaje natural.
    """

    BASE = "https://api.spotify.com/v1"

    def __init__(self, token: str, device_id: str | None,
                 http: Callable | None = None):
        self.token = token
        self.device_id = device_id
        self._http = http or urllib.request.urlopen

    def _put(self, url: str, body: dict) -> dict:
        req = urllib.request.Request(
            url, data=json.dumps(body).encode(), method="PUT",
            headers={"Authorization": f"Bearer {self.token}",
                     "Content-Type": "application/json"},
        )
        try:
            self._http(req, timeout=20)
            return {"ok": True}
        except urllib.error.HTTPError as e:
            detail = e.read().decode() if e.fp else ""
            return {"ok": False, "message": f"Error Web API ({e.code}): {detail[:200]}"}
        except urllib.error.URLError as e:
            return {"ok": False, "message": f"Error de red: {e.reason}"}

    def _get(self, url: str) -> dict:
        req = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {self.token}"}
        )
        try:
            with self._http(req, timeout=20) as r:
                return {"ok": True, "data": json.loads(r.read())}
        except urllib.error.HTTPError as e:
            detail = e.read().decode() if e.fp else ""
            return {"ok": False, "message": f"Error Web API ({e.code}): {detail[:200]}"}
        except urllib.error.URLError as e:
            return {"ok": False, "message": f"Error de red: {e.reason}"}

    # --- primitivas (sin NL, sin decisión de play/list) ---

    def play_show(self, show_uri: str) -> dict:
        url = f"{self.BASE}/me/player/play"
        if self.device_id:
            url += f"?device_id={self.device_id}"
        r = self._put(url, {"context_uri": show_uri})
        if r.get("ok"):
            return {"ok": True, "message": f"Reproduciendo show: {show_uri}",
                    "show_uri": show_uri}
        return r

    def play_episode(self, episode_uri: str) -> dict:
        url = f"{self.BASE}/me/player/play"
        if self.device_id:
            url += f"?device_id={self.device_id}"
        r = self._put(url, {"uris": [episode_uri]})
        if r.get("ok"):
            return {"ok": True, "message": f"Reproduciendo episodio: {episode_uri}",
                    "episode_uri": episode_uri}
        return r

    def search_episode(self, show_id: str, query: str) -> list[dict]:
        """Devuelve episodes del show cuyo título contiene `query`."""
        listing = self.list_episodes(show_id, limit=50, offset=0)
        if not listing.get("ok"):
            return []
        return [e for e in listing["items"]
                if query.lower() in (e.get("name") or "").lower()]

    def list_episodes(self, show_id: str, limit: int = 10, offset: int = 0) -> dict:
        url = f"{self.BASE}/shows/{show_id}/episodes?limit={limit}&offset={offset}"
        r = self._get(url)
        if not r.get("ok"):
            return r
        # El backend envuelve en Listing; aquí devolvemos el formato crudo
        # que espera el backend (items + total), no anidado.
        raw = r["data"].get("items", [])
        return {"ok": True, "items": [self._norm(e, "episode") for e in raw],
                "total": r["data"].get("total", len(raw))}

    def search(self, entity_type: str, query: str, limit: int = 10) -> dict:
        """Búsqueda genérica de catálogo (type=album|artist|track|playlist|
        show|episode). Devuelve {"items":[{id,uri,name,extra}], "total"}."""
        url = f"{self.BASE}/search?type={entity_type}&q={urllib.parse.quote(query)}&limit={limit}"
        r = self._get(url)
        if not r.get("ok"):
            return r
        # Spotify anida bajo la clave del tipo (ej. "albums", "tracks").
        key = entity_type + "s" if not entity_type.endswith("y") else entity_type[:-1] + "ies"
        bucket = r["data"].get(key, r["data"].get(entity_type, {}))
        raw = bucket.get("items", []) if isinstance(bucket, dict) else []
        total = bucket.get("total", len(raw)) if isinstance(bucket, dict) else len(raw)
        items = [self._norm(e, entity_type) for e in raw]
        return {"ok": True, "items": items, "total": total}

    def list_tracks(self, album_id: str, limit: int = 50, offset: int = 0) -> dict:
        url = f"{self.BASE}/albums/{album_id}/tracks?limit={limit}&offset={offset}"
        r = self._get(url)
        if not r.get("ok"):
            return r
        raw = r["data"].get("items", [])
        items = [self._norm(e, "track") for e in raw]
        return {"ok": True, "items": items, "total": r["data"].get("total", len(raw))}

    def list_albums(self, artist_id: str, limit: int = 10, offset: int = 0) -> dict:
        url = f"{self.BASE}/artists/{artist_id}/albums?limit={limit}&offset={offset}"
        r = self._get(url)
        if not r.get("ok"):
            return r
        raw = r["data"].get("items", [])
        items = [self._norm(e, "album") for e in raw]
        return {"ok": True, "items": items, "total": r["data"].get("total", len(raw))}

    @staticmethod
    def _norm(e: dict, entity_type: str) -> dict:
        """Normaliza un item crudo de Spotify al formato interno."""
        uri = e.get("uri", "")
        name = e.get("name", "")
        eid = e.get("id", "")
        extra = {}
        if entity_type in ("track", "album") and "artists" in e:
            extra["artists"] = [a.get("name", "") for a in e["artists"]]
        if entity_type == "album" and "release_date" in e:
            extra["release_date"] = e["release_date"]
        return {"id": eid, "uri": uri, "name": name, "extra": extra}
