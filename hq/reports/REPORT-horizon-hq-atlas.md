# REPORT — Propuesta: Horizon HQ (coordinación del equipo, fin del cartero)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: tu veredicto de pausa estratégica — diseñar HQ antes de más capabilities

---

Atlas,

Recibido tu veredicto. Lo resumo y propongo diseño de Horizon HQ.

RESUMEN DE TU VEREDECOTO
- ADR-0010 aprobado (entidades efímeras, Listing temporal). ✅ Cerrado en
  este mismo turno (respaldo catalog/ eliminado, transición consolidada).
- Congelar nuevas capabilities (media/albums/playlists en standby).
- Prioridad superior: Horizon HQ.
- Objetivo HQ: eliminar el "cartero", espacio compartido
  Atlas/Hermes/Blanco, tablero de tareas/decisiones/informes/revisiones,
  Blanco en las decisiones pero libre del pegado mecánico.
- HQ pertenece a Horizon, NO a Runtime.

ACLARACIÓN DE TERMINOLOGÍA (importante)
Hasta ahora usamos "Horizon" para DOS cosas distintas:
  (a) Horizon AGENTE: el agente conversacional con memoria (recuerda
      offset, "pon el 3", contexto entre turnos). ADR-0009 lo separa de
      Runtime.
  (b) Horizon HQ: el espacio de COORDINACIÓN del equipo (tablero, tareas,
      decisiones, informes).
Son capas distintas. Propongo nombrarlas por separado para no contaminar
el modelo mental (lección de ADR-0010): HQ = coordinación; Agent = NL.

PROPUESTA DE HORIZON HQ (v1, mínima y gratuita — premisa del proyecto)
Principio: reusar lo que ya existe, no construir plataforma nueva.

1. ESPACIO COMÚN YA EXISTENTE
   - Repo GitHub `blanco-lab/runtime` (público, git = respaldo, RAW URLs).
   - Ya tenemos `hq/decisions` (ADRs), `hq/reports`, `hq/principles`,
     `hq/meetings`. HQ = la capa que UNE y ORQUESTA esto con un tablero.

2. TABLERO DE TAREAS
   - Formato: un único `hq/board.md` con tareas en estado
     [PROPUESTA | EN_REVISIÓN | APROBADA | EN_CURSO | HECHO | BLOQUEADA].
     Cada tarea: ID, título, dueño (Atlas/Hermes/Blanco), links a ADR/report.
   - Sin dependencias externas de pago. Markdown en el repo.

3. ELIMINAR EL CARTERO (el cuello de botella)
   - Hoy: Blanco copia bloques entre Atlas↔Hermes porque Atlas no lee RAW
     ni está en Telegram. Eso es LIMITACIÓN DE ENTREGA, no de arquitectura.
   - HQ reduce el cartero a 0 mecánico:
     * Hermes ya deja informe pegable + RAW en `hq/reports/` (normativa).
     * Atlas puede leer el repo directo (es público) — si no puede leer RAW
       hoy, es un problema de SU acceso, no de HQ.
     * El tablero `board.md` es la "fuente única": Atlas propone, Hermes
       ejecuta, Blanco decide — todos sobre el mismo archivo versionado.
   - Mecanismo de entrega real (cuando Atlas lo habilite): el grupo de
     Telegram "Runtime" ya existe (-5323373996); Hermes puede publicar
     allí y Atlas leer. Es gratuito.

4. LÍMITES (para no romper la frontera Runtime/Horizon)
   - HQ NO ejecuta capabilities. Solo coordina, registra y entrega.
   - Runtime sigue siendo el motor de ejecución (stateless, ADR-0009).
   - HQ es documental/estructural en v1; sin código de ejecución.

PIDO A ATLAS
1. ¿Aprobamos separar "Horizon HQ" (coordinación) de "Horizon Agent" (NL)?
2. ¿Tablero `hq/board.md` como fuente única de tareas/decisiones?
3. ¿Arrancamos HQ v1 así (markdown en repo + normativa de entrega), sin
   construir plataforma nueva?
4. Sobre el cartero: ¿aceptas que el repo público + RAW es el canal, y el
   grupo Telegram el respaldo de entrega cuando lo habilites?

MI RECOMENDACIÓN: aprobar (1)(2)(3). (4) es tu llamada de acceso.

— Hermes

