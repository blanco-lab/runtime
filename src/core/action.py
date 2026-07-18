"""Action: traduce una intención a una acción interna estandarizada.

Una Action es la representación neutral que el resto del pipeline entiende,
independiente de quién la ejecute. El Executor la consume.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Action:
    """Acción estandarizada lista para el Safety/Executor."""
    type: str                       # ej. "play_music"
    capability: str = "music_player"  # capacidad requerida (proveedor-agnóstico)
    params: dict[str, Any] = field(default_factory=dict)
    intent_label: str = ""


def build(intent_label: str, intent=None) -> Action:
    """Construye la Action correspondiente a una intención.

    Punto de extensión: aquí se mapea intención -> (capacidad, parámetros).
    Recibe el Intent completo para tomar params como `query`.
    """
    query = None
    percent = None
    if intent is not None:
        query = intent.entities.get("query")
        percent = intent.entities.get("percent")

    # Órdenes de la capability music_player (play + control de reproducción).
    _MUSIC_ACTIONS = {
        "play_music", "pause_music", "resume_music",
        "next_track", "previous_track", "set_volume",
    }
    if intent_label in _MUSIC_ACTIONS:
        params: dict[str, Any] = {}
        if intent_label == "play_music":
            params["query"] = query
        elif intent_label == "set_volume":
            params["percent"] = percent
        return Action(
            type=intent_label,
            capability="music_player",
            params=params,
            intent_label=intent_label,
        )
    if intent_label == "shutdown_system":
        # Intención conocida pero sensible: se construye la Action y el
        # corte lo debe hacer Safety (defensa en profundidad), no el Intent.
        return Action(
            type="shutdown_system",
            capability="shutdown_system",
            params={},
            intent_label=intent_label,
        )
    # Intención no mapeada todavía.
    return Action(
        type="unknown",
        capability="none",
        params={},
        intent_label=intent_label,
    )
