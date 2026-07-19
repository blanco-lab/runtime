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
    "stop": "pause_music",
    "stop la música": "pause_music",
    "stop la musica": "pause_music",
    "parar": "pause_music",
    "parar la música": "pause_music",
    "parar la musica": "pause_music",
    "detener": "pause_music",
    "detener la música": "pause_music",
    "detener la musica": "pause_music",
    "apaga la música": "pause_music",
    "apaga la musica": "pause_music",
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
        # ¿Es una petición de podcast (con o sin "pon")?
        if _is_podcast_request(text):
            # Listar episodios vs reproducir.
            if any(w in text for w in ["lista", "listar", "muestra", "muéstrame",
                                     "enseña", "enseñame", "ver los", "ver las"]):
                label = "list_podcast"
            else:
                label = "play_podcast"
        # Reproducir algo concreto: "pon <x>" / "reproduce <x>".
        elif any(text.startswith(p) for p in _PLAY_PREFIXES):
            label = "play_music"
        # Volumen: "sube/baja el volumen", "volumen al 50%", "pon el volumen a 40".
        elif "volumen" in text or (("sube" in text or "baja" in text) and "%" in text):
            label = "set_volume"
        # Control por palabra clave (variantes naturales).
        elif "siguiente" in text or "salta" in text or "próxima" in text or "proxima" in text:
            label = "next_track"
        elif "anterior" in text or "atrás" in text or "atras" in text or "previa" in text:
            label = "previous_track"
        elif "pausa" in text or "para" in text or "detén" in text or "deten" in text or "stop" in text or "parar" in text or "detener" in text or "apaga la música" in text or "apaga la musica" in text:
            label = "pause_music"
        elif "reanuda" in text or "continúa" in text or "continua" in text or "sigue" in text:
            label = "resume_music"
        # Fallback: si contiene "música"/"musica" -> play_music
        elif "música" in text or "musica" in text:
            label = "play_music"
        else:
            label = "unknown"

    # Entidades según el label.
    if label == "play_music":
        q = _extract_query(user_text)
        if q:
            entities["query"] = q
    elif label in ("play_podcast", "list_podcast"):
        entities.update(_extract_podcast_entities(user_text))
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


# --- podcast ---

def _is_podcast_request(text: str) -> bool:
    """Detecta si la petición es de podcast (no música)."""
    return any(w in text for w in (
        "podcast", "pódcast", "capítulo", "capitulo",
        "episodio", "episodio", "monólogo", "monologo",
    ))


def _extract_podcast_entities(user_text: str) -> dict[str, Any]:
    """Extrae entidades de una petición de podcast (ADR/ajustes Atlas).

    - show_query: nombre del podcast (ej. "Monos Estocásticos").
    - episode_title: si pide "que se llama X" / "titulado X".
    - episode_number: si pide "capítulo N" / "episodio N" (LITERAL).
    - list: si pide ver la lista de episodios.
    """
    import re
    text = user_text.strip()
    t = text.lower()
    ents: dict[str, Any] = {}

    # Número de capítulo/episodio: número LITERAL (regla de Blanco).
    m = re.search(r"(?:capí?tulo|episodio)\s+(?:n[ºo°]?\s*)?(\d+)", t)
    if m:
        ents["episode_number"] = int(m.group(1))

    # Título de episodio: "que se llama X" / "titulado X" / "llamado X".
    mt = re.search(r"(?:que se llama|titulado|llamado|llamada)\s+([^,.!?]+)", t)
    if mt:
        ents["episode_title"] = mt.group(1).strip().rstrip(".!?¡¿")

    # Listado: "lista"/"muestra"/"enséñame" + "capítulos"/"episodios".
    if any(w in t for w in ["lista", "listar", "muestra", "muéstrame", "enseña", "enseñame", "ver los", "ver las"]):
        if any(w in t for w in ["capítulo", "capitulo", "episodio", "episodio", "podcast"]):
            ents["list"] = True

    # Show query: el nombre del podcast. Eliminamos cortesía y marcas.
    show = text
    for pat in (
        # cortesía inicial (hasta el nombre del podcast)
        r"^.*?\b(?:pon|quiero|dame|ponme|escuchar|o[ií]r|quier[oa]|querr[íi]a|"
        r"lista|listar|muestra|ense[ñn]a|ense[ñn]ame|ver)\b\s*"
        r"(?:los|las|un\s+|una\s+)?(?:podcast|p[oó]dcast|el|la|los|las)?\s*(?:de\s+|sobre\s+|los\s+|las\s+)?",
        # "que se llama X" / "titulado X" -> borra desde ahí (el título va en episode_title)
        r"\b(?:que se llama|titulado|llamado|llamada)\b.*$",
        # "capítulo N de" / "episodio N de" -> conserva el nombre que queda
        r"\b(?:cap[íi]tulo|episodio)\s+\d+\s+de\s+",
        r"\b(?:cap[íi]tulo|episodio)\s+\d+\b",
        # marcas sueltas
        r"\b(?:y|el|la|los|las|un|una|este|esta|ese|esa)\s+(?:podcast|p[oó]dcast|cap[íi]tulo|episodio)\b",
        r"\b(?:podcast|p[oó]dcast|cap[íi]tulo|episodios|cap[íi]tulos|episodio)\b",
    ):
        show = re.sub(pat, " ", show, flags=re.IGNORECASE)
    show = re.sub(r"\s+", " ", show).strip(" .!?¡¿,")
    # Quita artículos sueltos que pudieran quedar al inicio tras los reemplazos.
    show = re.sub(r"^(el|la|los|las|un|una|este|esta|ese|esa)\b", " ", show,
                  flags=re.IGNORECASE).strip(" .!?¡¿,")
    if show:
        ents["show_query"] = show
    return ents
