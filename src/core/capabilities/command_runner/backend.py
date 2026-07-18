"""Backend base para la capability command_runner.

Un CommandBackend ejecuta una operación ya catalogada (argv concreto) y
devuelve un resultado. La capability NO se acopla a subprocess: hoy
existe LocalCommandBackend; mañana podrían añadirse SSHBackend,
DockerBackend, etc. sin tocar la capability (ADR-0004).

El backend recibe SIEMPRE un argv (lista de argumentos) resuelto por la
capability desde su catálogo. Nunca interpreta lenguaje ni cadenas de
shell.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import CommandResult


class CommandBackend(ABC):
    """Interfaz que todo backend de command_runner debe cumplir."""

    @abstractmethod
    def execute(self, operation: str, argv: list[str]) -> "CommandResult":
        """Ejecuta `argv` y devuelve un CommandResult.

        `operation` es la clave del catálogo (para trazabilidad); `argv`
        es la lista de argumentos ya validada por la capability.
        """
        ...
