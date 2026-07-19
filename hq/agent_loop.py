#!/usr/bin/env python3
"""Hermes Agent Loop — Hermes real conectado a Horizon HQ (HQ-003).

Proceso background que hace de Hermes dentro de la sala "Horizon Team":
  - sondea GET /api/v2/team/messages
  - ante un mensaje nuevo de Blanco (no de Hermes), invoca al motor REAL de
    Hermes (`hermes -z --safe-mode`, usa la credential de Nous ya configurada,
    gratuito) y postea la respuesta en la sala como Hermes.
  - NO ejecuta acciones: --safe-mode limita a razonamiento + texto.
  - NO escribe en git salvo promoción explícita del usuario desde la UI.

Fin del cartero: Blanco escribe solo en HQ; Hermes contesta solo en HQ.

Uso:  hq agent          (bucle 24/7; Ctrl+C para parar)
       hq agent --once  (una pasada, test)
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / "hq" / "workspace" / "agent_state.json"
API = "http://127.0.0.1:8765/api/v2/team"
POLL = 1.5  # segundos


def _http(method: str, path: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{API}{path}", data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read().decode())


def _load_seen() -> set[str]:
    if STATE.exists():
        try:
            return set(json.loads(STATE.read_text()).get("seen", []))
        except Exception:
            return set()
    return set()


def _save_seen(seen: set[str]):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"seen": sorted(seen)}))


SYSTEM = (
    "Eres Hermes, conectado a la sala 'Horizon Team' de Horizon HQ. "
    "Blanco (tu usuario) escribió en la sala. Responde de forma útil, "
    "concisa y en español (tú, singular). No uses markdown de botones. "
    "Si la petición requiere ejecutar acciones en su equipo, díselo y "
    "propón el paso, pero no inventes resultados."
)


def _hermes_think(text: str) -> str:
    """Invoca al motor real de Hermes (gratuito, credential Nous ya configurada)."""
    hermes = shutil.which("hermes")
    if not hermes:
        return "[Hermes] motor no disponible (hermes CLI no encontrado)."
    prompt = f"{SYSTEM}\n\nMensaje de Blanco:\n{text}\n\nRespuesta de Hermes:"
    try:
        r = subprocess.run(
            [hermes, "-z", prompt, "--safe-mode", "--cli"],
            capture_output=True, text=True, timeout=180,
        )
        out = (r.stdout or "").strip()
        if not out and r.stderr.strip():
            out = f"[Hermes] error motor: {r.stderr.strip()[:200]}"
        return out or "[Hermes] (sin respuesta del motor)"
    except subprocess.TimeoutExpired:
        return "[Hermes] tardé demasiado en responder; reintenta."
    except Exception as e:
        return f"[Hermes] fallo al invocar motor: {e}"


def loop(once: bool = False):
    seen = _load_seen()
    while True:
        try:
            msgs = _http("GET", "/messages").get("messages", [])
            nuevos = [m for m in msgs if m["id"] not in seen
                      and m["author"] != "Hermes"]
            for m in nuevos:
                seen.add(m["id"])
                resp = _hermes_think(m["text"])
                _http("POST", "/messages",
                      {"author": "Hermes", "text": resp, "parent_id": m["id"]})
                print(f"[agent] Blanco -> Hermes respondió ({len(resp)} chars)",
                      flush=True)
            _save_seen(seen)
        except Exception as e:
            print(f"[agent] error sondeo: {e}", flush=True)
        if once:
            break
        time.sleep(POLL)


def main():
    ap = argparse.ArgumentParser(description="Hermes Agent Loop (HQ Team, motor real)")
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    print("[agent] Hermes REAL conectado a Horizon Team. Fin del cartero.", flush=True)
    try:
        loop(once=args.once)
    except KeyboardInterrupt:
        print("\n[agent] detenido.")


if __name__ == "__main__":
    main()
