"""Safety: decide si una acción puede ejecutarse.

Resultados posibles:
- ALLOW      -> ejecutar directamente
- CONFIRM    -> requiere confirmación humana
- REJECT     -> no se ejecuta (inaceptable)

Defensa en profundidad: puede cortar tanto en fase Intent como en Action.
"""
from dataclasses import dataclass
from enum import Enum
from ..action import Action


class SafetyDecision(str, Enum):
    ALLOW = "allow"
    CONFIRM = "confirm"
    REJECT = "reject"


@dataclass
class SafetyResult:
    decision: SafetyDecision
    reason: str = ""


# Lista negra de capacidades siempre REJECT (defensa en profundidad).
_FORBIDDEN_CAPABILITIES = {"shutdown_system", "delete_everything"}


def evaluate(action: Action) -> SafetyResult:
    """Evalúa una Action y decide su destino.

    Extensible: reglas de lista blanca, confirmación, y corte temprano.
    """
    if action.capability in _FORBIDDEN_CAPABILITIES:
        return SafetyResult(
            SafetyDecision.REJECT,
            reason=f"Capacidad '{action.capability}' está prohibida.",
        )

    if action.type == "unknown":
        return SafetyResult(
            SafetyDecision.REJECT,
            reason="Intención no reconocida; no se puede ejecutar.",
        )

    # Mock: todo lo demás se ejecuta directamente.
    # (Más adelante: acciones destructivas -> CONFIRM.)
    return SafetyResult(SafetyDecision.ALLOW, reason="Acción permitida (mock).")
