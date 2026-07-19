"""CLI: `runtime auth <provider>` (ADR-0007).

Flujo PKCE para app instalada (sin client_secret). Pertenece a Runtime,
NO a ninguna Capability.

El proveedor necesita el client_id del USUARIO (cada usuario registra su
propia Spotify App; Runtime no distribuye ninguna). Se lee de config de
Runtime (~/.config/runtime/config.toml) o se pide por terminal la primera
vez.

Pasos:
  1. Pedir client_id (si no está en config).
  2. Generar PKCE verifier/challenge + state.
  3. Mostrar la URL de autorización; el usuario la abre y copia el
     `code` de la redirección (http://localhost:8080/...?code=...).
  4. Intercambiar el code por tokens vía el ProviderAdapter.
  5. Guardar tokens por usuario (AuthManager).
"""
from __future__ import annotations

import base64
import os
import secrets
import urllib.parse

from . import AuthManager
from .provider import ProviderAdapter
from .providers import SpotifyProvider


def _pkce() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(
        __import__("hashlib").sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    return verifier, challenge


def _client_id(provider: ProviderAdapter) -> str:
    # Config mínima de Runtime: ~/.config/runtime/config.toml
    # [auth.spotify] client_id = "..."
    cfg = os.path.expanduser("~/.config/runtime/config.toml")
    if os.path.exists(cfg):
        try:
            import tomllib
            with open(cfg, "rb") as f:
                data = tomllib.load(f)
            cid = data.get("auth", {}).get(provider.name, {}).get("client_id")
            if cid:
                return cid
        except Exception:
            pass
    return input(f"client_id de tu app de {provider.name} (regístrala en "
                 "developer.spotify.com como app instalada): ").strip()


def run_auth(argv: list[str]) -> int:
    if not argv:
        print("Uso: runtime auth <provider>")
        print("Proveedores disponibles:", ", ".join(_manager().available()))
        return 1
    name = argv[0]
    mgr = _manager()
    try:
        provider = mgr.provider(name)
    except KeyError as e:
        print(e)
        return 1

    client_id = _client_id(provider)
    if not client_id:
        print("client_id vacío. Abortado.")
        return 1

    verifier, challenge = _pkce()
    state = secrets.token_urlsafe(16)
    redirect_uri = "http://127.0.0.1:8080/callback"

    url = provider.build_auth_url(
        client_id=client_id, redirect_uri=redirect_uri,
        state=state, code_challenge=challenge,
    )
    print("\nAbre esta URL en tu navegador y autoriza a Runtime:\n")
    print(url)
    print("\nUna vez autorizado, copia la URL completa a la que redirige")
    print("(debe empezar por http://127.0.0.1:8080/callback?code=...):\n")
    callback = input("URL de redirección: ").strip()

    q = urllib.parse.urlparse(callback).query
    params = urllib.parse.parse_qs(q)
    code = (params.get("code") or [None])[0]
    if not code:
        print("No se encontró 'code' en la URL. Abortado.")
        return 1

    tokens = provider.exchange_code(
        client_id=client_id, redirect_uri=redirect_uri,
        code=code, code_verifier=verifier,
    )
    if not tokens.get("access_token"):
        print("Fallo en la autenticación:", tokens.get("error_description", tokens))
        return 1

    mgr.store_tokens(name, client_id, tokens)
    print(f"\n✅ Autenticado con {name}. Token guardado en "
          f"~/.config/runtime/auth/{name}.json")
    return 0


def _manager() -> AuthManager:
    mgr = AuthManager()
    mgr.register(SpotifyProvider())
    return mgr


if __name__ == "__main__":
    import sys
    raise SystemExit(run_auth(sys.argv[1:]))
