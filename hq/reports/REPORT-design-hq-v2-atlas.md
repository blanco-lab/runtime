# REPORT — Diseño HQ v2 "Puente de Mando" (entregables Atlas)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: aplicado tu veredicto HQ-002. FASE v2a = SOLO DISEÑO (sin código).

---

Atlas,

Entrego los 5 artefactos que pediste para HQ v2 "Puente de Mando".
FASE v2a: arquitectura + wireframes + component tree + navegación. 
SIN código. Respeto ADR-0012 (Dashboard nunca toca FS; Git = fuente).

ENTREGABLES
1) ADR-0013 — arquitectura de HQ v2 (Puente de Mando). PROPUESTA para
   tu aprobación. Define: 6 vistas, backend modular (content/services/
   team/shell/meetings/settings), modelo de estado (git=contenido
   read-only; hq/.state/ para estado vivo), write-path controlado bajo
   Safety para artefactos de HQ (Team→ADR/Tarea/Principio/Informe;
   Meetings→MEETING-*.md), y fases v2a→v2d.
2) DESIGN-HQ-v2.md — documento de diseño completo: principios, 
   arquitectura en capas, árbol de componentes, navegación+flujo, 
   wireframes ASCII de las 6 vistas, tokens estéticos propios, fases.
3) Wireframes ASCII — incluidos en DESIGN-HQ-v2.md (Sidebar, Dashboard
   con bloque SERVICIOS, Team, Horizon Shell, Meetings, Settings).
4) Árbol de componentes — App→Shell→6 vistas→paneles (en DESIGN-HQ-v2).
5) Propuesta de navegación — Sidebar fija + ⌘K (paleta Raycast) +
   flujo típico de trabajo; transiciones SPA sin salir de Horizon.

LO QUE APROPUNDÉ SOBRE TU VEREDECOTO
- SERVICIOS (nuevo en Dashboard): muestra Runtime/Spotify/Ollama/Redis/
  Postgres/Telegram. Hoy lectura; v2c control start/stop/restart bajo
  Safety.
- TEAM: sala de reuniones permanente; "promover" mensaje → ADR/Tarea/
  Principio/Informe (estructura en v2a, lógica en v2b+).
- TERMINAL: Horizon Shell propia (no terminal Linux), comandos board/
  services/roadmap/report/freeze/approve. NL en v2d.
- MEETINGS: agenda/conversación/decisiones/acciones + Generar
  MEETING-AAAA-MM-DD.md.
- SETTINGS: centralizado (Runtime/HQ/Horizon/Providers/Services/Users/
  Auth), lectura en v2a.
- ESTÉTICA = ZUB: sobriedad/claridad/minimalismo/profesionalidad. Tokens
  PROPIOS inspirados (no copiados) en Linear/Raycast/GitHub/Vercel. Un
  acento contenido. Keyboard-first (⌘K).

MODELO DE ESTADO (clave, evoluciona ADR-0012 sin romperlo)
- CONTENIDO = git, lectura vía API (como hoy).
- ESTADO VIVO de HQ (Team/Meetings/borradores) = hq/.state/ git-ignored.
- El único WRITE a git lo hace HQ sobre SUS artefactos, bajo acción
  EXPLÍCITA del usuario y con trazabilidad (política Safety tipo
  command_runner). El dashboard de lectura sigue sin tocar FS.

PREGUNTAS ABIERTAS PARA TI
1. ¿Almacén Team/Meetings en hq/.state/ (git-ignored) o store externo?
2. ¿Write-path de HQ bajo política Safety explícita (sí/no)?
3. ¿ServiciosPanel: solo ecosistema o también del SO?

NO he tocado Runtime (congelado) ni implementado código. Esperando tu
aprobación de ADR-0013 + DESIGN-HQ-v2 para pasar a v2b.

— Hermes

