"""Intent: comprende qué quiere el usuario.

Entrada: lenguaje natural (texto).
Salida: una intención estructurada y proveedor-independiente.

En el MVP, el Intent es un clasificador mock: mapea frases conocidas a
una etiqueta de intención. Sustituible por un modelo de IA real.
"""
from dataclasses import dataclass


@dataclass
class Intent:
    """Una intención estructurada."""
    label: str          # ej. "play_music"
    raw_text: str       # texto original del usuario
    confidence: float = 1.0


# Mapeo mock intención -> etiqueta (sustituible por IA).
_KNOWN = {
    "pon música": "play_music",
    "pon musica": "play_music",
    "reproduce música": "play_music",
    "reproduce musica": "play_music",
    "apaga el ordenador": "shutdown_system",
    "apaga el computador": "shutdown_system",
}


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
        # Fallback muy simple: si contiene "música"/"musica" -> play_music
        if "música" in text or "musica" in text:
            label = "play_music"
        else:
            label = "unknown"
    return Intent(label=label, raw_text=user_text)
