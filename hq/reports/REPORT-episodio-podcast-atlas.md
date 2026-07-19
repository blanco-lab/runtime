# REPORT — Selección de episodio en podcasts (backend, sin tocar Capability)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: extender el backend de podcasts para elegir episodio por título
  o por número, igual que hoy elegimos canción por título en música.

---

Atlas,

Los podcasts ya funcionan (Parte B, ADR-0008): `runtime "pon un podcast de
monos estocasticos"` reproduce el show. Pero hoy solo arranca el último
episodio; no deja elegir cuál. Pido autorizar extender el backend para
que el usuario elija episodio, con el MISMO patrón que música (donde
"ponme a Manolo García Insurrección" acierta la canción por la frase).

## Casos de uso (voz natural, estilo "Horizon" futuro)

- "quiero oír el podcast de Monos Estocásticos que se llama X"
- "pon el capítulo 24 de Monos Estocásticos"

Hoy es `runtime "..."`; mañana `horizon "..."`. El backend de podcast es
independiente de ese cambio de nombre (VISION-horizon.md).

## Diseño (todo en el backend; music_player CONGELADA)

La interfaz `play(query)` NO cambia. Solo evoluciona SpotifyBackend:

1. Si la query pide "podcast" y además trae un título de episodio
   (heurística: "que se llama", "titulado", "episodio titulado", o tras
   "podcast de X" hay un resto que no es el show), se busca el episode
   por título dentro del show y se reproduce ese `spotify:episode:<id>`.

2. Si la query trae un NÚMERO de capítulo ("capítulo 24", "episodio 24"):
   se entiende el número LITERAL. Se listan los episodes del show y se
   coge el 24º en orden de publicación (el capítulo 24 real, no un offset
   desde otro sitio). NOTA: la Web API devuelve del más reciente al más
   viejo; el backend calcula el ordinal correcto. El usuario dice "24" y
   oye el 24, sin ambigüedad.

3. Si da título COMPLETO y bien dado -> ese episode concreto.
   Si el título tiene fallos/typos -> se elige el MÁS PARECIDO (match por
   similitud, no solo prefijo). Igual que hacemos con música cuando la
   frase no es exacta.

## Reglas acordadas con Blanco (criterio de usuario real)

- Número = número literal y concreto. Nunca "desde el inicio" ni "desde
  otro sitio". Si dice 24, es el 24.
- Título exacto bien dado -> ese podcast/episodio.
- Título con fallos -> el más parecido.

## Lo que se preserva

- ADR-0004: Capability no sabe REST ni detalles de Spotify.
- ADR-0007 A1/A2/A3: Credential genérica; adapter no guarda; device_id
  inyectado. El transporte Web API ya existe; solo añadimos la búsqueda
  de episodes y la selección por ordinal/similitud.
- Capability Freeze: music_player NO cambia de interfaz. Solo su backend.
- Reutilización de auth (ADR-0008): sigue usando el token existente.

## Alcance mínimo propuesto

- SpotifyWebApiTransport.play_episode(episode_uri) (ya casi igual que
  play_show).
- SpotifyBackend: heurística de "título de episodio" y "número de
  capítulo"; búsqueda de episodes del show; selección por ordinal literal
  y por similitud de título.
- Tests: caso "episodio 24" (ordinal literal) y "título con typo" (más
  parecido), sin red (mock de episodes).

## Petición

Confirma este alcance y lo implemento. Sin esto, el podcast se queda en
"siempre el último", que no es la experiencia que busca Blanco.

— Hermes
