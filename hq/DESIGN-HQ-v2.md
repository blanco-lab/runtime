# DESIGN-HQ-v2 — Puente de Mando de Horizon

- Autor: Hermes · 2026-07-19
- Basado en: ADR-0011 (3 capas), ADR-0012 (principios permanentes),
  veredicto Atlas "HQ-002 Puente de Mando".
- Fase: v2a = SOLO DISEÑO (arquitectura, wireframes, component tree,
  navegación, flujo). Sin código.

──────────────────────────────────────────
0. PRINCIPIOS RECTORES (no negociables)
──────────────────────────────────────────
- Git = fuente única de verdad para CONTENIDO. La API lo lee (read-only).
- El Dashboard NUNCA toca el FS; todo pasa por el Backend (ADR-0012).
- NUEVO PRINCIPIO (Atlas, 2026-07-19): "La interfaz nunca conoce dónde
  viven los datos. Solo conoce la API." ⇒ El frontend ignora si un dato
  está en git, workspace, state o servicio externo. Solo habla con /api/*.
- Estética = ZUB: sobriedad, claridad, minimalismo, profesionalidad.
  Tokens propios inspirados en Linear/Raycast/GitHub/Vercel (no copiados).
  UN acento contenido. Interacción keyboard-first (estilo Raycast).
- HQ v2 NO implementa capabilities de Runtime. Es evolución de Horizon.
- Crecimiento guiado por uso (ADR-0012): v2a solo diseña; v2b implementa
  tras congelación del diseño.

──────────────────────────────────────────
1. ARQUITECTURA (capas)
──────────────────────────────────────────
   Git (fuente única oficial)
        │  lectura (read-only) — Safety OBLIGATORIA en write
        ▼
   HQ Backend (modular, /api/v2/*)        Workspace (hq/workspace/, git-ignored)
        │  lectura contenido                   │  borradores del equipo
        │                                      │  (team/meetings/tareas/ideas)
        ▼                                      │  reglas Safety MÁS LIGERAS
   API interna  ──────────────────────────────┘  "Promover" -> Git
        │
        ▼
   HQ v2 Frontend (SPA: navegación permanente + vistas)
        └─ State (puramente efímero: ventanas, sesión, terminal)

Módulos del Backend (cada uno = capa de API, NO capability Runtime):
  content   (existente)  board/adrs/principles/reports/roadmap/state
  workspace (nuevo)      borradores: team/meetings/tareas/ideas.
                         NO oficial. "Promover" lo pasa a git (Safety).
  services  (nuevo)      DOS grupos:
       ECOSYSTEM: Runtime, HQ, Horizon, Spotify, Ollama, Redis, Telegram...
       SYSTEM:    CPU, RAM, Discos, Red, Batería, Temperatura...
       (el portátil ES un nodo Horizon)
  team      (nuevo)      sala permanente; "promover" → ADR/Tarea/Principio/Informe
  shell     (nuevo)      Horizon Shell PROPIA con personalidad (no Linux)
  meetings  (nuevo)      agenda/conversación/decisiones/acciones + MEETING-*.md
  projects  (nuevo)      MÚLTIPLES proyectos del ecosistema (no solo Runtime)
  settings  (nuevo)      config (Runtime/HQ/Horizon/Providers/Services/Users/Auth)

SAFETY (AJUSTE 2): todo write a Git OBLIGATORIO por Safety (lista blanca,
sin shell). Workspace = reglas más ligeras (es borrador).

──────────────────────────────────────────
2. ÁRBOL DE COMPONENTES
──────────────────────────────────────────
App
├─ Shell (layout permanente, keyboard-first, personalidad Horizon)
│   ├─ Sidebar (nav: Dashboard/Team/Terminal/Meetings/Roadmap/Projects/Settings)
│   ├─ TopBar (⌘K, perfil, mini-estado ECOSYSTEM/SYSTEM)
│   └─ ViewContainer
├─ DashboardView
│   ├─ StatusOverview
│   ├─ BoardPanel
│   ├─ RecentAdrs
│   ├─ PrinciplesStrip
│   ├─ RoadmapPanel
│   ├─ RecentReports
│   └─ ServicesPanel (DOS grupos)
│       ├─ EcosystemGroup (Runtime/HQ/Horizon/Spotify/Ollama/Redis/Telegram)
│       └─ SystemGroup   (CPU/RAM/Discos/Red/Batería/Temperatura)
├─ TeamView
│   ├─ ConversationList (Atlas/Hermes/Blanco + Horizon Agent futuro)
│   ├─ ConversationThread
│   └─ PromoteMenu (→ ADR/Tarea/Principio/Informe) [v2a: mock]
├─ TerminalView
│   └─ HorizonShell (consola PROPIA con personalidad Horizon; input+historia+salida)
├─ MeetingsView
│   ├─ AgendaPanel ├─ ConversationPanel ├─ DecisionsPanel ├─ ActionsPanel
│   └─ GenerateBtn → MEETING-AAAA-MM-DD.md [v2a: mock]
├─ RoadmapView
│   └─ RoadmapBoard
├─ ProjectsView  (NUEVA, AJUSTE 4)
│   ├─ ProjectList (múltiples proyectos del ecosistema)
│   └─ ProjectDetail (estado, board, services por proyecto)
└─ SettingsView
    ├─ Section (Runtime) ├─ Section (HQ) ├─ Section (Horizon)
    ├─ Section (Providers) ├─ Section (Services) ├─ Section (Users)
    └─ Section (Auth)

──────────────────────────────────────────
3. NAVEGACIÓN Y FLUJO
──────────────────────────────────────────
- Sidebar permanente: 7 entradas (añadida Projects).
- ⌘K: paleta (Raycast) — salta a vista/sección/servicio/ADR/proyecto.
- Dashboard por defecto. Horizon Shell accesible en cualquier vista (⌘J).
- Flujo: entrar → Dashboard (general + Servicios ECOSYSTEM/SYSTEM)
  → Team (promover a ADR) → Terminal (Horizon Shell) → Meetings
  (generar MEETING) → Roadmap → Projects (gestionar varios) → Settings.
- Transiciones SPA. El portátil es un nodo Horizon más (SYSTEM).

──────────────────────────────────────────
4. WIREFRAMES (ASCII)
──────────────────────────────────────────
NAV PRINCIPAL (Sidebar, 7)
  ┌─────────────┐
  │ ◆ Horizon HQ│
  ├─────────────┤
  │ ▸ Dashboard │
  │   Team      │
  │   Terminal  │
  │   Meetings  │
  │   Roadmap   │
  │   Projects  │  (nuevo)
  │   Settings  │
  └─────────────┘   (⌘K paleta)

DASHBOARD — SERVICIOS (dos grupos)
  ┌──────────────────────────────────────────────┐
  │ Horizon HQ            [⌘K]   ECOSYSTEM ●5 SYS ●4│
  ├──────────────────────────────────────────────┤
  │ ESTADO GENERAL   [Runtime ●] [HQ ●] [Bloq ⚠]   │
  ├──────────────────────┬───────────────────────┤
  │ BOARD                 │ SERVICIOS              │
  │ [EN REVISIÓN] HQ-001  │ ▸ ECOSYSTEM            │
  │ [CONGELADA] RTC-001   │   Runtime   ● UP       │
  │ ...                   │   HQ        ● UP       │
  │                       │   Horizon   ○ DOWN     │
  │                       │   Spotify   ● UP       │
  │                       │   Ollama    ○ DOWN     │
  │                       │   Redis     ○ DOWN     │
  │                       │   Telegram  ● UP      │
  │                       │ ▸ SYSTEM (nodo local)  │
  │                       │   CPU 23%  RAM 41%     │
  │                       │   Disc 60% Net ▲ Batería 88% T 54°C │
  └──────────────────────┴───────────────────────┘

PROJECTS (nueva vista)
  ┌──────────────────────────────────────────────┐
  │ PROJECTS                  [+ nuevo proyecto]   │
  ├──────────────────────────────────────────────┤
  │ ◆ runtime      [EN CURSO]   board · 12 adrs   │
  │ ◇ horizon-dev  [IDEA]       sin board aún     │
  │ ◇ doc-site     [PROPUESTA]  pendiente         │
  └──────────────────────────────────────────────┘

TERMINAL — Horizon Shell (con personalidad)
  ┌──────────────────────────────────────────────┐
  │ ◇ horizon ❯ board                            │
  │   HQ-001  EN REVISIÓN   infra coord          │
  │ ◇ horizon ❯ services ecosystem               │
  │   Runtime UP · Spotify UP · Ollama DOWN       │
  │ ◇ horizon ❯ _                                │
  └──────────────────────────────────────────────┘
  (prompt propio "◇ horizon ❯"; no es bash)

[Team / Meetings / Settings: igual que v1 pero con PromoteMenu y
 grupos; véase árbol de componentes]

──────────────────────────────────────────
5. ESTÉTICA (tokens propios, inspiración no copia)
──────────────────────────────────────────
- Fondo #0B0B0F · Superficie #141419 · Borde #23232B
- Texto #E6E6EA / mute #8A8A93
- Acento ÚNICO #7C6CFF · éxito #3FB950 · warn #E3B341 · error #F85149 · info #58A6FF
- Tipo: Inter peso 500/400 · tracking -0.01em · radio 10px
- Sombra solo elevación sutil · transiciones 120–180ms ease-out
- Keyboard-first: ⌘K (paleta) y ⌘J (Horizon Shell) siempre disponibles
- Personalidad Horizon: micro-copys propios ("◇ horizon ❯"), sin estética
  de terminal Linux.

──────────────────────────────────────────
6. FASES (cronograma)
──────────────────────────────────────────
  v2a  este entregable (diseño con 5 ajustes de Atlas)
  v2b  implementación interfaz definitiva (tras congelar diseño)
  v2c  control de servicios (Safety)
  v2d  Horizon Shell con lenguaje natural + personalidad

──────────────────────────────────────────
7. ABIERTO PARA ATLAS
──────────────────────────────────────────
- ¿Almacén Team/Meetings en hq/workspace/ (git-ignored) confirmado?
- (Safety explícita: confirmada por Atlas.)
- ¿Projects: ¿un proyecto = un repo git, o una carpeta lógica dentro de
  runtime? Recomiendo: cada proyecto apunta a su propia fuente git.
