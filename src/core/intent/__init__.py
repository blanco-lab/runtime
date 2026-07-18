"""Intent: comprende qué quiere el usuario.

Entrada: lenguaje natural (texto).
Salida: una intención estructurada y proveedor-independiente.

En el MVP, el Intent es un clasificador mock: mapea frases conocidas a
una etiqueta de intención. Sustituible por un modelo de IA real.

Campos confidence y entities presentes desde el inicio (ADR-0003 #2),
aunque por ahora sean valores mock.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Intent:
    """Una intención estructurada."""
    label: str          # ej. "play_music"
    raw_text: str       # texto original del usuario
    confidence: float = 1.0
    entities: dict[str, Any] = field(default_factory=dict)


# Mapeo mock intención -> etiqueta (sustituible por IA).
_KNOWN = {
    "pon música": "play_music",
    "pon musica": "play_music",
    "reproduce música": "play_music",
    "reproduce musica": "play_music",
    "apaga el ordenador": "shutdown_system",
    "apaga el computador": "shutdown_system",
}


def _extract_query(text: str) -> str:
    """Extrae la query de 'pon <query>' / 'reproduce <query>'.

    Mock simple; mañana la IA hará este trabajo.
    """
    t = text.lower()
    for pref in ("pon ", "reproduce "):
        if t.startswith(pref):
            q = text[len(pref):].strip().rstrip(".!?¡¿")
            if q:
                return q
    return ""


def understand(user_text: str) -> Intent:
    """Devuelve la intención comprendida a partir del texto del usuario.

    Por ahora es un mock por palabras clave. El punto de extensión para
    conectar un proveedor de IA (Atlas/Hermes/Codex) es este método.
    """
    text = user_text.strip().lower()
    # Normaliza: quita signos de puntuación final para comparar frases.
    text_key = text.rstrip(".!?¡¿")
    label = _KNOWN.get(text_key)
    if label is None:
        # Fallback: "pon <x>" / "reproduce <x>" -> play_music (query extraída).
        if text.startswith("pon ") or text.startswith("reproduce "):
            label = "play_music"
        # Fallback 2: si contiene "música"/"musica" -> play_music
        elif "música" in text or "musica" in text:
            label = "play_music"
        else:
            label = "unknown"

    entities: dict[str, Any] = {}
    if label == "play_music":
        q = _extract_query(user_text)
        if q:
            entities["query"] = q

    return Intent(
        label=label,
        raw_text=user_text,
        confidence=1.0,
        entities=entities,
    )
