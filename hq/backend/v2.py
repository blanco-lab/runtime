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
        {"name": "Horizon", "kind": "ecosystem",
         "status": _systemctl_active("hq-agent"),
         "note": "agente en sala Team (hq-agent.service)"},
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
import json as _json
import uuid as _uuid

TEAM_DIR = WORKSPACE / "team"
TEAM_FILE = TEAM_DIR / "horizon-team.jsonl"


def _team_ensure():
    TEAM_DIR.mkdir(parents=True, exist_ok=True)
    if not TEAM_FILE.exists():
        TEAM_FILE.write_text("", encoding="utf-8")


def _team_append(msg: dict):
    _team_ensure()
    with TEAM_FILE.open("a", encoding="utf-8") as f:
        f.write(_json.dumps(msg, ensure_ascii=False) + "\n")


def _team_read_all() -> list[dict]:
    _team_ensure()
    out = []
    for line in TEAM_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(_json.loads(line))
            except _json.JSONDecodeError:
                pass
    return out


def team_post(author: str, text: str, parent_id: str | None = None) -> dict:
    msg = {
        "id": _uuid.uuid4().hex[:12],
        "author": author or "Anónimo",
        "text": text,
        "parent_id": parent_id,
        "ts": int(time.time()),
        "read": False,
    }
    _team_append(msg)
    return msg


def team_list() -> list[dict]:
    return _team_read_all()


def team_mark_read(ids: list[str] | None = None):
    msgs = _team_read_all()
    changed = False
    for m in msgs:
        if ids is None or m["id"] in ids:
            if not m["read"]:
                m["read"] = True
                changed = True
    if changed:
        TEAM_FILE.write_text(
            "\n".join(_json.dumps(m, ensure_ascii=False) for m in msgs) + "\n",
            encoding="utf-8",
        )
    return {"ok": True, "marked": len(ids) if ids else "all"}


def workspace_state() -> dict:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    has = any(WORKSPACE.iterdir())
    return {"path": str(WORKSPACE), "exists": True, "has_drafts": has,
            "note": "borradores no oficiales; 'Promover' -> Git (Safety)"}


def team_state() -> dict:
    return {"members": ["Atlas", "Hermes", "Blanco", "Horizon Agent (futuro)"],
            "channels": ["Horizon Team (permanente)"],
            "note": "sala permanente del equipo; promover a ADR/Tarea/Principio/Informe/Decisión"}


# ───────────────────────────────────────────────────────────── promoter (Safety)
def _safe_commit(files: list[str], message: str) -> dict:
    """Write a Git bajo Safety: solo `git add <file>` + `git commit`.
    Sin shell=True, argumentos en lista. Nada fuera de HQ/."""
    try:
        subprocess.run(["git", "add", "--", *files], cwd=str(ROOT),
                       check=True, capture_output=True, text=True, timeout=15)
        r = subprocess.run(["git", "commit", "-m", message], cwd=str(ROOT),
                           capture_output=True, text=True, timeout=15)
        if r.returncode != 0:
            return {"ok": False, "error": r.stderr.strip() or "commit sin cambios"}
        return {"ok": True, "commit": (r.stdout + r.stderr).strip()[:200]}
    except subprocess.CalledProcessError as e:
        return {"ok": False, "error": e.stderr.strip()}


def team_promote(msg_id: str, target: str, by: str = "Hermes") -> dict:
    """Promueve un mensaje de Workspace a Git (Safety).
    target: adr | tarea | principio | informe | decision
    Crea el artefacto en hq/ y lo commitea (sin shell libre)."""
    msgs = _team_read_all()
    msg = next((m for m in msgs if m["id"] == msg_id), None)
    if not msg:
        return {"ok": False, "error": "mensaje no encontrado"}
    text = msg["text"]
    ts = time.strftime("%Y-%m-%d", time.localtime(msg["ts"]))
    author = msg["author"]
    body: str | None = None

    if target == "adr":
        slug = "ADR-" + _uuid.uuid4().hex[:4]
        path = HQ / "decisions" / f"{slug}-promoted.md"
        body = f"# {slug} (promovido desde Team)\n\n- De: {author} · {ts}\n- Estado: PROPUESTA\n\n{text}\n"
    elif target == "informe":
        slug = f"REPORT-promoted-{ts}"
        path = HQ / "reports" / f"{slug}.md"
        body = f"# REPORT (promovido desde Team)\n\n- De: {author} · {ts}\n\n{text}\n"
    elif target == "principio":
        slug = f"PRINCIPLE-promoted-{_uuid.uuid4().hex[:4]}"
        path = HQ / "principles" / f"{slug}.md"
        body = f"# {slug} (promovido desde Team)\n\n- De: {author} · {ts}\n\n{text}\n"
    elif target == "tarea":
        # Las tareas viven en el board.md (workspace oficial). Añade entrada.
        path = HQ / "board.md"
        body = None  # se maneja aparte
    elif target == "decision":
        slug = f"MEETING-DEC-{_uuid.uuid4().hex[:4]}"
        path = HQ / "decisions" / f"{slug}.md"
        body = f"# Decisión (promovida desde Team)\n\n- De: {author} · {ts}\n\n{text}\n"
    else:
        return {"ok": False, "error": f"target desconocido: {target}"}

    if target == "tarea":
        # Añade a board.md bajo EN CURSO sin reescribir todo
        _team_ensure()
        board = HQ / "board.md"
        line = f"\n[HQ-TASK-{_uuid.uuid4().hex[:4]}] {text}\n  dueño: {author}  estado: EN CURSO  origen: Team (promovido)\n"
        with board.open("a", encoding="utf-8") as f:
            f.write(line)
        res = _safe_commit([str(board.relative_to(ROOT))], f"task(HQ-003): promovido desde Team por {by}")
        return {"ok": True, "target": "tarea", "file": str(board), **res}

    path.parent.mkdir(parents=True, exist_ok=True)
    assert body is not None, "body requerido para promover (no tarea)"
    path.write_text(body, encoding="utf-8")
    rel = str(path.relative_to(ROOT))
    res = _safe_commit([rel], f"{target}(HQ-003): promovido desde Team por {by}")
    return {"ok": True, "target": target, "file": rel, **res}


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
    "/api/v2/team/messages": lambda: {"messages": team_list()},
    "/api/v2/meetings": meetings_state,
    "/api/v2/settings": settings_state,
    "/api/v2/shell": lambda: {"ok": True, "commands": SHELL_COMMANDS},
}


def handle_post(path: str, payload: dict) -> tuple[int, dict]:
    """POST /api/v2/team/* — escribir en Workspace (no en Git)."""
    if path == "/api/v2/team/messages":
        author = payload.get("author", "Anónimo")
        text = (payload.get("text") or "").strip()
        parent = payload.get("parent_id")
        if not text:
            return 400, {"ok": False, "error": "texto vacío"}
        msg = team_post(author, text, parent)
        return 200, {"ok": True, "message": msg}
    if path == "/api/v2/team/read":
        ids = payload.get("ids")
        res = team_mark_read(ids)
        return 200, res
    if path == "/api/v2/team/promote":
        msg_id = payload.get("msg_id")
        target = payload.get("target")
        by = payload.get("by", "Hermes")
        if not msg_id or not target:
            return 400, {"ok": False, "error": "msg_id y target requeridos"}
        res = team_promote(msg_id, target, by)
        code = 200 if res.get("ok") else 400
        return code, res
    return 404, {"error": "not found", "path": path}


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
