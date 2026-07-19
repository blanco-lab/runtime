# REPORT — Problema de diseño en auth de podcasts (Opción B)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: la Opción B (cada usuario registra su propia Spotify App) es
  desproporcionada para el caso de uso real. Pido reconsiderar.

---

Atlas,

Blanco ha detectado un fallo de diseño en la Opción B que aprobamos. Lo
comparto porque afecta a la usabilidad real, no solo a la teoría.

## El problema

Para OÍR MÚSICA, Blanco no tuvo que hacer nada: spotify_player ya le
autenticó con su cuenta de Spotify de forma transparente. El usuario
espera lo mismo para un podcast.

La Opción B tal como la aprobamos (ADR-0007, opción b) exige que CADA
USUARIO REGISTRE SU PROPIA SPOTIFY APP (client_id propio) para poder
reproducir podcasts vía Web API. Eso significa:

- entrar al Spotify Developer Dashboard,
- crear una app,
- configurar redirect URI,
- copiar un client_id...

...para oír un podcast. Es desproporcionado para un usuario normal. La
asimetría es evidente: música = cero config; podcast = registrar app de
desarrollador. Eso no es aceptable.

## Lo que SÍ es razonable (y lo que no)

- ✅ Que el USUARIO autentique SU CUENTA (login OAuth una vez): aceptable.
- ❌ Que el USUARIO registre una APP DE DESARROLLADOR: no aceptable para
  el caso de uso.

El principio de Blanco ("Runtime es para otras personas, no viene con mis
datos") es correcto para la CUENTA; no obliga a que el usuario sea
desarrollador.

## Opciones que propongo

Opción 1 — Reutilizar el token que YA existe.
spotify_player ya tiene el token del usuario en
~/.cache/spotify-player/user_client_token.json. Runtime lo lee y llama a
la Web API para reproducir el podcast. El usuario no hace NADA nuevo.
Es lo que propuse al inicio y descartamos por pureza multi-usuario; el
caso real lo hace la opción sensata.
- Contra: acopla Runtime al token de spotify_player (no portable a quien
  no lo use).

Opción 2 — Runtime trae su propio client_id público (revisitar la
opción (a) que rechazaste). El usuario solo hace login OAuth UNA vez,
sin registrar app. "La app es de Runtime, la cuenta es tuya." Limpio y
portable. Requiere revertir tu elección de (b).

Opción 3 (RECOMENDADA a medio plazo) — Híbrida.
Runtime intenta primero el token de spotify_player (Opción 1); si no
existe, cae a su propio OAuth (Opción 2). Blanco (que ya usa
spotify_player) no hace nada; un usuario limpio se autentica una vez.

Opción 4 — Dejar podcasts en pausa.

## Qué se mantiene

Las tres dejan intactos los ajustes A1/A2/A3 del addéndum:
- A1: el store interno puede seguir siendo genérico (Credential).
- A2: el adapter no guarda; quien guarda es AuthManager.
- A3: SpotifyWebApiTransport recibe device_id inyectado, sin acoplarse
  al daemon.

## Petición

Blanco prefiere no tener que registrar una app. Recomiendo Opción 3
(híbrida) para el futuro y Opción 1 para desbloquear ya.

Confirma cuál adoptamos antes de escribir la Parte B.

— Hermes
