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
    (show_query, episode_title, episode_number, latest, first, list). Aquí
    el Executor invoca la primitiva técnica del backend vía BackendDispatcher.
    La Capability music_player queda congelada.

    Orden de publicación (como en la web de Spotify):
    - capítulo 1 = el MÁS ANTIGUO.
    - capítulo N = el N-ésimo desde el inicio (el más viejo de los N más
      recientes).
    - "último" = el MÁS RECIENTE (offset 0 de la API).
    """
    backend = mp._backend
    disp = BackendDispatcher(backend)
    show_query = params.get("show_query") or ""
    show = backend.cli.search_show(show_query)
    if not show or not show.get("id"):
        return {"ok": False, "message": f"No encontré el podcast '{show_query}'."}
    show_id = show["id"]
    show_name = show.get("name", show_query)

    def _list_formatted() -> dict:
        """Lista los 10 últimos publicados (texto para el usuario + datos
        estructurados para Horizon). Runtime NO recuerda nada: el objeto
        se devuelve, no se almacena (ADR-0009 / frontera Runtime-Horizon)."""
        r = disp.dispatch({"kind": "list_episodes", "show_id": show_id,
                           "limit": 10, "offset": 0})
        if not r.get("ok"):
            return r
        total = r["data"].get("total", len(r["data"]["items"]))
        items = r["data"]["items"]
        episodes = [{"uri": e.get("uri"), "name": e.get("name", "?")} for e in items]
        lines = [f"📋 {show_name} — últimos {len(items)} episodios (de {total}):"]
        for i, e in enumerate(items, 1):
            lines.append(f"  {i}. {e.get('name', '?')}")
        lines.append(f'(para ir directo: runtime podcast "capítulo N de {show_name}" '
                     f'o "el episodio que se llama ...")')
        return {
            "ok": True,
            "message": "\n".join(lines),
            "show_id": show_id,
            # Objeto estructurado para Horizon (Runtime no lo guarda).
            "data": {
                "show_id": show_id,
                "show_name": show_name,
                "total": total,
                "offset": 0,
                "episodes": episodes,
            },
        }

    # Listado de episodios (los 10 últimos publicados; "más" lo recordará
    # Horizon). "Últimos" = del más reciente al más viejo (orden de la API).
    if params.get("list"):
        return _list_formatted()

    def _by_ordinal(n: int) -> dict:
        """Devuelve el episodio n-ésimo en orden de publicación (1 = más
        antiguo) usando el total real del show."""
        meta = disp.dispatch({"kind": "list_episodes", "show_id": show_id,
                              "limit": 1, "offset": 0})
        if not meta.get("ok"):
            return meta
        total = meta["data"].get("total", 0)
        if total == 0:
            return {"ok": False, "message": f"{show_name} no tiene episodios."}
        if n < 1 or n > total:
            return {"ok": False,
                    "message": f"{show_name} tiene {total} episodios; no hay capítulo {n}."}
        # Posición en la respuesta de la API (0=reciente). Capítulo 1 =
        # más antiguo = offset total-1.
        offset = total - n
        r = disp.dispatch({"kind": "list_episodes", "show_id": show_id,
                           "limit": 1, "offset": offset})
        if not r.get("ok"):
            return r
        ep = r["data"]["items"][0]
        return disp.dispatch({"kind": "play_episode", "uri": ep["uri"]})

    # "último/a" => episodio MÁS RECIENTE (offset 0).
    if params.get("latest"):
        r = disp.dispatch({"kind": "list_episodes", "show_id": show_id,
                           "limit": 1, "offset": 0})
        if not r.get("ok"):
            return r
        items = r["data"]["items"]
        if not items:
            return {"ok": False, "message": f"{show_name} no tiene episodios."}
        return disp.dispatch({"kind": "play_episode", "uri": items[0]["uri"]})

    # "primero/a" => episodio MÁS ANTIGUO = capítulo 1.
    if params.get("first"):
        return _by_ordinal(1)

    # Capítulo N (número LITERAL, regla de Blanco), por orden de publicación.
    if params.get("episode_number") is not None:
        return _by_ordinal(int(params["episode_number"]))

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

    # "podcast X" a secas -> lista para que elija (ZUB), no dispara a ciegas.
    return _list_formatted()


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

