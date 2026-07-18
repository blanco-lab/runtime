"""Pipeline de Runtime: orquesta el flujo extremo a extremo.

    Intent -> Action -> Safety -> Executor -> Reporter

El Core toma decisiones; no implementa herramientas. Cada componente es
intercambiable y proveedor-independiente.
"""
from .intent import understand
from .action import build
from .security.safety import evaluate
from .executor import execute
from .reporter import report


def run(user_text: str) -> str:
    """Recorre el pipeline completo y devuelve el informe para el usuario.

    Demuestra que Runtime puede procesar una petición de extremo a extremo.
    """
    intent = understand(user_text)            # Intent
    action = build(intent.label, intent)       # Action
    safety = evaluate(action)                # Safety
    execution = None
    if safety.decision.value != "reject":
        execution = execute(action)          # Executor
    result = report(action, safety, execution)  # Reporter
    return result.text


if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else "Pon música."
    print(run(text))
