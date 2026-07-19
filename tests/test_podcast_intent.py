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
    captured = {}
    def _get(url):
        # list_episodes -> episodes; play -> 204
        if "episodes" in url:
            return {"ok": True, "data": {"items": episodes}}
        return {"ok": True}
    bk._api = lambda: mock.MagicMock(
        play_show=lambda u: {"ok": True, "message": f"show {u}"},
        play_episode=lambda u: {"ok": True, "message": f"ep {u}"},
        search_episode=lambda sid, q: [e for e in episodes if q.lower() in e["name"].lower()],
        list_episodes=lambda sid, lim, off: {"ok": True, "data": {"items": episodes[:lim]}},
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
    episodes = [{"name": f"Ep {n}", "uri": f"spotify:episode:E{n}"} for n in range(1, 31)]
    bk = _mock_backend(episodes)
    with mock.patch("src.core.capabilities.music_player._default_backend",
                    return_value=bk):
        # play_podcast por capítulo 24 -> play_episode del episodio 24.
        out = run("pon el capítulo 24 de monos estocasticos")
        ok_ep = "ep spotify:episode:E24" in out
        ok = ok and ok_ep
        print(f"  [{'OK ' if ok_ep else 'FAIL'}] capítulo 24 -> {out}")

        # play_podcast por título -> play_episode del más parecido.
        out2 = run("pon un podcast de monos estocasticos que se llama Ep 7")
        ok_t = "ep spotify:episode:E7" in out2
        ok = ok and ok_t
        print(f"  [{'OK ' if ok_t else 'FAIL'}] título 'Ep 7' -> {out2}")

        # list_podcast -> lista numerada.
        out3 = run("lista los capitulos de monos estocasticos")
        ok_l = "Ep 1" in out3 and "Ep 10" in out3 and "últimos 10" in out3
        ok = ok and ok_l
        print(f"  [{'OK ' if ok_l else 'FAIL'}] listado -> {out3[:60]!r}...")

    print("\nRESULTADO:", "TODO VERDE" if ok else "HAY FALLOS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
