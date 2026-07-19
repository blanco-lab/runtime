#!/usr/bin/env python3
"""Test del backend Spotify evolucionado (Parte B / ADR-0008).

Verifica SIN red:
- El backend elige transporte según tipo de _play (track vs show).
- Para podcast usa SpotifyWebApiTransport con token + device_id inyectados
  (ADR-0007 A3: device_id desacoplado, no sabe origen).
- Resolución de credencial (ADR-0008): ExistingCredentialProvider reusa
  token existente; si no hay, RuntimeCredentialProvider (AuthManager).
- La Capability music_player queda CONGELADA: su interfaz play(query) no
  cambia.

Ejecuta: python3 tests/test_spotify_backend.py
"""
import json
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.capabilities.music_player.backends.spotify_player import SpotifyBackend
from src.core.capabilities.music_player.backends.transports import (
    SpotifyCLITransport, SpotifyWebApiTransport,
)
from src.core.auth.credentials import (
    Credential, ExistingCredentialProvider, RuntimeCredentialProvider,
    resolve_credential,
)


def _fake_cli_with_show():
    """CLI mock: search_show devuelve un show; search_track None."""
    cli = mock.MagicMock(spec=SpotifyCLITransport)
    cli.search_show.return_value = {"id": "SHOW123", "name": "Monos Estocásticos"}
    cli.search_track.return_value = None
    return cli


def _fake_http_put(captured):
    """Simula urllib.request.urlopen para PUT /me/player/play."""
    def _fake(req, timeout=20):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.headers)
        captured["data"] = req.data
        # Respuesta OK (204 No Content en Web API de play).
        resp = mock.MagicMock()
        resp.status = 204
        resp.read.return_value = b""
        return resp
    return _fake


def main() -> int:
    ok = True

    print("== Backend elige transporte según tipo ==")
    cap = {}
    backend = SpotifyBackend()
    backend.cli = _fake_cli_with_show()
    backend._token_resolver = lambda: "TOK"
    backend._device_resolver = lambda: "DEV"
    captured = {}
    backend._http = _fake_http_put(captured)
    res = backend.play("pon un podcast de monos estocasticos")
    print("  respuesta:", res)
    ok = ok and res.get("ok") is True
    ok = ok and res.get("show_uri") == "spotify:show:SHOW123"
    # Verifica que la Web API se llamó con Bearer token y device_id.
    ok = ok and "DEV" in captured["url"]
    ok = ok and captured["headers"].get("Authorization") == "Bearer TOK"
    body = json.loads(captured["data"])
    ok = ok and body.get("context_uri") == "spotify:show:SHOW123"
    print("  [OK]" if ok else "  [FAIL]", "podcast vía Web API con token+device")

    print("\n== device_id desacoplado (None -> URL sin device_id) ==")
    backend2 = SpotifyBackend()
    backend2.cli = _fake_cli_with_show()
    backend2._token_resolver = lambda: "TOK"
    backend2._device_resolver = lambda: None  # viene de donde sea, hoy None
    cap2 = {}
    backend2._http = _fake_http_put(cap2)
    backend2.play("podcast x")
    ok = ok and "device_id" not in cap2["url"]
    print("  [OK]" if ok else "  [FAIL]", "device_id opcional (inyectado, no acoplado)")

    print("\n== Resolución de credencial (ADR-0008) ==")
    # Existing reusa token de spotify_player (mock de archivo).
    import tempfile
    d = Path(tempfile.mkdtemp()) / "user_client_token.json"
    d.write_text(json.dumps({"access_token": "EXISTING_TOK", "expires_at": 9999999999}))
    ecp = ExistingCredentialProvider(cache_path=d)
    cred = ecp.resolve()
    ok = ok and cred is not None and cred.token == "EXISTING_TOK"
    print("  [OK]" if ok else "  [FAIL]", "ExistingCredentialProvider reusa token")

    # Sin archivo -> Existing devuelve None; Runtime lo resuelve (mock).
    empty = Path(tempfile.mkdtemp()) / "x.json"
    empty.write_text("{}")
    ecp2 = ExistingCredentialProvider(cache_path=empty)
    mgr = mock.MagicMock()
    mgr.get_token.return_value = "RUNTIME_TOK"
    rcp = RuntimeCredentialProvider(mgr, "spotify")
    cred2 = resolve_credential(ecp2, rcp)
    ok = ok and cred2 is not None and cred2.token == "RUNTIME_TOK"
    print("  [OK]" if ok else "  [FAIL]", "fallback a RuntimeCredentialProvider")

    print("\n== Credential genérica (ADR-0007 A1: Auth ≠ OAuth) ==")
    c = Credential(token="X", metadata={"source": "test"})
    ok = ok and c.token == "X"
    print("  [OK]" if ok else "  [FAIL]", "Credential no acoplada a OAuth")

    print("\nRESULTADO:", "TODO VERDE" if ok else "HAY FALLOS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
