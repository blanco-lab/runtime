#!/usr/bin/env python3
"""Hermes Agent Loop — conecta a Horizon HQ (HQ-003).

Proceso background que hace de Hermes dentro de la sala "Horizon Team":
  - sondea GET /api/v2/team/messages
  - responde a los mensajes nuevos de Blanco (no de Hermes) posteando como Hermes
  - NO escribe en git salvo promoción explícita (la hace el usuario desde la UI)

Principio ZUB: un solo sitio de trabajo. Blanco escribe en HQ; Hermes responde
en HQ. El cartero desaparece.

Uso:  hq agent            (arranca el bucle; Ctrl+C para parar)
       hq agent --once    (una pasada, útil para test)

No requiere APIs de pago. 100% local/gratuito.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / "hq" / "workspace" / "agent_state.json"
API = "http://127.0.0.1:8765/api/v2/team"
POLL = 3.0  # segundos


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


def _respond(text: str) -> str:
    """Criterio de Hermes. Por ahora: acuse + eco con personalidad.
    Aquí es donde en el futuro entraría el razonamiento real de Hermes
    (esta sesión). Hoy devuelve una respuesta útil y honesta."""
    t = text.strip().lower()
    if any(k in t for k in ["hola", "buenas", "hey"]):
        return "Hermes por aquí. Recibido en la sala. ¿En qué trabajamos?"
    if "cartero" in t:
        return "El cartero es historia: lees y escribes solo en Horizon HQ. Yo contesto aquí."
    return f"Entendido, Blanco. Anotado en la sala: «{text[:80]}». Dime y actúo."


def loop(once: bool = False):
    seen = _load_seen()
    while True:
        try:
            d = _http("GET", "/messages")
            msgs = d.get("messages", [])
            nuevos = [m for m in msgs if m["id"] not in seen
                      and m["author"] != "Hermes"]
            for m in nuevos:
                seen.add(m["id"])
                resp = _respond(m["text"])
                _http("POST", "/messages",
                      {"author": "Hermes", "text": resp, "parent_id": m["id"]})
                print(f"[agent] Blanco escribió -> Hermes respondió en sala",
                      flush=True)
            _save_seen(seen)
        except Exception as e:
            print(f"[agent] error sondeo: {e}", flush=True)
        if once:
            break
        time.sleep(POLL)


def main():
    ap = argparse.ArgumentParser(description="Hermes Agent Loop (HQ Team)")
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    print("[agent] Hermes conectado a Horizon Team. Fin del cartero.", flush=True)
    try:
        loop(once=args.once)
    except KeyboardInterrupt:
        print("\n[agent] detenido.")


if __name__ == "__main__":
    main()
