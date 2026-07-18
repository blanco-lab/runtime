"""Executor: realiza la acción utilizando el proveedor adecuado.

En el MVP, el Executor es un MOCK: no reproduce música de verdad, solo
demuestra que el pipeline llega hasta aquí y devuelve un resultado.

Punto de extensión: aquí se enruta la Action a la capacidad real
(music_player, email.send, bash.run, ...) según el proveedor disponible.
La capacidad es indiferente de quién la provea (Atlas/Hermes/script/API).
"""
from dataclasses import dataclass
from typing import Any

from ..action import Action


@dataclass
class ExecutionResult:
    success: bool
    message: str
    data: dict[str, Any] | None = None


# Registro mock de capacidades disponibles (sustituible por descubrimiento real).
_MOCK_CAPABILITIES = {"music_player"}


def execute(action: Action) -> ExecutionResult:
    """Ejecuta la Action. En el MVP, mock: imprime por pantalla.

    Demuestra que el pipeline recorre de extremo a extremo.
    """
    if action.capability not in _MOCK_CAPABILITIES:
        return ExecutionResult(
            success=False,
            message=f"Capacidad '{action.capability}' no disponible en el mock.",
        )

    # Mock: no reproduce música real, solo lo certifica.
    return ExecutionResult(
        success=True,
        message=f"[MOCK] Ejecutando capacidad '{action.capability}' "
                f"para acción '{action.type}'. (Sin efecto real en el MVP.)",
        data={"capability": action.capability, "type": action.type},
    )
