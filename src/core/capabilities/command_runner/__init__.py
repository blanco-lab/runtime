"""Capability: command_runner

Ejecuta operaciones del sistema previamente catalogadas. El resto de
Runtime nunca piensa en comandos: piensa en OPERACIONES (disk_usage,
memory_usage, uptime...). El backend traduce operación -> comando real.

Principios (AR-003, ADR-0004):
- La capability NO conoce comandos del sistema, solo un catálogo de
  operaciones permitidas. El backend hace la traducción y la ejecución.
- La capability NO se acopla a subprocess: delega en un CommandBackend
  (hoy LocalCommandBackend; mañana SSHBackend, DockerBackend...).
- Sin lenguaje natural: se invoca por clave de operación.
- Safety sigue siendo la única política de seguridad; command_runner solo
  ejecuta operaciones existentes en su catálogo.
"""
from dataclasses import dataclass, field
from typing import Any

from .backends.local_command import LocalCommandBackend


@dataclass
class CommandResult:
    """Resultado estandarizado de ejecutar una operación.

    Sigue el estilo del dominio (Intent, Action, SafetyResult,
    ExecutionResult...).
    """
    ok: bool
    operation: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    message: str = ""


# Catálogo de operaciones permitidas: operación -> argv (lista, shell=False).
# Ampliar aquí es la ÚNICA forma de habilitar una nueva operación.
CATALOG: dict[str, list[str]] = {
    "disk_usage": ["df", "-h"],
    "memory_usage": ["free", "-h"],
    "uptime": ["uptime"],
    "hostname": ["hostnamectl"],
    "network_interfaces": ["ip", "addr"],
    "current_directory": ["pwd"],
}


def _default_backend():
    # Hoy solo existe ejecución local. No se "elige": se inyecta.
    # Mañana un BackendFactory resolverá esto sin tocar esta capability.
    return LocalCommandBackend()


class CommandRunner:
    def __init__(self, backend=None, catalog: dict[str, list[str]] | None = None):
        self._backend = backend or _default_backend()
        self._catalog = catalog if catalog is not None else CATALOG

    def operations(self) -> list[str]:
        """Operaciones disponibles en el catálogo."""
        return sorted(self._catalog)

    def run(self, operation: str) -> CommandResult:
        """Ejecuta una operación del catálogo.

        Rechaza cualquier operación no catalogada (contrato de la
        capability). Safety sigue siendo la última palabra aguas arriba.
        """
        argv = self._catalog.get(operation)
        if argv is None:
            return CommandResult(
                ok=False,
                operation=operation,
                message=f"Operación '{operation}' no está en el catálogo.",
            )
        return self._backend.execute(operation, argv)
