# REPORT — Revisión ADR-0013 (aprobada con ajustes) aplicada a diseño HQ v2

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: aplicados tus 5 ajustes + nuevo principio a ADR-0013 y DESIGN-HQ-v2.
  Diseño listo para congelar y pasar a v2b.

---

Atlas,

Aplicados tus 5 ajustes y el nuevo principio. ADR-0013 = APROBADA CON
AJUSTES; DESIGN-HQ-v2 actualizado. Sin código (fase v2a).

AJUSTE 1 — CAPA WORKSPACE
Añadida entre Git y State:
    Git (oficial, read-only) → Workspace (borradores) → State (efímero)
Workspace = conversaciones, reuniones, tareas, ideas, borradores. NO es
conocimiento oficial; vive en hq/workspace/ (git-ignored) con reglas
Safety MÁS LIGERAS. Solo al "Promover" (acción explícita) pasa a Git.

AJUSTE 2 — SAFETY
Confirmado en ADR-0013: TODO write permanente a Git pasa OBLIGATORIAMENTE
por Safety (lista blanca, sin shell, como command_runner). Workspace =
reglas más ligeras (es borrador).

AJUSTE 3 — PANEL SERVICIOS (dos grupos)
Separados en DESIGN-HQ-v2 (wireframe Dashboard):
  ECOSYSTEM: Runtime, HQ, Horizon, Spotify, Ollama, Redis, Telegram...
  SYSTEM:    CPU, RAM, Discos, Red, Batería, Temperatura...
El portátil ES un nodo Horizon (SYSTEM). v2c: control bajo Safety.

AJUSTE 4 — VISTA PROJECTS (7ª vista)
Añadida a Sidebar, árbol de componentes, navegación y wireframe. HQ gestiona
MÚLTIPLES proyectos del ecosistema (no solo Runtime).

AJUSTE 5 — HORIZON SHELL
Redefinida como consola PROPIA con personalidad Horizon (prompt "◇ horizon ❯",
micro-copys propios), NO terminal Linux incrustada. Comandos board/services/
roadmap/report/freeze/approve. NL + personalidad en v2d.

NUEVO PRINCIPIO (añadido a ADR-0013 y DESIGN-HQ-v2)
"La interfaz nunca conoce dónde viven los datos. Solo conoce la API."
Amplía ADR-0012: el frontend ignora si el dato está en git, workspace,
state o servicio externo. Solo habla con /api/*.

ENTREGABLES ACTUALIZADOS
1) ADR-0013 (aprobada con ajustes) — hq/decisions/ADR-0013-hq-v2-puentemando.md
2) DESIGN-HQ-v2.md — con los 5 ajustes + nuevo principio + wireframes.
3) Wireframes ASCII — Sidebar(7), Dashboard con ECOSYSTEM/SYSTEM, Projects,
   Horizon Shell con personalidad.
4) Árbol de componentes — 7 vistas + Workspace/Safety.
5) Navegación — Sidebar 7 + ⌘K + ⌘J (Horizon Shell global).

ESTADO
Diseño cerrado y coherente. Listo para CONGELAR y empezar v2b (cuando
apruebes). Runtime intacto (congelado). HQ v2 = evolución de Horizon.

PREGUNTA ABIERTA (decisión tuya para cerrar)
- ¿Projects: cada proyecto = su propio repo git, o carpeta lógica en
  runtime? Recomiendo: cada proyecto apunta a su fuente git propia.

— Hermes

