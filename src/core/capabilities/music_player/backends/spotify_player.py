"""Backend spotify_player para la capability music_player.

Implementa la interfaz Backend usando el CLI `spotify_player`,
que ya está instalado y autenticado en el equipo de Blanco.

Flujo play(query):
    1. spotify_player search <query>  -> JSON
    2. tomar tracks[0].id              (primera coincidencia)
    3. spotify_player playback start track <id>

NO es dependencia de Runtime: es un backend intercambiable (ADR-0004).
Cambiar a mpv/vlc/jellyfin no debe afectar a music_player.
"""
import json
import shutil
import subprocess
from pathlib import Path

from ...backend import Backend  # sube a capabilities/backend.py

_BIN = "spotify_player"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_BIN, *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


class SpotifyPlayerBackend(Backend):
    def play(self, query: str) -> dict:
        if not query:
            return {"ok": False, "message": "Query vacía."}
        if shutil.which(_BIN) is None:
            return {"ok": False, "message": f"{_BIN} no encontrado en PATH."}

        # 1) búsqueda
        try:
            res = _run(["search", query])
        except subprocess.TimeoutExpired:
            return {"ok": False, "message": "Timeout en la búsqueda."}
        if res.returncode != 0:
            return {"ok": False, "message": f"Error search: {res.stderr.strip()}"}

        # 2) primer resultado
        try:
            data = json.loads(res.stdout)
            track = data["tracks"][0]
            track_id = track["id"]
            name = track.get("name", "?")
            artists = ", ".join(a.get("name", "") for a in track.get("artists", []))
        except (json.JSONDecodeError, KeyError, IndexError):
            return {"ok": False, "message": "No se encontró ningún resultado."}

        # 3) reproducir
        try:
            res2 = _run(["playback", "start", "track", "--id", track_id])
        except subprocess.TimeoutExpired:
            return {"ok": False, "message": "Timeout al iniciar reproducción."}
        if res2.returncode != 0:
            err = res2.stderr.strip()
            hint = ""
            if "404" in err or "no playback" in err.lower():
                hint = " (sin dispositivo de Spotify activo: abre la app y reproduce algo)"
            return {
                "ok": False,
                "message": f"Error playback: {err}{hint}",
                "track_id": track_id,
                "name": name,
                "artists": artists,
            }

        return {
            "ok": True,
            "message": f"Reproduciendo: {name} — {artists}",
            "track_id": track_id,
            "name": name,
            "artists": artists,
        }

    def _simple(self, args: list[str], ok_msg: str) -> dict:
        """Ejecuta un comando de control y reporta el resultado real."""
        if shutil.which(_BIN) is None:
            return {"ok": False, "message": f"{_BIN} no encontrado en PATH."}
        try:
            res = _run(args)
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
