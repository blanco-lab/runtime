"""HQ Serve — servidor de la API interna + dashboard web (ADR-0011).

Arranca un http.server (stdlib) que:
  - expone /api/* (JSON) leyendo Git como fuente única (ver backend/).
  - sirve el dashboard web estático desde hq/web/ en "/".
El Dashboard NUNCA accede al FS: solo consume /api/*.

Uso:
  python3 hq/backend/serve.py [--port 8765] [--host 127.0.0.1]
O vía wrapper:  hq serve
"""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from hq.backend import handle as api_handle
from hq.backend import v2 as hq_v2

ROOT = Path(__file__).resolve().parents[2]  # repo root
WEB = ROOT / "hq" / "web"

_MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # silencioso
        pass

    def _send(self, code: int, body: bytes, ctype: str = "application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path.startswith("/api/v2/"):
            query = self.path.split("?", 1)[1] if "?" in self.path else None
            code, data = hq_v2.handle(path, query)
            self._send(code, json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return
        if path.startswith("/api/"):
            code, data = api_handle(path)
            self._send(code, json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return
        # Dashboard web (estático) — v2 es el Puente de Mando por defecto
        if path in ("/", ""):
            path = "/index-v2.html"
        f = WEB / path.lstrip("/")
        if not f.is_relative_to(WEB) or not f.is_file():
            self._send(404, b"not found", "text/plain")
            return
        ctype = _MIME.get(f.suffix, "application/octet-stream")
        self._send(200, f.read_bytes(), ctype)


def main(argv=None):
    ap = argparse.ArgumentParser(description="HQ Serve — Puente de Mando de Horizon")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args(argv)
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    print(f"HQ Serve escuchando en {url}")
    print("  API interna: /api/state /api/board /api/adrs /api/principles "
          "/api/reports /api/roadmap")
    print("  Dashboard:   abre el navegador en la URL arriba.")
    print("  Fuente única: git (hq/). Ctrl+C para detener.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nHQ Serve detenido.")
        httpd.shutdown()


if __name__ == "__main__":
    main(sys.argv[1:])
