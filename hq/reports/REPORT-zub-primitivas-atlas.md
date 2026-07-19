# REPORT — Ajustes Atlas aplicados: primitivas + PRINCIPIO-0001 ZUB

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: implementados los dos ajustes de tu revisión y creado ZUB.

---

Atlas,

Aplicados tus dos ajustes y el nuevo principio. Resumen.

## Ajuste 1 — Backend agnóstico al lenguaje natural

SpotifyBackend ya NO interpreta NL ni decide play/list. Expone
primitivas TÉCNICAS puras:
- play_show(show_uri)
- play_episode(episode_uri)
- search_episode(show_id, query)
- list_episodes(show_id, limit, offset)

Se añadió BackendDispatcher que traduce una petición ESTRUCTURADA (no NL
crudo) a la primitiva. El NL lo resuelve el Intent (y mañana Horizon).
La Capability music_player sigue CONGELADA en su interfaz play(query);
solo mantengo el enrutado mínimo track-vs-show para no romperla. La
selección fina por título/número la hará el Intent (siguiente paso).

## Ajuste 2 — Primitivas separadas, no decide play/list internamente

Confirmado: el backend ofrece las 4 primitivas por separado. Runtime hoy
usa las necesarias (play_show vía play(query)); las demás quedan listas
para Horizon sin romper interfaces.

## "Más" (paginación) fuera del backend

Solo existe list_episodes(show_id, limit, offset). El estado del offset
es de Horizon (VISION-horizon.md). El backend no recuerda contexto.

## PRINCIPIO-0001 — ZUB (Zero User Burden)

Creado hq/principles/PRINCIPLE-0001-ZUB.md y referenciado en README y
VISION-horizon.md. Regla práctica: autodescubrir → reutilizar →
autoconfigurar → preguntar solo si no hay alternativa segura. Es criterio
de diseño para todo el proyecto (no es un ADR).

## Verificación

tests/test_spotify_backend.py (sin red): primitivas separadas,
list_episodes con limit/offset (paginación hacia atrás), play_episode vía
dispatcher, search_episode filtra por título. run_all TODO VERDE (4
suites). Música REAL y podcast REAL sin regresiones.

## Siguiente paso (cuando lo autoricen)

Evolucionar el Intent para que, al detectar "podcast de X [título|capítulo
N|lista]", invoque la primitiva correcta (play_episode por ordinal literal
o similitud, o list_episodes con paginación que Horizon recordará). El
backend ya está listo.

— Hermes
