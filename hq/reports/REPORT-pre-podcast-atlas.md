# REPORT — Diagnóstico podcasts + actualización spotify_player (pre-AR-00X)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: "Pon un podcast de Monos Estocásticos" -> intención no reconocida.
  Diagnóstico real, actualización de spotify_player, y petición de
  decisión de arquitectura para podcasts.

---

Atlas,

Blanco pidió esta mañana "pon un podcast de Monos Estocásticos" y
Runtime respondió "intención no reconocida". Investigué a fondo. Aquí
el diagnóstico con pruebas, no suposiciones.

## 1. Por qué lo rechazó

El Intent de music_player solo entiende reproducir CANCIONES (tracks).
Un podcast no es un track, es un show/episode. "Pon un podcast de X" no
entra en ninguna regla -> rechazo esperado. NO es un bug de Runtime.

## 2. El bloqueo real está en spotify_player, no en nuestro código

Lo verifiqué contra el CLI instalado:

- `spotify_player search "Monos Estocásticos"` SÍ devuelve el podcast
  (show "monos estocásticos", id 0yhXkn2DdZUC6XySGBgftC; 20 resultados).
  La búsqueda funciona.
- Pero `playback start context` solo acepta
  `context_type` en {playlist, album, artist}. NO incluye show/episode.
- Y `playback start track --id <episode_id>` -> 404 (los episodes no son
  tracks).

Conclusión: la API de Spotify SÍ permite reproducir podcasts
(context_uri spotify:show:ID), pero spotify_player NO lo expone en su
CLI. Por mucho que añadiera la intención en Runtime, no sonaría.

## 3. ¿Actualizar spotify_player arregla algo?

Subí v0.23.0 -> v0.24.0 (última release, jun 2026). Comprobado:

- v0.24.0 SIGUE sin aceptar show/episode en `playback start`. La
  limitación es de la propia herramienta, no de la versión.
- NOTA de impacto en infra: v0.24.0 cambió el modelo de daemon (el
  feature `daemon` ya no viene en default; hay que compilar con
  --features daemon). Lo gestioné: recompilé con el feature, daemon
  reactivado y active. Respaldo de v0.23.0 conservado.
- VERIFICACIÓN de no regresión: `python3 tests/run_all.py` -> TODO VERDE.
  music_player NO se tocó y sigue funcionando tras el cambio de versión.
  El contrato CLI (search / playback start track / pause) se mantuvo.

Decidimos con Blanco dejar spotify_player en v0.24.0 (música sigue
igual, sin tocar código).

## 4. Conclusión

Los podcasts NO se arreglan actualizando. Hace falta una decisión de
arquitectura. Como music_player está bajo Capability Freeze, la vía la
decides tú. Mis dos propuestas:

### Opción A — capability `podcast` (buscar + informar, sin reproducir)
Nueva capability que, dada una frase, busca el show/episode y devuelve
nombre + enlace + último episodio. NO reproduce (spotify_player no
puede). El usuario escucha desde la app. Útil ya, sin romper congelación
de música.

### Opción B — reproducción real vía Web API directa
Llamada directa a la Web API de Spotify (PUT /me/player/play con
context_uri spotify:show:ID) usando el token que ya guarda
spotify_player. Reproduciría el podcast de verdad desde Runtime.
Inconveniente: rompe la abstracción "todo va por el CLI spotify_player"
y hay que gestionar el token (leerlo del cache de spotify_player o usar
un client propio). Más potente, más superficie.

Mi recomendación: si el objetivo es que Runtime reproduzca podcasts de
verdad, Opción B. Si basta con descubrimiento + enlace, Opción A (más
simple y respetuosa con la congelación).

¿Cuál eliges? Si es B, necesito tu visto bueno para tocar la capa de
ejecución (y cómo obtener el token sin acoplarnos a los internos de
spotify_player).

— Hermes
