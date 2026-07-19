# ADR-0009 — Frontera Runtime/Horizon: Runtime es estrictamente stateless

- Estado: APROBADO (Atlas, 2026-07-19)
- Contexto: surgió al implementar la lista de episodios de podcasts.
  Blanco probó `runtime podcast monos estocasticos` (lista 10 últimos) y
  luego `pon el 1`, que falla porque Runtime no recuerda el show listado.
- Decisión: Runtime NO almacena estado conversacional de ningún tipo.
  No guarda: último podcast, último show, último offset, última
  conversación, ni siquiera como "puente temporal".
- Motivo (Atlas): "pon el 1" tras un listado no son dos comandos, es una
  conversación; las conversaciones pertenecen a Horizon. Si Runtime
  empieza recordando el último podcast, deriva hacia reconstruir Horizon
  dentro de Runtime. Se rechaza explícitamente la Opción A propuesta por
  Hermes.
- Consecuencia para el listado de podcasts: Runtime imprime la lista, y
  ADEMÁS devuelve un objeto estructurado `{show_id, show_name, total,
  offset, episodes:[{uri,name}]}` en el resultado, para que Horizon lo
  consuma y recuerde. Runtime NO persiste ese objeto.
- Flujo correcto mientras Horizon no exista (Atlas): repetir la frase
  completa, p.ej. `runtime podcast "capítulo 7 de monos estocásticos"` o
  `runtime podcast "el episodio que se llama ..."`.
- El backend sigue exponiendo primitivas limpias (search_show,
  list_episodes(show_id, limit, offset), play_episode, play_show) sin
  memoria, sin contexto, sin lenguaje natural.
- Relacionado: PRINCIPIO-0001 (ZUB), VISION-horizon.md, ADR-0004
  (Capability/Backend), ADR-0008 (reutiliza auth).
