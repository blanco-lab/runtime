"""Backend Spotify para music_player (evolucionado, Parte B / ADR-0008).

Este backend es el ÚNICO que cambia en la Parte B. La Capability
music_player sigue CONGELADA: su interfaz `play(query)` NO cambia. El
backend internamente:

- Resuelve una credencial válida usando la infra de auth (ADR-0008):
  ExistingCredentialProvider (token de spotify_player) -> si no,
  RuntimeCredentialProvider (AuthManager/PKCE).
- Para música (track): usa SpotifyCLITransport (spotify_player CLI),
  igual que antes (REAL, ya verificado).
- Para podcast (show): usa SpotifyWebApiTransport (Web API) con el token
  resuelto y un device_id inyectado (ADR-0007 A3). El CLI no reproduce
  podcasts; la Web API sí.

La Capability NO sabe qué transporte se usa (ADR-0004). El token y el
device_id se inyectan; el backend no conoce su origen.
"""
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


def _run_cli(args: list[str], retries: int = 3) -> subprocess.CompletedProcess:
    """Ejecuta spotify_player con reintentos ante fallos de red (igual que antes)."""
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
    """Backend Spotify con dos transportes internos (ADR-0004)."""

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
        # A3: device_id desacoplado. Hoy del daemon vía Web API.
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

    # --- API pública de la Capability ( congelada ) ---
    def play(self, query: str) -> dict:
        if not query:
            return {"ok": False, "message": "Query vacía."}
        q = query.lower()
        # Si el usuario pide explícitamente un podcast, forzamos ruta show.
        wants_podcast = "podcast" in q
        if wants_podcast:
            show = self.cli.search_show(query)
            if show and show.get("id"):
                return self._play_podcast(show, query)
            return {"ok": False, "message": "No se encontró ese podcast."}
        # Si no, música: priorizamos track. Solo si no hay track, show.
        track = self.cli.search_track(query)
        if track and track.get("id"):
            return self._play_track(query)
        show = self.cli.search_show(query)
        if show and show.get("id"):
            return self._play_podcast(show, query)
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

    def _play_podcast(self, show: dict, query: str) -> dict:
        token = self._token_resolver()
        if not token:
            return {"ok": False,
                    "message": "Sin credencial de Spotify para reproducir podcasts. "
                               "Ejecuta 'runtime auth spotify' o usa spotify_player."}
        device_id = self._device_resolver()
        transport = SpotifyWebApiTransport(token, device_id, http=self._http)
        show_uri = f"spotify:show:{show['id']}"
        name = show.get("name", "?")
        r = transport.play_show(show_uri)
        if r.get("ok"):
            return {"ok": True, "message": f"Reproduciendo podcast: {name}",
                    "show_uri": show_uri, "name": name}
        return r

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


# Reexport para no romper importaciones existentes (compatibilidad).
SpotifyPlayerBackend = SpotifyBackend
