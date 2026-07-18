"""Backend base para capabilities de Runtime.

Un Backend implementa una Capability concreta usando una aplicación
o servicio real (Spotify, mpv, VLC, Jellyfin...). Los backends son
intercambiables y NO deben acoplarse a la Capability (ADR-0004).

En el futuro un BackendFactory eligirá el backend según configuración,
descubrimiento o perfil de usuario. Por ahora se instancia el backend
directamente.
"""
from abc import ABC, abstractmethod


class Backend(ABC):
    """Interfaz que todo backend de music_player debe cumplir."""

    @abstractmethod
    def play(self, query: str) -> dict:
        """Busca y reproduce la mejor coincidencia para `query`."""
        ...

    @abstractmethod
    def pause(self) -> dict:
        ...

    @abstractmethod
    def resume(self) -> dict:
        ...

    @abstractmethod
    def next(self) -> dict:
        ...

    @abstractmethod
    def previous(self) -> dict:
        ...

    @abstractmethod
    def volume(self, percent: int) -> dict:
        ...
