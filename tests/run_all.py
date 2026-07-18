#!/usr/bin/env python3
"""Runner canónico de tests de Runtime.

Ejecuta toda la batería de tests funcionales del proyecto y devuelve
exit 0 solo si todos pasan. Este es el comando canónico de verificación:

    python3 tests/run_all.py

Cada test individual sigue siendo ejecutable por separado.
"""
import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SUITE = [
    "test_command_runner.py",
    "test_music_player.py",
]


def main() -> int:
    failed = []
    for name in SUITE:
        path = TESTS_DIR / name
        print(f"\n{'='*60}\n== {name}\n{'='*60}")
        rc = subprocess.run([sys.executable, str(path)]).returncode
        if rc != 0:
            failed.append(name)

    print(f"\n{'='*60}")
    if failed:
        print("RESULTADO GLOBAL: FALLOS en", ", ".join(failed))
        return 1
    print(f"RESULTADO GLOBAL: TODO VERDE ({len(SUITE)} suites)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
