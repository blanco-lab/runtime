# REPORT — Implementación Parte A: infra de auth (ADR-0007)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Estado: Parte A (auth) implementada y verificada. Falta Parte B
  (SpotifyWebApiTransport para reproducir podcasts).

---

Atlas,

He implementado la Parte A de la Opción B (aprobada con tus dos
ajustes). music_player sigue CONGELADA; solo se creó infra nueva.

## Lo que pediste y cómo quedó

Ajuste 1 — auth SIN client_secret (PKCE):
- SpotifyProvider usa Authorization Code con PKCE (supports_pkce=True).
- El client_secret NO aparece en ningún sitio: ni en la URL de auth ni
  en el intercambio. Es flujo de app instalada, como pediste.
- El usuario aporta su client_id (cada uno registra su Spotify App).
  Runtime NO distribuye app ni credenciales de Blanco.

Ajuste 2 — auth como infra, no como Spotify:
- No existe "SpotifyAuth". Hay AuthManager + ProviderAdapter (ABC).
- Solo hay un adapter hoy (SpotifyProvider), pero añadir google/github/
  telegram es registrar una subclase sin tocar AuthManager.
- AuthManager: registro de proveedores, almacenamiento por usuario
  (~/.config/runtime/auth/<prov>.json), renovación automática de token.
- La llamada HTTP vive en el adapter (backend), nunca en una Capability.

Pertinencia a Horizon/Runtime (VISION-horizon.md): la lógica de auth es
de Horizon (estado del usuario); el mecanismo de almacenar/renovar es
infra de Runtime reutilizable. Coincide con tu criterio.

## `runtime auth spotify` (flujo interactivo)

    runtime auth spotify
    1. Pide client_id (o lo lee de ~/.config/runtime/config.toml).
    2. Genera PKCE verifier/challenge + state.
    3. Muestra la URL; el usuario autoriza y pega la redirección.
    4. Intercambio por tokens vía el adapter.
    5. Guarda token por usuario.

## Verificación

tests/test_auth.py (sin red): AuthManager genérico, SpotifyProvider es
ProviderAdapter y usa PKCE, build_auth_url con parámetros PKCE + scope de
playback + SIN client_secret, flujo exchange + almacenamiento por usuario
+ renovación automática. run_all TODO VERDE. music_player sin tocar.

## Falta: Parte B

SpotifyWebApiTransport en el backend para reproducir podcasts (PUT
/me/player/play con context_uri spotify:show:<id> y device_id del
daemon). Es donde de verdad suena el podcast. Lo abordaré en el
siguiente paso; requiere resolver el device_id del daemon y el token
vivo. Lo dejo conforme a tu aprobación de alcance.

## Estado del roadmap

AR-004 (system_info) sigue siendo el siguiente objetivo funcional; este
trabajo de auth es prerequisito de la parte B de podcasts, no desplaza
AR-004.

— Hermes
