"""Capability: music_player

Reproduce música. Es completamente independiente de la aplicación
que la implementa: delega en un Backend (hoy spotify_player).

Interfaz pública (estable):
    play(query)      -> reproduce la mejor coincidencia
    pause()         -> pausa
    resume()        -> reanuda
    next()          -> siguiente
    previous()      -> anterior
    volume(percent) -> volumen 0-100

La selección del backend (BackendFactory) llegará en el futuro; por
ahora se inyecta spotify_player directamente, sin acoplar la lógica.
"""
from .backends.spotify_player import SpotifyPlayerBackend


def _default_backend():
    # Hoy solo existe spotify_player. No se "elige": se inyecta.
    # Mañana un BackendFactory resolverá esto sin tocar esta capability.
    return SpotifyPlayerBackend()


class MusicPlayer:
    def __init__(self, backend=None):
        self._backend = backend or _default_backend()

    def play(self, query: str) -> dict:
        return self._backend.play(query)

    def pause(self) -> dict:
        return self._backend.pause()

    def resume(self) -> dict:
        return self._backend.resume()

    def next(self) -> dict:
        return self._backend.next()

    def previous(self) -> dict:
        return self._backend.previous()

    def volume(self, percent: int) -> dict:
        return self._backend.volume(percent)
