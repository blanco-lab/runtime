#!/usr/bin/env python3
"""Test de la infra de autenticación de Runtime (ADR-0007).

Ejecuta:
    python3 tests/test_auth.py

Verifica la infra GENÉRICA (AuthManager + ProviderAdapter) y el adapter
de Spotify SIN tocar la red:
- AuthManager registra proveedores y lista disponibles.
- ProviderAdapter es la interfaz (Spotify la implementa).
- SpotifyProvider usa PKCE (supports_pkce) => sin client_secret.
- build_auth_url contiene los parámetros PKCE y el scope de playback.
- El flujo exchange/refresh delega en el adapter (probado con mock de red).
- AuthManager guarda/lee tokens por usuario y renueva si expiraron.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.auth import AuthManager
from src.core.auth.provider import ProviderAdapter
from src.core.auth.providers import SpotifyProvider


def _tmp_auth_dir(tmp: Path) -> AuthManager:
    mgr = AuthManager(auth_dir=tmp / "auth")
    mgr.register(SpotifyProvider())
    return mgr


class _FakeSpotify(SpotifyProvider):
    """Adapter que no hace red: simula exchange/refresh."""
    def exchange_code(self, *, client_id, redirect_uri, code, code_verifier):
        return {"access_token": "AT-" + code, "refresh_token": "RT-1",
                "expires_in": 3600}
    def refresh(self, *, client_id, refresh_token):
        return {"access_token": "AT-refreshed", "expires_in": 3600}


def main() -> int:
    import tempfile, time
    ok = True

    print("== AuthManager genérico ==")
    tmp = Path(tempfile.mkdtemp())
    mgr = AuthManager(auth_dir=tmp / "auth")
    mgr.register(_FakeSpotify())
    print("  disponibles:", mgr.available())
    ok = ok and mgr.available() == ["spotify"]

    print("\n== SpotifyProvider es ProviderAdapter y usa PKCE ==")
    sp = SpotifyProvider()
    print("  isinstance ProviderAdapter:", isinstance(sp, ProviderAdapter))
    print("  supports_pkce:", sp.supports_pkce)
    ok = ok and isinstance(sp, ProviderAdapter) and sp.supports_pkce

    print("\n== build_auth_url (PKCE, sin client_secret en URL) ==")
    url = sp.build_auth_url(client_id="CID", redirect_uri="http://x/cb",
                            state="ST", code_challenge="CH")
    print("  url:", url[:90], "...")
    checks = ("response_type=code" in url, "code_challenge=CH" in url,
              "code_challenge_method=S256" in url, "user-modify-playback-state" in url,
              "client_secret" not in url)
    ok = ok and all(checks)

    print("\n== flujo exchange + almacenamiento por usuario ==")
    mgr.store_tokens("spotify", "CID", mgr.provider("spotify").exchange_code(
        client_id="CID", redirect_uri="x", code="CODE123", code_verifier="V"))
    tok = mgr.get_token("spotify")
    print("  token guardado:", tok)
    ok = ok and tok == "AT-CODE123"
    print("  autenticado:", mgr.is_authenticated("spotify"))
    ok = ok and mgr.is_authenticated("spotify")

    print("\n== renovación automática al expirar ==")
    # Fuerza expiración escribiendo expires_at en el pasado.
    p = tmp / "auth" / "spotify.json"
    d = json.loads(p.read_text()); d["expires_at"] = time.time() - 10
    p.write_text(json.dumps(d))
    tok2 = mgr.get_token("spotify")
    print("  token tras refresco:", tok2)
    ok = ok and tok2 == "AT-refreshed"

    print("\nRESULTADO:", "TODO VERDE" if ok else "HAY FALLOS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
