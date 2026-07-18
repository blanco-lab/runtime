"""Executor: realiza la acción utilizando el proveedor adecuado.

En la Fase 1, music_player es una CAPABILITY REAL (delega en
spotify_player). El resto de capacidades permanece mock hasta que se
implementen (ADR-0003 / ADR-0004).
"""
from dataclasses import dataclass
from typing import Any

from ..action import Action
from ..capabilities.music_player import MusicPlayer


@dataclass
class ExecutionResult:
    success: bool
    message: str
    data: dict[str, Any] | None = None


def execute(action: Action) -> ExecutionResult:
    """Ejecuta la Action.

    - music_player: capability REAL (spotify_player hoy).
    - lo demás: mock (sin efecto).
    """
    if action.capability == "music_player":
        mp = MusicPlayer()
        t = action.type
        if t == "play_music":
            result = mp.play(action.params.get("query") or "")
        elif t == "pause_music":
            result = mp.pause()
        elif t == "resume_music":
            result = mp.resume()
        elif t == "next_track":
            result = mp.next()
        elif t == "previous_track":
            result = mp.previous()
        elif t == "set_volume":
            result = mp.volume(action.params.get("percent") or 50)
        else:
            result = {"ok": False, "message": f"Orden '{t}' no soportada."}
        return ExecutionResult(
            success=result.get("ok", False),
            message=result.get("message", ""),
            data=result,
        )

    # Mock para el resto de capacidades (no implementadas todavía).
    if action.capability not in _MOCK_CAPABILITIES:
        return ExecutionResult(
            success=False,
            message=f"Capacidad '{action.capability}' no disponible.",
        )
    return ExecutionResult(
        success=True,
        message=f"[MOCK] Ejecutando capacidad '{action.capability}' "
                f"para acción '{action.type}'. (Sin efecto real.)",
        data={"capability": action.capability, "type": action.type},
    )


_MOCK_CAPABILITIES = {"none"}
