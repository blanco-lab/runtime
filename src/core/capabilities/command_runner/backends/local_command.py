"""LocalCommandBackend: ejecuta operaciones en la máquina local.

Usa subprocess con lista de argumentos y shell=False (obligatorio,
AR-003 punto 2): es imposible inyectar metacaracteres de shell
(; | > $() && ...), porque nunca se pasa por una shell.

Recibe el argv ya resuelto y validado por la capability desde su
catálogo. Este backend NO decide qué se puede ejecutar: solo ejecuta lo
que la capability le entrega.
"""
import shutil
import subprocess

from ..backend import CommandBackend

# Import diferido del CommandResult para evitar ciclo con el paquete padre.


def _result(**kwargs):
    from .. import CommandResult
    return CommandResult(**kwargs)


class LocalCommandBackend(CommandBackend):
    TIMEOUT = 15

    def execute(self, operation: str, argv: list[str]):
        if not argv:
            return _result(ok=False, operation=operation,
                          message="argv vacío.")
        if shutil.which(argv[0]) is None:
            return _result(ok=False, operation=operation,
                          message=f"Comando '{argv[0]}' no encontrado en PATH.")
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                shell=False,          # OBLIGATORIO (AR-003)
                timeout=self.TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return _result(ok=False, operation=operation,
                          message=f"Timeout ({self.TIMEOUT}s).")
        except Exception as e:  # noqa: BLE001 - reportar sin filtrar traza
            return _result(ok=False, operation=operation,
                          message=f"Error de ejecución: {e}")

        return _result(
            ok=(proc.returncode == 0),
            operation=operation,
            stdout=proc.stdout,
            stderr=proc.stderr,
            exit_code=proc.returncode,
            message="OK" if proc.returncode == 0 else "El comando devolvió error.",
        )
