# REPORT — Parte B completa: podcasts vía Web API (ADR-0008)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: Parte B implementada y verificada REAL. El usuario no tuvo que
  hacer nada nuevo (reusa su token de spotify_player).

---

Atlas,

Parte B terminada y funcionando. Resumen de lo hecho y la verificación.

## Lo que pediste y cómo quedó

Política ADR-0008 (reutilizar auth existente antes de pedir nueva):
- CredentialProvider (ABC) + Credential genérica (A1: Auth ≠ OAuth).
- ExistingCredentialProvider: reusa el token de spotify_player. NO guarda
  nada (cumple A2: la persistencia no se reparte en adapters; solo LEE).
- RuntimeCredentialProvider: usa AuthManager (PKCE) si no hay credencial
  previa.
- resolve_credential: intenta Existing -> si None, Runtime. Vive en la
  infra de auth, NO en el backend.

Backend Spotify (evolución, Capability music_player CONGELADA):
- Dos transportes internos (ADR-0004): SpotifyCLITransport (tracks, CLI
  actual) y SpotifyWebApiTransport (podcasts, Web API).
- SpotifyWebApiTransport recibe token y device_id INYECTADOS (A3: device_id
  desacoplado, no sabe de dónde procede). La Capability no conoce REST.
- El backend elige transporte por tipo de _play: si la query dice
  "podcast" -> show; si no -> track (música), y solo cae a show si no hay
  track.
- spotify_player NO es requisito permanente: es el primer
  ExistingCredentialProvider, como acordamos.

## Verificación

REAL (sin que el usuario hiciera nada nuevo):
    runtime "pon un podcast de monos estocasticos"
    -> Reproduciendo podcast: monos estocásticos
       (spotify:show:0yhXkn2DdZUC6XySGBgftC)

tests/test_spotify_backend.py (sin red): enrutado track vs show, token +
device inyectados, device_id opcional/desacoplado, resolución ADR-0008
(Existing reusa, fallback a Runtime), Credential genérica.

run_all TODO VERDE (4 suites): command_runner, music_player (REAL, Pájaros
de Barro / Paganini vía CLI intactos), auth, spotify_backend. Sin
regresiones en música.

## Valor (como anticipaste)

No solo añadimos podcasts: creamos la infra de autenticación reutilizable
para todos los proveedores futuros (AuthManager, ProviderAdapter, PKCE,
CredentialProvider, Existing/Runtime). Esto vale más que Spotify en sí.

## Estado del roadmap

music_player sigue congelada (solo evolucionó su backend, como dijiste).
AR-004 (system_info) sigue siendo el siguiente objetivo funcional.

— Hermes
