"""Executor: realiza la acción utilizando el proveedor adecuado.

En la Fase 1, music_player es una CAPABILITY REAL (delega en
spotify_player). El resto de capacidades permanece mock hasta que se
implementen (ADR-0003 / ADR-0004).
"""
from dataclasses import dataclass
from typing import Any

from ..action import Action
from ..capabilities.music_player import MusicPlayer
from ..capabilities.music_player.backends.spotify_player import BackendDispatcher


@dataclass
class ExecutionResult:
    success: bool
    message: str
    data: dict[str, Any] | None = None


def execute(action: Action) -> ExecutionResult:
    """Ejecuta la Action.

    - music_player: capability REAL (spotify_player hoy).
    - lo demás: mock (sin efecto).
    """
    if action.capability == "music_player":
        mp = MusicPlayer()
        t = action.type
        if t == "play_music":
            result = mp.play(action.params.get("query") or "")
        elif t == "pause_music":
            result = mp.pause()
        elif t == "resume_music":
            result = mp.resume()
        elif t == "next_track":
            result = mp.next()
        elif t == "previous_track":
            result = mp.previous()
        elif t == "set_volume":
            result = mp.volume(action.params.get("percent") or 50)
        elif t in ("play_podcast", "list_podcast"):
            # El Intent ya decidió y extrajo entidades. El Executor invoca
            # la primitiva correcta del backend vía BackendDispatcher
            # (ajuste Atlas: el backend no parsea NL). La Capability
            # music_player queda congelada; usamos su backend directamente.
            result = _execute_podcast(mp, action.params)
        else:
            result = {"ok": False, "message": f"Orden '{t}' no soportada."}
        return ExecutionResult(
            success=result.get("ok", False),
            message=result.get("message", ""),
            data=result,
        )

    # Mock para el resto de capacidades (no implementadas todavía).
    if action.capability not in _MOCK_CAPABILITIES:
        return ExecutionResult(
            success=False,
            message=f"Capacidad '{action.capability}' no disponible.",
        )
    return ExecutionResult(
        success=True,
        message=f"[MOCK] Ejecutando capacidad '{action.capability}' "
                f"para acción '{action.type}'. (Sin efecto real.)",
        data={"capability": action.capability, "type": action.type},
    )


_MOCK_CAPABILITIES = {"none"}


def _execute_podcast(mp: "MusicPlayer", params: dict) -> dict:
    """Resuelve la primitiva de podcast correcta (ajuste Atlas).

    El Intent ya decidió play_podcast/list_podcast y extrajo entidades
    (show_query, episode_title, episode_number, list). Aquí el Executor
    invoca la primitiva técnica del backend vía BackendDispatcher. La
    Capability music_player queda congelada.
    """
    backend = mp._backend
    disp = BackendDispatcher(backend)
    show_query = params.get("show_query") or ""
    show = backend.cli.search_show(show_query)
    if not show or not show.get("id"):
        return {"ok": False, "message": f"No encontré el podcast '{show_query}'."}
    show_id = show["id"]
    show_name = show.get("name", show_query)

    # Listado de episodios (los 10 últimos; "más" lo recordará Horizon).
    if params.get("list"):
        r = disp.dispatch({"kind": "list_episodes", "show_id": show_id,
                           "limit": 10, "offset": 0})
        if not r.get("ok"):
            return r
        items = r["data"]["items"]
        lines = [f"📋 {show_name} — últimos {len(items)} episodios:"]
        for i, e in enumerate(items, 1):
            name = e.get("name", "?")
            lines.append(f"  {i}. {name}")
        lines.append("(di 'pon el 7' o 'más' para seguir — Horizon recordará el offset)")
        return {"ok": True, "message": "\n".join(lines), "show_id": show_id}

    # Capítulo N (número LITERAL, regla de Blanco).
    if params.get("episode_number") is not None:
        n = int(params["episode_number"])
        # La API devuelve del más reciente al más viejo; el capítulo N
        # (orden de publicación, 1 = más antiguo) es el N-ésimo desde el
        # inicio => último de los N más recientes.
        r = disp.dispatch({"kind": "list_episodes", "show_id": show_id,
                           "limit": n, "offset": 0})
        if not r.get("ok"):
            return r
        items = r["data"]["items"]
        if len(items) < n:
            return {"ok": False,
                    "message": f"El podcast solo tiene {len(items)} episodios; no hay capítulo {n}."}
        ep = items[-1]
        return disp.dispatch({"kind": "play_episode",
                              "uri": ep["uri"]})

    # Título de episodio (el más parecido si hay typo).
    if params.get("episode_title"):
        title = params["episode_title"].lower()
        found = disp.dispatch({"kind": "search_episode",
                               "show_id": show_id, "query": title})["items"]
        if not found:
            return {"ok": False,
                    "message": f"No encontré un episodio que diga '{params['episode_title']}' en {show_name}."}
        # Más parecido: mayor ratio de coincidencia de substring.
        best = max(found, key=lambda e: _similarity(title, (e.get("name") or "").lower()))
        return disp.dispatch({"kind": "play_episode", "uri": best["uri"]})

    # Solo show: reproduce el show entero (último episodio).
    return disp.dispatch({"kind": "play_show", "uri": f"spotify:show:{show_id}"})


def _similarity(a: str, b: str) -> float:
    """Similitud simple por substring común (para título con typo)."""
    a, b = a.strip(), b.strip()
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.9
    # Cuenta palabras comunes.
    wa, wb = set(a.split()), set(b.split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)

