#!/usr/bin/env python3
"""Test funcional de la capability command_runner (AR-003).

Ejecuta:
    python3 tests/test_command_runner.py

Verifica:
- Operaciones del catálogo se ejecutan y devuelven CommandResult ok.
- Operaciones NO catalogadas se rechazan (contrato de la capability).
- Intentos de inyección (metacaracteres, comandos compuestos) NO existen
  como operación => rechazados. Además shell=False lo hace inofensivo.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.capabilities.command_runner import CommandRunner, CommandResult, CATALOG


def main() -> int:
    cr = CommandRunner()
    ok = True

    print("== Catálogo disponible ==")
    print(" ", cr.operations())

    print("\n== Operaciones permitidas (deben ejecutarse) ==")
    for op in CATALOG:
        res = cr.run(op)
        assert isinstance(res, CommandResult), "no devuelve CommandResult"
        passed = res.ok and res.exit_code == 0
        ok = ok and passed
        head = (res.stdout or res.stderr).strip().splitlines()[:1]
        print(f"[{'OK ' if passed else 'FAIL'}] {op} (exit={res.exit_code}) {head}")

    print("\n== Operaciones NO catalogadas (deben rechazarse) ==")
    for op in ["rm", "shutdown", "df", "ls -la ; rm -rf ~", "disk_usage; rm", "__nope__"]:
        res = cr.run(op)
        passed = (not res.ok) and res.exit_code is None
        ok = ok and passed
        print(f"[{'OK ' if passed else 'FAIL'}] {op!r} -> {res.message}")

    print("\n== CommandResult es dataclass del dominio ==")
    r = cr.run("uptime")
    print(f"  ok={r.ok} operation={r.operation!r} exit_code={r.exit_code}")

    print("\nRESULTADO:", "TODO VERDE" if ok else "HAY FALLOS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
