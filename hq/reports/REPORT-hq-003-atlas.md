# REPORT — HQ-003 "Team Communication" (fin del cartero)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: implementada comunicación del equipo en HQ. Sala permanente
  "Horizon Team" con escritura/lectura/respuesta/marcar leído y promoción
  a ADR/Tarea/Principio/Informe/Decisión vía Workspace→Git (Safety).

---

Atlas,

Implementado HQ-003 según tu veredicto. Objetivo: eliminar al cartero.

LO CONSTRUIDO
- Vista TEAM funcional (no placeholder): sala permanente "Horizon Team",
  siempre abierta.
- Escribir / Leer / Responder / Marcar leídos: mensajes en
  hq/workspace/team/horizon-team.jsonl (git-ignored). La interfaz NO sabe
  dónde viven; usa la API.
- Promover desde la conversación (botones por mensaje) a:
  ADR · Tarea · Principio · Informe · Decisión.
  Al promover: Workspace → Git mediante Safety (solo `git add` + `git
  commit` del archivo creado, sin shell libre). El artefacto queda en
  hq/decisions|reports|principles|board.md.

PRINCIPIOS RESPETADOS
- "La interfaz nunca conoce dónde viven los datos; solo la API" (ADR-0013).
  El frontend consume /api/v2/team/*; no toca FS.
- Workspace (borrador) → Git (oficial) bajo Safety, exactamente como
  pediste.
- Runtime congelado. HQ evoluciona por uso real.

BACKEND
- hq/backend/v2.py: team_post/list/mark_read + team_promote (Safety:
  _safe_commit con argumentos en lista, sin shell=True).
- hq/backend/serve.py: do_POST para /api/v2/team/* (mensajes/read/promote)
  + CORS. GET intacto.
- Frontend index-v2.html: vista TEAM con composer + tarjetas de mensaje +
  acciones de promoción. Estética ZUB.

VERIFICACIÓN
- run_all: 7 suites VERDE (test_hq_v2 ampliado cubre HQ-003: mensaje
  round-trip en workspace + promover a ADR crea archivo y commitea en git,
  y a tarea añade a board.md; ambos revertidos en el test para no ensuciar).
- Servidor en vivo: POST mensaje (Blanco/Atlas) → 200; GET mensajes → 200
  con los mensajes; archivo horizon-team.jsonl creado en workspace
  (git-ignored). Promoción validada en test con commit real.
- Repo limpio: sin rastros de prueba (workspace y artefactos de test
  eliminados/deshechos).

OBJETIVO ALCANZADO
Cuando HQ-003 esté en uso: Blanco abre HQ, Hermes escribe allí, Atlas
responde allí, y cualquier mensaje se promueve a ADR/Tarea/Principio/
Informe/Decisión sin que Blanco transporte texto manualmente. El cartero
queda eliminado de la fricción cotidiana.

FORMA DE TRABAJO: v2b en USO REAL; HQ-003 en prueba inmediata (como pediste:
"cuando funcione, lo probaremos inmediatamente").

— Hermes

