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


# Mapeo mock frase exacta -> etiqueta (sustituible por IA).
_KNOWN = {
    "pon música": "play_music",
    "pon musica": "play_music",
    "reproduce música": "play_music",
    "reproduce musica": "play_music",
    # control de reproducción
    "para": "pause_music",
    "para la música": "pause_music",
    "para la musica": "pause_music",
    "pausa": "pause_music",
    "pausa la música": "pause_music",
    "pausa la musica": "pause_music",
    "detén la música": "pause_music",
    "deten la musica": "pause_music",
    "reanuda": "resume_music",
    "reanuda la música": "resume_music",
    "reanuda la musica": "resume_music",
    "continúa": "resume_music",
    "continua": "resume_music",
    "sigue": "resume_music",
    "siguiente": "next_track",
    "pasa": "next_track",
    "pasa de canción": "next_track",
    "pasa de cancion": "next_track",
    "salta": "next_track",
    "anterior": "previous_track",
    "atrás": "previous_track",
    "atras": "previous_track",
    "canción anterior": "previous_track",
    "cancion anterior": "previous_track",
    # sistema
    "apaga el ordenador": "shutdown_system",
    "apaga el computador": "shutdown_system",
}

# Prefijos que indican reproducir algo concreto.
_PLAY_PREFIXES = ("pon ", "reproduce ", "reproduce a ", "pon a ")


def _extract_query(text: str) -> str:
    """Extrae la query de 'pon <query>' / 'reproduce <query>'.

    Mock simple; mañana la IA hará este trabajo.
    """
    t = text.lower()
    for pref in _PLAY_PREFIXES:
        if t.startswith(pref):
            q = text[len(pref):].strip().rstrip(".!?¡¿")
            if q:
                return q
    return ""


def _extract_volume(text: str) -> int | None:
    """Extrae un porcentaje de volumen del texto, si lo hay."""
    import re
    m = re.search(r"(\d{1,3})\s*%?", text)
    if m:
        return max(0, min(100, int(m.group(1))))
    if "sube" in text:
        return 80
    if "baja" in text:
        return 30
    return None


def understand(user_text: str) -> Intent:
    """Devuelve la intención comprendida a partir del texto del usuario.

    Por ahora es un mock por palabras clave. El punto de extensión para
    conectar un proveedor de IA (Atlas/Hermes/Codex) es este método.
    """
    text = user_text.strip().lower()
    # Normaliza: quita signos de puntuación final para comparar frases.
    text_key = text.rstrip(".!?¡¿")
    label = _KNOWN.get(text_key)
    entities: dict[str, Any] = {}

    if label is None:
        # Reproducir algo concreto: "pon <x>" / "reproduce <x>".
        if any(text.startswith(p) for p in _PLAY_PREFIXES):
            label = "play_music"
        # Volumen: "sube/baja el volumen", "volumen al 50%", "pon el volumen a 40".
        elif "volumen" in text or (("sube" in text or "baja" in text) and "%" in text):
            label = "set_volume"
        # Control por palabra clave (variantes naturales).
        elif "siguiente" in text or "salta" in text or "próxima" in text or "proxima" in text:
            label = "next_track"
        elif "anterior" in text or "atrás" in text or "atras" in text or "previa" in text:
            label = "previous_track"
        elif "pausa" in text or "para" in text or "detén" in text or "deten" in text:
            label = "pause_music"
        elif "reanuda" in text or "continúa" in text or "continua" in text or "sigue" in text:
            label = "resume_music"
        # Fallback: si contiene "música"/"musica" -> play_music
        elif "música" in text or "musica" in text:
            label = "play_music"
        else:
            label = "unknown"

    if label == "play_music":
        q = _extract_query(user_text)
        if q:
            entities["query"] = q
    elif label == "set_volume":
        v = _extract_volume(text)
        if v is not None:
            entities["percent"] = v

    return Intent(
        label=label,
        raw_text=user_text,
        confidence=1.0,
        entities=entities,
    )
