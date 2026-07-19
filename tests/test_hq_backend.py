#!/usr/bin/env python3
"""Test de HQ Backend (sin red): la API interna parsea hq/ a JSON.

Verifica que el backend lee Git como fuente única y expone:
  /api/state /api/board /api/adrs /api/principles /api/reports /api/roadmap
El dashboard NO toca FS; esto prueba que la API sí lee el repo.

Ejecuta: python3 tests/test_hq_backend.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hq.backend import handle  # noqa: E402


def main() -> int:
    ok = True
    routes = ["/api/state", "/api/board", "/api/adrs", "/api/principles",
              "/api/reports", "/api/roadmap", "/api/meta"]
    for r in routes:
        code, data = handle(r)
        good = code == 200 and isinstance(data, dict) and data.get("ok") is True
        if not good:
            ok = False
        print(f"  [{'OK' if good else 'FAIL'}] {r} -> {code}")

    # state tiene counts coherentes
    _, st = handle("/api/state")
    assert st["source_of_truth"] == "git"
    assert st["counts"]["adrs"] >= 11, st["counts"]
    print("  [OK] state.source_of_truth = git, adrs >= 11")

    # board expone las 8 secciones de estado
    _, b = handle("/api/board")
    for s in ["IDEA", "PROPUESTA", "DISEÑO", "APROBADA", "EN CURSO",
              "EN REVISIÓN", "CONGELADA", "ARCHIVADA"]:
        if s not in b["sections"]:
            ok = False
            print(f"  [FAIL] board sin sección {s}")
    print("  [OK] board tiene las 8 secciones de estado")

    # adrs incluye ADR-0011 y ADR-0010 (cerrada)
    _, a = handle("/api/adrs")
    ids = [x["id"] for x in a["adrs"]]
    assert "ADR-0011-horizon-hq" in ids, ids
    assert "ADR-0010-domain-model" in ids
    print("  [OK] adrs incluye ADR-0011 y ADR-0010")

    # roadmap = activas (no congeladas/archivadas)
    _, rm = handle("/api/roadmap")
    assert isinstance(rm["active"], list)
    print(f"  [OK] roadmap activas = {rm['total_active']}")

    # ruta inexistente -> 404
    code, _ = handle("/api/nope")
    assert code == 404
    print("  [OK] /api/nope -> 404")

    print("\nRESULTADO:", "TODO VERDE" if ok else "HAY FALLOS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
