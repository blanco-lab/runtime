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
- Estética = ZUB: sobriedad, claridad, minimalismo, profesionalidad.
  Tokens propios inspirados en Linear/Raycast/GitHub/Vercel (no copiados).
  UN acento contenido. Interacción keyboard-first (estilo Raycast).
- HQ v2 NO implementa capabilities de Runtime. Es evolución de Horizon.
- Crecimiento guiado por uso (ADR-0012): v2a solo diseña; v2b implementa
  tras aprobación.

──────────────────────────────────────────
1. ARQUITECTURA (capas)
──────────────────────────────────────────
   Git (fuente única: hq/, src/)
        │  lectura (read-only)
        ▼
   HQ Backend (modular, /api/v2/*)        HQ State (hq/.state/, git-ignored)
        │  lectura contenido                   │  estado vivo (Team/Meetings/
        │                                      │  borradores, sesión)
        ▼                                      ▲
   API interna  ──────────────────────────────┘
        │
        ▼
   HQ v2 Frontend (SPA: navegación permanente + vistas)

Módulos del Backend (cada uno = capa de API, NO capability Runtime):
  content   (existente)  board/adrs/principles/reports/roadmap/state
  services  (nuevo)      estado de servicios (systemd user, spotify,
                          ollama, redis, postgres, telegram...). v2a: solo
                          lectura. v2c: control (start/stop/restart).
  team      (nuevo)      conversaciones del equipo + "convertir" en
                          ADR/Tarea/Principio/Informe (solo estructura).
  shell     (nuevo)      dispatcher Horizon Shell (board/services/roadmap/
                          report/freeze/approve...). v2a: solo lectura.
  meetings  (nuevo)      agenda/conversación/decisiones/acciones +
                          generar MEETING-AAAA-MM-DD.md (solo estructura).
  settings  (nuevo)      lectura de config (Runtime/HQ/Horizon/Providers/
                          Services/Users/Auth). Escritura en fase posterior.

──────────────────────────────────────────
2. ÁRBOL DE COMPONENTES
──────────────────────────────────────────
App
├─ Shell (layout permanente, keyboard-first)
│   ├─ Sidebar (nav principal: Dashboard/Team/Terminal/Meetings/Roadmap/Settings)
│   ├─ TopBar (búsqueda global ⌘K, perfil, estado de servicios mini)
│   └─ ViewContainer
├─ DashboardView
│   ├─ StatusOverview (estado general del proyecto)
│   ├─ BoardPanel (tablero por estado)
│   ├─ RecentAdrs (ADRs recientes)
│   ├─ PrinciplesStrip (principios)
│   ├─ RoadmapPanel (activas)
│   ├─ RecentReports (informes recientes)
│   └─ ServicesPanel (NUEVO: Runtime/Spotify/Ollama/Redis/Postgres/Telegram)
│       └─ ServiceTile (nombre, estado, acción futura: start/stop/restart)
├─ TeamView
│   ├─ ConversationList (hilos Atlas/Hermes/Blanco + Horizon Agent futuro)
│   ├─ ConversationThread (mensajes del equipo)
│   └─ PromoteMenu (convertir → ADR/Tarea/Principio/Informe) [v2a: mock]
├─ TerminalView
│   └─ HorizonShell (consola propia; input + historia + salida formateada)
│       ej: `board` `services` `roadmap` `report` `freeze` `approve`
├─ MeetingsView
│   ├─ AgendaPanel
│   ├─ ConversationPanel
│   ├─ DecisionsPanel
│   ├─ ActionsPanel
│   └─ GenerateBtn → MEETING-AAAA-MM-DD.md [v2a: mock]
├─ RoadmapView
│   └─ RoadmapBoard (activas + estado de flujo IDEA→ARCHIVADA)
└─ SettingsView
    ├─ Section (Runtime)   ├─ Section (HQ)
    ├─ Section (Horizon)   ├─ Section (Providers)
    ├─ Section (Services)  ├─ Section (Users)
    └─ Section (Auth)

──────────────────────────────────────────
3. NAVEGACIÓN Y FLUJO
──────────────────────────────────────────
- Sidebar permanente: 6 entradas fijas. Estado activo resaltado.
- ⌘K: paleta de comandos (Raycast) — salta a cualquier vista/sección/
  servicio/ADR. Keyboard-first.
- Dashboard es la pantalla por defecto al entrar.
- Flujo típico:
    entrar → Dashboard (visor general + Servicios)
          → Team (lee charla del equipo; "promover" a ADR con un clic mock)
          → Terminal (Horizon Shell: `roadmap`, `services`, `board`)
          → Meetings (reunión → Generar MEETING-*.md mock)
          → Roadmap (visor de estado)
          → Settings (config centralizada, lectura)
- Transiciones: SPA, sin recarga. Sin salir de Horizon para lo cotidiano.
- v2c: desde ServicesPanel se podrá start/stop/restart (Safety).
- v2d: Horizon Shell acepta lenguaje natural.

──────────────────────────────────────────
4. WIREFRAMES (ASCII)
──────────────────────────────────────────
NAV PRINCIPAL (Sidebar)
  ┌─────────────┐
  │ ◆ Horizon HQ│
  ├─────────────┤
  │ ▸ Dashboard │
  │   Team      │
  │   Terminal  │
  │   Meetings  │
  │   Roadmap   │
  │   Settings  │
  └─────────────┘   (⌘K paleta)

DASHBOARD
  ┌──────────────────────────────────────────────┐
  │ Horizon HQ            [⌘K buscar]   ● 6 svc   │
  ├──────────────────────────────────────────────┤
  │ ESTADO GENERAL   [Runtime ●] [HQ ●] [Bloq ⚠]  │
  ├──────────────────────┬───────────────────────┤
  │ BOARD                 │ SERVICIOS             │
  │ [EN CURSO] HQ-001     │ Runtime      ● UP     │
  │ [CONGELADA] RTC-001   │ Spotify      ● UP     │
  │ ...                   │ Ollama       ○ DOWN   │
  │                       │ Redis        ○ DOWN   │
  │                       │ Postgres     ○ DOWN   │
  │                       │ Telegram     ● UP     │
  ├──────────────────────┴───────────────────────┤
  │ ADRs recientes │ Principios │ Roadmap │ Inf.  │
  └──────────────────────────────────────────────┘

TEAM (sala de reuniones permanente)
  ┌────────────┬─────────────────────────────────┐
  │ Hilos      │ Atlas · Hermes · Blanco         │
  │ ─────      ├─────────────────────────────────┤
  │ #arquitect │ > Atlas: elevamos HQ a Puente.. │
  │ #runtime   │ > Hermes: ADR-0013 propuesto    │
  │ #hq        │ [promover ▾] → ADR/Tarea/...    │
  └────────────┴─────────────────────────────────┘

TERMINAL (Horizon Shell)
  ┌──────────────────────────────────────────────┐
  │ horizon> board                               │
  │   HQ-001  EN REVISIÓN   infra coord          │
  │   RTC-001 CONGELADA    music_player          │
  │ horizon> services                              │
  │   Runtime UP · Spotify UP · Ollama DOWN       │
  │ horizon> _                                    │
  └──────────────────────────────────────────────┘

MEETINGS
  ┌──────────┬──────────┬──────────┬─────────────┐
  │ Agenda   │ Convers. │ Decisiones│ Acciones   │
  │ · revisar│ > ...    │ D1: v2.. │ A1: ADR..  │
  └──────────┴──────────┴──────────┴─────────────┘
  [ Generar MEETING-2026-07-19.md ]

SETTINGS (centralizado)
  ┌──────────────────────────────────────────────┐
  │ Runtime | HQ | Horizon | Providers | Services │
  │ Users   | Auth                                 │
  │ ───────────────────────────────────────────── │
  │ [Runtime]  daemon: on · port: 8765            │
  │ [HQ]      theme: dark · accent: ──            │
  │ [Auth]    provider: spotify (reuse token)     │
  └──────────────────────────────────────────────┘

──────────────────────────────────────────
5. ESTÉTICA (tokens propios, inspiración no copia)
──────────────────────────────────────────
- Fondo: #0B0B0F (casi negro, leve azul). Superficie: #141419.
- Borde: #23232B. Texto: #E6E6EA / mute #8A8A93.
- Acento ÚNICO: #7C6CFF (índigo sobrio). Éxito #3FB950 · warn #E3B341 ·
  error #F85149 · info #58A6FF.
- Tipo: Inter (o sistema) peso 500 títulos / 400 cuerpo. Tracking -0.01em.
- Radio 10px. Sombra: solo elevación sutil, sin glow.
- Movimiento: transiciones 120–180ms ease-out. Sin espectacularidad.
- Keyboard-first: ⌘K siempre disponible.

──────────────────────────────────────────
6. FASES (cronograma de construcción)
──────────────────────────────────────────
  v2a  este entregable (diseño)
  v2b  implementación interfaz definitiva (tras aprobación)
  v2c  control de servicios (Safety, write-path)
  v2d  Horizon Shell con lenguaje natural
  (systemd arrancará Horizon, que levanta HQ — ADR-0012)

──────────────────────────────────────────
7. ABIERTO PARA ATLAS
──────────────────────────────────────────
- ¿Almacén Team/Meetings en hq/.state/ (git-ignored) o store externo?
- ¿Write-path de HQ bajo política Safety explícita (sí/no)?
- ¿ServiciosPanel muestra solo los del ecosistema o también del SO?
