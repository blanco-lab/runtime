#!/usr/bin/env python3
"""Hermes Agent Loop — Hermes real conectado a Horizon HQ (HQ-003).

Proceso background que hace de Hermes dentro de la sala "Horizon Team":
  - sondea GET /api/v2/team/messages
  - ante un mensaje nuevo de Blanco (no de Hermes), invoca al motor REAL de
    Hermes (`hermes -z --safe-mode`, usa la credential de Nous ya configurada,
    gratuito) y postea la respuesta en la sala como Hermes.
  - NO ejecuta acciones: --safe-mode limita a razonamiento + texto.
  - NO escribe en git salvo promoción explícita del usuario desde la UI.

Robusto: cualquier fallo se registra y el bucle sigue vivo (no crashea el
servicio). Logs en hq/workspace/agent.log (git-ignored).

Uso:  hq agent          (bucle 24/7; Ctrl+C para parar)
       hq agent --once  (una pasada, test)
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORKSPACE = REPO / "hq" / "workspace"
STATE = WORKSPACE / "agent_state.json"
LOG = WORKSPACE / "agent.log"
API = "http://127.0.0.1:8765/api/v2/team"
POLL = 5.0  # segundos
THINK_TIMEOUT = 240  # s (hermes -z gratis puede tardar; antes 150 daba timeouts)

logging.basicConfig(
    filename=str(LOG), level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("hq-agent")


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


def _build_context(msgs: list[dict], until_id: str) -> str:
    """Historial de la sala hasta el mensaje actual (memoria de conversación)."""
    # mensajes anteriores al actual, en orden cronológico
    prev = [m for m in msgs if m["id"] != until_id]
    prev = prev[-5:]  # ventana de contexto (5 mensajes, prompt ligero)
    lines = []
    for m in prev:
        who = "Blanco" if m["author"] != "Hermes" else "Hermes"
        lines.append(f"{who}: {m['text']}")
    return "\n".join(lines)


def _hermes_think(text: str, context: str = "") -> str:
    """Invoca al motor real de Hermes (gratuito, credential Nous ya configurada).

    Usa `bash -lc` para cargar el perfil COMPLETO de Blanco (no solo 3 vars),
    porque `hermes` necesita el entorno de login (auth Nous/keyring) que el
    daemon de systemd no tiene. El prompt va a un tempfile para evitar
    problemas de quoting.
    """
    hermes = shutil.which("hermes")
    if not hermes:
        return "[Hermes] motor no disponible (hermes CLI no encontrado)."
    hist = ""
    if context.strip():
        hist = "Historial de la conversación en la sala (de más antiguo a más reciente):\n" + context + "\n\n"
    prompt = (
        f"{SYSTEM}\n"
        f"Esta es una conversación CONTINUA en la sala; usa el historial "
        f"para no perder el hilo.\n{hist}"
        f"Mensaje actual de Blanco:\n{text}\n\nRespuesta de Hermes:"
    )
    # tempfile con el prompt (evita quoting frágil)
    tmp = WORKSPACE / f"prompt_{int(time.time()*1000)}.txt"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(prompt, encoding="utf-8")
    try:
        cmd = f'hermes -z "$(cat {tmp})" --safe-mode'
        r = subprocess.run(
            ["bash", "-lc", cmd],
            capture_output=True, text=True, timeout=THINK_TIMEOUT,
        )
        out = (r.stdout or "").strip()
        if not out:
            out = (r.stderr or "").strip().splitlines()
            out = [l for l in out if l and "warn" not in l.lower()][:1]
            out = out[0] if out else ""
        if not out:
            return "[Hermes] (sin respuesta del motor; reintenta)"
        return out
    except subprocess.TimeoutExpired:
        return "[Hermes] tardé demasiado en responder; reintenta."
    except Exception as e:
        log.exception("hermes_think falló")
        return f"[Hermes] falló al invocar motor: {e}"
    finally:
        try:
            tmp.unlink()
        except Exception:
            pass


def loop(once: bool = False):
    seen = _load_seen()
    while True:
        try:
            msgs = _http("GET", "/messages").get("messages", [])
            nuevos = [m for m in msgs if m["id"] not in seen
                      and m["author"] != "Hermes"]
            for m in nuevos:
                try:
                    # Pasa el historial de la sala (memoria de conversación),
                    # no solo el mensaje aislado, para que Hermes no "olvide"
                    # lo hablado entre iteraciones.
                    ctx = _build_context(msgs, m["id"])
                    resp = _hermes_think(m["text"], ctx)
                    _http("POST", "/messages",
                          {"author": "Hermes", "text": resp, "parent_id": m["id"]})
                    seen.add(m["id"])  # solo tras postear con éxito
                    log.info("Blanco -> Hermes respondió (%d chars)", len(resp))
                except Exception:
                    log.exception("error al responder mensaje %s", m["id"])
            _save_seen(seen)
        except Exception:
            log.exception("error en sondeo")
        if once:
            break
        time.sleep(POLL)


def main():
    ap = argparse.ArgumentParser(description="Hermes Agent Loop (HQ Team, motor real)")
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    log.info("Hermes REAL conectado a Horizon Team. Fin del cartero.")
    try:
        loop(once=args.once)
    except KeyboardInterrupt:
        log.info("detenido")


if __name__ == "__main__":
    main()
