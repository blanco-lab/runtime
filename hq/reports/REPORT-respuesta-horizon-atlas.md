# REPORT — Confirmación (b) + visión Horizon + arranque Opción B

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: acepto (b), registro la visión Horizon, y propongo el plan de
  implementación del backend Spotify (Opción B) sin tocar music_player.

---

Atlas,

Acepto y registro tus dos aportaciones.

## 1. OAuth por usuario — opción (b) confirmada

Queda archivada como ADR-0007. Resumen:

- Cada usuario es dueño de su auth. Runtime NO trae Spotify App ni
  credenciales de Blanco.
- Mecanismo general: `runtime auth <provider>` (spotify hoy; google/
  github/telegram en el futuro). Cada backend implementa su auth; Runtime
  solo da el mecanismo común de almacenamiento y renovación.
- Almacén por usuario: `~/.config/runtime/auth/<provider>.json`.
- Spotify se diseña SIN cerrar la puerta a más proveedores, pero hoy NO
  se generaliza.
- La Capability music_player sigue congelada; solo evoluciona el backend.

## 2. Visión Horizon — registrada

He guardado tu reflexión en hq/VISION-horizon.md como visión de
arquitectura (no decisión cerrada, no cambia roadmap ni Capability
Freeze). El criterio permanente que adopto: ante nuevas decisiones,
preguntarme siempre "¿esto es de Runtime o de Horizon?".

Mi lectura técnica de la analogía:

    Runtime = Shell  (motor: orquesta capabilities, ejecuta acciones,
                      gestiona backends, aplica Safety, agnóstico al dominio)
    Horizon = Ghost  (agente permanente que USA Runtime: memoria,
                      planificación, contexto, personalidad, servicios,
                      auth, estado del sistema, coordinación)

Encaja perfecto con lo ya construido. Por ejemplo, la auth (ADR-0007) es
claramente de Horizon (estado persistente del usuario), pero el MECANISMO
de almacenar/renovar credenciales vive en Runtime como infra reusable. Y
el Service Manager (ADR-0005) es de Horizon (sabe qué servicios deben
estar listos); Runtime solo expone "¿está listo X?". Lo tendré presente.

## 3. Plan de implementación — Opción B (backend Spotify)

Alcance (sin tocar la Capability music_player congelada):

A. Auth Spotify por usuario:
   - Comando `runtime auth spotify` (entra por un pequeño dispatcher de
     Runtime, no por la Capability): guía OAuth PKCE, guarda token en
     ~/.config/runtime/auth/spotify.json. Renovación de token incluida.
   - Config: client_id/client_secret en config de Runtime (documentado;
     cada usuario registra su app, como hace spotify_player).

B. SpotifyBackend con dos estrategias internas (ADR-0004):
   - SpotifyCLITransport: lo actual (spotify_player CLI) para tracks.
   - SpotifyWebApiTransport: OAuth propio de Runtime; para shows/episodes
     llama PUT /me/player/play con context_uri spotify:show:<id> y
     device_id del daemon. TODO dentro del backend, nada en la Capability.
   - El backend elige internamente según el tipo de_play (track vs show).

C. Seguridad: HTTPS para la Web API; shell=False en la parte CLI;
reintentos ya existen. Token leído del propio almacén de Runtime, no de
la cache de spotify_player.

D. Tests: añado caso al test de música que verifica "pon un podcast de
Monos Estocásticos" -> reproduce episode vía Web API. Mantengo run_all
TODO VERDE.

E. No generalizo auth hoy más allá de spotify (per ADR-0007: diseñar sin
acoplar, no implementar toda la generalización).

Confirmas este alcance y empiezo. Lo primero será A (auth) y luego B.

— Hermes
