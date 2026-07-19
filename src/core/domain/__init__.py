"""Modelo de dominio de Runtime (ADR-0010).

Vocabulario común independiente del proveedor. SpotifyBackend (y mañana
Jellyfin/Plex/Apple Music/LocalMusic) traduce el JSON del proveedor a
estas entidades. La Capability music_player sigue siendo quien REPRODUCE
audio; el modelo de dominio es el lenguaje con el que trabaja
(búsqueda/listado), proveedor-agnóstico.

Entidades del dominio (EFÍMERAS: se crean, se usan, se destruyen durante
la ejecución; NO se almacenan — ADR-0010 / ajuste de Atlas):
- Artist, Album, Track, Playlist, Show, Episode

NO es un catálogo: no hay BD local, no hay sincronización, no hay caché
permanente. Toda la información vive en el proveedor (Spotify hoy, otros
mañana). Runtime nunca es propietario de los datos.

Contrato de listado homogéneo para Horizon (ADR-0010):
    {
        "entity_type": "album",
        "items": [{"id", "uri", "name", "extra": {...}}],
        "total": int,
        "offset": int,
        "query": str,
    }

Todo stateless (ADR-0009): Runtime devuelve este objeto durante la
ejecución; no lo persiste.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EntityType(str, Enum):
    ARTIST = "artist"
    ALBUM = "album"
    TRACK = "track"
    PLAYLIST = "playlist"
    SHOW = "show"
    EPISODE = "episode"


@dataclass
class DomainEntity:
    """Un elemento del dominio (cualquier entidad). Vive solo durante la ejecución."""
    id: str
    uri: str
    name: str
    entity_type: EntityType
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Listing:
    """Resultado de listar/buscar en el dominio (contrato con Horizon).

    Runtime lo devuelve durante la ejecución; NO lo persiste (ADR-0009).
    """
    entity_type: EntityType
    items: list[DomainEntity]
    total: int
    offset: int
    query: str = ""


class DomainProvider:
    """Interfaz del proveedor de dominio (proveedor-agnóstico).

    SpotifyBackend la implementa hoy. Mañana: JellyfinBackend, etc.
    Sin memoria, sin contexto, sin lenguaje natural. Objetos efímeros.
    """

    def search(self, entity_type: EntityType, query: str, limit: int = 10) -> Listing:
        """Busca entidades de un tipo por query."""
        raise NotImplementedError

    def list_tracks(self, album_id: str, limit: int = 50, offset: int = 0) -> Listing:
        """Canciones de un album (entity_type=track)."""
        raise NotImplementedError

    def list_albums(self, artist_id: str, limit: int = 10, offset: int = 0) -> Listing:
        """Albums de un artista (entity_type=album)."""
        raise NotImplementedError

    def list_episodes(self, show_id: str, limit: int = 10, offset: int = 0) -> Listing:
        """Episodios de un show (entity_type=episode)."""
        raise NotImplementedError
