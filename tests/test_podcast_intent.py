#!/usr/bin/env python3
"""Test de evolución del Intent + Executor para podcasts (sin red).

Verifica que el Intent extrae entidades (show/title/number/list) y que
el Executor invoca la primitiva correcta del backend vía BackendDispatcher
(ajuste Atlas: el backend no parsea NL; el Intent/Executor sí). La
Capability music_player queda congelada.

Ejecuta: python3 tests/test_podcast_intent.py
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.intent import understand
from src.core.pipeline import run
from src.core.capabilities.music_player import MusicPlayer
from src.core.capabilities.music_player.backends.spotify_player import (
    SpotifyBackend, BackendDispatcher,
)


def _mock_backend(episodes):
    """Backend mock: search_show devuelve show fijo; Web API devuelve episodes."""
    bk = SpotifyBackend()
    bk.cli.search_show = mock.MagicMock(
        return_value={"id": "SHOW1", "name": "Monos Estocásticos"})
    import re as _re
    def _lim_from_url(url):
        m = _re.search(r"limit=(\d+)", url)
        return int(m.group(1)) if m else 10
    def _get(url):
        # list_episodes -> episodes; play -> 204
        if "episodes" in url:
            return {"ok": True, "data": {
                "total": len(episodes),
                "items": episodes[:_lim_from_url(url)],
            }}
        return {"ok": True}
    bk._api = lambda: mock.MagicMock(
        play_show=lambda u: {"ok": True, "message": f"show {u}"},
        play_episode=lambda u: {"ok": True, "message": f"ep {u}"},
        search_episode=lambda sid, q: [e for e in episodes if q.lower() in e["name"].lower()],
        list_episodes=lambda sid, lim, off: {
            # Formato del transporte real: {items, total} (no anidado).
            "total": len(episodes),
            # La Web API devuelve del MÁS RECIENTE al más viejo; el mock
            # invierte para simular ese orden (episodes[0] = E1 más antiguo).
            "items": episodes[::-1][off:off + lim],
        },
    )
    return bk


def main() -> int:
    ok = True
    print("== Intent: extracción de entidades de podcast ==")
    cases = [
        ("pon un podcast de monos estocasticos", "play_podcast", {"show_query": "monos estocasticos"}),
        ("pon el capítulo 24 de monos estocasticos", "play_podcast", {"episode_number": 24}),
        ("quiero oir el podcast de monos estocasticos que se llama atom y la red",
         "play_podcast", {"episode_title": "atom y la red"}),
        ("ponme el ultimo (es decir el ultimo publicado) capitulo de monos estocasticos",
         "play_podcast", {"latest": True, "show_query": "monos estocasticos"}),
        ("podcast monos estocasticos", "list_podcast", {"show_query": "monos estocasticos"}),
        ("lista los capitulos de monos estocasticos", "list_podcast", {}),
        ("pon musica de manolo garcia insurreccion", "play_music", {}),
    ]
    for frase, label, must in cases:
        i = understand(frase)
        passed = (i.label == label)
        for k, v in must.items():
            passed = passed and i.entities.get(k) == v
        ok = ok and passed
        print(f"  [{'OK ' if passed else 'FAIL'}] {frase!r} -> {i.label} {i.entities}")
    # Música no debe confundirse con podcast.
    ok = ok and understand("pon musica de manolo garcia").label == "play_music"

    print("\n== Executor: resuelve primitiva correcta (sin red) ==")
    episodes = [{"name": f"Ep {n}", "uri": f"spotify:episode:E{n}", "id": f"E{n}"}
                for n in range(1, 31)]
    bk = _mock_backend(episodes)
    with mock.patch("src.core.capabilities.music_player._default_backend",
                    return_value=bk):
        # play_podcast por capítulo 24 -> episodio 24 (ordinal real, no el
        # primero de la lista). episodes[23] = "Ep 24".
        out = run("pon el capítulo 24 de monos estocasticos")
        ok_ep = "ep spotify:episode:E24" in out
        ok = ok and ok_ep
        print(f"  [{'OK ' if ok_ep else 'FAIL'}] capítulo 24 -> {out}")

        # play_podcast por "último publicado" -> episodio MÁS RECIENTE
        # (offset 0 = E30), NO el primero de la lista (E1).
        out4 = run("ponme el ultimo (es decir el ultimo publicado) capitulo de monos estocasticos")
        ok_last = "ep spotify:episode:E30" in out4 and "E1" not in out4.split("ep ")[-1]
        ok = ok and ok_last
        print(f"  [{'OK ' if ok_last else 'FAIL'}] último publicado -> {out4}")

        # "podcast X" a secas -> lista (ZUB: no dispara a ciegas).
        out5 = run("podcast monos estocasticos")
        # Mock de 30 episodes: la lista (más recientes primero) es E30..E21.
        ok_bare = "últimos" in out5 and "Ep 30" in out5 and "ep spotify" not in out5
        ok = ok and ok_bare
        print(f"  [{'OK ' if ok_bare else 'FAIL'}] podcast X a secas -> lista")

        # play_podcast por título -> play_episode del más parecido.
        out2 = run("pon un podcast de monos estocasticos que se llama Ep 7")
        ok_t = "ep spotify:episode:E7" in out2
        ok = ok and ok_t
        print(f"  [{'OK ' if ok_t else 'FAIL'}] título 'Ep 7' -> {out2}")

        # list_podcast -> lista numerada (más recientes primero: E30..E21).
        out3 = run("lista los capitulos de monos estocasticos")
        ok_l = "Ep 30" in out3 and "Ep 21" in out3 and "últimos" in out3
        ok = ok and ok_l
        print(f"  [{'OK ' if ok_l else 'FAIL'}] listado -> {out3[:60]!r}...")

        # El resultado del listado debe ser estructurado para Horizon y
        # Runtime no debe guardar nada en disco (ADR-0009).
        import os
        res = run("lista los capitulos de monos estocasticos")
        # run() devuelve texto; verificamos el objeto vía Executor directo.
        from src.core.executor import execute
        from src.core.action import build
        from src.core.intent import understand as _u
        ex = execute(build(_u("lista los capitulos de monos estocasticos").label,
                            _u("lista los capitulos de monos estocasticos")))
        structured = ex.data.get("data") if ex.data else None
        ok_struct = (structured and structured.get("show_id") == "SHOW1"
                     and structured.get("offset") == 0
                     and "episodes" in structured)
        ok = ok and ok_struct
        print(f"  [{'OK ' if ok_struct else 'FAIL'}] objeto estructurado para Horizon -> {bool(structured)}")
        # Runtime no debe haber creado caché de podcast.
        cache_dir = Path.home() / ".cache" / "runtime"
        ok_nocache = not (cache_dir / "last_podcast.json").exists()
        ok = ok and ok_nocache
        print(f"  [{'OK ' if ok_nocache else 'FAIL'}] Runtime no guarda caché de podcast")

    print("\nRESULTADO:", "TODO VERDE" if ok else "HAY FALLOS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
