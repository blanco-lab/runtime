#!/usr/bin/env python3
"""Test funcional de la capability music_player (batería de Atlas + bordes).

Verificación REAL: requiere spotify_player con device activo
(servicio spotify-player-daemon). Ejecuta:

    python3 tests/test_music_player.py

Comprueba que el pipeline reconoce y ejecuta correctamente las órdenes
de reproducción y control, y que rechaza lo desconocido/prohibido.
El reconocimiento de intención se valida siempre; la reproducción real
se valida si hay device de Spotify disponible.
"""
import sys
import time
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.intent import understand
from src.core.pipeline import run


def _has_spotify_device() -> bool:
    try:
        r = subprocess.run(
            ["spotify_player", "get", "key", "playback"],
            capture_output=True, text=True, timeout=15,
        )
        return r.returncode == 0
    except Exception:
        return False


# (frase, label esperado de Intent)
INTENT_CASES = [
    ("Pon Pájaros de Barro", "play_music"),
    ("Pon Fito y Fitipaldis", "play_music"),
    ("Pon Sabina", "play_music"),
    ("Pon Héroes del Silencio", "play_music"),
    ("Pon rock español", "play_music"),
    ("Pon música para dormir", "play_music"),   # 'para' no debe romperlo
    ("Pausa", "pause_music"),
    ("Stop", "pause_music"),
    ("Stop la música", "pause_music"),
    ("Parar", "pause_music"),
    ("Detener la música", "pause_music"),
    ("Apaga la música", "pause_music"),
    ("Continúa", "resume_music"),
    ("Siguiente canción", "next_track"),
    ("Canción anterior", "previous_track"),
    ("Volumen al 40%", "set_volume"),
    ("¿Qué tiempo hace?", "unknown"),
    ("Apaga el ordenador", "shutdown_system"),
]


def test_intents() -> bool:
    ok = True
    print("== Intent (siempre) ==")
    for frase, esperado in INTENT_CASES:
        got = understand(frase).label
        passed = got == esperado
        ok = ok and passed
        print(f"[{'OK ' if passed else 'FAIL'}] {frase!r} -> {got} (esperado {esperado})")
    return ok


def test_pipeline_real() -> bool:
    ok = True
    print("\n== Pipeline REAL (con device Spotify) ==")
    checks = [
        ("Pon Pájaros de Barro", "reproduciendo"),
        ("Pausa", "pausado"),
        ("Stop", "pausado"),
        ("Continúa", "reanudado"),
        ("Siguiente canción", "siguiente"),
        ("Volumen al 40%", "volumen 40%"),
        ("¿Qué tiempo hace?", "no se puede ejecutar"),
        ("Apaga el ordenador", "prohibida"),
    ]
    for frase, sub in checks:
        out = run(frase)
        passed = sub.lower() in out.lower()
        ok = ok and passed
        print(f"[{'OK ' if passed else 'FAIL'}] {frase!r} -> {out}")
        time.sleep(1.2)
    subprocess.run(["spotify_player", "playback", "pause"],
                  capture_output=True, timeout=10)
    return ok


if __name__ == "__main__":
    ok = test_intents()
    if _has_spotify_device():
        ok = test_pipeline_real() and ok
    else:
        print("\n[SKIP] Sin device de Spotify activo: se omite la parte REAL.")
    print("\nRESULTADO:", "TODO VERDE" if ok else "HAY FALLOS")
    sys.exit(0 if ok else 1)
