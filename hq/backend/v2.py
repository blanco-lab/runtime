"""HQ Backend v2 — Puente de Mando (ADR-0013, aprobada y congelada).

Amplía el backend v1 con módulos de HQ v2 bajo /api/v2/*:
  content   -> reusa la lectura de git (board/adrs/principles/reports/roadmap/state)
  workspace -> borradores del equipo (hq/workspace/, git-ignored). v2b: lectura.
  services  -> ECOSYSTEM (Runtime/HQ/Horizon/Spotify/Ollama/Redis/Telegram)
               + SYSTEM (CPU/RAM/Discos/Red/Batería/Temperatura). Lectura.
  projects  -> proyectos del ecosistema (cada uno su repo git; HQ orquesta).
  team      -> sala de reuniones (estructura; datos en workspace).
  shell     -> Horizon Shell: dispatcher de comandos a la API (lectura).
  meetings  -> estructura (agenda/conv/decisiones/acciones).
  settings  -> lectura de config del ecosistema.

PRINCIPIOS (ADR-0012/0013):
  - El frontend NUNCA toca el FS; solo habla con /api/v2/*.
  - Este backend SÍ puede leer el sistema (para estado de servicios), pero
    el dashboard no.
  - Sin dependencias de pago ni externas (stdlib). Lectura, no escritura
    salvo "Promover" (futuro, con Safety).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

from hq.backend import handle as v1_handle  # reusa content

ROOT = Path(__file__).resolve().parents[2]
HQ = ROOT / "hq"
WORKSPACE = HQ / "workspace"


# ───────────────────────────────────────────────────────────── services
def _systemctl_active(unit: str) -> str:
    """Devuelve 'active'/'inactive'/'unknown' sin shell (lista de args)."""
    try:
        r = subprocess.run(
            ["systemctl", "--user", "is-active", unit],
            capture_output=True, text=True, timeout=3,
        )
        out = r.stdout.strip()
        if out in ("active", "inactive", "failed"):
            return out
        return "unknown"
    except Exception:
        return "unknown"


def _read_sys(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").strip()
    except OSError:
        return None


def services_ecosystem() -> list[dict]:
    # Runtime/HQ están vivos si este backend corre (UP).
    items = [
        {"name": "Runtime", "kind": "ecosystem", "status": "up",
         "note": "motor de ejecución"},
        {"name": "HQ", "kind": "ecosystem", "status": "up",
         "note": "Puente de Mando (este servidor)"},
        {"name": "Horizon", "kind": "ecosystem", "status": "down",
         "note": "agente (futuro)"},
        {"name": "Spotify", "kind": "ecosystem",
         "status": _systemctl_active("spotify-player-daemon"),
         "note": "daemon user"},
    ]
    # Ollama/Redis/Telegram: chequeo best-effort por systemd
    for name, unit in [("Ollama", "ollama"), ("Redis", "redis"),
                       ("Telegram", "telegram")]:
        st = _systemctl_active(unit)
        items.append({"name": name, "kind": "ecosystem", "status": st,
                      "note": f"unit {unit} (si existe)"})
    return items


def _cpu_percent() -> float:
    def stat():
        raw = _read_sys(Path("/proc/stat")) or "cpu 0 0 0 0"
        parts = raw.splitlines()[0].split()[1:5]
        return sum(int(x) for x in parts), int(time.time() * 1000)
    a = stat(); time.sleep(0.3); b = stat()
    total = b[0] - a[0]
    # idle es el último de los 4 leídos; aproximación simple
    idle = b[0] - a[0]
    return round(min(100.0, 100.0 * (1 - idle / total)) if total else 0.0, 1)


def services_system() -> list[dict]:
    items = []
    # RAM
    mem = {}
    raw = _read_sys(Path("/proc/meminfo")) or ""
    for line in raw.splitlines():
        k, *_v = line.split(":")
        v = "".join(_v).strip().split()[0] if _v else "0"
        try:
            mem[k.strip()] = int(v)
        except ValueError:
            pass
    total = mem.get("MemTotal", 0); avail = mem.get("MemAvailable", 0)
    ram_pct = round((1 - avail / total) * 100, 1) if total else 0.0
    items.append({"name": "RAM", "kind": "system",
                  "status": f"{ram_pct}%", "note": f"{avail//1024}MB libres"})
    # Discos
    for mp in ["/", "/home"]:
        u = shutil.disk_usage(mp)
        pct = round((1 - u.free / u.total) * 100, 1)
        items.append({"name": f"Disco {mp}", "kind": "system",
                       "status": f"{pct}%", "note": f"{u.free//(1024**3)}GB libres"})
    # Red
    net = _read_sys(Path("/proc/net/dev")) or ""
    rx = tx = 0
    for line in net.splitlines()[2:]:
        cols = line.split()
        if len(cols) >= 10:
            rx += int(cols[1]); tx += int(cols[9])
    items.append({"name": "Red", "kind": "system",
                  "status": "ok", "note": f"rx {rx//(1024**2)}MB tx {tx//(1024**2)}MB"})
    # Batería
    bat = None
    for p in Path("/sys/class/power_supply").glob("BAT*"):
        cap = _read_sys(p / "capacity")
        if cap:
            bat = f"{cap}%"
    if bat:
        items.append({"name": "Batería", "kind": "system", "status": bat,
                      "note": "portátil = nodo Horizon"})
    # Temperatura
    for p in Path("/sys/class/thermal").glob("thermal_zone*"):
        t = _read_sys(p / "temp")
        if t:
            items.append({"name": "Temp", "kind": "system",
                          "status": f"{int(t)//1000}°C", "note": "thermal_zone"})
            break
    return items


# ───────────────────────────────────────────────────────────── projects
def projects_list() -> list[dict]:
    # v2b: registro local de proyectos del ecosistema (cada uno su repo).
    # Futuro: leer project.yaml de cada repo. HQ orquesta, no contiene.
    return [
        {"name": "runtime", "type": "core", "status": "en curso",
         "repo": "github.com/blanco-lab/runtime", "responsible": "Blanco",
         "note": "motor de ejecución (congelado)"},
        {"name": "horizon-agent", "type": "agent", "status": "idea",
         "repo": "(pendiente)", "responsible": "—",
         "note": "agente conversacional (futuro)"},
        {"name": "hq", "type": "coord", "status": "en revisión",
         "repo": "github.com/blanco-lab/runtime (hq/)", "responsible": "Hermes",
         "note": "Puente de Mando (este)"},
        {"name": "sdk", "type": "lib", "status": "idea",
         "repo": "(pendiente)", "responsible": "—", "note": "futuro"},
        {"name": "plugins", "type": "ext", "status": "idea",
         "repo": "(pendiente)", "responsible": "—", "note": "futuro"},
        {"name": "website", "type": "web", "status": "propuesta",
         "repo": "(pendiente)", "responsible": "—", "note": "futuro"},
        {"name": "documentation", "type": "docs", "status": "propuesta",
         "repo": "(pendiente)", "responsible": "—", "note": "futuro"},
    ]


# ───────────────────────────────────────────────────────────── workspace/team
def workspace_state() -> dict:
    # v2b: workspace existe pero está vacío (borradores del equipo).
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    has = any(WORKSPACE.iterdir())
    return {"path": str(WORKSPACE), "exists": True, "has_drafts": has,
            "note": "borradores no oficiales; 'Promover' -> Git (futuro, Safety)"}


def team_state() -> dict:
    return {"members": ["Atlas", "Hermes", "Blanco", "Horizon Agent (futuro)"],
            "channels": ["#arquitectura", "#runtime", "#hq"],
            "note": "sala permanente del equipo; promover a ADR/Tarea/Principio/Informe"}


def meetings_state() -> dict:
    return {"fields": ["agenda", "conversación", "decisiones", "acciones"],
            "generates": "MEETING-AAAA-MM-DD.md",
            "note": "estructura lista; generación al guardar (futuro)"}


def settings_state() -> dict:
    return {
        "runtime": {"daemon": "spotify_player -d (systemd user)", "tests": "python3 tests/run_all.py"},
        "hq": {"theme": "dark", "accent": "#7C6CFF", "port": 8765},
        "horizon": {"status": "no implementado"},
        "providers": {"spotify": "reuse token (ADR-0008)"},
        "services": {"policy": "lectura hoy; control v2c con Safety"},
        "users": {"authorized": ["8581085602 (Blanco)"]},
        "auth": {"email": "gmail app password (.env)", "spotify": "existing credential"},
    }


# ───────────────────────────────────────────────────────────── shell
SHELL_COMMANDS = {
    "board": "listado de tablero por estado",
    "services": "estado de servicios (ecosystem/system)",
    "roadmap": "piezas activas",
    "report": "informes recientes",
    "freeze": "(futuro) congelar pieza — requiere Safety",
    "approve": "(futuro) aprobar ADR — requiere Safety",
    "help": "comandos disponibles",
}


def shell_dispatch(cmd: str) -> dict:
    """Horizon Shell: mapea comando a datos de la API (lectura)."""
    c = (cmd or "").strip().lower().split()[0] if cmd else ""
    if c in ("help", ""):
        return {"ok": True, "type": "help", "commands": SHELL_COMMANDS}
    if c == "board":
        code, data = v1_handle("/api/board")
        return {"ok": True, "type": "board", "data": data.get("sections", {})}
    if c == "services":
        return {"ok": True, "type": "services",
                "ecosystem": services_ecosystem(), "system": services_system()}
    if c == "roadmap":
        code, data = v1_handle("/api/roadmap")
        return {"ok": True, "type": "roadmap", "data": data.get("active", [])}
    if c == "report":
        code, data = v1_handle("/api/reports")
        return {"ok": True, "type": "reports", "data": data.get("reports", [])}
    return {"ok": False, "error": f"comando desconocido: {c}",
            "hint": "escribe 'help'"}


# ───────────────────────────────────────────────────────────── router
_ROUTES = {
    "/api/v2/content/state": lambda: v1_handle("/api/state")[1],
    "/api/v2/content/board": lambda: v1_handle("/api/board")[1],
    "/api/v2/content/adrs": lambda: v1_handle("/api/adrs")[1],
    "/api/v2/content/principles": lambda: v1_handle("/api/principles")[1],
    "/api/v2/content/reports": lambda: v1_handle("/api/reports")[1],
    "/api/v2/content/roadmap": lambda: v1_handle("/api/roadmap")[1],
    "/api/v2/workspace": workspace_state,
    "/api/v2/services": lambda: {"ecosystem": services_ecosystem(),
                                 "system": services_system()},
    "/api/v2/projects": lambda: {"projects": projects_list()},
    "/api/v2/team": team_state,
    "/api/v2/meetings": meetings_state,
    "/api/v2/settings": settings_state,
    "/api/v2/shell": lambda: {"ok": True, "commands": SHELL_COMMANDS},
}


def handle(path: str, query: str | None = None) -> tuple[int, dict]:
    # Shell acepta query ?cmd=...
    if path == "/api/v2/shell" and query:
        from urllib.parse import parse_qs
        cmd = parse_qs(query).get("cmd", [""])[0]
        return 200, {"ok": True, **shell_dispatch(cmd)}
    fn = _ROUTES.get(path)
    if fn is None:
        return 404, {"error": "not found", "path": path}
    try:
        return 200, {"ok": True, **fn()}
    except Exception as e:
        return 500, {"error": str(e)}
