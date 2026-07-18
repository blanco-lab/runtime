"""Reporter: devuelve un resultado uniforme al usuario.

Independiente de qué pasó internamente, el Reporter produce una salida
legible y estandarizada para el usuario (texto, y en el futuro voz/UI).
"""
from dataclasses import dataclass

from .action import Action
from .security.safety import SafetyResult, SafetyDecision
from .executor import ExecutionResult


@dataclass
class Report:
    text: str
    ok: bool


def report(
    action: Action,
    safety: SafetyResult,
    execution: ExecutionResult | None = None,
) -> Report:
    """Construye el informe final para el usuario."""
    if safety.decision == SafetyDecision.REJECT:
        return Report(
            text=f"No se ejecuta: {safety.reason}",
            ok=False,
        )

    if execution is None:
        return Report(text="Acción no ejecutada.", ok=False)

    if execution.success:
        return Report(text=execution.message, ok=True)

    return Report(text=f"Error al ejecutar: {execution.message}", ok=False)
