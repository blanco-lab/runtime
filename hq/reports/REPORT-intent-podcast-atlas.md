# REPORT — Intent evolucionado para podcasts (selección fina)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: el Intent ahora comprende "capítulo N" / "episodio titulado X"
  / "lista episodios" y decide la primitiva del backend. Cierre de la
  propuesta de selección de podcasts.

---

Atlas,

Cerrada la propuesta de selección/listado de podcasts. El Intent evoluciona
y el backend (ya con primitivas puras) se invoca correctamente.

## Qué hice (respetando tus ajustes)

1. Backend agnóstico al NL (ajuste 1 ya aplicado): el backend sigue
   exponiendo play_show/play_episode/search_episode/list_episodes. El
   Intent/Executor deciden cuál invocar.
2. El Intent ahora detecta play_podcast / list_podcast y extrae entidades:
   - show_query (nombre del podcast)
   - episode_number (capítulo N, LITERAL — regla de Blanco)
   - episode_title (si pide "que se llama X"; con typo -> el más parecido)
   - list (si pide "lista/muestra episodios")
3. El Executor resuelve la primitiva vía BackendDispatcher:
   - número N -> list_episodes(limit=N) y play_episode del N-ésimo.
   - título -> search_episode + el más parecido -> play_episode.
   - list -> list_episodes(limit=10) formateado; "más" lo recordará
     Horizon (estado fuera del backend).
   - solo show -> play_show.
4. La Capability music_player sigue CONGELADA: su interfaz no cambia; el
   Executor usa su backend directamente.

## Verificación REAL (ZUB: usuario no hizo nada nuevo; reusa token)

- "pon el capítulo 24 de monos estocasticos"
  -> Reproduciendo episodio: spotify:episode:78gVNusiv6R53EH5Ea0fDp
- "lista los capitulos de monos estocasticos"
  -> 📋 monos estocásticos — últimos 10 episodios: (títulos reales)

tests/test_podcast_intent.py (sin red): extracción de entidades y
resolución de primitiva (cap 24, título 'Ep 7', listado). run_all TODO
VERDE (5 suites). Música REAL sin regresiones.

## Valor (como anticipaste)

El usuario ya puede decir "pon el capítulo 24 de Monos Estocásticos" o
"lista los episodios", con el mismo patrón natural que "ponme a Manolo
García Insurrección". Y el backend quedó listo para Horizon (el "más"
paginado es su estado, no del backend).

— Hermes
