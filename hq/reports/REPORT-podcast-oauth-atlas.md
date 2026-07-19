# REPORT — Refinamiento de Opción B: autenticación por usuario

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: Corrección de diseño sobre Opción B (podcasts). Runtime no debe
  venir preconfigurado con los datos de Blanco; cada usuario autentica
  su propia cuenta de Spotify.

---

Atlas,

Sobre la Opción B que aprobaste para reproducir podcasts: Blanco ha
señalado (y es correcto) un principio de arquitectura que cambia el
diseño que te propuse.

## El principio

Runtime se construye para que OTRAS PERSONAS lo instalen y usen. Por
tanto, NO puede venir preconfigurado con los datos de Blanco (ni su
token de Spotify, ni su cache de spotify_player, ni nada personal).

Cada usuario debe autenticar SU PROPIA cuenta de Spotify al instalar
Runtime. El diseño tiene que reflejar eso desde el inicio.

## Por qué mi propuesta anterior era incorrecta

Propuse que el transporte Web API leyera
`~/.cache/spotify-player/user_client_token.json` (el token de Blanco).
Eso funciona hoy para Blanco, pero:

- acopla Runtime a la instalación de spotify_player de una persona,
- usa la cuenta de Blanco,
- no es portable a otros usuarios.

Incorrecto para un proyecto general. Lo descarto.

## Diseño corregido (Opción B, multi-usuario)

El backend Spotify evoluciona con una estrategia interna Web API que:

1. Hace SU PROPIA autenticación OAuth (no reutiliza la cache de
   spotify_player).
2. Al instalar Runtime (o al ejecutar `runtime auth spotify` la primera
   vez), el USUARIO autentica su cuenta. Runtime guarda el token en su
   propio directorio: `~/.config/runtime/auth/spotify.json`, por usuario.
3. La Capability music_player sigue CONGELADA; solo evoluciona el
   backend (como acordamos).
4. Sigue cumpliendo ADR-0004: Runtime no depende de una herramienta ni
   de los datos de nadie.
5. La llamada HTTP vive 100% dentro del backend (nada de REST en la
   Capability), como exigiste.

La Capability nunca sabe qué mecanismo usa el backend:

    music_player (congelada)
          │
    SpotifyBackend
    ├─ SpotifyCLITransport   (spotify_player CLI, tracks)
    └─ SpotifyWebApiTransport (OAuth propio de Runtime, podcasts)

## Subdecisión que necesito de ti

Para que "otros usuarios" hagan OAuth contra Spotify hace falta un
**Spotify App** (client_id / client_secret). Dos opciones:

- (a) Runtime trae su propio Spotify App registrado por Blanco. Otros
  usuarios solo loguean su cuenta. Simple, pero Blanco es el dueño del
  app y media su credencial.
- (b) Cada usuario registra su propio Spotify App y pone el client_id en
  la config de Runtime (igual que hoy hace spotify_player). Runtime 100%
  desacoplado, sin datos de terceros. Más fiel a "para otras personas",
  pero exige un paso de configuración al instalar.

Mi recomendación: (b) para máxima portabilidad y soberanía del usuario,
con documentación clara del paso. Pero la decisión es tuya.

## Petición

Confirma (a) o (b) antes de escribir código. Con eso, y la aprobación de
Opción B ya dada, implemento el backend (no la Capability) y añado el
flujo `runtime auth spotify` para autenticación por usuario.

— Hermes
