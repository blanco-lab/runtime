"""Backend Spotify para music_player (evolucionado, Parte B / ADR-0008).

Este backend es el ÚNICO que cambia. La Capability music_player sigue
CONGELADA: su interfaz `play(query)` NO cambia. El backend internamente
resuelve credenciales (ADR-0008) y delega en transportes.

AJUSTE DE ATLAS (revisión podcasts): el backend NO interpreta lenguaje
natural ni decide play/list. Expone PRIMITIVAS TÉCNICAS PURAS:
    play_show(show_uri)
    play_episode(episode_uri)
    search_episode(show_id, query)
    list_episodes(show_id, limit, offset)
Quién invoca qué es decisión del Intent (y mañana Horizon), no del
backend. Este módulo incluye un `BackendDispatcher` que traduce una
petición ya estructurada (no NL crudo) a la primitiva correcta; el NL lo
resuelve el Intent aguas arriba.

- Resolución de credencial (ADR-0008): ExistingCredentialProvider (token
  de spotify_player) -> si no, RuntimeCredentialProvider (AuthManager/PKCE).
- Para música (track): SpotifyCLITransport (CLI), igual que antes (REAL).
- Para podcast: SpotifyWebApiTransport con token + device_id inyectados
  (ADR-0007 A3). El CLI no reproduce podcasts; la Web API sí.

La Capability NO sabe qué transporte se usa (ADR-0004).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Callable

from ...backend import Backend
from .transports import SpotifyCLITransport, SpotifyWebApiTransport
from ....auth.credentials import (
    ExistingCredentialProvider, RuntimeCredentialProvider, resolve_credential,
)
from ....auth import AuthManager
from ....auth.providers import SpotifyProvider
from ....domain import EntityType, DomainEntity, Listing


def _run_cli(args: list[str], retries: int = 3) -> subprocess.CompletedProcess:
    import time
    last_err = None
    for attempt in range(retries):
        try:
            return subprocess.run(
                ["spotify_player", *args], capture_output=True, text=True, timeout=30
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            last_err = e
            if attempt == retries - 1:
                break
            time.sleep(0.5 * (2 ** attempt))
    assert last_err is not None
    raise last_err


class SpotifyBackend(Backend):
    """Backend Spotify con primitivas separadas (ADR-0004 / ajuste Atlas)."""

    def __init__(self, token_resolver: Callable[[], str | None] | None = None,
                 device_id_resolver: Callable[[], str | None] | None = None,
                 http: Callable | None = None):
        self.cli = SpotifyCLITransport()
        self._token_resolver = token_resolver or self._default_token
        self._device_resolver = device_id_resolver or self._default_device
        self._http = http

    # --- resolución de credencial (ADR-0008) ---
    def _default_token(self) -> str | None:
        mgr = AuthManager()
        mgr.register(SpotifyProvider())
        cred = resolve_credential(
            ExistingCredentialProvider(),
            RuntimeCredentialProvider(mgr, "spotify"),
        )
        return cred.token if cred else None

    def _default_device(self) -> str | None:
        token = self._token_resolver()
        if not token:
            return None
        try:
            req = urllib.request.Request(
                "https://api.spotify.com/v1/me/player/devices",
                headers={"Authorization": f"Bearer {token}"},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            for d in data.get("devices", []):
                if d.get("is_active"):
                    return d["id"]
        except Exception:
            return None
        return None

    def _api(self) -> SpotifyWebApiTransport:
        token = self._token_resolver()
        if not token:
            raise RuntimeError("Sin credencial de Spotify para Web API.")
        return SpotifyWebApiTransport(token, self._device_resolver(), http=self._http)

    # --- PRIMITIVAS (sin NL, sin decisión de play/list) ---

    def play_show(self, show_uri: str) -> dict:
        return self._api().play_show(show_uri)

    def play_episode(self, episode_uri: str) -> dict:
        return self._api().play_episode(episode_uri)

    def search_episode(self, show_id: str, query: str) -> list[dict]:
        return self._api().search_episode(show_id, query)

    # NOTA: list_episodes de dominio (devuelve Listing) está definido más
    # abajo, en la sección "Dominio de catálogo". El BackendDispatcher y el
    # Executor lo consumen vía Listing.items / Listing.total.

    # --- compatibilidad: play(query) sigue siendo la entrada de la Capability ---
    # NOTA: aquí el backend hace un enrutado mínimo track-vs-show SOLO para
    # mantener la interfaz play(query) de la Capability congelada. La
    # selección fina por episodio/título/número la resuelve el dispatcher
    # (ver BackendDispatcher) invocado por el Intent aguas arriba.
    def play(self, query: str) -> dict:
        if not query:
            return {"ok": False, "message": "Query vacía."}
        track = self.cli.search_track(query)
        if track and track.get("id"):
            return self._play_track(query)
        show = self.cli.search_show(query)
        if show and show.get("id"):
            return self.play_show(f"spotify:show:{show['id']}")
        return {"ok": False, "message": "No se encontró ningún resultado."}

    def _play_track(self, query: str) -> dict:
        track = self.cli.search_track(query)
        if not track:
            return {"ok": False, "message": "No se encontró ningún resultado."}
        track_id = track["id"]
        name = track.get("name", "?")
        artists = ", ".join(a.get("name", "") for a in track.get("artists", []))
        r = self.cli.start_track(track_id)
        if not r.get("ok"):
            return {"ok": False, "message": r.get("message", "Error"),
                    "track_id": track_id, "name": name, "artists": artists}
        return {"ok": True, "message": f"Reproduciendo: {name} — {artists}",
                "track_id": track_id, "name": name, "artists": artists}

    # --- controles (CLI, igual que antes) ---
    def _simple(self, args: list[str], ok_msg: str) -> dict:
        if shutil.which("spotify_player") is None:
            return {"ok": False, "message": "spotify_player no encontrado en PATH."}
        try:
            res = _run_cli(args)
        except subprocess.TimeoutExpired:
            return {"ok": False, "message": "Timeout."}
        if res.returncode != 0:
            err = res.stderr.strip()
            hint = ""
            if "404" in err or "no playback" in err.lower():
                hint = " (sin dispositivo de Spotify activo o nada sonando)"
            return {"ok": False, "message": f"Error: {err}{hint}"}
        return {"ok": True, "message": ok_msg}

    def pause(self) -> dict:
        return self._simple(["playback", "pause"], "Pausado.")

    def resume(self) -> dict:
        return self._simple(["playback", "play"], "Reanudado.")

    def next(self) -> dict:
        return self._simple(["playback", "next"], "Siguiente.")

    def previous(self) -> dict:
        return self._simple(["playback", "previous"], "Anterior.")

    def volume(self, percent: int) -> dict:
        p = max(0, min(100, int(percent)))
        return self._simple(["playback", "volume", str(p)], f"Volumen {p}%.")

    # --- Modelo de dominio (ADR-0010): proveedor-agnóstico, objetos efímeros ---

    def list_tracks(self, album_id: str, limit: int = 50, offset: int = 0) -> Listing:
        """Canciones de un album (DomainProvider)."""
        data = self._api().list_tracks(album_id, limit, offset)
        items = [DomainEntity(id=e["id"], uri=e["uri"], name=e["name"],
                             entity_type=EntityType.TRACK, extra=e.get("extra", {}))
                 for e in data.get("items", [])]
        return Listing(entity_type=EntityType.TRACK, items=items,
                      total=data.get("total", len(items)), offset=offset, query="")

    def list_albums(self, artist_id: str, limit: int = 10, offset: int = 0) -> Listing:
        """Albums de un artista (DomainProvider)."""
        data = self._api().list_albums(artist_id, limit, offset)
        items = [DomainEntity(id=e["id"], uri=e["uri"], name=e["name"],
                             entity_type=EntityType.ALBUM, extra=e.get("extra", {}))
                 for e in data.get("items", [])]
        return Listing(entity_type=EntityType.ALBUM, items=items,
                      total=data.get("total", len(items)), offset=offset, query="")

    def list_episodes(self, show_id: str, limit: int = 10, offset: int = 0) -> Listing:
        """Episodios de un show (DomainProvider)."""
        data = self._api().list_episodes(show_id, limit, offset)
        items = [DomainEntity(id=e["id"], uri=e["uri"], name=e["name"],
                             entity_type=EntityType.EPISODE, extra=e.get("extra", {}))
                 for e in data.get("items", [])]
        return Listing(entity_type=EntityType.EPISODE, items=items,
                      total=data.get("total", len(items)), offset=offset, query="")

    def search(self, entity_type, query: str, limit: int = 10) -> Listing:
        """Busca entidades de un tipo en el dominio (DomainProvider)."""
        t = EntityType(entity_type)
        data = self._api().search(str(t.value), query, limit)
        items = [DomainEntity(id=e["id"], uri=e["uri"], name=e["name"],
                             entity_type=t, extra=e.get("extra", {}))
                 for e in data.get("items", [])]
        return Listing(entity_type=t, items=items, total=data.get("total", len(items)),
                      offset=0, query=query)


# Reexport para no romper importaciones existentes (compatibilidad).
SpotifyPlayerBackend = SpotifyBackend


class BackendDispatcher:
    """Traduce una petición ESTRUCTURADA (no NL crudo) a la primitiva.

    El NL lo resuelve el Intent aguas arriba. Aquí solo enruta según el
    tipo de petición. Esto mantiene el backend agnóstico al lenguaje
    natural (ajuste de Atlas).
    """

    def __init__(self, backend: SpotifyBackend):
        self.b = backend

    def dispatch(self, req: dict) -> dict:
        kind = req.get("kind")
        if kind == "play_show":
            return self.b.play_show(req["uri"])
        if kind == "play_episode":
            return self.b.play_episode(req["uri"])
        if kind == "search_episode":
            return {"ok": True, "items": self.b.search_episode(req["show_id"], req["query"])}
        if kind == "list_episodes":
            listing = self.b.list_episodes(req["show_id"], req.get("limit", 10),
                                           req.get("offset", 0))
            return {"ok": True, "data": {
                "items": [{"uri": i.uri, "name": i.name} for i in listing.items],
                "total": listing.total,
            }}
        return {"ok": False, "message": f"Primitiva desconocida: {kind}"}
