"""HQ Backend — Puente de Mando de Horizon (ADR-0011 / Atlas 2026-07-19).

Arquitectura (Atlas): Git (fuente única) -> HQ Backend -> API interna
-> Dashboard Web. El Dashboard NUNCA toca el FS; solo habla con esta API.

Sin dependencias externas: stdlib (http.server + json). El repo es la
fuente de verdad; este backend LO LEE y lo expone como JSON. No escribe.

Endpoints:
  GET /api/state      -> estado global del proyecto
  GET /api/board      -> tablero de tareas (por estado)
  GET /api/adrs       -> decisiones (ADR-*)
  GET /api/principles -> principios rectores
  GET /api/reports    -> informes (reports/)
  GET /api/roadmap    -> roadmap derivado del board (no CONGELADA/ARCHIVADA)
  GET /api/meta       -> info del backend

ZUB: un solo comando `hq serve` levanta todo. El equipo edita hq/ con
git; el dashboard solo consulta.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root (hq/backend -> hq -> runtime)
HQ = ROOT / "hq"


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def _list_dir(d: Path) -> list[Path]:
    if not d.is_dir():
        return []
    return sorted(d.glob("*.md"), key=lambda x: x.name)


def _front_state(text: str) -> str:
    """Extrae estado de una línea tipo 'estado: CONGELADA' o 'Estado: ...'."""
    m = re.search(r"(?im)^\s*(?:estado|Estado)\s*[:=]\s*([A-ZÁÉÍÓÚÑ ]+)", text)
    if m:
        return m.group(1).strip()
    return ""


def _title_from_board(text: str) -> dict[str, list[dict]]:
    """Parsea board.md en secciones por estado.

    Cada entrada: [ID] Título — descripción  (con 'dueño:'/'estado:' en la
    línea o siguientes). Heurística simple y robusta.
    """
    out: dict[str, list[dict]] = {}
    cur = None
    item_re = re.compile(r"^\[([A-Z0-9\-]+)\]\s+(.*)$")
    for line in text.splitlines():
        h = re.match(r"^#{2,3}\s+(.*)$", line)
        if h:
            cur = h.group(1).strip().upper()
            out.setdefault(cur, [])
            continue
        m = item_re.match(line.strip())
        if m and cur:
            out[cur].append({
                "id": m.group(1),
                "title": m.group(2).strip(),
                "state": cur,
            })
    return out


def api_state() -> dict:
    board = _read(HQ / "board.md")
    adrs = _list_dir(HQ / "decisions")
    principles = _list_dir(HQ / "principles")
    reports = _list_dir(HQ / "reports")
    blocked = "BLK-" in board
    return {
        "project": "Runtime / Horizon",
        "source_of_truth": "git",
        "hq_path": str(HQ),
        "counts": {
            "adrs": len(adrs),
            "principles": len(principles),
            "reports": len(reports),
            "board_sections": len(_title_from_board(board)),
        },
        "has_blockers": blocked,
        "backend": "hq-backend",
    }


def api_board() -> dict:
    board = _read(HQ / "board.md")
    sections = _title_from_board(board)
    states = ["IDEA", "PROPUESTA", "DISEÑO", "APROBADA", "EN CURSO",
              "EN REVISIÓN", "CONGELADA", "ARCHIVADA"]
    ordered = {s: sections.get(s, []) for s in states}
    # Incluir secciones no previstas
    for k, v in sections.items():
        if k not in ordered:
            ordered[k] = v
    return {"states": states, "sections": ordered}


def api_adrs() -> dict:
    items = []
    for p in _list_dir(HQ / "decisions"):
        if not p.name.startswith("ADR-"):
            continue
        t = _read(p)
        title = ""
        for line in t.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        items.append({
            "id": p.stem,
            "title": title,
            "status": _front_state(t),
            "path": f"hq/decisions/{p.name}",
        })
    return {"adrs": items}


def api_principles() -> dict:
    items = []
    for p in _list_dir(HQ / "principles"):
        t = _read(p)
        title = ""
        for line in t.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        items.append({"id": p.stem, "title": title, "path": f"hq/principles/{p.name}"})
    return {"principles": items}


def api_reports() -> dict:
    items = []
    for p in _list_dir(HQ / "reports"):
        if p.name.upper() == "TEMPLATE.md":
            continue
        t = _read(p)
        title = ""
        for line in t.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        items.append({"id": p.stem, "title": title, "path": f"hq/reports/{p.name}"})
    return {"reports": items}


def api_roadmap() -> dict:
    """Roadmap = piezas no CONGELADA/ARCHIVADA del board."""
    board = api_board()
    active = []
    for st, items in board["sections"].items():
        if st in ("CONGELADA", "ARCHIVADA"):
            continue
        active.extend(items)
    return {"active": active, "total_active": len(active)}


_ROUTES = {
    "/api/state": api_state,
    "/api/board": api_board,
    "/api/adrs": api_adrs,
    "/api/principles": api_principles,
    "/api/reports": api_reports,
    "/api/roadmap": api_roadmap,
    "/api/meta": lambda: {"ok": True, "backend": "hq-backend", "root": str(ROOT)},
}


def handle(path: str) -> tuple[int, dict]:
    fn = _ROUTES.get(path)
    if fn is None:
        return 404, {"error": "not found", "path": path}
    try:
        return 200, {"ok": True, **fn()}
    except Exception as e:  # nunca romper la API por un parseo
        return 500, {"error": str(e)}


if __name__ == "__main__":
    # Uso directo para pruebas: imprime JSON de cada ruta.
    import sys
    for r in _ROUTES:
        code, data = handle(r)
        print(r, code, json.dumps(data, ensure_ascii=False)[:200])
