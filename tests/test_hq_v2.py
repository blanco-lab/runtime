#!/usr/bin/env python3
"""Test del Backend HQ v2 (Puente de Mando), sin red.

Verifica que /api/v2/* expone los módulos de ADR-0013 y que la Horizon
Shell hace dispatch real a la API (lectura). No toca el FS el dashboard;
estos son los datos que el frontend consumiría.

Ejecuta: python3 tests/test_hq_v2.py
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hq.backend import v2  # noqa: E402


def main() -> int:
    ok = True
    # content (reusa v1)
    for r in ("/api/v2/content/state", "/api/v2/content/board",
              "/api/v2/content/adrs", "/api/v2/content/principles",
              "/api/v2/content/reports", "/api/v2/content/roadmap"):
        code, d = v2.handle(r)
        if not (code == 200 and d.get("ok")):
            ok = False
        print(f"  [{'OK' if code==200 and d.get('ok') else 'FAIL'}] {r} -> {code}")

    # services: dos grupos presentes
    code, d = v2.handle("/api/v2/services")
    assert code == 200 and d["ecosystem"] and d["system"], d
    print(f"  [OK] services: {len(d['ecosystem'])} ecosystem, {len(d['system'])} system")

    # projects: cada uno su repo (no carpetas de runtime)
    code, d = v2.handle("/api/v2/projects")
    projs = d["projects"]
    assert any(p["name"] == "runtime" and "github.com" in p["repo"] for p in projs)
    print(f"  [OK] projects: {len(projs)} (cada uno su repo propio)")

    # workspace/team/meetings/settings presentes
    for r in ("/api/v2/workspace", "/api/v2/team", "/api/v2/meetings", "/api/v2/settings"):
        code, d = v2.handle(r)
        assert code == 200 and d.get("ok"), (r, d)
        print(f"  [OK] {r} -> {code}")

    # Horizon Shell: dispatch real
    code, d = v2.handle("/api/v2/shell", "cmd=board")
    assert d["ok"] and d["type"] == "board", d
    print("  [OK] shell 'board' -> dispatch a API (board)")
    code, d = v2.handle("/api/v2/shell", "cmd=services")
    assert d["ok"] and d["type"] == "services", d
    print("  [OK] shell 'services' -> dispatch (services)")
    code, d = v2.handle("/api/v2/shell", "cmd=desconocido")
    assert d["ok"] is False, d
    print("  [OK] shell comando desconocido -> error controlado")

    # 404 para ruta inexistente
    code, _ = v2.handle("/api/v2/nope")
    assert code == 404
    print("  [OK] /api/v2/nope -> 404")

    # ── HQ-003: comunicación del equipo (Workspace -> Git bajo Safety)
    from pathlib import Path as _P
    team_file = ROOT / "hq" / "workspace" / "team" / "horizon-team.jsonl"
    # limpiar workspace para test aislado (git-ignored, seguro)
    if team_file.exists():
        team_file.unlink()
    m = v2.team_post("Blanco", "Propuesta de prueba HQ-003")
    assert m["id"] and m["text"].startswith("Propuesta")
    msgs = v2.team_list()
    assert any(x["id"] == m["id"] for x in msgs), "mensaje no persistido en workspace"
    print("  [OK] team: mensaje escrito y leído en workspace (git-ignored)")

    # marcar leído
    v2.team_mark_read([m["id"]])
    assert v2.team_list()[0]["read"] is True
    print("  [OK] team: marcar leído")

    # promover a ADR -> crea archivo en hq/decisions y commitea en git
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT),
                            capture_output=True, text=True).stdout.strip()
    res = v2.team_promote(m["id"], "adr", by="HQ-003")
    assert res.get("ok"), res
    assert (ROOT / res["file"]).exists(), res
    after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT),
                           capture_output=True, text=True).stdout.strip()
    assert before != after, "promover no commiteó en git"
    print(f"  [OK] team: promovido a ADR -> {res['file']} (commit en git)")
    # limpiar: borrar el ADR de prueba y deshacer commit para no ensuciar repo
    subprocess.run(["git", "reset", "--soft", "HEAD~1"], cwd=str(ROOT),
                   capture_output=True, text=True)
    (ROOT / res["file"]).unlink()

    # promover a tarea -> añade a board.md y commitea
    res2 = v2.team_promote(m["id"], "tarea", by="HQ-003")
    assert res2.get("ok"), res2
    subprocess.run(["git", "reset", "--soft", "HEAD~1"], cwd=str(ROOT),
                   capture_output=True, text=True)
    # restaurar board.md (el append queda en working tree; lo descartamos)
    subprocess.run(["git", "checkout", "--", "hq/board.md"], cwd=str(ROOT),
                   capture_output=True, text=True)
    print("  [OK] team: promovido a tarea (board.md + commit, revertido)")

    print("\nRESULTADO:", "TODO VERDE" if ok else "HAY FALLOS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
